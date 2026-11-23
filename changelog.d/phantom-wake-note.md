Docs-only: one-line phantom-wake triage law in references/operations.md — a wake
naming a run_id with no run dir anywhere cannot be a kit stamp (door refusals
return before any registration; notify() no-ops on a missing run dir), so
status's `no run at <path>` is terminal truth and the notice was confabulated in
the woken agent's context. Root-caused from incident 20261123-101559-ui2-receiptcheck
(door-refused launch at 10:54:33; no wake turn in gateway log, no user message in
state.db, no lane entry, no run-dir birth time in the minute).
