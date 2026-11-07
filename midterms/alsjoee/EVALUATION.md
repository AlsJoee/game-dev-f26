# Evaluation: Prince of Persia: One Room

Sources: [results/results.csv](results/results.csv), [results/summary.md](results/summary.md), [traces/](traces/), [explanations/](explanations/), [CI.md](CI.md) and the git log. `results.csv` has 90 rows: 30 BFS and 60 model episodes.

## Declared suite

Rooms A, B, C and the held-out room H were declared on 2026-10-26 in commit `b188c61`, with 2 trials for each situation.

**Correction to room B.** Commit `2862f33` (2026-11-04) changed row 3 of room B from `..#  ...#` to `...  ...#` and made walls solid. An invariant test, `test_prince_is_never_inside_a_wall`, had found that a fall could put the Prince inside that wall. The regression test is `WallLandingBug20261104Test` in [tests/test_regressions.py](tests/test_regressions.py), which includes `test_room_b_wall_became_floor`. The shortest solution stayed at 10 moves.

Room B was rerun at commit `519909c`. Earlier room B rows are reported as "B (pre-fix)". CI.md records the wall state as reachable only in room B, and rooms A and C were not rerun.

**Room H.** H was never used for tuning. Its layout has not changed since `b188c61`. Its first results are the rows at commit `cbdf1ed`, and those rows use the same Rules text as the A, B and C rows. The only prompt change made after those rows is `d2b9e72`, and no row in `results.csv` uses it.

### Evaluation runs

| Row date | Row commit | Results committed in | Rooms | Players |
|---|---|---|---|---|
| 2026-11-02 | `b31388b` | `ec1101e` | A, B (pre-fix), C | BFS; gemini-3.5-flash-lite map |
| 2026-11-02 | `9fe5c19` | `bcb4117` | A, B (pre-fix), C | BFS; gemini-3.5-flash-lite local |
| 2026-11-02 | `c028466` | `c55b8be` | A, B (pre-fix), C | BFS; gemini-3.8-flash local |
| 2026-11-04 | `519909c` | `cbdf1ed` | B | BFS; all three model configurations |
| 2026-11-06 | `cbdf1ed` | `10301f3` | H | BFS; all three model configurations |

Each model configuration ran with history 0 and 5, using seeds 1 and 2. BFS ran in every evaluation command for its rooms, so it has 6 trials per room rather than 2.

## Players and configurations

| Player | Views | History |
|---|---|---|
| BFS baseline | - | - |
| gemini-3.5-flash-lite | map, local | 0, 5 |
| gemini-3.8-flash | local | 0, 5 |

- **Views.** Local view adds a "Next to you" line to the map view's prompt. The line names the adjacent tiles and can include what a fall would do, for example "you would fall off the map".
- **History.** With history 5, the prompt also lists the last 5 moves.

### Limits

- **Per-call timeout: 30 s.** A failed or timed-out call plays `wait` as a labelled fallback. That step counts as a step and as a model call, and it records no tokens.
- **Fallback causes.** All 29 fallbacks in the rows are server errors: 16 of 504 `DEADLINE_EXCEEDED`, 12 of 429 `RESOURCE_EXHAUSTED` and 1 of 500 `INTERNAL`. The slowest recorded call took 28.84 s, and no trace records a local timeout. All 29 are gemini-3.8-flash calls, in 9 episodes that all reached the exit.
- **Step limit: 40 steps per episode.**
- **Model-call limit: 60 calls per episode**, recorded as `max_model_calls` in every model trace. Each call uses a step, so the 40-step limit always comes first. The most calls in any row is 40, and no row ended with reason `model-call limit`.
- **Limits that did not apply to these rows.** Commit `d2b9e72` (2026-11-06) added a 600 s episode limit and a limit of 5 failed calls in a row. In the rows, the longest episode took 330.879 s of model latency and the longest failure streak was 4.

### Prompt version

All rows used the earlier prompt. The Rules text is identical in all 60 model rows. It does not state that falling off the bottom of the room kills the Prince, and with history on, a fallback appears as an ordinary move (`- wait: wait`).

Commit `d2b9e72` added the fall-off rule and a fallback label to the prompt. The rows were not rerun.

## Comparison

- **Wins/trials and mean steps.** Mean steps include fallback waits.
- **Totals across a cell's trials.** Invalid actions, fallbacks, model calls, tokens and estimated cost.
- **Mean latency per episode.** The mean of `total_latency_s`, the same figure as "Mean latency" in `summary.md`.
- **Mean latency per call.** Total latency divided by model calls, including failed calls.
- **Tokens.** Input plus output. Output includes thinking tokens.

| Player | View | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks | Model calls | Mean latency per episode (s) | Mean latency per call (s) | Tokens | Est. cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BFS | - | - | A | 6/6 | 7.0 | 0 | 0 | 0 | 0.00 | - | 0 | 0.000000 |
| BFS | - | - | B | 6/6 | 10.0 | 0 | 0 | 0 | 0.00 | - | 0 | 0.000000 |
| BFS | - | - | C | 6/6 | 8.0 | 0 | 0 | 0 | 0.00 | - | 0 | 0.000000 |
| BFS | - | - | H | 6/6 | 10.0 | 0 | 0 | 0 | 0.00 | - | 0 | 0.000000 |
| gemini-3.5-flash-lite | map | 0 | A | 0/2 | 2.0 | 0 | 0 | 4 | 2.43 | 1.21 | 1278 | 0.000392 |
| gemini-3.5-flash-lite | map | 0 | B | 0/2 | 26.5 | 0 | 0 | 53 | 30.15 | 1.14 | 18430 | 0.005650 |
| gemini-3.5-flash-lite | map | 0 | C | 0/2 | 3.0 | 0 | 0 | 6 | 3.22 | 1.07 | 2002 | 0.000614 |
| gemini-3.5-flash-lite | map | 0 | H | 0/2 | 4.0 | 0 | 0 | 8 | 5.01 | 1.25 | 2793 | 0.000855 |
| gemini-3.5-flash-lite | map | 5 | A | 0/2 | 2.0 | 0 | 0 | 4 | 1.96 | 0.98 | 1310 | 0.000402 |
| gemini-3.5-flash-lite | map | 5 | B | 0/2 | 23.0 | 0 | 0 | 46 | 27.08 | 1.18 | 17516 | 0.005360 |
| gemini-3.5-flash-lite | map | 5 | C | 0/2 | 3.5 | 0 | 0 | 7 | 3.80 | 1.09 | 2443 | 0.000750 |
| gemini-3.5-flash-lite | map | 5 | H | 0/2 | 4.0 | 0 | 0 | 8 | 4.61 | 1.15 | 2940 | 0.000906 |
| gemini-3.5-flash-lite | local | 0 | A | 0/2 | 2.0 | 0 | 0 | 4 | 2.36 | 1.18 | 1402 | 0.000430 |
| gemini-3.5-flash-lite | local | 0 | B | 0/2 | 40.0 | 0 | 0 | 80 | 42.65 | 1.07 | 29823 | 0.009127 |
| gemini-3.5-flash-lite | local | 0 | C | 0/2 | 14.5 | 0 | 0 | 29 | 14.85 | 1.02 | 10414 | 0.003197 |
| gemini-3.5-flash-lite | local | 0 | H | 0/2 | 20.0 | 0 | 0 | 40 | 22.46 | 1.12 | 14926 | 0.004570 |
| gemini-3.5-flash-lite | local | 5 | A | 0/2 | 2.0 | 0 | 0 | 4 | 2.73 | 1.36 | 1434 | 0.000438 |
| gemini-3.5-flash-lite | local | 5 | B | 0/2 | 40.0 | 0 | 0 | 80 | 50.98 | 1.27 | 32597 | 0.009955 |
| gemini-3.5-flash-lite | local | 5 | C | 0/2 | 4.5 | 0 | 0 | 9 | 6.21 | 1.38 | 3422 | 0.001055 |
| gemini-3.5-flash-lite | local | 5 | H | 0/2 | 5.0 | 0 | 0 | 10 | 5.02 | 1.00 | 3934 | 0.001206 |
| gemini-3.8-flash | local | 0 | A | 2/2 | 7.5 | 0 | 1 | 15 | 50.74 | 6.77 | 7815 | 0.014714 |
| gemini-3.8-flash | local | 0 | B | 2/2 | 24.0 | 0 | 12 | 48 | 223.66 | 9.32 | 40240 | 0.110592 |
| gemini-3.8-flash | local | 0 | C | 2/2 | 8.0 | 0 | 0 | 16 | 44.64 | 5.58 | 11965 | 0.027648 |
| gemini-3.8-flash | local | 0 | H | 2/2 | 12.5 | 0 | 3 | 25 | 115.69 | 9.26 | 18712 | 0.045555 |
| gemini-3.8-flash | local | 5 | A | 2/2 | 7.0 | 0 | 0 | 14 | 35.42 | 5.06 | 8418 | 0.015763 |
| gemini-3.8-flash | local | 5 | B | 2/2 | 18.5 | 0 | 8 | 37 | 171.84 | 9.29 | 33417 | 0.089803 |
| gemini-3.8-flash | local | 5 | C | 2/2 | 8.0 | 0 | 0 | 16 | 40.58 | 5.07 | 13336 | 0.031386 |
| gemini-3.8-flash | local | 5 | H | 2/2 | 10.5 | 0 | 1 | 21 | 86.82 | 8.27 | 16738 | 0.038542 |

### B (pre-fix)

These rows were recorded before walls became solid, on the old room B layout. They should not be compared with B.

| Player | View | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks | Model calls | Mean latency per episode (s) | Mean latency per call (s) | Tokens | Est. cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BFS | - | - | B (pre-fix) | 6/6 | 10.0 | 0 | 0 | 0 | 0.00 | - | 0 | 0.000000 |
| gemini-3.5-flash-lite | map | 0 | B (pre-fix) | 0/2 | 28.0 | 0 | 0 | 56 | 32.27 | 1.15 | 19596 | 0.006007 |
| gemini-3.5-flash-lite | map | 5 | B (pre-fix) | 0/2 | 23.0 | 0 | 0 | 46 | 26.85 | 1.17 | 17580 | 0.005380 |
| gemini-3.5-flash-lite | local | 0 | B (pre-fix) | 0/2 | 40.0 | 0 | 0 | 80 | 41.36 | 1.03 | 29756 | 0.009102 |
| gemini-3.5-flash-lite | local | 5 | B (pre-fix) | 1/2 | 28.5 | 0 | 0 | 57 | 28.06 | 0.98 | 23447 | 0.007168 |
| gemini-3.8-flash | local | 0 | B (pre-fix) | 2/2 | 28.5 | 0 | 1 | 57 | 237.81 | 8.34 | 66866 | 0.187625 |
| gemini-3.8-flash | local | 5 | B (pre-fix) | 2/2 | 33.5 | 0 | 3 | 67 | 284.41 | 8.49 | 80691 | 0.223142 |

### Prices used for estimated cost

| Model | Input (USD per 1M tokens) | Output (USD per 1M tokens) | Checked | Note in `prices.json` |
|---|---|---|---|---|
| gemini-3.5-flash-lite | 0.30 | 2.50 | 2026-11-02 | Global endpoint, standard text; introductory rate valid through 2026-12-31 |
| gemini-3.8-flash | 0.75 | 3.75 | 2026-11-02 | Global endpoint, standard text; introductory rate valid through 2026-12-31, rising to 1.50 / 7.50 from 2027-01-01 |

Source for both: <https://cloud.google.com/model-garden/pricing>, as recorded in [prices.json](prices.json).

Costs are estimates from these prices, not billed amounts. Failed calls recorded no tokens, so they add 0 to the estimate. The estimate for all 90 rows, including B (pre-fix), is USD 0.857334.

## Traces and explanations

Each model row has one trace. BFS rows have no trace files. Pre-fix room B traces are in [traces/pre-fix/](traces/pre-fix/).

| Model | View | History | A | B | C | H | B (pre-fix) |
|---|---|---|---|---|---|---|---|
| gemini-3.5-flash-lite | map | 0 | [seed 1](traces/A-seed1-h0-gemini-3.5-flash-lite.jsonl), [seed 2](traces/A-seed2-h0-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/B-seed1-h0-gemini-3.5-flash-lite.jsonl), [seed 2](traces/B-seed2-h0-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/C-seed1-h0-gemini-3.5-flash-lite.jsonl), [seed 2](traces/C-seed2-h0-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/H-seed1-h0-gemini-3.5-flash-lite.jsonl), [seed 2](traces/H-seed2-h0-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/pre-fix/B-seed1-h0-gemini-3.5-flash-lite.jsonl), [seed 2](traces/pre-fix/B-seed2-h0-gemini-3.5-flash-lite.jsonl) |
| gemini-3.5-flash-lite | map | 5 | [seed 1](traces/A-seed1-h5-gemini-3.5-flash-lite.jsonl), [seed 2](traces/A-seed2-h5-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/B-seed1-h5-gemini-3.5-flash-lite.jsonl), [seed 2](traces/B-seed2-h5-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/C-seed1-h5-gemini-3.5-flash-lite.jsonl), [seed 2](traces/C-seed2-h5-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/H-seed1-h5-gemini-3.5-flash-lite.jsonl), [seed 2](traces/H-seed2-h5-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/pre-fix/B-seed1-h5-gemini-3.5-flash-lite.jsonl), [seed 2](traces/pre-fix/B-seed2-h5-gemini-3.5-flash-lite.jsonl) |
| gemini-3.5-flash-lite | local | 0 | [seed 1](traces/A-seed1-h0-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/A-seed2-h0-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/B-seed1-h0-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/B-seed2-h0-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/C-seed1-h0-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/C-seed2-h0-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/H-seed1-h0-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/H-seed2-h0-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/pre-fix/B-seed1-h0-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/pre-fix/B-seed2-h0-local-gemini-3.5-flash-lite.jsonl) |
| gemini-3.5-flash-lite | local | 5 | [seed 1](traces/A-seed1-h5-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/A-seed2-h5-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/B-seed1-h5-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/B-seed2-h5-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/C-seed1-h5-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/C-seed2-h5-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/H-seed1-h5-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/H-seed2-h5-local-gemini-3.5-flash-lite.jsonl) | [seed 1](traces/pre-fix/B-seed1-h5-local-gemini-3.5-flash-lite.jsonl), [seed 2](traces/pre-fix/B-seed2-h5-local-gemini-3.5-flash-lite.jsonl) |
| gemini-3.8-flash | local | 0 | [seed 1](traces/A-seed1-h0-local-gemini-3.8-flash.jsonl), [seed 2](traces/A-seed2-h0-local-gemini-3.8-flash.jsonl) | [seed 1](traces/B-seed1-h0-local-gemini-3.8-flash.jsonl), [seed 2](traces/B-seed2-h0-local-gemini-3.8-flash.jsonl) | [seed 1](traces/C-seed1-h0-local-gemini-3.8-flash.jsonl), [seed 2](traces/C-seed2-h0-local-gemini-3.8-flash.jsonl) | [seed 1](traces/H-seed1-h0-local-gemini-3.8-flash.jsonl), [seed 2](traces/H-seed2-h0-local-gemini-3.8-flash.jsonl) | [seed 1](traces/pre-fix/B-seed1-h0-local-gemini-3.8-flash.jsonl), [seed 2](traces/pre-fix/B-seed2-h0-local-gemini-3.8-flash.jsonl) |
| gemini-3.8-flash | local | 5 | [seed 1](traces/A-seed1-h5-local-gemini-3.8-flash.jsonl), [seed 2](traces/A-seed2-h5-local-gemini-3.8-flash.jsonl) | [seed 1](traces/B-seed1-h5-local-gemini-3.8-flash.jsonl), [seed 2](traces/B-seed2-h5-local-gemini-3.8-flash.jsonl) | [seed 1](traces/C-seed1-h5-local-gemini-3.8-flash.jsonl), [seed 2](traces/C-seed2-h5-local-gemini-3.8-flash.jsonl) | [seed 1](traces/H-seed1-h5-local-gemini-3.8-flash.jsonl), [seed 2](traces/H-seed2-h5-local-gemini-3.8-flash.jsonl) | [seed 1](traces/pre-fix/B-seed1-h5-local-gemini-3.8-flash.jsonl), [seed 2](traces/pre-fix/B-seed2-h5-local-gemini-3.8-flash.jsonl) |

### Traces not in the results

These four traces were recorded at commit `26bdb0a` with the later prompt, using seeds 3 and 4. They are not in `results.csv`, `summary.md` or the tables above.

| Trace | Outcome | Steps | Fallbacks |
|---|---|---|---|
| [A-seed3-h0-local-gemini-3.5-flash-lite](traces/A-seed3-h0-local-gemini-3.5-flash-lite.jsonl) | died: fell off the bottom | 6 | 0 |
| [A-seed4-h0-local-gemini-3.5-flash-lite](traces/A-seed4-h0-local-gemini-3.5-flash-lite.jsonl) | died: fell off the bottom | 8 | 0 |
| [H-seed3-h5-local-gemini-3.8-flash](traces/H-seed3-h5-local-gemini-3.8-flash.jsonl) | reached the exit | 13 | 3 |
| [H-seed4-h5-local-gemini-3.8-flash](traces/H-seed4-h5-local-gemini-3.8-flash.jsonl) | reached the exit | 14 | 0 |

### Explanations

- [explanations/A-seed1-h0-local-gemini-3.5-flash-lite.md](explanations/A-seed1-h0-local-gemini-3.5-flash-lite.md): room A, died at step 2 by falling off the bottom.
- [explanations/H-seed1-h5-local-gemini-3.8-flash.md](explanations/H-seed1-h5-local-gemini-3.8-flash.md): room H, reached the exit in 10 steps, the same length as the BFS solution by a different route.

## CI evidence

The workflow is [`.github/workflows/midterm-alsjoee.yml`](../../.github/workflows/midterm-alsjoee.yml). It is set to run on pull requests that change `midterms/alsjoee/**` or the workflow itself. It runs `python -m unittest discover tests` with no secrets and blank cloud settings, so no model can be called.

[CI.md](CI.md) maps five kinds of check to their tests:

1. **Rule invariants:** every reachable state in rooms A, B, C and H.
2. **Legal and illegal actions:** walking, jumping, climbing, waiting, gates and invalid replies.
3. **Terminal outcomes:** win, death and step limit.
4. **Observed regression:** the wall landing bug, the `play` crash after a fall off the map, and the fall-off rule being stated to players.
5. **Episode limits:** step limit, model-call limit, per-call timeout, episode time limit and model unavailable.

CI.md also describes an earlier bug, in which the final step was rejected, and a test failure it does not count as a regression. It lists the checks and does not record the result of a workflow run.

## Limitations

I asked the professor for the playtest week pairing via email but got no answer and therefore no peer playtest reports. So the only human playtests were my own ones. For the first playtest, there was no legend or goal description in the game, and I ran into the spikes. Therefore, I added an introduction and a legend. For the second playtest, I fell through the gap and onto the spikes in room C because I walked instead of jumping, and this is how the trap should work.

Each room was played twice per setup, which is an insufficient sample size, and a single lucky or unlucky play could alter the results substantially. These are the results of my runs, not general conclusions on the models' performance.

Gemini 3.8 Flash encountered many server timeout issues in room B during which the game showed a labelled wait instead of a model move. There was even a game with 11 waits. This increased the number of moves required by a model, so not all of its excessive moves in room B were due to the model.

An invariant test found a bug: the Prince could fall and land inside a wall in room B. I made walls solid, changed that one wall tile in room B to floor, and reran room B for every player. The old room B results are kept and marked as pre-fix.

There are some things I knowingly didn't fix. The 60-call limit can never trigger before the 40-step limit. After a limit ends an episode, the episode would technically still accept a move, although nothing in the code does that. And after the experiments, I added the fall-off rule and fallback labels to the prompt, so all the recorded results used the earlier prompt.
