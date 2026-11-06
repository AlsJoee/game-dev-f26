"""Player-facing rules text, shared by human play and the model prompt."""

from .world import GATE_OPEN_TURNS, START_HEALTH

LEGEND = "@ you  E exit  . floor  (space) gap  ^ spikes  P plate  G gate  # wall"


def intro(max_steps):
    return "\n".join([
        "Prince of Persia: One Room",
        "Goal: reach the exit E.",
        "",
        "Map legend:",
        "  @  you (the Prince)",
        "  E  exit",
        "  .  floor",
        "     (space) gap: walking or jumping onto it makes you fall",
        "  ^  spikes",
        "  P  pressure plate",
        "  G  gate",
        "  #  wall",
        "",
        "Rules:",
        "  Each turn you take one of the listed actions.",
        "  left / right walk one tile.",
        "  jump_left / jump_right clear a 1-tile gap and land two tiles away.",
        "  climb goes up one floor onto the tile directly above.",
        "  Falling 1 floor is safe.",
        f"  Falling 2 floors costs 1 health (you start with {START_HEALTH}).",
        "  Falling 3 or more floors kills you.",
        "  Falling off the bottom of the room kills you.",
        "  Spikes kill you.",
        f"  Stepping on the plate P opens the gate G for {GATE_OPEN_TURNS} turns; a closed gate blocks you.",
        f"  You have at most {max_steps} steps.",
    ])


def render(observation):
    """The observed map with "@" at the Prince's position, if he is still on the map."""
    row, col = observation["prince"]["row"], observation["prince"]["col"]
    lines = list(observation["map"])
    if row < len(lines):  # after a fall off the bottom, row is one past the last line
        lines[row] = lines[row][:col] + "@" + lines[row][col + 1:]
    return "\n".join(lines)
