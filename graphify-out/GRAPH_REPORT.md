# Graph Report - tree  (2026-09-26)

## Corpus Check
- 90 files · ~123,516 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1081 nodes · 2153 edges · 63 communities (48 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 124 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- __init__.py
- wf.py
- plugin_api.py
- wfcommon.py
- test_fanout_expand.mjs
- CurrentAttemptMetrics
- jload
- test_fanout_item_goal.py
- test_prompt_workdir.py
- json
- test_tiers.py
- importlib_util
- sys
- os
- test_sprint101w2_C3-fanout-gates.py
- tempfile
- test_live_truth_ui.mjs
- test_register_surface.mjs
- EngineNextCut
- ref_node_fs
- pathlib
- test_canvas_wrap.mjs
- run_agent_node
- test_edge_routing.mjs
- test_session_strip.mjs
- efp
- LiveTruth
- test_node_panel.mjs
- test_orphan_adopt_790c6ad.py
- validate_graph_errors
- test_metrics_missing_ui.mjs
- subprocess
- CardBackend
- test_deleted_cwd_resume_5c37b19.py
- test_card_frontend_contract.mjs
- Contributing to hermes-workflows
- test_sprint101w2_B2-retry.py
- _SV
- AGENTS.md — front door for agents
- test_engine.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- Hermes Workflows
- test_lifecycle_next_cut_0923.py
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_steer_live_40.py
- AGENTS.md
- 3. Operate
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Manual installation — Hermes Workflows 0.9.0
- graph_check.py
- test_prune_0923.py
- test_v3_fixes.py
- test_waitgate_0923.py
- child_metrics
- Patched core: typed turn-cap deaths (optional)
- manifest.json
- Integrated
- FakeProcess
- Run
- fake

## God Nodes (most connected - your core abstractions)
1. `efp()` - 31 edges
2. `jload()` - 28 edges
3. `run_child()` - 26 edges
4. `main()` - 20 edges
5. `run_state()` - 20 edges
6. `_adopt_child()` - 19 edges
7. `NodePanel()` - 18 edges
8. `CurrentAttemptMetrics` - 18 edges
9. `loop()` - 18 edges
10. `EngineNextCut` - 16 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Run and handoff` --references--> `node_facts()`  [INFERRED]
  SKILL.md → wfcommon.py
- `Nodes and data` --references--> `build()`  [INFERRED]
  references/grammar.md → scripts/pack.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `Run operations and read model` --references--> `blocked_by()`  [INFERRED]
  references/operations.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (63 total, 15 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "__init__.py"
Cohesion: 0.05
Nodes (69): difflib, act_amend(), act_inbox(), act_library(), act_list(), act_release(), act_run(), act_save() (+61 more)

### Community 2 - "wf.py"
Cohesion: 0.05
Nodes (64): concurrent_futures, What the plugin gains, fcntl, _adopt_child(), _AdoptedHandle, build_inputs(), _child_spoke(), child_work_dir() (+56 more)

### Community 3 - "plugin_api.py"
Cohesion: 0.06
Nodes (40): asyncio, 0.9.0 — 2026-09-24, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, Added, Additions, Archify: no (verdict + evidence), SMIL for candy (+32 more)

### Community 4 - "wfcommon.py"
Cohesion: 0.07
Nodes (40): shlex, deps_ok(), _active_spawn(), _active_spawns(), amend_preview(), blocked_by(), current_attempt(), dep_satisfied() (+32 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "CurrentAttemptMetrics"
Cohesion: 0.16
Nodes (9): Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Run and handoff, Smallest working graph, Workflow authoring (1.0.2) (+1 more)

### Community 7 - "jload"
Cohesion: 0.12
Nodes (27): acquire_lock(), _bounded_retry(), emit(), finalize(), log(), main(), consume_markers(), loop() (+19 more)

### Community 8 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 9 - "test_prompt_workdir.py"
Cohesion: 0.11
Nodes (23): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+15 more)

### Community 10 - "json"
Cohesion: 0.10
Nodes (9): json, shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+1 more)

### Community 11 - "test_tiers.py"
Cohesion: 0.09
Nodes (9): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v(), Ctx, Ctx (+1 more)

### Community 12 - "importlib_util"
Cohesion: 0.10
Nodes (8): contextlib, importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Current-attempt heartbeat with real fake child identity; no provider access., Runner identity and truthful public read paths; fixture home is isolated here., Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…, unittest_mock

### Community 13 - "sys"
Cohesion: 0.11
Nodes (16): copy, glob, hashlib, hermes_constants, re, sys, Regression: launch a run in the tool's session; the payload carries a parser-…, Engine branch contracts, exercised by the actual runner and fake CLI (no… (+8 more)

### Community 14 - "os"
Cohesion: 0.11
Nodes (8): os, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., Integrated read-model and parser-valid card dedup checks., Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…, time

### Community 15 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.09
Nodes (7): Ctx, Deterministic regressions for explicit workflow provider/model routing., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, threading

### Community 16 - "tempfile"
Cohesion: 0.10
Nodes (8): tempfile, Authoring door regressions; all state stays in this worktree, no…, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…, err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 17 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 18 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 19 - "EngineNextCut"
Cohesion: 0.20
Nodes (3): Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), EngineNextCut

### Community 20 - "ref_node_fs"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 21 - "pathlib"
Cohesion: 0.13
Nodes (8): pathlib, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…

### Community 22 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 23 - "run_agent_node"
Cohesion: 0.15
Nodes (15): _dangling_placeholders(), fmt_goal(), Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported…, run_agent_node(), _cancel_stragglers() (+7 more)

### Community 24 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 25 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 26 - "efp"
Cohesion: 0.19
Nodes (15): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer(), mirror(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run… (+7 more)

### Community 28 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 29 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.15
Nodes (8): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 30 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): apply_graph_defaults(), _defaults_errors(), Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, reasoning_levels() (+4 more)

### Community 31 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 32 - "subprocess"
Cohesion: 0.15
Nodes (5): Serial bounded suite with durable per-case logs and atomic exit ledger., subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph()

### Community 35 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 36 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 37 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 39 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 40 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 41 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (6): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is

### Community 42 - "Hermes Workflows"
Cohesion: 0.29
Nodes (7): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get

### Community 46 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 48 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 49 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 50 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 51 - "Manual installation — Hermes Workflows 0.9.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 0.9.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 52 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 56 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 57 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.40
Nodes (5): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds

### Community 58 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

## Knowledge Gaps
- **179 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+174 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 568 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EngineNextCut` connect `EngineNextCut` to `sys`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `efp()` connect `efp` to `subprocess`, `__init__.py`, `test_deleted_cwd_resume_5c37b19.py`, `wf.py`, `wfcommon.py`, `jload`, `test_tiers.py`, `test_review_fixes.py`, `sys`, `test_sprint101w2_C3-fanout-gates.py`, `tempfile`, `4. Contribute`, `run_agent_node`, `test_orphan_adopt_790c6ad.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `4a. Map` connect `4. Contribute` to `efp`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _179 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06538987688098495 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053208137715179966 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.048846675712347354 - nodes in this community are weakly interconnected._