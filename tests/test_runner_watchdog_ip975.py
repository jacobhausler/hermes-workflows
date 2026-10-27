#!/usr/bin/env python3
"""est-ip975: self-terminating singleton watchdog tick for dead-runner runs (PR-2).

The job lifecycle is PR-1's landed `cron_bridge.py` (name-keyed singleton,
find-then-create, delete-not-disable, bash shim under the scripts dir); this
test rides the whole bead acceptance THROUGH it:
  * exactly one named no_agent job while the active-run set is non-empty
  * the tick body self-deletes at drain (zero idle wakes: no job, no wakes)
  * an interrupted run (dead runner) is revived within one tick period
  * arm, drain-self-delete, and double-arm idempotence each have a check

No live cron store is touched: a fake `cron.jobs` module is injected into
sys.modules BEFORE any cron read (it satisfies cron_bridge's guarded `_jobs()`
seam), and the door's _spawn_runner is a spy (the launch spawn and the revival
spawn are the same door bridge, _respawn_runner -> _reap_silent_death ->
_spawn_runner). PR-1's tests/test_tick_bridge.py covers the lifecycle seam on
its own; this file proves the end-to-end wiring: boot arms, tick revives,
drain self-deletes.
"""
import importlib.util
import json
import os
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

failures = 0


def check(label, ok, detail=""):
    global failures
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else "  ::  " + str(detail)[:600]))
    failures += not ok


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_fake_cron(store):
    """Bind `cron.jobs` (the real and the injected path both) to the in-memory
    store, never to core."""
    jobs = types.ModuleType("cron.jobs")
    seq = {"n": 0}

    def create_job(prompt, schedule, name=None, repeat=None, deliver=None,
                   origin=None, script=None, no_agent=False, **kw):
        seq["n"] += 1
        job = {"id": f"fake-{seq['n']}", "name": name, "prompt": prompt,
               "schedule": schedule, "script": script, "no_agent": no_agent,
               "repeat": repeat, "deliver": deliver, "origin": origin}
        store["jobs"].append(job)
        return dict(job)

    def list_jobs(include_disabled=False):
        return [dict(j) for j in store["jobs"]]

    def remove_job(job_id):
        for j in list(store["jobs"]):
            if j["id"] == job_id:
                store["jobs"].remove(j)
                return True
        return False

    jobs.create_job = create_job
    jobs.list_jobs = list_jobs
    jobs.remove_job = remove_job
    pkg = types.ModuleType("cron")
    pkg.jobs = jobs
    sys.modules["cron"] = pkg
    sys.modules["cron.jobs"] = jobs
    return jobs


def uninstall_cron():
    return [sys.modules.pop(k, None) for k in ("cron", "cron.jobs")]


GRAPH = {"name": "wd-probe", "nodes": [
    {"id": "a", "type": "echo", "output": {"ok": True}}]}

with tempfile.TemporaryDirectory(prefix="wf-watchdog-") as scratch:
    home = Path(scratch)
    env_saved = {k: os.environ.get(k) for k in
                 ("HERMES_HOME", "WF_RUNS_ROOT", "WF_TICK_SCHEDULE")}
    os.environ["HERMES_HOME"] = str(home / "home")
    os.environ["WF_RUNS_ROOT"] = str(home / "runs")
    os.environ["WF_TICK_SCHEDULE"] = "every 1m"

    store = {"jobs": []}
    fake = install_fake_cron(store)
    # est-7ncu0 (#570, merged) refuses to bake a volatile wf.py into the persisted
    # shim — true in production (installed plugin root is stable) and here (worktree
    # is volatile). The test mirrors production: load the plugin from a stable-root
    # copy declared via WF_ARGV_STABLE_ROOTS, the guard's own override knob.
    STABLE = Path(tempfile.mkdtemp(prefix="wd-stable-"))
    STABLE.mkdir(exist_ok=True)
    import glob as _glob
    for src_f in _glob.glob(str(ROOT / "*.py")):
        (STABLE / Path(src_f).name).write_bytes(Path(src_f).read_bytes())
    os.environ["WF_ARGV_STABLE_ROOTS"] = str(STABLE)
    door = load("_hw_watchdog_door", STABLE / "__init__.py")
    import wf_test_isolation
    wf_test_isolation.install(door)
    cb = load("cron_bridge", STABLE / "cron_bridge.py")
    wd = load("runner_watchdog", STABLE / "runner_watchdog.py")
    wd.bind(door._common)

    spawns = []
    real_spawn = door._spawn_runner
    door._spawn_runner = lambda r: spawns.append(Path(r))

    try:
        # --- arm: the first RUNNER BOOT arms exactly one named no_agent job.
        # The arm moved off the door (measured ~5-6 s cold cron.jobs import inside
        # the lane flock breaks claim dedupe); this fakes the spawn and calls the
        # runner's own boot seam - the exact function wf.py main() runs. ---
        a = door.act_run({"graph": {**GRAPH, "name": "wd-arm-1"}})
        check("launch armed the watchdog tick", bool(a.get("run_id")), a)
        _wf = load("_hw_watchdog_wf", STABLE / "wf.py")
        _wf.arm_tick()
        jobs = [j for j in store["jobs"] if j["name"] == cb.TICK_NAME]
        check("exactly one named job after first launch", len(jobs) == 1, store["jobs"])
        job = jobs[0] if jobs else {}
        check("job is no_agent with no prompt",
              job.get("no_agent") is True and job.get("prompt") is None, job)
        check("armed cadence rides the WF_TICK_SCHEDULE resolution",
              job.get("schedule") == "every 1m", job)
        shim = Path(job.get("script") or "")
        check("shim lives under the hermes scripts dir and exists",
              shim.is_file() and shim.parent == (home / "home" / "scripts"), str(shim))
        check("shim is the bash shim execing this plugin's wf.py tick",
              shim.is_file() and str(STABLE / "wf.py") in shim.read_text()
              and shim.read_text().strip().split()[-1] == "tick", "")
        check("shim is executable", bool(shim.stat().st_mode & 0o111) if shim.is_file() else False, "")

        # --- double-arm idempotence: another launch, another direct ensure ---
        b = door.act_run({"graph": {**GRAPH, "name": "wd-arm-2"}})
        again = wd.ensure_tick()
        jobs = [j for j in store["jobs"] if j["name"] == cb.TICK_NAME]
        check("double-arm stays one job", len(jobs) == 1 and b.get("run_id"), (len(jobs), store["jobs"]))
        check("ensure_tick reports the incumbent id",
              again.get("armed") is True and again.get("id") == jobs[0]["id"], again)

        # --- tick revives a dead-runner run within one tick period (the
        # spy run reads `pending`: launched, runner never booted - the same
        # revival class act_wait drives for interrupted) ---
        del spawns[:]
        res = wd.tick(door=door)
        check("dead-runner run revived within one tick", spawns and spawns[0].name == a["run_id"],
              {"spawns": [str(s) for s in spawns], "res": res})
        check("tick reports the runs active and revived",
              res.get("active") == 2 and sorted(res.get("revived") or []) == sorted([a["run_id"], b["run_id"]]), res)
        check("watchdog stays armed while active",
              len([j for j in store["jobs"] if j["name"] == cb.TICK_NAME]) == 1, store["jobs"])

        # --- drain: terminal runs self-delete the job in the tick body ---
        for rid in (a["run_id"], b["run_id"]):
            with (home / "runs" / rid / "events.jsonl").open("a") as f:
                f.write(json.dumps({"ts": "2026-10-23T00:00:00+00:00", "event": "run.stopped"}) + "\n")
        res = wd.tick(door=door)
        check("drained tick self-deletes the job (zero idle wakes)",
              res.get("active") == 0 and store["jobs"] == [], {"res": res, "store": store["jobs"]})
        res2 = wd.tick(door=door)
        check("idle tick is a harmless no-op", res2.get("active") == 0 and store["jobs"] == [], res2)

        # --- core-less: a host without the cron store still launches runs ---
        saved = uninstall_cron()
        sys.modules["cron"] = None  # canonical force-ImportError pin
        c = door.act_run({"graph": {**GRAPH, "name": "wd-coreless"}})
        deg = wd.ensure_tick()
        check("core-less launch unaffected (fail-open)", bool(c.get("run_id")), c)
        check("core-less arm degrades honestly",
              deg.get("armed") is False and "reason" in deg, deg)
        uninstall_cron()
        install_fake_cron(store)
        # the core-less test run is still active; drain it before exiting
        with (home / "runs" / c["run_id"] / "events.jsonl").open("a") as f:
            f.write(json.dumps({"ts": "2026-10-23T00:00:00+00:00", "event": "run.stopped"}) + "\n")
        wd.tick(door=door)
        check("store drained clean at test end", store["jobs"] == [], store["jobs"])
    finally:
        door._spawn_runner = real_spawn
        for k, v in env_saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

sys.exit(1 if failures else 0)
