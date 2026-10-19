# Design and playtesting

## Decisions

I chose three hint levels: a question, a useful feature, then the next move.
I want a stuck player to feel willing to continue, even if they eventually need
the direct answer. This applies the course's progressive-hints exercise for
Schell, *The Art of Game Design*, third edition, Chapter 14 and Lens 58: The
Puzzle. It is a classroom application, not a quotation from the book.

The sliding rules, exit detection, boards and shortest-path solver stay the
same. Hints are optional. A successful move or undo starts the hint sequence
again at the new position; a blocked move preserves the current clue.

## Possible outcomes

My prediction is that a small nudge can make a stuck player more willing to
try another move. I am not predicting that they will never need level three.
An alternative is that the first two levels feel like extra clicks and the
player immediately asks for the answer. That would question whether the
earlier clues are useful enough. Completion or speed alone cannot show
whether someone felt encouraged.

## Playtest

I played the reference and completed the board-design/exchange activity. After
exchanging boards, I carried over the previous approach, then realized I had
to rethink the route. I paused to compare choices and hesitated about trying
again. I felt some frustration, but also curiosity about the intended solution.
This is my reference-game experience, not evidence that the variation helped
another player. No exact move count or board code was recorded here.

The variation has not yet had a confirmed human playtest. Give Player A a board
without coaching and let them choose whether to request hints. Watch whether
they attempt another move after each level, ask for more help, reset or stop.
Record the board and order, then ask: "What made you keep trying or stop?"
Use a different comparable board for a second attempt; repeating a known
solution introduces a practice effect. The downloaded trace records hint
levels and actions, not feelings.

## Next decision

If the first two levels feel unhelpful, I would keep the staged clues but add
an explicit option to request the next move immediately. If the player says
the early clues helped them continue, I would keep them and try another
unfamiliar board. The question is whether the extra choice supports continued
play, not whether everyone uses fewer hints.

## Checks and limitations

Implementation: `hints.js` supplies state-aware clues; `app.js`, `index.html`
and `style.css` add the sequence and persistent clue panel. Trace export keeps
the existing format marker and adds the requested levels and counts. The pure
rules and reference sources are unchanged.

Owner validation and report validation passed. All 11 deterministic game/hint
tests and all 83 Python tests (including the lab tooling tests) passed in an
isolated environment installed from the course lockfile. Offline headless setup
diagnostics and gallery generation passed; no live model request was made. A local jsdom integration
check passed eight groups of UI lifecycle cases, including hint progression,
move/undo/reset clearing, editor cancellation, board imports, completion and
trace export. This is a simulated DOM check, not a real-browser playtest.

A separate code reviewer found no blocking defects, reran the 11 game tests,
and independently checked the UI lifecycle with a mocked DOM. The rules engine,
teaching boards and original engine tests are byte-identical to the reference.

Real-browser, phone and human-play checks remain manual: the browser tool
blocks opening local file URLs. No successful real-browser or peer-variation
test is claimed here.

At PR creation, GitHub's submission-boundary check passed. The full Minigame
lab and Setup workflows require a course maintainer to approve this fork's
workflow runs; they are not being reported as passing CI.
