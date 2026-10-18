# Get Out: visited stopping places

Principle: `progress` — visible progress.

## Prediction before building

The student chose route history and approved this prediction in the implementation plan:

> If I mark places where the player has stopped, I expect them to recognize repeated routes and make more deliberate choices.

The marks could instead add clutter, go unnoticed, or make a player avoid a useful repeated stop. That would challenge the prediction. These are predictions, not playtest findings.

## Implementation

Added an exploration record to the existing Get Out interface. It marks the start and the endpoint of each successful move. Visited stops remain after Undo and clear on Reset or loading another board. Canceling the editor or rejecting an invalid board preserves the record. Movement rules, scoring, hints, and the solver are unchanged.

The marks say where the player has stopped. They do not measure closeness to the solution. All history stays in memory.

## Design and playtesting

**Decisions:** Add visible marks to visited stopping places. The student selected this experiment to investigate whether an exploration record helps players recognize repeated routes. The chosen idea is Puzzle Principle 3 in Schell's Chapter 14: giving a sense of progress. In the third edition, this principle and Lens 55 (Visible Progress) appear on page 258. Schell writes:

> Players need to see that they are making progress when solving a difficult problem.

Source: Jesse Schell, *The Art of Game Design: A Book of Lenses*, third edition (2019), Chapter 14, p. 258. [Chapter DOI](https://doi.org/10.1201/b22101-14).

Lens 58 (The Puzzle), on page 265, asks designers to identify which puzzle principles apply to their puzzles. Here the rings make exploration visible. Whether that helps the player understand the route is the question being tested. The marks do not show distance to the solution.

**Possible outcomes:** A player may recognize a loop and deliberately try another direction. That would suggest the record helps orientation. A player may ignore the marks or treat a visited square as a mistake. That would suggest the display is unclear or discourages useful revisiting. Fewer moves alone would not establish better understanding.

**Playtest:** Ask Player A to solve an unfamiliar board using the on-screen instructions. Watch without coaching. Record the board code, version, order, hints, resets, completion, and a revealing action or remark. Ask, "What were you trying to do?" and "What did the marks mean to you?" For a later comparison, alternate reference/variation order across players and avoid interpreting a faster repeat of a known solution as an interface effect.

**Next decision:** If the player notices a loop and uses the record to choose a move, keep the markers and test another unfamiliar board. If they avoid necessary revisits, clarify the legend and retest. If the display feels cluttered, reduce marker prominence and check whether it remains readable. If the marks go unnoticed, test a clearer legend before adding more features.

## Actual playtest observations

TODO: The student missed the classmate-exchange session. That exchange remains incomplete. Player A is available for a planned playtest, but no human observations of the reference or variation have been reported. Automated and browser checks below are software validation, not a human playtest.

## Interpretation and revision

TODO: Add the student's interpretation after human play. Compare the observation with the prediction. Record prior familiarity, practice effects, and the limits of a small sample. Do not claim that the design improved understanding without evidence.

## AI assistance and human decisions

The student chose the route-history experiment and approved the scope and prediction before implementation. Codex scaffolded the copy, implemented the markers and tests, and organized the approved plan into this report. At the student's request, Codex then verified the quotation and page references directly in the third-edition chapter through Columbia Libraries. The student's human-playtest observations and interpretation remain pending. The current CourseWorks assignment does not require a separate AI-use disclosure.

## Independent review and checks

A separate Codex reviewer compared the student copy with the instructor reference. The reviewer flagged that generic spans do not reliably expose accessible names. Play cells now use `role="img"`; editor cells remain native buttons. The reviewer confirmed the fix and found no remaining actionable issues. That review was static, separate from the checks below.

- `python3 scripts/minigames.py check --owner oscarodonnell1`: passed.
- `python3 scripts/minigames.py test --owner oscarodonnell1`: all 12 tests passed, including five new exploration tests.
- Full lab validation and all 45 Node tests passed; gallery generation succeeded.
- `uv run --frozen python -m unittest discover -s tests -v`: all 83 Python tests passed. The system Python lacked dependencies, so the checks used the repository's locked environment.
- `uv run --frozen python -m course_game.setup_check --offline --headless`: passed offline checks, including the Pyxel engine. This is partial setup verification, with no live model call.
- Browser checks passed for keyboard and on-screen movement, blocked actions, stopping-cell marks, hints, completion, Undo after completion, Reset, editor Cancel, malformed and unsolvable imports, valid board exchange, and switching boards.
- Opening both workshop guides and using arrow keys within them preserved the move count and history.
- At a 390 × 844 viewport, the page had no horizontal overflow, the corner rings and legend remained legible, and direction buttons measured 58 × 48 pixels.
- The browser exposed the starting cell as a named image with its visited-stop label. A physical touchscreen and screen-reader-only play were not tested.

These checks establish software behavior, not whether the marks help a person understand the puzzle. Human evidence remains pending, so the PR stays in draft.

## Sources

- Jesse Schell, *The Art of Game Design: A Book of Lenses*, third edition (A K Peters/CRC Press, 2019), Chapter 14, pp. 251–265. Puzzle Principle 3 and Lens 55: Visible Progress, p. 258; Lens 58: The Puzzle, p. 265. Quotation and page references verified in Columbia's licensed third edition on October 18, 2026. [Chapter DOI](https://doi.org/10.1201/b22101-14) · [Columbia library access](https://clio.columbia.edu/catalog/on1118981796). This does not claim the student has completed the reading.
- [Course exercise: visible progress](https://github.com/columbia-university-ai-games/game-dev-f26/blob/main/minigames/EXERCISES.md).
- Eric Zimmerman, *The Rules We Break*, exercise 11, Get Out! Reference-game attribution and original course boards are retained in `README.md` and the game.
