#!/usr/bin/env python3
"""est-ip975 PR-1: cron_bridge — the tick job is a NAME-KEYED SINGLETON that is
deleted, never disabled, and every host-import touch goes through the guarded
_jobs() seam.

The law pinned here:
  * ensure_tick() creates exactly ONE job: name == cron_bridge.TICK_NAME,
    no_agent=True, prompt=None, and a shim script that lives under
    <resolved HERMES_HOME>/scripts/ (core's scheduler refuses any script that
    resolves outside that dir — cron/scheduler_script.py validates the path),
    the shim being an executable bash file that execs this plugin's OWN
    absolute wf.py entrypoint;
  * a second ensure_tick() while the job exists returns the SAME id, creates
    NOTHING (double-arm is idempotent — the singleton is keyed BY NAME, so a
    re-arm on every launch can never accumulate rows);
  * teardown_tick() DELETES the job (store empty afterwards) and returns True;
    teardown with no job present returns False — deletion, never disable, so
    tick jobs never accumulate;
  * a host with no importable core cron (_jobs() -> None) degrades HONESTLY:
    ensure_tick() returns None, teardown_tick() returns False, neither raises
    (AGENTS.md 4c rule 8 — silent no-op, the launcher never fails over the tick);
  * tick_schedule() precedence WF_TICK_SCHEDULE env > configured
    workflows.tick_schedule > DEFAULT_TICK_SCHEDULE (the same resolution shape
    as wfcommon.seat_max_seats — resolved at use, never baked).

Hermetic per est-z2heo: a fake jobs module is injected at the _jobs seam and
HERMES_HOME points at a tmp dir — the live cron store is NEVER touched.

Plain script, no pytest: exits non-zero on the first red.
"""
import os
import stat
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import cron_bridge  # noqa: E402  (the module under test, flat root layout)

FAILS = []


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:600]))
    if not cond:
        FAILS.append(name)


class FakeJobs:
    """Stand-in for the core cron.jobs module — records every create call."""

    def __init__(self):
        self.jobs = []
        self.create_calls = 0

    def create_job(self, **kw):
        self.create_calls += 1
        # Pin the call shape against core cron/jobs.py create_job (:1788).
        check("create_job called with exactly prompt/schedule/name/script/no_agent",
              set(kw) == {"prompt", "schedule", "name", "script", "no_agent"}, sorted(kw))
        job = dict(kw)
        job["id"] = "fake%02d" % self.create_calls
        self.jobs.append(job)
        return job

    def list_jobs(self, include_disabled=False):
        return [dict(j) for j in self.jobs]

    def remove_job(self, job_id):
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j.get("id") != job_id]
        return len(self.jobs) < before


def main():
    fake = FakeJobs()
    cron_bridge._jobs = lambda: fake  # THE test seam: no core import, ever

    saved_env = {k: os.environ.get(k) for k in ("HERMES_HOME", "WF_TICK_SCHEDULE")}
    try:
        with tempfile.TemporaryDirectory(prefix="tickbridge-") as td:
            home = Path(td) / "hermes-home"
            home.mkdir()
            os.environ["HERMES_HOME"] = str(home)
            os.environ["WF_TICK_SCHEDULE"] = "every 7m"  # env precedence, pinned hermetically

            # A. arm: exactly one job, no_agent, right name, shim under tmp scripts dir.
            jid = cron_bridge.ensure_tick()
            check("A: ensure_tick returns a job id", isinstance(jid, str) and bool(jid), jid)
            check("A: exactly one create call", fake.create_calls == 1, fake.create_calls)
            check("A: store holds exactly one job", len(fake.jobs) == 1, fake.jobs)
            job = fake.jobs[0] if fake.jobs else {}
            check("A: the job is named with the singleton tick name",
                  job.get("name") == cron_bridge.TICK_NAME, job.get("name"))
            check("A: the job is no_agent (zero agent wakes)",
                  job.get("no_agent") is True, job.get("no_agent"))
            check("A: the job carries no prompt", job.get("prompt") is None, job.get("prompt"))
            check("A: the schedule rides the env knob",
                  job.get("schedule") == "every 7m", job.get("schedule"))
            script = Path(str(job.get("script", "")))
            scripts_dir = (home / "scripts").resolve()
            check("A: the shim lives under <HERMES_HOME>/scripts",
                  script.is_file() and scripts_dir in script.resolve().parents,
                  str(script))
            if script.is_file():
                body = script.read_text()
                mode = script.stat().st_mode
                check("A: the shim is executable", bool(mode & stat.S_IXUSR), oct(mode))
                wf_py = (ROOT / "wf.py").resolve()
                check("A: the shim execs this plugin's absolute wf.py",
                      str(wf_py) in body and body.lstrip().startswith("#!"), body[:200])

            # B. double-arm: idempotent by NAME — same id, nothing created.
            jid2 = cron_bridge.ensure_tick()
            check("B: second ensure_tick returns the SAME id", jid2 == jid, (jid, jid2))
            check("B: still exactly one job in the store", len(fake.jobs) == 1, fake.jobs)
            check("B: NO second create call", fake.create_calls == 1, fake.create_calls)
            check("B: the shim is not duplicated",
                  sorted(p.name for p in (home / "scripts").iterdir())
                  == [cron_bridge.TICK_NAME + ".sh"],
                  sorted(p.name for p in (home / "scripts").iterdir()))

            # C. teardown: DELETION, never disable.
            check("C: teardown_tick returns True when a job existed",
                  cron_bridge.teardown_tick() is True, "teardown returned falsy")
            check("C: the store is empty afterwards (deleted, not disabled)",
                  fake.jobs == [], fake.jobs)

            # D. teardown with nothing to remove: False, and nothing removed by force.
            check("D: teardown with no job returns False",
                  cron_bridge.teardown_tick() is False, "teardown returned truthy")

            # E. honest degradation: a host with no core cron is a silent no-op.
            cron_bridge._jobs = lambda: None
            try:
                got = cron_bridge.ensure_tick()
                check("E: ensure_tick on a cron-less host returns None (never raises)",
                      got is None, got)
                down = cron_bridge.teardown_tick()
                check("E: teardown_tick on a cron-less host returns False (never raises)",
                      down is False, down)
            except Exception as exc:  # noqa: BLE001 — the law is: this never raises
                check("E: cron-less degradation never raises", False, repr(exc))

        # F. schedule precedence: env > configured > default (seat_max_seats shape).
        os.environ.pop("WF_TICK_SCHEDULE", None)
        check("F: tick_schedule falls back to the module default",
              cron_bridge.tick_schedule(core_config={}) == cron_bridge.DEFAULT_TICK_SCHEDULE,
              cron_bridge.tick_schedule(core_config={}))
        check("F: a configured workflows.tick_schedule beats the default",
              cron_bridge.tick_schedule(
                  core_config={"workflows": {"tick_schedule": "every 9m"}}) == "every 9m",
              cron_bridge.tick_schedule(core_config={"workflows": {"tick_schedule": "every 9m"}}))
        os.environ["WF_TICK_SCHEDULE"] = "every 3m"
        check("F: WF_TICK_SCHEDULE beats the configured value",
              cron_bridge.tick_schedule(
                  core_config={"workflows": {"tick_schedule": "every 9m"}}) == "every 3m",
              cron_bridge.tick_schedule(core_config={"workflows": {"tick_schedule": "every 9m"}}))
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        # Hermeticity receipt (est-z2heo): the REAL core cron module was never
        # imported under any code path this test exercised.
        check("Z: the live cron store was never touched (core cron.jobs never imported)",
              "cron.jobs" not in sys.modules, sorted(m for m in sys.modules if m.startswith("cron")))

    print("ALL PASS" if not FAILS else f"FAILED: {FAILS}")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
