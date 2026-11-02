import unittest

from pop_room.baseline import BfsPlayer
from pop_room.episode import PLAYER_ID, PopRoomEpisode

P = PLAYER_ID
SHORTEST = {"A": 7, "B": 10, "C": 8, "H": 10}


class BfsPlanTest(unittest.TestCase):
    def test_plan_lengths_match_declared_shortest_solutions(self):
        for room, length in SHORTEST.items():
            with self.subTest(room=room):
                obs = PopRoomEpisode().reset(room=room)
                self.assertEqual(len(BfsPlayer().plan(obs)), length)

    def test_baseline_wins_each_room(self):
        for room, length in SHORTEST.items():
            with self.subTest(room=room):
                ep = PopRoomEpisode()
                obs = ep.reset(seed=0, room=room)
                player = BfsPlayer()
                player.plan(obs)
                while ep.outcome()["status"] != "terminal":
                    action = player.choose(obs, ep.legal_actions(P))
                    obs = ep.step(P, action)["observation"]
                outcome = ep.outcome()
                self.assertEqual((outcome["reason"], outcome["score"]), ("reached the exit", 1))
                self.assertEqual((outcome["steps"], outcome["invalid_actions"]), (length, 0))
                self.assertFalse(any(t["fallback"] for t in player.trace))

    def test_empty_plan_falls_back_to_wait(self):
        player = BfsPlayer()
        obs = PopRoomEpisode().reset(room="A")
        self.assertEqual(player.choose(obs, ["right", "wait"]), "wait")
        self.assertEqual(player.trace, [{"step": 1, "action": "wait", "fallback": True}])

    def test_illegal_planned_action_falls_back_to_wait(self):
        player = BfsPlayer()
        obs = PopRoomEpisode().reset(room="A")
        player.plan(obs)
        self.assertEqual(player.choose(obs, ["wait"]), "wait")
        self.assertTrue(player.trace[-1]["fallback"])


if __name__ == "__main__":
    unittest.main()
