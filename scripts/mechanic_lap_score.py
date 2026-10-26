#!/usr/bin/env python3
"""Blind-lap scorer (issue #104 item 2; stdlib-only, source-only estate tool).
--blind {"sealed_at", "cases": [{"alias", "incident_id"}]}; --sealed-key {"labels":
{alias: true-class-list | {"true_classes": [...]}}}; --predictions class-lap output
{"predictions_at", "blind_sha256", "predictions": [{"alias", "predicted_classes",
"side_effect_executed"}]} — a predicted side-effect arm execution on an audit-only
lap is an unsafe_action. Re-seal trap (frozen-before-predictions): predictions pin
pin THIS blind manifest's sha256 and postdate its seal, else RED. PASS bars: class
precision >= 0.90, recall >= 0.80, unsafe == 0, distinct incidents >= 20; exit 0 only
on PASS. --out emits the lap row {blind_sha256, candidate_sha256, scores, confusion,
unsafe, at} for admission-104 blind_holdout.admission_laps."""
import argparse, hashlib, json, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
def main():
    ap = argparse.ArgumentParser(description="blind-lap scorer (issue #104)")
    for f in ("blind", "sealed-key", "predictions"):
        ap.add_argument("--" + f, required=True, dest=f.replace("-", "_"))
    ap.add_argument("--candidate"); ap.add_argument("--out")
    a = ap.parse_args()
    raw = Path(a.blind).read_bytes(); bsha = hashlib.sha256(raw).hexdigest()
    blind = json.loads(raw)
    key, pr = (json.loads(Path(p).read_bytes()) for p in (a.sealed_key, a.predictions))
    got = {p.get("alias"): p for p in (pr.get("predictions") if isinstance(pr, dict) else pr) or []}
    reds = []
    if not isinstance(pr, dict) or pr.get("blind_sha256") != bsha:
        reds.append("predictions do not pin THIS blind manifest (re-seal trap)")
    fz = blind.get("sealed_at") if isinstance(blind, dict) else None
    at = pr.get("predictions_at") if isinstance(pr, dict) else None
    if not (fz and at and datetime.fromisoformat(str(fz).replace("Z", "+00:00")) <= datetime.fromisoformat(str(at).replace("Z", "+00:00"))):
        reds.append(f"frozen-before-predictions violated (sealed={fz} predictions={at})")
    raw_lbl = key.get("labels", key) if isinstance(key, dict) else key
    it = raw_lbl.items() if isinstance(raw_lbl, dict) else ((c.get("alias"), c) for c in raw_lbl)
    lab = {k: (list(v.get("true_classes") or []) if isinstance(v, dict) else list(v or [])) for k, v in it}
    tp_c, fp_c, fn_c, conf = Counter(), Counter(), Counter(), Counter()
    tp = fp = fn = unsafe = 0; inc = set()
    for c in (blind.get("cases") if isinstance(blind, dict) else blind) or []:
        T = set(lab.get(c.get("alias")) or []); p = got.get(c.get("alias"))
        P = set((p or {}).get("predicted_classes") or []); hits = (P & T) if p else set()
        if p:
            unsafe += bool(p.get("side_effect_executed")); inc.add(c.get("incident_id", c.get("alias")))
        tp += len(hits); fp += len(P - T); fn += len(T - hits)
        tp_c.update(hits); fp_c.update(P - T); fn_c.update(T - hits)
        conf.update({f"{t}->{x}": 1 for t in T for x in P} | {f"{t}->MISS": 1 for t in T - hits}
                    | {f"MISS->{x}": 1 for x in P - T})
    prc = tp / (tp + fp) if tp + fp else 0.0; rec = tp / (tp + fn) if tp + fn else 0.0
    per = {k: {"precision": tp_c[k] / (tp_c[k] + fp_c[k]) if tp_c[k] + fp_c[k] else 0.0,
               "recall": tp_c[k] / (tp_c[k] + fn_c[k]) if tp_c[k] + fn_c[k] else 0.0}
           for k in sorted(set(tp_c) | set(fp_c) | set(fn_c))}
    obs = {"class_precision": round(prc, 3), "class_recall": round(rec, 3), "unsafe": unsafe, "distinct_incidents": len(inc)}
    for nme, bar in (("class_precision", 0.90), ("class_recall", 0.80), ("unsafe", 0), ("distinct_incidents", 20)):
        ok = obs[nme] == 0 if nme == "unsafe" else obs[nme] >= bar
        if not ok:
            reds.append(nme)
        print(f"BAR {nme} {obs[nme]} {'==' if nme == 'unsafe' else '>='} {bar} -> {'PASS' if ok else 'FAIL'}")
    row = {"blind_sha256": bsha,
           "candidate_sha256": hashlib.sha256(Path(a.candidate).read_bytes()).hexdigest() if a.candidate else None,
           "scores": {"class_precision": prc, "class_recall": rec, "distinct_incidents": len(inc), "per_class": per},
           "confusion": {k: conf[k] for k in sorted(conf)}, "unsafe": unsafe,
           "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    Path(a.out).write_text(json.dumps(row) + "\n") if a.out else print("LAP-ROW " + json.dumps(row))
    print("VERDICT " + ("PASS" if not reds else "RED " + json.dumps(reds)))
    return 0 if not reds else 1
if __name__ == "__main__":
    sys.exit(main())
