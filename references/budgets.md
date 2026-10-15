# Node budgets

Leave `max_turns`/`timeout` unset and name a `shape`; the runner fills them from the
measured p95 presets in `wfcommon.SHAPE_PRESETS` (the single source; measured 2026-09-25):

| shape | max_turns | timeout |
|---|---|---|
| recon | 100 | 2400 |
| build | 65 | 1500 |
| review | 65 | 2400 |
| publish | 75 | 1500 |

Set `max_turns`/`timeout` explicitly only with a measured reason. `validate` returns
non-fatal `warnings` when an agent's effective `max_turns` is below its shape's p95
preset (the default shape is `build`). A named shape wins over graph defaults;
an explicit node cap wins over both. Warnings do not change caps or reject the graph.

A lane node whose result is consumed downstream must end with bare JSON as its last
message and exit 0. State that exit hygiene in its goal: persist the work before the
turn cap, return the JSON required by its schema, and add no trailing commentary.
A complete answer does not make a nonzero exit successful; a harvested partial can
still block plain downstream edges.
