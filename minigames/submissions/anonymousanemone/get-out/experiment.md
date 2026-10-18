# Get Out experiment: anonymousanemone

Principle: sequence

## Prediction (student writes before building)

TODO: Describe one design change, the player behavior you predict, and what
observation would make you question that prediction.

## Implementation

Student request: “make certain blocks moveable, so the player can push it as it collides.”
Student clarification: “the block should get pushed to the end.”

Added B blocks, collision pushes to the next obstacle or edge, an introductory board, orange rendering,
and an editor tool. Engine and solver share the same rule; solver keys include block
layouts. Undo keeps immutable board snapshots; reset reloads the original board.
Changed engine.js, app.js, levels.js, index.html, style.css, tests/engine.test.cjs,
and submission.json. Rule evidence and assumptions: docs/rule-source-map.md.

Check and test commands for owner anonymousanemone passed (10 engine tests).
Three new tests failed before implementation because the engine rejected B.
Revised end-of-push tests then failed against one-square pushing and passed after revision.
All 43 course tests passed using .venv/bin/python. Offline diagnostics passed Python,
Git, Pyxel, tests and scripted fixture; sandboxed GitHub authentication check failed
though the explicitly authorized GitHub account lookup succeeded. Setup verification
remains partial; no live provider call was made.
Verified pushes, refused pushes, immutable prior states, solver hints, completion,
visible observations, and solvability of all five boards with deterministic tests.
Browser tools unavailable: manual checks remain TODO for rendered movement,
Undo, Reset, Hint buttons, completion display, editor/exchange, and narrow-screen controls.
Human experience and prediction remain student-written TODOs.

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

Independent rules-reviewer inspected the final engine, UI, map, tests and README;
no blocking findings. Fixed copied README paths and instructions, and clarified
adjacent versus distant obstacles in the rule map. Reviewer reran all 10 tests.
Remaining coverage note: no dedicated solver regression board requiring revisiting
a player position with a different block layout. Browser checks remain TODO.
Human play supplies experience evidence; the student and instructor retain approval decisions.

## Ten-level sequence update

Student request: “there are no pushable blocks in the later 9 games. generate completable levels of increasing difficulty and pushable blocks”

Replaced the four wall-only boards with nine generated push puzzles, preserving
the introductory board. All ten include B blocks and require pushing: replacing
B with fixed walls makes each board unsolvable. The unchanged engine's BFS proves
shortest solutions of 2, 3, 4, 5, 6, 7, 8, 9, 10, and 11 moves. Every solution
was replayed to a win. Increasing shortest-path length is an objective ordering,
not evidence of increasing human difficulty. Human playtest remains TODO.

The new sequence test failed first (five rather than ten levels), then passed.
Owner validation and all 11 engine tests passed. Updated levels.js, tests,
README and manifest. No movement rule or player boundary changed.
Browser interaction and narrow-screen checks remain manual TODOs.

## Local PR preparation review (2026-10-18)

Updated the local branch to the fetched class main before preparing the submission.
Current verification supersedes the earlier five-board results: owner validation
and all 11 game tests pass for the ten-board sequence; all 83 course tests pass.
Offline headless diagnostics pass outside the sandbox (partial Setup Verification;
no live model call or CI evidence was produced).

A separate read-only reviewer found no blocking engine or player-interface defect.
The solver test still lacks a dedicated board requiring a return to the same
player position with a changed block layout. Human observations, student-written
sections, and browser interaction checks remain TODOs; this is draft material.
Preparation is local only, with no push or PR creation. The student will write
the PR description.
