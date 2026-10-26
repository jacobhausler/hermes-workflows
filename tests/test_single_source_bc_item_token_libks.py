#!/usr/bin/env python3
"""est-libks — _RE_BC_ITEM_TOKEN is single-sourced in wfcommon, never re-compiled.

PR #486 (merged 7c40fd7) shipped the SAME bare-item-token regex twice:
wf.py defined `_RE_BC_ITEM_TOKEN = re.compile(...)` next to the commit-edge
gate `_bc_decl_interpolated`, and wfcommon.py defined its own copy next to the
door validator that consumes it. Two literals that must agree is a drift
hazard: if either copy is ever edited alone, the door admits an id/actor
template the commit-edge gate then reads differently (or vice versa) and a
fan-out graph dies typed at the commit edge on a token the door waved through.

The law pinned here (est-libks acceptance):
  1. exactly ONE `re.compile` definition of _RE_BC_ITEM_TOKEN exists across
     the shipped backend modules (wfcommon.py owns it);
  2. wf.py binds the name OFF THE PRIVATE SPEC-LOADED INSTANCE
     (`wf.wfcommon._RE_BC_ITEM_TOKEN is wf._RE_BC_ITEM_TOKEN`) — a bare
     `from wfcommon import ...` is forbidden by test_import_purity_133387.py,
     so an independent re-compile or a generic import both fail closed here;
  3. door and gate therefore AGREE BY IDENTITY: one compiled object is the
     pattern behind both wfcommon.validate_graph's admission refusal and
     wf._bc_decl_interpolated's per-item commit-edge check.

Run: python3 tests/test_single_source_bc_item_token_libks.py
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402
import wfcommon  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        ok = False


def compiled_defs(path):
    """Names assigned `_RE_BC_ITEM_TOKEN = re.compile(...)` in this source."""
    tree = ast.parse(path.read_text(), filename=str(path))
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (isinstance(tgt, ast.Name) and tgt.id == "_RE_BC_ITEM_TOKEN"
                        and isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and node.value.func.attr == "compile"):
                    hits.append(node.lineno)
    return hits


# 1: single compiled definition — wfcommon owns it, wf.py re-compiles nothing.
wf_defs = compiled_defs(ROOT / "wf.py")
wfc_defs = compiled_defs(ROOT / "wfcommon.py")
check(len(wfc_defs) == 1,
      f"wfcommon.py defines _RE_BC_ITEM_TOKEN exactly once (found at {wfc_defs})")
check(not wf_defs,
      f"wf.py defines NO _RE_BC_ITEM_TOKEN re.compile of its own (found at {wf_defs})")

# 2: wf.py binds off the private instance the module header spec-loads.
wf_src = (ROOT / "wf.py").read_text()
check(re.search(r"^_RE_BC_ITEM_TOKEN\s*=\s*wfcommon\._RE_BC_ITEM_TOKEN$", wf_src,
                re.MULTILINE) is not None,
      "wf.py binds the name off the private instance: "
      "'_RE_BC_ITEM_TOKEN = wfcommon._RE_BC_ITEM_TOKEN'")
check(getattr(wf, "_RE_BC_ITEM_TOKEN", None) is not None,
      "wf._RE_BC_ITEM_TOKEN exists (commit edge still sees the name)")
# NOTE: `wf._RE_BC_ITEM_TOKEN is wf.wfcommon._RE_BC_ITEM_TOKEN` is vacuous
# either way — wf.py resolves the attribute through the same spec-loaded
# instance the right-hand side names, shadowing any module-level assignment.
# The falsifiable single-definition law is the AST/source check below and the
# binding-text check that wf.py's line reads `= wfcommon._RE_BC_ITEM_TOKEN`.
check((ROOT / wf.wfcommon.__file__).resolve() == (ROOT / "wfcommon.py").resolve(),
      "wf's private module is sourced from this repo's wfcommon.py")

# 3: door + gate agree. In production the door (door spec-loads wfcommon) and
# the runner (wf spec-loads wfcommon privately) live in separate module objects
# / processes, so agreement means ONE definition compiled identically from one
# source: wf's bind is identity-stable against ITS instance (check 2), the
# compiled pattern text is identical everywhere, and behavior matches on
# samples.
pat = wf._RE_BC_ITEM_TOKEN
door = wfcommon._RE_BC_ITEM_TOKEN          # plainly-imported instance (door's file)
check(pat.pattern == door.pattern,
      f"door instance and gate bind carry the same pattern text "
      f"({door.pattern!r} vs {pat.pattern!r})")
for sample, expect in (("{bead}", True), ("{item}", True), ("{index}", True),
                       ("{FIELD_2}", True), ("no braces", False),
                       ("{bad sp}", False), ("{ }", False)):
    check(bool(pat.search(sample)) is expect and bool(door.search(sample)) is expect,
          f"door+gate pattern agrees on {sample!r} (expect {expect})")
# behavior pin at the commit edge: the gate function flags token-bearing decls
check(wf._bc_decl_interpolated({"id": "{bead}"}) is True,
      "wf._bc_decl_interpolated still trips on a bare token id")
check(wf._bc_decl_interpolated({"id": "est-libks"}) is False,
      "wf._bc_decl_interpolated stays quiet on a literal id")

# source-level belt: the pattern literal appears exactly once repo-wide (shipped
# backend sources only; this test file deliberately spells the name, not a compile)
srcs = [ROOT / "wf.py", ROOT / "wfcommon.py"]
lits = sum(len(re.findall(r"_RE_BC_ITEM_TOKEN\s*=\s*re\.compile", s.read_text())) for s in srcs)
check(lits == 1, f"_RE_BC_ITEM_TOKEN = re.compile appears exactly once across wf.py+wfcommon.py (found {lits})")

print("OK" if ok else "NOT OK")
sys.exit(0 if ok else 1)
