# Graph Report - tree  (2026-10-01)

## Corpus Check
- 194 files · ~303,845 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 4, .a 3, .b 3)

## Summary
- 2129 nodes · 4313 edges · 134 communities (104 shown, 30 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 287 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- CurrentAttemptMetrics
- wf.py
- Disclosure verification — clause-by-clause evidence
- .meta
- json
- lane_recover.py
- sys
- pathlib
- _Importer
- test_fanout_expand.mjs
- tempfile
- _Exporter
- shutil
- __init__.py
- plugin_api.py
- jload
- test_11_ui_imports.mjs
- wf_test_isolation.py
- wf_dialect.py
- test_preflight_liveness_152be7f7.py
- os
- act_steer
- test_fanout_item_goal.py
- time
- importlib_util
- ref_node_fs
- run_agent_node
- loop
- act_run
- wfcommon.py
- test_live_truth_ui.mjs
- test_daemonize_8.py
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- _ping_route_once
- test
- test_register_surface.mjs
- test_validate_0923.py
- _create_run
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- Changelog
- act_save
- efp
- shutil
- _route_enforcement
- EngineNextCut
- test_pill_rail.mjs
- test_require_route_25.py
- test_route_efforts_b3c98b2a.py
- settings_runs_root
- test_silent_death_reaper_8.py
- LiveTruth
- test_machine_watch_94.py
- test_node_panel.mjs
- _stamp_served
- validate_graph_errors
- wfcommon.py.c
- test_lane_hygiene_preamble_8edcc9bf.py
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- TeamIntegration
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- hermes_home
- test_route_efforts_b3c98b2a.py
- act_amend
- The js dialect seam (#33): `wf_dialect.py`
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- Run operations and read model
- 11-golden-solo.py
- Contributing to hermes-workflows
- graph_check.py
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- .run
- test_sprint101w2_B2-retry.py
- _expand_config_value
- _SV
- jload
- test_routing_routes.py
- run_state
- model_preflight
- dep_satisfied
- act_inbox
- install
- ref_node_assert
- suite.py
- test_failures_0923.py
- graph_fingerprint
- CoreFaithfulCtx
- test_incident_response_93.py
- test_steer_live_40.py
- build_inputs
- _defaults_errors
- _when_or
- 3. Operate
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- Hermes Workflows
- Portable workflow files (publish = put the file on git)
- DoorLane
- Claim
- test_model_law_dad50be0.py
- Ctx
- test_suite_admission_17.py
- _expand_config_values
- 1.0.1 — 2026-09-25
- manifest.json
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- Run
- date-now.js
- meta-nonliteral.js
- Ctx
- fake
- args-iterable.js
- args-template.js
- audit-routes.js
- pipeline-glue-stage.js
- pipeline-length-template.js
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
- `Ergonomics` --references--> `model()`  [INFERRED]
  references/operator-playbook.md → blobs/__init__.py.c
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` --references--> `useValue()`  [INFERRED]
  CHANGELOG.md → tests/test_fanout_expand.mjs
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (134 total, 30 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (98): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+90 more)

### Community 1 - "CurrentAttemptMetrics"
Cohesion: 0.05
Nodes (43): after(), NEVER, or, else(), hermes_home(), resolves(), Returns(), 1.1.2 — 2026-10-01 (+35 more)

### Community 2 - "wf.py"
Cohesion: 0.05
Nodes (65): concurrent_futures, What the plugin gains, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output() (+57 more)

### Community 3 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.04
Nodes (40): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+32 more)

### Community 4 - ".meta"
Cohesion: 0.06
Nodes (41): as, or, e(), except(), model(), return(), runner_alive(), OSError() (+33 more)

### Community 5 - "json"
Cohesion: 0.05
Nodes (14): json, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, 45b038: cron's core-less interpreter must still bake a proved pinned route. The… (+6 more)

### Community 6 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 7 - "sys"
Cohesion: 0.07
Nodes (21): ast, hashlib, re, sys, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source. (+13 more)

### Community 8 - "pathlib"
Cohesion: 0.08
Nodes (19): copy, pathlib, subprocess, Identical solo child wrapper for both tag and candidate; records env key sets.…, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper (+11 more)

### Community 9 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 10 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (29): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+21 more)

### Community 11 - "tempfile"
Cohesion: 0.07
Nodes (17): atexit, importlib, tempfile, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v(), The child launcher is operator-controlled, never a tool argument. (+9 more)

### Community 12 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 13 - "shutil"
Cohesion: 0.06
Nodes (11): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+3 more)

### Community 14 - "__init__.py"
Cohesion: 0.10
Nodes (31): difflib, _alias_provider_pair(), handle(), _lane_key_error(), _last_event_ts(), _model_policy_error(), model_tiers(), _output_pointer() (+23 more)

### Community 15 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 16 - "jload"
Cohesion: 0.12
Nodes (28): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_state() (+20 more)

### Community 17 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 18 - "wf_test_isolation.py"
Cohesion: 0.07
Nodes (7): Authoring door regressions; all state stays in this worktree, no…, Library verbs + /wf command: save (from run_id / inline), library list, run…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, 4052d57719653b1a: atomic library replay binding, no real runner., Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, #71 (r5): the in-process door-writer isolation mechanism — a resolver-level…

### Community 19 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 20 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.10
Nodes (23): dict, check(), contract(), EscapeLineOnly, fake_call_llm(), _fake_parse_retry_after(), FakeHTTPError, graph_two_routes() (+15 more)

### Community 21 - "os"
Cohesion: 0.09
Nodes (12): os, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, #100: optional graph scheduling limits are owner-clamped at the door. Run: env…, #50 (epic #49, door half): discovery-first library. Contracts pinned here: (1)…, #57 — `list` payload gains the per-root provenance rollup (QM digest contract).…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…, fields() (+4 more)

### Community 23 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 24 - "time"
Cohesion: 0.08
Nodes (7): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…, time

### Community 25 - "importlib_util"
Cohesion: 0.09
Nodes (13): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes. (+5 more)

### Community 26 - "ref_node_fs"
Cohesion: 0.10
Nodes (16): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+8 more)

### Community 27 - "run_agent_node"
Cohesion: 0.10
Nodes (24): _bounded_retry(), _dangling_placeholders(), _lane_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING… (+16 more)

### Community 28 - "loop"
Cohesion: 0.13
Nodes (22): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), _fail_precondition(), finalize(), log(), main() (+14 more)

### Community 29 - "act_run"
Cohesion: 0.11
Nodes (23): act_library(), act_run(), _concurrency_bake(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+15 more)

### Community 30 - "wfcommon.py"
Cohesion: 0.09
Nodes (21): shlex, _active_spawn(), amend_preview(), blocked_legibility(), current_attempt(), _downstream(), precondition_facts(), quote_json_parse_error() (+13 more)

### Community 31 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 32 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 33 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 34 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 35 - "_ping_route_once"
Cohesion: 0.12
Nodes (18): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal(), One auxiliary ping on the pinned (provider, model) route — explicit provider… (+10 more)

### Community 36 - "test"
Cohesion: 0.16
Nodes (17): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), fingerprint_valid() (+9 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 38 - "test_validate_0923.py"
Cohesion: 0.12
Nodes (9): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, Exception, #71 regression pin: the shelf is a live production surface — no test may write…, SavedGolden, mkrun() (+1 more)

### Community 39 - "_create_run"
Cohesion: 0.13
Nodes (17): _card(), _create_run(), _hermes_bin(), _identity_stamps(), ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+9 more)

### Community 40 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 41 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 42 - "Changelog"
Cohesion: 0.12
Nodes (14): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+6 more)

### Community 43 - "act_save"
Cohesion: 0.13
Nodes (16): act_save(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 44 - "efp"
Cohesion: 0.17
Nodes (16): File-authored graphs, Per-run concurrency (optional), Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), gate(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run() (+8 more)

### Community 45 - "shutil"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 46 - "_route_enforcement"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 49 - "test_require_route_25.py"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 50 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 51 - "settings_runs_root"
Cohesion: 0.15
Nodes (14): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), _nested(), _no_unresolved_ref(), owner_setting(), A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives…, A surviving `${...}` after expansion means the referenced var is unset (or a…, One owner-settings read: the door's plugin ctx when it has one (its answer is… (+6 more)

### Community 52 - "test_silent_death_reaper_8.py"
Cohesion: 0.14
Nodes (7): signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner…

### Community 54 - "test_machine_watch_94.py"
Cohesion: 0.16
Nodes (8): argv(), check(), native_engine(), spawn(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling., Door-transport guard: run_context must never silently route a map to seed.…, state()

### Community 55 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 56 - "_stamp_served"
Cohesion: 0.15
Nodes (15): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+7 more)

### Community 57 - "validate_graph_errors"
Cohesion: 0.15
Nodes (13): grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), _tok_when() (+5 more)

### Community 58 - "wfcommon.py.c"
Cohesion: 0.14
Nodes (13): _active_spawns, never, enumerate(), list(), object(), path(), safe_load(), fixed (+5 more)

### Community 59 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.22
Nodes (12): check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file., step() (+4 more)

### Community 60 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 61 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 62 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 63 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 64 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 65 - "1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance"
Cohesion: 0.17
Nodes (12): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, find_run(), launch_runs_root(), node_child_home(), node_child_metrics(), profile_home(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as… (+4 more)

### Community 67 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 68 - "hermes_home"
Cohesion: 0.18
Nodes (11): hermes_home(), hermes_root(), launcher_profile(), profile_errors(), profiles_root(), Read model.workflows_forbidden_models on the child seat, including bare CLI…, The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a…, Launcher identity — NEVER from a graph/run arg. Ranked (#41): 1. the process's… (+3 more)

### Community 69 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 70 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+3 more)

### Community 71 - "The js dialect seam (#33): `wf_dialect.py`"
Cohesion: 0.20
Nodes (7): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 72 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 74 - "Run operations and read model"
Cohesion: 0.24
Nodes (10): The door validates from lists, What you get, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Smart defaults (#50 audit) (+2 more)

### Community 75 - "11-golden-solo.py"
Cohesion: 0.29
Nodes (7): contextlib, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Current-attempt heartbeat with real fake child identity; no provider access.

### Community 76 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 77 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 78 - "_fake_parse_retry_after"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 79 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 80 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 81 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 82 - "_expand_config_value"
Cohesion: 0.22
Nodes (9): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain… (+1 more)

### Community 84 - "jload"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 85 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 87 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 88 - "dep_satisfied"
Cohesion: 0.33
Nodes (7): 1.1.3 — 2026-10-01, deps_ok(), blocked_by(), dep_satisfied(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's…, deps_ok()

### Community 89 - "act_inbox"
Cohesion: 0.29
Nodes (7): act_inbox(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 90 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 91 - "ref_node_assert"
Cohesion: 0.29
Nodes (6): ref_node_assert, [first, second], header, match, root, source

### Community 92 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 94 - "graph_fingerprint"
Cohesion: 0.48
Nodes (6): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 95 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 96 - "test_incident_response_93.py"
Cohesion: 0.38
Nodes (4): engine_case(), poll_sequence(), probe_argv(), Execute the shipped incident probe argv and the real parked-gate loop.

### Community 97 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 98 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet.…, Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 99 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 100 - "_when_or"
Cohesion: 0.38
Nodes (7): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not(), _when_or()

### Community 101 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 102 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 103 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 104 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 105 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 106 - "Portable workflow files (publish = put the file on git)"
Cohesion: 0.53
Nodes (6): Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), 1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the…, source_digest()

### Community 109 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 111 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 112 - "_expand_config_values"
Cohesion: 0.33
Nodes (6): _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings(), _yaml_load()

### Community 113 - "1.0.1 — 2026-09-25"
Cohesion: 0.50
Nodes (4): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The graph carries less

### Community 114 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 115 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **282 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+277 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1062 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `CurrentAttemptMetrics`, `build_inputs`, `test`, `test_fanout_expand.mjs`, `Changelog`, `__init__.py`, `jload`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `ref_node_fs`, `.meta`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `useValue()` connect `test_fanout_expand.mjs` to `plugin.js`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _282 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05586477015048444 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.05030181086519115 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05311676909569798 - nodes in this community are weakly interconnected._