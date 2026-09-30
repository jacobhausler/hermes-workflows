# Graph Report - tree  (2026-09-30)

## Corpus Check
- 172 files · ~222,727 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1866 nodes · 3766 edges · 128 communities (99 shown, 29 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 245 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- os
- subprocess
- wf.py
- importlib_util
- lane_recover.py
- _Importer
- test_fanout_expand.mjs
- _Exporter
- .meta
- hermes_home
- test_lane_hygiene_preamble_8edcc9bf.py
- pathlib
- jload
- test_11_ui_imports.mjs
- wf_dialect.py
- test_require_route_25.py
- test_preflight_liveness_152be7f7.py
- act_run
- run_state
- test_fanout_item_goal.py
- sys
- graph_check.py
- run_agent_node
- wfcommon.py
- _adopt_child
- json
- ref_node_fs
- test_failures_0923.py
- __init__.py
- test_live_truth_ui.mjs
- test_pill_rail_expand.mjs
- 3. Operate
- CurrentAttemptMetrics
- EngineNextCut
- plugin_api.py
- _ping_route_once
- test_register_surface.mjs
- efp
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- test_route_efforts_b3c98b2a.py
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- amend
- Disclosure verification — clause-by-clause evidence
- owner_setting
- test_node_panel.mjs
- _resolve_models
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- validate_graph_errors
- test_pill_rail.mjs
- AGENTS.md
- SKILL.md
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- when_true
- Changelog
- _create_run
- DialectRefusal
- test_amend_rebake_034849a2.py
- test_node_facts.py
- Contributing to hermes-workflows
- ref_node_path
- Portable workflow files (publish = put the file on git)
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- test_packaging.py
- ProvenanceCounters
- .run
- test_sprint101w2_B2-retry.py
- _SV
- _bind_run_context
- Run operations and read model
- test_engine.py
- test_routing_routes.py
- _expand_config_values
- model_preflight
- suite.py
- test
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- build_inputs
- _env_ref_var_name
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Manual installation — Hermes Workflows 1.1.1
- DoorLane
- test_run_context_seed_guard.py
- test_suite_admission_17.py
- test_tier_report_0924.py
- _bounded_retry
- 1.0.1 — 2026-09-25
- node_facts
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- _defaults_errors
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- acquire_lock
- _LADDER
- Integrated
- Run
- release_gate
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
1. `efp()` - 37 edges
2. `jload()` - 36 edges
3. `run_child()` - 33 edges
4. `_Importer` - 27 edges
5. `_Exporter` - 26 edges
6. `loop()` - 23 edges
7. `run_state()` - 23 edges
8. `log()` - 22 edges
9. `_adopt_child()` - 22 edges
10. `main()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (128 total, 29 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "os"
Cohesion: 0.05
Nodes (19): os, shutil, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled… (+11 more)

### Community 2 - "subprocess"
Cohesion: 0.06
Nodes (16): subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Integrated read-model and parser-valid card dedup checks. (+8 more)

### Community 3 - "wf.py"
Cohesion: 0.07
Nodes (44): concurrent_futures, _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), extract_json(), _first_message_s(), _is_build_lane() (+36 more)

### Community 4 - "importlib_util"
Cohesion: 0.07
Nodes (24): importlib_util, signal, tempfile, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, main() (+16 more)

### Community 5 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 6 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 7 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 8 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 9 - ".meta"
Cohesion: 0.09
Nodes (30): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+22 more)

### Community 10 - "hermes_home"
Cohesion: 0.08
Nodes (31): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Commit actual child seat truth, never the requested alias. No row means unknown., _route_hold() (+23 more)

### Community 11 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 12 - "pathlib"
Cohesion: 0.08
Nodes (9): pathlib, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 13 - "jload"
Cohesion: 0.14
Nodes (28): drain_inbox(), emit(), _fail_precondition(), finalize(), log(), main(), consume_markers(), loop() (+20 more)

### Community 14 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 15 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 16 - "test_require_route_25.py"
Cohesion: 0.08
Nodes (12): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned…, set_ping() (+4 more)

### Community 17 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.10
Nodes (23): dict, check(), contract(), EscapeLineOnly, fake_call_llm(), _fake_parse_retry_after(), FakeHTTPError, graph_two_routes() (+15 more)

### Community 18 - "act_run"
Cohesion: 0.09
Nodes (28): act_amend(), act_run(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _lane_entry(), _lane_paths() (+20 more)

### Community 19 - "run_state"
Cohesion: 0.11
Nodes (26): act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state() (+18 more)

### Community 20 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 21 - "sys"
Cohesion: 0.10
Nodes (14): glob, hermes_constants, plugin_api, re, sys, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+6 more)

### Community 22 - "graph_check.py"
Cohesion: 0.17
Nodes (10): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+2 more)

### Community 23 - "run_agent_node"
Cohesion: 0.11
Nodes (22): 1.0.17 — 2026-09-28, _dangling_placeholders(), fmt_goal(), _lane_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING… (+14 more)

### Community 24 - "wfcommon.py"
Cohesion: 0.09
Nodes (23): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), launch_runs_root(), precondition_facts(), quote_json_parse_error() (+15 more)

### Community 25 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _proc_alive(), _quota_cache_path() (+14 more)

### Community 26 - "json"
Cohesion: 0.11
Nodes (11): copy, hashlib, json, Identical solo child wrapper for both tag and candidate; records env key sets.…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses() (+3 more)

### Community 27 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 28 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 29 - "__init__.py"
Cohesion: 0.14
Nodes (20): difflib, act_library(), handle(), _lib_path(), _lib_read(), library_root(), _library_roots(), model_tiers() (+12 more)

### Community 30 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 31 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 32 - "3. Operate"
Cohesion: 0.11
Nodes (19): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+11 more)

### Community 34 - "EngineNextCut"
Cohesion: 0.21
Nodes (4): EngineNextCut, deps_ok(), dep_satisfied(), deps_ok()

### Community 35 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 36 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+9 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 38 - "efp"
Cohesion: 0.18
Nodes (16): File-authored graphs, put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to… (+8 more)

### Community 39 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 40 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 41 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.12
Nodes (8): agent_reasoning_effort, contextlib, Current-attempt heartbeat with real fake child identity; no provider access., core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 42 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 43 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 44 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 45 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).…, Fresh interpreter; cfg_text is the RAW config.yaml (settings + legacy config). (+4 more)

### Community 46 - "amend"
Cohesion: 0.14
Nodes (15): 3d. Failures, resume, amend, For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get (+7 more)

### Community 47 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 48 - "owner_setting"
Cohesion: 0.14
Nodes (14): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting(), profile_errors(), A surviving `${...}` after expansion means the referenced var is unset (or a… (+6 more)

### Community 49 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 50 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 51 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 52 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 53 - "validate_graph_errors"
Cohesion: 0.17
Nodes (11): _v(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), validate_graph_errors() (+3 more)

### Community 54 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 55 - "AGENTS.md"
Cohesion: 0.20
Nodes (7): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Node budgets

### Community 56 - "SKILL.md"
Cohesion: 0.18
Nodes (6): Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 58 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 59 - "when_true"
Cohesion: 0.21
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr() (+4 more)

### Community 60 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 61 - "_create_run"
Cohesion: 0.22
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.… (+3 more)

### Community 62 - "DialectRefusal"
Cohesion: 0.20
Nodes (7): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 63 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 64 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 65 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 66 - "ref_node_path"
Cohesion: 0.20
Nodes (5): ref_node_path, code, { fanItems, fanCounts }, here, src

### Community 67 - "Portable workflow files (publish = put the file on git)"
Cohesion: 0.27
Nodes (10): Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes() (+2 more)

### Community 69 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 70 - "test_packaging.py"
Cohesion: 0.22
Nodes (6): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types, zipfile

### Community 71 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 72 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 73 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 75 - "_bind_run_context"
Cohesion: 0.25
Nodes (6): Unreleased, act_list(), _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 76 - "Run operations and read model"
Cohesion: 0.25
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 77 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 78 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 79 - "_expand_config_values"
Cohesion: 0.25
Nodes (8): _expand_config_value(), _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Expand one `${VAR}` (legacy bare name) or `${env:VAR}` (Cursor-style SecretRef)…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings(), _yaml_load()

### Community 80 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 81 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 82 - "test"
Cohesion: 0.43
Nodes (6): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, _verify_spawn_rec()

### Community 83 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 87 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 88 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 89 - "_env_ref_var_name"
Cohesion: 0.29
Nodes (7): _env_ref_lookup(), _env_ref_var_name(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain…

### Community 90 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 91 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 92 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 93 - "Manual installation — Hermes Workflows 1.1.1"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 96 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 98 - "_bounded_retry"
Cohesion: 0.33
Nodes (6): _bounded_retry(), #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, _resume_preamble(), _tool_progress()

### Community 99 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 100 - "node_facts"
Cohesion: 0.40
Nodes (5): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, node_facts(), Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 101 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 104 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 105 - "_defaults_errors"
Cohesion: 0.40
Nodes (4): _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 106 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 107 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 108 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 109 - "acquire_lock"
Cohesion: 0.50
Nodes (4): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), Single-runner admission. An advisory flock held for the process lifetime IS the…

### Community 113 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **269 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 938 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `jload`, `test`, `_resolve_models`, `run_state`, `build_inputs`, `Changelog`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_fs`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.04816326530612245 - nodes in this community are weakly interconnected._
- **Should `subprocess` be split into smaller, more focused modules?**
  _Cohesion score 0.05507246376811594 - nodes in this community are weakly interconnected._