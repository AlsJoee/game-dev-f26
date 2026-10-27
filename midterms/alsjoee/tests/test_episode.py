import unittest

from pop_room.episode import PLAYER_ID, PopRoomEpisode

P = PLAYER_ID
ROOM_A_SOLUTION = ["right", "jump_right", "right", "right", "right", "right", "right"]


def run(episode, *actions):
    for action in actions:
        result = episode.step(P, action)
    return result


class ResetAndObserveTest(unittest.TestCase):
    def test_reset_observation(self):
        ep = PopRoomEpisode()
        obs = ep.reset(seed=7, room="C")
        self.assertEqual((ep.seed, ep.room), (7, "C"))
        self.assertEqual(obs, {
            "map": ["#...G..E", "#.. P###", "...^####"],
            "prince": {"row": 2, "col": 0},
            "health": 2,
            "gate": "closed",
            "steps_used": 0,
            "steps_left": 40,
            "last_result": "",
        })

    def test_reset_clears_steps_invalid_actions_and_trace(self):
        ep = PopRoomEpisode()
        run(ep, "right", "fly")
        ep.reset(room="A")
        self.assertEqual((ep.steps, ep.invalid_actions, ep.trace), (0, 0, []))
        self.assertEqual(ep.observe(P)["last_result"], "")

    def test_start_tile_not_in_observed_map(self):
        ep = PopRoomEpisode()
        for room in ("A", "B", "C", "H"):
            with self.subTest(room=room):
                obs = ep.reset(room=room)
                self.assertFalse(any("S" in row for row in obs["map"]))

    def test_observation_never_contains_gate_turn_count(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        run(ep, "right", "jump_right", "right")  # onto the plate: gate open
        obs = ep.observe(P)
        self.assertEqual(obs["gate"], "open")
        self.assertNotIn("gate_turns", obs)
        self.assertEqual(set(obs), {"map", "prince", "health", "gate",
                                    "steps_used", "steps_left", "last_result"})

    def test_other_player_id_raises(self):
        ep = PopRoomEpisode()
        for call in (ep.observe, ep.legal_actions, lambda p: ep.step(p, "wait")):
            with self.assertRaises(ValueError):
                call("guard")

    def test_unknown_room_raises(self):
        with self.assertRaises(ValueError):
            PopRoomEpisode().reset(room="Z")


class StepTest(unittest.TestCase):
    def test_win_room_a_in_seven_moves(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        for action in ROOM_A_SOLUTION:
            self.assertTrue(ep.step(P, action)["accepted"])
        self.assertEqual(ep.outcome(), {"status": "terminal", "reason": "reached the exit",
                                        "score": 1, "steps": 7, "invalid_actions": 0})
        self.assertEqual(ep.legal_actions(P), [])

    def test_action_is_normalised(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        self.assertTrue(ep.step(P, "  RIGHT \n")["accepted"])

    def test_invalid_move_counts_as_step_without_changing_world_or_gate(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        run(ep, "right", "jump_right", "right")  # on the plate, gate open for 3 turns
        before = ep._world.to_dict()
        result = ep.step(P, "climb")
        self.assertFalse(result["accepted"])
        self.assertEqual(ep._world.to_dict(), before)  # includes gate_turns: no tick
        self.assertEqual((ep.steps, ep.invalid_actions), (4, 1))
        self.assertEqual(result["observation"]["steps_used"], 4)
        self.assertEqual(result["observation"]["last_result"], result["text"])

    def test_non_string_action_is_invalid(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        self.assertFalse(ep.step(P, 42)["accepted"])
        self.assertEqual(ep.invalid_actions, 1)

    def test_trace_records_each_step(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        run(ep, "right", "left_up")
        self.assertEqual(ep.trace[0], {"step": 1, "action": "right", "accepted": True,
                                       "text": "right", "row": 0, "col": 1, "health": 2})
        self.assertEqual(ep.trace[1]["accepted"], False)
        self.assertEqual((ep.trace[1]["row"], ep.trace[1]["col"]), (0, 1))

    def test_steps_after_end_are_refused_and_not_counted(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        run(ep, *ROOM_A_SOLUTION)
        result = ep.step(P, "left")
        self.assertFalse(result["accepted"])
        self.assertEqual((ep.steps, ep.invalid_actions, len(ep.trace)), (7, 0, 7))


class OutcomeTest(unittest.TestCase):
    def test_ongoing(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        self.assertEqual(ep.outcome()["status"], "ongoing")

    def test_step_limit_after_40_steps(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        for _ in range(39):
            ep.step(P, "wait")
        self.assertEqual(ep.outcome()["status"], "ongoing")
        ep.step(P, "wait")
        self.assertEqual(ep.outcome(), {"status": "terminal", "reason": "step limit",
                                        "score": 0, "steps": 40, "invalid_actions": 0})
        self.assertEqual(ep.observe(P)["steps_left"], 0)
        self.assertEqual(ep.legal_actions(P), [])
        self.assertFalse(ep.step(P, "wait")["accepted"])
        self.assertEqual(ep.steps, 40)

    def test_invalid_actions_also_reach_step_limit(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        for _ in range(40):
            ep.step(P, "dance")
        self.assertEqual(ep.outcome()["reason"], "step limit")
        self.assertEqual(ep.outcome()["invalid_actions"], 40)

    def test_died_on_spikes(self):
        ep = PopRoomEpisode()
        ep.reset(room="C")
        run(ep, "right", "right", "right")
        self.assertEqual(ep.outcome()["reason"], "died: spikes")
        self.assertEqual(ep.outcome()["score"], 0)

    def test_died_falling_off_bottom(self):
        ep = PopRoomEpisode()
        ep.reset(room="A")
        run(ep, "right", "right")
        self.assertEqual(ep.outcome()["reason"], "died: fell off the bottom")

    def test_win_on_last_step_beats_step_limit(self):
        ep = PopRoomEpisode(max_steps=7)
        ep.reset(room="A")
        run(ep, *ROOM_A_SOLUTION)
        self.assertEqual(ep.outcome()["reason"], "reached the exit")


if __name__ == "__main__":
    unittest.main()
