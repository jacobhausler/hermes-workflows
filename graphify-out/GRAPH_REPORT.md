# Graph Report - tree  (2026-10-03)

## Corpus Check
- 250 files · ~334,748 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2468 nodes · 5054 edges · 161 communities (123 shown, 38 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- json
- wf.py
- test_fanout_item_goal.py
- os
- jload
- sys
- lane_recover.py
- shutil
- test_fanout_expand.mjs
- _Exporter
- .meta
- plugin_api.py
- run_state
- re
- test_lane_hygiene_preamble_8edcc9bf.py
- __init__.py
- test_11_ui_imports.mjs
- main
- _final_quiesce
- test_require_route_25.py
- subprocess
- plugin.js
- DoorLib50
- node_rec
- ref_node_fs
- wf_dialect.py
- _Importer
- _sidecar_live_registered
- Run operations and read model
- pathlib
- Changelog
- test_silent_death_reaper_8.py
- hermes_home
- .agent_args
- _ping_route_once
- wfcommon.py
- threading
- test_preflight_liveness_152be7f7.py
- act_save
- test_live_truth_ui.mjs
- test_session_wake_matrix_101.py
- test_daemonize_8.py
- act_run
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- NodePanel
- 11-golden-solo.py
- CurrentAttemptMetrics
- SKILL.md
- test_register_surface.mjs
- _input_graph
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance
- CardBackend
- test_confidence_substrate_116.py
- test_edge_routing.mjs
- EngineNextCut
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- LiveTruth
- test_machine_watch_94.py
- test_node_panel.mjs
- 3. Operate
- _create_run
- test_proctree_61b.py
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- test_orphan_adopt_790c6ad.py
- GraphView
- Disclosure verification — clause-by-clause evidence
- test_sprint101w2_B1-classes.py
- TeamIntegration
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- node_facts
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- validate_graph_errors
- when_true
- test_route_efforts_b3c98b2a.py
- DirectiveBody
- test_card_frontend_contract.mjs
- efp
- settings_runs_root
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- test_malformed_turn_541.py
- Contributing to hermes-workflows
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- test_schema_enum_107.py
- _expand_config_values
- Proposed core hook: tool-result card rendering (optional, upstream-shaped)
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_lost_handoff_sync_wake_r18.py
- test_sprint101w2_B2-retry.py
- DialectRefusal
- hermes_home
- _SV
- WorkflowsPage
- Owner
- test_numeric_type_validation_113.py
- test_resume_fresh_session_102.py
- test_routing_routes.py
- test_run_dry_run.py
- _aux_run
- dep_satisfied
- Vitals
- install
- suite.py
- LifecycleNotice
- graph_fingerprint
- test_incident_response_93.py
- test_status_next.py
- test_steer_live_40.py
- build_inputs
- _defaults_errors
- _env_ref_var_name
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- Manual installation — Hermes Workflows 1.2.0
- Portable workflow files (publish = put the file on git)
- DoorLane
- Claim
- test_failed_events_77.py
- test_model_law_dad50be0.py
- _fake_parse_retry_after
- test_suite_admission_17.py
- test_tier_report_0924.py
- _dead_session_harvest
- Contributor checks (not ordinary user setup)
- Operator playbook (measured lessons)
- test_sprint101w2_C1-defaults.py
- manifest.json
- Graph grammar and authoring boundaries
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- _wake_append
- date-now.js
- meta-nonliteral.js
- Ctx
- Ctx
- Ctx
- _NoRedirect
- fake
- args-iterable.js
- args-template.js
- audit-routes.js
- pipeline-glue-stage.js
- pipeline-length-template.js
- dialect/README.md
- sequential-awaits.js
- static-parallel.js
- two-stage-pipeline.js
- unknown-option.js
- while-loop.js

## God Nodes (most connected - your core abstractions)
1. `run_child()` - 47 edges
2. `jload()` - 40 edges
3. `efp()` - 40 edges
4. `main()` - 32 edges
5. `DoorLib50` - 27 edges
6. `log()` - 27 edges
7. `_Importer` - 27 edges
8. `loop()` - 26 edges
9. `_Exporter` - 26 edges
10. `_adopt_child()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `What the plugin would then register (one block, `desktop/plugin.js`)` --references--> `SessionStrip()`  [INFERRED]
  docs/card-toolresult-hook.md → desktop/plugin.js
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` --references--> `useValue()`  [INFERRED]
  CHANGELOG.md → tests/test_fanout_expand.mjs
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (161 total, 38 thin omitted)

### Community 0 - "json"
Cohesion: 0.04
Nodes (38): atexit, importlib, json, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+30 more)

### Community 1 - "wf.py"
Cohesion: 0.05
Nodes (74): concurrent_futures, socket, urllib_error, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir() (+66 more)

### Community 2 - "test_fanout_item_goal.py"
Cohesion: 0.06
Nodes (45): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), _assert_no_fail_closed(), _assert_prompts_carry_own(), cards() (+37 more)

### Community 3 - "os"
Cohesion: 0.05
Nodes (21): os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.… (+13 more)

### Community 4 - "jload"
Cohesion: 0.06
Nodes (49): _bounded_retry(), drain_inbox(), _fail_precondition(), finalize(), _isolate_prior(), log(), loop(), notify() (+41 more)

### Community 5 - "sys"
Cohesion: 0.05
Nodes (20): copy, importlib_util, sys, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Docs-surface drift guard: the README's tool-action table must name exactly the…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes., Core-10 #89 review blocker: the EFFECTIVE synthesis prompt must not carry the… (+12 more)

### Community 6 - "lane_recover.py"
Cohesion: 0.08
Nodes (40): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+32 more)

### Community 7 - "shutil"
Cohesion: 0.05
Nodes (13): shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Ledger e68544a37be37657 (fb-fix-2dd8de73): a harvest-on-death `partial` must…, #61 — the runner is process-tree aware before it judges an attempt. Evidence…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, 4052d57719653b1a: atomic library replay binding, no real runner. (+5 more)

### Community 8 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (29): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+21 more)

### Community 9 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 10 - ".meta"
Cohesion: 0.09
Nodes (30): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+22 more)

### Community 11 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 12 - "run_state"
Cohesion: 0.09
Nodes (29): act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state() (+21 more)

### Community 13 - "re"
Cohesion: 0.09
Nodes (18): re, _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this… (+10 more)

### Community 14 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 15 - "__init__.py"
Cohesion: 0.11
Nodes (29): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), difflib, _alias_provider_pair(), handle(), _model_policy_error(), model_preflight(), model_tiers(), _nearest_effort() (+21 more)

### Community 16 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 17 - "main"
Cohesion: 0.08
Nodes (28): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), _crash_gen(), emit(), main(), consume_markers(), _stop_watcher() (+20 more)

### Community 18 - "_final_quiesce"
Cohesion: 0.09
Nodes (30): _account_tree(), _complete(), _boot_sweep(), _final_quiesce(), _kill_pool(), _left_live_record(), _proc_alive(), _proc_pids_by_pgid() (+22 more)

### Community 19 - "test_require_route_25.py"
Cohesion: 0.07
Nodes (16): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+8 more)

### Community 20 - "subprocess"
Cohesion: 0.09
Nodes (15): contextlib, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness., GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., LaneSupervisor (+7 more)

### Community 21 - "plugin.js"
Cohesion: 0.09
Nodes (27): api(), BREATHE, ctxRest(), EDGE_TONE, $fanExpanded, $fanItem, $fanOpen, GATE_PULSE (+19 more)

### Community 23 - "node_rec"
Cohesion: 0.10
Nodes (27): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), terminal_action_pending(), The run's ALREADY-COMMITTED failed-node set straight from the node records…, _wake_resolved_failed() (+19 more)

### Community 24 - "ref_node_fs"
Cohesion: 0.10
Nodes (18): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, here, plugin, src (+10 more)

### Community 25 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _line() (+16 more)

### Community 26 - "_Importer"
Cohesion: 0.16
Nodes (10): _control_kw(), _forbidden_label(), _Importer, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the… (+2 more)

### Community 27 - "_sidecar_live_registered"
Cohesion: 0.09
Nodes (26): _proc_boottime(), _proc_children_of(), _proc_envv(), _proc_snapshot(), _proc_state(), Can the process table be read at all? #61b B2 (fail-closed family of the door's…, Kernel start tick of a pid: field 22 of /proc/pid/stat (starttime, clock ticks…, One pass over /proc: {pid: (ppid, pgid)} for LIVE (non-zombie) pids. Zombie =… (+18 more)

### Community 28 - "Run operations and read model"
Cohesion: 0.10
Nodes (25): For agents and contributors, Graph grammar in 30 seconds, Hermes Workflows, Install, License, Requirements, The `workflow` tool, Two builds, one codebase (+17 more)

### Community 29 - "pathlib"
Cohesion: 0.09
Nodes (13): pathlib, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), porcelain(), est-954r pin — the B1 test's raw run must never dirty the tracked tree.…, Tracked-path dirt as {path: XY}, parsed from git status --porcelain. (+5 more)

### Community 30 - "Changelog"
Cohesion: 0.09
Nodes (23): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+15 more)

### Community 31 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 32 - "hermes_home"
Cohesion: 0.09
Nodes (23): Nodes and data, _attempt_api_calls(), _dangling_placeholders(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, Where to POST a wake, host config first (mirrors the api_server adapter's own…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, _tool_progress() (+15 more)

### Community 33 - ".agent_args"
Cohesion: 0.15
Nodes (13): _ordered(), _parse_literal(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the… (+5 more)

### Community 34 - "_ping_route_once"
Cohesion: 0.10
Nodes (21): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+13 more)

### Community 35 - "wfcommon.py"
Cohesion: 0.09
Nodes (20): shlex, _active_spawn(), apply_substrate_disclosure(), current_attempt(), launch_runs_root(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, ±40 chars of the source around the offset of a JSONDecodeError — what the door… (+12 more)

### Community 36 - "threading"
Cohesion: 0.09
Nodes (8): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, wf(), Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, wf(), P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 37 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 38 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 39 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 40 - "test_session_wake_matrix_101.py"
Cohesion: 0.11
Nodes (10): _A, answer(), _B, base_env(), drive(), mk(), BaseHTTPRequestHandler, A run dir as the door creates one (wake_protocol stamp included), so the… (+2 more)

### Community 41 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 42 - "act_run"
Cohesion: 0.12
Nodes (20): act_amend(), act_run(), _concurrency_bake(), _confidence_substitute(), _frozen_committed(), _lane_entry(), _lane_paths(), _liveness_hint_suffix() (+12 more)

### Community 43 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 44 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 45 - "NodePanel"
Cohesion: 0.15
Nodes (19): attemptNo(), box(), defaultTabFor(), factText(), fanCounts(), fanItems(), FanStrip(), fanSummary() (+11 more)

### Community 46 - "11-golden-solo.py"
Cohesion: 0.13
Nodes (12): glob, hermes_constants, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Exception (+4 more)

### Community 48 - "SKILL.md"
Cohesion: 0.17
Nodes (7): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Node budgets

### Community 49 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 50 - "_input_graph"
Cohesion: 0.12
Nodes (17): act_inbox(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., #50 (epic #49): submit a hand-rolled graph for STUDY — the quarantine inbox… (+9 more)

### Community 51 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 52 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 53 - "1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance"
Cohesion: 0.13
Nodes (15): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, launcher_profile(), _no_unresolved_ref(), node_child_home(), node_child_metrics(), profile_errors(), profile_home(), profiles_root() (+7 more)

### Community 54 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 55 - "test_confidence_substrate_116.py"
Cohesion: 0.14
Nodes (11): alive(), HTTP429, Meta, dict, Exception, #116 — confidence_substrate: engine-stamped fallback when a pinned confidence…, Stub the core ping seam like test_require_route_25: behavior keyed by…, Estate config.yaml: top-level `workflows:` section with the owner's… (+3 more)

### Community 56 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 59 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 60 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 62 - "test_machine_watch_94.py"
Cohesion: 0.16
Nodes (8): argv(), check(), native_engine(), spawn(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling., Door-transport guard: run_context must never silently route a map to seed.…, state()

### Community 63 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 64 - "3. Operate"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+6 more)

### Community 65 - "_create_run"
Cohesion: 0.18
Nodes (14): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), _lifecycle_notice(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env. (+6 more)

### Community 66 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 67 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.23
Nodes (13): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, DirectiveCard(), focusAtom(), groupRuns(), ownedRuns(), PillRail(), RailPanel(), register() (+5 more)

### Community 68 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 69 - "GraphView"
Cohesion: 0.26
Nodes (13): bandRows(), columnGroups(), depthMap(), edgeFlowPolicy(), Edges(), edgeTone(), FanStack(), GraphView() (+5 more)

### Community 70 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.15
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, 6. Desktop gate answer (maintainer ask #122099, teknium1), Disclosure verification — clause-by-clause evidence, One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or… (+5 more)

### Community 71 - "test_sprint101w2_B1-classes.py"
Cohesion: 0.15
Nodes (4): hashlib, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, #32 publish-as-file: the portable workflow file convention. (1) top-level…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…

### Community 72 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 73 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 74 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 75 - "node_facts"
Cohesion: 0.17
Nodes (12): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS, node_facts(), precondition_facts() (+4 more)

### Community 77 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 78 - "validate_graph_errors"
Cohesion: 0.18
Nodes (10): grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), validate_graph_errors(), E() (+2 more)

### Community 79 - "when_true"
Cohesion: 0.21
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr() (+4 more)

### Community 80 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 81 - "DirectiveBody"
Cohesion: 0.31
Nodes (11): ago(), DirectiveBody(), fmtDur(), nodesCount(), PaneRow(), parseTime(), pillModel(), runHeaderModel() (+3 more)

### Community 82 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 83 - "efp"
Cohesion: 0.22
Nodes (11): File-authored graphs, Per-run concurrency (optional), Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then… (+3 more)

### Community 84 - "settings_runs_root"
Cohesion: 0.20
Nodes (10): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), _nested(), owner_setting(), A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives…, One owner-settings read: the door's plugin ctx when it has one (its answer is…, `settings.runs_root` as a validated absolute Path, or None when unset/empty.…, The runs root a process RUNS UNDER, from its environment mapping (str->str,… (+2 more)

### Community 85 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 87 - "test_malformed_turn_541.py"
Cohesion: 0.18
Nodes (5): est-2ek.1.541 — a malformed turn (final reply = serialized tool-call markup)…, Spawns = per-attempt stdout logs the runner wrote (logs/<node>.a<N>.log)., The markup must never ride a COMMITTED answer: no done/partial status, and…, record_never_commits_markup(), spawns_of()

### Community 88 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 89 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 90 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 91 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 92 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 93 - "_expand_config_values"
Cohesion: 0.20
Nodes (10): _expand_config_value(), _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Expand one `${VAR}` (legacy bare name) or `${env:VAR}` (Cursor-style SecretRef)…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, Top-level `workflows: confidence_substrate:` — full YAML when a loader is…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings() (+2 more)

### Community 94 - "Proposed core hook: tool-result card rendering (optional, upstream-shaped)"
Cohesion: 0.22
Nodes (8): 1. New area + payload type — `lib/tool-result-contribs.ts` (new file), 2. Export from the SDK — `sdk/index.ts`, 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`, Plugin-side readiness, Proposed core hook: tool-result card rendering (optional, upstream-shaped), The patch (≈30 lines, additive), What the plugin would then register (one block, `desktop/plugin.js`), Why (issue #157)

### Community 95 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 96 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.28
Nodes (6): http_server, inspect, action_rows(), parked(), PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous…, wait_for()

### Community 97 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 98 - "DialectRefusal"
Cohesion: 0.28
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 99 - "hermes_home"
Cohesion: 0.25
Nodes (9): hermes_home(), Message-existence evidence for the #102 dead-session guard: True when the dead…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map() (+1 more)

### Community 101 - "WorkflowsPage"
Cohesion: 0.32
Nodes (8): Dot(), ItemCard(), Pill(), pillProgress(), PolishStyles(), railModel(), statusLabel(), WorkflowsPage()

### Community 102 - "Owner"
Cohesion: 0.29
Nodes (5): _append_act(), _door_call(), Owner, BaseHTTPRequestHandler, The api_server shape: the POST stays open for the whole owner turn…

### Community 105 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 107 - "_aux_run"
Cohesion: 0.25
Nodes (8): _aux_run(), _kill_aux_tree(), _lane_gate(), Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, subprocess.run-shaped helper for the runner's OWN auxiliary probes, registered…, SIGKILL the aux child AND its group (the child is its own group leader via…, fb-digest-29d (64c6772b): a node that declares `repo: <path>` owns a git lane,…, _resume_preamble()

### Community 108 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 109 - "Vitals"
Cohesion: 0.48
Nodes (7): idleS(), idleTone(), inlineHeader(), ItemChips(), kfmt(), usd(), Vitals()

### Community 110 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 111 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 113 - "graph_fingerprint"
Cohesion: 0.48
Nodes (6): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 114 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 115 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 116 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 117 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet.…, Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 118 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 119 - "_env_ref_var_name"
Cohesion: 0.29
Nodes (7): _env_ref_lookup(), _env_ref_var_name(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain…

### Community 120 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 121 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 122 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 123 - "Manual installation — Hermes Workflows 1.2.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.2.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 124 - "Portable workflow files (publish = put the file on git)"
Cohesion: 0.53
Nodes (6): Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), 1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the…, source_digest()

### Community 128 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 129 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (5): _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, Meta, dict

### Community 130 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 132 - "_dead_session_harvest"
Cohesion: 0.33
Nodes (6): _banked_work(), _clean_capture(), _dead_session_harvest(), Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —…, The #102 harvest preamble for a re-drive whose prior session persisted NO…

### Community 133 - "Contributor checks (not ordinary user setup)"
Cohesion: 0.40
Nodes (4): Build-lane hygiene and lane recovery, Contributor checks (not ordinary user setup), RED before green, The one canonical suite command

### Community 134 - "Operator playbook (measured lessons)"
Cohesion: 0.40
Nodes (5): Babysitting (read the status model, not `ps`), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons)

### Community 136 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 137 - "Graph grammar and authoring boundaries"
Cohesion: 0.50
Nodes (4): Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Tags (meta envelope)

### Community 138 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 142 - "_wake_append"
Cohesion: 0.50
Nodes (4): Redact bearer/credential shapes out of anything the wake path may persist., Append one ledger row; a failure is loud on stderr (runner.log) and NEVER…, _wake_append(), _wake_safe()

## Knowledge Gaps
- **302 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1242 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `GraphView`, `test_fanout_expand.mjs`, `run_state`, `__init__.py`, `plugin.js`, `build_inputs`, `node_rec`, `Changelog`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `useValue()` connect `test_fanout_expand.mjs` to `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `label()` connect `NodePanel` to `.meta`, `test_card_frontend_contract.mjs`, `plugin.js`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _302 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.04395604395604396 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04647983595352016 - nodes in this community are weakly interconnected._
- **Should `test_fanout_item_goal.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._