# Get Out: Blue & Orange

Personal variation by yw4626. The four original course puzzles are unchanged.
The previous practice/patrol campaign is removed. Puzzles 5–8 use a single
blue/orange pair; there are no enemies, waits or timed rules.

## Play

Open this folder's `index.html`, or run `python -m http.server 8000` from the
repository root and visit <http://127.0.0.1:8000/minigames/submissions/yw4626/get-out/>.
No build, account, runtime dependency or model call is needed.

Arrow keys, WASD, swipe or buttons slide until a wall/border. Crossing the
green exit wins. Enter blue B to emerge at orange O, or orange O to emerge
at blue B. Teleportation stops the slide and costs one move, including travel
to the entrance. Choose a new direction afterward. Standing on a portal
does not trigger it again; entering it does. A trip ending at the same square
still counts, but a blocked direction does not.

| Puzzle | Idea | Shortest route |
| --- | --- | --- |
| 1–4 | Original lessons, unchanged | 3, 5, 7, 9 moves |
| 5. Across the wall | Cross a barrier and choose a new direction | 4 moves |
| 6. Find the approach | Line up with the orange entrance | 6 moves |
| 7. There and back | Use both directions of the connection | 8 moves |
| 8. The last connection | Combine detours and both directions | 10 moves |

Removing portals makes every new puzzle unsolvable. Route length is a
structural measure, not evidence of human difficulty. Undo reverses a full
move including teleportation. Reset restores the start; hints obey portals.
**Watch solution** demonstrates the current puzzle from its start, then
restores progress/history on completion or Stop. It is disabled when editing.

The right-hand **Minimum moves** card shows the shortest solution length from
the puzzle's start, including portal rules. The target stays fixed during play.
Finishing at the minimum earns a matching message; a longer finish shows the
extra moves and invites another attempt. Custom boards also get a calculated
target; the card is hidden while editing an unvalidated draft.

## Design and exchange

The editor paints walls, floor, S, E, B and O. Placing a letter moves its
previous instance. Use both portals or neither. Check & play rejects incomplete
pairs and unsolvable boards before changing the game. Export copies the
initial grid. Portal codes require this variant; the reference accepts only
non-portal grids. Progress lives in memory; copy custom codes before closing.
The inherited Designer’s guide and Codex starter guide remain below the game.

## Validation

Run from the repository root:

```sh
python scripts/minigames.py check --owner yw4626
python scripts/minigames.py test --owner yw4626
```

14 tests cover inherited rules, portal pairing, both directions, stopping,
refused actions, same-position transfers, observation isolation, hints and
all eight solutions. Optional `tools/portal-ui-check.cjs` uses jsdom via
`GETOUT_JSDOM` to check eight UI groups without rendering a browser; it is
not a game dependency. Browser layout, touch input and human playtesting
remain unverified because browser access was denied.

`engine.js` exposes pure create/step/observe/legalActions/solve functions.
Observations show the public grid and legal moves, not solver answers.
No model player or live provider is connected.

## Attribution

Based on the course adaptation of Eric Zimmerman's *Get Out!*, exercise 11
in *The Rules We Break*, pp. 90–97; game sheets pp. 185–189. Reference boards,
workshop interface and guides come from `minigames/get-out/`. Book artwork
and prose are not bundled. The portal rule and four new layouts are variation
choices, not claims about the printed game.
