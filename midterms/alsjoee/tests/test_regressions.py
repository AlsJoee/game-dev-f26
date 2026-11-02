"""Regression tests for bugs that were observed and fixed.

Final step rejected (found 2026-10-27, fixed before commit f2ed3ab).
PopRoomEpisode.step adds 1 to the step count before checking the action.
The first version checked the action with self.legal_actions(), which
returns [] once the episode looks terminal. On the last allowed step the
count had already reached max_steps, so the last move was always rejected
as invalid and a room needing exactly max_steps moves could never be won.
The fix asks the World for its legal actions instead. The bug was caught by
the episode tests while it was being written, so git history never contained
the broken version; the account is in the 2026-10-27 development session.
"""

import unittest

from pop_room.episode import PLAYER_ID, PopRoomEpisode

P = PLAYER_ID
ROOM_A_SOLUTION = ["right", "jump_right", "right", "right", "right", "right", "right"]


class FinalStepRegressionTest(unittest.TestCase):
    def test_last_allowed_step_is_accepted(self):
        ep = PopRoomEpisode(max_steps=3)
        ep.reset(room="A")
        ep.step(P, "wait")
        ep.step(P, "wait")
        result = ep.step(P, "right")  # step 3 of 3
        self.assertTrue(result["accepted"])
        self.assertEqual(ep.trace[-1]["action"], "right")
        self.assertEqual(ep.observe(P)["prince"], {"row": 0, "col": 1})
        self.assertEqual((ep.outcome()["reason"], ep.outcome()["invalid_actions"]), ("step limit", 0))

    def test_room_needing_exactly_max_steps_can_be_won(self):
        ep = PopRoomEpisode(max_steps=len(ROOM_A_SOLUTION))
        ep.reset(room="A")
        for action in ROOM_A_SOLUTION:
            ep.step(P, action)
        self.assertEqual(ep.outcome()["reason"], "reached the exit")
        self.assertEqual(ep.outcome()["invalid_actions"], 0)


if __name__ == "__main__":
    unittest.main()
