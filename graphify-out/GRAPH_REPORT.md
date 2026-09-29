# Graph Report - tree  (2026-09-29)

## Corpus Check
- 164 files · ~203,897 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1717 nodes · 3466 edges · 119 communities (91 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 230 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- sys
- os
- wf.py
- wfcommon.py
- test_fanout_expand.mjs
- .meta
- test_prompt_workdir.py
- jload
- json
- tempfile
- test_11_ui_imports.mjs
- test_sprint101w2_D2-steer-liveness.py
- test_fanout_item_goal.py
- log
- _Exporter
- hermes_home
- pathlib
- efp
- .refuse
- subprocess
- ref_node_fs
- test_live_truth_ui.mjs
- validate_graph_errors
- test_pill_rail_expand.mjs
- _adopt_child
- loop
- CurrentAttemptMetrics
- _Importer
- AGENTS.md
- 3. Operate
- EngineNextCut
- Run operations and read model
- plugin_api.py
- __init__.py
- _ping_route_once
- test_require_route_25.py
- test_register_surface.mjs
- wf_dialect.py
- test_cross_container_liveness_91b9a3de.py
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- test_orphan_adopt_790c6ad.py
- act_run
- SKILL.md
- CardBackend
- test_edge_routing.mjs
- test_session_strip.mjs
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- main
- test_tiers.py
- _resolve_models
- act_amend
- _create_run
- DialectRefusal
- test_pill_rail.mjs
- test_review_fixes.py
- test_route_efforts_b3c98b2a.py
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- Changelog
- act_save
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- test
- test_node_facts.py
- Contributing to hermes-workflows
- TeamIntegration
- FakeHTTPError
- test_sprint101w2_B2-retry.py
- test_engine.py
- test_routing_routes.py
- _parse_literal
- model_preflight
- suite.py
- CoreFaithfulCtx
- test_sprint101w2_C1-defaults.py
- test_steer_live_40.py
- build_inputs
- hermes_home
- 1.0.2 — 2026-09-26 — the run watches itself
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- graph_check.py
- DoorLane
- test_failed_events_77.py
- child_metrics
- 1.0.1 — 2026-09-25
- _bind_run_context
- 11-claim-wrapper.py
- Claim
- test_papercuts_0922.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- Run
- find_run
- release_gate
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
1. `jload()` - 36 edges
2. `efp()` - 36 edges
3. `run_child()` - 31 edges
4. `_Importer` - 24 edges
5. `loop()` - 23 edges
6. `_Exporter` - 23 edges
7. `run_state()` - 23 edges
8. `log()` - 22 edges
9. `_adopt_child()` - 22 edges
10. `main()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` --references--> `useValue()`  [INFERRED]
  CHANGELOG.md → tests/test_fanout_expand.mjs
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (119 total, 28 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.06
Nodes (91): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+83 more)

### Community 1 - "sys"
Cohesion: 0.05
Nodes (22): importlib_util, shutil, sys, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).… (+14 more)

### Community 2 - "os"
Cohesion: 0.05
Nodes (16): os, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.… (+8 more)

### Community 3 - "wf.py"
Cohesion: 0.07
Nodes (43): concurrent_futures, _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), extract_json(), _first_message_s(), last_balanced_object() (+35 more)

### Community 4 - "wfcommon.py"
Cohesion: 0.06
Nodes (33): shlex, _active_spawn(), amend_preview(), blocked_by(), current_attempt(), _downstream(), effective_runs_root(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE… (+25 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (29): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+21 more)

### Community 6 - ".meta"
Cohesion: 0.09
Nodes (30): 1.0.17 — 2026-09-28, 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block (+22 more)

### Community 7 - "test_prompt_workdir.py"
Cohesion: 0.10
Nodes (26): argparse, fnmatch, Pattern, excluded(), load_guards(), main(), Path, Build a publishable tree from git ls-files, refusing to emit private strings.… (+18 more)

### Community 8 - "jload"
Cohesion: 0.12
Nodes (27): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), Explicit resume/watch verb. Read-only status/list never spawn; wait may resume… (+19 more)

### Community 9 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 10 - "tempfile"
Cohesion: 0.07
Nodes (12): tempfile, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), Authoring door regressions; all state stays in this worktree, no…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, The child launcher is operator-controlled, never a tool argument., lock(), mk() (+4 more)

### Community 11 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (24): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+16 more)

### Community 12 - "test_sprint101w2_D2-steer-liveness.py"
Cohesion: 0.09
Nodes (13): capture(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Lane A preconditions: null and missing ancestor fields fail before Popen, then…, fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>. (+5 more)

### Community 13 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 14 - "log"
Cohesion: 0.11
Nodes (26): _bounded_retry(), _dangling_placeholders(), _lane_gate(), log(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for… (+18 more)

### Community 15 - "_Exporter"
Cohesion: 0.16
Nodes (11): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, goal (+context) + the exporter-owned refs section for after/inputs. (+3 more)

### Community 16 - "hermes_home"
Cohesion: 0.09
Nodes (23): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, hermes_home(), hermes_root(), launcher_profile(), node_child_home(), node_child_metrics(), node_facts(), precondition_facts() (+15 more)

### Community 17 - "pathlib"
Cohesion: 0.11
Nodes (14): glob, hashlib, hermes_constants, pathlib, re, 1.1 door contracts: advisory keyed claims, no implicit resume, opt-in source., Regression: launch a run in the tool's session; the payload carries a parser-…, check() (+6 more)

### Community 18 - "efp"
Cohesion: 0.15
Nodes (22): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), Walk-in example, nodes(), put(), f0f154d5dd80220c: live-shaped unstamped replay and fail-closed boundaries.…, run() (+14 more)

### Community 19 - ".refuse"
Cohesion: 0.13
Nodes (9): _control_kw(), _forbidden_label(), Top-level statements as (start, end) offsets: split on `;` or newline at…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the…, A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the…, A fan-out ITEM goal: item/prev fields -> bare `{field}` (wf.py fmt_goal). (+1 more)

### Community 20 - "subprocess"
Cohesion: 0.12
Nodes (12): copy, subprocess, F3 boundary/claim integration: real door processes + kernel flock; no hook in…, GoldenSolo, Frozen v1.0.15 solo gate; six real fake_hermes workflows; no team settings., Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Lane E: cross-lane executable integration fixtures; no production… (+4 more)

### Community 21 - "ref_node_fs"
Cohesion: 0.12
Nodes (14): ref_node_assert, ref_node_fs, ref_node_path, ref_node_url, tmp, code, { fanItems, fanCounts }, here (+6 more)

### Community 22 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 23 - "validate_graph_errors"
Cohesion: 0.11
Nodes (17): _v(), apply_graph_defaults(), _defaults_errors(), grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key… (+9 more)

### Community 24 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 25 - "_adopt_child"
Cohesion: 0.11
Nodes (18): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _note_turn_tier(), _proc_alive() (+10 more)

### Community 26 - "loop"
Cohesion: 0.13
Nodes (18): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., acquire_lock(), drain_inbox(), emit(), _fail_precondition(), finalize(), consume_markers() (+10 more)

### Community 28 - "_Importer"
Cohesion: 0.23
Nodes (10): _Importer, _line(), _match_close(), _ordered(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., Offset of the bracket closing the one at `open_at`., Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids). (+2 more)

### Community 29 - "AGENTS.md"
Cohesion: 0.12
Nodes (13): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+5 more)

### Community 30 - "3. Operate"
Cohesion: 0.11
Nodes (18): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+10 more)

### Community 31 - "EngineNextCut"
Cohesion: 0.22
Nodes (3): 3c. Fan-out, gates, branches, EngineNextCut, deps_ok()

### Community 32 - "Run operations and read model"
Cohesion: 0.11
Nodes (17): 3d. Failures, resume, amend, For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get (+9 more)

### Community 33 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 34 - "__init__.py"
Cohesion: 0.14
Nodes (17): difflib, act_inbox(), handle(), _lane_key_error(), _lane_state(), _last_event_ts(), model_tiers(), _output_pointer() (+9 more)

### Community 35 - "_ping_route_once"
Cohesion: 0.12
Nodes (17): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy… (+9 more)

### Community 36 - "test_require_route_25.py"
Cohesion: 0.12
Nodes (10): check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned…, set_ping() (+2 more)

### Community 37 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 38 - "wf_dialect.py"
Cohesion: 0.12
Nodes (15): export_report(), _fmt_goal(), _has_tpl(), js_import(), _main(), _mask(), node_check(), _ordered_item() (+7 more)

### Community 39 - "test_cross_container_liveness_91b9a3de.py"
Cohesion: 0.12
Nodes (8): contextlib, fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, Current-attempt heartbeat with real fake child identity; no provider access., SystemExit must never reach the crash net (phantom 'crashed: SystemExit: 0').…

### Community 40 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 41 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 42 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.14
Nodes (9): datetime, signal, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until(), env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):… (+1 more)

### Community 43 - "act_run"
Cohesion: 0.16
Nodes (16): act_library(), act_run(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), library_root(), _library_roots() (+8 more)

### Community 44 - "SKILL.md"
Cohesion: 0.13
Nodes (10): Contributor checks (not ordinary user setup), Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay, Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics (+2 more)

### Community 45 - "CardBackend"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 46 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 47 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 48 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 50 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 51 - "main"
Cohesion: 0.19
Nodes (14): main(), state(), dep_satisfied(), fingerprint_valid(), gate_answer_valid(), _legacy_chain_unchanged(), node_rec(), prune_states() (+6 more)

### Community 52 - "test_tiers.py"
Cohesion: 0.16
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 53 - "_resolve_models"
Cohesion: 0.19
Nodes (14): _alias_provider_pair(), _model_policy_error(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Validate effective node routes after defaults and resolution, before graph.json., Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model. (+6 more)

### Community 54 - "act_amend"
Cohesion: 0.15
Nodes (13): act_amend(), _frozen_committed(), _liveness_hint_suffix(), _profile_error(), 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, FEEDBACK #152be7f7: warn-and-surface liveness, called ONCE at the…, Dead-route copy appended to the run/amend hint (agent-visible, warn-and-… (+5 more)

### Community 55 - "_create_run"
Cohesion: 0.18
Nodes (12): act_list(), _card(), _create_run(), _hermes_bin(), _identity_stamps(), Use the tool worker's task-local session, not another turn's process env., 1.1 (RATIFY F1): run.json identity keys, emitted ONLY when derivable — a no-…, Under the lane flock: complete run dir, atomic registry entry, then spawn. (+4 more)

### Community 56 - "DialectRefusal"
Cohesion: 0.18
Nodes (8): The js dialect seam (#33): `wf_dialect.py`, DialectRefusal, js_export(), _NonLiteral, Exception, wf/1 graph dict -> js source (str). Raises DialectRefusal with a named reason., Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 57 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 58 - "test_review_fixes.py"
Cohesion: 0.14
Nodes (3): answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…

### Community 59 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.17
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 61 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 62 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is…, behavior=None restores the non-core host (import raises); dict stubs the… (+2 more)

### Community 63 - "Changelog"
Cohesion: 0.18
Nodes (10): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+2 more)

### Community 64 - "act_save"
Cohesion: 0.18
Nodes (11): act_save(), _coerce_graph(), _input_graph(), _model_names_valid(), Return graph-level and node-level defects together, before any write/spawn., The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline… (+3 more)

### Community 65 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 66 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 67 - "test"
Cohesion: 0.24
Nodes (10): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), active_child(), ONE verification law for a spawn record (790c6ad): status=running + efp match +… (+2 more)

### Community 68 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 69 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 71 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 72 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 73 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 74 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 75 - "_parse_literal"
Cohesion: 0.25
Nodes (6): _parse_literal(), A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, _Ref, _Tpl, _unescape()

### Community 76 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 77 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 78 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 80 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 81 - "build_inputs"
Cohesion: 0.29
Nodes (7): build_inputs(), _inputs_block(), plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet., Node-level `inputs: [refs]` -> (prompt section, error). ONE fenced json block…, resolve_ref(), _unmet_requires()

### Community 82 - "hermes_home"
Cohesion: 0.33
Nodes (7): hermes_home(), {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., _route_hold(), _route_home(), _seat_alias_map()

### Community 83 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 84 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (5): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, Meta

### Community 85 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 86 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 89 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 90 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 91 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 92 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (4): die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write()

### Community 95 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 96 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 97 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 101 - "find_run"
Cohesion: 0.50
Nodes (4): find_run(), launch_runs_root(), Runs root of the RAW process environment (never the context-resolved home).…, Locate a run dir by id: resolved runs_root() first; legacy launch root only for…

### Community 102 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **269 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 870 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `jload` to `plugin.js`, `test`, `test_fanout_expand.mjs`, `build_inputs`, `main`, `_resolve_models`, `Changelog`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **Why does `useValue()` connect `test_fanout_expand.mjs` to `jload`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `test_card_frontend_contract.mjs`, `.meta`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06020066889632107 - nodes in this community are weakly interconnected._
- **Should `sys` be split into smaller, more focused modules?**
  _Cohesion score 0.05012531328320802 - nodes in this community are weakly interconnected._
- **Should `os` be split into smaller, more focused modules?**
  _Cohesion score 0.05319148936170213 - nodes in this community are weakly interconnected._