# Independent review: Prince of Persia: One Room

- Commit reviewed: `10301f3` on `alsjoee/midterm`.
- Reviewer: Claude Code (`claude-opus-5-5`), 2026-11-06, following `.claude/agents/rules-reviewer.md`. Some commits in this folder are also credited to Claude Code; this review had no access to those sessions.
- This is not an approval. The student decides what happens with these findings.
- Result: 3 blocking, 10 should fix, 13 notes.
- Paths are relative to `midterms/alsjoee/` unless they start with `.github/`, `.claude/` or `course_game/`.

## Findings, most serious first

- [blocking] pop_room/model_player.py:233: a timeout has no terminal reason. A timed-out call becomes a fallback `wait` (lines 241-244) and play continues. With a client that always times out, the outcome was `{'reason': 'step limit', 'score': 0}`. A client that always raises gave the same reason after 40 calls. There is no per-episode time limit either, so one outage can last 40 x 30 s = 20 minutes and is then reported as if the player had run out of steps.
- [blocking] pop_room/__main__.py:46: `play` crashes when the Prince falls off the map. `printf 'right\nright\n' | python -m pop_room play --room A` ends in `IndexError: list index out of range` at pop_room/rules_text.py:41, before the outcome prints. The cause is pop_room/world.py:112-115, which leaves `row` equal to the grid height, so the final observation reports `{'row': 1, 'col': 2}` on a 1-row map. `baseline`, `model` and `evaluate` do not render after the end, so they are not affected.
- [blocking] pop_room/world.py:114: falling off the bottom kills the Prince, but neither README.md nor the player's rules say so. README.md:23 says a fall reaches "the floor below", and pop_room/rules_text.py:17 says only "you fall". This decides real results: 8 of the 48 current traces end `died: fell off the bottom`, which is all 8 `gemini-3.5-flash-lite` episodes in room A. Map-view prompts never state the rule. The local view does, and those 4 episodes died the same way, so the missing rule is not shown to be the only cause.
- [should fix] pop_room/baseline.py:40: BFS simulates moves with the real `World`, so it knows the rules players are not given (falling off the bottom, the gap above a wall, waiting on the plate) and avoids those deaths at lines 43-44. It reads no hidden state, but the BFS and model comparison is not on equal rule knowledge until those rules are in pop_room/rules_text.py.
- [should fix] pop_room/model_player.py:146: the local view tells the model two rules that map view never states: "you would fall off the map" and, at line 142, "you would stop on top of it". The map and local comparison therefore differs in rule knowledge as well as presentation, and README.md:169-170 describes it only as a line naming nearby tiles.
- [should fix] pop_room/model_player.py:273: fallback waits go into the model's memory and are shown under "Your last N moves" (lines 190-191). The model is told it made a move it did not make. In the current traces, 9 prompts directly after a fallback show it this way, for example `traces/H-seed2-h5-local-gemini-3.8-flash.jsonl`, record index 8 ("- wait: wait").
- [should fix] pop_room/evaluate.py:38: `results.csv` and `summary.md` have no model-moves figure. Only the JSONL trace summaries keep `model_moves`, and the table's "Mean steps" includes fallback waits. For example, `B-seed2-h0-local-gemini-3.8-flash` is a win in 29 steps, 11 of them fallbacks, so 18 were model moves. All 7 current traces with fallbacks are wins. Fallbacks also use up steps and tick the gate timer (pop_room/world.py:100), so provider errors change the game the model is playing. README.md never mentions fallbacks.
- [should fix] pop_room/world.py:101: standing on the plate reopens the gate every turn, so `wait` on the plate holds it open indefinitely. tests/test_world.py:189 shows this is intended, but README.md:28 and pop_room/rules_text.py:32 say only "stepping" opens it for 3 turns. It is reachable in rooms A, C and H.
- [should fix] pop_room/episode.py:65: an invalid action uses a step but does not tick the gate (lines 72-74). Neither README.md nor pop_room/rules_text.py says this, and "invalid" appears in none of the 584 current prompts. A human's typo in `play` silently costs a step.
- [should fix] tests/test_model_player.py:98: the only timeout test checks the fallback label. It asserts no terminal reason, because `max_model_calls=1` ends that episode. CI.md:18 lists no timeout test under episode limits.
- [should fix] tests/test_evaluate.py:279: this is the only test that drives the command line, and it runs only `evaluate`. Nothing runs `play` or `baseline`, and tests/test_episode.py:151-155 checks the fall-off reason without rendering, so all 128 tests pass with the `play` crash present.
- [should fix] .github/workflows/midterm-alsjoee.yml:3: this workflow has not been seen running. It triggers only on `pull_request`, no pull request exists for this branch in the fork or upstream, and `gh run list` returns 404 because the workflow is not on the fork's default branch. Only local runs are evidence so far.
- [should fix] README.md:218: the links to `EVALUATION.md` (line 218) and `AGENT-TEAM.md` (line 219) point to files that do not exist. The recording at line 222 is still "to be added".
- [note] pop_room/world.py:47: gates block only horizontal moves and climbing. A fall can land on a closed gate: `World(['S ', '.G'])` after `right` puts the Prince at (1, 1) with the gate closed, despite README.md:28. No declared room has a gap above a gate. Separately, the Prince can stand in a gate as it closes, which I reproduced in room A at column 6.
- [note] pop_room/baseline.py:20: the private model overwrites the tile under the Prince with `S`, so `wait` on a plate ticks to 2 there but stays at 3 in the real World. This is the only difference found across all reachable state and action pairs (one pair each in A, C and H). It changes no plan: all four plans equal an independent BFS on the real World.
- [note] pop_room/model_player.py:27: the default model-call limit of 60 cannot fire, because each call uses a step and steps stop at 40 (an always-failing client made 40 calls). The limit code works when set below 40, and README.md:172 ("at most 40") is correct.
- [note] pop_room/model_player.py:229: abandoned threads are not truly abandoned at exit. With a 2 s stuck client and a 0.01 s timeout, the episode returned in 0.01 s but the process took about 2.1 s to exit. The real client's HTTP timeout should bound this. No committed fallback came from this local timeout: the 25 current fallbacks are 14 server 504s, 10 server 429s and 1 server 500.
- [note] pop_room/model_player.py:289: failed calls add 0 tokens, so their cost shows as 0 rather than `unknown` (pop_room/evaluate.py:125-127). This affects the 25 current fallback calls. Whether any of them was billed was not checked.
- [note] pop_room/model_player.py:113: the parser takes the first legal action word anywhere in a reply, so "You're right, I'll climb" plays `right`, and "Don't go left" plays `left`. tests/test_model_player.py:52 makes this deliberate. Actual risk looks low: 1 of 918 committed replies was not an exact action word (`wait)`).
- [note] README.md:31: rule 13 has no player-facing text, and no declared room has a gap directly above a wall. The gap clause in tests/test_invariants.py:62-63, which CI.md:14 counts as covering every reachable state, is therefore never exercised by that walk. Only the synthetic layouts in tests/test_regressions.py test the rule.
- [note] README.md:22: rule 4 and pop_room/rules_text.py:27 do not say that climbing requires floor, start, plate, exit or an open gate above (pop_room/world.py:64). A player can only learn this from the legal-action list.
- [note] README.md:19: rules 1, 2, 10, 12 and 13 use the label `design`, which is not one of `code`, `manual`, `observed` or `assumed` (.claude/skills/rule-change/SKILL.md:16). No row cites a file and line. Rules 3-9 and 11 stay `assumed` from memory, and rule 1's claim about the original's health is unsourced.
- [note] README.md:51: "row 2, column 2" counts from 0 (as CI.md:25 says), but README.md:36 says row 1 is the top floor.
- [note] README.md:193: the small `evaluate` check is refused if run after the full suite, because its trace already exists. The error message explains why, but the README does not warn about this order.
- [note] pop_room/__main__.py:154: `evaluate` defaults to rooms A, B and C, leaving out H. The README commands name H explicitly, so they are correct.
- [note] tests/: nothing tests that `VertexClient` sends no tools, or that BFS ignores anything beyond the observation. Both held when I checked them for this review, but CI would not catch a future change. pyproject.toml:7 also allows `google-genai>=1.0`, while pop_room/model_player.py:75-78 was checked only against 2.23.0.

## What was checked, by area

### Rules in README.md against pop_room/world.py
- Checked: all 13 rows against `world.py` and the tests, the four room layouts in README.md against `rooms.py` (identical), and declared shortest solutions with an independent BFS on the real World (A 7, B 10, C 8, H 10).
- Agrees: rules 1, 2, 3, 6, 7, 8, 9, 11, 12 and 13, plus the 3-turn gate count.
- Problems: fall-off death (blocking), holding the plate, invalid actions and steps, closed-gate landing, and climb targets.
- Declared rooms: H, A and C are unchanged since `b188c61` (2026-10-26). B was changed by the wall fix, and README.md:51 discloses that.

### observe() and legal_actions()
- Checked: pop_room/episode.py:38-55, every use of `gate_turns`, `_world` and `to_dict`, and all 584 prompts in the current traces.
- No problem found: the observation has the seven expected keys, the gate is only "open" or "closed", and the start tile is drawn as floor. `gate_turns` appears in no prompt, and `legal_actions` depends only on position, map and gate state, all of which are observed. A refused action changes no state.
- Problems: the off-grid position in the final observation (blocking, above). No countdown or other hidden state leaks.

### Model player boundary and fallbacks
- Checked: `build_prompt`, `ModelPlayer`, `run_episode`, and `VertexClient` against `google-genai` 2.23.0 with a stubbed client (no network).
- No problem found: the player holds only a client and receives only the observation and legal actions. The request has `tools=None`, `tool_config=None`, automatic function calling off and one attempt. The player has no file access, World object or credentials path of its own.
- Fallback counting: `fallback` is labelled on every record, and `model_moves = records - fallbacks` was correct in all 48 current trace summaries.
- Problems: fallbacks presented to the model as its own moves, and missing from the results files as model moves (both should fix).

### Limits and terminal reasons
- Step limit: enforced in pop_room/episode.py:87, reason `step limit`, tested, and a win on the last step takes priority. No problem found.
- Model-call limit: enforced in pop_room/model_player.py:267, reason `model-call limit`, tested, and failed calls count. It cannot fire at default settings (note).
- Timeout: a 30 s limit is enforced per call (HTTP setting and `result(timeout=...)`), but it has no terminal reason (blocking).

### BFS baseline
- Checked: pop_room/baseline.py in full, and a plan made from a JSON copy of the reset observation.
- No problem found on hidden state: it imports no episode or room data, reads only `map`, `prince`, `health` and `gate`, and takes gate timing only from its own simulation of the rules.
- Problems: rule knowledge players lack (should fix) and the plate difference in its private model (note).

### README commands from a fresh clone
- Ran, from the clean working tree: `play`, `baseline` on all four rooms, and the tests. `model` without cloud settings exits with a clear message before any call. `play`, `baseline` and the tests also ran with `python -S`, which confirms they need no installed packages.
- Confirmed by `git ls-remote`: both clone sources exist, and the fork branch is at `10301f3`. The clean tree means the tracked files match a clone. `.venv/` in this folder is ignored, so it cannot trip the dirty-tree check.
- Confirmed by reading: `model` and `evaluate` argument handling, the 24-episode and 640-call arithmetic, seed 3 being unused, and `rm traces/*.jsonl` plus `git restore` both falling within the paths the dirty-tree check ignores.
- Problems: the `play` crash (blocking), dead document links (should fix), and the small-check order (note).

### CI and the five check kinds in CI.md
- Checked: the workflow file, every test name in CI.md (all exist), and a full local run: 128 tests pass on Python 3.14 and 3.13, including with cloud variables unset.
- Each of the five kinds has tests: rule invariants, legal and illegal actions, terminal outcomes, observed regression, and episode limits. The workflow uses no secrets and blank cloud settings.
- Regression claims tested in memory: all 7 `WallLandingBug20261104Test` tests fail against the `2862f33^` rules and rooms. Both `FinalStepRegressionTest` tests fail when the old check is patched back in. `expectedFailure` and the single known state `("B", 2, 2)` are present at `ac601e2`.
- Problems: no timeout or `play` coverage (should fix), and the workflow has not been seen running (should fix).

## Not checked

- The midterm brief is not in this repository. I used the requirements given for this review, plus README.md:259 and course_game/player_interface.py. Other brief requirements were not assessed.
- No clone, virtual environment or `pip install` was made, because this review could create only this file. Setup steps 1 and 2 were checked by reading, not by running them. The tests' own temporary directories were the only other files created, and they clean themselves up.
- No live model call was made, so nothing was spent. `model` and `evaluate` were not run against Vertex AI, and token and price figures were not compared with billing.
- Python 3.11 and 3.12 are not installed here, so the README's 3.11 claim and CI's 3.12 were not reproduced.
- macOS only; Linux was not run. Rule accuracy against the original 1989 game was not checked.
- The rules-reviewer definition lists only Read, Grep and Glob. I also ran commands, with bytecode writing off, to confirm behavior. `git status` was clean until this file was written, and this file is the only change.
