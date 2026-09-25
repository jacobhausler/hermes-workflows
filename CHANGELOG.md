# Changelog

## 0.9.0 — 2026-09-24

### Added
- Boolean is accepted as an output schema type, so a node can contractually return a
  simple yes/no verdict (pre-validation whitelist plus runner-side validation).
- Submit-time model/provider preflight: a graph whose node routes to a dead or unknown
  seat alias is rejected at submit, after the route table and before the first wave
  spawns anything.
- Per-shape budget recipes reference (`references/budgets.md`) with an authoring-skill
  pointer, distilled from measured runs (42 completions vs 9 timeout deaths).
- Every `node.failed` event now carries typed fields — `error_class` and `attempts` —
  so a parent agent reads failure facts instead of inferring them from an exit code
  and prose.
- B1 cooperative steer: a running child can pull late steering itself via the
  `workflow` tool's `action="inbox"`. Steering text is baked per-spawn with a
  high-water mark and a delivery cursor; the read model exposes the evidence.
- Transcript card delivery is kept honest across held-launch replays: the auto card
  survives past blank or interrupted final turns instead of being dropped.
- Fan-out stacks can expand: the stack badge toggles the stack open into per-item
  cards on the canvas.

### Changed
- `status` and `wait` are compact by default: mid-run payloads carry output pointers
  instead of full bodies, `detail: "full"` opts in, and terminal (finished) payloads
  are always full.
- Canvas wrap law: depth columns fold into width-fitted bands, and backwards
  band-to-band edges route through an orthogonal gutter instead of slicing cards.
- Steer is truthful about liveness: steering a finished (terminal) run or node is
  refused honestly rather than quietly accepted.

### Fixed
- Metrics guards: torn metric objects can no longer crash the desktop views
  (item chips, item detail, mini-graph, timeline, run header), and a missing
  `api_calls` count renders as `unknown` rather than `0`.
