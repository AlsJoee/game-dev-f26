# Get Out: progressive hints

Principle: `hints`.

## Prediction before building

The student selected progressive hints: a question, then a clue, then a move.
The student's goal, in their own words:

> Help them figure out the route themselves and feel that they solved it.

The expected behavior below is a prediction. There are no reported human
playtest results for this variation.

## Design and playtesting

**Decisions:** I added a question, then a clue, then a move. Each step is optional.
I want players to figure out the route themselves and feel that they solved it.
This uses Schell's Chapter 14, Principle 8: hints can sustain interest (p. 263).
Schell writes that "a well-timed hint can renew their hope and their curiosity."
Lens 58 asks, "Which of the ten puzzle principles apply to each of my puzzles?"
(p. 265). Here I am applying the hints principle to the route-finding puzzle.

**Possible outcomes:** I expect a player to use a question or clue and then work
out a move themselves. If they can explain the move and say they felt they
solved it, that would support my goal. They might instead click through to the
move every time. That could mean the earlier hints are too vague or that the
player wants a direct answer. Completing the board alone would not show
understanding or ownership.

**Playtest:** Ask Player A to solve an unfamiliar board. Say the hints are
optional. Watch without coaching. Record which levels they request, what they
do next, and whether they continue without more help. Ask, "How did you decide
your next move?" and "What felt like your own discovery?" Record their actual
words separately from my prediction. A comparison with direct hints should use
comparable unfamiliar boards and alternate version order across players;
repeating a known solution introduces practice effects.

**Next decision:** If a question or clue helps the player reason through a move,
I would keep the sequence and test another board. If they skip to the answer,
I would ask why and revise the earlier hints if they were unclear. If hints
spoil the discovery, I would make the clue less specific. Checks and known
limits are listed below. Human interpretation remains pending.

## Implementation

- The first request shows a question. The second adds a clue about a useful
  stopping feature or exit alignment. The third reveals one move.
- Clues are derived from the current board and the reference solver. They
  apply to imported and edited boards as well as the teaching boards.
- Every hint is optional. Requesting help never moves the player.
- Successful moves and Undo restart the sequence. Blocked moves preserve it.
- Reset and valid new boards clear help. Editor Cancel and invalid imports
  preserve the previous sequence. Help is hidden during editing.
- Unreachable positions receive staged recovery help. Finished boards disable
  hints. After all three levels, further requests are disabled until play changes.
- The trace records the level, kind, message, and position. The hint count
  counts revealed levels, not how many positions needed help.
- Reference rules, solver, move scoring, and teaching boards are unchanged.
  The earlier route-history experiment is preserved in Git history; its
  markers are absent from this variation.

## Actual playtest observations

TODO: No human playtest of progressive hints has been reported. The student
missed the classmate-board exchange. That exchange remains incomplete.
A family member is available to test the variation as Player A. This does not
claim that a family test fulfills the classmate-exchange requirement.

## Interpretation and revision

TODO: Add the student's observations and interpretation after play. Ask
whether the hints supported their intended feeling of solving it themselves.
Keep the player's words distinct from inferred understanding. A small test is
exploratory, and no positive result is required.

## Checks and known limits

- All 13 student-game tests pass. The hint tests first failed because the new
  hint module was absent, then passed after implementation.
- Move hints were checked at every reachable position on the four teaching
  boards. No rule or solver changes were needed.
- Submission validation passes. All 83 deterministic Python tests pass.
  Offline/headless setup diagnostics pass; this is partial setup verification,
  with no live model calls.
- Browser checks pass for all hint levels, blocked/successful moves, Undo,
  Reset, board selection, completion, custom-board hints, no-route recovery,
  editor Cancel after an invalid edit, invalid/unsolvable imports, valid board
  exchange, trace display/download, and keyboard focus in both guides.
- At 390 x 844, there is no horizontal overflow. Direction buttons are
  58 x 48 pixels; the hint button is at least 44 pixels high. On-screen
  movement and completion work at that size. The browser reports no errors.
- An independent reviewer found that hiding the empty hint live region could
  suppress the first announcement. The region now stays rendered. The
  reviewer verified the fix and found no remaining actionable issues.
- The reviewer also checked clue and move validity over 6,262 positions on
  1,000 generated boards. This is software validation, not human evidence.
- The engine, solver, teaching boards, and original rule tests are byte-identical
  to the instructor reference.
- A question can repeat at different positions. Some clues may still be too
  vague or too revealing; the playtest should investigate that.
- Physical touchscreen and screen-reader-only play have not been tested.

## Decision provenance

The student chose progressive hints and supplied the design goal before this
change was built. Codex implemented the sequence and organized a proposed
test plan and conditional interpretations for student review. No human
observations or feelings are invented. The PR remains in draft.

## Sources

- Jesse Schell, *The Art of Game Design: A Book of Lenses*, third edition,
  Chapter 14, Principle 8, p. 263; Lens 58: The Puzzle, p. 265. Verified in the
  full publisher PDF accessed through Columbia Libraries. These are PDF pages
  306 and 308. [Chapter DOI](https://doi.org/10.1201/b22101-14) ·
  [Columbia library access](https://clio.columbia.edu/catalog/on1118981796).
- [Course hints exercise](https://github.com/columbia-university-ai-games/game-dev-f26/blob/main/minigames/EXERCISES.md).
- Eric Zimmerman, *The Rules We Break*, exercise 11, Get Out! Reference-game
  attribution and original course boards remain in `README.md` and the game.
