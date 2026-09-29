# Graph Report - tree  (2026-09-29)

## Corpus Check
- 159 files · ~189,890 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1584 nodes · 3133 edges · 105 communities (78 shown, 27 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 211 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- CurrentAttemptMetrics
- wfcommon.py
- __init__.py
- jload
- run_state
- test_fanout_expand.mjs
- Changelog
- plugin_api.py
- test_prompt_workdir.py
- importlib_util
- json
- Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet
- test_11_ui_imports.mjs
- test_fanout_item_goal.py
- wf.py
- shutil
- efp
- tempfile
- time
- subprocess
- _adopt_child
- run_child
- test_failures_0923.py
- test_preflight_liveness_152be7f7.py
- ref_node_fs
- test_live_truth_ui.mjs
- test_pill_rail_expand.mjs
- os
- sys
- test_sprint101w2_D2-steer-liveness.py
- test_register_surface.mjs
- log
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- _ping_route_once
- pathlib
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- test_require_route_25.py
- test_orphan_adopt_790c6ad.py
- test_pill_rail.mjs
- hermes_home
- test_route_efforts_b3c98b2a.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- build_inputs
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- test_validate_0923.py
- TeamIntegration
- test_sprint101w2_B2-retry.py
- _SV
- AGENTS.md — front door for agents
- Disclosure verification — clause-by-clause evidence
- test_engine.py
- test_routing_routes.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- CoreFaithfulCtx
- test_lane_gate_64c6772b.py
- test_steer_live_40.py
- hermes_home
- AGENTS.md
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Manual installation — Hermes Workflows 1.1.0
- Hermes Workflows
- DoorLane
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tiers.py
- test_v3_fixes.py
- child_metrics
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- _quota_note
- Run
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
1. `jload()` - 35 edges
2. `efp()` - 35 edges
3. `run_child()` - 31 edges
4. `_adopt_child()` - 22 edges
5. `loop()` - 22 edges
6. `run_state()` - 22 edges
7. `log()` - 21 edges
8. `main()` - 21 edges
9. `act_run()` - 20 edges
10. `NodePanel()` - 18 edges

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

## Communities (105 total, 27 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): Unreleased, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "CurrentAttemptMetrics"
Cohesion: 0.06
Nodes (28): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Contributor checks (not ordinary user setup) (+20 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.04
Nodes (58): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, shlex, amend_preview(), apply_graph_defaults(), blocked_by(), current_attempt(), _defaults_errors(), _downstream() (+50 more)

### Community 3 - "__init__.py"
Cohesion: 0.06
Nodes (60): difflib, act_amend(), act_library(), act_run(), act_save(), _alias_provider_pair(), _coerce_graph(), _frozen_committed() (+52 more)

### Community 4 - "jload"
Cohesion: 0.09
Nodes (38): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), acquire_lock(), emit(), finalize(), main() (+30 more)

### Community 5 - "run_state"
Cohesion: 0.09
Nodes (35): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _card(), _create_run() (+27 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "Changelog"
Cohesion: 0.06
Nodes (32): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+24 more)

### Community 8 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 9 - "test_prompt_workdir.py"
Cohesion: 0.10
Nodes (26): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+18 more)

### Community 10 - "importlib_util"
Cohesion: 0.08
Nodes (14): hashlib, importlib_util, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Library verbs + /wf command: save (from run_id / inline), library list, run…, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks. (+6 more)

### Community 11 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 12 - "Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet"
Cohesion: 0.09
Nodes (27): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+19 more)

### Community 13 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 14 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 15 - "wf.py"
Cohesion: 0.09
Nodes (25): concurrent_futures, _dangling_placeholders(), drain_inbox(), extract_json(), _fail_precondition(), _lane_gate(), last_balanced_object(), _match_object() (+17 more)

### Community 16 - "shutil"
Cohesion: 0.08
Nodes (8): fcntl, shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…

### Community 17 - "efp"
Cohesion: 0.13
Nodes (25): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+17 more)

### Community 18 - "tempfile"
Cohesion: 0.09
Nodes (12): signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), Lane E: cross-lane executable integration fixtures; no production…, Authoring door regressions; all state stays in this worktree, no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+4 more)

### Community 19 - "time"
Cohesion: 0.08
Nodes (7): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, time

### Community 20 - "subprocess"
Cohesion: 0.11
Nodes (13): contextlib, copy, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness. (+5 more)

### Community 21 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 22 - "run_child"
Cohesion: 0.10
Nodes (24): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+16 more)

### Community 23 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 24 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 25 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 26 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 27 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 28 - "os"
Cohesion: 0.11
Nodes (8): os, admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 4052d57719653b1a: atomic library replay binding, no real runner.

### Community 29 - "sys"
Cohesion: 0.11
Nodes (7): sys, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 30 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.13
Nodes (8): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…, unittest_mock

### Community 31 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 32 - "log"
Cohesion: 0.19
Nodes (17): _bounded_retry(), log(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Commit actual child seat truth, never the requested alias. No row means unknown., run_agent_node() (+9 more)

### Community 33 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 34 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 35 - "_ping_route_once"
Cohesion: 0.12
Nodes (15): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+7 more)

### Community 36 - "pathlib"
Cohesion: 0.19
Nodes (12): pathlib, re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), _fake_state_row() (+4 more)

### Community 37 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 38 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 39 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 41 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 42 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 43 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 44 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 45 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 46 - "hermes_home"
Cohesion: 0.17
Nodes (12): hermes_home(), hermes_root(), launcher_profile(), profile_errors(), profile_home(), profiles_root(), Read model.workflows_forbidden_models on the child seat, including bare CLI…, The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a… (+4 more)

### Community 47 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 49 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 50 - "build_inputs"
Cohesion: 0.18
Nodes (10): 1.0.17 — 2026-09-28, 3. The importable subset, stated once, build_inputs(), fmt_goal(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block… (+2 more)

### Community 51 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 52 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 53 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 54 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 56 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 58 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 59 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.25
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 60 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 61 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 62 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 63 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 64 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 65 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 66 - "hermes_home"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 68 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 69 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 70 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 71 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 72 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 73 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 75 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 76 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 79 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 80 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 81 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 84 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 85 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 86 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 89 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

## Knowledge Gaps
- **271 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+266 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 831 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `label()` connect `plugin.js` to `test_card_frontend_contract.mjs`, `Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `2. The mapping table` connect `Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet` to `plugin.js`, `CurrentAttemptMetrics`, `log`?**
  _High betweenness centrality (0.197) - this node is a cross-community bridge._
- **Why does `Unreleased` connect `plugin.js` to `__init__.py`, `Changelog`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _271 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.05789235639981909 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0449497620306716 - nodes in this community are weakly interconnected._