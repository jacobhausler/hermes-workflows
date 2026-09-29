# Changelog

## 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance

Every feature is OPTIONAL: a no-team run (default profile, no `WF_RUNS_ROOT`) is byte-identical to 1.0.15 — proven by the frozen 1.0.15 suite pass-set plus a golden solo diff (`tests/golden_solo/v1.0.15.json`, EMPTY diff across six fake_hermes graphs) re-run after every lane merge. Stdlib-only backend; desktop imports frozen to `@hermes/plugin-sdk`, `react`, `react/jsx-runtime`. Sprint contract: `wf-team-sprint-1.1/RATIFY.md` (F1–F5; F6 cut, F7 skill-side). Integrator @wf-mechanic; lanes A–F built by qwen children (git author `Hermes Agent`), one writer per file.

- F1 runs root + run identity (scaffold 0e8b1e8, @wf-mechanic): ONE resolver `wfcommon.runs_root()` (`WF_RUNS_ROOT` if set, else `$HERMES_HOME/workflows`) replaces the four inline computations in door, runner, read model and dashboard; `runner_alive` compares the runner's EFFECTIVE root from `/proc` environ (legacy env reduces to the 1.0.15 `HERMES_HOME == r.parent.parent` check verbatim). `run.json` gains `dispatched_by`, `launch_root`, `team`, `lane_key`, `targets[]`, `graph_source` ONLY when derivable; solo default-profile key set == 1.0.15. Children receive `HERMES_WF_RUN_DIR` so `inbox` resolves without guessing the root. `source_digest(graph)` = sha256 over canonical nodes JSON (`graph_fingerprint` untouched).
- F2 profile-routed agent nodes — lane C read model (e43639c, Hermes Agent / lane C) + lane A runner (4a2f15b, Hermes Agent / lane A): `profile` on an agent node (node-level only, `{run.KEY}` rendered BEFORE validation) runs the child AS a named teammate profile — delegation, not isolation. Validation before any write/spawn: non-empty profile DIRECTORY with `config.yaml`, never `default`, and the TARGET-owned `<profile_home>/workflow_team.json` lists the launcher in `accept_from` (launcher identity from the door's own HERMES_HOME, never a graph arg). Runner spawns with `-p <profile>` under an env whitelist + `HERMES_HOME=<root>`, re-checks the target before Popen (deleted target → typed `error_class:"spawn"` `profile gone: <name>`, never a launcher fallback), records `profile_home` on node records and reads child metrics from the target's state.db. `node_facts` render the routed profile.
- F4 `requires` output preconditions — lane C validation + lane A schedule-time check: `requires:{"<ancestor>":["field","dotted.path"]}` on agent OR gate nodes; every key must be in the `after` closure, every path a non-empty string. At wave scheduling a missing OR null value commits the node `failed` with `error_class:"precondition"` (`output.missing` lists the paths) with ZERO spawns; the run fails on the existing failed/blocked path. Retry ladders never see it; a resume re-evaluates (supply the field via `amend`). 1.0.x `skipped` semantics untouched.
- F3 `lane_key` in-flight registry — lane B door (097b717, Hermes Agent / lane B): `run` gains optional `lane_key` (≤128) and `team` (≤64); `status` accepts `lane_key` as an alternative to `run_id` (never spawns). Registry `<runs_root>/lanes/<sha16>.json` written tmp+`os.replace` under a per-key `fcntl.flock`; while an UNFINISHED incumbent holds the key a second `run` is deduped (`{deduped:true, run_id, state, runner_live, needs_resume, last_event_ts, hint}`) — the incumbent is resumed via `wait`, never replaced; terminal `stopped` releases the key. Stored key must EQUAL the supplied key (mismatch → `lane_key hash collision`, never a cross-key dedupe). Entries append-only; keys global per runs root. `list` rows carry `lane_key`/`team` when present.
- F5 library provenance (opt-in) — lane B door: `save` gains optional `source` (≤200). `{owner, source, saved_at, source_digest}` is written into the library entry ONLY when `source` is supplied or the saving door runs under a named profile; a default-profile save without `source` writes the 1.0.15 bytes exactly. Top-level graph key `provenance` (closed key set). `library` rows show the fields only when present; `run from:<name>` stamps `run.json.graph_source`. Attribution only — nothing reads it to allow or deny.
- Desktop — lane D (3a4aa70, Hermes Agent / lane D): node card and panel show `as @<profile>` for routed nodes; solo trees render structurally IDENTICAL to the 1.0.15 baseline (`tests/test_11_ui_imports.mjs` snapshot + frozen import baseline).
- Fixtures — lane E (0a505ba, Hermes Agent / lane E; integrator fixes 4805b0e, 79ae59d): `tests/test_11_integration_*.py`, `tests/fixtures/11-*`, `tests/11-golden-solo.py` capture/compare, `tests/11-keeper.py` 20-cycle keeper harness, claim-crash wrapper, env-leak probe, throwaway consent profile. Counted matrix on the merged tree: liveness 8/8, cross-profile wait 3/3, validation negatives 4/4, env 2/2, spawn-race 1/1, SOUL 3/3, harvest-DB 2/2, keeper cycles 20/20, dedupe 3/3, boundary kills 3/3, concurrent claim 1/1, precondition 5/5, provenance 6/6+1+1.
- Docs — lane F (5a7e631, Hermes Agent / lane F): SKILL.md team paragraph; `references/grammar.md` (`profile`, `requires`, gate `requires`, top-level `provenance`); `references/operations.md` (lanes/dedupe, runs root + identity + TRUST BOUNDARY: a shared `WF_RUNS_ROOT` is common trust, same UID; team fields are provenance, never an ACL).

## Unreleased

- #32 publish-as-file: top-level `grammar: "wf/1"` accepted (absent = wf/1; unknown value refused listing the supported values), def_hash-neutral like `provenance`; `references/portable.md` convention + `examples/portable-review.workflow.json` walk-in with its digests pinned in the doc (`tests/test_portable_32.py`).
- #31 grammar-dialect-1: `references/dialect.md` maps Anthropic's Claude Code dynamic-workflow JS grammar (agent/parallel/pipeline/phase/args/plain-JS glue/caps/worktrees) to our JSON graph with a filled DEVIATION JUSTIFICATION column per row, and `tests/fixtures/dialect/` (13 `.js` scripts + `.expected.json` verdicts) pins the constrained-subset import contract that #33 implements. Docs + fixtures only; no importer/exporter code.
- #24 fatal_quota (from @pf-mechanic-2's report): a 429 whose own text carries a
  reset horizon (`resets in ~109h`) is classed `fatal_quota` — the node fails on the
  FIRST attempt (the bounded retry ladder can never beat a multi-day reset; the
  field case burned 3 spawns in 60s), and the model + horizon land in the seat quota
  cache (`$HERMES_HOME/cache/workflow-quota-cache.json`). The door refuses a launch
  whose node pins a cache-marked model — one recovery ping first, so a stale stamp
  can't wedge a model that recovered early. Minute-granularity horizons
  (`resets in 30 minutes`) are honored as minutes, not folded into the 6h default;
  a provider-less (seat-default) stamp recovers on any answered ping, an
  explicit-provider stamp only on a same-route alive ping (attribution law).
- #25 fail-closed pinned routes (field report fb-fix-9c575645): a node that pins an
  explicit model now gets `require_route` default TRUE — if the door's submit ping
  AFFIRMATIVELY proves the pinned route dead, or answered from the fallback ladder
  (recorded route != pinned route), the launch is REFUSED with
  `error_class=route_unavailable` instead of silently billing the seat's fallback.
  `require_route: false` (node or `defaults`) opts into the ladder explicitly;
  infra-absence (ping impossible) stays unknown = warn-only, never a false block.
  A ping that PROVES the route alive bakes `route_verified` (door-only proof — the
  validator carries the key for the runner; `_resolve_models` drops any author or
  stale value) and the runner's commit hold fails a node whose committed
  served_model contradicts the proof. Deep-review pass 2 hardened: policy keys
  (`require_route`/`route_verified`) are fingerprint-ignored like budgets, frozen
  replay comparisons exclude the proof annotation, quota refusal skips replay-skip
  nodes on amend, and a profile-routed hold reads the TARGET's aliases, never the
  runner seat's. Tests: `test_fatal_quota_24` / `test_require_route_25` (+ runner
  validator + forged-proof + def_hash + un-bake regression rows), golden-solo EMPTY
  diff holds (solo graphs pin no models → no new bytes).
- Runner lane-clean gate (feedback digest 29d, ledger 64c6772b): an agent node may declare `repo: <path>` — the git lane it owns. At commit the runner runs `git status --porcelain --untracked-files=no` on the lane; a done/partial over a lane with uncommitted TRACKED changes commits `failed` `error_class:"incomplete_work"` carrying `lane_dirty` (the porcelain), instead of the dad50be0 false-green where the fix died uncommitted in a capped child and downstream verified a HEAD equal to the mutant. Refusal, never auto-commit (no runner author identity); untracked never dirties; git-unable fails open; default-off keeps every existing graph byte-identical (golden-solo EMPTY). Door description, AGENTS closed set, and grammar.md document the field; `tests/test_lane_gate_64c6772b.py` covers clean/dirty/untracked/fail-open/mutation.
- Door schema legibility (feedback digest 29d, ledger 0b680871): the registered `graph` param description is built from adjacent short string literals (each < 400 chars) instead of one 3.4k-char line — the runtime string is byte-identical (pinned by `test_validator_caps` ROW 1 + a segment-boundary test); the "schema is truncated" report was core `search_files`' 500-char per-match clamp on that single line, not a core defect. Comment at `tests/test_validator_caps.py` fixed to stop blaming the schema validator.

- Desktop — pill rail for the session's live runs + expansion (#22 rail half; the
  auto-card half stays backlog): `railModel(ownedRuns)` (exported pure) folds the live
  set into pills — held first, then running by `started` desc, capped at 3 + overflow
  (same policy as `splitRuns`, which stays for the pane); `PillRail` renders one
  horizontal row of compact pills `[Dot][short name][done/total]` and gate-held pills
  keep `GateActions`; progress is `${nodes_done}/${nodes_total}` and `?` when either
  count is absent — never fabricated. Clicking a pill expands the run's existing
  `MiniGraph` (via `runQuery`) in a mini node-strip ABOVE the rail; clicking the open
  pill, Esc, a click outside the rail, or switching the focused chat collapses it.
  Open state is the in-memory `$railOpen` atom (`{sid, runId}`, never localStorage);
  `toggleRail` is the exported pure transition core. Theme via
  `var(--ui-sidebar-surface-background, var(--card))` + `--ui-stroke-secondary`, inline
  style only. Tests: `tests/test_pill_rail.mjs`, `tests/test_pill_rail_expand.mjs`.
- Desktop — the session strip mounts in `composer.underside` when the SDK offers it
  (#22): `register()` uses `COMPOSER_AREAS.underside ?? COMPOSER_AREAS.top`. On core
  >= v2026.7.30 the strip is the floating strip BELOW the composer dock —
  bottom-anchored, grows upward over the thread, and does not dim on scroll-up
  (composer/index.tsx:1558-1560). `COMPOSER_AREAS` is an SDK const map, so a missing
  key means the core doesn't mount the area at all; `??` then keeps today's
  `composer.top` slot on older shells. One mount, never both.
  `tests/test_register_surface.mjs` loads the module against both stub SDK shapes
  (area-set assertions per shape) and asserts hook-order safety: `SessionStrip` calls
  `useValue`/`useQuery` before its null return.
- fix #23 (desktop): `SessionStrip` and the pane's `this chat` pill read the focused-chat
  atoms from `host.state.focusedSessionId` / `host.state.focusedStoredSessionId` — the SDK
  exposes them ONLY under `host.state` (sdk/index.ts:665-697). Reading `host.focusedSessionId`
  left `focusAtom(undefined)` → null sid → the strip never rendered and `owned` stayed empty.
  The test stubs previously placed the atoms at the SDK `host` top level — the stub encoded
  the bug; they now live under `host.state` with a red-on-base render assertion.

## 1.0.17 — 2026-09-28

- Landed via #5 (repo owner) — `release 1.0.17 — catalog sync + F5/F6 replay & run_context fixes`: public tree synced with the PR #4-reviewed catalog fixes (visible `composer.submit` gate answers, launcher-only `hermes_bin`, disclosure docs), the 1.0.16 guarded per-route reasoning validation, and the two review fixes below (F5 replay, F6 brace guard). Review round R8 flipped the `f0f154d5`/`v4_fixes` regression tests to any-rule-match and refreshed `graphify-out`.
- R10 replay fix (review of #4, F5): an unstamped (pre-1.0.12) node record whose hash matches BOTH historical fingerprint rules now loads as committed (`done`), not `pending`. Two rules agreeing on the same hash prove the definition is unchanged; the old unique-match rule re-spawned every pre-1.0.12 no-budget node (measured: 25 nodes, 8 runs flipped to `interrupted` over 166 real run dirs). Fail-closed is now zero matches — a real definition change and a budget amendment against an old-rule stamp both still invalidate. Old run dirs stop re-running after upgrade.
- run_context brace guard (review of #4, F6): a `{run.KEY}` value containing `{`/`}` bound into a fan-out goal or `items[].goal` is rejected at the door before any run write. The runner re-renders fan-out goals per item (`fmt_goal`), which would have interpolated the bound value a second time against item fields — contradicting the documented no-interpolation-of-substituted-values contract. Non-fan-out goals are unaffected (rendered once at launch).

## 1.0.16 — 2026-09-28

- fb b3c98b2a0518a8f0: the 1.0.15 rewrite dropped per-route reasoning validation for non-Codex routes, falling back to global levels and accepting anthropic `ultra`; it also crashed coreless hosts on Codex nodes. Restore `route_supported_efforts` with a guarded `codex_supported_efforts` fallback for older cores and guard every host import.
- 1.0.15: a served forbidden model now fails the fan-out parent and its `node.failed` event with `forbidden_model` even when quorum otherwise succeeds; per-item evidence remains typed and downstream is blocked. Reasoning validation uses the installed core's Codex effort function for Codex routes; non-Codex routes fall back to global levels (corrected above). Added credential-free A-door validation and historical fingerprint-run regression tests (dad50be002da89d5, f0f154d5dd80220c).
- Regression pin for f0f154d5dd80220c: budget-bearing, unstamped historical runs report done under the cross-rule reader already shipped in 1.0.12 (7deffc3); an era-A reader reproduces stale/pending. Separate run-shape locks keep both-rule ambiguity, unknown hashes, and genuine budget-bearing amendments fail-closed. Test-only coverage of the earlier fix; no runtime change for this row.
- 1.0.14: model law enforced. Every node commit (solo and per fan-out item) stamps the ACTUAL served model + billing provider from the child metrics onto nodes/<id>.json (`served_model`, `served_billing_provider`); an absent sessions row stays null (unknown, never forbidden). If the served model hits the forbidden set (graph `model_policy.forbidden_models` ∪ seat `workflows_forbidden_models`), the node/item commits `failed` with `error_class='forbidden_model'` and blocks downstream. Seat-floor submit rejection runs BEFORE model resolution so a seat-forbidden name reports field=model instead of being swallowed as unknown-model (fb dad50be002da89d5).
- 1.0.12: fingerprint rule provenance on new run, node, spawn, gate, and runner-exit records. Readers verify each stamped record against the current graph using its own known rule; unknown versions and ambiguous unstamped hashes fail closed. Historical no-budget unstamped commits may replay instead of skip; restart old in-memory readers after deployment (95d7010295d70102).
- 1.0.13: `workflow run from=<name>` accepts optional `run_context`: a non-empty string
  delivered to every first-wave agent (including gate-first/parallel roots), or a
  string map that resolves only explicit `{run.KEY}` in node goals, contexts,
  fan-out goals/item goals, and gate questions. Invalid/missing bindings fail
  before run creation. Resolution follows defaults, precedes persistence and
  fingerprinting; the shelved graph is unchanged. `/wf <name> [note]` now sends
  its note atomically as a string seed rather than a post-launch steer. A seed
  does not replace baked target literals: reusable graphs must contain explicit
  `{run.key}`, `{run.branch}`, `{run.argv}` binding points. Bound values persist
  in prompts and must not contain secrets (fb 4052d57719653b1a).

## 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed)


- A false `gate.when` with omitted `on_skip` now prunes the gate and exclusively dependent descendants in both human and wait-gate paths; `gate.skipped` reports `prune` to match the saved status. Explicit `pass` still permits the arm, and explicit `prune` is unchanged (fb e4c98f6e550e3a90). This does not change explicit `on_skip:"pass"` in existing graphs, including `library/fb-fix.json` before publish.

- Desktop gate answers now resume the run's owner session through the public
  composer SDK as a visible turn; on older Desktop builds, the resume text is
  inserted for the user to send, or the UI asks for manual resume. No app DOM
  query or private composer event (per maintainer review on
  NousResearch/hermes-agent#122099, teknium1).
- The workflow tool no longer accepts `hermes_bin`; only operator plugin settings
  or `HERMES_WF_HERMES_BIN` may select the child launcher. Tool-arg attempts
  fail closed (per maintainer review on NousResearch/hermes-agent#122099).
- Document the detached runner's lifecycle and the stop-before-disable rule;
  align the documented Hermes floor and catalog metadata.


## 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT

- A child's advertised durable work dir (`<run>/work/<node>[.<i>]`) is now
  writable when the runner's env carries a non-empty `HERMES_WRITE_SAFE_ROOT`:
  the runner appends the child's OWN work dir (nothing wider — never the run dir,
  `run/work`, or `$HERMES_HOME/workflows`). Unset/empty is left exactly as
  inherited (unrestricted). Previously children silently lost artifact writes
  (fb 625a3241cfcc9dee). Moots 2c639b96 (fb-fix children could not write
  findings). The TMPDIR half of ea743553 is untouched.

## 1.0.9 — 2026-09-27 — amend keeps committed routes only where they replay

- amend keeps committed nodes' baked routes only where the node replay-skips;
  edited/re-running nodes re-route on the current seat; a node's own tier target
  is a known model (fb 034849a23af94418)

## 1.0.8 — 2026-09-27 — quorum cancels never fire blind

- A fan-out straggler cancelled at an explicit `quorum` now states its output
  state AT THE KILL INSTANT: `cancelled: quorum already met — no output on disk
  at quorum moment` vs `— had output at quorum moment (log N bytes, workdir M
  files)` (snapshot dict `cancel_evidence` rides the record). The kill itself
  is unchanged (A5 opt-in intact); the SIGKILL freezes the capture, so the
  snapshot is faithful (fb a2d7f66443910813).
- Harvest-at-cancel: a cancelled straggler whose frozen capture carries a
  valid fenced answer keeps it (`harvest` + `item.harvested_at_cancel` event).
  Classification and quorum math untouched — error_class stays `cancelled`.

## 1.0.7 — 2026-09-27 — door quorum blurb matches the runner

- The `workflow` tool's graph-param description told authors fanout `quorum`
  "defaults to majority ... stragglers are cancelled" — the runner cancels
  stragglers ONLY when quorum is EXPLICIT; unset quorum waits for every item
  (grammar.md always agreed with the runner; the door did not). Door copy now
  states: quorum OPTIONAL positive int; with it set, once N items commit the
  still-running stragglers get `error_class: cancelled` and are excluded from
  the failure math; without it the fan-out waits for all. Pin test
  `tests/test_door_quorum_copy.py` (red-first) pins the registered string.
  fb 2f9653b1; lane 89d86c9 (red-first pin) + a874255 (copy) + 0c5c05e (graphify).

## 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named

- `scripts/suite.py` no longer seeds `exits.json` from disk: each run resets the
  ledger (atomic `[]` seed via tmp+os.replace) so a re-run into a non-empty ci-out
  reports the CURRENT pass only — no more `TOTAL 120` citing the previous run's
  stale red rows. fb 3d2175e9.
- `references/grammar.md` now names the fanout closed set exactly
  `{items | items_from, goal, schema, quorum}` (matching the validator at
  wfcommon.py:68) and documents `fanout.schema` (per-item reply contract, same
  rules as node `schema`) — previously undocumented, authors had to guess.
  fb aa9a65e0.

## 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)

- A graph pinned to a live-but-quota-dead seat used to launch happily and die hours
  later at the FIRST child spawn (`transport_exhausted` after the fixed 5s/20s retry
  ladder); `model_preflight` proves resolution, not liveness, and the provider's
  `Retry-After` header never survived to the door. Now: one `wf-preflight-ping`
  auxiliary request (max_tokens=1, ~10s timeout, explicit provider+model, one
  attempt) per DISTINCT resolved route at run AND amend submit annotates the existing
  `routes` entries with `liveness=alive|dead|unknown` + `retry_after_s` (never
  fabricated) + scrubbed note, and dead routes append a repoint hint. STRICTLY
  fail-open: every exception path (timeout, non-core host, transient 5xx, fallback
  answered cross-route) maps to `unknown` and the run LAUNCHES — warn-and-surface,
  no blocking, no new door schema keys. Ledger 152be7f7; lane de228d5+b28254f;
  targeted 34/34, mutation-checked (revert -> 30 FAIL), suite 61/61.

## 1.0.4 — 2026-09-26 — manifest floor matches the fleet

- `requires_hermes` reverted `>=0.21.4` -> `>=0.21`: the CI-pin (09-25) raised the
  floor above the fleet image (0.21.3), so the plugin was silently SKIPPED at boot
  (`Plugin 'hermes-workflows' skipped: requires hermes >=0.21.4, running 0.21.3`)
  and the workflow tool vanished after the next serve restart. The CI pin stays in
  the workflow file; the manifest must only state the floor the stock `-Q`
  contract actually needs. Deploy lesson: after restart, prove
  `Mounted plugin API routes: /api/plugins/hermes-workflows/` in gui.log —
  `/api/health` 200 does NOT prove the plugin loaded.

## 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes

Merged from the feedback-triage commander's verified lanes (each:
adversarial-check ruling, mutation-checked targeted test, full suite green):

- **Deleted-cwd runner resilience (5c37b19)**: the runner degrades instead of
  dying ENOENT when a written-to dir is gone (deleted cwd, wiped `gates/`);
  spawn garnish and when-skip writes survive, respawn clean.
- **Live-orphan adoption (790c6ad)**: a respawned runner ADOPTS verified live
  fan-out children (pid alive + skey-title-in-argv) instead of re-spawning from
  zero — no duplicate item.started, deadline re-armed from adoption.
- **Fan-out own-goal drift guard (fb12da4)**: when `fo.goal` declares
  `{item.FIELD}` and an item bakes a sibling's value, a loud `item.goal_drift`
  event fires and the template render wins (warn-and-prefer-template ONLY,
  never fail-closed); dangling `{item.X}` placeholders warn at spawn.
- **Validator honesty (validator-duo)**: numeric-bound rejections name the
  offending value AND the cap (`max_turns 240 exceeds cap 200 (must be a
  number in (0, 200])`); the wait tool's 1800s clamp echoes a `timeout_note`
  instead of swallowing it. Pin-test guards the registered graph description.

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
  `host.state.focusedSessionId`); `owner.ui_session_id` is the desktop stored id (pairs with
  `host.state.focusedStoredSessionId`). The SDK exposes both atoms only under `host.state`
  (sdk/index.ts:665-697); reading them at the top level was the #23 render bug, fixed in
  the follow-up below.

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
