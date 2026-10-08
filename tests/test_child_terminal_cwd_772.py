"""est-2ek.1.772 — a child's terminal-tool default cwd is its own work dir.

The runner spawns each agent child with Popen cwd=<run>/work/<node>[.<i>], but the
Hermes terminal tool takes its default cwd from $TERMINAL_CWD, not the process cwd.
A runner env that already carries TERMINAL_CWD (hosts export one) therefore sent a
`git clone` with no `workdir` to that host path, outside the declared node
workspace. The runner must pin TERMINAL_CWD to the child's own work dir.

Cases: INHERITED (runner env has a foreign TERMINAL_CWD), UNSET (runner env has
none), FAN-OUT (each item sees only its own <node>.<i>).

Self-contained fake CLI (written to the temp dir). Plain script: exit non-zero on
any red.
"""
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILS = []


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:400]))
    if not cond:
        FAILS.append(name)


# The fake child records the cwd the process has and the terminal default cwd the
# Hermes terminal tool would resolve (TERMINAL_CWD), then commits.
FAKE = r'''#!/usr/bin/env python3
import json, os
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"terminal_cwd": os.environ.get("TERMINAL_CWD"),
                        "cwd": os.getcwd()}) + "\n")
print("```json\n" + json.dumps({"result": "ok"}) + "\n```")
'''

UNSET = object()


def run_graph(tmp, name, graph, terminal_cwd):
    home = tmp / "home"
    home.mkdir(parents=True, exist_ok=True)
    fake_bin = tmp / "fake-hermes"
    fake_bin.write_text(FAKE)
    fake_bin.chmod(fake_bin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    run = home / "workflows" / name
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    (run / "graph.json").write_text(json.dumps(graph))
    (run / "run.json").write_text(json.dumps({"hermes_bin": str(fake_bin), "concurrency": 4}))
    fake_log = tmp / (name + ".fake.log")
    env = dict(os.environ, HERMES_HOME=str(home), WF_RUNS_ROOT=str(home / "workflows"),
               FAKE_LOG=str(fake_log))
    env.pop("TERMINAL_CWD", None)
    if terminal_cwd is not UNSET:
        env["TERMINAL_CWD"] = terminal_cwd
    p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", name],
                       env=env, text=True, capture_output=True, timeout=90, cwd=str(tmp))
    out = p.stdout + p.stderr
    check(f"{name}: lifecycle WORKFLOW_DONE", "WORKFLOW_DONE" in out and p.returncode == 0, out[:300])
    seen = [json.loads(l) for l in fake_log.read_text().splitlines() if l.strip()] \
        if fake_log.exists() else []
    return home, run, seen


SOLO = {"name": "s", "nodes": [{"id": "recon", "type": "agent", "goal": "do it"}]}


def main():
    with tempfile.TemporaryDirectory(prefix="tc-inh-") as t:
        tmp = Path(t)
        foreign = str(tmp / "host-default-cwd")
        _h, run, seen = run_graph(tmp, "inh", dict(SOLO, name="inh"), foreign)
        check("INHERITED one child spawned", len(seen) == 1, seen)
        c = seen[0] if seen else {}
        want = str((run / "work" / "recon").resolve())
        check("INHERITED terminal default cwd == child's work dir", c.get("terminal_cwd") == want,
              (c, want))
        check("INHERITED terminal default cwd == process cwd", c.get("terminal_cwd") == c.get("cwd"), c)
        check("INHERITED foreign TERMINAL_CWD not forwarded", c.get("terminal_cwd") != foreign, c)

    with tempfile.TemporaryDirectory(prefix="tc-unset-") as t:
        _h, run, seen = run_graph(Path(t), "unset", dict(SOLO, name="unset"), UNSET)
        check("UNSET one child spawned", len(seen) == 1, seen)
        c = seen[0] if seen else {}
        check("UNSET terminal default cwd == child's work dir",
              c.get("terminal_cwd") == str((run / "work" / "recon").resolve()), c)

    with tempfile.TemporaryDirectory(prefix="tc-fan-") as t:
        graph = {"name": "fan", "nodes": [{"id": "recon", "type": "agent",
                                           "fanout": {"items": ["alpha", "beta"],
                                                      "goal": "audit {item}"}}]}
        _h, run, seen = run_graph(Path(t), "fan", graph, str(Path(t) / "host-default-cwd"))
        check("FAN-OUT two children spawned", len(seen) == 2, seen)
        wants = {str((run / "work" / f"recon.{i}").resolve()) for i in (0, 1)}
        check("FAN-OUT each item's terminal cwd is its own dir, no sibling",
              {c.get("terminal_cwd") for c in seen} == wants
              and all(c.get("terminal_cwd") == c.get("cwd") for c in seen), (seen, wants))

    print(("" if not FAILS else "\nRED: ") + f"{len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
