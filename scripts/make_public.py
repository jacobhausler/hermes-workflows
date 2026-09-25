#!/usr/bin/env python3
"""Build a publishable tree from git ls-files, refusing to emit private strings.

Copies every tracked file (via `git -C <repo> ls-files`) EXCEPT:
  - docs/PUBLISH-SCRUB.md            (the audit itself quotes private strings)
  - .git/  __pycache__  tests/home*  *.log
(.github/, .gitignore, examples/ and scripts/.scrub-guards ship: CI runs this
same audit in the public repo and needs the allow-list.)
Then audits the staged copy with the scrub pattern; any hit not allow-listed
in scripts/.scrub-guards (file / file:LINE / regex:PATTERN) exits 1 printing
file:line of every offender. Stdlib only.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import shutil
import subprocess
import sys
from pathlib import Path

GIT = "/usr/bin/git"
PATTERN = re.compile(r"192\.168|\bhaus\b|callindor|gaidin|rhuidean|jacob|nous", re.I)
EXCLUDE_DIRS = {".git", "__pycache__"}
EXCLUDE_PATTERNS = ["docs/PUBLISH-SCRUB.md",
                    "*/__pycache__/*", "__pycache__/*",
                    "tests/home*", "*.log", "*/.git", "*/.git/*"]
AUDIT_SUFFIXES = {".py", ".js", ".md", ".json", ".yaml"}


def excluded(rel: str) -> bool:
    parts = Path(rel).parts
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    return any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDE_PATTERNS)


def load_guards(repo: Path) -> tuple[set[str], set[str], list[re.Pattern]]:
    files, lines, regexes = set(), set(), []
    text = (repo / "scripts" / ".scrub-guards").read_text(encoding="utf-8")
    for raw in text.splitlines():
        entry = raw.strip()
        if not entry or entry.startswith("#"):
            continue
        if entry.startswith("regex:"):
            regexes.append(re.compile(entry[len("regex:"):], re.I))
        elif ":" in entry:
            files_part, line_no = entry.rsplit(":", 1)
            lines.add((files_part, int(line_no)))
        else:
            files.add(entry)
    return files, lines, regexes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="destination directory for the publishable tree")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    target = Path(args.target).resolve()
    if target.exists() and any(target.iterdir()):
        print(f"refusing: target exists and is not empty: {target}", file=sys.stderr)
        return 1

    listed = subprocess.run([GIT, "-C", str(repo), "ls-files"],
                            capture_output=True, text=True, check=True).stdout.splitlines()
    copied = [rel for rel in listed if not excluded(rel)]

    # Audit BEFORE copying: a non-guard hit in any copied file is fatal.
    guard_files, guard_lines, guard_regexes = load_guards(repo)
    offences: list[str] = []
    for rel in copied:
        if Path(rel).suffix not in AUDIT_SUFFIXES:
            continue
        text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if PATTERN.search(line):
                if rel in guard_files or (rel, i) in guard_lines:
                    continue
                if any(rx.search(line) for rx in guard_regexes):
                    continue
                offences.append(f"{repo / rel}:{i}: {line.strip()[:120]}")
    if offences:
        print("SCRUB FAILED — non-guard private-string hits in copied files:", file=sys.stderr)
        for o in offences:
            print(o, file=sys.stderr)
        return 1

    target.mkdir(parents=True, exist_ok=True)
    for rel in copied:
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / rel, dst)
    print(f"OK: {len(copied)} files published to {target} (0 scrub hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
