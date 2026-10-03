# Hermes Workflows

**Agent-owned workflow graphs for [Hermes Agent](https://github.com/NousResearch/hermes-agent).**
Your agent authors a JSON graph of agent nodes, fan-outs and gates; a background
runner executes it, survives crashes and restarts, and hands results back through
the same `workflow` tool it launched from. Hermes Desktop draws the live DAG.

![A nine-node review fleet: four parallel recon lanes, a synthesis node, two adversarial critics, a human gate, and a final sign-off — with the per-node timeline on the right](assets/dag-review.png)

## Why this exists

A single agent turn is one long, fragile thread of work: one context, one
timeout, no resumable checkpoints. A **graph** splits the job into nodes with
explicit dependencies — parallel recon lanes, a synthesis join, an adversarial
review gate — each node a separate child session with its own model, budget, and
typed failure. When something dies or you change your mind mid-flight, only the
affected nodes re-run: completed work is replayed from its fingerprint, not re-paid.

## What you get

| Capability | In one line |
|---|---|
| **Graph runs** | Agent nodes with `goal`, `after` edges, per-node `model`/`provider`/`reasoning`, and `max_turns`/`timeout`/`run_budget` caps |
| **Fan-out** | One node → N live children from `fanout.items` or `items_from:"<node>.items"`; per-item liveness; optional `quorum` cancels stragglers once N succeed |
| **Human + machine gates** | A `gate` holds on a question until `release`; `gate.wait` holds on a timer or an argv probe at zero token cost; `when` predicates branch on upstream output; `on_skip:"prune"` retires the losing arm |
| **Composite graphs** | A graph-level `include` expands shelved library graphs into a run at launch, namespace-isolated and capacity-guarded (open PR #84) |
| **Fingerprint resume** | Every finished node records an effective fingerprint. Crash, restart, or `amend` the graph mid-flight — only what actually changed re-runs |
| **Cooperative steer** | `steer` queues text for a running node; the child pulls it at its next natural seam via the tool's `inbox` action — prompts are never rewritten mid-flight |
| **Profile delegation** | A node can run *as* another local Hermes profile (its instructions, memory, tools) behind a per-profile consent file — multi-personality graphs on one machine |
| **Typed failures** | Every `node.failed` carries `error_class` + `attempts` from a closed set (`timeout`, `cap_exhausted`, `provider_400`, `schema`, `cancelled`, `route_unavailable`, …) — you never infer a cause from prose |
| **Route integrity** | A node that pins a `model` is fail-closed (`require_route`, on by default): a proven-dead pin refuses to launch rather than silently bill another model; an alive-proved pin is stamped and the runner holds the served model to it |
| **Fallback ladder** | With an owner-configured `confidence_substrate`, a proven-dead pin falls to the next live rung, and the substitution is stamped into the node's result contract — never silent (open PR #118) |
| **Compact status** | Mid-run `status`/`wait` return output *pointers* and per-node metrics; `detail:"full"` opts into everything |
| **Wedged-lock recovery** | A dead runner's lock is cleared by an audited escape hatch that proves death first and never deletes a live lock (open PR #47) |
| **Desktop DAG view** | Live graph, fan-out stacks, timeline, and a `::workflow{id="…"}` inline card in any reply; a session strip under the composer shows this chat's runs (core ≥ v2026.7.30; older shells get the fallback slot) |
| **Library** | `save` a proven graph, `library` lists it, `run from:"<name>"` replays it byte-for-byte |
| **Authoring skill** | Bundled `workflow` skill: grammar, operations, and **measured** per-shape budget presets (`recon`/`build`/`review`/`publish`) |

<table><tr>
<td width="50%"><img src="assets/fanout.png" alt="A fan-out node showing 2/2 items terminal, stacked behind the card, feeding a join node"><br><sub><b>Fan-out.</b> One node, two live children; items stack behind the card and the join reads both outputs.</sub></td>
<td width="50%"><img src="assets/branch-gate.png" alt="A judge node feeding two complementary machine gates; each gate opens its own arm"><br><sub><b>Branch on verdict.</b> Two complementary <code>when</code> gates on one judge; each arm runs only when its gate opens.</sub></td>
</tr></table>

## The `workflow` tool

One tool, action-routed — the complete surface, with the flags that matter:

| Action | What it does |
|---|---|
| `run` | Launch a graph from `graph` (inline), `graph_path` (≤1 MiB file), or `from` (library name). Optional `name`, `run_context` (seed string or `{run.KEY}` binding map), `team`, `lane_key` (dedupe: a concurrent run with an unfinished incumbent returns it instead of spawning). |
| `status` | Read-only read model: per-node state, metrics, held gate, derived `next` steps. Never spawns a runner. |
| `wait` | The resume-and-watch verb: the only read action that respawns an idle runner; blocks to the next boundary, self-yielding before the host's tool deadline. |
| `release` | Answer a held human gate (`gate_id`, `answer`); respawns the runner when idle. A human release pre-empts a machine park. |
| `steer` | Queue steering text for a running node (refused on gates and terminal nodes; delivery is cooperative via the child's `inbox` pull). |
| `inbox` | Child-side pull of steering lines baked for this spawn — exactly-once per spawn, called by the workflow child itself. |
| `amend` | Replace the graph mid-run (`dry_run:true` previews `will_rerun` without writing). Unchanged, fingerprint-valid nodes replay-skip. |
| `stop` | Request a stop at the next boundary; in-flight children are killed; stop ≠ failure — cancelled work re-drives on resume. |
| `list` | All runs (capped page + full-census counts); `lane_key` reads the incumbent run. |
| `save` | Shelve a graph in the library under a name (overwrite = current best); optional `source` attribution writes provenance (owner, digest, timestamp). |
| `library` | List shelved graphs with node/gate/fan-out counts and provenance. |
| `release_lock` | *(open PR #47)* Release a wedged `runner.lock` after proving the holder dead (also `python3 wf.py release-lock <run_id>`). Refuses contested, gate-held, or alive cases; never unlinks a lock. |

Plus a `/wf` slash command: bare `/wf` lists the library; `/wf <name> [note]`
launches that graph with the note as its context seed.

## Graph grammar in 30 seconds

Three node types — `agent`, `gate`, `echo` — and a closed key set per type
(anything outside it is refused at submit with a per-defect error list, never
silently ignored). The smallest useful graph:

```json
{ "name": "check",
  "nodes": [{ "id": "inspect", "type": "agent",
              "goal": "Inspect the target. Return one fenced JSON object." }] }
```

```
workflow { "action": "run",  "graph": <the object above> }   → run_id
workflow { "action": "wait", "run_id": "<run_id>" }          → repeat until terminal
```

Fan-out with `quorum`, gates with `when`/`on_skip`/`wait`, `requires`
preconditions, `inputs` selection from upstream output, graph-level `defaults`
and `model_policy` — the authoritative vocabulary is
[references/grammar.md](references/grammar.md); the bundled authoring skill keeps
a compressed working copy in [SKILL.md](SKILL.md). Runnable examples live in
[examples/](examples/): a provider smoke graph, approve-then-publish with
complementary gates, branch-on-verdict, and a portable-file walk-in.

## What a run leaves behind

Each run is a directory (`~/.hermes/workflows/<run-id>/` by default): the
committed `graph.json`, an append-only `events.jsonl` typed event log, per-node
results under `nodes/`, prompts and logs under `logs/`, gate answers under
`gates/`, and a `summary.md`. Resume, `amend`, and the desktop all read the same
shared state. There is no hidden control plane and no daemon: exactly one runner
process per run, admitted by a kernel lock, spawned by the tool call that
launched it. Run states, liveness semantics (including `interrupted` — a runner
not verified alive with unfinished work — and `liveness-unknown` where a probe
cannot answer, open PR #47), and recovery procedures:
[references/operations.md](references/operations.md).

## Install

```sh
hermes plugins install hermes-workflows      # from the catalog (pinned SHA)
hermes plugins enable hermes-workflows
```

Restart the backend (`hermes serve`) so the tool and dashboard routes mount.
Before disabling or removing the plugin, stop live runs: use `workflow {"action":"list"}`
to find their run IDs, then `workflow {"action":"stop","run_id":"<id>"}` for each.
Detached runners can outlive a session, gateway restart, or plugin disable until a
boundary; disabling alone does not stop them. Desktop gate answers use the SDK to
send a visible resume turn to the run owner's chat; older Desktop builds insert
text for you to send, or ask you to type `workflow wait` in that owner chat.
If Hermes Desktop runs on a **different machine** than the backend, copy
`desktop/plugin.js` to that machine's `~/.hermes/desktop-plugins/hermes-workflows/plugin.js`
— the app hot-loads it. Manual/zip install and removal: [INSTALL.md](INSTALL.md).

## Two builds, one codebase

The plugin needs **no patched Hermes**. Every child spawn rides the stock quiet
one-shot CLI contract, and every install runs the same code. Exactly one field
differs, and it is optional:

|  | stock Hermes (catalog install) | with the optional core patch |
|---|---|---|
| graphs, fan-out, gates, steer, resume, desktop view, cards | ✓ | ✓ |
| a child that dies on its `max_turns` cap | `error_class: unknown` + preserved partial/log | typed `error_class: cap_exhausted` + reason |
| how | nothing to do | one sha-stamped patch — [docs/patched-core.md](docs/patched-core.md) |

The tier is self-reported: after a failed child, `status` shows
`turn_report: typed` or `untyped`, so you always know which build you're on.
When upstream [PR #121041](https://github.com/NousResearch/hermes-agent/pull/121041)
lands, the branch collapses and that doc deletes itself.

## Requirements

- Hermes Agent **≥ v2026.9.21 (package version 0.21.4)** — measured stock `-Q`
  CLI and quiet turn-report contract; see [docs/catalog/pr-body.md](docs/catalog/pr-body.md).
  Older 0.21.3 deployments are below this declared floor and will skip plugin admission.
- Python 3 (stdlib only — the plugin imports nothing outside Hermes)
- Node for the desktop half's tests only; the app loads `plugin.js` uncompiled

## For agents and contributors

[AGENTS.md](AGENTS.md) is the front door: repo map, operate/contribute
procedures, and the rules that keep the tree publishable. Changes are gated by
the serial suite (`python3 scripts/suite.py . ci-out`) and
`hermes plugins validate .` — both run in [CI](.github/workflows/ci.yml).

The repo ships a [graphify](https://github.com/Graphify-Labs/graphify) knowledge
graph (`graphify-out/`, deterministic AST extraction — no LLM in the build; the
committed graph is drift-gated by CI). `graphify query "<question>"` returns a
scoped subgraph instead of a grep dump; `graphify-out/GRAPH_REPORT.md` is the
architecture overview and the current node/edge census.

## License

MIT — see [LICENSE](LICENSE).
