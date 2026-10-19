# Get Out experiment: yvnvii

Principle: entry

## Decisions

After watching a classmate, I chose to show the player's move count next to
both the fewest possible moves for the board and the fewest moves left from
the current position. Both counts come from `engine.solve`: the board target
is computed when a board loads, and the remaining count is recomputed during
play. On completion, the game says whether the player matched the board
target. This tests Schell #1 (make the goal easy to understand) and #4 (sense
of solvability). The remaining count also acts as a progress or hot/cold
signal, testing #3: a lower shortest-path count means the current position is
closer in moves to a solution, though it does not show which move to make.
Boards, rules, and hints are unchanged.

## Possible outcomes

**Prediction:** Players who finish above the fewest-moves count will undo or
reset and try to match it.

**Alternative:** Players may accept their first solution, or may not notice or
care about the comparison. That would suggest the count is not a useful prompt
for replay, or that its presentation needs to be clearer. If players do replay
but cannot reduce their count, the number may create pressure without helping
them find a better route. Players may also treat the fewest-left number as a
guaranteed monotonic progress bar; changes in that number would show whether
the signal helps them judge moves or confuses them.

## Playtest

**Prior reference-game observation (student report):** A classmate tried to
solve each puzzle in as few moves as possible but had no way to know whether
they had found an optimal solution.

**Variation playtest observation:** TODO — test the variation with an anonymous
player. Record whether they notice each count, how the fewest-left count changes
after moves, completion count, undo/reset behavior, hints, and a revealing
action or remark. Do not treat predicted behavior as an observed result.

**Plan:** Ask a player to solve a board while thinking aloud if comfortable.
Watch whether they notice the move counts, whether they undo or reset after a
non-optimal completion, whether they use the fewest-left signal to compare
candidate moves, and whether they can explain what the counts mean. Ask what
they were trying to do and what changed their understanding.

## Next decision

TODO — decide whether to keep or revise the comparison after observing a
player. If players replay and improve, test whether the board target helped
them choose another route. If players use the fewest-left signal to assess
moves, keep it and test with another board. If they ignore it, find it
distracting, or read it as a monotonic progress bar, revise its label or
explanation and test again. A small number of playtests is exploratory.

## Implementation and checks

The variation updates the move-count display and completion announcement in
`app.js` and `index.html`, with counter layout styling in `style.css`. It uses
the existing solver for both counts; it does not change the solver, boards,
movement rules, or hint behavior.
`python3 scripts/minigames.py check --owner yvnvii` passed; `python3
scripts/minigames.py test --owner yvnvii` passed all 7 tests; `node --check` and
`git diff --cached --check` passed. Browser interaction and narrow-screen checks
remain to be done manually.

## AI assistance and human decisions

Codex implemented the requested displays and comparison. I chose the design
principles and prediction. TODO — after reviewing and playtesting, record what
I kept or changed and any remaining issue.

## Independent review

TODO — record the review and any follow-up checks.
