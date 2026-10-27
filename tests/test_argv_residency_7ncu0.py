#!/usr/bin/env python3
"""Persisted launch locations use stable roots. All fixtures are temporary."""
import importlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

failures = 0
def check(label, ok, detail: object=""):
    global failures
    print(("PASS " if ok else "FAIL ") + label + (" " + str(detail) if not ok else ""))
    failures += not ok

def make_shim(dirpath, name, target):
    d = Path(dirpath) / "scripts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text("#!/usr/bin/env bash\nexec " + target + "\n")
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return p

def relhome(base, *parts):
    h = Path(base) / ".hermes"
    h.mkdir(parents=True, exist_ok=True)
    return h.joinpath(*parts)

with tempfile.TemporaryDirectory(prefix="wf-residency-") as tdir:
    T = Path(tdir)
    homeR = relhome(T / "homeR")
    target = homeR / "payload" / "job.sh"
    target.parent.mkdir(parents=True)
    target.write_text("#!/bin/sh\ntrue\n")
    shimR = make_shim(homeR, "job.sh", str(target))

    homeV = relhome(T / "homeV")
    wt = T / "wt" / "worktrees" / "lane-a"
    (wt / "payload").mkdir(parents=True)
    gone = wt / "payload" / "job.sh"
    gone.write_text("#!/bin/sh\ntrue\n")
    make_shim(homeV, "job.sh", str(gone))

    homeM = relhome(T / "homeM")
    make_shim(homeM, "job.sh", str(homeM / "payload" / "nope.sh"))

    checker = ROOT / "scripts" / "argv_residency.py"

    def run_check(*args, home=None):
        env = {k: v for k, v in os.environ.items() if k != "WF_ARGV_STABLE_ROOTS"}
        if home is not None:
            env["HERMES_HOME"] = str(home)
        return subprocess.run([sys.executable, str(checker)] + [str(a) for a in args],
                              capture_output=True, text=True, env=env, timeout=60)

    r = run_check("--home", homeR, "--stable-root", T / "homeR", "--json")
    report = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
    findings = report.get("findings", [])
    check("audit: resident shim exits 0", r.returncode == 0, (r.returncode, r.stdout[-300:]))
    check("audit: resident shim reports zero violations", not findings, findings)

    r = run_check("--home", homeV, "--json")
    report = json.loads(r.stdout) if r.stdout.strip() else {}
    findings = report.get("findings", [])
    check("audit: worktree-resident shim exits 1", r.returncode == 1, r.returncode)
    check("audit: violation names the volatile segment",
          any("worktree" in (f.get("detail", "") + str(f.get("segments", ""))) for f in findings),
          findings)

    r = run_check("--home", homeM, "--stable-root", T / "homeM", "--json")
    findings = json.loads(r.stdout).get("findings", []) if r.stdout.strip() else []
    check("audit: missing entrypoint exits 1", r.returncode == 1, r.returncode)
    check("audit: violation is the missing class",
          any(f.get("status") == "missing" for f in findings), findings)

    storeV = T / "storeV"
    (storeV / "scripts").mkdir(parents=True)
    (storeV / "jobs.json").write_text(json.dumps({"jobs": [
        {"id": "x1", "name": "vol", "script": str(gone)},
        {"id": "x2", "name": "res", "script": "resident.sh"},
    ]}))
    (storeV / "scripts" / "resident.sh").write_text("#!/bin/sh\ntrue\n")
    r = run_check("--cron-store", storeV / "jobs.json", "--stable-root", storeV, "--json")
    findings = json.loads(r.stdout).get("findings", []) if r.stdout.strip() else []
    check("audit: volatile store script refuses", r.returncode == 1, r.returncode)
    check("audit: only the volatile row flags",
          len(findings) == 1 and "worktrees" in json.dumps(findings), findings)

    before = sorted((p.relative_to(T).as_posix(), p.stat().st_mtime_ns)
                    for p in T.rglob("*") if p.is_file())
    run_check("--home", homeV, "--home", T / "homeR")
    after = sorted((p.relative_to(T).as_posix(), p.stat().st_mtime_ns)
                   for p in T.rglob("*") if p.is_file())
    check("audit: dry by default, nothing written", before == after)

    r = run_check("--home", homeV, "--guard")
    check("guard: volatile fixture exits nonzero", r.returncode != 0, r.returncode)
    r = run_check("--home", homeR, "--stable-root", T / "homeR", "--guard")
    check("guard: resident fixture exits 0", r.returncode == 0, r.returncode)

    import wfcommon
    err = wfcommon.wait_spec_ok({"until_argv": [str(T / "wt" / "worktrees" / "lane-a" / "bin" / "probe.sh")]})
    check("grammar: volatile absolute argv[0] refused",
          any("until_argv" in (e.get("field") or "") or "resid" in e.get("msg", "").lower()
              for e in err), err)
    check("grammar: PATH-relative argv[0] stays legal",
          wfcommon.wait_spec_ok({"until_argv": ["git", "status"]}) == [])
    os.environ["WF_ARGV_STABLE_ROOTS"] = str(homeR)
    try:
        check("grammar: resident absolute argv[0] passes",
              wfcommon.wait_spec_ok({"until_argv": [str(target)]}) == [])
    finally:
        del os.environ["WF_ARGV_STABLE_ROOTS"]
    check("grammar: unbound placeholder argv[0] left to the bind gate",
          wfcommon.wait_spec_ok({"until_argv": ["/srv/{run.WHAT}/probe.sh"]}) == [])

    cb = importlib.import_module("cron_bridge")
    cb._home = lambda: T / "fakehome"
    cb.PLUGIN_ROOT = wt  # the plugin loaded from a throwaway worktree
    cb.WF_PY = wt / "wf.py"
    (wt / "wf.py").write_text("# stub\n")
    try:
        cb.write_shim("tick", "tick")
        check("bake: volatile plugin root refused", False, "write_shim returned without raising")
    except ValueError as e:
        check("bake: volatile plugin root refused", "resid" in str(e).lower()
              or "worktree" in str(e).lower(), e)
    stable_root = T / "plugin"
    stable_root.mkdir()
    (stable_root / "wf.py").write_text("# stub\n")
    cb.PLUGIN_ROOT = stable_root
    cb.WF_PY = stable_root / "wf.py"
    os.environ["WF_ARGV_STABLE_ROOTS"] = str(stable_root)
    try:
        p = cb.write_shim("tick", "tick")
    finally:
        del os.environ["WF_ARGV_STABLE_ROOTS"]
    check("bake: resident plugin root bakes the shim",
          p.is_file() and str(cb.WF_PY) in p.read_text()
          and p.stat().st_mode & stat.S_IXUSR, p)

with tempfile.TemporaryDirectory(prefix="wf-residency-boundary-") as tdir:
    T = Path(tdir)
    stable = T / "install"
    stable.mkdir()
    good = stable / "probe"
    good.write_text("#!/bin/sh\nexit 0\n")
    good.chmod(0o755)
    volatile = T / "worktrees" / "lane" / "probe"
    volatile.parent.mkdir(parents=True)
    volatile.write_text(good.read_text())
    volatile.chmod(0o755)
    link = stable / "linked-probe"
    link.symlink_to(volatile)
    check("boundary: resident symlink cannot hide a worktree target",
          wfcommon.entrypoint_residency(str(link), [stable])[0] != "resident")
    outside = T / "unregistered"
    outside.write_text(good.read_text())
    check("boundary: existence alone does not declare a stable root",
          wfcommon.entrypoint_residency(str(outside), [stable])[0] != "resident")
    check("boundary: relative paths cannot bake the submitter cwd",
          wfcommon.entrypoint_residency("./probe", [stable])[0] != "resident")
    from unittest.mock import patch
    with patch.object(sys, "executable", str(volatile)):
        check("boundary: the running interpreter does not declare its own install root",
              wfcommon.entrypoint_residency(str(volatile))[0] != "resident")
    with patch.dict(os.environ, {"PATH": str(volatile.parent)}):
        check("boundary: PATH resolution also checks the actual target",
              wfcommon.entrypoint_residency("probe", [stable])[0] != "resident")
    with patch.dict(os.environ, {"WF_ARGV_STABLE_ROOTS": str(stable)}):
        errors = wfcommon.wait_spec_ok({"until_argv": [sys.executable, str(volatile)]})
        check("boundary: interpreter does not hide a volatile script operand",
              any(str(volatile) in e["msg"] for e in errors), errors)
        errors = wfcommon.wait_spec_ok({"until_argv": [sys.executable, "-O", str(volatile)]})
        check("boundary: Python -O does not consume the script operand", bool(errors), errors)
        check("boundary: Python -O permits a resident script",
              not wfcommon.wait_spec_ok({"until_argv": [sys.executable, "-O", str(good)]}))
        disguised = volatile.with_name("true")
        disguised.write_text(good.read_text())
        disguised.chmod(0o755)
        errors = wfcommon.wait_spec_ok({"until_argv": ["/usr/bin/env", "PATH=" + str(volatile.parent), "true"]})
        check("boundary: env PATH override cannot certify the caller's executable", bool(errors), errors)

    home = T / "home"
    scripts = home / "scripts"
    scripts.mkdir(parents=True)
    shim = scripts / "quoted.sh"
    shim.write_text("#!/bin/sh\nexec '" + str(volatile) + "'\n")
    r = run_check("--home", home, "--stable-root", T, "--json")
    check("audit: suffixless executable in a quoted exec is checked", r.returncode == 1)
    shim.write_text("#!/bin/sh\nexec " + sys.executable + " '" + str(volatile) + "'\n")
    r = run_check("--home", home, "--stable-root", T, "--json")
    check("audit: interpreter-backed shim checks the script operand", r.returncode == 1)
    shim.write_text("#!/bin/sh\nPATH=" + str(volatile.parent) + " true\n")
    r = run_check("--home", home, "--stable-root", T, "--json")
    check("audit: shell PATH assignment cannot hide a volatile command", r.returncode == 1)
    shim.write_text("#!/bin/sh\nPY=/usr/bin/python3\nexec 9>\"$LOCKFILE\"\ntrue\n")
    r = run_check("--home", home, "--stable-root", T, "--json")
    check("audit: variable assignments and descriptor-only exec are not programs", r.returncode == 0, r.stdout)
    shim.unlink()
    profile = home / "profiles" / "fixture"
    (profile / "scripts").mkdir(parents=True)
    (profile / "cron").mkdir()
    (profile / "scripts" / "job.sh").write_text("#!/bin/sh\ntrue\n")
    (profile / "cron" / "jobs.json").write_text(json.dumps({"jobs": [{"script": "job.sh"}]}))
    r = run_check("--home", home, "--json", home=home)
    check("audit: a profile's scripts are its own install boundary", r.returncode == 0, r.stdout)

    run = home / "workflows" / "fixture"
    run.mkdir(parents=True)
    (run / "graph.json").write_text(json.dumps({"nodes": [
        {"id": "probe", "type": "gate", "wait": {"until_argv": [str(volatile)]}}]}))
    r = run_check("--home", home, "--stable-root", T, "--json")
    check("audit: home scan includes persisted wake gates", r.returncode == 1)
    (run / "graph.json").unlink()
    (run / "post_exit_hook.json").write_text(json.dumps({"script": str(volatile)}))
    r = run_check("--home", home, "--stable-root", T, "--json")
    check("audit: home scan includes post-exit registrations", r.returncode == 1)
    (run / "post_exit_hook.json").unlink()

    import wf
    (run / "nodes").mkdir()
    gate = {"id": "probe", "type": "gate", "wait": {
        "until_argv": [str(good)], "every_s": 0.2, "timeout_s": 1}}
    with patch.dict(os.environ, {"WF_ARGV_STABLE_ROOTS": str(stable)}):
        check("wake: resident probe admits before removal", not wfcommon.wait_spec_ok(gate["wait"]))
        good.unlink()
        with patch.object(wf, "_aux_run", side_effect=RuntimeError("must not spawn")) as spawn:
            result = wf.park_gate(run, run.name, gate, {gate["id"]: gate}, lambda: None)
        record = json.loads((run / "nodes" / "probe.json").read_text())
        check("wake: missing entrypoint fails before any subprocess",
              result == "failed" and not spawn.called
              and record.get("error_class") == "precondition", record)

sys.exit(1 if failures else 0)
