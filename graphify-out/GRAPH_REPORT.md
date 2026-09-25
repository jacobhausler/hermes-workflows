# Graph Report - integrate  (2026-09-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 941 nodes · 1920 edges · 57 communities (45 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 118 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `637a93e3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Desktop Plugin UI Components
- Child Process Runner
- Fan-out Expand UI Tests
- Fake Hermes Test Harness
- System Architecture Documentation
- Run Loop Orchestration
- Run Lifecycle Actions
- Workflow Graph Validation
- Card Backend Registration
- Schema and Card Tests
- Library and Card Commands
- Model Preflight Checks
- Live Truth UI Tests
- Dashboard Plugin Backend
- Graph Gate Contract Tests
- Current Attempt Metrics
- Engine Graph Execution
- Bounded Retry Handling
- Publishable Tree Builder
- Sprint Regression Tests
- Canvas Wrap Layout
- Graph Edge Routing
- Runner Liveness Detection
- Graph Defaults Validation
- Graph Drift Gate
- Workflow Door Suite
- Model Alias Resolution
- Card Frontend Contract
- Metrics Missing UI
- Gateway Surface Tests
- Graph Input Validation
- Fanout UI Testing
- Retry Contract Testing
- Syntax Mode Ordering
- Inline Header Assertions
- Engine Gate Testing
- Routing Provider Regressions
- Lifecycle Regression Testing
- Review Fixes Regressions
- Run Defaults Testing
- Steer Liveness Testing
- Cooperative Steer Testing
- Steering Inbox Events
- Model Preflight Routing
- Packaging Reproducibility Testing
- Prune Gate Testing
- Tier Self-Report Testing
- V0.3 Regression Sign-Off
- API Call Metrics Tracking
- Transcript Directive Parsing
- Integrated Spawn and Card Tests
- V4 Regression Sign-Off
- Node Input Resolution
- API Manifest Tab
- Runner Verdict Writing
- Hot-Reloadable Graph Snapshot
- Fake Script

## God Nodes (most connected - your core abstractions)
1. `efp()` - 28 edges
2. `run_child()` - 24 edges
3. `jload()` - 24 edges
4. `main()` - 20 edges
5. `run_state()` - 20 edges
6. `CurrentAttemptMetrics` - 18 edges
7. `loop()` - 18 edges
8. `EngineNextCut` - 16 edges
9. `Drawer()` - 16 edges
10. `LiveTruth` - 14 edges

## Surprising Connections (you probably didn't know these)
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `Nodes and data` --references--> `build()`  [INFERRED]
  references/grammar.md → scripts/pack.py
- `Run operations and read model` --references--> `blocked_by()`  [INFERRED]
  references/operations.md → wfcommon.py
- `_steer_state()` --calls--> `jload()`  [INFERRED]
  __init__.py → wfcommon.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Transcript Directive Rendering Pipeline** — func_parse_transcript_directive, func_segment_transcript_directives, comp_transcript_directive_leaf, const_transcript_directive_area, concept_transcript_directives [EXTRACTED 0.90]
- **Two-Build Architecture (Backend + Desktop)** — concept_backend_half, concept_desktop_half, concept_child_spawn_contract, concept_quiet_turn_report, concept_hermes_agent [EXTRACTED 0.90]
- **Core Workflow Abstractions** — concept_dag, concept_fanout, concept_gate, concept_fingerprint_resume, concept_typed_failures, concept_cooperative_steer [EXTRACTED 0.90]

## Communities (57 total, 12 thin omitted)

### Community 0 - "Desktop Plugin UI Components"
Cohesion: 0.08
Nodes (69): ago(), api(), bandRows(), box(), columnGroups(), ctxRest(), depthMap(), DirectiveBody() (+61 more)

### Community 1 - "Child Process Runner"
Cohesion: 0.08
Nodes (27): What the plugin gains, _child_spoke(), _classify_rc_output(), derived_contract(), _first_message_s(), _harvest_death(), _log_recent(), _next_spawn_no() (+19 more)

### Community 2 - "Fan-out Expand UI Tests"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 3 - "Fake Hermes Test Harness"
Cohesion: 0.09
Nodes (10): sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+2 more)

### Community 4 - "System Architecture Documentation"
Cohesion: 0.07
Nodes (44): Backend Half (Python), Child Spawn Contract (hermes chat -Q), Cooperative Steer, DAG of Agent Nodes, Desktop DAG View, Desktop Half (plugin.js), Fan-out, Fingerprint Replay-Skip Resume (+36 more)

### Community 5 - "Run Loop Orchestration"
Cohesion: 0.11
Nodes (33): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), finalize(), hermes_home() (+25 more)

### Community 6 - "Run Lifecycle Actions"
Cohesion: 0.18
Nodes (20): act_amend(), act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid… (+12 more)

### Community 7 - "Workflow Graph Validation"
Cohesion: 0.05
Nodes (43): Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), shlex, _active_spawn(), amend_preview(), apply_graph_defaults(), blocked_by(), current_attempt() (+35 more)

### Community 8 - "Card Backend Registration"
Cohesion: 0.16
Nodes (3): CardBackend, CardDelivery, clear_session_vars()

### Community 9 - "Schema and Card Tests"
Cohesion: 0.12
Nodes (14): contextlib, json, os, tempfile, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session, deliver one parser-valid card., Regression: a launch whose turn ends blank/interrupted replays its card exactly…, Current-attempt heartbeat with real fake child identity; no provider access. (+6 more)

### Community 10 - "Library and Card Commands"
Cohesion: 0.17
Nodes (16): datetime, difflib, _auto_card(), _card(), _clear_launch(), handle(), model_tiers(), _output_pointer() (+8 more)

### Community 11 - "Model Preflight Checks"
Cohesion: 0.11
Nodes (8): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 12 - "Live Truth UI Tests"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 13 - "Dashboard Plugin Backend"
Cohesion: 0.18
Nodes (16): _events(), _fold_metrics(), get_run(), _list_runs(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``., UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate() (+8 more)

### Community 14 - "Graph Gate Contract Tests"
Cohesion: 0.11
Nodes (9): importlib_util, Serial bounded suite with durable per-case logs and atomic exit ledger., sys, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph() (+1 more)

### Community 16 - "Engine Graph Execution"
Cohesion: 0.12
Nodes (14): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get, Run and handoff (+6 more)

### Community 17 - "Bounded Retry Handling"
Cohesion: 0.27
Nodes (14): _bounded_retry(), log(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, run_agent_node() (+6 more)

### Community 18 - "Publishable Tree Builder"
Cohesion: 0.08
Nodes (28): argparse, fnmatch, hashlib, Pattern, re, File-authored graphs, Gates and branches, Graph grammar and authoring boundaries (+20 more)

### Community 19 - "Sprint Regression Tests"
Cohesion: 0.10
Nodes (6): shutil, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 20 - "Canvas Wrap Layout"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 21 - "Graph Edge Routing"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 23 - "Graph Defaults Validation"
Cohesion: 0.10
Nodes (20): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+12 more)

### Community 25 - "Workflow Door Suite"
Cohesion: 0.12
Nodes (5): copy, subprocess, Engine branch contracts, exercised by the actual runner and fake CLI (no…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…

### Community 26 - "Model Alias Resolution"
Cohesion: 0.21
Nodes (12): _alias_provider_pair(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., resolve_models(), _resolve_models() (+4 more)

### Community 27 - "Card Frontend Contract"
Cohesion: 0.17
Nodes (9): ref_node_assert, ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp (+1 more)

### Community 28 - "Metrics Missing UI"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 29 - "Gateway Surface Tests"
Cohesion: 0.18
Nodes (5): gateway, mk_run(), _NoSpawn, Sprint-101 lane D-surface, item #15: the inline card is machinery, not a…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 30 - "Graph Input Validation"
Cohesion: 0.25
Nodes (8): act_save(), _coerce_graph(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Return graph-level and node-level defects together, before any write/spawn., _validation_error()

### Community 31 - "Fanout UI Testing"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 32 - "Retry Contract Testing"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 33 - "Syntax Mode Ordering"
Cohesion: 0.24
Nodes (12): act_library(), act_run(), _hermes_bin(), _lib_path(), library_root(), _note_launch(), `/wf` — the library front door. `/wf` lists; `/wf <name> [note]` tells the…, Absolute launcher path — background runners do NOT inherit an interactive PATH. (+4 more)

### Community 34 - "Inline Header Assertions"
Cohesion: 0.20
Nodes (10): 0.9.0 — 2026-09-24, 1.0.1 — 2026-09-25, Added, Changed, Changelog, Deaths become outcomes, Fixed, Operator surface (+2 more)

### Community 35 - "Engine Gate Testing"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 36 - "Routing Provider Regressions"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 37 - "Lifecycle Regression Testing"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 41 - "Cooperative Steer Testing"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 42 - "Steering Inbox Events"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 43 - "Model Preflight Routing"
Cohesion: 0.33
Nodes (6): model_preflight(), _nearest_effort(), Reasoning levels the (provider, model) route accepts; the global set when the…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 45 - "Prune Gate Testing"
Cohesion: 0.40
Nodes (5): _node_file(), Q1 spawn-time record: written right after Popen succeeds, BEFORE the child is…, B1 (feedback #13/#40): at spawn, copy every inbox line addressed to this node…, _steer_bake(), write_spawn_record()

### Community 49 - "API Call Metrics Tracking"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), Tool-progress evidence for the #5 bounded retry: True only when the dead…, api_calls for ONE dead attempt via the state.db join. Return an integer only…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 50 - "Transcript Directive Parsing"
Cohesion: 0.90
Nodes (5): TranscriptDirectiveLeaf (React Component), TRANSCRIPT_DIRECTIVE_AREA, parseTranscriptDirective(), segmentTranscriptDirectives(), tests/fixtures/mac-source.txt — Transcript Directives Fixture

### Community 53 - "V4 Regression Sign-Off"
Cohesion: 0.15
Nodes (6): pathlib, main(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 54 - "Node Input Resolution"
Cohesion: 0.10
Nodes (23): concurrent_futures, fcntl, signal, build_inputs(), drain_inbox(), extract_json(), fmt_goal(), _inputs_block() (+15 more)

### Community 57 - "API Manifest Tab"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 58 - "Runner Verdict Writing"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

## Knowledge Gaps
- **132 isolated node(s):** `EDGE_TONE`, `$fanExpanded`, `$fanItem`, `$fanOpen`, `MINI` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 469 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `blocked_by()` connect `Workflow Graph Validation` to `Run Lifecycle Actions`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `Run operations and read model` connect `Workflow Graph Validation` to `System Architecture Documentation`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `EngineNextCut` connect `Engine Graph Execution` to `Workflow Door Suite`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **What connects `EDGE_TONE`, `$fanExpanded`, `$fanItem` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Desktop Plugin UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.07950310559006211 - nodes in this community are weakly interconnected._
- **Should `Child Process Runner` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `Fan-out Expand UI Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06890756302521009 - nodes in this community are weakly interconnected._