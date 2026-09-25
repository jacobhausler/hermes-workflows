# Graph Report - tree  (2026-09-25)

## Corpus Check
- 79 files · ~105,423 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 924 nodes · 1840 edges · 62 communities (45 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 115 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Desktop Plugin UI Components
- __init__.py
- wf.py
- plugin_api.py
- test_fanout_expand.mjs
- efp
- sys
- CurrentAttemptMetrics
- jload
- time
- wfcommon.py
- clear_session_vars
- test_packaging.py
- log
- subprocess
- pathlib
- test_live_truth_ui.mjs
- EngineNextCut
- test_sprint101w2_C3-fanout-gates.py
- test_canvas_wrap.mjs
- test_edge_routing.mjs
- LiveTruth
- validate_graph_errors
- test_card_frontend_contract.mjs
- test_metrics_missing_ui.mjs
- 1.0.1 — 2026-09-25
- test_sprint101_D-surface.py
- Contributing to hermes-workflows
- test_fanout_ui.mjs
- test_sprint101w2_B2-retry.py
- _SV
- AGENTS.md — front door for agents
- Patched core: typed turn-cap deaths (optional)
- test_inline_header.mjs
- test_engine.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- Hermes Workflows
- test_lifecycle_next_cut_0923.py
- Review Fixes Regressions
- Run Defaults Testing
- Steer Liveness Testing
- Cooperative Steer Testing
- AGENTS.md
- 3. Operate
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Manual installation — Hermes Workflows 0.9.0
- graph_check.py
- test_failed_events_77.py
- test_prune_0923.py
- test_tier_report_0924.py
- test_v3_fixes.py
- test_waitgate_0923.py
- child_metrics
- Integrated
- manifest.json
- FakeProcess
- write_runner_exit
- Run
- Ctx
- dep_satisfied
- Fake Script

## God Nodes (most connected - your core abstractions)
1. `efp()` - 28 edges
2. `run_child()` - 24 edges
3. `jload()` - 24 edges
4. `main()` - 20 edges
5. `run_state()` - 20 edges
6. `CurrentAttemptMetrics` - 18 edges
7. `loop()` - 18 edges
8. `Drawer()` - 16 edges
9. `EngineNextCut` - 16 edges
10. `GraphView()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Nodes and data` --references--> `build()`  [INFERRED]
  references/grammar.md → scripts/pack.py
- `Run operations and read model` --references--> `blocked_by()`  [INFERRED]
  references/operations.md → wfcommon.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `_validation_error()` --calls--> `validate_graph_errors()`  [INFERRED]
  __init__.py → wfcommon.py

## Import Cycles
- None detected.

## Communities (62 total, 17 thin omitted)

### Community 0 - "Desktop Plugin UI Components"
Cohesion: 0.08
Nodes (69): ago(), api(), bandRows(), box(), columnGroups(), ctxRest(), depthMap(), DirectiveBody() (+61 more)

### Community 1 - "__init__.py"
Cohesion: 0.06
Nodes (59): datetime, difflib, act_inbox(), act_library(), act_run(), act_save(), _alias_provider_pair(), _auto_card() (+51 more)

### Community 2 - "wf.py"
Cohesion: 0.07
Nodes (41): concurrent_futures, fcntl, signal, _child_spoke(), _classify_rc_output(), derived_contract(), extract_json(), _first_message_s() (+33 more)

### Community 3 - "plugin_api.py"
Cohesion: 0.07
Nodes (23): atexit, _events(), _fold_metrics(), get_run(), _list_runs(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``., UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).… (+15 more)

### Community 4 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 5 - "efp"
Cohesion: 0.10
Nodes (31): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), drain_inbox(), emit(), finalize() (+23 more)

### Community 6 - "sys"
Cohesion: 0.12
Nodes (18): contextlib, copy, json, os, sys, tempfile, Regression: launch a run in the tool's session, deliver one parser-valid card., Regression: a launch whose turn ends blank/interrupted replays its card exactly… (+10 more)

### Community 7 - "CurrentAttemptMetrics"
Cohesion: 0.15
Nodes (8): Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), CurrentAttemptMetrics

### Community 8 - "jload"
Cohesion: 0.15
Nodes (26): act_amend(), act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid… (+18 more)

### Community 9 - "time"
Cohesion: 0.09
Nodes (14): glob, hermes_constants, plugin_api, re, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+6 more)

### Community 10 - "wfcommon.py"
Cohesion: 0.11
Nodes (25): shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), _downstream(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:… (+17 more)

### Community 11 - "clear_session_vars"
Cohesion: 0.16
Nodes (3): CardBackend, CardDelivery, clear_session_vars()

### Community 12 - "test_packaging.py"
Cohesion: 0.11
Nodes (22): argparse, fnmatch, hashlib, Pattern, excluded(), load_guards(), main(), Path (+14 more)

### Community 13 - "log"
Cohesion: 0.12
Nodes (24): _bounded_retry(), build_inputs(), fmt_goal(), _inputs_block(), log(), now(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block… (+16 more)

### Community 14 - "subprocess"
Cohesion: 0.10
Nodes (9): Serial bounded suite with durable per-case logs and atomic exit ledger., shutil, subprocess, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on… (+1 more)

### Community 15 - "pathlib"
Cohesion: 0.11
Nodes (7): importlib_util, pathlib, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes., v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run…

### Community 16 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 17 - "EngineNextCut"
Cohesion: 0.21
Nodes (4): Run and handoff, Smallest working graph, Workflow authoring (1.0.1), EngineNextCut

### Community 18 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.11
Nodes (5): sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, threading

### Community 19 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 20 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 22 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): apply_graph_defaults(), _defaults_errors(), Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, reasoning_levels() (+4 more)

### Community 23 - "test_card_frontend_contract.mjs"
Cohesion: 0.17
Nodes (9): ref_node_crypto, ref_node_os, ref_node_path, macEvidence, parserSource, plugin, root, temp (+1 more)

### Community 24 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 25 - "1.0.1 — 2026-09-25"
Cohesion: 0.18
Nodes (10): 0.9.0 — 2026-09-24, 1.0.1 — 2026-09-25, Added, Changed, Changelog, Deaths become outcomes, Fixed, Operator surface (+2 more)

### Community 26 - "test_sprint101_D-surface.py"
Cohesion: 0.18
Nodes (5): gateway, mk_run(), _NoSpawn, Sprint-101 lane D-surface, item #15: the inline card is machinery, not a…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 27 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 28 - "test_fanout_ui.mjs"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 29 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 31 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 32 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.25
Nodes (8): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Typed termination from the child's quiet turn report (core PR pending; the…, _typed_error_class()

### Community 33 - "test_inline_header.mjs"
Cohesion: 0.25
Nodes (7): ref_node_assert, ref_node_fs, [first, second], header, match, root, source

### Community 34 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 35 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (6): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is

### Community 36 - "Hermes Workflows"
Cohesion: 0.29
Nodes (7): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get

### Community 41 - "Cooperative Steer Testing"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 43 - "3. Operate"
Cohesion: 0.33
Nodes (6): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run

### Community 44 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 45 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 46 - "Manual installation — Hermes Workflows 0.9.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 0.9.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 47 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 53 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 55 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 57 - "write_runner_exit"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 60 - "dep_satisfied"
Cohesion: 0.67
Nodes (3): deps_ok(), dep_satisfied(), deps_ok()

## Knowledge Gaps
- **139 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+134 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 477 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EngineNextCut` connect `EngineNextCut` to `sys`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `efp()` connect `efp` to `wf.py`, `plugin_api.py`, `Review Fixes Regressions`, `jload`, `time`, `wfcommon.py`, `4. Contribute`, `log`, `subprocess`, `test_sprint101w2_C3-fanout-gates.py`, `write_runner_exit`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `4a. Map` connect `4. Contribute` to `efp`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _139 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Desktop Plugin UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.07950310559006211 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05649717514124294 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07317073170731707 - nodes in this community are weakly interconnected._