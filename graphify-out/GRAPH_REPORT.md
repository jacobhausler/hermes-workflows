# Graph Report - tree  (2026-09-30)

## Corpus Check
- 174 files · ~232,145 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1904 nodes · 3827 edges · 133 communities (103 shown, 30 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 249 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- sys
- importlib_util
- lane_recover.py
- plugin_api.py
- subprocess
- test_fanout_expand.mjs
- .meta
- _Exporter
- time
- wfcommon.py
- test_lane_hygiene_preamble_8edcc9bf.py
- Changelog
- test_11_ui_imports.mjs
- hermes_home
- jload
- test_fanout_item_goal.py
- json
- act_run
- test_sprint101w2_C3-fanout-gates.py
- log
- wf_dialect.py
- ref_node_fs
- efp
- wf.py
- test_live_truth_ui.mjs
- run_child
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- _Importer
- act_status
- CurrentAttemptMetrics
- _adopt_child
- 3. Operate
- validate_graph_errors
- test_register_surface.mjs
- EngineNextCut
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- .refuse
- _resolve_models
- pathlib
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- __init__.py
- _ping_route_once
- LiveTruth
- test_node_panel.mjs
- _expand_config_values
- test_sprint101_A-door.py
- test_require_route_25.py
- run_state
- amend
- test_orphan_adopt_790c6ad.py
- test_cross_container_liveness_91b9a3de.py
- DialectRefusal
- test_pill_rail.mjs
- test_route_efforts_b3c98b2a.py
- AGENTS.md
- _create_run
- SKILL.md
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- test_amend_rebake_034849a2.py
- test
- _stamp_served
- Contributing to hermes-workflows
- _lib_path
- ref_node_url
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- test_packaging.py
- FakeHTTPError
- ProvenanceCounters
- plugin-catalog: add `hermes-workflows` (community, automation)
- Disclosure verification — clause-by-clause evidence
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- test_run_dry_run.py
- model_preflight
- suite.py
- js_import
- CoreFaithfulCtx
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- build_inputs
- _harvest_cancelled
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- Manual installation — Hermes Workflows 1.1.1
- Hermes Workflows
- Run operations and read model
- DoorLane
- test_model_law_dad50be0.py
- test_run_context_seed_guard.py
- test_suite_admission_17.py
- test_tiers.py
- child_metrics
- _fmt_goal
- node_facts
- 11-claim-wrapper.py
- Claim
- test_validator_caps.py
- manifest.json
- _coerce_graph
- dynamic-agent-count.js
- _LADDER
- Integrated
- _lane_hygiene_preamble
- _quota_note
- Run
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
1. `efp()` - 37 edges
2. `jload()` - 36 edges
3. `run_child()` - 33 edges
4. `_Importer` - 27 edges
5. `_Exporter` - 26 edges
6. `loop()` - 23 edges
7. `run_state()` - 23 edges
8. `log()` - 22 edges
9. `_adopt_child()` - 22 edges
10. `act_run()` - 21 edges

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

## Communities (133 total, 30 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (100): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+92 more)

### Community 1 - "sys"
Cohesion: 0.05
Nodes (23): os, shutil, sys, Identical solo child wrapper for both tag and candidate; records env key sets.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), #24 — subscription-quota 429s are NOT transient transport. (a) a marker… (+15 more)

### Community 2 - "importlib_util"
Cohesion: 0.07
Nodes (26): contextlib, importlib_util, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), F3 boundary/claim integration: real door processes + kernel flock; no hook in… (+18 more)

### Community 3 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 4 - "plugin_api.py"
Cohesion: 0.08
Nodes (26): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+18 more)

### Community 5 - "subprocess"
Cohesion: 0.06
Nodes (9): subprocess, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is… (+1 more)

### Community 6 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 7 - ".meta"
Cohesion: 0.09
Nodes (31): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+23 more)

### Community 8 - "_Exporter"
Cohesion: 0.13
Nodes (12): _Exporter, _js_literal(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics…, Plain-agent schema with the defaults.schema fill of wfcommon.py:411-413., Per-item schema as the runner resolves it: fanout.schema, else the node schema… (+4 more)

### Community 9 - "time"
Cohesion: 0.07
Nodes (14): glob, hermes_constants, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.… (+6 more)

### Community 10 - "wfcommon.py"
Cohesion: 0.09
Nodes (31): shlex, amend_preview(), current_attempt(), _downstream(), find_run(), launch_runs_root(), node_child_home(), node_child_metrics() (+23 more)

### Community 11 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 12 - "Changelog"
Cohesion: 0.07
Nodes (28): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.1 — 2026-09-25, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes (+20 more)

### Community 13 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 14 - "hermes_home"
Cohesion: 0.09
Nodes (27): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), hermes_home(), hermes_root(), launcher_profile(), _nested(), _no_unresolved_ref() (+19 more)

### Community 15 - "jload"
Cohesion: 0.13
Nodes (26): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), emit(), finalize(), main(), consume_markers(), loop() (+18 more)

### Community 16 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 17 - "json"
Cohesion: 0.09
Nodes (10): copy, hashlib, json, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Authoring door regressions; all state stays in this worktree, no…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes. (+2 more)

### Community 18 - "act_run"
Cohesion: 0.10
Nodes (26): act_amend(), act_run(), act_save(), _frozen_committed(), _input_graph(), _lane_entry(), _lane_paths(), _liveness_hint_suffix() (+18 more)

### Community 19 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 20 - "log"
Cohesion: 0.13
Nodes (24): _bounded_retry(), _dangling_placeholders(), _fail_precondition(), log(), now(), park_gate(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose… (+16 more)

### Community 21 - "wf_dialect.py"
Cohesion: 0.11
Nodes (21): _const_name(), _forbidden_label(), _has_tpl(), _line(), _match_close(), node_check(), _ordered_item(), _parse_literal() (+13 more)

### Community 22 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 23 - "efp"
Cohesion: 0.15
Nodes (21): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+13 more)

### Community 24 - "wf.py"
Cohesion: 0.12
Nodes (20): concurrent_futures, drain_inbox(), extract_json(), _lane_gate(), last_balanced_object(), _match_object(), Return {node_id: [steering texts]} for un-consumed steering lines., hermes-workflows engine — replay-skip runner. One process per run, owned by the… (+12 more)

### Community 25 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 26 - "run_child"
Cohesion: 0.11
Nodes (21): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _profile_evidence() (+13 more)

### Community 27 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 28 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 29 - "_Importer"
Cohesion: 0.22
Nodes (8): _Importer, _ordered(), Best-effort name for a glue expression, from its visible method calls., A literal label -> str; a template label -> its literal spine (for ids)., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, The exporter's own `## Inputs (wf/1 refs)` tail is pure refs: fold it back to…, A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the…, A fan-out ITEM goal: item/prev fields -> bare `{field}` (wf.py fmt_goal). An…

### Community 30 - "act_status"
Cohesion: 0.13
Nodes (17): act_release(), act_status(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error(), _lane_state(), _last_event_ts() (+9 more)

### Community 32 - "_adopt_child"
Cohesion: 0.11
Nodes (17): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _kill_adopted(), _log_recent(), _note_turn_tier(), _proc_alive(), Typed termination from the child's quiet turn report (core PR pending; the… (+9 more)

### Community 33 - "3. Operate"
Cohesion: 0.11
Nodes (18): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+10 more)

### Community 34 - "validate_graph_errors"
Cohesion: 0.12
Nodes (15): _v(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.… (+7 more)

### Community 35 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 37 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 38 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 39 - ".refuse"
Cohesion: 0.19
Nodes (6): _control_kw(), Top-level statements as (start, end) offsets: split on `;` or newline at…, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., _statements()

### Community 40 - "_resolve_models"
Cohesion: 0.17
Nodes (16): _alias_provider_pair(), _model_policy_error(), model_tiers(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,… (+8 more)

### Community 41 - "pathlib"
Cohesion: 0.17
Nodes (9): pathlib, re, capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Regression: launch a run in the tool's session; the payload carries a parser-…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-… (+1 more)

### Community 42 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 43 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 44 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 45 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).…, Fresh interpreter; cfg_text is the RAW config.yaml (settings + legacy config). (+4 more)

### Community 46 - "__init__.py"
Cohesion: 0.16
Nodes (14): difflib, act_inbox(), _owner_setting_read(), _ping_note(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD… (+6 more)

### Community 47 - "_ping_route_once"
Cohesion: 0.14
Nodes (14): _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the… (+6 more)

### Community 49 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 50 - "_expand_config_values"
Cohesion: 0.13
Nodes (15): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _expand_config_values(), _is_non_env_secret_ref(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,… (+7 more)

### Community 51 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 52 - "test_require_route_25.py"
Cohesion: 0.15
Nodes (9): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, HTTP429, Meta, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+1 more)

### Community 53 - "run_state"
Cohesion: 0.16
Nodes (14): act_steer(), deps_ok(), blocked_by(), dep_satisfied(), 91b9a3de: cross-container liveness truth. The runner takes an exclusive…, 91b9a3de: ONE liveness law, cross-container safe. The runner holds an exclusive…, Graph-bound runner verdict, or a crash when a previous pid lacks identity. No…, P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with… (+6 more)

### Community 54 - "amend"
Cohesion: 0.17
Nodes (13): 3d. Failures, resume, amend, What you get, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Run and handoff, Smallest working graph (+5 more)

### Community 55 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 56 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.15
Nodes (6): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 57 - "DialectRefusal"
Cohesion: 0.18
Nodes (8): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 58 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 59 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 60 - "AGENTS.md"
Cohesion: 0.20
Nodes (7): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Node budgets

### Community 61 - "_create_run"
Cohesion: 0.20
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+4 more)

### Community 62 - "SKILL.md"
Cohesion: 0.18
Nodes (6): Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 64 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 65 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 66 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 67 - "test"
Cohesion: 0.24
Nodes (10): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), _active_spawn(), _active_spawns(), ONE verification law for a spawn record (790c6ad): status=running + efp match +…, All verified uncommitted child identities, never historical DB liveness. (+2 more)

### Community 68 - "_stamp_served"
Cohesion: 0.22
Nodes (11): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Commit actual child seat truth, never the requested alias. No row means unknown., _route_hold(), _route_home(), _seat_alias_map() (+3 more)

### Community 69 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 70 - "_lib_path"
Cohesion: 0.22
Nodes (10): act_library(), _lib_path(), _lib_read(), library_root(), _library_roots(), `/wf` — the library front door. `/wf <name> [note]` supplies the note…, Resolved library root first; legacy launch-root library second (F1 #14). Graphs…, WRITE resolver: always the resolved root (current best version lands there). (+2 more)

### Community 71 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 72 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 74 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 75 - "test_packaging.py"
Cohesion: 0.22
Nodes (6): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, types, zipfile

### Community 76 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 77 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 78 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 79 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.22
Nodes (9): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), _owner_settings_error() (+1 more)

### Community 80 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 82 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 83 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 85 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 86 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 87 - "js_import"
Cohesion: 0.29
Nodes (7): check(), refuses(), export_report(), js_import(), _main(), See module docstring. `node_check=False` skips the optional subprocess gate., {"ok": True, "js": str, "lossy": [{node, key, value}], "warnings": [...]} |…

### Community 88 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 91 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 92 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 93 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 94 - "_harvest_cancelled"
Cohesion: 0.29
Nodes (7): _harvest_cancelled(), _harvest_death(), Tiny forgiving validator: type / required / properties / items., #4 harvest-on-death: a child that died (rc!=0 / timeout / cap — the CALLER…, a2d7f664 harvest-at-cancel: the cancelled class was deliberately excluded from…, validate(), chk()

### Community 95 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 96 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 97 - "Manual installation — Hermes Workflows 1.1.1"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.1, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 98 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 99 - "Run operations and read model"
Cohesion: 0.33
Nodes (5): Lanes: in-flight dedupe for pollers, Library provenance, Run operations and read model, Runs root, identity, and the trust boundary, Small, parent-gated escalation recipe (no new engine feature)

### Community 101 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 103 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 105 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 106 - "_fmt_goal"
Cohesion: 0.27
Nodes (4): _fmt_goal(), _mask(), wf.py fmt_goal, duplicated so the exporter stays standalone., Return a same-length copy of `src` where the INSIDE of every string literal and…

### Community 107 - "node_facts"
Cohesion: 0.33
Nodes (6): node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.…, B1 + #17 evidence read model for one node: queued = lines addressed to the node…, _steer_state()

### Community 108 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 110 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 111 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 112 - "_coerce_graph"
Cohesion: 0.50
Nodes (4): _coerce_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, quote_json_parse_error(), ±40 chars of the source around the offset of a JSONDecodeError — what the door…

### Community 113 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 116 - "_lane_hygiene_preamble"
Cohesion: 0.50
Nodes (4): _is_build_lane(), _lane_hygiene_preamble(), The build shape: `shape: "build"` declared, or a `repo:` lane declared (the…, Machine-generated lane-hygiene preamble for build-shape nodes ("" otherwise).…

### Community 117 - "_quota_note"
Cohesion: 0.50
Nodes (4): _quota_cache_path(), _quota_note(), #24 (b): seat-local memory of models known to be subscription-exhausted., #24 (b): record model -> reset horizon from a fatal_quota marker. Advisory…

## Knowledge Gaps
- **288 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+283 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 968 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `test`, `_resolve_models`, `Changelog`, `jload`, `run_state`, `build_inputs`, `act_status`?**
  _High betweenness centrality (0.224) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `ref_node_fs`, `.meta`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _288 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05405940594059406 - nodes in this community are weakly interconnected._
- **Should `sys` be split into smaller, more focused modules?**
  _Cohesion score 0.04706504494976203 - nodes in this community are weakly interconnected._
- **Should `importlib_util` be split into smaller, more focused modules?**
  _Cohesion score 0.06859903381642513 - nodes in this community are weakly interconnected._