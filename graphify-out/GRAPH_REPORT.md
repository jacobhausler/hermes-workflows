# Graph Report - tree  (2026-09-30)

## Corpus Check
- 171 files · ~221,236 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1863 nodes · 3755 edges · 129 communities (97 shown, 32 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 245 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- lane_recover.py
- EngineNextCut
- pathlib
- sys
- Disclosure verification — clause-by-clause evidence
- os
- log
- test_fanout_expand.mjs
- subprocess
- _Exporter
- plugin_api.py
- shutil
- wf_dialect.py
- test_11_ui_imports.mjs
- jload
- test_fanout_item_goal.py
- run_state
- test_sprint101w2_C3-fanout-gates.py
- _Importer
- re
- wf.py
- _adopt_child
- run_child
- run_agent_node
- json
- ref_node_assert
- wfcommon.py
- __init__.py
- test_prompt_workdir.py
- test_live_truth_ui.mjs
- Changelog
- test_pill_rail_expand.mjs
- act_run
- CurrentAttemptMetrics
- _ping_route_once
- test_require_route_25.py
- test_register_surface.mjs
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- .statement
- CardBackend
- test_edge_routing.mjs
- test
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- owner_setting
- LiveTruth
- test_node_panel.mjs
- test_tiers.py
- hermes_home
- _resolve_models
- validate_graph_errors
- test_lane_hygiene_preamble_8edcc9bf.py
- test_orphan_adopt_790c6ad.py
- act_amend
- SKILL.md
- efp
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- node_facts
- Portable workflow files (publish = put the file on git)
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- when_true
- _create_run
- test_amend_rebake_034849a2.py
- _stamp_served
- _bind_run_context
- Contributing to hermes-workflows
- test_validate_0923.py
- ref_node_fs
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- ProvenanceCounters
- _transient_retry
- DialectRefusal
- test_sprint101w2_B2-retry.py
- _expand_config_value
- _SV
- Run operations and read model
- test_engine.py
- test_routing_routes.py
- model_preflight
- amend
- suite.py
- CoreFaithfulCtx
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- DoorLane
- test_lane_gate_64c6772b.py
- test_run_context_seed_guard.py
- test_suite_admission_17.py
- test_v3_fixes.py
- _expand_config_values
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- _defaults_errors
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- .render_item_template
- Run
- _verify_spawn_rec
- node_child_home
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
4. `_Importer` - 27 edges
5. `_Exporter` - 26 edges
6. `loop()` - 23 edges
7. `run_state()` - 23 edges
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
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (129 total, 32 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (93): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest() (+85 more)

### Community 1 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 2 - "EngineNextCut"
Cohesion: 0.08
Nodes (24): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+16 more)

### Community 3 - "pathlib"
Cohesion: 0.06
Nodes (15): importlib_util, pathlib, Identical solo child wrapper for both tag and candidate; records env key sets.…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, 4052d57719653b1a: atomic library replay binding, no real runner. (+7 more)

### Community 4 - "sys"
Cohesion: 0.06
Nodes (13): sys, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, End-to-end test of the `workflow` tool door against fake hermes., #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, Library verbs + /wf command: save (from run_id / inline), library list, run… (+5 more)

### Community 5 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.06
Nodes (31): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+23 more)

### Community 6 - "os"
Cohesion: 0.07
Nodes (17): os, tempfile, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session; the payload carries a parser-…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, Integrated read-model and parser-valid card dedup checks., The child launcher is operator-controlled, never a tool argument. (+9 more)

### Community 7 - "log"
Cohesion: 0.09
Nodes (32): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+24 more)

### Community 8 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 9 - "subprocess"
Cohesion: 0.09
Nodes (19): contextlib, copy, signal, subprocess, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), F3 boundary/claim integration: real door processes + kernel flock; no hook in… (+11 more)

### Community 10 - "_Exporter"
Cohesion: 0.15
Nodes (12): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+4 more)

### Community 11 - "plugin_api.py"
Cohesion: 0.10
Nodes (24): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+16 more)

### Community 12 - "shutil"
Cohesion: 0.07
Nodes (11): fcntl, io, shutil, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).… (+3 more)

### Community 13 - "wf_dialect.py"
Cohesion: 0.08
Nodes (25): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _mask(), _match_close() (+17 more)

### Community 14 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 15 - "jload"
Cohesion: 0.14
Nodes (25): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), drain_inbox(), emit(), finalize(), main(), consume_markers() (+17 more)

### Community 16 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 17 - "run_state"
Cohesion: 0.12
Nodes (24): act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state() (+16 more)

### Community 18 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 19 - "_Importer"
Cohesion: 0.17
Nodes (12): _Importer, _line(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., _match_close or a named refusal (F2 #36): an unterminated construct is reported…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to… (+4 more)

### Community 20 - "re"
Cohesion: 0.10
Nodes (13): hashlib, re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., check() (+5 more)

### Community 21 - "wf.py"
Cohesion: 0.12
Nodes (23): concurrent_futures, build_inputs(), extract_json(), _inputs_block(), last_balanced_object(), _match_object(), _quota_cache_path(), _quota_note() (+15 more)

### Community 22 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 23 - "run_child"
Cohesion: 0.10
Nodes (24): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+16 more)

### Community 24 - "run_agent_node"
Cohesion: 0.12
Nodes (20): 1.0.17 — 2026-09-28, _bounded_retry(), _dangling_placeholders(), fmt_goal(), _lane_gate(), #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave… (+12 more)

### Community 25 - "json"
Cohesion: 0.10
Nodes (6): json, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 26 - "ref_node_assert"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 27 - "wfcommon.py"
Cohesion: 0.10
Nodes (21): shlex, _active_spawn(), amend_preview(), current_attempt(), _downstream(), launch_runs_root(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE… (+13 more)

### Community 28 - "__init__.py"
Cohesion: 0.13
Nodes (20): difflib, act_inbox(), act_library(), handle(), library_root(), _library_roots(), model_tiers(), _owner_setting_read() (+12 more)

### Community 29 - "test_prompt_workdir.py"
Cohesion: 0.15
Nodes (18): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+10 more)

### Community 30 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 31 - "Changelog"
Cohesion: 0.10
Nodes (19): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named (+11 more)

### Community 32 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 33 - "act_run"
Cohesion: 0.13
Nodes (19): act_run(), act_save(), _coerce_graph(), _input_graph(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+11 more)

### Community 35 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+9 more)

### Community 36 - "test_require_route_25.py"
Cohesion: 0.12
Nodes (10): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned…, set_ping() (+2 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 38 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 39 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 40 - ".statement"
Cohesion: 0.15
Nodes (8): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, _statements()

### Community 41 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 42 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 43 - "test"
Cohesion: 0.20
Nodes (14): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run(), test() (+6 more)

### Community 44 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 45 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).…, Fresh interpreter; cfg_text is the RAW config.yaml (settings + legacy config). (+4 more)

### Community 46 - "owner_setting"
Cohesion: 0.14
Nodes (14): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting(), profile_errors(), A surviving `${...}` after expansion means the referenced var is unset (or a… (+6 more)

### Community 48 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 49 - "test_tiers.py"
Cohesion: 0.16
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 50 - "hermes_home"
Cohesion: 0.18
Nodes (13): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, find_run(), hermes_home(), hermes_root(), profile_home(), profiles_root(), `settings.runs_root` as a validated absolute Path, or None when unset/empty.…, Locate a run dir by id: resolved runs_root() first; legacy launch root only for… (+5 more)

### Community 51 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 52 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): rerr(), _v(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors() (+4 more)

### Community 53 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.22
Nodes (12): check(), home_and_fake(), leaks(), main(), mk_run(), #37 lane hygiene — the RED-by-checkout ban rides the machine build-lane…, Every (file, token) pair where a preamble token appears in a record file., step() (+4 more)

### Community 54 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 55 - "act_amend"
Cohesion: 0.15
Nodes (13): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+5 more)

### Community 56 - "SKILL.md"
Cohesion: 0.17
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 57 - "efp"
Cohesion: 0.19
Nodes (13): Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally…, run_graph(), Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer() (+5 more)

### Community 58 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 59 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 60 - "node_facts"
Cohesion: 0.17
Nodes (12): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS, node_facts(), precondition_facts() (+4 more)

### Community 61 - "Portable workflow files (publish = put the file on git)"
Cohesion: 0.24
Nodes (12): File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example (+4 more)

### Community 63 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 64 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 65 - "when_true"
Cohesion: 0.21
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr() (+4 more)

### Community 66 - "_create_run"
Cohesion: 0.22
Nodes (11): _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn., Operator-controlled launcher; tool arguments never choose a child executable.… (+3 more)

### Community 67 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 68 - "_stamp_served"
Cohesion: 0.22
Nodes (11): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Commit actual child seat truth, never the requested alias. No row means unknown., _route_hold(), _route_home(), _seat_alias_map() (+3 more)

### Community 69 - "_bind_run_context"
Cohesion: 0.20
Nodes (8): Unreleased, act_list(), _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…, Machine-generated resume preamble prepended to the goal for the ONE #5 re-…, _resume_preamble()

### Community 70 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 71 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 72 - "ref_node_fs"
Cohesion: 0.20
Nodes (5): ref_node_fs, code, { fanItems, fanCounts }, here, src

### Community 73 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 75 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 76 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 77 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 78 - "_transient_retry"
Cohesion: 0.20
Nodes (10): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, Backoff schedule / per-run budget come ONLY from run.json meta (the door's…, _retry_conf_params(), _tool_progress(), _transient_retry() (+2 more)

### Community 79 - "DialectRefusal"
Cohesion: 0.24
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 80 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 81 - "_expand_config_value"
Cohesion: 0.22
Nodes (9): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain… (+1 more)

### Community 83 - "Run operations and read model"
Cohesion: 0.25
Nodes (7): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 84 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 85 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 86 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 87 - "amend"
Cohesion: 0.38
Nodes (7): What you get, 2. The mapping table, Run and handoff, Smallest working graph, Workflow authoring (1.1.1), amend(), gate()

### Community 88 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 89 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 92 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 93 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (5): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, Meta

### Community 94 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 96 - "test_lane_gate_64c6772b.py"
Cohesion: 0.33
Nodes (3): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>.

### Community 98 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 100 - "_expand_config_values"
Cohesion: 0.33
Nodes (6): _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings(), _yaml_load()

### Community 101 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 104 - "_defaults_errors"
Cohesion: 0.40
Nodes (4): _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 105 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 106 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 111 - "_verify_spawn_rec"
Cohesion: 0.50
Nodes (4): _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, All verified uncommitted child identities, never historical DB liveness., _verify_spawn_rec()

### Community 112 - "node_child_home"
Cohesion: 0.50
Nodes (4): node_child_home(), node_child_metrics(), The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's…, Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as…

## Knowledge Gaps
- **269 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 937 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `_verify_spawn_rec`, `jload`, `run_state`, `_resolve_models`, `wf.py`, `Changelog`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `ref_node_assert`, `amend`, `log`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05948295584534431 - nodes in this community are weakly interconnected._
- **Should `lane_recover.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07682926829268293 - nodes in this community are weakly interconnected._
- **Should `EngineNextCut` be split into smaller, more focused modules?**
  _Cohesion score 0.07557354925775979 - nodes in this community are weakly interconnected._