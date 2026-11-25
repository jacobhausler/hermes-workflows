fix(packaging): `node_telemetry.py` and `runner_watchdog.py` join the release ZIP.
Both are spec-loaded by FILE PATH from shipped runtime code — the observer-hook
registration and the runner settle-seam fold load `node_telemetry.py`, and
`wf.py tick` plus the door's arm load `runner_watchdog.py` — so the import-closure
probe never saw them: packaged installs lost child telemetry silently and died on
`TICK REFUSED runner_watchdog.py not present`, while the shipped
`tests/test_wfcommon_contract_pins_batch4.py` died `ModuleNotFoundError` at an
unpacked root. The pack-list gate now catches the class mechanically: every `.py`
path literal inside shipped runtime modules (ZIP root-level + dashboard API) must
itself be a ZIP member, derived from the archive's own bytes — no parallel
package registry.
