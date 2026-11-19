Runner death is loud and clean through the watchdog tick (bd_2026-11-13-3qo, E23)

The tick now REAPs as loudly as it revives: a dead-runner run with a death
scene (dead `wf.pid` and/or node records claiming `running`) wakes the OWNER
SESSION in the same tick, naming the dead pid, the lost lanes and the
re-drive plan, with the row on `wake.jsonl` deduped by the scene tid (one
wake per death, never a re-notice). SIGKILLed runners used to record nothing
while `act_wait` quietly replaced them.

A re-drive the tick cannot perform (wedged-lock heal refusal) is SCHEDULED as
a one-shot `redrive.request` continuation carrying its own expiry; the
consumer enforces it — past-due is dropped with `watchdog.redrive_expired`
and never re-fired from an old receipt (the launchd-treadmill law: a one-shot
maintenance continuation without an expiry becomes a perpetual boot tax).
Holders-dead pruning: a terminal run over a dead runner loses its `wf.pid`
corpse and its `lanes/<stem>.json` claim (under the entry's own lock, so a
concurrent relaunch is never clobbered); an unfinished run keeps its claim.

Behavior test: tests/test_death_loud_3qo.py (fake cron + wake_native stub in
a stable-root copy; asserts observable outcomes only). Idempotent by
construction: a rerun converges, refreshes count tries without extending the
expiry, and settled scenes deliver once.
