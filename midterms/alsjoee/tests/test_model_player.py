"""Model player tests with a fake client. No network, no credits."""

import json
import time
from types import SimpleNamespace
import unittest

from pop_room.episode import PopRoomEpisode
from pop_room.model_player import (LIMIT_REASON, ModelPlayer, ModelReply, build_prompt,
                                   local_view, parse_action, reply_from_response, run_episode,
                                   summarize)
from pop_room.rules_text import intro
from pop_room.world import World

_, LEGEND_LINES, RULE_LINES = intro(40).split("\n\n")  # goal, "Map legend:" block, "Rules:" block


class FakeClient:
    """Replies from a script. An Exception item is raised; a float item sleeps that long."""

    def __init__(self, *script):
        self.script = list(script)
        self.prompts = []

    def __call__(self, prompt, seed=None):
        self.prompts.append(prompt)
        item = self.script.pop(0) if self.script else "wait"
        if isinstance(item, Exception):
            raise item
        if isinstance(item, float):
            time.sleep(item)
            return ModelReply("wait")
        return ModelReply(item, input_tokens=100, output_tokens=2, model_version="fake-model")


def play(client, room="A", **kwargs):
    player = ModelPlayer(client, **kwargs)
    episode = PopRoomEpisode()
    records, outcome = run_episode(episode, player, room, seed=1)
    return player, episode, records, outcome


class ParseTest(unittest.TestCase):
    def test_clean_reply(self):
        self.assertEqual(parse_action("right", ["right", "wait"]), "right")

    def test_messy_reply(self):
        legal = ["left", "right", "jump_right", "wait"]
        self.assertEqual(parse_action("Sure! I'll **Jump Right**.", legal), "jump_right")
        self.assertEqual(parse_action("Action: `jump-right`\n", legal), "jump_right")

    def test_first_legal_action_wins(self):
        # "climb" is not legal here, so the first legal word is "right".
        self.assertEqual(parse_action("climb, or else right, then wait", ["right", "wait"]), "right")

    def test_right_inside_jump_right_is_not_right(self):
        self.assertIsNone(parse_action("jump_right", ["left", "right", "wait"]))

    def test_no_legal_action(self):
        self.assertIsNone(parse_action("I am not sure.", ["right", "wait"]))


class EpisodeTest(unittest.TestCase):
    def test_clean_replies_win_room_a(self):
        client = FakeClient("right", "jump_right", "right", "right", "right", "right", "right")
        player, episode, records, outcome = play(client)
        self.assertEqual(outcome["reason"], "reached the exit")
        self.assertEqual((outcome["steps"], outcome["invalid_actions"]), (7, 0))
        first = records[0]
        self.assertEqual((first["raw_reply"], first["parsed_action"], first["accepted"],
                          first["fallback"]), ("right", "right", True, False))
        for key in ("step", "observation", "latency_s", "input_tokens", "output_tokens"):
            self.assertIn(key, first)

    def test_messy_reply_is_played(self):
        _, _, records, _ = play(FakeClient("I will go **RIGHT**."), max_model_calls=1)
        self.assertEqual((records[0]["parsed_action"], records[0]["accepted"]), ("right", True))

    def test_reply_without_legal_action_counts_invalid(self):
        _, episode, records, _ = play(FakeClient("fly away"), max_model_calls=1)
        self.assertEqual(records[0]["action"], "fly away")
        self.assertIsNone(records[0]["parsed_action"])
        self.assertFalse(records[0]["accepted"])
        self.assertFalse(records[0]["fallback"])
        self.assertEqual(episode.invalid_actions, 1)

    def test_failed_call_is_labelled_fallback(self):
        player, episode, records, outcome = play(FakeClient(RuntimeError("503")), max_model_calls=1)
        record = records[0]
        self.assertEqual((record["action"], record["fallback"], record["accepted"]), ("wait", True, True))
        self.assertIsNone(record["raw_reply"])
        self.assertIn("RuntimeError", record["error"])
        self.assertEqual(player.model_calls, 1)
        summary = summarize(records, outcome, player, model="fake", room="A", seed=1, git_commit="x")
        self.assertEqual((summary["fallbacks"], summary["model_moves"], summary["model_calls"]), (1, 0, 1))
        self.assertEqual(episode.invalid_actions, 0)

    def test_timed_out_call_is_labelled_fallback(self):
        _, _, records, _ = play(FakeClient(0.5), max_model_calls=1, timeout_s=0.05)
        self.assertTrue(records[0]["fallback"])
        self.assertIn("timed out", records[0]["error"])

    def test_model_call_limit_ends_episode(self):
        client = FakeClient("wait", RuntimeError("boom"), "wait")
        player, episode, records, outcome = play(client, max_model_calls=3)
        self.assertEqual((outcome["status"], outcome["reason"], outcome["score"]),
                         ("terminal", LIMIT_REASON, 0))
        self.assertEqual((player.model_calls, len(records), episode.steps), (3, 3, 3))
        self.assertEqual(len(client.prompts), 3)


class PromptTest(unittest.TestCase):
    def test_prompt_contains_rules_observation_and_legal_actions(self):
        obs = PopRoomEpisode().reset(room="A")
        prompt = build_prompt(obs, ["right", "wait"], [], 40)
        self.assertIn(intro(40), prompt)
        self.assertIn('"gate": "closed"', prompt)
        self.assertIn("Legal actions: right, wait", prompt)
        self.assertNotIn("gate_turns", prompt)

    def test_trace_records_full_prompt(self):
        # The third move steps on the plate, so the fourth prompt is seen with the gate open.
        client = FakeClient("right", "jump_right", "right", "right")
        _, _, records, _ = play(client, max_model_calls=4)
        self.assertEqual([r["prompt"] for r in records], client.prompts)
        for record in records:
            with self.subTest(step=record["step"]):
                prompt = record["prompt"]
                self.assertIn(LEGEND_LINES, prompt)
                self.assertIn(RULE_LINES, prompt)
                self.assertIn(json.dumps(record["observation"]), prompt)
                self.assertIn("Legal actions: " + ", ".join(record["legal_actions"]), prompt)
                self.assertNotIn("gate_turns", prompt)
                self.assertNotRegex(prompt, r'"gate": \d')
        self.assertIn('"gate": "open"', records[3]["prompt"])

    def test_history_zero_shows_no_moves(self):
        client = FakeClient("right", "right", "right")
        play(client, max_model_calls=3, history=0)
        self.assertTrue(all("Your last" not in p for p in client.prompts))

    def test_history_is_capped_at_n(self):
        client = FakeClient("wait", "right", "wait", "jump_right", "wait")
        play(client, max_model_calls=5, history=2)
        last = client.prompts[-1]
        self.assertIn("Your last 2 moves (oldest first):", last)
        moves = [line for line in last.splitlines() if line.startswith("- ")]
        self.assertEqual(moves, ["- wait: wait", "- jump_right: jump_right"])
        self.assertIn("Your last 1 moves", client.prompts[1])



def gemini_response(text="right", prompt=120, candidates=1, thoughts=None, usage=True):
    """Shaped like a google-genai GenerateContentResponse, as far as reply_from_response reads it."""
    metadata = SimpleNamespace(prompt_token_count=prompt, candidates_token_count=candidates,
                               thoughts_token_count=thoughts) if usage else None
    return SimpleNamespace(text=text, usage_metadata=metadata, model_version="gemini-3.8-flash-001")


class ThinkingTokensTest(unittest.TestCase):
    def test_thinking_tokens_count_as_output_and_are_kept_separately(self):
        reply = reply_from_response(gemini_response(candidates=1, thoughts=250), "gemini-3.8-flash")
        self.assertEqual((reply.text, reply.input_tokens, reply.output_tokens, reply.thinking_tokens),
                         ("right", 120, 251, 250))
        self.assertEqual(reply.model_version, "gemini-3.8-flash-001")

    def test_no_thinking_reported_is_zero(self):
        reply = reply_from_response(gemini_response(candidates=2, thoughts=None), "m")
        self.assertEqual((reply.output_tokens, reply.thinking_tokens), (2, 0))

    def test_thinking_without_reply_tokens(self):
        # A reply cut off while thinking may have no candidate tokens.
        reply = reply_from_response(gemini_response(text=None, candidates=None, thoughts=1024), "m")
        self.assertEqual((reply.text, reply.output_tokens, reply.thinking_tokens), ("", 1024, 1024))

    def test_no_usage_metadata(self):
        reply = reply_from_response(gemini_response(usage=False), "m")
        self.assertEqual((reply.input_tokens, reply.output_tokens, reply.thinking_tokens),
                         (None, None, None))

    def test_thinking_tokens_in_trace_and_summary(self):
        class ThinkingFake(FakeClient):
            def __call__(self, prompt, seed=None):
                return reply_from_response(gemini_response(text=super().__call__(prompt).text,
                                                           thoughts=40), "gemini-3.8-flash")

        player, _, records, outcome = play(ThinkingFake("right", "jump_right"), max_model_calls=2)
        self.assertEqual([(r["output_tokens"], r["thinking_tokens"]) for r in records],
                         [(41, 40), (41, 40)])
        summary = summarize(records, outcome, player, model="gemini-3.8-flash", room="A", seed=1,
                            git_commit="x")
        self.assertEqual((summary["output_tokens"], summary["thinking_tokens"]), (82, 80))

    def test_fallback_has_no_thinking_tokens(self):
        _, _, records, _ = play(FakeClient(RuntimeError("503")), max_model_calls=1)
        self.assertIsNone(records[0]["thinking_tokens"])


def obs(grid, row, col, gate="closed"):
    """A hand-made observation; local_view must use only these fields."""
    return {"map": grid, "prince": {"row": row, "col": col}, "health": 2, "gate": gate,
            "steps_used": 0, "steps_left": 40, "last_result": ""}


class LocalViewTest(unittest.TestCase):
    def test_room_a_start_is_at_the_edge_of_the_map(self):
        observation = PopRoomEpisode().reset(room="A")
        self.assertEqual(local_view(observation), "Next to you: left = edge of map; right = floor; "
                                                   "above = edge of map; below = edge of map")

    def test_gap_over_spikes(self):
        grid = [".. .",
                "#.^#"]
        self.assertEqual(local_view(obs(grid, 0, 1)),
                         "Next to you: left = floor; right = gap (below it: spikes, fall 1 floor); "
                         "above = edge of map; below = floor")

    def test_gap_counts_floors_and_falling_off(self):
        grid = [". . ",
                "#   ",
                "#P. "]
        self.assertEqual(local_view(obs(grid, 0, 2)),
                         "Next to you: left = gap (below it: plate, fall 2 floors); "
                         "right = gap (below it: nothing; you would fall off the map); "
                         "above = edge of map; below = gap")

    def test_gap_directly_above_a_wall_is_no_fall(self):
        grid = [".. ",
                "..#"]
        self.assertEqual(local_view(obs(grid, 0, 1)),
                         "Next to you: left = floor; right = gap (below it: wall; you would stop "
                         "on top of it); above = edge of map; below = floor")

    def test_gap_above_more_gap_then_a_wall_counts_floors_dropped(self):
        grid = [".. ",
                ".. ",
                "..#"]
        self.assertEqual(local_view(obs(grid, 0, 1)),
                         "Next to you: left = floor; right = gap (below it: wall; you would stop "
                         "on top of it, fall 1 floor); above = edge of map; below = floor")

    def test_local_view_agrees_with_the_world_on_a_fall_onto_a_wall(self):
        world = World(["S ",
                       ". ",
                       ".#"])
        view = local_view(obs([". ", ". ", ".#"], 0, 0))
        self.assertIn("right = gap (below it: wall; you would stop on top of it, fall 1 floor)", view)
        self.assertIn("fell 1 floor", world.act("right"))
        self.assertEqual((world.row, world.col), (1, 1))

    def test_gate_state_wall_and_exit(self):
        grid = ["###",
                "G.E",
                "..."]
        self.assertEqual(local_view(obs(grid, 1, 1, gate="open")),
                         "Next to you: left = gate (open); right = exit; above = wall; below = floor")

    def test_room_c_after_two_steps(self):
        ep = PopRoomEpisode()
        ep.reset(room="C")
        ep.step("prince", "right")
        observation = ep.step("prince", "right")["observation"]
        self.assertEqual(local_view(observation), "Next to you: left = floor; right = spikes; "
                                                   "above = floor; below = edge of map")

    def test_local_view_only_with_view_local(self):
        observation = PopRoomEpisode().reset(room="A")
        self.assertNotIn("Next to you:", build_prompt(observation, ["right"], [], 40))
        self.assertIn(local_view(observation),
                      build_prompt(observation, ["right"], [], 40, view="local"))
        with self.assertRaises(ValueError):
            build_prompt(observation, ["right"], [], 40, view="far")

    def test_view_recorded_in_trace_summary(self):
        player, _, records, outcome = play(FakeClient("right"), max_model_calls=1, view="local")
        self.assertIn("Next to you:", records[0]["prompt"])
        summary = summarize(records, outcome, player, model="fake", room="A", seed=1, git_commit="x")
        self.assertEqual(summary["view"], "local")


if __name__ == "__main__":
    unittest.main()
