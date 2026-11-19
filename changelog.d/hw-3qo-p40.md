Respawn grant ledger resets per runner generation (bd_2026-11-13-3qo, P40)

The transient ladder persists its spend to `retry-window.json` so a killed
boot cannot amplify attempts past the node cap — but the same persistence
made those grants a LIFETIME debt: the estate's pre-heal boot saved 2 grants,
the post-update boot read `attempts >= cap`, refused every spawn as
`lifetime_cap_spent`, and genuinely new transient deaths under fixed code were
capped by a dead boot's spend (the same ghost-debt shape the 18-day launchd
treadmill wore out).

The watchdog's revival path is the runner-generation boundary, so it now
zeroes `attempts` on every respawn it performs, before the fresh boot can
read the file: the new generation grants retries from its own ledger. The
deadline (the backoff pacer) and the attempt log survive byte-exact — reset
per generation stays paced and evidence-preserving. The boundary is on the
event record (`watchdog.grant_ledger_reset`, naming the spent grants) exactly
once per boundary that actually spent anything; a rerun converges, an absent
or corrupt ledger is never clobbered.

Behavior test: tests/test_grant_ledger_generation_3qo.py.
