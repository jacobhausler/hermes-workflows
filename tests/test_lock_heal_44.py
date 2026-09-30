"""#44: runner.lock stranded with NO visible holder after a gateway sweep.

The A1 liveness probe took LOCK_EX|LOCK_NB *inside the door (gateway) process*.
A gateway SIGKILLed mid-probe — with the probe fd inherited across a spawn into
another pid-namespace view — left the flock held by nobody we can see: /proc/locks
no inode line, /proc/*/fd scan empty, runner pid dead, wait-resume wedged forever.

Contract pinned here (the fix):
  CHILD-PROBE  every probe a long-lived process makes against runner.lock runs in a
               short-lived CHILD (open, LOCK_EX|LOCK_NB, exit) — the child's death is
               the release; the parent NEVER holds the probe fd, so nothing it spawns
               can inherit it and no SIGKILL of the parent can strand the lock.
  ONE-READ     door status/list/wait still consume the ONE published runner_live
               (A2, 91b9a3de) — one status call == at most ONE child-probe.
  ESCAPE HATCH wf.py release-lock <run_id> / door action release_lock: refuses (exit 2)
               unless runner pid dead AND not held/parked AND two child-probes 100 ms
               apart both acquire; never unlinks; a contested probe prints the holder
               evidence; a kernel-held lock with zero visible holders is reported as
               STRANDED with the honest 'new lane key' recovery, never a fake success.
Standalone (no pytest): PYTHONPATH=/opt/hermes python tests/test_lock_heal_44.py
"""
import importlib.util, json, os, shutil, signal, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
home = HERE / "home44"
if home.exists():
    shutil.rmtree(home)
home.mkdir()
os.environ["HERMES_HOME"] = str(home)
os.environ.pop("WF_RUNS_ROOT", None)
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}"
    ok += 1; print("PASS", msg)

runs = home / "workflows"; runs.mkdir(exist_ok=True)

def mkrun(name, pid=None, held_gate=False):
    r = runs / name
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True)
    nodes = [{"id": "a", "type": "agent", "goal": "JSON:{\"result\":\"ok\"}"}]
    if held_gate:
        nodes.append({"id": "g", "type": "gate", "after": ["a"], "question": "go?", "options": ["yes", "no"]})
        byid = {n["id"]: n for n in nodes}
        (r / "nodes" / "a.json").write_text(json.dumps({"status": "done", "output": {"result": "ok"},
                                                        "efp": wfcommon.efp(byid, byid["a"]),
                                                        "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    (r / "graph.json").write_text(json.dumps({"name": name, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"name": name}))
    (r / "runner.lock").write_text("")   # the runner's admission file, currently unheld
    if pid is not None:
        (r / "wf.pid").write_text(str(pid))
    return r

HOLDER = str(home / "holder_44.py")   # scratch home, never tests/ (a collector would run it)
Path(HOLDER).write_text(
    "import fcntl, os, sys, time\n"
    "fd = os.open(sys.argv[1], os.O_RDWR)\n"
    "fcntl.flock(fd, fcntl.LOCK_EX)\n"
    "print('held', flush=True)\n"
    "time.sleep(float(sys.argv[2]))\n")

def hold(r, secs=30):
    p = subprocess.Popen([sys.executable, HOLDER, str(r / "runner.lock"), str(secs)],
                         stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "held", "holder failed to take the flock"
    return p

def wf_release_lock(rid):
    p = subprocess.run([sys.executable, str(BUILD / "wf.py"), "release-lock", rid],
                       capture_output=True, text=True, timeout=30,
                       env={**os.environ, "HERMES_HOME": str(home)})
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        out = {"_raw": p.stdout, "_err": p.stderr}
    return p.returncode, out

# --- (a) THE PIN: holder SIGKILLed mid-hold => a following child-probe reads FREE ----
ra = mkrun("h44-killed", pid=999999)
lk = ra / "runner.lock"
h = hold(ra)
check(wfcommon.lock_probe_child(str(lk)) == "busy", "child-probe reads BUSY while the holder lives")
h.send_signal(signal.SIGKILL); h.wait()
deadline = time.monotonic() + 5
while wfcommon.lock_probe_child(str(lk)) != "free" and time.monotonic() < deadline:
    time.sleep(0.05)
check(wfcommon.lock_probe_child(str(lk)) == "free",
      "SIGKILLed holder -> child-probe reads FREE (the fd died with the holder; nothing stranded)")
check(wfcommon.runner_alive(ra) is False, "and the ONE liveness predicate reads dead")

# --- (a') the incident shape itself: a PROBING parent SIGKILLed mid-probe cannot strand.
# The pre-fix door held the probe fd in-process; a sweep that killed it mid-flight
# (with the fd leaked across a spawn) left the lock held by a ghost. With the
# child-probe the parent never owns the fd, so killing it at ANY instant leaves free.
PROBER = str(home / "prober_44.py")
Path(PROBER).write_text(
    "import os, sys, time\n"
    f"sys.path.insert(0, {str(BUILD)!r})\n"
    "import wfcommon\n"
    "print('go', flush=True)\n"
    "while True:\n"
    "    wfcommon.runner_lock_held(sys.argv[1])\n")
for i in range(5):
    pr = subprocess.Popen([sys.executable, PROBER, str(ra)], stdout=subprocess.PIPE, text=True)
    assert pr.stdout.readline().strip() == "go"
    time.sleep(0.02 + 0.007 * i)      # land the kill at different phases of the probe loop
    pr.send_signal(signal.SIGKILL); pr.wait()
time.sleep(0.2)
check(wfcommon.lock_probe_child(str(lk)) == "free",
      "a probing parent SIGKILLed mid-probe (x5, staggered) never strands the lock")

# --- (b) live holder => probe BUSY, release-lock REFUSES with holder evidence --------
rb = mkrun("h44-live", pid=999999)
hb = hold(rb)
try:
    check(wfcommon.lock_probe_child(str(rb / "runner.lock")) == "busy", "live holder -> child-probe BUSY")
    check(wfcommon.runner_alive(rb) is True, "held lock reads LIVE (A1/A2 law untouched)")
    v = wfcommon.release_lock_verdict(rb)
    check(v["ok"] is False and v["lock"] == "busy", "release-lock verdict refuses a contested lock", v)
    fx = v.get("forensics") or {}
    pids = {int(x["pid"]) for x in fx.get("fd_holders", [])}
    check(hb.pid in pids, "refusal carries the holder evidence (/proc/*/fd scan names the holder pid)", fx)
    check(any(str(fx.get("inode")) in ln for ln in fx.get("proc_locks", [])) or fx.get("proc_locks") == [],
          "forensics carry the /proc/locks lines for the inode (or an honest empty)", fx)
    check(not v.get("stranded"), "a VISIBLE holder is contention, not the stranded case", v)
    rc, out = wf_release_lock(rb.name)
    check(rc == 2 and out.get("ok") is False, "wf.py release-lock exits 2 on a contested lock", (rc, out))
    check((rb / "runner.lock").exists(), "refusal never unlinks the lock file")
finally:
    hb.kill(); hb.wait()

# --- (c) runner pid ALIVE => refuse even when the lock is free ----------------------
sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
try:
    rc_ = mkrun("h44-pidalive", pid=sleeper.pid)
    v = wfcommon.release_lock_verdict(rc_)
    check(v["ok"] is False and "pid" in v["reason"] and str(sleeper.pid) in v["reason"],
          "release-lock refuses while the recorded runner pid is alive (names the pid)", v)
    rc, out = wf_release_lock(rc_.name)
    check(rc == 2, "wf.py release-lock exits 2 while the runner pid is alive", (rc, out))
finally:
    sleeper.kill(); sleeper.wait()

# --- (c') a held (human gate) run keeps its parked-runner contract: refuse ----------
rg = mkrun("h44-held", pid=999999, held_gate=True)
st = wfcommon.run_state(rg)
check(st["status"] == "held", "fixture is a held run", st["status"])
v = wfcommon.release_lock_verdict(rg)
check(v["ok"] is False and "held" in v["reason"], "release-lock refuses a run held at a gate", v)

# --- (d) holder killed => double-probe (100 ms apart) both free => reported free ----
rd = mkrun("h44-freed", pid=999999)
hd = hold(rd)
v = wfcommon.release_lock_verdict(rd)
check(v["ok"] is False, "contested first", v)
hd.kill(); hd.wait(); time.sleep(0.2)
t0 = time.monotonic()
v = wfcommon.release_lock_verdict(rd)
el = time.monotonic() - t0
check(v["ok"] is True and v["lock"] == "free" and v["probes"] == ["free", "free"],
      "after the holder dies: two consecutive child-probes acquire -> reported FREE", v)
check(el >= 0.1, "the two probes really were ~100 ms apart (not one probe echoed)", f"{el:.3f}s")
check((rd / "runner.lock").exists(), "success never unlinks the lock file either (nothing to race)")
rc, out = wf_release_lock(rd.name)
check(rc == 0 and out.get("ok") is True and out.get("probes") == ["free", "free"],
      "wf.py release-lock exits 0 and reports free", (rc, out))

# --- (d') door passthrough: action release_lock ------------------------------------
spec = importlib.util.spec_from_file_location("hw44", BUILD / "__init__.py")
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
door = json.loads(hw.handle({"action": "release_lock", "run_id": rd.name}))
check(door.get("ok") is True and door.get("probes") == ["free", "free"], "door release_lock passes the verdict through", door)
hb2 = hold(rd)
try:
    door = json.loads(hw.handle({"action": "release_lock", "run_id": rd.name}))
    check(door.get("ok") is False and door.get("lock") == "busy" and hb2.pid in
          {int(x["pid"]) for x in (door.get("forensics") or {}).get("fd_holders", [])},
          "door release_lock refuses a contested lock with the holder evidence", door)
finally:
    hb2.kill(); hb2.wait()
check(json.loads(hw.handle({"action": "release_lock", "run_id": "no-such-run-44"})).get("error"),
      "door release_lock on an unknown run is an error, not a verdict")

# --- (e) A2 one-read: one door status == at most ONE child-probe; parent holds nothing
import fcntl
calls = []
_real_probe = hw._common.lock_probe_child
def _counting(path, *a, **k):
    calls.append(str(path)); return _real_probe(path, *a, **k)
hw._common.lock_probe_child = _counting
_real_flock = fcntl.flock
inproc = []
fcntl.flock = lambda *a, **k: (inproc.append(a), _real_flock(*a, **k))[1]
try:
    for action in ("status", "list"):
        calls.clear(); inproc.clear()
        out = json.loads(hw.handle({"action": action, "run_id": rd.name}))
        n = sum(1 for c in calls if c == str(rd / "runner.lock"))
        check(n <= 1, f"door {action}: at most ONE child-probe for the run (A2 one-read law)", f"probes={n}")
        check("runner_live" in (out if action == "status" else out["runs"][0]),
              f"door {action}: consumers read the published runner_live field")
        check(not any(str(rd / "runner.lock") in str(a) for a in inproc),
              f"door {action}: the door process itself NEVER flocks runner.lock (child-probe only)")
    calls.clear()
    st = hw.run_state(rd)
    check(sum(1 for c in calls if c == str(rd / "runner.lock")) == 1 and st["runner_live"] is False,
          "run_state derives runner_live from exactly ONE child-probe")
    fds = [os.readlink(f"/proc/self/fd/{f}") for f in os.listdir("/proc/self/fd") if os.path.islink(f"/proc/self/fd/{f}")]
    check(not any(str(rd / "runner.lock") in x for x in fds),
          "the parent holds NO fd on runner.lock after probing (nothing to inherit across a spawn)")
finally:
    hw._common.lock_probe_child = _real_probe
    fcntl.flock = _real_flock

# --- (f) the stranded case is reported HONESTLY, never as a fake success ------------
rs = mkrun("h44-stranded", pid=999999)
_orig = wfcommon.lock_probe_child
wfcommon.lock_probe_child = lambda path, *a, **k: "busy"   # kernel says held; nobody visible
try:
    v = wfcommon.release_lock_verdict(rs)
    check(v["ok"] is False and v.get("stranded") is True and "lane key" in v["reason"],
          "kernel-held + zero visible holders => STRANDED verdict names the only recovery (new lane key)", v)
    check((v.get("forensics") or {}).get("fd_holders") == [] and v["forensics"].get("runner_pid_alive") is False,
          "the stranded verdict carries the forensic dump (empty fd scan, dead pid)", v)
finally:
    wfcommon.lock_probe_child = _orig

# --- (h) #47 review C1: probe 'unknown' is NEVER free (tri-state liveness) ----------
# The A1/A2 false-'interrupted' class: holder ALIVE + probe child cannot answer
# (hang, SIGKILL, fork EAGAIN) -> lock_probe_child 'unknown' -> the pre-fix bool
# predicate collapsed unknown into dead: runner_alive False, status 'interrupted',
# runner_live False — exactly the fb-squad shape, violating the docstring law
# 'a held probe can only ever ADD liveness, never remove it'.
# CHOSEN SHAPE (documented, reviewer-preferred): TRI-STATE — unknown => runner_live
# None + liveness 'probe-timeout'|'probe-failed'; fail-closed-means-held could wedge
# the whole list behind a hung flock binary, so unknown reads as UNKNOWN (never free,
# never held), status must not claim 'interrupted', and `next`/wait REFUSE to resume.
rh = mkrun("h44-unknown", pid=999999)
lk_h = rh / "runner.lock"
hh = hold(rh)
_fakebin = home / "bin_44"; _fakebin.mkdir(exist_ok=True)
_real_path = os.environ["PATH"]; _real_probe_defaults = wfcommon.lock_probe_child.__defaults__
try:
    wfcommon.lock_probe_child.__defaults__ = (1.0,)   # bound the hanging probes in this section
    def _unknown_pins(tag):
        alive = wfcommon.runner_alive(rh)
        st = wfcommon.run_state(rh)
        assert isinstance(st, dict), f"(h/{tag}) run_state returned {st!r}"
        check(alive is not False, f"(h/{tag}) holder alive + probe broken => runner_alive is NOT False", repr(alive))
        check(st.get("runner_live") is None, f"(h/{tag}) run_state publishes runner_live None (never False)", repr(st.get("runner_live")))
        check(st.get("status") != "interrupted", f"(h/{tag}) status must never claim 'interrupted' on a probe failure", st.get("status"))
        check(st.get("liveness") in ("probe-timeout", "probe-failed"),
              f"(h/{tag}) run_state names the liveness cause", repr(st.get("liveness")))
    # (a) probe child hangs: shadow `flock` on PATH with a sleeper (fs-stall shape)
    (_fakebin / "flock").write_text("#!/bin/sh\nsleep 30\n"); (_fakebin / "flock").chmod(0o755)
    os.environ["PATH"] = f"{_fakebin}:{_real_path}"; wfcommon._FLOCK_BIN = None
    check(wfcommon.lock_probe_child(str(lk_h)) == "unknown", "(h/a) hanging probe child -> 'unknown' (bounded)")
    _unknown_pins("a-hang")
    # (b) probe child SIGKILLed mid-run (kill -9 $$)
    (_fakebin / "flock").write_text("#!/bin/sh\nkill -9 $$\n"); (_fakebin / "flock").chmod(0o755)
    wfcommon._FLOCK_BIN = None
    check(wfcommon.lock_probe_child(str(lk_h)) == "unknown", "(h/b) SIGKILLed probe child -> 'unknown'")
    _unknown_pins("b-kill9")
    # (c) the probe child cannot even fork: subprocess.run raises OSError(EAGAIN)
    os.environ["PATH"] = _real_path; wfcommon._FLOCK_BIN = None
    _real_sp_run = wfcommon.subprocess.run
    def _eagain(argv, *a, **k):
        if argv and "flock" in str(argv[0]):
            raise OSError(11, "Resource temporarily unavailable")
        return _real_sp_run(argv, *a, **k)
    wfcommon.subprocess.run = _eagain
    try:
        check(wfcommon.lock_probe_child(str(lk_h)) == "unknown", "(h/c) probe fork EAGAIN -> 'unknown'")
        _unknown_pins("c-eagain")
        # door level under the fork failure: status refuses wait, wait refuses to spawn
        _spawned = []
        _real_spawn = hw._spawn_runner
        hw._spawn_runner = lambda r: _spawned.append(str(r))
        try:
            out = json.loads(hw.handle({"action": "status", "run_id": rh.name}))
            check(out["runner_live"] is None and out["status"] != "interrupted",
                  "(h/c) door status: runner_live None, status not 'interrupted'",
                  json.dumps({k: out.get(k) for k in ("status", "runner_live")}))
            check(out.get("next") != [{"action": "wait"}] and not any(
                      (row or {}).get("action") == "wait" for row in out.get("next") or []),
                  "(h/c) `next` must NOT say wait on an unknown liveness", json.dumps(out.get("next")))
            w = json.loads(hw.handle({"action": "wait", "run_id": rh.name, "timeout": 1}))
            check(not _spawned and w.get("runner_live") is None,
                  "(h/c) wait REFUSES to spawn on unknown (unknown is never free)",
                  json.dumps({"spawned": _spawned, "runner_live": w.get("runner_live")}))
        finally:
            hw._spawn_runner = _real_spawn
    finally:
        wfcommon.subprocess.run = _real_sp_run
    # the refusal must not wedge forever: once the probe can run again, truth returns
    check(wfcommon.runner_alive(rh) is True, "(h) recovered probe reads the live holder again (no permanent wedge)")
finally:
    os.environ["PATH"] = _real_path
    wfcommon.lock_probe_child.__defaults__ = _real_probe_defaults
    wfcommon._FLOCK_BIN = None
    hh.kill(); hh.wait()

# --- (i) #47 review C2: the list probe is BATCHED — one child per list call ----------
ri_runs = [mkrun(f"h44-batch-{i}", pid=999999) for i in range(50)]
hb_i = hold(ri_runs[7])
try:
    verdicts = wfcommon.lock_probe_children([str(r / "runner.lock") for r in ri_runs])
    check(isinstance(verdicts, dict) and len(verdicts) == 50,
          "lock_probe_children(paths) -> {path: verdict} for every path", len(verdicts))
    check(verdicts[str(ri_runs[7] / "runner.lock")] == "busy"
          and all(verdicts[str(r / "runner.lock")] == "free" for r in ri_runs[:7] + ri_runs[8:]),
          "the batch reports BUSY for the held lock and FREE for the rest")
    _batch_spawns = []
    _real_run_i = wfcommon.subprocess.run
    def _count_i(argv, *a, **k):
        _batch_spawns.append(list(argv)); return _real_run_i(argv, *a, **k)
    wfcommon.subprocess.run = _count_i
    try:
        wfcommon.lock_probe_children([str(r / "runner.lock") for r in ri_runs])
    finally:
        wfcommon.subprocess.run = _real_run_i
    check(len(_batch_spawns) <= 1,
          "N paths == AT MOST ONE probe child (batched; not one fork per run)", f"children={len(_batch_spawns)}")
    # door act_list: 50 runs == at most ONE probe child for the whole call
    door_spawns = []
    _real_run_d = hw._common.subprocess.run
    def _count_d(argv, *a, **k):
        door_spawns.append(list(argv)); return _real_run_d(argv, *a, **k)
    _real_spawn_d = hw._spawn_runner
    hw._spawn_runner = lambda r: None   # list must never spawn anyway; pin it loudly
    hw._common.subprocess.run = _count_d
    try:
        out = json.loads(hw.handle({"action": "list"}))
    finally:
        hw._common.subprocess.run = _real_run_d
        hw._spawn_runner = _real_spawn_d
    n_probe_children = sum(1 for a in door_spawns if "flock" in str(a[:1]) or "-S" in a[:4])
    rows = {row["run_id"]: row for row in out["runs"]}
    check(len(out["runs"]) == 50 and all(r["run_id"] in rows for r in ri_runs),
          "the door lists all 50 synthetic runs", len(out["runs"]))
    check(rows[ri_runs[7].name]["runner_live"] is True
          and all(rows[r.name]["runner_live"] is False for r in ri_runs if r is not ri_runs[7]),
          "act_list threads the ONE batch verdict into every row (held=True, rest False)")
    check(n_probe_children <= 1,
          "ONE list call == at most ONE probe child spawned (fork-cost pin, #47 C2)",
          f"probe children={n_probe_children} of {len(door_spawns)} subprocess.run")
    check(not any("runner.lock" in str(a) and str(a[0]).endswith("flock") for a in door_spawns),
          "act_list never forks a per-run flock probe child (batch child only)")
finally:
    hb_i.kill(); hb_i.wait()

# --- (g) probe hygiene: no lock-file creation, bounded, env-clean --------------------
rm = mkrun("h44-missing", pid=999999)
(rm / "runner.lock").unlink()
check(wfcommon.lock_probe_child(str(rm / "runner.lock")) == "missing" and not (rm / "runner.lock").exists(),
      "a missing lock file probes 'missing' and is never created by the probe")
check(wfcommon.runner_alive(rm) is False, "missing lock + dead pid reads dead (absence law unchanged)")
v = wfcommon.release_lock_verdict(rm)
check(v["ok"] is True and v["lock"] == "missing", "release-lock on a missing lock file: nothing held, ok", v)
src = (BUILD / "wfcommon.py").read_text()
region = src[src.index("def lock_probe_child"):src.index("def _runner_pid_alive")]
check("close_fds=True" in region and "env={}" in region and "timeout=" in region,
      "the child-probe inherits nothing dangerous (close_fds, empty env) and is bounded")
check("os.O_CREAT" not in region, "no probe path ever creates a lock file")

print(f"ALL PASS ({ok})")
