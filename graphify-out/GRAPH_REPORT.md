# Graph Report - tree  (2026-09-29)

## Corpus Check
- 120 files · ~159,053 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1406 nodes · 2832 edges · 96 communities (80 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 166 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- tempfile
- efp
- test_fanout_expand.mjs
- run_agent_node
- sys
- test_prompt_workdir.py
- importlib_util
- os
- shutil
- test_11_ui_imports.mjs
- pathlib
- run_state
- test_fanout_item_goal.py
- wf.py
- test_preflight_liveness_152be7f7.py
- _adopt_child
- run_child
- __init__.py
- test_card_frontend_contract.mjs
- json
- test_live_truth_ui.mjs
- test_register_surface.mjs
- jload
- CurrentAttemptMetrics
- EngineNextCut
- plugin_api.py
- wfcommon.py
- test_sprint101w2_D2-steer-liveness.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- _SV
- Disclosure verification — clause-by-clause evidence
- SKILL.md
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- graph_check.py
- _ping_route_once
- test_orphan_adopt_790c6ad.py
- test_metrics_missing_ui.mjs
- AGENTS.md
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- amend
- Changelog
- test_fp_rule_f0f154d5.py
- validate_graph_errors
- test_node_facts.py
- Contributing to hermes-workflows
- act_amend
- TeamIntegration
- test_hermes_bin_reserved_0928.py
- test_fanout_ui.mjs
- test
- test_sprint101w2_B2-retry.py
- hermes_home
- test_engine.py
- test_routing_routes.py
- model_preflight
- Run operations and read model
- test_failures_0923.py
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_status_next.py
- test_steer_live_40.py
- _defaults_errors
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Hermes Workflows
- DoorLane
- test_model_law_dad50be0.py
- test_tier_report_0924.py
- test_v3_fixes.py
- 1.0.1 — 2026-09-25
- node_facts
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- profile_errors
- when_true
- 0.9.0 — 2026-09-24
- manifest.json
- Integrated
- Run
- node_child_home
- release_gate
- Ctx
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
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (96 total, 16 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (86): Unreleased, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+78 more)

### Community 1 - "tempfile"
Cohesion: 0.06
Nodes (21): agent_reasoning_effort, atexit, importlib, tempfile, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes… (+13 more)

### Community 2 - "efp"
Cohesion: 0.11
Nodes (34): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), _fail_precondition(), finalize() (+26 more)

### Community 3 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 4 - "run_agent_node"
Cohesion: 0.08
Nodes (32): 1.0.17 — 2026-09-28, _attempt_api_calls(), _bounded_retry(), _dangling_placeholders(), fmt_goal(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+24 more)

### Community 5 - "sys"
Cohesion: 0.07
Nodes (17): glob, hermes_constants, plugin_api, re, sqlite3, sys, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-… (+9 more)

### Community 6 - "test_prompt_workdir.py"
Cohesion: 0.09
Nodes (28): argparse, fnmatch, Pattern, Nodes and data, excluded(), load_guards(), main(), Path (+20 more)

### Community 7 - "importlib_util"
Cohesion: 0.08
Nodes (13): importlib_util, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), Lane E: cross-lane executable integration fixtures; no production…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes. (+5 more)

### Community 8 - "os"
Cohesion: 0.08
Nodes (9): os, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 9 - "shutil"
Cohesion: 0.07
Nodes (10): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when… (+2 more)

### Community 10 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 11 - "pathlib"
Cohesion: 0.10
Nodes (15): contextlib, copy, pathlib, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings. (+7 more)

### Community 12 - "run_state"
Cohesion: 0.13
Nodes (25): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_key_error(), _lane_state() (+17 more)

### Community 13 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 14 - "wf.py"
Cohesion: 0.11
Nodes (24): concurrent_futures, build_inputs(), drain_inbox(), extract_json(), hermes_home(), _inputs_block(), last_balanced_object(), _match_object() (+16 more)

### Community 15 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.12
Nodes (21): Exception, check(), contract(), EscapeLineOnly, fake_call_llm(), call_llm(), _fake_parse_retry_after(), FakeHTTPError (+13 more)

### Community 16 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 17 - "run_child"
Cohesion: 0.10
Nodes (24): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+16 more)

### Community 18 - "__init__.py"
Cohesion: 0.16
Nodes (21): difflib, _alias_provider_pair(), handle(), _last_event_ts(), _model_policy_error(), model_tiers(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat… (+13 more)

### Community 19 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 20 - "json"
Cohesion: 0.10
Nodes (7): fcntl, json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Authoring door regressions; all state stays in this worktree, no…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 21 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 22 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 23 - "jload"
Cohesion: 0.15
Nodes (19): act_library(), act_run(), act_save(), _coerce_graph(), _input_graph(), _lane_entry(), _lane_paths(), _lib_path() (+11 more)

### Community 25 - "EngineNextCut"
Cohesion: 0.21
Nodes (4): EngineNextCut, deps_ok(), dep_satisfied(), deps_ok()

### Community 26 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 27 - "wfcommon.py"
Cohesion: 0.12
Nodes (17): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), effective_runs_root(), precondition_facts(), quote_json_parse_error() (+9 more)

### Community 28 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.13
Nodes (8): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…, unittest_mock

### Community 29 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 30 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 31 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 32 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 33 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 34 - "_SV"
Cohesion: 0.14
Nodes (9): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not() (+1 more)

### Community 35 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 36 - "SKILL.md"
Cohesion: 0.13
Nodes (10): Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics (+2 more)

### Community 38 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 39 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 40 - "graph_check.py"
Cohesion: 0.20
Nodes (11): hashlib, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., check() (+3 more)

### Community 41 - "_ping_route_once"
Cohesion: 0.14
Nodes (13): _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the…, Server Retry-After, best-effort via core's parser. None when no header — NEVER… (+5 more)

### Community 42 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 43 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 44 - "AGENTS.md"
Cohesion: 0.20
Nodes (7): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component, Node budgets

### Community 45 - "_create_run"
Cohesion: 0.17
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), _liveness_hint_suffix(), Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+3 more)

### Community 47 - "amend"
Cohesion: 0.18
Nodes (11): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Run and handoff (+3 more)

### Community 48 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 49 - "test_fp_rule_f0f154d5.py"
Cohesion: 0.25
Nodes (10): Top-level provenance, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes. (+2 more)

### Community 50 - "validate_graph_errors"
Cohesion: 0.20
Nodes (9): rerr(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, requires_errors(), validate_graph_errors(), E(), schema_check() (+1 more)

### Community 51 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 52 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 53 - "act_amend"
Cohesion: 0.20
Nodes (10): act_amend(), _frozen_committed(), _model_names_valid(), _profile_error(), Return graph-level and node-level defects together, before any write/spawn., fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+2 more)

### Community 55 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 56 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 57 - "test"
Cohesion: 0.31
Nodes (8): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, _verify_spawn_rec()

### Community 58 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 59 - "hermes_home"
Cohesion: 0.22
Nodes (9): hermes_home(), hermes_root(), profile_home(), profiles_root(), The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a…, Read model.workflows_forbidden_models on the child seat, including bare CLI…, `WF_RUNS_ROOT` if set (non-empty), else `$HERMES_HOME/workflows`., runs_root() (+1 more)

### Community 60 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 61 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 62 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 63 - "Run operations and read model"
Cohesion: 0.29
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 67 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 68 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 69 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 70 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 71 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 72 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 73 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 74 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 76 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 79 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 80 - "node_facts"
Cohesion: 0.40
Nodes (5): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, node_facts(), Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 81 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 82 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 85 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 86 - "profile_errors"
Cohesion: 0.40
Nodes (4): launcher_profile(), profile_errors(), Launcher identity, resolved from the door's OWN HERMES_HOME — never from a…, 1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER…

### Community 87 - "when_true"
Cohesion: 0.40
Nodes (5): Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), when_expr_ok(), when_true()

### Community 88 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 89 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 92 - "node_child_home"
Cohesion: 0.50
Nodes (4): node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as…

### Community 93 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **224 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 724 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `plugin.js`, `run_agent_node`, `1.0.2 — 2026-09-26 — the run watches itself`, `1.0.1 — 2026-09-25`, `node_facts`, `0.9.0 — 2026-09-24`, `model_preflight`?**
  _High betweenness centrality (0.338) - this node is a cross-community bridge._
- **Why does `Unreleased` connect `plugin.js` to `Changelog`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06388666132050254 - nodes in this community are weakly interconnected._
- **Should `tempfile` be split into smaller, more focused modules?**
  _Cohesion score 0.058693244739756366 - nodes in this community are weakly interconnected._
- **Should `efp` be split into smaller, more focused modules?**
  _Cohesion score 0.10793650793650794 - nodes in this community are weakly interconnected._
- **Should `test_fanout_expand.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.06890756302521009 - nodes in this community are weakly interconnected._