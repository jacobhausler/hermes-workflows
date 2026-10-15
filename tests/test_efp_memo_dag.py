#!/usr/bin/env python3
"""efp DAG-memo test — the memo must be exact, must collapse rehashing, and must
never move a verdict.

Contracts pinned (a perf fix must never change the law):
  A exactness: for a diamond, every node's efp under a shared memo equals the
    un-memoized value, under BOTH fingerprint rules.
  B collapse: sweeping a K-wide layered diamond counts def_hash at most one def
    per node with a memo, while the un-memoized sweep strictly exceeds it — and
    the gap widens with depth (the exponential the memo removes).
  C malformed cyclic byid: a memoized sweep answers exactly what an un-memoized
    sweep answers (cycle law byte-identical, memo merely unused there).
  D memo lifecycle: reusing one memo across reads of the SAME graph is stable;
    an amended def read under a FRESH memo shows the new efp and propagates to
    downstream nodes (memo lifetime is the caller's contract, per the docstring).

Run: cd tests && python3 test_efp_memo_dag.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import wfcommon

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " if cond is False else "ERR  ") + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and cond is True

def agent(nid, after):
    return {"id": nid, "type": "agent", "goal": f"goal {nid}", "after": list(after)}

def layered(k, depth, offset=0):
    """K-wide fully-connected layer graph: every node of layer i+1 depends on ALL
    of layer i — each adjacent layer pair is a stack of diamonds."""
    nodes, prev = [], []
    for d in range(depth):
        cur = []
        for j in range(k):
            nid = f"n{offset}_{d}_{j}"
            nodes.append(agent(nid, prev))
            cur.append(nid)
        prev = cur
    return nodes

def sweep(nodes, memo):
    byid = {n["id"]: n for n in nodes}
    return {n["id"]: wfcommon.efp(byid, n, memo=memo) for n in nodes}

def count_defhash(fn):
    real, box = wfcommon.def_hash, [0]
    def counting(node, rule=wfcommon.FP_RULE_VERSION):
        box[0] += 1
        return real(node, rule)
    wfcommon.def_hash = counting
    try:
        fn()
    finally:
        wfcommon.def_hash = real
    return box[0]

# ---- A. exactness on a diamond, both rules ----
diamond = [agent("a", []), agent("b", ["a"]), agent("c", ["a"]),
           agent("d", ["b", "c"]), agent("e", ["b", "c"]),
           agent("f", ["d", "e"])]
byid = {n["id"]: n for n in diamond}
for rule in wfcommon.FP_RULES:
    plain = {n["id"]: wfcommon.efp(byid, n, rule=rule) for n in diamond}
    memoized = {n["id"]: wfcommon.efp(byid, n, rule=rule, memo={}) for n in diamond}
    diff = {k: (plain[k], memoized[k]) for k in plain if plain[k] != memoized[k]}
    check(f"A exact under shared memo (rule {rule})", plain == memoized, repr(diff))

# ---- B. collapse and widening gap on layered diamonds ----
ratios = []
for depth in (3, 5):
    g = layered(4, depth)
    base = count_defhash(lambda: sweep(g, None))
    memo = count_defhash(lambda: sweep(g, {}))
    check(f"B memo hashes at most one def per node (depth {depth})",
          memo <= len(g), f"{memo} def hashes vs {len(g)} nodes")
    check(f"B unmemoized strictly exceeds memo (depth {depth})", base > memo, f"{base} vs {memo}")
    ratios.append(base / memo)
check("B gap widens with depth (un-memoized growth is exponential)", ratios[1] > ratios[0],
      f"depth3 {ratios[0]:.1f}x -> depth5 {ratios[1]:.1f}x")

# ---- C. malformed cyclic byid: law byte-identical with or without memo ----
cyc = [agent("x", ["z"]), agent("y", ["x"]), agent("z", ["y"])]
check("C cyclic byid: memoized sweep == un-memoized sweep",
      sweep(cyc, {}) == sweep(cyc, None))

# ---- D. memo lifecycle ----
m = {}
first, second = sweep(diamond, m), sweep(diamond, m)
check("D same memo reused on the same graph is stable", first == second == sweep(diamond, None))
gB = [dict(n) for n in diamond]
next(n for n in gB if n["id"] == "b")["goal"] = "AMENDED goal b"
b_new = sweep(gB, {})
check("D fresh memo sees the amended def (not the stale hash)",
      b_new["b"] != first["b"] and b_new["b"] == sweep(gB, None)["b"])
check("D amend propagates downstream through the memo path",
      b_new["f"] != first["f"] and b_new["f"] == sweep(gB, None)["f"])

sys.exit(0 if ok else 1)
