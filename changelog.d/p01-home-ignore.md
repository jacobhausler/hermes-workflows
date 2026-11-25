chore(ci): ignore the `p01-home-*/` temp-home prefix at the repo root.

`tests/test_agent_experience_p01.py` builds its fake HERMES_HOME with
`tempfile.TemporaryDirectory(dir=ROOT)` so the runner path guard accepts it.
The ignore family covered `tests/home*` and root `home-*/` but not this
prefix, so any crash between create and cleanup leaves an unignored
directory in an otherwise clean tree — enough to trip every porcelain-
gated lane boot check and the publish scrub. One-line ignore rule; no
runtime surface.
