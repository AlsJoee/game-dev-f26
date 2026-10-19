# Get Out experiment: rohitr4547

Principle: perception

## Prediction (student writes before building)

Starting point: the swap-sides rule from rajvardhan19's variation (class PR
#12, co-developed by rajvardhan19 and rohitr4547). When a slide misses the
exit, the ball and the exit trade places.

Design change, in the student's words from the build request: "adding an
obstacle which shows up from the start and this obstacle can show up at any
random location to block the path from the start to the end ... while
preserving the change of swapping locations of the start and end points. The
obstacle needs to have an icon possibly of a traffic sign indicating no
movement through that path."

Draft prediction for the student to confirm or rewrite: the roadblock breaks
the route a player has memorised or worked out first, so they must re-read the
board from both the ball's side and the exit's side. Because the roadblock
stops a slide like a wall, some players should notice that it creates a new
stopping point and start using it on purpose. An observation that would
question this: players treat the sign only as "can't go here", route around
it, and never stop against it on purpose.

TODO: Confirm or rewrite the prediction above in your own words.

## Implementation

**Rule change.** A new square type, the no-entry roadblock (`X`, drawn as a red
no-entry traffic sign), stops a slide exactly like a wall. It is on the board
from the first move. The swap rule is unchanged. The exit can never land on
the roadblock, because the exit only goes where the ball stops.

**Random placement.** When a puzzle loads, `placeRoadblock` finds the current
shortest route under the swap rule, collects the floor squares the ball slides
across on it, and picks one at random. It prefers a square that stops the old
shortest route from working, keeps a square only if the board stays solvable,
falls back to another floor square if no route square works, and leaves the
board alone if nothing works. Reset keeps the roadblock; **New roadblock**
rolls another, on a different square whenever another square works. A board
code with an `X` keeps it as written. The editor opens on the board without
its random roadblock.

Choices made while implementing, for the student to confirm or change:

- One roadblock per puzzle, fixed until **New roadblock** or a new puzzle
  (it does not move each turn).
- It stops the ball like a wall rather than, for example, bouncing it back.
- Placement always keeps the board solvable, so hints still work.

Effect on the four teaching boards (300 random placements each; shortest
route under swap only → with roadblock):

| Board | Swap only | With roadblock | Distinct roadblock squares |
|---|---|---|---|
| 1. Find your feet | 4 | 7 (21%) or 9 (79%) | 4 |
| 2. Take the long way | 5 | 4 (10%) or 6 (90%) | 11 |
| 3. Change direction | 7 | 4 to 9 (7 most often, 53%) | 16 |
| 4. A useful detour | 3 | 4 (100%) | 2 |

In all 1,200 placements the old shortest route no longer reaches the exit.
The roadblock can still make a board *shorter* (board 2 at 4 moves, board 3
at 4 to 6), because it gives the ball a new place to stop. That is the "useful
obstacle" moment the prediction is about.

Changed files, all in this folder (starting from the swap variation):

- `engine.js`: `X` is a valid square that stops slides; a shared `slide`
  helper lists the squares a slide crosses; new
  `placeRoadblock(board, random, avoid)`.
- `tests/engine.test.cjs`: 7 new tests (16 total). Against the swap-only
  engine, all 7 new tests fail and the 9 existing ones pass.
- `app.js`: roadblock placed on load, kept on reset, **New roadblock** button,
  status and trace say when the roadblock stopped a slide, editor tool, trace
  format `get-out-roadblock-trace-v1` with roadblock positions and whether
  the roadblock was random or authored.
- `index.html`, `style.css`: rule card, legend, no-entry sign, discussion
  prompt, editor and exchange text.
- `README.md`, `submission.json`: describe the roadblock. `levels.js` is unchanged.

Checks run (no human playtest yet):

- `python3 scripts/minigames.py check --owner rohitr4547`: 1 valid submission.
- `python3 scripts/minigames.py test --owner rohitr4547`: 16 of 16 pass.
- `python3 scripts/minigames.py boundary` against class `main`: passes.
- Course tooling tests: `python3 -m unittest tests.test_minigame_tools` pass.
- Headless Chrome, 31 of 31 pass: one roadblock with a no-entry sign and an
  accessible label at start; the first move still swaps; undo and reset keep
  the roadblock; all four boards completed by following hints; New roadblock
  always leaves exactly one and never repeats the previous square in 15
  rolls; an imported `X` stays put and hides New roadblock; moving into the
  roadblock is blocked, costs no move, and is traced; a slide stopped by it
  still swaps; a code without `X` gets one; an exit walled in by roadblocks
  is rejected; a board with no safe square says so; the editor opens without
  the random roadblock, and Check & play draws a new one; the editor paints
  one roadblock; phone width (375 px) has no horizontal scroll; no console
  errors.

The implementation and these checks were produced with Claude Code at the
student's request.

## Playtest observations

TODO: Record anonymous player labels, board, version and order played, hints
requested, restarts, completion, and one revealing action or remark. Separate
observations from interpretations. No names, emails, or other personal data.
Useful trace fields: `roadblock: true` events show when a player stopped
against the roadblock.

## Interpretation and revision (student writes)

TODO: Compare the evidence with the prediction. Mention prior familiarity,
practice effects, sample size, or other limits. Describe the revision made or
one next test. A single player's response supports a question, not a general claim.

## AI assistance and human decisions (student writes)

TODO: State what you checked, and one design decision you retained or changed
(for example, the three implementation choices above). Include any remaining
known issues.

Known issues so far:

- Board 4 has only two possible roadblock squares, so New roadblock just
  alternates between them.
- On custom boards where no route square works, the roadblock goes on an
  off-route square and does not block the route. The teaching boards never
  hit this case (0 of 1,200 placements).
- Because placement is random, two players can face different routes on the
  same board. Use a board code with an `X` when you need players to see the
  same puzzle.
- Not tested with a screen reader alone.

## Independent review

Reviewer: a separate, read-only Claude Code review task, given the change
summary and the repository's `rules-reviewer` checklist. It did not write the
change. It reran the tests and ran the new tests against the swap-only engine
(the new tests fail there, as expected). It also fuzzed both engines:

- Swap-only vs this engine on 3,000 boards without a roadblock: 0 differences
  in 60,000 steps or in solver output, so the swap rule is unchanged.
- `X` vs `#` on 3,000 boards: 0 differences.
- `placeRoadblock` on 2,000 boards: 0 inputs mutated and 0 solvable boards
  made unsolvable.

No blocking findings. Issues found and resolved:

- The editor copied the random roadblock into the new design, where it then
  counted as authored and hid New roadblock. The editor now opens on the board
  without it.
- New roadblock could land on the same square again (50% of the time on board
  4). It now avoids the previous square whenever another square works.
- The README, rule card, and editor text claimed the roadblock is always on
  the shortest route. The off-route fallback is now described.
- Two fallback paths were untested. Added a test for a solvable board where
  every square would trap the ball. The other surviving mutant (dropping the
  solvability check in the off-route fallback) cannot change behaviour: an
  off-route square never touches a slide on the route, so that check is now
  commented as a guard.
- The import message claimed a roadblock even when none could be placed, and
  the rejection text did not mention roadblocks. Both fixed.
- The README's editor and board-code sections did not mention `X`. Fixed.
- Notes also addressed: placement now stops at the first good square (the
  reviewer's worst random 20 × 20 board took 389 ms before; the worst of 300
  new random 20 × 20 boards now takes 12 ms), and
  the trace records whether the roadblock was random or authored. A
  meaningless invalid-board test case was removed.

After the fixes: 16 of 16 rules tests, course check, boundary check, tooling
tests, and 31 of 31 browser checks pass. Code review does not replace human
play evidence.

TODO: Record your own resolution of the review, including whether you keep the
three implementation choices listed under Implementation. The student and
instructor retain approval decisions.
