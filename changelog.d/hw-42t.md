Steer delivery truth and wall truth (bd_2026-11-13-42t, E14+E24)

E14 — the steer.baked receipt now states the ONE guaranteed mechanism
(`mechanism: bake-at-spawn`) and COUNTS the budget cues drained for that spawn
(`drained_cues: N`). A budget cue is the dying generation's fact: the claim
file stamps which spawn earned it, and every LATER spawn DRAINS the inbox line
instead of re-baking it into the steer file or re-feeding it into the runner's
prompt injection — a stale 'budget left: N' can never lie against a fresh
budget. The drain is an event fact (`budget_cue.drained`), never a silent
swallow. The live pull stays an OPT-IN child seam: it happened exactly when a
`steer.consumed` event and the per-spawn cursor advance exist, never otherwise.
The fake seat's child interpreter is now the runner's own (`HERMES_WF_PYTHON`,
stamped at the spawn seam) so the pull seam survives on a seat whose
`/usr/bin/python3` predates the door's syntax — the reason s38 pull_count
scored zero on mac seats while every cursor stayed 0.

E24 — the declared node timeout is honored or clamped LOUDLY at bake time. An
effective wall below the author's number is a `node.timeout_clamped` event
naming declared-vs-effective and every reason that moved it (park_cap /
resume_wall / bake), never a silent min(). A death on the wall carries the same
account as prose AND structure: the failure text reads `timeout after Xs
(declared Ds, clamped at bake to Bs (park_cap), +Es extension grant (basis
S), died at effective Xs)` and the record gains a `wall_account` dict. The
adopted-child wall death names the same account (the one adopted grant, if it
moved the wall). The owner never sees a wall the author didn't write.

Behavior tests: tests/test_steer_delivery_truth_42t.py (S1 stale-cue drain on
the respawn bake + prompt channel, S2 live pull + cursor + spawn-env stamp) and
tests/test_wall_truth_42t.py (W1 grant-moved-the-wall death names
declared-vs-effective, W2 parked-respawn clamp event at the bake, W3 the
1500+750=2250 evidence phrase) — assert observable outcomes only. Golden
sanctioned deltas: `HERMES_WF_PYTHON` env key and the two new `steer.baked`
receipt fields are excluded both sides; presence is proven by the behavior
test, not the frozen capture. Idempotent: the budget-cue claim is O_EXCL per
(node,index) for the life of the run; the drain consumes the line exactly once.
