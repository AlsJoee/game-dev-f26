# Get Out experiment: jarrettchen217

Principle: perception

## Prediction (student writes before building)

TODO: Describe one design change, the player behavior you predict, and what
observation would make you question that prediction.

## Implementation

Student-selected change: “加入新墙的类型 - 一次性墙.”

Codex changed engine.js (F collisions and board-aware solver), app.js (rendering and collision trace), index.html/style.css (crack symbol, instructions, editor), and levels.js (one new experiment board). Manifest and README describe this variation. Rule evidence is in docs/rule-source-map.md; new tests are in tests/engine.test.cjs.

An F wall stops a slide once, then becomes floor. Adjacent collisions consume it and count as an action without movement. Undo/reset restore walls. Reaching E still wins mid-slide.

Four new rule tests were run before implementation and failed because F was unsupported. After engine implementation, all 11 engine tests passed. Final checks: `python3 scripts/minigames.py check --owner jarrettchen217` passed; `python3 scripts/minigames.py test --owner jarrettchen217` passed all 12 Node tests. The existing `.venv/bin/python -m unittest discover -s tests -v` passed all 43 Python tests. Initial system-Python run could not import anthropic; the existing project venv resolved that environment issue.

Automated browser interaction checks in Chrome: consuming F renders floor, Undo restores F and prior move count, Reset restores the initial board, hint after consumption recommends down, and sample completion is five moves. F painting and editor Cancel checked. Imported `SF.E / ####` consumes adjacent F without displacement and counts one move. Export preserves the original F layout. At 390×844, content width equals viewport width and direction buttons consume F correctly. Both guides preserve move count; arrow input focused in the designer guide does not move the player. No browser console errors observed. These are assistant checks, not human playtest evidence.

Offline setup diagnostic passed after using the existing project venv and running outside the network-restricted sandbox. No live model was called. Offline success remains partial Setup Verification.

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

An independent read-only rules reviewer inspected the reference/student differences, rule map, engine, UI, tests, levels, and metadata. One should-fix finding requested exact code line references in the map. Those references were added; reviewer rechecked the map, rendering adjustment, and additional experiment-board test, independently reran all 12 Node tests, and reported “No findings.” The reviewer did not perform browser checks or approve a gate. Human experience evidence remains TODO above.

## Advanced board extension

Student request: “可以多加几个然后built in到第六第七个map里,这样可以方便我们去看, 去研究”.

Added puzzles 6 and 7 in levels.js, keeping the first five unchanged. Both are 7×7 with one F and shortest solutions of 10 moves. The solver verifies each is unsolvable if F is replaced at the start with either permanent wall or floor. This verifies dependence on the new mechanic, not greater human difficulty. A new test failed before implementation (only five levels present).

TODO: Student prediction and human comparison of these boards.

## Fragile-wall trap boards

Student requested built-in puzzles where removing the fragile wall can prevent completion. Added puzzles 8 and 9 without changing the rule engine. Each starts solvable; a specific wrong-side collision creates an unsolvable current state. Undo/Reset can recover. Tests verify both safe solutions and the losing traces (8: right; 9: right/up/down). The ninth board remains solvable after right/up, becoming unsolvable specifically after the F collision. Tests were run before adding each board and failed on missing levels.

TODO: Human observations: did discovering the lost stopping point feel fair, frustrating, or informative? Student interpretation and prediction remain unwritten.

## Verification of built-in puzzles 6–9

Metadata check passed. All 15 engine tests and all 43 project Python tests passed using the existing venv. Independent read-only reviewer rechecked levels, tests, README, and this report, independently ran all 15 engine tests and reported no findings.

Chrome checks: all four new puzzles are in the selector. Puzzles 6/7 complete in 10 moves and Next advances correctly. Puzzle 8 completes in 7 moves; initial right followed by hint reports no route, and Undo restores F plus a valid next-move hint. Puzzle 9 completes in 9 moves; right/up/down followed by hint reports no route, Undo restores F and a valid hint, and Reset restores its original layout. Last puzzle has no Next button. Page left at puzzle 6 with zero moves for student study. These assistant checks do not supply human playtest evidence.

## Progressive fragile-wall introduction: replacement puzzles 1–5

Student request: “可以intuitive的把前面1-5关都替换一下, 让玩家能够get used to 这个fragile的逻辑”, followed by “fregile的墙可以越来越多这种”.

Replaced only the first five boards and their prompts; kept puzzles 6–9 and all rules unchanged. F counts are 1/1/2/2/3. Lessons are stop/pass, stop/turn, two independent walls, combining turn/continuation, then a three-wall route. Introductory shortest routes use 2/2/3/4/8 actions. Solver enumerates every reachable state on boards 1–3 to verify they never become unsolvable, giving early learning room for mistakes. Board 4 can lose a stopping point and become unsolvable; Undo recovers. Board 5 combines three walls while remaining solvable at every reachable state, as independently checked by the reviewer. Both prompts remind players of Undo. All five shortest routes consume every F before completion.

Two new teaching tests failed before the replacement. The original five-step experiment board remains in a fixed rule test, rather than being tied to the changing first level.

TODO: Student prediction, human transfer observations and interpretation. Codex proposes that the first three forgiving boards help players predict stopping positions before taking on the later traps; this has not been demonstrated by human play.

## Teaching-sequence verification

Scaffold metadata check passed; 17 Node engine tests and 43 project Python tests passed. Independent reviewer found no functional issues and noted README should distinguish puzzle 4's recoverable trap from puzzle 5's forgiving layout. Documentation clarified. Reviewer independently enumerated all 30 reachable states of puzzle 5 and found each solvable.

Chrome checks: each introductory shortest route completed in 2/2/3/4/8 moves with all F consumed; Next advanced through all five to puzzle 6. First collision stopped at the expected cell; Undo restored the wall. On puzzle 5, consuming one wall left two, Undo restored three, Reset restored three, and hint recommended down. At 390×844, content width matched viewport width and direction buttons worked. Browser restored to puzzle 1 at zero moves. Human learning and transfer remain TODO.

## Fragile-wall collision animation

Student asked to optimize fragile-wall collision animation after publishing the initial branch. Presentation only: player DOM is preserved on F consumption so its slide transition continues. The wall splits into four pieces and fades outward after the 220ms slide, over 320ms; adjacent collisions begin immediately. Further moves clear old effects, and Undo/Reset restore board visuals. CSS hides effects for reduced motion; fallback cleanup removes overlays even when no animation event fires. Engine state and action timing are unchanged.

Chrome checks observed four shards and the delayed effect class for moving collisions, immediate effect class plus unchanged position for adjacent collision, correct move count, rapid continuation to completion, Undo restoring F with no residual overlay, and Reset restoring F with no residual overlay. At 390×844, content width remained 390 and shards rendered. Reduced-motion behavior was checked from source only: this browser tool exposes no media emulation. Independent reviewer found no issues and confirmed JavaScript syntax plus all 17 engine tests. Human preference for timing and feel remains TODO.
