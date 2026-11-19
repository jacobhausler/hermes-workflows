# Reading seats (hw-6og; ships in #689, open, layout final)

Seat-pool occupancy as a QUERY — the read that retires pgrep and
log-staleness heuristics. Ask the door:

```
workflow {action: "status", run_id: "...", seats: true}
```

`seats: true` attaches an engine-wide `seats` block to the status payload
(opt-in: without the flag every payload is byte-identical to previous builds):

```
{ "dir":     the seats pool THIS door resolves,
  "cap":     pool-recorded cap, or null while none is recorded (a disabled
             semaphore reports null too),
  "free":    cap - live — rides only when the cap is known; a NEGATIVE free
             is honest over-admission, never clamped,
  "live":    held tickets whose holder the occupant probe verifies, PLUS
             unparseable rows (unknown is never undercounted on an occupancy
             report),
  "holders": [{pid, name?, held_for_s, child_pid?}] longest-held first,
  "queued":  [{pid, name?, waited_s}] longest-waiting first — live waiters
             only (owner pid verified AND marker heartbeat younger than the
             queue's live window) }
```

Everything derives from the ledger files admission itself writes, and the
read takes no locks and changes nothing — it never prunes a ticket and never
seeds the cap:

| Ledger file | Meaning |
|---|---|
| `<seats>/<pid>.json` | one held-seat ticket per spawn (holder pid, optional bound child pid) |
| `<seats>/.cap` | the pool's recorded cap — first-writer-wins |
| `<seats>/queue/<pid>.json` | FIFO wait markers with owner heartbeat |

Where the pool lives: `WF_SEATS_DIR` if set, else `<runs_root>/.seats`; the
`dir` field rides in the payload, so a cross-root read is visible, not silent.

Cap law (unchanged, restated where operators read occupancy): the pool truth
comes from `WORKFLOW_MAX_SEATS` (env or `.env`) or config
`workflows.max_seats` — an integer in [4, 64], or `0` to disable the
semaphore. The graph key `max_seats` is a per-run CEILING that lowers within
range and never raises the pool truth; a malformed knob refuses the launch
(`seat_cap`). Seat deaths type as `seat_wait` (queue starved past the node
wall — zero tokens spent, `exhaustion_reason: queue_timeout`) and
`seat_unsupported` (no /proc and no `ps` to prove ancestor identity); both
rows are in `references/death-table.md`, and the fan-out wait math is in
`references/grammar.md` §concurrency.

## Citations

- `wfcommon.py` — `seats_view(seats_dir, now_s=None)` (the docstring names the
  occupant law: read-only by law, no prune, no cap seeding, fail-open counts);
  ships in #689.
- `__init__.py` — `_seats_root()` (WF_SEATS_DIR else runs-root `.seats`), the
  `seats` arg schema in the tool surface, and the `status` leg
  `out["seats"] = _common.seats_view(_seats_root())`; ships in #689.
- `references/operations.md` — "Seat-pool occupancy (`status` + `seats:true`,
  hw-6og read surface)"; ships in #689.
- `references/grammar.md` / `references/death-table.md` — cap knob, ceiling
  law, `seat_cap` / `seat_unsupported` / `seat_wait` rows (merged trunk).
