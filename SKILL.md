---
name: workflow
description: "Workflow fan-out audit and census: run agent graphs"
version: 1.0.2
metadata:
  hermes:
    tags: [workflows, fan-out, audit, census, orchestration]
---

# Workflow authoring (1.0.2)

Use the `workflow` tool when a task needs independent lanes, a human gate, or a resumable graph. For one or two independent calls, use ordinary delegation instead. The authoring agent owns the graph and its side effects; the dashboard is a reader, not an executor.

## Smallest working graph

Build `{ "name": "check", "nodes": [{"id":"inspect","type":"agent","goal":"Inspect the specified target. Return one fenced JSON object."}] }`. Submit with `workflow{action:"run", graph:<object>}`, then use its returned `run_id` with `workflow{action:"wait", run_id:<id>}` until a boundary. An `after` edge orders nodes AND hands each direct parent's committed output to the child under `## Inputs` (8 KB per parent). Use `inputs:["inspect.key"]` only to pick a dotted path or a non-parent ancestor, or `fanout.items_from:"inspect.items"` where the upstream output has an `items` array. A missing input fails at spawn. Give a node a `schema` and the runner writes the reply contract into the prompt itself — no contract prose in goals.

Independent tasks: put them in separate nodes or one `fanout` with `items` (per-item `goal` optional; the node goal prefixes each item). `quorum` (optional) races: once N succeed, the rest are cancelled. Put shared settings — schema, budgets, reasoning, provider/model, a context preamble — in a graph-level `defaults` block once, not on every node; `shape:recon|build|review|publish` sizes budgets from measured presets. A constant travels as an `echo` node, never an agent spawn. Set `model` per node only when needed: an unset model uses the seat default, including fan-outs. A configured tier, alias, or literal is a request, not a guarantee of provider availability. Inspect the returned routing table and check errors before trusting execution. Use an explicit `provider` with a nonempty `model` when routing is needed; do not change persistent model preferences just to make a graph work.

For a decision, a `gate` with `question` and `options` holds; present it to the owner and pass their answer with `release`. A decorative gate gets `hold_timeout` + `default_option` and releases itself; with `hold_timeout` alone it logs `gate.expired` and keeps holding. Machine waits use `gate.wait`. A false `gate.when` without `on_skip:"prune"` skips the QUESTION but still lets the arm run. For mutually exclusive arms, use two complementary gate predicates with `on_skip:"prune"`; see [grammar](references/grammar.md). `when` belongs on gates: agent predicates and other unknown fields are rejected before write/spawn. The tested `approve-publish` and `branch-on-verdict` examples demonstrate branching.

## Run and handoff

- `running` requires a verified live runner. `interrupted` means unfinished work without one; inspect surviving outputs before explicitly resuming with `wait`. Fatal recorded runner errors are `failed`, not automatic respawn loops. Held gates are not counted as running. `status` explains current nodes and every `status`/`wait` payload carries `next` — do what `next` says; `wait` again until it is empty. `next` is derived, never a guess. On a failed run, read the failed node's facts (`node_facts`: error_class — closed set; `cancelled` is never a failure; attempts, final words, log path — `partial` is a harvested answer downstream can use; retryable deaths already got one machine re-drive) and committed outputs before `amend` or stop. `amend` submits the WHOLE replacement graph; `dry_run:true` previews invalidation. `stop` is terminal. Details: [operations](references/operations.md).
- To save a reusable proven graph: `workflow{action:"save", run_id:<id>, name:<name>, description:<trigger>}`. `library` lists it; `run` with `from:<name>` replays it. Do not save one-off graphs by default.
- Report a finished run by its vanity numbers from the read model's metrics: token in | token out | api calls | tool calls (per node and run total). Don't lead with the dollar figure: it is core's `estimated_cost_usd`, a price-table estimate (subscription routes report `included`, not `actual`), and it freaks humans out when quoted as spend.
- Put the `card` line alone on its own line in the reply that launches a run and in the one that reports it; the desktop shows every run of this chat above the composer regardless.
- Use `graph_path` on run/save/amend for a caller-authorized absolute local JSON file instead of embedding a large graph. Choose exactly one graph source. See [grammar](references/grammar.md).
- Leave node budgets unset and name a `shape`; see [budgets](references/budgets.md).

The graph vocabulary, boundaries and examples live in [grammar](references/grammar.md); read-model/recovery in [operations](references/operations.md). [Development checks](references/development.md) are for contributors, not ordinary-user prerequisites.
