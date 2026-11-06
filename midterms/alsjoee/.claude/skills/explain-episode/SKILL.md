---
name: explain-episode
description: "Use when asked to explain, walk through or summarize one recorded episode from a trace file in traces/. Writes a short plain-English account to explanations/<trace-name>.md: the setup, the moves, the first mistake, the ending and the comparison with the BFS shortest solution."
---

# Explain one episode

Turns one trace into an explanation a person can read without opening the JSONL.
It reports what the trace shows and does not guess at what the model was thinking.

## When to use

Use it when someone asks what happened in a particular episode, or wants one
episode written up for a report or a recording.

Do not use it to compare many episodes (`results/summary.md` does that) or for a
trace in `traces/pre-fix/`. Those episodes played an earlier room B and earlier
rules, so the current game cannot reproduce them.

## Inputs

- **Trace:** one file directly in `traces/`, such as
  `traces/A-seed1-h0-gemini-3.5-flash-lite.jsonl`. If the request doesn't name
  one, ask which. Don't pick one yourself.

Run every command from `midterms/alsjoee/`.

## Steps

1. **Check the paths.** The trace must exist directly in `traces/`. The output is
   `explanations/<trace-name>.md`, where `<trace-name>` is the file name without
   `.jsonl`. If that output already exists, ask before replacing it.

2. **Get the facts.**

   ```sh
   python -B .claude/skills/explain-episode/episode_facts.py traces/<trace-name>.jsonl
   ```

   This replays the moves on the current game and writes nothing. If it prints
   `MISMATCH`, stop and report that message. The current game does not reproduce
   the trace, and an explanation written anyway could be wrong.

   Take positions, the first mistake and the BFS solution from this output. Don't
   work them out by hand. A trace holds the state before each move, so the position
   after the last move appears only here.

3. **Find the rule.** Match the first mistake to its rule number in the rule table
   in `README.md`.

4. **Check what the model was told.** Read the `prompt` field of the trace record
   for the mistake's step. Say whether it stated the rule involved. The facts line
   `fall-off rule in the prompt` answers this for the fall-off rule. Local-view
   prompts can also describe a fall in their "Next to you" line, so read that too.

5. **Write the explanation** in the format below. Keep these distinctions:
   - **What it did, not why.** Replies are normally one word and record no
     reasoning. Say what the move did and which rule made it a mistake. Never say
     why the model chose it.
   - **Fallbacks are not the model's moves.** A `fallback` row is a `wait` the game
     played after a failed call. Never call it a mistake or a choice.
   - **The hidden timer.** "To exit" counts the fewest moves left using the gate
     timer, which players can't see. It is a measure made afterwards, not something
     the model could have known. It also ignores the steps left in the episode.
   - **"Lost ground" is not always fatal.** That move cost time, and the episode may
     still have won. Later moves that lost ground are in the table but aren't the
     first mistake.

6. **Check it, then save.** Compare every number in your text with the facts output.
   Create `explanations/` if needed and write only the one output file.

7. **Report back.** Give the path. Mention that an uncommitted file in
   `explanations/` makes `evaluate` refuse to start until it is committed.

## Do not

- Change anything except the one output file. Everything else is read-only,
  including `traces/`, `results/`, `pop_room/`, `README.md` and `review.md`.
- Make a model call or run `model` or `evaluate`. An explanation costs no credits.
- Copy a whole prompt into the explanation. Quote only the line that matters.

## Output format

Use these sections in this order, and keep the prose to a few sentences each.

```markdown
# Episode: <trace-name>

## Setup
Room <room>, seed <seed>. Model <model>, <view> view, history <N>.
Recorded at commit <first 7 characters>.

## Moves
Positions are row, column, counting from 0.

| Step | Who | Action | Result | Position after |
|---|---|---|---|---|
| 1 | model | right | right | 0, 1 |

"Who" is model, invalid or fallback. Copy every row from the facts output.

## First mistake
Step <N>: <action>. <What happened, and the rule number that made it a mistake.>
<Whether the prompt stated that rule.>
Or: "None. Every model move brought the exit closer."

## How it ended
<Outcome and score, in words. Steps used, invalid moves and fallbacks.>

## Compared with BFS
BFS shortest solution: <N> moves: <actions>.
<This episode's steps against that number, or how far from the exit it stopped.
How many of the extra steps were fallback waits. BFS knows the rules by simulating
them, so this compares against the best possible route, not an equal player.>
```
