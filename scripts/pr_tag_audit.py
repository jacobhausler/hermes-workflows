#!/usr/bin/env python3
"""pr_tag_audit.py — release-time gate for `(open PR #NN)` doc tags.

Docs that describe UNMERGED behavior carry an `(open PR #NN)` tag (see
tests/test_docs_surface_drift.py for the README action-table half of the same
law). A tag that only a human remembers to age is a definition that rots in
prose: when the PR merges, the tag must be rewritten to shipped-in-vX. This
script makes the aging mechanical — run it in the release/pack step.

FAILS CLOSED:
  - any tag whose PR is MERGED or CLOSED -> exit 1, with file:line and the
    rewrite owed (`(shipped in vX)` / remove for closed-without-merge);
  - a tag whose PR state cannot be verified (no gh, no auth, unknown repo) ->
    exit 2; an unverifiable tag is an unaged tag.

Exit 0 only when every documented open-PR tag points at a PR that is, in fact,
still open. Usage:  python3 scripts/pr_tag_audit.py [--repo owner/name]
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ["README.md", "SKILL.md", "AGENTS.md", "CONTRIBUTING.md", "INSTALL.md",
        "CHANGELOG.md"] + [str(p.relative_to(ROOT)) for p in
                          (ROOT / "references").glob("*.md")]
# 'open PR #47', 'open PRs #47/#79', and '(open PR #84)' bolded variants
TAG_RE = re.compile(r"open PRs?\s+((?:#\d+)(?:[/:,\s-]*#\d+)*)")
NUM_RE = re.compile(r"#(\d+)")


def resolve_repo(argv_repo: str | None) -> str | None:
    if argv_repo:
        return argv_repo
    for remote in ("upstream", "origin"):
        r = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", remote],
                           capture_output=True, text=True)
        m = re.search(r"[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$", r.stdout.strip())
        if r.returncode == 0 and m:
            return m.group(1)
    return None


def main() -> int:
    argv_repo = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--repo" else None
    repo = resolve_repo(argv_repo)
    if repo is None:
        print("pr_tag_audit: cannot resolve the GitHub repo (pass --repo owner/name)", file=sys.stderr)
        return 2
    hits = []  # (file, line_no, pr_numbers)
    for rel in SCAN:
        path = ROOT / rel
        if not path.is_file():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in TAG_RE.finditer(line):
                nums = [int(n) for n in NUM_RE.findall(m.group(1))]
                if nums:
                    hits.append((rel, i, nums))
    if not hits:
        print("pr_tag_audit: no open-PR doc tags — nothing to age")
        return 0
    state_cache: dict[int, str | None] = {}

    def state(n: int) -> str | None:
        if n not in state_cache:
            r = subprocess.run(["gh", "pr", "view", str(n), "--repo", repo,
                                "--json", "state,mergedAt", "-q",
                                'if (.mergedAt != null and .mergedAt != "") then "MERGED" else .state end'],
                               capture_output=True, text=True)
            state_cache[n] = r.stdout.strip() if r.returncode == 0 else None
        return state_cache[n]

    problems, unverifiable = [], []
    for rel, line_no, nums in hits:
        for n in nums:
            s = state(n)
            if s is None:
                unverifiable.append((rel, line_no, n))
            elif s != "OPEN":
                problems.append((rel, line_no, n, s))
    for rel, line_no, n in unverifiable:
        print(f"{rel}:{line_no}: cannot verify PR #{n} state (gh unavailable/unauthenticated?) — fail closed")
    for rel, line_no, n, s in problems:
        owed = "(shipped in vX)" if s == "MERGED" else "remove (closed without merge)"
        print(f"{rel}:{line_no}: tag says open, PR #{n} is {s} — rewrite to {owed}")
    if unverifiable:
        print(f"pr_tag_audit: FAIL-CLOSED — {len(unverifiable)} unverifiable tag(s)")
        return 2
    if problems:
        print(f"pr_tag_audit: FAIL — {len(problems)} stale tag(s) must age before release")
        return 1
    print(f"pr_tag_audit: OK — {len(hits)} tagged line(s), every referenced PR still open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
