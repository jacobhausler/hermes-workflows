#!/usr/bin/env python3
"""E23 (bd_2026-11-13-3qo): runner death is loud and clean, through the tick.

Pins the observable outcomes of the reap leg of `runner_watchdog.tick`:
  * a SIGKILLed runner (dead wf.pid + a node record claiming running) wakes
    the OWNER SESSION within the same tick, naming the dead pid, the lost
    lane and the re-drive plan (delivery rides an injected wake_native stub
    in the stable-root copy; the wake.jsonl row is the receipt),
  * the same death scene never wakes twice (dedupe by the scene tid),
  * no wf.pid and no lanes/*.json entry outlives its holders (terminal runs
    and dir-gone claims are pruned under the entry's own lock; an unfinished
    run keeps its claim),
  * a re-drive the tick cannot perform (wedged-lock heal refusal) becomes a
    one-shot `redrive.request` continuation with a FIXED expiry; the consumer
    enforces it: past-due is dropped with a `watchdog.redrive_expired` event
    and never re-fired from an old receipt (the launchd-treadmill law); a
    successful re-drive consumes the continuation exactly once.

The cron store is the same injected fake as test_runner_watchdog_ip975 (the
cron_bridge `_jobs()` seam); the door's spawn is a spy, so revival is
observed without booting runners.
"""
import importlib.util
import json
import os
import sys
import tempfile
import time
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


WAKE_STUB = '''
import json, os
SCHEMA = "stub-admission/v1"
def deliver(sid, text, tid, home):
    with open(os.environ["STUB_WAKE_CALLS"], "a") as f:
        f.write(json.dumps({"sid": sid, "text": text, "tid": tid}) + "\\n")
    return {"outcome": "delivered", "admission_id": "stub-1", "status": "queued"}
'''

GRAPH = {"name": "wd3qo-probe", "nodes": [
    {"id": "a", "type": "echo", "output": {"ok": True}}]}

with tempfile.TemporaryDirectory(prefix="wf-deathloud-") as scratch:
    home = Path(scratch)
    env_saved = {k: os.environ.get(k) for k in
                 ("HERMES_HOME", "WF_RUNS_ROOT", "WF_TICK_SCHEDULE",
                  "WF_OWNER_SESSION", "STUB_WAKE_CALLS", "WF_ARGV_STABLE_ROOTS",
                  "WF_REDRIVE_TTL_S")}
    os.environ["HERMES_HOME"] = str(home / "home")
    os.environ["WF_RUNS_ROOT"] = str(home / "runs")
    os.environ["WF_TICK_SCHEDULE"] = "every 1m"
    os.environ["WF_OWNER_SESSION"] = "sess-reap-owner"
    os.environ["WF_REDRIVE_TTL_S"] = "3600"
    calls = home / "wake_calls.jsonl"
    os.environ["STUB_WAKE_CALLS"] = str(calls)

    store = {"jobs": []}
    install_fake_cron(store)
    STABLE = Path(tempfile.mkdtemp(prefix="wd3qo-stable-"))
    import glob as _glob
    for src_f in _glob.glob(str(ROOT / "*.py")):
        (STABLE / Path(src_f).name).write_bytes(Path(src_f).read_bytes())
    (STABLE / "wake_native.py").write_text(WAKE_STUB)
    # macOS: TMPDIR lives under a symlinked /var; declare both spellings so the
    # residency guard's raw-and-resolved both check the same fixture root.
    os.environ["WF_ARGV_STABLE_ROOTS"] = os.pathsep.join(
        (str(STABLE), str(STABLE.resolve())))
    door = load("_hw_deathloud_door", STABLE / "__init__.py")
    import wf_test_isolation
    wf_test_isolation.install(door)
    wd = load("runner_watchdog", STABLE / "runner_watchdog.py")
    wd.bind(door._common)

    spawns = []
    real_spawn = door._spawn_runner
    door._spawn_runner = lambda r: spawns.append(Path(r))

    def dead_pid():
        for cand in range(999999, 999000, -1):
            try:
                os.kill(cand, 0)
            except ProcessLookupError:
                return cand
            except OSError:
                return cand
        raise RuntimeError("no free pid")

    DEAD = dead_pid()

    def events(rid):
        p = Path(home) / "runs" / rid / "events.jsonl"
        out = []
        try:
            for line in p.read_text().splitlines():
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
        except OSError:
            pass
        return out

    def wake_calls():
        if not calls.is_file():
            return []
        return [json.loads(x) for x in calls.read_text().splitlines() if x.strip()]

    try:
        # --- RUN A: the SIGKILL scene — dead wf.pid, one lane claiming running.
        a = door.act_run({"graph": {**GRAPH, "name": "wd3qo-a"}, "lane_key": "wd3qo-a"})
        ra = Path(home) / "runs" / a["run_id"]
        (ra / "wf.pid").write_text(str(DEAD))
        (ra / "nodes").mkdir(exist_ok=True)
        (ra / "nodes" / "a.json").write_text(json.dumps(
            {"status": "running", "pid": DEAD, "node": "a", "attempt": 1, "skey": "s1"}))
        with (ra / "events.jsonl").open("a") as f:
            f.write(json.dumps({"ts": "2026-11-13T00:00:00+00:00", "event": "run.started"}) + "\n")

        # --- RUN B: terminal corpse — stopped, dead wf.pid, lane claim.
        b = door.act_run({"graph": {**GRAPH, "name": "wd3qo-b"}, "lane_key": "wd3qo-b"})
        rb = Path(home) / "runs" / b["run_id"]
        (rb / "wf.pid").write_text(str(DEAD))
        with (rb / "events.jsonl").open("a") as f:
            f.write(json.dumps({"ts": "2026-11-13T00:00:00+00:00", "event": "run.stopped"}) + "\n")

        # --- RUN C: wedged-lock revival refusal -> scheduled (not performed) re-drive.
        c = door.act_run({"graph": {**GRAPH, "name": "wd3qo-c"}})
        rc = Path(home) / "runs" / c["run_id"]
        (rc / "wf.pid").write_text(str(DEAD))
        common = door._common
        real_lock_states, real_heal = common.runner_lock_states, common.heal_wedged_runner_lock

        def wedged_states(runs):
            out = dict(real_lock_states(runs))
            for x in runs:
                if Path(x).name == c["run_id"]:
                    out[x] = ("wedged", {"errno": 11, "stub": True})
            return out
        common.runner_lock_states = wedged_states
        common.heal_wedged_runner_lock = lambda r, **kw: {"reason": "live holder"}

        # --- tick 1: A wakes loudly; C's re-drive is scheduled; B is pruned.
        del spawns[:]
        out1 = wd.tick(door=door)
        check("tick 1 respawned the death-scene run", spawns and spawns[0].name == a["run_id"], spawns)
        wk = {w["run"]: w for w in out1.get("wakes") or []}
        check("tick 1 reports one reap wake naming pid and lane",
              a["run_id"] in wk and wk[a["run_id"]]["pid"] == DEAD
              and wk[a["run_id"]]["lanes"] == ["a"]
              and wk[a["run_id"]]["wake"] == "delivered", out1)
        cc = wake_calls()
        check("owner session woken within one tick, naming dead pid + lane + plan",
              len(cc) == 1 and cc[0]["sid"] == "sess-reap-owner"
              and str(DEAD) in cc[0]["text"] and "a" in cc[0]["text"]
              and "respawned" in cc[0]["text"]
              and "grants no new scope and revokes no existing authority" in cc[0]["text"],
              cc)
        wrows = [json.loads(x) for x in (ra / "wake.jsonl").read_text().splitlines()]
        check("the wake receipt row is on the ledger, deduped by scene tid",
              len(wrows) == 1 and wrows[0]["id"] == f"{a['run_id']}|runner.reaped|{DEAD}"
              and wrows[0]["delivered"] is True, wrows)
        check("the wedged-refused run carries a scheduled re-drive with an expiry",
              (rc / "redrive.request").is_file()
              and json.loads((rc / "redrive.request").read_text())["expires_at"] > time.time(),
              events(c["run_id"]))
        check("the scheduling is on the event record",
              any(e.get("event") == "watchdog.redrive_scheduled" for e in events(c["run_id"])),
              events(c["run_id"]))
        check("holders-dead: the stopped run's wf.pid corpse is pruned",
              not (rb / "wf.pid").exists(), sorted(p.name for p in rb.iterdir()))
        lane_b = (Path(home) / "runs" / "lanes")
        lane_files = sorted(p.name for p in lane_b.glob("*.json"))
        import hashlib
        stem_a = hashlib.sha256(b"wd3qo-a").hexdigest()[:16]
        stem_b = hashlib.sha256(b"wd3qo-b").hexdigest()[:16]
        check("the terminal run's lane claim is pruned, the live run's kept",
              (lane_b / f"{stem_a}.json").is_file()
              and not (lane_b / f"{stem_b}.json").exists()
              and (lane_b / f"{stem_b}.lock").is_file(), lane_files)

        # --- tick 2: the same scene never wakes twice; the continuation refreshes
        # without extending its fixed expiry.
        del spawns[:]
        before = json.loads((rc / "redrive.request").read_text())
        out2 = wd.tick(door=door)
        check("a repeat sighting of the same death scene does not re-wake",
              len(wake_calls()) == 1
              and {w["run"]: w["wake"] for w in out2.get("wakes") or []}.get(a["run_id"]) == "deduped",
              out2)
        after = json.loads((rc / "redrive.request").read_text())
        check("refreshing a continuation counts tries, never extends the expiry",
              after["tries"] == 2 and after["expires_at"] == before["expires_at"], after)

        # --- expiry is enforced by the consumer, on the receipt: backdate past due.
        (rc / "redrive.request").write_text(json.dumps(
            {"at": time.time() - 7200, "expires_at": time.time() - 10,
             "reason": "wedged runner lock: heal refused", "tries": 9}))
        wd.tick(door=door)
        check("a past-due continuation is dropped and never re-fired",
              any(e.get("event") == "watchdog.redrive_expired" for e in events(c["run_id"])),
              events(c["run_id"]))
        fresh = json.loads((rc / "redrive.request").read_text())
        check("the re-scheduled continuation is a fresh one-shot, not the old receipt",
              fresh["tries"] == 1 and fresh["expires_at"] > time.time(), fresh)

        # --- un-wedge: the re-drive is consumed exactly once by the revival.
        common.runner_lock_states = real_lock_states
        common.heal_wedged_runner_lock = real_heal
        (rc / "nodes").mkdir(exist_ok=True)
        (rc / "nodes" / "a.json").write_text(json.dumps({"status": "running", "pid": DEAD}))
        del spawns[:]
        wd.tick(door=door)
        check("revival consumes the scheduled re-drive (one-shot)",
              c["run_id"] in [s.name for s in spawns] and not (rc / "redrive.request").exists(),
              spawns)
        check("the consumed scene woke its owner naming the interruption",
              len(wake_calls()) == 2
              and json.loads(calls.read_text().splitlines()[-1])["tid"]
              == f"{c['run_id']}|runner.reaped|{DEAD}", wake_calls())
        out4 = wd.tick(door=door)
        check("a rerun converges: no second delivery for a settled scene",
              len(wake_calls()) == 2
              and all(w["wake"] == "deduped" for w in out4.get("wakes") or [])
              and out4.get("wakes") != [], out4)

        # --- drain keeps working through the new legs.
        for rid in (a["run_id"], c["run_id"]):
            with (Path(home) / "runs" / rid / "events.jsonl").open("a") as f:
                f.write(json.dumps({"ts": "2026-11-13T00:00:00+00:00", "event": "run.stopped"}) + "\n")
        out5 = wd.tick(door=door)
        check("drained tick still self-deletes the job",
              out5.get("active") == 0 and store["jobs"] == [], {"out": out5, "jobs": store["jobs"]})
        check("drain pruned the remaining lane claim",
              not (lane_b / f"{stem_b}.json").exists(), sorted(lane_b.glob("*.json")))
    finally:
        common.runner_lock_states, common.heal_wedged_runner_lock = real_lock_states, real_heal
        door._spawn_runner = real_spawn
        for k, v in env_saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

sys.exit(1 if failures else 0)
