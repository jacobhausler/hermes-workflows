# GATES.md — est-z717 tray settings gate + zero-directive capture (branch feat/session-run-tray-230, rides PR #233)

## Gate 1 — RED-FIRST (test-only commit c425d3c, then RED runs)
- Test-only commit c425d3c adds the trayShouldShow gate pins to
  tests/test_run_tray.mjs + tests/test_session_tray.mjs (lane-hygiene: no
  checkout-over-dirty-tree).
- RED run in a throwaway detached worktree of c425d3c (new tests, old
  desktop/plugin.js — stash-popped back immediately after):
  `node tests/test_run_tray.mjs` rc=1 (AssertionError: "z717: gate ABSENT ->
  no tray even with live runs (default OFF)");
  `node tests/test_session_tray.mjs` rc=1 (AssertionError: "z717: gate absent
  -> hidden even with a live run (default OFF)", test_session_tray.mjs:162).
- Zero-directive capture pin RED-vs-mutated-model (house law): with the
  implementation in place, desktop/plugin.js ownedRuns was MUTATED to return
  [] (capture removed); `node tests/test_z717_zero_directive_capture.mjs`
  rc=1 (AssertionError: "ownedRuns includes the door-launched run under the
  fake session (zero directives)") — the pin CAN fail; the mutation was
  reverted from the pre-mutation copy (byte-identical restore verified,
  git diff shows only the intended z717 hunks) and the test re-ran ALL PASS.
- Door override RED on base: with __init__.py stashed (base owner stamp),
  `python3 tests/test_owner_session_override_z717.py` rc=1 — 3 override
  tests FAIL (WF_OWNER_SESSION ignored), the unchanged-default inheritance
  guard passes on base AND head; implementation restored, OK (4/4).
- Settings route RED on base: with dashboard/plugin_api.py stashed, `python3
  tests/test_settings_route_z717.py` rc=1 (4 AttributeError cases — base has
  no /settings route); restored, OK (5/5).

## Gate 2 — green (targeted)
node tests/test_run_tray.mjs                      -> ALL PASS
node tests/test_session_tray.mjs                  -> ALL PASS
node tests/test_z717_zero_directive_capture.mjs   -> ALL PASS
python3 tests/test_owner_session_override_z717.py -> OK (4)
python3 tests/test_settings_route_z717.py         -> OK (5)
neighbours: test_session_strip / test_pill_rail / test_pill_rail_expand /
test_register_surface / test_11_ui_imports / test_composer_owner -> ALL PASS
node --check desktop/plugin.js -> parse OK

## Gate 3 — suite
python3 scripts/suite.py . ci-out-z717 -> exits.json (result recorded in the
lane log; CI re-runs the same gate on the pushed head)

## Gate 4 — push
branch feat/session-run-tray-230 repushed to origin (SAME branch — PR #233
updated, no new PR); first push within minute 25 of the wake.

## Gate 5 — PR
UPDATE evidence comment PATCHed onto the existing repo-admin comment on #233
with the head-aligned marker (verdict=merge-pending-stamp,
reviewer=gh-dispatch lane=z717); @zingzapuj noted the binding head moved.
No self-stamp.
