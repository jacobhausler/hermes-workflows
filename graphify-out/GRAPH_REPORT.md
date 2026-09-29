# Graph Report - tree  (2026-09-29)

## Corpus Check
- 121 files · ~160,018 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1417 nodes · 2846 edges · 89 communities (75 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 165 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- CurrentAttemptMetrics
- wf.py
- test_amend_rebake_034849a2.py
- pathlib
- test_prompt_workdir.py
- test_fanout_expand.mjs
- plugin_api.py
- os
- time
- json
- test_11_ui_imports.mjs
- efp
- shutil
- test_fanout_item_goal.py
- __init__.py
- test_preflight_liveness_152be7f7.py
- run_state
- test_card_frontend_contract.mjs
- subprocess
- jload
- wfcommon.py
- test_live_truth_ui.mjs
- run_agent_node
- test_register_surface.mjs
- Changelog
- act_amend
- 11-golden-solo.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- sys
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- LiveTruth
- test_node_panel.mjs
- _stamp_served
- _resolve_models
- test_orphan_adopt_790c6ad.py
- test_metrics_missing_ui.mjs
- node_facts
- _create_run
- test_11_integration_team.py
- test_deleted_cwd_resume_5c37b19.py
- Contributing to hermes-workflows
- act_run
- validate_graph_errors
- test_fanout_ui.mjs
- test_sprint101w2_B2-retry.py
- _SV
- AGENTS.md — front door for agents
- Disclosure verification — clause-by-clause evidence
- test_engine.py
- test_routing_routes.py
- model_preflight
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_fp_rule_f0f154d5.py
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_steer_live_40.py
- build_inputs
- _defaults_errors
- AGENTS.md
- 3. Operate
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Manual installation — Hermes Workflows 1.1.0
- graph_check.py
- DoorLane
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tier_report_0924.py
- test_v3_fixes.py
- _transient_retry
- _bind_run_context
- 11-keeper.py
- 11-claim-wrapper.py
- Claim
- test_sprint101_D-surface.py
- profile_errors
- when_true
- manifest.json
- Integrated
- Run
- fake
- effective_runs_root

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
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (89 total, 14 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "CurrentAttemptMetrics"
Cohesion: 0.05
Nodes (34): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, For agents and contributors, Hermes Workflows, Install (+26 more)

### Community 2 - "wf.py"
Cohesion: 0.05
Nodes (65): concurrent_futures, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+57 more)

### Community 3 - "test_amend_rebake_034849a2.py"
Cohesion: 0.05
Nodes (22): agent_reasoning_effort, atexit, importlib, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;… (+14 more)

### Community 4 - "pathlib"
Cohesion: 0.07
Nodes (21): contextlib, copy, hashlib, importlib_util, pathlib, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo (+13 more)

### Community 5 - "test_prompt_workdir.py"
Cohesion: 0.07
Nodes (36): argparse, fnmatch, Pattern, File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay (+28 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 8 - "os"
Cohesion: 0.08
Nodes (14): os, tempfile, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), Lane A preconditions: null and missing ancestor fields fail before Popen, then…, Authoring door regressions; all state stays in this worktree, no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, The child launcher is operator-controlled, never a tool argument. (+6 more)

### Community 9 - "time"
Cohesion: 0.08
Nodes (12): glob, hermes_constants, plugin_api, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final… (+4 more)

### Community 10 - "json"
Cohesion: 0.08
Nodes (9): json, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 11 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 12 - "efp"
Cohesion: 0.12
Nodes (26): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), drain_inbox(), emit(), _fail_precondition() (+18 more)

### Community 13 - "shutil"
Cohesion: 0.07
Nodes (9): fcntl, shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Library verbs + /wf command: save (from run_id / inline), library list, run…, 4052d57719653b1a: atomic library replay binding, no real runner., Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').… (+1 more)

### Community 14 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 15 - "__init__.py"
Cohesion: 0.11
Nodes (23): difflib, handle(), _import_call_llm(), _lane_key_error(), _last_event_ts(), model_tiers(), _output_pointer(), _ping_note() (+15 more)

### Community 16 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.12
Nodes (21): Exception, check(), contract(), EscapeLineOnly, fake_call_llm(), call_llm(), _fake_parse_retry_after(), FakeHTTPError (+13 more)

### Community 17 - "run_state"
Cohesion: 0.17
Nodes (20): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_state(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume… (+12 more)

### Community 18 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 19 - "subprocess"
Cohesion: 0.09
Nodes (9): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, subprocess, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;… (+1 more)

### Community 20 - "jload"
Cohesion: 0.15
Nodes (21): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), _active_spawns() (+13 more)

### Community 21 - "wfcommon.py"
Cohesion: 0.13
Nodes (20): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, Compatibility: first verified spawn for existing blocked-by consumers. (+12 more)

### Community 22 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 23 - "run_agent_node"
Cohesion: 0.12
Nodes (20): _bounded_retry(), _dangling_placeholders(), #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported…, Tool-progress evidence for the #5 bounded retry: True only when the dead… (+12 more)

### Community 24 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 25 - "Changelog"
Cohesion: 0.11
Nodes (17): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+9 more)

### Community 26 - "act_amend"
Cohesion: 0.12
Nodes (18): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _liveness_hint_suffix(), _model_names_valid(), _profile_error() (+10 more)

### Community 27 - "11-golden-solo.py"
Cohesion: 0.15
Nodes (13): re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+5 more)

### Community 28 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 29 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 30 - "sys"
Cohesion: 0.12
Nodes (5): sys, Identical solo child wrapper for both tag and candidate; records env key sets.…, End-to-end test of the `workflow` tool door against fake hermes., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…

### Community 31 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 32 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 33 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 35 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 36 - "_stamp_served"
Cohesion: 0.15
Nodes (14): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Commit actual child seat truth, never the requested alias. No row means unknown., _stamp_served(), child_metrics(), hermes_home(), node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's… (+6 more)

### Community 37 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 38 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 39 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 40 - "node_facts"
Cohesion: 0.17
Nodes (12): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS, node_facts(), precondition_facts() (+4 more)

### Community 41 - "_create_run"
Cohesion: 0.20
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.…, ONE resolver (wfcommon.runs_root): `WF_RUNS_ROOT` if set, else…, Use the tool worker's task-local session, not another turn's process env. (+3 more)

### Community 42 - "test_11_integration_team.py"
Cohesion: 0.27
Nodes (3): Lane E: cross-lane executable integration fixtures; no production…, TeamIntegration, until()

### Community 44 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 45 - "act_run"
Cohesion: 0.27
Nodes (10): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), library_root(), `/wf` — the library front door. `/wf <name> [note]` supplies the note…, 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty… (+2 more)

### Community 46 - "validate_graph_errors"
Cohesion: 0.22
Nodes (8): 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, requires_errors(), validate_graph_errors(), E(), schema_check(), wait_spec_ok()

### Community 47 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 48 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 50 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 51 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.25
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 52 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 53 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 54 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 55 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 56 - "test_fp_rule_f0f154d5.py"
Cohesion: 0.48
Nodes (6): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 57 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 60 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 61 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 62 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 64 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 65 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 66 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 67 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 68 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 69 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 70 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 72 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 73 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 76 - "_transient_retry"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, _retry_conf_params(), _transient_retry()

### Community 77 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 78 - "11-keeper.py"
Cohesion: 0.50
Nodes (4): signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until()

### Community 79 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 81 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 82 - "profile_errors"
Cohesion: 0.40
Nodes (4): launcher_profile(), profile_errors(), Launcher identity, resolved from the door's OWN HERMES_HOME — never from a…, 1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER…

### Community 83 - "when_true"
Cohesion: 0.40
Nodes (5): Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), when_expr_ok(), when_true()

### Community 84 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

## Knowledge Gaps
- **225 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+220 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 732 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.388) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.376) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _225 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.05191146881287726 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053994732221246705 - nodes in this community are weakly interconnected._
- **Should `test_amend_rebake_034849a2.py` be split into smaller, more focused modules?**
  _Cohesion score 0.047872340425531915 - nodes in this community are weakly interconnected._