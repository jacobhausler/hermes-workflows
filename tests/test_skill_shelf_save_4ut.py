"""SKILL.md shelf-save law: the save source changes the shelved bytes, and the
runner verdict's fingerprint lives in runner_exit.json — all three facts must be
in the skill doc, inside the line budget (SKILL.md stays <110 lines)."""
from pathlib import Path

skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")

# 1. save-from-run_id shelves the run's BAKED graph.json (defaults/shape budgets
#    concrete), so its source_digest never matches the author file; a file-sourced
#    save (graph/graph_path) shelves author bytes and keeps the two equal.
assert "`source_digest`" in skill, "SKILL.md must name source_digest on the save law"
assert "budgets included" in skill, "source_digest hashes the canonical nodes, budgets included"
assert "baked `graph.json`" in skill, "save(run_id) shelves the door-baked graph.json"
assert "source: null" in skill, "save-from-run_id leaves provenance source null unless passed"
# 2. The runner verdict is graph-bound and the binding rides runner_exit.json.
assert "graph_fingerprint" in skill and "runner_exit.json" in skill, \
    "the graph-bound verdict fingerprint lives in runner_exit.json, not run.json"
# 3. Doc law is budget-neutral: the line budget the suite freezes still holds.
assert len(skill.splitlines()) < 110, len(skill.splitlines())
print("ALL PASS: shelf save semantics documented within budget")
