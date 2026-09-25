# Graph Report - tree  (2026-09-25)

## Corpus Check
- 71 files · ~91,190 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 827 nodes · 1650 edges · 49 communities (35 shown, 14 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 114 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Graph View UI Components
- __init__.py
- Hermes Workflows
- EngineNextCut
- test_fanout_expand.mjs
- graph_check.py
- os
- wf.py
- test_card_delivery_0924.py
- wfcommon.py
- pathlib
- time
- main
- json
- jload
- test_live_truth_ui.mjs
- CurrentAttemptMetrics
- test_fanout_ui.mjs
- plugin_api.py
- test_canvas_wrap.mjs
- run_agent_node
- test_edge_routing.mjs
- LiveTruth
- test_waitgate_0923.py
- test_card_frontend_contract.mjs
- efp
- test_metrics_missing_ui.mjs
- Contributing to hermes-workflows
- sys
- _SV
- validate_graph_errors
- test_engine.py
- test_lifecycle_next_cut_0923.py
- test_review_fixes.py
- test_steer_live_40.py
- 0.9.0 — 2026-09-24
- Manifest decisions (publish pass, 2026-09-24)
- test_prune_0923.py
- test_v3_fixes.py
- test_v5_fixes.py
- Integrated
- test_papercuts_0922b.py
- Manifest API UI
- Attempt API Metrics
- Runner Verdict Fingerprint
- Run
- Ctx
- Ctx
- Fake Scripts

## God Nodes (most connected - your core abstractions)
1. `efp()` - 26 edges
2. `jload()` - 23 edges
3. `main()` - 20 edges
4. `run_state()` - 20 edges
5. `run_child()` - 19 edges
6. `CurrentAttemptMetrics` - 18 edges
7. `Drawer()` - 16 edges
8. `EngineNextCut` - 16 edges
9. `loop()` - 16 edges
10. `GraphView()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Run operations and read model` --references--> `blocked_by()`  [INFERRED]
  references/operations.md → wfcommon.py
- `_list_runs()` --indirect_call--> `v()`  [INFERRED]
  dashboard/plugin_api.py → tests/test_papercuts_0922.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `_validation_error()` --calls--> `validate_graph_errors()`  [INFERRED]
  __init__.py → wfcommon.py

## Import Cycles
- None detected.

## Communities (49 total, 14 thin omitted)

### Community 0 - "Graph View UI Components"
Cohesion: 0.08
Nodes (69): ago(), api(), bandRows(), box(), columnGroups(), ctxRest(), depthMap(), DirectiveBody() (+61 more)

### Community 1 - "__init__.py"
Cohesion: 0.06
Nodes (59): datetime, act_amend(), act_inbox(), act_library(), act_list(), act_release(), act_run(), act_save() (+51 more)

### Community 2 - "Hermes Workflows"
Cohesion: 0.05
Nodes (35): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is, Apply (source install only), Patched core: typed `max_turns` deaths (optional) (+27 more)

### Community 3 - "EngineNextCut"
Cohesion: 0.08
Nodes (24): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed `max_turns` deaths, 3. Operate, 3a. The loop (+16 more)

### Community 4 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 5 - "graph_check.py"
Cohesion: 0.08
Nodes (29): argparse, fnmatch, hashlib, Pattern, re, _ast(), main(), _norm() (+21 more)

### Community 6 - "os"
Cohesion: 0.09
Nodes (10): os, Serial bounded suite with durable per-case logs and atomic exit ledger., shutil, subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+2 more)

### Community 7 - "wf.py"
Cohesion: 0.11
Nodes (28): concurrent_futures, fcntl, signal, _classify_rc_output(), extract_json(), hermes_home(), _next_spawn_no(), _node_file() (+20 more)

### Community 8 - "test_card_delivery_0924.py"
Cohesion: 0.15
Nodes (4): CardBackend, CardDelivery, clear_session_vars(), Regression: a launch whose turn ends blank/interrupted replays its card exactly…

### Community 9 - "wfcommon.py"
Cohesion: 0.11
Nodes (25): shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), _downstream(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:… (+17 more)

### Community 10 - "pathlib"
Cohesion: 0.11
Nodes (10): atexit, importlib, pathlib, tempfile, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal… (+2 more)

### Community 11 - "time"
Cohesion: 0.09
Nodes (12): glob, hermes_constants, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+4 more)

### Community 12 - "main"
Cohesion: 0.15
Nodes (20): acquire_lock(), drain_inbox(), emit(), finalize(), log(), main(), consume_markers(), loop() (+12 more)

### Community 13 - "json"
Cohesion: 0.15
Nodes (12): contextlib, copy, importlib_util, json, Regression: launch a run in the tool's session, deliver one parser-valid card., Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no…, Integrated read-model and parser-valid card dedup checks. (+4 more)

### Community 14 - "jload"
Cohesion: 0.15
Nodes (20): act_status(), act_steer(), act_wait(), B1 evidence read model for one node: queued = lines addressed to the node in…, Explicit resume/watch verb. Read-only status/list never spawn; wait may resume…, ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), _steer_state() (+12 more)

### Community 15 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 17 - "test_fanout_ui.mjs"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 18 - "plugin_api.py"
Cohesion: 0.20
Nodes (15): _events(), _fold_metrics(), get_run(), _list_runs(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``., UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate() (+7 more)

### Community 19 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 20 - "run_agent_node"
Cohesion: 0.15
Nodes (16): build_inputs(), fmt_goal(), Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block… (+8 more)

### Community 21 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 23 - "test_waitgate_0923.py"
Cohesion: 0.15
Nodes (6): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing., P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 24 - "test_card_frontend_contract.mjs"
Cohesion: 0.17
Nodes (9): ref_node_assert, ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp (+1 more)

### Community 25 - "efp"
Cohesion: 0.20
Nodes (12): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, answer(), mirror(), def_hash(), efp() (+4 more)

### Community 26 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 27 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 28 - "sys"
Cohesion: 0.22
Nodes (3): sys, End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run…

### Community 30 - "validate_graph_errors"
Cohesion: 0.25
Nodes (8): gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, reasoning_levels(), validate_graph_errors(), E(), schema_check(), wait_spec_ok()

### Community 31 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 34 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 35 - "0.9.0 — 2026-09-24"
Cohesion: 0.33
Nodes (5): 0.9.0 — 2026-09-24, Added, Changed, Changelog, Fixed

### Community 36 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 42 - "Manifest API UI"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 43 - "Attempt API Metrics"
Cohesion: 0.50
Nodes (4): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 44 - "Runner Verdict Fingerprint"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

## Knowledge Gaps
- **135 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+130 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 415 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EngineNextCut` connect `EngineNextCut` to `json`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `efp()` connect `efp` to `test_review_fixes.py`, `EngineNextCut`, `wf.py`, `wfcommon.py`, `pathlib`, `time`, `main`, `Runner Verdict Fingerprint`, `jload`, `run_agent_node`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `CurrentAttemptMetrics` connect `CurrentAttemptMetrics` to `json`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _135 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Graph View UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.07950310559006211 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06327683615819209 - nodes in this community are weakly interconnected._
- **Should `Hermes Workflows` be split into smaller, more focused modules?**
  _Cohesion score 0.047474747474747475 - nodes in this community are weakly interconnected._