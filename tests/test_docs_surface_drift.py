"""Docs-surface drift guard: the README's tool-action table must name exactly
the actions the door dispatches, and no open-PR-tagged feature may be described
as shipping. If the code's action set changes, the table changes in the same
commit — or this fails. One source (code), commentary checked against it."""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
readme = (root / "README.md").read_text(encoding="utf-8")

import sys
sys.path.insert(0, str(root))
import importlib.util
spec = importlib.util.spec_from_file_location("_wf_actions_probe", root / "__init__.py")
# ACTIONS is defined at module top; import is cheap (host imports are lazy) — but
# the module name is not importable as a package alias in a bare checkout, so
# parse the literal instead: the dict is the single home of truth (__init__.py).
src = (root / "__init__.py").read_text(encoding="utf-8")
m = re.search(r"ACTIONS = \{", src)
assert m, "ACTIONS dict not found in __init__.py — did its shape change? Update this test WITH the code."
block = src[m.end():m.end() + 1200].split("}", 1)[0]
code_actions = set(re.findall(r'"([a-z_]+)":\s*act_', block))
assert "run" in code_actions and "library" in code_actions and len(code_actions) >= 11, code_actions

# README action table rows: first backticked token of each row under '## The `workflow` tool'
section = readme.split("## The `workflow` tool", 1)
assert len(section) == 2, "README lost the 'The workflow tool' section the action table lives in"
table = section[1].split("Plus a `/wf`", 1)[0]
doc_actions = set(re.findall(r"^\|\s*`([a-z_]+)`", table, re.M))

missing = code_actions - doc_actions
extra = doc_actions - code_actions
assert not missing, f"README action table missing code actions: {sorted(missing)}"
for a in extra:
    row = next(l for l in table.splitlines() if l.strip().startswith(f"| `{a}`"))
    assert re.search(r"open PR #\d+", row), f"README documents action `{a}` not in code and not PR-tagged: {row[:80]}"
print("ALL PASS: docs surface matches code")
