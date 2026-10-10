#!/usr/bin/env python3
"""est-1nkx — the release ZIP must run the tests it ships.

INSTALL.md documents running all shipped tests in the extracted ZIP. The PR #158
second-read found two package deaths, both the est-4vnq finding-4 shape (a
shipped test executes an unpackaged input):

  (1) tests/test_sprint101w2_B1-classes.py snapshots tests/fake-b1
      (TRACKED_SHA_BEFORE) — pack.py's INCLUDE_FILES never carried the fixture,
      so the ZIP copy died FileNotFoundError.
  (2) tests/test_fakeb1_gitpin_954r.py unconditionally ran `git status` — the
      ZIP carries no git metadata, so it died rc=128 not-a-repository. The pin
      now falls back (git-free ZIPs only) to the byte-equivalent guarantee:
      SHA-256 over the same fixture bytes porcelain reads. A checkout without
      git metadata is NOT a silent pass of the git law — it verifies the
      equivalent, and a real checkout still runs the porcelain legs.

Pins (all against a fresh build via scripts/pack.py, no network, no git):
  A) fake-b1 ships, executable (the est-954r fixture is audited/snapshotted by
     a shipped test — finding-4 law), and the EXECUTABLE_FILES set carries it.
  (B) the shipped ZIP has no .git directory (precondition of the fallback),
      and the gitpin source carries BOTH paths — the git law stays present and
      the fallback is byte-snapshot, never a skip.
  (C) every shipped test that references `tests/fake-b1` has the fixture in the
     package (derived sweep, mirrors the SCRIPT_REF discipline above).

Run: env -u WF_RUNS_ROOT -u HERMES_HOME PYTHONPATH=/opt/hermes /opt/hermes/.venv/bin/python tests/test_release_zip_1nkx.py
"""
import importlib.util
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

_spec = importlib.util.spec_from_file_location("pack_1nkx", ROOT / "scripts/pack.py")
assert _spec and _spec.loader
pack = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pack)

import tempfile
with tempfile.TemporaryDirectory(prefix="zip-1nkx-") as tmp:
    archive = Path(tmp) / "release.zip"
    pack.build(archive)
    with zipfile.ZipFile(archive) as z:
        prefix = pack.PACKAGE_NAME + "/"
        members = {n.removeprefix(prefix) for n in z.namelist()}
        infos = {n.removeprefix(prefix): z.getinfo(prefix + n) for n in members}

        check("A: tests/fake-b1 ships in the release ZIP (est-1nkx finding 1)",
              "tests/fake-b1" in members,
              str(sorted(m for m in members if m.startswith("tests/fake"))))
        mode = (infos["tests/fake-b1"].external_attr >> 16) & 0o111 if "tests/fake-b1" in infos else 0
        check("A: the shipped fake-b1 keeps its executable bit (child, like tests/fake)",
              mode == 0o111, oct(mode))
        check("A: EXECUTABLE_FILES names fake-b1 (the mode pin's source of truth)",
              "tests/fake-b1" in pack.EXECUTABLE_FILES, str(sorted(pack.EXECUTABLE_FILES)))
        check("A: fake-b1 is an explicit INCLUDE_FILES entry (pattern globs never cover it)",
              "tests/fake-b1" in pack.INCLUDE_FILES)

        check("B: the ZIP carries no git metadata — the fallback path is the live one",
              not any(n.startswith(".git/") or n == ".git" for n in members))
        gp = (ROOT / "tests/test_fakeb1_gitpin_954r.py").read_text(encoding="utf-8")
        check("B: the gitpin keeps its git law (porcelain + git-present probe present)",
              "status --porcelain" in gp and "_git_present" in gp)
        check("B: the git-free fallback verifies bytes, never passes silently",
              "sha256" in gp and "byte-identical" in gp and "GIT" in gp)

        # (C) derived sweep: any shipped test touching tests/fake-b1 needs the fixture.
        refs = [m for m in sorted(members)
                if m.startswith("tests/test_") and m.endswith(".py")
                and ("tests/fake-b1" in (ROOT / m).read_text(encoding="utf-8")
                     or "fake-b1" in m)]
        check("C: shipped tests reference tests/fake-b1 (sweep sees them)", bool(refs), str(refs))
        check("C: every shipped test referencing tests/fake-b1 gets the packaged fixture",
              ("tests/fake-b1" in members) if refs else True, str(refs))

print("ALL PASS" if ok else "FAILURES")
raise SystemExit(0 if ok else 1)
