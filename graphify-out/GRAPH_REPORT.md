# Graph Report - release  (2026-09-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 851 nodes · 1685 edges · 49 communities (36 shown, 13 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 114 edges (avg confidence: 0.86)
- Token cost: 146 input · 216 output

## Graph Freshness
- Built from commit: `ef880374`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Workflow Action Handlers
- Plugin UI Components
- Dashboard Plugin API
- UI Component Tests
- Workflow Engine Core
- Workflow Feature Documentation
- Workflow Validation Engine
- Card Registration and Hooks
- Test Fixtures and Fakes
- Workflow Lifecycle Tests
- Live Truth UI Tests
- Runner Lifecycle Loop
- Schema Validation Tests
- Spawn Attempt Metrics Tests
- Agent Node Retry Logic
- Canvas Layout Tests
- Engine Authoring Tests
- Failed Event Recovery
- Edge Routing Tests
- Run Gate Management
- Runner Liveness Tests
- Plugin Catalog Documentation
- Workflow Routing Gate Tests
- Frontend Contract Tests
- Metrics UI Tests
- Regression Test Suite
- Fanout UI Tests
- Operator Runbook Guide
- Lane A Contract Tests
- Release Changelog
- Inline Header Tests
- Engine Integration Tests
- Manifest Validation Decisions
- Publish Scrub Audit
- Library and Inputs Tests
- Cooperative Steer Protocol
- Packaging Reproducibility Tests
- Prune Gate Tests
- V3 Regression Fixes
- Runner Verdict Fingerprints
- Integrated Spawn & Steer Tests
- API Manifest Config
- API Call Metrics Tracking
- Hot-Reloadable Graph Snapshot
- Desktop Plugin SDK
- Fake Test Scripts
- Contributor Development Docs
- V5 Regression Fixes
- Waitgate Test Runner

## God Nodes (most connected - your core abstractions)
1. `efp()` - 26 edges
2. `jload()` - 23 edges
3. `run_state()` - 20 edges
4. `main()` - 20 edges
5. `run_child()` - 19 edges
6. `CurrentAttemptMetrics` - 18 edges
7. `EngineNextCut` - 16 edges
8. `Drawer()` - 16 edges
9. `loop()` - 16 edges
10. `LiveTruth` - 14 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Run operations and read model` --references--> `blocked_by()`  [INFERRED]
  references/operations.md → wfcommon.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `act_amend()` --calls--> `amend_preview()`  [INFERRED]
  __init__.py → wfcommon.py
- `_coerce_graph()` --calls--> `quote_json_parse_error()`  [INFERRED]
  __init__.py → wfcommon.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graph Authoring System — Skill, Grammar, Budgets, Operations** — skill_md, references_grammar_md, references_budgets_md, references_operations_md [EXTRACTED 0.95]

## Communities (49 total, 13 thin omitted)

### Community 0 - "Workflow Action Handlers"
Cohesion: 0.06
Nodes (74): datetime, act_amend(), act_inbox(), act_library(), act_list(), act_release(), act_run(), act_save() (+66 more)

### Community 1 - "Plugin UI Components"
Cohesion: 0.08
Nodes (69): ago(), api(), bandRows(), box(), columnGroups(), ctxRest(), depthMap(), DirectiveBody() (+61 more)

### Community 2 - "Dashboard Plugin API"
Cohesion: 0.10
Nodes (23): argparse, fnmatch, hashlib, Pattern, re, excluded(), load_guards(), main() (+15 more)

### Community 3 - "UI Component Tests"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 4 - "Workflow Engine Core"
Cohesion: 0.10
Nodes (30): concurrent_futures, What the plugin gains, fcntl, signal, _classify_rc_output(), extract_json(), hermes_home(), _next_spawn_no() (+22 more)

### Community 5 - "Workflow Feature Documentation"
Cohesion: 0.14
Nodes (26): AGENTS.md — Agent Front Door, branch-gate.png — Branch-on-Verdict DAG Screenshot, dag-review.png — Nine-Node Review Fleet DAG Screenshot, fanout.png — Fan-Out Stack DAG Screenshot, CHANGELOG.md — Version History, Cooperative Steer — Inbox Pull, Fan-Out — N Live Children with Quorum, Fingerprint Resume — Replay-Skip (+18 more)

### Community 6 - "Workflow Validation Engine"
Cohesion: 0.06
Nodes (35): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, ±40 chars of the source around the offset of a JSONDecodeError — what the door… (+27 more)

### Community 7 - "Card Registration and Hooks"
Cohesion: 0.15
Nodes (4): CardBackend, CardDelivery, clear_session_vars(), Regression: a launch whose turn ends blank/interrupted replays its card exactly…

### Community 8 - "Test Fixtures and Fakes"
Cohesion: 0.12
Nodes (12): contextlib, copy, pathlib, tempfile, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session, deliver one parser-valid card., Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no… (+4 more)

### Community 9 - "Workflow Lifecycle Tests"
Cohesion: 0.18
Nodes (7): glob, hermes_constants, plugin_api, sqlite3, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 10 - "Live Truth UI Tests"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 11 - "Runner Lifecycle Loop"
Cohesion: 0.25
Nodes (7): ref_node_assert, ref_node_fs, [first, second], header, match, root, source

### Community 12 - "Schema Validation Tests"
Cohesion: 0.07
Nodes (23): atexit, _events(), _fold_metrics(), get_run(), _list_runs(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``., UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).… (+15 more)

### Community 14 - "Agent Node Retry Logic"
Cohesion: 0.16
Nodes (18): build_inputs(), fmt_goal(), log(), now(), Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave… (+10 more)

### Community 15 - "Canvas Layout Tests"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 16 - "Engine Authoring Tests"
Cohesion: 0.07
Nodes (25): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed `max_turns` deaths, 3. Operate, 3a. The loop (+17 more)

### Community 17 - "Failed Event Recovery"
Cohesion: 0.14
Nodes (8): os, main(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…

### Community 18 - "Edge Routing Tests"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 19 - "Run Gate Management"
Cohesion: 0.11
Nodes (31): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), finalize(), main() (+23 more)

### Community 21 - "Plugin Catalog Documentation"
Cohesion: 0.05
Nodes (34): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is, Apply (source install only), Patched core: typed `max_turns` deaths (optional) (+26 more)

### Community 22 - "Workflow Routing Gate Tests"
Cohesion: 0.15
Nodes (6): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing., Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, threading

### Community 23 - "Frontend Contract Tests"
Cohesion: 0.17
Nodes (9): ref_node_crypto, ref_node_os, ref_node_path, macEvidence, parserSource, plugin, root, temp (+1 more)

### Community 24 - "Metrics UI Tests"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 26 - "Fanout UI Tests"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 29 - "Release Changelog"
Cohesion: 0.33
Nodes (5): 0.9.0 — 2026-09-24, Added, Changed, Changelog, Fixed

### Community 30 - "Inline Header Tests"
Cohesion: 0.16
Nodes (6): importlib_util, sys, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…

### Community 31 - "Engine Integration Tests"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 32 - "Manifest Validation Decisions"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 33 - "Publish Scrub Audit"
Cohesion: 0.33
Nodes (5): EXPOSURE — removed from the publishable surface, FALSE-POSITIVE — `haus` inside `exhaust*` (kept), GUARD — kept verbatim, Publish scrub audit — 2026-09-24, Publish-tree exclusions (scripts/make_public.py)

### Community 34 - "Library and Inputs Tests"
Cohesion: 0.15
Nodes (4): Serial bounded suite with durable per-case logs and atomic exit ledger., subprocess, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 35 - "Cooperative Steer Protocol"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 37 - "Prune Gate Tests"
Cohesion: 0.13
Nodes (8): json, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, End-to-end test of the `workflow` tool door against fake hermes., Integrated read-model and parser-valid card dedup checks., on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, time

### Community 39 - "Runner Verdict Fingerprints"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 42 - "API Manifest Config"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 43 - "API Call Metrics Tracking"
Cohesion: 0.50
Nodes (4): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 45 - "Desktop Plugin SDK"
Cohesion: 0.67
Nodes (3): Transcript Directives — ::name{...} Inline Cards, @hermes/plugin-sdk — Desktop Plugin SDK, tests/fixtures/mac-source.txt — Desktop SDK Fixture

## Knowledge Gaps
- **137 isolated node(s):** `EDGE_TONE`, `$fanExpanded`, `$fanItem`, `$fanOpen`, `MINI` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 417 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EngineNextCut` connect `Engine Authoring Tests` to `Test Fixtures and Fakes`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `efp()` connect `Run Gate Management` to `Workflow Action Handlers`, `Workflow Engine Core`, `Workflow Validation Engine`, `Runner Verdict Fingerprints`, `Workflow Lifecycle Tests`, `Schema Validation Tests`, `Agent Node Retry Logic`, `Engine Authoring Tests`, `V5 Regression Fixes`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `CurrentAttemptMetrics` connect `Spawn Attempt Metrics Tests` to `Test Fixtures and Fakes`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **What connects `EDGE_TONE`, `$fanExpanded`, `$fanItem` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Workflow Action Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.05649122807017544 - nodes in this community are weakly interconnected._
- **Should `Plugin UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.07950310559006211 - nodes in this community are weakly interconnected._
- **Should `Dashboard Plugin API` be split into smaller, more focused modules?**
  _Cohesion score 0.10461538461538461 - nodes in this community are weakly interconnected._