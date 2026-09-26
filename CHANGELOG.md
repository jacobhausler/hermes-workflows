# Changelog

## 1.0.2 — 2026-09-26 — the run watches itself

Designed by a 4-seat blind counsel (fable/sol/opus/qwen), critic-voted, and built in 8
write-set lanes. Four overhauls, six additions — every one paid for by a deletion, zero new
verbs, zero new graph keys.

### Launching is showing (no agent control)
- A session-owned strip above the composer shows every run the focused chat launched,
  live, from the dashboard API — no hooks, no TTL, no transcript. Cron launches (no owner)
  show only in the pane. The `transform_llm_output`/`on_session_end` auto-card machine
  (~90 LOC + 2 hooks) is deleted; `provides_hooks` is gone from the manifest.
- The `::workflow{}` directive is now an agent-authored evidence PILL: one line, click to
  expand in place. The tool hands you the exact `card` line; paste it alone in the reply
  that launches or reports a run.
- KEY PAIRING (measured): `owner.session_id` is the runtime id (pairs with
  `host.focusedSessionId`); `owner.ui_session_id` is the desktop stored id (pairs with
  `host.focusedStoredSessionId`).

### Explorer V2: one node truth, two readers
- `wfcommon.node_facts` is the closed record the panel AND `status` read: `error_class,
  attempts_log, final` (the child's last words), `log_path, prompt_path, efp, steer`.
- NodePanel replaces the Drawer: FACTS column + Log/Output/Prompt/Final tabs, default by
  status; live log tail (4 s, only while open); `unknown` for absent, never zero.
- New read-only route `GET /runs/{id}/nodes/{nid}/log` (contained tail-seek). The
  partial-output drop in `_view` is fixed.

### WORKFLOWS beside SESSIONS | BOTS
- Top-level pane tab (the hermes-bots dock pattern), grouped NEEDS YOU / RUNNING / DONE
  with the one act-on fact per row; `WORKFLOWS · n` title is the sole live count.
- Deleted: the sidebar nav row, the status-bar LiveChip, the hand-rolled runs column.

### Archify: no (verdict + evidence), SMIL for candy
- Edges leaving a running node animate; one fan-stack implementation.

### Additions
- The prompt as sent is durable at `logs/<id>.a<n>.prompt.md` — "what did my child get?"
  is one file read; the `<prompt>` redaction and tempfile dance are gone.
- Failed/partial nodes ship their facts (last words, attempts, paths) in `status`; no
  detail:full + tail dance.
- Every `status`/`wait` ends with `next`: release/wait/amend rows derived from state, or [].
- Children start in a durable `<run>/work/<node>/` cwd — the deleted-cwd crash class dies;
  the write-first law moves from three doc homes into the spawn CONTRACT.
- Fan-out without `quorum` waits for ALL items (stragglers cancel only on an explicit
  `quorum`); the commit threshold is unchanged — partial credit survives.
- budgets.md shrinks to the `shape` presets the door already bakes; a test locks doc==code.


## 1.0.1 — 2026-09-25

Measured against 80 runs / 64 postmortems: 30.6 % of failures died at 0 s on a route or
grammar mistake, 50.8 % were untyped deaths, and authors wrote the same boilerplate in half
of all graphs. Every item below is a fix for something the census counted.

### The door validates from lists
- `(model, provider, reasoning)` validated against the seat catalog at `run`/`amend`;
  `provider` inherited from a provider-qualified alias; `reasoning` validated per route with
  the supported list and nearest level in the error; near-miss model suggestions.
- Full-graph submit validation: unknown keys per node type, `when` syntax, gate vocabulary.

### Deaths become outcomes
- `error_class` on every `node.failed` from a closed set (`cap_exhausted` replaces
  `max_turns`, `schema` replaces `no_json`; new `early_death`, `unresolved_model`,
  `transport_exhausted`, `incomplete_work`, `graph_invalid`).
- Harvest-on-death: a child that dies after printing a valid fenced answer is committed as
  `status: partial`; downstream runs on it; the death cause stays as `error_class`.
- Bounded auto-retry: `transport | early_death | cap_exhausted | timeout` with tool progress
  get exactly one re-drive with a machine resume preamble (`node.retry`); permfails never.
- Stop ≠ failure: `cancelled` is excluded from quorum and failure math; a stopped run reads
  `stopped` and `wait` re-drives the cancelled work.
- Child liveness: no output within 120 s of spawn → `early_death`; `last_tool_at`/`idle_s`
  surfaced for live nodes. Extend-not-kill: a child still writing at the wall gets one 50 %
  extension (`node.extended`).

### The graph carries less
- Graph-level `defaults:{schema, timeout, max_turns, reasoning, provider, model, context}`.
- `shape: recon|build|review|publish` fills budgets from measured p95 presets.
- Schema-derived reply contract written by the runner; last-balanced-object extraction on
  noisy stdout. Authors stop writing contract prose.
- Direct parents' outputs auto-injected under `## Inputs` (8 KB cap per parent).
- `fanout.goal` optional; quorum defaults to a majority; stragglers cancelled at quorum.
- `echo` node type commits a constant with no spawn.
- Gate `default_option` + `hold_timeout`: parks at zero tokens, auto-releases or logs
  `gate.expired` once and keeps holding.

### Operator surface
- The inline card is registered by `run`, `wait` and `status`; `card_rule` prose is gone.
- Steer honesty: `steer.queued/baked/consumed` events; per-node counts in `status`.
- Budget keys (`max_turns`, `timeout`, `run_budget`, `shape`) leave the node fingerprint:
  raising a wall no longer invalidates committed work.

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
