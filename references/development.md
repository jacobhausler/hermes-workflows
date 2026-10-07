# Contributor checks (not ordinary user setup)

The plugin code is stdlib-only and imports host modules lazily. Test source from an
isolated checkout, with fixture homes under the checkout or in unique temporary
directories there; never point tests at an active user's home. Use the backend
Python from that checkout's environment, for example `python3 tests/test_engine.py`
from the project root.

## The one canonical suite command

```sh
python3 scripts/suite.py . ci-out
```

This is exactly what CI runs ([.github/workflows/ci.yml](../.github/workflows/ci.yml)).
It executes every `tests/test_*.py` serially with the project Python and every
`tests/test_*.mjs` with `node --experimental-strip-types`, and writes each case's
real exit code to `ci-out/exits.json` plus per-test logs. Do not hand-roll the sweep
with a shell loop or bare `node` — the runner owns the command form; match it and
your local result matches CI. `node --check desktop/plugin.js` remains the quick
syntax-only gate for the desktop half. Record each command's real exit code; never
convert failed tests into a passing aggregate. Admission is strict — a red on the
base counts against the merge gate too, and a run that discovers zero test cases is
a failure, not a green `(shipped in v1.2.1)`. The release integrator owns the complete
clean-copy sweep and package validation, not the skill.

## RED before green

For an apparent bug: reproduce it, write a focused failing (RED) check first, then
make the minimal source fix and rerun that check plus the relevant existing suites.
A fix without a test that would have caught the bug is not a contribution. Inspect
source and the live host API before believing an old feedback receipt; historical
counts are not an open-ticket list. Keep runtime dependencies and plugin writes
separate from documentation. The desktop app and the backend plugin can live on
different machines; testing JS syntax in one location does not prove the app loaded
it. No production restart, installation, or publication is implied by a green source
test.

## Build-lane hygiene and lane recovery

When a workflow build lane runs under this plugin's own runner: never check a base
ref out over a dirty tree to produce a failing run (that overwrites uncommitted work
in place). Commit tests first, use a throwaway detached worktree or a named stash
for the failing state, and bank a work-in-progress commit before the child hits its
turn cap. If a lane still dies with work uncommitted, recovery exists:

```sh
python3 scripts/lane_recover.py --run <id> --node <node> [--out <dir>]
```

It replays the lane's journaled file writes from the profile's session database
(opened read-only) into a restore directory — a triage list by default, files plus
an unmatched-patch report with `--out`. The replay and the prompt-side hygiene
preamble are pinned by their tests under `tests/`.
