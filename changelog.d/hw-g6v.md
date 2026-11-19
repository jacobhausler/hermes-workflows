fix(tick): the tick launcher is interpreter-pinned and survives install/update

The watchdog tick's baked shim now execs the absolute bundled python
(override: `WF_TICK_PYTHON`) with `wf.py` as an argument, so a plugin
install/update can no longer silently revert the tick: `wf.py`'s exec
bit is irrelevant (the interpreter reads it) and its
`#!/usr/bin/env python3` shebang is never resolved (macOS ships 3.9.6
there; the plugin is >=3.10 syntax — P41's tick rc=1). `wf.py` also
ships with its exec bit (`EXECUTABLE_FILES`, so the ZIP lands it 0755
and git checkouts keep it). A re-arm over a running tick, and the new
post-update self-check (`python3 cron_bridge.py selfcheck` → `TICK
SELFCHECK rc=0 …`), re-bake the launcher only on drift — a rerun
converges and never clobbers a settled one. docs/registered-jobs.md
ships beside the code with the one-line operator rule-out for
"Gateway draining".
Tests: tests/test_tick_pinned_launcher_p41.py.
