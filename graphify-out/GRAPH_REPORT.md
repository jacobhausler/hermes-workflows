# Graph Report - tree  (2026-10-03)

## Corpus Check
- 259 files · ~343,824 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 5)

## Summary
- 2537 nodes · 5192 edges · 148 communities (112 shown, 36 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- wf.py
- wfcommon.py
- os
- jload
- pathlib
- json
- .meta
- time
- graph_regen.py
- subprocess
- test_preflight_liveness_152be7f7.py
- ref_node_fs
- test_require_route_25.py
- _Exporter
- test_fanout_expand.mjs
- Run operations and read model
- plugin.js
- efp
- lane_recover.py
- plugin_api.py
- threading
- test_11_ui_imports.mjs
- DoorLib50
- test_fanout_item_goal.py
- _Importer
- test_failures_0923.py
- act_amend
- agent
- wf_dialect.py
- _ping_route_once
- Changelog
- WorkflowsPage
- test_silent_death_reaper_8.py
- 11-golden-solo.py
- act_run
- test_lane_hygiene_preamble_8edcc9bf.py
- test_proctree_identity_80.py
- test_orphan_adopt_790c6ad.py
- act_save
- test_live_truth_ui.mjs
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- 3. Operate
- NodePanel
- CurrentAttemptMetrics
- __init__.py
- validate_graph_errors
- test_register_surface.mjs
- SKILL.md
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- Disclosure verification — clause-by-clause evidence
- test_lost_handoff_sync_wake_r18.py
- CardBackend
- test_confidence_substrate_116.py
- test_edge_routing.mjs
- EngineNextCut
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- _resolve_models
- LiveTruth
- test_node_panel.mjs
- .agent_args
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- test_proctree_61b.py
- GraphView
- test_session_wake_101.py
- TeamIntegration
- test_pill_rail.mjs
- BaseHTTPRequestHandler
- test_session_wake_matrix_101.py
- test_wfpid_owner_8.py
- test_sprint101w2_D2-steer-liveness.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- ConcurrencyBake100
- test_malformed_turn_541.py
- Contributing to hermes-workflows
- graph_check.py
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- test_proctree_61.py
- ProvenanceCounters
- test_schema_enum_107.py
- _parse_literal
- Proposed core hook: tool-result card rendering (optional, upstream-shaped)
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_B2-retry.py
- DialectRefusal
- _sweep_orphans
- _SV
- _input_graph
- test_graph_single_writer_153.py
- test_numeric_type_validation_113.py
- test_run_dry_run.py
- _B
- _proc_boottime
- model_preflight
- install
- suite.py
- LifecycleNotice
- test_incident_response_93.py
- test_status_next.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- _route_enforcement
- Manual installation — Hermes Workflows 1.2.0
- DoorLane
- Claim
- test_suite_admission_17.py
- test_suite_zero_discovery_112.py
- _dead_session_harvest
- _wake_identity
- dep_satisfied
- Operator playbook (measured lessons)
- test_jec0_recursion_containment.py
- native_engine
- manifest.json
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- _AdoptedHandle
- _lane_hygiene_preamble
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
1. `run_child()` - 48 edges
2. `jload()` - 40 edges
3. `efp()` - 40 edges
4. `main()` - 32 edges
5. `DoorLib50` - 27 edges
6. `log()` - 27 edges
7. `_Importer` - 27 edges
8. `_adopt_child()` - 26 edges
9. `loop()` - 26 edges
10. `_Exporter` - 26 edges

## Surprising Connections (you probably didn't know these)
- `What the plugin would then register (one block, `desktop/plugin.js`)` --references--> `SessionStrip()`  [INFERRED]
  docs/card-toolresult-hook.md → desktop/plugin.js
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (148 total, 36 thin omitted)

### Community 0 - "wf.py"
Cohesion: 0.04
Nodes (118): concurrent_futures, socket, urllib_error, _account_tree(), _adopt_child(), _complete(), _boot_sweep(), _cancel_evidence() (+110 more)

### Community 1 - "wfcommon.py"
Cohesion: 0.03
Nodes (88): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, Where to POST a wake, host config first (mirrors the api_server adapter's own…, _wake_endpoint(), _active_spawn(), apply_substrate_disclosure(), blocked_by() (+80 more)

### Community 2 - "os"
Cohesion: 0.05
Nodes (43): contextlib, hashlib, importlib_util, os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.… (+35 more)

### Community 3 - "jload"
Cohesion: 0.04
Nodes (77): ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test() (+69 more)

### Community 4 - "pathlib"
Cohesion: 0.05
Nodes (31): copy, pathlib, re, main(), pr_tag_audit.py — release-time gate for `(open PR #NN)` doc tags. Docs that…, resolve_repo(), sys, _fake_state_row() (+23 more)

### Community 5 - "json"
Cohesion: 0.04
Nodes (22): json, shutil, Identical solo child wrapper for both tag and candidate; records env key sets.…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, B2b probes (peer-review owed items): (A) empty-array query shares the save law,… (+14 more)

### Community 6 - ".meta"
Cohesion: 0.04
Nodes (57): 1.0.17 — 2026-09-28, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3. The importable subset, stated once, Nodes and data, The js dialect seam: `wf_dialect.py` (+49 more)

### Community 7 - "time"
Cohesion: 0.05
Nodes (23): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, wf() (+15 more)

### Community 8 - "graph_regen.py"
Cohesion: 0.07
Nodes (44): argparse, fnmatch, Pattern, ban_decision(), build_parser(), changed_files(), exempt_branch(), _git() (+36 more)

### Community 9 - "subprocess"
Cohesion: 0.05
Nodes (15): subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., LaneSupervisor, Suite hook for the standalone 20-cycle lane-supervisor kill/resume harness., porcelain(), est-954r pin — the B1 test's raw run must never dirty the tracked tree.…, Tracked-path dirt as {path: XY}, parsed from git status --porcelain. (+7 more)

### Community 10 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check(), contract() (+21 more)

### Community 11 - "ref_node_fs"
Cohesion: 0.07
Nodes (26): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource (+18 more)

### Community 12 - "test_require_route_25.py"
Cohesion: 0.06
Nodes (15): atexit, importlib, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v() (+7 more)

### Community 13 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 14 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 15 - "Run operations and read model"
Cohesion: 0.08
Nodes (33): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, For agents and contributors, Graph grammar in 30 seconds (+25 more)

### Community 16 - "plugin.js"
Cohesion: 0.09
Nodes (31): api(), BREATHE, ctxRest(), DirectiveCard(), EDGE_TONE, $fanExpanded, $fanItem, $fanOpen (+23 more)

### Community 17 - "efp"
Cohesion: 0.10
Nodes (31): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Per-run concurrency (optional), Staleness and replay, Tags (meta envelope), Top-level provenance, Portable workflow files (publish = put the file on git) (+23 more)

### Community 18 - "lane_recover.py"
Cohesion: 0.10
Nodes (30): apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls(), main(), open_ro(), profile_db() (+22 more)

### Community 19 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 20 - "threading"
Cohesion: 0.07
Nodes (10): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., est-tmuu — a deterministic provider/alias config death is NOT transient…, Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing., Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, wf() (+2 more)

### Community 21 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 23 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 24 - "_Importer"
Cohesion: 0.16
Nodes (10): _control_kw(), _forbidden_label(), _Importer, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the… (+2 more)

### Community 25 - "test_failures_0923.py"
Cohesion: 0.08
Nodes (7): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, 45b038: cron's core-less interpreter must still bake a proved pinned route. The…

### Community 26 - "act_amend"
Cohesion: 0.10
Nodes (23): act_amend(), act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _frozen_committed(), _lane_key_error() (+15 more)

### Community 27 - "agent"
Cohesion: 0.10
Nodes (23): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 3.1 `agent(prompt, options?)`, 3.2 `parallel(tasks)`, 3.3 `pipeline(items, stage1, stage2, ...)`, 3.4 `phase(title)`, 3.5 `log(message)` (+15 more)

### Community 28 - "wf_dialect.py"
Cohesion: 0.09
Nodes (22): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _line() (+14 more)

### Community 29 - "_ping_route_once"
Cohesion: 0.09
Nodes (23): _hermes_bin(), _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess() (+15 more)

### Community 30 - "Changelog"
Cohesion: 0.09
Nodes (23): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+15 more)

### Community 31 - "WorkflowsPage"
Cohesion: 0.18
Nodes (23): ago(), DirectiveBody(), Dot(), fmtDur(), idleS(), idleTone(), inlineHeader(), ItemCard() (+15 more)

### Community 32 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 33 - "11-golden-solo.py"
Cohesion: 0.10
Nodes (14): glob, hermes_constants, plugin_api, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3… (+6 more)

### Community 34 - "act_run"
Cohesion: 0.11
Nodes (23): act_list(), act_run(), _card(), _concurrency_bake(), _create_run(), _identity_stamps(), _lane_entry(), _lane_paths() (+15 more)

### Community 35 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.14
Nodes (19): stat, check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file. (+11 more)

### Community 36 - "test_proctree_identity_80.py"
Cohesion: 0.10
Nodes (12): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+4 more)

### Community 37 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.10
Nodes (8): datetime, est-jam8 — the config death is typed config_input on EVERY read path. Deep…, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 38 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 39 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 40 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 41 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 42 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 43 - "3. Operate"
Cohesion: 0.11
Nodes (19): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+11 more)

### Community 44 - "NodePanel"
Cohesion: 0.15
Nodes (19): attemptNo(), box(), defaultTabFor(), factText(), fanCounts(), fanItems(), FanStrip(), fanSummary() (+11 more)

### Community 46 - "__init__.py"
Cohesion: 0.16
Nodes (17): difflib, act_inbox(), act_steer(), act_submit(), _model_names_valid(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, Return graph-level and node-level defects together, before any write/spawn., #50 (epic #49): submit a hand-rolled graph for STUDY — the quarantine inbox… (+9 more)

### Community 47 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): _v(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+7 more)

### Community 48 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 49 - "SKILL.md"
Cohesion: 0.18
Nodes (5): Node budgets, Build-lane hygiene and lane recovery, Contributor checks (not ordinary user setup), RED before green, The one canonical suite command

### Community 50 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 51 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 52 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.12
Nodes (16): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+8 more)

### Community 53 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.17
Nodes (10): inspect, action_rows(), _append_act(), _door_call(), Owner, parked(), BaseHTTPRequestHandler, PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous… (+2 more)

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

### Community 61 - "_resolve_models"
Cohesion: 0.18
Nodes (15): _alias_provider_pair(), _model_policy_error(), model_tiers(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+7 more)

### Community 63 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 64 - ".agent_args"
Cohesion: 0.25
Nodes (7): _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the…, _skip_ws(), _split_top()

### Community 65 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.21
Nodes (14): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, GateActions(), nudgeOwner(), Pill(), pillProgress(), PillRail(), railModel(), RailPanel() (+6 more)

### Community 66 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 67 - "GraphView"
Cohesion: 0.26
Nodes (13): bandRows(), columnGroups(), depthMap(), edgeFlowPolicy(), Edges(), edgeTone(), FanStack(), GraphView() (+5 more)

### Community 68 - "test_session_wake_101.py"
Cohesion: 0.15
Nodes (6): http_server, answer(), drive(), One runner process, stdout captured (the door's spawn redirects this to…, Session-wake law: lifecycle TRANSITIONS reach the owner session stamp, exactly…, _Sink

### Community 69 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 70 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 71 - "BaseHTTPRequestHandler"
Cohesion: 0.15
Nodes (5): _Hang, _Hang10, BaseHTTPRequestHandler, _Redir, _SinkB

### Community 72 - "test_session_wake_matrix_101.py"
Cohesion: 0.17
Nodes (7): answer(), base_env(), drive(), mk(), A run dir as the door creates one (wake_protocol stamp included), so the…, Session-wake maintainer matrix: the round-1/round-2 law set, exercised through…, urllib_request

### Community 73 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 74 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.18
Nodes (5): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…

### Community 76 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 77 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 79 - "test_malformed_turn_541.py"
Cohesion: 0.18
Nodes (5): est-2ek.1.541 — a malformed turn (final reply = serialized tool-call markup)…, Spawns = per-attempt stdout logs the runner wrote (logs/<node>.a<N>.log)., The markup must never ride a COMMITTED answer: no done/partial status, and…, record_never_commits_markup(), spawns_of()

### Community 80 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 81 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 82 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 83 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 85 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 86 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 87 - "_parse_literal"
Cohesion: 0.20
Nodes (8): _match_close(), _parse_literal(), Offset of the bracket closing the one at `open_at`., A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, _Ref, _Tpl, _unescape()

### Community 88 - "Proposed core hook: tool-result card rendering (optional, upstream-shaped)"
Cohesion: 0.22
Nodes (8): 1. New area + payload type — `lib/tool-result-contribs.ts` (new file), 2. Export from the SDK — `sdk/index.ts`, 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`, Plugin-side readiness, Proposed core hook: tool-result card rendering (optional, upstream-shaped), The patch (≈30 lines, additive), What the plugin would then register (one block, `desktop/plugin.js`), Why (issue #157)

### Community 89 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 90 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 91 - "DialectRefusal"
Cohesion: 0.28
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 92 - "_sweep_orphans"
Cohesion: 0.22
Nodes (9): _stop_watcher(), Every pid the runner itself launched or attached: the _procs registry (Popen…, Live pids whose PPid is THIS runner that the runner did not launch: subreaper-…, best-effort waitpid for a runner-adopted orphan that died (zombie hygiene;…, Kill+reap every runner-adopted orphan, /proc-proven, cascading: killing an…, _reap_zombie(), _registered_child_pids(), _runner_orphans() (+1 more)

### Community 94 - "_input_graph"
Cohesion: 0.25
Nodes (8): _coerce_graph(), _inline_graph_size_error(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 95 - "test_graph_single_writer_153.py"
Cohesion: 0.36
Nodes (5): commit_all(), git(), make_case(), graph_path_ban.py contract (#153, single-writer knowledge graph). The ban: a PR…, Bare origin + clone seeded with tracked source and a tracked graphify-out file.

### Community 98 - "_B"
Cohesion: 0.32
Nodes (3): _A, _B, BaseHTTPRequestHandler

### Community 99 - "_proc_boottime"
Cohesion: 0.25
Nodes (8): _proc_boottime(), _proc_envv(), Kernel start tick of a pid: field 22 of /proc/pid/stat (starttime, clock ticks…, /proc/PID/environ as a dict; {} when unreadable (absence loses only the token…, Append one fsync'd registry row — the documented CHILD-side contract, called by…, Child-side helper implementing the registration contract: a detached descendant…, _register_self_if_detached(), _register_survivor()

### Community 100 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 101 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 102 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 104 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 105 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 106 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 107 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 108 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 109 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 110 - "_route_enforcement"
Cohesion: 0.33
Nodes (6): _confidence_substitute(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #116: declared-fallback branch of the #25 gate (R6: same path, not a parallel…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 111 - "Manual installation — Hermes Workflows 1.2.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.2.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 114 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 115 - "test_suite_zero_discovery_112.py"
Cohesion: 0.33
Nodes (3): make_root(), #112 zero-discovery is a failed admission, never green: scripts/suite.py must…, spec: {test name: exit code}; a stub test that exits with that code. empty=True…

### Community 116 - "_dead_session_harvest"
Cohesion: 0.33
Nodes (6): _banked_work(), _clean_capture(), _dead_session_harvest(), Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —…, The #102 harvest preamble for a re-drive whose prior session persisted NO…

### Community 117 - "_wake_identity"
Cohesion: 0.33
Nodes (6): Durable amendment generation: how many graph.amended events the run's own…, The run's ALREADY-COMMITTED failed-node set straight from the node records…, THE transition-instance discriminant (B3 law): a string that is IDENTICAL…, _wake_identity(), _wake_resolved_failed(), _wake_rev()

### Community 118 - "dep_satisfied"
Cohesion: 0.50
Nodes (5): 1.1.3 — 2026-10-01, deps_ok(), dep_satisfied(), After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 119 - "Operator playbook (measured lessons)"
Cohesion: 0.40
Nodes (5): Babysitting (read the status model, not `ps`), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons)

### Community 120 - "test_jec0_recursion_containment.py"
Cohesion: 0.40
Nodes (3): est-jec0 / PR #122 B1 pin: the prose-JSON fallback must never crash the node.…, last_balanced_object(), Sprint101 #9: the LAST top-level balanced {...} in stdout that json accepts…

### Community 121 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 122 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 123 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 128 - "_lane_hygiene_preamble"
Cohesion: 0.50
Nodes (4): _is_build_lane(), _lane_hygiene_preamble(), The build shape: `shape: "build"` declared, or a `repo:` lane declared (the…, Machine-generated lane-hygiene preamble for build-shape nodes ("" otherwise).…

### Community 129 - "_wake_append"
Cohesion: 0.50
Nodes (4): Redact bearer/credential shapes out of anything the wake path may persist., Append one ledger row; a failure is loud on stderr (runner.log) and NEVER…, _wake_append(), _wake_safe()

## Knowledge Gaps
- **302 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1282 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `jload`, `GraphView`, `.meta`, `act_amend`, `_resolve_models`, `Changelog`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `useValue()` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `label()` connect `NodePanel` to `plugin.js`, `ref_node_fs`, `agent`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _302 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.03617718273750178 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.034400382226469184 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.050837496326770495 - nodes in this community are weakly interconnected._