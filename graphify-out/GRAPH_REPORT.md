# Graph Report - tree  (2026-09-29)

## Corpus Check
- 164 files · ~198,725 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1654 nodes · 3284 edges · 123 communities (95 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 214 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- CurrentAttemptMetrics
- importlib_util
- lane_recover.py
- plugin_api.py
- os
- shutil
- test_fanout_expand.mjs
- sys
- test_lane_hygiene_preamble_8edcc9bf.py
- wf.py
- json
- test_11_ui_imports.mjs
- test_failures_0923.py
- efp
- wfcommon.py
- test_fanout_item_goal.py
- __init__.py
- loop
- _adopt_child
- pathlib
- _stamp_served
- ref_node_fs
- test_live_truth_ui.mjs
- run_child
- run_agent_node
- test_pill_rail_expand.mjs
- jload
- test_register_surface.mjs
- _ping_route_once
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- test_require_route_25.py
- act_status
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- run_state
- LiveTruth
- test_node_panel.mjs
- test_tiers.py
- act_amend
- validate_graph_errors
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- _create_run
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- write_spawn_record
- Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet
- test_11_integration_team.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- Changelog
- agent
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- test
- gate_answer_valid
- Contributing to hermes-workflows
- FakeHTTPError
- test_sprint101w2_B2-retry.py
- _SV
- AGENTS.md — front door for agents
- Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON)
- Disclosure verification — clause-by-clause evidence
- test_engine.py
- test_routing_routes.py
- model_preflight
- plugin-catalog: add `hermes-workflows` (community, automation)
- act_steer
- suite.py
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- _defaults_errors
- AGENTS.md
- 4. Contribute
- 1.0.2 — 2026-09-26 — the run watches itself
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Manual installation — Hermes Workflows 1.1.1
- Hermes Workflows
- graph_check.py
- DoorLane
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- node_facts
- 1.0.1 — 2026-09-25
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_sprint101_D-surface.py
- test_validator_caps.py
- profile_errors
- 0.9.0 — 2026-09-24
- manifest.json
- _coerce_graph
- 2. The `meta` export block
- dynamic-agent-count.js
- _LADDER
- Integrated
- Run
- date-now.js
- meta-nonliteral.js
- Ctx
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
1. `efp()` - 37 edges
2. `jload()` - 36 edges
3. `run_child()` - 33 edges
4. `run_state()` - 23 edges
5. `_adopt_child()` - 22 edges
6. `loop()` - 22 edges
7. `log()` - 21 edges
8. `main()` - 21 edges
9. `act_run()` - 20 edges
10. `NodePanel()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `6. Runtime constraints & limits (verbatim table, S1 §"Behavior and limits")` --references--> `agent()`  [INFERRED]
  references/anthropic-grammar.md → tests/test_prune_0923.py
- `9. Worktree isolation for workflow subagents` --references--> `agent()`  [INFERRED]
  references/anthropic-grammar.md → tests/test_prune_0923.py
- `4. What this PR does not decide` --references--> `agent()`  [INFERRED]
  references/dialect.md → tests/test_prune_0923.py

## Import Cycles
- None detected.

## Communities (123 total, 28 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (91): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+83 more)

### Community 1 - "CurrentAttemptMetrics"
Cohesion: 0.05
Nodes (31): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Contributor checks (not ordinary user setup) (+23 more)

### Community 2 - "importlib_util"
Cohesion: 0.07
Nodes (25): contextlib, hashlib, importlib_util, signal, tempfile, capture(), main(), normalize() (+17 more)

### Community 3 - "lane_recover.py"
Cohesion: 0.08
Nodes (34): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+26 more)

### Community 4 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 5 - "os"
Cohesion: 0.07
Nodes (11): os, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Integrated read-model and parser-valid card dedup checks., Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;… (+3 more)

### Community 6 - "shutil"
Cohesion: 0.06
Nodes (9): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, 4052d57719653b1a: atomic library replay binding, no real runner., lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+1 more)

### Community 7 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 8 - "sys"
Cohesion: 0.08
Nodes (16): copy, subprocess, sys, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-… (+8 more)

### Community 9 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (27): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+19 more)

### Community 10 - "wf.py"
Cohesion: 0.09
Nodes (28): Unreleased, concurrent_futures, build_inputs(), drain_inbox(), extract_json(), _inputs_block(), last_balanced_object(), _match_object() (+20 more)

### Community 11 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 12 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 13 - "test_failures_0923.py"
Cohesion: 0.08
Nodes (10): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, check(), main(), #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run() (+2 more)

### Community 14 - "efp"
Cohesion: 0.12
Nodes (26): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+18 more)

### Community 15 - "wfcommon.py"
Cohesion: 0.11
Nodes (26): shlex, current_attempt(), effective_runs_root(), launch_runs_root(), node_child_home(), node_child_metrics(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,… (+18 more)

### Community 16 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 17 - "__init__.py"
Cohesion: 0.13
Nodes (25): difflib, _alias_provider_pair(), handle(), _model_policy_error(), model_tiers(), _ping_note(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty… (+17 more)

### Community 18 - "loop"
Cohesion: 0.14
Nodes (22): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), _bounded_retry(), emit(), _fail_precondition(), finalize(), log() (+14 more)

### Community 19 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _note_turn_tier() (+14 more)

### Community 20 - "pathlib"
Cohesion: 0.11
Nodes (13): glob, hermes_constants, pathlib, plugin_api, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+5 more)

### Community 21 - "_stamp_served"
Cohesion: 0.11
Nodes (22): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+14 more)

### Community 22 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 23 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 24 - "run_child"
Cohesion: 0.10
Nodes (21): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _is_build_lane(), _lane_hygiene_preamble(), _next_spawn_no() (+13 more)

### Community 25 - "run_agent_node"
Cohesion: 0.12
Nodes (20): _dangling_placeholders(), _lane_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported…, fb-digest-29d (64c6772b): a node that declares `repo: <path>` owns a git lane,… (+12 more)

### Community 26 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 27 - "jload"
Cohesion: 0.16
Nodes (19): act_library(), act_run(), act_save(), _input_graph(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+11 more)

### Community 28 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 29 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 30 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 31 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 32 - "test_require_route_25.py"
Cohesion: 0.12
Nodes (9): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned…, set_ping() (+1 more)

### Community 33 - "act_status"
Cohesion: 0.16
Nodes (14): act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts(), _output_pointer() (+6 more)

### Community 34 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 35 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 36 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 37 - "run_state"
Cohesion: 0.16
Nodes (15): act_release(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…, Derived truth of a run dir: status, per-node status, held gate meta. status:…, 91b9a3de: cross-container liveness truth. The runner takes an exclusive…, A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives… (+7 more)

### Community 39 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 40 - "test_tiers.py"
Cohesion: 0.16
Nodes (6): atexit, importlib, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 41 - "act_amend"
Cohesion: 0.14
Nodes (14): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _model_names_valid(), _profile_error(), Return graph-level and node-level defects together, before any write/spawn., 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY… (+6 more)

### Community 42 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): rerr(), _v(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors() (+4 more)

### Community 43 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 44 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 45 - "_create_run"
Cohesion: 0.18
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+4 more)

### Community 46 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 47 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 48 - "write_spawn_record"
Cohesion: 0.17
Nodes (12): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, _node_file(), _profile_evidence(), B1 (feedback #13/#40): at spawn, copy every inbox line addressed to this node…, Q1 spawn-time record: written right after Popen succeeds, BEFORE the child is…, _steer_bake(), write_spawn_record(), find_run() (+4 more)

### Community 49 - "Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet"
Cohesion: 0.17
Nodes (11): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 4. `args` global, 5. File locations & discovery, 6. Runtime constraints & limits (verbatim table, S1 §"Behavior and limits"), 7. Plain-JS rule, TypeScript, and loops, 8. Model routing precedence per stage (+3 more)

### Community 50 - "test_11_integration_team.py"
Cohesion: 0.27
Nodes (3): Lane E: cross-lane executable integration fixtures; no production…, TeamIntegration, until()

### Community 52 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 53 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 54 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 55 - "agent"
Cohesion: 0.25
Nodes (11): label(), Labeled(), 3.1 `agent(prompt, options?)`, 3.2 `parallel(tasks)`, 3.3 `pipeline(items, stage1, stage2, ...)`, 3.4 `phase(title)`, 3.5 `log(message)`, 3.6 Script return value (+3 more)

### Community 56 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 57 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 58 - "test"
Cohesion: 0.24
Nodes (10): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), _active_spawn(), _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, All verified uncommitted child identities, never historical DB liveness. (+2 more)

### Community 59 - "gate_answer_valid"
Cohesion: 0.24
Nodes (11): amend_preview(), _downstream(), fingerprint_valid(), gate_answer_valid(), _legacy_chain_unchanged(), node_rec(), {added, removed, changed, will_rerun, unchanged} for a proposed graph against…, A record's own rule is authoritative; an unstamped record matches ANY rule. A… (+3 more)

### Community 60 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 61 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 62 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 64 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 65 - "Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON)"
Cohesion: 0.25
Nodes (6): 1.0.17 — 2026-09-28, 1. Shape of each side in one screen, 3. The importable subset, stated once, 4. What this PR does not decide, Dialect map: Claude Code dynamic workflows (.js) ↔ hermes-workflows graphs (JSON), fmt_goal()

### Community 66 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.25
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 67 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 68 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 69 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 70 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 71 - "act_steer"
Cohesion: 0.29
Nodes (7): act_inbox(), act_steer(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 72 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 73 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 77 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 78 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 80 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 81 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 82 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (5): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, Meta

### Community 83 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 84 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 85 - "Manual installation — Hermes Workflows 1.1.1"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 86 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 87 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 89 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 90 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 91 - "node_facts"
Cohesion: 0.33
Nodes (6): node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 92 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 93 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 94 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 96 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 97 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 98 - "profile_errors"
Cohesion: 0.40
Nodes (4): launcher_profile(), profile_errors(), Launcher identity, resolved from the door's OWN HERMES_HOME — never from a…, 1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER…

### Community 99 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 100 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 101 - "_coerce_graph"
Cohesion: 0.50
Nodes (4): _coerce_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 102 - "2. The `meta` export block"
Cohesion: 0.50
Nodes (4): 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block

### Community 103 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **271 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+266 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 862 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `act_status`, `run_state`, `wf.py`, `__init__.py`, `Changelog`, `test`, `gate_answer_valid`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Why does `label()` connect `agent` to `plugin.js`, `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _271 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06067845198279981 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.0546583850931677 - nodes in this community are weakly interconnected._
- **Should `importlib_util` be split into smaller, more focused modules?**
  _Cohesion score 0.06565656565656566 - nodes in this community are weakly interconnected._