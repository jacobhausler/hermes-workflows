# Runtime doc map

This directory is the map of the engine's runtime surfaces: where each shipped
behavior lives on disk and in code. It closes the six doc gaps wave-3 recorded
(s21/s25/s36 families): the disposition table, amendment evidence paths, the
wall account, the quarantine layout, the live steer mechanism, and the seats
readout. Read [01-quickstart.md](01-quickstart.md) for the run-dir layout, then
the topic file for whatever you are chasing.

The six questions, answered once, with the file that carries the full story:

| Question | Answer (short) | Read |
|---|---|---|
| Where does disposition live? | `wfcommon.DISPOSITION_BY_STATUS` — the ONE total status→disposition table; every read view (`run_state` per-node dict, finalized fan item records) carries a `disposition` field beside the raw `status`. | [02-disposition.md](02-disposition.md) |
| Where does amendment evidence land? | `runs/<run>/amends.jsonl` (the admission ledger) plus, at APPLICATION time, `runs/<run>/nodes/<node>/amendment-applied.json` and one JSON line per revision in `runs/<run>/logs/boundary.log`. | [04-amendments.md](04-amendments.md) |
| How is a wall death accounted? | Every timeout death record carries a structured `wall_account` (declared / baked / clamps / grants / effective) and its prose twin in the `error` text; the author never sees a wall the author didn't write. | [03-incidents.md](03-incidents.md) |
| Where are quarantine rows written? | Durable rows at `runs/<run>/quarantine/<node>[.<index>].jsonl`; the event twins ride `events.jsonl`; finalized item records stamp `quarantine: {rows_path, rows}`. | [03-incidents.md](03-incidents.md) |
| Which steer mechanism is live? | Bake-at-spawn is the ONE guaranteed channel (`steer.baked` receipts carry `mechanism: "bake-at-spawn"`); the live pull is an OPT-IN child seam recorded only by `steer.consumed` + a cursor advance. | [05-steering.md](05-steering.md) |
| How do I read seats? | `status` with `seats: true` attaches a read-only `seats` block (cap, live, free, holders, queue) derived from the admission ledger files in the seats dir. | [06-seats.md](06-seats.md) |

## Conventions

- A `ships in #NNN (open)` tag marks a surface whose code lives on an open PR
  at the time of writing; the behavior itself is final and the named paths are
  the shipped layout. Everything else is merged on trunk.
- Every topic file ends with a **Citations** block: the exact files and
  symbols the claims resolve to. Open them; the docs do not ask for trust.
- Deeper prose on verbs and read-model semantics lives in
  `references/operations.md` and the death table in `references/death-table.md`;
  the efp field law in prose and the annotate verb live in
  `references/operations.md` ("The efp field law: which fields move a
  fingerprint", PR #685) and are not restated here.
