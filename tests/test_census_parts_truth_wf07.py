#!/usr/bin/env python3
"""WF-07 census truth: the /runs payload can never contradict itself.

QA read 'runs 7 - running 2 - held 0 - failed 8' with 38+ rows on the pane
census. Zoomed truth of that screenshot (report 10-M12): the glyph after
'runs' is a '?', not a '7' — the plugin reads counts.total, and the payload
answers total TOP-LEVEL (the WF-UI lane fixes that reader). The parts
observed (running 2, failed 8) sum to 10, comfortably <= the ~38-row census:
no part ever exceeded the total. Backend finding: the payload is provably
consistent — run_summary counts parts and total in ONE loop over the SAME
list _list_runs pages, so total == len(runs) >= every part is structural.
No backend change ships; this test pins the invariant so the next census
scare separates payload truth from reader bugs in one command.

Cases:
  (A) run_summary arithmetic (synthetic statuses, incl. the QA shape
      running 2 / held 1 / failed 8 / done 25): total == len(rows), every
      part <= total, status parts sum to total exactly, executed (supplied)
      <= total.
  (B) Endpoint through an isolated REAL _list_runs() (fresh private
      WF_RUNS_ROOT per process, test_measured_zero_7ps8 pattern): 2 done +
      1 failed + 1 pending (3 executed) -> total == len(page), counts match
      the page histogram key-for-key, every part <= total, executed <= total.
      Golden key set pinned: total rides TOP-LEVEL and counts never carries
      a total key — a UI reading counts.total renders '?', which is the
      WF-UI lane's bug, not a missing backend key (the v1.0.15 golden-solo
      key set {runs, total, counts} stays byte-identical).
  (C) Page-capped census (105 rows > the runs[:100] page): counts cover the
      FULL enumeration (parts sum to total == 105), the page is exactly 100
      rows, unique ids, and the page histogram is bounded component-wise by
      counts — page subset-of-scope, never a scope the parts disagree with.

Red discipline: green at base (the invariant already holds); the pin exists
so a future refactor that counts parts over the PAGE while total counts the
CENSUS — or vice versa — turns (C) red the moment page and scope diverge.

Run: python3 tests/test_census_parts_truth_wf07.py
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# --- hermetic env: fresh private runs root, inherited lane roots scrubbed --
BASE = Path(tempfile.mkdtemp(prefix="wf07-cpt-"))
RESOLVED = BASE / "resolved"   # settings-resolved root (scanned first)
LEGACY = BASE / "legacy"       # legacy launch root (scanned second)
RESOLVED.mkdir()
LEGACY.mkdir()
for k in [k for k in os.environ if k.startswith(("WF_", "HERMES_WF_"))]:
    os.environ.pop(k)  # scrub lane-exported roots; a hostile env must not steer us
os.environ["HERMES_HOME"] = str(BASE / "home")
os.environ["WF_RUNS_ROOT"] = str(LEGACY)   # launch_runs_root() answer
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else "  ::  " + str(detail)[:300]))
    if not cond:
        ok = False


def seed_run(root, name, status="pending", logs=False):
    """A VALID row whose run_state reads `status` (pending|done|failed).
    logs=True gives the dir a logs/ entry so run_executed counts it."""
    r = root / name
    (r / "nodes").mkdir(parents=True)
    if logs:
        (r / "logs").mkdir()
        (r / "logs" / "a.log").write_text("line\n")
    node = {"id": "a", "type": "agent", "goal": "x"}
    (r / "graph.json").write_text(json.dumps({"name": name[-4:], "nodes": [node]}))
    (r / "run.json").write_text(json.dumps({"run_id": name, "name": name[-4:],
                                            "started": "2099-01-01T00:00:00+00:00"}))
    if status in ("done", "failed"):
        (r / "nodes" / "a.json").write_text(json.dumps(
            {"status": status, "efp": wfcommon.efp({"a": node}, node),
             "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    return r


def fresh_dashboard():
    spec = importlib.util.spec_from_file_location("dash_wf07", str(ROOT / "dashboard" / "plugin_api.py"))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    d._workflow_common().set_owner_setting_reader(
        lambda key: (str(RESOLVED) if key == "runs_root" else None))
    return d


def invariants(payload, expect_total, page_capped=False):
    """The WF-07 law over one atomic payload: total == the full enumeration,
    every part <= total, and the page is a subset of the counted scope."""
    counts = payload["counts"]
    page = payload["runs"]
    parts = {k: v for k, v in counts.items() if k != "executed"}
    check("total answers TOP-LEVEL and matches the full census",
          payload.get("total") == expect_total, json.dumps({k: payload.get(k) for k in ("total",)}))
    check("total == sum(status parts) — one enumeration, no double count",
          sum(parts.values()) == payload["total"], json.dumps(parts))
    check("every counts part <= total (no 'failed 8' inside 'runs 7')",
          all(v <= payload["total"] for v in parts.values()), json.dumps(parts))
    check("executed (when supplied) <= total",
          counts.get("executed", 0) <= payload["total"], json.dumps(counts))
    hist = {}
    for row in page:
        hist[row["status"]] = hist.get(row["status"], 0) + 1
    check("page histogram is bounded component-wise by counts (page subset-of-scope)",
          all(v <= counts.get(k, 0) for k, v in hist.items()), json.dumps({"page": hist, "counts": counts}))
    check("page rows carry unique ids",
          len({r["id"] for r in page}) == len(page))
    if not page_capped:
        check("uncapped census: page == full enumeration", len(page) == payload["total"],
              f"page={len(page)} total={payload['total']}")


# ------------------------------------------------- (A) run_summary arithmetic
rows = ([{"status": "running"}] * 2 + [{"status": "held"}] + [{"status": "failed"}] * 8
        + [{"status": "done"}] * 25)
summ = wfcommon.run_summary(rows, executed=12)
check("(A1) total == len(rows)", summ["total"] == len(rows) == 36, summ["total"])
check("(A2) the QA census shape itself satisfies total >= every part",
      summ["counts"]["running"] == 2 and summ["counts"]["failed"] == 8 and summ["counts"]["held"] == 1
      and all(v <= summ["total"] for k, v in summ["counts"].items() if k != "executed"),
      json.dumps(summ["counts"]))
check("(A3) status parts sum to total exactly (parts can never outrun total)",
      sum(v for k, v in summ["counts"].items() if k != "executed") == summ["total"], json.dumps(summ["counts"]))
check("(A4) run_summary never mirrors total inside counts (the 'runs ?' half is a reader bug, WF-UI lane)",
      "total" not in summ["counts"], json.dumps(summ["counts"]))

# ------------------------------------------------- (B) real _list_runs, capped nowhere
seed_run(RESOLVED, "20990101-000001-dn1", "done", logs=True)
seed_run(RESOLVED, "20990101-000002-dn2", "done", logs=True)
seed_run(RESOLVED, "20990101-000003-fa1", "failed", logs=True)
seed_run(RESOLVED, "20990101-000004-pd1", "pending")          # fixture: not executed
p = fresh_dashboard()._list_runs()
check("(B1) payload key set is the golden {runs, total, counts}",
      sorted(p.keys()) == ["counts", "runs", "total"], json.dumps(sorted(p.keys())))
invariants(p, expect_total=4)
check("(B2) counts match the seeded census key-for-key",
      p["counts"] == {"running": 0, "done": 2, "failed": 1, "pending": 1, "executed": 3},
      json.dumps(p["counts"]))

# ------------------------------------------------- (C) page-capped full census
for i in range(101):                                          # 4 + 101 == 105 rows
    seed_run(RESOLVED, f"20981231-235900-pad{i:03d}", "pending")
p = fresh_dashboard()._list_runs()
check("(C1) capped page is exactly 100 rows while the census keeps its full total",
      len(p["runs"]) == 100 and p["total"] == 105, f"page={len(p['runs'])} total={p['total']}")
invariants(p, expect_total=105, page_capped=True)
check("(C2) counts cover the FULL census, not the page (pending 102 = 101 pads + 1 fixture)",
      p["counts"].get("pending") == 102 and p["counts"].get("executed") == 3, json.dumps(p["counts"]))

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
