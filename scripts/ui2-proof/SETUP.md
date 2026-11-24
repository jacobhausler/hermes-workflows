# ui2-proof — real-app proof driver (source-only)

Repeatable capture of the ACTUAL React/SDK renderer of the hermes-workflows
desktop half — never CHATFRAME, never `synthesis/index.html`, never a
file-openable RC or a JSX-to-DOM fake, as production proof.

Interface (the contract later beads use):

```sh
node scripts/ui2-proof/capture.mjs --case CASE --out DIR
```

`--out DIR` is driver-owned scratch (ownership marker `.ui2-proof-owned`;
a pre-existing DIR without the marker is refused, and a stale marked DIR is
archived to `DIR.stale-<ts>` — never rm'd under the cold-before-delete law).
Evidence lands at `DIR/captures/*.png`, `DIR/report.json`, `DIR/identity.json`
(app commit/dirty count/package/electron/hermes versions, candidate+staged
plugin sha256, seeded run ids, config-before/after, teardown survivors).

## Prerequisites (one-time, host-side)

1. A hermes-agent checkout with a provisioned desktop app:
   `<repo>/apps/desktop/node_modules/.bin/{electron,vite,tsc}` must exist
   (`pnpm install` at the repo root). Default checkout:
   `$UI2_PROOF_HOME/hermes-agent` (i.e. `~/.hermes/hermes-agent`); override
   with `--app-repo` or `UI2_PROOF_APP_REPO`.
2. A running `hermes serve` gateway whose plugin API mounts
   `/api/plugins/hermes-workflows/` (proof: AGENTS.md §2a — the gui.log line,
   not a 401). The `hermes` CLI must be on PATH (or `--hermes-bin` /
   `UI2_PROOF_HERMES_BIN`) — used for the config writes below and their revert.
3. The candidate desktop half is the checkout's `desktop/plugin.js`
   (or `--plugin PATH`). It is staged into a bench-local
   `HERMES_HOME/desktop-plugins/hermes-workflows/plugin.js` and re-hashed:
   the app loads exactly the candidate bytes (identity.json pins both hashes).

## What the driver owns and touches

* Fresh Electron `--user-data-dir` per run (isolated user data; dodges the
  single-instance lock; dodges stale plugin decisions).
* Bench-local `HERMES_HOME` with the staged candidate and COPIES of the
  read-only discovery/state files (`spawn-ledger.json`, `gateway_state.json`,
  `auth.json`, `config.yaml`) — never a symlink and never the real
  `plugins/` tree: the desktop-half migration would resurrect the installed
  half over the candidate.
* An isolated TEST RUNS ROOT (`DIR/bench/runs`). The pane lists it because
  the driver writes `plugins.entries.hermes-workflows.settings.runs_root`
  and arms the settings-gated tray with `settings.tray` (both `--force`),
  reusing the proven `hermes-workflows-ui-qa` recipe. These are writes to
  the SHARED gateway config for the minutes of the run — trusted inputs,
  reverted at teardown (recorded `before`-absence is restored via
  `config unset`). Teardown records any revert failure and exits 8.
* Owned supervisors only: vite + electron are spawned detached (own process
  groups); teardown SIGTERMs→SIGKILLs `-pgid` for exactly those groups, then
  survivor-scans `ps` by THIS bench's `--user-data-dir` path. It never kills
  by a broad `electron` pattern (other benches and the user's app survive).

## Trusted inputs (provenance)

* `cases.json` — the case manifest. Every seed declares
  `kind: engine_seed | historical_snapshot`. Engine seeds launch live
  (`door_run`: zero-token echo+gate graph through the plugin door, proven
  until `gate.held` appears; `oneshot_echo`: ONE real assistant turn —
  rides the seat default model unless the case pins one, so the directive
  card renders from assistant-role text as the skill requires).
  Historical snapshots are pinned fixtures (run id + `run.json` sha256) read
  via the launch-root fallback; they are NEVER relaunched and must match
  their pinned bytes byte-for-byte or the run refuses.
* `--plugin` candidate bytes, the checkout's `desktop/plugin.js`.

## Failure semantics (nonzero, never a green no-op)

| code | meaning |
|---|---|
| 2 | usage error, or unknown case (prints the known-case list) |
| 3 | known case names a surface not yet wired — explicitly a NEW test, not an existing command |
| 4 | preflight: absent candidate plugin, unprovisioned app checkout, busy bench ports, foreign `--out` dir |
| 5 | boot: dev renderer or CDP target never appeared |
| 6 | API attachment not proven: registry areas missing and/or seeded run row never rendered |
| 7 | capture: zero shots, a PNG under 4 KiB, or missing PNG magic |
| 8 | teardown: survivor under the owned `--user-data-dir` path, or config revert failed |

Engine-seeded runs are stopped through the door (`action:stop`) in teardown —
parked held-gate runners never outlive the bench.

### Tray ownership law (why the tray needs its OWN seed)

The composer strip renders ONLY the FOCUSED chat's owned runs
(`ownedRuns`/`SessionStrip`, desktop/plugin.js:728-737/1288): a run whose
`owner.session_id` is blank (a bare door launch) is PANE-ONLY by the
honest-absence law — a settings-true tray stays hidden. The baseline case
therefore seeds TWO engine runs: run #1 (blank owner) drives the pane and the
directive card; the tray seed relaunches the SAME graph with
`WF_OWNER_SESSION=<the one-shot's session id>` — the door's on-behalf stamp
(`__init__.py` `_owner_stamp`) — so the tray row appears in the seeded
transcript with count 1. The driver parses `session_id:` from the one-shot's
own output (never a fixture edit) and pins it in identity.json.

## Mandatory screenshot review

The driver proves PNG magic, size and hash — it CANNOT make a visual claim.
Every `captures/*.png` must be inspected with `vision_analyze` (see the
`hermes-workflows-ui-qa` skill: capture and DOM success are NOT visual
passes). `report.json` ships every shot as `reviewed:false`; flip the verdict
in the BEAD RECEIPT after review, not in the driver's file.

## Adding a case (later beads)

Append an entry to `cases.json`. If it renders a surface the driver does not
know, capture.mjs exits 3 naming it a new test. Do not "make it pass" by
pointing at `synthesis/index.html`. Wire real renderer surfaces into the
capture section of capture.mjs and extend `surfaces_registry` instead.

## The `gate` case (bd_2026-11-13-qri)

`node scripts/ui2-proof/capture.mjs --case gate --out DIR` proves the ONE
decision surface end-to-end on the real renderer: the held gate cell, a
trusted option click, the PENDING frame made real by holding the answer POST
at CDP `Fetch` interception (never a staged screenshot), the durable
`[data-gate-receipt]` saved frame, the success toast carrying the exact
ledger line (`◇ Held · <requester> · <run> / <gate>`) with its
`View exact gate` action, and the route-away/route-back identity proof.
The seed SIGKILLs the isolated runner at `gate.held` (seed field
`kill_runner_after_hold`), then the driver reads `gates/<id>.json` back from
disk and refuses the run unless: the answer matches byte-for-byte, `_ui` is
literally true, `events.jsonl` is byte-identical before/after (Nothing
restarted — verified for THIS tested runner only, not a universal scheduler
claim), and the gate node was never consumed. Frames 07-11; report.json
entries are `reviewed:false` until the mandatory vision pass.

## Verification (this bead's command)

```sh
node --check scripts/ui2-proof/capture.mjs \
  && node scripts/ui2-proof/capture.mjs --case baseline --out "$PROOF_DIR/baseline"
```

Before this driver lands, use the existing real-client QA driver:
`node ~/.hermes/skills/hermes-workflows-ui-qa/scripts/wfqa.mjs <cmd> [args]`
against a manually booted bench (setup recipe at the top of
`hermes-workflows-ui-qa/SKILL.md`); capture.mjs automates exactly that loop
and adds identity, seeding, revert and teardown law.

## Packaging decision

`scripts/ui2-proof/` is a SOURCE-ONLY helper directory (estate/app QA
tooling; the release ZIP ships `desktop/plugin.js`, never this). The
mechanical pack-list contract scans the flat `scripts/*.py` set, so the
subdirectory needs no `SOURCE_ONLY_SCRIPTS` row; the behavior test
`tests/test_ui2_proof_driver.mjs` DOES ride the `tests/test_*.mjs` glob, so
it is declared in `pack.py` `SOURCE_ONLY_TESTS` (with reason) and mirrored
in `tests/test_package_source_only_756.py`. ZIP membership is otherwise
byte-for-byte unchanged.
