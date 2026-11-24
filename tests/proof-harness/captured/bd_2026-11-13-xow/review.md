# Slice B capture review (bd_2026-11-13-xow)

Candidate: `desktop/plugin.js` sha256 `ae149734e4ba167e84c45ba119677ed593e5a615c9e9ad9f57a0d3b98b3f3f76`
(== qri's reviewed bytes from #724; slice B ships zero plugin.js changes).
App: hermes-agent `0f602c5f6f18` (dirty_entries 0), electron 44.10.2,
renderer checkout `~/.cache/xow-bench/app` (dedicated copy, app-copy law).
Two independent benches (ports 9514/5314 and 9524/5324, own user-data, own
seeds). Repro combined hash `1ecee8a65e9746bb184533993f2a7dd41e48aeb4a96aefeebe0d13fa3c7700cf`
— IDENTICAL across set-1 and set-2. Raster-only drift (clock pixels) recorded
for exactly 10-gate-toast, 09-gate-saved, 11-gate-after-view; held/error/
pending frames byte-identical.

Per-frame verdicts (raster magic+size+region entropy verified by the driver;
text layer is DOM-extract, volatile-masked — the transcription claim below is
the masked content file, not a hand caption):

* `07-gate-held.png` (332x262, content) — held cell: verbatim question,
  `requester: Isolated review workflow`, both option buttons, held-elapsed
  chip (masked `<HELD-CLOCK>` — this capture class is WHY the slice B run
  added the held-clock volatile mask: field-proven by set-1 breaking the
  double-run hash before the mask law widened).
* `08b-gate-error.png` (300x66, raster-only by design) — REAL `{ok:false}`
  fail-once door response rendered as the inline failure; driver asserts no
  `[data-gate-receipt]` appeared and the options came back retryable.
* `08-gate-pending.png` (300x32, raster-only by design) — `Saving answer…`
  while the second click's response is in flight on the door delay; driver
  asserts the option buttons were DISABLED (duplicate prevention).
* `10-gate-toast.png` (702x184 / set-2 690x180, content, SURFACE=toast) —
  `◇ Answer saved · Approve review · Isolated review workflow · <RUN-ID> /
  review · <DATE>` + `View exact gate`. The toast IS the receipt (review-2
  Q2 shape). The only frame on the `toast` surface.
* `09-gate-saved.png` (332x648, content) — durable receipt card incl.
  `Answered · <DATE>`, the nothing-restarted scope note, and the answer.
* `11-gate-after-view.png` (332x648, content) — the SAME receipt re-rendered
  after route-away (SESSIONS) and the toast's View-exact-gate jump: identity
  proof, never a bare list.

Ledger read-back both runs: `gates/review.json` answer byte-exact
(`Approve review`), `_ui: true`, `events.jsonl` sha256 byte-identical
before/after (record-only, nothing restarted), gate node never consumed
(`gate_node_committed: false` — runner was SIGKILLed at the hold).

Vision pass: `vision_analyze` timed out on every attempt at capture time
(loaded crew box); the manifest therefore keeps `reviewed:false` per the
honesty law — layout claims ride qri's #724 vision review of the identical
plugin bytes, and this PR makes no NEW layout claim (frames are the
artifact; text claims are machine-verified via the masked content layers).
