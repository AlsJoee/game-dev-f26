# Get Out experiment: Follow your trail

Principle: progress

## Design and playtesting

- **Decisions:** Show the full traveled path, with dots at stopping points,
  to apply the visible-progress idea from Schell Chapter 14 and Lens 58.
  The trail makes previous exploration visible while allowing necessary revisits.
- **Possible outcomes:** The prediction is that recognizing previous attempts
  helps players avoid unproductive repeated routes. Alternatively, the trail
  might add clutter or discourage revisits that are needed to solve the board.
  The first outcome would support the design; the second would suggest changing
  how the history is displayed or explained.
- **Playtest:** In the designer's actual self-test, the trail felt a little
  helpful, but the easy levels required little assistance. A classmate test is
  planned, not completed: use an unfamiliar, more challenging board, watch for
  repeated routes and necessary revisits, and ask how the player chose a move.
- **Next decision:** Keep the current trail for the proposed test. If players
  use it to reason about routes, retain it; if it obscures the board or creates
  confusion, try fading older trail segments and test again. The easy-level
  self-test does not establish a measurable improvement. Functional checks and
  known limits are recorded below.

## Design rationale and prediction

Chosen design: show the full traveled path, extending the Designer's guide's
visible-progress idea beyond stopping positions. The student's request was:
"What about not just stopping positions, but the full path?"

Working prediction proposed in the design conversation: a visible record of
slides may help players recognize prior attempts and repeat unproductive
routes less often. An alternative is that the trail clutters the board or
discourages necessary revisits. These are predictions, not observed results.

## Implementation

`app.js` renders a continuous SVG line through the start and each successful
slide's endpoint, covering all intermediate squares. Small dots identify
stopping points. The display is derived from the current undo history: undo
removes the last slide while retaining older overlapping paths; reset and
new puzzles clear it. Blocked moves and hints do not alter it. The editor
hides it, and Cancel restores it. Rejected imports preserve the current trail.

`style.css` places the faint trail under the player, exit, and start symbols.
`index.html` adds the trail legend and explains that revisiting can be useful.
`submission.json` names this progress experiment; `README.md` explains play.
There are no movement, solver, level, or victory-rule changes.

Checks performed on October 19, 2026:

- `python3 scripts/minigames.py check --owner noahschwed`: valid submission.
- `python3 scripts/minigames.py test --owner noahschwed`: all 7 rule tests pass.
- `node --check minigames/submissions/noahschwed/get-out/app.js`: passes.
- `.venv/bin/python -m unittest discover -s tests -v`: all 83 tests pass.
- `.venv/bin/python -m course_game.setup_check --offline --headless`: all
  offline checks pass. This is partial Setup Verification, with no live model
  calls or CI evidence claimed.
- Chrome interaction checks: full segments through intermediate squares,
  blocked moves, hints, completion, undo after completion, overlapping route
  revisits, reset, editor cancel, and puzzle switching all behave correctly.
- A 2-by-5 custom board confirmed rectangular scaling and that the trail ends
  at a mid-slide exit. An unsolvable import preserved the existing board/trail.
- At 390-by-844, no horizontal overflow; direction controls are 58-by-48 pixels.
  Direction buttons and keyboard both add the expected path segments.

The first attempt to run the repository-wide Python checks lacked its
dependencies. Installing the locked environment with `uv sync --frozen`
resolved that setup issue; the passing results above use that environment.

## Playtest observations

Designer self-test, reported October 19, 2026: the student said the trail
"helps a little bit," but that they are good at the easy levels and are unsure
how much help is needed on those boards. This is reported perceived usefulness;
no reduction in repeated moves was measured. Exact boards, move counts, hint
use, resets, and completion details were not supplied.

TODO: If a peer tests it, record anonymous player labels, board, version and
order played, hints requested, restarts, completion, and one revealing action
or remark. Separate observations from interpretations. No personal data.

Proposed test: ask Player A to solve an unfamiliar board using the variation,
without coaching. Watch for repeated routes and decisions to revisit a square.
Afterward ask, "What helped you choose your moves?" and "How did you use the
trail, if at all?" Ask for a specific example. If comparing against the
reference, use different players or alternate board/version order to limit
the effect of remembering a solution. Browser automation above is functional
verification and supplies no human-experience evidence.

## Interpretation and next test

The student's own limitation: the easy levels require little help for them,
so this self-test gives limited evidence of the trail's effect.

Proposed next test: keep the current trail and ask
a classmate to try an unfamiliar, more challenging board without coaching.
Watch whether they refer to the trail when choosing a route, repeat an
unproductive route, or avoid a necessary revisit. Ask for a specific example
of how they chose a move. This would test usefulness when remembering earlier
attempts matters more; it is not a result already observed.

The self-test is one designer's subjective impression on easy levels, with no
comparison or measured change in repeated routes. It is a reason to investigate
the question on unfamiliar boards, not a general claim of improved performance.

## Build assistance

The student chose a full-path trail and reported the self-test above. Codex
implemented the display, ran the checks, and organized the reflection. Peer
observations remain pending and the next test is explicitly a proposal. The
CourseWorks assignment states that no AI-use disclosure is required.

Known design limits: overlapping paths do not show visit counts or travel
order. The trail records the active attempt, so undo removes its last segment.
Like the reference, reloading the page clears in-memory progress. Whether the
trail helps reasoning still needs human evidence.

## Independent review

A separate read-only Codex reviewer examined the student copy against the
reference on October 19, 2026 and found no actionable issues. The review
covered rendering, undo history, reset/load/editor behavior, CSS stacking,
accessibility attributes, ownership scope, metadata, and report accuracy.
It confirmed that the engine, solver, boards, and engine tests are unchanged
and that the report distinguishes the self-test from planned peer testing.

The reviewer repeated submission validation, all 7 engine tests, and the
JavaScript syntax check successfully. The reviewer did not repeat the browser
checks or the 83 repository tests; those results above were recorded during
implementation. This review supplies no additional human-playtest evidence.
