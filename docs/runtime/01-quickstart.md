# Quickstart: one run, its directory, its read model

`workflow {action:"run", graph:{...}}` returns a `run_id`. The run's whole
world is `$HERMES_HOME/workflows/<run_id>/` (§"The run directory"); its state
answers come from `workflow {action:"status", run_id:"<run>"}` (§"Reading a
run"). The door writes the run directory and a detached runner owns it; you
observe with `status` / `wait` and the lifecycle wakes (`wake.jsonl` is the
wake ledger). Verbs and payload semantics: `references/operations.md`. This
page is only the on-disk map — what exists, and when it appears.

## The run directory

Root: `$HERMES_HOME/workflows/<run_id>/` (the resolved runs root; `WF_RUNS_ROOT`
overrides). The layout below is the shipped surface — every path here exists on
a run that saw the event it names (the signature law from wf.py's module head).

| Path | What writes it | When |
|---|---|---|
| `graph.json` | door at submit; runner on amend consumption | frozen plan — the committed definitions whose efp decides staleness |
| `run.json` | door | meta: hermes_bin, name, launch-frozen knob bake (concurrency, retry ladder, `max_seats`) |
| `amends.jsonl` | door | one row per admitted amendment; the physical line ordinal IS the amendment revision |
| `events.jsonl` | runner + door | the append-only event log: `node.*`, `steer.*`, `budget_cue.drained`, `runner.reaped`, `graph.amended`/`graph.reloaded` … |
| `nodes/<id>.json` | runner | committed node records (efp-guarded). Failed/partial records carry `node_facts` (`error_class`, `final`, `log_path`, `prompt_path`, attempts) and, on a wall death, the `wall_account` ([03-incidents.md](03-incidents.md)) |
| `nodes/<id>.<i>.json` | runner | fan-out item records; finalized records carry `disposition` and, once quarantined, `quarantine: {rows_path, rows}` ([02-disposition.md](02-disposition.md), [03-incidents.md](03-incidents.md)) |
| `nodes/<id>/amendment-applied.json` + `logs/boundary.log` | runner | amendment APPLICATION evidence — the per-node efp movement and one boundary row per amends revision ([04-amendments.md](04-amendments.md)); ships in #691 (open), layout final |
| `inbox.jsonl` | owner (via `steer`) | steering / kill lines dropped by the owner — the ONE steer channel ([05-steering.md](05-steering.md)) |
| `steer/<node>[.<i>].a<n>.jsonl` + `.cursor` | runner at spawn | the per-spawn bake of addressed steering lines + its read cursor |
| `quarantine/<node>[.<i>].jsonl` | runner | durable #61 tree-quarantine rows, one per kill/reap/fail-closed instant; ships in #691 (open), layout final |
| `gates/<id>.json` | door on `release` | human-gate answers (`<id>.json.unconsumed` when an admission death refused to swallow one) |
| `wake.jsonl` | runner | every owner-wake attempt with its tri-state `delivered` field |
| `logs/<id>.a<n>.log` | runner | per-attempt child stdout (the `log_path` the records name) |
| `nodes/<id>[.<i>].corpus/` | runner | the banked corpse of a wall-killed lane (`work/`, `stdout_tail.txt`, `manifest.json`) — death-table row `timeout` |
| `stop.request`, `restart.request`, `wf.pid`, `runner_exit.json` | door / runner | control markers, live pid, the recorded exit verdict |
| `side_effects.jsonl` | runner | the committed side-effect journal; `wf.py recover <run_id>` reads it back as `{applied, torn, unprovable, safe_redrive}` (ships in #691) |

One level up, the door's other roots: `library/` (shelved graphs),
`inbox/` (study submissions quarantined by `workflow submit` — a different
quarantine, see [03-incidents.md](03-incidents.md) §"three quarantines"), and
`.seats/` (the seat-pool ledger, [06-seats.md](06-seats.md)).

## Reading a run

`status` returns the derived read model: run `status`, per-node `status` +
`disposition` (never guess from the raw state —
[02-disposition.md](02-disposition.md)), `next`, `failed_nodes`
(`[{id, error, error_class}]`), `run.blocked` with `residue` and `dead_letter`,
and — opt-in — the `seats` block ([06-seats.md](06-seats.md)). Every typed
death and its one sanctioned repair is in `references/death-table.md`.

## Citations

- Run-dir layout at the runner's module head: `wf.py` docstring
  (`Run dir: $HERMES_HOME/workflows/<run_id>/` — names `quarantine/`,
  `logs/boundary.log`, `nodes/<id>/amendment-applied.json`, `side_effects.jsonl`).
- Read model + `node_facts`: `wfcommon.run_state`; the node-facts assembly
  described in `references/operations.md` ("Failed and partial nodes ship
  `node_facts`").
- Banked corpus + `timeout` row: `references/death-table.md` (`_bank_the_corpse`,
  `nodes/<id>[.<i>].corpus/`).
- Amendment ledger/evidence: [04-amendments.md](04-amendments.md).
