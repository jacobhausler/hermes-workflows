feat(orphan_watch): subscribe on_session_delete — deleted owner sessions surface at once

Core v0.22.5 (upstream ee3ce9a4d9) added the `on_session_delete` observer: it fires
once per committed session-row delete — single, bulk (`deleted_ids` carries the full
set whenever the count differs from 1), empty-sweep, retention prune and ghost-prune.
A gateway-deleted owner never end/finalizes, so an orphan-held gate parked under that
id kept its claim until a signal that can never arrive. orphan_watch now marks the
deleted id and every `deleted_ids` member dead through the existing `mark_session`
(one run.json scan per fire; dedup and the (run_id, gate_id) idempotency law
unchanged). The handler joins `HOOKS`, so `_hook_surface()` and the config-gated
register loop pick it up with no new literal site; the floor core ignores the
unknown-name registration, so `requires_hermes` stays. Docs table synced
(docs/orphan-held.md).

Tests: tests/test_orphan_watch.py — wiring check now names the four observers; new
legs for single delete, bulk delete (every member marked, live owner omitted stays
unmarked), re-delete idempotency, and no-op/malformed shapes (no ids, empty list,
string in the ids slot, junk members dropped) never row and never raise; the
garbage-run fail-open block covers both payload shapes.
