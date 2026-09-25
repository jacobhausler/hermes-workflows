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
assert '::workflow{id="<run_id>"}' in skill
assert "graph_path" in skill and "proposed" not in skill.lower()
assert "interrupted" in skill
assert "seat default" in skill.lower() and "not" in skill.lower()
assert all((root / "references" / f).is_file() for f in ("grammar.md", "operations.md", "development.md"))
assert "agent.when" in (root / "references/grammar.md").read_text()
assert "workflow 0.9.0" in (root / "references/grammar.md").read_text().lower()
print("ALL PASS: portable workflow skill")
