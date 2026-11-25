"""Portable authoring skill contract; no provider or live-home dependencies."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
skill = (root / "SKILL.md").read_text(encoding="utf-8")
assert skill.startswith("---\n")
front, body = skill.split("---\n", 2)[1:]
match = re.search(r'^description:\s*["\']?([^\n"\']+)', front, re.M)
assert match is not None
desc = match.group(1)
assert all(word in desc[:57].lower() for word in ("workflow", "fan-out", "audit", "census")), desc
assert len(desc) <= 60, desc
assert len(skill.splitlines()) < 110, len(skill.splitlines())
assert "cheapest tier" not in skill.lower()
assert "haus " not in skill.lower()
assert "/opt/hermes" not in skill
assert "```json" not in skill  # main guide should not duplicate reference grammar
assert "Cards are optional" in skill, "SKILL.md must not require rendered cards for execution"
# 2.0 gate-handoff law (bd_2026-11-13-1v2, W6 fix-forward). #716 deleted the
# nudge/composer handoff: a Desktop answer is RECORD-ONLY (the UI door calls
# _release_core(..., ui=True), which respawns nothing — dashboard/plugin_api.py
# release_gate says so in its own docstring); `release` is the verb that moves
# an idle runner; `View exact gate` on the receipt is NAVIGATION only. The old
# `"composer" in skill` pin forced the retired teaching to survive, so green
# here now means behavior-aware: the three distinct effects are named AND the
# mechanism #716 removed is absent from both the skill copy and the shipped
# desktop surface.
_skill_l = skill.lower()
assert "composer" not in _skill_l and "draft text" not in _skill_l and "resume line" not in _skill_l, \
    "SKILL.md must not teach the retired composer/draft gate handoff (#716)"
assert "record-only" in _skill_l, "SKILL.md must state the record-only Desktop answer"
assert "`_ui`" in skill, "SKILL.md must name the _ui provenance the door stamps"
assert "respawn" in _skill_l, "SKILL.md must name what a Desktop answer never does and which verb does"
assert "View exact gate" in skill, "SKILL.md must distinguish the receipt's navigation-only action"
_plugin = (root / "desktop" / "plugin.js").read_text(encoding="utf-8")
for _gone in ("nudgeOwner", "composer.submit", "insertText"):
    assert _gone not in _plugin, f"desktop half still carries the retired {_gone}"
# Closed-list pin, behavior not string: the AGENTS §4a action census must equal
# the REGISTERED door schema exactly, both directions, and its stated count must
# equal the real set size. SKILL.md may only name actions that exist. Extracted
# via AST, not import: __init__.py evaluates 3.10+ annotations at exec, and this
# contract must run on the system python.
import ast as _ast
_tree = _ast.parse((root / "__init__.py").read_text(encoding="utf-8"))
_params = next(_n for _n in _tree.body if isinstance(_n, _ast.Assign)
               and getattr(_n.targets[0], "id", "") == "WORKFLOW_PARAMS")
_door_actions = set(_ast.literal_eval(_params.value)["properties"]["action"]["enum"])
_agents = (root / "AGENTS.md").read_text(encoding="utf-8")
_m = re.search(r"all (\d+): `([a-z_/]+)`", _agents)
assert _m is not None, "AGENTS.md §4a must carry the closed action census"
_doc_actions = set(_m.group(2).split("/"))
assert _doc_actions == _door_actions, \
    f"AGENTS action census {_doc_actions ^ _door_actions} drifts from the registered schema"
assert int(_m.group(1)) == len(_door_actions), f"AGENTS names {_m.group(1)} but the schema has {len(_door_actions)}"
assert set(re.findall(r'action:"(\w+)"', skill)) <= _door_actions, \
    "SKILL.md teaches an action the door does not register"
assert "redrive" in _skill_l, "SKILL.md must teach the redrive re-drive"
assert "graph_path" in skill and "proposed" not in skill.lower()
assert "interrupted" in skill
assert "seat default" in skill.lower() and "not" in skill.lower()
assert all((root / "references" / f).is_file() for f in ("grammar.md", "operations.md", "development.md"))
assert "agent.when" in (root / "references/grammar.md").read_text()
_ver = re.search(r"^version:\s*([\d.]+)", (root / "plugin.yaml").read_text(), re.M).group(1)
assert f"workflow {_ver}" in (root / "references/grammar.md").read_text().lower(), f"grammar.md must name {_ver}"
assert f"version: {_ver}" in skill, f"SKILL.md front-matter must name {_ver}"
# A6 drift guard: every shape row in budgets.md must equal SHAPE_PRESETS exactly.
import sys as _sys
_sys.path.insert(0, str(root))
import wfcommon as _wfc
_budgets = (root / "references/budgets.md").read_text(encoding="utf-8")
_rows = dict((m[0], (int(m[1]), int(m[2]))) for m in
             re.findall(r"^\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", _budgets, re.M))
assert set(_rows) == set(_wfc.SHAPE_PRESETS), f"budgets.md shapes {_rows} != SHAPE_PRESETS"
for _shape, _preset in _wfc.SHAPE_PRESETS.items():
    assert _rows[_shape] == (_preset["max_turns"], _preset["timeout"]), \
        f"budgets.md row {_shape}={_rows[_shape]} drifts from SHAPE_PRESETS {_preset}"
print("ALL PASS: portable workflow skill")
