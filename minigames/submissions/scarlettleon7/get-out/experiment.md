# Get Out experiment: scarlettleon7

Principle: perception

## Prediction (student account recorded after implementation)

“I wanted the player to not only think about where they would land on the board, but also where the door would be after they made their move. I just wanted to make the game a little bit harder to complete.”

“I think a player might try to use the up/down moves to simply get themselves on the same row as the door, rather use the blocking tiles to move towards the door.”

“I would watch out for the moves a playtester makes, whether they make more up/down moves or right/left moves due to the shifting rows.”

Timing note: these are the student's stated original intentions, supplied after playing the implementation; this is not a recorded pre-build prediction.
TODO: Student identifies an observation that would challenge this prediction.

## Implementation

Requested change (student's words): “the bottom row of the board becomes the top row, the top row becomes the second row, and so on. The only thing that changes is the order of the rows, nothing else.”

Implemented in engine.js: rotate intact rows after successful slides and carry the player with their row. Blocked inputs leave state unchanged. Crossing the exit still wins; the winning slide also rotates. The latter timing and carrying the player are implementation assumptions to confirm through play. Solver tracks board order as well as position. app.js redraws the board for movement and undo. index.html explains the rule; submission.json names the variation. See rule-source-map.md for scoped evidence.

Verification: tests were changed first; three failed on the reference engine (expected changed position/row ordering). After implementation, `python3 scripts/minigames.py check --owner scarlettleon7` passed and `python3 scripts/minigames.py test --owner scarlettleon7` passed all 9 tests, including all four teaching-board solutions. A temporary Node 22.20.0 runtime in /tmp was used because Node was absent from PATH.

No browser automation is available: visual row movement, Undo, Reset, hints, completion and narrow-screen controls still need manual browser checks. Code checks do not establish player experience.

Separate starter checks: Python unittest ran 36 tests with two import errors for missing anthropic; offline setup diagnostics also reported missing Pyxel, authentication check failure and failed deterministic tests. No live provider calls were made.

## Playtest observations

Student self-play report: “All four levels I tried were solvable.” The student tried all four included levels in the shifting-rows variation.

TODO: Record play order, hints, resets, move counts, and completion details; these were not supplied. No neighbor playtest observations have been reported. The proposed comparison of up/down versus right/left moves is a future observation, not an observed result.

## Interpretation and revision (student writes)

“My version of the game came out exactly how I wanted and predicted it to be.”

“I don't think I would change anything unless my version makes some of the level designs impossible to solve. All four levels I tried were solvable.”

Next test, in the student's words: “I would watch out for the moves a playtester makes, whether they make more up/down moves or right/left moves due to the shifting rows.”

Evidence limit: the reported play is the designer's own experience. The independent solver also verified all four levels, but neither result establishes greater difficulty for a new player. Neighbor play and movement-direction counts remain TODO.

## AI assistance and human decisions (student writes)

Codex assistance record: Codex scaffolded the personal game copy, implemented row rotation, updated the solver and instructions, wrote and ran rule tests, arranged an independent code review, and formatted this report using the student's supplied words. The student chose the row-shifting rule, tried all four levels, and retained the design: “I don't think I would change anything unless my version makes some of the level designs impossible to solve.”

TODO: Student adds or confirms their own AI disclosure wording. Manual browser checks of Undo, Reset, hints, and narrow-screen controls remain unfinished unless separately reported.

## Independent review

Independent rule review (read-only Codex agent): found stale reference paths
and smoke instructions in README, and insufficient explicit labels/locations
in the scoped rule map. Both corrected. Reviewer checked engine, UI, tests,
and maps; no rule disagreement reported. Independent test execution was
blocked by Node missing from its PATH; implementation verification used the
temporary runtime. This is code review evidence, not student approval or a
human playtest.

## Draft PR verification

Fresh independent read-only review: No findings. Reviewer read the engine,
UI, README, evidence map, manifest, experiment and tests, and independently
reran all 9 Node tests successfully. Submission validation also passed again.
The full branch comparison against fetched class main contains only this
student game folder. Student self-play, intentions and interpretation are now recorded above.
Remaining browser checks, neighbor observations, and student confirmation of
the AI disclosure remain TODOs.
No ready-for-review or gate approval is claimed.
