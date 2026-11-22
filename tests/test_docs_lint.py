#!/usr/bin/env python3
"""bd_2026-11-13-7m0 — the runtime-docs dead-reference lint bites.

Behavior contract of tools/docs_lint.py (not its internals):
  (1) the real tree is GREEN in full mode (fixture run + executed commands);
  (2) the summary line proves the fixture really exercised docs claims
      (exercised >= 40 and at least 3 doc commands executed — a number
      reported is a number run: the counts come from the tool's own stdout);
  (3) every violation class bites with exact `file:line` naming, proven by
      targeted mutations of a COPY of docs/runtime (the real tree untouched):
      dead-verb, dead-action, dead-env, dead-path, dead-field, dead-symbol;
  (4) the lint is read-only and idempotent (same exit, clean git status).

Standalone, stdlib-only: python3 tests/test_docs_lint.py
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LINT = str(ROOT / "tools" / "docs_lint.py")
DOCS = ROOT / "docs" / "runtime"

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


def lint(*args):
    p = subprocess.run([sys.executable, LINT, *args], capture_output=True,
                       text=True, timeout=180, cwd=str(ROOT))
    return p.returncode, p.stdout + p.stderr


def mutated_copy(old, new):
    """Copy docs/runtime, replace the FIRST occurrence of `old`, return
    (docs_dir, expected_file_stem, expected_line)."""
    tmp = Path(tempfile.mkdtemp(prefix="docsmut-"))
    dst = tmp / "runtime"
    shutil.copytree(DOCS, dst)
    for md in sorted(dst.rglob("*.md")):
        text = md.read_text()
        if old in text:
            line = next(i for i, ln in enumerate(text.splitlines(), 1) if old in ln)
            md.write_text(text.replace(old, new, 1))
            return dst, md.name, line
    raise AssertionError(f"mutation anchor {old!r} not found in docs/runtime")


try:
    # ------------------------------------------------------------- (1) green
    rc, out = lint()
    check("1 real tree green, full mode (fixture + executed commands)", rc == 0, out[-1500:])

    # --------------------------------------------------- (2) exercise counts
    m = re.search(r"claims=(\d+).*exercised=(\d+) literal-backed=(\d+) violations=(\d+)", out)
    claims, exercised, literal, viol = (list(map(int, m.groups())) if m else [0, 0, 0, 1])
    check("2 summary parses and claims a real extraction", claims >= 150 and viol == 0, out)
    check("2 fixture exercised >= 40 claims (paths/fields/commands on disk, not regex)",
          exercised >= 40, f"exercised={exercised}")
    check("2 the three `wf.py recover <run_id>` doc commands EXECUTED rc0 "
          "(no cmd-exec-fail, and the not-executed note is absent)",
          "cmd-exec-fail" not in out and "cmd not executed" not in out)

    # -------------------------------------------------- (3) mutation bites
    for label, old, new, why in [
        ("3 dead verb bites", "wf.py recover <run_id>", "wf.py resurrect <run_id>", "dead-verb"),
        ("3 dead action bites", '{action:"run"', '{action:"resume"', "dead-action"),
        ("3 dead env bites", "WF_RUNS_ROOT", "WF_RUNS_ROOTX", "dead-env"),
        ("3 dead path bites", "`events.jsonl`", "`event-log.jsonl`", "dead-path"),
        ("3 dead field bites (shape block key)", '"declared_s"', '"declared_q"', "dead-field"),
        ("3 dead symbol bites (Citations)", "`wfcommon.run_state`", "`wfcommon.run_states`",
         "dead-symbol"),
    ]:
        dst, stem, line = mutated_copy(old, new)
        rc2, out2 = lint("--docs", str(dst), "--no-fixture")
        named = re.search(rf"{re.escape(stem)}:{line}: {why} ", out2)
        check(label + " — exits nonzero naming file:line",
              rc2 == 1 and named is not None, out2[:900])
        shutil.rmtree(dst.parent, ignore_errors=True)

    # (3b) the mutation's file:line is the TRUE mutated line (±0): re-check
    # one case with a second anchor at a different line to pin naming truth.
    dst, stem, line = mutated_copy("`wake.jsonl`", "`wakened.jsonl`")
    rc2, out2 = lint("--docs", str(dst), "--no-fixture")
    check("3 dead path names the exact mutated line",
          rc2 == 1 and re.search(rf"{re.escape(stem)}:{line}: dead-path ", out2), out2[:900])
    shutil.rmtree(dst.parent, ignore_errors=True)

    # ------------------------------------------------ (4) read-only + idempotent
    gs_before = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                               capture_output=True, text=True).stdout
    rc3, out3 = lint("--no-fixture")
    rc4, out4 = lint("--no-fixture")
    gs_after = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                              capture_output=True, text=True).stdout
    check("4 idempotent: static mode exits identically on repeat runs", rc3 == rc4 == 0)
    check("4 the lint writes nothing (git status identical before/after)",
          gs_before == gs_after)
finally:
    pass

print("RESULT " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
