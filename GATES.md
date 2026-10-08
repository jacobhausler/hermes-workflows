# GATES.md — fix/graph-orphan-deletion-aware-i24i (est-i24i)

Reconciles the deletion-PR graph orphan check with the graphify single-writer
gate (adversary 231 counterfactual, est-i24i).

## Gate 1 — RED-FIRST (red-tests)
- Test-only commit f140a8a adds tests/test_graph_orphan_deletion_231.py.
- RED run in a throwaway detached worktree of origin/main (a1a1eec) with the
  committed test copied in (lane-hygiene: no checkout-over-dirty-tree):
  `FAIL scripts/graph_orphans.py exists (the orphan library) ... FAIL 1`, rc=1.
- Replay of the adversary's counterfactual shape inside the new test
  (test_graph_gate on the deletion-PR tree) is part of the suite file and
  passes only with the library present.

## Gate 2 — green (targeted)
`python3 tests/test_graph_orphan_deletion_231.py` → ALL PASS (13 checks)
`python3 tests/test_graph_gate.py` → ALL PASS
`python3 tests/test_graph_single_writer_153.py` → ALL PASS (ban untouched)
`python3 tests/test_graphify_dedupe_27.py` → ALL PASS

## Gate 3 — suite
No full-suite result was recorded in this historical lane receipt; use exact-head CI for current suite status.

## Gate 4 — push
branch fix/graph-orphan-deletion-aware-i24i pushed to origin (first push before minute 25)

## Gate 5 — PR
Draft PR opened against main; @zingzapuj peer-stamp requested (no self-merge).
