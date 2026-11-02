# Evaluation summary

- Date: 2026-11-02
- Model: gemini-3.5-flash-lite
- Commit: 9fe5c194fde458853b52aeb1f6e32ac2f195ae56
- Price source: https://cloud.google.com/model-garden/pricing (checked 2026-11-02)
- Episodes: 18

Costs are estimates from prices.json, not billed amounts.

| Player | View | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks | Mean latency (s) | Total tokens | Est. cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|
| bfs | - | - | A | 2/2 | 7.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | B | 2/2 | 10.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | C | 2/2 | 8.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| model | local | 0 | A | 0/2 | 2.0 | 0 | 0 | 2.36 | 1402 | 0.000430 |
| model | local | 0 | B | 0/2 | 40.0 | 0 | 0 | 41.36 | 29756 | 0.009102 |
| model | local | 0 | C | 0/2 | 14.5 | 0 | 0 | 14.85 | 10414 | 0.003197 |
| model | local | 5 | A | 0/2 | 2.0 | 0 | 0 | 2.73 | 1434 | 0.000438 |
| model | local | 5 | B | 1/2 | 28.5 | 0 | 0 | 28.06 | 23447 | 0.007168 |
| model | local | 5 | C | 0/2 | 4.5 | 0 | 0 | 6.21 | 3422 | 0.001055 |
