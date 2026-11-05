"""est-tscez: direct coverage for wf.clip_head_tail (zero test references at tip
026edf0). Sole caller is _clip_record's redact-then-clip walk (wf.py:717), so every
branch is pinned here at the function itself. Stdlib only, serial, no network.
Why the pointer lives here: AGENTS.md sits 135 chars under its 32,000 cap (pinned by
tests/test_docs_hint_cap_73c.py), so there is no AGENTS.md line to spend."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import wf

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

X = "0123456789" * 50  # 500 chars; the head/tail repeat makes any leak or slip visible
def marker(dropped, total, ceiling):
    return (f"…[clipped {dropped} of {total} chars; "
            f"head+tail retained; ceiling {ceiling}]…")

# 1. boundary pass-through: len==ceiling unchanged; len==ceiling+1 clips
check("len==ceiling passes through", wf.clip_head_tail(X[:80], 80) == X[:80])
r81 = wf.clip_head_tail(X[:81], 80)
check("len==ceiling+1 clips", r81 != X[:81] and len(r81) <= 80, r81)

# 2. marker content + ceiling hold for a 500-char text
for C, dropped in ((80, 480), (120, 441), (200, 361)):
    r = wf.clip_head_tail(X, C)
    check(f"C={C} carries {marker(dropped, 500, C)}", marker(dropped, 500, C) in r, r)
    check(f"C={C} result within ceiling", len(r) <= C, str(len(r)))

# 3. tiny-ceiling branch (ceiling < marker width): widest marker truncated to size
r10 = wf.clip_head_tail(X, 10)
check("ceiling 10 returns truncated widest marker", r10 == "…[clipped " and len(r10) == 10, r10)

# 4. odd-budget rounding: budget==1 at C=61 -> head=1/tail=0; the tail leg must NOT
# fall through to text[-0:] (that slice is the whole string). budget==3 at C=63 ->
# head=2/tail=1, so the last char survives.
check("C=61: head=1/tail=0, no text[-0:] whole-string leak",
      wf.clip_head_tail(X, 61) == X[:1] + marker(499, 500, 61), wf.clip_head_tail(X, 61))
check("C=63: head=2/tail=1 keeps the last char",
      wf.clip_head_tail(X, 63) == X[:2] + marker(497, 500, 63) + X[-1:],
      wf.clip_head_tail(X, 63))

# 5. re-clip idempotence (store promise: a clipped value is already under its ceiling)
for C in (10, 40, 80, 120, 200, 501):
    once = wf.clip_head_tail(X, C)
    check(f"clip(clip(x,{C}),{C}) == clip(x,{C})", wf.clip_head_tail(once, C) == once, once)

print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
