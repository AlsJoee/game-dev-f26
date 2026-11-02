"""BFS baseline player for Prince of Persia: One Room.

The player plans once from the observation at reset. It builds its own
World from the observed map as a model of the public rules; it never sees
the live episode's World. The observation reports the gate only as open or
closed, so the plan assumes the reset state: gate closed (0 turns left).
"""

from collections import deque

from .world import START, World

MAX_DEPTH = 40


def _model(grid, row, col, health, gate_turns):
    """A private World in the given state, built only from observed facts."""
    # World needs one start tile; the observed map draws it as floor.
    layout = list(grid)
    layout[row] = layout[row][:col] + START + layout[row][col + 1:]
    world = World(layout)
    world.health = health
    world.gate_turns = gate_turns
    return world


def shortest_plan(observation, max_depth=MAX_DEPTH):
    """Shortest list of actions that wins from the observation, or None."""
    if observation["gate"] != "closed":
        raise ValueError("BFS plans from the reset observation, where the gate is closed.")
    grid = observation["map"]
    start = (observation["prince"]["row"], observation["prince"]["col"],
             observation["health"], 0)
    frontier = deque([(start, [])])
    seen = {start}
    while frontier:
        state, path = frontier.popleft()
        if len(path) >= max_depth:
            continue
        for action in _model(grid, *state).legal_actions():
            world = _model(grid, *state)
            world.act(action)
            if world.status == "dead":
                continue
            if world.status == "won":
                return path + [action]
            nxt = (world.row, world.col, world.health, world.gate_turns)
            if nxt not in seen:
                seen.add(nxt)
                frontier.append((nxt, path + [action]))
    return None


class BfsPlayer:
    def __init__(self):
        self.plan_actions = []
        self.trace = []

    def plan(self, observation):
        self.plan_actions = shortest_plan(observation) or []
        self.trace = []
        return list(self.plan_actions)

    def choose(self, observation, legal_actions):
        if self.plan_actions and self.plan_actions[0] in legal_actions:
            action, fallback = self.plan_actions.pop(0), False
        else:
            action, fallback = "wait", True
        self.trace.append({"step": observation["steps_used"] + 1,
                           "action": action, "fallback": fallback})
        return action
