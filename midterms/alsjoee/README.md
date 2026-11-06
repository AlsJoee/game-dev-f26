# Prince of Persia: One Room (turn-based)

Author: AlsJoee

## Scope

A turn-based reconstruction of a single Prince of Persia (Broderbund, Apple II,
1989) room puzzle. The Prince moves one tile per turn on a small multi-floor
grid and must reach the exit. Included: walking, jumping a one-tile gap,
climbing one floor, falling, health, spikes, a pressure plate and a gate.
Excluded: real-time movement, guards and sword fighting, potions, the
60-minute clock, animation and sound. These are cut to keep one bounded,
turn-based episode that a model player can be evaluated on.

## Rules and rule/source map

| # | Rule | Label | Evidence |
|---|------|-------|----------|
| 1 | The Prince starts with 2 health. | design | Adapted: the original starts with 3 health points; 2 makes a 2-floor drop cost half. |
| 2 | Actions: `left`, `right`, `jump_left`, `jump_right`, `climb`, `wait`. One action per turn. | design | Turn-based adaptation of real-time controls. |
| 3 | A jump clears exactly one empty tile and lands two tiles away. | assumed | From memory of play; to verify. |
| 4 | `climb` moves up one floor onto the tile directly above. | assumed | From memory of play; to verify. |
| 5 | Walking or jumping onto an empty tile makes the Prince fall to the floor below. | assumed | From memory of playing Prince of Persia (1989); not verified against the original. |
| 6 | Falling 1 floor is safe. | assumed | From memory of playing Prince of Persia (1989); not verified against the original. |
| 7 | Falling 2 floors costs 1 health. | assumed | From memory of playing Prince of Persia (1989); not verified against the original. |
| 8 | Falling 3 or more floors kills the Prince. | assumed | From memory of playing Prince of Persia (1989); not verified against the original. |
| 9 | Landing on or walking into spikes kills the Prince. | assumed | From memory of playing Prince of Persia (1989); not verified against the original. |
| 10 | Stepping on a pressure plate opens the gate for 3 turns; a closed gate blocks movement. | design | The original gate closes after real time; converted to turns. |
| 11 | Reaching the exit wins. | assumed | From memory of playing Prince of Persia (1989); not verified against the original. |
| 12 | An episode ends after 40 steps. | design | Episode limit for evaluation. |
| 13 | Walls are solid; a fall onto a wall stops on top of it | design | Decided 2026-11-04 after an invariant test found the Prince could land inside a wall; see `tests/test_regressions.py`. Not checked against the original game. |

## Declared evaluation suite (declared October 26, 2026, before tuning)

Legend: `S` start, `E` exit, `.` floor, space = empty, `^` spikes,
`P` pressure plate, `G` gate, `#` wall. Row 1 is the top floor.

**A: First gate** (shortest solution: 7 moves)
```
S. .P.G.E
```

**B: The long way down** (shortest solution: 10 moves)
```
S...  ..#
#. ...^.#
...  ...#
#^.....E#
```

Corrected 2026-11-04: an invariant test found the Prince could land inside the wall at row 2, column 2; the wall became floor and walls became solid (see tests/test_regressions.py). Results for B from commit ac601e2 and earlier are pre-fix.

**C: Plate below** (shortest solution: 8 moves)
```
#...G..E
#.. P###
S..^####
```

**H: Held-out** (not used during prompt tuning; shortest solution: 10 moves)
```
E..G..##
###.P..#
#.. ...#
S..^ ..#
```

Each situation is run twice with the model player and with the BFS baseline.

## Setup, play, test and evaluation

Commands are for a macOS or Linux shell. They were tested on macOS.

Play, baseline and the tests need no cloud account, no credentials and no
installed packages. Only the `model` and `evaluate` commands call a cloud model,
and those calls cost money on the Google Cloud project you set.

### 1. Get the code

Working directory: any folder outside an existing repository.

```sh
git clone https://github.com/columbia-university-ai-games/game-dev-f26.git
cd game-dev-f26
```

Working directory: `game-dev-f26/`. If `midterms/alsjoee/` is not there yet
because the pull request has not been merged, get it from the fork first:

```sh
git fetch https://github.com/AlsJoee/game-dev-f26.git alsjoee/midterm
git switch --detach FETCH_HEAD
```

Working directory: `game-dev-f26/`. Move into the project folder, where every
command below runs:

```sh
cd midterms/alsjoee
```

### 2. Create the environment

Working directory: `midterms/alsjoee/`. Use Python 3.11 or newer (the tests were
run on 3.11 and 3.14; CI is set to 3.12). If `python3` is older, name a newer
one, such as `python3.11`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -c "import tomllib, subprocess, sys; subprocess.check_call([sys.executable, '-m', 'pip', 'install', *tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']])"
```

The last line installs the dependencies listed in this folder's
`pyproject.toml`, which is only `google-genai`. Do not use `pip install .`: this
folder is not a buildable package, so that command fails. Run
`source .venv/bin/activate` again in each new terminal.

### 3. Play, baseline and tests (no cloud account)

Working directory: `midterms/alsjoee/`. Rooms are `A`, `B`, `C` and `H`.

Play a room yourself. Type one action per turn; Ctrl-D quits.

```sh
python -m pop_room play --room A
```

Run the BFS baseline, which prints its plan and each move:

```sh
python -m pop_room baseline --room A
```

Run the tests. They use a fake model client and make no network calls:

```sh
python -m unittest discover tests -v
```

### 4. Google Cloud setup (live runs only)

Working directory: `midterms/alsjoee/`. You need the
[Google Cloud CLI](https://cloud.google.com/sdk/docs/install) and a project with
the Vertex AI API turned on. Sign in once, then set the three variables in each
new terminal:

```sh
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
export COURSE_MODEL='gemini-3.5-flash-lite'
```

`prices.json` has prices for `gemini-3.5-flash-lite` and `gemini-3.8-flash`. With
any other model, the runs still work but the cost shows as `unknown`.

### 5. One model episode (live)

Working directory: `midterms/alsjoee/`.

```sh
python -m pop_room model --room A --seed 3 --history 5 --view local
```

- `--seed` is required. Traces for seeds 1 and 2 are committed, and the command
  refuses to overwrite a trace, before making any call. Seed 3 is unused.
- `--history N` shows the model its last N moves (default 0).
- `--view map` gives the map and observation (default). `--view local` adds one
  line naming the tiles next to the Prince.

An episode makes at most 40 model calls. The trace is written to `traces/`.

### 6. Evaluation (live)

Working directory: `midterms/alsjoee/`. `evaluate` refuses to start if any trace
it would write already exists, and a fresh clone already has the submitted ones.
They are tracked by git, so remove them from your clone first:

```sh
rm traces/*.jsonl
```

Run the declared suite in both views:

```sh
python -m pop_room evaluate --rooms A B C H --trials 2 --history 0 5 --view map
python -m pop_room evaluate --rooms A B C H --trials 2 --history 0 5 --view local
```

Each command plays 24 episodes: 8 BFS and 16 model, using seeds 1 and 2 and at
most 640 model calls. For a small check, run
`python -m pop_room evaluate --rooms A --trials 1 --history 0`, which plays one
BFS episode and one model episode.

`evaluate` appends to `results/results.csv` and rewrites `results/summary.md`. It
refuses to start if there are uncommitted changes outside `traces/` and
`results/`, so that each row points to an exact commit. To get the submitted
traces and results back afterwards:

```sh
git restore traces results
```

## Sources and reuse

Prince of Persia (Broderbund, 1989, designed by Jordan Mechner) is the
inspiration for this game. No code, art, text or level data was copied from it
or from its released source code.

The episode interface follows the shape of the course starter's
`course_game/player_interface.py`.

Gemini models are called through Google Vertex AI.

## Other submission documents

- [EVALUATION.md](EVALUATION.md)
- [AGENT-TEAM.md](AGENT-TEAM.md)
- [CI.md](CI.md)
- [review.md](review.md)
- Recording: link to be added.