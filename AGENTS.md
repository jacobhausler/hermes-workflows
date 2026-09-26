# AGENTS.md — front door for agents

You are an agent. This file is written for you. It covers **installing** the plugin,
**operating** workflows once installed, and **contributing** to this repo. Each
section is self-contained; jump to the one that matches your task. Commands are
exact and copy-pasteable. Where a claim needs proof, the proof command is given.

---

## 1. What this is (30 seconds)

`hermes-workflows` is a [Hermes Agent](https://github.com/NousResearch/hermes-agent)
plugin. It registers one tool, `workflow`, that runs a **DAG of agent nodes** as a
background process owned by the calling session, plus a desktop DAG view.

- **Backend half** (`__init__.py`, `wf.py`, `wfcommon.py`, `dashboard/`): Python,
  stdlib-only, lives under `~/.hermes/plugins/hermes-workflows/` on the machine that
  runs `hermes serve`. Registers the `workflow` tool, the `workflow` skill, and
  read-only dashboard routes.
- **Desktop half** (`desktop/plugin.js`): plain ESM on the Hermes Desktop plugin SDK
  surface only. Lives under `~/.hermes/desktop-plugins/hermes-workflows/` on the
  machine that runs the **app**. When app and backend are the same machine, Hermes
  copies it for you; otherwise you copy it by hand.

Children are spawned as `hermes chat --query-file … -Q --max-turns N` — the stock
quiet one-shot CLI contract. **No patched Hermes is required.** See
[docs/patched-core.md](docs/patched-core.md) for the one optional field.

---

## 2. Install

### 2a. Catalog install (stock Hermes)

```sh
hermes plugins install hermes-workflows
hermes plugins enable hermes-workflows
hermes plugins validate ~/.hermes/plugins/hermes-workflows
```

Then restart the backend (`hermes serve`) — tools and dashboard routes mount only at
serve start. **Proof it loaded:** this line in the gateway's `~/.hermes/logs/gui.log`:

```
Mounted plugin API routes: /api/plugins/hermes-workflows/
```

A `401` on `/api/plugins/hermes-workflows/runs` is *not* proof — the auth layer
answers 401 for any path, mounted or not.

### 2b. Remote desktop app

If the app runs on a different machine than the backend:

```sh
mkdir -p ~/.hermes/desktop-plugins/hermes-workflows
cp desktop/plugin.js ~/.hermes/desktop-plugins/hermes-workflows/plugin.js
shasum -a 256 ~/.hermes/desktop-plugins/hermes-workflows/plugin.js   # compare to the repo's file
```

The app fs-watches that directory and hot-loads. If the WORKFLOWS tab is missing from
the SESSIONS | BOTS | WORKFLOWS strip: Settings → Plugins (toggle on), then ⌘K →
*Reload desktop plugins*.

### 2c. From a release zip

See [INSTALL.md](INSTALL.md) — verify the `.sha256` sidecar and `SHA256SUMS`, unpack,
copy the backend and desktop halves, validate, enable, restart.

### 2d. Optional: typed turn-cap deaths

Stock Hermes records a child that dies on its turn cap as `error_class: unknown`
(partial output and log preserved). Applying the one-field core patch in
[docs/patched-core.md](docs/patched-core.md) makes it `error_class: cap_exhausted` with the
loop's own reason. It is an operator choice; the plugin never patches your core. After
a failed child, `status` reports `turn_report: typed|untyped` so you can tell.

---

## 3. Operate

The bundled `workflow` skill ([SKILL.md](SKILL.md)) is loaded into any session that
has the plugin; it is the authoritative grammar. This section is the operating loop.

### 3a. The loop

```
workflow { "action": "run",    "graph": {…} }             → { run_id, routes, … }
workflow { "action": "wait",   "run_id": "<id>" }         → repeat until status ∈ {done, failed, stopped}
workflow { "action": "status", "run_id": "<id>" }         → read-only; never spawns
workflow { "action": "release","run_id": "<id>", "gate_id": "<gate>", "answer": "…" }
workflow { "action": "stop",   "run_id": "<id>" }         → terminal, not rollback
```

`wait` blocks while a verified runner is live and self-yields ~330 s with a
"call wait again" note to stay under the harness tool deadline. **Stay in the loop.**
Ending your turn after `run` is the single most common way a workflow stalls.

### 3b. Minimal graph

```json
{ "name": "check",
  "nodes": [
    { "id": "inspect", "type": "agent",
      "goal": "Inspect <target>. Return one fenced JSON object {ok, findings}.",
      "model": "<model-id>", "provider": "<provider-name>", "reasoning": "medium",
      "max_turns": 20, "timeout": 900 }
  ] }
```

Or, the 1.0.1 way — settings once, nodes carry only their work:

```json
{ "name": "check",
  "defaults": { "model": "<model-id>", "provider": "<provider-name>", "reasoning": "medium",
                "schema": { "type": "object", "required": ["ok"] } },
  "nodes": [
    { "id": "inspect", "type": "agent", "shape": "recon", "goal": "Inspect <target>." },
    { "id": "verdict", "type": "agent", "after": ["inspect"], "goal": "Judge the inspection." }
  ] }
```

Rules that bite:

- **Pin `model` + `provider` on every node** unless you have verified the seat
  default is the route you want. An unset model rides the seat default — including
  fan-out children — and a usage-capped or wrong-provider default surfaces as
  `provider_400`/`429` on every child.
- **`reasoning` is passed verbatim** to `hermes chat --reasoning`. Hermes clamps it to
  what the route supports (`agent/reasoning_effort.py`); a level the *relay* itself
  rejects (some local servers accept only `low|medium|xhigh`) comes back as
  `provider_400` with the server's message — read it and pick from that list.
- **`after` orders AND injects.** Every direct parent's committed output lands under
  `## Inputs` automatically (8 KB per parent). Use `inputs:["a.key"]` only to pick a
  dotted path or a non-parent ancestor, or `fanout.items_from:"a.items"`. A missing
  path fails at spawn.
- **Shared settings go in `defaults`, once.** `defaults:{schema, timeout, max_turns,
  reasoning, provider, model, context}` at graph level; `shape:recon|build|review|publish`
  sizes budgets from measured presets. A `schema` makes the runner write the reply
  contract itself — no contract prose in goals.
- **Leave budgets unset and name a `shape`; see [references/budgets.md](references/budgets.md).**

### 3c. Fan-out, gates, branches

```json
{ "id": "lanes", "type": "agent",
  "fanout": { "items": ["alpha", "beta"], "goal": "Audit {item}. Write <path>/{item}.md first.", "quorum": 1 } }

{ "id": "approve", "type": "gate", "after": ["lanes"],
  "question": "Ship the report?", "options": ["ship", "hold"] }

{ "id": "go",   "type": "gate", "after": ["judge"], "when": "out.judge.verdict == 'ship'", "on_skip": "prune" }
{ "id": "hold", "type": "gate", "after": ["judge"], "when": "out.judge.verdict != 'ship'", "on_skip": "prune" }
```

A human gate holds until `release`; the desktop view shows the question and hands
the answer back to the owning session. `hold_timeout` + `default_option` makes a
decorative gate release itself (`gate.auto_released`); `hold_timeout` alone logs
`gate.expired` once and keeps holding. Fan-out `quorum` (optional) races: once N
succeed, the rest are cancelled; without it the fan-out waits for every item;
`goal` is optional when items carry their own. Machine gates: `wait:{"wait_s":N}` or
`wait:{"until_argv":[…],"every_s":60,"timeout_s":3600}`. Tested examples:
[examples/approve-publish.json](examples/approve-publish.json),
[examples/branch-on-verdict.json](examples/branch-on-verdict.json).

### 3d. Failures, resume, amend

- `node.failed` events carry `error_class` from a closed set — `timeout | cap_exhausted |
  early_death | provider_400 | unresolved_model | transport | transport_exhausted | schema |
  crashed | spawn | graph_invalid | cancelled | inputs | quorum | fanout_empty | unknown` —
  plus `attempts`. Read the class, not the prose. `cancelled` (a `stop`, or a fan-out
  straggler at quorum) is never a failure: the run reads `stopped`, and a `wait` re-drives it.
- A child that dies after printing a valid fenced answer (rc≠0, wall, cap) is committed as
  `status: partial` with the death cause kept as `error_class`; downstream runs on it.
- `transport | early_death | cap_exhausted | timeout` deaths with tool progress get ONE
  automatic re-drive with a machine resume preamble (`node.retry`); permfails never retry.
- A child silent for 120 s after spawn is killed as `early_death`; a child still writing its
  log when the wall fires gets one 50 % extension (`node.extended`), then dies.
- A run with unfinished work and no live runner is `interrupted`. Inspect committed
  outputs, then `wait` to resume — finished nodes replay-skip by fingerprint.
- To change the graph mid-flight: `amend` with the **whole** replacement graph.
  `dry_run:true` previews `{added, removed, changed, will_rerun, unchanged}`.
  Amending a `pending` node changes what spawns next; amending a `done` node
  invalidates it.
- To resume a lane that died at its wall with work already banked: amend its `goal`
  to a *resume* prompt that names what is already committed and forbids redoing it.
  Cold re-runs of a timed-out research lane time out again.
- Steering: `steer` queues text; a running child pulls it via `inbox` at its next
  seam. It does not interrupt a child mid-turn.

### 3e. Reporting a finished run

Quote the read model's vanity numbers: `tokens in ▸ out | api_calls | tool_calls`,
per node and run total (they are in every `status`/`wait` payload). Do not lead with
`estimated_cost_usd` — it is a price-table estimate and reads as spend on
subscription routes.

---

## 4. Contribute

### 4a. Map

| Path | Owns |
|---|---|
| `__init__.py` | The tool door: schema, action dispatch (`run/status/wait/release/steer/inbox/amend/stop/list/save/library`), model-tier resolution, preflight, compact/full payload shaping |
| `wf.py` | The background runner: scheduling, child spawn (`-Q` contract), retry gate, typed error classification, steer baking, tier stamping |
| `wfcommon.py` | The read model: run state, fingerprints (`efp`), node records, metrics join, liveness. Read-only over a run directory |
| `dashboard/plugin_api.py` | Dashboard routes (API-only; the manifest hides the tab) |
| `desktop/plugin.js` | Desktop half: runs list, DAG canvas, fan-out stacks, timeline, gate hand-off, `::workflow` card |
| `SKILL.md`, `references/` | The authoring skill loaded into sessions. Portable: no host names, install paths, or provider lore |
| `tests/` | Stdlib-only serial scripts; each prints `PASS`/`FAIL` lines, exit 0 = green. `.mjs` under Node. `tests/fake_hermes.py` is the child stand-in (`FAKE_MODE=…`) |
| `scripts/suite.py` | Serial runner with per-test logs + `exits.json` ledger (the merge gate) |
| `scripts/pack.py` | Release zip + `SHA256SUMS` + sidecar |
| `scripts/make_public.py` | Publish-tree exporter with a private-string audit gate (`scripts/.scrub-guards` allow-list) |
| `docs/` | Patched-core guide, manifest decisions, catalog entry + PR body, scrub audit |

### 4b. Run the checks

```sh
python3 tests/test_engine.py                      # one targeted suite while iterating
python3 tests/test_skill_docs.py                  # the portable-skill contract
node --check desktop/plugin.js                    # desktop half parses
node --experimental-strip-types tests/test_edge_routing.mjs
python3 scripts/suite.py . ci-out                 # full serial suite → ci-out/exits.json (merge gate)
hermes plugins validate .                         # manifest + SDK-surface + security scan
python3 scripts/make_public.py /tmp/public-tree   # private-string audit; must print "0 scrub hits"
python3 scripts/graph_check.py                    # committed knowledge graph matches the tree
```

A change is done when: its targeted test is green, the full suite is green, validate
prints `Validation passed.`, the scrub audit prints `0 scrub hits`, and the graph gate
prints `OK`. CI runs the same five gates ([.github/workflows/ci.yml](.github/workflows/ci.yml)).

### 4b′. Navigate with the knowledge graph

The repo ships a [graphify](https://github.com/Graphify-Labs/graphify) knowledge
graph at `graphify-out/` — 924 nodes / 1840 edges over every function, class, test
and doc heading, built by deterministic tree-sitter parsing (no LLM, no network).
Query it before you grep or open files one by one:

```sh
uv tool install graphifyy                                      # once; the CLI is `graphify`
graphify query "how does a failed node get its error_class"    # scoped subgraph for a question
graphify path "act_run" "run_child" --undirected               # how two symbols connect
graphify explain "run_state"                                   # one symbol + every neighbour
graphify god-nodes --top 12                                    # the hubs everything flows through
```

`graphify-out/GRAPH_REPORT.md` is the broad-architecture view (community hubs,
surprising cross-file links). Every edge is tagged `EXTRACTED` (read from source) or
`INFERRED` (resolved by graphify) so you know what was found vs guessed.

Keeping it current:

| you did | run |
|---|---|
| changed any `.py`/`.js`/`.md` | `graphify update .` (AST only, ~3 s) and commit `graphify-out/{graph.json,GRAPH_REPORT.md,manifest.json}` |
| want to check without rewriting | `python3 scripts/graph_check.py` (`--fix` rewrites) |
| added/renamed whole subsystems | `graphify label . --missing-only` names new communities — the ONLY LLM step; any OpenAI-compatible endpoint works (`OPENAI_BASE_URL`, `OPENAI_MODEL`, `GRAPHIFY_MAX_OUTPUT_TOKENS=16000` for thinking models). Never run in CI |

Committed: `graph.json`, `GRAPH_REPORT.md`, `manifest.json`, `.graphify_labels.json(.sig)`,
`.graphify_analysis.json`, `.graphify_root`. Ignored: `graph.html`, `cache/`, `cost.json`,
dated backups. `.graphifyignore` excludes `graphify-out/` and `.github/` from the corpus.

### 4c. Rules

1. **Lane-scoped edits.** Touch only the files your task names. Never amend or rebase
   shared history — forward-only commits.
2. **Write-first.** Commit the artifact before polishing it. An uncommitted worktree
   at a wall death is lost work.
3. **Targeted tests while iterating; the full suite at merge.** Lanes that run the
   whole suite time out.
4. **No private strings in shipped files.** No hostnames, LAN addresses, machine
   vocabularies, real names outside `plugin.yaml`/`docs/catalog`. The scrub audit is
   the gate; add a guard line to `scripts/.scrub-guards` only with a reason.
5. **SKILL.md stays portable and under 110 lines.** Foreign agents on foreign hosts
   load it. Deep detail goes in `references/`.
6. **Desktop half stays on the SDK surface.** Imports only `@hermes/plugin-sdk`,
   `react`, `react/jsx-runtime`; no `window.hermesDesktop`, no core localStorage
   keys, no DOM edits of core UI. `hermes plugins validate` checks the automated
   subset; a human reviewer checks the rest.
7. **Stdlib-only Python; host imports lazy and guarded.** A local-backend Mac runs
   the plugin under system Python with neither `hermes_cli` nor PyYAML on path.
8. **Honest degradation over hidden failure.** If a field is absent (untyped turn
   report, missing metrics row), say `unknown`; never fabricate a value.

### 4d. Release

```sh
# bump plugin.yaml / SKILL.md / references/grammar.md / CHANGELOG.md to the new version
python3 scripts/suite.py . ci-out && hermes plugins validate . && python3 scripts/make_public.py /tmp/pub
python3 scripts/pack.py                            # artifacts/hermes-workflows-<v>.zip + .sha256
git tag v<version> && git push --tags
```

The catalog entry pins a full 40-char commit SHA
([docs/catalog/entry.yaml](docs/catalog/entry.yaml)); bump it in a PR to
`NousResearch/hermes-agent` → `plugin-catalog/hermes-workflows.yaml`.

---

## 5. Where things live at runtime

| What | Where |
|---|---|
| Run directories | `$HERMES_HOME/workflows/<run_id>/` — `graph.json`, `run.json`, `events.jsonl`, `nodes/<id>.json`, `logs/<id>.a<n>.log`, `steer/`, `gates/` |
| Library | `$HERMES_HOME/workflows/library/` |
| Child turn report | `HERMES_QUIET_TURN_REPORT_FILE` (per spawn, read then unlinked) |
| Tier stamp | `<run>/turn_report.tier` (`typed` / `untyped`, write-once) |
| Dashboard API | `/api/plugins/hermes-workflows/runs`, `/runs/{id}`, `POST /runs/{id}/gate` |
| Desktop plugin | `~/.hermes/desktop-plugins/hermes-workflows/plugin.js` on the **app** machine |
