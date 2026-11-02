# Evaluation summary

- Date: 2026-11-02
- Model: gemini-3.5-flash-lite
- Commit: b31388b194bbcb33257427fe1e03cd8c5a314a4f
- Price source: https://cloud.google.com/model-garden/pricing (checked 2026-11-02)
- Episodes: 18

Costs are estimates from prices.json, not billed amounts.

| Player | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks | Mean latency (s) | Total tokens | Est. cost (USD) |
|---|---|---|---|---|---|---|---|---|---|
| bfs | - | A | 2/2 | 7.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | B | 2/2 | 10.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | C | 2/2 | 8.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| model | 0 | A | 0/2 | 2.0 | 0 | 0 | 2.43 | 1278 | 0.000392 |
| model | 0 | B | 0/2 | 28.0 | 0 | 0 | 32.27 | 19596 | 0.006007 |
| model | 0 | C | 0/2 | 3.0 | 0 | 0 | 3.22 | 2002 | 0.000614 |
| model | 5 | A | 0/2 | 2.0 | 0 | 0 | 1.96 | 1310 | 0.000402 |
| model | 5 | B | 0/2 | 23.0 | 0 | 0 | 26.85 | 17580 | 0.005380 |
| model | 5 | C | 0/2 | 3.5 | 0 | 0 | 3.80 | 2443 | 0.000750 |
