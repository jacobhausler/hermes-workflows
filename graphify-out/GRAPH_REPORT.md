# Graph Report - tree  (2026-10-01)

## Corpus Check
- 195 files · ~236,788 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: .jsonl 9, .cursor 5, (none) 4)

## Summary
- 1983 nodes · 4012 edges · 129 communities (93 shown, 36 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 252 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- run_child
- pathlib
- jload
- Changelog
- _final_quiesce
- os
- wf.py
- lane_recover.py
- test_preflight_liveness_152be7f7.py
- plugin_api.py
- shutil
- test_fanout_expand.mjs
- log
- test_lane_hygiene_preamble_8edcc9bf.py
- _Exporter
- test_require_route_25.py
- importlib_util
- subprocess
- wf_dialect.py
- sys
- test_11_ui_imports.mjs
- __init__.py
- efp
- CurrentAttemptMetrics
- test_fanout_item_goal.py
- _Importer
- json
- hermes_home
- ref_node_assert
- test_live_truth_ui.mjs
- act_run
- settings_runs_root
- wfcommon.py
- test_pill_rail_expand.mjs
- re
- runner_alive
- test_register_surface.mjs
- _ping_route_once
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- .statement
- act_amend
- _resolve_models
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- SKILL.md
- test_proctree_61b.py
- test_cross_container_liveness_91b9a3de.py
- validate_graph_errors
- test_sprint101w2_D2-steer-liveness.py
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- amend
- node_facts
- test_deleted_cwd_resume_5c37b19.py
- when_true
- test_orphan_adopt_790c6ad.py
- test_card_frontend_contract.mjs
- AGENTS.md
- Contributing to hermes-workflows
- ref_node_fs
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- ProvenanceCounters
- DialectRefusal
- plugin-catalog: add `hermes-workflows` (community, automation)
- Disclosure verification — clause-by-clause evidence
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- test_run_dry_run.py
- _expand_config_values
- model_preflight
- Run operations and read model
- CoreFaithfulCtx
- test_review_fixes.py
- test_status_next.py
- test_steer_live_40.py
- _env_ref_var_name
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- Hermes Workflows
- DoorLane
- test_run_context_seed_guard.py
- test_suite_admission_17.py
- 1.0.1 — 2026-09-25
- 11-claim-wrapper.py
- Claim
- test_sprint101_D-surface.py
- test_validator_caps.py
- _defaults_errors
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- .render_item_template
- Run
- Workflow 'p80-b2' — done
- Workflow 'p80-ok' — done
- date-now.js
- meta-nonliteral.js
- Ctx
- p80-b2/logs/s.a0.prompt.md
- p80-b3/logs/s.a0.prompt.md
- s.a1.prompt.md
- s.a2.prompt.md
- h.a0.prompt.md
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
1. `run_child()` - 45 edges
2. `efp()` - 37 edges
3. `jload()` - 36 edges
4. `log()` - 27 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
7. `_adopt_child()` - 25 edges
8. `main()` - 24 edges
9. `loop()` - 23 edges
10. `run_state()` - 23 edges

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

## Communities (129 total, 36 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (94): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+86 more)

### Community 1 - "run_child"
Cohesion: 0.05
Nodes (54): _adopt_child(), _AdoptedHandle, _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), _first_message_s() (+46 more)

### Community 2 - "pathlib"
Cohesion: 0.07
Nodes (28): contextlib, copy, pathlib, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+20 more)

### Community 3 - "jload"
Cohesion: 0.08
Nodes (47): ONE gate-answer path for tool and UI. Stale answers never block: the answer…, _release_core(), _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test() (+39 more)

### Community 4 - "Changelog"
Cohesion: 0.05
Nodes (43): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+35 more)

### Community 5 - "_final_quiesce"
Cohesion: 0.06
Nodes (47): _account_tree(), _complete(), _boot_sweep(), _final_quiesce(), _kill_pool(), _left_live_record(), _proc_alive(), _proc_pids_by_pgid() (+39 more)

### Community 6 - "os"
Cohesion: 0.06
Nodes (16): os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires… (+8 more)

### Community 7 - "wf.py"
Cohesion: 0.06
Nodes (42): concurrent_futures, build_inputs(), drain_inbox(), extract_json(), _fail_precondition(), hermes_home(), _inputs_block(), _is_build_lane() (+34 more)

### Community 8 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 9 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.07
Nodes (29): dict, author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat(), check() (+21 more)

### Community 10 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 11 - "shutil"
Cohesion: 0.06
Nodes (7): shutil, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, #61 — the runner is process-tree aware before it judges an attempt. Evidence…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 12 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 13 - "log"
Cohesion: 0.10
Nodes (30): 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, The js dialect seam (#33): `wf_dialect.py`, _bounded_retry(), _dangling_placeholders(), _isolate_prior() (+22 more)

### Community 14 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (27): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+19 more)

### Community 15 - "_Exporter"
Cohesion: 0.15
Nodes (12): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+4 more)

### Community 16 - "test_require_route_25.py"
Cohesion: 0.07
Nodes (14): atexit, importlib, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, HTTP429 (+6 more)

### Community 17 - "importlib_util"
Cohesion: 0.06
Nodes (9): importlib_util, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, 4052d57719653b1a: atomic library replay binding, no real runner., Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph() (+1 more)

### Community 18 - "subprocess"
Cohesion: 0.06
Nodes (11): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…, subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker… (+3 more)

### Community 19 - "wf_dialect.py"
Cohesion: 0.08
Nodes (25): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _mask(), _match_close() (+17 more)

### Community 20 - "sys"
Cohesion: 0.08
Nodes (9): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 21 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 22 - "__init__.py"
Cohesion: 0.11
Nodes (26): difflib, act_list(), act_status(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), _lane_key_error() (+18 more)

### Community 23 - "efp"
Cohesion: 0.11
Nodes (27): 2. The mapping table, File-authored graphs, Portable workflow files (publish = put the file on git), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test(), Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally… (+19 more)

### Community 24 - "CurrentAttemptMetrics"
Cohesion: 0.17
Nodes (10): Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Top-level provenance, Walk-in example, nodes(), CurrentAttemptMetrics (+2 more)

### Community 25 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 26 - "_Importer"
Cohesion: 0.17
Nodes (12): _Importer, _line(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to… (+4 more)

### Community 27 - "json"
Cohesion: 0.11
Nodes (13): hashlib, json, Identical solo child wrapper for both tag and candidate; records env key sets.…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., check(), #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, refuses(), check() (+5 more)

### Community 28 - "hermes_home"
Cohesion: 0.09
Nodes (23): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), find_run(), hermes_home() (+15 more)

### Community 29 - "ref_node_assert"
Cohesion: 0.11
Nodes (15): ref_node_assert, ref_node_path, ref_node_url, tmp, [first, second], header, match, root (+7 more)

### Community 30 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 31 - "act_run"
Cohesion: 0.12
Nodes (20): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), library_root(), _library_roots() (+12 more)

### Community 32 - "settings_runs_root"
Cohesion: 0.12
Nodes (18): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting(), profile_errors(), A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives… (+10 more)

### Community 33 - "wfcommon.py"
Cohesion: 0.11
Nodes (19): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), launch_runs_root(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE… (+11 more)

### Community 34 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 35 - "re"
Cohesion: 0.12
Nodes (11): glob, hermes_constants, re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-… (+3 more)

### Community 36 - "runner_alive"
Cohesion: 0.13
Nodes (18): act_inbox(), act_release(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Explicit resume/watch verb. Read-only status/list never spawn; wait may resume… (+10 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 38 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+8 more)

### Community 39 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 40 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 41 - ".statement"
Cohesion: 0.15
Nodes (8): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, _statements()

### Community 42 - "act_amend"
Cohesion: 0.13
Nodes (16): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY… (+8 more)

### Community 43 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+8 more)

### Community 44 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 45 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 46 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 47 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).…, Fresh interpreter; cfg_text is the RAW config.yaml (settings + legacy config). (+4 more)

### Community 50 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 51 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 52 - "SKILL.md"
Cohesion: 0.15
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 53 - "test_proctree_61b.py"
Cohesion: 0.22
Nodes (10): alive(), check(), cleanup(), escape_case(), mk(), #61b — the four adversarial blockers, RED first, standalone (not pytest).…, read_rows(), rec_of() (+2 more)

### Community 54 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 55 - "validate_graph_errors"
Cohesion: 0.17
Nodes (11): _v(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), validate_graph_errors() (+3 more)

### Community 56 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.15
Nodes (4): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission., Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…

### Community 57 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 58 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 59 - "amend"
Cohesion: 0.20
Nodes (11): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3d. Failures, resume, amend, 3e. Reporting a finished run, What you get, Run and handoff (+3 more)

### Community 60 - "node_facts"
Cohesion: 0.17
Nodes (12): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS, node_facts(), precondition_facts() (+4 more)

### Community 62 - "when_true"
Cohesion: 0.21
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr() (+4 more)

### Community 63 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (5): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 64 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 65 - "AGENTS.md"
Cohesion: 0.24
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 66 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 67 - "ref_node_fs"
Cohesion: 0.20
Nodes (5): ref_node_fs, code, { fanItems, fanCounts }, here, src

### Community 68 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 70 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 71 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 72 - "DialectRefusal"
Cohesion: 0.24
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 73 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 74 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.22
Nodes (9): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+1 more)

### Community 75 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 77 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 78 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 80 - "_expand_config_values"
Cohesion: 0.25
Nodes (8): _expand_config_value(), _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Expand one `${VAR}` (legacy bare name) or `${env:VAR}` (Cursor-style SecretRef)…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings(), _yaml_load()

### Community 81 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 82 - "Run operations and read model"
Cohesion: 0.29
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 83 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 85 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 86 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 87 - "_env_ref_var_name"
Cohesion: 0.29
Nodes (7): _env_ref_lookup(), _env_ref_var_name(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain…

### Community 88 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 89 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 90 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 91 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 94 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 95 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 96 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 98 - "test_sprint101_D-surface.py"
Cohesion: 0.40
Nodes (3): mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 99 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 100 - "_defaults_errors"
Cohesion: 0.40
Nodes (4): _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 101 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 102 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **277 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+272 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1002 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `jload`, `runner_alive`, `Changelog`, `wf.py`, `_resolve_models`?**
  _High betweenness centrality (0.215) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `test_card_frontend_contract.mjs`, `efp`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _277 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05845464725643897 - nodes in this community are weakly interconnected._
- **Should `run_child` be split into smaller, more focused modules?**
  _Cohesion score 0.048051948051948054 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.06802721088435375 - nodes in this community are weakly interconnected._