# North stars for agent workflow estates

The stance layer, not the verb layer: the claims that survived six weeks of
running these graphs as the primary execution surface, genericized on purpose —
no estate numbers, only shapes (a cap, a queue, a typed refusal), and every
receipt named below is one this package can hand you itself. The full scars stay
in the ledger and in the owner's chat.

| North star | What it costs when ignored | Receipt in this package |
|---|---|---|
| Sequencing, gating, joining agent work IS graph authoring — write the DAG, even a one-node one. | Prose orchestration: unresumable, ungated, unplayable. | one-node graphs in `library/` |
| The graph is compute; the ledger is memory, and the graph ends at PR-open. | State stranded in a transcript; a lane only a chat replay can read. | `bead_close`/`effects` read-back (`bd` is one adapter) |
| The close carries its receipt and the runner re-reads the ledger. | Close-out left as tail work inside the acting seat. | mandatory close-out node |
| The shelf is the deploy surface; fix library graphs in place. | A defect you work around by hand-rolling a private replacement is a defect you adopted. | `library` + `run from:<name>` |
| Put the law in the graph, not in the operator's memory. | Prose restated across skills drifts; a seat skips a rule it never saw. | `defaults.context` |
| Gates are the only place a human talks to the graph; the timer default is a verdict, not a failure. | A human question that is not a gate node is nagging. | `hold_timeout` + `default_option` |
| Handoff between seats is files with a fixed schema, not prose. | One shared scratch root under concurrent lanes: six false clears in one 118-lane wave. | per-key state roots in the shipped templates |
| A gate that cannot answer "what would prove this?" is decoration; machine gates fail closed. | Implicit match-all, stale witness metrics, an empty sweep that exits 0. | `scripts/gate_lint.py` |
| Wakes, not polls; the only in-lane wait is a paved waiter that fails loudly on the first probe error. | Hand-rolled sleep loops swallowing errors into eternal "pending". | `wake.jsonl` |
| Deadlines beat diligence inside a seat; the clamp lives in the script, not the prose. | A long check that outlives the harness window; retries ground to budget death. | `--run-budget`, detached receipts |
| Unjam by freeing work, never by launching it. | A wave hand-launched around the governor turns a stall into a pile-up. | the seat cap + typed `seat_wait` |
| Claimed-count is a badge, not a process count; report one backlog vocabulary, each field by its exact query. | Any claimed count above live runner pids is dead-claim debt. | `list` `counts`/`total` |
| A watchdog needs a signature, not a hunch, and must kill and re-drive in the same pass. | Killing on silence; a kill that strands what it killed. | `runner_watchdog.py` |
| No daemons until a number proves one: silent-when-clean, push-on-find, dead-man-on-itself. | A monitor that cannot tell "nothing to do" from "watchdog dead". | `park_watch.py` (the 9.3 h park burn) |
| Measured rules only: no receipt, no rule. | Doctrine that outlived the run that bought it. | `docs/retention.md` (4.5-vs-19.5 GiB), `showcase.md` §3, peer lanes `atbrace:hw-36y` |

Three words, each defined once by the exact query that finds it: a *husk* is a
`status`/`list` row reading `runner_live:false` over unfinished work; a *wedge* is
that row reading `needs_resume:true`; a *graveyard* is a marker whose target
answers `unknown run_id`.
