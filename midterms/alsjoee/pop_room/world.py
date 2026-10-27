"""Authoritative state and rules for Prince of Persia: One Room.

The World owns all state. Callers ask for legal_actions() and pass one of
them to act(); act() refuses anything that is not currently legal.
"""

START, EXIT, FLOOR, EMPTY = "S", "E", ".", " "
SPIKES, PLATE, GATE, WALL = "^", "P", "G", "#"

ACTIONS = ("left", "right", "jump_left", "jump_right", "climb", "wait")
START_HEALTH = 2
GATE_OPEN_TURNS = 3


class World:
    def __init__(self, layout):
        if not layout or len({len(row) for row in layout}) != 1:
            raise ValueError("layout must be a non-empty list of equal-length rows")
        starts = [(r, c) for r, row in enumerate(layout)
                  for c, tile in enumerate(row) if tile == START]
        if len(starts) != 1:
            raise ValueError("layout must contain exactly one start tile")

        self.grid = tuple(layout)
        self.height = len(layout)
        self.width = len(layout[0])
        self.row, self.col = starts[0]
        self.health = START_HEALTH
        self.gate_turns = 0
        self.status = "playing"
        self.death_reason = None

    # --- queries -----------------------------------------------------------

    def tile(self, row, col):
        """Tile at (row, col), or None if off the grid."""
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col]
        return None

    @property
    def gate_open(self):
        return self.gate_turns > 0

    def _blocked(self, tile):
        """True if a horizontal move cannot end on this tile."""
        return tile is None or tile == WALL or (tile == GATE and not self.gate_open)

    def is_legal(self, action):
        if self.status != "playing" or action not in ACTIONS:
            return False
        r, c = self.row, self.col
        if action == "wait":
            return True
        if action in ("left", "right"):
            step = -1 if action == "left" else 1
            return not self._blocked(self.tile(r, c + step))
        if action in ("jump_left", "jump_right"):
            step = -1 if action == "jump_left" else 1
            return (self.tile(r, c + step) == EMPTY
                    and not self._blocked(self.tile(r, c + 2 * step)))
        # climb
        above = self.tile(r - 1, c)
        return above in (FLOOR, START, PLATE, EXIT) or (above == GATE and self.gate_open)

    def legal_actions(self):
        return [a for a in ACTIONS if self.is_legal(a)]

    def to_dict(self):
        return {
            "row": self.row,
            "col": self.col,
            "health": self.health,
            "gate_turns": self.gate_turns,
            "status": self.status,
            "death_reason": self.death_reason,
        }

    # --- transitions -------------------------------------------------------

    def act(self, action):
        """Apply one legal action and return a short description."""
        if not self.is_legal(action):
            raise ValueError(f"illegal action: {action!r}")

        r, c = self.row, self.col
        if action in ("left", "right"):
            c += -1 if action == "left" else 1
        elif action in ("jump_left", "jump_right"):
            c += -2 if action == "jump_left" else 2
        elif action == "climb":
            r -= 1
        self.row, self.col = r, c

        parts = [action]
        self._resolve(parts)

        # The turn is over: tick the gate down, then a plate under the
        # Prince (re)opens it for the next GATE_OPEN_TURNS turns.
        self.gate_turns = max(0, self.gate_turns - 1)
        if self.status == "playing" and self.tile(self.row, self.col) == PLATE:
            self.gate_turns = GATE_OPEN_TURNS
            parts.append("the gate opens")
        return "; ".join(parts)

    def _resolve(self, parts):
        """Apply falling and the effect of the tile the Prince is on."""
        fallen = 0
        while self.tile(self.row, self.col) == EMPTY:
            self.row += 1
            fallen += 1
        if self.tile(self.row, self.col) is None:
            return self._die("fell off the bottom", parts)
        if fallen:
            parts.append(f"fell {fallen} floor{'s' if fallen > 1 else ''}")
        if fallen >= 3:
            return self._die("fell 3 or more floors", parts)
        if fallen == 2:
            self.health -= 1
            parts.append(f"health {self.health}")
            if self.health <= 0:
                return self._die("health reached 0", parts)

        tile = self.tile(self.row, self.col)
        if tile == SPIKES:
            return self._die("spikes", parts)
        if tile == EXIT:
            self.status = "won"
            parts.append("reached the exit")

    def _die(self, reason, parts):
        self.status = "dead"
        self.death_reason = reason
        parts.append(f"died: {reason}")
