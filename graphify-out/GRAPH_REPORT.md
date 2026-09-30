# Graph Report - tree  (2026-09-30)

## Corpus Check
- 170 files · ~222,859 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1848 nodes · 3743 edges · 120 communities (92 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 258 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- __init__.py
- wf.py
- wfcommon.py
- os
- efp
- lane_recover.py
- run_state
- plugin_api.py
- test_fanout_expand.mjs
- .meta
- _Exporter
- shutil
- time
- wf_dialect.py
- test_11_ui_imports.mjs
- test_lock_heal_44.py
- test_lane_hygiene_preamble_8edcc9bf.py
- Changelog
- subprocess
- test_fanout_item_goal.py
- test_sprint101w2_C3-fanout-gates.py
- jload
- _Importer
- log
- sys
- ref_node_fs
- test_failures_0923.py
- test_live_truth_ui.mjs
- _stamp_served
- test_pill_rail_expand.mjs
- CurrentAttemptMetrics
- EngineNextCut
- test_register_surface.mjs
- json
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- .statement
- _ping_route_once
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- 3. Operate
- amend
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- test_require_route_25.py
- pathlib
- SKILL.md
- test_orphan_adopt_790c6ad.py
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- test_validate_0923.py
- ref_node_url
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- ProvenanceCounters
- DialectRefusal
- Portable workflow files (publish = put the file on git)
- test_packaging.py
- test_sprint101w2_B2-retry.py
- _SV
- graph_fingerprint
- test_engine.py
- test_routing_routes.py
- find_run
- model_preflight
- act_status
- Hermes Workflows
- suite.py
- CoreFaithfulCtx
- test_lane_gate_64c6772b.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- build_inputs
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Manual installation — Hermes Workflows 1.1.1
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- test_model_law_dad50be0.py
- test_tiers.py
- test_v3_fixes.py
- 2. Install
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_safe_root_workdir.py
- test_validator_caps.py
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- _AdoptedHandle
- .render_item_template
- _lane_hygiene_preamble
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
4. `run_state()` - 29 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
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
- `1.0.17 — 2026-09-28` --references--> `fmt_goal()`  [INFERRED]
  CHANGELOG.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (120 total, 28 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "__init__.py"
Cohesion: 0.05
Nodes (72): difflib, act_amend(), act_library(), act_list(), act_run(), act_save(), _alias_provider_pair(), _card() (+64 more)

### Community 2 - "wf.py"
Cohesion: 0.06
Nodes (60): concurrent_futures, _adopt_child(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), extract_json() (+52 more)

### Community 3 - "wfcommon.py"
Cohesion: 0.05
Nodes (56): shlex, apply_graph_defaults(), current_attempt(), _defaults_errors(), effective_runs_root(), grammar_errors(), launcher_profile(), lock_forensics() (+48 more)

### Community 4 - "os"
Cohesion: 0.08
Nodes (26): contextlib, hashlib, importlib_util, os, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.… (+18 more)

### Community 5 - "efp"
Cohesion: 0.07
Nodes (39): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), gate(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run() (+31 more)

### Community 6 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 7 - "run_state"
Cohesion: 0.09
Nodes (36): Unreleased, act_release(), act_release_lock(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_state() (+28 more)

### Community 8 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 9 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 10 - ".meta"
Cohesion: 0.09
Nodes (28): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+20 more)

### Community 11 - "_Exporter"
Cohesion: 0.15
Nodes (12): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+4 more)

### Community 12 - "shutil"
Cohesion: 0.06
Nodes (12): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when… (+4 more)

### Community 13 - "time"
Cohesion: 0.07
Nodes (8): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…, time

### Community 14 - "wf_dialect.py"
Cohesion: 0.08
Nodes (25): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _mask(), _match_close() (+17 more)

### Community 15 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 16 - "test_lock_heal_44.py"
Cohesion: 0.07
Nodes (12): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, check(), mkrun(), Exception (+4 more)

### Community 17 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.11
Nodes (24): Nodes and data, build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat (+16 more)

### Community 18 - "Changelog"
Cohesion: 0.07
Nodes (26): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes (+18 more)

### Community 19 - "subprocess"
Cohesion: 0.07
Nodes (10): subprocess, Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must… (+2 more)

### Community 20 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 21 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 22 - "jload"
Cohesion: 0.12
Nodes (25): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), active_child(), _active_spawn(), _active_spawns(), amend_preview() (+17 more)

### Community 23 - "_Importer"
Cohesion: 0.17
Nodes (12): _Importer, _line(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to… (+4 more)

### Community 24 - "log"
Cohesion: 0.12
Nodes (23): 3.5 `log(message)`, The js dialect seam (#33): `wf_dialect.py`, _bounded_retry(), _dangling_placeholders(), _lane_gate(), log(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+15 more)

### Community 25 - "sys"
Cohesion: 0.12
Nodes (12): re, sys, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-… (+4 more)

### Community 26 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 27 - "test_failures_0923.py"
Cohesion: 0.09
Nodes (6): sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 28 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 29 - "_stamp_served"
Cohesion: 0.11
Nodes (21): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+13 more)

### Community 30 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 32 - "EngineNextCut"
Cohesion: 0.21
Nodes (4): EngineNextCut, deps_ok(), dep_satisfied(), deps_ok()

### Community 33 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (15): areas, { Edges, depthMap }, g, g2, grab(), here, jsxPath, loadPlugin() (+7 more)

### Community 34 - "json"
Cohesion: 0.13
Nodes (8): copy, json, check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses(), Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Engine branch contracts, exercised by the actual runner and fake CLI (no…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 35 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 36 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 37 - ".statement"
Cohesion: 0.15
Nodes (8): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, _statements()

### Community 38 - "_ping_route_once"
Cohesion: 0.12
Nodes (15): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+7 more)

### Community 39 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 40 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 41 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 42 - "3. Operate"
Cohesion: 0.13
Nodes (15): 1. What this is (30 seconds), 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, 4. Contribute (+7 more)

### Community 43 - "amend"
Cohesion: 0.15
Nodes (14): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), Run and handoff, amend() (+6 more)

### Community 44 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 46 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 47 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 48 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 49 - "pathlib"
Cohesion: 0.14
Nodes (5): pathlib, Identical solo child wrapper for both tag and candidate; records env key sets.…, End-to-end test of the `workflow` tool door against fake hermes., v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run…

### Community 50 - "SKILL.md"
Cohesion: 0.21
Nodes (4): Node budgets, Contributor checks (not ordinary user setup), Smallest working graph, Workflow authoring (1.1.1)

### Community 51 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 52 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 53 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 55 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 56 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 57 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 58 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 59 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 60 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 61 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 63 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 64 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 65 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 66 - "DialectRefusal"
Cohesion: 0.24
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 67 - "Portable workflow files (publish = put the file on git)"
Cohesion: 0.31
Nodes (9): Gates and branches, Graph grammar and authoring boundaries, Staleness and replay, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), 1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the… (+1 more)

### Community 68 - "test_packaging.py"
Cohesion: 0.25
Nodes (5): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types

### Community 69 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 71 - "graph_fingerprint"
Cohesion: 0.39
Nodes (7): File-authored graphs, put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

### Community 72 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 73 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 74 - "find_run"
Cohesion: 0.25
Nodes (8): #44 escape hatch: `wf.py release-lock <run_id>`. Prints the verdict JSON…, release_lock_cli(), find_run(), launch_runs_root(), Runs root of the RAW process environment (never the context-resolved home).…, Locate a run dir by id: resolved runs_root() first; legacy launch root only for…, `WF_RUNS_ROOT` if set (non-empty), else `$HERMES_HOME/workflows`., runs_root()

### Community 75 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 76 - "act_status"
Cohesion: 0.29
Nodes (6): act_status(), _lane_key_error(), _output_pointer(), Compact stand-in for a committed node output: enough to DECIDE to pay for…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 77 - "Hermes Workflows"
Cohesion: 0.29
Nodes (7): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get

### Community 78 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 79 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 80 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 82 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 83 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 84 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 85 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 86 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 87 - "Manual installation — Hermes Workflows 1.1.1"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 88 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 90 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 93 - "2. Install"
Cohesion: 0.40
Nodes (5): 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths

### Community 94 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 95 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 97 - "test_safe_root_workdir.py"
Cohesion: 0.70
Nodes (4): check(), main(), fb 625a3241cfcc9dee — the child's advertised durable work dir is writable under…, run_graph()

### Community 98 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 99 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 100 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 105 - "_lane_hygiene_preamble"
Cohesion: 0.50
Nodes (4): _is_build_lane(), _lane_hygiene_preamble(), The build shape: `shape: "build"` declared, or a `repo:` lane declared (the…, Machine-generated lane-hygiene preamble for build-shape nodes ("" otherwise).…

## Knowledge Gaps
- **270 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+265 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 932 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `__init__.py`, `run_state`, `Changelog`, `build_inputs`, `jload`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_fs`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _270 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05109218807848945 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06174863387978142 - nodes in this community are weakly interconnected._