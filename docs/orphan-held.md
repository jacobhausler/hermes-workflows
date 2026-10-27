# Orphan-held runs

## The state it names

A run is **orphan-held** when it is parked at a human gate (`gate.held` in
`events.jsonl`, no later release/skip, no `run.stopped`) and the session that
launched it (`run.json` `owner.session_id`) has ended. Nobody is listening for
that gate any more, so without this the run waits silently until it ages out of
the card window.

## Where it surfaces

- `<runs_root>/orphan-held.jsonl` — append-only index. Row:
  `{ts, run_id, gate_id, session_id, hook, since, question}`. A revoke row
  (`revoked: true`, `reason`) cancels the latest row for that `(run_id, gate_id)`.
- `run.json` carries an advisory `orphan_at` stamp (removed on revoke).
- `workflow status` / `wait`: `orphan_held: true`, `waiting_on: {gate_id, since}`,
  and a `{"action":"stop","note":"owner session died; stop or re-attach"}` row
  FIRST in `next`. The `release` row stays: a human can still answer.
- `/wf orphans` lists unrevoked rows with the gate question.

## How it is detected

Three core hooks, all observers, registered by default:

| Hook | Marks runs owned by |
|---|---|
| `on_session_end` | `session_id`, only when the turn was interrupted / exited abort-shaped (`interrupted`, `turn_exit_reason` containing interrupt/abort/shutdown/cancel). The hook fires after EVERY turn; a normally completed turn of a live session is never marked. |
| `on_session_finalize` | `old_session_id` when present (rotation), else `session_id` |
| `agent_loop_stopped` | the session whose id is the suffix of `session_key` (separator-delimited, id >= 8 chars) |

Each fire scans `<runs_root>/*/run.json` (one read per run dir; the 64-line events tail fires only for matched holds).
Idempotent per `(run_id, gate_id)`.

## Revocation

Appended on `release` (any path, incl. the UI), on `stop`, and when `status`/`wait`
is read by a live session whose id differs from the owner's (a re-attach). Status
reports the flag only while the run is actually `held`.

## Why default-on

The failure it prevents is silent, and the cost is one run.json read per run dir at session end
plus one small file. Disable with the owner setting `orphan_watch: false`
(read at fire time, no restart).

## What it deliberately does NOT do

Never kills, restarts, resumes, re-parents or edits a run or its graph. No
liveness probing beyond the hook payload: a session that is `/stop`-ed but
still alive is marked until it (or any other session) reads status — then it
is revoked only if the reader is a *different* session; the owner answering
via `release` revokes too. Every path is fail-open: unreadable `run.json`,
truncated events, locked files or a read-only runs root produce no row and
no exception. Dead-runner *revival* is a separate authority and does exist:
the self-terminating watchdog tick (`runner_watchdog.py`, est-ip975) re-drives
dead-runner runs on a named `no_agent` cron job while any run is active and
deletes itself at drain. This advisory stays advisory either way.
