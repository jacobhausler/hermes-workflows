# Graph Report - tree  (2026-09-29)

## Corpus Check
- 120 files · ~158,135 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1406 nodes · 2830 edges · 91 communities (77 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 165 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- CurrentAttemptMetrics
- pathlib
- plugin_api.py
- efp
- test_fanout_expand.mjs
- run_agent_node
- jload
- os
- test_prompt_workdir.py
- shutil
- json
- test_11_ui_imports.mjs
- test_fanout_item_goal.py
- wf.py
- __init__.py
- importlib_util
- _adopt_child
- run_child
- test_failures_0923.py
- Changelog
- sys
- test_card_frontend_contract.mjs
- test_live_truth_ui.mjs
- test_register_surface.mjs
- act_amend
- wfcommon.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- test_orphan_adopt_790c6ad.py
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- Disclosure verification — clause-by-clause evidence
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- _ping_route_once
- test_preflight_liveness_152be7f7.py
- test_route_efforts_b3c98b2a.py
- test_sprint101w2_D2-steer-liveness.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- when_true
- test_fp_rule_f0f154d5.py
- validate_graph_errors
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- FakeHTTPError
- act_run
- _create_run
- ref_node_url
- TeamIntegration
- test
- test_sprint101w2_B2-retry.py
- hermes_home
- _SV
- AGENTS.md — front door for agents
- amend
- test_engine.py
- test_routing_routes.py
- model_preflight
- Run operations and read model
- CoreFaithfulCtx
- test_review_fixes.py
- test_status_next.py
- test_steer_live_40.py
- _defaults_errors
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Hermes Workflows
- DoorLane
- test_model_law_dad50be0.py
- test_prune_0923.py
- test_tier_report_0924.py
- test_tiers.py
- 3. Operate
- _bind_run_context
- Graph grammar and authoring boundaries
- Claim
- test_sprint101_D-surface.py
- test_validator_caps.py
- profile_errors
- manifest.json
- .states
- Integrated
- Run
- node_child_home
- fake

## God Nodes (most connected - your core abstractions)
1. `jload()` - 35 edges
2. `efp()` - 33 edges
3. `run_child()` - 30 edges
4. `run_state()` - 22 edges
5. `_adopt_child()` - 21 edges
6. `main()` - 21 edges
7. `loop()` - 21 edges
8. `NodePanel()` - 18 edges
9. `CurrentAttemptMetrics` - 18 edges
10. `act_run()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py
- `1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)` --references--> `model_preflight()`  [INFERRED]
  CHANGELOG.md → __init__.py

## Import Cycles
- None detected.

## Communities (91 total, 14 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "CurrentAttemptMetrics"
Cohesion: 0.07
Nodes (23): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+15 more)

### Community 2 - "pathlib"
Cohesion: 0.08
Nodes (27): contextlib, copy, hashlib, pathlib, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, subprocess, tempfile, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source. (+19 more)

### Community 3 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 4 - "efp"
Cohesion: 0.11
Nodes (34): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), _fail_precondition(), finalize() (+26 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "run_agent_node"
Cohesion: 0.08
Nodes (32): 1.0.17 — 2026-09-28, _attempt_api_calls(), _bounded_retry(), _dangling_placeholders(), fmt_goal(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+24 more)

### Community 7 - "jload"
Cohesion: 0.11
Nodes (32): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_state() (+24 more)

### Community 8 - "os"
Cohesion: 0.07
Nodes (10): os, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on… (+2 more)

### Community 9 - "test_prompt_workdir.py"
Cohesion: 0.09
Nodes (28): argparse, fnmatch, Pattern, Nodes and data, excluded(), load_guards(), main(), Path (+20 more)

### Community 10 - "shutil"
Cohesion: 0.07
Nodes (9): fcntl, shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Feedback #68: steer on a node/run that can never spawn reports HONEST results.… (+1 more)

### Community 11 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 12 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 13 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 14 - "wf.py"
Cohesion: 0.11
Nodes (24): concurrent_futures, build_inputs(), drain_inbox(), extract_json(), hermes_home(), _inputs_block(), last_balanced_object(), _match_object() (+16 more)

### Community 15 - "__init__.py"
Cohesion: 0.13
Nodes (24): difflib, _alias_provider_pair(), handle(), _lane_key_error(), _last_event_ts(), _model_policy_error(), model_tiers(), _output_pointer() (+16 more)

### Community 16 - "importlib_util"
Cohesion: 0.09
Nodes (10): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-… (+2 more)

### Community 17 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 18 - "run_child"
Cohesion: 0.10
Nodes (24): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+16 more)

### Community 19 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (7): sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 20 - "Changelog"
Cohesion: 0.09
Nodes (21): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+13 more)

### Community 21 - "sys"
Cohesion: 0.13
Nodes (15): glob, hermes_constants, plugin_api, re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this… (+7 more)

### Community 22 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 23 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 24 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 25 - "act_amend"
Cohesion: 0.12
Nodes (18): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _liveness_hint_suffix(), _model_names_valid(), _profile_error() (+10 more)

### Community 26 - "wfcommon.py"
Cohesion: 0.12
Nodes (17): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), effective_runs_root(), precondition_facts(), quote_json_parse_error() (+9 more)

### Community 27 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 28 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 29 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.14
Nodes (9): datetime, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):… (+1 more)

### Community 30 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 31 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 32 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 33 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 36 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 37 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 38 - "_ping_route_once"
Cohesion: 0.14
Nodes (13): _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the…, Server Retry-After, best-effort via core's parser. None when no header — NEVER… (+5 more)

### Community 39 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.21
Nodes (13): check(), contract(), fake_call_llm(), call_llm(), _fake_parse_retry_after(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.… (+5 more)

### Community 40 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 41 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.20
Nodes (5): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…

### Community 43 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 44 - "when_true"
Cohesion: 0.21
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr() (+4 more)

### Community 45 - "test_fp_rule_f0f154d5.py"
Cohesion: 0.25
Nodes (10): Top-level provenance, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes. (+2 more)

### Community 46 - "validate_graph_errors"
Cohesion: 0.20
Nodes (9): rerr(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, requires_errors(), validate_graph_errors(), E(), schema_check() (+1 more)

### Community 47 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 48 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 49 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): Exception, EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 50 - "act_run"
Cohesion: 0.27
Nodes (10): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), library_root(), `/wf` — the library front door. `/wf <name> [note]` supplies the note…, 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty… (+2 more)

### Community 51 - "_create_run"
Cohesion: 0.20
Nodes (9): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.…, Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+1 more)

### Community 52 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 54 - "test"
Cohesion: 0.31
Nodes (8): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, _verify_spawn_rec()

### Community 55 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 56 - "hermes_home"
Cohesion: 0.22
Nodes (9): hermes_home(), hermes_root(), profile_home(), profiles_root(), The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a…, Read model.workflows_forbidden_models on the child seat, including bare CLI…, `WF_RUNS_ROOT` if set (non-empty), else `$HERMES_HOME/workflows`., runs_root() (+1 more)

### Community 58 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 59 - "amend"
Cohesion: 0.25
Nodes (8): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, What you get, amend()

### Community 60 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 61 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 62 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 63 - "Run operations and read model"
Cohesion: 0.29
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 64 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 66 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 67 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 68 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 69 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 70 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 71 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 72 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 74 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 78 - "3. Operate"
Cohesion: 0.40
Nodes (5): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run

### Community 79 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 80 - "Graph grammar and authoring boundaries"
Cohesion: 0.40
Nodes (4): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay

### Community 82 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 83 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 84 - "profile_errors"
Cohesion: 0.40
Nodes (4): launcher_profile(), profile_errors(), Launcher identity, resolved from the door's OWN HERMES_HOME — never from a…, 1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER…

### Community 85 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 86 - ".states"
Cohesion: 0.67
Nodes (3): deps_ok(), dep_satisfied(), deps_ok()

### Community 89 - "node_child_home"
Cohesion: 0.50
Nodes (4): node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as…

## Knowledge Gaps
- **225 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+220 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 725 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.397) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.384) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _225 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.07346938775510205 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.07729468599033816 - nodes in this community are weakly interconnected._
- **Should `plugin_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08253968253968254 - nodes in this community are weakly interconnected._