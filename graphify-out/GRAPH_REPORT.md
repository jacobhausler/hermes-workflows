# Graph Report - tree  (2026-10-04)

## Corpus Check
- 268 files · ~358,287 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 5)

## Summary
- 2658 nodes · 5404 edges · 159 communities (129 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- wf.py
- wfcommon.py
- CurrentAttemptMetrics
- sys
- jload
- os
- run_child
- time
- efp
- test_orphan_adopt_790c6ad.py
- json
- shutil
- test_require_route_25.py
- test_preflight_liveness_152be7f7.py
- test_fanout_expand.mjs
- subprocess
- lane_recover.py
- validate_graph_errors
- _Exporter
- pathlib
- _adopt_child
- test_11_ui_imports.mjs
- wf_dialect.py
- DoorLib50
- ref_node_fs
- test_fanout_item_goal.py
- __init__.py
- _Importer
- plugin.js
- act_amend
- .meta
- test_silent_death_reaper_8.py
- act_run
- test_lane_hygiene_preamble_8edcc9bf.py
- test_proctree_identity_80.py
- plugin_api.py
- NodePanel
- act_save
- _ping_route_once
- agent
- test_live_truth_ui.mjs
- _stamp_served
- test_daemonize_8.py
- DirectiveBody
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- test_pane_render_uncapped.mjs
- .statement
- test_lost_handoff_sync_wake_r18.py
- test_ratelimit_park_walls_159c.py
- CardBackend
- test_confidence_substrate_116.py
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- test_dialect_js_33.py
- graph_path_ban.py
- LiveTruth
- test_node_panel.mjs
- test_pane_model_agentfirst.mjs
- 4. Contribute
- Changelog
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- 11-golden-solo.py
- _input_graph
- graph_regen.py
- test_proctree_61b.py
- GraphView
- test_session_wake_101.py
- re
- TeamIntegration
- test_pane_origin_hardening.mjs
- test_pill_rail.mjs
- BaseHTTPRequestHandler
- test_session_wake_matrix_101.py
- test_wfpid_owner_8.py
- README.md
- Disclosure verification — clause-by-clause evidence
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- make_public.py
- test_card_frontend_contract.mjs
- ConcurrencyBake100
- test_malformed_turn_541.py
- test_node_facts.py
- Contributing to hermes-workflows
- GateActions
- graph_check.py
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- test_machine_watch_94.py
- test_proctree_61.py
- ProvenanceCounters
- test_schema_enum_107.py
- _cancel_evidence
- DialectRefusal
- Proposed core hook: tool-result card rendering (optional, upstream-shaped)
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_enum_clamp_5med_flah.py
- test_sprint101w2_B2-retry.py
- Workflow examples
- act_inbox
- Hermes Workflows
- pack.py
- test_graph_single_writer_153.py
- test_routing_routes.py
- test_run_dry_run.py
- _B
- model_preflight
- install
- suite.py
- LifecycleNotice
- test_incident_response_93.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- 3. Operate
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- _route_enforcement
- Manual installation — Hermes Workflows 1.2.0
- DoorLane
- Claim
- test_suite_admission_17.py
- test_suite_zero_discovery_112.py
- 1.0.1 — 2026-09-25
- Contributor checks (not ordinary user setup)
- Operator playbook (measured lessons)
- pr_tag_audit.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON)
- dynamic-agent-count.js
- _LADDER
- Integrated
- .render_item_template
- date-now.js
- meta-nonliteral.js
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
1. `run_child()` - 56 edges
2. `jload()` - 40 edges
3. `efp()` - 40 edges
4. `main()` - 32 edges
5. `log()` - 29 edges
6. `DoorLib50` - 27 edges
7. `_Importer` - 27 edges
8. `_adopt_child()` - 26 edges
9. `loop()` - 26 edges
10. `_Exporter` - 26 edges

## Surprising Connections (you probably didn't know these)
- `What the plugin would then register (one block, `desktop/plugin.js`)` --references--> `SessionStrip()`  [INFERRED]
  docs/card-toolresult-hook.md → desktop/plugin.js
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What a run leaves behind` --references--> `amend()`  [INFERRED]
  README.md → tests/test_amend_rebake_034849a2.py
- `basics/ — one idea each, read these first` --references--> `gate()`  [INFERRED]
  examples/README.md → tests/test_graphify_dedupe_27.py

## Import Cycles
- None detected.

## Communities (159 total, 30 thin omitted)

### Community 0 - "wf.py"
Cohesion: 0.03
Nodes (92): concurrent_futures, socket, est-jec0 / PR #122 B1 pin: the prose-JSON fallback must never crash the node.…, urllib_error, _aux_run(), _bespoke_middle(), build_inputs(), _child_spoke() (+84 more)

### Community 1 - "wfcommon.py"
Cohesion: 0.04
Nodes (89): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, Where to POST a wake, host config first (mirrors the api_server adapter's own…, _wake_endpoint(), _active_spawn(), _active_spawns(), current_attempt() (+81 more)

### Community 2 - "CurrentAttemptMetrics"
Cohesion: 0.05
Nodes (32): agent_reasoning_effort, 1.1.3 — 2026-10-01, The `workflow` tool, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature) (+24 more)

### Community 3 - "sys"
Cohesion: 0.04
Nodes (23): importlib_util, sys, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Docs-surface drift guard: the README's tool-action table must name exactly the… (+15 more)

### Community 4 - "jload"
Cohesion: 0.05
Nodes (60): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., All per-item spawn records with a live pid, once every item is RUNNING., read_children(), acquire_lock(), _crash_gen(), drain_inbox(), emit() (+52 more)

### Community 5 - "os"
Cohesion: 0.06
Nodes (33): hashlib, os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), main() (+25 more)

### Community 6 - "run_child"
Cohesion: 0.07
Nodes (58): _account_tree(), _boot_sweep(), _bounded_retry(), _final_quiesce(), _isolate_prior(), _kill_pool(), _left_live_record(), log() (+50 more)

### Community 7 - "time"
Cohesion: 0.04
Nodes (25): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), Integrated read-model and parser-valid card dedup checks., Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, wf() (+17 more)

### Community 8 - "efp"
Cohesion: 0.06
Nodes (50): ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), What you get, 2. The mapping table, File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data (+42 more)

### Community 9 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.05
Nodes (11): datetime, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., est-jam8 — the config death is typed config_input on EVERY read path. Deep…, est-tmuu — a deterministic provider/alias config death is NOT transient…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):… (+3 more)

### Community 10 - "json"
Cohesion: 0.06
Nodes (17): glob, json, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.… (+9 more)

### Community 11 - "shutil"
Cohesion: 0.05
Nodes (10): shutil, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, #113 — validate() must split integer from number and reject booleans. Before…, Ledger e68544a37be37657 (fb-fix-2dd8de73): a harvest-on-death `partial` must…, est-t0vz / issue #54 — credential-window 429s get their own `ratelimit` class…, #102 bounded re-drive must not pretend-resume a DEAD (empty) session. Measured…, Door-transport guard: run_context must never silently route a map to seed.… (+2 more)

### Community 12 - "test_require_route_25.py"
Cohesion: 0.05
Nodes (17): atexit, importlib, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal… (+9 more)

### Community 13 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check(), contract() (+21 more)

### Community 14 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 15 - "subprocess"
Cohesion: 0.07
Nodes (15): contextlib, subprocess, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness., GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., LaneSupervisor, Suite hook for the standalone 20-cycle lane-supervisor kill/resume harness. (+7 more)

### Community 16 - "lane_recover.py"
Cohesion: 0.10
Nodes (30): apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls(), main(), open_ro(), profile_db() (+22 more)

### Community 17 - "validate_graph_errors"
Cohesion: 0.07
Nodes (23): _v(), grammar_errors(), Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this… (+15 more)

### Community 18 - "_Exporter"
Cohesion: 0.15
Nodes (12): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+4 more)

### Community 19 - "pathlib"
Cohesion: 0.06
Nodes (11): pathlib, ancestors(), Cold structural gate for examples/release/submit-pr.workflow.json. The stub is…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, porcelain(), est-954r pin — the B1 test's raw run must never dirty the tracked tree.…, Tracked-path dirt as {path: XY}, parsed from git status --porcelain., B2b probes (peer-review owed items): (A) empty-array query shares the save law,… (+3 more)

### Community 20 - "_adopt_child"
Cohesion: 0.07
Nodes (29): _adopt_child(), _AdoptedHandle, _classify_config_input(), _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent() (+21 more)

### Community 21 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 22 - "wf_dialect.py"
Cohesion: 0.08
Nodes (25): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _mask(), _match_close() (+17 more)

### Community 24 - "ref_node_fs"
Cohesion: 0.10
Nodes (18): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, here, plugin, src (+10 more)

### Community 25 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 26 - "__init__.py"
Cohesion: 0.13
Nodes (25): difflib, _alias_provider_pair(), handle(), _model_policy_error(), model_tiers(), _owner_settings_error(), _ping_note(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The… (+17 more)

### Community 27 - "_Importer"
Cohesion: 0.17
Nodes (12): _Importer, _line(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to… (+4 more)

### Community 28 - "plugin.js"
Cohesion: 0.09
Nodes (24): BREATHE, EDGE_TONE, $fanExpanded, $fanItem, fanItems(), $fanOpen, GATE_PULSE, itemLabel() (+16 more)

### Community 29 - "act_amend"
Cohesion: 0.10
Nodes (23): act_amend(), act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _frozen_committed(), _lane_key_error() (+15 more)

### Community 30 - ".meta"
Cohesion: 0.09
Nodes (22): 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3. The importable subset, stated once, _complete(), _clamp_warn(), _filter_child_toolsets() (+14 more)

### Community 31 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 32 - "act_run"
Cohesion: 0.11
Nodes (23): act_list(), act_run(), _card(), _concurrency_bake(), _create_run(), _identity_stamps(), _lane_entry(), _lane_paths() (+15 more)

### Community 33 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.14
Nodes (19): stat, check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file. (+11 more)

### Community 34 - "test_proctree_identity_80.py"
Cohesion: 0.10
Nodes (12): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+4 more)

### Community 35 - "plugin_api.py"
Cohesion: 0.17
Nodes (19): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+11 more)

### Community 36 - "NodePanel"
Cohesion: 0.16
Nodes (21): attemptNo(), box(), defaultTabFor(), Dot(), factText(), fanCounts(), FanStrip(), fanSummary() (+13 more)

### Community 37 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 38 - "_ping_route_once"
Cohesion: 0.10
Nodes (20): _hermes_bin(), _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+12 more)

### Community 39 - "agent"
Cohesion: 0.12
Nodes (20): Graph grammar in 30 seconds, 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 3.1 `agent(prompt, options?)`, 3.2 `parallel(tasks)`, 3.3 `pipeline(items, stage1, stage2, ...)`, 3.4 `phase(title)` (+12 more)

### Community 40 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 41 - "_stamp_served"
Cohesion: 0.10
Nodes (21): _attempt_api_calls(), hermes_home(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, Message-existence evidence for the #102 dead-session guard: True when the dead…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, The target owns the child's session DB; absent routing preserves legacy home., {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed… (+13 more)

### Community 42 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 43 - "DirectiveBody"
Cohesion: 0.18
Nodes (20): ago(), DirectiveBody(), fmtDur(), idleS(), idleTone(), inlineHeader(), ItemChips(), kfmt() (+12 more)

### Community 44 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 45 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 46 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 47 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 48 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 49 - "test_pane_render_uncapped.mjs"
Cohesion: 0.12
Nodes (16): FLEET, here, iso(), jsxPath, keys, labels, modPath, now (+8 more)

### Community 50 - ".statement"
Cohesion: 0.15
Nodes (8): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, _statements()

### Community 51 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.17
Nodes (10): inspect, action_rows(), _append_act(), _door_call(), Owner, parked(), BaseHTTPRequestHandler, PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous… (+2 more)

### Community 52 - "test_ratelimit_park_walls_159c.py"
Cohesion: 0.14
Nodes (5): random, Late, Committee wf159c fix-response (PR #159) — three blocking findings, pinned. The…, respawn_fail(), stub_r()

### Community 53 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 54 - "test_confidence_substrate_116.py"
Cohesion: 0.14
Nodes (11): alive(), HTTP429, Meta, dict, Exception, #116 — confidence_substrate: engine-stamped fallback when a pinned confidence…, Stub the core ping seam like test_require_route_25: behavior keyed by…, Estate config.yaml: top-level `workflows:` section with the owner's… (+3 more)

### Community 55 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 57 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 58 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 59 - "test_dialect_js_33.py"
Cohesion: 0.14
Nodes (7): copy, check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses(), Core-10 #89 review blocker: the EFFECTIVE synthesis prompt must not carry the…, census-fanout example gate (Core-10 authoring contract). The template's…, release-lifecycle example gate (Core-10 authoring contract). The template's…

### Community 60 - "graph_path_ban.py"
Cohesion: 0.22
Nodes (14): ban_decision(), build_parser(), changed_files(), exempt_branch(), _git(), head_branch(), main(), merge_base() (+6 more)

### Community 62 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 63 - "test_pane_model_agentfirst.mjs"
Cohesion: 0.13
Nodes (12): bare, here, jsxPath, m, modPath, none, now, reactPath (+4 more)

### Community 64 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 65 - "Changelog"
Cohesion: 0.14
Nodes (14): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+6 more)

### Community 66 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.21
Nodes (14): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, DirectiveCard(), focusAtom(), isBusy(), listQuery(), ownedRuns(), PaneTabTitle(), register() (+6 more)

### Community 67 - "11-golden-solo.py"
Cohesion: 0.19
Nodes (9): hermes_constants, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Exception, #71 regression pin: the shelf is a live production surface — no test may write… (+1 more)

### Community 68 - "_input_graph"
Cohesion: 0.14
Nodes (14): act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., #50 (epic #49): submit a hand-rolled graph for STUDY — the quarantine inbox…, The door only ever sees `graph` as a parsed object from the tool schema, but a… (+6 more)

### Community 69 - "graph_regen.py"
Cohesion: 0.25
Nodes (13): build_parser(), _git(), graph_check(), graph_diff_files(), head_sha(), main(), Undo working-tree dirt under graphify-out/ (git checkout HEAD -- ...)., graph_regen.py — the single-writer knowledge-graph regen (issue #153). Used by… (+5 more)

### Community 70 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 71 - "GraphView"
Cohesion: 0.26
Nodes (13): bandRows(), columnGroups(), depthMap(), edgeFlowPolicy(), Edges(), edgeTone(), FanStack(), GraphView() (+5 more)

### Community 72 - "test_session_wake_101.py"
Cohesion: 0.15
Nodes (6): http_server, answer(), drive(), One runner process, stdout captured (the door's spawn redirects this to…, Session-wake law: lifecycle TRANSITIONS reach the owner session stamp, exactly…, _Sink

### Community 73 - "re"
Cohesion: 0.15
Nodes (6): re, Doc-side closed-set pin: AGENTS.md §3d must name EXACTLY wf.ERROR_CLASSES. The…, error-class closed set — ERROR_CLASSES is the closed set AGENTS.md cites; it…, Core-10 exchange-run regression: the leaf verifies by RE-READING its committed…, walk(), Portable authoring skill contract; no provider or live-home dependencies.

### Community 74 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 75 - "test_pane_origin_hardening.mjs"
Cohesion: 0.15
Nodes (9): m2, m3, map, model, owned, paneModel, poisoned, runs (+1 more)

### Community 76 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 77 - "BaseHTTPRequestHandler"
Cohesion: 0.15
Nodes (5): _Hang, _Hang10, BaseHTTPRequestHandler, _Redir, _SinkB

### Community 78 - "test_session_wake_matrix_101.py"
Cohesion: 0.17
Nodes (7): answer(), base_env(), drive(), mk(), A run dir as the door creates one (wake_protocol stamp included), so the…, Session-wake maintainer matrix: the round-1/round-2 law set, exercised through…, urllib_request

### Community 79 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 81 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.17
Nodes (12): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law… (+4 more)

### Community 83 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 84 - "make_public.py"
Cohesion: 0.27
Nodes (10): argparse, fnmatch, Pattern, excluded(), load_guards(), load_scrub_list(), main(), Path (+2 more)

### Community 85 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 87 - "test_malformed_turn_541.py"
Cohesion: 0.18
Nodes (5): est-2ek.1.541 — a malformed turn (final reply = serialized tool-call markup)…, Spawns = per-attempt stdout logs the runner wrote (logs/<node>.a<N>.log)., The markup must never ride a COMMITTED answer: no done/partial status, and…, record_never_commits_markup(), spawns_of()

### Community 88 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 89 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 90 - "GateActions"
Cohesion: 0.22
Nodes (10): api(), ctxRest(), GateActions(), nudgeOwner(), Pill(), pillProgress(), PillRail(), railModel() (+2 more)

### Community 91 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 92 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 93 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 94 - "test_machine_watch_94.py"
Cohesion: 0.27
Nodes (7): argv(), check(), native_engine(), spawn(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling., state()

### Community 96 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 97 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 98 - "_cancel_evidence"
Cohesion: 0.20
Nodes (10): _banked_work(), _cancel_evidence(), child_work_dir(), _clean_capture(), _dead_session_harvest(), a2d7f664: honest evidence for a quorum-straggler cancel. Snapshot of the…, Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —… (+2 more)

### Community 99 - "DialectRefusal"
Cohesion: 0.24
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 100 - "Proposed core hook: tool-result card rendering (optional, upstream-shaped)"
Cohesion: 0.22
Nodes (8): 1. New area + payload type — `lib/tool-result-contribs.ts` (new file), 2. Export from the SDK — `sdk/index.ts`, 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`, Plugin-side readiness, Proposed core hook: tool-result card rendering (optional, upstream-shaped), The patch (≈30 lines, additive), What the plugin would then register (one block, `desktop/plugin.js`), Why (issue #157)

### Community 101 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 102 - "test_enum_clamp_5med_flah.py"
Cohesion: 0.31
Nodes (6): drive(), mk(), est-flah — unknown enum values clamp at RESOLVE time, never a hard child death.…, record(), toolsets_run(), toolsets

### Community 103 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 104 - "Workflow examples"
Cohesion: 0.25
Nodes (7): basics/ — one idea each, read these first, build/ — fan-out, barriers, ledgers, ops/ — incident & fleet, release/ — the SDLC back half, review/ — independent judgment, Running one, Workflow examples

### Community 105 - "act_inbox"
Cohesion: 0.25
Nodes (8): act_inbox(), act_steer(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 106 - "Hermes Workflows"
Cohesion: 0.25
Nodes (8): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What a run leaves behind, Why this exists

### Community 107 - "pack.py"
Cohesion: 0.39
Nodes (7): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), ZipInfo

### Community 108 - "test_graph_single_writer_153.py"
Cohesion: 0.36
Nodes (5): commit_all(), git(), make_case(), graph_path_ban.py contract (#153, single-writer knowledge graph). The ban: a PR…, Bare origin + clone seeded with tracked source and a tracked graphify-out file.

### Community 109 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 111 - "_B"
Cohesion: 0.32
Nodes (3): _A, _B, BaseHTTPRequestHandler

### Community 112 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 113 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 114 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 116 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 118 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 119 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 120 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 121 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 122 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 123 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 124 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 125 - "_route_enforcement"
Cohesion: 0.33
Nodes (6): _confidence_substitute(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #116: declared-fallback branch of the #25 gate (R6: same path, not a parallel…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 126 - "Manual installation — Hermes Workflows 1.2.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.2.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 129 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 130 - "test_suite_zero_discovery_112.py"
Cohesion: 0.33
Nodes (3): make_root(), #112 zero-discovery is a failed admission, never green: scripts/suite.py must…, spec: {test name: exit code}; a stub test that exits with that code. empty=True…

### Community 131 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 132 - "Contributor checks (not ordinary user setup)"
Cohesion: 0.40
Nodes (4): Build-lane hygiene and lane recovery, Contributor checks (not ordinary user setup), RED before green, The one canonical suite command

### Community 133 - "Operator playbook (measured lessons)"
Cohesion: 0.40
Nodes (5): Babysitting (read the status model, not `ps`), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons)

### Community 134 - "pr_tag_audit.py"
Cohesion: 0.50
Nodes (3): main(), pr_tag_audit.py — release-time gate for `(open PR #NN)` doc tags. Docs that…, resolve_repo()

### Community 135 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 136 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 137 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 138 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 139 - "Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON)"
Cohesion: 0.50
Nodes (3): 1. Shape of each side in one screen, 4. What this PR does not decide, Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON)

### Community 140 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **341 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+336 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1365 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `wf.py`, `wfcommon.py`, `Changelog`, `GateActions`, `GraphView`, `DirectiveBody`, `__init__.py`, `act_amend`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `useValue()` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `label()` connect `NodePanel` to `efp`, `plugin.js`, `test_card_frontend_contract.mjs`, `agent`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _341 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.026535087719298245 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.035998129967274424 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.0546583850931677 - nodes in this community are weakly interconnected._