#!/usr/bin/env python3
"""Registered external work outlives its agent, then re-drive harvests once."""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon


def test_detach_redrive_once():
    with tempfile.TemporaryDirectory(prefix="detach-reap-") as td:
        home = Path(td)
        runs = home / "workflows"
        r = runs / "detach"
        (r / "nodes").mkdir(parents=True)
        (r / "gates").mkdir()
        agent = home / "agent.py"
        agent.write_text("#!/usr/bin/env python3\n" + '''import sys, os, subprocess
from pathlib import Path
sys.path.insert(0, os.environ["O79J_ROOT"])
import wf, wfcommon
r = Path(os.environ["O79J_RUN"])
with (r / "launches").open("a") as f: f.write("launch\\n")
with (r / "job.log").open("w") as log:
    p = subprocess.Popen([sys.executable, str(r / "job.py")], stdout=log, stderr=log,
                         start_new_session=True)
    graph = wfcommon.jload(r / "graph.json")
    node = graph["nodes"][0]
    subprocess.run([sys.executable, str(Path(os.environ["O79J_ROOT"]) / "wf.py"),
                    "register-job", r.name, node["id"], str(p.pid),
                    str(r / "answer.json"), str(r / "job.log")], check=True)
print("registered external work")
''')
        agent.chmod(0o755)
        (r / "job.py").write_text('''import json, time
from pathlib import Path
r = Path(__file__).resolve().parent
import os
(r / "job.pid").write_text(str(os.getpid()))
time.sleep(5)
p = r / "answer.json.tmp"
p.write_text(json.dumps({"exit_code": 0, "output": {"ok": True}}))
p.replace(r / "answer.json")
print("job finished", flush=True)
''')
        node = {"id": "work", "type": "agent", "goal": "external job", "timeout": 2,
                "schema": {"type": "object", "required": ["ok"]}}
        (r / "graph.json").write_text(json.dumps({"name": "detach", "nodes": [node]}))
        (r / "run.json").write_text(json.dumps({"hermes_bin": str(agent), "node_timeout": 2}))
        env = dict(os.environ, HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
                   O79J_ROOT=str(ROOT), O79J_RUN=str(r), PYTHONDONTWRITEBYTECODE="1")
        for k in list(env):
            if k.startswith(("HERMES_SESSION_", "HERMES_UI_SESSION_", "WF_TEST_")):
                env.pop(k)
        runners = []
        jobpid = None
        try:
            p = subprocess.Popen([sys.executable, str(ROOT / "wf.py"), "run", r.name],
                                 env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            runners.append(p)
            end = time.monotonic() + 15
            job = None
            while time.monotonic() < end:
                job = wfcommon.jload(r / "jobs/work.json")
                rec = wfcommon.jload(r / "nodes/work.json") or {}
                if job and not wfcommon._verify_spawn_rec(r, node, {"work": node}, rec):
                    break
                if p.poll() is not None:
                    raise AssertionError("runner exited before registration: " + p.communicate()[0].decode()
                                         + repr(wfcommon.jload(r / "nodes/work.json"))
                                         + "\n".join(f.read_text(errors="replace") for f in (r / "logs").glob("*.log")))
                time.sleep(.05)
            assert job, "no supported durable registration seam"
            jobpid = job["pid"]
            # Runner dies AFTER the agent exits, while the actual work is live.
            p.kill()
            p.communicate(timeout=10)
            assert Path(f"/proc/{jobpid}").exists()
            q = subprocess.Popen([sys.executable, str(ROOT / "wf.py"), "run", r.name],
                                 env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            runners.append(q)
            out = q.communicate(timeout=25)[0].decode()
            assert q.returncode == 0 and "WORKFLOW_DONE" in out, out
            assert (r / "launches").read_text().splitlines() == ["launch"]
            result = wfcommon.jload(r / "nodes/work.json")
            assert result["status"] == "done" and result["output"] == {"ok": True}, result
            assert result["detached_job"]["pid"] == jobpid
            # A third drive must neither harvest again nor launch another agent.
            again = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", r.name],
                                   env=env, capture_output=True, text=True, timeout=15)
            assert again.returncode == 0 and "WORKFLOW_DONE" in again.stdout
            ev = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
            assert len([e for e in ev if e.get("event") == "job.harvested"]) == 1
            assert (r / "launches").read_text().splitlines() == ["launch"]
            assert wfcommon.jload(r / "jobs/work.json")["status"] == "harvested"
        finally:
            for p in runners:
                if p.poll() is None: p.kill()
                p.communicate(timeout=10)
            if not jobpid and (r / "job.pid").exists():
                jobpid = int((r / "job.pid").read_text())
            if jobpid:
                try: os.kill(jobpid, signal.SIGKILL)
                except ProcessLookupError: pass
                try: os.waitpid(jobpid, 0)
                except ChildProcessError: pass


if __name__ == "__main__":
    test_detach_redrive_once()
    print("PASS external-job registration, no deadline kill, redrive harvest once")
