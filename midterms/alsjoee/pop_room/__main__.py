"""Command line, run from midterms/alsjoee/:

    python -m pop_room play --room A
    python -m pop_room baseline --room A [--seed N]
    python -m pop_room model --room A --seed N [--history H]
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from .baseline import BfsPlayer
from .episode import PLAYER_ID, PopRoomEpisode
from . import model_player as mp
from .rooms import ROOMS
from .rules_text import LEGEND, intro, render

TRACES = Path(__file__).resolve().parent.parent / "traces"


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


def git_commit():
    """HEAD commit, with "-dirty" if the working tree has uncommitted changes."""
    here = Path(__file__).resolve().parent
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=here, capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=here, capture_output=True,
                               text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return sha + ("-dirty" if dirty else "")


def model(episode, room, seed, history, max_model_calls):
    try:
        settings = mp.vertex_settings()
    except mp.ModelConfigError as error:
        sys.exit(str(error))
    safe_model = re.sub(r"[^A-Za-z0-9._-]", "_", settings["model"])
    path = TRACES / f"{room}-seed{seed}-h{history}-{safe_model}.jsonl"
    if path.exists():
        # Checked before any call, so no credits are spent on a run that cannot be saved.
        sys.exit(f"{path} already exists; move it or use another seed.")
    commit = git_commit()
    client = mp.VertexClient(settings["project"], settings["location"], settings["model"])
    player = mp.ModelPlayer(client, history=history, max_model_calls=max_model_calls,
                            max_steps=episode.max_steps, seed=seed)
    print(f"room {room}  seed {seed}  history {history}  model {settings['model']} (live Vertex AI call)")

    def show_step(record):
        if record["fallback"]:
            move = f"wait (fallback: {record['error']})"
        elif record["parsed_action"] is None:
            move = f"invalid reply {record['raw_reply']!r}"
        else:
            move = record["action"]
        print(f"{record['step']:2d}. {move}: {record['result']}  [{record['latency_s']:.2f} s]")

    records, outcome = mp.run_episode(episode, player, room, seed, on_step=show_step)
    summary = mp.summarize(records, outcome, player, model=settings["model"], room=room,
                           seed=seed, git_commit=commit)
    TRACES.mkdir(exist_ok=True)
    with path.open("w") as out:
        for line in (*records, summary):
            out.write(json.dumps(line) + "\n")
    print(f"outcome: {summary['outcome']}  score {summary['score']}  steps {summary['steps']}  "
          f"invalid {summary['invalid_actions']}  fallbacks {summary['fallbacks']}  "
          f"model calls {summary['model_calls']}  tokens {summary['total_tokens']}  "
          f"latency {summary['total_latency_s']} s")
    print(f"trace: {path}")


def print_outcome(episode):
    outcome = episode.outcome()
    print(f"outcome: {outcome['reason']}  score {outcome['score']}  "
          f"steps {outcome['steps']}  invalid {outcome['invalid_actions']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m pop_room")
    parser.add_argument("command", choices=["play", "baseline", "model"])
    parser.add_argument("--room", default="A", choices=sorted(ROOMS))
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--history", type=int, default=0, help="model: last N moves shown (default 0)")
    parser.add_argument("--max-model-calls", type=int, default=mp.MAX_MODEL_CALLS)
    args = parser.parse_args(argv)
    if args.command == "model" and args.seed is None:
        parser.error("model needs --seed so the trace can be named and repeated")
    if args.history < 0:
        parser.error("--history must be 0 or more")
    episode = PopRoomEpisode()
    if args.command == "play":
        play(episode, args.room, args.seed)
    elif args.command == "baseline":
        baseline(episode, args.room, args.seed)
    else:
        model(episode, args.room, args.seed, args.history, args.max_model_calls)


if __name__ == "__main__":
    main()
