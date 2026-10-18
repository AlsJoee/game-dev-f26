# Get Out experiment: ghanikhalid

Principle: sequence

## Prediction (student writes before building)

TODO: Describe one design change, the player behavior you predict, and what
observation would make you question that prediction.

## Implementation

Added a key micro-objective to all four original boards. E is a wall until K is
collected. Entering K stops the slide and unlocks E; K then blocks re-entry,
and the first departure cannot reverse the collecting slide, preventing exact retracing. Each supplied board
has a solver route with at least three moves after collecting K. This is a
structural constraint, not evidence of human difficulty.

Changed engine.js, levels.js, app.js, index.html, submission.json and tests.
Rule evidence is in local rule-source-map.md to respect student-folder scope.
The key test first failed because the old engine rejected K; after implementation,
all nine Node tests and owner-scoped check/test passed. Solver states include
position, key status, and the key arrival direction. Observations expose visible key status. No change
to the Python playing-agent boundary. Legacy exchanged boards without K retain
the original rules; the editor supports adding one K.

Browser check was blocked by the browser tool's file-URL security policy.
TODO manual checks: collect key, undo collection, reset, hints, complete each
board, editor/exchange, guides, touch controls and narrow-screen layout.
Repository Python tests hit missing anthropic; offline diagnostics also reported
Pyxel/authentication checks incomplete. GitHub identity was verified separately
with gh api user. No live model calls were made.

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

Independent rules reviewer found a reverse-route loophole on level 3. Fixed by blocking reversal of the collecting slide, with a regression test that failed first. Added precise local rule-map references. Independent re-review: no findings; all nine tests passed. Human approval and playtest observations remain with the student. A fresh Codex review can check code; human play supplies
experience evidence. The student and instructor retain approval decisions.

## Draft PR validation — October 18, 2026

- `python3 scripts/minigames.py check --owner ghanikhalid`: passed.
- `python3 scripts/minigames.py test --owner ghanikhalid`: all 9 tests passed.
- Tests cover wall/border movement, blocked/unknown actions, terminal behavior,
  shortest paths, invalid boards, detached observations, all four levels,
  locked exit, key collection, sealed key tile and refused reverse departure.
- Reviewed branch scope against fetched class main; only this student's game
  folder is included in the draft.
- Browser interaction, undo/reset UI, touch/narrow-screen checks and human
  experience observations remain unverified TODOs above. No human playtest
  result has been inferred from automated tests.
- Earlier full Python suite: two import errors for missing `anthropic`.
  Earlier offline setup diagnostics: incomplete Pyxel/authentication checks.
  These are recorded limitations, not passing checks for this draft.

Fresh independent draft review found that editor key/door visuals inherited
collected status from the active game. Fixed rendering to derive initial key
status from the draft board while editing. Repeated owner validation, all 9
Node tests and `node --check` for app.js successfully. This is source review
and automated evidence; browser interaction remains TODO.

Independent re-review of the editor fix: no findings.
