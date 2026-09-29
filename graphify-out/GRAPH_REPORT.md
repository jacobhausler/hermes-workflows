# Graph Report - tree  (2026-09-29)

## Corpus Check
- 126 files · ~171,315 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1478 nodes · 2981 edges · 95 communities (78 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- pathlib
- wfcommon.py
- efp
- test_fanout_expand.mjs
- time
- test_prompt_workdir.py
- plugin_api.py
- run_agent_node
- sys
- test_11_ui_imports.mjs
- CurrentAttemptMetrics
- shutil
- test_fanout_item_goal.py
- runner_alive
- subprocess
- __init__.py
- test_card_frontend_contract.mjs
- test_preflight_liveness_152be7f7.py
- test_orphan_adopt_790c6ad.py
- test_live_truth_ui.mjs
- json
- os
- test_register_surface.mjs
- validate_graph_errors
- _SV
- _ping_route_once
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- act_amend
- act_run
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- Changelog
- test_require_route_25.py
- _resolve_models
- graph_check.py
- amend
- _create_run
- test_route_efforts_b3c98b2a.py
- Run operations and read model
- test_11_integration_team.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_cross_container_liveness_91b9a3de.py
- SKILL.md
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- ref_node_url
- test_hermes_bin_reserved_0928.py
- test_fp_rule_f0f154d5.py
- test_sprint101w2_B2-retry.py
- _stamp_served
- AGENTS.md — front door for agents
- Disclosure verification — clause-by-clause evidence
- test_engine.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- act_steer
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- build_inputs
- AGENTS.md
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Manual installation — Hermes Workflows 1.1.0
- Hermes Workflows
- DoorLane
- test_model_law_dad50be0.py
- test_prune_0923.py
- test_suite_admission_17.py
- test_tier_report_0924.py
- test_tiers.py
- 1.0.2 — 2026-09-26 — the run watches itself
- 11-golden-solo.py
- Claim
- test_papercuts_0922.py
- test_run_binding.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- 1.0.1 — 2026-09-25
- manifest.json
- _LADDER
- Integrated
- Run
- fake

## God Nodes (most connected - your core abstractions)
1. `jload()` - 36 edges
2. `efp()` - 34 edges
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
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py
- `1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)` --references--> `model_preflight()`  [INFERRED]
  CHANGELOG.md → __init__.py

## Import Cycles
- None detected.

## Communities (95 total, 17 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "wf.py"
Cohesion: 0.06
Nodes (62): concurrent_futures, _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+54 more)

### Community 2 - "pathlib"
Cohesion: 0.06
Nodes (29): contextlib, copy, hashlib, importlib_util, pathlib, signal, tempfile, main() (+21 more)

### Community 3 - "wfcommon.py"
Cohesion: 0.09
Nodes (42): Unreleased, shlex, fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), _active_spawn(), _active_spawns() (+34 more)

### Community 4 - "efp"
Cohesion: 0.09
Nodes (34): Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), drain_inbox() (+26 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "time"
Cohesion: 0.07
Nodes (14): glob, hermes_constants, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.… (+6 more)

### Community 7 - "test_prompt_workdir.py"
Cohesion: 0.09
Nodes (27): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+19 more)

### Community 8 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 9 - "run_agent_node"
Cohesion: 0.08
Nodes (30): _attempt_api_calls(), _bounded_retry(), _dangling_placeholders(), _lane_gate(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+22 more)

### Community 10 - "sys"
Cohesion: 0.08
Nodes (9): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 11 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 12 - "CurrentAttemptMetrics"
Cohesion: 0.17
Nodes (10): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Top-level provenance, nodes(), CurrentAttemptMetrics (+2 more)

### Community 13 - "shutil"
Cohesion: 0.07
Nodes (9): shutil, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the… (+1 more)

### Community 14 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 15 - "runner_alive"
Cohesion: 0.11
Nodes (23): act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts() (+15 more)

### Community 16 - "subprocess"
Cohesion: 0.08
Nodes (9): subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph() (+1 more)

### Community 17 - "__init__.py"
Cohesion: 0.13
Nodes (21): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), difflib, act_library(), handle(), _lib_path(), library_root(), model_preflight(), model_tiers() (+13 more)

### Community 18 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 19 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.13
Nodes (18): check(), contract(), EscapeLineOnly, fake_call_llm(), FakeHTTPError, graph_two_routes(), HostileStr, KeyLeak (+10 more)

### Community 20 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.10
Nodes (11): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner(), Ctx (+3 more)

### Community 21 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 22 - "json"
Cohesion: 0.11
Nodes (9): json, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Identical solo child wrapper for both tag and candidate; records env key sets.…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Library verbs + /wf command: save (from run_id / inline), library list, run… (+1 more)

### Community 23 - "os"
Cohesion: 0.10
Nodes (9): os, admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, End-to-end test of the `workflow` tool door against fake hermes., graph_check.py contract: committed graph ⇔ tree, both directions, plus the… (+1 more)

### Community 24 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 25 - "validate_graph_errors"
Cohesion: 0.11
Nodes (16): rerr(), _v(), apply_graph_defaults(), _defaults_errors(), 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+8 more)

### Community 26 - "_SV"
Cohesion: 0.12
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, _SV, _tok_when(), _when_and(), _when_atom(), _when_cmp() (+4 more)

### Community 27 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 28 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 29 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 30 - "act_amend"
Cohesion: 0.13
Nodes (16): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _liveness_hint_suffix(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 31 - "act_run"
Cohesion: 0.13
Nodes (15): act_run(), _bind_run_context(), agent_ancestor(), render(), _lane_entry(), _lane_paths(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,… (+7 more)

### Community 32 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 33 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 34 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 35 - "1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance"
Cohesion: 0.15
Nodes (14): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, hermes_home(), hermes_root(), launcher_profile(), profile_errors(), profile_home(), profiles_root(), The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a… (+6 more)

### Community 38 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 39 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 40 - "Changelog"
Cohesion: 0.14
Nodes (12): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+4 more)

### Community 41 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 42 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 43 - "graph_check.py"
Cohesion: 0.21
Nodes (11): re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), check(), main() (+3 more)

### Community 44 - "amend"
Cohesion: 0.18
Nodes (12): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, The door validates from lists, What you get (+4 more)

### Community 45 - "_create_run"
Cohesion: 0.18
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.… (+4 more)

### Community 46 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 47 - "Run operations and read model"
Cohesion: 0.17
Nodes (12): Explorer V2: one node truth, two readers, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), node_facts(), precondition_facts() (+4 more)

### Community 48 - "test_11_integration_team.py"
Cohesion: 0.27
Nodes (3): Lane E: cross-lane executable integration fixtures; no production…, TeamIntegration, until()

### Community 50 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 51 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.18
Nodes (5): fcntl, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 52 - "SKILL.md"
Cohesion: 0.18
Nodes (6): Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 53 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 54 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 55 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 56 - "test_hermes_bin_reserved_0928.py"
Cohesion: 0.22
Nodes (4): CoreFaithfulCtx, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 57 - "test_fp_rule_f0f154d5.py"
Cohesion: 0.33
Nodes (8): put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 58 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 59 - "_stamp_served"
Cohesion: 0.28
Nodes (9): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Commit actual child seat truth, never the requested alias. No row means unknown., _route_hold(), _route_home(), _seat_alias_map() (+1 more)

### Community 60 - "AGENTS.md — front door for agents"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 61 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.25
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 62 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 63 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 64 - "act_steer"
Cohesion: 0.29
Nodes (7): act_inbox(), act_steer(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 67 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 68 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 70 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 71 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 72 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 73 - "Manual installation — Hermes Workflows 1.1.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 74 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 76 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 78 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 81 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.40
Nodes (5): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 82 - "11-golden-solo.py"
Cohesion: 0.70
Nodes (4): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…

### Community 86 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 87 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 88 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 89 - "1.0.1 — 2026-09-25"
Cohesion: 0.50
Nodes (4): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The graph carries less

### Community 90 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

## Knowledge Gaps
- **224 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 764 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.381) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.369) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05673076923076923 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.06429070580013976 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08773784355179703 - nodes in this community are weakly interconnected._