# Reconcile churn: passes are cheap, notices are transitions (bd_2026-11-13-az9)

## Problem

A quorum fan-out storm left 4,343 events.jsonl rows and 16 provably zero-info
owner re-notices on one run. Every re-notice traced to a RECONCILE PASS — the
respawn boot scan, the settled-failed re-entry, or a straggler-watchdog
re-eval — re-firing on states that had not moved: an unchanged settled run
re-logged its block and re-armed the straggler latch because a retry had
merely overwritten a launch stamp. The shipped disposition table (#684, total
with an explicit UNKNOWN) already says when a run's answer moved; the notify
channel ignored it.

## Change

* wf.py gains the reconcile-pass stamp law at `RECONCILE_STAMP_FILE`:
  one pass = re-read the run's TOTAL disposition vector + amendment generation,
  compare against `<run>/reconcile.stamp.json`, write exactly one
  `run.reconcile` audit row. An unchanged pass (the pass that finds
  explicit-unknowns is exactly this case) only updates the stamp's touched
  fields — 0 notices. The first pass after a node transition or an amendment
  writes exactly ONE `run.reconciled` notice whose identity key carries the
  diff naming what changed (node old->new / the rev step). A pass with no
  stamp SEEDS silently; a broken stamp re-seeds, never re-notices.
  Two consecutive passes converge (idempotent).
* The respawn boot scan (`run.respawn_reconcile` site) and the settled-failed
  boundary are now reconcile passes: an unchanged settled re-entry still
  EMITS the lifecycle line (spawner contract) but logs no second run.blocked
  and wakes nobody.
* The straggler census splits its latch: the audit identity (full disc, launch
  stamps included) still writes one `fanout.stragglers` row per cohort state
  (now with an explicit `noticed` field); the NOTICE identity is the cohort's
  disposition shape — the first trip alarms, an open set merely SHRINKING
  (stragglers landing) or a retry re-stamp refreshes silently, and only a
  GROWN/RE-SHAPED open set or a rolled-back done count re-alarms. The s34
  storm geometry now costs <= 2 owner notices.
* New registered wake event `run.reconciled` (template table stays the only
  author of owner prose; the diff rides the transition pointer like #501's
  pointers).

## Test

tests/test_reconcile_pass_az9.py — seed, unchanged-settled (0 notices / one
audit row), convergence, transition notice, amendment notice, UNKNOWN
re-paint honesty, and the s34 storm fixture re-run (<= 2 owner notices, zero
new notices on re-drive).
