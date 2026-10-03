# Graph Report - tree  (2026-10-03)

## Corpus Check
- 261 files · ~359,422 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 5)

## Summary
- 2606 nodes · 5321 edges · 154 communities (121 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 306 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- wfcommon.py
- wf.py
- pathlib
- jload
- os
- json
- shutil
- run_agent_node
- _final_quiesce
- subprocess
- graph_regen.py
- ref_node_fs
- time
- _Importer
- plugin.js
- test_fanout_expand.mjs
- _Exporter
- efp
- lane_recover.py
- plugin_api.py
- test_11_ui_imports.mjs
- wf_dialect.py
- amend
- threading
- DoorLib50
- test_fanout_item_goal.py
- __init__.py
- act_status
- _ping_route_once
- test_silent_death_reaper_8.py
- act_save
- .meta
- test_lane_hygiene_preamble_8edcc9bf.py
- Changelog
- test_preflight_liveness_152be7f7.py
- test_proctree_identity_80.py
- EngineNextCut
- NodePanel
- act_run
- test_live_truth_ui.mjs
- _expand_include_pass
- 3. Operate
- test_tiers.py
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- test_orphan_adopt_790c6ad.py
- CurrentAttemptMetrics
- test_register_surface.mjs
- SKILL.md
- Graph grammar and authoring boundaries
- test_canvas_wrap.mjs
- test_proctree_61.py
- test_node_click_expand.mjs
- DirectiveBody
- _resolve_models
- test_lost_handoff_sync_wake_r18.py
- CardBackend
- test_confidence_substrate_116.py
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- graph_fingerprint
- 11-golden-solo.py
- test_require_route_25.py
- test_proctree_61b.py
- fmt_goal
- test_session_wake_101.py
- act_amend
- TeamIntegration
- test_pill_rail.mjs
- BaseHTTPRequestHandler
- test_session_wake_matrix_101.py
- test_wfpid_owner_8.py
- WorkflowsPage
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- validate_graph_errors
- test_route_efforts_b3c98b2a.py
- pack.py
- DialectRefusal
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- test_malformed_turn_541.py
- test_include_expansion_core.py
- Contributing to hermes-workflows
- graph_check.py
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- test_schema_enum_107.py
- .run
- structural_graph_errors
- Proposed core hook: tool-result card rendering (optional, upstream-shaped)
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_B2-retry.py
- _SV
- _input_graph
- test_graph_single_writer_153.py
- test_numeric_type_validation_113.py
- test_routing_routes.py
- test_run_dry_run.py
- _B
- _proc_boottime
- model_preflight
- install
- suite.py
- LifecycleNotice
- CoreFaithfulCtx
- test_include_door.py
- test_lane_gate_64c6772b.py
- test_status_next.py
- test_steer_live_40.py
- _include_text_fields
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- Manual installation — Hermes Workflows 1.2.0
- DoorLane
- Claim
- test_suite_admission_17.py
- test_suite_zero_discovery_112.py
- Operator playbook (measured lessons)
- 11-claim-wrapper.py
- test_11_common_team_readmodel.py
- native_engine
- test_papercuts_0922.py
- test_validator_caps.py
- manifest.json
- label
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- node_child_home
- date-now.js
- meta-nonliteral.js
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
1. `run_child()` - 48 edges
2. `jload()` - 41 edges
3. `efp()` - 41 edges
4. `main()` - 32 edges
5. `DoorLib50` - 27 edges
6. `log()` - 27 edges
7. `_Importer` - 27 edges
8. `act_run()` - 26 edges
9. `_adopt_child()` - 26 edges
10. `loop()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `What the plugin would then register (one block, `desktop/plugin.js`)` --references--> `SessionStrip()`  [INFERRED]
  docs/card-toolresult-hook.md → desktop/plugin.js
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `4. What this PR does not decide` --references--> `echo()`  [INFERRED]
  references/dialect.md → tests/test_include_expansion_core.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (154 total, 33 thin omitted)

### Community 0 - "wfcommon.py"
Cohesion: 0.04
Nodes (85): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, Where to POST a wake, host config first (mirrors the api_server adapter's own…, _wake_endpoint(), amend_preview(), apply_substrate_disclosure(), blocked_legibility(), confidence_substrate() (+77 more)

### Community 1 - "wf.py"
Cohesion: 0.04
Nodes (83): concurrent_futures, socket, est-jec0 / PR #122 B1 pin: the prose-JSON fallback must never crash the node.…, urllib_error, _adopt_child(), _AdoptedHandle, _banked_work(), _cancel_evidence() (+75 more)

### Community 2 - "pathlib"
Cohesion: 0.04
Nodes (34): copy, pathlib, re, main(), pr_tag_audit.py — release-time gate for `(open PR #NN)` doc tags. Docs that…, resolve_repo(), sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.… (+26 more)

### Community 3 - "jload"
Cohesion: 0.04
Nodes (68): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), All per-item spawn records with a live pid, once every item is RUNNING., read_children(), _crash_gen(), main() (+60 more)

### Community 4 - "os"
Cohesion: 0.06
Nodes (39): contextlib, hashlib, importlib_util, os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.… (+31 more)

### Community 5 - "json"
Cohesion: 0.04
Nodes (18): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Authoring door regressions; all state stays in this worktree, no…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, B2b probes (peer-review owed items): (A) empty-array query shares the save law,…, #146 item 2 (peer review): the empty-result self-diagnosis must distinguish…, Library verbs + /wf command: save (from run_id / inline), library list, run… (+10 more)

### Community 6 - "shutil"
Cohesion: 0.04
Nodes (24): shutil, answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.… (+16 more)

### Community 7 - "run_agent_node"
Cohesion: 0.05
Nodes (50): _attempt_api_calls(), _aux_run(), _bounded_retry(), build_inputs(), hermes_home(), _inputs_block(), _kill_aux_tree(), _lane_gate() (+42 more)

### Community 8 - "_final_quiesce"
Cohesion: 0.06
Nodes (50): _account_tree(), _complete(), _boot_sweep(), _final_quiesce(), _isolate_prior(), _kill_pool(), _left_live_record(), _proc_alive() (+42 more)

### Community 9 - "subprocess"
Cohesion: 0.04
Nodes (16): subprocess, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, porcelain(), est-954r pin — the B1 test's raw run must never dirty the tracked tree.…, Tracked-path dirt as {path: XY}, parsed from git status --porcelain., 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate… (+8 more)

### Community 10 - "graph_regen.py"
Cohesion: 0.08
Nodes (37): argparse, fnmatch, Pattern, ban_decision(), build_parser(), changed_files(), exempt_branch(), _git() (+29 more)

### Community 11 - "ref_node_fs"
Cohesion: 0.07
Nodes (26): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource (+18 more)

### Community 12 - "time"
Cohesion: 0.06
Nodes (14): glob, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+6 more)

### Community 13 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 14 - "plugin.js"
Cohesion: 0.10
Nodes (34): bandRows(), BREATHE, columnGroups(), depthMap(), EDGE_TONE, edgeFlowPolicy(), Edges(), edgeTone() (+26 more)

### Community 15 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 16 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 17 - "efp"
Cohesion: 0.09
Nodes (32): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then… (+24 more)

### Community 18 - "lane_recover.py"
Cohesion: 0.10
Nodes (30): apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls(), main(), open_ro(), profile_db() (+22 more)

### Community 19 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 20 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 21 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 22 - "amend"
Cohesion: 0.09
Nodes (28): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, For agents and contributors, Graph grammar in 30 seconds, Hermes Workflows (+20 more)

### Community 23 - "threading"
Cohesion: 0.07
Nodes (8): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., est-tmuu — a deterministic provider/alias config death is NOT transient…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, wf(), P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 25 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 26 - "__init__.py"
Cohesion: 0.12
Nodes (22): difflib, act_inbox(), act_library(), act_steer(), act_submit(), _from_unknown_error(), _library_rows(), _norm_tags() (+14 more)

### Community 27 - "act_status"
Cohesion: 0.10
Nodes (22): act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts() (+14 more)

### Community 28 - "_ping_route_once"
Cohesion: 0.09
Nodes (23): _hermes_bin(), _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess() (+15 more)

### Community 29 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 30 - "act_save"
Cohesion: 0.11
Nodes (22): act_save(), _expand_includes_at_door(), _include_error_from_valueerror(), _lib_path(), _lib_read(), _lib_rel_name(), _library_reader(), read() (+14 more)

### Community 31 - ".meta"
Cohesion: 0.10
Nodes (21): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.2 `parallel(tasks)` (+13 more)

### Community 32 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.14
Nodes (19): stat, check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file. (+11 more)

### Community 33 - "Changelog"
Cohesion: 0.09
Nodes (22): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+14 more)

### Community 34 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 35 - "test_proctree_identity_80.py"
Cohesion: 0.10
Nodes (12): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+4 more)

### Community 36 - "EngineNextCut"
Cohesion: 0.19
Nodes (6): 1.1.3 — 2026-10-01, EngineNextCut, deps_ok(), dep_satisfied(), After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 37 - "NodePanel"
Cohesion: 0.16
Nodes (21): attemptNo(), defaultTabFor(), Dot(), factText(), fanCounts(), FanStrip(), fanSummary(), fmtOutput() (+13 more)

### Community 38 - "act_run"
Cohesion: 0.12
Nodes (21): act_list(), act_run(), _card(), _concurrency_bake(), _create_run(), _identity_stamps(), _lane_entry(), _lane_paths() (+13 more)

### Community 39 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 40 - "_expand_include_pass"
Cohesion: 0.12
Nodes (21): _expand_include_pass(), map_site(), own(), _include_error(), _include_namespace_child(), _include_render(), replace(), _include_seed_scan() (+13 more)

### Community 41 - "3. Operate"
Cohesion: 0.10
Nodes (20): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+12 more)

### Community 42 - "test_tiers.py"
Cohesion: 0.11
Nodes (8): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 43 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 44 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 45 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 46 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.11
Nodes (6): datetime, est-jam8 — the config death is typed config_input on EVERY read path. Deep…, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 48 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 49 - "SKILL.md"
Cohesion: 0.18
Nodes (5): Node budgets, Build-lane hygiene and lane recovery, Contributor checks (not ordinary user setup), RED before green, The one canonical suite command

### Community 50 - "Graph grammar and authoring boundaries"
Cohesion: 0.18
Nodes (17): Composite graphs (include), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Per-run concurrency (optional), Staleness and replay, Tags (meta envelope), Top-level provenance (+9 more)

### Community 51 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 52 - "test_proctree_61.py"
Cohesion: 0.12
Nodes (5): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop., #61 — the runner is process-tree aware before it judges an attempt. Evidence…

### Community 53 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 54 - "DirectiveBody"
Cohesion: 0.19
Nodes (16): ago(), DirectiveBody(), DirectiveCard(), fmtDur(), focusAtom(), groupRuns(), nodesCount(), ownedRuns() (+8 more)

### Community 55 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+8 more)

### Community 56 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.17
Nodes (10): inspect, action_rows(), _append_act(), _door_call(), Owner, parked(), BaseHTTPRequestHandler, PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous… (+2 more)

### Community 57 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 58 - "test_confidence_substrate_116.py"
Cohesion: 0.14
Nodes (11): alive(), HTTP429, Meta, dict, Exception, #116 — confidence_substrate: engine-stamped fallback when a pinned confidence…, Stub the core ping seam like test_require_route_25: behavior keyed by…, Estate config.yaml: top-level `workflows:` section with the owner's… (+3 more)

### Community 59 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 61 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 62 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 63 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.21
Nodes (15): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, box(), GateActions(), ItemCard(), nudgeOwner(), Pill(), pillProgress(), PillRail() (+7 more)

### Community 64 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (15): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+7 more)

### Community 66 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 67 - "graph_fingerprint"
Cohesion: 0.19
Nodes (13): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), node_facts(), precondition_facts() (+5 more)

### Community 68 - "11-golden-solo.py"
Cohesion: 0.19
Nodes (9): hermes_constants, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Exception, #71 regression pin: the shelf is a live production surface — no test may write… (+1 more)

### Community 69 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, dict, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 70 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 71 - "fmt_goal"
Cohesion: 0.15
Nodes (10): 1.0.17 — 2026-09-28, 1. Shape of each side in one screen, 3. The importable subset, stated once, 4. What this PR does not decide, Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON), fmt_goal(), apply_graph_defaults(), _defaults_errors() (+2 more)

### Community 72 - "test_session_wake_101.py"
Cohesion: 0.15
Nodes (6): http_server, answer(), drive(), One runner process, stdout captured (the door's spawn redirects this to…, Session-wake law: lifecycle TRANSITIONS reach the owner session stamp, exactly…, _Sink

### Community 73 - "act_amend"
Cohesion: 0.15
Nodes (13): act_amend(), _confidence_substitute(), _frozen_committed(), _profile_error(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #116: declared-fallback branch of the #25 gate (R6: same path, not a parallel…, #25: a node that pins an explicit route and did NOT opt into the fallback…, Fail-closed check for composite runs (live composite-run receipt, 2026-09-30):… (+5 more)

### Community 74 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 75 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 76 - "BaseHTTPRequestHandler"
Cohesion: 0.15
Nodes (5): _Hang, _Hang10, BaseHTTPRequestHandler, _Redir, _SinkB

### Community 77 - "test_session_wake_matrix_101.py"
Cohesion: 0.17
Nodes (7): answer(), base_env(), drive(), mk(), A run dir as the door creates one (wake_protocol stamp included), so the…, Session-wake maintainer matrix: the round-1/round-2 law set, exercised through…, urllib_request

### Community 78 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 79 - "WorkflowsPage"
Cohesion: 0.20
Nodes (12): api(), ctxRest(), isBusy(), listQuery(), PaneTabTitle(), PolishStyles(), RailPanel(), register() (+4 more)

### Community 81 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 82 - "validate_graph_errors"
Cohesion: 0.18
Nodes (10): gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, reasoning_levels(), requires_errors(), validate_graph_errors(), E() (+2 more)

### Community 83 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 84 - "pack.py"
Cohesion: 0.25
Nodes (10): Nodes and data, build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), _dangling_placeholders() (+2 more)

### Community 85 - "DialectRefusal"
Cohesion: 0.20
Nodes (7): The js dialect seam: `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 86 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 88 - "test_malformed_turn_541.py"
Cohesion: 0.18
Nodes (5): est-2ek.1.541 — a malformed turn (final reply = serialized tool-call markup)…, Spawns = per-attempt stdout logs the runner wrote (logs/<node>.a<N>.log)., The markup must never ride a COMMITTED answer: no done/partial status, and…, record_never_commits_markup(), spawns_of()

### Community 89 - "test_include_expansion_core.py"
Cohesion: 0.22
Nodes (6): Unreleased, check(), expand_includes / include_provenance core-resolver contracts (design…, refuses(), expand_includes(), expand_includes(graph, library_reader) -> (expanded_graph, notes[]). Expand a…

### Community 90 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 91 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 92 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 93 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 94 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 95 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 96 - "structural_graph_errors"
Cohesion: 0.22
Nodes (9): grammar_errors(), model_names_valid(), model_policy_errors(), Closed-set + type rules for one model_policy object, as messages of the form…, Graph-level (non-node) defects as [{node:None, field, msg}] — the exact checks…, The WHOLE structural+node validation of a graph object (unnormalized) — what a…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, structural_graph_errors() (+1 more)

### Community 97 - "Proposed core hook: tool-result card rendering (optional, upstream-shaped)"
Cohesion: 0.22
Nodes (8): 1. New area + payload type — `lib/tool-result-contribs.ts` (new file), 2. Export from the SDK — `sdk/index.ts`, 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`, Plugin-side readiness, Proposed core hook: tool-result card rendering (optional, upstream-shaped), The patch (≈30 lines, additive), What the plugin would then register (one block, `desktop/plugin.js`), Why (issue #157)

### Community 98 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 99 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 101 - "_input_graph"
Cohesion: 0.25
Nodes (8): _coerce_graph(), _inline_graph_size_error(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 102 - "test_graph_single_writer_153.py"
Cohesion: 0.36
Nodes (5): commit_all(), git(), make_case(), graph_path_ban.py contract (#153, single-writer knowledge graph). The ban: a PR…, Bare origin + clone seeded with tracked source and a tracked graphify-out file.

### Community 104 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 106 - "_B"
Cohesion: 0.32
Nodes (3): _A, _B, BaseHTTPRequestHandler

### Community 107 - "_proc_boottime"
Cohesion: 0.25
Nodes (8): _proc_boottime(), _proc_envv(), Kernel start tick of a pid: field 22 of /proc/pid/stat (starttime, clock ticks…, /proc/PID/environ as a dict; {} when unreadable (absence loses only the token…, Append one fsync'd registry row — the documented CHILD-side contract, called by…, Child-side helper implementing the registration contract: a detached descendant…, _register_self_if_detached(), _register_survivor()

### Community 108 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 109 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 110 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 112 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 114 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 115 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 116 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 117 - "_include_text_fields"
Cohesion: 0.29
Nodes (7): _include_get(), _include_scratch_paths(), _include_text_fields(), _include_texts(), The string fields the {run.KEY} seed-render surface touches: the exact set…, Read one authored string by path segments (str = dict key, int = list index).…, Absolute/~-rooted path literals appearing in a node's authored strings.

### Community 118 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 119 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 120 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 121 - "Manual installation — Hermes Workflows 1.2.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.2.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 124 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 125 - "test_suite_zero_discovery_112.py"
Cohesion: 0.33
Nodes (3): make_root(), #112 zero-discovery is a failed admission, never green: scripts/suite.py must…, spec: {test name: exit code}; a stub test that exits with that code. empty=True…

### Community 126 - "Operator playbook (measured lessons)"
Cohesion: 0.40
Nodes (5): Babysitting (read the status model, not `ps`), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons)

### Community 127 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 129 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 131 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 132 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 133 - "label"
Cohesion: 0.50
Nodes (4): label(), Labeled(), 3.1 `agent(prompt, options?)`, 2. The mapping table

### Community 134 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 138 - "node_child_home"
Cohesion: 0.50
Nodes (4): node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as…

## Knowledge Gaps
- **303 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+298 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1318 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `Changelog`, `jload`, `run_agent_node`, `plugin.js`, `WorkflowsPage`, `_resolve_models`, `act_status`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Why does `useValue()` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `label()` connect `label` to `ref_node_fs`, `NodePanel`, `plugin.js`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _303 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.03600612870275792 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04101358411703239 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.04225352112676056 - nodes in this community are weakly interconnected._