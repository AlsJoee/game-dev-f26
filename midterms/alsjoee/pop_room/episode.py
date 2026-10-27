"""The machine-playable interface: what a playing agent may see and do.

Follows the shape of course_game/player_interface.py. The episode holds the
authoritative World; a player gets copies of observations and a list of
action strings, never the World itself.

Design choices: the observed map draws the start tile as floor and has no
marker for the Prince (his position is given separately), and the gate is
reported only as "open" or "closed", never with the turns it has left.
"""

from .rooms import ROOMS
from .world import World

PLAYER_ID = "prince"


class PopRoomEpisode:
    PLAYER_ID = PLAYER_ID

    def __init__(self, max_steps: int = 40):
        self.max_steps = max_steps
        self.reset()

    def reset(self, seed: int | None = None, room: str = "A") -> dict[str, object]:
        # The rooms have no randomness; the seed is kept so a trace can record it.
        if room not in ROOMS:
            raise ValueError(f"Unknown room {room!r}; choose from {sorted(ROOMS)}.")
        self.seed = seed
        self.room = room
        self._world = World(ROOMS[room])
        self.steps = 0
        self.invalid_actions = 0
        self.last_result = ""
        self.trace: list[dict[str, object]] = []
        return self.observe(PLAYER_ID)

    def observe(self, player_id: str) -> dict[str, object]:
        _check_player(player_id)
        world = self._world
        return {
            "map": [row.replace("S", ".") for row in world.grid],
            "prince": {"row": world.row, "col": world.col},
            "health": world.health,
            "gate": "open" if world.gate_open else "closed",
            "steps_used": self.steps,
            "steps_left": max(0, self.max_steps - self.steps),
            "last_result": self.last_result,
        }

    def legal_actions(self, player_id: str) -> list[str]:
        _check_player(player_id)
        if self.outcome()["status"] == "terminal":
            return []
        return self._world.legal_actions()

    def step(self, player_id: str, action: object) -> dict[str, object]:
        _check_player(player_id)
        if self.outcome()["status"] == "terminal":
            return {"accepted": False, "text": "The episode is over.", "observation": self.observe(player_id)}
        if not isinstance(action, str):
            # A malformed model reply is an invalid action, not a crash.
            action = f"<not text: {type(action).__name__}>"
        action = action.strip().lower()
        self.steps += 1
        # Ask the World, not self.legal_actions: counting this step may already
        # have reached the step limit, and the final step must still be playable.
        accepted = action in self._world.legal_actions()
        if accepted:
            text = self._world.act(action)
        else:
            # The World is untouched, so the gate timer does not tick.
            self.invalid_actions += 1
            text = "That action is not available now."
        self.last_result = text
        world = self._world
        self.trace.append({"step": self.steps, "action": action, "accepted": accepted, "text": text,
                           "row": world.row, "col": world.col, "health": world.health})
        return {"accepted": accepted, "text": text, "observation": self.observe(player_id)}

    def outcome(self) -> dict[str, object]:
        world = self._world
        if world.status == "won":
            status, reason, score = "terminal", "reached the exit", 1
        elif world.status == "dead":
            status, reason, score = "terminal", f"died: {world.death_reason}", 0
        elif self.steps >= self.max_steps:
            status, reason, score = "terminal", "step limit", 0
        else:
            status, reason, score = "ongoing", "", 0
        return {"status": status, "reason": reason, "score": score,
                "steps": self.steps, "invalid_actions": self.invalid_actions}


def _check_player(player_id: str) -> None:
    if player_id != PLAYER_ID:
        raise ValueError(f"Prince of Persia: One Room has one player, {PLAYER_ID!r}.")
