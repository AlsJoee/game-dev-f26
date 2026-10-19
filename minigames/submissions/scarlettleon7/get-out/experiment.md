# Get Out experiment: scarlettleon7

Principle: perception

## Prediction (student writes before building)

TODO: Describe one design change, the player behavior you predict, and what
observation would make you question that prediction.

## Implementation

Requested change (student's words): “the bottom row of the board becomes the top row, the top row becomes the second row, and so on. The only thing that changes is the order of the rows, nothing else.”

Implemented in engine.js: rotate intact rows after successful slides and carry the player with their row. Blocked inputs leave state unchanged. Crossing the exit still wins; the winning slide also rotates. The latter timing and carrying the player are implementation assumptions to confirm through play. Solver tracks board order as well as position. app.js redraws the board for movement and undo. index.html explains the rule; submission.json names the variation. See rule-source-map.md for scoped evidence.

Verification: tests were changed first; three failed on the reference engine (expected changed position/row ordering). After implementation, `python3 scripts/minigames.py check --owner scarlettleon7` passed and `python3 scripts/minigames.py test --owner scarlettleon7` passed all 9 tests, including all four teaching-board solutions. A temporary Node 22.20.0 runtime in /tmp was used because Node was absent from PATH.

No browser automation is available: visual row movement, Undo, Reset, hints, completion and narrow-screen controls still need manual browser checks. Code checks do not establish player experience.

Separate starter checks: Python unittest ran 36 tests with two import errors for missing anthropic; offline setup diagnostics also reported missing Pyxel, authentication check failure and failed deterministic tests. No live provider calls were made.

## Playtest observations

TODO: Record anonymous player labels, board, version and order played, hints
requested, restarts, completion, and one revealing action or remark. Separate
observations from interpretations. No names, emails, or other personal data.

## Interpretation and revision (student writes)

TODO: Compare the evidence with the prediction. Mention prior familiarity,
practice effects, sample size, or other limits. Describe the revision made or
one next test. A single player's response supports a question, not a general claim.

## AI assistance and human decisions (student writes)

TODO: State what Codex generated, what you checked, and one design decision you
retained or changed. Include any remaining known issues.

## Independent review

TODO: Student confirmation and human play evidence.


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
student game folder. Manual browser checks and human observations remain
pending; prediction, interpretation and student AI disclosure remain TODOs.
No ready-for-review or gate approval is claimed.
