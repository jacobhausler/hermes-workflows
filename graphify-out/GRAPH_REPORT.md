# Graph Report - tree  (2026-10-02)

## Corpus Check
- 199 files · ~266,566 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2129 nodes · 4329 edges · 135 communities (103 shown, 32 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- sys
- json
- lane_recover.py
- loop
- time
- pathlib
- jload
- test_fanout_expand.mjs
- _Importer
- _Exporter
- __init__.py
- test_lane_hygiene_preamble_8edcc9bf.py
- wf_dialect.py
- plugin_api.py
- importlib_util
- efp
- test_11_ui_imports.mjs
- run_agent_node
- DoorLib50
- test_fanout_item_goal.py
- .meta
- act_run
- ref_node_fs
- Changelog
- test_live_truth_ui.mjs
- os
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- validate_graph_errors
- test_failures_0923.py
- CurrentAttemptMetrics
- test_cross_container_liveness_91b9a3de.py
- act_save
- _create_run
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- CardBackend
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- test_silent_death_reaper_8.py
- DialectRefusal
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- test_review_fixes.py
- SKILL.md
- 4. Contribute
- test_sprint101_A-door.py
- test_require_route_25.py
- Disclosure verification — clause-by-clause evidence
- _ping_route_once
- amend
- TeamIntegration
- test
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- test_route_efforts_b3c98b2a.py
- test_packaging.py
- Run operations and read model
- test_orphan_adopt_790c6ad.py
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- 3. The importable subset, stated once
- tempfile
- ref_node_url
- graph_check.py
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- ProvenanceCounters
- test_schema_enum_107.py
- act_amend
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- test_run_dry_run.py
- model_preflight
- dep_satisfied
- _spawn_runner
- _bind_run_context
- Claim
- suite.py
- js_import
- CoreFaithfulCtx
- test_incident_response_93.py
- test_lane_gate_64c6772b.py
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- Manual installation — Hermes Workflows 1.1.3
- Hermes Workflows
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- Claim
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tiers.py
- _dead_session_harvest
- native_engine
- test_papercuts_0922.py
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
1. `efp()` - 38 edges
2. `jload()` - 37 edges
3. `run_child()` - 33 edges
4. `DoorLib50` - 27 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
7. `loop()` - 25 edges
8. `act_run()` - 23 edges
9. `main()` - 23 edges
10. `run_state()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `4. What this PR does not decide` --references--> `agent()`  [INFERRED]
  references/dialect.md → tests/test_prune_0923.py
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

## Communities (135 total, 32 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (100): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+92 more)

### Community 1 - "wf.py"
Cohesion: 0.04
Nodes (90): concurrent_futures, _adopt_child(), _AdoptedHandle, build_inputs(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output() (+82 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.04
Nodes (69): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, child_metrics(), current_attempt(), effective_runs_root(), _env_ref_lookup(), _env_ref_var_name() (+61 more)

### Community 3 - "sys"
Cohesion: 0.04
Nodes (21): shutil, subprocess, sys, CrashResume, Suite hook for the standalone 20-cycle crash/resume harness., GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry… (+13 more)

### Community 4 - "json"
Cohesion: 0.06
Nodes (33): hashlib, json, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), main() (+25 more)

### Community 5 - "lane_recover.py"
Cohesion: 0.08
Nodes (40): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+32 more)

### Community 6 - "loop"
Cohesion: 0.09
Nodes (36): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), _fail_precondition(), finalize(), log(), main() (+28 more)

### Community 7 - "time"
Cohesion: 0.06
Nodes (10): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+2 more)

### Community 8 - "pathlib"
Cohesion: 0.07
Nodes (17): glob, hermes_constants, pathlib, plugin_api, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+9 more)

### Community 9 - "jload"
Cohesion: 0.10
Nodes (32): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_state() (+24 more)

### Community 10 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 11 - "_Importer"
Cohesion: 0.14
Nodes (12): _control_kw(), _Importer, _ordered(), _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., A literal label -> str; a template label -> its literal spine (for ids). (+4 more)

### Community 12 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 13 - "__init__.py"
Cohesion: 0.10
Nodes (31): difflib, _alias_provider_pair(), handle(), _lane_key_error(), _last_event_ts(), _model_policy_error(), model_tiers(), _output_pointer() (+23 more)

### Community 14 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (27): Nodes and data, build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat (+19 more)

### Community 15 - "wf_dialect.py"
Cohesion: 0.08
Nodes (26): _const_name(), _fmt_goal(), _forbidden_label(), _has_tpl(), _mask(), _match_close(), node_check(), _ordered_item() (+18 more)

### Community 16 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 17 - "importlib_util"
Cohesion: 0.07
Nodes (11): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes. (+3 more)

### Community 18 - "efp"
Cohesion: 0.11
Nodes (29): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Per-run concurrency (optional), Staleness and replay, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example (+21 more)

### Community 19 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 20 - "run_agent_node"
Cohesion: 0.09
Nodes (28): _attempt_api_calls(), _bounded_retry(), _dangling_placeholders(), _lane_gate(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+20 more)

### Community 22 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 23 - ".meta"
Cohesion: 0.12
Nodes (23): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+15 more)

### Community 24 - "act_run"
Cohesion: 0.11
Nodes (23): act_library(), act_run(), _concurrency_bake(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+15 more)

### Community 25 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 26 - "Changelog"
Cohesion: 0.10
Nodes (21): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+13 more)

### Community 27 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 28 - "os"
Cohesion: 0.12
Nodes (10): copy, os, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Engine branch contracts, exercised by the actual runner and fake CLI (no…, argv(), check(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling. (+2 more)

### Community 29 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 30 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 31 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 32 - "validate_graph_errors"
Cohesion: 0.11
Nodes (17): _defaults_errors(), grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+9 more)

### Community 33 - "test_failures_0923.py"
Cohesion: 0.11
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, 45b038: cron's core-less interpreter must still bake a proved pinned route. The…

### Community 35 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.14
Nodes (11): contextlib, io, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, hold() (+3 more)

### Community 36 - "act_save"
Cohesion: 0.12
Nodes (18): act_save(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Return graph-level and node-level defects together, before any write/spawn. (+10 more)

### Community 37 - "_create_run"
Cohesion: 0.12
Nodes (17): _card(), _create_run(), _hermes_bin(), _identity_stamps(), _liveness_hint_suffix(), _ping_subprocess(), Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >… (+9 more)

### Community 38 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 39 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 40 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 41 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 42 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 44 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 45 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 46 - "test_silent_death_reaper_8.py"
Cohesion: 0.13
Nodes (5): fcntl, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 47 - "DialectRefusal"
Cohesion: 0.15
Nodes (9): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _line(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.… (+1 more)

### Community 50 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 51 - "test_review_fixes.py"
Cohesion: 0.12
Nodes (3): #102 bounded re-drive must not pretend-resume a DEAD (empty) session. Measured…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…

### Community 52 - "SKILL.md"
Cohesion: 0.19
Nodes (5): Node budgets, Contributor checks (not ordinary user setup), Run and handoff, Smallest working graph, Workflow authoring (1.1.3)

### Community 53 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 54 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 55 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 56 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.14
Nodes (12): 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation) (+4 more)

### Community 57 - "_ping_route_once"
Cohesion: 0.15
Nodes (14): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), One auxiliary ping on the pinned (provider, model) route — explicit provider…, Weak-law recovery probe for a PROVIDER-LESS quota entry (A5): the same-route… (+6 more)

### Community 58 - "amend"
Cohesion: 0.15
Nodes (13): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, 1.0.1 — 2026-09-25, Deaths become outcomes (+5 more)

### Community 59 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 60 - "test"
Cohesion: 0.19
Nodes (12): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), _active_spawn(), _active_spawns() (+4 more)

### Community 61 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 62 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 64 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 65 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, behavior=None restores the non-core host (import raises); dict stubs the…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is… (+2 more)

### Community 66 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 67 - "test_packaging.py"
Cohesion: 0.20
Nodes (7): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types, zipfile

### Community 68 - "Run operations and read model"
Cohesion: 0.22
Nodes (8): What you get, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit), submit()

### Community 69 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 70 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 72 - "3. The importable subset, stated once"
Cohesion: 0.20
Nodes (8): 1.0.17 — 2026-09-28, 1. Shape of each side in one screen, 3. The importable subset, stated once, 4. What this PR does not decide, Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON), fmt_goal(), apply_graph_defaults(), Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…

### Community 73 - "tempfile"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 74 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 75 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 76 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 77 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 78 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 79 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 80 - "act_amend"
Cohesion: 0.22
Nodes (9): act_amend(), _frozen_committed(), _profile_error(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, _require_route_effective() (+1 more)

### Community 81 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 82 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 83 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 85 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 86 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 87 - "_spawn_runner"
Cohesion: 0.29
Nodes (7): 1. Detached runner, One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law…, Direct spawn for no-fork platforms / refused fork: here the Popen'd child IS…, _ready_pid(), _spawn_runner(), _spawn_runner_legacy()

### Community 88 - "_bind_run_context"
Cohesion: 0.29
Nodes (7): act_inbox(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 89 - "Claim"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 90 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 91 - "js_import"
Cohesion: 0.29
Nodes (7): check(), refuses(), export_report(), js_import(), _main(), See module docstring. `node_check=False` skips the optional subprocess gate., {"ok": True, "js": str, "lossy": [{node, key, value}], "warnings": [...]} |…

### Community 92 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 93 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 94 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 97 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 98 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 99 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 100 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 101 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 102 - "Manual installation — Hermes Workflows 1.1.3"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.3, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 103 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 104 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 107 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 108 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 110 - "_dead_session_harvest"
Cohesion: 0.33
Nodes (6): _banked_work(), _clean_capture(), _dead_session_harvest(), Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —…, The #102 harvest preamble for a re-drive whose prior session persisted NO…

### Community 111 - "native_engine"
Cohesion: 0.40
Nodes (3): native_engine(), spawn(), state()

### Community 113 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 114 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 115 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 116 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1073 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `wf.py`, `loop`, `jload`, `__init__.py`, `Changelog`, `test`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `ref_node_fs`, `amend`, `.meta`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05405940594059406 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.03740065451145395 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.039240506329113925 - nodes in this community are weakly interconnected._