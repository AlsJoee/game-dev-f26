# Get Out experiment: rohitr4547

Principle: perception

## Prediction (student writes before building)

Starting point: the swap-sides rule from rajvardhan19's variation (class PR
#12, co-developed by rajvardhan19 and rohitr4547). When a slide misses the
exit, the ball and the exit trade places.

Design change, in the student's words from the build requests: "adding an
obstacle which shows up from the start and this obstacle can show up at any
random location to block the path from the start to the end ... while
preserving the change of swapping locations of the start and end points. The
obstacle needs to have an icon possibly of a traffic sign indicating no
movement through that path." Then: "this obstacle should be ensured to keep
changing its position from turn to turn. The previous logic of start and end
changing has to be maintained."

Draft prediction for the student to confirm or rewrite: with the exit and the
roadblock both moving, a player cannot replay a remembered route. They have to
re-read the board after every move, from the ball's side, the exit's side, and
now the roadblock's. Because the roadblock stops a slide like a wall, some
players should start using it as a stopping point. An observation that would
question this: players feel the jumps are random noise, press keys hoping for
luck, and lean on hints.

TODO: Confirm or rewrite the prediction above in your own words.

## Implementation

**Rule change.** A no-entry roadblock, drawn as a red no-entry traffic sign,
stops a slide exactly like a wall. It is on the board from the first move.
After every move that misses the exit, it jumps to a new square on the new
shortest way out. The swap rule is unchanged.

**Where it jumps.** From the new ball and exit positions, the game finds the
shortest way out as if there were no roadblock. It orders the floor squares
the ball would slide across on that route with a seeded shuffle, then picks:

1. the first square that breaks that route;
2. otherwise any route square;
3. otherwise any other floor square.

It never uses the ball's, exit's, or start square, and never stays on the
square it just left, unless no other free square exists. A blocked move does
not move it.

**Why seeded, not truly random.** A truly random jump could make the board
unsolvable mid-game and would make hints meaningless. With a seed, the choice
depends only on the seed, the ball, the exit, and the previous square. It
looks random to the player, but the solver can plan around it. The game only
uses seeds that leave a way out.

**Seeds in the app:**

- Each teaching board has a fixed seed, so every playtester sees the same
  sequence. Reset replays it.
- **New roadblock** picks a new random seed that leaves a way out.
- Custom and imported boards get a random seed.

Choices made while implementing, for the student to confirm or change:

- The roadblock jumps after every move, but not on blocked moves.
- It acts like a wall rather than doing something new.
- Teaching boards use a fixed sequence for comparable playtests.
- Board codes no longer carry a roadblock; the game always places it.
- A board with no solvable sequence plays without a roadblock and says so.

Effect on the four teaching boards (shortest route; 100 seeds per board):

| Board | Swap only | Fixed seed | Seeds that leave a way out | Route range over 100 seeds |
|---|---|---|---|---|
| 1. Find your feet | 4 | 6 | 83 | 5 to 11 |
| 2. Take the long way | 5 | 7 | 100 | 5 to 9 |
| 3. Change direction | 7 | 7 | 94 | 5 to 11 |
| 4. A useful detour | 3 | 9 | 100 | 3 to 10 |

In random play on the teaching boards, the roadblock changed square on
10,009 of 10,009 moves that missed the exit.

Changed files, all in this folder (starting from the swap variation):

- `engine.js`: the roadblock is part of the game state; `create(board, seed)`;
  `step` moves it after each move; a distance table per board makes each jump
  a lookup; `solve` searches ball, exit, and roadblock; new `solveWithin`
  (search with a budget) and `solvableSeed`.
- `tests/engine.test.cjs`: 10 roadblock tests (19 total). They fail against
  the swap-only engine; the 9 swap tests pass unchanged.
- `app.js`, `index.html`, `style.css`: the animated roadblock piece, status
  and trace messages about each jump, New roadblock, fixed seeds for teaching
  boards, bounded seed search, and hints that give up on huge boards rather
  than freezing.
- `serve.py`: a local launcher. Run
  `python3 minigames/submissions/rohitr4547/get-out/serve.py` from the
  repository root to serve the game on 127.0.0.1 and open it in a browser.
- `README.md`, `submission.json`: describe the moving roadblock. `levels.js`
  is unchanged.

Checks run (no human playtest yet):

- `python3 scripts/minigames.py check --owner rohitr4547`: 1 valid submission.
- `python3 scripts/minigames.py test --owner rohitr4547`: 19 of 19 pass.
- `python3 -m unittest tests.test_minigame_tools`: OK.
- Headless Chrome against the game served by `serve.py`, 24 of 24 pass:
  - the roadblock and sign shown at start, with an accessible label;
  - the first move still swaps, and the roadblock jumps;
  - the status line and trace report the jump;
  - undo restores the ball, exit, and roadblock;
  - reset replays the same sequence;
  - the roadblock changes square on every move that misses the exit (41 moves
    across four boards);
  - all four boards completed by following hints;
  - board 1 always starts the same;
  - New roadblock always starts on a different square;
  - a slide stopped by the roadblock is reported;
  - a board code with `X` is rejected, and the editor has no roadblock tool;
  - phone width (375 px) has no horizontal scroll;
  - no console errors.
- Speed on random 20 × 20 custom boards: finding a seed took at most 1.7 s,
  and a hint at most 55 ms.

The implementation and these checks were produced with Claude Code at the
student's request.

## Playtest observations

TODO: Record anonymous player labels, board, version and order played, hints
requested, restarts, completion, and one revealing action or remark. Separate
observations from interpretations. No names, emails, or other personal data.
Useful trace fields: `block` after each move, and `roadblock: true` when the
roadblock stopped a slide.

## Interpretation and revision (student writes)

TODO: Compare the evidence with the prediction. Mention prior familiarity,
practice effects, sample size, or other limits. Describe the revision made or
one next test. A single player's response supports a question, not a general claim.

## AI assistance and human decisions (student writes)

TODO: State what you checked, and one design decision you retained or changed
(for example, the implementation choices above). Include any remaining known
issues.

Known issues so far:

- Routes get longer (board 4 goes from 3 to 9 moves with its fixed seed),
  so the boards may now feel much harder.
- The jump is predictable in principle but not to a player, so it may read as
  random. That is the main thing the playtest should check.
- Some seeds leave no way out (17 of 100 on board 1). The game skips them,
  but a custom board can end up with no roadblock.
- On very large custom boards, a hint may report "no hint found quickly".
- Not tested with a screen reader alone.

## Independent review

Two separate, read-only Claude Code review tasks, each given the change
summary and the repository's `rules-reviewer` checklist. Neither wrote the
change.

**Review 1** covered an earlier version where the roadblock stayed put. It
fuzzed thousands of boards and found no rule errors. Its six should-fix items
were fixed before that design was replaced by the moving roadblock.

**Review 2** covered the moving roadblock. It confirmed the rule invariants:

- the roadblock never lands on the ball, exit, start, or a wall;
- it never reuses the previous square;
- blocked moves don't move it;
- the solver's search key is sufficient;
- undo restores it.

Issues found and resolved:

- **Blocking:** the solver was far too slow on 20 × 20 boards (one solve took
  155 s). Each jump re-ran a full search. A per-board distance table now makes
  each jump a lookup, and hints and seed search have a budget. Worst case is
  now about 1.7 s to start a 20 × 20 custom board, and 55 ms per hint.
- New roadblock could run up to about 1,000 solves. It is now bounded.
- Teaching boards gave no message if no seed worked. The status line now says
  when a board plays without a roadblock.
- The roadblock could vanish if no other square was free. It now stays put.
- A Hint during the swap animation jumped the pieces. Hint now waits.
- A near-vacuous determinism test was replaced. New tests cover different
  seeds, a move blocked by the roadblock itself, staying put, boards no seed
  can solve, and the search budget.

After the fixes: 19 of 19 rules tests, course check, tooling tests, and 24 of
24 browser checks pass. Code review does not replace human play evidence.

TODO: Record your own resolution of the review, including whether you keep the
implementation choices listed above. The student and instructor retain
approval decisions.
