"""Evaluation runner: BFS baseline and Gemini player over rooms, seeds and history sizes.

Every row records the git commit it ran on. A run on a tree with uncommitted
code changes is refused unless allow_dirty is set, and then its commit is
marked "-dirty". The run's own outputs (traces/ and results/) do not count
as uncommitted changes.

Costs are estimates from prices.json. A price that has not been filled in
gives "unknown", never zero.
"""

import csv
from datetime import date as Date
import json
from pathlib import Path
import re
import subprocess

from .baseline import BfsPlayer
from .episode import PLAYER_ID, PopRoomEpisode
from . import model_player as mp

ROOT = Path(__file__).resolve().parent.parent
TRACES = ROOT / "traces"
RESULTS = ROOT / "results"
PRICES = ROOT / "prices.json"
OUTPUT_DIRS = ("traces/", "results/")
UNKNOWN = "unknown"

COLUMNS = ["date", "git_commit", "player", "model", "view", "history", "room", "seed", "outcome",
           "score", "steps", "invalid_actions", "fallbacks", "model_calls", "input_tokens",
           "output_tokens", "thinking_tokens", "total_latency_s", "est_cost_usd"]
# Columns added after results were first recorded, with the value earlier rows get.
# Every earlier model row used the map view, and those models reported no thinking.
ADDED_COLUMNS = {"view": lambda row: "map" if row["player"] == "model" else "",
                 "thinking_tokens": lambda row: "0"}


class DirtyTreeError(RuntimeError):
    """The working tree has uncommitted changes, so results would not match a commit."""


# --- git -------------------------------------------------------------------

def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def git_state():
    """(HEAD commit, True if there are uncommitted changes outside traces/ and results/)."""
    try:
        sha = _git("rev-parse", "HEAD").strip()
        prefix = _git("rev-parse", "--show-prefix").strip()  # e.g. "midterms/alsjoee/"
        status = _git("status", "--porcelain").splitlines()
    except (OSError, subprocess.CalledProcessError):
        return UNKNOWN, True
    outputs = tuple(prefix + d for d in OUTPUT_DIRS)
    changed = [line[3:] for line in status if not line[3:].strip('"').startswith(outputs)]
    return sha, bool(changed)


def commit_label(sha, dirty):
    return sha + ("-dirty" if dirty else "")


def require_clean(sha, dirty, allow_dirty):
    """The commit label to record, or DirtyTreeError if dirty and not allowed."""
    if dirty and not allow_dirty:
        raise DirtyTreeError("The working tree has uncommitted changes. Commit them so every "
                             "result points to an exact commit, or pass --allow-dirty for a quick test.")
    return commit_label(sha, dirty)


# --- traces ----------------------------------------------------------------

def trace_path(room, seed, history, model, traces_dir=None, view="map"):
    # Map-view names are unchanged from before the view option, so old traces keep their names.
    safe_model = re.sub(r"[^A-Za-z0-9._-]", "_", model)
    view_part = "" if view == "map" else f"-{view}"
    return Path(traces_dir or TRACES) / f"{room}-seed{seed}-h{history}{view_part}-{safe_model}.jsonl"


def write_trace(path, records, summary):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as out:
        for line in (*records, summary):
            out.write(json.dumps(line) + "\n")


# --- prices ----------------------------------------------------------------

def load_prices(path=PRICES):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return {}


def price_for(prices, model):
    """(input, output) USD per 1M tokens, or None if not filled in."""
    entry = prices.get(model) or {}
    rates = (entry.get("input_usd_per_1m"), entry.get("output_usd_per_1m"))
    if all(isinstance(r, (int, float)) and not isinstance(r, bool) for r in rates):
        return rates
    return None


def price_source(prices, model):
    entry = prices.get(model) or {}
    if price_for(prices, model) is None:
        return f"no price filled in for {model} in prices.json; costs are unknown"
    return f"{entry.get('source', 'source not given')} (checked {entry.get('checked') or 'date not given'})"


def est_cost(input_tokens, output_tokens, price):
    if price is None or input_tokens is None or output_tokens is None:
        return UNKNOWN
    return round((input_tokens * price[0] + output_tokens * price[1]) / 1_000_000, 6)


# --- episodes --------------------------------------------------------------

def bfs_row(room, seed, *, today, commit):
    episode = PopRoomEpisode()
    observation = episode.reset(seed=seed, room=room)
    player = BfsPlayer()
    player.plan(observation)
    while episode.outcome()["status"] != "terminal":
        action = player.choose(observation, episode.legal_actions(PLAYER_ID))
        observation = episode.step(PLAYER_ID, action)["observation"]
    outcome = episode.outcome()
    return {"date": today, "git_commit": commit, "player": "bfs", "model": "", "view": "", "history": "",
            "room": room, "seed": seed, "outcome": outcome["reason"], "score": outcome["score"],
            "steps": outcome["steps"], "invalid_actions": outcome["invalid_actions"],
            "fallbacks": sum(t["fallback"] for t in player.trace), "model_calls": 0,
            "input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "total_latency_s": 0.0, "est_cost_usd": 0.0}


def model_row(summary, *, today, price):
    return {"date": today, "git_commit": summary["git_commit"], "player": "model",
            "model": summary["model"], "view": summary["view"], "history": summary["history"], "room": summary["room"],
            "seed": summary["seed"], "outcome": summary["outcome"], "score": summary["score"],
            "steps": summary["steps"], "invalid_actions": summary["invalid_actions"],
            "fallbacks": summary["fallbacks"], "model_calls": summary["model_calls"],
            "input_tokens": summary["input_tokens"], "output_tokens": summary["output_tokens"],
            "thinking_tokens": summary["thinking_tokens"],
            "total_latency_s": summary["total_latency_s"],
            "est_cost_usd": est_cost(summary["input_tokens"], summary["output_tokens"], price)}


def planned_traces(rooms, trials, histories, model, traces_dir=None, view="map"):
    return [trace_path(room, seed, h, model, traces_dir, view)
            for room in rooms for seed in range(1, trials + 1) for h in histories]


def run_evaluation(rooms, trials, histories, client, *, model, commit, prices, today=None,
                   max_model_calls=mp.MAX_MODEL_CALLS, traces_dir=None, view="map", on_row=None):
    """Play every episode and write model traces. Returns the result rows."""
    today = today or Date.today().isoformat()
    existing = [p for p in planned_traces(rooms, trials, histories, model, traces_dir, view)
                if p.exists()]
    if existing:
        # Checked before any call, so no credits are spent on a run that cannot be saved.
        raise FileExistsError("Traces already exist; move them first: "
                              + ", ".join(str(p) for p in existing))
    price = price_for(prices, model)
    rows = []
    for room in rooms:
        for seed in range(1, trials + 1):
            episodes = [("bfs", None)] + [("model", h) for h in histories]
            for player_kind, history in episodes:
                if player_kind == "bfs":
                    row = bfs_row(room, seed, today=today, commit=commit)
                else:
                    episode = PopRoomEpisode()
                    player = mp.ModelPlayer(client, history=history, max_model_calls=max_model_calls,
                                            max_steps=episode.max_steps, seed=seed, view=view)
                    records, outcome = mp.run_episode(episode, player, room, seed)
                    summary = mp.summarize(records, outcome, player, model=model, room=room,
                                           seed=seed, git_commit=commit)
                    write_trace(trace_path(room, seed, history, model, traces_dir, view),
                                records, summary)
                    row = model_row(summary, today=today, price=price)
                rows.append(row)
                if on_row:
                    on_row(row)
    return rows


# --- results ---------------------------------------------------------------

def append_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size:
        with path.open(newline="") as f:
            header = next(csv.reader(f), None)
        if header != COLUMNS and _is_earlier_header(header):
            _add_columns(path)
        elif header != COLUMNS:
            raise ValueError(f"{path} has different columns; move it before appending.")
        new = False
    else:
        new = True
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            writer.writeheader()
        writer.writerows(rows)


def _is_earlier_header(header):
    """True if header is COLUMNS with some ADDED_COLUMNS left out."""
    return header == [c for c in COLUMNS if c in header] and set(COLUMNS) - set(header) <= set(ADDED_COLUMNS)


def _add_columns(path):
    """Upgrade a results file written before some ADDED_COLUMNS existed."""
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for column, value in ADDED_COLUMNS.items():
            if column not in row:
                row[column] = value(row)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _group_key(row):
    history = row["history"]
    return (0 if row["player"] == "bfs" else 1, row["view"],
            -1 if history == "" else int(history), row["room"])


def summary_markdown(rows, *, today, model, commit, source):
    groups = {}
    for row in rows:
        groups.setdefault(_group_key(row), []).append(row)
    lines = [
        "# Evaluation summary",
        "",
        f"- Date: {today}",
        f"- Model: {model}",
        f"- Commit: {commit}",
        f"- Price source: {source}",
        f"- Episodes: {len(rows)}",
        "",
        "Costs are estimates from prices.json, not billed amounts.",
        "",
        "| Player | View | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks "
        "| Mean latency (s) | Total tokens | Est. cost (USD) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for key in sorted(groups):
        group = groups[key]
        n = len(group)
        costs = [r["est_cost_usd"] for r in group]
        cost = UNKNOWN if UNKNOWN in costs else f"{sum(costs):.6f}"
        first = group[0]
        lines.append(
            f"| {first['player']} | {first['view'] or '-'} "
            f"| {first['history'] if first['history'] != '' else '-'} "
            f"| {first['room']} | {sum(r['score'] for r in group)}/{n} "
            f"| {sum(r['steps'] for r in group) / n:.1f} "
            f"| {sum(r['invalid_actions'] for r in group)} | {sum(r['fallbacks'] for r in group)} "
            f"| {sum(r['total_latency_s'] for r in group) / n:.2f} "
            f"| {sum(r['input_tokens'] + r['output_tokens'] for r in group)} | {cost} |")
    return "\n".join(lines) + "\n"
