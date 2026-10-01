# Graph Report - tree  (2026-10-01)

## Corpus Check
- 189 files · ~258,132 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2066 nodes · 4198 edges · 133 communities (101 shown, 32 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 262 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- pathlib
- run_child
- json
- _Importer
- shutil
- plugin_api.py
- jload
- test_preflight_liveness_152be7f7.py
- sys
- _Exporter
- .meta
- test_fanout_expand.mjs
- wf_dialect.py
- __init__.py
- time
- wf.py
- efp
- test_11_ui_imports.mjs
- importlib_util
- loop
- run_agent_node
- DoorLib50
- test_v5_fixes.py
- test_fanout_item_goal.py
- subprocess
- test_silent_death_reaper_8.py
- os
- act_run
- _ping_route_once
- ref_node_fs
- lane_recover.py
- 11-golden-solo.py
- wfcommon.py
- test_live_truth_ui.mjs
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- validate_graph_errors
- CurrentAttemptMetrics
- _create_run
- test_register_surface.mjs
- Changelog
- __init__.py
- act_save
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- _SV
- AGENTS.md
- amend
- SKILL.md
- Changelog
- settings_runs_root
- LiveTruth
- test_node_panel.mjs
- _stamp_served
- 4. Contribute
- Disclosure verification — clause-by-clause evidence
- Run operations and read model
- test_lane_hygiene_preamble_8edcc9bf.py
- DialectRefusal
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- hermes_home
- test_orphan_adopt_790c6ad.py
- act_amend
- Contributing to hermes-workflows
- ref_node_url
- pack.py
- _stamp_served
- 1.0.2 — 2026-09-26 — the run watches itself
- _fake_parse_retry_after
- ProvenanceCounters
- make_public.py
- test
- test_sprint101w2_B2-retry.py
- _expand_config_value
- jload
- native_engine
- run_state
- dep_satisfied
- act_inbox
- install
- suite.py
- CoreFaithfulCtx
- test_prompt_workdir.py
- test_status_next.py
- test_steer_live_40.py
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- journaled_calls
- test_safe_root_workdir.py
- date-now.js
- Claim
- test_model_law_dad50be0.py
- test_review_fixes.py
- test_suite_admission_17.py
- _expand_config_values
- test_sprint101_D-surface.py
- test_validator_caps.py
- _defaults_errors
- manifest.json
- apply_patch
- sequential-awaits.js
- static-parallel.js
- two-stage-pipeline.js
- FakeProcess
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
1. `jload()` - 37 edges
2. `efp()` - 37 edges
3. `run_child()` - 33 edges
4. `DoorLib50` - 27 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
7. `loop()` - 24 edges
8. `run_state()` - 23 edges
9. `act_run()` - 22 edges
10. `log()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py

## Import Cycles
- None detected.

## Communities (133 total, 32 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (99): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+91 more)

### Community 1 - "pathlib"
Cohesion: 0.06
Nodes (20): atexit, importlib, pathlib, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, End-to-end test of the `workflow` tool door against fake hermes., The child launcher is operator-controlled, never a tool argument., FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Runner + children must inherit the OWNER's resolved profile home. Host fact… (+12 more)

### Community 2 - "run_child"
Cohesion: 0.06
Nodes (47): What the plugin gains, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+39 more)

### Community 3 - "json"
Cohesion: 0.06
Nodes (25): json, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source. (+17 more)

### Community 4 - "_Importer"
Cohesion: 0.12
Nodes (18): fields(), _control_kw(), _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated… (+10 more)

### Community 5 - "shutil"
Cohesion: 0.05
Nodes (8): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 6 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 7 - "jload"
Cohesion: 0.09
Nodes (34): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_state() (+26 more)

### Community 8 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (28): dict, author(), commit_run(), Ctx, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check(), contract() (+20 more)

### Community 9 - "sys"
Cohesion: 0.07
Nodes (17): glob, hashlib, hermes_constants, re, sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-… (+9 more)

### Community 10 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 11 - ".meta"
Cohesion: 0.09
Nodes (31): label(), 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block (+23 more)

### Community 12 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 13 - "wf_dialect.py"
Cohesion: 0.07
Nodes (28): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _line(), _main() (+20 more)

### Community 14 - "__init__.py"
Cohesion: 0.10
Nodes (31): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), difflib, _alias_provider_pair(), handle(), _lane_key_error(), _last_event_ts(), _model_policy_error(), model_preflight() (+23 more)

### Community 15 - "time"
Cohesion: 0.07
Nodes (11): plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final… (+3 more)

### Community 16 - "wf.py"
Cohesion: 0.09
Nodes (29): concurrent_futures, build_inputs(), drain_inbox(), extract_json(), _inputs_block(), last_balanced_object(), _match_object(), _quota_cache_path() (+21 more)

### Community 17 - "efp"
Cohesion: 0.10
Nodes (30): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes() (+22 more)

### Community 18 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 19 - "importlib_util"
Cohesion: 0.07
Nodes (10): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, 4052d57719653b1a: atomic library replay binding, no real runner. (+2 more)

### Community 20 - "loop"
Cohesion: 0.13
Nodes (27): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), _fail_precondition(), finalize(), log(), main() (+19 more)

### Community 21 - "run_agent_node"
Cohesion: 0.09
Nodes (26): 1.0.17 — 2026-09-28, _bounded_retry(), _dangling_placeholders(), fmt_goal(), _lane_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+18 more)

### Community 23 - "test_v5_fixes.py"
Cohesion: 0.07
Nodes (8): Ctx, Deterministic regressions for explicit workflow provider/model routing., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 24 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 25 - "subprocess"
Cohesion: 0.10
Nodes (15): copy, subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Engine branch contracts, exercised by the actual runner and fake CLI (no…, engine_case() (+7 more)

### Community 26 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 27 - "os"
Cohesion: 0.09
Nodes (7): os, Identical solo child wrapper for both tag and candidate; records env key sets.…, Authoring door regressions; all state stays in this worktree, no…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, Library verbs + /wf command: save (from run_id / inline), library list, run…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…

### Community 28 - "act_run"
Cohesion: 0.12
Nodes (22): act_library(), act_run(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), _lib_rel_name() (+14 more)

### Community 29 - "_ping_route_once"
Cohesion: 0.10
Nodes (21): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+13 more)

### Community 30 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 31 - "lane_recover.py"
Cohesion: 0.16
Nodes (20): Bail, find_session(), _hermes_home(), main(), open_ro(), profile_db(), Exception, The sessions row for a child key. `skey` may already carry `#a<n>`; a bare key… (+12 more)

### Community 32 - "11-golden-solo.py"
Cohesion: 0.11
Nodes (13): agent_reasoning_effort, contextlib, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Current-attempt heartbeat with real fake child identity; no provider access. (+5 more)

### Community 33 - "wfcommon.py"
Cohesion: 0.10
Nodes (19): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), precondition_facts(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE… (+11 more)

### Community 34 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 35 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 36 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 37 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 38 - "validate_graph_errors"
Cohesion: 0.12
Nodes (17): rerr(), _v(), grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this… (+9 more)

### Community 40 - "_create_run"
Cohesion: 0.12
Nodes (18): 1. Detached runner, _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+10 more)

### Community 41 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 42 - "Changelog"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 43 - "__init__.py"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 44 - "act_save"
Cohesion: 0.13
Nodes (16): act_save(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 45 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 46 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 49 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 50 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 51 - "_SV"
Cohesion: 0.14
Nodes (9): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not() (+1 more)

### Community 52 - "AGENTS.md"
Cohesion: 0.15
Nodes (11): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.3 (+3 more)

### Community 53 - "amend"
Cohesion: 0.13
Nodes (15): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, 1.0.1 — 2026-09-25, Deaths become outcomes (+7 more)

### Community 54 - "SKILL.md"
Cohesion: 0.14
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 55 - "Changelog"
Cohesion: 0.13
Nodes (15): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+7 more)

### Community 56 - "settings_runs_root"
Cohesion: 0.15
Nodes (14): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), _nested(), _no_unresolved_ref(), owner_setting(), A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives…, A surviving `${...}` after expansion means the referenced var is unset (or a…, One owner-settings read: the door's plugin ctx when it has one (its answer is… (+6 more)

### Community 58 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 59 - "_stamp_served"
Cohesion: 0.15
Nodes (15): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+7 more)

### Community 60 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 61 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.14
Nodes (12): 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation) (+4 more)

### Community 62 - "Run operations and read model"
Cohesion: 0.15
Nodes (14): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get, Lanes: in-flight dedupe for pollers (+6 more)

### Community 63 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.22
Nodes (12): check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file., step() (+4 more)

### Community 64 - "DialectRefusal"
Cohesion: 0.18
Nodes (8): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 65 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 66 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 67 - "1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance"
Cohesion: 0.17
Nodes (12): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, find_run(), launch_runs_root(), node_child_home(), node_child_metrics(), profile_home(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as… (+4 more)

### Community 69 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 70 - "hermes_home"
Cohesion: 0.18
Nodes (11): hermes_home(), hermes_root(), launcher_profile(), profile_errors(), profiles_root(), Read model.workflows_forbidden_models on the child seat, including bare CLI…, The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a…, Launcher identity — NEVER from a graph/run arg. Ranked (#41): 1. the process's… (+3 more)

### Community 71 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 72 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+3 more)

### Community 73 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 74 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 75 - "pack.py"
Cohesion: 0.29
Nodes (9): Nodes and data, build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), zipfile (+1 more)

### Community 76 - "_stamp_served"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 78 - "_fake_parse_retry_after"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 79 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 80 - "make_public.py"
Cohesion: 0.28
Nodes (8): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.…

### Community 81 - "test"
Cohesion: 0.31
Nodes (8): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, _verify_spawn_rec()

### Community 82 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 83 - "_expand_config_value"
Cohesion: 0.22
Nodes (9): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain… (+1 more)

### Community 84 - "jload"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 85 - "native_engine"
Cohesion: 0.25
Nodes (6): argv(), check(), native_engine(), spawn(), probe_transitions(), state()

### Community 87 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 88 - "act_inbox"
Cohesion: 0.29
Nodes (7): act_inbox(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 89 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 90 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 91 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 92 - "test_prompt_workdir.py"
Cohesion: 0.52
Nodes (6): check(), home_and_fakes(), main(), mk_run(), L7 — A1 durable prompt file + A4 durable child work dir. A1: the prompt as sent…, step()

### Community 93 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 94 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 95 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 96 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 97 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 98 - "journaled_calls"
Cohesion: 0.33
Nodes (6): journaled_calls(), The error text carried by a role='tool' result row, or None when the call…, {tool_call_id: content} for every role='tool' row of the session — the result…, Ordered [{index, tool, args, call_id, msg_id, error}] of write_file/patch…, result_error(), tool_results()

### Community 99 - "test_safe_root_workdir.py"
Cohesion: 0.53
Nodes (5): stat, check(), main(), fb 625a3241cfcc9dee — the child's advertised durable work dir is writable under…, run_graph()

### Community 102 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 104 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 105 - "_expand_config_values"
Cohesion: 0.33
Nodes (6): _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings(), _yaml_load()

### Community 106 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 107 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 108 - "_defaults_errors"
Cohesion: 0.40
Nodes (4): _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 109 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 110 - "apply_patch"
Cohesion: 0.50
Nodes (4): apply_patch(), Whitespace-flexible regex for a patch anchor: every INNER run of whitespace…, (new_text, how) — how in {'exact', 'fuzzy', 'ambiguous:<n>', None}. Exact…, _ws_flex()

### Community 111 - "sequential-awaits.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1040 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `jload`, `__init__.py`, `wf.py`, `test`, `loop`, `Changelog`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `label()` connect `.meta` to `plugin.js`, `ref_node_fs`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.054343434343434346 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `run_child` be split into smaller, more focused modules?**
  _Cohesion score 0.055272108843537414 - nodes in this community are weakly interconnected._