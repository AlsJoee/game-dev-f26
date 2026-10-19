# Get Out experiment: tony-wang-zh

Principle: parallelism

## Prediction (student writes before building)

TODO: Describe one design change, the player behavior you predict, and what
observation would make you question that prediction.

## Implementation

Changed `engine.js`, `app.js`, `index.html`, `README.md`, and
`tests/engine.test.cjs`. Each directional action advances the player and exit
together. Each actor stops independently at a wall or board edge; the player
escapes if both occupy the same square during that slide. Hints and the solver
now track both positions.

Checks run: `python3 scripts/minigames.py check --owner tony-wang-zh` and
`python3 scripts/minigames.py test --owner tony-wang-zh` (7 tests passed).
Browser checks remain to be done.

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

TODO: Record reviewer role, issues found, tests or browser checks repeated,
and your resolution. A fresh Codex review can check code; human play supplies
experience evidence. The student and instructor retain approval decisions.
