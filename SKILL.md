---
name: workflow
description: "Workflow fan-out audit and census: run agent graphs"
version: 1.3.1
metadata:
  hermes:
    tags: [workflows, fan-out, audit, census, orchestration]
---

# Workflow authoring (1.3.1)

Requires Hermes Agent v2026.9.21 or newer (package >=0.21.4). Use the `workflow`
tool for independent lanes, a human gate, or a resumable graph; for one or two
independent calls, delegate ordinarily. The authoring agent owns the graph and its
side effects; the dashboard is a reader, not an executor. A held Desktop gate
resumes the run owner's chat via the composer (older builds draft it instead).
Before disabling the plugin, stop every live run:
`workflow{action:"stop",run_id:<id>}`.

## Smallest working graph

`{ "name": "check", "nodes": [{"id":"inspect","type":"agent","goal":"Inspect the
specified target. Return one fenced JSON object."}] }`. Submit with
`workflow{action:"run", graph:<object>}`, then `wait` on the returned `run_id` until
a boundary. An `after` edge orders nodes AND injects each direct parent's committed
output into the child's `## Inputs` (8 KB per parent); a missing input fails at
spawn. `inputs:["a.key"]` picks a dotted path or non-parent ancestor;
`fanout.items_from:"a.items"` reads an upstream `items` array. A node `schema` makes
the runner write the reply contract itself — no contract prose in goals.
Independent tasks: separate nodes, or one `fanout` with `items`; `quorum` races —
once N succeed the rest cancel. Shared settings (schema, budgets, reasoning,
provider/model, preamble) go in a graph-level `defaults` once; leave node budgets
unset and name a `shape` (measured presets: [budgets](references/budgets.md)). A
constant travels as an `echo` node, never an agent spawn. `concurrency` /
`item_concurrency` are positive integers clamped to the owner's caps (4 / 8).
Full syntax: [grammar](references/grammar.md).

## Model routing

An unset `model` uses the seat default, including fan-outs — set it per node only
when needed. A tier, alias, or literal is a request, not an availability guarantee:
inspect the returned routing table and its errors before trusting execution; never
rewrite persistent model preferences to make a graph work. A pinned model is
fail-closed (`require_route`): a ping proving the pin dead — or answered from the
fallback ladder — REFUSES the launch (`route_unavailable`) instead of billing
another model; `require_route: false` opts into the ladder deliberately. A ping
proving the pin alive bakes the door-only `route_verified` proof (author values are
always dropped); the runner fails any node whose served model contradicts it.

## Gates and branching

A `gate` with `question` and `options` holds; present it to the owner, release with
their answer. `hold_timeout` + `default_option` releases a decorative gate itself;
`hold_timeout` alone logs `gate.expired` and keeps holding; machine waits use
`gate.wait`. A false `gate.when` prunes the gate and its exclusively dependent arm —
use two complementary predicates for mutually exclusive arms; `on_skip:"pass"` skips
only the question and is deliberate. `when` belongs on gates only. Branching
examples: `approve-publish`, `branch-on-verdict`.
Details: [grammar](references/grammar.md).

## Delegation, preconditions, partials

`profile` runs a node AS a named teammate profile: DELEGATION, not isolation — the
child carries that profile's SOUL, memory, `.env`, tools, same UID; its
owner-written `workflow_team.json` must list the launcher in `accept_from`;
`default` is never a target. `requires:{ancestor:["field",…]}` fails the node
`error_class:"precondition"` with zero spawns when an ancestor's committed output
lacks or nulls a path — the run FAILS, never skips quietly; skip-on-missing is
`when` + `on_skip:"prune"`. A `partial` (harvest-on-death) ancestor blocks plain
after-edges (`blocked_by_partial_ancestor`); the consumer opts in with
`after_partial: true`. Shelf `source:` provenance is attribution — never access
control. Details: [grammar](references/grammar.md).

## Run and handoff

- `running` needs a verified live runner; `interrupted` is unfinished work without
  one — inspect committed outputs, then `wait` to resume; held gates don't count as
  running. Payloads carry `next` — do what it says; it is derived, never a guess.
  On failure read `node_facts` first (`error_class` is a closed set; `cancelled` is
  never a failure); retryable deaths already got one machine re-drive. `amend`
  submits the WHOLE replacement graph; `run`/`amend` with `dry_run:true` preview
  with zero writes; `stop` is terminal. Details:
  [operations](references/operations.md).
- Shelf proven graphs with `save` + `tags` (reuse `library`'s `tag_vocab` verbatim;
  never coin tags). `save(run_id=...)` REFUSES a run whose `run.json` carries
  `includes` — save the AUTHOR graph instead, or one expansion gets frozen.
  Not library-worthy: `submit` with `why_not_library` (>=80 chars) quarantines for
  study. Don't save one-offs by default.
- Must not double-dispatch: `run` with `lane_key:<key>` — an UNFINISHED incumbent
  holds the key; a second run returns it, spawns nothing; `needs_resume` means
  `wait` it, never replace; `status` reads spawn-free. Keys are global per runs
  root; prefix `<team>/` yourself.
- Report finished runs by metrics (token in | out | api calls | tool calls), not
  dollars: `estimated_cost_usd` is a price-table estimate.
- The `card` line goes alone on its own line, in plain prose, never fenced or
  backticked (a fenced card renders dead) — once in the launching reply, once in
  the report. The composer strip shows this chat's runs regardless.
- `graph_path` (run/save/amend/validate) reads a caller-authorized absolute JSON
  file instead of an embedded graph — exactly one source. Sharing graphs as files:
  [portable](references/portable.md).
- Before launching an authored graph: `validate` dry-runs the door (defaults fill,
  defects, model/route policy), zero writes, no liveness ping.

Vocabulary and boundaries: [grammar](references/grammar.md); read-model/recovery:
[operations](references/operations.md); lanes and long runs:
[operator playbook](references/operator-playbook.md); contributor checks:
[development](references/development.md) (not ordinary-user setup).
