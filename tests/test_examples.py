#!/usr/bin/env python3
"""examples/: the two shape graphs must pass the real door, not a mirror of it.

Data shapes under test (the deliverables, named before the logic):
  - examples/review/council-shape.workflow.json — docket echo -> blind review
    fan-out -> adjudicate barrier -> report; graph dict {grammar, name,
    description, provenance, nodes[]}.
  - examples/build/crew-shape.workflow.json — orders echo -> crew fan-out ->
    re-run verify -> closeout; same dict shape.
  - examples/README.md — first screen is exactly the three TTFW steps
    (write goal -> workflows start -> workflows status <run_id>).

Behavior, not internals: the door is invoked through its own CLI and its own
API (the same pipeline the `workflow` tool walks), the shipped bytes pass the
publish scrub audit, and the README's opening screen carries exactly three
numbered steps naming the two commands. Run directly (suite.py law) or under
pytest; exit 0 = green either way.
"""
import importlib.util as _ilu
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

COUNCIL = ROOT / "examples" / "review" / "council-shape.workflow.json"
CREW = ROOT / "examples" / "build" / "crew-shape.workflow.json"
README = ROOT / "examples" / "README.md"

# Import the publish scrub's OWN merged pattern (built-in + scripts/scrub-list.txt)
# so estate vocab or a vendor model name smuggled into an example fails HERE, at
# the change that introduced it — same law as test_example_census_fanout.py.
_mp_spec = _ilu.spec_from_file_location("make_public", ROOT / "scripts" / "make_public.py")
assert _mp_spec and _mp_spec.loader, "scripts/make_public.py must exist"
_make_public = _ilu.module_from_spec(_mp_spec)
_mp_spec.loader.exec_module(_make_public)
SCRUB = _make_public.load_scrub_list(ROOT)


def _door_cli(graph_path):
    """The real door CLI: rc 0 and a VALID ok line, or the printed verdict."""
    r = subprocess.run([sys.executable, str(ROOT / "wf.py"), "validate", str(graph_path)],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, f"door CLI refused {graph_path.name} (rc={r.returncode}):\n{r.stdout}{r.stderr}"
    assert "VALID ok" in r.stdout, f"door CLI printed no VALID ok for {graph_path.name}:\n{r.stdout}"
    return r.stdout


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _readme_first_screen():
    """Text from the H1 down to the first '##' section — what a reader sees first."""
    text = README.read_text(encoding="utf-8")
    head = text.split("\n## ", 1)[0]
    return head


def test_council_shape_passes_the_door():
    assert _door_cli(COUNCIL)
    assert wfcommon.validate_graph_full(_load(COUNCIL)) == []


def test_crew_shape_passes_the_door():
    assert _door_cli(CREW)
    assert wfcommon.validate_graph_full(_load(CREW)) == []


def test_shipped_bytes_pass_the_scrub_audit():
    """The two shipped graphs are the new bytes; the README's map rows predate
    this PR and ride the publish audit's guard list (bead-to-prod etc.)."""
    for path in (COUNCIL, CREW):
        assert SCRUB.search(path.read_text(encoding="utf-8")) is None, \
            f"{path.name} carries a scrub hit (estate vocab or a vendor model name)"


def test_no_seat_pins_a_model():
    """Route rides the seat default / capability classes, never a vendor id."""
    for path in (COUNCIL, CREW):
        g = _load(path)
        assert "model" not in g.get("defaults", {})
        for n in g["nodes"]:
            assert "model" not in n, f"{path.name}: node {n.get('id')} pins a model"


def test_readme_first_screen_is_exactly_three_steps():
    head = _readme_first_screen()
    steps = re.findall(r"(?m)^[123]\. ", head)
    numbered_any = re.findall(r"(?m)^\d+\. ", head)
    assert len(numbered_any) == 3 and steps == ["1. ", "2. ", "3. "], \
        f"first screen carries {len(numbered_any)} numbered steps, expected exactly 3"
    assert re.search(r"write the goal", head, re.I), "step 1 must be: write the goal"
    assert "workflows start" in head, "step 2 must name: workflows start"
    assert "workflows status <run_id>" in head, "step 3 must name: workflows status <run_id>"


def test_shapes_are_on_the_map():
    text = README.read_text(encoding="utf-8")
    for row in ("council-shape.workflow.json", "crew-shape.workflow.json"):
        assert row in text, f"README map is missing the {row} row"


if __name__ == "__main__":
    ok = True
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                ok = False
                print(f"FAIL {name} :: {e}")
    print("ALL PASS (6 example-shape contracts)" if ok else "FAILURES PRESENT")
    sys.exit(0 if ok else 1)
