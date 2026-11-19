#!/usr/bin/env python3
"""hw-6og (1/4): the SEATS read surface — occupancy as a query.

Rows:
  A  units over hand-made ledgers: cap truth, live/dead/stranger holders,
     uncertain tickets, stale vs live queue markers, honest emptiness.
  B  door e2e: five real launches under a pool cap of 4 — the seats block
     reports cap/live/free and the fifth launch surfaces as a live queue
     entry; the read never prunes (tickets survive a holder's death); and
     the block is strictly opt-in (a plain status stays byte-identical).
Stdlib-only; prints PASS/FAIL lines; exit 0 = green.
"""
import importlib.util, json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
import wfcommon

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " + ("")[:0]) + label + ("" if cond or not detail else f"  {detail}")
          if not cond else "PASS " + label)
    ok = ok and cond

def boot_of(pid):
    return int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])

tmp = Path(tempfile.mkdtemp(prefix="seats6og-"))
S = tmp / "seats"
(S / wfcommon.SEAT_QUEUE_DIR).mkdir(parents=True)
now = time.time()
dead = subprocess.Popen([sys.executable, "-c", "pass"]); dead.wait()   # reaped: a dead pid

def ticket(name, pid, bt=None, child=None, cbt=None, ts=None):
    row = {"pid": pid, "name": name, "ts": ts if ts is not None else now - 5}
    if bt is not None: row["boottime"] = bt
    if child is not None: row["child"] = child; row["child_boottime"] = cbt
    (S / name + ".json" if False else S / f"{name}.json").write_text(json.dumps(row))

def marker(name, pid, bt=None, hb=None, enq=None):
    row = {"pid": pid, "name": name, "uuid": name, "enqueued": enq if enq is not None else now - 12}
    if bt is not None: row["boottime"] = bt
    row["hb"] = hb if hb is not None else now
    (S / wfcommon.SEAT_QUEUE_DIR / f"{name}.json").write_text(json.dumps(row))

(S / ".cap").write_text("6")
ticket("live.work", os.getpid(), bt=boot_of(os.getpid()))
ticket("legacy.work", os.getpid())                       # unpinned boottime: live
ticket("stranger.work", os.getpid(), bt=boot_of(os.getpid()) + 10_000_000)  # recycled pid
ticket("dead.work", dead.pid)
(S / "garbage.json").write_text("{")
marker("waiter.a", os.getpid(), bt=boot_of(os.getpid()))
marker("waiter.stale", os.getpid(), hb=now - 99)
marker("waiter.dead", dead.pid)
v = wfcommon.seats_view(S, now_s=now)
check("A cap rides from the pool-recorded file", v["cap"] == 6 and v["free"] == 6 - v["live"])
check("A live + legacy holders count; stranger and dead do not", v["live"] == 3,
      f"live={v['live']} holders={[h['name'] for h in v['holders']]}")
check("A unparseable ticket is uncertain capacity — counted", any(h["pid"] == os.getpid() for h in v["holders"]) and v["live"] == 3)
check("A holder names itself and its hold time", all("name" in h and h["held_for_s"] >= 0 for h in v["holders"]))
check("A only fresh-heartbeat live waiters are queued",
      [q["name"] for q in v["queued"]] == ["waiter.a"], f"queued={v['queued']}")
check("A the waiter reports its wait", v["queued"] and v["queued"][0]["waited_s"] > 10)
check("A the read is read-only (nothing pruned)", len(list(S.glob("*.json"))) == 5
      and len(list((S / wfcommon.SEAT_QUEUE_DIR).glob("*.json"))) == 3)
v2 = wfcommon.seats_view(tmp / "nowhere")
check("A an absent pool reads empty, cap unknown", v2 == {"dir": str(tmp / "nowhere"), "cap": None,
      "live": 0, "holders": [], "queued": []})
(S / ".cap").write_text("0")
check("A a disabled semaphore reports no numeric cap", wfcommon.seats_view(S)["cap"] is None)

# ---------- B: door e2e under a real pool ----------
env = {"WF_SEATS_DIR": str(tmp / "seats2"), "WORKFLOW_MAX_SEATS": "4",
       "WF_RUNS_ROOT": str(tmp / "runs"), "HERMES_HOME": str(tmp / "home"),
       "HERMES_WF_HERMES_BIN": str(root / "tests" / "fake"),
       "PYTHONDONTWRITEBYTECODE": "1"}
os.environ.update(env)
(tmp / "home").mkdir()
spec = importlib.util.spec_from_file_location("hw_seats6og", root / "__init__.py")
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
# Shelf-isolation law (test_shelf_isolation_71 S3): an in-process door writer
# must pin settings.runs_root alongside the env, not just the env.
sys.path.insert(0, str(root / "tests"))
import wf_test_isolation
wf_test_isolation.install(hw)

runners = []
def kill_runners():
    for p in runners:
        try: os.kill(p, signal.SIGKILL)
        except OSError: pass
import atexit; atexit.register(kill_runners)

rids = []
for i in range(5):
    out = hw.act_run({"graph": {"name": f"seats6og-r{i}",
                                "nodes": [{"id": "work", "type": "agent", "goal": "hold the seat QSLEEP 60"}]}})
    check(f"B launch r{i} ok", "run_id" in out, json.dumps(out)[:160])
    if "run_id" not in out: sys.exit(1)
    rids.append(out["run_id"])

deadline = time.time() + 40
view = {}
run_dirs = [hw._resolve_read_run(rid)[0] for rid in rids]
while time.time() < deadline:
    view = hw._common.seats_view(hw._seats_root())
    if view.get("live", 0) == 4 and len(view.get("queued", [])) >= 1:
        break
    time.sleep(0.5)
check("B the pool records the cap the first admission seeded", view.get("cap") == 4, f"view={view}")
check("B exactly the four admitted holders are live", view.get("live") == 4, f"live={view.get('live')}")
check("B free is cap minus live", view.get("free") == 0)
holder_pids = set()
for d in run_dirs:
    try: holder_pids.add(int((d / "wf.pid").read_text().strip()))
    except (OSError, ValueError): pass
check("B every reported holder is one of our runners",
      all(h["pid"] in holder_pids for h in view["holders"]) and len(view["holders"]) == 4,
      f"holders={view['holders']}")
check("B holders name their lane", all(str(h.get("name", "")).endswith(".work") for h in view["holders"]))
check("B the fifth launch is a visible queue entry",
      any(q.get("name", "").endswith(".work") and q.get("waited_s", -1) >= 0 for q in view["queued"]),
      f"queued={view['queued']}")
st = hw.act_status({"run_id": rids[0], "seats": True})
check("B status(seats:true) carries the block", isinstance(st.get("seats"), dict)
      and st["seats"]["dir"] == view["dir"] and st["seats"]["cap"] == 4)
st_plain = hw.act_status({"run_id": rids[0]})
check("B plain status stays byte-identical (no seats key)", "seats" not in st_plain)

# --- the no-prune law, on a quiet pool: kill every runner, settle, then read.
# (Live runners run their own two-pass pruner at acquire — that write-side
# hygiene must not race a read-side assertion.)
kill_runners(); time.sleep(0.8)
ghost = Path(env["WF_SEATS_DIR"]) / "ghost.work.json"
ghost.write_text(json.dumps({"pid": dead.pid, "name": "ghost.work", "ts": time.time()}))
before = sorted(p.name for p in Path(env["WF_SEATS_DIR"]).glob("*.json"))
q_view = hw._common.seats_view(hw._seats_root())
q_view2 = hw._common.seats_view(hw._seats_root())     # twice: steady state
after = sorted(p.name for p in Path(env["WF_SEATS_DIR"]).glob("*.json"))
check("B the read prunes nothing: dead tickets survive repeated reads", before == after,
      f"{len(before)} -> {len(after)}")
check("B a dead holder is absent from live while its file stands",
      ghost.exists() and all(h["pid"] != dead.pid for h in q_view["holders"])
      and q_view["live"] == q_view2["live"], f"live={q_view['live']}")
kill_runners()

print("seats_status_read_6og: " + ("OK" if ok else "FAILURE(S)"))
sys.exit(0 if ok else 1)
