# Graph Report - tree  (2026-09-30)

## Corpus Check
- 170 files · ~217,374 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1835 nodes · 3704 edges · 119 communities (91 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 241 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- sys
- wfcommon.py
- .meta
- run_child
- wf.py
- subprocess
- lane_recover.py
- loop
- _Importer
- test_fanout_expand.mjs
- _Exporter
- pathlib
- test_lane_hygiene_preamble_8edcc9bf.py
- time
- test_11_ui_imports.mjs
- wf_dialect.py
- importlib_util
- test_fanout_item_goal.py
- test_sprint101w2_C3-fanout-gates.py
- json
- efp
- run_agent_node
- test_preflight_liveness_152be7f7.py
- ref_node_fs
- test_live_truth_ui.mjs
- test_daemonize_8.py
- __init__.py
- test_pill_rail_expand.mjs
- CurrentAttemptMetrics
- plugin_api.py
- SKILL.md
- test_register_surface.mjs
- _ping_route_once
- EngineNextCut
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- AGENTS.md
- act_run
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- amend
- _resolve_models
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_sprint101_A-door.py
- Changelog
- test_require_route_25.py
- _spawn_runner
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- test_pill_rail.mjs
- hermes_root
- test_route_efforts_b3c98b2a.py
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- act_amend
- act_save
- test_card_frontend_contract.mjs
- DialectRefusal
- test_amend_rebake_034849a2.py
- test_node_facts.py
- Disclosure verification — clause-by-clause evidence
- Contributing to hermes-workflows
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- .run
- _when_or
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- model_preflight
- suite.py
- CoreFaithfulCtx
- test_lifecycle_next_cut_0923.py
- test_status_next.py
- test_steer_live_40.py
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Hermes Workflows
- Run operations and read model
- DoorLane
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tiers.py
- test_v3_fixes.py
- _bind_run_context
- 11-golden-solo.py
- Claim
- test_papercuts_0922.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
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
10. `main()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
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

## Communities (119 total, 28 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "sys"
Cohesion: 0.05
Nodes (19): os, shutil, sys, Identical solo child wrapper for both tag and candidate; records env key sets.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate… (+11 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.07
Nodes (54): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, act_steer(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), shlex, fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change. (+46 more)

### Community 3 - ".meta"
Cohesion: 0.05
Nodes (46): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+38 more)

### Community 4 - "run_child"
Cohesion: 0.05
Nodes (49): _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), _first_message_s() (+41 more)

### Community 5 - "wf.py"
Cohesion: 0.06
Nodes (48): concurrent_futures, _attempt_api_calls(), build_inputs(), extract_json(), hermes_home(), _inputs_block(), _is_build_lane(), _lane_hygiene_preamble() (+40 more)

### Community 6 - "subprocess"
Cohesion: 0.07
Nodes (26): contextlib, copy, signal, subprocess, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+18 more)

### Community 7 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 8 - "loop"
Cohesion: 0.09
Nodes (32): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), log() (+24 more)

### Community 9 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 10 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 11 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 12 - "pathlib"
Cohesion: 0.08
Nodes (17): hashlib, pathlib, re, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Regression: launch a run in the tool's session; the payload carries a parser-…, check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses() (+9 more)

### Community 13 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 14 - "time"
Cohesion: 0.07
Nodes (9): _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, End-to-end test of the `workflow` tool door against fake hermes., answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer… (+1 more)

### Community 15 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 16 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 17 - "importlib_util"
Cohesion: 0.08
Nodes (10): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-… (+2 more)

### Community 18 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 19 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 20 - "json"
Cohesion: 0.09
Nodes (11): glob, hermes_constants, json, plugin_api, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+3 more)

### Community 21 - "efp"
Cohesion: 0.13
Nodes (24): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+16 more)

### Community 22 - "run_agent_node"
Cohesion: 0.10
Nodes (24): _bounded_retry(), _dangling_placeholders(), _lane_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING… (+16 more)

### Community 23 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 24 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 25 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 26 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 27 - "__init__.py"
Cohesion: 0.14
Nodes (18): difflib, act_inbox(), act_status(), _lane_key_error(), _lane_state(), _last_event_ts(), _output_pointer(), _ping_note() (+10 more)

### Community 28 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 30 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 31 - "SKILL.md"
Cohesion: 0.12
Nodes (11): Node budgets, Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo) (+3 more)

### Community 32 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 33 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 35 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 36 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 37 - "AGENTS.md"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+4 more)

### Community 38 - "act_run"
Cohesion: 0.16
Nodes (16): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), library_root(), _library_roots() (+8 more)

### Community 39 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 40 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 41 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 42 - "amend"
Cohesion: 0.13
Nodes (15): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, 1.0.1 — 2026-09-25, Deaths become outcomes (+7 more)

### Community 43 - "_resolve_models"
Cohesion: 0.18
Nodes (15): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Validate effective node routes after defaults and resolution, before graph.json., Resolve tier keys in place and return (error, model_table, routes). Explicit…, Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+7 more)

### Community 45 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 46 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 47 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 48 - "Changelog"
Cohesion: 0.14
Nodes (12): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+4 more)

### Community 49 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 50 - "_spawn_runner"
Cohesion: 0.18
Nodes (13): act_release(), act_stop(), act_wait(), _respawn_throttled(), Strict: no silent normalization — ids double as directory names. Profile-scoped…, Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law… (+5 more)

### Community 51 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 52 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 53 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 54 - "hermes_root"
Cohesion: 0.15
Nodes (12): hermes_root(), launcher_profile(), node_child_home(), node_child_metrics(), profile_errors(), profile_home(), profiles_root(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's… (+4 more)

### Community 55 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 56 - "_create_run"
Cohesion: 0.20
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `WF_RUNS_ROOT` if set, else…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+3 more)

### Community 58 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 59 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit… (+3 more)

### Community 60 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's… (+3 more)

### Community 61 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 62 - "DialectRefusal"
Cohesion: 0.20
Nodes (7): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 63 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 64 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 65 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.20
Nodes (10): Unreleased, 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, act_list() (+2 more)

### Community 66 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 67 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 69 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 70 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 71 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 72 - "_when_or"
Cohesion: 0.24
Nodes (10): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr(), when_expr_ok() (+2 more)

### Community 73 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 74 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 76 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 77 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 78 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 79 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 80 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 82 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 83 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 84 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 85 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 86 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 87 - "Run operations and read model"
Cohesion: 0.33
Nodes (5): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature)

### Community 89 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 90 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 93 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 94 - "11-golden-solo.py"
Cohesion: 0.70
Nodes (4): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…

### Community 97 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 98 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 99 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 100 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 101 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 104 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **269 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 924 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `wfcommon.py`, `wf.py`, `_resolve_models`, `Changelog`, `_spawn_runner`, `test_daemonize_8.py`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `sys` be split into smaller, more focused modules?**
  _Cohesion score 0.05021173623714459 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06753246753246753 - nodes in this community are weakly interconnected._