# Graph Report - tree  (2026-10-01)

## Corpus Check
- 175 files · ~235,763 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1965 nodes · 3996 edges · 135 communities (106 shown, 29 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 252 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- os
- jload
- lane_recover.py
- wfcommon.py
- runner_alive
- test_fanout_expand.mjs
- time
- shutil
- _Exporter
- plugin_api.py
- .meta
- test_lane_hygiene_preamble_8edcc9bf.py
- wf.py
- wf_dialect.py
- test_11_ui_imports.mjs
- test_fanout_item_goal.py
- importlib_util
- efp
- test_sprint101w2_C3-fanout-gates.py
- _Importer
- pathlib
- _final_quiesce
- json
- _adopt_child
- run_child
- subprocess
- ref_node_assert
- test_failures_0923.py
- test_preflight_liveness_152be7f7.py
- test_live_truth_ui.mjs
- sys
- test_pill_rail_expand.mjs
- CurrentAttemptMetrics
- Run operations and read model
- validate_graph_errors
- test_register_surface.mjs
- act_status
- _ping_route_once
- SKILL.md
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- .statement
- AGENTS.md
- __init__.py
- act_amend
- act_run
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- _sidecar_live_registered
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- _expand_config_values
- 4. Contribute
- test_sprint101_A-door.py
- test_require_route_25.py
- test_proctree_61b.py
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- _create_run
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- _boot_sweep
- Changelog
- test_amend_rebake_034849a2.py
- 3. The importable subset, stated once
- _bind_run_context
- Contributing to hermes-workflows
- test_validate_0923.py
- ref_node_fs
- Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet
- agent
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- DialectRefusal
- plugin-catalog: add `hermes-workflows` (community, automation)
- Disclosure verification — clause-by-clause evidence
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_fatal_quota_24.py
- test_routing_routes.py
- test_run_dry_run.py
- model_preflight
- suite.py
- CoreFaithfulCtx
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- hermes_home
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Hermes Workflows
- DoorLane
- test_suite_admission_17.py
- test_tiers.py
- _proc_envv
- _verify_spawn_rec
- 1.0.1 — 2026-09-25
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- _route_enforcement
- dynamic-agent-count.js
- test_fp_rule_95d70102.py
- Integrated
- .render_item_template
- _lane_hygiene_preamble
- _quota_note
- Run
- node_child_home
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
1. `run_child()` - 45 edges
2. `efp()` - 37 edges
3. `jload()` - 36 edges
4. `log()` - 27 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
7. `_adopt_child()` - 25 edges
8. `main()` - 24 edges
9. `loop()` - 23 edges
10. `run_state()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `4. What this PR does not decide` --references--> `agent()`  [INFERRED]
  references/dialect.md → tests/test_prune_0923.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (135 total, 29 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "os"
Cohesion: 0.06
Nodes (24): os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), F3 boundary/claim integration: real door processes + kernel flock; no hook in…, Lane E: cross-lane executable integration fixtures; no production… (+16 more)

### Community 2 - "jload"
Cohesion: 0.10
Nodes (44): ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., test(), acquire_lock(), emit(), _fail_precondition() (+36 more)

### Community 3 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 4 - "wfcommon.py"
Cohesion: 0.08
Nodes (35): shlex, amend_preview(), blocked_by(), current_attempt(), _downstream(), find_run(), launch_runs_root(), node_facts() (+27 more)

### Community 5 - "runner_alive"
Cohesion: 0.07
Nodes (33): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), hermes_home(), hermes_root(), launcher_profile(), _nested(), _no_unresolved_ref() (+25 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "time"
Cohesion: 0.06
Nodes (8): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #61 — the runner is process-tree aware before it judges an attempt. Evidence…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…, time

### Community 8 - "shutil"
Cohesion: 0.06
Nodes (9): shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+1 more)

### Community 9 - "_Exporter"
Cohesion: 0.15
Nodes (12): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+4 more)

### Community 10 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 11 - ".meta"
Cohesion: 0.09
Nodes (29): 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, The js dialect seam (#33): `wf_dialect.py`, _attempt_api_calls(), _bounded_retry(), api_calls for ONE dead attempt via the state.db join. Return an integer only… (+21 more)

### Community 12 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 13 - "wf.py"
Cohesion: 0.09
Nodes (29): concurrent_futures, _aux_run(), build_inputs(), drain_inbox(), extract_json(), _inputs_block(), _lane_gate(), last_balanced_object() (+21 more)

### Community 14 - "wf_dialect.py"
Cohesion: 0.08
Nodes (25): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _mask(), _match_close() (+17 more)

### Community 15 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 16 - "test_fanout_item_goal.py"
Cohesion: 0.18
Nodes (28): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+20 more)

### Community 17 - "importlib_util"
Cohesion: 0.07
Nodes (8): importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, 4052d57719653b1a: atomic library replay binding, no real runner., Door-transport guard: run_context must never silently route a map to seed.…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph()

### Community 18 - "efp"
Cohesion: 0.12
Nodes (26): 2. The mapping table, File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.… (+18 more)

### Community 19 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 20 - "_Importer"
Cohesion: 0.17
Nodes (12): _Importer, _line(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to… (+4 more)

### Community 21 - "pathlib"
Cohesion: 0.10
Nodes (14): hashlib, pathlib, Identical solo child wrapper for both tag and candidate; records env key sets.…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses(), check() (+6 more)

### Community 22 - "_final_quiesce"
Cohesion: 0.14
Nodes (25): _account_tree(), _complete(), _final_quiesce(), _isolate_prior(), _left_live_record(), _proc_alive(), _proc_pids_by_pgid(), _proc_unreadable_record() (+17 more)

### Community 23 - "json"
Cohesion: 0.08
Nodes (8): json, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 24 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _note_turn_tier() (+14 more)

### Community 25 - "run_child"
Cohesion: 0.10
Nodes (23): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _profile_evidence() (+15 more)

### Community 26 - "subprocess"
Cohesion: 0.11
Nodes (12): contextlib, copy, subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Current-attempt heartbeat with real fake child identity; no provider access. (+4 more)

### Community 27 - "ref_node_assert"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 28 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 29 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 30 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 31 - "sys"
Cohesion: 0.14
Nodes (12): re, sys, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-… (+4 more)

### Community 32 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 34 - "Run operations and read model"
Cohesion: 0.13
Nodes (16): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Lanes: in-flight dedupe for pollers (+8 more)

### Community 35 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): _v(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+7 more)

### Community 36 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 37 - "act_status"
Cohesion: 0.15
Nodes (15): act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts() (+7 more)

### Community 38 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 39 - "SKILL.md"
Cohesion: 0.12
Nodes (11): Node budgets, Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo) (+3 more)

### Community 40 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 41 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 42 - ".statement"
Cohesion: 0.15
Nodes (8): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, _statements()

### Community 43 - "AGENTS.md"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+4 more)

### Community 44 - "__init__.py"
Cohesion: 0.16
Nodes (15): difflib, act_inbox(), act_steer(), _owner_setting_read(), _ping_note(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,… (+7 more)

### Community 45 - "act_amend"
Cohesion: 0.13
Nodes (16): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _model_names_valid(), _profile_error(), Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 46 - "act_run"
Cohesion: 0.16
Nodes (16): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), library_root(), _library_roots() (+8 more)

### Community 47 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+8 more)

### Community 48 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 49 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 50 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 51 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).…, Fresh interpreter; cfg_text is the RAW config.yaml (settings + legacy config). (+4 more)

### Community 52 - "_sidecar_live_registered"
Cohesion: 0.14
Nodes (16): _proc_children_of(), _proc_snapshot(), _proc_state(), One pass over /proc: {pid: (ppid, pgid)} for LIVE (non-zombie) pids. Zombie =…, The FULL live process SUBTREE under `pid` (not just direct children): a double-…, Every pid the runner itself launched or attached: the _procs registry (Popen…, Live pids whose PPid is THIS runner that the runner did not launch: subreaper-…, Live descendants of `pid` (recursive ppid walk over a fresh snapshot); None… (+8 more)

### Community 55 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 56 - "_expand_config_values"
Cohesion: 0.13
Nodes (15): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _expand_config_values(), _is_non_env_secret_ref(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,… (+7 more)

### Community 57 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 58 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 59 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 60 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 61 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 62 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 63 - "_create_run"
Cohesion: 0.18
Nodes (13): _card(), _create_run(), _hermes_bin(), _identity_stamps(), _liveness_hint_suffix(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+5 more)

### Community 64 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 65 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 67 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 68 - "_boot_sweep"
Cohesion: 0.17
Nodes (12): _boot_sweep(), _kill_pool(), _proctree_kill_proof_s(), best-effort waitpid for a runner-adopted orphan that died (zombie hygiene;…, #61c: /proc-verify every pid is dead within the budget. (True, []) when PROVEN…, SIGTERM (grace) -> SIGKILL fallback -> /proc re-walk for a scattered set of…, [(pid, token)] for every registration row. A torn line (a writer mid-append) is…, #61c: before a (re)spawned runner launches anything, reap the survivors the… (+4 more)

### Community 69 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 70 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 71 - "3. The importable subset, stated once"
Cohesion: 0.20
Nodes (8): 1.0.17 — 2026-09-28, 1. Shape of each side in one screen, 3. The importable subset, stated once, 4. What this PR does not decide, Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON), fmt_goal(), apply_graph_defaults(), Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…

### Community 72 - "_bind_run_context"
Cohesion: 0.20
Nodes (8): Unreleased, act_list(), _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…, Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, _resume_preamble()

### Community 73 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 74 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 75 - "ref_node_fs"
Cohesion: 0.20
Nodes (5): ref_node_fs, code, { fanItems, fanCounts }, here, src

### Community 76 - "Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet"
Cohesion: 0.20
Nodes (9): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 4. `args` global, 5. File locations & discovery, 7. Plain-JS rule, TypeScript, and loops, 8. Model routing precedence per stage, Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet (+1 more)

### Community 77 - "agent"
Cohesion: 0.27
Nodes (10): 3.1 `agent(prompt, options?)`, 3.2 `parallel(tasks)`, 3.3 `pipeline(items, stage1, stage2, ...)`, 3.4 `phase(title)`, 3.5 `log(message)`, 3.6 Script return value, 3. Runtime globals / primitives, 6. Runtime constraints & limits (verbatim table, S1 §"Behavior and limits") (+2 more)

### Community 78 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 80 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 81 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 82 - "DialectRefusal"
Cohesion: 0.24
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 83 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 84 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.22
Nodes (9): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+1 more)

### Community 85 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 87 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 88 - "test_fatal_quota_24.py"
Cohesion: 0.29
Nodes (3): _LADDER, _OK, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…

### Community 89 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 91 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 92 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 93 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 95 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 96 - "hermes_home"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 97 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 98 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 99 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 101 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 103 - "_proc_envv"
Cohesion: 0.33
Nodes (6): _proc_envv(), /proc/PID/environ as a dict; {} when unreadable (absence loses only the token…, Append one fsync'd registry row — the documented CHILD-side contract, called by…, Child-side helper implementing the registration contract: a detached descendant…, _register_self_if_detached(), _register_survivor()

### Community 104 - "_verify_spawn_rec"
Cohesion: 0.33
Nodes (6): _active_spawn(), _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, All verified uncommitted child identities, never historical DB liveness., Compatibility: first verified spawn for existing blocked-by consumers., _verify_spawn_rec()

### Community 105 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 106 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 109 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 110 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 111 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 112 - "_route_enforcement"
Cohesion: 0.50
Nodes (4): #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 113 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 114 - "test_fp_rule_95d70102.py"
Cohesion: 0.67
Nodes (3): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change.

### Community 117 - "_lane_hygiene_preamble"
Cohesion: 0.50
Nodes (4): _is_build_lane(), _lane_hygiene_preamble(), The build shape: `shape: "build"` declared, or a `repo:` lane declared (the…, Machine-generated lane-hygiene preamble for build-shape nodes ("" otherwise).…

### Community 118 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

### Community 120 - "node_child_home"
Cohesion: 0.50
Nodes (4): node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as…

## Knowledge Gaps
- **270 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+265 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 987 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `jload`, `runner_alive`, `act_status`, `Changelog`, `_verify_spawn_rec`, `wf.py`, `_resolve_models`?**
  _High betweenness centrality (0.214) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `efp`, `ref_node_assert`, `agent`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _270 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.06376811594202898 - nodes in this community are weakly interconnected._
- **Should `jload` be split into smaller, more focused modules?**
  _Cohesion score 0.09696969696969697 - nodes in this community are weakly interconnected._