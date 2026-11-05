"""Direct coverage for wf.clip_head_tail (est-13fu5, census est-tscez): the 2026-11-05
export-reference census found 0 test references at tip 026edf0. The production caller is
the redact-then-clip walk _clip_record (wf.py:717, save_node), which bounds every run
record; these probes pin the ceiling contract the store's idempotence rests on. The
pointer rides this docstring because AGENTS.md has only 135 chars of headroom against
the 32,000 cap (test_docs_hint_cap_73c). Stdlib only, serial, no network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import wf

fails = 0
def check(label, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + label)
    fails += 0 if cond else 1

X = "x" * 500
def m(dropped, total, ceiling):  # independent oracle for the retention marker
    return f"…[clipped {dropped} of {total} chars; head+tail retained; ceiling {ceiling}]…"

# 1. boundary pass-through: within the ceiling unchanged, one over clips
check("len==ceiling passes through", wf.clip_head_tail("y" * 80, 80) == "y" * 80)
check("len==ceiling+1 clips", wf.clip_head_tail(X, 499) != X)

# 2. normal clip: marker names dropped/total/ceiling, result never over the ceiling
#    (dropped is 3 digits at these ceilings, so the widest marker has the same width)
for c in (80, 120, 200):
    budget = c - len(m(500, 500, c))
    r = wf.clip_head_tail(X, c)
    check(f"C={c}: len==ceiling and marker names {500 - budget}/500/{c}",
          len(r) == c and m(500 - budget, 500, c) in r
          and r.startswith(X[:(budget + 1) // 2]) and r.endswith(X[-(budget // 2):]))

# 3. tiny ceiling (< marker width): widest marker truncated to the ceiling
r10 = wf.clip_head_tail(X, 10)
check("C=10: marker[:10] branch", r10 == m(500, 500, 10)[:10] and len(r10) == 10)

# 4. odd-budget rounding: budget 1 -> head=1 tail=0 (no text[-0:] leak);
#    budget 3 -> head=2 tail=1
check("C=61: head=1 tail=0", wf.clip_head_tail(X, 61) == X[:1] + m(499, 500, 61))
check("C=63: head=2 tail=1", wf.clip_head_tail(X, 63) == X[:2] + m(497, 500, 63) + X[-1:])

# 5. re-clip idempotence across pass-through, tiny-ceiling and normal-clip shapes
check("re-clip idempotent", all(
    wf.clip_head_tail(wf.clip_head_tail(X, c), c) == wf.clip_head_tail(X, c)
    for c in (10, 40, 80, 120, 200, 501)))

print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
