# Episode: A-seed1-h0-local-gemini-3.5-flash-lite

## Setup
Room A, seed 1. Model gemini-3.5-flash-lite, local view, history 0.
Recorded at commit 9fe5c19.

## Moves
Positions are row, column, counting from 0.

| Step | Who | Action | Result | Position after |
|---|---|---|---|---|
| 1 | model | right | right | 0, 1 |
| 2 | model | right | right; died: fell off the bottom | off the map |

## First mistake
Step 2: right. The Prince walked from row 0, column 1 onto the gap at column 2. Nothing lies below that gap, so he fell off the bottom of the room and died under rule 14. Before the move he was 6 moves from the exit; that count uses the hidden gate timer and was made afterwards, so the model could not have seen it. `jump_right` was a legal action on this step.

The prompt's Rules section did not state rule 14: the facts output reports the fall-off rule as absent. It covered falls only by distance, and the map legend said a gap "makes you fall". The local view did describe this fall in its "Next to you" line: "right = gap (below it: nothing; you would fall off the map)". That line says he would fall off the map, but not that doing so kills him.

## How it ended
The Prince died by falling off the bottom, for a score of zero. The episode used 2 of its 40 steps, with no invalid moves and no fallbacks.

## Compared with BFS
BFS shortest solution: 7 moves: right, jump_right, right, right, right, right, right.

The episode's first move matched this route, and its second move was `right` where BFS has `jump_right`. It ended after 2 steps without reaching the exit; it had been 6 moves from the exit just before the fatal step. None of its steps were fallback waits. BFS knows the rules by simulating them, so this compares against the best possible route, not an equal player.
