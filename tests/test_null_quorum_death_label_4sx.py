#!/usr/bin/env python3
"""est-4sx pin: null-quorum fan-out death must name the REAL cause.

The runner commits a fan-out on the implicit majority (len(items)//2+1,
sprint101 #12) when the graph declares no quorum; the projected graph shows
quorum:null while node.failed used to read bare 'quorum not met' — honest vs
runtime, misleading vs the projection (hm2 lap case-01). Pin the seam:
  1. null-quorum death text names fanout_timeout_majority_unmet + effective
     implicit threshold (candidate (b) of the row, since the effective quorum
     is unknowable in the pre-run projection — items don't exist yet);
  2. explicit-quorum death keeps the exact legacy text (retry copy stable);
  3. the runner seam routes through the helper (no bare string reappears at
     the node.failed quorum site).
Stdlib-only; PASS/FAIL lines; exit 0 = green.
"""
import importlib.util, os, sys, tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.environ.setdefault("HERMES_HOME", tempfile.mkdtemp())
spec = importlib.util.spec_from_file_location("wf_4sx", root / "wf.py")
assert spec and spec.loader
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and cond

lbl = wf._quorum_death_label
check("null-quorum death names fanout_timeout_majority_unmet",
      lbl(False, 3, 5) == "fanout_timeout_majority_unmet (implicit majority 3/5; quorum not declared)",
      lbl(False, 3, 5))
check("null-quorum death carries the EFFECTIVE threshold in the text",
      "3/5" in lbl(False, 3, 5) and "quorum not declared" in lbl(False, 3, 5))
check("explicit-quorum death keeps exact legacy text",
      lbl(True, 2, 5) == "quorum not met", lbl(True, 2, 5))
check("explicit-quorum death text is threshold-free (no projection lie either way)",
      "2/5" not in lbl(True, 2, 5))

src = (root / "wf.py").read_text()
seam = [ln for ln in src.splitlines() if 'log(run, "node.failed"' in ln and "quorum" in ln]
check("node.failed quorum site routes through the helper",
      len(seam) == 1 and "_quorum_death_label(bool(explicit_quorum)" in seam[0],
      (seam[0][:120] if seam else "no seam found"))
check("no bare error=\"quorum not met\" literal survives at any log seam",
      'error="quorum not met"' not in src)

print("ALL PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
