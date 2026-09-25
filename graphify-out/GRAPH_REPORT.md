# Graph Report - release  (2026-09-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 832 nodes · 1679 edges · 54 communities (42 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 118 edges (avg confidence: 0.86)
- Token cost: 263 input · 294 output

## Graph Freshness
- Built from commit: `d89d78e3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Graph View UI Components
- Dashboard Plugin API
- Fan-Out UI Test
- Authoring Regression Tests
- Workflow Tool Plugin
- DAG Documentation & Concepts
- Runner Process Execution
- Card Backend Registration
- Run State Actions
- Workflow Shared Semantics
- Live Truth UI Test
- Graph Gate Tests
- Run Lifecycle Management
- Attempt Metrics Tracking
- Engine Next-Cut States
- Runner Contract Tests
- Fan-Out UI Tests
- Canvas Layout Rendering
- Schema Preflight Feedback
- Edge Routing Tests
- Runner Process Management
- Agent Node Execution
- Fake Hermes Engine Tests
- Runner Liveness Detection
- Routing Regression Tests
- Workflow Library CLI
- Graph Drift Gate
- Card Frontend Contract
- Metrics UI Rendering
- Graph Save Validation
- Parse-Only Syntax Mode
- Gate Wait Validation
- Papercut Skill Tests
- Engine Gate Tests
- Lifecycle Regression Tests
- Review Fixes Regression
- Cooperative Steer Tests
- Amend Preview Validation
- Failed Event Recovery
- Prune Gate Tests
- V3 Fixes Regression
- Integrated Spawn Steer Tests
- Manifest API UI
- Attempt API Metrics
- Runner Verdict Fingerprint
- Context Config Init
- Context Config Init
- Schema Validation
- Fake Scripts
- Contributor Checks
- Plugin Catalog Versioning
- Manual Installation Guide
- Authoring Regression Tests
- Graph Snapshot Hot-Reload

## God Nodes (most connected - your core abstractions)
1. `efp()` - 26 edges
2. `jload()` - 23 edges
3. `main()` - 20 edges
4. `run_state()` - 20 edges
5. `run_child()` - 19 edges
6. `CurrentAttemptMetrics` - 18 edges
7. `EngineNextCut` - 16 edges
8. `Drawer()` - 16 edges
9. `loop()` - 16 edges
10. `LiveTruth` - 14 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `_list_runs()` --indirect_call--> `v()`  [INFERRED]
  dashboard/plugin_api.py → tests/test_papercuts_0922.py
- `Run operations and read model` --references--> `blocked_by()`  [INFERRED]
  references/operations.md → wfcommon.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `_release_core()` --calls--> `efp()`  [INFERRED]
  __init__.py → wfcommon.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graph Authoring Contract (Skill + References)** — skill, references_grammar, references_operations, references_budgets, concept_dag, concept_fanout, concept_gate [EXTRACTED 0.90]

## Communities (54 total, 12 thin omitted)

### Community 0 - "Graph View UI Components"
Cohesion: 0.08
Nodes (69): ago(), api(), bandRows(), box(), columnGroups(), ctxRest(), depthMap(), DirectiveBody() (+61 more)

### Community 1 - "Dashboard Plugin API"
Cohesion: 0.11
Nodes (22): argparse, fnmatch, hashlib, Pattern, excluded(), load_guards(), main(), Path (+14 more)

### Community 2 - "Fan-Out UI Test"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 3 - "Authoring Regression Tests"
Cohesion: 0.15
Nodes (12): contextlib, copy, os, tempfile, Regression: launch a run in the tool's session, deliver one parser-valid card., Regression: a launch whose turn ends blank/interrupted replays its card exactly…, Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no… (+4 more)

### Community 4 - "Workflow Tool Plugin"
Cohesion: 0.06
Nodes (73): act_amend(), act_inbox(), act_library(), act_list(), act_release(), act_run(), act_save(), act_status() (+65 more)

### Community 5 - "DAG Documentation & Concepts"
Cohesion: 0.57
Nodes (6): branch-gate.png — Branch on Verdict DAG, dag-review.png — Mega-Review Fleet DAG, fanout.png — Fan-out Demo DAG, DAG of Agent Nodes, Fan-out, Human and Machine Gates

### Community 6 - "Runner Process Execution"
Cohesion: 0.09
Nodes (32): concurrent_futures, datetime, What the plugin gains, fcntl, signal, _classify_rc_output(), extract_json(), hermes_home() (+24 more)

### Community 7 - "Card Backend Registration"
Cohesion: 0.16
Nodes (3): CardBackend, CardDelivery, clear_session_vars()

### Community 8 - "Run State Actions"
Cohesion: 0.10
Nodes (20): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed `max_turns` deaths, 3. Operate, 3a. The loop (+12 more)

### Community 9 - "Workflow Shared Semantics"
Cohesion: 0.12
Nodes (25): shlex, _active_spawn(), _active_spawns(), amend_preview(), current_attempt(), _downstream(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:… (+17 more)

### Community 10 - "Live Truth UI Test"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 11 - "Graph Gate Tests"
Cohesion: 0.10
Nodes (10): main(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), Serial bounded suite with durable per-case logs and atomic exit ledger., shutil, subprocess, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.… (+2 more)

### Community 12 - "Run Lifecycle Management"
Cohesion: 0.19
Nodes (15): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer(), mirror(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run… (+7 more)

### Community 13 - "Attempt Metrics Tracking"
Cohesion: 0.24
Nodes (5): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, CurrentAttemptMetrics

### Community 14 - "Engine Next-Cut States"
Cohesion: 0.13
Nodes (11): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get, Run and handoff (+3 more)

### Community 15 - "Runner Contract Tests"
Cohesion: 0.10
Nodes (7): plugin_api, sqlite3, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Integrated read-model and parser-valid card dedup checks., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, time

### Community 16 - "Fan-Out UI Tests"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 17 - "Canvas Layout Rendering"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 18 - "Schema Preflight Feedback"
Cohesion: 0.16
Nodes (7): atexit, importlib, json, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v(), Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 19 - "Edge Routing Tests"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 20 - "Runner Process Management"
Cohesion: 0.14
Nodes (19): acquire_lock(), drain_inbox(), emit(), finalize(), main(), consume_markers(), loop(), deps_ok() (+11 more)

### Community 21 - "Agent Node Execution"
Cohesion: 0.16
Nodes (17): build_inputs(), fmt_goal(), log(), Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is… (+9 more)

### Community 24 - "Routing Regression Tests"
Cohesion: 0.15
Nodes (6): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing., Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, threading

### Community 25 - "Workflow Library CLI"
Cohesion: 0.20
Nodes (15): _events(), _fold_metrics(), get_run(), _list_runs(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``., UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate() (+7 more)

### Community 27 - "Card Frontend Contract"
Cohesion: 0.17
Nodes (9): ref_node_crypto, ref_node_os, ref_node_path, macEvidence, parserSource, plugin, root, temp (+1 more)

### Community 28 - "Metrics UI Rendering"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 29 - "Graph Save Validation"
Cohesion: 0.25
Nodes (7): 0.9.0 — 2026-09-24, Added, Changed, Changelog, Fixed, Cooperative Steer, Typed Failure Events

### Community 31 - "Gate Wait Validation"
Cohesion: 0.25
Nodes (8): gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, reasoning_levels(), validate_graph_errors(), E(), schema_check(), wait_spec_ok()

### Community 32 - "Papercut Skill Tests"
Cohesion: 0.16
Nodes (10): glob, hermes_constants, pathlib, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Portable authoring skill contract; no provider or live-home dependencies. (+2 more)

### Community 33 - "Engine Gate Tests"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 34 - "Lifecycle Regression Tests"
Cohesion: 0.25
Nodes (7): error_class Taxonomy, Quiet Turn Report (HERMES_QUIET_TURN_REPORT_FILE), Apply (source install only), Patched core: typed `max_turns` deaths (optional), The patch, Verify, What the patch adds

### Community 36 - "Cooperative Steer Tests"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 37 - "Amend Preview Validation"
Cohesion: 0.25
Nodes (7): Fingerprint Replay-Skip Resume, Transcript Directive ::workflow{id}, Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), tests/fixtures/mac-source.txt — Transcript Directives Fixture, blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 39 - "Prune Gate Tests"
Cohesion: 0.11
Nodes (7): importlib_util, sys, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes., v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…

### Community 42 - "Manifest API UI"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 43 - "Attempt API Metrics"
Cohesion: 0.50
Nodes (4): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 44 - "Runner Verdict Fingerprint"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 46 - "Context Config Init"
Cohesion: 0.25
Nodes (7): docs/catalog/entry.yaml — Catalog Entry, (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24), plugin.yaml — Plugin Manifest

### Community 47 - "Schema Validation"
Cohesion: 0.25
Nodes (7): ref_node_assert, ref_node_fs, [first, second], header, match, root, source

### Community 49 - "Contributor Checks"
Cohesion: 0.36
Nodes (4): Budget Invariants, workflow Tool, Node budgets (measured, 2026-09-24), Contributor checks (not ordinary user setup)

### Community 50 - "Plugin Catalog Versioning"
Cohesion: 0.29
Nodes (6): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is

### Community 51 - "Manual Installation Guide"
Cohesion: 0.29
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 0.9.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

## Knowledge Gaps
- **128 isolated node(s):** `EDGE_TONE`, `$fanExpanded`, `$fanItem`, `$fanOpen`, `MINI` (+123 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 405 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `blocked_by()` connect `Amend Preview Validation` to `Workflow Shared Semantics`, `Workflow Tool Plugin`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `efp()` connect `Run Lifecycle Management` to `Papercut Skill Tests`, `Review Fixes Regression`, `Workflow Tool Plugin`, `Runner Process Execution`, `Run State Actions`, `Workflow Shared Semantics`, `Runner Verdict Fingerprint`, `Schema Preflight Feedback`, `Runner Process Management`, `Agent Node Execution`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **What connects `EDGE_TONE`, `$fanExpanded`, `$fanItem` to the rest of the system?**
  _128 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Graph View UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.07950310559006211 - nodes in this community are weakly interconnected._
- **Should `Dashboard Plugin API` be split into smaller, more focused modules?**
  _Cohesion score 0.10666666666666667 - nodes in this community are weakly interconnected._
- **Should `Fan-Out UI Test` be split into smaller, more focused modules?**
  _Cohesion score 0.06890756302521009 - nodes in this community are weakly interconnected._
- **Should `Workflow Tool Plugin` be split into smaller, more focused modules?**
  _Cohesion score 0.057297297297297295 - nodes in this community are weakly interconnected._