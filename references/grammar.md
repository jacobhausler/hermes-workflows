# Graph grammar and authoring boundaries

Workflow 1.1.1. Minimal form: `workflow{action:"run", graph:{"name":"check","nodes":[{"id":"a","type":"agent","goal":"Return a fenced JSON object with key ok=true"}]}}`. The run action's `name` parameter overrides `graph.name`; otherwise the graph name is used, then `workflow`. The tool entry point that validates and launches runs is referred to below as the plugin's launch path.

## Top-level keys (closed set)

Any key outside this set is refused at run/amend, reporting EVERY defect at once as `{node, field, msg}` errors — unknown keys are rejected, never silently ignored.

| key | shape | notes |
|---|---|---|
| `name` | string | run label; the run action's `name` parameter overrides it |
| `description` | string | purpose of the graph |
| `nodes` | list | see node types below |
| `defaults` | closed object | shared agent keys; see Defaults and precedence |
| `model_policy` | `{require_model: bool, forbidden_models: [str]}` | checked against effective routes; the owner-configured floor is unioned in, never relaxed out |
| `provenance` | `{owner, source, saved_at, source_digest}` | written by `save` only; attribution, not an access control |
| `grammar` | `"wf/1"` | dialect tag; absent = `wf/1`; a value this reader doesn't support is refused before any write or spawn, with the supported list |
| `include` | list of directives | expand shelved library graphs into the run (open PR #84); see Includes |

## Node types and keys (closed sets)

Node ids must match `^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$` — ids double as filenames.

| type | allowed keys |
|---|---|
| `agent` | `id`, `type`, `after`, `goal`, `context`, `schema`, `model`, `provider`, `toolsets`, `max_turns`, `timeout`, `run_budget`, `inputs`, `fanout`, `reasoning`, `tier`, `shape`, `repo`, `require_route`, `route_verified`, `profile`, `requires` |
| `gate` | `id`, `type`, `after`, `question`, `options`, `context`, `when`, `wait`, `on_skip`, `default_option`, `hold_timeout`, `requires` |
| `echo` | `id`, `type`, `after`, `output` |

Unknown keys — including `agent.when` (`when` is a gate-only predicate; agent predicates are rejected before write/spawn) — are refused, never ignored. `route_verified` is engine-baked only (see Route integrity): author-supplied values are always stripped.

## Agent key semantics

| key | semantics |
|---|---|
| `goal` | the child's task text; keep it outcome-shaped and idempotent — unfinished work may replay |
| `context` | extra preamble for this node; `defaults.context` is prepended once to every agent |
| `after` | ordering edges AND data injection: every direct parent's committed output lands under `## Inputs` automatically, capped 8000 bytes per parent with a truncation marker; a skipped dependency counts as satisfied |
| `inputs` | `"<ancestor>"` or `"<ancestor>.<dotted.path>"` to pick a field or a non-parent ancestor (12000-char cap per injected block); a parent named in both `after` and `inputs` appears once; a gate cannot declare `inputs` but its committed answer is readable downstream. An unresolvable reference FAILS the node at spawn (`error_class:"inputs"`) — never an empty spawn |
| `schema` | reply contract: JSON-schema keywords EXACTLY {`type`, `required`, `properties`, `items`, `description`} (anything stricter, like `enum`, cannot be enforced and is refused). The runner renders the contract into the child's prompt (4000-char cap) and extracts the last balanced JSON object from the reply — authors never write contract prose. A validation failure buys one free in-node redo, then `error_class:"schema"` |
| `model` | literal model id, a local alias, or an owner-configured tier name; resolved at run/amend and the literal BAKED into the node, so a later tier remap never retroacts. Unset = the seat default (this profile's default model), fan-out items included. `provider` is optional and requires a nonempty `model` |
| `reasoning` | `none`/`minimal`/`low`/`medium`/`high`/`xhigh`/`max`/`ultra`, validated against each RESOLVED route at launch; an unsupported value is refused naming that route's supported levels — never silently downgraded |
| `shape` | `recon`/`build`/`review`/`publish`: fills unset `max_turns`/`timeout` from measured p95 presets (default shape: `build`) — see [budgets](budgets.md) |
| `timeout` | node wall in seconds (default 900, cap 86400); extends ONCE if the child's log was active in the last 120s (event `node.extended`). `max_turns` caps at 200. Budget keys never participate in a node's effective fingerprint, so a budget edit can't un-freeze committed work |
| `run_budget` | the child's own seconds budget, separate from the node wall |
| `toolsets` | restricts which tool families the child may use |
| `repo` | declares the git lane the node owns (absolute or run-dir-relative). At commit the runner checks that lane's tracked changes: a done/partial answer over a lane with uncommitted TRACKED changes commits `failed` `error_class:"incomplete_work"` with the porcelain evidence, instead of handing off a fix nobody committed. Never an auto-commit; untracked files never dirty a lane; if git can't answer, the gate fails open |
| `fanout` | see Fan-out |
| `profile` | run the node AS a named local profile — see Team keys |
| `requires` | output preconditions — see Team keys |

## Route integrity (`require_route`, `route_verified`)

`require_route` (bool) defaults to TRUE on any node that pins an explicit model (explicit node key > `defaults` > the presence of `model` itself); left unset it is never baked into the node.

- A launch-time probe that affirmatively proves a pinned route dead — or answers from a fallback ladder (served route ≠ pinned route) — REFUSES the launch (`route_unavailable`) instead of silently billing another model. `require_route:false` is the deliberate opt-in to fallback.
- Missing evidence (probe can't answer; offline installation) stays warn-only: absence of evidence never blocks.
- A probe proving the pin alive bakes the engine-only `route_verified: "provider/model"` annotation. Author values for it are stripped at validation and dropped again at resolve — never trusted from an author, never forged through `save`. The runner then holds the child's served model to the proof; a contradiction commits `failed`/`route_unavailable`.
- `require_route` and `route_verified` never participate in a node's fingerprint (policy/annotation, not work), so an engine bake or a `defaults` flip cannot un-freeze committed nodes.
- A node death classed `fatal_quota` (a rate-limit refusal carrying its own reset horizon) fails on the first attempt — the retry ladder can't beat a multi-day reset — and relaunch on that model is refused until the horizon passes, with one recovery probe first.
- `confidence_substrate` (open PR #118) is an owner-configured fallback ladder, not a graph key: consulted only when the probe proves a pin dead; the first live rung serves, the node is annotated `substrate_substituted`, and the node's result schema gains a REQUIRED `substrate_disclosure` property naming the original pin. No config or all rungs dead = the plain `route_unavailable` refusal.

## Team keys

`profile` (agent only, optional): run that node AS a named local profile — DELEGATION, not isolation: the child runs with the target profile's instructions, memory, env, and tools, same OS user; no sandboxing is claimed or possible. Node-level only — fan-out items carry no profile of their own. `{run.KEY}` placeholders in `profile` are substituted before validation, so a graph can name its teammate per launch. Validation completes before any write/spawn: the name must be a non-empty profile directory with an existing config; `default` is never a target; the target's owner-written `workflow_team.json` must list the LAUNCHER's profile in its `accept_from` array. The launcher identity comes from the plugin's own config, never from a graph argument. A target deleted between validation and spawn is a typed `error_class:"spawn"` failure — never a silent fallback to the launcher.

`requires` (agent OR gate, optional): output preconditions on ancestors — `{"<ancestor>": ["field", "dotted.path", …]}`. Every key must be in the node's `after` closure and every path a non-empty string, or the graph is rejected before write/spawn. At schedule time each path resolves against the ancestor's committed output: a missing OR null value fails the node with `error_class:"precondition"` (`precondition unmet: <ancestor>.<path>`, `output.missing` lists the paths) with ZERO spawns, and the run fails on the normal failed path — a reader can never discharge an obligation on a null output. Retry ladders never see a precondition death; a resume re-evaluates it (supply the missing field via `amend` and the node spawns). A graph that WANTS skip-on-missing uses the `when` gate + `on_skip:"prune"` path. A node without `requires` facing a null upstream spawns exactly as before.

## Fan-out

`fanout` keys form a closed set: exactly `{items | items_from, goal, schema, quorum}` — anything else is rejected naming the allowed set. Exactly one of `items` (a literal list) or `items_from` (`"<node>.<dotted.path>"`).

- `goal` template is OPTIONAL when every item carries its own `goal`; otherwise the node goal prefixes each item prompt. `{item}` is the item value, `{index}` the zero-based number; dict item fields interpolate as `{item.field}`, and a dict item's nonempty `goal` overrides the template. Unreferenced item keys are not injected.
- `schema` constrains EACH item's reply (same reply-contract rules as the node `schema`).
- Up to 8 items run concurrently (per-item concurrency; node wave concurrency is 4).
- `quorum` (optional positive int) changes BOTH halves of the finish rule: with `quorum` SET, once N items commit, the stragglers are cancelled with `error_class:"cancelled"` and are EXCLUDED from the failure math — cancellation is never a failure. With `quorum` UNSET the node still WAITS for every item, but the commit threshold is the majority (`n // 2 + 1`): a single dead item does not sink a six-item audit; it lands in `failed_items` with partial credit.
- The committed output is `{items: […], failed_items, cancelled_items?, all_results}`. A downstream reducer with `inputs` can aggregate; no extra tool action or worker boilerplate is needed.

## Gates and branches

| key | semantics |
|---|---|
| `question` / `options` | the hold text and the answer choices; options are answer DATA — a "no" answer alone does not prune work |
| `hold_timeout` / `default_option` | seconds to hold before the runner self-releases with `default_option` (must be one of `options`; event `gate.auto_released`); with `hold_timeout` alone it logs `gate.expired` once and KEEPS holding |
| `wait` | machine-answered park at zero tokens: `{wait_s}` timer alone, and/or `{until_argv:["program","arg"], every_s:60, timeout_s:3600}` re-running a fixed argv (no shell) until exit 0 — its stdout/stderr tail becomes the gate's committed output, consumable via `inputs`. A wait timeout FAILS the gate — never an implied approval. A human `release` pre-empts a park |
| `when` | bounded predicate over `out.<node>.<dotted.path>`: `== != > >= < <=`, and/or/not, parentheses, string/number/True/False literals; parsed, never evaluated. Malformed at submit = refused; a runtime predicate error FAILS SAFE (holds the gate, event `gate.when_error`) — never a silent skip |
| `on_skip` | `'pass'` (default; arms still run) or `'prune'` (with `when`): the gate commits `skipped` and every node whose dependencies are ALL skipped skips too — terminal, not a failure; a join with one live dependency still runs |
| `requires` | same output preconditions as agents (see Team keys) |

A false `when` predicate defaults to prune. For mutually exclusive arms, use two complementary gate predicates, each with its agent arm, then a mixed join. A missing upstream input fails rather than injecting an empty value. There is no native vote/loop/foreach engine.

## Defaults and precedence

`defaults` is a closed object: `{schema, timeout, max_turns, reasoning, provider, model, context, require_route}`; it fills agent keys the author left unset. Precedence per key: explicit node value > node's named `shape` preset > graph `defaults` (the default-shape preset is the floor). `defaults.context` is a shared preamble prepended once to each agent's own context. A graph's `defaults` never cross an include boundary (open PR #84).

## Includes (open PR #84)

Top-level `include` is a graph-level COMPOSITE annotation: a list of `{as, use, seeds?, exports?}` directives that expand shelved library graphs INTO the run at launch (run/amend/save), before validation, defaults, and binding — so the runner, read model, fingerprint, and desktop never see includes; the committed graph is expanded and include-stripped, while `run.json` records the include names and digests.

- `as` = alias (alnum start, ≤24 chars, unique); included node ids become `alias__<inner-id>` (64-char cap, refused on overflow, never truncated).
- Every id reference inside an included graph is rewritten mechanically: `after`, `inputs` heads, `requires` keys, `fanout.items_from` (and its `after` entry, in lockstep), and `when` `out.<id>.` paths.
- `seeds:{KEY: string}` substitutes `{run.KEY}` inside that include's own subtree only; a surviving `{run.*}` is a fail-closed refusal.
- Guards, re-checked on the final fused graph: alias/id collisions, cross-include cycles, depth cap 4, 256 nodes, 1 MiB.
- A library save REFUSES a run whose record carries includes — save the author form inline instead.

## Staleness and replay

Every node definition carries an effective fingerprint (efp). Re-driving (wait/amend/respawn) replays any run whose stored efp matches the current graph: completed nodes replay-skip; stale definitions and their downstream re-run. Budget keys (`max_turns`, `timeout`, `run_budget`, `shape`) and policy keys (`require_route`, `route_verified`, `reasoning`, model-policy) are EXCLUDED from the efp, so those edits cannot invalidate committed work. An unknown fingerprint rule fails closed. An `amend` freeze law: nodes with an unchanged definition, untouched route, valid efp, and all-frozen ancestors keep their committed result verbatim and replay-skip.

## Top-level provenance

A graph may carry `provenance:{owner, source, saved_at, source_digest}` (closed keys). `save` writes it only when `source` is supplied (≤200 chars: repo path, URL, skill) or the saving profile is named; `source_digest` is a sha256 over the canonical `nodes` JSON. `library` rows and `run from:<name>` surface it when present. Provenance is attribution metadata, not an access control: nothing reads it to allow or deny.

## File-authored graphs

Use `graph_path` with run/save/amend for a caller-authorized absolute local regular UTF-8 JSON file, at most 1 MiB, no final symlink. Choose exactly one source: inline graph, `graph_path`, or run's `from` / save's `run_id`. Validation completes before writing or spawning. A shared file may state its dialect with top-level `grammar` (`"wf/1"`; absent = `wf/1`); an unsupported value is refused before any write or spawn, with the supported list. Like `provenance`, `grammar` is a top-level annotation — never part of a node — so node fingerprints and `source_digest` are unchanged by it. The publishing convention (`<name>.workflow.json`, provenance, pinned digests) is [portable](portable.md).
