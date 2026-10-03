# AGENTS.md — front door for agents

Written for agents, usable by humans: **install**, **operate**, **contribute**.
Deep detail lives once, in `references/` and the guide files; this file summarizes
and points — one source per fact.

> Union state: items tagged `(open PR #NN)` exist in an open pull request and are
> not merged yet. Everything untagged is on `main`.

## 1. What this is

`hermes-workflows` is a [Hermes Agent](https://github.com/NousResearch/hermes-agent)
plugin. It registers one tool, `workflow`, that runs a **DAG of agent nodes** as a
background process owned by the calling session, plus a desktop DAG view. No daemon,
no control plane: one runner process per run, spawned by the tool call itself. The
**backend half** (`__init__.py`, `wf.py`, `wfcommon.py`, `dashboard/`; stdlib-only
Python) lives under `~/.hermes/plugins/hermes-workflows/` on the machine running
`hermes serve`; the **desktop half** (`desktop/plugin.js`, plain ESM on the desktop
plugin SDK surface) under `~/.hermes/desktop-plugins/hermes-workflows/` on the
machine running the **app**. Children spawn via the stock quiet one-shot CLI; **no
patched Hermes is required** ([docs/patched-core.md](docs/patched-core.md) covers
the one optional field that types turn-cap deaths).

## 2. Install

```sh
hermes plugins install hermes-workflows && hermes plugins enable hermes-workflows
hermes plugins validate ~/.hermes/plugins/hermes-workflows   # then restart hermes serve
```

**Proof it loaded:** `Mounted plugin API routes: /api/plugins/hermes-workflows/` in
`~/.hermes/logs/gui.log` (a `401` on a dashboard path is *not* proof — auth answers
401 for any path). **Remote app:** copy `desktop/plugin.js` to that machine's
`~/.hermes/desktop-plugins/hermes-workflows/`; it hot-loads (missing tab →
Settings → Plugins, then ⌘K → *Reload desktop plugins*). Zip install and removal:
[INSTALL.md](INSTALL.md).

## 3. Operate

The bundled skill ([SKILL.md](SKILL.md)) loads into any session with the plugin.
Deep docs, one source each: [grammar](references/grammar.md) ·
[budgets](references/budgets.md) · [read model & recovery](references/operations.md)
· [operating lessons](references/operator-playbook.md).

### 3a. Surfaces map

The `workflow` tool is action-routed — **twelve actions in the union**: eleven on
`main` (`run`, `status`, `wait`, `release`, `steer`, `inbox`, `amend`, `stop`,
`list`, `save`, `library`) plus `release_lock` `(open PR #47)`. Parameters and
refusal rules live once in operations.md:

| Surface | In one line |
|---|---|
| `run` `wait` `status` `stop` | Launch (inline `graph`, `graph_path`, or `from:` the library; `lane_key` dedupe) / block & resume — the only read action that respawns an idle runner / read-only snapshot, never spawns / cancel (terminal, not a rollback) |
| `release` `steer` `inbox` | Answer a held gate / queue text for a running child (cooperative, never interrupts) / the child-side pull of that text |
| `amend` `save` `library` `list` | Replace the whole graph mid-flight (`dry_run` previews) / shelve a graph / list the shelf / census all runs |
| `release_lock` `(open PR #47)` | Escape hatch for a wedged runner lock; refuses unless the recorded runner is provably dead and fresh lock probes prove the lock free |
| Run states | `running`, `held`, `interrupted`, `done`, `failed`, `stopped` + `liveness-unknown` `(open PR #47)`: while the probe can't answer (`runner_live: null`), `wait` refuses to spawn |
| Graph keys | `name, nodes, description, defaults, model_policy, provenance, grammar` + `include` `(open PR #84)`: expand shelved library graphs into a run at launch (aliased ids, `seeds` for `{run.KEY}`) |
| Owner config | `workflows.runs_root`, `hermes_bin`, model tiers, `confidence_substrate` `(open PR #118)`: a fallback ladder for a route proved dead; substitutions must be disclosed |
| Desktop / slash | `/workflows` page, live-run strip under the composer, `::workflow` card; `/wf` lists the library, `/wf <name> [note]` runs it with `note` as run context |

### 3b. The loop

```
run {graph} → run_id … then wait {run_id} until done/failed/stopped
status {run_id}   release {run_id, gate_id, answer}   stop {run_id}
```

`wait` self-yields ~330 s with a "call wait again" note (host tool deadline).
Payloads carry a derived `next`: held gate → `release`; running/interrupted →
`wait`; failure to fix → `amend`; terminal → empty. **Stay in the loop** — ending
your turn after `run` is the most common way a workflow stalls. Paste the payload's
`card` line (a pasteable run card) alone on its own line in your reply.

### 3c. Authoring rules that bite

Full law: [references/grammar.md](references/grammar.md); tested examples:
`examples/`.

- **Pin `model` + `provider`**: an unset model rides this installation's default
  (fan-out children too); a wrong or capped default surfaces per child.
- **`reasoning` is validated per resolved route, not clamped**: each level is
  checked at launch against the resolved `(provider, model)` route's supported set;
  an unsupported level is **refused** naming the supported list and nearest level —
  never a silent downgrade.
- **`after` orders AND injects**: each direct parent's committed output lands under
  `## Inputs` (8 KB per parent). Use `inputs` for dotted paths or non-parent
  ancestors; an unresolvable path fails the node at spawn.
- **Leave budgets unset and name a `shape`** (fills `max_turns`/`timeout` from
  measured presets — [budgets](references/budgets.md)); shared settings go in
  graph-level `defaults`, once. A node `schema` writes the output contract for you.
- Human gates hold until `release`; `when` branches on upstream output,
  `on_skip:"prune"` kills the losing arm; machine gates park on a timer or argv
  probe at zero cost. `fanout` runs N children; an optional `quorum` commits at N
  and cancels stragglers (`cancelled`, never a failure).

### 3d. Failures, resume, amend

- Every `node.failed` carries `attempts` and `error_class` from the closed set in
  `wf.py`: `cancelled, cap_exhausted, crashed, early_death, fanout_empty,
  fatal_quota, forbidden_model, incomplete_work, inputs, precondition, quorum,
  route_unavailable, schema, spawn, timeout, transport, transport_exhausted,
  provider_400, unresolved_model, graph_invalid` (`unknown` is only a harvest-time
  default). Read the class, not the prose; failed nodes also carry `node_facts`
  (attempts log, final words, log/prompt paths) — answer from those before
  re-driving. Per-class semantics live once in operations.md.
- An explicit `model` pin is fail-closed by default (`require_route: true`): a
  submit ping proving the pin dead **refuses the launch** (`route_unavailable`)
  rather than silently billing another model; `require_route: false` opts into
  fallback. `(open PR #118)` `confidence_substrate`: an owner-declared ladder for
  proved-dead pins; substituted nodes must disclose the original pin.
- Unfinished work with no verified live runner reads `interrupted`: inspect
  committed outputs, then `wait` — finished nodes replay-skip by effective
  fingerprint (efp); only stale work and its downstream re-run. `amend` takes the
  **whole** replacement graph (`dry_run:true` previews `{added, removed, changed,
  will_rerun, unchanged}`); nodes with untouched definition and route keep their
  results (freeze law).
- A build lane that dies with work uncommitted is not lost:
  `python3 scripts/lane_recover.py --run <id> --node <node> [--out <dir>]` replays
  its journaled file writes from the profile database (read-only) into a restore dir.
- Report a finished run by the read model's counts (`tokens in/out`, `api_calls`,
  `tool_calls`); missing evidence reads `unknown`, never a false zero. Never lead
  with `estimated_cost_usd` — an estimate, not a bill.

## 4. Contribute

### 4a. Repo map

| Path | Owns |
|---|---|
| `__init__.py` | Tool entry point: schema, action dispatch, model resolution, preflight, payload shaping |
| `wf.py` · `wfcommon.py` | Runner (scheduling, spawn, retry gate, typed failures in `ERROR_CLASSES`, steer baking) · read model (state, fingerprints, node records, metrics, liveness) |
| `dashboard/` · `desktop/` | Dashboard routes (API-only) · desktop half (DAG canvas, fan-out stacks, timeline, gate hand-off, card) |
| `SKILL.md`, `references/` | Authoring skill + deep docs. Portable: no host names, private paths, or provider lore |
| `tests/` | Stdlib-only serial scripts (exit 0 = green) + `.mjs` under Node; `fake_hermes.py` is the child stand-in |
| `scripts/` | `suite.py` merge-gate runner + admission ledger — `(open PR #121)`: zero discovered cases is a failure, never green; `graph_check.py` graph drift; `make_public.py` private-string audit; `pack.py` release zip; `lane_recover.py` lane replay |
| `graphify-out/` | **Tracked** knowledge graph — CI drift-gates it (§4c) |
| `docs/` · `.github/` | Patched-core guide, catalog entry, scrub audit · the five CI gates, on every push/PR |

### 4b. Run the checks

One canonical entry — what CI itself runs:

```sh
python3 scripts/suite.py . ci-out
```

It runs every `tests/test_*.py` serially and every `tests/test_*.mjs` under
`node --experimental-strip-types`, writing `ci-out/exits.json` + per-test logs.
While iterating, run one targeted test (`python3 tests/test_engine.py`); the quick
desktop syntax gate is `node --check desktop/plugin.js`. The other three CI gates —
`hermes plugins validate .`, the `make_public.py` scrub audit, `graph_check.py` —
and the full block with expected verdicts are in [CONTRIBUTING.md](CONTRIBUTING.md);
contributor discipline in [references/development.md](references/development.md).

### 4c. Navigate with the knowledge graph

`graphify-out/` is a committed [graphify](https://github.com/Graphify-Labs/graphify)
graph of every function, class, test, and doc heading (deterministic tree-sitter
parsing; no LLM, no network). It is **tracked and CI drift-gated**
(`scripts/graph_check.py` fails if it diverges from the tree);
`graphify-out/GRAPH_REPORT.md` is the source of truth for its size — never restate
node/edge counts in docs. Install once (`uv tool install graphifyy`); query before
you grep: `graphify query "<question>"`, `graphify affected "<symbol>" --depth 2`
(every caller — review gate R8). After changing any `.py`/`.js`/`.md`:
`graphify update .` (~3 s) and commit the `graphify-out/` delta with your PR.

### 4d. Rules

1. **Touch only the files your task names;** forward-only commits, never rewrite history.
2. **Write-first:** commit the artifact before polishing; an uncommitted worktree at
   a wall death is lost work.
3. **Targeted tests while iterating; the full suite at merge.**
4. **No private strings in shipped files:** no hostnames, LAN addresses, machine
   vocabularies, or personal paths outside `plugin.yaml`/`docs/catalog`.
5. **SKILL.md stays portable and under 110 lines;** detail goes in `references/`.
   One source per fact — write a table or rule once, link it elsewhere.
6. **Desktop half stays on the SDK surface** (only `@hermes/plugin-sdk`, `react`,
   `react/jsx-runtime`; no `window.hermesDesktop`, core localStorage, core-UI DOM).
7. **Stdlib-only Python; host imports lazy and guarded.**
8. **Honest degradation:** an absent field reads `unknown`; never fabricate.

### 4e. Release

Bump `plugin.yaml` / `SKILL.md` / `references/grammar.md` / `CHANGELOG.md`, then run
the five gates, `python3 scripts/pack.py` (zip + `.sha256` into `artifacts/`), and
`git tag v<version> && git push --tags`. The catalog entry pins a full commit SHA
([docs/catalog/entry.yaml](docs/catalog/entry.yaml)); bump it in a PR to
`NousResearch/hermes-agent` → `plugin-catalog/hermes-workflows.yaml`.

## 5. Where things live at runtime

Run dirs: `<runs_root>/<run_id>/` (settings `workflows.runs_root` > `$WF_RUNS_ROOT`
> resolved Hermes home's `workflows/`; precedence law: operations.md), holding
`run.json`, `graph.json`, `events.jsonl`, `nodes/`, `logs/`, `steer/`, `gates/`.
Library: `<runs_root>/library/`. Turn report: `HERMES_QUIET_TURN_REPORT_FILE` (per
spawn); cap tier at `<run>/turn_report.tier`. Dashboard API:
`/api/plugins/hermes-workflows/runs`, `/runs/{id}`, `POST /runs/{id}/gate`.
