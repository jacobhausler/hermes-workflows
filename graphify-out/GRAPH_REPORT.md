# Graph Report - tree  (2026-10-03)

## Corpus Check
- 233 files · ~312,955 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2363 nodes · 4838 edges · 139 communities (107 shown, 32 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 286 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- importlib_util
- Changelog
- shutil
- run_child
- test_lane_hygiene_preamble_8edcc9bf.py
- os
- wf.py
- json
- test_preflight_liveness_152be7f7.py
- pathlib
- subprocess
- wfcommon.py
- main
- test_fanout_expand.mjs
- _Importer
- _Exporter
- .meta
- log
- lane_recover.py
- wf_dialect.py
- test_11_ui_imports.mjs
- ref_node_assert
- DoorLib50
- _sidecar_live_registered
- test_silent_death_reaper_8.py
- test_fanout_item_goal.py
- jload
- sys
- __init__.py
- act_status
- efp
- settings_runs_root
- 11-golden-solo.py
- _ping_route_once
- test_failures_0923.py
- threading
- test_proctree_identity_80.py
- act_save
- test_live_truth_ui.mjs
- _final_quiesce
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- validate_graph_errors
- 3. Operate
- runner_alive
- CurrentAttemptMetrics
- act_run
- Graph grammar and authoring boundaries
- test_register_surface.mjs
- notify
- EngineNextCut
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- AGENTS.md
- _resolve_models
- test_lost_handoff_sync_wake_r18.py
- CardBackend
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- Disclosure verification — clause-by-clause evidence
- DialectRefusal
- LiveTruth
- test_node_panel.mjs
- test_status_next.py
- amend
- test_proctree_61b.py
- hermes_home
- test_session_wake_101.py
- TeamIntegration
- test_pill_rail.mjs
- BaseHTTPRequestHandler
- test_session_wake_matrix_101.py
- test_wfpid_owner_8.py
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- test_orphan_adopt_790c6ad.py
- ConcurrencyBake100
- _sweep_orphans
- Contributing to hermes-workflows
- ref_node_fs
- graph_check.py
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- test_schema_enum_107.py
- _cancel_evidence
- Run operations and read model
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_B2-retry.py
- hermes_home
- _SV
- _input_graph
- test_routing_routes.py
- test_run_dry_run.py
- _B
- dep_satisfied
- install
- suite.py
- js_import
- test_incident_response_93.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- Hermes Workflows
- DoorLane
- Claim
- test_suite_admission_17.py
- native_engine
- test_sprint101_D-surface.py
- test_validator_caps.py
- manifest.json
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- Run
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
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
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

## Communities (139 total, 32 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (100): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+92 more)

### Community 1 - "importlib_util"
Cohesion: 0.06
Nodes (36): hashlib, importlib_util, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), main() (+28 more)

### Community 2 - "Changelog"
Cohesion: 0.05
Nodes (46): asyncio, 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+38 more)

### Community 3 - "shutil"
Cohesion: 0.05
Nodes (22): shutil, answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, wf() (+14 more)

### Community 4 - "run_child"
Cohesion: 0.05
Nodes (45): _adopt_child(), _AdoptedHandle, _child_spoke(), _classify_rc_output(), derived_contract(), _first_message_s(), _harvest_cancelled(), _harvest_death() (+37 more)

### Community 5 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.07
Nodes (36): argparse, fnmatch, Pattern, excluded(), load_guards(), load_scrub_list(), main(), Path (+28 more)

### Community 6 - "os"
Cohesion: 0.06
Nodes (12): os, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Library verbs + /wf command: save (from run_id / inline), library list, run…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer… (+4 more)

### Community 7 - "wf.py"
Cohesion: 0.07
Nodes (38): concurrent_futures, socket, urllib_error, _aux_run(), build_inputs(), extract_json(), _inputs_block(), _is_build_lane() (+30 more)

### Community 8 - "json"
Cohesion: 0.07
Nodes (19): copy, json, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-… (+11 more)

### Community 9 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 10 - "pathlib"
Cohesion: 0.07
Nodes (18): atexit, importlib, pathlib, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v(), FEEDBACK #43: model preflight at run/amend submit time, before the first wave.… (+10 more)

### Community 11 - "subprocess"
Cohesion: 0.05
Nodes (12): subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., LaneSupervisor, Suite hook for the standalone 20-cycle lane-supervisor kill/resume harness., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+4 more)

### Community 12 - "wfcommon.py"
Cohesion: 0.08
Nodes (35): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), _env_ref_lookup(), _env_ref_var_name(), _expand_config_value() (+27 more)

### Community 13 - "main"
Cohesion: 0.07
Nodes (34): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), _crash_gen(), drain_inbox(), emit(), finalize(), main() (+26 more)

### Community 14 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 15 - "_Importer"
Cohesion: 0.14
Nodes (12): _control_kw(), _Importer, _ordered(), _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., A literal label -> str; a template label -> its literal spine (for ids). (+4 more)

### Community 16 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 17 - ".meta"
Cohesion: 0.09
Nodes (31): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+23 more)

### Community 18 - "log"
Cohesion: 0.10
Nodes (30): 1.0.17 — 2026-09-28, _bounded_retry(), _dangling_placeholders(), _fail_precondition(), fmt_goal(), _isolate_prior(), log(), now() (+22 more)

### Community 19 - "lane_recover.py"
Cohesion: 0.10
Nodes (30): apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls(), main(), open_ro(), profile_db() (+22 more)

### Community 20 - "wf_dialect.py"
Cohesion: 0.08
Nodes (26): _const_name(), _fmt_goal(), _forbidden_label(), _has_tpl(), _mask(), _match_close(), node_check(), _ordered_item() (+18 more)

### Community 21 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 22 - "ref_node_assert"
Cohesion: 0.09
Nodes (21): ref_node_assert, ref_node_crypto, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+13 more)

### Community 24 - "_sidecar_live_registered"
Cohesion: 0.08
Nodes (28): _proc_boottime(), _proc_children_of(), _proc_envv(), _proc_snapshot(), _proc_state(), Snapshot the spawn's live SUBTREE while it still LIVES: after it dies and is…, Can the process table be read at all? #61b B2 (fail-closed family of the door's…, Kernel start tick of a pid: field 22 of /proc/pid/stat (starttime, clock ticks… (+20 more)

### Community 25 - "test_silent_death_reaper_8.py"
Cohesion: 0.07
Nodes (11): contextlib, fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, Current-attempt heartbeat with real fake child identity; no provider access., kill_tree() (+3 more)

### Community 26 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 27 - "jload"
Cohesion: 0.14
Nodes (26): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), All per-item spawn records with a live pid, once every item is RUNNING., read_children(), terminal_action_pending(), active_child() (+18 more)

### Community 28 - "sys"
Cohesion: 0.08
Nodes (10): sys, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Identical solo child wrapper for both tag and candidate; records env key sets.…, B2b probes (peer-review owed items): (A) empty-array query shares the save law,…, #146 item 2 (peer review): the empty-result self-diagnosis must distinguish… (+2 more)

### Community 29 - "__init__.py"
Cohesion: 0.11
Nodes (24): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), difflib, act_inbox(), act_steer(), act_submit(), _model_names_valid(), model_preflight(), _nearest_effort() (+16 more)

### Community 30 - "act_status"
Cohesion: 0.10
Nodes (22): act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts() (+14 more)

### Community 31 - "efp"
Cohesion: 0.14
Nodes (23): File-authored graphs, Per-run concurrency (optional), Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.… (+15 more)

### Community 32 - "settings_runs_root"
Cohesion: 0.10
Nodes (22): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), node_child_home(), node_child_metrics(), owner_setting() (+14 more)

### Community 33 - "11-golden-solo.py"
Cohesion: 0.10
Nodes (14): glob, hermes_constants, plugin_api, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3… (+6 more)

### Community 34 - "_ping_route_once"
Cohesion: 0.10
Nodes (21): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+13 more)

### Community 35 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 36 - "threading"
Cohesion: 0.09
Nodes (8): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, wf(), Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, wf(), P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 37 - "test_proctree_identity_80.py"
Cohesion: 0.10
Nodes (12): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+4 more)

### Community 38 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 39 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 40 - "_final_quiesce"
Cohesion: 0.14
Nodes (21): _account_tree(), _complete(), _final_quiesce(), _left_live_record(), _proc_alive(), _proc_pids_by_pgid(), _proc_unreadable_record(), _proctree_hold_s() (+13 more)

### Community 41 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 42 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 43 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 44 - "validate_graph_errors"
Cohesion: 0.11
Nodes (17): _defaults_errors(), grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+9 more)

### Community 45 - "3. Operate"
Cohesion: 0.11
Nodes (19): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+11 more)

### Community 46 - "runner_alive"
Cohesion: 0.11
Nodes (19): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, find_run(), launch_runs_root(), node_facts(), precondition_facts(), 91b9a3de: cross-container liveness truth. The runner takes an exclusive…, A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives…, 91b9a3de: ONE liveness law, cross-container safe. The runner holds an exclusive… (+11 more)

### Community 48 - "act_run"
Cohesion: 0.13
Nodes (18): act_amend(), act_run(), _concurrency_bake(), _frozen_committed(), _lane_entry(), _lane_paths(), _liveness_hint_suffix(), _profile_error() (+10 more)

### Community 49 - "Graph grammar and authoring boundaries"
Cohesion: 0.12
Nodes (11): Node budgets, Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Tags (meta envelope), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo) (+3 more)

### Community 50 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 51 - "notify"
Cohesion: 0.12
Nodes (18): notify(), Redact bearer/credential shapes out of anything the wake path may persist., The runner-authored owner turn, or None when the event has no template (an…, Fresh no-redirect opener per call. Module-level would share urllib's per-…, (rows, delivered_ids) from wake.jsonl, fail-open on every shape the file can be…, Append one ledger row; a failure is loud on stderr (runner.log) and NEVER…, Durable amendment generation: how many graph.amended events the run's own…, The run's ALREADY-COMMITTED failed-node set straight from the node records… (+10 more)

### Community 53 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 54 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 55 - "AGENTS.md"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+4 more)

### Community 56 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+8 more)

### Community 57 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.17
Nodes (10): inspect, action_rows(), _append_act(), _door_call(), Owner, parked(), BaseHTTPRequestHandler, PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous… (+2 more)

### Community 58 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 59 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 61 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 62 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 63 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (15): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+7 more)

### Community 64 - "DialectRefusal"
Cohesion: 0.15
Nodes (9): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _line(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.… (+1 more)

### Community 66 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 67 - "test_status_next.py"
Cohesion: 0.12
Nodes (4): #102 bounded re-drive must not pretend-resume a DEAD (empty) session. Measured…, lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 68 - "amend"
Cohesion: 0.15
Nodes (14): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, What you get, Nodes and data, Run and handoff (+6 more)

### Community 69 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 70 - "hermes_home"
Cohesion: 0.14
Nodes (14): _attempt_api_calls(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, Where to POST a wake, host config first (mirrors the api_server adapter's own…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, _tool_progress(), _wake_endpoint(), child_metrics(), hermes_home() (+6 more)

### Community 71 - "test_session_wake_101.py"
Cohesion: 0.15
Nodes (6): http_server, answer(), drive(), One runner process, stdout captured (the door's spawn redirects this to…, Session-wake law: lifecycle TRANSITIONS reach the owner session stamp, exactly…, _Sink

### Community 72 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 73 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 74 - "BaseHTTPRequestHandler"
Cohesion: 0.15
Nodes (5): _Hang, _Hang10, BaseHTTPRequestHandler, _Redir, _SinkB

### Community 75 - "test_session_wake_matrix_101.py"
Cohesion: 0.17
Nodes (7): answer(), base_env(), drive(), mk(), A run dir as the door creates one (wake_protocol stamp included), so the…, Session-wake maintainer matrix: the round-1/round-2 law set, exercised through…, urllib_request

### Community 76 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 77 - "_create_run"
Cohesion: 0.20
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+4 more)

### Community 79 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 80 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 81 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 83 - "_sweep_orphans"
Cohesion: 0.20
Nodes (11): _boot_sweep(), _kill_pool(), _proctree_kill_proof_s(), best-effort waitpid for a runner-adopted orphan that died (zombie hygiene;…, #61c: /proc-verify every pid is dead within the budget. (True, []) when PROVEN…, SIGTERM (grace) -> SIGKILL fallback -> /proc re-walk for a scattered set of…, Kill+reap every runner-adopted orphan, /proc-proven, cascading: killing an…, #61c: before a (re)spawned runner launches anything, reap the survivors the… (+3 more)

### Community 84 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 85 - "ref_node_fs"
Cohesion: 0.20
Nodes (5): ref_node_fs, code, { fanItems, fanCounts }, here, src

### Community 86 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 87 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 88 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 89 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 90 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 91 - "_cancel_evidence"
Cohesion: 0.20
Nodes (10): _banked_work(), _cancel_evidence(), child_work_dir(), _clean_capture(), _dead_session_harvest(), a2d7f664: honest evidence for a quorum-straggler cancel. Snapshot of the…, Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —… (+2 more)

### Community 92 - "Run operations and read model"
Cohesion: 0.25
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit), submit()

### Community 93 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 94 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 95 - "hermes_home"
Cohesion: 0.25
Nodes (9): hermes_home(), Message-existence evidence for the #102 dead-session guard: True when the dead…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map() (+1 more)

### Community 97 - "_input_graph"
Cohesion: 0.25
Nodes (8): _coerce_graph(), _inline_graph_size_error(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 98 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 100 - "_B"
Cohesion: 0.32
Nodes (3): _A, _B, BaseHTTPRequestHandler

### Community 101 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 102 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 103 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 104 - "js_import"
Cohesion: 0.29
Nodes (7): check(), refuses(), export_report(), js_import(), _main(), See module docstring. `node_check=False` skips the optional subprocess gate., {"ok": True, "js": str, "lossy": [{node, key, value}], "warnings": [...]} |…

### Community 105 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 106 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 107 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 108 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 109 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 112 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 113 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 114 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 115 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 116 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 117 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **293 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+288 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1181 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `Changelog`, `wf.py`, `runner_alive`, `_resolve_models`, `jload`, `act_status`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_assert`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _293 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05405940594059406 - nodes in this community are weakly interconnected._
- **Should `importlib_util` be split into smaller, more focused modules?**
  _Cohesion score 0.056535504296698326 - nodes in this community are weakly interconnected._
- **Should `Changelog` be split into smaller, more focused modules?**
  _Cohesion score 0.050072568940493466 - nodes in this community are weakly interconnected._