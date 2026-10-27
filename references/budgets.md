# Node budgets

Leave `max_turns`/`timeout` unset and name a `shape`; the runner fills them from the
measured p95 presets in `wfcommon.SHAPE_PRESETS` (the single source; measured 2026-09-25):

| shape | max_turns | timeout |
|---|---|---|
| recon | 100 | 2400 |
| build | 65 | 1500 |
| review | 65 | 2400 |
| publish | 75 | 1500 |

Set `max_turns`/`timeout` explicitly only with a measured reason. `validate` returns
non-fatal `warnings` when an agent's effective `max_turns` is below its shape's p95
preset (the default shape is `build`). A named shape wins over graph defaults;
an explicit node cap wins over both. Warnings do not change caps or reject the graph.

A lane node whose result is consumed downstream must end with bare JSON as its last
message and exit 0. State that exit hygiene in its goal: persist the work before the
turn cap, return the JSON required by its schema, and add no trailing commentary.
A complete answer does not make a nonzero exit successful; a harvested partial can
still block plain downstream edges.

## Turn accounting — `api_calls` is the counter that kills

`max_turns` is billed **per API call**. The child runs
`hermes chat --max-turns N` and the core loop consumes one turn for every
provider request it makes, whatever triggered that request — so today
`api_calls == turns`: ONE counter, no distinction between productive turns and
retry turns, and no reservation seam. You cannot ring-fence "the last two turns
for the final answer", because the counter you would reserve against is the
counter that kills the lane. Ruled on issue #387
(2026-10-11, option (b)): contract documented, behavior unchanged — a separate
tool-turn counter or a `reset_after_harvest` knob was declined, so no such key
exists or may be assumed.

Consequences at the cap, all machine-visible:

- The death is TYPED, never prose: `error_class: cap_exhausted` on the node
  record, the run clock reports `phase: expired` with
  `exhaustion_reason: turn_cap`, and the door's `stop_reason.class` carries it
  (`kind: budget` when the pre-cap budget cue had fired first).
- The death is re-drivable, not final: `cap_exhausted` rides the bounded ladder
  (`retry.bounded`, default ONE machine-resume re-drive; a second cap death
  commits `failed`). A schema-valid fenced answer in the dead attempt is still
  kept as `partial` under the harvest-on-death law.
- The budget cue is notice, not turns: at `max_turns - 5` (run.json
  `budget_cue_margin`) the runner steers the lane ONCE to persist work and
  prepare its final fenced answer. It buys seconds to write, not extra turns.
- The cue rides the ONE steer channel, and the panel shows it. The injector
  appends an `inbox.jsonl` line `{node, index, text, budget_cue: true}` (the
  same schema `steer` writes) and appends `i=-1` to the live spawn's bake file,
  so the lane pulls the cue at its next inbox seam even though its bake was
  HWM-frozen at spawn. Consequence for readers of `_steer_state` / the
  NodePanel steer counts: a capped lane that reached the cue shows
  `queued 1 · baked 1` although the OWNER never steered — `queued >= 1` does
  not imply owner steering. The tell is the `budget_cue: true` flag on the
  inbox line itself (one per (node,index) generation, claim-file idempotent);
  see QA WF-08, seed run 20261027-143703-wf-qa-quorum (race.0/1/2).

To land the final answer inside the cap, shrink the work per node instead of
reserve turns inside one: raise the cap with the answer-writing calls counted
in; split a big node into two nodes whose budgets each include their own
commit turn; and write-first — persist artifacts to the work dir every few
turns and emit the fenced JSON the moment the last required section lands, so a
cap death costs only the answer, not the work.

This contract is pinned by `tests/test_turn_accounting_contract_lw1eh.py`
(spawn carries `--max-turns <cap>`; the capped lane's recorded `api_calls`
reach the cap and the death is typed with the `turn_cap` clock reason and
exactly one bounded re-drive; the twin lane that answers below the cap ends
`done` with no cap evidence).
