# Graph Report - tree  (2026-09-29)

## Corpus Check
- 120 files · ~158,326 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1411 nodes · 2838 edges · 86 communities (72 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 164 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- pathlib
- plugin_api.py
- os
- test_fanout_expand.mjs
- graph_check.py
- Changelog
- test_11_ui_imports.mjs
- json
- CurrentAttemptMetrics
- test_fanout_item_goal.py
- test_lifecycle_next_cut_0923.py
- loop
- run_state
- subprocess
- tempfile
- jload
- importlib_util
- test_card_frontend_contract.mjs
- __init__.py
- act_run
- test_live_truth_ui.mjs
- test_register_surface.mjs
- sys
- validate_graph_errors
- main
- _resolve_models
- test_canvas_wrap.mjs
- efp
- test_node_click_expand.mjs
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- test_session_strip.mjs
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_sprint101_A-door.py
- test_preflight_liveness_152be7f7.py
- test_orphan_adopt_790c6ad.py
- test_metrics_missing_ui.mjs
- test_prompt_workdir.py
- test_route_efforts_b3c98b2a.py
- amend
- test_11_integration_team.py
- test_deleted_cwd_resume_5c37b19.py
- AGENTS.md
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- FakeHTTPError
- _create_run
- act_amend
- test_fanout_ui.mjs
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- model_preflight
- node_facts
- Run operations and read model
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_C3-fanout-gates.py
- test_steer_live_40.py
- build_inputs
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Manual installation — Hermes Workflows 1.1.0
- Hermes Workflows
- DoorLane
- test_failed_events_77.py
- test_suite_admission_17.py
- test_tiers.py
- _bind_run_context
- 11-golden-solo.py
- Claim
- test_validator_caps.py
- manifest.json
- Integrated
- _active_spawns
- fake

## God Nodes (most connected - your core abstractions)
1. `jload()` - 35 edges
2. `efp()` - 33 edges
3. `run_child()` - 30 edges
4. `run_state()` - 22 edges
5. `_adopt_child()` - 21 edges
6. `main()` - 21 edges
7. `loop()` - 21 edges
8. `NodePanel()` - 18 edges
9. `CurrentAttemptMetrics` - 18 edges
10. `act_run()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)` --references--> `model_preflight()`  [INFERRED]
  CHANGELOG.md → __init__.py

## Import Cycles
- None detected.

## Communities (86 total, 14 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "wf.py"
Cohesion: 0.05
Nodes (72): concurrent_futures, _adopt_child(), _AdoptedHandle, _attempt_api_calls(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output() (+64 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.08
Nodes (37): shlex, child_metrics(), current_attempt(), effective_runs_root(), hermes_home(), hermes_root(), launcher_profile(), node_child_home() (+29 more)

### Community 3 - "pathlib"
Cohesion: 0.06
Nodes (13): fcntl, pathlib, shutil, Identical solo child wrapper for both tag and candidate; records env key sets.…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.… (+5 more)

### Community 4 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 5 - "os"
Cohesion: 0.08
Nodes (18): contextlib, glob, hermes_constants, os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-… (+10 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "graph_check.py"
Cohesion: 0.09
Nodes (27): argparse, fnmatch, Pattern, re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this… (+19 more)

### Community 8 - "Changelog"
Cohesion: 0.07
Nodes (28): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes (+20 more)

### Community 9 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 10 - "json"
Cohesion: 0.09
Nodes (13): hashlib, json, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Lane A preconditions: null and missing ancestor fields fail before Popen, then… (+5 more)

### Community 11 - "CurrentAttemptMetrics"
Cohesion: 0.17
Nodes (10): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Top-level provenance, nodes(), CurrentAttemptMetrics (+2 more)

### Community 12 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 13 - "test_lifecycle_next_cut_0923.py"
Cohesion: 0.08
Nodes (6): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 14 - "loop"
Cohesion: 0.14
Nodes (24): _bounded_retry(), _fail_precondition(), finalize(), log(), loop(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+16 more)

### Community 15 - "run_state"
Cohesion: 0.15
Nodes (23): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_key_error(), _lane_state() (+15 more)

### Community 16 - "subprocess"
Cohesion: 0.08
Nodes (9): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, subprocess, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+1 more)

### Community 17 - "tempfile"
Cohesion: 0.08
Nodes (10): tempfile, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, Authoring door regressions; all state stays in this worktree, no…, The child launcher is operator-controlled, never a tool argument., check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission., lock() (+2 more)

### Community 18 - "jload"
Cohesion: 0.14
Nodes (22): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), amend_preview() (+14 more)

### Community 19 - "importlib_util"
Cohesion: 0.10
Nodes (11): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run… (+3 more)

### Community 20 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 21 - "__init__.py"
Cohesion: 0.12
Nodes (19): difflib, _import_call_llm(), _last_event_ts(), _output_pointer(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status() (+11 more)

### Community 22 - "act_run"
Cohesion: 0.12
Nodes (21): act_library(), act_run(), act_save(), _coerce_graph(), _input_graph(), _lane_entry(), _lane_paths(), _lib_path() (+13 more)

### Community 23 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 24 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 25 - "sys"
Cohesion: 0.13
Nodes (11): copy, sys, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Regression: launch a run in the tool's session; the payload carries a parser-… (+3 more)

### Community 26 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): rerr(), apply_graph_defaults(), _defaults_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:… (+7 more)

### Community 27 - "main"
Cohesion: 0.14
Nodes (15): acquire_lock(), emit(), main(), consume_markers(), deps_ok(), Mutable graph snapshot; hot-reloadable at wave boundaries., Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, Single-runner admission. An advisory flock held for the process lifetime IS the… (+7 more)

### Community 28 - "_resolve_models"
Cohesion: 0.15
Nodes (17): _alias_provider_pair(), handle(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)… (+9 more)

### Community 29 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 30 - "efp"
Cohesion: 0.18
Nodes (16): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then… (+8 more)

### Community 31 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 32 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 33 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 35 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 36 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 38 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 39 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 40 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 41 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.21
Nodes (13): check(), contract(), fake_call_llm(), call_llm(), _fake_parse_retry_after(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.… (+5 more)

### Community 42 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 43 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 44 - "test_prompt_workdir.py"
Cohesion: 0.26
Nodes (11): stat, check(), home_and_fakes(), main(), mk_run(), L7 — A1 durable prompt file + A4 durable child work dir. A1: the prompt as sent…, step(), check() (+3 more)

### Community 45 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 46 - "amend"
Cohesion: 0.20
Nodes (11): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Run and handoff (+3 more)

### Community 47 - "test_11_integration_team.py"
Cohesion: 0.27
Nodes (3): Lane E: cross-lane executable integration fixtures; no production…, TeamIntegration, until()

### Community 50 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 51 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 52 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): Exception, EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 53 - "_create_run"
Cohesion: 0.20
Nodes (9): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+1 more)

### Community 54 - "act_amend"
Cohesion: 0.22
Nodes (9): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+1 more)

### Community 55 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 56 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 58 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 59 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 60 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 61 - "node_facts"
Cohesion: 0.29
Nodes (7): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 62 - "Run operations and read model"
Cohesion: 0.29
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 63 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 67 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 68 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 69 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 70 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 71 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 72 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 73 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 76 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 78 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 79 - "11-golden-solo.py"
Cohesion: 0.70
Nodes (4): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…

### Community 81 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 82 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 84 - "_active_spawns"
Cohesion: 0.50
Nodes (4): _active_spawn(), _active_spawns(), Compatibility: first verified spawn for existing blocked-by consumers., All verified uncommitted child identities, never historical DB liveness.

## Knowledge Gaps
- **222 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+217 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 729 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.378) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.366) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _222 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04504504504504504 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08097165991902834 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.06258890469416785 - nodes in this community are weakly interconnected._