# Evaluation summary

- Date: 2026-11-04
- Models: gemini-3.5-flash-lite, gemini-3.8-flash
- Commits: b31388b194bbcb33257427fe1e03cd8c5a314a4f, 9fe5c194fde458853b52aeb1f6e32ac2f195ae56, c028466b5b7c6f0bdbc2b7546b7316447eebb54c, 519909c2551c0db9419a26aed5c95f6373c87792
- Price sources: gemini-3.5-flash-lite: https://cloud.google.com/model-garden/pricing (checked 2026-11-02); gemini-3.8-flash: https://cloud.google.com/model-garden/pricing (checked 2026-11-02)
- Episodes: 72

Costs are estimates from prices.json, not billed amounts.

B (pre-fix) rows were recorded before walls became solid, on the old room B layout. Do not compare them with B.

| Player | Model | View | History | Room | Wins/trials | Mean steps | Invalid actions | Fallbacks | Mean latency (s) | Total tokens | Est. cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bfs | - | - | - | A | 6/6 | 7.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | - | B | 6/6 | 10.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | - | B (pre-fix) | 6/6 | 10.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| bfs | - | - | - | C | 6/6 | 8.0 | 0 | 0 | 0.00 | 0 | 0.000000 |
| model | gemini-3.5-flash-lite | local | 0 | A | 0/2 | 2.0 | 0 | 0 | 2.36 | 1402 | 0.000430 |
| model | gemini-3.5-flash-lite | local | 0 | B | 0/2 | 40.0 | 0 | 0 | 42.65 | 29823 | 0.009127 |
| model | gemini-3.5-flash-lite | local | 0 | B (pre-fix) | 0/2 | 40.0 | 0 | 0 | 41.36 | 29756 | 0.009102 |
| model | gemini-3.5-flash-lite | local | 0 | C | 0/2 | 14.5 | 0 | 0 | 14.85 | 10414 | 0.003197 |
| model | gemini-3.5-flash-lite | local | 5 | A | 0/2 | 2.0 | 0 | 0 | 2.73 | 1434 | 0.000438 |
| model | gemini-3.5-flash-lite | local | 5 | B | 0/2 | 40.0 | 0 | 0 | 50.98 | 32597 | 0.009955 |
| model | gemini-3.5-flash-lite | local | 5 | B (pre-fix) | 1/2 | 28.5 | 0 | 0 | 28.06 | 23447 | 0.007168 |
| model | gemini-3.5-flash-lite | local | 5 | C | 0/2 | 4.5 | 0 | 0 | 6.21 | 3422 | 0.001055 |
| model | gemini-3.5-flash-lite | map | 0 | A | 0/2 | 2.0 | 0 | 0 | 2.43 | 1278 | 0.000392 |
| model | gemini-3.5-flash-lite | map | 0 | B | 0/2 | 26.5 | 0 | 0 | 30.15 | 18430 | 0.005650 |
| model | gemini-3.5-flash-lite | map | 0 | B (pre-fix) | 0/2 | 28.0 | 0 | 0 | 32.27 | 19596 | 0.006007 |
| model | gemini-3.5-flash-lite | map | 0 | C | 0/2 | 3.0 | 0 | 0 | 3.22 | 2002 | 0.000614 |
| model | gemini-3.5-flash-lite | map | 5 | A | 0/2 | 2.0 | 0 | 0 | 1.96 | 1310 | 0.000402 |
| model | gemini-3.5-flash-lite | map | 5 | B | 0/2 | 23.0 | 0 | 0 | 27.08 | 17516 | 0.005360 |
| model | gemini-3.5-flash-lite | map | 5 | B (pre-fix) | 0/2 | 23.0 | 0 | 0 | 26.85 | 17580 | 0.005380 |
| model | gemini-3.5-flash-lite | map | 5 | C | 0/2 | 3.5 | 0 | 0 | 3.80 | 2443 | 0.000750 |
| model | gemini-3.8-flash | local | 0 | A | 2/2 | 7.5 | 0 | 1 | 50.74 | 7815 | 0.014714 |
| model | gemini-3.8-flash | local | 0 | B | 2/2 | 24.0 | 0 | 12 | 223.66 | 40240 | 0.110592 |
| model | gemini-3.8-flash | local | 0 | B (pre-fix) | 2/2 | 28.5 | 0 | 1 | 237.81 | 66866 | 0.187625 |
| model | gemini-3.8-flash | local | 0 | C | 2/2 | 8.0 | 0 | 0 | 44.64 | 11965 | 0.027648 |
| model | gemini-3.8-flash | local | 5 | A | 2/2 | 7.0 | 0 | 0 | 35.42 | 8418 | 0.015763 |
| model | gemini-3.8-flash | local | 5 | B | 2/2 | 18.5 | 0 | 8 | 171.84 | 33417 | 0.089803 |
| model | gemini-3.8-flash | local | 5 | B (pre-fix) | 2/2 | 33.5 | 0 | 3 | 284.41 | 80691 | 0.223142 |
| model | gemini-3.8-flash | local | 5 | C | 2/2 | 8.0 | 0 | 0 | 40.58 | 13336 | 0.031386 |
