# Switchback — Design and playtesting

## Decisions

I chose a switch that alternates two groups of gates. Entering T immediately opens A and closes B, or reverses them; closed gates stop a slide. This applies the course's **perception / change in perspective** exercise, inspired by Schell Chapter 14 and Lens 58: The Puzzle. The intended discovery is that closing a door can help by creating a stopping point. The main level preserves the walls, start and exit of my classroom screenshot and adds one switch and three gates. A one-move tutorial explains the timing. The original classroom board remains selectable for comparison.

## Possible outcomes

The working prediction is that a player will initially seek open paths, then deliberately use closed B to stop at a new row and explain why closing it helped. A different outcome would be finishing through repeated guesses without understanding B, or confusing the mid-slide toggle with a change on the next turn. That would suggest the mechanic or its feedback is unclear, rather than demonstrate a satisfying insight. Completion time alone cannot distinguish these outcomes.

## Playtest

I designed the original classroom board shown in my screenshot, but I have not yet exchanged it with a classmate or watched a classmate play. No human playtest of this variation has been conducted. The observations below are a plan, not completed playtest evidence.

Plan: give Player A the tutorial and then the main board, without coaching. Allow undo, reset and optional hints. Record whether they predict the first switch's effect, where they stop after B closes, whether they deliberately return toward B, and any hints/resets. Ask afterward: “What were you trying to do?” and “What changed your understanding?” Record actual actions and remarks anonymously and separately from these predictions. A single playtest would be exploratory, and replaying the original board could introduce a practice effect.

## Next decision

Keep the main layout if the player deliberately uses B and can explain the stopping point. If timing is misunderstood, revise the tutorial or switch feedback first and test with a new player. If the rule is understood but the route is found only by guessing, simplify the approach to B rather than add more gates.

## Technical validation

Automated checks cover gate collision, immediate toggles, re-entry, multiple switches, blocked actions, exit crossing, immutable state, phase-aware solving and preserved classroom walls/start/exit. The main level has a verified 12-move shortest route and becomes unsolvable when its switch is removed. Browser checks cover tutorial and main completion, hints, undo/reset, editor switch painting, code export/reload, rejection of an unsolvable code, and direction buttons at 390px width (no horizontal overflow). Independent read-only code review reported no findings. The course scaffold check and all 14 game tests passed. The unrelated Python starter suite could not fully run because its provider dependencies (including anthropic) are not installed; its offline setup diagnostics also report missing Pyxel. No live-model calls were made. These are implementation checks, not human experience evidence.

## Remaining coursework

I confirmed the design intention: closing a gate can create a useful stopping point. TODO: exchange the original board with a classmate using Exchange a board and observe each other playing, as required by the first assignment step. Personally play the finished variation before submission. The new-variation peer playtest remains the clearly labeled plan above; no participant behavior or comments have been invented.
