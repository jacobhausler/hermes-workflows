# Persisted transient-retry window (est-9ceqc, bounded by est-9qhpf)

The transient ladder writes the node's `{deadline, attempts, log}` to
`retry-window.json` in the run dir BEFORE each backoff sleep (the `log` is the
attempts_log ledger as of that save — est-9qhpf) and clears the key once the
node settles anything but the transient death. A runner killed mid-backoff
resumes by waiting the window out (polled, stop-aware, per node) before its
first spawn for that node, and the ladder seeds its attempt counter from the
persisted count. The same persisted read is ALSO a spawn gate (est-9qhpf):
before the first spawn of a boot for a node (or fan-out item) the runner
compares the persisted attempts against the node's transient cap — at or over
the cap the spawn NEVER happens and the boot commits `transport_exhausted`
with the seeded lifetime count and the persisted ledger (never `attempts=1`
with an empty `attempts_log` on that exit — est-ja41 record-vs-ledger
agreement across the restart seam). The refusal is once per boot per key:
in-boot ladders stay bounded by their seeded loop, so a single fresh boot runs
the full 1 + cap ladder untouched, and ADOPT-NOT-RESPAWN attaches to a
still-live prior child instead of refusing. Restarts cannot re-grant a spent
cap.

The default transient schedule is exponential (base 2 s, ceiling 30 s); an
explicit `retry_backoff: [a, b]` keeps the fixed two-point schedule. The state
is ONE run-dir file, `retry-window.json`, keyed per node (fan-out items key as
`<id>#<index>`), written atomically under an in-process lock — a deliberate
counter (not a second queue): the run's event ledger stays the record, the
window file carries the backoff clock, the spend cap, and the attempt ledger
a refusal boot commits. The consolidate
(batch-partner) ladder site carries no key and keeps the pre-graft restart
behavior. The `node.retrying` event shape is unchanged (`backoff_s`,
`attempts_log`).

Pinned by `tests/test_persisted_retry_window_9ceqc.py` (includes a SIGKILL
restart-resume case: the window survives, the cap does not regenerate) and
`tests/test_lifetime_bound_redrive_9qhpf.py` (SIGKILL at the
kill-during-third-spawn seam: the re-drive spawns no 4th child, the committed
record is `transport_exhausted` with the lifetime count and the persisted
2-entry ledger, and a further re-drive stays refusal-idempotent).
