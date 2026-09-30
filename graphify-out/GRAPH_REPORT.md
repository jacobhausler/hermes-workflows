# Graph Report - tree  (2026-09-30)

## Corpus Check
- 170 files · ~216,974 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1814 nodes · 3675 edges · 123 communities (95 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- sys
- tempfile
- lane_recover.py
- wfcommon.py
- test_preflight_liveness_152be7f7.py
- shutil
- test_fanout_expand.mjs
- _Importer
- _Exporter
- wf_dialect.py
- .meta
- test_lane_hygiene_preamble_8edcc9bf.py
- wf.py
- pathlib
- test_11_ui_imports.mjs
- json
- efp
- test_lifecycle_next_cut_0923.py
- test_fanout_item_goal.py
- subprocess
- _adopt_child
- run_child
- loop
- os
- ref_node_fs
- test_live_truth_ui.mjs
- _stamp_served
- jload
- _ping_route_once
- log
- test_pill_rail_expand.mjs
- CurrentAttemptMetrics
- 3. Operate
- plugin_api.py
- __init__.py
- validate_graph_errors
- test_register_surface.mjs
- EngineNextCut
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- AGENTS.md
- amend
- act_amend
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- _SV
- run_dir
- _create_run
- DialectRefusal
- LiveTruth
- test_node_panel.mjs
- _resolve_models
- SKILL.md
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- act_run
- re
- test_pill_rail.mjs
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- Changelog
- test_card_frontend_contract.mjs
- test_node_facts.py
- Contributing to hermes-workflows
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- test_packaging.py
- ProvenanceCounters
- plugin-catalog: add `hermes-workflows` (community, automation)
- test
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- model_preflight
- suite.py
- js_import
- CoreFaithfulCtx
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_status_next.py
- test_steer_live_40.py
- build_inputs
- gate_answer_valid
- fmt_goal
- 1.0.2 — 2026-09-26 — the run watches itself
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Run operations and read model
- DoorLane
- test_suite_admission_17.py
- 1.0.1 — 2026-09-25
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- test_sprint101_D-surface.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- _route_enforcement
- dynamic-agent-count.js
- _LADDER
- Integrated
- Run
- release_gate
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
1. `efp()` - 37 edges
2. `jload()` - 36 edges
3. `run_child()` - 33 edges
4. `_Importer` - 27 edges
5. `_Exporter` - 26 edges
6. `loop()` - 23 edges
7. `run_state()` - 23 edges
8. `log()` - 22 edges
9. `_adopt_child()` - 22 edges
10. `main()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (123 total, 28 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "sys"
Cohesion: 0.06
Nodes (21): importlib_util, signal, sys, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-… (+13 more)

### Community 2 - "tempfile"
Cohesion: 0.05
Nodes (24): agent_reasoning_effort, atexit, contextlib, importlib, tempfile, Current-attempt heartbeat with real fake child identity; no provider access., fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit… (+16 more)

### Community 3 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 4 - "wfcommon.py"
Cohesion: 0.07
Nodes (37): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, shlex, amend_preview(), current_attempt(), _downstream(), effective_runs_root(), find_run(), launch_runs_root() (+29 more)

### Community 5 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 6 - "shutil"
Cohesion: 0.06
Nodes (8): shutil, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, 4052d57719653b1a: atomic library replay binding, no real runner., Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…

### Community 7 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 8 - "_Importer"
Cohesion: 0.14
Nodes (12): _control_kw(), _Importer, _ordered(), _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., A literal label -> str; a template label -> its literal spine (for ids). (+4 more)

### Community 9 - "_Exporter"
Cohesion: 0.13
Nodes (13): _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413. (+5 more)

### Community 10 - "wf_dialect.py"
Cohesion: 0.08
Nodes (26): _const_name(), _fmt_goal(), _forbidden_label(), _has_tpl(), _mask(), _match_close(), node_check(), _ordered_item() (+18 more)

### Community 11 - ".meta"
Cohesion: 0.10
Nodes (29): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+21 more)

### Community 12 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 13 - "wf.py"
Cohesion: 0.09
Nodes (28): concurrent_futures, _dangling_placeholders(), drain_inbox(), extract_json(), _is_build_lane(), _lane_gate(), _lane_hygiene_preamble(), last_balanced_object() (+20 more)

### Community 14 - "pathlib"
Cohesion: 0.08
Nodes (13): pathlib, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission., #57 — `list` payload gains the per-root provenance rollup (QM digest contract).…, Portable authoring skill contract; no provider or live-home dependencies., Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer… (+5 more)

### Community 15 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 16 - "json"
Cohesion: 0.08
Nodes (13): glob, hermes_constants, json, plugin_api, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires… (+5 more)

### Community 17 - "efp"
Cohesion: 0.12
Nodes (27): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+19 more)

### Community 18 - "test_lifecycle_next_cut_0923.py"
Cohesion: 0.07
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, threading

### Community 19 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 20 - "subprocess"
Cohesion: 0.09
Nodes (12): subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Integrated read-model and parser-valid card dedup checks., Runner identity and truthful public read paths; fixture home is isolated here. (+4 more)

### Community 21 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 22 - "run_child"
Cohesion: 0.10
Nodes (24): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+16 more)

### Community 23 - "loop"
Cohesion: 0.13
Nodes (21): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), finalize(), main(), consume_markers(), loop() (+13 more)

### Community 24 - "os"
Cohesion: 0.11
Nodes (9): copy, hashlib, os, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Authoring door regressions; all state stays in this worktree, no…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Engine branch contracts, exercised by the actual runner and fake CLI (no… (+1 more)

### Community 25 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 26 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 27 - "_stamp_served"
Cohesion: 0.11
Nodes (21): _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead…, Commit actual child seat truth, never the requested alias. No row means unknown. (+13 more)

### Community 28 - "jload"
Cohesion: 0.13
Nodes (20): act_steer(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), _active_spawn(), _active_spawns(), blocked_by(), jload(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with… (+12 more)

### Community 29 - "_ping_route_once"
Cohesion: 0.11
Nodes (19): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+11 more)

### Community 30 - "log"
Cohesion: 0.16
Nodes (19): 3.5 `log(message)`, _bounded_retry(), _fail_precondition(), log(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave… (+11 more)

### Community 31 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 33 - "3. Operate"
Cohesion: 0.11
Nodes (18): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+10 more)

### Community 34 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 35 - "__init__.py"
Cohesion: 0.17
Nodes (17): difflib, 2. Agent-child argv and environment, act_library(), handle(), _lib_path(), _lib_read(), library_root(), _library_roots() (+9 more)

### Community 36 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): _v(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+7 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 39 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 40 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 41 - "AGENTS.md"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+4 more)

### Community 42 - "amend"
Cohesion: 0.12
Nodes (16): 3d. Failures, resume, amend, For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get (+8 more)

### Community 43 - "act_amend"
Cohesion: 0.13
Nodes (16): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _model_names_valid(), _profile_error(), Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 44 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 45 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 46 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 47 - "_SV"
Cohesion: 0.14
Nodes (9): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr(), _when_not() (+1 more)

### Community 48 - "run_dir"
Cohesion: 0.16
Nodes (14): 1. Detached runner, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, act_release(), act_stop(), act_wait() (+6 more)

### Community 49 - "_create_run"
Cohesion: 0.15
Nodes (14): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), _liveness_hint_suffix(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-… (+6 more)

### Community 50 - "DialectRefusal"
Cohesion: 0.15
Nodes (9): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _line(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.… (+1 more)

### Community 52 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 53 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 54 - "SKILL.md"
Cohesion: 0.15
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 55 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 56 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 57 - "act_run"
Cohesion: 0.18
Nodes (12): act_run(), act_status(), _lane_entry(), _lane_key_error(), _lane_paths(), _lane_state(), _last_event_ts(), _output_pointer() (+4 more)

### Community 58 - "re"
Cohesion: 0.19
Nodes (7): re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Regression: launch a run in the tool's session; the payload carries a parser-…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-…

### Community 59 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 61 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 62 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 63 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 64 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 65 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 66 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 68 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 69 - "test_packaging.py"
Cohesion: 0.22
Nodes (6): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types, zipfile

### Community 70 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 71 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 72 - "test"
Cohesion: 0.31
Nodes (8): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, _verify_spawn_rec()

### Community 73 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 74 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 75 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 76 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 77 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 78 - "js_import"
Cohesion: 0.29
Nodes (7): check(), refuses(), export_report(), js_import(), _main(), See module docstring. `node_check=False` skips the optional subprocess gate., {"ok": True, "js": str, "lossy": [{node, key, value}], "warnings": [...]} |…

### Community 79 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 82 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 83 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 84 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 85 - "gate_answer_valid"
Cohesion: 0.43
Nodes (7): def_hash(), fingerprint_valid(), gate_answer_valid(), _legacy_chain_unchanged(), A record's own rule is authoritative; an unstamped record matches ANY rule. A…, A pre-efp record is valid ONLY if the stored def_hash matches AND every…, record_efp_valid()

### Community 86 - "fmt_goal"
Cohesion: 0.33
Nodes (5): 1.0.17 — 2026-09-28, Unreleased, fmt_goal(), Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, _resume_preamble()

### Community 87 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 88 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 89 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, _steer_event(), _steer_lines()

### Community 90 - "Run operations and read model"
Cohesion: 0.33
Nodes (5): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature)

### Community 92 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 93 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 94 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 95 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 98 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 99 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 100 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 101 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 102 - "_route_enforcement"
Cohesion: 0.50
Nodes (4): #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, _require_route_effective(), _route_enforcement()

### Community 103 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 107 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **270 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+265 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 913 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `test`, `run_dir`, `build_inputs`, `gate_answer_valid`, `_resolve_models`, `jload`, `Changelog`?**
  _High betweenness centrality (0.209) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _270 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `sys` be split into smaller, more focused modules?**
  _Cohesion score 0.05505279034690799 - nodes in this community are weakly interconnected._
- **Should `tempfile` be split into smaller, more focused modules?**
  _Cohesion score 0.04816326530612245 - nodes in this community are weakly interconnected._