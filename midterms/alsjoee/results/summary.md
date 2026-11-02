# Evaluation summary

- Date: 2026-11-02
- Model: gemini-3.8-flash
- Commit: c028466b5b7c6f0bdbc2b7546b7316447eebb54c
- Price source: https://cloud.google.com/model-garden/pricing (checked 2026-11-02)
- Episodes: 18

Costs are estimates from prices.json, not billed amounts.

| Player | View | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks | Mean latency (s) | Total tokens | Est. cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|
| bfs | - | - | A | 2/2 | 7.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | B | 2/2 | 10.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | C | 2/2 | 8.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| model | local | 0 | A | 2/2 | 7.5 | 0 | 1 | 50.74 | 7815 | 0.014714 |
| model | local | 0 | B | 2/2 | 28.5 | 0 | 1 | 237.81 | 66866 | 0.187625 |
| model | local | 0 | C | 2/2 | 8.0 | 0 | 0 | 44.64 | 11965 | 0.027648 |
| model | local | 5 | A | 2/2 | 7.0 | 0 | 0 | 35.42 | 8418 | 0.015763 |
| model | local | 5 | B | 2/2 | 33.5 | 0 | 3 | 284.41 | 80691 | 0.223142 |
| model | local | 5 | C | 2/2 | 8.0 | 0 | 0 | 40.58 | 13336 | 0.031386 |
