# Get Out! — Switch & Door: ruaj77

Principle: `perception` — A Change in Perspective.
Reference: Schell, Chapter 14, Lens #58: The Puzzle (course third edition).

## Prediction (student supplied before building)

"Introducing a switch-controlled door will encourage players to reconsider
obstacles as potentially useful tools rather than simply barriers."

Intended player experience, supplied by the student: Players may initially
focus on opening the door, but eventually discover that the closed door can
be strategically useful.

Central insight: "A closed door is not merely an obstacle. It can also serve
as a useful stopping point."

TODO: Student supplies an observation that would challenge this prediction.
The engine fixtures verify the rules; they do not establish this experience.

## Phase 3 engine implementation (approved by student)

This increment changes only the personal game engine and supporting tests and
documentation. It adds `T`/`D` validation, a frozen `doorOpen: false` initial
snapshot, closed-door collision, immediate one-time switch activation,
continued sliding, and door-state observations. Saved snapshots restore
position, move count, victory and door state; recreating the initial board
resets them. BFS distinguishes position and door state and still finds a
shortest path from the current snapshot without mutating it.

No fifth level, UI rendering, animation, editor tools, or trace integration
is added. The original four levels, browser assets, and seven copied reference
tests are preserved. See `rule-source-map.md` for rule evidence.

Automated checks observed:

- Test-first run: 29 tests, 8 passed and 21 failed because T/D and door state
  were unsupported. After state/movement changes, 28 passed and the solver
  revisit test still failed (`null` instead of down, up, right). Adding door
  state to BFS keys made all 29 pass (7 original + 22 new).
- `python3 scripts/minigames.py check --owner ruaj77`: valid submissions: 1.
- `python3 scripts/minigames.py test --owner ruaj77`: exit 0; default cloud
  Node runner reports two file-level tests. The explicit individual-test run
  with `--test-isolation=none` above verifies all 29 tests.
- Instructor reference engine suite with `--test-isolation=none`: 7 passed.
- Plain `python3 -B -m unittest discover -s tests -v` initially ran 34 tests
  successfully but could not import `test_providers` because the host lacked
  `anthropic`. This was an environment dependency issue, not a rule failure.
- With frozen course dependencies in a temporary environment, all 43 repository
  Python tests passed. Command: `UV_PROJECT_ENVIRONMENT=/tmp/ruaj77-course-venv
  UV_CACHE_DIR=/tmp/ruaj77-uv-cache UV_PYTHON_DOWNLOADS=never
  PYTHONDONTWRITEBYTECODE=1 uv run --frozen python -B -m unittest discover -s tests -v`.
  No dependency manifests or shared configuration were changed; SDK tests use
  mocked transports, not live model calls.
- Scope verification: all 12 new files are inside this personal directory;
  all seven instructor reference files match fetched `upstream/main`.
  Copied `app.js`, `index.html`, `levels.js`, `style.css` and original engine
  tests match the reference byte-for-byte. Branch is `ruaj77/get-out`, with
  no new commits. `origin` is the personal fork and `upstream` the class repo.

Browser interactions were not tested during Phase 3; Phase 4 results follow.

## Playtest observations

TODO: Record anonymous player labels, board, version and order played, hints
requested, restarts, completion, and one revealing action or remark. Separate
observations from interpretations. No names, emails, or other personal data.
No human playtest has been reported for this implementation.

## Interpretation and revision (student writes)

TODO: Compare actual human evidence with the prediction. Consider prior
familiarity, practice effects and sample size; choose a revision or next test.
No claim about player insight or satisfaction follows from solver correctness.

## AI assistance and human decisions (student writes)

Recorded provenance: the student supplied the title, principle, design
hypothesis, intended experience, exact switch/door rules and scope limits.
Codex performed the course scaffold, engine implementation, deterministic
tests, and basic metadata/documentation under that specification.

TODO: Student records what they personally checked, their interpretation,
and any design decisions they retain or change after playing.

## Phase 3 independent review

An independent read-only Codex rules reviewer reported "No findings" after
reading the student specification, engine, tests, local rule map and supporting
documentation. They independently ran all 29 individual Node tests and
confirmed the copied assets/levels/original tests and instructor reference
were unchanged. No issues required resolution.

Human play evidence remains TODO and is separate from code review. Browser
interactions were untested at the end of Phase 3. The student and instructor retain approval
decisions; no commit, push, PR, or merge was performed.

## Phase 4 UI integration

The approved engine, both existing test files, four teaching levels, and
manifest were preserved. This stage modifies `app.js`, `index.html`,
`style.css`, `README.md`, this report, the local implementation plan and rule
map, and adds `tests/test_ui_browser.py`.

The UI derives door and switch appearance exclusively from engine state:
closed doors are solid with `D×`, open doors are dashed with `D✓`; switches are
oval with `T○`/`T✓`. Labels and a conditional legend communicate state without
color alone. Editing shows the initial closed/inactive draft configuration.
The reference visual style and movement input methods are retained.

Activation feedback accompanies the normal move/victory message. Undo
restores snapshots, all visible indicators and counters, with door-specific
feedback only when that value changes. Reset recreates initial state and
clears history/trace. Hints retain the existing current-state solver call.

Switch and Door editor tools accept T/D. Check & play and import reject
missing/duplicate pairs or unsolvable boards before replacing the playable
board. Exchange exports the initial row format; activation is not exported.
Trace events record actual before/after door values, activation and Undo
positions/counters; trace JSON adds final door state without changing rules.

### Phase 4 automated results

- Existing personal engine tests: 29/29 passed with `--test-isolation=none`.
- `python3 scripts/minigames.py check --owner ruaj77`: valid submissions: 1.
- `python3 scripts/minigames.py test --owner ruaj77`: exit 0 (two Node test files).
- Repository Python deterministic suite with frozen dependencies: 43/43 passed.
- `python3 -B -m unittest discover -s minigames/submissions/ruaj77/get-out/tests
  -p test_ui_browser.py -v`: 17/17 real Chromium browser tests passed.

Browser tests were added and run before UI implementation. The existing hint
tests passed; tests for the missing visuals, editor tools and trace fields
failed. After integration, the keyboard focus check was corrected to navigate
with Tab: programmatic focus after mouse input is not `:focus-visible` in
Chromium. The complete browser suite then passed.

Completed browser checks: closed/open door and inactive/active switch labels
and glyphs; activation including same-slide victory; Undo/Reset visuals,
position/counters/history; hints before/after activation, after Undo/Reset,
and at an unreachable current position; valid/invalid editor boards; legacy
and T/D exchange; preservation after failed import; arrow/WASD/on-screen
controls; simulated swipe pointer events; downloaded trace JSON; keyboard
Tab focus; and 375px-wide layout without horizontal overflow. Closed/open
and narrow-editor screenshots from Chromium were inspected.

Not performed: physical-phone swipes, manual screen-reader testing,
cross-browser checks, and human playtesting or perception observations.
Playtest/interpretation TODOs above remain open. No fifth level was added;
browser fixtures are test boards only. No commit, push, PR or merge was made.

Phase 4 independent read-only review: "No findings." The reviewer independently
ran all 17 Chromium UI tests and all 29 engine tests, confirmed preservation
hashes for the engine, existing tests, levels and manifest, and verified the
branch and personal file scope. Student/instructor approval remains theirs.

## Phase 5: original fifth puzzle (superseded by Phase 5B)

Level 5 is **The Door Is a Tool**, a 7 × 7 board with eight walls and exactly
one S, E, T and D. Introductory instruction: "Cross the switch to open the door.
Think carefully about your stopping points." The shortest winning solution
is seven moves. The winning move sequence is deliberately not included.

The geometry partitions the board through the door. Reaching the switch
requires first using the closed door as a genuine stopping obstacle. Reaching
the exit then requires entering the opened door. These are consequences of
the existing rules, not scripted goals, new mechanics or additional restrictions.

### Exhaustive verification

`verify-level5.cjs` uses the approved engine for every forward transition.
It records position, current door state, whether a successful slide stopped
at the closed door, and whether the player entered the open door. It ignores
blocked inputs; an exit ends a slide and cannot count as a door stop merely
because a door lies beyond it. Same-slide activation/traversal is handled.
Visited augmented keys avoid infinite loops while preserving both historical
events. Undo and Reset are controls, not forward verification moves.

All reachable states, rather than one selected solution, were explored:

| Measurement | Result |
| --- | --- |
| Reachable augmented states, including initial/winning | 23 |
| Position/door states | 17 |
| Closed / open augmented states | 7 / 16 |
| Successful directed transitions | 43 |
| Blocked inputs ignored | 45 |
| Winning augmented states | 1 |
| Winning states without switch activation | 0 |
| Winning states without a qualifying closed-door stop | 0 |
| Winning states without open-door traversal | 0 |
| Shortest length from augmented BFS and game solver | 7 / 7 |
| Activation transitions before a qualifying stop | 0 |
| Reachable nonwinning dead-end states | 0 |

One winning augmented state can be reached by multiple routes; it does not
mean only one winning sequence exists. Reverse graph reachability verifies
that every reachable state can still reach a win. There is no prematurely
activated losing state in this board. Undo/Reset remain available if players
want to reconsider a decision. This analysis cannot establish understanding,
deliberate strategy, perceived fairness or satisfaction.

Reproduce the proof with:

```sh
node minigames/submissions/ruaj77/get-out/verify-level5.cjs
```

### Tests and preservation

Eighteen new deterministic tests were run RED before the helper and fifth
level existed. Nine helper tests then passed before level integration,
including adversarial boards with bypasses, no traversal, and no solution.
All 47 Node tests now pass (29 previously approved plus 18 new).
Six Level 5 browser tests initially failed because Level 5 was absent;
all 23 Chromium tests now pass (17 approved UI regressions plus six new).

Browser checks completed for Level 5: selector entry and navigation from
original Level 4; all 49 cells and distinct switch/door indicators; closed-door
collision while moving; activation feedback and open-door passage; full
engine-solved completion with ordinary victory feedback; Undo restoring
closed state and position/counter; Reset restoring initial board/history;
legal hints before/after activation and after Undo/Reset; and usability at
375px width. Initial desktop and narrow screenshots were inspected.

Owner check/test commands passed. The repository Python suite passed all
43 tests using frozen dependencies. The engine, UI, existing test files and
manifest remain unchanged. Original four level objects match the reference;
all instructor reference files are unchanged. All source changes are personal.
No additional level beyond Level 5, commit, push, PR or merge was created.

### Prepared human playtest plan — not performed

Design hypothesis supplied by the student:

"Introducing a switch-controlled door will encourage players to reconsider
obstacles as potentially useful tools rather than simply barriers."

Prediction: Players may initially focus on opening the door, but eventually
discover that the closed door can be strategically useful.

Alternative outcomes to consider:

- Players immediately recognize the usefulness of the closed door.
- Players activate the switch before understanding the door's usefulness.
- Players repeatedly attempt ineffective routes.
- Players fail to understand the mechanic.
- Players understand the mechanic but do not find the discovery satisfying.

After the student's approval, give anonymous Player A/B labels and show the
normal instructions, without coaching or revealing a winning route. Record
prior familiarity and whether the original four boards were played first.
Observe whether each player uses the closed door to stop, whether they seem
to use it deliberately, and whether they activate the switch. Record moves,
resets, hints and completion. Count resets separately because Reset clears
the current attempt's trace. Capture their explanation afterward; completion
or a mechanically necessary stop alone is not evidence of deliberate insight.

Ask neutral questions: "What were you trying to do?" and "What changed your
understanding?" Interpret remarks and observed actions together, without
equating a solver route with human experience. The sparse 23-state graph may
make trial-and-error completion possible; test whether the key insight is
noticed rather than assuming the seven-move target establishes difficulty.

TODO: Actual human playtest observations, deliberate-use evidence, player
explanations, interpretations, perceived fairness/satisfaction, and revisions.
Physical-device, screen-reader and cross-browser checks remain unperformed.
Final playtesting, refinement and PR preparation await explicit approval.

Phase 5 independent read-only review: "No findings." The reviewer independently
passed all 47 Node tests, confirmed all proof counts and eight preservation
hashes, checked the unchanged original four levels, and cross-checked every
one of the 43 augmented transitions using separate cell-by-cell event
instrumentation. They also checked the documentation and honest playtest plan.
Their attempted browser rerun in the default sandbox was blocked at Chromium
startup by socket permissions; it is not counted as a browser pass. The
primary agent's successful 23-case Chromium run used the authorized localhost
network permission. No source/Git mutation or approval was issued by review.

## Phase 5B: designer self-play revision to Candidate C

This section records **designer self-play feedback**, not independent human
playtesting. The designer personally played the initial Level 5, reported
that the game worked correctly, and found the puzzle slightly too easy.
The original geometry passed all mechanical constraints; the revision aims
to improve the experience, not repair a rule defect.

### Previous board (recorded before replacement)

```text
S..#E..
..##...
...D...
#..#...
..T#...
...#...
...#...
```

Previous measurements: 7 × 7, eight walls, seven-move shortest solution,
23 reachable augmented states and 43 successful transitions.

**Designer observation:** "After playing the initial version of Level 5,
I found the puzzle relatively easy to solve."

**Design decision:** "I revised the board layout to create more meaningful
movement choices while preserving the switch-and-door mechanic."

**Prediction:** "I expect the revised puzzle to require more exploration
and create a stronger moment of discovery when players recognize the
usefulness of the closed door."

The designer approved Candidate C, with the original title and instruction
retained. Its small exit alcove and less conspicuous alignment role were
selected to encourage a strategic detour and support the perception principle.
This rationale and prediction are not observed results for the revised board.

TODO: independent human playtest observations, player explanations,
interpretation, perceived difficulty/fairness and satisfaction for Candidate C.
The prepared neutral playtest plan above remains applicable.

### Candidate C integration results

The title and instruction are unchanged. Current board:

```text
.T.....
.....#.
....#E#
.....D.
.......
#...#..
S.....#
```

The installed verifier rechecked the actual integrated board instead of
importing the temporary candidate study. It confirms six walls, an eleven-move
shortest solution, 33 augmented states (21 position/door states), 65 successful
transitions, 11 closed / 22 open states, 63 blocked inputs and one winning
augmented state. All wins require activation, a successful closed-door stop
before activation, and open-door traversal. All three bypass counts, early
activation edges and nonwinning dead-end counts are zero. Generic exhaustive
analysis is retained, while CLI success additionally checks the approved exact
Candidate C board and metrics. No winning sequence is printed.

Permanent Level 5 tests were updated before replacement: four Node cases
failed against the previous board/helper interface and three browser cases
failed against its old layout, reset position and victory counter. After
integration, all 48 Node tests and 23 Chromium tests passed. Browser checks
pin the exact board and switch/door/exit positions, then exercise collision,
activation, traversal, Undo, Reset to (6,0), legal hints, completion, selection,
Next navigation and 375px layout. The 17 prior UI regression cases also pass.

Required owner check/test commands passed. All 43 repository Python tests
passed using the existing frozen dependency environment. The first four
level objects remain identical to the instructor reference and solvable.
Engine, solver, UI, controls, accessibility, prior engine tests and manifest
hashes are unchanged. All source modifications are personal; no additional
level, commit, push, PR or merge was created.

At the end of integration, independent human playtesting remained TODO and
the designer had not yet played the revised board. The subsequent designer
self-play feedback is recorded below; it is not independent playtest evidence.

Phase 5B independent read-only review: "No findings." The reviewer passed all
48 Node tests, confirmed the installed CLI counts/constraints, independently
cross-checked all 65 transitions cell by cell across the 33 augmented states,
and verified eight preservation hashes plus the original four levels/reference.
They confirmed the previous board and correctly labelled designer feedback,
and that permanent verification has no temporary candidate-study dependency.
Browser test code was reviewed; the successful 23-case Chromium run was
performed by the primary agent, not repeated by the reviewer. No approval,
source mutation or Git mutation was issued by the review.

## Final designer self-play feedback and design approval

These statements are **designer self-play feedback**, supplied by the designer
after personally playing both versions. They are not independent human
playtesting results.

**Initial version — designer observation:** "I found the original 7-move
Level 5 slightly too easy."

**Design revision — designer decision:** "I selected Candidate C to provide
more meaningful exploration and spatial reasoning without adding new mechanics."

**Revised version — designer observation:** "After personally playing
Candidate C, I found its difficulty appropriate."

The designer approves retaining Candidate C as the final puzzle design for
now. This feedback supports the designer's assessment of difficulty; it does
not establish other players' understanding, deliberate strategy, or satisfaction.

TODO: independent human playtest observations, participant explanations,
interpretation, and limitations. The prepared neutral playtest plan remains
available, and no participant observations or outcomes have been fabricated.

The current save is limited to validation and one commit/push to the personal
fork. Pull request preparation remains pending the designer's next instructions.
