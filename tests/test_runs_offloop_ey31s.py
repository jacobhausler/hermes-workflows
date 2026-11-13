#!/usr/bin/env python3
"""est-ey31s — the /runs census must not occupy the shared event loop, and
the same census must be scanned ONCE per short window, not once per poll.

Production measurement (rhuidean serve :9119, 2026-11-12): one GET /runs cost
1.06-1.29s over ~560 run dirs, SYNCHRONOUS inside an `async def` handler — so
it froze the event loop of the process that also hosts every agent lane, and
every other webui call queued behind it (the owner-visible "webui not
working"). /api/sessions already reads through sync def (threadpool); this
module was the outlier.

Behaviour pins (R6: no source-text pins):

  (R) every GET route in this module dispatches OFF the loop — the endpoint
      is a plain function (Starlette runs those in its worker threadpool);
      an `async def` there would run ON the loop. RED AT BASE: the GETs were
      coroutines. The gate-release POST stays async on purpose (write path,
      door answer flow) — its dispatch is pinned too, so the split is a
      stated contract rather than drift.
  (T) TTL snapshot: a route read inside the window reflects the ONE scan
      (a run seeded after it is invisible until the window passes), and the
      very next read after the window shows it. The cache key seam is the
      module's _monotonic (a fake clock, not sleep).
  (C) collapse: concurrent route reads over an empty cache pay EXACTLY ONE
      scan (double-checked lock), not N.
  (I) invalidation: the gate-release POST drops the snapshot even for an
      unknown id — a UI action must reflect in the next response, not one
      TTL window later.
  (P) pagination over ONE census: default answer keeps the pre-est-ey31s
      contract (newest-100 page, whole-census total/counts incl. executed,
      golden key set); offset/limit slice the page while total/counts stay
      census-wide; an offset past the end is an empty PAGE, not an empty
      census (no roots key).

Run: PYTHONPATH=/opt/hermes python3 tests/test_runs_offloop_ey31s.py
"""
import asyncio, importlib.util, json, os, shutil, sys, threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = Path(os.environ.get("TMPDIR", "/tmp")) / "wf-ey31s-offloop"
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


_seq = [0]
def seed_run(root, name, *, logs=False):
    """The 7ps8 valid-run trio (graph+run+node) — the smallest shape
    run_state accepts — plus optional non-empty logs/ (run_executed truth)."""
    r = root / name
    (r / "nodes").mkdir(parents=True)
    if logs:
        (r / "logs").mkdir()
        (r / "logs" / "a.log").write_text("line\n")
    (r / "graph.json").write_text(json.dumps({"name": name[-4:], "nodes": [
        {"id": "a", "type": "agent", "goal": "x"}]}))
    (r / "run.json").write_text(json.dumps({"run_id": name, "name": name[-4:],
                                            "started": "2099-01-01T00:00:00+00:00"}))
    (r / "nodes" / "a.json").write_text(json.dumps(
        {"status": "done", "output": {"answer": "ok"}, "efp": "",
         "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    return r


def rid(i):
    # name-DESC order is the traversal contract (iter_run_dirs): higher i sorts
    # earlier under reverse=True, so ids stay sortable-by-freshness here.
    return "20990101-%06d-ey31s" % (100000 + i)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dash = load("dashEy31s", ROOT / "dashboard" / "plugin_api.py")
if dash.router is None:
    print("SKIP fastapi unavailable in this interpreter (dashboard has no routes)")
    sys.exit(0)
dash._workflow_common().set_owner_setting_reader(
    lambda key: (str(RESOLVED) if key == "runs_root" else None))

routes = {r.path: r for r in dash.router.routes}

# ---------------------------------------------------------------- (R) dispatch
import inspect
for path in ("/runs", "/settings", "/runs/{run_id}", "/runs/{run_id}/nodes/{nid}/log"):
    ep = routes[path].endpoint
    check("(R) GET %s dispatches off the loop (plain def -> threadpool)" % path,
          not inspect.iscoroutinefunction(ep), "iscoroutine=%r" % inspect.iscoroutinefunction(ep))
check("(R) POST /runs/{run_id}/gate stays async (write path, stated)",
      inspect.iscoroutinefunction(routes["/runs/{run_id}/gate"].endpoint))

# seed a census: 5 resolved + 1 legacy, exactly 2 executed
for i in range(5):
    seed_run(RESOLVED, rid(i), logs=(i < 2))
seed_run(LEGACY, rid(9))

# --------------------------------------------------------- (T) TTL snapshot
clock = [1000.0]
dash._monotonic = lambda: clock[0]
dash._runs_cache_invalidate()

r1 = dash.list_runs(0, 100)
check("(T0) baseline census total counts all six dirs",
      r1["total"] == 6 and r1["counts"].get("executed") == 2, json.dumps(r1["counts"]))

seed_run(RESOLVED, rid(7))                       # a run appears mid-window
r2 = dash.list_runs(0, 100)
check("(T1) inside the TTL window a new run is NOT rescanned for",
      r2["total"] == 6, json.dumps(r2["counts"]))
clock[0] += dash.RUNS_CACHE_TTL + 0.01           # window passes (fake clock)
r3 = dash.list_runs(0, 100)
check("(T2) the first read after the window shows the new run",
      r3["total"] == 7 and any(x["id"] == rid(7) for x in r3["runs"]),
      json.dumps(r3["counts"]))

# ---------------------------------------------------------------- (C) collapse
scans = {"n": 0}
lk = threading.Lock()
_real_scan = dash._scan_runs
def slow_scan():
    with lk:
        scans["n"] += 1
    import time as _t
    _t.sleep(0.08)                               # hold the lock open for the race
    return _real_scan()
dash._scan_runs = slow_scan
dash._runs_cache_invalidate()
errs = []
def poll():
    try:
        out = dash.list_runs(0, 100)
        errs.append(None if out.get("total") == 7 else out.get("total"))
    except Exception as e:
        errs.append(repr(e))
threads = [threading.Thread(target=poll) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
check("(C) 8 concurrent reads over an empty cache pay exactly ONE scan",
      scans["n"] == 1 and all(e is None for e in errs), "scans=%d errs=%r" % (scans["n"], errs[:3]))
dash._scan_runs = _real_scan

# ---------------------------------------------------------------- (P) paging
check("(P1) limit slices the page, summary stays census-wide",
      [x["id"] for x in dash.list_runs(0, 2)["runs"]]
      == [x["id"] for x in r3["runs"][:2]]
      and dash.list_runs(0, 2)["total"] == 7, json.dumps(r3["counts"]))
mid = dash.list_runs(6, 2)
check("(P2) second page carries the tail (legacy-root row sits last: roots-arg order, est-1n7gx)",
      [x["id"] for x in mid["runs"]] == [rid(9)], [x["id"] for x in mid["runs"]])
past = dash.list_runs(99, 2)
check("(P3) offset past the end is an empty PAGE, not an empty census",
      past["runs"] == [] and past["total"] == 7 and "roots" not in past,
      json.dumps(sorted(past)))

# ------------------------------------------------ (K1) contract untouched
check("(K1) default answer keeps the pre-est-ey31s key set (golden-solo law)",
      set(r3) == {"runs", "total", "counts"} and r3["runs"], sorted(r3))

# ------------------------------------------------- (K2) direct reads stay live
dash._runs_cache_invalidate()
dash.list_runs(0, 100)                           # route fills the snapshot at total 7
seed_run(RESOLVED, rid(8))
check("(K2) direct _list_runs() answers live truth, route stays in its window",
      dash._list_runs()["total"] == 8 and dash.list_runs(0, 100)["total"] == 7,
      json.dumps({"direct": dash._list_runs()["total"], "route": dash.list_runs(0, 100)["total"]}))

# ---------------------------------------------------------------- (I) gate POST
dash._runs_cache_invalidate()
r4 = dash.list_runs(0, 100)                      # fills the snapshot (total 8)
seed_run(RESOLVED, rid(6))                       # invisible inside the window
ans = asyncio.run(dash.release_gate("no-such-run", {}))
r5 = dash.list_runs(0, 100)
check("(I) gate POST invalidates even for an unknown run — next read is fresh",
      ans.get("ok") is False and r5["total"] == 9, json.dumps({"ans": ans, "total": r5["total"]}))

print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
