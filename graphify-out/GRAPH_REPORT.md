# Graph Report - tree  (2026-09-28)

## Corpus Check
- 106 files · ~139,641 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1251 nodes · 2494 edges · 81 communities (66 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 144 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- test_prompt_workdir.py
- test_fanout_expand.mjs
- pathlib
- os
- plugin_api.py
- CurrentAttemptMetrics
- test_fanout_item_goal.py
- log
- jload
- sys
- efp
- __init__.py
- test_card_frontend_contract.mjs
- Changelog
- test_live_truth_ui.mjs
- test_register_surface.mjs
- importlib_util
- subprocess
- EngineNextCut
- shutil
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- act_amend
- runner_alive
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- AGENTS.md
- LiveTruth
- test_node_panel.mjs
- Hermes Workflows
- test_sprint101_A-door.py
- test_orphan_adopt_790c6ad.py
- test_preflight_liveness_152be7f7.py
- 3. Operate
- act_run
- test_metrics_missing_ui.mjs
- test_route_efforts_b3c98b2a.py
- test_deleted_cwd_resume_5c37b19.py
- test_amend_rebake_034849a2.py
- _stamp_served
- Contributing to hermes-workflows
- FakeHTTPError
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_fanout_ui.mjs
- test_fp_rule_f0f154d5.py
- test_sprint101w2_B2-retry.py
- test_engine.py
- model_preflight
- Disclosure verification — clause-by-clause evidence
- CoreFaithfulCtx
- test_lifecycle_next_cut_0923.py
- test_review_fixes.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Manual installation — Hermes Workflows 1.0.11
- test_model_law_dad50be0.py
- test_tier_report_0924.py
- test_tiers.py
- test_v3_fixes.py
- test_v5_fixes.py
- _bind_run_context
- test_papercuts_0922.py
- test_safe_root_workdir.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- write_spawn_record
- manifest.json
- Run operations and read model
- Integrated
- FakeProcess
- Run
- fake

## God Nodes (most connected - your core abstractions)
1. `efp()` - 33 edges
2. `jload()` - 31 edges
3. `run_child()` - 28 edges
4. `_adopt_child()` - 21 edges
5. `main()` - 21 edges
6. `run_state()` - 21 edges
7. `loop()` - 19 edges
8. `NodePanel()` - 18 edges
9. `CurrentAttemptMetrics` - 18 edges
10. `act_run()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `4. State location` --references--> `runs_root()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)` --references--> `model_preflight()`  [INFERRED]
  CHANGELOG.md → __init__.py

## Import Cycles
- None detected.

## Communities (81 total, 15 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "wf.py"
Cohesion: 0.05
Nodes (59): concurrent_futures, fcntl, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output() (+51 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.06
Nodes (39): shlex, _active_spawn(), amend_preview(), apply_graph_defaults(), current_attempt(), _defaults_errors(), _downstream(), quote_json_parse_error() (+31 more)

### Community 3 - "test_prompt_workdir.py"
Cohesion: 0.08
Nodes (35): argparse, fnmatch, hashlib, Pattern, re, Nodes and data, _ast(), main() (+27 more)

### Community 4 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 5 - "pathlib"
Cohesion: 0.10
Nodes (17): contextlib, copy, json, pathlib, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, tempfile, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session; the payload carries a parser-… (+9 more)

### Community 6 - "os"
Cohesion: 0.07
Nodes (16): glob, hermes_constants, os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+8 more)

### Community 7 - "plugin_api.py"
Cohesion: 0.10
Nodes (23): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+15 more)

### Community 8 - "CurrentAttemptMetrics"
Cohesion: 0.18
Nodes (9): Explorer V2: one node truth, two readers, Run and handoff, Smallest working graph, Workflow authoring (1.0.11), CurrentAttemptMetrics, node_facts(), Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node… (+1 more)

### Community 9 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 10 - "log"
Cohesion: 0.12
Nodes (25): _bounded_retry(), build_inputs(), _dangling_placeholders(), _inputs_block(), log(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+17 more)

### Community 11 - "jload"
Cohesion: 0.15
Nodes (24): ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), _active_spawns(), def_hash() (+16 more)

### Community 12 - "sys"
Cohesion: 0.09
Nodes (9): sys, Ctx, Deterministic regressions for explicit workflow provider/model routing., Portable authoring skill contract; no provider or live-home dependencies., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 13 - "efp"
Cohesion: 0.13
Nodes (23): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), finalize(), main() (+15 more)

### Community 14 - "__init__.py"
Cohesion: 0.12
Nodes (22): difflib, act_inbox(), act_steer(), _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status() (+14 more)

### Community 15 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 16 - "Changelog"
Cohesion: 0.10
Nodes (20): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+12 more)

### Community 17 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 18 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 19 - "importlib_util"
Cohesion: 0.11
Nodes (5): importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, 4052d57719653b1a: atomic library replay binding, no real runner., Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…

### Community 20 - "subprocess"
Cohesion: 0.11
Nodes (6): subprocess, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 21 - "EngineNextCut"
Cohesion: 0.21
Nodes (4): EngineNextCut, deps_ok(), dep_satisfied(), deps_ok()

### Community 22 - "shutil"
Cohesion: 0.11
Nodes (5): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…

### Community 23 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 24 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 25 - "act_amend"
Cohesion: 0.13
Nodes (16): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _liveness_hint_suffix(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 26 - "runner_alive"
Cohesion: 0.17
Nodes (14): act_release(), act_status(), act_stop(), act_wait(), _card(), _output_pointer(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid… (+6 more)

### Community 27 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+8 more)

### Community 28 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 29 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 30 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 31 - "AGENTS.md"
Cohesion: 0.16
Nodes (6): Node budgets, Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay

### Community 33 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 34 - "Hermes Workflows"
Cohesion: 0.14
Nodes (14): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, For agents and contributors, Hermes Workflows (+6 more)

### Community 35 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 36 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.15
Nodes (8): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 37 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.21
Nodes (13): check(), contract(), fake_call_llm(), call_llm(), _fake_parse_retry_after(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.… (+5 more)

### Community 38 - "3. Operate"
Cohesion: 0.15
Nodes (13): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+5 more)

### Community 39 - "act_run"
Cohesion: 0.21
Nodes (12): act_library(), act_list(), act_run(), _hermes_bin(), _lib_path(), library_root(), `/wf` — the library front door. `/wf <name> [note]` supplies the note…, Operator-controlled launcher; tool arguments never choose a child executable.… (+4 more)

### Community 40 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 41 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 43 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 44 - "_stamp_served"
Cohesion: 0.18
Nodes (11): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Commit actual child seat truth, never the requested alias. No row means unknown., Tool-progress evidence for the #5 bounded retry: True only when the dead…, _stamp_served(), _tool_progress(), child_metrics() (+3 more)

### Community 45 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 46 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): Exception, EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 47 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 48 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 49 - "test_fp_rule_f0f154d5.py"
Cohesion: 0.33
Nodes (8): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 50 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 51 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 52 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 53 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.29
Nodes (7): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle()

### Community 54 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 59 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 60 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 61 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 62 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 63 - "Manual installation — Hermes Workflows 1.0.11"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.0.11, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 64 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 69 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 71 - "test_safe_root_workdir.py"
Cohesion: 0.70
Nodes (4): check(), main(), fb 625a3241cfcc9dee — the child's advertised durable work dir is writable under…, run_graph()

### Community 72 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 73 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 74 - "write_spawn_record"
Cohesion: 0.40
Nodes (5): _node_file(), B1 (feedback #13/#40): at spawn, copy every inbox line addressed to this node…, Q1 spawn-time record: written right after Popen succeeds, BEFORE the child is…, _steer_bake(), write_spawn_record()

### Community 75 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 76 - "Run operations and read model"
Cohesion: 0.50
Nodes (4): Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

## Knowledge Gaps
- **201 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 649 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`, `plugin-catalog: add `hermes-workflows` (community, automation)`?**
  _High betweenness centrality (0.397) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.392) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05222734254992319 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05697278911564626 - nodes in this community are weakly interconnected._
- **Should `test_prompt_workdir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07564102564102564 - nodes in this community are weakly interconnected._