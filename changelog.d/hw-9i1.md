feat(start): one verb from prose to a dispatched run

`workflow{action:"start", goal:<prose | five-line yaml>}` synthesizes the
smallest graph that satisfies the input and dispatches it through the FULL
existing run door — no second validator. The synthesizer lives in its own
module (`wfstart.py`); the verb is thin (parse -> synthesize -> act_run).

Smart defaults, all by reference to existing tables: model/provider stay
unset so the node rides the seat's own route; a `shape` name bakes the
measured-p95 census preset (wfcommon.SHAPE_PRESETS) for timeout and turn
budgets; the lane key derives as `<team>/start-<slug>` (or `start-<slug>`),
so a double-start of the same goal dedupes while the incumbent is unfinished.
v1 scope is single-node plus fixed fan-out from a json path
(`items_from` -> `fanout.items_from` verbatim); plural prose is NOT inferred.
The response carries `run_id` and the one `watch` status command; both misuse
paths (empty input, spec without content) refuse with the accepting example
rendered by the same module — until the door-side example channel (z79)
lands, that static string is the teach example.

No door/validation file is touched. Tests: tests/test_start_verb.py (7
behavior checks at the tool seam, spawn stubbed; the README action row is
pinned by the existing docs-surface drift law). The registration makes
wfstart.py part of the executed dispatch surface and a bind-time import, so
every surface-pinning fixture copy set and the pack manifest learn the file:
tests/test_docs_surface_drift.py, tests/test_pr_tag_audit.py,
tests/test_terminal_handoff_boundary_r19.py, scripts/pack.py INCLUDE_FILES
(one line each — the est-4vnq finding-4 law: an unshipped bind-time module
dies at import on every install, and test_packaging stayed green while
CI's copied-plugin test went red, so the manifest line is load-bearing).
