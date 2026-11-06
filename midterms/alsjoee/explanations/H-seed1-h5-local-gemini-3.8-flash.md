# Episode: H-seed1-h5-local-gemini-3.8-flash

## Setup
Room H, seed 1. Model gemini-3.8-flash, local view, history 5.
Recorded at commit cbdf1ed.

## Moves
Positions are row, column, counting from 0.

| Step | Who | Action | Result | Position after |
|---|---|---|---|---|
| 1 | model | right | right | 3, 1 |
| 2 | model | climb | climb | 2, 1 |
| 3 | model | right | right | 2, 2 |
| 4 | model | jump_right | jump_right | 2, 4 |
| 5 | model | climb | climb; the gate opens | 1, 4 |
| 6 | model | climb | climb | 0, 4 |
| 7 | model | left | left | 0, 3 |
| 8 | model | left | left | 0, 2 |
| 9 | model | left | left | 0, 1 |
| 10 | model | left | left; reached the exit | 0, 0 |

## First mistake
None. Every model move brought the exit closer.

The count of moves left fell by one on every step, from 9 after step 1 to 0 after step 10. That count uses the hidden gate timer and was made afterwards, so the model could not have seen it. The timing was close: the Prince stepped onto the gate tile (row 0, column 3) on step 7, and the gate had closed behind him by the end of step 8.

## How it ended
The Prince reached the exit for a score of one, with his full 2 health. The episode used 10 of its 40 steps, with no invalid moves and no fallbacks.

## Compared with BFS
BFS shortest solution: 10 moves: right, right, climb, jump_right, climb, left, climb, left, left, left.

The episode also took 10 steps, so it matched the shortest length with no extra steps and no fallback waits. Its route was different: it climbed at column 1 where BFS walks on to column 2 first, and it climbed twice at column 4 where BFS moves left between climbs. BFS knows the rules by simulating them, so this compares against the best possible route, not an equal player.
