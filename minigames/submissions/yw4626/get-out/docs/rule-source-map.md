# Portal variation: rule/source map

Paths are relative to this personal game folder. Reference and shared tools stay unchanged.

| Rule | Evidence | Implementation / acceptance |
| --- | --- | --- |
| Keep the original four puzzles unchanged; add exactly four portal puzzles. | manual: student's request | levels.js; tests/portal.test.cjs |
| There is one blue B and one orange O portal, or neither. | manual: colors; assumed: one pair and grid encoding | engine.js create; tests/portal.test.cjs |
| Sliding into either portal transfers to the other and stops the move there. Leaving a portal does not teleport; reentering does. Portals are bidirectional. | assumed: explicit design proposal in this conversation | engine.js step; tests/portal.test.cjs |
| A teleport costs one move including the slide. Blocked/unknown actions do not mutate state. Undo and reset restore exact positions and counts. | code: inherited movement; assumed: teleport cost | engine.js step; app.js; tests/portal.test.cjs |
| Hints search stopping positions under the portal rule. The board, including portal locations, is visible; observations are detached and contain no solution. | code: inherited public-board interface | engine.js observe/solve; tests/portal.test.cjs |
| Board exchange uses plain grids including B/O, validated before replacing the live game. | assumed: extension of inherited grid exchange | engine.js create; app.js loadCustom |
| Show the minimum solution length from the starting board as a fixed replay target; compare completed runs with it. | manual: student's request to encourage retries; code: existing shortest-path solver | app.js:16; tools/portal-ui-check.cjs |

Human difficulty remains untested. Evidence labels remain unchanged.

## Implementation and acceptance anchors

| Rule group | Code | Tests |
| --- | --- | --- |
| Four original + four portal puzzles | levels.js:3 | tests/portal.test.cjs:32 |
| Pair validation | engine.js:5 | tests/portal.test.cjs:19 |
| Entry transfers in either direction and stops | engine.js:22 | tests/portal.test.cjs:4, tests/portal.test.cjs:10 |
| Refused actions; same-square trip costs a move | engine.js:22 | tests/portal.test.cjs:15, tests/portal.test.cjs:28 |
| Detached observation; portal hints | engine.js:46, engine.js:50 | tests/portal.test.cjs:19, tests/portal.test.cjs:24 |
| Rendering, editor and exchange | app.js:46, app.js:112 | tools/portal-ui-check.cjs |
| Undo/reset and walkthrough preserve progress | app.js:14, app.js:73 | tools/portal-ui-check.cjs |

No files, credentials or solver answers are provided through observe.
The fully visible board is inherited reference behavior. No model is connected.
