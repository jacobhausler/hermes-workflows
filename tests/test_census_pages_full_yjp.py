#!/usr/bin/env python3
"""bd_2026-11-13-yjp: the >100-row page-walk contract of GET /runs.

est-ey31s (pin P) proved the route CAN page; the desktop transport never
walked the pages, so a full-census promise silently stopped at the first
window of 100. This test is the acceptance floor for the client-side walk
(mirrored behaviorally in tests/test_census_full_fetch_yjp.mjs against the
real transport): with a census LARGER than one page, the client's bounded
offset loop reaches EVERY counted run exactly once, and every page answers
the SAME census-wide summary — the global summary is distinct from the
loaded rows on every slice.

Pins:
  (W1) 137 rows > 1 page; the loop offset 0,100(,...) partitions the census
       exactly: no duplicate id, no lost row, order matches the snapshot.
  (W2) every page carries the same whole-census total/counts (summary is
       not page-local) and the golden key set {runs,total,counts} — no new
       public keys on the route.
  (W3) the DEFAULT call (route defaults offset=0, limit=100) is exactly the
       newest-100 window plus the whole-census summary — the pre-yjp payload,
       unchanged (this is what made the first-page ceiling invisible).
  (W4) inside the TTL window the walk is ONE snapshot: a run seeded between
       two page calls is invisible to the rest of that walk (pages cannot
       disagree mid-walk); after the window the next read shows it.
  (W5) an offset past the end is an empty PAGE (no roots key, census-wide
       total) — 'roots' stays the empty-census-only hint.
  (W6) empty census still answers roots + zero-count summary.

Run: python3 tests/test_census_pages_full_yjp.py
"""
import importlib.util, json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = Path(os.environ.get("TMPDIR", "/tmp")) / "wf-yjp-census-pages"
shutil.rmtree(BASE, ignore_errors=True)
RESOLVED = BASE / "resolved"
LEGACY = BASE / "legacy"
for d in (RESOLVED, LEGACY):
    d.mkdir(parents=True)
os.environ["HERMES_HOME"] = str(BASE / "home")
os.environ["WF_RUNS_ROOT"] = str(LEGACY)   # launch_runs_root() answer
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else "  ::  " + str(detail)[:300]))
    ok = ok and bool(cond)


def seed_run(root, name):
    """The valid-run trio (graph+run+node) — smallest shape run_state accepts."""
    r = root / name
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": name[-4:], "nodes": [
        {"id": "a", "type": "agent", "goal": "x"}]}))
    (r / "run.json").write_text(json.dumps({"run_id": name, "name": name[-4:],
                                           "started": "2099-01-01T00:00:00+00:00"}))
    (r / "nodes" / "a.json").write_text(json.dumps(
        {"status": "done", "output": {"answer": "ok"}, "efp": "",
         "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    return r


def rid(i):
    # name-DESC traversal (iter_run_dirs, reverse=True): higher i sorts earlier,
    # so window order equals reverse-i order — the exactness checks stay boring.
    return "20990101-%06d-yjp" % (100000 + i)


spec = importlib.util.spec_from_file_location("dashYjpPages", str(ROOT / "dashboard" / "plugin_api.py"))
dash = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dash)
if dash.router is None:
    print("SKIP fastapi unavailable in this interpreter (dashboard has no routes)")
    sys.exit(0)
dash._workflow_common().set_owner_setting_reader(
    lambda key: (str(RESOLVED) if key == "runs_root" else None))

clock = [1000.0]
dash._monotonic = lambda: clock[0]

N = 137
for i in range(N - 1):
    seed_run(RESOLVED, rid(i))
seed_run(LEGACY, rid(99999))          # the legacy-root row sits last (roots-arg order)
dash._runs_cache_invalidate()
all_ids = [rid(i) for i in reversed(range(N - 1))] + [rid(99999)]

# (W1) the client's bounded walk: offsets 0,100,200 partition the census.
seen, windows = [], []
off = 0
while True:
    page = dash.list_runs(off, 100)
    windows.append(page)
    ids = [x["id"] for x in page["runs"]]
    seen.extend(ids)
    if len(ids) < 100:
        break
    off += len(ids)
check("(W1) the walk reaches every counted run — no duplicate, no lost page",
      seen == all_ids, json.dumps({"seen": len(seen), "pages": len(windows)}))
check("(W1b) the counted total is reachable: total == len(union of pages)",
      windows[0]["total"] == len(seen) == N, windows[0]["total"])

# (W2) one whole-census summary on every page; golden key set.
check("(W2) every page answers the SAME census-wide summary",
      all(p["total"] == N and p["counts"].get("running", 0) == 0 for p in windows),
      json.dumps([p.get("total") for p in windows]))
check("(W2b) golden key set on a page (no new public keys)",
      all(set(p) == {"runs", "total", "counts"} for p in windows),
      json.dumps(sorted(set(windows[1]))))

# (W3) the default call is the first window plus the whole-census summary.
default = dash.list_runs(0, 100)
check("(W3) default window = newest 100 rows, summary stays census-wide",
      [x["id"] for x in default["runs"]] == all_ids[:100] and default["total"] == N,
      json.dumps({"first": default["runs"][0]["id"], "n": len(default["runs"])}))

# (W4) one snapshot per walk: a mid-window seeding cannot split the walk.
seed_run(RESOLVED, rid(500))                        # sorts into the FIRST window
p_a = dash.list_runs(0, 100)
p_b = dash.list_runs(100, 100)
check("(W4) inside the TTL window the walk stays on ONE scan (new run invisible)",
      p_a["total"] == N and all(x["id"] != rid(500) for x in p_a["runs"])
      and [x["id"] for x in p_a["runs"]] + [x["id"] for x in p_b["runs"]] == all_ids,
      json.dumps({"a": p_a["total"], "b": p_b["total"]}))
clock[0] += dash.RUNS_CACHE_TTL + 0.01
check("(W4b) after the window the next read rescans (138 counted)",
      dash.list_runs(0, 100)["total"] == N + 1)

# (W5) offset past the end: empty PAGE, not empty census.
past = dash.list_runs(999, 100)
check("(W5) offset past the end is an empty page with census-wide total, no roots",
      past["runs"] == [] and past["total"] == N + 1 and "roots" not in past,
      json.dumps(sorted(past)))

# (W6) an empty census answers roots + measured-zero summary (unchanged).
EMPTY_LEGACY = BASE / "empty-legacy"
EMPTY_LEGACY.mkdir()
os.environ["WF_RUNS_ROOT"] = str(EMPTY_LEGACY)   # launch root moves too, or its row leaks in
dash._workflow_common().set_owner_setting_reader(
    lambda key: (str(BASE / "later") if key == "runs_root" else None))
dash._runs_cache_invalidate()
empty = dash.list_runs(0, 100)
check("(W6) empty census names its roots and answers total 0 (measured zero)",
      empty["runs"] == [] and empty["total"] == 0
      and any(Path(x).resolve() == (BASE / "later").resolve() for x in empty.get("roots", [])),
      json.dumps(empty)[:200])

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
