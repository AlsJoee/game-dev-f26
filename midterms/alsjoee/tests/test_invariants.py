"""Rule invariants, checked in every state reachable in every declared room.

The other World tests check one example each. These walk every reachable
(row, col, health, gate_turns) state by trying every action, and check
properties that must hold in all of them.
"""

import copy
import unittest

from pop_room.rooms import ROOMS
from pop_room.world import (ACTIONS, EMPTY, EXIT, GATE_OPEN_TURNS, SPIKES, START_HEALTH, WALL,
                            World)


def key(world):
    return (world.row, world.col, world.health, world.gate_turns, world.status)


def reachable(layout):
    """Every World state reachable from the start, including terminal ones."""
    start = World(layout)
    seen, frontier, states = {key(start)}, [start], [start]
    while frontier:
        world = frontier.pop()
        for action in world.legal_actions():
            nxt = copy.deepcopy(world)
            nxt.act(action)
            if key(nxt) not in seen:
                seen.add(key(nxt))
                states.append(nxt)
                if nxt.status == "playing":
                    frontier.append(nxt)
    return states


STATES = [(room, world) for room, layout in ROOMS.items() for world in reachable(layout)]
KNOWN_WALL_LANDINGS = {("B", 2, 2)}


def wall_states():
    """(room, row, col) of every reachable state with the Prince on a wall tile."""
    return {(room, w.row, w.col) for room, w in STATES if w.tile(w.row, w.col) == WALL}


class RuleInvariantTest(unittest.TestCase):
    def check_each_state(self, check):
        for room, world in STATES:
            with self.subTest(room=room, state=key(world)):
                check(world)

    def test_rooms_have_many_reachable_states(self):
        # Guards against the walk silently checking almost nothing.
        for room, layout in ROOMS.items():
            self.assertGreater(len(reachable(layout)), 10, room)

    def test_prince_is_always_on_the_grid_and_never_in_a_gap(self):
        def check(world):
            tile = world.tile(world.row, world.col)
            if world.status == "dead" and world.death_reason == "fell off the bottom":
                return  # the only way to leave the grid, and it ends the game
            self.assertIsNotNone(tile)
            self.assertNotEqual(tile, EMPTY)
        self.check_each_state(check)

    def test_no_wall_landings_beyond_the_known_one(self):
        self.assertLessEqual(wall_states(), KNOWN_WALL_LANDINGS)

    # KNOWN ISSUE, found 2026-11-02 by this test; rule decision pending.
    # A fall stops on the first tile below that is not a gap, and a wall counts
    # as one, so the Prince can end up inside a wall. This happens only in room B:
    # walking left from (1,3) into the gap at (1,2) lands him in the wall at (2,2),
    # and room B's declared 10-move shortest solution goes through that state.
    # When the rule is fixed this test passes, unittest reports an unexpected
    # success and CI fails: then remove this marker and KNOWN_WALL_LANDINGS.
    @unittest.expectedFailure
    def test_prince_is_never_inside_a_wall(self):
        self.assertEqual(wall_states(), set())

    def test_health_and_gate_timer_stay_in_range(self):
        def check(world):
            self.assertLessEqual(world.health, START_HEALTH)
            self.assertTrue(0 <= world.gate_turns <= GATE_OPEN_TURNS)
            if world.status == "playing":
                self.assertGreater(world.health, 0)
        self.check_each_state(check)

    def test_status_matches_the_tile(self):
        def check(world):
            tile = world.tile(world.row, world.col)
            if world.status == "won":
                self.assertEqual(tile, EXIT)
            if world.status == "playing":
                self.assertNotIn(tile, (EXIT, SPIKES))
            self.assertEqual(world.death_reason is not None, world.status == "dead")
        self.check_each_state(check)

    def test_legal_actions_are_known_and_wait_is_always_legal_while_playing(self):
        def check(world):
            legal = world.legal_actions()
            self.assertLessEqual(set(legal), set(ACTIONS))
            self.assertEqual("wait" in legal, world.status == "playing")
        self.check_each_state(check)

    def test_illegal_actions_raise_and_change_nothing(self):
        def check(world):
            before = world.to_dict()
            for action in [a for a in ACTIONS if a not in world.legal_actions()] + ["fly"]:
                with self.assertRaises(ValueError):
                    world.act(action)
                self.assertEqual(world.to_dict(), before)
        self.check_each_state(check)


if __name__ == "__main__":
    unittest.main()
