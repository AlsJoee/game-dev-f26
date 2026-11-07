# Agent team log

## Who did what

| Agent | What it could see and do | What it did | Evidence |
|---|---|---|---|
| **Claude Code (implementation)** | Local sessions in my repo, told to touch only `midterms/alsjoee/` | Wrote the world, episode, BFS baseline, Gemini player, evaluation runner, CI workflow and tests from my prompts | Commits marked "built with Claude Code"; session transcripts in `agent-logs/` |
| **Claude Code (independent review)** | A fresh session that hadn't written the code, read-only except for `review.md` | Reviewed the game against the brief and found 3 blocking problems | `review.md` (commit 44b0aa3) |
| **explain-episode skill** | Reads one trace file and writes a short explanation | Used in two separate sessions, on a failure (room A) and a success (room H) | `.claude/skills/explain-episode/`, `explanations/` |
| **Gemini (the player)** | Only the observation, legal actions, rules and up to 5 past moves; no files or tools | Played the game | `traces/`, `results/` |

## How I worked with it

I decided the rules and design myself, then gave Claude Code detailed prompts, and checked its work by running things rather than just trusting its tests.

## Decisions I made

- **Rules:** I chose them from how I remembered Prince of Persia: a 1-floor fall is safe, 2 floors costs half your health, 3 kills you; spikes kill instantly; jumps clear one tile; the gate stays open 3 turns.
- **Illegal moves:** they don't change the game, but they still use up a step, so a confused AI can't loop forever.
- **What the AI sees:** the map plus coordinates, and the gate only as open or closed, with no countdown. Deadly moves stay in the legal list, otherwise the list would do the thinking for the AI.
- **Fair baseline:** the BFS only uses what's in the observation, the same as Gemini.
- **Checking the agent's work:** I ran a known winning route and a gate-closing test myself. When I played the game myself, I found it had no legend or goal, so I had that added.
- **After the first results** (flash-lite won 0 out of 12), I added a "local view" describing the tiles around the Prince, then tested the bigger model, 3.8 Flash, to see whether the problem was the model.
- **When the tests found the wall bug**, I chose to fix the rule properly, change one tile in room B, and rerun B, keeping the old results marked pre-fix, rather than calling the bug a feature.
- **After the review**, I fixed the play crash, the missing fall-off rule and the timeout reason. I chose not to rerun everything, so room H stayed a true held-out test, and I noted the rest in my limitations.
- **One time Claude Code was wrong:** it wrote a test that assumed placeholder prices, which broke when I added the real ones, so I had it rewritten.