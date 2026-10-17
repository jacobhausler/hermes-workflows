#!/usr/bin/env python3
"""Run the B1 isolation tests from a freshly packed, git-free release ZIP.

The release carries executable fixtures. Its gitpin checks fixture bytes without
repository metadata, while real checkouts retain the porcelain regression pin.
A mutating B1 stand-in must fail the extracted-ZIP pin even when it prints PASS.
"""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ("tests/fake-b1", "tests/fake", "tests/fake_hermes.py")
B1 = "tests/test_sprint101w2_B1-classes.py"
PIN = "tests/test_fakeb1_gitpin_954r.py"
ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label +
          (f"  {detail}" if detail and not cond else ""), flush=True)
    ok = ok and bool(cond)


def snapshot(package):
    return {f: hashlib.sha256((package / f).read_bytes()).hexdigest()
            for f in FIXTURES}


def run(package, test, env):
    result = subprocess.run([sys.executable, str(package / test)], cwd=package,
                            env=env, text=True, capture_output=True, timeout=150)
    return result, result.stdout + result.stderr


spec = importlib.util.spec_from_file_location("pack_1nkx", ROOT / "scripts/pack.py")
assert spec and spec.loader
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)

with tempfile.TemporaryDirectory(prefix="zip-1nkx-") as tmp:
    temporary = Path(tmp)
    archive = temporary / "release.zip"
    pack.build(archive)
    with zipfile.ZipFile(archive) as z:
        prefix = pack.PACKAGE_NAME + "/"
        members = {n.removeprefix(prefix) for n in z.namelist()}
        check("A: tests/fake-b1 ships in the release ZIP",
              "tests/fake-b1" in members)
        mode = ((z.getinfo(prefix + "tests/fake-b1").external_attr >> 16) & 0o111
                if "tests/fake-b1" in members else 0)
        check("A: fake-b1 ships executable", mode == 0o111, oct(mode))
        check("A: fake-b1 is explicitly included and executable",
              "tests/fake-b1" in pack.INCLUDE_FILES and
              "tests/fake-b1" in pack.EXECUTABLE_FILES)
        check("B: the ZIP has no git metadata",
              not any(n.startswith(".git/") or n == ".git" for n in members))
        gp = z.read(prefix + PIN).decode("utf-8")
        check("B: the shipped gitpin retains its checkout porcelain law",
              "status --porcelain" in gp and "_git_present" in gp)
        check("B: the git-free fallback verifies bytes rather than skipping",
              "sha256" in gp and "byte-identical" in gp and "GIT" in gp)
        refs = [m for m in sorted(members)
                if m.startswith("tests/test_") and m.endswith(".py") and
                ("tests/fake-b1" in z.read(prefix + m).decode("utf-8") or
                 "fake-b1" in m)]
        check("C: shipped tests referencing fake-b1 have the fixture",
              bool(refs) and "tests/fake-b1" in members, str(refs))
        z.extractall(temporary / "extract")
        for info in z.infolist():
            path = temporary / "extract" / info.filename
            if path.is_file():
                path.chmod((info.external_attr >> 16) & 0o777)

    package = temporary / "extract" / pack.PACKAGE_NAME
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_") and
           not k.startswith("HERMES_SESSION_") and
           not k.startswith("HERMES_UI_SESSION_") and
           k not in {"WF_TEST_BUILD", "WF_RUNS_ROOT", "HERMES_HOME"}}
    env["GIT_CEILING_DIRECTORIES"] = str(package.parent)
    # The shipped pin executes B1, so one subprocess exercises both originals
    # within the serial suite's per-case wall. Missing fixtures fail admission.
    if all((package / f).is_file() for f in FIXTURES):
        before = snapshot(package)
        result, output = run(package, PIN, env)
        check("D: extracted gitpin executes B1 successfully without git metadata",
              result.returncode == 0 and "ALL PASS" in output and
              "PASS B1 raw run" in output and "git-free fallback" in output,
              f"rc={result.returncode}\n{output[-2000:]}")
        check("D: extracted runtime leaves all fixture bytes unchanged",
              snapshot(package) == before)

        # Only this disposable tree changes: child success must not hide mutation.
        (package / B1).write_text(
            "from pathlib import Path\n"
            "p = Path(__file__).resolve().parent / 'fake-b1'\n"
            "p.write_bytes(p.read_bytes() + b'\\n# mutation tripwire\\n')\n"
            "print('ALL PASS')\n", encoding="utf-8")
        result, output = run(package, PIN, env)
        check("E: git-free pin rejects fixture mutation despite child success",
              result.returncode == 1 and "FAIL est-1nkx ZIP" in output and
              "tests/fake-b1" in output, f"rc={result.returncode}\n{output[-2000:]}")

print("ALL PASS" if ok else "FAILURES", flush=True)
raise SystemExit(0 if ok else 1)
