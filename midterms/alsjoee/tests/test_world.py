import unittest

from pop_room.rooms import ROOMS
from pop_room.world import World


def play(world, *actions):
    for action in actions:
        world.act(action)
    return world


class InitialStateTest(unittest.TestCase):
    def test_starts_on_s_with_two_health_and_closed_gate(self):
        w = World(ROOMS["C"])
        self.assertEqual(w.to_dict(), {
            "row": 2, "col": 0, "health": 2, "gate_turns": 0,
            "status": "playing", "death_reason": None,
        })

    def test_rooms_are_rectangular_with_one_start(self):
        for name, layout in ROOMS.items():
            with self.subTest(room=name):
                World(layout)


class WalkTest(unittest.TestCase):
    def test_walk_moves_one_tile(self):
        w = play(World(["S.."]), "right")
        self.assertEqual((w.row, w.col), (0, 1))

    def test_walk_off_grid_is_illegal(self):
        self.assertNotIn("left", World(["S.."]).legal_actions())

    def test_walk_into_wall_is_illegal(self):
        self.assertNotIn("right", World(["S#."]).legal_actions())

    def test_closed_gate_blocks_walking(self):
        w = World(["SG."])
        self.assertNotIn("right", w.legal_actions())
        with self.assertRaises(ValueError):
            w.act("right")

    def test_open_gate_allows_walking(self):
        w = play(World(["SPG."]), "right")
        self.assertIn("right", w.legal_actions())

    def test_walk_into_spikes_is_legal_and_kills(self):
        w = World(["S^."])
        self.assertIn("right", w.legal_actions())
        w.act("right")
        self.assertEqual(w.status, "dead")
        self.assertEqual(w.death_reason, "spikes")


class JumpTest(unittest.TestCase):
    def test_jump_clears_one_gap_and_lands_two_away(self):
        w = play(World(["S ."]), "jump_right")
        self.assertEqual((w.row, w.col, w.status), (0, 2, "playing"))

    def test_jump_needs_empty_adjacent_tile(self):
        self.assertNotIn("jump_right", World(["S.."]).legal_actions())

    def test_jump_landing_off_grid_wall_or_closed_gate_is_illegal(self):
        for layout in (["S "], ["S #"], ["S G"]):
            with self.subTest(layout=layout):
                self.assertNotIn("jump_right", World(layout).legal_actions())

    def test_jump_left(self):
        w = play(World([". S"]), "jump_left")
        self.assertEqual(w.col, 0)

    def test_jump_onto_spikes_is_legal_and_kills(self):
        w = World(["S ^"])
        self.assertIn("jump_right", w.legal_actions())
        w.act("jump_right")
        self.assertEqual(w.death_reason, "spikes")


class ClimbTest(unittest.TestCase):
    def test_climb_moves_up_one_floor(self):
        w = play(World([".", "S"]), "climb")
        self.assertEqual((w.row, w.col), (0, 0))

    def test_climb_targets_that_are_legal(self):
        for tile in ".SPE":
            layout = [tile, "S"] if tile != "S" else ["S", "."]
            w = World(layout)
            if tile == "S":
                w.row = 1  # stand below the start tile
            with self.subTest(tile=tile):
                self.assertIn("climb", w.legal_actions())

    def test_climb_targets_that_are_illegal(self):
        for above in (" ", "#", "^", "G"):
            with self.subTest(above=above):
                self.assertNotIn("climb", World([above, "S"]).legal_actions())

    def test_climb_from_top_row_is_illegal(self):
        self.assertNotIn("climb", World(["S"]).legal_actions())

    def test_climb_into_open_gate_is_legal(self):
        w = play(World([".G", "SP"]), "right")
        self.assertIn("climb", w.legal_actions())


class WaitTest(unittest.TestCase):
    def test_wait_is_always_legal_and_keeps_position(self):
        w = World(["#S#"])
        self.assertEqual(w.legal_actions(), ["wait"])
        w.act("wait")
        self.assertEqual((w.row, w.col), (0, 1))


class FallTest(unittest.TestCase):
    def test_one_floor_fall_is_safe(self):
        w = play(World(["S ", ".."]), "right")
        self.assertEqual((w.row, w.col, w.health, w.status), (1, 1, 2, "playing"))

    def test_two_floor_fall_costs_one_health(self):
        w = play(World(["S ", ". ", ".."]), "right")
        self.assertEqual((w.row, w.health, w.status), (2, 1, "playing"))

    def test_three_floor_fall_kills(self):
        w = play(World(["S ", ". ", ". ", ".."]), "right")
        self.assertEqual(w.status, "dead")
        self.assertEqual(w.death_reason, "fell 3 or more floors")

    def test_falling_off_bottom_kills(self):
        w = play(World(["S "]), "right")
        self.assertEqual(w.status, "dead")
        self.assertEqual(w.death_reason, "fell off the bottom")

    def test_health_reaching_zero_kills(self):
        w = World(["S  ", ".  ", ".. ", "#. ", "#.."])
        w.act("right")   # row 0 -> row 2, health 1
        w.act("right")   # row 2 -> row 4, health 0
        self.assertEqual(w.health, 0)
        self.assertEqual(w.death_reason, "health reached 0")

    def test_falling_onto_spikes_kills(self):
        w = play(World(["S ", ".^"]), "right")
        self.assertEqual(w.death_reason, "spikes")

    def test_jump_onto_empty_tile_falls(self):
        w = play(World(["S  ", "..."]), "jump_right")
        self.assertEqual((w.row, w.col), (1, 2))


class ExitTest(unittest.TestCase):
    def test_walking_onto_exit_wins(self):
        w = play(World(["SE"]), "right")
        self.assertEqual(w.status, "won")
        self.assertEqual(w.legal_actions(), [])

    def test_falling_onto_exit_wins(self):
        w = play(World(["S ", ".E"]), "right")
        self.assertEqual(w.status, "won")

    def test_no_actions_after_game_over(self):
        w = play(World(["S^"]), "right")
        self.assertEqual(w.legal_actions(), [])
        with self.assertRaises(ValueError):
            w.act("wait")


class GateTest(unittest.TestCase):
    def test_stepping_on_plate_opens_gate_for_three_turns(self):
        w = play(World(["SP.."]), "right")
        self.assertEqual(w.gate_turns, 3)
        self.assertTrue(w.gate_open)

    def test_gate_closes_after_exactly_three_turns(self):
        w = play(World(["SP.........G"]), "right")
        for expected in (2, 1, 0):
            self.assertTrue(w.gate_open)  # open at the start of this turn
            w.act("right")
            self.assertEqual(w.gate_turns, expected)
        self.assertFalse(w.gate_open)

    def test_gate_usable_on_third_turn_but_not_fourth(self):
        # third turn after the plate: walking into the gate is still legal
        w = play(World(["SP..G"]), "right", "right", "right")
        self.assertIn("right", w.legal_actions())
        # fourth turn after the plate: the gate has closed
        w = play(World(["SP...G"]), "right", "right", "right", "right")
        self.assertNotIn("right", w.legal_actions())

    def test_waiting_on_plate_keeps_gate_open(self):
        w = play(World(["SP.G"]), "right", "wait", "wait", "wait", "wait")
        self.assertEqual(w.gate_turns, 3)

    def test_climbing_onto_plate_opens_gate(self):
        w = play(World(["P", "S"]), "climb")
        self.assertEqual(w.gate_turns, 3)


class RoomSolutionTest(unittest.TestCase):
    def test_room_a_declared_solution_wins_in_seven(self):
        w = play(World(ROOMS["A"]),
                 "right", "jump_right", "right", "right", "right", "right", "right")
        self.assertEqual(w.status, "won")


if __name__ == "__main__":
    unittest.main()
