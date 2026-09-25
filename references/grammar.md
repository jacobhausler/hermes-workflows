# Graph grammar and authoring boundaries

Workflow 0.9.0. Minimal form: `workflow{action:"run", graph:{"name":"check","nodes":[{"id":"a","type":"agent","goal":"Return a fenced JSON object with key ok=true"}]}}`. The run action's `name` overrides `graph.name`; otherwise the graph name is used, then `workflow`.

## Nodes and data

Agent fields: `id`, `type:"agent"`, `goal`, `after:[ids]`, `context`, `schema`, `inputs`, `model`, optional `provider` paired with a nonempty model, `reasoning`, `toolsets`, `max_turns`, `timeout`, `run_budget`, `fanout`. Unknown keys (including `agent.when`) are rejected before write/spawn. The node's `schema` constrains fenced JSON and the child gets a correction retry. Keep work idempotent: unfinished work may replay. An explicit provider routes via the child `--provider` flag; unset model uses the seat default even for fan-out.

`after` schedules only. `inputs:["a", "a.key"]` injects committed ancestor output, failing loudly on missing paths. A gate cannot declare `inputs`, but a downstream agent can read its committed output. Fan-out uses `fanout:{"items":[...],"goal":"Audit {item}"}` or `items_from:"a.items"`. `{item}` is the item value; `{index}` is the zero-based item number. Dict item fields may be interpolated, and a dict item's nonempty `goal` overrides the template. Unreferenced keys are not injected. `quorum` is optional minimum success count, default all. A reducer with `inputs` can aggregate; optional schema-defined feedback arrays need no new workflow action or mandatory worker boilerplate.

## Gates and branches

A gate has `type:"gate"`, `after`, optional `question`/`options`, `when` and `on_skip`. Human gates hold until release. `wait:{"wait_s":N}` is a timer; `wait:{"until_argv":["program","arg"],"every_s":60,"timeout_s":3600}` rechecks fixed argv without a shell. A machine timeout is failure, not approval. Gate options are answer DATA; a "no" response alone does not prune work.

Bounded `when` reads `out.<ancestor>.<path>`, with string/number/boolean literals (`true`, `false`, `True`, `False`), comparisons, and/or/not and parentheses. A false predicate with default `on_skip:"pass"` skips the gate question but lets descendants proceed. `on_skip:"prune"` makes the gate and descendants with only skipped dependencies terminal-skipped. For mutually exclusive arms, use two complementary gates with `on_skip:"prune"`, each with its agent, then a mixed join. See tested `examples/approve-publish.json` and `examples/branch-on-verdict.json`. A missing upstream input fails rather than injecting an empty value. There is no native vote/loop/foreach engine.

## File-authored graphs

Use `graph_path` with run/save/amend for a caller-authorized absolute local regular UTF-8 JSON file, at most 1 MiB, no final symlink. Choose exactly one source: inline graph, graph_path, or run's `from` / save's `run_id`. Validation completes before writing or spawning. Save to the library and replay with `from` for repeated use; graph_path is valuable for an unsaved local graph or replacement amendment. Neither feature asserts a universal tool-argument length limit.
