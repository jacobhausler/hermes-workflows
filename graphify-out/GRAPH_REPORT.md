# Graph Report - tree  (2026-09-29)

## Corpus Check
- 162 files · ~200,197 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1697 nodes · 3420 edges · 107 communities (78 shown, 29 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 228 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- __init__.py
- wfcommon.py
- efp
- pathlib
- test_preflight_liveness_152be7f7.py
- plugin_api.py
- .meta
- time
- test_fanout_expand.mjs
- os
- sys
- shutil
- test_prompt_workdir.py
- subprocess
- test_11_ui_imports.mjs
- runner_alive
- test_fanout_item_goal.py
- _Exporter
- Changelog
- test_sprint101w2_C3-fanout-gates.py
- run_child
- json
- validate_graph_errors
- run_agent_node
- wf.py
- ref_node_fs
- test_live_truth_ui.mjs
- _adopt_child
- wf_dialect.py
- _Importer
- test_pill_rail_expand.mjs
- CurrentAttemptMetrics
- Run operations and read model
- re
- test_require_route_25.py
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- .refuse
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- Disclosure verification — clause-by-clause evidence
- SKILL.md
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- _create_run
- graph_fingerprint
- DialectRefusal
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- AGENTS.md
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- hermes_home
- test_orphan_adopt_790c6ad.py
- test_card_frontend_contract.mjs
- Contributing to hermes-workflows
- TeamIntegration
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- _parse_literal
- model_preflight
- suite.py
- CoreFaithfulCtx
- test_sprint101w2_C1-defaults.py
- test_steer_live_40.py
- hermes_home
- Manifest decisions (publish pass, 2026-09-24)
- Manual installation — Hermes Workflows 1.1.0
- Hermes Workflows
- DoorLane
- test_failed_events_77.py
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- _bind_run_context
- Claim
- test_sprint101_D-surface.py
- manifest.json
- dynamic-agent-count.js
- _LADDER
- test_fp_rule_95d70102.py
- Integrated
- _AdoptedHandle
- _cancel_evidence
- _quota_note
- Run
- date-now.js
- meta-nonliteral.js
- Ctx
- fake
- args-iterable.js
- args-template.js
- audit-routes.js
- pipeline-glue-stage.js
- pipeline-length-template.js
- dialect/README.md
- sequential-awaits.js
- static-parallel.js
- two-stage-pipeline.js
- unknown-option.js
- while-loop.js

## God Nodes (most connected - your core abstractions)
1. `jload()` - 35 edges
2. `efp()` - 35 edges
3. `run_child()` - 31 edges
4. `_Importer` - 24 edges
5. `loop()` - 23 edges
6. `_Exporter` - 23 edges
7. `log()` - 22 edges
8. `_adopt_child()` - 22 edges
9. `run_state()` - 22 edges
10. `main()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (107 total, 29 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (92): Unreleased, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+84 more)

### Community 1 - "__init__.py"
Cohesion: 0.05
Nodes (75): difflib, act_amend(), act_library(), act_run(), act_save(), _alias_provider_pair(), _coerce_graph(), _frozen_committed() (+67 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.05
Nodes (50): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), _downstream(), effective_runs_root() (+42 more)

### Community 3 - "efp"
Cohesion: 0.08
Nodes (50): File-authored graphs, test(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), All per-item spawn records with a live pid, once every item is RUNNING., read_children(), make_run(), Create the run dir through the door with the runner spawn suppressed, then… (+42 more)

### Community 4 - "pathlib"
Cohesion: 0.08
Nodes (22): contextlib, hashlib, importlib_util, pathlib, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+14 more)

### Community 5 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 6 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 7 - ".meta"
Cohesion: 0.08
Nodes (32): 1.0.17 — 2026-09-28, label(), 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5) (+24 more)

### Community 8 - "time"
Cohesion: 0.07
Nodes (15): glob, hermes_constants, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.… (+7 more)

### Community 9 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 10 - "os"
Cohesion: 0.07
Nodes (15): copy, os, tempfile, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, Authoring door regressions; all state stays in this worktree, no…, Engine branch contracts, exercised by the actual runner and fake CLI (no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+7 more)

### Community 11 - "sys"
Cohesion: 0.07
Nodes (14): atexit, fcntl, importlib, sys, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>. (+6 more)

### Community 12 - "shutil"
Cohesion: 0.06
Nodes (8): shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 13 - "test_prompt_workdir.py"
Cohesion: 0.10
Nodes (26): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+18 more)

### Community 14 - "subprocess"
Cohesion: 0.07
Nodes (9): subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, answer() (+1 more)

### Community 15 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 16 - "runner_alive"
Cohesion: 0.10
Nodes (25): act_inbox(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_key_error(), _lane_state() (+17 more)

### Community 17 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 18 - "_Exporter"
Cohesion: 0.17
Nodes (9): _Exporter, _js_literal(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, goal (+context) + the exporter-owned refs section for after/inputs., `{field}` tokens -> `${param.field}` per wf.py fmt_goal, `{item}` ->…, _run_args() (+1 more)

### Community 19 - "Changelog"
Cohesion: 0.08
Nodes (25): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+17 more)

### Community 20 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 21 - "run_child"
Cohesion: 0.09
Nodes (25): _child_spoke(), _classify_rc_output(), derived_contract(), _first_message_s(), _log_recent(), _next_spawn_no(), _node_file(), _profile_evidence() (+17 more)

### Community 22 - "json"
Cohesion: 0.09
Nodes (10): json, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Identical solo child wrapper for both tag and candidate; records env key sets.…, End-to-end test of the `workflow` tool door against fake hermes., Library verbs + /wf command: save (from run_id / inline), library list, run… (+2 more)

### Community 23 - "validate_graph_errors"
Cohesion: 0.09
Nodes (20): rerr(), _v(), apply_graph_defaults(), _defaults_errors(), grammar_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key… (+12 more)

### Community 24 - "run_agent_node"
Cohesion: 0.11
Nodes (22): _bounded_retry(), _dangling_placeholders(), _lane_gate(), #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported… (+14 more)

### Community 25 - "wf.py"
Cohesion: 0.13
Nodes (21): concurrent_futures, build_inputs(), drain_inbox(), extract_json(), _inputs_block(), last_balanced_object(), _match_object(), Return {node_id: [steering texts]} for un-consumed steering lines. (+13 more)

### Community 26 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 27 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 28 - "_adopt_child"
Cohesion: 0.12
Nodes (21): _adopt_child(), _fail_precondition(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), log(), _note_turn_tier(), now() (+13 more)

### Community 29 - "wf_dialect.py"
Cohesion: 0.10
Nodes (18): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), node_check() (+10 more)

### Community 30 - "_Importer"
Cohesion: 0.21
Nodes (11): _Importer, _line(), _match_close(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., Offset of the bracket closing the one at `open_at`., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids). (+3 more)

### Community 31 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 33 - "Run operations and read model"
Cohesion: 0.13
Nodes (16): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Lanes: in-flight dedupe for pollers (+8 more)

### Community 34 - "re"
Cohesion: 0.17
Nodes (14): re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), capture(), main() (+6 more)

### Community 35 - "test_require_route_25.py"
Cohesion: 0.12
Nodes (10): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned…, set_ping() (+2 more)

### Community 36 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 37 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 38 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 39 - ".refuse"
Cohesion: 0.21
Nodes (6): _control_kw(), _forbidden_label(), Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, A fan-out ITEM goal: item/prev fields -> bare `{field}` (wf.py fmt_goal).

### Community 40 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 41 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 42 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 43 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 44 - "SKILL.md"
Cohesion: 0.14
Nodes (10): Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics (+2 more)

### Community 47 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 48 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 49 - "_create_run"
Cohesion: 0.18
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+4 more)

### Community 50 - "graph_fingerprint"
Cohesion: 0.26
Nodes (12): Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test() (+4 more)

### Community 51 - "DialectRefusal"
Cohesion: 0.18
Nodes (8): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 52 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 53 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 54 - "AGENTS.md"
Cohesion: 0.20
Nodes (7): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Node budgets

### Community 56 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 57 - "hermes_home"
Cohesion: 0.17
Nodes (12): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), hermes_home(), hermes_root(), Read model.workflows_forbidden_models on the child seat, including bare CLI… (+4 more)

### Community 58 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 59 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 60 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 62 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 64 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 65 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 66 - "_parse_literal"
Cohesion: 0.25
Nodes (6): _parse_literal(), A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, _Ref, _Tpl, _unescape()

### Community 67 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 68 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 69 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 71 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 72 - "hermes_home"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 73 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 74 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 75 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 78 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 79 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 80 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 82 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 83 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 84 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 86 - "test_fp_rule_95d70102.py"
Cohesion: 0.67
Nodes (3): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change.

### Community 89 - "_cancel_evidence"
Cohesion: 0.50
Nodes (4): _cancel_evidence(), child_work_dir(), A4: every child starts in <run>/work/<node>[.<i>]/. Relative paths land in the…, a2d7f664: honest evidence for a quorum-straggler cancel. Snapshot of the…

### Community 90 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

## Knowledge Gaps
- **269 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 858 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `label()` connect `.meta` to `plugin.js`, `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **Why does `2. The mapping table` connect `.meta` to `Run operations and read model`, `_adopt_child`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `Unreleased` connect `plugin.js` to `__init__.py`, `Changelog`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.059841047218326324 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04750512645249488 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05429864253393665 - nodes in this community are weakly interconnected._