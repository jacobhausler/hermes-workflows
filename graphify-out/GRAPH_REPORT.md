# Graph Report - tree  (2026-10-03)

## Corpus Check
- 232 files · ~312,339 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2357 nodes · 4829 edges · 137 communities (108 shown, 29 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 286 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- os
- wf.py
- run_child
- test_review_fixes.py
- test_lane_hygiene_preamble_8edcc9bf.py
- sys
- shutil
- test_preflight_liveness_152be7f7.py
- re
- _Exporter
- .meta
- test_fanout_expand.mjs
- wfcommon.py
- log
- ref_node_fs
- lane_recover.py
- threading
- jload
- time
- test_11_ui_imports.mjs
- main
- _final_quiesce
- hermes_home
- subprocess
- act_run
- DoorLib50
- _sidecar_live_registered
- wf_dialect.py
- test_fanout_item_goal.py
- _Importer
- test_failures_0923.py
- test_session_wake_101.py
- _ping_route_once
- settings_runs_root
- json
- test_silent_death_reaper_8.py
- .agent_args
- test_deleted_cwd_resume_5c37b19.py
- efp
- test_proctree_identity_80.py
- act_save
- test_live_truth_ui.mjs
- test_session_wake_matrix_101.py
- test_daemonize_8.py
- pathlib
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- 3. Operate
- CurrentAttemptMetrics
- validate_graph_errors
- plugin_api.py
- __init__.py
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- Hermes Workflows
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- SKILL.md
- Disclosure verification — clause-by-clause evidence
- act_amend
- graph_fingerprint
- LiveTruth
- test_node_panel.mjs
- _expand_config_values
- test_proctree_61b.py
- Changelog
- Run operations and read model
- test_orphan_adopt_790c6ad.py
- TeamIntegration
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- amend
- ConcurrencyBake100
- test_node_facts.py
- Contributing to hermes-workflows
- graph_check.py
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- test_schema_enum_107.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_lost_handoff_sync_wake_r18.py
- act_wait
- test_sprint101w2_B2-retry.py
- DialectRefusal
- _SV
- _input_graph
- Owner
- test_run_dry_run.py
- model_preflight
- install
- suite.py
- test_incident_response_93.py
- test_steer_live_40.py
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- Manual installation — Hermes Workflows 1.2.0
- DoorLane
- Claim
- node_facts
- 1.0.1 — 2026-09-25
- 11-claim-wrapper.py
- native_engine
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- node_child_home
- release_gate
- date-now.js
- meta-nonliteral.js
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
1. `run_child()` - 45 edges
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
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `1.0.17 — 2026-09-28` --references--> `fmt_goal()`  [INFERRED]
  CHANGELOG.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (137 total, 29 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (100): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+92 more)

### Community 1 - "os"
Cohesion: 0.06
Nodes (36): hashlib, importlib_util, os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+28 more)

### Community 2 - "wf.py"
Cohesion: 0.05
Nodes (50): concurrent_futures, socket, urllib_error, _banked_work(), build_inputs(), _clean_capture(), _dead_session_harvest(), drain_inbox() (+42 more)

### Community 3 - "run_child"
Cohesion: 0.05
Nodes (49): _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), _first_message_s() (+41 more)

### Community 4 - "test_review_fixes.py"
Cohesion: 0.04
Nodes (22): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, wf(), answer() (+14 more)

### Community 5 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.07
Nodes (36): argparse, fnmatch, Pattern, excluded(), load_guards(), load_scrub_list(), main(), Path (+28 more)

### Community 6 - "sys"
Cohesion: 0.06
Nodes (19): atexit, importlib, sys, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v(), FEEDBACK #43: model preflight at run/amend submit time, before the first wave.… (+11 more)

### Community 7 - "shutil"
Cohesion: 0.05
Nodes (14): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, Ledger e68544a37be37657 (fb-fix-2dd8de73): a harvest-on-death `partial` must…, #102 bounded re-drive must not pretend-resume a DEAD (empty) session. Measured…, Door-transport guard: run_context must never silently route a map to seed.…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is… (+6 more)

### Community 8 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 9 - "re"
Cohesion: 0.07
Nodes (19): glob, hermes_constants, plugin_api, re, capture(), _core_home(), main(), normalize() (+11 more)

### Community 10 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 11 - ".meta"
Cohesion: 0.09
Nodes (30): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+22 more)

### Community 12 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 13 - "wfcommon.py"
Cohesion: 0.08
Nodes (31): shlex, _active_spawn(), blocked_legibility(), current_attempt(), _downstream(), launch_runs_root(), prune_states(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE… (+23 more)

### Community 14 - "log"
Cohesion: 0.10
Nodes (31): _bounded_retry(), _dangling_placeholders(), _fail_precondition(), finalize(), _isolate_prior(), log(), loop(), notify() (+23 more)

### Community 15 - "ref_node_fs"
Cohesion: 0.08
Nodes (22): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource (+14 more)

### Community 16 - "lane_recover.py"
Cohesion: 0.10
Nodes (30): apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls(), main(), open_ro(), profile_db() (+22 more)

### Community 17 - "threading"
Cohesion: 0.07
Nodes (11): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal… (+3 more)

### Community 18 - "jload"
Cohesion: 0.11
Nodes (31): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), terminal_action_pending(), active_child(), _active_spawns() (+23 more)

### Community 19 - "time"
Cohesion: 0.06
Nodes (8): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Library verbs + /wf command: save (from run_id / inline), library list, run…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…, time

### Community 20 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 21 - "main"
Cohesion: 0.08
Nodes (28): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), _crash_gen(), emit(), main(), consume_markers(), _stop_watcher() (+20 more)

### Community 22 - "_final_quiesce"
Cohesion: 0.09
Nodes (30): _account_tree(), _complete(), _boot_sweep(), _final_quiesce(), _kill_pool(), _left_live_record(), _proc_alive(), _proc_pids_by_pgid() (+22 more)

### Community 23 - "hermes_home"
Cohesion: 0.08
Nodes (29): _attempt_api_calls(), hermes_home(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, Message-existence evidence for the #102 dead-session guard: True when the dead…, Where to POST a wake, host config first (mirrors the api_server adapter's own…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed… (+21 more)

### Community 24 - "subprocess"
Cohesion: 0.08
Nodes (14): contextlib, subprocess, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness., GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no… (+6 more)

### Community 25 - "act_run"
Cohesion: 0.09
Nodes (27): act_list(), act_run(), act_status(), _card(), _concurrency_bake(), _create_run(), _identity_stamps(), _lane_entry() (+19 more)

### Community 27 - "_sidecar_live_registered"
Cohesion: 0.08
Nodes (28): _proc_boottime(), _proc_children_of(), _proc_envv(), _proc_snapshot(), _proc_state(), Snapshot the spawn's live SUBTREE while it still LIVES: after it dies and is…, Can the process table be read at all? #61b B2 (fail-closed family of the door's…, Kernel start tick of a pid: field 22 of /proc/pid/stat (starttime, clock ticks… (+20 more)

### Community 28 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _line() (+16 more)

### Community 29 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 30 - "_Importer"
Cohesion: 0.16
Nodes (10): _control_kw(), _forbidden_label(), _Importer, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the… (+2 more)

### Community 31 - "test_failures_0923.py"
Cohesion: 0.08
Nodes (9): sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+1 more)

### Community 32 - "test_session_wake_101.py"
Cohesion: 0.09
Nodes (10): answer(), drive(), _Hang, _Hang10, BaseHTTPRequestHandler, One runner process, stdout captured (the door's spawn redirects this to…, Session-wake law: lifecycle TRANSITIONS reach the owner session stamp, exactly…, _Redir (+2 more)

### Community 33 - "_ping_route_once"
Cohesion: 0.09
Nodes (23): _hermes_bin(), _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess() (+15 more)

### Community 34 - "settings_runs_root"
Cohesion: 0.11
Nodes (21): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting(), profile_errors() (+13 more)

### Community 35 - "json"
Cohesion: 0.11
Nodes (13): copy, json, Identical solo child wrapper for both tag and candidate; records env key sets.…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Core-10 #89 review blocker: the EFFECTIVE synthesis prompt must not carry the…, census-fanout example gate (Core-10 authoring contract). The template's…, argv(), check() (+5 more)

### Community 36 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 37 - ".agent_args"
Cohesion: 0.15
Nodes (13): _ordered(), _parse_literal(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the… (+5 more)

### Community 38 - "test_deleted_cwd_resume_5c37b19.py"
Cohesion: 0.09
Nodes (3): mk(), 5c37b19 — deleted-cwd runner killers (fb 5c37b19109179eab, run…, #61 — the runner is process-tree aware before it judges an attempt. Evidence…

### Community 39 - "efp"
Cohesion: 0.11
Nodes (22): Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), gate(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, _aux_run() (+14 more)

### Community 40 - "test_proctree_identity_80.py"
Cohesion: 0.10
Nodes (12): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+4 more)

### Community 41 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 42 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 43 - "test_session_wake_matrix_101.py"
Cohesion: 0.11
Nodes (10): _A, answer(), _B, base_env(), drive(), mk(), BaseHTTPRequestHandler, A run dir as the door creates one (wake_protocol stamp included), so the… (+2 more)

### Community 44 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 45 - "pathlib"
Cohesion: 0.10
Nodes (7): pathlib, LaneSupervisor, Suite hook for the standalone 20-cycle lane-supervisor kill/resume harness., Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, B2b probes (peer-review owed items): (A) empty-array query shares the save law,…, 4052d57719653b1a: atomic library replay binding, no real runner.

### Community 46 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 47 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 48 - "3. Operate"
Cohesion: 0.11
Nodes (19): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+11 more)

### Community 50 - "validate_graph_errors"
Cohesion: 0.11
Nodes (16): apply_graph_defaults(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,… (+8 more)

### Community 51 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 52 - "__init__.py"
Cohesion: 0.16
Nodes (17): difflib, act_inbox(), act_steer(), act_submit(), _model_names_valid(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, Return graph-level and node-level defects together, before any write/spawn., #50 (epic #49): submit a hand-rolled graph for STUDY — the quarantine inbox… (+9 more)

### Community 53 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 54 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 55 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 56 - "Hermes Workflows"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, For agents and contributors, Hermes Workflows (+4 more)

### Community 57 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+8 more)

### Community 58 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 59 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 62 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 63 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 64 - "SKILL.md"
Cohesion: 0.14
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 65 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (15): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+7 more)

### Community 66 - "act_amend"
Cohesion: 0.15
Nodes (15): act_amend(), act_release(), act_stop(), _frozen_committed(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, Strict: no silent normalization — ids double as directory names. Profile-scoped…, ONE gate-answer path for tool and UI. Stale answers never block: the answer… (+7 more)

### Community 67 - "graph_fingerprint"
Cohesion: 0.23
Nodes (14): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+6 more)

### Community 69 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 70 - "_expand_config_values"
Cohesion: 0.13
Nodes (15): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _expand_config_values(), _is_non_env_secret_ref(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,… (+7 more)

### Community 71 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 72 - "Changelog"
Cohesion: 0.15
Nodes (13): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+5 more)

### Community 73 - "Run operations and read model"
Cohesion: 0.18
Nodes (13): 1.1.3 — 2026-10-01, What you get, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit) (+5 more)

### Community 74 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 75 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 76 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 77 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 78 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 79 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 80 - "amend"
Cohesion: 0.20
Nodes (11): 3d. Failures, resume, amend, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Per-run concurrency (optional), Staleness and replay, Tags (meta envelope), Run and handoff (+3 more)

### Community 82 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 83 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 84 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 85 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 86 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 87 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 88 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 89 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 90 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.28
Nodes (6): http_server, inspect, action_rows(), parked(), PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous…, wait_for()

### Community 91 - "act_wait"
Cohesion: 0.25
Nodes (8): act_wait(), _respawn_throttled(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, #8 fix-law item 2 (crash-visibility): make a silent runner death loud BEFORE a…, ONE bridge: the crash-visibility reaper, then the spawn. Every door path that…, _reap_silent_death(), _respawn_runner(), _after_death()

### Community 92 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 93 - "DialectRefusal"
Cohesion: 0.28
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 95 - "_input_graph"
Cohesion: 0.25
Nodes (8): _coerce_graph(), _inline_graph_size_error(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 96 - "Owner"
Cohesion: 0.29
Nodes (5): _append_act(), _door_call(), Owner, BaseHTTPRequestHandler, The api_server shape: the POST stays open for the whole owner turn…

### Community 98 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 99 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 100 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

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

### Community 106 - "Manual installation — Hermes Workflows 1.2.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.2.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 109 - "node_facts"
Cohesion: 0.33
Nodes (6): node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 110 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 111 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 112 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 113 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 114 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 115 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 119 - "node_child_home"
Cohesion: 0.50
Nodes (4): node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as…

### Community 120 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1176 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `wf.py`, `Changelog`, `jload`, `_resolve_models`, `act_wait`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_fs`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05405940594059406 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.058385093167701865 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.049019607843137254 - nodes in this community are weakly interconnected._