# Graph Report - tree  (2026-10-01)

## Corpus Check
- 181 files · ~240,704 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1946 nodes · 3905 edges · 133 communities (102 shown, 31 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 251 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- importlib_util
- sys
- wfcommon.py
- lane_recover.py
- _Importer
- test_fanout_expand.mjs
- _Exporter
- .meta
- wf.py
- time
- test_11_ui_imports.mjs
- jload
- settings_runs_root
- wf_dialect.py
- test_fanout_item_goal.py
- __init__.py
- efp
- test_sprint101w2_C3-fanout-gates.py
- _adopt_child
- subprocess
- loop
- log
- ref_node_fs
- json
- act_status
- os
- test_prompt_workdir.py
- test_live_truth_ui.mjs
- run_child
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- re
- CurrentAttemptMetrics
- plugin_api.py
- SKILL.md
- validate_graph_errors
- test_register_surface.mjs
- EngineNextCut
- Unreleased
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- AGENTS.md
- act_run
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- amend
- pathlib
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_sprint101_A-door.py
- test_require_route_25.py
- Run operations and read model
- test_lane_hygiene_preamble_8edcc9bf.py
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- test_route_efforts_b3c98b2a.py
- 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- hermes_home
- Changelog
- act_amend
- act_save
- _create_run
- DialectRefusal
- test_amend_rebake_034849a2.py
- test_node_facts.py
- Contributing to hermes-workflows
- ref_node_url
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- test_packaging.py
- FakeHTTPError
- ProvenanceCounters
- .run
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- test_run_dry_run.py
- model_preflight
- suite.py
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- hermes_home
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Hermes Workflows
- DoorLane
- test_model_law_dad50be0.py
- test_tier_report_0924.py
- test_tiers.py
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- _quota_note
- Run
- fmt_goal
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

## Communities (133 total, 31 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (100): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+92 more)

### Community 1 - "importlib_util"
Cohesion: 0.07
Nodes (28): contextlib, hashlib, importlib_util, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+20 more)

### Community 2 - "sys"
Cohesion: 0.05
Nodes (13): shutil, sys, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Library verbs + /wf command: save (from run_id / inline), library list, run… (+5 more)

### Community 3 - "wfcommon.py"
Cohesion: 0.06
Nodes (34): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), _env_ref_lookup(), _env_ref_var_name(), _m() (+26 more)

### Community 4 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 5 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 8 - ".meta"
Cohesion: 0.09
Nodes (30): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+22 more)

### Community 9 - "wf.py"
Cohesion: 0.09
Nodes (29): concurrent_futures, build_inputs(), _dangling_placeholders(), drain_inbox(), extract_json(), _inputs_block(), _lane_gate(), last_balanced_object() (+21 more)

### Community 10 - "time"
Cohesion: 0.08
Nodes (12): glob, hermes_constants, plugin_api, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final… (+4 more)

### Community 11 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 12 - "jload"
Cohesion: 0.13
Nodes (28): act_steer(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), active_child() (+20 more)

### Community 13 - "settings_runs_root"
Cohesion: 0.08
Nodes (27): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), _expand_config_value(), _expand_config_values(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting() (+19 more)

### Community 14 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 15 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 16 - "__init__.py"
Cohesion: 0.11
Nodes (24): difflib, _import_call_llm(), _owner_setting_read(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status() (+16 more)

### Community 17 - "efp"
Cohesion: 0.13
Nodes (25): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+17 more)

### Community 18 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 19 - "_adopt_child"
Cohesion: 0.08
Nodes (24): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _note_turn_tier() (+16 more)

### Community 20 - "subprocess"
Cohesion: 0.08
Nodes (8): subprocess, Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 21 - "loop"
Cohesion: 0.12
Nodes (23): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), _fail_precondition(), finalize(), main(), consume_markers() (+15 more)

### Community 22 - "log"
Cohesion: 0.14
Nodes (22): _bounded_retry(), log(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Write one verdict per runner process, tied to the graph snapshot it ran. An… (+14 more)

### Community 23 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 24 - "json"
Cohesion: 0.11
Nodes (11): copy, json, check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses(), Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Engine branch contracts, exercised by the actual runner and fake CLI (no…, Core-10 #89 review blocker: the EFFECTIVE synthesis prompt must not carry the… (+3 more)

### Community 25 - "act_status"
Cohesion: 0.12
Nodes (19): act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts() (+11 more)

### Community 26 - "os"
Cohesion: 0.10
Nodes (9): os, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is… (+1 more)

### Community 27 - "test_prompt_workdir.py"
Cohesion: 0.15
Nodes (18): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+10 more)

### Community 28 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 29 - "run_child"
Cohesion: 0.11
Nodes (21): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _profile_evidence() (+13 more)

### Community 30 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 31 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 32 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 33 - "re"
Cohesion: 0.12
Nodes (10): re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+2 more)

### Community 35 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 36 - "SKILL.md"
Cohesion: 0.12
Nodes (11): Node budgets, Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo) (+3 more)

### Community 37 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): _v(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+7 more)

### Community 38 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 40 - "Unreleased"
Cohesion: 0.12
Nodes (15): Unreleased, 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, act_list() (+7 more)

### Community 41 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 42 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 43 - "AGENTS.md"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+4 more)

### Community 44 - "act_run"
Cohesion: 0.16
Nodes (16): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), library_root(), _library_roots() (+8 more)

### Community 45 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), Names the seat itself resolves for -m: model aliases + the default model., Validate effective node routes after defaults and resolution, before graph.json., (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Compatibility wrapper: resolve models and return the historical (error, table)… (+8 more)

### Community 46 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 47 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 48 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 49 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).…, Fresh interpreter; cfg_text is the RAW config.yaml (settings + legacy config). (+4 more)

### Community 50 - "amend"
Cohesion: 0.13
Nodes (15): 3. Operate, 3a. The loop, 3b. Minimal graph, 3d. Failures, resume, amend, 3e. Reporting a finished run, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface (+7 more)

### Community 51 - "pathlib"
Cohesion: 0.13
Nodes (5): pathlib, Authoring door regressions; all state stays in this worktree, no…, End-to-end test of the `workflow` tool door against fake hermes., 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, Portable authoring skill contract; no provider or live-home dependencies.

### Community 53 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 54 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 55 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 56 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 57 - "Run operations and read model"
Cohesion: 0.14
Nodes (13): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), node_facts(), precondition_facts() (+5 more)

### Community 58 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.22
Nodes (12): check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file., step() (+4 more)

### Community 59 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 60 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 61 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 62 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 63 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 64 - "1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance"
Cohesion: 0.17
Nodes (12): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, find_run(), launch_runs_root(), node_child_home(), node_child_metrics(), profile_home(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as… (+4 more)

### Community 66 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 67 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 68 - "hermes_home"
Cohesion: 0.17
Nodes (12): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), hermes_home(), hermes_root(), Read model.workflows_forbidden_models on the child seat, including bare CLI… (+4 more)

### Community 69 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 70 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit… (+3 more)

### Community 71 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's… (+3 more)

### Community 72 - "_create_run"
Cohesion: 0.22
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+3 more)

### Community 73 - "DialectRefusal"
Cohesion: 0.20
Nodes (7): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 74 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 75 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 76 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 77 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 78 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 80 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 81 - "test_packaging.py"
Cohesion: 0.22
Nodes (6): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types, zipfile

### Community 82 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 83 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 84 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 85 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 86 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 87 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 88 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 90 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 91 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 92 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 95 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 96 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 97 - "hermes_home"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 98 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 99 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 100 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 101 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 103 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

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

### Community 112 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 115 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

### Community 118 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **288 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+283 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 990 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `Changelog`, `wf.py`, `jload`, `_resolve_models`, `act_status`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_fs`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _288 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05405940594059406 - nodes in this community are weakly interconnected._
- **Should `importlib_util` be split into smaller, more focused modules?**
  _Cohesion score 0.06693877551020408 - nodes in this community are weakly interconnected._
- **Should `sys` be split into smaller, more focused modules?**
  _Cohesion score 0.04995374653098982 - nodes in this community are weakly interconnected._