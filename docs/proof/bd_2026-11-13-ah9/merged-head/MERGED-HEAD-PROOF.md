# bd_2026-11-13-ah9 — merged-head real-app proof (Astra W1 review gate)

Attempt #1 (resume) evidence; completes the partial_open gate "run the proof
driver against the MERGED head, attach the captures". PR #714 was merged by the
owner at 2026-11-24T03:04:20Z (merge commit db405cf) before this session; all
captures below were re-rendered against the merged tree afterwards.

## SHA / provenance
- base: 1967586 · PR head: 89b12ca · merged: db405cf (owner jacobhausler)
- current origin/main: 50f02d4 (#715 l62 driver lands on top; it does not touch
  desktop/plugin.js)
- candidate plugin.js sha256 = d22feb08d72d4ed012e8d1ff652a2849adb02d5516bd285cbecbd3f457c211c8
  (identical at db405cf and 50f02d4; pinned three ways: candidate file, staged
  bench copy, staged-after-load — baseline-run/identity.json)

## Verification at merged head 50f02d4 (fresh worktree, this session)
- node --check desktop/plugin.js → exit 0
- node --experimental-strip-types tests/test_metrics_missing_ui.mjs → exit 0
- node --experimental-strip-types tests/test_live_truth_ui.mjs → exit 0
- node --experimental-strip-types tests/test_lifecycle_numeric_view_models.mjs → exit 0

## l62 driver (real installed/dev app, isolated bench)
Command (from merged tree /Users/jacobhausler/code/wf-pr-20261123):
  node tests/proof-harness/capture.mjs --case baseline --out .../baseline-run \
    --cdp-port 9633 --renderer-port 5333 --paint-budget 300
Result: identity.json complete, teardown survivors=[], revert_failures=[];
driver-iqf3.log contains no UI2_PROOF_FAIL. Earlier partial runs recorded
honestly: first baseline run exit=6 (run-row click), baseline-iqf exit=7
(then-current plugin lacked the fix — superseded), iqf2 exit=4 (ownership
marker refusal), and this resume dir's tray-directive case captured the app's
"Hermes couldn't start" diagnostic (00-diagnostic-pane.png) — a bench gateway
startup timeout, not a candidate defect.

## Minimal local capture at merged head (documented wfqa bench + running/shotcdp.mjs)
Candidate deployed to both sanctioned roots (deploy-hashes.txt, d22feb08 at
both), restored byte-identical afterwards (restore-verification.txt, 918f205
== before.txt). DOM verbatim dumps (running/dom-*.json) + PNGs:
- 14-live-pane-held-words.png — held neutrality: explicit words `held`,
  `gate held`, run clock `run 3m 52s`, release/stop; no color-only status.
- 15-running-row-fresh.png — fresh (1s/6s): census `runs 2 · running 1 · held 1
  · failed 0`, row `0/3 terminal · 1s · IDLE —`, header `Running · activity
  unknown` (honest unknown), run clock `run 6s`, `1 live`, child clock `n1 6s`
  without run word.
- 16-running-row-quiet.png — quiet (>5s): `0/3 terminal · 14s · IDLE —`,
  timeline `14s on-track`.
- 17-running-row-activity.png — recorded activity: run 27s, timeline 29s,
  census exact integers; no template artifacts (no undefined/NaN/{{}}).
- baseline-run/captures/01+02 — driver capture at merged head: census exact
  integers, held detail `held` + `run 1m 24s` + `gate held` pill, say Finished
  / hold held / tail pending.

## Screenshot review (this session, vision)
Reviewed: baseline-run/01, baseline-run/02, running/14,15,16,17,
tray-directive/00. All render real React UI; transcriptions above are from the
review. Known transience (documented, not defects of this bead): a
"Runtime not ready" startup toast in the two baseline-run shots (bench gateway
still binding) and a one-time `Google Profile Picture.png` chrome-icon sweep
noise in the first whole-dir hash attempt.

## Capture sha256 (authoritative, this dir)
a4d51e038984c7172247aa562099c227d627021ab338b16a4aec7df46dba8c29  baseline-run/captures/01-pane-runs.png
759fa3bddaffd57c45ca8d8faf8d99ccfac0a2c7ba41d4762ff4803b237def5e  baseline-run/captures/02-pane-run-detail.png
ef8672601788243d0bb4d3859eb1adc4b1d8f74ba7dbbaf776360869b8721bc5  running/14-live-pane-held-words.png
a8d19427ce242b14f91f07bd6e661a94486240d795374b05c9d693bef640843e  running/15-running-row-fresh.png
36119ae79388a138f07e195462c5937e7d06232ea2a69db73c6ff45bcb2d2707  running/16-running-row-quiet.png
6ed830c0a5316c10fa8f4dfe3f8b3bd7de1652b561515acb302bb534ba0930ce  running/17-running-row-activity.png
e5f38555edadcd26535ccc3c35f6938ebf8b3020241ba231945893ceb54d2094  baseline-iqf/captures/01-pane-runs.png
f26612b047381b8790736a58ad949620defd37a9dfe52ad9bf06ab63d2d3d4fe  baseline-iqf/captures/02-pane-run-detail.png
e607152bd3487c4563ab9c463b820aeca07a90baa9be8b4d01baab43571f6f4e  baseline/captures/01-pane-runs.png
33a4805ee139ff9d2e198a6bebd4d8d564702ad5031a099ac5376fd0e7263da1  baseline/captures/02-pane-run-detail.png
e0b9fa80e97c0a1912c0622e8f08a95a8be0501530ca458941eb5c5fd4dbcfd6  tray-directive/captures/00-diagnostic-pane.png

Historical fixtures (prior attempt dirs bd_2026-11-13-ah9-20261124T014516Z,
...T025502Z, ...T025846Z-wfqa, and the pre-merge PR comment 7120907184
attachments) are untouched, byte-for-byte.
