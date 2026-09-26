# Graph Report - tree  (2026-09-26)

## Corpus Check
- 85 files · ~115,728 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1003 nodes · 1966 edges · 65 communities (48 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- __init__.py
- wfcommon.py
- test_prompt_workdir.py
- test_fanout_expand.mjs
- plugin_api.py
- run_child
- json
- time
- wf.py
- test_tiers.py
- sys
- test_live_truth_ui.mjs
- main
- 3. Operate
- test_register_surface.mjs
- CurrentAttemptMetrics
- log
- pathlib
- ref_node_fs
- test_canvas_wrap.mjs
- efp
- test_v5_fixes.py
- 1.0.2 — 2026-09-26 — the run watches itself
- test_edge_routing.mjs
- test_session_strip.mjs
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- importlib_util
- test_metrics_missing_ui.mjs
- CardBackend
- os
- test_card_frontend_contract.mjs
- AGENTS.md
- Contributing to hermes-workflows
- test_sprint101w2_B2-retry.py
- test_engine.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- Hermes Workflows
- test_review_fixes.py
- test_sprint101w2_C3-fanout-gates.py
- test_status_next.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- test_validate_0923.py
- Manual installation — Hermes Workflows 0.9.0
- test_failed_events_77.py
- test_prune_0923.py
- test_v3_fixes.py
- child_metrics
- Patched core: typed turn-cap deaths (optional)
- Run operations and read model
- test_papercuts_0922b.py
- test_v4_fixes.py
- validate
- manifest.json
- Graph grammar and authoring boundaries
- .states
- Integrated
- FakeProcess
- write_runner_exit
- Run
- Smallest working graph
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

## Communities (65 total, 17 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "__init__.py"
Cohesion: 0.05
Nodes (77): Explorer V2: one node truth, two readers, difflib, act_amend(), act_inbox(), act_library(), act_list(), act_release(), act_run() (+69 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.06
Nodes (37): shlex, _active_spawn(), amend_preview(), apply_graph_defaults(), current_attempt(), _defaults_errors(), _downstream(), quote_json_parse_error() (+29 more)

### Community 3 - "test_prompt_workdir.py"
Cohesion: 0.08
Nodes (34): argparse, fnmatch, hashlib, Pattern, re, _ast(), main(), _norm() (+26 more)

### Community 4 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 5 - "plugin_api.py"
Cohesion: 0.10
Nodes (23): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+15 more)

### Community 6 - "run_child"
Cohesion: 0.08
Nodes (28): What the plugin gains, _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _log_recent(), _next_spawn_no(), _node_file() (+20 more)

### Community 7 - "json"
Cohesion: 0.09
Nodes (10): json, shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn. (+2 more)

### Community 8 - "time"
Cohesion: 0.09
Nodes (9): plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a… (+1 more)

### Community 9 - "wf.py"
Cohesion: 0.11
Nodes (22): concurrent_futures, datetime, fcntl, signal, build_inputs(), _classify_rc_output(), extract_json(), _inputs_block() (+14 more)

### Community 10 - "test_tiers.py"
Cohesion: 0.09
Nodes (9): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v(), Ctx, Ctx (+1 more)

### Community 11 - "sys"
Cohesion: 0.15
Nodes (12): contextlib, copy, subprocess, sys, tempfile, Regression: launch a run in the tool's session; the payload carries a parser-…, Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no… (+4 more)

### Community 12 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 13 - "main"
Cohesion: 0.14
Nodes (19): acquire_lock(), drain_inbox(), emit(), finalize(), hermes_home(), main(), consume_markers(), loop() (+11 more)

### Community 14 - "3. Operate"
Cohesion: 0.10
Nodes (20): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+12 more)

### Community 15 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 17 - "log"
Cohesion: 0.16
Nodes (18): _bounded_retry(), fmt_goal(), log(), Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+10 more)

### Community 18 - "pathlib"
Cohesion: 0.12
Nodes (7): pathlib, Ctx, Deterministic regressions for explicit workflow provider/model routing., Portable authoring skill contract; no provider or live-home dependencies., Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…, unittest_mock

### Community 19 - "ref_node_fs"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 20 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 21 - "efp"
Cohesion: 0.16
Nodes (17): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer(), mirror(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run… (+9 more)

### Community 22 - "test_v5_fixes.py"
Cohesion: 0.12
Nodes (4): sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 23 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.12
Nodes (15): 0.9.0 — 2026-09-24, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, Added, Additions, Archify: no (verdict + evidence), SMIL for candy, Changed, Changelog (+7 more)

### Community 24 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 25 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 28 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 29 - "importlib_util"
Cohesion: 0.14
Nodes (5): importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…

### Community 30 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 32 - "os"
Cohesion: 0.17
Nodes (4): os, Serial bounded suite with durable per-case logs and atomic exit ledger., Authoring door regressions; all state stays in this worktree, no…, End-to-end test of the `workflow` tool door against fake hermes.

### Community 33 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 35 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 36 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 37 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 38 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (6): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is

### Community 39 - "Hermes Workflows"
Cohesion: 0.29
Nodes (7): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get

### Community 43 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 44 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 45 - "test_validate_0923.py"
Cohesion: 0.33
Nodes (4): glob, hermes_constants, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 46 - "Manual installation — Hermes Workflows 0.9.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 0.9.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 50 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 51 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.40
Nodes (5): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds

### Community 52 - "Run operations and read model"
Cohesion: 0.40
Nodes (4): Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 55 - "validate"
Cohesion: 0.40
Nodes (5): _harvest_death(), Tiny forgiving validator: type / required / properties / items., #4 harvest-on-death: a child that died (rc!=0 / timeout / cap — the CALLER…, validate(), chk()

### Community 56 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 57 - "Graph grammar and authoring boundaries"
Cohesion: 0.50
Nodes (4): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data

### Community 58 - ".states"
Cohesion: 0.67
Nodes (3): deps_ok(), dep_satisfied(), deps_ok()

### Community 61 - "write_runner_exit"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 63 - "Smallest working graph"
Cohesion: 0.67
Nodes (3): Run and handoff, Smallest working graph, Workflow authoring (1.0.2)

## Knowledge Gaps
- **178 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+173 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 529 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `node_facts()` connect `__init__.py` to `wfcommon.py`, `Run operations and read model`, `Smallest working graph`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `efp()` connect `efp` to `__init__.py`, `wfcommon.py`, `run_child`, `test_review_fixes.py`, `test_sprint101w2_C3-fanout-gates.py`, `test_status_next.py`, `test_tiers.py`, `wf.py`, `test_validate_0923.py`, `3. Operate`, `main`, `log`, `write_runner_exit`, `importlib_util`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _178 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06538987688098495 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05258033106134372 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.058279370952821465 - nodes in this community are weakly interconnected._