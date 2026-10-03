# Graph Report - tree  (2026-10-03)

## Corpus Check
- 248 files · ~332,702 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2454 nodes · 5029 edges · 143 communities (110 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- pathlib
- json
- test_fanout_item_goal.py
- os
- wf.py
- subprocess
- jload
- SKILL.md
- lane_recover.py
- shutil
- wfcommon.py
- test_preflight_liveness_152be7f7.py
- run_child
- test_session_wake_matrix_101.py
- hermes_home
- time
- EngineNextCut
- run_agent_node
- _final_quiesce
- _Importer
- Run operations and read model
- efp
- test_fanout_expand.mjs
- _Exporter
- .meta
- plugin.js
- test_lane_hygiene_preamble_8edcc9bf.py
- act_run
- test_11_ui_imports.mjs
- test_require_route_25.py
- wf_dialect.py
- DoorLib50
- test_lane_gate_64c6772b.py
- ref_node_fs
- _sidecar_live_registered
- __init__.py
- WorkflowsPage
- test_silent_death_reaper_8.py
- 11-golden-solo.py
- test_failures_0923.py
- act_save
- threading
- test_live_truth_ui.mjs
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- NodePanel
- _ping_route_once
- CurrentAttemptMetrics
- _bounded_retry
- _expand_config_values
- plugin_api.py
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- CardBackend
- test_confidence_substrate_116.py
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- LiveTruth
- test_node_panel.mjs
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- _resolve_models
- test_proctree_61b.py
- Changelog
- test_orphan_adopt_790c6ad.py
- GraphView
- act_amend
- TeamIntegration
- test
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- Disclosure verification — clause-by-clause evidence
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- test_card_frontend_contract.mjs
- DialectRefusal
- ConcurrencyBake100
- test_node_facts.py
- Contributing to hermes-workflows
- graph_check.py
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- test_schema_enum_107.py
- .run
- Proposed core hook: tool-result card rendering (optional, upstream-shaped)
- act_wait
- test_sprint101w2_B2-retry.py
- _SV
- _input_graph
- test_routing_routes.py
- test_run_dry_run.py
- child_work_dir
- model_preflight
- dep_satisfied
- install
- LifecycleNotice
- CoreFaithfulCtx
- test_incident_response_93.py
- test_steer_live_40.py
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- _route_enforcement
- DoorLane
- Claim
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- 1.0.1 — 2026-09-25
- 11-claim-wrapper.py
- native_engine
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- _AdoptedHandle
- _lane_hygiene_preamble
- _quota_note
- Run
- substrate_disclosure_text
- release_gate
- date-now.js
- meta-nonliteral.js
- Ctx
- Ctx
- Ctx
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
1. `run_child()` - 46 edges
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
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (143 total, 33 thin omitted)

### Community 0 - "pathlib"
Cohesion: 0.05
Nodes (32): copy, hashlib, pathlib, re, main(), pr_tag_audit.py — release-time gate for `(open PR #NN)` doc tags. Docs that…, resolve_repo(), sys (+24 more)

### Community 1 - "json"
Cohesion: 0.04
Nodes (21): importlib_util, json, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, B2b probes (peer-review owed items): (A) empty-array query shares the save law,… (+13 more)

### Community 2 - "test_fanout_item_goal.py"
Cohesion: 0.06
Nodes (45): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), _assert_no_fail_closed(), _assert_prompts_carry_own(), cards() (+37 more)

### Community 3 - "os"
Cohesion: 0.06
Nodes (33): contextlib, os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), main() (+25 more)

### Community 4 - "wf.py"
Cohesion: 0.04
Nodes (52): concurrent_futures, socket, est-6st - a reply that IS serialized tool-call markup must never coerce. Field…, urllib_error, _child_spoke(), _crash_gen(), drain_inbox(), extract_json() (+44 more)

### Community 5 - "subprocess"
Cohesion: 0.04
Nodes (19): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, subprocess, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness. (+11 more)

### Community 6 - "jload"
Cohesion: 0.09
Nodes (44): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), finalize(), main(), consume_markers(), loop() (+36 more)

### Community 7 - "SKILL.md"
Cohesion: 0.06
Nodes (29): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is, Apply (source install only) (+21 more)

### Community 8 - "lane_recover.py"
Cohesion: 0.08
Nodes (40): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+32 more)

### Community 9 - "shutil"
Cohesion: 0.05
Nodes (13): shutil, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, #113 — validate() must split integer from number and reject booleans. Before…, #61 — the runner is process-tree aware before it judges an attempt. Evidence…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), lock() (+5 more)

### Community 10 - "wfcommon.py"
Cohesion: 0.07
Nodes (35): shlex, amend_preview(), current_attempt(), _defaults_errors(), _downstream(), grammar_errors(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, Install the door's plugin-scoped reader: fn(key) -> value | None | NO_READER. (+27 more)

### Community 11 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check(), contract() (+21 more)

### Community 12 - "run_child"
Cohesion: 0.09
Nodes (39): _adopt_child(), _cancel_evidence(), _classify_rc_output(), derived_contract(), _harvest_cancelled(), _harvest_death(), log(), _log_recent() (+31 more)

### Community 13 - "test_session_wake_matrix_101.py"
Cohesion: 0.07
Nodes (21): http_server, inspect, action_rows(), _append_act(), _door_call(), Owner, parked(), BaseHTTPRequestHandler (+13 more)

### Community 14 - "hermes_home"
Cohesion: 0.07
Nodes (35): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), find_run(), hermes_home(), hermes_root(), launch_runs_root(), launcher_profile() (+27 more)

### Community 15 - "time"
Cohesion: 0.05
Nodes (12): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, wf(), on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, sh(), Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1… (+4 more)

### Community 16 - "EngineNextCut"
Cohesion: 0.08
Nodes (21): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+13 more)

### Community 17 - "run_agent_node"
Cohesion: 0.07
Nodes (34): 1.0.17 — 2026-09-28, _attempt_api_calls(), build_inputs(), _dangling_placeholders(), fmt_goal(), _inputs_block(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, Backoff schedule / per-run budget come ONLY from run.json meta (the door's… (+26 more)

### Community 18 - "_final_quiesce"
Cohesion: 0.09
Nodes (36): _account_tree(), _complete(), _boot_sweep(), _final_quiesce(), _isolate_prior(), _kill_pool(), _left_live_record(), _proc_alive() (+28 more)

### Community 19 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 20 - "Run operations and read model"
Cohesion: 0.08
Nodes (35): For agents and contributors, Graph grammar in 30 seconds, Hermes Workflows, Install, License, Requirements, The `workflow` tool, Two builds, one codebase (+27 more)

### Community 21 - "efp"
Cohesion: 0.10
Nodes (33): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Per-run concurrency (optional), Staleness and replay, Tags (meta envelope), Top-level provenance, Portable workflow files (publish = put the file on git) (+25 more)

### Community 22 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 23 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 24 - ".meta"
Cohesion: 0.09
Nodes (30): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+22 more)

### Community 25 - "plugin.js"
Cohesion: 0.09
Nodes (31): api(), BREATHE, ctxRest(), DirectiveCard(), EDGE_TONE, $fanExpanded, $fanItem, $fanOpen (+23 more)

### Community 26 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 27 - "act_run"
Cohesion: 0.09
Nodes (29): act_list(), act_run(), act_status(), _card(), _concurrency_bake(), _create_run(), _hermes_bin(), _identity_stamps() (+21 more)

### Community 28 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 29 - "test_require_route_25.py"
Cohesion: 0.07
Nodes (16): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+8 more)

### Community 30 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 32 - "test_lane_gate_64c6772b.py"
Cohesion: 0.08
Nodes (12): atexit, importlib, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v(), FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal… (+4 more)

### Community 33 - "ref_node_fs"
Cohesion: 0.10
Nodes (18): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, here, plugin, src (+10 more)

### Community 34 - "_sidecar_live_registered"
Cohesion: 0.09
Nodes (27): _proc_boottime(), _proc_children_of(), _proc_envv(), _proc_snapshot(), _proc_state(), Can the process table be read at all? #61b B2 (fail-closed family of the door's…, Kernel start tick of a pid: field 22 of /proc/pid/stat (starttime, clock ticks…, One pass over /proc: {pid: (ppid, pgid)} for LIVE (non-zombie) pids. Zombie =… (+19 more)

### Community 35 - "__init__.py"
Cohesion: 0.11
Nodes (25): difflib, act_inbox(), act_steer(), act_submit(), handle(), _model_names_valid(), model_tiers(), _owner_settings_error() (+17 more)

### Community 36 - "WorkflowsPage"
Cohesion: 0.18
Nodes (23): ago(), DirectiveBody(), Dot(), fmtDur(), idleS(), idleTone(), inlineHeader(), ItemCard() (+15 more)

### Community 37 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 38 - "11-golden-solo.py"
Cohesion: 0.10
Nodes (14): glob, hermes_constants, plugin_api, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3… (+6 more)

### Community 39 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 40 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 41 - "threading"
Cohesion: 0.10
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, wf(), P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 42 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 43 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 44 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 45 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 46 - "NodePanel"
Cohesion: 0.15
Nodes (19): attemptNo(), box(), defaultTabFor(), factText(), fanCounts(), fanItems(), FanStrip(), fanSummary() (+11 more)

### Community 47 - "_ping_route_once"
Cohesion: 0.12
Nodes (18): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal(), Core-less cron door: use the operator's child launcher's venv Python. Missing… (+10 more)

### Community 49 - "_bounded_retry"
Cohesion: 0.11
Nodes (19): _aux_run(), _bounded_retry(), hermes_home(), _kill_aux_tree(), _lane_gate(), Message-existence evidence for the #102 dead-session guard: True when the dead…, Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, subprocess.run-shaped helper for the runner's OWN auxiliary probes, registered… (+11 more)

### Community 50 - "_expand_config_values"
Cohesion: 0.11
Nodes (19): Where to POST a wake, host config first (mirrors the api_server adapter's own…, _wake_endpoint(), _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _expand_config_values(), _is_non_env_secret_ref() (+11 more)

### Community 51 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 52 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 53 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 54 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 55 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 56 - "test_confidence_substrate_116.py"
Cohesion: 0.14
Nodes (11): alive(), HTTP429, Meta, dict, Exception, #116 — confidence_substrate: engine-stamped fallback when a pinned confidence…, Stub the core ping seam like test_require_route_25: behavior keyed by…, Estate config.yaml: top-level `workflows:` section with the owner's… (+3 more)

### Community 57 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 59 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 60 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 62 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 63 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.21
Nodes (14): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, GateActions(), nudgeOwner(), Pill(), pillProgress(), PillRail(), railModel(), RailPanel() (+6 more)

### Community 64 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Compatibility wrapper: resolve models and return the historical (error, table)… (+6 more)

### Community 65 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 66 - "Changelog"
Cohesion: 0.15
Nodes (13): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+5 more)

### Community 67 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 68 - "GraphView"
Cohesion: 0.26
Nodes (13): bandRows(), columnGroups(), depthMap(), edgeFlowPolicy(), Edges(), edgeTone(), FanStack(), GraphView() (+5 more)

### Community 69 - "act_amend"
Cohesion: 0.18
Nodes (13): act_amend(), act_release(), act_stop(), _frozen_committed(), _profile_error(), Strict: no silent normalization — ids double as directory names. Profile-scoped…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, ONE gate-answer path for tool and UI. Stale answers never block: the answer… (+5 more)

### Community 70 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 71 - "test"
Cohesion: 0.19
Nodes (12): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), active_child(), _active_spawn(), _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +… (+4 more)

### Community 72 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 73 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 74 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.17
Nodes (12): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law… (+4 more)

### Community 76 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 77 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 78 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 79 - "DialectRefusal"
Cohesion: 0.20
Nodes (7): The js dialect seam: `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 81 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 82 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 83 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 84 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 85 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 86 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 87 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 88 - "Proposed core hook: tool-result card rendering (optional, upstream-shaped)"
Cohesion: 0.22
Nodes (8): 1. New area + payload type — `lib/tool-result-contribs.ts` (new file), 2. Export from the SDK — `sdk/index.ts`, 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`, Plugin-side readiness, Proposed core hook: tool-result card rendering (optional, upstream-shaped), The patch (≈30 lines, additive), What the plugin would then register (one block, `desktop/plugin.js`), Why (issue #157)

### Community 89 - "act_wait"
Cohesion: 0.25
Nodes (8): act_wait(), _respawn_throttled(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, #8 fix-law item 2 (crash-visibility): make a silent runner death loud BEFORE a…, ONE bridge: the crash-visibility reaper, then the spawn. Every door path that…, _reap_silent_death(), _respawn_runner(), _after_death()

### Community 90 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 92 - "_input_graph"
Cohesion: 0.25
Nodes (8): _coerce_graph(), _inline_graph_size_error(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 93 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 95 - "child_work_dir"
Cohesion: 0.25
Nodes (8): _banked_work(), child_work_dir(), _clean_capture(), _dead_session_harvest(), Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —…, The #102 harvest preamble for a re-drive whose prior session persisted NO…, A4: every child starts in <run>/work/<node>[.<i>]/. Relative paths land in the…

### Community 96 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 97 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 98 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 100 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 101 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 102 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 103 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 104 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 105 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 106 - "_route_enforcement"
Cohesion: 0.33
Nodes (6): _confidence_substitute(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #116: declared-fallback branch of the #25 gate (R6: same path, not a parallel…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 109 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 110 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 111 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 112 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 113 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 114 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 115 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 116 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 121 - "_lane_hygiene_preamble"
Cohesion: 0.50
Nodes (4): _is_build_lane(), _lane_hygiene_preamble(), The build shape: `shape: "build"` declared, or a `repo:` lane declared (the…, Machine-generated lane-hygiene preamble for build-shape nodes ("" otherwise).…

### Community 122 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

### Community 124 - "substrate_disclosure_text"
Cohesion: 0.50
Nodes (4): apply_substrate_disclosure(), The engine's honest-label sentence — verbatim material for the schema…, Engine-inject the disclosure clause into the node's RESULT SCHEMA (mirrors how…, substrate_disclosure_text()

### Community 125 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **302 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1232 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `_resolve_models`, `Changelog`, `GraphView`, `jload`, `test`, `run_agent_node`, `act_wait`?**
  _High betweenness centrality (0.210) - this node is a cross-community bridge._
- **Why does `useValue()` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `label()` connect `NodePanel` to `.meta`, `plugin.js`, `Run operations and read model`, `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _302 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.047086247086247084 - nodes in this community are weakly interconnected._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.04278846153846154 - nodes in this community are weakly interconnected._
- **Should `test_fanout_item_goal.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._