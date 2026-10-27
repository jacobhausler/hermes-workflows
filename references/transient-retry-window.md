# Persisted transient-retry window (est-9ceqc)

The transient ladder writes the node's `{deadline, attempts}` to
`retry-window.json` in the run dir BEFORE each backoff sleep and clears the key
once the node settles anything but the transient death. A runner killed
mid-backoff resumes by waiting the window out (polled, stop-aware, per node)
before its first spawn for that node, and the ladder seeds its attempt counter
from the persisted count — restarts cannot re-grant a spent cap.

The default transient schedule is exponential (base 2 s, ceiling 30 s); an
explicit `retry_backoff: [a, b]` keeps the fixed two-point schedule. The state
is ONE run-dir file, `retry-window.json`, keyed per node (fan-out items key as
`<id>#<index>`), written atomically under an in-process lock — a deliberate
counter (not a second queue): the run's event ledger stays the record, the
window file carries only the backoff clock and the spend cap. The consolidate
(batch-partner) ladder site carries no key and keeps the pre-graft restart
behavior. The `node.retrying` event shape is unchanged (`backoff_s`,
`attempts_log`).

Pinned by `tests/test_persisted_retry_window_9ceqc.py` (includes a SIGKILL
restart-resume case: the window survives, the cap does not regenerate).
