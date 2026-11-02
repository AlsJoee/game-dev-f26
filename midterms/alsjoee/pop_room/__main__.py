"""Command line: python -m pop_room play|baseline --room A [--seed N]."""

import argparse

from .baseline import BfsPlayer
from .episode import PLAYER_ID, PopRoomEpisode
from .rooms import ROOMS
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
        "  Spikes kill you.",
        f"  Stepping on the plate P opens the gate G for {GATE_OPEN_TURNS} turns; a closed gate blocks you.",
        f"  You have at most {max_steps} steps.",
    ])


def render(observation):
    """The observed map with "@" at the Prince's position."""
    row, col = observation["prince"]["row"], observation["prince"]["col"]
    lines = list(observation["map"])
    lines[row] = lines[row][:col] + "@" + lines[row][col + 1:]
    return "\n".join(lines)


def show(observation, legal):
    print()
    print(render(observation))
    print(LEGEND)
    print(f"health {observation['health']}  gate {observation['gate']}  "
          f"steps left {observation['steps_left']}")
    if observation["last_result"]:
        print(f"last: {observation['last_result']}")
    print("actions: " + ", ".join(legal))


def play(episode, room, seed):
    observation = episode.reset(seed=seed, room=room)
    print(intro(episode.max_steps))
    while episode.outcome()["status"] != "terminal":
        show(observation, episode.legal_actions(PLAYER_ID))
        try:
            action = input("> ")
        except EOFError:
            print()
            return
        result = episode.step(PLAYER_ID, action)
        observation = result["observation"]
        if not result["accepted"]:
            print(result["text"])
    print()
    print(render(observation))
    print(f"last: {observation['last_result']}")
    print_outcome(episode)


def baseline(episode, room, seed):
    observation = episode.reset(seed=seed, room=room)
    player = BfsPlayer()
    plan = player.plan(observation)
    print(f"room {room}: plan of {len(plan)} actions")
    while episode.outcome()["status"] != "terminal":
        action = player.choose(observation, episode.legal_actions(PLAYER_ID))
        result = episode.step(PLAYER_ID, action)
        observation = result["observation"]
        mark = " (fallback)" if player.trace[-1]["fallback"] else ""
        print(f"{episode.steps:2d}. {action}{mark}: {result['text']}")
    print_outcome(episode)


def print_outcome(episode):
    outcome = episode.outcome()
    print(f"outcome: {outcome['reason']}  score {outcome['score']}  "
          f"steps {outcome['steps']}  invalid {outcome['invalid_actions']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m pop_room")
    parser.add_argument("command", choices=["play", "baseline"])
    parser.add_argument("--room", default="A", choices=sorted(ROOMS))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)
    episode = PopRoomEpisode()
    if args.command == "play":
        play(episode, args.room, args.seed)
    else:
        baseline(episode, args.room, args.seed)


if __name__ == "__main__":
    main()
