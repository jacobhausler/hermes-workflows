# The disposition table (E15, merged #684)

"What does this status mean?" is answered one field away in the read model:
`workflow {action:"status", run_id:"<run>"}` → each node entry carries
`disposition` beside `status`, from the single table `wfcommon.DISPOSITION_BY_STATUS`
(map below). A node record's `status` is the raw engine value (lowercase, as committed).
Its **`disposition`** is the terminal answer an operator may state as known.
One total table maps every status value the engine ever writes — a reader never
guesses whether `done` is terminal or what a torn `running` means, and an
absent field is never read as success.

| record status | disposition | meaning |
|---|---|---|
| `done` | `SUCCEEDED` | committed answer, current under its efp |
| `partial` | `PARTIAL` | committed, incomplete: re-drive is a decision, not an obligation |
| `failed` | `FAILED` | committed failure |
| `failed` + `error_class: cancelled` | `CANCELLED` | stop is history, not failure: a resume re-drives |
| `skipped` | `SKIPPED` | terminal routing, not done output |
| `running` | `UNKNOWN` | torn: applied effects may outrank the record |
| `interrupted` | `UNKNOWN` | crash mid-flight: say UNKNOWN; never upgrade, never downgrade |
| `registered` | `UNKNOWN` | survivor registration, no verdict |
| anything else / absent | `UNKNOWN` | explicit unknown — never a silent success |

Where it lives and where you see it:

- The mapping: `wfcommon.DISPOSITION_BY_STATUS` with
  `wfcommon.disposition_of(status, error_class)` — the ONLY implementation,
  total by construction, importable from the door and the runner.
- Every read view carries the answer one field away: `run_state`'s per-node
  dict stamps `disposition` beside `status` (including the interruption
  demotion, where a torn `running` projects as `UNKNOWN`).
- Finalized fan-out item records (`nodes/<id>.<i>.json`) carry `disposition`
  too — the same table, never a locally re-invented vocabulary (ships in #691,
  open; see [03-incidents.md](03-incidents.md)).
- The set is pinned: a status value the engine writes that is absent from the
  table is a build failure, asserted in `tests/test_disposition_table_25t.py`
  (`{SUCCEEDED, PARTIAL, FAILED, CANCELLED, SKIPPED, UNKNOWN}` and
  `DISPOSITION_BY_STATUS` domain/range checks).

The committed pinnable records (done/failed/skipped/partial) need no stamped
disposition field — they are pinnable from the journal — but you never have to
recompute it: read the `disposition` field off the view.

## Citations

- `wfcommon.py` — module head, "DATA SHAPES — node-record disposition (the
  total mapping; est-25t / E15)" (the table in the docstring itself).
- `wfcommon.py` — `DISPOSITION_BY_STATUS`, `DISPOSITION_UNKNOWN`,
  `disposition_of` (section "est-25t (E15): the ONE total state->disposition
  table").
- `wfcommon.py` — `run_state` (per-node `"disposition": disposition_of(...)`)
  and the `node_rec` interruption demotion beside it.
- `tests/test_disposition_table_25t.py` — the pinned closed set.
