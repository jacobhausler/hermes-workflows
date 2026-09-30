# Graph Report - tree  (2026-09-30)

## Corpus Check
- 169 files · ~217,475 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1817 nodes · 3686 edges · 126 communities (97 shown, 29 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 246 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- CurrentAttemptMetrics
- wfcommon.py
- importlib_util
- lane_recover.py
- _Importer
- jload
- test_fanout_expand.mjs
- _Exporter
- pathlib
- test_lifecycle_next_cut_0923.py
- shutil
- json
- wf.py
- test_11_ui_imports.mjs
- run_child
- wf_dialect.py
- time
- test_fanout_item_goal.py
- loop
- efp
- test_cross_container_liveness_91b9a3de.py
- subprocess
- ref_node_assert
- act_run
- test_prompt_workdir.py
- validate_graph_errors
- test_live_truth_ui.mjs
- __init__.py
- test_pill_rail_expand.mjs
- os
- plugin_api.py
- _ping_route_once
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- sys
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- _SV
- Disclosure verification — clause-by-clause evidence
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- one
- test_require_route_25.py
- _resolve_models
- test_lane_hygiene_preamble_8edcc9bf.py
- run_agent_node
- 3. Operate
- test_orphan_adopt_790c6ad.py
- act_amend
- _create_run
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- Changelog
- DialectRefusal
- test_amend_rebake_034849a2.py
- test
- test_node_facts.py
- Contributing to hermes-workflows
- ref_node_fs
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- _transient_retry
- .run
- Run operations and read model
- test_sprint101w2_B2-retry.py
- _stamp_served
- emit
- test_engine.py
- test_routing_routes.py
- model_preflight
- CoreFaithfulCtx
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- AGENTS.md
- 4. Contribute
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _input_graph
- Manual installation — Hermes Workflows 1.1.1
- Hermes Workflows
- DoorLane
- test_suite_admission_17.py
- test_tier_report_0924.py
- test_tiers.py
- 1.0.1 — 2026-09-25
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- _AdoptedHandle
- _cancel_evidence
- _quota_note
- Run
- release_gate
- date-now.js
- meta-nonliteral.js
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
1. `efp()` - 38 edges
2. `jload()` - 36 edges
3. `run_child()` - 33 edges
4. `_Importer` - 27 edges
5. `_Exporter` - 26 edges
6. `run_state()` - 26 edges
7. `loop()` - 23 edges
8. `log()` - 22 edges
9. `_adopt_child()` - 22 edges
10. `main()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (126 total, 29 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "CurrentAttemptMetrics"
Cohesion: 0.05
Nodes (45): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+37 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.06
Nodes (46): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), _downstream(), effective_runs_root() (+38 more)

### Community 3 - "importlib_util"
Cohesion: 0.06
Nodes (25): importlib_util, signal, tempfile, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, main() (+17 more)

### Community 4 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 5 - "_Importer"
Cohesion: 0.14
Nodes (16): _forbidden_label(), _Importer, _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,… (+8 more)

### Community 6 - "jload"
Cohesion: 0.10
Nodes (33): Unreleased, act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume… (+25 more)

### Community 7 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 8 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 9 - "pathlib"
Cohesion: 0.08
Nodes (17): hashlib, pathlib, re, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Regression: launch a run in the tool's session; the payload carries a parser-…, check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses() (+9 more)

### Community 10 - "test_lifecycle_next_cut_0923.py"
Cohesion: 0.06
Nodes (8): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 11 - "shutil"
Cohesion: 0.06
Nodes (9): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn. (+1 more)

### Community 12 - "json"
Cohesion: 0.08
Nodes (15): glob, hermes_constants, json, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+7 more)

### Community 13 - "wf.py"
Cohesion: 0.08
Nodes (28): concurrent_futures, _child_spoke(), derived_contract(), drain_inbox(), extract_json(), _fail_precondition(), _first_message_s(), _kill_adopted() (+20 more)

### Community 14 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 15 - "run_child"
Cohesion: 0.12
Nodes (29): _adopt_child(), _classify_rc_output(), _harvest_cancelled(), _harvest_death(), log(), _log_recent(), _node_file(), _note_turn_tier() (+21 more)

### Community 16 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): _const_name(), export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), _match_close() (+16 more)

### Community 17 - "time"
Cohesion: 0.07
Nodes (8): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Library verbs + /wf command: save (from run_id / inline), library list, run…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, time

### Community 18 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 19 - "loop"
Cohesion: 0.13
Nodes (25): main(), consume_markers(), loop(), deps_ok(), state(), park_gate(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run…, save_node() (+17 more)

### Community 20 - "efp"
Cohesion: 0.13
Nodes (24): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+16 more)

### Community 21 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.08
Nodes (10): contextlib, fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, Current-attempt heartbeat with real fake child identity; no provider access., mkrun() (+2 more)

### Community 22 - "subprocess"
Cohesion: 0.10
Nodes (10): copy, subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Engine branch contracts, exercised by the actual runner and fake CLI (no…, Integrated read-model and parser-valid card dedup checks. (+2 more)

### Community 23 - "ref_node_assert"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 24 - "act_run"
Cohesion: 0.12
Nodes (21): act_library(), act_run(), act_save(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), library_root() (+13 more)

### Community 25 - "test_prompt_workdir.py"
Cohesion: 0.15
Nodes (18): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+10 more)

### Community 26 - "validate_graph_errors"
Cohesion: 0.10
Nodes (18): _v(), _defaults_errors(), grammar_errors(), Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key… (+10 more)

### Community 27 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 28 - "__init__.py"
Cohesion: 0.13
Nodes (19): difflib, act_inbox(), act_release_lock(), handle(), _lane_key_error(), _lane_state(), _last_event_ts(), model_tiers() (+11 more)

### Community 29 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 30 - "os"
Cohesion: 0.11
Nodes (9): os, admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+1 more)

### Community 31 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 32 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+9 more)

### Community 33 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 34 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 35 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 36 - "sys"
Cohesion: 0.12
Nodes (7): sys, Identical solo child wrapper for both tag and candidate; records env key sets.…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph(), Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…

### Community 37 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 38 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 39 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 40 - "_SV"
Cohesion: 0.14
Nodes (9): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not() (+1 more)

### Community 41 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 44 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 45 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 46 - "one"
Cohesion: 0.14
Nodes (12): 1.0.17 — 2026-09-28, _bounded_retry(), _dangling_placeholders(), fmt_goal(), #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported…, Machine-generated resume preamble prepended to the goal for the ONE #5 re-… (+4 more)

### Community 47 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 48 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 49 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.22
Nodes (12): check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file., step() (+4 more)

### Community 50 - "run_agent_node"
Cohesion: 0.16
Nodes (14): build_inputs(), _inputs_block(), _lane_gate(), Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block… (+6 more)

### Community 51 - "3. Operate"
Cohesion: 0.15
Nodes (13): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+5 more)

### Community 52 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 53 - "act_amend"
Cohesion: 0.15
Nodes (13): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+5 more)

### Community 54 - "_create_run"
Cohesion: 0.18
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+4 more)

### Community 55 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 56 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 58 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 59 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 60 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 61 - "DialectRefusal"
Cohesion: 0.20
Nodes (7): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…

### Community 62 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 63 - "test"
Cohesion: 0.24
Nodes (10): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), active_child(), ONE verification law for a spawn record (790c6ad): status=running + efp match +… (+2 more)

### Community 64 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 65 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 66 - "ref_node_fs"
Cohesion: 0.20
Nodes (5): ref_node_fs, code, { fanItems, fanCounts }, here, src

### Community 67 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 69 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 70 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 71 - "_transient_retry"
Cohesion: 0.20
Nodes (10): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, _retry_conf_params(), _tool_progress(), _transient_retry() (+2 more)

### Community 72 - ".run"
Cohesion: 0.22
Nodes (5): _control_kw(), _line(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _Refuse, _statements()

### Community 73 - "Run operations and read model"
Cohesion: 0.25
Nodes (8): 3c. Fan-out, gates, branches, What you get, Flock law: liveness, the child-probe rule, and `release-lock`, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature)

### Community 74 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 75 - "_stamp_served"
Cohesion: 0.28
Nodes (9): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Commit actual child seat truth, never the requested alias. No row means unknown., _route_hold(), _route_home(), _seat_alias_map() (+1 more)

### Community 76 - "emit"
Cohesion: 0.25
Nodes (8): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), finalize(), Single-runner admission. An advisory flock held for the process lifetime IS the…, #44 escape hatch: `wf.py release-lock <run_id>`. Prints the verdict JSON…, release_lock_cli()

### Community 77 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 78 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 79 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 80 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 82 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 83 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 85 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 86 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 87 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 88 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 89 - "_input_graph"
Cohesion: 0.33
Nodes (6): _coerce_graph(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 90 - "Manual installation — Hermes Workflows 1.1.1"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 91 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 93 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 96 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 97 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 98 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 101 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 102 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 103 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 104 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 108 - "_cancel_evidence"
Cohesion: 0.50
Nodes (4): _cancel_evidence(), child_work_dir(), A4: every child starts in <run>/work/<node>[.<i>]/. Relative paths land in the…, a2d7f664: honest evidence for a quorum-straggler cancel. Snapshot of the…

### Community 109 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

### Community 111 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **269 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 916 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `jload`, `_resolve_models`, `run_agent_node`, `loop`, `Changelog`, `test`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `CurrentAttemptMetrics`, `ref_node_assert`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.05046948356807512 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05585106382978723 - nodes in this community are weakly interconnected._