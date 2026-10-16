# Get Out experiment: howrdwng

Principle: progress

## Prediction

I added a visible trail of stopping positions. This uses the Chapter 14 / Lens
58 idea that a puzzle should give understandable feedback without giving away
the answer. I expect a player to notice repeated routes and try a different
direction sooner. If the dots are ignored, feel cluttered, or are mistaken for
the correct path, that would challenge the design.

## Implementation

`app.js`, `index.html`, and `variation.css` add a small dot to each stopping position
and a truthful explored-stop count. Undo keeps the trail because the stop was
still explored; reset and changing puzzles clear it. The trail is hidden while
editing. Movement, collision, exit, hint, undo, and solver rules are unchanged.

Checks on October 17, 2026: `python scripts/minigames.py check --owner howrdwng`
reported one valid submission, and `python scripts/minigames.py test --owner
howrdwng` passed 7/7 tests. A Chromium browser check confirmed the two-stop
trail, undo, reset, hint, three-move completion, editor, invalid-import error,
and a 390 px layout without horizontal scrolling.

## Playtest observations

TODO after a real playtest: Ask Player A to try Puzzle 2 without coaching. Watch
whether they use a dot to avoid repeating a route, request a hint, reset, and
finish. Ask, “What were you trying to do?” and “What did the dots mean to you?”
Record actual behavior separately from this prediction.

## Interpretation and revision

If Player A uses the trail to choose a new route and describes it as exploration,
I would keep it. If they treat it as a solution path, I would reduce its visual
weight or change the label. If it is ignored, I would test a short one-time
prompt. One player is exploratory evidence, and prior experience with the board
could make the result look better than it is.

## Independent review

An independent reviewer checked the full student folder, manifest,
experiment write-up, branch boundary, and game behavior. It found no new runtime
logic bug. It confirmed the owner check, 7/7 engine tests, and JavaScript syntax.
It also identified that the copied README still pointed to the instructor game;
those paths now point to this variation. The reviewer correctly kept the missing
human playtest separate from browser and rule evidence, so this remains a draft.
The student and instructor retain approval decisions.
