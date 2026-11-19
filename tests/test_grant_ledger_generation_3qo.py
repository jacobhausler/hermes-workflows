#!/usr/bin/env python3
"""P40 (bd_2026-11-13-3qo): respawn grants reset per runner generation.

The estate incident this law came from: a pre-heal boot saved 2 transient
grants to `retry-window.json`; the post-update boot read `attempts >= cap`,
refused the spawn as `lifetime_cap_spent`, and a genuinely NEW transient
death under fixed code was capped by a dead boot's spend — the 18-day
treadmill shape in miniature.

Pins the observable outcome at the tick's generation boundary:
  * the respawn the tick performs goes through a ledger whose `attempts` are
    zeroed — the fresh runner's first-sighting refusal gate reads THIS boot's
    spend, not the old boot's;
  * the deadline (the backoff pacer) and the attempt log survive the reset
    byte-shape intact: per-generation reset stays paced and evidence-preserving;
  * the reset is on the event record exactly once per boundary that actually
    spent grants; a rerun over a clean (or absent, or corrupt) ledger converges
    with no event and no file invented.
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

    def create_job(prompt, schedule, name=None, repeat=None, deliver=None,
                   origin=None, script=None, no_agent=False, **kw):
        job = {"id": "fake-1", "name": name, "prompt": prompt,
               "schedule": schedule, "script": script, "no_agent": no_agent}
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


GRAPH = {"name": "wd3qo-grants", "nodes": [
    {"id": "a", "type": "echo", "output": {"ok": True}}]}

with tempfile.TemporaryDirectory(prefix="wf-grants-") as scratch:
    home = Path(scratch)
    env_saved = {k: os.environ.get(k) for k in
                 ("HERMES_HOME", "WF_RUNS_ROOT", "WF_TICK_SCHEDULE",
                  "WF_ARGV_STABLE_ROOTS")}
    os.environ["HERMES_HOME"] = str(home / "home")
    os.environ["WF_RUNS_ROOT"] = str(home / "runs")
    os.environ["WF_TICK_SCHEDULE"] = "every 1m"
    install_fake_cron({"jobs": []})
    STABLE = Path(tempfile.mkdtemp(prefix="wd3qo-grants-stable-"))
    import glob as _glob
    for src_f in _glob.glob(str(ROOT / "*.py")):
        (STABLE / Path(src_f).name).write_bytes(Path(src_f).read_bytes())
    (STABLE / "wake_native.py").write_text(
        "SCHEMA = 'stub'\ndef deliver(sid, text, tid, home):\n    return {'outcome': 'unavailable'}\n")
    os.environ["WF_ARGV_STABLE_ROOTS"] = os.pathsep.join(
        (str(STABLE), str(STABLE.resolve())))
    door = load("_hw_grants_door", STABLE / "__init__.py")
    import wf_test_isolation
    wf_test_isolation.install(door)
    wd = load("runner_watchdog", STABLE / "runner_watchdog.py")
    wd.bind(door._common)
    spawns = []
    real_spawn = door._spawn_runner
    door._spawn_runner = lambda r: spawns.append(Path(r))

    try:
        a = door.act_run({"graph": {**GRAPH, "name": "wd3qo-g"}})
        ra = Path(home) / "runs" / a["run_id"]
        pid = os.getpid() + 500000 if os.getpid() + 500000 < 2**22 else os.getpid() - 100
        (ra / "wf.pid").write_text(str(pid))
        (ra / "nodes").mkdir(exist_ok=True)
        (ra / "nodes" / "a.json").write_text(json.dumps({"status": "running", "pid": pid}))
        deadline = time.time() + 300
        log_entries = [{"attempt": 0, "error_class": "transport"},
                       {"attempt": 1, "error_class": "transport"}]
        window = ra / "retry-window.json"
        # The pre-heal boot's persisted spend: 2 grants == the default cap.
        window.write_text(json.dumps({"a": {"deadline": deadline, "attempts": 2,
                                            "log": log_entries},
                                      "b#3": {"deadline": deadline, "attempts": 1,
                                              "log": []}}))

        wd.tick(door=door)
        w = json.loads(window.read_text())
        check("the reap zeroes the old generation's grants (no lifetime_cap_spent debt)",
              w["a"]["attempts"] == 0 and w["b#3"]["attempts"] == 0, w)
        check("the backoff pacer survives the boundary byte-exact",
              w["a"]["deadline"] == deadline and w["b#3"]["deadline"] == deadline, w)
        check("the attempt log survives (record-vs-ledger evidence unharmed)",
              w["a"]["log"] == log_entries, w)
        evs = [json.loads(x) for x in (ra / "events.jsonl").read_text().splitlines()]
        resets = [e for e in evs if e.get("event") == "watchdog.grant_ledger_reset"]
        check("the reset is on the event record, naming the spent grants",
              len(resets) == 1 and resets[0]["grants"] == {"a": 2, "b#3": 1}, evs[-4:])

        # A rerun over the reset ledger converges: no second event, no new file.
        wd.tick(door=door)
        evs = [json.loads(x) for x in (ra / "events.jsonl").read_text().splitlines()]
        check("rerun converges: an already-reset ledger resets to nothing",
              sum(1 for e in evs if e.get("event") == "watchdog.grant_ledger_reset") == 1, evs[-3:])

        # A fresh death under the NEW generation re-charges normally: the next
        # boundary resets THAT spend too — the ledger is per boot, not lifetime.
        window.write_text(json.dumps({"a": {"deadline": deadline, "attempts": 1,
                                            "log": log_entries[:1]}}))
        wd.tick(door=door)
        evs = [json.loads(x) for x in (ra / "events.jsonl").read_text().splitlines()]
        check("post-heal transient deaths charge the fresh generation's own ledger",
              json.loads(window.read_text())["a"]["attempts"] == 0
              and sum(1 for e in evs if e.get("event") == "watchdog.grant_ledger_reset") == 2,
              evs[-3:])

        # Absent ledger: nothing invented, no event.
        window.unlink()
        (ra / "redrive.request").write_text(json.dumps(
            {"at": time.time(), "expires_at": time.time() + 600, "reason": "x", "tries": 1}))
        # (a live continuation keeps the leg honest: consume path only)
        wd.tick(door=door)
        check("no ledger, no clobber: absent retry-window.json is not created",
              not window.exists(), sorted(p.name for p in ra.iterdir()))
        # Corrupt ledger: left alone for the consumer's own honest fallback.
        before_tail = (ra / "events.jsonl").read_text().count("grant_ledger_reset")
        window.write_text("not json")
        wd.tick(door=door)
        check("a corrupt ledger is left alone (fail-open, no event)",
              window.read_text() == "not json"
              and (ra / "events.jsonl").read_text().count("grant_ledger_reset") == before_tail,
              "")
    finally:
        door._spawn_runner = real_spawn
        for k, v in env_saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

sys.exit(1 if failures else 0)
