# Graph Report - tree  (2026-09-28)

## Corpus Check
- 104 files · ~139,934 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1255 nodes · 2505 edges · 80 communities (64 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 145 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- efp
- test_amend_rebake_034849a2.py
- plugin_api.py
- test_fanout_expand.mjs
- wfcommon.py
- os
- Changelog
- subprocess
- test_fanout_item_goal.py
- sys
- test_prompt_workdir.py
- test_preflight_liveness_152be7f7.py
- test_card_frontend_contract.mjs
- importlib_util
- test_live_truth_ui.mjs
- test_v5_fixes.py
- test_register_surface.mjs
- run_agent_node
- test_failures_0923.py
- CurrentAttemptMetrics
- runner_alive
- __init__.py
- graph_check.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- _resolve_models
- json
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- test_session_strip.mjs
- LiveTruth
- test_node_panel.mjs
- AGENTS.md
- 4. Contribute
- test_orphan_adopt_790c6ad.py
- pathlib
- validate_graph_errors
- act_run
- test_metrics_missing_ui.mjs
- node_facts
- test_deleted_cwd_resume_5c37b19.py
- act_save
- Contributing to hermes-workflows
- test_validate_0923.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_fanout_ui.mjs
- test_sprint101w2_B2-retry.py
- _stamp_served
- _SV
- test_engine.py
- model_preflight
- Disclosure verification — clause-by-clause evidence
- act_amend
- act_steer
- test_fp_rule_f0f154d5.py
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C3-fanout-gates.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Manual installation — Hermes Workflows 1.0.17
- Hermes Workflows
- test_packaging.py
- test_tier_report_0924.py
- 3. Operate
- _bind_run_context
- manifest.json
- test_fp_rule_95d70102.py
- Integrated
- _AdoptedHandle
- Run
- fake
- drain_inbox
- chk

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
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (80 total, 16 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "wf.py"
Cohesion: 0.06
Nodes (65): concurrent_futures, _adopt_child(), _bounded_retry(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+57 more)

### Community 2 - "efp"
Cohesion: 0.09
Nodes (43): test(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), finalize() (+35 more)

### Community 3 - "test_amend_rebake_034849a2.py"
Cohesion: 0.05
Nodes (20): agent_reasoning_effort, atexit, importlib, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;… (+12 more)

### Community 4 - "plugin_api.py"
Cohesion: 0.08
Nodes (25): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+17 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "wfcommon.py"
Cohesion: 0.09
Nodes (31): shlex, _active_spawn(), _active_spawns(), amend_preview(), blocked_by(), current_attempt(), _downstream(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE… (+23 more)

### Community 7 - "os"
Cohesion: 0.08
Nodes (11): fcntl, os, shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, The child launcher is operator-controlled, never a tool argument., Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, 4052d57719653b1a: atomic library replay binding, no real runner. (+3 more)

### Community 8 - "Changelog"
Cohesion: 0.07
Nodes (26): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes (+18 more)

### Community 9 - "subprocess"
Cohesion: 0.10
Nodes (15): contextlib, copy, subprocess, tempfile, Regression: launch a run in the tool's session; the payload carries a parser-…, Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+7 more)

### Community 10 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 11 - "sys"
Cohesion: 0.10
Nodes (9): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., Integrated read-model and parser-valid card dedup checks., Library verbs + /wf command: save (from run_id / inline), library list, run…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship… (+1 more)

### Community 12 - "test_prompt_workdir.py"
Cohesion: 0.13
Nodes (21): argparse, hashlib, Nodes and data, build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only). (+13 more)

### Community 13 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.12
Nodes (21): Exception, check(), contract(), EscapeLineOnly, fake_call_llm(), call_llm(), _fake_parse_retry_after(), FakeHTTPError (+13 more)

### Community 14 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 15 - "importlib_util"
Cohesion: 0.10
Nodes (7): importlib_util, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 16 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 17 - "test_v5_fixes.py"
Cohesion: 0.10
Nodes (7): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing., Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 18 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 19 - "run_agent_node"
Cohesion: 0.13
Nodes (19): build_inputs(), _dangling_placeholders(), _inputs_block(), Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING… (+11 more)

### Community 20 - "test_failures_0923.py"
Cohesion: 0.11
Nodes (6): sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 22 - "runner_alive"
Cohesion: 0.15
Nodes (16): act_release(), act_status(), act_stop(), act_wait(), _card(), _output_pointer(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, ONE gate-answer path for tool and UI. Stale answers never block: the answer… (+8 more)

### Community 23 - "__init__.py"
Cohesion: 0.16
Nodes (15): difflib, _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+7 more)

### Community 24 - "graph_check.py"
Cohesion: 0.17
Nodes (14): fnmatch, Pattern, re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig() (+6 more)

### Community 25 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 26 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 27 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+8 more)

### Community 28 - "json"
Cohesion: 0.12
Nodes (4): json, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…

### Community 29 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 30 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 32 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 34 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 35 - "AGENTS.md"
Cohesion: 0.18
Nodes (6): Node budgets, Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay

### Community 36 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 37 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.15
Nodes (8): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 38 - "pathlib"
Cohesion: 0.14
Nodes (6): pathlib, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 39 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): apply_graph_defaults(), _defaults_errors(), Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, reasoning_levels() (+4 more)

### Community 40 - "act_run"
Cohesion: 0.21
Nodes (12): act_library(), act_list(), act_run(), _hermes_bin(), _lib_path(), library_root(), `/wf` — the library front door. `/wf <name> [note]` supplies the note…, Operator-controlled launcher; tool arguments never choose a child executable.… (+4 more)

### Community 41 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 42 - "node_facts"
Cohesion: 0.18
Nodes (11): 3d. Failures, resume, amend, Explorer V2: one node truth, two readers, What you get, Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), Run and handoff, Smallest working graph, Workflow authoring (1.0.17) (+3 more)

### Community 44 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Choose one explicitly supplied source; never discover files on the caller's… (+3 more)

### Community 45 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 46 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 47 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 48 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 49 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 50 - "_stamp_served"
Cohesion: 0.22
Nodes (9): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Commit actual child seat truth, never the requested alias. No row means unknown., _stamp_served(), child_metrics(), Read model.workflows_forbidden_models on the child seat, including bare CLI…, {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,… (+1 more)

### Community 52 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 53 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 54 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.29
Nodes (7): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle()

### Community 55 - "act_amend"
Cohesion: 0.29
Nodes (7): act_amend(), _frozen_committed(), _liveness_hint_suffix(), fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, _route_liveness_ping()

### Community 56 - "act_steer"
Cohesion: 0.29
Nodes (7): act_inbox(), act_steer(), Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, _steer_event(), _steer_lines()

### Community 57 - "test_fp_rule_f0f154d5.py"
Cohesion: 0.48
Nodes (6): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 58 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 63 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 64 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 65 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 66 - "Manual installation — Hermes Workflows 1.0.17"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.0.17, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 67 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 68 - "test_packaging.py"
Cohesion: 0.40
Nodes (5): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., types, zipfile

### Community 70 - "3. Operate"
Cohesion: 0.40
Nodes (5): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run

### Community 71 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 72 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 73 - "test_fp_rule_95d70102.py"
Cohesion: 0.67
Nodes (3): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change.

## Knowledge Gaps
- **200 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+195 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 650 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`, `plugin-catalog: add `hermes-workflows` (community, automation)`?**
  _High betweenness centrality (0.395) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.387) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _200 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05827505827505827 - nodes in this community are weakly interconnected._
- **Should `efp` be split into smaller, more focused modules?**
  _Cohesion score 0.09393939393939393 - nodes in this community are weakly interconnected._
- **Should `test_amend_rebake_034849a2.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05426356589147287 - nodes in this community are weakly interconnected._