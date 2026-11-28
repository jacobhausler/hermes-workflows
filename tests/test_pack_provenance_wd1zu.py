#!/usr/bin/env python3
"""Provenance honesty (gauntlet-1): pack.py refuses to build on a dirty tree and
`--verify` demands every shipped member equal its git blob at the rev install.json
stamps — install.json can never lie about its bytes. The dirty guard is exercised
in-process against scratch repos; the ZIP-vs-blob leg runs against the real tree
(skipping visibly when the checkout is dirty or not a repo, where the refusal
itself has already proven the guard).
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(label: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{label} — {detail}")
    print("PASS", label)


def load_pack():
    spec = importlib.util.spec_from_file_location("pack_wd1zu", ROOT / "scripts" / "pack.py")
    if spec is None or spec.loader is None:
        raise AssertionError("scripts/pack.py cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.email=wd1zu@example.invalid",
         "-c", "user.name=wd1zu", *args],
        cwd=repo, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {result.stderr[-200:]}")
    return result.stdout


def make_scratch_repo() -> Path:
    repo = Path(tempfile.mkdtemp(prefix="wd1zu-")) / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "plugin.yaml").write_text("version: 9.9.9\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    return repo


def guard_legs(pack) -> None:
    if not os.environ.get("PATH", "").strip():
        print("SKIP dirty-tree legs (no git on PATH)")
        return
    saved_root = pack.ROOT
    try:
        repo = make_scratch_repo()
        pack.ROOT = repo
        check("clean scratch tree passes the dirty guard", pack.dirty_tree_report() == [])

        (repo / "tracked.txt").write_text("edited\n", encoding="utf-8")
        report = pack.dirty_tree_report()
        check("modified tracked file trips the guard",
              any("tracked.txt" in line and "dirty tracked" in line for line in report),
              repr(report))

        (repo / "tracked.txt").write_text("staged\n", encoding="utf-8")
        git(repo, "add", "tracked.txt")
        check("staged change trips the guard",
              any("tracked.txt" in line for line in pack.dirty_tree_report()))

        git(repo, "restore", "--staged", "tracked.txt")
        git(repo, "checkout", "--", "tracked.txt")
        (repo / "junk-dir").mkdir()
        check("untracked residue outside the include patterns does not trip the guard",
              pack.dirty_tree_report() == [])

        (repo / "untracked_test_probe.py").write_text("x = 1\n", encoding="utf-8")
        pack.INCLUDE_PATTERNS = ("untracked_*",)
        report = pack.dirty_tree_report()
        check("untracked file matched by an include pattern trips the guard",
              any("untracked_test_probe.py" in line for line in report), repr(report))

        os.environ["HERMES_WF_PACK_ALLOW_DIRTY"] = "1"
        check("explicit override silences the guard (non-git dist path seam)",
              pack.dirty_tree_report() == [])
        del os.environ["HERMES_WF_PACK_ALLOW_DIRTY"]
    finally:
        pack.ROOT = saved_root


def zip_blob_leg() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain", "-uno"], cwd=ROOT, capture_output=True, text=True,
    )
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True)
    if status.returncode != 0 or head.returncode != 0:
        print("SKIP ZIP-vs-blob leg (checkout is not a git repo)")
        return
    if status.stdout.strip():
        print("SKIP ZIP-vs-blob leg (tracked tree dirty; dirty guard already reported)")
        return
    stamp = head.stdout.strip()
    with tempfile.TemporaryDirectory(prefix="wd1zu-zip-") as td:
        out = Path(td) / "release.zip"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "pack.py"), "--output", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        check("clean tree builds", result.returncode == 0,
              (result.stdout + result.stderr)[-400:])
        with zipfile.ZipFile(out) as archive:
            root = [n for n in archive.namelist() if n.endswith("/install.json")][0]
            rec = json.loads(archive.read(root).decode("utf-8"))
        check("install.json stamps this checkout's rev",
              rec.get("source_commit") == stamp, repr(rec.get("source_commit")))
        verified = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "pack.py"), "--verify", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )
        check("--verify proves every member matches the blob at the stamped rev",
              verified.returncode == 0, (verified.stdout + verified.stderr)[-400:])


def main() -> None:
    pack = load_pack()
    guard_legs(pack)
    zip_blob_leg()
    print("ALL PASS")


if __name__ == "__main__":
    main()
