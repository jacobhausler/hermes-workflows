# Graph Report - tree  (2026-10-02)

## Corpus Check
- 186 files · ~258,252 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2073 nodes · 4204 edges · 130 communities (97 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 260 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- importlib_util
- jload
- subprocess
- os
- test_require_route_25.py
- _Importer
- lane_recover.py
- test_preflight_liveness_152be7f7.py
- _Exporter
- test_fanout_expand.mjs
- wf_dialect.py
- .meta
- one
- plugin_api.py
- pathlib
- test_lane_hygiene_preamble_8edcc9bf.py
- test_11_ui_imports.mjs
- json
- DoorLib50
- sys
- test_fanout_item_goal.py
- ref_node_fs
- act_run
- _ping_route_once
- validate_graph_errors
- test_live_truth_ui.mjs
- test_daemonize_8.py
- efp
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- CurrentAttemptMetrics
- __init__.py
- act_status
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- Changelog
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- 11-golden-solo.py
- Run operations and read model
- test_orphan_adopt_790c6ad.py
- DialectRefusal
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- _create_run
- act_save
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- act_amend
- Contributing to hermes-workflows
- graph_check.py
- TeamIntegration
- test_hermes_bin_reserved_0928.py
- test_lane_recover_8edcc9bf.py
- test_packaging.py
- ProvenanceCounters
- test_silent_death_reaper_8.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- SKILL.md
- test_sprint101w2_B2-retry.py
- _SV
- AGENTS.md — front door for agents
- test_cross_container_liveness_91b9a3de.py
- test_engine.py
- test_resume_fresh_session_102.py
- test_routing_routes.py
- test_run_dry_run.py
- model_preflight
- install
- ref_node_assert
- suite.py
- test_lane_gate_64c6772b.py
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- AGENTS.md
- 4. Contribute
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- Manual installation — Hermes Workflows 1.1.3
- Hermes Workflows
- Portable workflow files (publish = put the file on git)
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- Claim
- test_suite_admission_17.py
- test_tier_report_0924.py
- _dead_session_harvest
- _verify_spawn_rec
- 3. Operate
- 1.0.1 — 2026-09-25
- dep_satisfied
- test_sprint101_D-surface.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
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
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
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

## Communities (130 total, 33 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (99): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+91 more)

### Community 1 - "wf.py"
Cohesion: 0.04
Nodes (83): concurrent_futures, _adopt_child(), _AdoptedHandle, build_inputs(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output() (+75 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.04
Nodes (80): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), shlex, amend_preview(), blocked_by(), current_attempt(), _downstream(), effective_runs_root() (+72 more)

### Community 3 - "importlib_util"
Cohesion: 0.06
Nodes (30): contextlib, hashlib, importlib_util, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+22 more)

### Community 4 - "jload"
Cohesion: 0.07
Nodes (53): act_release(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change. (+45 more)

### Community 5 - "subprocess"
Cohesion: 0.05
Nodes (16): shutil, subprocess, Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+8 more)

### Community 6 - "os"
Cohesion: 0.05
Nodes (17): os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.… (+9 more)

### Community 7 - "test_require_route_25.py"
Cohesion: 0.05
Nodes (17): atexit, fcntl, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v(), HTTP429 (+9 more)

### Community 8 - "_Importer"
Cohesion: 0.12
Nodes (18): fields(), _control_kw(), _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated… (+10 more)

### Community 9 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 10 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 11 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 12 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 13 - "wf_dialect.py"
Cohesion: 0.07
Nodes (28): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _line(), _main() (+20 more)

### Community 14 - ".meta"
Cohesion: 0.10
Nodes (29): label(), 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block (+21 more)

### Community 15 - "one"
Cohesion: 0.07
Nodes (31): _attempt_api_calls(), _bounded_retry(), _dangling_placeholders(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed… (+23 more)

### Community 16 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 17 - "pathlib"
Cohesion: 0.08
Nodes (15): copy, glob, pathlib, re, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Engine branch contracts, exercised by the actual runner and fake CLI (no…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-…, engine_case() (+7 more)

### Community 18 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 19 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 20 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 22 - "sys"
Cohesion: 0.08
Nodes (11): sys, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-… (+3 more)

### Community 23 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 24 - "ref_node_fs"
Cohesion: 0.10
Nodes (16): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+8 more)

### Community 25 - "act_run"
Cohesion: 0.12
Nodes (22): act_library(), act_run(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), _lib_rel_name() (+14 more)

### Community 26 - "_ping_route_once"
Cohesion: 0.10
Nodes (21): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+13 more)

### Community 27 - "validate_graph_errors"
Cohesion: 0.10
Nodes (19): apply_graph_defaults(), _defaults_errors(), grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key… (+11 more)

### Community 28 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 29 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 30 - "efp"
Cohesion: 0.15
Nodes (19): File-authored graphs, put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), gate() (+11 more)

### Community 31 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 32 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 34 - "__init__.py"
Cohesion: 0.16
Nodes (17): difflib, act_inbox(), act_steer(), act_submit(), _model_names_valid(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, Return graph-level and node-level defects together, before any write/spawn., #50 (epic #49): submit a hand-rolled graph for STUDY — the quarantine inbox… (+9 more)

### Community 35 - "act_status"
Cohesion: 0.14
Nodes (16): act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts(), _output_pointer() (+8 more)

### Community 36 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 37 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 38 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 39 - "Changelog"
Cohesion: 0.12
Nodes (13): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+5 more)

### Community 40 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+8 more)

### Community 41 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 42 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 45 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 46 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 47 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (15): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+7 more)

### Community 49 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 50 - "11-golden-solo.py"
Cohesion: 0.19
Nodes (9): hermes_constants, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Exception, #71 regression pin: the shelf is a live production surface — no test may write… (+1 more)

### Community 51 - "Run operations and read model"
Cohesion: 0.18
Nodes (13): 3d. Failures, resume, amend, What you get, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit) (+5 more)

### Community 52 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 53 - "DialectRefusal"
Cohesion: 0.18
Nodes (8): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 54 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 55 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 56 - "_create_run"
Cohesion: 0.20
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+4 more)

### Community 57 - "act_save"
Cohesion: 0.17
Nodes (12): act_save(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, The door only ever sees `graph` as a parsed object from the tool schema, but a…, #62 F-1: the INLINE branch must cap exactly like the graph_path branch — the… (+4 more)

### Community 59 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 60 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 61 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+3 more)

### Community 62 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 63 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 65 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 66 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 67 - "test_packaging.py"
Cohesion: 0.22
Nodes (6): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types, zipfile

### Community 68 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 69 - "test_silent_death_reaper_8.py"
Cohesion: 0.20
Nodes (3): kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner…

### Community 70 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 71 - "SKILL.md"
Cohesion: 0.25
Nodes (5): Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay

### Community 72 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 74 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 75 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.25
Nodes (4): io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…

### Community 76 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 78 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 80 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 81 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 82 - "ref_node_assert"
Cohesion: 0.29
Nodes (6): ref_node_assert, [first, second], header, match, root, source

### Community 83 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 84 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 88 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 89 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 91 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 92 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 93 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 94 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 95 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 96 - "Manual installation — Hermes Workflows 1.1.3"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.3, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 97 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 98 - "Portable workflow files (publish = put the file on git)"
Cohesion: 0.53
Nodes (6): Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), 1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the…, source_digest()

### Community 99 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 102 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 104 - "_dead_session_harvest"
Cohesion: 0.33
Nodes (6): _banked_work(), _clean_capture(), _dead_session_harvest(), Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —…, The #102 harvest preamble for a re-drive whose prior session persisted NO…

### Community 105 - "_verify_spawn_rec"
Cohesion: 0.33
Nodes (6): _active_spawn(), _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, All verified uncommitted child identities, never historical DB liveness., Compatibility: first verified spawn for existing blocked-by consumers., _verify_spawn_rec()

### Community 106 - "3. Operate"
Cohesion: 0.40
Nodes (5): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run

### Community 107 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 108 - "dep_satisfied"
Cohesion: 0.50
Nodes (5): 1.1.3 — 2026-10-01, deps_ok(), dep_satisfied(), After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 109 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 110 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 111 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 112 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 113 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1049 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `wf.py`, `act_status`, `jload`, `Changelog`, `_resolve_models`, `_verify_spawn_rec`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `label()` connect `.meta` to `plugin.js`, `ref_node_fs`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.054343434343434346 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0426812585499316 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.037292025243832475 - nodes in this community are weakly interconnected._