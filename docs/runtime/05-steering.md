# The live steer mechanism (E14, merged #687)

One channel in, one guaranteed delivery mechanism, one opt-in live seam. The
live mechanism is **bake-at-spawn**: `steer.baked` receipts say so —
`mechanism: "bake-at-spawn"` is stamped on every receipt event. The live pull
is a child's OPT-IN seam, and it counts as having happened exactly when its
evidence exists, never otherwise.

## The path a steer line takes

1. Owner: `workflow {action:"steer", run_id, node, text}` (optional
   `graph_revision` CAS). The door admits — terminal runs and terminal nodes
   refuse and name `amend` as the correct verb; gate nodes refuse toward
   `release` — then appends
   `{node, text, at}` to `runs/<run>/inbox.jsonl` under the graph lock and
   logs `steer.queued`. The refusal and the CAS miss write NOTHING: no inbox
   line, no event.
2. Runner, at spawn: `_steer_bake` copies every un-consumed line addressed to
   this node into the per-spawn file
   `runs/<run>/steer/<node>[.<index>].a<spawn>.jsonl` (atomic rename — the
   child sees the full bake or none), writes a sibling `.cursor` at `0`, and
   logs the receipt `steer.baked {node, spawn_no, n_lines, drained_cues,
   mechanism: "bake-at-spawn"}`. The HIGH-WATERMARK is the inbox line count at
   bake time: lines appended after this spawn never reach the live child —
   they are baked into its NEXT spawn.
3. Child, at a natural seam: the `workflow inbox` call (cooperative,
   once-per-turn guidance) reads its baked file between cursor and HWM,
   advances the cursor atomically, and logs `steer.consumed`. Honesty law: a
   line counts as delivered ONLY after the cursor advanced and the event
   exists — "the file was written" is not delivery. The baked coordinates ride
   the spawn env (`HERMES_WF_STEER_FILE` / `_CURSOR` / `_HWM`); a stranger
   without them has no pull branch.

## Budget cues are drained, not re-baked

A turn-budget cue injected near a child's cap is a steer line stamped to the
spawn that EARNED it — it names THAT generation's remaining turns. On respawn
the cue line is consumed WITHOUT re-feeding the steering prompt (quoting it
would restate a number that no longer describes the spawn); the drain is an
event fact, `budget_cue.drained`, never a silent swallow, and the bake receipt
counts it in `drained_cues`.

## What the steer receipt promises

`act_steer`'s `delivery` line states the mechanism per node state, no hedging:

- node `running`: the live child may pull at its next inbox call — NO
  delivery guarantee; anything it does not pull is baked into the node's next
  spawn (a running child's prompt is never rewritten).
- run `held` / runner live / runner down: baked into the next spawn — on gate
  release / at the next spawn / when `wait` resumes the runner.
- terminal run or committed node: refused — no runner will ever spawn that
  node, so the text would vanish; `amend` (or re-run) is the verb.

`steer cmd=kill` is not steering text: it routes to the node-targeted lane
kill (`error_class: killed`, siblings keep going).

## Citations

- `wf.py` — `_steer_bake` (its docstring's "DELIVERY TRUTH (E14," block:
  "bake-at-spawn is the ONE guaranteed channel and the";
  the `mechanism="bake-at-spawn"` receipt stamp), `drain_inbox`
  ("budget-cue lines are consumed WITHOUT re-feeding…",
  `budget_cue.drained`), the spawn env pins (`HERMES_WF_STEER_*`).
- `__init__.py` — `act_steer` (admission refusals, the `delivery` strings),
  `_steer_lines`/`_steer_event` and the `inbox` action's two halves
  ("Two inbox halves, one action name, never in conflict"),
  `_graph_lock`/`_revision_cas` for the CAS law.
- `tests/test_steer_delivery_truth_42t.py` — receipts, cursor law, cue drain.
- `references/operations.md` — the operator-facing steer paragraph.
