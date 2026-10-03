# Graph Report - tree  (2026-10-03)

## Corpus Check
- 251 files · ~335,302 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2491 nodes · 5083 edges · 153 communities (122 shown, 31 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- test_fanout_item_goal.py
- pathlib
- run_child
- json
- wf.py
- SKILL.md
- tempfile
- log
- lane_recover.py
- shutil
- time
- test_preflight_liveness_152be7f7.py
- wf_test_isolation.py
- os
- main
- importlib_util
- subprocess
- .meta
- test_fanout_expand.mjs
- __init__.py
- _Exporter
- jload
- test_11_ui_imports.mjs
- wf_dialect.py
- wfcommon.py
- hermes_home
- ref_node_fs
- efp
- DoorLib50
- _final_quiesce
- Run operations and read model
- _Importer
- plugin.js
- test_silent_death_reaper_8.py
- 11-golden-solo.py
- test_lane_hygiene_preamble_8edcc9bf.py
- act_run
- test_proctree_identity_80.py
- NodePanel
- act_save
- test_live_truth_ui.mjs
- test_session_wake_matrix_101.py
- test_daemonize_8.py
- DirectiveBody
- _ping_route_once
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- act_amend
- CurrentAttemptMetrics
- plugin_api.py
- test_register_surface.mjs
- settings_runs_root
- test_canvas_wrap.mjs
- node_rec
- test_node_click_expand.mjs
- .statement
- _expand_config_values
- CardBackend
- test_confidence_substrate_116.py
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- _SV
- Changelog
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- test_pane_model_agentfirst.mjs
- validate_graph_errors
- 3. Operate
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- act_wait
- test_proctree_61b.py
- test_orphan_adopt_790c6ad.py
- GraphView
- TeamIntegration
- test_pane_origin_hardening.mjs
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_provenance_counters_57.py
- test_route_efforts_b3c98b2a.py
- ConcurrencyBake100
- test_node_facts.py
- Contributing to hermes-workflows
- GateActions
- ref_node_url
- graph_check.py
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- test_schema_enum_107.py
- DialectRefusal
- Proposed core hook: tool-result card rendering (optional, upstream-shaped)
- test_lost_handoff_sync_wake_r18.py
- test_sprint101w2_B2-retry.py
- pack.py
- Owner
- test_routing_routes.py
- test_run_dry_run.py
- _aux_run
- hermes_root
- dep_satisfied
- act_inbox
- install
- confidence_substrate
- suite.py
- LifecycleNotice
- test_incident_response_93.py
- test_status_next.py
- test_steer_live_40.py
- build_inputs
- _defaults_errors
- 4. Contribute
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- _route_enforcement
- DoorLane
- Claim
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tool_call_text_6st.py
- _dead_session_harvest
- _wake_identity
- 1.0.1 — 2026-09-25
- 11-claim-wrapper.py
- native_engine
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- .render_item_template
- release_gate
- date-now.js
- meta-nonliteral.js
- test_error_classes_exhaustive_vb65.py
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
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `What the plugin would then register (one block, `desktop/plugin.js`)` --references--> `SessionStrip()`  [INFERRED]
  docs/card-toolresult-hook.md → desktop/plugin.js
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (153 total, 31 thin omitted)

### Community 0 - "test_fanout_item_goal.py"
Cohesion: 0.06
Nodes (45): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does., sh(), wf(), _assert_no_fail_closed(), _assert_prompts_carry_own(), cards() (+37 more)

### Community 1 - "pathlib"
Cohesion: 0.06
Nodes (30): copy, pathlib, re, main(), pr_tag_audit.py — release-time gate for `(open PR #NN)` doc tags. Docs that…, resolve_repo(), sys, _fake_state_row() (+22 more)

### Community 2 - "run_child"
Cohesion: 0.05
Nodes (51): _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), _first_message_s() (+43 more)

### Community 3 - "json"
Cohesion: 0.05
Nodes (17): json, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), Lane A: routed spawn, env boundary, missing-profile race and DB ownership., v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+9 more)

### Community 4 - "wf.py"
Cohesion: 0.06
Nodes (50): concurrent_futures, socket, urllib_error, extract_json(), _is_build_lane(), _lane_hygiene_preamble(), last_balanced_object(), _match_object() (+42 more)

### Community 5 - "SKILL.md"
Cohesion: 0.05
Nodes (35): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+27 more)

### Community 6 - "tempfile"
Cohesion: 0.05
Nodes (20): atexit, importlib, tempfile, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v(), The child launcher is operator-controlled, never a tool argument. (+12 more)

### Community 7 - "log"
Cohesion: 0.07
Nodes (44): _bounded_retry(), drain_inbox(), emit(), _fail_precondition(), finalize(), _isolate_prior(), log(), consume_markers() (+36 more)

### Community 8 - "lane_recover.py"
Cohesion: 0.08
Nodes (40): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+32 more)

### Community 9 - "shutil"
Cohesion: 0.05
Nodes (12): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, #113 — validate() must split integer from number and reject booleans. Before…, Ledger e68544a37be37657 (fb-fix-2dd8de73): a harvest-on-death `partial` must…, #102 bounded re-drive must not pretend-resume a DEAD (empty) session. Measured…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, wf() (+4 more)

### Community 10 - "time"
Cohesion: 0.05
Nodes (12): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, wf(), #61 — the runner is process-tree aware before it judges an attempt. Evidence…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Regression: an amend after the final in-loop marker check survives > grace_s.…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1… (+4 more)

### Community 11 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check(), contract() (+21 more)

### Community 12 - "wf_test_isolation.py"
Cohesion: 0.05
Nodes (11): Authoring door regressions; all state stays in this worktree, no…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, B2b probes (peer-review owed items): (A) empty-array query shares the save law,…, #146 item 2 (peer review): the empty-result self-diagnosis must distinguish…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Door-transport guard: run_context must never silently route a map to seed.…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is… (+3 more)

### Community 13 - "os"
Cohesion: 0.07
Nodes (19): os, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+11 more)

### Community 14 - "main"
Cohesion: 0.06
Nodes (35): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), _boot_sweep(), _crash_gen(), main(), _stop_watcher(), _proctree_kill_proof_s() (+27 more)

### Community 15 - "importlib_util"
Cohesion: 0.06
Nodes (13): hashlib, importlib_util, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, #32 publish-as-file: the portable workflow file convention. (1) top-level… (+5 more)

### Community 16 - "subprocess"
Cohesion: 0.07
Nodes (17): contextlib, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness., GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., BlockedLegibility100 (+9 more)

### Community 17 - ".meta"
Cohesion: 0.09
Nodes (30): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+22 more)

### Community 18 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 19 - "__init__.py"
Cohesion: 0.10
Nodes (31): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), difflib, _alias_provider_pair(), handle(), _lane_key_error(), _last_event_ts(), _model_policy_error(), model_preflight() (+23 more)

### Community 20 - "_Exporter"
Cohesion: 0.15
Nodes (12): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+4 more)

### Community 21 - "jload"
Cohesion: 0.11
Nodes (29): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, act_list(), act_release(), act_status(), act_steer(), act_stop(), _lane_state(), _output_pointer() (+21 more)

### Community 22 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 23 - "wf_dialect.py"
Cohesion: 0.08
Nodes (25): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _mask(), _match_close() (+17 more)

### Community 24 - "wfcommon.py"
Cohesion: 0.07
Nodes (27): shlex, _active_spawn(), amend_preview(), apply_substrate_disclosure(), current_attempt(), _downstream(), launch_runs_root(), node_child_home() (+19 more)

### Community 25 - "hermes_home"
Cohesion: 0.08
Nodes (29): _attempt_api_calls(), hermes_home(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, Message-existence evidence for the #102 dead-session guard: True when the dead…, Where to POST a wake, host config first (mirrors the api_server adapter's own…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed… (+21 more)

### Community 26 - "ref_node_fs"
Cohesion: 0.09
Nodes (21): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+13 more)

### Community 27 - "efp"
Cohesion: 0.12
Nodes (27): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Per-run concurrency (optional), Staleness and replay, Tags (meta envelope), Top-level provenance, Portable workflow files (publish = put the file on git) (+19 more)

### Community 29 - "_final_quiesce"
Cohesion: 0.10
Nodes (27): _account_tree(), _complete(), _final_quiesce(), _kill_pool(), _left_live_record(), _proc_alive(), _proc_pids_by_pgid(), _proc_unreadable_record() (+19 more)

### Community 30 - "Run operations and read model"
Cohesion: 0.11
Nodes (25): For agents and contributors, Graph grammar in 30 seconds, Hermes Workflows, Install, License, Requirements, The `workflow` tool, Two builds, one codebase (+17 more)

### Community 31 - "_Importer"
Cohesion: 0.17
Nodes (12): _Importer, _line(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to… (+4 more)

### Community 32 - "plugin.js"
Cohesion: 0.09
Nodes (24): BREATHE, EDGE_TONE, $fanExpanded, $fanItem, fanItems(), $fanOpen, GATE_PULSE, itemLabel() (+16 more)

### Community 33 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 34 - "11-golden-solo.py"
Cohesion: 0.10
Nodes (14): glob, hermes_constants, plugin_api, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3… (+6 more)

### Community 35 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.14
Nodes (19): stat, check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file. (+11 more)

### Community 36 - "act_run"
Cohesion: 0.12
Nodes (22): act_run(), _card(), _concurrency_bake(), _create_run(), _hermes_bin(), _identity_stamps(), _lane_entry(), _lane_paths() (+14 more)

### Community 37 - "test_proctree_identity_80.py"
Cohesion: 0.10
Nodes (12): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., alive(), boottime(), kill_all(), #80 review findings — a sidecar row is a CLAIM; /proc is the COURT… (+4 more)

### Community 38 - "NodePanel"
Cohesion: 0.16
Nodes (21): attemptNo(), box(), defaultTabFor(), Dot(), factText(), fanCounts(), FanStrip(), fanSummary() (+13 more)

### Community 39 - "act_save"
Cohesion: 0.13
Nodes (21): act_library(), act_save(), _from_unknown_error(), _lib_path(), _lib_read(), _lib_rel_name(), library_root(), _library_roots() (+13 more)

### Community 40 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 41 - "test_session_wake_matrix_101.py"
Cohesion: 0.11
Nodes (10): _A, answer(), _B, base_env(), drive(), mk(), BaseHTTPRequestHandler, A run dir as the door creates one (wake_protocol stamp included), so the… (+2 more)

### Community 42 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 43 - "DirectiveBody"
Cohesion: 0.18
Nodes (20): ago(), DirectiveBody(), fmtDur(), idleS(), idleTone(), inlineHeader(), ItemChips(), kfmt() (+12 more)

### Community 44 - "_ping_route_once"
Cohesion: 0.11
Nodes (19): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+11 more)

### Community 45 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 46 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 47 - "act_amend"
Cohesion: 0.11
Nodes (19): act_amend(), act_submit(), _coerce_graph(), _frozen_committed(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), _profile_error() (+11 more)

### Community 49 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 50 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 51 - "settings_runs_root"
Cohesion: 0.14
Nodes (16): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting(), A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives…, A surviving `${...}` after expansion means the referenced var is unset (or a… (+8 more)

### Community 52 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 53 - "node_rec"
Cohesion: 0.18
Nodes (16): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), terminal_action_pending(), fingerprint_valid(), gate_answer_valid() (+8 more)

### Community 54 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 55 - ".statement"
Cohesion: 0.15
Nodes (8): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, _statements()

### Community 56 - "_expand_config_values"
Cohesion: 0.12
Nodes (17): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _expand_config_values(), _is_non_env_secret_ref(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Top-level `workflows: confidence_substrate:` — full YAML when a loader is… (+9 more)

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

### Community 63 - "_SV"
Cohesion: 0.14
Nodes (9): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not() (+1 more)

### Community 64 - "Changelog"
Cohesion: 0.13
Nodes (14): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+6 more)

### Community 67 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 68 - "test_pane_model_agentfirst.mjs"
Cohesion: 0.13
Nodes (12): bare, here, jsxPath, m, modPath, none, now, reactPath (+4 more)

### Community 69 - "validate_graph_errors"
Cohesion: 0.15
Nodes (13): grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), _tok_when() (+5 more)

### Community 70 - "3. Operate"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+6 more)

### Community 71 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.21
Nodes (14): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, DirectiveCard(), focusAtom(), isBusy(), listQuery(), ownedRuns(), PaneTabTitle(), register() (+6 more)

### Community 72 - "act_wait"
Cohesion: 0.15
Nodes (13): act_wait(), _respawn_throttled(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, #8 fix-law item 2 (crash-visibility): make a silent runner death loud BEFORE a…, ONE bridge: the crash-visibility reaper, then the spawn. Every door path that…, One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law…, Direct spawn for no-fork platforms / refused fork: here the Popen'd child IS… (+5 more)

### Community 73 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 74 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 75 - "GraphView"
Cohesion: 0.26
Nodes (13): bandRows(), columnGroups(), depthMap(), edgeFlowPolicy(), Edges(), edgeTone(), FanStack(), GraphView() (+5 more)

### Community 76 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 77 - "test_pane_origin_hardening.mjs"
Cohesion: 0.15
Nodes (9): m2, m3, map, model, owned, paneModel, poisoned, runs (+1 more)

### Community 78 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 79 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 81 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 82 - "test_provenance_counters_57.py"
Cohesion: 0.23
Nodes (4): mk_run(), ProvenanceCounters, #57 — `list` payload gains the per-root provenance rollup (QM digest contract).…, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 83 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 85 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 86 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 87 - "GateActions"
Cohesion: 0.22
Nodes (10): api(), ctxRest(), GateActions(), nudgeOwner(), Pill(), pillProgress(), PillRail(), railModel() (+2 more)

### Community 88 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 89 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 90 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 91 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 92 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 93 - "DialectRefusal"
Cohesion: 0.24
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 94 - "Proposed core hook: tool-result card rendering (optional, upstream-shaped)"
Cohesion: 0.22
Nodes (8): 1. New area + payload type — `lib/tool-result-contribs.ts` (new file), 2. Export from the SDK — `sdk/index.ts`, 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`, Plugin-side readiness, Proposed core hook: tool-result card rendering (optional, upstream-shaped), The patch (≈30 lines, additive), What the plugin would then register (one block, `desktop/plugin.js`), Why (issue #157)

### Community 95 - "test_lost_handoff_sync_wake_r18.py"
Cohesion: 0.28
Nodes (6): http_server, inspect, action_rows(), parked(), PR #97 R18 — the lost handoff: an owner action taken INSIDE the synchronous…, wait_for()

### Community 96 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 97 - "pack.py"
Cohesion: 0.39
Nodes (7): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), ZipInfo

### Community 98 - "Owner"
Cohesion: 0.29
Nodes (5): _append_act(), _door_call(), Owner, BaseHTTPRequestHandler, The api_server shape: the POST stays open for the whole owner turn…

### Community 99 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 101 - "_aux_run"
Cohesion: 0.25
Nodes (8): _aux_run(), _kill_aux_tree(), _lane_gate(), Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, subprocess.run-shaped helper for the runner's OWN auxiliary probes, registered…, SIGKILL the aux child AND its group (the child is its own group leader via…, fb-digest-29d (64c6772b): a node that declares `repo: <path>` owns a git lane,…, _resume_preamble()

### Community 102 - "hermes_root"
Cohesion: 0.29
Nodes (7): hermes_root(), profile_errors(), profiles_by_session(), profiles_root(), {session_id: profile_name} across the estate root's default db and every…, The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a…, 1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER…

### Community 103 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 104 - "act_inbox"
Cohesion: 0.29
Nodes (7): act_inbox(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 105 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 106 - "confidence_substrate"
Cohesion: 0.29
Nodes (7): Nodes and data, _dangling_placeholders(), Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, confidence_substrate(), Normalize any accepted raw shape to an ORDERED list of 'provider/model' rungs;…, (ordered rungs, source) for the estate's sanctioned fallback substrate. [] = no…, _substrate_rungs()

### Community 107 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 109 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 110 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 111 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 112 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet.…, Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 113 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 114 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 115 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 116 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 117 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 118 - "_route_enforcement"
Cohesion: 0.33
Nodes (6): _confidence_substitute(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #116: declared-fallback branch of the #25 gate (R6: same path, not a parallel…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 121 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 122 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 123 - "test_tool_call_text_6st.py"
Cohesion: 0.27
Nodes (3): est-6st - a reply that IS serialized tool-call markup must never coerce. Field…, _NoRedirect, Credentials must NEVER ride a redirect (NEW blocker): urlopen's default handler…

### Community 124 - "_dead_session_harvest"
Cohesion: 0.33
Nodes (6): _banked_work(), _clean_capture(), _dead_session_harvest(), Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —…, The #102 harvest preamble for a re-drive whose prior session persisted NO…

### Community 125 - "_wake_identity"
Cohesion: 0.33
Nodes (6): Durable amendment generation: how many graph.amended events the run's own…, The run's ALREADY-COMMITTED failed-node set straight from the node records…, THE transition-instance discriminant (B3 law): a string that is IDENTICAL…, _wake_identity(), _wake_resolved_failed(), _wake_rev()

### Community 126 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 127 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 128 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 129 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 130 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 131 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 135 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **323 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+318 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1263 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `Changelog`, `act_wait`, `DirectiveBody`, `GraphView`, `build_inputs`, `__init__.py`, `node_rec`, `jload`, `GateActions`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `useValue()` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `label()` connect `NodePanel` to `plugin.js`, `.meta`, `ref_node_fs`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _323 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_fanout_item_goal.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `run_child` be split into smaller, more focused modules?**
  _Cohesion score 0.04934687953555878 - nodes in this community are weakly interconnected._