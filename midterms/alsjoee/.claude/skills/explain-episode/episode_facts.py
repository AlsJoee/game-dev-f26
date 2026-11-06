"""Print the facts about one recorded episode, for the explain-episode skill.

Replays the trace's moves on the current game code. A trace holds the state
before each move, so the replay supplies the position after the last one, and
the check against the trace shows whether the current code still matches it.
Writes nothing. A development tool: no player ever sees this.

    python -B .claude/skills/explain-episode/episode_facts.py traces/<name>.jsonl
"""

from collections import deque
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from pop_room.baseline import shortest_plan  # noqa: E402
from pop_room.episode import PLAYER_ID, PopRoomEpisode  # noqa: E402

NO_ROUTE = "none"


def moves_to_win(world):
    """Fewest moves to the exit from this exact state (hidden gate timer included), or None."""
    if world.status == "won":
        return 0
    if world.status != "playing":
        return None
    key = lambda w: (w.row, w.col, w.health, w.gate_turns)
    frontier = deque([(world, 0)])
    seen = {key(world)}
    while frontier:
        current, depth = frontier.popleft()
        for action in current.legal_actions():
            after = copy.deepcopy(current)
            after.act(action)
            if after.status == "won":
                return depth + 1
            if after.status == "playing" and key(after) not in seen:
                seen.add(key(after))
                frontier.append((after, depth + 1))
    return None


def mistake_kind(source, status, before, after):
    """Why this move counts as the first mistake, or None. Fallbacks are not the model's moves."""
    if source == "fallback":
        return None
    if source == "invalid":
        return "invalid move"
    if status == "dead":
        return "fatal: the move killed the Prince"
    if after is None:
        return "fatal: no route to the exit remained"
    if before is not None and after >= before:
        return "lost ground: the exit got no closer"
    return None


def main(path):
    lines = [json.loads(line) for line in Path(path).read_text().splitlines()]
    records = [line for line in lines if line["type"] == "step"]
    summary = next(line for line in lines if line["type"] == "summary")
    room = summary["room"]

    episode = PopRoomEpisode()
    start = episode.reset(seed=summary["seed"], room=room)
    plan = shortest_plan(start)
    print(f"trace: {Path(path).stem}")
    print(f"room {room}  seed {summary['seed']}  model {summary['model']}  "
          f"view {summary.get('view', 'map')}  history {summary['history']}  commit {summary['git_commit']}")
    print(f"outcome: {summary['outcome']}  score {summary['score']}  steps {summary['steps']}  "
          f"invalid {summary['invalid_actions']}  fallbacks {summary['fallbacks']}")
    print(f"bfs shortest: {len(plan)} moves: {', '.join(plan)}")
    print(f"fall-off rule in the prompt: {'Falling off the bottom' in records[0]['prompt']}")
    print("positions are row, col, counting from 0; 'to exit' uses the hidden gate timer")
    print("step | source | action | result | position after | health | gate | to exit")

    before = moves_to_win(episode._world)
    first = None
    for record in records:
        if episode.observe(PLAYER_ID) != record["observation"]:
            sys.exit(f"MISMATCH before step {record['step']}: the current game does not "
                     f"reproduce this trace, so it cannot be explained from this code.")
        result = episode.step(PLAYER_ID, record["action"])
        if result["text"] != record["result"]:
            sys.exit(f"MISMATCH at step {record['step']}: the trace says {record['result']!r}, "
                     f"the current game says {result['text']!r}.")
        world = episode._world
        source = ("fallback" if record["fallback"] else "model" if record["accepted"] else "invalid")
        after = moves_to_win(world)
        position = f"{world.row}, {world.col}" if world.tile(world.row, world.col) else "off the map"
        action = record["action"] if record["accepted"] else repr(record["action"])[:40]
        print(f"{record['step']} | {source} | {action} | {result['text']} | {position} | {world.health} | "
              f"{'open' if world.gate_open else 'closed'} | {NO_ROUTE if after is None else after}")
        kind = mistake_kind(source, world.status, before, after)
        if first is None and kind:
            first = f"step {record['step']}: {kind} ({NO_ROUTE if before is None else before} moves "
            first += f"to the exit before, {NO_ROUTE if after is None else after} after)"
        before = after
    print(f"first mistake: {first or 'none'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
