# Get Out: Blue & Orange — design and playtesting

## Decisions

Student request: “删去之前新的设计的全部文件，重新设计游戏。只保留传送门思路。前面的4关不变，然后多设计四关加入传送门的版本，传送门应该是蓝色和橙色。”

The original four boards, names and prompts are unchanged.
Four new boards teach a paired connection, finding an entrance, reverse use,
and a combined route. This applies the course's sequence principle to the
Schell Chapter 14 / Lens 58 exercise; it is an interpretation, not a quotation.

Colors and the eight-board structure are the student's decisions. Codex
proposed one bidirectional pair and stopping after teleportation. These are
labeled assumed rules in the local map.

The student also requested a visible minimum solution length “以此激励玩家不断尝试”
(to encourage repeated attempts). The right sidebar shows the fixed minimum
from the starting board, with feedback for matching it or finishing above it.
This adds a concrete replay goal without revealing the move sequence.

## Possible outcomes / prediction

TODO (student): write your prediction and reasoning in your own words.
Suggested question: after the first portal board, can a player predict where
the move stops and recognize that either color can be an entrance?
Possible success: deliberate reverse use on puzzles 7–8. Alternative: trying
to keep sliding on arrival, or treating orange as exit-only. These would
suggest revising the explanation or the first example.

## Playtest

The student confirmed that no classmate has played this version yet. Proposed
peer test: play puzzles 5–8 without
coaching; predict portal move endpoints. Record anonymous player labels,
hints, resets, transfer directions and revealing remarks. Separate behavior
from interpretation. Observe whether the minimum-move target prompts deliberate
retries and revised routes, or discourages a player after a longer solution.
Familiarity and learning order limit small-sample findings.

Five initial portal tests failed on the reference engine before implementation.
A further test caught same-position transfers mistaken for blocked moves;
it failed before the fix. All 14 rule/campaign tests and eight browser-free
DOM groups now pass. New boards all require portals; shortest paths have
4/6/8/10 moves and 1/1/2/2 transfers. Automated reachability does not establish
a smooth human difficulty curve.

UI checks cover all eight solutions, hints, colors/labels, undo/reset, exchange,
editor validation, minimum targets and completion feedback, and Watch solution
completion/cancellation preserving progress.
Browser access was explicitly denied, so rendered desktop/narrow layouts,
swipe controls and experience remain manual checks.

Owner validation passed. The separate repository Python starter suite ran
35 tests with three environment errors: two Windows symlink-privilege errors
and the missing `anthropic` package. These are not reported as passes. The
browser minigame does not depend on these Python/provider components.

## Next decision

TODO (student): interpret a real peer test and decide what to retain or revise.
If players transfer the portal rule and voluntarily improve their route, retain
the sequence and visible target. If they misread arrival behavior, revise the
first portal lesson or its explanation. If the target discourages exploration,
try showing it only after the first completion. These are conditional proposals,
not changes supported by observations yet. Choose the revision from what the
peer misunderstood, not completion time alone.
No human observations or student judgments are fabricated.

## Independent review

A separate read-only rules reviewer inspected engine, interface, campaign,
styles, rule map and tests, independently ran all 14 rules/campaign tests,
and reported “No findings.” They did not operate a browser. Student and
instructor judgment still govern the design and any submission.

A fresh PR review also checked the minimum-moves feature, custom-board changes,
undo/reset and walkthrough restoration. The reviewer independently ran 14 rule
tests, the then-current seven DOM groups, and additional target/feedback checks,
reporting “No findings.” Minimum-target regression checks were subsequently
added to the committed UI suite; all eight groups passed locally.
