"""P01: factual notifications and optional execution presentation."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
HOME = tempfile.TemporaryDirectory(prefix="p01-home-", dir=ROOT)
os.environ["HERMES_HOME"] = HOME.name
os.environ["WF_RUNS_ROOT"] = str(Path(HOME.name) / "workflows")
import wf
spec = importlib.util.spec_from_file_location("p01_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)


from unittest.mock import patch

class Experience(unittest.TestCase):
    def test_static_validate_and_launch_preview_have_distinct_probe_contracts(self):
        graph = {"nodes": [{"id": "e", "type": "echo", "output": "ok"}]}
        with patch.object(door, "_route_liveness_ping", return_value=[]) as ping, patch.object(door, "_quota_refusal", return_value=None), patch.object(door, "_spawn_runner") as spawn:
            self.assertTrue(door.act_validate({"graph": graph})["ok"])
            ping.assert_not_called()
            self.assertTrue(door.act_run({"graph": graph, "dry_run": True})["ok"])
            ping.assert_called_once()
            spawn.assert_not_called()

    def test_one_off_launch_is_usable_without_rendered_card(self):
        graph = {"name": "one-off", "nodes": [{"id": "e", "type": "echo", "output": "ok"}]}
        with patch.object(door, "_spawn_runner") as spawn:
            result = door.act_run({"graph": graph})
        self.assertNotIn("error", result)
        spawn.assert_called_once()
        self.assertIn("run_id", result)
        self.assertNotIn("PASTE", result["hint"])
        self.assertIn("optional", result["lifecycle_notice"])
        self.assertIn("wait", result["hint"])

    def test_registration_exposes_one_exact_id_without_launch(self):
        class Registry:
            def __init__(self):
                self.tools = {}
            def get_config(self, *args):
                return None
            def register_tool(self, **kwargs):
                self.tools[kwargs["name"]] = kwargs
            def register_skill(self, *args, **kwargs):
                pass
            def register_hook(self, *args, **kwargs):
                pass
            def register_command(self, *args, **kwargs):
                pass
        registry = Registry()
        with patch.object(door, "model_tiers", return_value={}), patch.object(door, "_spawn_runner") as spawn:
            door.register(registry)
            self.assertEqual(list(registry.tools), ["workflow"])
            self.assertEqual(registry.tools["workflow"]["toolset"], "workflows")
            self.assertIs(registry.tools["workflow"]["handler"], door.handle)
            spawn.assert_not_called()
        door._CTX = None

    def test_recipe_guidance_does_not_require_execution_curation_or_card(self):
        graph = {"name": "optional", "nodes": [{"id": "echo", "type": "echo", "output": "ok"}]}
        saved = door.act_save({"graph": graph, "name": "optional", "description": "recipe"})
        self.assertNotIn("error", saved)
        listing = door.act_library({})
        self.assertTrue(listing["library"])
        self.assertNotIn("why_not_library", listing["hint"])
        command = door._wf_command("optional")
        self.assertIn('from:"optional"', command)
        self.assertNotIn("emit", command)
        self.assertNotIn("Call `library` first", door.WORKFLOW_PARAMS["properties"]["tags"]["description"])

    def test_release_never_promises_push_delivery(self):
        r = Path(HOME.name) / "workflows" / "held"
        r.mkdir(parents=True, exist_ok=True)
        graph = {"nodes": [{"id": "approve", "type": "gate", "question": "yes?", "options": ["yes", "no"]}]}
        (r / "graph.json").write_text(json.dumps(graph))
        with patch.object(door, "_resume_after_action", return_value="live"):
            result = door.act_release({"run_id": "held", "gate_id": "approve", "answer": "yes"})
        self.assertTrue(result["ok"])
        self.assertIn("optional", result["hint"])
        self.assertIn("wait", result["hint"])
        self.assertNotIn("automatically", result["hint"])

    def test_unknown_recipe_keeps_detail_without_curation(self):
        out = door._from_unknown_error("missing-recipe")
        self.assertEqual(out.get("error_class"), "library_not_found")
        self.assertIn("missing-recipe", out["error"])
        self.assertNotIn("why_not_library", out["error"])
        self.assertIn("run", out["hint"])

    def test_invalid_graph_has_typed_original_defects(self):
        out = door._validation_error({"nodes": []})
        self.assertEqual(out.get("error_class"), "graph_invalid")
        self.assertTrue(out["errors"])
        self.assertIn(out["errors"][0]["msg"], out["error"])

    def test_wakes_are_facts_not_new_authority(self):
        for event in ("run.done", "run.failed", "gate.held"):
            text = wf._wake_owner_text("research-only", event)
            self.assertIn('event=' + json.dumps(event), text)
            self.assertIn("does not authorize", text)
            for mandate in ("must land", "must be dispatched", "apply ONE", "wakes this session", "FAILED run", "PRs"):
                self.assertNotIn(mandate, text)
        self.assertIsNone(wf._wake_owner_text("research-only", "unknown"))


if __name__ == "__main__":
    unittest.main()
