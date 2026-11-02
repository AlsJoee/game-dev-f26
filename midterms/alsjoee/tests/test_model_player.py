"""Model player tests with a fake client. No network, no credits."""

import json
import time
import unittest

from pop_room.episode import PopRoomEpisode
from pop_room.model_player import (LIMIT_REASON, ModelPlayer, ModelReply, build_prompt,
                                   parse_action, run_episode, summarize)
from pop_room.rules_text import intro

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


if __name__ == "__main__":
    unittest.main()
