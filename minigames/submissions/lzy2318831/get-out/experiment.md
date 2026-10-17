# Get Out experiment: lzy2318831

Principle: entry

## Prediction (student writes before building)

Student's requested design: "add a simple introductory puzzle that teaches
players how sliding and stopping work," using accessible entry (Schell,
Chapter 14 / Lens 58).

TODO (student): Write your predicted player behavior and an observation that
would make you question that prediction. No human learning result is claimed.

## Implementation

`levels.js` prepends the 5-by-5 "Slide, stop, turn" board. Its first move
slides right two squares and stops before a wall; down then reaches the exit.
The prompt asks the player to predict the stopping point. The four reference
boards follow unchanged. `engine.js`, `app.js`, and the controls are unchanged;
there are no rule changes. `submission.json` records the entry principle.

Automated checks (2026-10-17, Python 3.13.9 / Node 22.20.0):
- `scripts/minigames.py check --owner lzy2318831`: PASS.
- `scripts/minigames.py test --owner lzy2318831`: PASS, 8 tests.
  The new test checks the initial legal move, exact wall stopping position,
  blocked move, two-move shortest solution, next hint route, and completion.
  All five boards have solver-verified routes to their exits.
- JavaScript syntax checks: PASS for `app.js`, `levels.js`, and `engine.js`.
- Repository unittest discovery: 36 tests attempted, 32 passed, 4 errors:
  two modules require missing `anthropic`; two symlink tests require a Windows
  privilege unavailable in this environment. No shared code was changed.
- Offline/headless setup diagnostic: INCOMPLETE (missing Pyxel/dependencies,
  Git/gh unavailable on default PATH, and deterministic suite errors above).
  The scripted fixture passed; no live provider call was made.

Student-reported browser verification: "The introductory puzzle works and can
be completed in exactly 2 moves (right, then down)." This confirms the reported
functional check, not learning or transfer by a new player. Browser checks of
undo, reset, hints, Next puzzle, and narrow-screen controls remain TODO.
Automated solver evidence does not establish that players learn the rule.

## Design and playtesting

Draft for the PR; expected outcomes and next steps below are proposals for
student review, not a prediction recorded before implementation.

- **Design decision:** Add a small introductory puzzle before the original
  boards, applying accessible entry from Schell Chapter 14 / Lens 58. A right
  slide stops at a wall, then a down slide reaches the exit; sliding mechanics
  remain unchanged.
- **Expected outcome:** A new player predicts the stopping point after one
  press and applies the same rule on a later board.
- **Alternative outcomes:** A player may expect one-square movement, follow
  the prompt without understanding why the slide stops, or finish the tutorial
  but struggle to choose stopping points on the next board.
- **Playtest plan:** Ask a new peer to play without coaching. Before a move,
  ask where they expect to stop; then try an unfamiliar board to check transfer.
  Record anonymous player label, board/order, predicted and actual stopping
  points, hints, resets, completion, and a revealing action or remark. Avoid
  treating completion speed alone as evidence of understanding.
- **Actual observations:** TODO: Await student-supplied peer playtest evidence.
  The student's browser check confirms the right/down two-move route only.
- **Possible next decisions:** Keep the introduction if predictions transfer;
  clarify the prompt if one-square expectations persist; try a second short
  board with a different stopping point if players only copy the directions.
  Choose a revision after observing play.

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

An independent read-only Codex review found no code defects. It checked the
intro board, regression test, manifest, dynamic board sizing/level sequencing,
and preservation of the four original boards and engine. All nine new files
are inside `minigames/submissions/lzy2318831/get-out/`; tracked files have no
diff against the local class base `origin/main`.

The reviewer identified stale browser-verification wording. It is now updated
to distinguish the student's reported two-move browser completion from pending
control checks and peer learning observations. Submission validation and all
8 game tests passed again during this review. No new browser checks were run.
The student and instructor retain approval decisions; no PR was created.
