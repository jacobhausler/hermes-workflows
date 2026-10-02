# Graph Report - tree  (2026-10-02)

## Corpus Check
- 193 files · ~264,067 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2119 nodes · 4301 edges · 141 communities (108 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 266 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- jload
- EngineNextCut
- importlib_util
- shutil
- lane_recover.py
- efp
- os
- time
- test_fanout_expand.mjs
- _Exporter
- hermes_home
- .meta
- test_lane_hygiene_preamble_8edcc9bf.py
- test_11_ui_imports.mjs
- json
- subprocess
- CurrentAttemptMetrics
- DoorLib50
- run_state
- sys
- wf_dialect.py
- test_fanout_item_goal.py
- _Importer
- __init__.py
- pathlib
- test_silent_death_reaper_8.py
- act_run
- .agent_args
- ref_node_fs
- _ping_route_once
- test_live_truth_ui.mjs
- run_agent_node
- test_daemonize_8.py
- settings_runs_root
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- test_require_route_25.py
- plugin_api.py
- wfcommon.py
- test_register_surface.mjs
- Changelog
- __init__.py
- act_save
- shutil
- _route_enforcement
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- LiveTruth
- test_machine_watch_94.py
- test_node_panel.mjs
- test_sprint101_A-door.py
- 11-golden-solo.py
- test_orphan_adopt_790c6ad.py
- TeamIntegration
- test_pill_rail.mjs
- test_wfpid_owner_8.py
- Changelog
- _create_run
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_preflight_liveness_152be7f7.py
- _bounded_retry
- validate_graph_errors
- when_true
- test_route_efforts_b3c98b2a.py
- test_amend_rebake_034849a2.py
- ConcurrencyBake100
- test_node_facts.py
- Contributing to hermes-workflows
- ref_node_url
- graph_check.py
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- ProvenanceCounters
- test_schema_enum_107.py
- act_amend
- test_sprint101w2_B2-retry.py
- DialectRefusal
- _expand_config_value
- _SV
- Disclosure verification — clause-by-clause evidence
- jload
- test_resume_fresh_session_102.py
- test_routing_routes.py
- test_run_dry_run.py
- SKILL.md
- model_preflight
- plugin-catalog: add `hermes-workflows` (community, automation)
- act_inbox
- install
- suite.py
- CoreFaithfulCtx
- test_lane_gate_64c6772b.py
- test_status_next.py
- test_steer_live_40.py
- _defaults_errors
- AGENTS.md
- 1.0.2 — 2026-09-26 — the run watches itself
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- _bind_run_context
- _spawn_runner
- Manual installation — Hermes Workflows 1.1.3
- Hermes Workflows
- Operator playbook (measured lessons; each one was paid for)
- DoorLane
- Claim
- test_model_law_dad50be0.py
- test_suite_admission_17.py
- test_tiers.py
- _expand_config_values
- 1.0.1 — 2026-09-25
- test_papercuts_0922.py
- test_validator_caps.py
- 0.9.0 — 2026-09-24
- manifest.json
- dynamic-agent-count.js
- BlockedLegibility100
- _LADDER
- Integrated
- _AdoptedHandle
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
2. `jload()` - 37 edges
3. `run_child()` - 33 edges
4. `DoorLib50` - 27 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
7. `loop()` - 25 edges
8. `act_run()` - 23 edges
9. `main()` - 23 edges
10. `run_state()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `3d. Failures, resume, amend` --references--> `amend()`  [INFERRED]
  AGENTS.md → tests/test_amend_rebake_034849a2.py
- `The door validates from lists` --references--> `amend()`  [INFERRED]
  CHANGELOG.md → tests/test_amend_rebake_034849a2.py
- `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` --references--> `useValue()`  [INFERRED]
  CHANGELOG.md → tests/test_fanout_expand.mjs
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py

## Import Cycles
- None detected.

## Communities (141 total, 33 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (98): ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups(), ctxRest() (+90 more)

### Community 1 - "wf.py"
Cohesion: 0.05
Nodes (70): concurrent_futures, _adopt_child(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), extract_json() (+62 more)

### Community 2 - "jload"
Cohesion: 0.07
Nodes (50): _acquire(), Run acquire_lock in-process; return ('busy', emitted) or ('acquired', '')., fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), acquire_lock(), drain_inbox() (+42 more)

### Community 3 - "EngineNextCut"
Cohesion: 0.06
Nodes (35): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+27 more)

### Community 4 - "importlib_util"
Cohesion: 0.07
Nodes (28): contextlib, hashlib, importlib_util, signal, tempfile, main(), Twenty real runner crash/resume cycles; status lane_key checked against /proc.…, until() (+20 more)

### Community 5 - "shutil"
Cohesion: 0.05
Nodes (14): shutil, #24 — subscription-quota 429s are NOT transient transport. (a) a marker…, _hermes_bin must never raise under a live door ctx (09-28 launch blocker).…, Library verbs + /wf command: save (from run_id / inline), library list, run…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, 4052d57719653b1a: atomic library replay binding, no real runner., mk_run() (+6 more)

### Community 6 - "lane_recover.py"
Cohesion: 0.08
Nodes (38): argparse, fnmatch, Pattern, apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls() (+30 more)

### Community 7 - "efp"
Cohesion: 0.09
Nodes (36): What you get, 2. The mapping table, File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Per-run concurrency (optional), Staleness and replay (+28 more)

### Community 8 - "os"
Cohesion: 0.06
Nodes (10): os, sqlite3, Dedicated 1.1 child fixture. Never imports the installed Hermes installation.…, Lane C (read model) acceptance, 1.1 team sprint — wfcommon profile/requires…, rerr(), Authoring door regressions; all state stays in this worktree, no…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final… (+2 more)

### Community 9 - "time"
Cohesion: 0.06
Nodes (8): End-to-end test of the `workflow` tool door against fake hermes., Integrated read-model and parser-valid card dedup checks., Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, Sprint-101 w2 lane D2 — #17 steer honesty + #18 child liveness. 1. steer…, v0.3 regressions — the mega-review sign-off (NO_GO) items, each test-locked: V1…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…, time

### Community 10 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (29): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+21 more)

### Community 11 - "_Exporter"
Cohesion: 0.12
Nodes (14): _const_name(), _Exporter, _js_literal(), _js_str(), Deterministic JS literal (sorted object keys) — JSON is a JS subset., fan-out b directly after fan-out a with items_from a.items and no other reader…, A fan-out that is one template for every item (no per-item goals) -> template…, Effective `context` of an agent node = wfcommon.apply_graph_defaults semantics… (+6 more)

### Community 12 - "hermes_home"
Cohesion: 0.07
Nodes (32): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, _attempt_api_calls(), hermes_home(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, {alias -> target model} for one seat's config, stdlib-only (same YAML-lite…, #25: commit-time fail-closed hold (field report fb-fix-9c575645: pinned billed…, The target owns the child's session DB; absent routing preserves legacy home., Tool-progress evidence for the #5 bounded retry: True only when the dead… (+24 more)

### Community 13 - ".meta"
Cohesion: 0.09
Nodes (28): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.1 `agent(prompt, options?)` (+20 more)

### Community 14 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.10
Nodes (26): build(), collect_sources(), main(), Path, Build the private, reproducible Hermes Workflows source ZIP (stdlib only)., _zip_info(), stat, check() (+18 more)

### Community 15 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 16 - "json"
Cohesion: 0.08
Nodes (9): json, Identical solo child wrapper for both tag and candidate; records env key sets.…, Lane A: routed spawn, env boundary, missing-profile race and DB ownership., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.… (+1 more)

### Community 17 - "subprocess"
Cohesion: 0.07
Nodes (10): subprocess, Keeper, Suite hook for the standalone 20-cycle keeper kill/resume harness., Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, 00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Ledger e68544a37be37657 (fb-fix-2dd8de73): a harvest-on-death `partial` must…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when… (+2 more)

### Community 18 - "CurrentAttemptMetrics"
Cohesion: 0.17
Nodes (10): Run and handoff, Smallest working graph, Workflow authoring (1.1.3), CurrentAttemptMetrics, node_facts(), precondition_facts(), 1.1 (RATIFY F4) fact rendering for a precondition failure: the string 'failed…, Record facts for one node (fan-out item via `index`), plus its steer truth.… (+2 more)

### Community 20 - "run_state"
Cohesion: 0.12
Nodes (25): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _lane_key_error() (+17 more)

### Community 21 - "sys"
Cohesion: 0.09
Nodes (15): copy, sys, die(), Test-only crash injector: kill the claiming process at an actual filesystem…, replace(), write(), Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, #33 js-dialect interop: the 13-fixture corpus is the spec. (1) every `verdict:… (+7 more)

### Community 22 - "wf_dialect.py"
Cohesion: 0.08
Nodes (24): check(), refuses(), export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _line() (+16 more)

### Community 23 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 24 - "_Importer"
Cohesion: 0.16
Nodes (10): _control_kw(), _forbidden_label(), _Importer, _match_close or a named refusal (F2 #36): an unterminated construct is reported…, True when masked[s:e] does not close every bracket it opens (an unterminated…, Best-effort name for a glue expression, from its visible method calls., dialect.md row 13: name Date.now()/Math.random()/new Date()/Promise.* by name., `${expr}` -> ('args', key) | ('const', name, [fields]) | refuse. Accepts the… (+2 more)

### Community 25 - "__init__.py"
Cohesion: 0.13
Nodes (25): difflib, _alias_provider_pair(), handle(), _model_policy_error(), model_tiers(), _owner_settings_error(), _ping_note(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The… (+17 more)

### Community 26 - "pathlib"
Cohesion: 0.09
Nodes (13): glob, pathlib, plugin_api, re, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, #27 regression pin: graph_check's canonical multi-edge policy. graphify-… (+5 more)

### Community 27 - "test_silent_death_reaper_8.py"
Cohesion: 0.09
Nodes (9): fcntl, io, hold(), 91b9a3de (recurrence of baa0088f19452326): cross-container runner liveness. The…, A holder in ANOTHER process group — the kernel view of 'a runner in a sibling…, kill_tree(), Sweep the current runner (own pgid via start_new_session) and every child the…, #8 fix-law item 2 (crash-visibility half): a door respawn after a SILENT runner… (+1 more)

### Community 28 - "act_run"
Cohesion: 0.11
Nodes (23): act_library(), act_run(), _concurrency_bake(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read() (+15 more)

### Community 29 - ".agent_args"
Cohesion: 0.15
Nodes (13): _ordered(), _parse_literal(), Split masked[s:e] on `sep` at bracket depth 0 -> list of (start, end)., A template literal: parts are str (literal text) or _Ref (an `${expr}`)., Parse one literal starting at offset i (whitespace allowed). Returns (value,…, Parse `agent(<prompt>, {opts})` between the parens. Returns (prompt, opts,…, A literal label -> str; a template label -> its literal spine (for ids)., A NON-fan-out goal: refs -> after/inputs (§3 data-flow rule), prose names the… (+5 more)

### Community 30 - "ref_node_fs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, macEvidence, parserSource, plugin (+9 more)

### Community 31 - "_ping_route_once"
Cohesion: 0.10
Nodes (20): _hermes_bin(), _import_call_llm(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _ping_subprocess(), _quota_refusal() (+12 more)

### Community 32 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 33 - "run_agent_node"
Cohesion: 0.11
Nodes (20): build_inputs(), _dangling_placeholders(), _inputs_block(), _lane_gate(), Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, plan.items.0.name' -> outputs['plan'] walked by dotted path. `missing` is…, Inspect committed ancestor outputs only; null and absent are both unmet.… (+12 more)

### Community 34 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (13): ctypes, select, alive(), call(), descendants(), _kill(), proc_map(), psutil children(recursive) equivalent: live ppid links, /proc only. (+5 more)

### Community 35 - "settings_runs_root"
Cohesion: 0.12
Nodes (18): Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), effective_runs_root(), launcher_profile(), _nested(), _no_unresolved_ref(), owner_setting(), profile_errors(), A pid is not ownership: verify a live, non-zombie `wf.py run <id>`. /proc gives… (+10 more)

### Community 36 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 37 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 38 - "test_require_route_25.py"
Cohesion: 0.11
Nodes (11): ast, check(), main(), Packaging-specific reproducibility, manifest, and import-isolation checks., Runner + children must inherit the OWNER's resolved profile home. Host fact…, HTTP429, Exception, #25 — fail-closed pinned routes, default ON. fb-fix-9c575645: nodes pinned… (+3 more)

### Community 39 - "plugin_api.py"
Cohesion: 0.21
Nodes (16): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+8 more)

### Community 40 - "wfcommon.py"
Cohesion: 0.11
Nodes (16): shlex, _active_spawn(), current_attempt(), launch_runs_root(), quote_json_parse_error(), hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE…, ±40 chars of the source around the offset of a JSONDecodeError — what the door…, 91b9a3de: cross-container liveness truth. The runner takes an exclusive… (+8 more)

### Community 41 - "test_register_surface.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 42 - "Changelog"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 43 - "__init__.py"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 44 - "act_save"
Cohesion: 0.13
Nodes (16): act_save(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _model_names_valid(), #50: `tags` is a list of 1..TAGS_MAX short tokens, each under the library-name…, Return graph-level and node-level defects together, before any write/spawn. (+8 more)

### Community 45 - "shutil"
Cohesion: 0.16
Nodes (3): CardBackend, Context, Core-faithful get_config: plugin-scoped, reserved roots RAISE. The real core…

### Community 46 - "_route_enforcement"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 48 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 49 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (12): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;…, #41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).… (+4 more)

### Community 51 - "test_machine_watch_94.py"
Cohesion: 0.16
Nodes (8): argv(), check(), native_engine(), spawn(), probe_transitions(), Executable machine-watch contract: probe transitions and native gate scheduling., Door-transport guard: run_context must never silently route a map to seed.…, state()

### Community 52 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 53 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 54 - "11-golden-solo.py"
Cohesion: 0.19
Nodes (9): hermes_constants, capture(), _core_home(), main(), normalize(), Golden solo capture/compare against v1.0.15 using the SAME fake_hermes. python3…, Exception, #71 regression pin: the shelf is a live production surface — no test may write… (+1 more)

### Community 55 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.17
Nodes (7): datetime, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 56 - "TeamIntegration"
Cohesion: 0.26
Nodes (3): Parse the child's first trace record once it has LANDED. The old predicate was…, TeamIntegration, until()

### Community 57 - "test_pill_rail.mjs"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 58 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (9): alive(), cmdline(), _proc_pids(), #8 (review findings 3+4, P1): the ADMITTED runner is the SOLE wf.pid owner.…, Live runner pids for THIS run id: cmdline carries the exact run dir name., Poll until the run's admitted runner self-stamped wf.pid and is alive., runners_for(), wait_live() (+1 more)

### Community 59 - "Changelog"
Cohesion: 0.17
Nodes (12): 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+4 more)

### Community 60 - "_create_run"
Cohesion: 0.18
Nodes (12): act_list(), _card(), _create_run(), _identity_stamps(), _liveness_hint_suffix(), Dead-route copy appended to the run/amend hint (agent-visible, warn-and-…, ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) >…, Use the tool worker's task-local session, not another turn's process env. (+4 more)

### Community 62 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 63 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.26
Nodes (10): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, behavior=None restores the non-core host (import raises); dict stubs the…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is… (+2 more)

### Community 64 - "_bounded_retry"
Cohesion: 0.17
Nodes (12): _banked_work(), _bounded_retry(), _clean_capture(), _dead_session_harvest(), #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Message-existence evidence for the #102 dead-session guard: True when the dead…, Strip the dead-session CLI noise lines from a death capture (#102)., (file_names, [(name, content_excerpt), ...]) of the child's durable work dir —… (+4 more)

### Community 65 - "validate_graph_errors"
Cohesion: 0.18
Nodes (10): grammar_errors(), gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, 1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called…, Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, requires_errors(), validate_graph_errors(), E() (+2 more)

### Community 66 - "when_true"
Cohesion: 0.21
Nodes (12): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, Conditional-gate predicate over a BOUNDED grammar (out paths, literals,…, _tok_when(), _when_and(), _when_atom(), _when_cmp(), _when_expr() (+4 more)

### Community 67 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (6): agent_reasoning_effort, core(), Ctx, fake(), fb b3c98b2a0518a8f0: the submit door validates routes and survives absent core.…, Isolate both parent package and child module, including poisoned imports.

### Community 68 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 70 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 71 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 72 - "ref_node_url"
Cohesion: 0.20
Nodes (5): ref_node_url, code, { fanItems, fanCounts }, here, src

### Community 73 - "graph_check.py"
Cohesion: 0.40
Nodes (9): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), Graph drift gate: is the committed graphify-out/graph.json current for this…, Return a NEW graph dict in canonical form (see module docstring). Pure; input… (+1 more)

### Community 74 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (7): check(), main(), The #39 review probes (3b/3c/3e) in one session: the role='tool' row is joined…, #37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled…, run(), seed(), seed_review()

### Community 75 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, Exception, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 76 - "ProvenanceCounters"
Cohesion: 0.27
Nodes (3): mk_run(), ProvenanceCounters, Materialise a committed-done run dir; run_json_body is written verbatim to…

### Community 77 - "test_schema_enum_107.py"
Cohesion: 0.22
Nodes (3): agent_node(), enum_err(), #107 — the door ADMITS and the runner ENFORCES schema `enum`. Closed vocabulary…

### Community 78 - "act_amend"
Cohesion: 0.22
Nodes (9): act_amend(), _frozen_committed(), _profile_error(), #25: node key > graph defaults > default True on nodes that pin an explicit…, #25: a node that pins an explicit route and did NOT opt into the fallback…, 1.1 (RATIFY F2): node `profile:` validation — AFTER `{run.KEY}` rendering,…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, _require_route_effective() (+1 more)

### Community 79 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 80 - "DialectRefusal"
Cohesion: 0.28
Nodes (5): DialectRefusal, _NonLiteral, Exception, Raised by the exporter when a graph's semantics have no representable form.…, _Refuse

### Community 81 - "_expand_config_value"
Cohesion: 0.22
Nodes (9): _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m(), _is_non_env_secret_ref(), True for a SecretRef body with a non-`env` source (`bitwarden:FOO`,…, Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source…, Core's policy verbatim: the profile secret scope when one is active, else plain… (+1 more)

### Community 83 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.25
Nodes (6): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence

### Community 84 - "jload"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 86 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (4): Ctx, fake_popen(), FakeProcess, Deterministic regressions for explicit workflow provider/model routing.

### Community 89 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Prefer the core route API; on older cores use the Codex vocabulary for openai-…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 90 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 91 - "act_inbox"
Cohesion: 0.29
Nodes (7): act_inbox(), Two inbox halves, one action name, never in conflict (a child's steer env and a…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, _steer_event(), _steer_lines(), _submit_dir()

### Community 92 - "install"
Cohesion: 0.29
Nodes (6): _owner_setting_read(), THE owner-settings read (#41/#42 share it with hermes_bin): plugin-scoped…, install(), Wrap the door's owner-settings reader: the `runs_root` lookup answers the…, Pin the door's `settings.runs_root` to whatever `WF_RUNS_ROOT` says at call…, _wrap_resolver()

### Community 93 - "suite.py"
Cohesion: 0.29
Nodes (5): admission(), load_baseline(), Serial bounded suite with durable per-case logs and atomic exit ledger. The…, Read a prior ledger into {test: exit}. Contract is exact identities, so an…, Diff red identities base vs fix. An identity match requires BOTH the test name…

### Community 94 - "CoreFaithfulCtx"
Cohesion: 0.29
Nodes (3): CoreFaithfulCtx, get_config with core's exact plugin-relative key rules (plugins_state.py)., RecordingCtx

### Community 95 - "test_lane_gate_64c6772b.py"
Cohesion: 0.29
Nodes (4): fresh(), Digest 29d (64c6772b): a node that declares `repo: <lane>` may not commit…, A fresh throwaway git lane + a fresh run dir under <tmp>/runs/<name>., _v()

### Community 96 - "test_status_next.py"
Cohesion: 0.29
Nodes (3): lock(), mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 97 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 98 - "_defaults_errors"
Cohesion: 0.29
Nodes (6): apply_graph_defaults(), _defaults_errors(), Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, reasoning_levels()

### Community 100 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.33
Nodes (6): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 101 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (5): dict, _fake_parse_retry_after(), Mirrors core's parse contract: headers mapping (both casings) or raw value ->…, FRResult, Meta

### Community 102 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 103 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 104 - "_bind_run_context"
Cohesion: 0.33
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 105 - "_spawn_runner"
Cohesion: 0.33
Nodes (6): One newline-terminated pid off the ready pipe, <= _READY_WAIT_S. None on EOF or…, Spawn the run's runner process — DAEMONIZED out of the caller's tree (#8). Law…, Direct spawn for no-fork platforms / refused fork: here the Popen'd child IS…, _ready_pid(), _spawn_runner(), _spawn_runner_legacy()

### Community 106 - "Manual installation — Hermes Workflows 1.1.3"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.1.3, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 107 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 108 - "Operator playbook (measured lessons; each one was paid for)"
Cohesion: 0.33
Nodes (5): Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 111 - "test_model_law_dad50be0.py"
Cohesion: 0.40
Nodes (3): check(), parent_denied(), dad50be002da89d5: model policy at the door and actual served-route admission.

### Community 112 - "test_suite_admission_17.py"
Cohesion: 0.33
Nodes (3): make_root(), #17 pass-gate admission contract: scripts/suite.py --baseline <ledger> must…, spec: {test name: exit code}; a stub test that exits with that code.

### Community 114 - "_expand_config_values"
Cohesion: 0.33
Nodes (6): _expand_config_values(), Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1…, Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-…, `plugins.entries.hermes-workflows` raw read from the resolved home's…, _raw_owner_settings(), _yaml_load()

### Community 115 - "1.0.1 — 2026-09-25"
Cohesion: 0.40
Nodes (5): 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less

### Community 117 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 118 - "0.9.0 — 2026-09-24"
Cohesion: 0.50
Nodes (4): 0.9.0 — 2026-09-24, Added, Changed, Fixed

### Community 119 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 120 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

### Community 126 - "release_gate"
Cohesion: 0.67
Nodes (3): UI door onto the SAME answer path the tool uses (incl. stale-answer overwrite).…, release_gate(), post

## Knowledge Gaps
- **289 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+284 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1071 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `run_state` to `plugin.js`, `run_agent_node`, `jload`, `test_fanout_expand.mjs`, `__init__.py`, `Changelog`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `useValue()` connect `test_fanout_expand.mjs` to `run_state`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_fs`, `efp`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _289 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.054627911770768915 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05472837022132797 - nodes in this community are weakly interconnected._
- **Should `jload` be split into smaller, more focused modules?**
  _Cohesion score 0.0660377358490566 - nodes in this community are weakly interconnected._