# Graph Report - tree  (2026-09-26)

## Corpus Check
- 84 files · ~115,207 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1001 nodes · 1962 edges · 62 communities (47 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Graph View UI Components
- __init__.py
- wfcommon.py
- sys
- time
- test_fanout_expand.mjs
- test_prompt_workdir.py
- json
- plugin_api.py
- run_child
- pathlib
- wf.py
- test_live_truth_ui.mjs
- main
- importlib_util
- test_register_surface.mjs
- CurrentAttemptMetrics
- EngineNextCut
- log
- ref_node_fs
- test_canvas_wrap.mjs
- 1.1.0 — 2026-09-26 — the run watches itself
- test_edge_routing.mjs
- test_session_strip.mjs
- efp
- LiveTruth
- test_node_panel.mjs
- 3. Operate
- AGENTS.md
- test_metrics_missing_ui.mjs
- CardBackend
- test_card_frontend_contract.mjs
- Contributing to hermes-workflows
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- Hermes Workflows
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_status_next.py
- test_steer_live_40.py
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Manual installation — Hermes Workflows 0.9.0
- graph_check.py
- test_prune_0923.py
- test_tier_report_0924.py
- test_v3_fixes.py
- child_metrics
- Patched core: typed turn-cap deaths (optional)
- Run operations and read model
- test_sprint101_D-surface.py
- validate
- manifest.json
- Graph grammar and authoring boundaries
- Integrated
- Run
- Ctx
- Ctx
- Ctx
- fake

## God Nodes (most connected - your core abstractions)
1. `efp()` - 29 edges
2. `run_child()` - 26 edges
3. `jload()` - 25 edges
4. `main()` - 20 edges
5. `run_state()` - 20 edges
6. `NodePanel()` - 18 edges
7. `CurrentAttemptMetrics` - 18 edges
8. `loop()` - 18 edges
9. `EngineNextCut` - 16 edges
10. `GraphView()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Run and handoff` --references--> `node_facts()`  [INFERRED]
  SKILL.md → wfcommon.py
- `Explorer V2: one node truth, two readers` --references--> `_view()`  [INFERRED]
  CHANGELOG.md → dashboard/plugin_api.py
- `Nodes and data` --references--> `build()`  [INFERRED]
  references/grammar.md → scripts/pack.py
- `Run operations and read model` --references--> `node_facts()`  [INFERRED]
  references/operations.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (62 total, 15 thin omitted)

### Community 0 - "Graph View UI Components"
Cohesion: 0.07
Nodes (83): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+75 more)

### Community 1 - "__init__.py"
Cohesion: 0.05
Nodes (79): Explorer V2: one node truth, two readers, difflib, act_amend(), act_inbox(), act_library(), act_list(), act_release(), act_run() (+71 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.05
Nodes (41): shlex, _active_spawn(), amend_preview(), apply_graph_defaults(), current_attempt(), def_hash(), _defaults_errors(), _downstream() (+33 more)

### Community 3 - "sys"
Cohesion: 0.09
Nodes (21): atexit, contextlib, copy, importlib, os, Serial bounded suite with durable per-case logs and atomic exit ledger., sys, tempfile (+13 more)

### Community 4 - "time"
Cohesion: 0.06
Nodes (9): End-to-end test of the `workflow` tool door against fake hermes., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading (+1 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "test_prompt_workdir.py"
Cohesion: 0.09
Nodes (28): argparse, fnmatch, hashlib, Pattern, excluded(), load_guards(), main(), Path (+20 more)

### Community 7 - "json"
Cohesion: 0.09
Nodes (11): json, shutil, subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when… (+3 more)

### Community 8 - "plugin_api.py"
Cohesion: 0.10
Nodes (23): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+15 more)

### Community 9 - "run_child"
Cohesion: 0.09
Nodes (26): What the plugin gains, _child_spoke(), child_work_dir(), _first_message_s(), _log_recent(), _next_spawn_no(), _node_file(), _note_turn_tier() (+18 more)

### Community 10 - "pathlib"
Cohesion: 0.09
Nodes (14): glob, hermes_constants, pathlib, plugin_api, re, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-… (+6 more)

### Community 11 - "wf.py"
Cohesion: 0.10
Nodes (24): concurrent_futures, datetime, fcntl, signal, build_inputs(), _classify_rc_output(), derived_contract(), extract_json() (+16 more)

### Community 12 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 13 - "main"
Cohesion: 0.14
Nodes (19): acquire_lock(), drain_inbox(), emit(), finalize(), hermes_home(), main(), consume_markers(), loop() (+11 more)

### Community 14 - "importlib_util"
Cohesion: 0.10
Nodes (5): importlib_util, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…

### Community 15 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 17 - "EngineNextCut"
Cohesion: 0.21
Nodes (4): EngineNextCut, deps_ok(), dep_satisfied(), deps_ok()

### Community 18 - "log"
Cohesion: 0.16
Nodes (18): _bounded_retry(), fmt_goal(), log(), Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+10 more)

### Community 19 - "ref_node_fs"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 20 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 21 - "1.1.0 — 2026-09-26 — the run watches itself"
Cohesion: 0.12
Nodes (15): 0.9.0 — 2026-09-24, 1.0.1 — 2026-09-25, 1.1.0 — 2026-09-26 — the run watches itself, Added, Additions, Archify: no (verdict + evidence), SMIL for candy, Changed, Changelog (+7 more)

### Community 22 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 23 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 24 - "efp"
Cohesion: 0.16
Nodes (15): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer(), mirror(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run… (+7 more)

### Community 26 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 27 - "3. Operate"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+6 more)

### Community 28 - "AGENTS.md"
Cohesion: 0.19
Nodes (5): Node budgets, Contributor checks (not ordinary user setup), Run and handoff, Smallest working graph, Workflow authoring (1.1.0)

### Community 29 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 31 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 32 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 33 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 34 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 35 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 36 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (6): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is

### Community 37 - "Hermes Workflows"
Cohesion: 0.29
Nodes (7): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get

### Community 41 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 42 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 43 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 44 - "Manual installation — Hermes Workflows 0.9.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 0.9.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 45 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 49 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 50 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.40
Nodes (5): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds

### Community 51 - "Run operations and read model"
Cohesion: 0.40
Nodes (4): Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 52 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 53 - "validate"
Cohesion: 0.40
Nodes (5): _harvest_death(), Tiny forgiving validator: type / required / properties / items., #4 harvest-on-death: a child that died (rc!=0 / timeout / cap — the CALLER…, validate(), chk()

### Community 54 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 55 - "Graph grammar and authoring boundaries"
Cohesion: 0.50
Nodes (4): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data

## Knowledge Gaps
- **177 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+172 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 528 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `node_facts()` connect `__init__.py` to `wfcommon.py`, `Run operations and read model`, `AGENTS.md`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `label()` connect `Graph View UI Components` to `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `Explorer V2: one node truth, two readers` connect `__init__.py` to `plugin_api.py`, `1.1.0 — 2026-09-26 — the run watches itself`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _177 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Graph View UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.06741250717154332 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05092592592592592 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.054901960784313725 - nodes in this community are weakly interconnected._