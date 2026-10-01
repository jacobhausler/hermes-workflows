# Graph Report - tree  (2026-10-01)

## Corpus Check
- 191 files · ~259,777 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2093 nodes · 4256 edges · 130 communities (100 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- subprocess
- sys
- run_agent_node
- lane_recover.py
- os
- loop
- tempfile
- jload
- test_fanout_expand.mjs
- _Exporter
- wf_test_isolation.py
- importlib_util
- plugin_api.py
- test_lane_hygiene_preamble_8edcc9bf.py
- validate_graph_errors
- __init__.py
- test_11_ui_imports.mjs
- DoorLib50
- wf_dialect.py
- test_fanout_item_goal.py
- _Importer
- test_v5_fixes.py
- act_run
- ref_node_fs
- efp
- .agent_args
- test_preflight_liveness_152be7f7.py
- test_live_truth_ui.mjs
- pathlib
- test_daemonize_8.py
- _create_run
- Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- CurrentAttemptMetrics
- act_save
- test_register_surface.mjs
- _ping_route_once
- test_silent_death_reaper_8.py
- Changelog
- __init__.py
- Changelog
- shutil
- _route_enforcement
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- EngineNextCut
- LiveTruth
- test_machine_watch_94.py
- test_node_panel.mjs
- _stamp_served
- test_require_route_25.py
- 11-golden-solo.py
- SKILL.md
- test_tiers.py
- test_cross_container_liveness_91b9a3de.py
- TeamIntegration
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- importlib
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- amend
- test_orphan_adopt_790c6ad.py
- act_status
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- Run operations and read model
- tempfile
- graph_check.py
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- test
- test_sprint101w2_B2-retry.py
- DialectRefusal
- _SV
- AGENTS.md — front door for agents
- dep_satisfied
- Disclosure verification — clause-by-clause evidence
- jload
- test_routing_routes.py
- run_state
- plugin-catalog: add `hermes-workflows` (community, automation)
- _bind_run_context
- Claim
- ref_node_assert
- suite.py
- CoreFaithfulCtx
- test_incident_response_93.py
- test_lane_gate_64c6772b.py
- test_steer_live_40.py
- AGENTS.md
- 3. Operate
- 4. Contribute
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- _spawn_runner
- Manual installation — Hermes Workflows 1.1.3
- Hermes Workflows
- DoorLane
- Claim
- test_model_law_dad50be0.py
- pipeline-length-template.js
- _route_enforcement
- sequential-awaits.js
- BlockedLegibility100
- _LADDER
- Integrated
- Run
- test_node_facts.py
- test_validate_0923.py
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
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` --references--> `useValue()`  [INFERRED]
  CHANGELOG.md → tests/test_fanout_expand.mjs
- `4. What this PR does not decide` --references--> `agent()`  [INFERRED]
  references/dialect.md → tests/test_prune_0923.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (130 total, 30 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (98): ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups(), ctxRest() (+90 more)

### Community 1 - "wf.py"
Cohesion: 0.05
Nodes (66): concurrent_futures, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+58 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.05
Nodes (60): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, current_attempt(), effective_runs_root(), _env_ref_lookup(), _env_ref_var_name(), _expand_config_value() (+52 more)

### Community 3 - "subprocess"
Cohesion: 0.04
Nodes (14): shutil, subprocess, Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).… (+6 more)

### Community 4 - "sys"
Cohesion: 0.07
Nodes (22): json, sys, Identical solo child wrapper for both tag and candidate; records env key sets.…, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Lane A preconditions: null and missing ancestor fields fail before Popen, then…, #100: run.blocked preserves its old verdict and adds causal context. Run: env… (+14 more)

### Community 5 - "run_agent_node"
Cohesion: 0.06
Nodes (42): 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 1. Shape of each side in one screen, 2. The mapping table, 3. The importable subset, stated once, 4. What this PR does not decide (+34 more)

### Community 6 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 7 - "os"
Cohesion: 0.07
Nodes (18): contextlib, glob, os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+10 more)

### Community 8 - "loop"
Cohesion: 0.08
Nodes (39): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), log() (+31 more)

### Community 9 - "tempfile"
Cohesion: 0.05
Nodes (16): tempfile, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), Authoring door regressions; all state stays in this worktree, no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, The child launcher is operator-controlled, never a tool argument., 45b038: cron's core-less interpreter must still bake a proved pinned route. The…, lock() (+8 more)

### Community 10 - "jload"
Cohesion: 0.09
Nodes (34): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, act_amend(), act_list(), act_release(), act_steer(), act_stop(), act_wait(), _respawn_throttled() (+26 more)

### Community 11 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (29): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+21 more)

### Community 12 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 13 - "wf_test_isolation.py"
Cohesion: 0.06
Nodes (10): End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn. (+2 more)

### Community 14 - "importlib_util"
Cohesion: 0.08
Nodes (18): ast, hashlib, importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source. (+10 more)

### Community 15 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 16 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 17 - "validate_graph_errors"
Cohesion: 0.08
Nodes (28): apply_graph_defaults(), _defaults_errors(), grammar_errors(), Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called… (+20 more)

### Community 18 - "__init__.py"
Cohesion: 0.11
Nodes (29): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), difflib, _alias_provider_pair(), handle(), _model_policy_error(), model_preflight(), model_tiers(), _nearest_effort() (+21 more)

### Community 19 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 21 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _line() (+16 more)

### Community 22 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 23 - "_Importer"
Cohesion: 0.16
Nodes (10): _control_kw(), _forbidden_label(), _Importer, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the… (+2 more)

### Community 24 - "test_v5_fixes.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 25 - "act_run"
Cohesion: 0.10
Nodes (25): act_library(), act_run(), _concurrency_bake(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+17 more)

### Community 26 - "ref_node_fs"
Cohesion: 0.10
Nodes (16): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+8 more)

### Community 27 - "efp"
Cohesion: 0.13
Nodes (24): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+16 more)

### Community 28 - ".agent_args"
Cohesion: 0.15
Nodes (13): _ordered(), _parse_literal(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the… (+5 more)

### Community 29 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 30 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 31 - "pathlib"
Cohesion: 0.12
Nodes (9): copy, pathlib, re, Regression: launch a run in the tool's session; the payload carries a parser-…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Engine branch contracts, exercised by the actual runner and fake CLI (no…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-…, Portable authoring skill contract; no provider or live-home dependencies. (+1 more)

### Community 32 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 33 - "_create_run"
Cohesion: 0.11
Nodes (19): _card(), _create_run(), _hermes_bin(), _identity_stamps(), _lane_state(), _last_event_ts(), _liveness_hint_suffix(), _ping_subprocess() (+11 more)

### Community 34 - "Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet"
Cohesion: 0.13
Nodes (19): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 3.1 `agent(prompt, options?)`, 3.2 `parallel(tasks)`, 3.3 `pipeline(items, stage1, stage2, ...)`, 3.4 `phase(title)`, 3.5 `log(message)` (+11 more)

### Community 35 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 36 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 38 - "act_save"
Cohesion: 0.12
Nodes (18): act_save(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Return graph-level and node-level defects together, before any write/spawn. (+10 more)

### Community 39 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 40 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), One auxiliary ping on the pinned (provider, model) route — explicit provider… (+9 more)

### Community 41 - "test_silent_death_reaper_8.py"
Cohesion: 0.12
Nodes (8): signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), Lane E: cross-lane executable integration fixtures; no production…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner…

### Community 42 - "Changelog"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 43 - "__init__.py"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 44 - "Changelog"
Cohesion: 0.12
Nodes (16): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+8 more)

### Community 45 - "shutil"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 46 - "_route_enforcement"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 48 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 49 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 52 - "test_machine_watch_94.py"
Cohesion: 0.16
Nodes (8): argv(), check(), native_engine(), spawn(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling., Door-transport guard: run_context must never silently route a map to seed.…, state()

### Community 53 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 54 - "_stamp_served"
Cohesion: 0.15
Nodes (15): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+7 more)

### Community 55 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 56 - "11-golden-solo.py"
Cohesion: 0.19
Nodes (9): hermes_constants, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Exception, #71 regression pin: the shelf is a live production surface — no test may write… (+1 more)

### Community 57 - "SKILL.md"
Cohesion: 0.15
Nodes (9): Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for), Run and handoff, Smallest working graph (+1 more)

### Community 58 - "test_tiers.py"
Cohesion: 0.15
Nodes (5): atexit, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 59 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 60 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 61 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 62 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 63 - "importlib"
Cohesion: 0.17
Nodes (5): importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v()

### Community 65 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 66 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 67 - "amend"
Cohesion: 0.20
Nodes (11): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, Gates and branches, Graph grammar and authoring boundaries, Nodes and data (+3 more)

### Community 68 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 69 - "act_status"
Cohesion: 0.18
Nodes (10): act_status(), _lane_key_error(), _output_pointer(), Compact stand-in for a committed node output: enough to DECIDE to pay for…, node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.… (+2 more)

### Community 70 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 72 - "Run operations and read model"
Cohesion: 0.22
Nodes (8): What you get, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit), submit()

### Community 73 - "tempfile"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 74 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 75 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 76 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 77 - "test"
Cohesion: 0.31
Nodes (8): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, _verify_spawn_rec()

### Community 78 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 79 - "DialectRefusal"
Cohesion: 0.28
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 81 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 82 - "dep_satisfied"
Cohesion: 0.32
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 83 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.25
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 84 - "jload"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 85 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 87 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 88 - "_bind_run_context"
Cohesion: 0.29
Nodes (7): act_inbox(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 89 - "Claim"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 90 - "ref_node_assert"
Cohesion: 0.29
Nodes (6): ref_node_assert, [first, second], header, match, root, source

### Community 91 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 92 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 93 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 94 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 95 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 97 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 98 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 99 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 100 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 101 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 102 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 103 - "_spawn_runner"
Cohesion: 0.33
Nodes (6): One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law…, Direct spawn for no-fork platforms / refused fork: here the Popen'd child IS…, _ready_pid(), _spawn_runner(), _spawn_runner_legacy()

### Community 104 - "Manual installation — Hermes Workflows 1.1.3"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.3, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 105 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 108 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 109 - "pipeline-length-template.js"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 110 - "_route_enforcement"
Cohesion: 0.50
Nodes (4): #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 111 - "sequential-awaits.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1053 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `jload` to `plugin.js`, `run_agent_node`, `loop`, `test_fanout_expand.mjs`, `Changelog`, `test`, `__init__.py`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `useValue()` connect `test_fanout_expand.mjs` to `jload`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet`, `ref_node_fs`, `run_agent_node`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.054627911770768915 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05285592497868713 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.049107142857142856 - nodes in this community are weakly interconnected._