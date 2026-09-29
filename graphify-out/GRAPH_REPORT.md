# Graph Report - tree  (2026-09-29)

## Corpus Check
- 122 files · ~164,937 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1442 nodes · 2906 edges · 91 communities (72 shown, 19 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- EngineNextCut
- plugin_api.py
- pathlib
- sys
- test_fanout_expand.mjs
- run_agent_node
- test_prompt_workdir.py
- Changelog
- test_11_ui_imports.mjs
- __init__.py
- test_fanout_item_goal.py
- shutil
- test_sprint101w2_C3-fanout-gates.py
- main
- importlib_util
- json
- run_state
- test_card_frontend_contract.mjs
- test_live_truth_ui.mjs
- 11-golden-solo.py
- test_register_surface.mjs
- CurrentAttemptMetrics
- test
- os
- validate_graph_errors
- _ping_route_once
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- Disclosure verification — clause-by-clause evidence
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- test_require_route_25.py
- test_orphan_adopt_790c6ad.py
- test_metrics_missing_ui.mjs
- efp
- test_route_efforts_b3c98b2a.py
- amend
- test_deleted_cwd_resume_5c37b19.py
- test_preflight_liveness_152be7f7.py
- act_amend
- act_save
- test_amend_rebake_034849a2.py
- SKILL.md
- Contributing to hermes-workflows
- test_validate_0923.py
- act_run
- _create_run
- TeamIntegration
- FakeHTTPError
- Graph grammar and authoring boundaries
- test_fanout_ui.mjs
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- model_preflight
- Run operations and read model
- CoreFaithfulCtx
- test_review_fixes.py
- test_status_next.py
- test_steer_live_40.py
- _route_hold
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Manual installation — Hermes Workflows 1.1.0
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- test_failed_events_77.py
- test_model_law_dad50be0.py
- test_prune_0923.py
- test_tiers.py
- test_v3_fixes.py
- _bind_run_context
- Claim
- test_papercuts_0922b.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- manifest.json
- _LADDER
- Integrated
- _AdoptedHandle
- Run
- fake

## God Nodes (most connected - your core abstractions)
1. `jload()` - 35 edges
2. `efp()` - 33 edges
3. `run_child()` - 31 edges
4. `_adopt_child()` - 22 edges
5. `run_state()` - 22 edges
6. `main()` - 21 edges
7. `loop()` - 21 edges
8. `act_run()` - 19 edges
9. `NodePanel()` - 18 edges
10. `CurrentAttemptMetrics` - 18 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `Unreleased` --references--> `_resolve_models()`  [INFERRED]
  CHANGELOG.md → __init__.py
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (91 total, 19 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (84): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+76 more)

### Community 1 - "wf.py"
Cohesion: 0.06
Nodes (60): concurrent_futures, _adopt_child(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), extract_json() (+52 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.05
Nodes (58): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, shlex, Commit actual child seat truth, never the requested alias. No row means unknown., _stamp_served(), _active_spawn(), _active_spawns(), amend_preview(), child_metrics() (+50 more)

### Community 3 - "EngineNextCut"
Cohesion: 0.08
Nodes (22): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+14 more)

### Community 4 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 5 - "pathlib"
Cohesion: 0.09
Nodes (20): contextlib, copy, hashlib, pathlib, subprocess, tempfile, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., F3 boundary/claim integration: real door processes + kernel flock; no hook in… (+12 more)

### Community 6 - "sys"
Cohesion: 0.07
Nodes (13): sqlite3, sys, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires… (+5 more)

### Community 7 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 8 - "run_agent_node"
Cohesion: 0.07
Nodes (33): _attempt_api_calls(), _bounded_retry(), build_inputs(), _dangling_placeholders(), _inputs_block(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+25 more)

### Community 9 - "test_prompt_workdir.py"
Cohesion: 0.10
Nodes (26): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+18 more)

### Community 10 - "Changelog"
Cohesion: 0.07
Nodes (28): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes (+20 more)

### Community 11 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 12 - "__init__.py"
Cohesion: 0.11
Nodes (27): difflib, _alias_provider_pair(), handle(), _lane_key_error(), _last_event_ts(), _model_policy_error(), model_tiers(), _output_pointer() (+19 more)

### Community 13 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 14 - "shutil"
Cohesion: 0.08
Nodes (7): fcntl, shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…

### Community 15 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 16 - "main"
Cohesion: 0.14
Nodes (22): acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), log(), main(), consume_markers() (+14 more)

### Community 17 - "importlib_util"
Cohesion: 0.09
Nodes (8): importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, 4052d57719653b1a: atomic library replay binding, no real runner., Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph()

### Community 18 - "json"
Cohesion: 0.11
Nodes (11): json, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane E: cross-lane executable integration fixtures; no production…, Lane A preconditions: null and missing ancestor fields fail before Popen, then… (+3 more)

### Community 19 - "run_state"
Cohesion: 0.17
Nodes (20): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), _lane_state(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume… (+12 more)

### Community 20 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 21 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 22 - "11-golden-solo.py"
Cohesion: 0.15
Nodes (16): re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), capture(), main() (+8 more)

### Community 23 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 25 - "test"
Cohesion: 0.16
Nodes (18): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), state(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), def_hash() (+10 more)

### Community 26 - "os"
Cohesion: 0.12
Nodes (8): os, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Authoring door regressions; all state stays in this worktree, no…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 27 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): rerr(), apply_graph_defaults(), _defaults_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:… (+7 more)

### Community 28 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 29 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 30 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 31 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.12
Nodes (14): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, 6. Desktop gate answer (maintainer ask #122099, teknium1), Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA (+6 more)

### Community 32 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 33 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 34 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 36 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 37 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 38 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 39 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 40 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 41 - "efp"
Cohesion: 0.23
Nodes (12): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then… (+4 more)

### Community 42 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 43 - "amend"
Cohesion: 0.17
Nodes (12): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get, Nodes and data (+4 more)

### Community 45 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 46 - "act_amend"
Cohesion: 0.18
Nodes (11): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, #25: node key > graph defaults > default True on nodes that pin an explicit… (+3 more)

### Community 47 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline… (+3 more)

### Community 48 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 50 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 51 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 52 - "act_run"
Cohesion: 0.27
Nodes (10): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), library_root(), 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty…, `/wf` — the library front door. `/wf <name> [note]` supplies the note… (+2 more)

### Community 53 - "_create_run"
Cohesion: 0.20
Nodes (9): _card(), _create_run(), _hermes_bin(), _identity_stamps(), 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.…, Use the tool worker's task-local session, not another turn's process env. (+1 more)

### Community 55 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 56 - "Graph grammar and authoring boundaries"
Cohesion: 0.22
Nodes (8): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Top-level provenance, nodes(), 1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the…, source_digest()

### Community 57 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 58 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 60 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 61 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 62 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 63 - "Run operations and read model"
Cohesion: 0.29
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 64 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 66 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 67 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 68 - "_route_hold"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 69 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 70 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 71 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 72 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 73 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 76 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 80 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 83 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 84 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 85 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

## Knowledge Gaps
- **224 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 743 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.345) - this node is a cross-community bridge._
- **Why does `nudgeOwner()` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06638655462184874 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06174863387978142 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05480225988700565 - nodes in this community are weakly interconnected._
- **Should `EngineNextCut` be split into smaller, more focused modules?**
  _Cohesion score 0.07957957957957958 - nodes in this community are weakly interconnected._