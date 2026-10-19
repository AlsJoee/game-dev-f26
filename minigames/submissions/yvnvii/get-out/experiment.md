# Get Out experiment: yvnvii

Principle: entry

## Decisions

After watching a classmate, I chose to show the player's move count next to the
fewest possible moves for the current board. The shortest count is computed
with `engine.solve` when a board loads. On completion, the game says whether
the player matched that count. This addresses the entry principle (make the
goal easy to understand) and the sense of solvability: players can see the
shortest route length and compare their own result with it. Boards, rules, and
hints are unchanged.

## Possible outcomes

**Prediction:** Players who finish above the fewest-moves count will undo or
reset and try to match it.

**Alternative:** Players may accept their first solution, or may not notice or
care about the comparison. That would suggest the count is not a useful prompt
for replay, or that its presentation needs to be clearer. If players do replay
but cannot reduce their count, the number may create pressure without helping
them find a better route.

## Playtest

**Prior reference-game observation (student report):** A classmate tried to
solve each puzzle in as few moves as possible but had no way to know whether
they had found an optimal solution.

**Variation playtest observation:** TODO — test the variation with an anonymous
player. Record board, version, order, hints, completion count, undo/reset
behavior, and a revealing action or remark. Do not treat predicted behavior as
an observed result.

**Plan:** Ask a player to solve a board while thinking aloud if comfortable.
Watch whether they notice the two counts, whether they undo or reset after a
non-optimal completion, and whether they can explain what the fewest count
means. Ask what they were trying to do and what changed their understanding.

## Next decision

TODO — decide whether to keep or revise the comparison after observing a
player. If players replay and improve, test whether the count helped them
choose a different route. If they ignore it or find it distracting, revise its
label or placement and test again. A small number of playtests is exploratory.

## Implementation and checks

The variation updates the board header and completion announcement in
`app.js` and `index.html`, with counter layout styling in `style.css`. It calls
the existing solver on each board load; it does not change the solver, boards,
movement rules, or hint behavior. `python3 scripts/minigames.py check --owner
yvnvii` passed; `python3 scripts/minigames.py test --owner yvnvii` passed all 7
tests; `node --check` and `git diff --cached --check` passed. Browser interaction
and narrow-screen checks remain to be done manually.

## AI assistance and human decisions

Codex implemented the requested display and comparison. I chose the design
principle and prediction. TODO — after reviewing and playtesting, record what
I kept or changed and any remaining issue.

## Independent review

TODO — record the review and any follow-up checks.
