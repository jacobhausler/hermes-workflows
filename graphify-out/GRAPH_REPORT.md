# Graph Report - tree  (2026-09-29)

## Corpus Check
- 130 files · ~178,518 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1523 nodes · 3067 edges · 98 communities (83 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 190 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- os
- pathlib
- test_preflight_liveness_152be7f7.py
- test_prompt_workdir.py
- sys
- test_fanout_expand.mjs
- wfcommon.py
- test_11_ui_imports.mjs
- run_agent_node
- json
- time
- test_fanout_item_goal.py
- jload
- test_sprint101w2_C3-fanout-gates.py
- run_child
- subprocess
- wf.py
- main
- _adopt_child
- importlib_util
- efp
- test_route_efforts_b3c98b2a.py
- ref_node_fs
- test_live_truth_ui.mjs
- test_pill_rail_expand.mjs
- CurrentAttemptMetrics
- Run operations and read model
- plugin_api.py
- __init__.py
- _ping_route_once
- test
- test_register_surface.mjs
- test_validate_0923.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- test_session_strip.mjs
- hermes_home
- _SV
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- _resolve_models
- test_orphan_adopt_790c6ad.py
- act_amend
- SKILL.md
- validate_graph_errors
- test_sprint101w2_D2-steer-liveness.py
- test_pill_rail.mjs
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- Changelog
- act_save
- test_card_frontend_contract.mjs
- AGENTS.md
- test_node_facts.py
- Contributing to hermes-workflows
- act_run
- TeamIntegration
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- model_preflight
- CoreFaithfulCtx
- test_status_next.py
- test_steer_live_40.py
- hermes_home
- _defaults_errors
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Manual installation — Hermes Workflows 1.1.0
- Hermes Workflows
- graph_check.py
- DoorLane
- test_suite_admission_17.py
- 1.0.1 — 2026-09-25
- node_facts
- _bind_run_context
- 11-golden-solo.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- _LADDER
- Integrated
- Run
- release_gate
- Ctx
- Ctx
- Ctx
- fake

## God Nodes (most connected - your core abstractions)
1. `jload()` - 35 edges
2. `efp()` - 35 edges
3. `run_child()` - 31 edges
4. `_adopt_child()` - 22 edges
5. `run_state()` - 22 edges
6. `main()` - 21 edges
7. `loop()` - 21 edges
8. `act_run()` - 20 edges
9. `NodePanel()` - 18 edges
10. `CurrentAttemptMetrics` - 18 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (98 total, 15 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): Unreleased, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "os"
Cohesion: 0.06
Nodes (16): os, shutil, Identical solo child wrapper for both tag and candidate; records env key sets.…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run… (+8 more)

### Community 2 - "pathlib"
Cohesion: 0.08
Nodes (25): contextlib, copy, hashlib, pathlib, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.… (+17 more)

### Community 3 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 4 - "test_prompt_workdir.py"
Cohesion: 0.08
Nodes (30): argparse, fnmatch, Pattern, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, excluded() (+22 more)

### Community 5 - "sys"
Cohesion: 0.07
Nodes (16): atexit, fcntl, importlib, sys, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>. (+8 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "wfcommon.py"
Cohesion: 0.08
Nodes (30): shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), _downstream(), effective_runs_root(), launch_runs_root() (+22 more)

### Community 8 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 9 - "run_agent_node"
Cohesion: 0.09
Nodes (26): 1.0.17 — 2026-09-28, _bounded_retry(), _dangling_placeholders(), fmt_goal(), _lane_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+18 more)

### Community 10 - "json"
Cohesion: 0.09
Nodes (10): json, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr() (+2 more)

### Community 11 - "time"
Cohesion: 0.07
Nodes (7): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, time

### Community 12 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 13 - "jload"
Cohesion: 0.14
Nodes (24): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, ONE gate-answer path for tool and UI. Stale answers never block: the answer… (+16 more)

### Community 14 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 15 - "run_child"
Cohesion: 0.09
Nodes (26): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+18 more)

### Community 16 - "subprocess"
Cohesion: 0.08
Nodes (9): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, subprocess, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;… (+1 more)

### Community 17 - "wf.py"
Cohesion: 0.12
Nodes (23): concurrent_futures, build_inputs(), extract_json(), _inputs_block(), last_balanced_object(), _match_object(), _quota_cache_path(), _quota_note() (+15 more)

### Community 18 - "main"
Cohesion: 0.14
Nodes (22): acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), log(), main(), consume_markers() (+14 more)

### Community 19 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 20 - "importlib_util"
Cohesion: 0.09
Nodes (9): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes. (+1 more)

### Community 21 - "efp"
Cohesion: 0.15
Nodes (22): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+14 more)

### Community 22 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.10
Nodes (12): agent_reasoning_effort, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, core(), Ctx, fake() (+4 more)

### Community 23 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 24 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 25 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 27 - "Run operations and read model"
Cohesion: 0.13
Nodes (16): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Lanes: in-flight dedupe for pollers (+8 more)

### Community 28 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 29 - "__init__.py"
Cohesion: 0.16
Nodes (17): difflib, act_library(), handle(), _lane_key_error(), _lane_state(), _last_event_ts(), library_root(), _library_roots() (+9 more)

### Community 30 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+9 more)

### Community 31 - "test"
Cohesion: 0.16
Nodes (17): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), active_child(), fingerprint_valid(), gate_answer_valid() (+9 more)

### Community 32 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 33 - "test_validate_0923.py"
Cohesion: 0.12
Nodes (9): glob, hermes_constants, plugin_api, re, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, #32 publish-as-file: the portable workflow file convention. (1) top-level…, Portable authoring skill contract; no provider or live-home dependencies., mkrun() (+1 more)

### Community 34 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 35 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 36 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 37 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 39 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 40 - "hermes_home"
Cohesion: 0.12
Nodes (16): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), find_run(), hermes_home(), hermes_root() (+8 more)

### Community 41 - "_SV"
Cohesion: 0.14
Nodes (9): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not() (+1 more)

### Community 42 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 44 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 45 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 46 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 47 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 48 - "act_amend"
Cohesion: 0.15
Nodes (13): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+5 more)

### Community 49 - "SKILL.md"
Cohesion: 0.17
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 50 - "validate_graph_errors"
Cohesion: 0.17
Nodes (11): _v(), grammar_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, requires_errors(), validate_graph_errors() (+3 more)

### Community 51 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.15
Nodes (4): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission., Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…

### Community 52 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 53 - "_create_run"
Cohesion: 0.20
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.… (+3 more)

### Community 55 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 56 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 57 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline… (+3 more)

### Community 58 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 59 - "AGENTS.md"
Cohesion: 0.24
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 60 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 61 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 62 - "act_run"
Cohesion: 0.24
Nodes (10): act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty…, WRITE side: the resolved root (new entries land with their runs)., WRITE resolver: always the resolved root (current best version lands there). (+2 more)

### Community 64 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 65 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 66 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 67 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 68 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 69 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 70 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 71 - "hermes_home"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 72 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 73 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 74 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 75 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 76 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 77 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 78 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 80 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 81 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 82 - "node_facts"
Cohesion: 0.40
Nodes (5): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.…

### Community 83 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 84 - "11-golden-solo.py"
Cohesion: 0.70
Nodes (4): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…

### Community 87 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 88 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 89 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 93 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **242 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+237 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 790 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Unreleased` connect `plugin.js` to `Changelog`, `_resolve_models`?**
  _High betweenness centrality (0.350) - this node is a cross-community bridge._
- **Why does `_resolve_models()` connect `_resolve_models` to `plugin.js`, `model_preflight`, `act_amend`, `__init__.py`, `act_run`?**
  _High betweenness centrality (0.292) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _242 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.05647840531561462 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.08013937282229965 - nodes in this community are weakly interconnected._