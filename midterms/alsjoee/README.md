# Prince of Persia: One Room (turn-based)

Author: AlsJoee

## Scope

A turn-based reconstruction of a single Prince of Persia (Broderbund, Apple II,
1989) room puzzle. The Prince moves one tile per turn on a small multi-floor
grid and must reach the exit. Included: walking, jumping a one-tile gap,
climbing one floor, falling, health, spikes, a pressure plate and a gate.
Excluded: real-time movement, guards and sword fighting, potions, the
60-minute clock, animation and sound. These are cut to keep one bounded,
turn-based episode that a model player can be evaluated on.

## Rules and rule/source map

| # | Rule | Label | Evidence |
|---|------|-------|----------|
| 1 | The Prince starts with 2 health. | design | Adapted: the original starts with 3 health points; 2 makes a 2-floor drop cost half. |
| 2 | Actions: `left`, `right`, `jump_left`, `jump_right`, `climb`, `wait`. One action per turn. | design | Turn-based adaptation of real-time controls. |
| 3 | A jump clears exactly one empty tile and lands two tiles away. | assumed | From memory of play; to verify. |
| 4 | `climb` moves up one floor onto the tile directly above. | assumed | From memory of play; to verify. |
| 5 | Walking or jumping onto an empty tile makes the Prince fall to the floor below. | observed | From memory of play; to verify. |
| 6 | Falling 1 floor is safe. | observed | From memory of play; to verify. |
| 7 | Falling 2 floors costs 1 health. | observed | From memory of play; to verify. |
| 8 | Falling 3 or more floors kills the Prince. | observed | From memory of play; to verify. |
| 9 | Landing on or walking into spikes kills the Prince. | observed | From memory of play; to verify. |
| 10 | Stepping on a pressure plate opens the gate for 3 turns; a closed gate blocks movement. | design | The original gate closes after real time; converted to turns. |
| 11 | Reaching the exit wins. | observed | From memory of play; to verify. |
| 12 | An episode ends after 40 steps. | design | Episode limit for evaluation. |

## Declared evaluation suite (declared October 26, 2026, before tuning)

Legend: `S` start, `E` exit, `.` floor, space = empty, `^` spikes,
`P` pressure plate, `G` gate, `#` wall. Row 1 is the top floor.

**A: First gate** (shortest solution: 7 moves)
```
S. .P.G.E
```

**B: The long way down** (shortest solution: 10 moves)
```
S...  ..#
#. ...^.#
..#  ...#
#^.....E#
```

**C: Plate below** (shortest solution: 8 moves)
```
#...G..E
#.. P###
S..^####
```

**H: Held-out** (not used during prompt tuning; shortest solution: 10 moves)
```
E..G..##
###.P..#
#.. ...#
S..^ ..#
```

Each situation is run twice with the model player and with the BFS baseline.

## Setup, play, test and evaluation

To be written.