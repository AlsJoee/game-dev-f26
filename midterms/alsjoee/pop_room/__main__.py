"""Command line, run from midterms/alsjoee/:

    python -m pop_room play --room A
    python -m pop_room baseline --room A [--seed N]
    python -m pop_room model --room A --seed N [--history H] [--view map|local]
    python -m pop_room evaluate --rooms A B C --trials 2 --history 0 5 [--view map|local] [--allow-dirty]
"""

import argparse
import sys

from .baseline import BfsPlayer
from .episode import PLAYER_ID, PopRoomEpisode
from . import evaluate as ev
from . import model_player as mp
from .rooms import ROOMS
from .rules_text import LEGEND, intro, render


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


def model(episode, room, seed, history, max_model_calls, view):
    try:
        settings = mp.vertex_settings()
    except mp.ModelConfigError as error:
        sys.exit(str(error))
    path = ev.trace_path(room, seed, history, settings["model"], view=view)
    if path.exists():
        # Checked before any call, so no credits are spent on a run that cannot be saved.
        sys.exit(f"{path} already exists; move it or use another seed.")
    commit = ev.commit_label(*ev.git_state())
    client = mp.VertexClient(settings["project"], settings["location"], settings["model"])
    player = mp.ModelPlayer(client, history=history, max_model_calls=max_model_calls,
                            max_steps=episode.max_steps, seed=seed, view=view)
    print(f"room {room}  seed {seed}  history {history}  view {view}  model {settings['model']} (live Vertex AI call)")

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
    ev.write_trace(path, records, summary)
    print(f"outcome: {summary['outcome']}  score {summary['score']}  steps {summary['steps']}  "
          f"invalid {summary['invalid_actions']}  fallbacks {summary['fallbacks']}  "
          f"model calls {summary['model_calls']}  tokens {summary['total_tokens']}  "
          f"latency {summary['total_latency_s']} s")
    print(f"trace: {path}")


def evaluate(rooms, trials, histories, max_model_calls, allow_dirty, view):
    try:
        settings = mp.vertex_settings()
        commit = ev.require_clean(*ev.git_state(), allow_dirty)
    except (mp.ModelConfigError, ev.DirtyTreeError) as error:
        sys.exit(str(error))
    model_id = settings["model"]
    prices = ev.load_prices()
    episodes = len(rooms) * trials * (1 + len(histories))
    print(f"rooms {' '.join(rooms)}  trials {trials}  history {' '.join(map(str, histories))}  view {view}  "
          f"model {model_id}  commit {commit}")
    print(f"{episodes} episodes, {len(rooms) * trials * len(histories)} with live Vertex AI calls")
    client = mp.VertexClient(settings["project"], settings["location"], model_id)

    def show_row(row):
        who = "bfs" if row["player"] == "bfs" else f"model h{row['history']} {row['view']}"
        print(f"{row['room']} seed {row['seed']} {who:15}: {row['outcome']}  steps {row['steps']}  "
              f"invalid {row['invalid_actions']}  fallbacks {row['fallbacks']}  "
              f"cost {row['est_cost_usd']}")

    try:
        rows = ev.run_evaluation(rooms, trials, histories, client, model=model_id, commit=commit,
                                 prices=prices, max_model_calls=max_model_calls, view=view,
                                 on_row=show_row)
    except FileExistsError as error:
        sys.exit(str(error))
    ev.append_csv(ev.RESULTS / "results.csv", rows)
    summary = ev.summary_markdown(ev.read_rows(ev.RESULTS / "results.csv"), today=rows[0]["date"],
                                  prices=prices)
    (ev.RESULTS / "summary.md").write_text(summary)
    print(f"results: {ev.RESULTS / 'results.csv'} (appended {len(rows)} rows)")
    print(f"summary: {ev.RESULTS / 'summary.md'}")


def print_outcome(episode):
    outcome = episode.outcome()
    print(f"outcome: {outcome['reason']}  score {outcome['score']}  "
          f"steps {outcome['steps']}  invalid {outcome['invalid_actions']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m pop_room")
    commands = parser.add_subparsers(dest="command", required=True)
    rooms = sorted(ROOMS)
    for name in ("play", "baseline", "model"):
        sub = commands.add_parser(name)
        sub.add_argument("--room", default="A", choices=rooms)
        sub.add_argument("--seed", type=int, default=None)
        if name == "model":
            sub.add_argument("--history", type=int, default=0, help="last N moves shown (default 0)")
            sub.add_argument("--max-model-calls", type=int, default=mp.MAX_MODEL_CALLS)
            sub.add_argument("--view", choices=mp.VIEWS, default="map",
                             help="local adds a line naming the tiles next to the Prince (default map)")
    sub = commands.add_parser("evaluate")
    sub.add_argument("--rooms", nargs="+", default=["A", "B", "C"], choices=rooms)
    sub.add_argument("--trials", type=int, default=2, help="seeds 1..N (default 2)")
    sub.add_argument("--history", nargs="+", type=int, default=[0], help="one or more history sizes")
    sub.add_argument("--max-model-calls", type=int, default=mp.MAX_MODEL_CALLS)
    sub.add_argument("--view", choices=mp.VIEWS, default="map",
                     help="local adds a line naming the tiles next to the Prince (default map)")
    sub.add_argument("--allow-dirty", action="store_true",
                     help="run with uncommitted changes; rows are marked -dirty")
    args = parser.parse_args(argv)

    histories = args.history if args.command == "evaluate" else [getattr(args, "history", 0)]
    if any(h < 0 for h in histories):
        parser.error("--history must be 0 or more")
    episode = PopRoomEpisode()
    if args.command == "play":
        play(episode, args.room, args.seed)
    elif args.command == "baseline":
        baseline(episode, args.room, args.seed)
    elif args.command == "model":
        if args.seed is None:
            parser.error("model needs --seed so the trace can be named and repeated")
        model(episode, args.room, args.seed, args.history, args.max_model_calls, args.view)
    else:
        if args.trials < 1:
            parser.error("--trials must be 1 or more")
        evaluate(args.rooms, args.trials, list(dict.fromkeys(histories)), args.max_model_calls,
                 args.allow_dirty, args.view)


if __name__ == "__main__":
    main()
