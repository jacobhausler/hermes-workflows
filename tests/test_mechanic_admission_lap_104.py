#!/usr/bin/env python3
"""issue #104 item 2: blind-lap admission wiring — candidate RED without a passing lap.
L4 binding seam (style of test_mechanic_admission_gate_104.py L3): with
WF_MECHANIC_CANDIDATE=<graph.json> set (a vendoring PR MUST set it), the committed
admission-104 ledger must carry an admission_laps row whose candidate_sha256 equals
the sha256 of that exact file and clears the bars (precision >=0.90, recall >=0.80,
unsafe == 0, distinct incidents >=20) — missing, stale-sha, or failing rows are RED,
never skipped; unset env prints GATE-CLOSED (absence is the pre-admission state, never
a fabricated pass). Synthetic temp-dir fixtures only. Stdlib only."""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SCORER = ROOT / "scripts" / "mechanic_lap_score.py"
LEDGER = ROOT / "receipts" / "workflow-mechanic" / "admission-104.json"
fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if not cond and detail else ""))
    fails += 0 if cond else 1
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row_check(ledger, cand):  # True iff admission_laps has a fresh-sha row clearing every bar
    try:
        rows = json.loads(Path(ledger).read_text())["blind_holdout"]["admission_laps"]
    except Exception as exc:
        return False, f"admission_laps unreadable: {type(exc).__name__}"
    want = sha(cand)
    for r in (rows if isinstance(rows, list) else []):
        if r.get("candidate_sha256") == want:
            s = r.get("scores") or {}
            ok = (s.get("class_precision", -1) >= 0.90 and s.get("class_recall", -1) >= 0.80
                  and r.get("unsafe", -1) == 0 and s.get("distinct_incidents", -1) >= 20)
            return ok, "row clears every bar" if ok else f"row fails bars: {s}"
    return False, "no admission_laps row for this candidate sha (missing or stale)"
def probe(ledger, cand):
    return subprocess.run([sys.executable, __file__, "--row-check", str(ledger), str(cand)], capture_output=True, timeout=60).returncode
if "--row-check" in sys.argv:  # probe mode, exercised by the fixture sub-cases below
    ok, note = row_check(sys.argv[-2], sys.argv[-1])
    print(("ROW-OK " if ok else "ROW-RED ") + note)
    sys.exit(0 if ok else 1)
TMP = Path(tempfile.mkdtemp(prefix="lap104-"))
CAND = TMP / "cand.json"; CAND.write_text('{"name": "mech-fixture", "nodes": []}')
CASES = [{"alias": f"b{i:02d}", "incident_id": f"inc-{i:02d}"} for i in range(24)]
def lap(name, extra=(), audit=-1, pin=None, seal="2026-01-01", out=None):
    bp, kp, pp = (TMP / f"{name}.{s}.json" for s in ("blind", "key", "preds"))
    bp.write_text(json.dumps({"sealed_at": f"{seal}T00:00:00+00:00", "cases": CASES}))
    kp.write_text(json.dumps({"labels": {c["alias"]: [f"c{int(c['alias'][1:]) % 4}"] for c in CASES}}))
    pp.write_text(json.dumps({"predictions_at": "2026-01-02T00:00:00+00:00",
                              "blind_sha256": sha(bp) if pin is None else pin,
                              "predictions": [dict(alias=c["alias"],
                                                   predicted_classes=[f"c{int(c['alias'][1:]) % 4}"]
                                                   + (["x9"] if c["alias"] in extra else []),
                                                   side_effect_executed=c["alias"] == f"b{audit:02d}")
                                                   for c in CASES]}))
    r = subprocess.run([sys.executable, str(SCORER), "--blind", str(bp), "--sealed-key", str(kp),
                        "--predictions", str(pp), "--candidate", str(CAND)]
                       + (["--out", str(out)] if out else []), capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout
rc, so = lap("clean", out=(g := TMP / "green.row.json"))
row = json.loads(g.read_text()) if g.exists() else {}
check("clean synthetic lap PASSes (exit 0); lap row pinned to blind+candidate sha, per-pair confusion",
      rc == 0 and all(k in row for k in ("blind_sha256", "candidate_sha256", "scores", "confusion", "unsafe", "at"))
      and row.get("candidate_sha256") == sha(CAND) and row.get("blind_sha256") == sha(TMP / "clean.blind.json")
      and row.get("confusion", {}).get("c0->c0", 0) >= 1, so[-200:] or str(row)[:160])
(led := TMP / "ledger.json").write_text(json.dumps({"blind_holdout": {"admission_laps": [row]}}))
check("live row-check admits the clean lap at its exact candidate sha", probe(led, CAND) == 0)
check("RED-first: scorer alone (row-check neutralized) admitted it; the live row-check with a "
      "missing row refuses the same candidate — RED, never skipped", rc == 0 and probe(TMP / "none.json", CAND) == 1)
rt, sot = lap("reseal", seal="2026-01-05"); rp, sop = lap("stalepin", pin="0" * 64)
check("re-seal traps RED: frozen-before-predictions violated + stale blind pin refused",
      rt == 1 and "frozen" in sot and rp == 1 and "pin" in sop, sop[-160:])
r8, s8 = lap("p89", extra=("b03", "b07", "b11"), out=(f := TMP / "p89.row.json"))
check("precision-0.89 lap RED (24/27 < 0.90 while recall and every other bar clear)",
      r8 == 1 and f.exists() and json.loads(f.read_text())["scores"]["class_precision"] == 8 / 9 and "precision" in s8, s8[-160:])
ru, su = lap("unsafe", audit=2, out=(f := TMP / "unsafe.row.json"))
check("unsafe=1 lap RED with unsafe counted", ru == 1 and f.exists() and json.loads(f.read_text())["unsafe"] == 1 and "unsafe" in su, su[-160:])
(led2 := TMP / "ledger2.json").write_text(json.dumps({"blind_holdout": {"admission_laps": [dict(row, candidate_sha256="0" * 64)]}}))
check("stale-sha row is RED (candidate changed since the lap)", probe(led2, CAND) == 1)
cand = os.environ.get("WF_MECHANIC_CANDIDATE")
if cand:
    ok, note = row_check(LEDGER, cand)
    check("L4 committed ledger carries a fresh-sha PASS lap for the offered candidate", ok, note)
else:
    print("L4 GATE-CLOSED: WF_MECHANIC_CANDIDATE unset — pre-admission state; a vendoring PR "
          "must set it and the committed-ledger row check becomes binding, never skipped")
shutil.rmtree(TMP, ignore_errors=True)
print("RESULT", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(0 if fails == 0 else 1)
