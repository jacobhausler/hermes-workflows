---
name: workflow
description: "Workflow fan-out audit and census: run agent graphs"
version: 1.1.1
metadata:
  hermes:
    tags: [workflows, fan-out, audit, census, orchestration]
---

# Workflow authoring (1.1.1)

Use the `workflow` tool when a task needs independent lanes, a human gate, or a resumable graph; for one or two independent calls, use ordinary delegation instead. The authoring agent owns the graph and its side effects; the dashboard and the run strip under the composer are readers, not executors. Requires Hermes >= 0.21.4. Before disabling the plugin, list runs and stop each live run with `workflow{action:"stop",run_id:<id>}`.

## Smallest working graph

Graph `{ "name": "check", "nodes": [{"id": "inspect", "type": "agent", "goal": "Inspect the target. Return one fenced JSON object."}] }`. Submit `workflow{action:"run", graph:<object>}` — the reply carries `run_id`, the routing table, and a `card` line — then `workflow{action:"wait", run_id:<id>}` until the work reaches a boundary. `status` is read-only; every `status`/`wait` payload carries a derived `next`: `held` → release, `running`/`interrupted` → wait, `failed` → amend or stop.

## Graph shape

Top-level keys are a closed set; anything else is refused before write or spawn, with every defect reported at once:

| key | purpose |
|---|---|
| `name` / `description` | run label (the `run` action's `name` overrides) and purpose |
| `nodes` | `agent` / `gate` / `echo` nodes; ids match `^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$` |
| `defaults` | shared agent keys; closed set {schema, timeout, max_turns, reasoning, provider, model, context, require_route} |
| `model_policy` | {require_model, forbidden_models[]}; checked against effective routes; the owner-configured floor is always unioned in, never relaxed |
| `provenance` | {owner, source, saved_at, source_digest}; written by `save` — attribution, not an access control |
| `grammar` | dialect tag; only `wf/1`; absent = `wf/1`; unknown refused |
| `include` | expand shelved library graphs into the run at launch (open PR #84); committed graphs stay expanded and include-free |

## Nodes and data

- `after` orders nodes AND auto-injects each direct parent's committed output under `## Inputs` (8000-byte cap per parent, truncation marker on overflow); skipped deps count as satisfied.
- `inputs:["a", "a.dotted.path"]` picks a field or a non-parent ancestor (12000-char cap per block); an unresolvable reference FAILS the node at spawn — never an empty spawn.
- A `schema` is rendered into the child's prompt as the reply contract — authors never write contract prose in goals. Accepted keywords: exactly {type, required, properties, items, description}. A failed validation buys one free in-node redo, then `error_class:"schema"`.
- An `echo` node (`{id, type:"echo", after, output}`) commits `output` verbatim with no spawn: a constant never costs an agent.
- `repo:<path>` makes the node own a git lane: committing over uncommitted tracked changes fails `error_class:"incomplete_work"` instead of a false green.
- Keep work idempotent: unfinished work may replay on resume.

## Models and routing

An unset `model` uses the seat default (this profile's default model), fan-out items included — pin only where it matters. A pin is a request, not a guarantee; read the returned routing table before trusting execution. `provider` is optional and requires `model`; a `tier` name is resolved by the engine at launch and baked into the node as a literal, so a later remap never retroacts.

- `require_route` defaults to TRUE on nodes that pin a model (node key > `defaults` > the pin itself): a launch-time probe that proves the pin dead — or answers from a fallback — REFUSES the launch (`route_unavailable`) instead of silently billing another model. `require_route:false` is the deliberate opt-in to fallback. A pin proved alive is annotated `route_verified` (author-supplied values are always dropped) and the runner fails any node whose served model contradicts the proof.
- `confidence_substrate` (open PR #118; owner config, not a graph key): a ranked fallback ladder consulted only when the probe proves a pin dead; the first live rung serves, and the substituted node's result schema gains a required `substrate_disclosure` naming the original pin.
- `reasoning` levels are validated against each resolved route at launch — unsupported values are refused with that route's supported list, never silently downgraded.

## Fan-out

`fanout:{items | items_from:"a.items", goal, schema, quorum}` — closed set, exactly one of items/items_from. `goal` is optional when every item carries its own; `{item}`, `{index}`, `{item.field}` interpolate; a dict item's own `goal` overrides the template. The engine runs up to 8 items concurrently and up to 4 nodes per scheduling round.

Quorum rule: with `quorum` UNSET the node waits for every item but still commits at the majority (`n // 2 + 1`) with partial credit — one dead item never sinks six. With `quorum:N`, the first N commits cancel the stragglers as `error_class:"cancelled"`, excluded from the failure math — cancellation is never a failure.

## Gates and branching

A `gate` holds for a human answer: give it `question`/`options`, present it to the owner, answer via `release`. With `hold_timeout` + `default_option` a hold self-releases; with `hold_timeout` alone it logs the expiry and keeps holding. `gate.when` is a bounded predicate over `out.<node>.<path>` (comparisons, and/or/not, parentheses; parsed, never evaluated) — false prunes the gate and exclusively-dependent arms (default `on_skip:"prune"`; `"pass"` skips only the question). Predicate errors fail safe: the gate holds; nothing skips quietly. `when` belongs on gates only — `agent.when` and other unknown fields are rejected at validation. `gate.wait` is a zero-token machine park (timer and/or a fixed argv re-run until exit 0; the output becomes the gate's committed answer); a human `release` pre-empts it and a wait timeout fails the gate.

## Team keys

- `profile` (agent nodes only): run the node AS a named local profile — DELEGATION, not isolation: the child carries that profile's instructions, memory, env, and tools under the same OS user. Consent: the target's `workflow_team.json` must list the launcher in `accept_from`; `default` is never a target.
- `requires:{"<ancestor>":["field","a.b"]}` (agent or gate): a missing or null path in an ancestor's committed output fails the node at schedule time with `error_class:"precondition"` and ZERO spawns — the run fails loudly, never skips quietly. Want skip-on-missing? Use a `when` gate + `on_skip:"prune"`.

## Defaults, budgets, seeding

Precedence per key: explicit node value > named `shape` preset > graph `defaults` (default shape: build). `shape:recon|build|review|publish` fills `max_turns`/`timeout` from measured p95 presets — see [budgets](references/budgets.md); otherwise leave both unset. Node `timeout` defaults to 900s and extends ONCE while the child's log is still active; `run_budget` caps the child's own seconds.

`run_context` on `run`: a non-empty string seed appended to every first-wave agent, or a map replacing `{run.KEY}` in node goals/contexts, fan-out goals, and gate questions; malformed or JSON-stringified maps are refused before anything is written. Values land in prompts — never put secrets in them.

## Run and handoff

- `running` requires a verified live runner; `interrupted` means unfinished work without one — inspect surviving outputs, then `wait` resumes it explicitly. A `stopped` run is not a failure: cancelled work re-drives on resume. On `failed`, read the node facts (`node_facts`: error_class — a closed set; `cancelled` never counts as a failure; attempts; log path) before `amend` (submits the WHOLE replacement graph; `dry_run:true` previews) or `stop`.
- Put the `card` line alone on its own line in the reply that launches a run and in the one that reports it; the desktop strip under the composer shows this chat's runs regardless.
- Pollers that must not double-dispatch pass `lane_key` (a dedupe key: a second run while an incumbent on the same key is unfinished returns the incumbent and spawns nothing). Save proven graphs with `save`, replay with `run from:<name>`; `/wf <name> [note]` runs a library graph.
- `graph_path` reads a large graph from a caller-authorized absolute local JSON file (<= 1 MiB) instead of embedding it; choose exactly one of `graph`, `graph_path`, `from`.
- Report finished runs by tokens in/out, API calls, tool calls. The dollar figure is an estimate, never a bill — don't lead with it; missing spend reads unknown, never zero.

Full key semantics: [grammar](references/grammar.md). Read-model, states, recovery: [operations](references/operations.md). Contributor checks: [development](references/development.md).
