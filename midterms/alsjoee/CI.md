# CI

Workflow: `.github/workflows/midterm-alsjoee.yml`. It runs on pull requests
that change `midterms/alsjoee/**` or the workflow itself. It installs only the
dependencies in this folder's `pyproject.toml`, then runs
`python -m unittest discover tests` from `midterms/alsjoee/`. It uses no
secrets, and the cloud settings are blank, so no model can be called. Every
model-player test uses a fake client.

## Check kinds and the tests that cover them

| Check | Tests |
|---|---|
| 1. Rule invariants | `test_invariants.py`: every reachable state in rooms A, B, C and H is checked. The Prince stays on the grid (except when he falls off the bottom, which ends the game), is never inside a wall, and is in a gap only directly above a wall. Health and the gate timer stay in range. The status matches the tile under him. Wait is legal exactly while playing. Illegal actions raise and change nothing. |
| 2. Legal and illegal actions | `test_world.py`: `WalkTest`, `JumpTest`, `ClimbTest`, `WaitTest`, `GateTest` (closed gate blocks, open gate allows). `test_episode.py`: `test_invalid_move_counts_as_step_without_changing_world_or_gate`, `test_non_string_action_is_invalid`. `test_model_player.py`: `test_reply_without_legal_action_counts_invalid`. |
| 3. Terminal outcomes | `test_episode.py` `OutcomeTest`: win (`test_win_on_last_step_beats_step_limit`), death (`test_died_on_spikes`, `test_died_falling_off_bottom`), step limit (`test_step_limit_after_40_steps`). `StepTest.test_win_room_a_in_seven_moves`. `test_world.py` `ExitTest.test_no_actions_after_game_over`. |
| 4. Observed regression | `test_regressions.py` `WallLandingBug20261104Test`: a fall could land the Prince inside a wall (details below). `FinalStepRegressionTest` covers an earlier bug. |
| 5. Episode limits | Step limit: `test_episode.py` `test_step_limit_after_40_steps`, `test_invalid_actions_also_reach_step_limit`, `test_steps_after_end_are_refused_and_not_counted`. Model-call limit: `test_model_player.py` `test_model_call_limit_ends_episode` (failed calls count toward the limit). |

## The observed regression

**Wall landing.** A fall stopped on the first tile below that was not a gap,
and a wall counted as one, so the Prince could end up inside a wall. The
invariant test `test_prince_is_never_inside_a_wall` found this on 2026-11-02,
in exactly one reachable state: room B, row 2, column 2 (counting from 0). Room
B's declared 10-move shortest solution went through that state, so the
evaluation results for B up to and including commit `ac601e2` are pre-fix. The
test was marked `expectedFailure` until the fix on 2026-11-04. Walls are now
solid, a fall stops on the empty tile directly above a wall, only floors
actually dropped count, and that wall in room B became floor. The shortest
solution is still 10 moves. The new tests failed before the change. Evaluation
summaries show the earlier rows as `B (pre-fix)`.

## An earlier bug

**Final step rejected.** Found by the episode tests on 2026-10-27, while
`pop_room/episode.py` was being written, and fixed before commit `f2ed3ab`.
`step()` adds 1 to the step count before it checks the action. The first
version checked the action with `self.legal_actions()`, which returns nothing
once the episode looks finished. So on the last allowed step the move was
always rejected as invalid, and a room needing exactly the step limit could
never be won. The fix asks the World for its legal actions instead.

The broken version was never committed, so git history doesn't show it. The
account comes from the 2026-10-27 development session. I checked that both
tests in `test_regressions.py` fail when the old check is patched back in.
The starter's `course_game/player_interface.py` has the same pattern.

Not counted as a regression: `test_shipped_placeholder_gives_unknown` failed
after real prices were entered in `prices.json`. That test depended on the
data file's contents. The code had no bug, and the test was rewritten to use
a temporary file.
