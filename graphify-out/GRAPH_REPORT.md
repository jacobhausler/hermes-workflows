# Graph Report - tree  (2026-09-29)

## Corpus Check
- 122 files · ~163,766 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1442 nodes · 2895 edges · 88 communities (71 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 176 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wfcommon.py
- __init__.py
- wf.py
- validate_graph_errors
- importlib_util
- test_fanout_expand.mjs
- run_agent_node
- test_prompt_workdir.py
- plugin_api.py
- jload
- os
- test_11_ui_imports.mjs
- pathlib
- test_fanout_item_goal.py
- Changelog
- time
- test_sprint101w2_C3-fanout-gates.py
- shutil
- _adopt_child
- ref_node_assert
- main
- test_live_truth_ui.mjs
- test_pill_rail_expand.mjs
- _ping_route_once
- json
- 11-golden-solo.py
- CurrentAttemptMetrics
- test_register_surface.mjs
- test_canvas_wrap.mjs
- EngineNextCut
- test_node_click_expand.mjs
- sys
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_sprint101_A-door.py
- test
- test_preflight_liveness_152be7f7.py
- test_review_fixes.py
- test_route_efforts_b3c98b2a.py
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_pill_rail.mjs
- SKILL.md
- Run operations and read model
- test_orphan_adopt_790c6ad.py
- act_save
- test_amend_rebake_034849a2.py
- efp
- Contributing to hermes-workflows
- FakeHTTPError
- ref_node_fs
- TeamIntegration
- Graph grammar and authoring boundaries
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- model_preflight
- CoreFaithfulCtx
- test_steer_live_40.py
- build_inputs
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Manual installation — Hermes Workflows 1.1.0
- Hermes Workflows
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- test_failed_events_77.py
- test_prune_0923.py
- test_tier_report_0924.py
- test_tiers.py
- 3. Operate
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_papercuts_0922b.py
- extract_json
- manifest.json
- Integrated
- Run
- fake

## God Nodes (most connected - your core abstractions)
1. `jload()` - 35 edges
2. `efp()` - 33 edges
3. `run_child()` - 30 edges
4. `run_state()` - 22 edges
5. `_adopt_child()` - 21 edges
6. `main()` - 21 edges
7. `loop()` - 21 edges
8. `NodePanel()` - 18 edges
9. `CurrentAttemptMetrics` - 18 edges
10. `act_run()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (88 total, 17 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): Unreleased, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "wfcommon.py"
Cohesion: 0.06
Nodes (51): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, hashlib, shlex, active_child(), _active_spawn(), amend_preview(), blocked_by(), current_attempt() (+43 more)

### Community 2 - "__init__.py"
Cohesion: 0.08
Nodes (41): difflib, act_library(), act_run(), _alias_provider_pair(), _frozen_committed(), handle(), _lane_entry(), _lane_key_error() (+33 more)

### Community 3 - "wf.py"
Cohesion: 0.09
Nodes (36): concurrent_futures, _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), hermes_home(), _next_spawn_no() (+28 more)

### Community 4 - "validate_graph_errors"
Cohesion: 0.06
Nodes (27): rerr(), apply_graph_defaults(), _defaults_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:… (+19 more)

### Community 5 - "importlib_util"
Cohesion: 0.08
Nodes (16): importlib_util, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Lane E: cross-lane executable integration fixtures; no production…, Lane A preconditions: null and missing ancestor fields fail before Popen, then… (+8 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "run_agent_node"
Cohesion: 0.08
Nodes (30): 1.0.17 — 2026-09-28, _attempt_api_calls(), _bounded_retry(), _dangling_placeholders(), fmt_goal(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+22 more)

### Community 8 - "test_prompt_workdir.py"
Cohesion: 0.09
Nodes (27): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+19 more)

### Community 9 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 10 - "jload"
Cohesion: 0.13
Nodes (28): act_amend(), act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_state() (+20 more)

### Community 11 - "os"
Cohesion: 0.08
Nodes (13): os, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, tempfile, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, Authoring door regressions; all state stays in this worktree, no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, The child launcher is operator-controlled, never a tool argument., lock() (+5 more)

### Community 12 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 13 - "pathlib"
Cohesion: 0.10
Nodes (15): copy, pathlib, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness. (+7 more)

### Community 14 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 15 - "Changelog"
Cohesion: 0.08
Nodes (25): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+17 more)

### Community 16 - "time"
Cohesion: 0.09
Nodes (10): contextlib, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Current-attempt heartbeat with real fake child identity; no provider access., v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+2 more)

### Community 17 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 18 - "shutil"
Cohesion: 0.08
Nodes (11): fcntl, glob, hermes_constants, plugin_api, shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').… (+3 more)

### Community 19 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 20 - "ref_node_assert"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 21 - "main"
Cohesion: 0.15
Nodes (20): acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), log(), main(), consume_markers() (+12 more)

### Community 22 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 23 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 24 - "_ping_route_once"
Cohesion: 0.10
Nodes (18): act_inbox(), _import_call_llm(), _ping_retry_after(), _ping_route_once(), _ping_status(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD… (+10 more)

### Community 25 - "json"
Cohesion: 0.11
Nodes (8): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…

### Community 26 - "11-golden-solo.py"
Cohesion: 0.16
Nodes (15): re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), capture(), main() (+7 more)

### Community 28 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 29 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 31 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 32 - "sys"
Cohesion: 0.12
Nodes (5): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 33 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 34 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 35 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 36 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 38 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 39 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 40 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 41 - "test"
Cohesion: 0.23
Nodes (12): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test() (+4 more)

### Community 42 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.21
Nodes (13): check(), contract(), fake_call_llm(), call_llm(), _fake_parse_retry_after(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.… (+5 more)

### Community 43 - "test_review_fixes.py"
Cohesion: 0.13
Nodes (3): answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…

### Community 44 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 45 - "_create_run"
Cohesion: 0.17
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), _liveness_hint_suffix(), Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+3 more)

### Community 47 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 48 - "test_pill_rail.mjs"
Cohesion: 0.17
Nodes (9): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+1 more)

### Community 50 - "Run operations and read model"
Cohesion: 0.18
Nodes (11): 3d. Failures, resume, amend, What you get, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Run and handoff (+3 more)

### Community 51 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 52 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Choose one explicitly supplied source; never discover files on the caller's… (+3 more)

### Community 53 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 54 - "efp"
Cohesion: 0.24
Nodes (11): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer(), mirror(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run… (+3 more)

### Community 55 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 56 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): Exception, EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 57 - "ref_node_fs"
Cohesion: 0.20
Nodes (5): ref_node_fs, code, { fanItems, fanCounts }, here, src

### Community 59 - "Graph grammar and authoring boundaries"
Cohesion: 0.22
Nodes (9): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Top-level provenance, nodes(), 1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the… (+1 more)

### Community 60 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 61 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 62 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 63 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 64 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 65 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 66 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 67 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 68 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 69 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 70 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 71 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 77 - "3. Operate"
Cohesion: 0.40
Nodes (5): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run

### Community 78 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 79 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 83 - "extract_json"
Cohesion: 0.40
Nodes (5): extract_json(), last_balanced_object(), _match_object(), Index of the '}' closing the '{' at i (string-aware), or -1 if unbalanced., Sprint101 #9: the LAST top-level balanced {...} in stdout that json.loads…

### Community 84 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

## Knowledge Gaps
- **243 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+238 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 746 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `plugin.js`, `wfcommon.py`, `model_preflight`, `run_agent_node`?**
  _High betweenness centrality (0.396) - this node is a cross-community bridge._
- **Why does `Unreleased` connect `plugin.js` to `Changelog`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance` connect `wfcommon.py` to `test`, `Run operations and read model`, `jload`, `Changelog`?**
  _High betweenness centrality (0.309) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _243 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05587808417997097 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08246225319396051 - nodes in this community are weakly interconnected._