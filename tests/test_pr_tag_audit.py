#!/usr/bin/env python3
"""Behavioral tests for scripts/pr_tag_audit.py (the release-side tag-state gate).

Numbered checks map to the reconcile findings (est-4vnq):
  A1-A4  finding 2 — INVERSE direction: an `(open PR #NN)` tag on a row whose
         action IS dispatched (shipped) must FAIL even while that PR is open.
         The old audit checked only PR STATE, so a shipped `run` row tagged
         `(open PR #47)` printed `OK — 8 tagged line(s)` and exited 0 (observed
         red-proof on base f83e5d0: `pr_tag_audit: OK — 8 tagged line(s),
         every referenced PR still open` / exit=0 with PR #47 verified OPEN).
  B1-B2  finding 3 — missing `gh` must exit 2 with file:line tag diagnostics,
         not raise FileNotFoundError and exit 1 (observed red-proof on base:
         uncaught traceback `FileNotFoundError: [Errno 2] No such file or
         directory: 'gh'` / exit=1, stdout empty).
  C1-C3  state machine, exercised with a deterministic fake `gh` (never the
         network): merged -> exit 1 + rewrite owed; closed -> exit 1; all open
         -> exit 0.

The script resolves ROOT from its own file location, so every scenario copies
the minimum file set into a scratch dir and mutates THAT — the tree is never
touched. Stdlib only; no network; gh is only ever the fixture or genuinely
absent (PATH=).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pr_tag_audit.py"
REPO = "octocat/whatever"  # never contacted: fake gh answers, or gh is absent

ok = True
count_pass = 0
count_fail = 0


def check(label, cond, detail: object = ""):
    global ok, count_pass, count_fail
    if cond:
        count_pass += 1
    else:
        count_fail += 1
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and cond


def make_tree(tmp: Path, readme_mut=None) -> Path:
    """Copy the minimal file set the audit touches; optionally rewrite README.md."""
    tree = tmp / "tree"
    (tree / "scripts").mkdir(parents=True)
    shutil.copy2(SCRIPT, tree / "scripts" / "pr_tag_audit.py")
    for f in ("__init__.py", "wfcommon.py", "README.md", "SKILL.md", "AGENTS.md",
              "CONTRIBUTING.md", "INSTALL.md", "CHANGELOG.md"):
        src = ROOT / f
        if src.is_file():
            shutil.copy2(src, tree / f)
    (tree / "references").mkdir()
    for p in sorted((ROOT / "references").glob("*.md")):
        shutil.copy2(p, tree / "references" / p.name)
    if readme_mut:
        p = tree / "README.md"
        p.write_text(readme_mut(p.read_text(encoding="utf-8")), encoding="utf-8")
    return tree


def make_fake_gh(tmp: Path, states: dict) -> Path:
    """A deterministic stand-in for gh: answers `pr view N --repo ... --json ...`
    from a {number: OPEN|MERGED|CLOSED} map; unknown number -> exit 3."""
    bindir = tmp / "fakebin"
    bindir.mkdir(exist_ok=True)
    gh = bindir / "gh"
    gh.write_text(
        f"#!{sys.executable}\n"
        "import json, sys\n"
        f"states = {states!r}\n"
        "argv = sys.argv[1:]\n"
        "assert argv[:2] == ['pr', 'view'], argv\n"
        "n = int(argv[2])\n"
        "if n not in states:\n"
        "    sys.exit(3)\n"
        "s = states[n]\n"
        "sys.stdout.write('MERGED\\n' if s == 'MERGED' else s + '\\n')\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    return bindir


def run_audit(tree: Path, env: dict):
    r = subprocess.run([sys.executable, str(tree / "scripts" / "pr_tag_audit.py"),
                        "--repo", REPO],
                       capture_output=True, text=True, env=env, timeout=60)
    return r


NO_GH = {k: v for k, v in os.environ.items() if k not in ("WF_RUNS_ROOT", "HERMES_HOME")}
NO_GH["PATH"] = ""  # gh (and git) genuinely absent; --repo passed so git is not needed

with tempfile.TemporaryDirectory(prefix=".tmp-prtag-", dir=ROOT / "tests") as td:
    tdp = Path(td)

    # ---- A1: shipped `run` row tagged (open PR #47) -> exit 1, names README.md + line
    tag_line = "| `run` | *(open PR #47)* Launch a graph from"
    tree = make_tree(tdp / "a", lambda s: s.replace(
        "| `run` | Launch a graph from", tag_line, 1))
    r = run_audit(tree, NO_GH)  # no gh at all: the shipped-row lie is decidable offline
    check("A1 shipped row tagged (open PR #47) exits nonzero", r.returncode == 1,
          f"exit={r.returncode} out={r.stdout!r} err={r.stderr!r}")
    check("A2 the failure names the file:line and the row",
          re.search(r"README\.md:\d+", r.stdout + r.stderr) is not None
          and "`run`" in r.stdout + r.stderr,
          f"out={r.stdout!r} err={r.stderr!r}")
    check("A3 the message says the row is shipped/dispatched",
          re.search(r"shipped|dispatch", r.stdout + r.stderr, re.I) is not None,
          f"out={r.stdout!r}")
    # A4: same mutation, fake gh says PR #47 is OPEN — the PR being open must NOT save it
    bindir = make_fake_gh(tdp / "a", {47: "OPEN", 84: "OPEN", 121: "OPEN"})
    r = run_audit(tree, {**NO_GH, "PATH": f"{bindir}:{NO_GH['PATH']}"})
    check("A4 open PR state cannot launder a shipped-row tag", r.returncode == 1,
          f"exit={r.returncode} out={r.stdout!r} err={r.stderr!r}")

    # ---- B1/B2: gh genuinely absent, unmutated tree -> exit 2 + named diagnostics
    tree = make_tree(tdp / "b")
    r = run_audit(tree, NO_GH)
    check("B1 missing gh exits 2 (docstring promise), not 1", r.returncode == 2,
          f"exit={r.returncode} err_tail={r.stderr[-160:]!r}")
    diag = r.stdout + r.stderr
    check("B2 no-gh diagnostics name file:line and PR number for each tag",
          r"Traceback" not in r.stderr
          and re.search(r"README\.md:\d+.*#", diag) is not None
          and re.search(r"references[/\\]\w+\.md:\d+", diag) is not None,
          f"out={r.stdout[:300]!r} err={r.stderr[:300]!r}")

    # ---- C: state machine with fake gh on the UNMUTATED tree
    states_all_open = {47: "OPEN", 84: "OPEN", 121: "OPEN"}
    tree = make_tree(tdp / "c")
    bindir = make_fake_gh(tdp / "c", states_all_open)
    r = run_audit(tree, {**NO_GH, "PATH": str(bindir)})
    check("C1 every tag pointing at an OPEN PR exits 0", r.returncode == 0,
          f"exit={r.returncode} out={r.stdout!r} err={r.stderr!r}")
    # find which PR numbers the tree actually references, to aim the C2/C3 mutations
    nums = set()
    tree_files = list((tree / "references").glob("*.md")) + [tree / f for f in
                    ("README.md", "SKILL.md", "AGENTS.md", "CONTRIBUTING.md", "INSTALL.md", "CHANGELOG.md")]
    tag_re = re.compile(r"open PRs?\s+((?:#\d+)(?:[/:,\s-]*#\d+)*)")
    for f in tree_files:
        if f.is_file():
            for m in tag_re.finditer(f.read_text(encoding="utf-8")):
                nums.update(int(n) for n in re.findall(r"#(\d+)", m.group(1)))
    check("C0 the audit target tree carries real open-PR tags to audit", bool(nums), nums)
    a_num = sorted(nums)[0]
    bindir = make_fake_gh(tdp / "c", {**states_all_open, a_num: "MERGED"})
    r = run_audit(tree, {**NO_GH, "PATH": str(bindir)})
    check(f"C2 merged PR #{a_num} -> exit 1 naming file:line and the rewrite owed",
          r.returncode == 1 and re.search(rf"README\.md:\d+.*#{a_num}|: {a_num}\b", r.stdout, re.M) is not None
          and "shipped in" in r.stdout,
          f"exit={r.returncode} out={r.stdout!r}")
    bindir = make_fake_gh(tdp / "c", {**states_all_open, a_num: "CLOSED"})
    r = run_audit(tree, {**NO_GH, "PATH": str(bindir)})
    check(f"C3 closed PR #{a_num} -> exit 1 with remove-for-closed guidance",
          r.returncode == 1 and re.search(r"closed", r.stdout, re.I) is not None,
          f"exit={r.returncode} out={r.stdout!r}")

    # ---- D: the doc-only sanctioned shape stays green — release_lock row + open #47
    tree = make_tree(tdp / "d")
    bindir = make_fake_gh(tdp / "d", states_all_open)
    r = run_audit(tree, {**NO_GH, "PATH": str(bindir)})
    check("D unshipped (doc-only) tagged rows are the sanctioned green shape",
          r.returncode == 0 and "OK" in r.stdout,
          f"exit={r.returncode} out={r.stdout!r}")

print(f"TOTAL {count_pass} PASS {count_fail} FAIL")
sys.exit(0 if ok else 1)
