# Get Out! — Think Before You Peek

Owner: `lfg2131` · Principle: `hints` · Status: draft; human evidence pending.

The student supplied this design and hypothesis before implementation. No human
playtest has been reported; technical checks do not establish understanding.

## Design and playtesting

### Decisions

I want to investigate whether progressively revealing help lets players discover
and understand a solution instead of simply following instructions. This applies
Schell's Chapter 14 / Lens 58 — The Puzzle to useful hints that preserve discovery.
The reference immediately supplies the next direction on a shortest route. My
one deliberate change replaces that answer with three optional requests:

1. **Think:** a concise question about useful stopping positions or exit alignment.
2. **Notice:** a truthful clue about a feature of a solver-verified route, such as
   the final approach's stopping point and its wall or border. It does not name
   the next movement direction; a generic truthful fallback covers other cases.
3. **Reveal:** clearly labeled direct solution help giving the solver's next move.

The UI shows assistance exposed and the next available request. Reveal exhausts
help for that position. Successful moves and undo clear progression; blocked
moves preserve it. Request totals survive moves/undo; reset or board load starts
a fresh counter and trace. Completion disables hints; unreachable states offer
honest undo/reset guidance. The engine, sliding rules, exit crossing, boards,
editor, exchange, and offline play remain unchanged. Hints are never required.

### Possible outcomes

**Prediction:** I expect some players to solve or make meaningful progress after
the first or second hint instead of needing the direct third hint. This would
suggest that progressive clues can support puzzle reasoning while preserving
discovery. A player explaining how a stopping point or alignment affected their
choice would provide stronger evidence than completion or speed alone.

- **A — All three hints immediately:** earlier hints may be too vague,
  insufficiently relevant, or difficult to apply.
- **B — Finish without explaining the clues:** completion alone does not establish
  understanding; success might come from following directions or trial and error.
- **C — Never use hints:** the board may be too easy or familiar. This does not
  establish that hints are unnecessary.
- **D — Frustration with extra requests:** disclosure may add friction without
  enough learning benefit. Establish this through actual comments/decisions and
  follow-up questions, not a trace alone.

These are predictions and possible interpretations, not observed outcomes.

### Playtest

**TODO — student:** manually play `minigames/get-out/index.html`, initially
without hints; note what you discovered and what the immediate hint changed.
Design a board, verify with **Check & play**, save its code, and exchange boards
with a classmate. Play theirs and observe them playing yours without coaching.
Keep your solution private.

For the focused variation test:

1. Give anonymous **Player A** an unfamiliar solvable board in this variation and
   its on-screen instructions. Record code, version, order, and prior familiarity.
   Do not coach or require thinking aloud.
2. Record hint levels and next actions, successful/blocked moves, undo, resets,
   completion, and a revealing decision or voluntary remark. Note possible clue
   use as an interpretation to check afterward.
3. Download traces before reset/board change, which clear the attempt. Keep
   separate anonymous notes; traces cannot show whether a clue was understood.
4. Ask: **“What were you trying to do?”** and
   **“What changed your understanding?”** Record actual answers; avoid leading
   questions about whether the hints were better.
5. For comparison, use different players or alternate order across pairs on
   unfamiliar comparable boards. Repeating a solution creates practice effects;
   shortest-path length alone does not match human difficulty.

Use this note form for each real attempt; leave it blank until observed:

| Field | Actual observation / record |
| --- | --- |
| Anonymous player; version; board code; order | TODO |
| Prior exposure to sliding puzzles / this board | TODO |
| Hint levels, next actions, blocked moves, undo, resets | TODO |
| Completion and revealing decision or actual remark | TODO |
| Answer: “What were you trying to do?” | TODO |
| Answer: “What changed your understanding?” | TODO |
| Interpretation, competing explanation, next test | TODO — separate from observations |

Use no personal data. A small classroom sample is exploratory; do not invent
statistics, quotes, emotions, or outcomes.

### Next decision

- **Expected outcome:** retain the three levels if early clues prompt explained
  progress. Test another unfamiliar board to see whether the reasoning transfers.
- **A:** revise the earliest ignored clue to point to a more usable relationship;
  retest one wording change before adding more help.
- **B:** use a fresh board involving the same idea and ask for the player's plan.
  Revise clues to support explanation if completion still depends on Reveal.
- **C:** test a more challenging or unfamiliar solvable board before changing
  hints. Avoid interpreting an unused feature as either success or failure.
- **D:** first improve the usefulness and clarity of the earlier clues. If actual
  evidence still shows unhelpful friction, consider testing a clearly labeled
  optional direct-reveal shortcut as a later experiment.

No outcome or human-driven revision is claimed. The student must interpret real
notes and choose what to retain or revise before marking the draft ready.

## Implementation and technical checks

`hints.js` derives clues from the existing rules/solver; `app.js`, `index.html`,
and `style.css` present help and trace requests. `tests/` checks rules and hints;
README documents play and checks.

Executed on October 16, 2026, using Node 24.15.0 and Python 3.13.3:

| Check | Actual result |
| --- | --- |
| `python3 scripts/minigames.py check --owner lfg2131` | Pass: one valid personal submission. |
| `python3 scripts/minigames.py test --owner lfg2131` | Pass: 22 tests, zero failures (7 inherited engine, 6 hint, 9 app integration). |
| `node --check` on `app.js`, `hints.js`, and both added test files | Pass. |
| `.venv/bin/python -m unittest discover -s tests -v` | Pass: all 43 repository tests. |
| `uv run --frozen python -m course_game.setup_check --offline --headless` | Pass on final run: Python, Git, GitHub authentication, Pyxel, deterministic tests, explicitly labeled offline fixture. Partial Setup Verification only; no live provider call. |

The added deterministic tests exercise 42 reachable teaching-board states and
226 states across 36 seeded custom boards. They check clue truth, solver
agreement, immutability, short routes, unreachable/terminal states, hint levels,
counts, JSON traces, blocked moves, undo/reset, imports, editor cancellation,
keyboard and synthetic touch. A solvable custom board can lead into a trap;
the app test verifies honest recovery, ignored extra requests, and undo recovery.

Headless Chrome passed at 1280 × 900 and a 320 × 740 touch viewport. Checks
included a complete no-hint puzzle run, all hint levels, real JSON download,
counts, terminal input, keyboard movement, undo/reset, editing a wall, custom
export/reload, invalid and unsolvable imports, both workshop guides, touch
buttons and an actual swipe. Both layouts fit without horizontal overflow;
reduced motion disabled the player transition. Screenshots were inspected.
No JavaScript page errors occurred. Local-file play and a hint worked with the
browser offline. The in-app browser had no connection; this check used a
separate headless Chrome session and a temporary Playwright smoke script.

Initial system-Python checks failed because its environment lacked dependencies
(the unit suite could not import `anthropic`; the Pyxel diagnostic also failed).
The existing project environment resolved those checks. An initial project
setup run reported an authentication failure; separate `gh auth status` and the
final setup retry passed. These earlier failures are not counted as passes.

Known limits: custom clues describe one shortest route, although other routes
may exist. On a very simple board a relevant clue may still make the answer
obvious. Progress and traces live only in memory until downloaded; resets clear
the attempt. The spatial interface has not been established as a complete
screen-reader-only experience. Human usefulness remains untested.

## AI assistance and human decisions

The student supplied the title, principle, design, prediction, alternatives, and
human-test questions. Codex generated code/tests, helped structure the report,
and arranged a separate technical review; executed results are recorded above.
The student retains interpretation/approval; the instructor controls
merging. No runtime model, network call, or paid service is required.

**TODO — student:** complete reference play, design/exchange, and observation;
supply anonymous notes, interpretation, and one decision retained or revised.
No human activity is marked complete.

## Independent review

A separate Codex reviewer, uninvolved in implementation, read the instructions,
reference, variation, tests, manifest and reflection. It found no substantive
issues. The reviewer independently enumerated 10,224 valid small boards and
34,464 reachable states to check clue truthfulness, solver consistency,
immutability, unreachable and terminal handling; all checks passed. It also ran
the owner validation and then-current 21 tests. The later trap integration test
brought the final owner suite to 22 passing tests. No fixes were required.

The engine, levels and inherited rule tests are byte-identical to the reference;
the submission changes only the personal folder. The reviewer did not perform
browser rendering or assistive-technology testing; the primary agent performed
the browser checks above. Neither review nor automation establishes human
usefulness. Keep the PR draft until the student supplies actual play evidence,
interprets it, chooses a next decision, and completes the ready check. No gate
approval or merge was performed.
