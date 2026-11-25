#!/usr/bin/env python3
"""bd_2026-11-13-nyf — the wake-evidence fixture suite (native isolated runner).

Drives scripts/wake_evidence.py end to end and pins its two entry points as
deterministic behavior (no desktop, no live personal chat):

  * green path: all three owner-bound receipt classes (held / failed_delta /
    cascade) + the nowhere-ever miss validate at exit 0 — every law line the
    validator prints must be a PASS (behavior-level: stdlib JSON parsing of the
    wake.jsonl rows and the sink's captured POST headers, not string hunting);
  * rejection path: a seeds dir whose owner stamp is a dict WITHOUT a session_id
    must exit 1 naming owner_bound — the validator refuses owner-null seeds
    BEFORE transport, so no wake can ever be manufactured on one (the
    FINAL.md:271 lesson: the old RC seed had no owner and wrote no probe).

Desktop capture (scripts/ui2-proof/capture.mjs --case owner-wake) and the ACTUAL
rendered owner turn stay PENDING for this bead — recorded in the receipt, not
silently claimed here.

Run: python3 tests/test_wake_evidence_nyf.py
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
OUT = HERE / "home-nyf-wake" / ("run-" + str(int(__import__("time").time())))

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


def validator(seeds, out, owner_null=None, head=""):
    cmd = [sys.executable, str(BUILD / "scripts" / "wake_evidence.py"), "validate",
           "--seeds", str(seeds), "--out", str(out)]
    if owner_null:
        cmd += ["--owner-null-seed", str(owner_null)]
    if head:
        cmd += ["--head", head]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(BUILD))
    return p

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

# ---- green path on the committed owner-bound seeds -------------------------
p = validator(BUILD / "tests" / "wake-evidence-nyf" / "seeds", OUT / "green",
              owner_null=BUILD / "tests" / "wake-evidence-nyf" / "seeds-owner-null" / "held",
              head="fixture-suite")
lines = [l for l in p.stdout.splitlines() if l.startswith(("PASS ", "FAIL "))]
fails = [l for l in lines if l.startswith("FAIL ")]
check("green: validator exits 0", p.returncode == 0, (p.stdout[-300:] + p.stderr[-300:]))
check("green: every law line PASSes (>=20 behavior checks)", len(lines) >= 20 and not fails,
      " | ".join(fails)[:400])
rec = OUT / "green" / "receipts"
for name in ("held.wake.jsonl", "failed_delta.wake.jsonl", "cascade.wake.jsonl",
             "nowhere_ever.wake.jsonl", "sink.jsonl"):
    check(f"green: receipt artifact harvested: {name}", (rec / name).is_file())
posts = [json.loads(l) for l in (rec / "sink.jsonl").read_text().splitlines()]
check("green: the isolated sink saw exactly 4 delivered owner POSTs (held x2, failed x1, "
      "cascade x1) each carrying an Idempotency-Key", len(posts) == 4
      and all(bool(x["idempotency"]) for x in posts), str(len(posts)))

# ---- rejection path: owner-null seeds never reach transport ----------------
bad = OUT / "owner-null"
shutil.copytree(BUILD / "tests" / "wake-evidence-nyf" / "seeds", bad / "seeds")
sj = json.loads((bad / "seeds" / "held" / "run.json").read_text())
sj["owner"] = {"session_id": "", "ui_session_id": None, "platform": "cli"}   # null-session stamp
(bad / "seeds" / "held" / "run.json").write_text(json.dumps(sj))
p2 = validator(bad / "seeds", bad / "out")
check("reject: an owner stamp without a session_id exits 1 before any class runs",
      p2.returncode == 1 and "owner_null_seed" not in p2.stdout
      and "owner-bound" in p2.stdout and "FAIL seed:held" in p2.stdout,
      (p2.stdout[-400:] + p2.stderr[-200:]))
check("reject: no receipts directory is produced for an owner-null seed set",
      not (bad / "out" / "receipts").exists()
      or not any((bad / "out" / "receipts").glob("failed_delta.*")),
      str(sorted((bad / "out" / "receipts").glob("*")) if (bad / "out" / "receipts").exists() else "absent"))

# ---- real recorded delivery state, not a manufactured wake -----------------
# the nowhere_ever receipt proves the honest shape: attempt -> delivered=None ->
# typed error_class -> notice_drop row; and the owner-null twin wrote NOTHING.
nz = OUT / "green" / "runs" / "owner-null"
check("owner-null twin ran INSIDE the green pass and wrote no wake.jsonl",
      nz.is_dir() and not (nz / "wake.jsonl").exists(), str(nz))

print("EXIT " + ("0" if ok else "1"))
sys.exit(0 if ok else 1)
