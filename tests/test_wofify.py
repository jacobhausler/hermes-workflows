"""tests/test_wofify.py — the WOFification authoring seam (est-h0huv).

Serial script (suite law: run as main, PASS/FAIL lines, exit 0 = green):
census shape and byte-stability, the loud-zero refusals (empty census, empty
shelf, zero graphs), the never-clobber rule, door-shaped validation of a
committed example graph plus a tampered twin and skipped card sidecars, and
the drift refusal on the shelf seam.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "scripts" / "wofify.py"
GOOD_GRAPH = ROOT / "examples" / "basics" / "approve-publish.json"

ok = 0
fails = []


def check(cond, msg, detail=""):
    global ok
    if cond:
        ok += 1
        print(f"PASS {msg}")
    else:
        fails.append(msg)
        print(f"FAIL {msg} {detail}")


def run_cli(*argv):
    return subprocess.run([sys.executable, str(SCRIPT), *argv],
                          capture_output=True, text=True, timeout=60)


def fixture_repo(base: Path) -> Path:
    repo = base / "repo"
    (repo / "skills" / "ship" / "playbooks").mkdir(parents=True)
    (repo / "skills" / "principle-honesty").mkdir(parents=True)
    (repo / "agents").mkdir()
    (repo / "automations").mkdir()
    (repo / "docs" / "guide").mkdir(parents=True)
    (repo / "skills" / "ship" / "SKILL.md").write_text(
        "---\nname: ship\ndescription: ship things\n---\n"
        "# Ship\n\nShip runs the release ladder end to end with named gates.\n\n"
        "## Phase 1 — prepare\nCut the branch.\n\n## Phase 2 — land\nMerge and tag.\n\n"
        "See [[review]] and skills/principle-honesty/ for the doctrine.\n")
    (repo / "skills" / "principle-honesty" / "SKILL.md").write_text(
        "# Honesty\n\nHonest numbers only; measured, never inherited from prose.\n")
    (repo / "skills" / "ship" / "playbooks" / "dry-run.md").write_text(
        "# Dry run\n\nWalk the ladder with no side effects at all.\n")
    (repo / "agents" / "critic.md").write_text(
        "# Critic\n\nAdversarial reviewer persona for the red team seat.\n")
    (repo / "automations" / "nightly.md").write_text(
        "# Nightly\n\nNightly sweep of the fleet health board.\n\n## Phase 1 — sweep\n")
    (repo / "docs" / "guide" / "intro.md").write_text(
        "# Intro\n\nGuide front door for a newcomer to the ways of working.\n")
    (repo / "plugin.json").write_text('{"name": "fixture"}\n')
    return repo


tmp = Path(tempfile.mkdtemp(prefix="wofify-test-"))
repo = fixture_repo(tmp)
pack = tmp / "pack"

r = run_cli("inventory", str(repo), "--out", str(pack))
check(r.returncode == 0, "inventory exits 0 on a real repo", r.stderr)
census = json.loads((pack / "inventory.json").read_text())
kinds = {u["path"]: u["kind"] for u in census["units"]}
check(kinds.get("skills/ship/SKILL.md") == "skill", "skill unit classified by path shape")
check(kinds.get("skills/principle-honesty/SKILL.md") == "principle", "principle kind from name prefix")
check(kinds.get("agents/critic.md") == "agent", "agent persona unit")
check(kinds.get("automations/nightly.md") == "automation", "automation unit")
check(kinds.get("docs/guide/intro.md") == "doc", "guide doc unit")
check(kinds.get("plugin.json") == "manifest", "manifest unit")
ship = next(u for u in census["units"] if u["id"] == "ship")
check(ship["phases"] == ["Phase 1 — prepare", "Phase 2 — land"], "phases captured full-heading",
      repr(ship["phases"]))
check(set(ship["calls"]) == {"review", "principle-honesty"}, "calls from wikilinks and skill refs",
      repr(ship["calls"]))
check(census["counts"] == {"agent": 1, "automation": 1, "doc": 1, "manifest": 1,
                           "playbook": 1, "principle": 1, "skill": 1},
      "counts are honest", repr(census["counts"]))

run_cli("inventory", str(repo), "--out", str(tmp / "b"))
check((tmp / "pack" / "inventory.json").read_bytes() == (tmp / "b" / "inventory.json").read_bytes(),
      "census is byte-stable (sorted walks, no clock)")

(tmp / "empty").mkdir()
r = run_cli("inventory", str(tmp / "empty"), "--out", str(tmp / "p3"))
check(r.returncode == 1 and "no units found" in r.stderr + r.stdout,
      "empty census is a loud zero")

r = run_cli("scaffold", str(pack), "--source", "https://example.invalid/repo")
check(r.returncode == 0, "scaffold exits 0 next to a census", r.stderr)
manifest = json.loads((pack / "pack.json").read_text())
check(manifest["pack"] == "pack" and manifest["units"] == [], "pack.json skeleton shape")
check((pack / "README.md").is_file(), "README stub written")
r = run_cli("scaffold", str(pack))
check(r.returncode == 1 and "refusing to overwrite" in r.stderr + r.stdout,
      "scaffold never clobbers authored state")

r = run_cli("validate", str(pack))
check(r.returncode == 1 and "refusing" in r.stderr + r.stdout, "zero graphs is never green")
pack_graph = pack / "workflows" / "ok.json"
pack_graph.write_bytes(GOOD_GRAPH.read_bytes())
(pack / "workflows" / "ok.cards.json").write_bytes(json.dumps({"cards": [{"dot": "cyan"}]}).encode())
r = run_cli("validate", str(pack))
report = json.loads(r.stdout) if r.returncode == 0 else {}
check(r.returncode == 0 and report == {"graphs": 1, "invalid": [], "valid": 1},
      "committed example graph passes the door validator (sidecar skipped)", r.stdout)
bad = json.loads(GOOD_GRAPH.read_text())
bad["nodes"][0]["after"] = "ghost-node"
(pack / "workflows" / "bad.json").write_text(json.dumps(bad))
r = run_cli("validate", str(pack))
report = json.loads(r.stdout)
check(r.returncode == 1 and report["valid"] == 1 and len(report["invalid"]) == 1
      and report["invalid"][0]["file"] == "workflows/bad.json"
      and any("after" in e for e in report["invalid"][0]["errors"]),
      "tampered graph refused with file and field named", r.stdout)
pack_graph.unlink()
(pack / "workflows" / "bad.json").unlink()

manifest["units"] = [
    {"id": "fixture-ship", "disposition": "wof", "artifact": "workflows/ok.json",
     "sha256": None},
    {"id": "principle-honesty", "disposition": "skill", "artifact": "skills/honesty.md"},
    {"id": "stale-thing", "disposition": "skip", "reason": "covered natively"},
]
(pack / "skills" / "honesty.md").write_text("# adapted doctrine body\n")
(pack / "pack.json").write_text(json.dumps(manifest))
r = run_cli("shelf", str(pack), "--skills-dir", "~/.hermes/skills")
check(r.returncode == 1 and "missing on disk" in r.stderr + r.stdout,
      "shelf refuses a unit whose artifact is missing", r.stdout)

manifest["units"][0].pop("sha256")  # no recorded hash -> accepted, drift check inert
pack_graph.write_bytes(GOOD_GRAPH.read_bytes())
(pack / "pack.json").write_text(json.dumps(manifest))
r = run_cli("shelf", str(pack), "--skills-dir", "~/.hermes/skills")
check(r.returncode == 0 and '"action": "save"' in r.stdout and '"name": "fixture-ship"' in r.stdout
      and "cp " in r.stdout and "principle-honesty/" in r.stdout
      and "stale-thing: skipped" in r.stdout,
      "shelf prints save/run/cp lines and honest skips", r.stdout)

manifest["units"] = []
(pack / "pack.json").write_text(json.dumps(manifest))
r = run_cli("shelf", str(pack))
check(r.returncode == 1 and "no units" in r.stderr + r.stdout, "empty shelf is a loud zero")

graph_bytes = GOOD_GRAPH.read_bytes()
pack_graph.write_bytes(graph_bytes)
manifest["units"] = [{"id": "fixture-ship", "disposition": "wof",
                      "artifact": "workflows/ok.json",
                      "sha256": hashlib.sha256(graph_bytes).hexdigest()}]
(pack / "pack.json").write_text(json.dumps(manifest))
r = run_cli("shelf", str(pack))
check(r.returncode == 0 and r.stdout.count("fixture-ship") >= 2, "hashed unit shelves clean")
pack_graph.write_bytes(graph_bytes + b"\n")
r = run_cli("shelf", str(pack))
check(r.returncode == 1 and "sha256 drift" in r.stderr + r.stdout
      and "fixture-ship" in r.stderr + r.stdout, "byte drift is a named refusal")

print(f"ALL PASS: wofify ({ok} checks)" if not fails else f"{len(fails)} FAILURES: {fails}")
sys.exit(1 if fails else 0)
