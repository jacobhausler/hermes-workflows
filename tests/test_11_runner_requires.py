#!/usr/bin/env python3
"""Lane A preconditions: null and missing ancestor fields fail before Popen, then amend recovers."""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("runner_11_requires", ROOT / "wf.py")
assert spec and spec.loader
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    runs = root / "workflows"
    r = runs / "precondition"
    r.mkdir(parents=True)
    binary = root / "fake"
    binary.write_text("#!/usr/bin/python3\nimport os\nfrom pathlib import Path\nPath(os.environ['HERMES_HOME'],'spawns').open('a').write('x')\nprint('```json\\n{}\\n```')\n")
    binary.chmod(0o755)
    fix = {"id": "fix", "type": "echo", "output": {"pr_url": None}}
    lint = {"id": "lint", "type": "echo", "output": {"ok": True}}
    review = {"id": "review", "type": "agent", "after": ["fix", "lint"], "goal": "review",
              "requires": {"fix": ["pr_url"]}}
    (r / "graph.json").write_text(json.dumps({"nodes": [fix, lint, review]}))
    (r / "run.json").write_text(json.dumps({"hermes_bin": str(binary), "concurrency": 1}))
    with patch.dict(os.environ, {"HERMES_HOME": str(root)}, clear=False), patch.object(wf, "validate_graph", return_value=None):
        verdict = wf.main("precondition")
        rec = json.loads((r / "nodes" / "review.json").read_text())
        assert rec["status"] == "failed" and rec["error_class"] == "precondition" and rec["error"] == "precondition unmet: fix.pr_url", rec
        assert rec["output"] == {"missing": ["fix.pr_url"]} and not (root / "spawns").exists()
        assert "blocked by failed review" in verdict, verdict
        events = [json.loads(x) for x in (r / "events.jsonl").read_text().splitlines()]
        assert any(x["event"] == "node.failed" and x.get("reason") == "precondition" for x in events)
        # Change the upstream definition: fingerprint replay invalidates the failed record.
        fix["output"]["pr_url"] = "https://example.test/pr"
        (r / "graph.json").write_text(json.dumps({"nodes": [fix, lint, review]}))
        os.close(wf._LOCK_FD)
        wf._LOCK_FD = None
        wf.main("precondition")
        rec = json.loads((r / "nodes" / "review.json").read_text())
        assert rec["status"] == "done" and (root / "spawns").read_text() == "x", rec
print("PASS Lane A precondition failure and amended replay")
