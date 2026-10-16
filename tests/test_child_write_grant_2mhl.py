"""est-2mhl — the runner's per-child write grant rides a channel core cannot replace.

Core's served-profile resolver (agent/file_safety.get_safe_write_roots) REPLACES the
process HERMES_WRITE_SAFE_ROOT with the served profile's own value, so the child
workdir appended to it (fb 625a3241, tests/test_safe_root_workdir.py) is dropped
whenever the profile carries a root. run_child therefore ALSO hands the child
HERMES_WRITE_SAFE_ROOT_EXTRA = the child's OWN work dir, the companion core unions
while a jail is in force. Inert until core reads it; this file pins the contract the
core change consumes.

Cases: SET (EXTRA == own dir, exactly one entry, root append unchanged), UNSET and
EMPTY root (EXTRA absent: no jail, no grant), HOST-EXTRA (an inherited grant is
replaced when a jail is in force and dropped when not -- never accumulated or
forwarded), FAN-OUT (each item sees only its own dir), ROUTE (a profile-routed child,
whose env is rebuilt from a keep-set, still receives the grant).

Self-contained fake CLI written to the temp dir (its log path rides HERMES_WF_FAKE_LOG, which the route keep-set forwards). Plain script: exit non-zero on any red.
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
EXTRA = "HERMES_WRITE_SAFE_ROOT_EXTRA"


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:400]))
    if not cond:
        FAILS.append(name)


FAKE = r'''#!/usr/bin/env python3
import json, os
with open(os.environ["HERMES_WF_FAKE_LOG"], "a") as f:
    f.write(json.dumps({"safe_root": os.environ.get("HERMES_WRITE_SAFE_ROOT"),
                        "extra": os.environ.get("HERMES_WRITE_SAFE_ROOT_EXTRA"),
                        "cwd": os.getcwd()}) + "\n")
print("progress line", flush=True)
print("```json\n" + json.dumps({"result": "ok"}) + "\n```")
'''

UNSET = object()


def run_graph(tmp, name, graph, safe_root, extra=UNSET):
    home = tmp / "home"
    home.mkdir(parents=True, exist_ok=True)
    fake_bin = tmp / "fake-hermes"
    fake_bin.write_text(FAKE)
    fake_bin.chmod(fake_bin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    for n in graph["nodes"]:
        if n.get("profile"):        # a routed node needs <profiles>/<name>/config.yaml
            (home / "profiles" / n["profile"]).mkdir(parents=True, exist_ok=True)
            (home / "profiles" / n["profile"] / "config.yaml").write_text("{}\n")
    run = home / "workflows" / name
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    (run / "graph.json").write_text(json.dumps(graph))
    (run / "run.json").write_text(json.dumps({"hermes_bin": str(fake_bin), "concurrency": 4}))
    fake_log = tmp / (name + ".fake.log")
    env = dict(os.environ, HERMES_HOME=str(home), WF_RUNS_ROOT=str(home / "workflows"), HERMES_WF_FAKE_LOG=str(fake_log))
    env.pop("HERMES_WRITE_SAFE_ROOT", None)
    env.pop(EXTRA, None)
    if safe_root is not UNSET:
        env["HERMES_WRITE_SAFE_ROOT"] = safe_root
    if extra is not UNSET:
        env[EXTRA] = extra
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

    with tempfile.TemporaryDirectory(prefix="ge-set-") as t:
        _h, run, seen = run_graph(Path(t), "set", dict(SOLO, name="set"), os.pathsep.join(inherited))
        check("SET one child spawned", len(seen) == 1, seen)
        c = seen[0] if seen else {}
        want = str((run / "work" / "recon").resolve())
        check("SET EXTRA == the child's own work dir, one entry", c.get("extra") == want, c)
        check("SET EXTRA == the child's cwd", c.get("extra") == c.get("cwd"), c)
        check("SET root append unchanged (last entry == own dir)",
              (c.get("safe_root") or "").split(os.pathsep) == inherited + [want], c)

    for label, root in (("UNSET", UNSET), ("EMPTY", "")):
        with tempfile.TemporaryDirectory(prefix="ge-none-") as t:
            _h, _r, seen = run_graph(Path(t), label.lower(), dict(SOLO, name=label.lower()), root)
            check(f"{label} child spawned", len(seen) == 1, seen)
            check(f"{label} no jail -> no grant (EXTRA absent)",
                  bool(seen) and seen[0].get("extra") is None, seen)

    with tempfile.TemporaryDirectory(prefix="ge-host-") as t:
        _h, run, seen = run_graph(Path(t), "hostset", dict(SOLO, name="hostset"),
                                  os.pathsep.join(inherited), extra="/host/foreign")
        want = str((run / "work" / "recon").resolve())
        check("HOST-EXTRA with jail: foreign grant replaced by own dir only",
              bool(seen) and seen[0].get("extra") == want, seen)
    with tempfile.TemporaryDirectory(prefix="ge-hostn-") as t:
        _h, _r, seen = run_graph(Path(t), "hostnone", dict(SOLO, name="hostnone"), UNSET, extra="/host/foreign")
        check("HOST-EXTRA without jail: foreign grant NOT forwarded",
              bool(seen) and seen[0].get("extra") is None, seen)

    with tempfile.TemporaryDirectory(prefix="ge-fan-") as t:
        graph = {"name": "fan", "nodes": [{"id": "recon", "type": "agent",
                                           "fanout": {"items": ["alpha", "beta"],
                                                      "goal": "audit {item}"}}]}
        _h, run, seen = run_graph(Path(t), "fan", graph, os.pathsep.join(inherited))
        check("FAN-OUT two children spawned", len(seen) == 2, seen)
        wants = {str((run / "work" / f"recon.{i}").resolve()) for i in (0, 1)}
        check("FAN-OUT each item's grant is its own dir, no sibling",
              {c.get("extra") for c in seen} == wants
              and all(c.get("extra") == c.get("cwd") for c in seen), (seen, wants))

    with tempfile.TemporaryDirectory(prefix="ge-route-") as t:
        graph = {"name": "route", "nodes": [{"id": "recon", "type": "agent", "goal": "do it",
                                             "profile": "other"}]}
        _h, run, seen = run_graph(Path(t), "route", graph, os.pathsep.join(inherited))
        check("ROUTE one child spawned", len(seen) == 1, seen)
        want = str((run / "work" / "recon").resolve())
        check("ROUTE routed child (rebuilt env) still receives the grant",
              bool(seen) and seen[0].get("extra") == want, seen)

    print(("" if not FAILS else "\nRED: ") + f"{len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
