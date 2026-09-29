# Graph Report - tree  (2026-09-29)

## Corpus Check
- 123 files · ~166,576 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1453 nodes · 2921 edges · 88 communities (72 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- pathlib
- test_prompt_workdir.py
- wfcommon.py
- plugin_api.py
- test_fanout_expand.mjs
- jload
- sys
- Changelog
- os
- shutil
- json
- test_11_ui_imports.mjs
- test_fanout_item_goal.py
- subprocess
- efp
- main
- run_agent_node
- child_metrics
- ref_node_fs
- test_live_truth_ui.mjs
- test_validate_0923.py
- test_register_surface.mjs
- __init__.py
- CurrentAttemptMetrics
- validate_graph_errors
- Run operations and read model
- _ping_route_once
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- CardBackend
- test_edge_routing.mjs
- EngineNextCut
- test_session_strip.mjs
- Disclosure verification — clause-by-clause evidence
- _resolve_models
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_sprint101_A-door.py
- test_require_route_25.py
- test_orphan_adopt_790c6ad.py
- test_route_efforts_b3c98b2a.py
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- SKILL.md
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- act_save
- act_run
- TeamIntegration
- test_hermes_bin_reserved_0928.py
- FakeHTTPError
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- model_preflight
- test_sprint101w2_C1-defaults.py
- test_status_next.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _input_graph
- Manual installation — Hermes Workflows 1.1.0
- Operator playbook (measured lessons; each one was paid for)
- graph_check.py
- DoorLane
- test_failed_events_77.py
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tiers.py
- 3. Operate
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_sprint101_D-surface.py
- test_validator_caps.py
- manifest.json
- _route_enforcement
- _LADDER
- Integrated
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
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (88 total, 16 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (84): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+76 more)

### Community 1 - "wf.py"
Cohesion: 0.04
Nodes (80): concurrent_futures, _adopt_child(), _AdoptedHandle, build_inputs(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output() (+72 more)

### Community 2 - "pathlib"
Cohesion: 0.06
Nodes (30): contextlib, copy, hashlib, importlib_util, pathlib, signal, tempfile, main() (+22 more)

### Community 3 - "test_prompt_workdir.py"
Cohesion: 0.07
Nodes (35): argparse, fnmatch, Pattern, File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay (+27 more)

### Community 4 - "wfcommon.py"
Cohesion: 0.08
Nodes (38): shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), def_hash(), _downstream(), effective_runs_root() (+30 more)

### Community 5 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - "jload"
Cohesion: 0.12
Nodes (31): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, act_amend(), act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait() (+23 more)

### Community 8 - "sys"
Cohesion: 0.07
Nodes (10): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on… (+2 more)

### Community 9 - "Changelog"
Cohesion: 0.07
Nodes (28): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes (+20 more)

### Community 10 - "os"
Cohesion: 0.08
Nodes (11): os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires… (+3 more)

### Community 11 - "shutil"
Cohesion: 0.07
Nodes (8): fcntl, shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, 4052d57719653b1a: atomic library replay binding, no real runner., SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…

### Community 12 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 13 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 14 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 15 - "subprocess"
Cohesion: 0.08
Nodes (11): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, subprocess, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, answer() (+3 more)

### Community 16 - "efp"
Cohesion: 0.13
Nodes (23): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test() (+15 more)

### Community 17 - "main"
Cohesion: 0.14
Nodes (21): acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), log(), main(), consume_markers() (+13 more)

### Community 18 - "run_agent_node"
Cohesion: 0.11
Nodes (22): _bounded_retry(), _dangling_placeholders(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported… (+14 more)

### Community 19 - "child_metrics"
Cohesion: 0.10
Nodes (21): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), hermes_home(), hermes_root(), launcher_profile() (+13 more)

### Community 20 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 21 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 22 - "test_validate_0923.py"
Cohesion: 0.12
Nodes (15): glob, hermes_constants, re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, check() (+7 more)

### Community 23 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 24 - "__init__.py"
Cohesion: 0.12
Nodes (18): difflib, act_inbox(), _frozen_committed(), _lane_key_error(), _last_event_ts(), _output_pointer(), _ping_note(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The… (+10 more)

### Community 26 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): rerr(), apply_graph_defaults(), _defaults_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:… (+7 more)

### Community 27 - "Run operations and read model"
Cohesion: 0.12
Nodes (17): 3d. Failures, resume, amend, For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get (+9 more)

### Community 28 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 29 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 30 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 31 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 32 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 34 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 35 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, 6. Desktop gate answer (maintainer ask #122099, teknium1), Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 36 - "_resolve_models"
Cohesion: 0.18
Nodes (15): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+7 more)

### Community 38 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 39 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 40 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 41 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 42 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 43 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 44 - "_create_run"
Cohesion: 0.17
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), _liveness_hint_suffix(), 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.… (+3 more)

### Community 46 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 47 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 49 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 50 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 51 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 52 - "act_save"
Cohesion: 0.22
Nodes (10): 2. Agent-child argv and environment, act_library(), act_save(), handle(), _lib_path(), library_root(), `/wf` — the library front door. `/wf <name> [note]` supplies the note…, Shelve a graph under a name: from an existing run (`run_id`) or an inline… (+2 more)

### Community 53 - "act_run"
Cohesion: 0.22
Nodes (10): act_run(), _lane_entry(), _lane_paths(), _model_names_valid(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, 1.1 (RATIFY F1/F3): `team` (<=64) and `lane_key` (<=128) are optional non-empty…, Return graph-level and node-level defects together, before any write/spawn. (+2 more)

### Community 55 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 56 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 57 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 59 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 60 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 61 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 63 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 64 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 65 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 66 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 67 - "_input_graph"
Cohesion: 0.33
Nodes (6): _coerce_graph(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 68 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 69 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 70 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 73 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 74 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 76 - "3. Operate"
Cohesion: 0.40
Nodes (5): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run

### Community 77 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 78 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 80 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 81 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 82 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 83 - "_route_enforcement"
Cohesion: 0.50
Nodes (4): #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

## Knowledge Gaps
- **224 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 750 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `act_save`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.354) - this node is a cross-community bridge._
- **Why does `nudgeOwner()` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.349) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06638655462184874 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04319717895974141 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.05683060109289618 - nodes in this community are weakly interconnected._