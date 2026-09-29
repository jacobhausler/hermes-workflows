# Graph Report - tree  (2026-09-29)

## Corpus Check
- 161 files · ~193,682 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1604 nodes · 3179 edges · 118 communities (90 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 213 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- os
- efp
- test_fanout_expand.mjs
- test_prompt_workdir.py
- plugin_api.py
- wfcommon.py
- tempfile
- json
- Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet
- test_11_ui_imports.mjs
- shutil
- test_fanout_item_goal.py
- Changelog
- pathlib
- importlib_util
- wf.py
- subprocess
- run_child
- jload
- ref_node_fs
- test_failures_0923.py
- test_live_truth_ui.mjs
- log
- _SV
- test_pill_rail_expand.mjs
- __init__.py
- sys
- CurrentAttemptMetrics
- _adopt_child
- _stamp_served
- Run operations and read model
- _ping_route_once
- test_register_surface.mjs
- graph_fingerprint
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- act_status
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_tiers.py
- test_require_route_25.py
- _resolve_models
- validate_graph_errors
- node_facts
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- act_amend
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- _create_run
- test_11_integration_team.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- SKILL.md
- build_inputs
- act_save
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- test_validate_0923.py
- act_run
- FakeHTTPError
- write_spawn_record
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- model_preflight
- suite.py
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_status_next.py
- test_steer_live_40.py
- Disclosure verification — clause-by-clause evidence
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Manual installation — Hermes Workflows 1.1.1
- Hermes Workflows
- Operator playbook (measured lessons; each one was paid for)
- graph_check.py
- DoorLane
- test_suite_admission_17.py
- gate_answer_valid
- _bind_run_context
- Claim
- test_papercuts_0922.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- profile_errors
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
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
1. `jload()` - 36 edges
2. `efp()` - 36 edges
3. `run_child()` - 31 edges
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
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (118 total, 28 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "os"
Cohesion: 0.07
Nodes (11): os, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Integrated read-model and parser-valid card dedup checks., Library verbs + /wf command: save (from run_id / inline), library list, run…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1… (+3 more)

### Community 2 - "efp"
Cohesion: 0.09
Nodes (34): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then… (+26 more)

### Community 3 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 4 - "test_prompt_workdir.py"
Cohesion: 0.09
Nodes (28): argparse, fnmatch, Pattern, Nodes and data, excluded(), load_guards(), main(), Path (+20 more)

### Community 5 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 6 - "wfcommon.py"
Cohesion: 0.07
Nodes (29): shlex, _active_spawn(), amend_preview(), apply_graph_defaults(), blocked_by(), current_attempt(), _defaults_errors(), _downstream() (+21 more)

### Community 7 - "tempfile"
Cohesion: 0.09
Nodes (19): signal, tempfile, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.… (+11 more)

### Community 8 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 9 - "Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet"
Cohesion: 0.09
Nodes (27): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+19 more)

### Community 10 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 11 - "shutil"
Cohesion: 0.07
Nodes (8): shutil, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, 4052d57719653b1a: atomic library replay binding, no real runner., Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…

### Community 12 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 13 - "Changelog"
Cohesion: 0.08
Nodes (25): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+17 more)

### Community 14 - "pathlib"
Cohesion: 0.11
Nodes (14): hashlib, pathlib, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., check() (+6 more)

### Community 15 - "importlib_util"
Cohesion: 0.09
Nodes (9): importlib_util, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate… (+1 more)

### Community 16 - "wf.py"
Cohesion: 0.11
Nodes (22): concurrent_futures, _dangling_placeholders(), drain_inbox(), extract_json(), last_balanced_object(), _match_object(), Return {node_id: [steering texts]} for un-consumed steering lines., hermes-workflows engine — replay-skip runner. One process per run, owned by the… (+14 more)

### Community 17 - "subprocess"
Cohesion: 0.11
Nodes (12): contextlib, copy, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness. (+4 more)

### Community 18 - "run_child"
Cohesion: 0.10
Nodes (22): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _harvest_cancelled(), _harvest_death(), _next_spawn_no() (+14 more)

### Community 19 - "jload"
Cohesion: 0.17
Nodes (20): act_list(), act_release(), act_steer(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change. (+12 more)

### Community 20 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 21 - "test_failures_0923.py"
Cohesion: 0.10
Nodes (5): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 22 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 23 - "log"
Cohesion: 0.16
Nodes (20): _bounded_retry(), _lane_gate(), log(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave… (+12 more)

### Community 24 - "_SV"
Cohesion: 0.11
Nodes (14): Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, _SV, _tok_when(), _when_and(), _when_atom() (+6 more)

### Community 25 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 26 - "__init__.py"
Cohesion: 0.15
Nodes (18): difflib, act_inbox(), act_library(), handle(), library_root(), _library_roots(), model_tiers(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The… (+10 more)

### Community 27 - "sys"
Cohesion: 0.11
Nodes (6): sys, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Feedback #68: steer on a node/run that can never spawn reports HONEST results.…

### Community 29 - "_adopt_child"
Cohesion: 0.11
Nodes (17): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _kill_adopted(), _log_recent(), _note_turn_tier(), _proc_alive(), Typed termination from the child's quiet turn report (core PR pending; the… (+9 more)

### Community 30 - "_stamp_served"
Cohesion: 0.13
Nodes (19): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+11 more)

### Community 31 - "Run operations and read model"
Cohesion: 0.13
Nodes (16): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Lanes: in-flight dedupe for pollers (+8 more)

### Community 32 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+9 more)

### Community 33 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 34 - "graph_fingerprint"
Cohesion: 0.19
Nodes (16): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes() (+8 more)

### Community 35 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 36 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 37 - "act_status"
Cohesion: 0.16
Nodes (14): act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts(), _output_pointer() (+6 more)

### Community 38 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 39 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 40 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 43 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 44 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 45 - "test_tiers.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 46 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 47 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 48 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): rerr(), _v(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors() (+4 more)

### Community 49 - "node_facts"
Cohesion: 0.15
Nodes (13): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, find_run(), launch_runs_root(), node_facts(), precondition_facts(), Runs root of the RAW process environment (never the context-resolved home).…, Locate a run dir by id: resolved runs_root() first; legacy launch root only for…, 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed… (+5 more)

### Community 50 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 51 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 52 - "act_amend"
Cohesion: 0.15
Nodes (13): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+5 more)

### Community 53 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 54 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 55 - "_create_run"
Cohesion: 0.20
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.… (+3 more)

### Community 56 - "test_11_integration_team.py"
Cohesion: 0.27
Nodes (3): Lane E: cross-lane executable integration fixtures; no production…, TeamIntegration, until()

### Community 58 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 59 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 61 - "build_inputs"
Cohesion: 0.18
Nodes (10): 1.0.17 — 2026-09-28, 3. The importable subset, stated once, build_inputs(), fmt_goal(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block… (+2 more)

### Community 62 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline… (+3 more)

### Community 63 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 64 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 65 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 66 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 67 - "act_run"
Cohesion: 0.24
Nodes (10): act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty…, WRITE side: the resolved root (new entries land with their runs)., WRITE resolver: always the resolved root (current best version lands there). (+2 more)

### Community 68 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 69 - "write_spawn_record"
Cohesion: 0.20
Nodes (10): _node_file(), _profile_evidence(), B1 (feedback #13/#40): at spawn, copy every inbox line addressed to this node…, Q1 spawn-time record: written right after Popen succeeds, BEFORE the child is…, _steer_bake(), write_spawn_record(), hermes_root(), profile_home() (+2 more)

### Community 70 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 71 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 72 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 73 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 74 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 75 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 76 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 79 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 80 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 81 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.33
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 82 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 83 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 84 - "Manual installation — Hermes Workflows 1.1.1"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 85 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 86 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 87 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 89 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 90 - "gate_answer_valid"
Cohesion: 0.47
Nodes (6): def_hash(), fingerprint_valid(), gate_answer_valid(), _legacy_chain_unchanged(), A record's own rule is authoritative; an unstamped record matches ANY rule. A…, A pre-efp record is valid ONLY if the stored def_hash matches AND every…

### Community 91 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 94 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 95 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 96 - "profile_errors"
Cohesion: 0.40
Nodes (4): launcher_profile(), profile_errors(), Launcher identity, resolved from the door's OWN HERMES_HOME — never from a…, 1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER…

### Community 97 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 98 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 101 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

## Knowledge Gaps
- **271 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+266 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 843 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `act_status`, `Changelog`, `_resolve_models`, `jload`, `gate_answer_valid`, `build_inputs`?**
  _High betweenness centrality (0.261) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `Anthropic Claude Code "dynamic workflows" — JS grammar fact sheet`, `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _271 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.06606606606606606 - nodes in this community are weakly interconnected._
- **Should `efp` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._