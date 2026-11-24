# proof-harness — real-app proof driver (source-only)

Repeatable capture of the ACTUAL React/SDK renderer of the hermes-workflows
desktop half — never CHATFRAME, never `synthesis/index.html`, never a
file-openable RC or a JSX-to-DOM fake, as production proof.

Interface (the contract later beads use — slice A, bd_2026-11-13-iqf):

```sh
node tests/proof-harness/capture.mjs [--case CASE] [--only directive,pane,tray] [--out DIR]
```

`--case` defaults to `baseline`; `--only` INTERSECTS the case's surfaces
(short tokens or full surface names; an unknown token exits 2, an
intersection that selects nothing exits 2 — never a green no-op); `--out`
defaults to `captured/run-<ts>` under this directory.

`--out DIR` is driver-owned scratch (ownership marker `.ui2-proof-owned`;
a pre-existing DIR without the marker is refused, and a stale marked DIR is
archived to `DIR.stale-<ts>` — never rm'd under the cold-before-delete law).
Evidence lands at `DIR/captures/*.png` (0444), `DIR/contents/*.txt` (0444),
`DIR/manifest.json` (0444, written last), `DIR/report.json`, `DIR/identity.json`
(app commit/dirty count/package/electron/hermes versions, candidate+staged
plugin sha256, repo head + merge-base pinning "current merged head", seeded
run ids, config-before/after, teardown survivors).

## Reproducibility law (slice A)

Every run writes an IMMUTABLE capture set. `manifest.json.captures[]` pins
each PNG's bytes with sha256 (immutability — files are write-once, stale dirs
are archived whole). The `manifest.json.repro` section pins only the
CONTENT layer: per capture, the masked visible text of the captured region
(pane-column text for viewport shots; the card element's innerText for card
shots) hashed after masking exactly the declared volatile classes
(`VOLATILE_MASKS`: run ids, run-clock words, relative timestamps, dates —
the pixels those words occupy legitimately differ between two live runs).
Two independent runs at one candidate pin the same
`repro.combined_sha256`: the double-run hash diff is empty at the content
layer. The committed proof is `captured/bd_2026-11-13-iqf/set-{1,2}/`
(two full sets); `tests/test_proof_harness_repro.mjs` verifies the pair,
recomputes the combined hash from disk, and pins the mask with samples.

## Prerequisites (one-time, host-side)

1. A hermes-agent checkout with a provisioned desktop app:
   `<repo>/apps/desktop/node_modules/.bin/{electron,vite,tsc}` must exist
   (`pnpm install` at the repo root). Default checkout:
   `$UI2_PROOF_HOME/hermes-agent` (i.e. `~/.hermes/hermes-agent`); override
   with `--app-repo` or `UI2_PROOF_APP_REPO`.
2. The `hermes` CLI must be on PATH (or `--hermes-bin` /
   `UI2_PROOF_HERMES_BIN`) — the bench boots its OWN gateway fork as a
   standalone satellite profile (see "Bench profile law" below), and the CLI
   is used for the profile-scoped config writes and their revert. A live
   estate/host gateway is NOT a prerequisite and is NOT disturbed: the bench
   fork runs beside it under an isolated `HERMES_GATEWAY_LOCK_DIR`.
3. The candidate desktop half is the checkout's `desktop/plugin.js`
   (or `--plugin PATH`). It is staged into a bench-local
   `HERMES_HOME/desktop-plugins/hermes-workflows/plugin.js` and re-hashed:
   the app loads exactly the candidate bytes (identity.json pins both hashes).

## Bench profile law (field-proven 2026-11-24, bd_2026-11-13-iqf)

One gateway per host serves every profile: while a live host gateway exists,
`gateway ensure` for the DEFAULT profile ATTACHes or refuses — a bench fork
under the default profile cannot exist ("The host gateway already serves
profile 'default'"), and a COPIED `gateway_state.json` poisons the fork's
profile reservation ("Gateway runtime already owns profile <real home>").
The bench therefore homes its backend at a satellite profile `ui2bench`
inside the bench home: the profile config carries `gateway.standalone: true`
(the sanctioned opt-out that STARTs beside the host multiplexer),
`HERMES_GATEWAY_LOCK_DIR` points inside the bench (the host rendezvous record
is invisible both ways), and `<userData>/active-profile.json` pins the app's
launch profile. Consequence: every trusted input — `settings.runs_root`,
`settings.tray` — lands in the BENCH PROFILE's config, never the shared one,
and teardown's revert + `gateway stop` are bench-local by construction.

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

## Verification (slice A command)

```sh
node --check tests/proof-harness/capture.mjs \
  && node tests/proof-harness/capture.mjs --only directive,pane --out "$PROOF_DIR/set-1" --cdp-port 9394 --renderer-port 5194 \
  && node tests/proof-harness/capture.mjs --only directive,pane --out "$PROOF_DIR/set-2" --cdp-port 9404 --renderer-port 5204 \
  && node -e 'const m=p=>JSON.parse(require("fs").readFileSync(p)).repro.combined_sha256; if (m(process.argv[1])!==m(process.argv[2])) { console.error("REPRO HASH DIFF NOT EMPTY"); process.exit(1) }' "$PROOF_DIR/set-1/manifest.json" "$PROOF_DIR/set-2/manifest.json"
```

The double-run diff is over the repro section — the two runs are fully
independent benches (own ports, own user-data, own seeds), so an equal
combined content hash is reproducibility, not a re-read of one scratch dir.
Committed copies of both sets ride at `captured/bd_2026-11-13-iqf/` and are
re-verified from bytes by `tests/test_proof_harness_repro.mjs` (CI-safe).

On a loaded box (crew waves), first paint can outgrow the 60 s default and
the run dies exit 5 while vite/CDP are healthy — pass
`--paint-budget 300`. Parallel lanes pick distinct
`--cdp-port/--renderer-port` pairs (preflight refuses busy ports at exit 4).

Before this driver lands, use the existing real-client QA driver:
`node ~/.hermes/skills/hermes-workflows-ui-qa/scripts/wfqa.mjs <cmd> [args]`
against a manually booted bench (setup recipe at the top of
`hermes-workflows-ui-qa/SKILL.md`); capture.mjs automates exactly that loop
and adds identity, seeding, revert and teardown law.

## Packaging decision

`tests/proof-harness/` (driver, case manifest, seeds, committed capture
sets) is a SOURCE-ONLY subdirectory — the ZIP's tests glob is the FLAT
`tests/test_*.py|mjs` set, so nothing under the subdirectory ships, and the
release ZIP stays `desktop/plugin.js` + shipped suite, byte-for-byte
otherwise unchanged. The behaviour spec `tests/test_ui2_proof_driver.mjs`
and the reproducibility spec `tests/test_proof_harness_repro.mjs` DO ride
that glob, so both are declared in `pack.py` `SOURCE_ONLY_TESTS` (with
reason) and mirrored in `tests/test_package_source_only_756.py` — the exact
est-4vnq finding-4 shape: a shipped test executing an unpackaged helper
dies at an unpacked root.
