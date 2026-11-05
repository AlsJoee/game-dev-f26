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

Wall landing (found 2026-11-02 by tests/test_invariants.py, fixed 2026-11-04).
A fall stopped on the first tile below that was not a gap, and a wall counted
as one, so the Prince could end up inside a wall. Room B's declared solution
went through the wall at row 2, column 2 (counting from 0). Walls are now
solid: a fall stops on the empty tile directly above a wall, and only floors
actually dropped count. That wall in room B became floor.
"""

import unittest

from pop_room.episode import PLAYER_ID, PopRoomEpisode
from pop_room.rooms import ROOMS
from pop_room.world import WALL, World

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


class WallLandingBug20261104Test(unittest.TestCase):
    def assert_not_on_wall(self, world):
        self.assertNotEqual(world.tile(world.row, world.col), WALL)

    def test_fall_straight_onto_a_wall_stops_on_top_of_it(self):
        world = World(["S ",
                       ".#"])
        text = world.act("right")
        self.assertEqual((world.row, world.col), (0, 1))  # the gap above the wall acts as floor
        self.assert_not_on_wall(world)
        self.assertEqual((world.status, world.health), ("playing", 2))
        self.assertNotIn("fell", text)

    def test_only_floors_actually_dropped_count(self):
        world = World(["S ",
                       ". ",
                       ".#"])
        self.assertIn("fell 1 floor", world.act("right"))
        self.assertEqual((world.row, world.col, world.health), (1, 1, 2))
        self.assert_not_on_wall(world)

    def test_two_floor_drop_onto_a_wall_costs_one_health_and_survives(self):
        world = World(["S ",
                       ". ",
                       ". ",
                       ".#"])
        self.assertIn("fell 2 floors", world.act("right"))
        self.assertEqual((world.row, world.col, world.health, world.status), (2, 1, 1, "playing"))
        self.assert_not_on_wall(world)

    def test_three_floor_drop_onto_a_wall_kills_without_entering_it(self):
        world = World(["S ",
                       ". ",
                       ". ",
                       ". ",
                       ".#"])
        world.act("right")
        self.assertEqual((world.row, world.col, world.status), (3, 1, "dead"))
        self.assert_not_on_wall(world)

    def test_jump_onto_a_gap_above_a_wall_stops_there(self):
        world = World(["S  ",
                       "..#"])
        world.act("jump_right")
        self.assertEqual((world.row, world.col), (0, 2))
        self.assert_not_on_wall(world)

    def test_standing_above_a_wall_is_stable_and_walls_stay_solid(self):
        world = World(["S #",
                       ".#."])
        world.act("right")
        world.act("wait")
        self.assertEqual((world.row, world.col), (0, 1))  # waiting does not sink into the wall
        self.assertFalse(world.is_legal("right"))         # the wall beside him still blocks
        before = world.to_dict()
        with self.assertRaises(ValueError):
            world.act("right")
        self.assertEqual(world.to_dict(), before)

    def test_room_b_wall_became_floor(self):
        self.assertEqual(ROOMS["B"][2], "...  ...#")
        self.assertEqual(ROOMS["B"][2][2], ".")


if __name__ == "__main__":
    unittest.main()
