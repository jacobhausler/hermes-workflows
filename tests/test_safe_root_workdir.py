"""fb 625a3241cfcc9dee — the child's advertised durable work dir is writable
under HERMES_WRITE_SAFE_ROOT.

WORK_DIR_NOTE tells every agent child 'Your working directory {WORK_DIR} is
durable; write your artifact there first'. That dir is <run>/work/<node>[.<i>]
under $HERMES_HOME/workflows/. When the runner's env carries a (non-empty)
HERMES_WRITE_SAFE_ROOT, core denies writes outside it, so the runner must append
the child's OWN work dir (narrowest) to the child's value. Unset/empty = no
restriction in core: the runner must leave it exactly as inherited.

Cases: SET (inherited order kept, last entry == child's cwd), NARROW (never the
run dir, run/work, or HOME/workflows), UNSET (child sees None), EMPTY (child
sees '' or None), FAN-OUT (each item sees only its own <node>.<i>).

Self-contained fake CLI (written to the temp dir): must not touch the shared
tests/fake_hermes.py. Plain script: exit non-zero on any red.
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


# The fake child appends one JSON line {safe_root, cwd} to FAKE_LOG, then commits.
FAKE = r'''#!/usr/bin/env python3
import json, os
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"safe_root": os.environ.get("HERMES_WRITE_SAFE_ROOT"),
                        "cwd": os.getcwd()}) + "\n")
print("progress line", flush=True)
print("```json\n" + json.dumps({"result": "ok"}) + "\n```")
'''

UNSET = object()


def run_graph(tmp, name, graph, safe_root):
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
    env = dict(os.environ, HERMES_HOME=str(home), WF_RUNS_ROOT=str(home / "workflows"), FAKE_LOG=str(fake_log))
    env.pop("HERMES_WRITE_SAFE_ROOT", None)
    if safe_root is not UNSET:
        env["HERMES_WRITE_SAFE_ROOT"] = safe_root
    p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", name],
                       env=env, text=True, capture_output=True, timeout=90, cwd=str(tmp))
    out = p.stdout + p.stderr
    check(f"{name}: lifecycle WORKFLOW_DONE", "WORKFLOW_DONE" in out and p.returncode == 0, out[:300])
    seen = [json.loads(l) for l in fake_log.read_text().splitlines() if l.strip()] \
        if fake_log.exists() else []
    return home, run, seen


SOLO = {"name": "s", "nodes": [{"id": "recon", "type": "agent", "goal": "do it"}]}


def main():
    inherited = ["/x/a", "/x/b"]

    # ---------------- SET + NARROW ----------------
    with tempfile.TemporaryDirectory(prefix="sr-set-") as t:
        tmp = Path(t)
        home, run, seen = run_graph(tmp, "set", dict(SOLO, name="set"), os.pathsep.join(inherited))
        check("SET one child spawned", len(seen) == 1, seen)
        c = seen[0] if seen else {}
        sr = c.get("safe_root") or ""
        parts = sr.split(os.pathsep)
        want = str((run / "work" / "recon").resolve())
        check("SET inherited entries first, original order", parts[:2] == inherited, sr)
        check("SET last entry == child's own work dir", parts[-1] == want, sr)
        check("SET last entry == child's cwd", parts[-1] == c.get("cwd"), c)
        check("SET exactly one entry added", len(parts) == len(inherited) + 1, sr)
        forbidden = {str(p) for p in (run, run.resolve(), run / "work", (run / "work").resolve(),
                                      home / "workflows", (home / "workflows").resolve())}
        check("NARROW no entry is the run dir, run/work, or HOME/workflows",
              not (set(parts) & forbidden), sr)

    # ---------------- UNSET ----------------
    with tempfile.TemporaryDirectory(prefix="sr-unset-") as t:
        _h, _r, seen = run_graph(Path(t), "unset", dict(SOLO, name="unset"), UNSET)
        check("UNSET child spawned", len(seen) == 1, seen)
        check("UNSET child sees None (never newly restricted)",
              bool(seen) and seen[0].get("safe_root") is None, seen)

    # ---------------- EMPTY ----------------
    with tempfile.TemporaryDirectory(prefix="sr-empty-") as t:
        _h, _r, seen = run_graph(Path(t), "empty", dict(SOLO, name="empty"), "")
        check("EMPTY child spawned", len(seen) == 1, seen)
        check("EMPTY child sees '' or None (never the work dir alone)",
              bool(seen) and seen[0].get("safe_root") in ("", None), seen)

    # ---------------- FAN-OUT ----------------
    with tempfile.TemporaryDirectory(prefix="sr-fan-") as t:
        graph = {"name": "fan", "nodes": [{"id": "recon", "type": "agent",
                                           "fanout": {"items": ["alpha", "beta"],
                                                      "goal": "audit {item}"}}]}
        _h, run, seen = run_graph(Path(t), "fan", graph, os.pathsep.join(inherited))
        check("FAN-OUT two children spawned", len(seen) == 2, seen)
        wants = {str((run / "work" / f"recon.{i}").resolve()) for i in (0, 1)}
        got = set()
        for c in seen:
            parts = (c.get("safe_root") or "").split(os.pathsep)
            check(f"FAN-OUT {Path(c.get('cwd', '?')).name}: inherited first",
                  parts[:2] == inherited, c)
            check(f"FAN-OUT {Path(c.get('cwd', '?')).name}: last entry == own cwd, one added",
                  parts[-1] == c.get("cwd") and len(parts) == 3, c)
            check(f"FAN-OUT {Path(c.get('cwd', '?')).name}: no sibling dir allowed",
                  not (set(parts) & (wants - {c.get("cwd")})), c)
            got.add(parts[-1])
        check("FAN-OUT per-item dirs recon.0 / recon.1", got == wants, (got, wants))

    print(("" if not FAILS else "\nRED: ") + f"{len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
