# Node budgets (measured, 2026-09-24)

Budgets are authored wrong in the common case: caps too tall, walls too short. Measured across 42 done spawns and 9 timeout deaths — the median timeout child died at 18 api calls against a 35–45 turn cap (utilization 0.49) because the wall-clock `timeout` fires first; `run_budget` is only checked between turns, so one slow call outruns it. Successful children finish near HALF their turn cap. The binding unit is the wall: at the observed ~80 s/call pace, a 900 s wall admits ~11 calls no matter how tall `max_turns` is.

Size to the shape; prefer a typed `cap_exhausted` death (partial + log preserved, cheap) over a timeout death (wastes half the cap, untyped work):

| shape | max_turns | run_budget | timeout | reasoning | write-first law |
|---|---|---|---|---|---|
| recon/probe | 25 | 600 | 660 | none/low | write notes file first, ≤5-line facts; reserve last 3 turns for the json block |
| single-file fix + targeted tests | 30 | 1000 | 1100 | medium | report skeleton first; reserve last 6 turns (compile + own tests + commit + json) |
| design-doc | 25 | 800 | 900 | high | skeleton file FIRST, fill per section; reserve last 3 turns |
| consolidator | 45 | 1400 | 1500 | high | write consolidated file first, merge from persisted per-item files; reserve last 5 turns — the only shape that legitimately presses its cap |
| fan-out item | 20 | 480 | 540 | medium | item MUST write its own file before the final json; reserve last 3 turns; if 3+ items hit max_turns the SPLIT is wrong, not the cap |

Two invariants behind the table:

- `timeout ≈ run_budget + 100`, and keep `timeout ≤ 0.9 × (max_turns × 80 s)` so the turn cap can actually fire (typed, partial preserved) before the wall. For tall caps this is unsatisfiable — cap `max_turns` to measured p95 + reserve instead of raising the wall.
- "Write-first + reserve final turns for the json block" is the same law the `max_turns` error text names; the table is that law turned into per-shape numbers. A lane runs only its OWN targeted tests — the full suite belongs to the merge owner, not to every lane.

Derived from run data (session-local receipts); shapes and numbers are 2026-09 house estimates from qwen-family lanes — re-measure on your own fleet before trusting them for another model or seat.
