# Graph Report - tree  (2026-10-02)

## Corpus Check
- 192 files · ~261,841 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2109 nodes · 4283 edges · 139 communities (106 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- importlib_util
- wfcommon.py
- run_child
- jload
- sys
- lane_recover.py
- efp
- test_lane_hygiene_preamble_8edcc9bf.py
- shutil
- test_fanout_expand.mjs
- _Exporter
- ref_node_fs
- plugin_api.py
- subprocess
- os
- test_11_ui_imports.mjs
- json
- DoorLib50
- pathlib
- test_fanout_item_goal.py
- _Importer
- 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail
- wf_dialect.py
- act_run
- _ping_route_once
- __init__.py
- test_live_truth_ui.mjs
- test_daemonize_8.py
- Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet
- .meta
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- test_require_route_25.py
- CurrentAttemptMetrics
- test_cross_container_liveness_91b9a3de.py
- test_register_surface.mjs
- test_validate_0923.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- test_silent_death_reaper_8.py
- EngineNextCut
- LiveTruth
- test_machine_watch_94.py
- test_node_panel.mjs
- .agent_args
- validate_graph_errors
- test_sprint101_A-door.py
- test_orphan_adopt_790c6ad.py
- TeamIntegration
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- Changelog
- _create_run
- act_save
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- test_route_efforts_b3c98b2a.py
- act_amend
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- Contributing to hermes-workflows
- graph_check.py
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- ProvenanceCounters
- _parse_literal
- Run operations and read model
- test_sprint101w2_B2-retry.py
- DialectRefusal
- _SV
- AGENTS.md — front door for agents
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_engine.py
- test_resume_fresh_session_102.py
- test_routing_routes.py
- test_run_dry_run.py
- active_child
- model_preflight
- Disclosure verification — clause-by-clause evidence
- install
- SKILL.md
- suite.py
- node_facts
- CoreFaithfulCtx
- test_incident_response_93.py
- test_lane_gate_64c6772b.py
- test_review_fixes.py
- test_status_next.py
- test_steer_live_40.py
- AGENTS.md
- 3. Operate
- 4. Contribute
- 1.0.2 — 2026-09-26 — the run watches itself
- dep_satisfied
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- _spawn_runner
- Manual installation — Hermes Workflows 1.1.3
- Hermes Workflows
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- Claim
- test_tiers.py
- 1.0.1 — 2026-09-25
- Patched core: typed turn-cap deaths (optional)
- 11-claim-wrapper.py
- test_papercuts_0922.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- _AdoptedHandle
- last_balanced_object
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
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` --references--> `useValue()`  [INFERRED]
  CHANGELOG.md → tests/test_fanout_expand.mjs
- `4. What this PR does not decide` --references--> `agent()`  [INFERRED]
  references/dialect.md → tests/test_prune_0923.py

## Import Cycles
- None detected.

## Communities (139 total, 33 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (98): ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups(), ctxRest() (+90 more)

### Community 1 - "wf.py"
Cohesion: 0.04
Nodes (75): concurrent_futures, _attempt_api_calls(), _banked_work(), _bounded_retry(), build_inputs(), _clean_capture(), _dangling_placeholders(), _dead_session_harvest() (+67 more)

### Community 2 - "importlib_util"
Cohesion: 0.06
Nodes (32): importlib_util, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., F3 boundary/claim integration: real door processes + kernel flock; no hook in… (+24 more)

### Community 3 - "wfcommon.py"
Cohesion: 0.05
Nodes (58): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, blocked_by(), current_attempt(), effective_runs_root(), _env_ref_lookup(), _env_ref_var_name(), _expand_config_value() (+50 more)

### Community 4 - "run_child"
Cohesion: 0.06
Nodes (51): What the plugin gains, _adopt_child(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), extract_json() (+43 more)

### Community 5 - "jload"
Cohesion: 0.08
Nodes (44): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), acquire_lock(), emit() (+36 more)

### Community 6 - "sys"
Cohesion: 0.06
Nodes (12): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Integrated read-model and parser-valid card dedup checks., Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;… (+4 more)

### Community 7 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 8 - "efp"
Cohesion: 0.09
Nodes (36): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, What you get, 2. The mapping table, File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Per-run concurrency (optional) (+28 more)

### Community 9 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.09
Nodes (30): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+22 more)

### Community 10 - "shutil"
Cohesion: 0.06
Nodes (11): shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked… (+3 more)

### Community 11 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (29): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+21 more)

### Community 12 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 13 - "ref_node_fs"
Cohesion: 0.08
Nodes (22): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource (+14 more)

### Community 14 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 15 - "subprocess"
Cohesion: 0.06
Nodes (11): subprocess, Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Ledger e68544a37be37657 (fb-fix-2dd8de73): a harvest-on-death `partial` must…, make_root() (+3 more)

### Community 16 - "os"
Cohesion: 0.08
Nodes (9): os, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, 45b038: cron's core-less interpreter must still bake a proved pinned route. The… (+1 more)

### Community 17 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 18 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 20 - "pathlib"
Cohesion: 0.09
Nodes (13): copy, hashlib, pathlib, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:… (+5 more)

### Community 21 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 22 - "_Importer"
Cohesion: 0.16
Nodes (10): _control_kw(), _forbidden_label(), _Importer, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the… (+2 more)

### Community 23 - "1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail"
Cohesion: 0.10
Nodes (24): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state() (+16 more)

### Community 24 - "wf_dialect.py"
Cohesion: 0.09
Nodes (22): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _line() (+14 more)

### Community 25 - "act_run"
Cohesion: 0.11
Nodes (23): act_library(), act_run(), _concurrency_bake(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+15 more)

### Community 26 - "_ping_route_once"
Cohesion: 0.10
Nodes (21): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+13 more)

### Community 27 - "__init__.py"
Cohesion: 0.14
Nodes (20): difflib, act_inbox(), act_steer(), act_submit(), handle(), _model_names_valid(), _owner_settings_error(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The… (+12 more)

### Community 28 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 29 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 30 - "Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet"
Cohesion: 0.13
Nodes (19): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 3.1 `agent(prompt, options?)`, 3.2 `parallel(tasks)`, 3.3 `pipeline(items, stage1, stage2, ...)`, 3.4 `phase(title)`, 3.5 `log(message)` (+11 more)

### Community 31 - ".meta"
Cohesion: 0.12
Nodes (16): 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 1. Shape of each side in one screen, 3. The importable subset, stated once, 4. What this PR does not decide, Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON) (+8 more)

### Community 32 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 33 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 34 - "test_require_route_25.py"
Cohesion: 0.11
Nodes (11): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+3 more)

### Community 36 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.14
Nodes (11): contextlib, io, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, hold() (+3 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 38 - "test_validate_0923.py"
Cohesion: 0.12
Nodes (9): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, Exception, #71 regression pin: the shelf is a live production surface — no test may write…, SavedGolden, mkrun() (+1 more)

### Community 39 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 40 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 41 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+8 more)

### Community 42 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 43 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 45 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 46 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 47 - "test_silent_death_reaper_8.py"
Cohesion: 0.13
Nodes (5): fcntl, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 50 - "test_machine_watch_94.py"
Cohesion: 0.16
Nodes (8): argv(), check(), native_engine(), spawn(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling., Door-transport guard: run_context must never silently route a map to seed.…, state()

### Community 51 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 52 - ".agent_args"
Cohesion: 0.25
Nodes (7): _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the…, _skip_ws(), _split_top()

### Community 53 - "validate_graph_errors"
Cohesion: 0.15
Nodes (13): grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), _tok_when() (+5 more)

### Community 54 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 55 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 56 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 57 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 58 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 59 - "Changelog"
Cohesion: 0.17
Nodes (12): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+4 more)

### Community 60 - "_create_run"
Cohesion: 0.20
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+4 more)

### Community 61 - "act_save"
Cohesion: 0.17
Nodes (12): act_save(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the… (+4 more)

### Community 63 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 64 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, behavior=None restores the non-core host (import raises); dict stubs the…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is… (+2 more)

### Community 65 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 66 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+3 more)

### Community 67 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 69 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 70 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 71 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 72 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 73 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 74 - "_parse_literal"
Cohesion: 0.20
Nodes (8): _match_close(), _parse_literal(), Offset of the bracket closing the one at `open_at`., A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, _Ref, _Tpl, _unescape()

### Community 75 - "Run operations and read model"
Cohesion: 0.25
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit), submit()

### Community 76 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 77 - "DialectRefusal"
Cohesion: 0.28
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 79 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 80 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.25
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 81 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 83 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 85 - "active_child"
Cohesion: 0.25
Nodes (8): active_child(), _active_spawn(), _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, All verified uncommitted child identities, never historical DB liveness., Per-item entry point to the verification law (790c6ad): the runner's fan-out…, Compatibility: first verified spawn for existing blocked-by consumers., _verify_spawn_rec()

### Community 86 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 87 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.29
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 88 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 89 - "SKILL.md"
Cohesion: 0.33
Nodes (3): Contributor checks (not ordinary user setup), Smallest working graph, Workflow authoring (1.1.3)

### Community 90 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 91 - "node_facts"
Cohesion: 0.29
Nodes (7): Run and handoff, node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 92 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 93 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 94 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 96 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 97 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 99 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 100 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 101 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 102 - "dep_satisfied"
Cohesion: 0.47
Nodes (5): 1.1.3 — 2026-10-01, deps_ok(), dep_satisfied(), After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 103 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (5): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, Meta

### Community 104 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 105 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 106 - "_spawn_runner"
Cohesion: 0.33
Nodes (6): One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law…, Direct spawn for no-fork platforms / refused fork: here the Popen'd child IS…, _ready_pid(), _spawn_runner(), _spawn_runner_legacy()

### Community 107 - "Manual installation — Hermes Workflows 1.1.3"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.3, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 108 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 109 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 113 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 114 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.40
Nodes (5): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds

### Community 115 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 117 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 118 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 119 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 120 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 124 - "last_balanced_object"
Cohesion: 0.50
Nodes (4): last_balanced_object(), _match_object(), Index of the '}' closing the '{' at i (string-aware), or -1 if unbalanced., Sprint101 #9: the LAST top-level balanced {...} in stdout that json.loads…

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1064 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` to `plugin.js`, `wf.py`, `jload`, `_resolve_models`, `test_fanout_expand.mjs`, `active_child`, `Changelog`?**
  _High betweenness centrality (0.182) - this node is a cross-community bridge._
- **Why does `useValue()` connect `test_fanout_expand.mjs` to `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `efp`, `ref_node_fs`, `Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.054627911770768915 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04101161995898838 - nodes in this community are weakly interconnected._
- **Should `importlib_util` be split into smaller, more focused modules?**
  _Cohesion score 0.05654761904761905 - nodes in this community are weakly interconnected._