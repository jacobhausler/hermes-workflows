#!/usr/bin/env python3
"""Policy bans share route identity at submit and served-seat admission; offline."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get("POLICY_TEST_REPO", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))
agent = types.ModuleType("agent")
agent.__path__ = []
retry = types.ModuleType("agent.retry_utils")
retry.parse_retry_after_seconds = lambda value: None
sys.modules.setdefault("agent", agent)
sys.modules.setdefault("agent.retry_utils", retry)
import wf
spec = importlib.util.spec_from_file_location("policy_identity_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)

DOT, HY = "claude-model-5.1", "claude-model-5-1"


class PolicyRouteIdentity(unittest.TestCase):
    def submit(self, model, ban, provider=None, *, floor=False, alias=None, tier=None):
        seat = {"default": None, "aliases": {"judge": alias} if alias else {},
                "workflows_forbidden_models": [ban] if floor else []}
        node = {"id": "worker", "type": "agent", "model": model}
        if provider:
            node["provider"] = provider
        if tier:
            node["tier"] = tier
        graph = {"nodes": [node], "model_policy": {"forbidden_models": [] if floor else [ban]}}
        with patch.object(door, "_seat_model_cfg", return_value=seat), \
                patch.object(door, "model_tiers", return_value={}):
            return door._model_policy_error(graph)

    def served(self, model, ban, provider=None, *, floor=False, node=None, metric=True):
        with tempfile.TemporaryDirectory(prefix="policy-route-") as td:
            run = Path(td)
            (run / "graph.json").write_text(json.dumps({"model_policy": {
                "forbidden_models": [] if floor else [ban]}}))
            rows = {"key": {"model": model, "billing_provider": provider}} if metric else {}
            with patch.object(wf, "child_metrics", return_value=rows), \
                    patch.object(wf, "seat_forbidden_models", return_value=[ban] if floor else []):
                return wf._stamp_served({"_run": run}, {"status": "done", "skey": "key"}, node)

    def test_submit_dotted_ban_cannot_be_dodged(self):
        for floor in (False, True):
            for banned, requested in ((DOT, HY), (HY, DOT), ("anthropic/" + DOT, HY)):
                with self.subTest(floor=floor, banned=banned, requested=requested):
                    self.assertIsNotNone(self.submit(requested, banned, "anthropic", floor=floor))

    def test_submit_alias_and_baked_tier_use_resolved_provider(self):
        for floor in (False, True):
            for model, tier in (("judge", None), (HY, "judge")):
                with self.subTest(floor=floor, model=model):
                    self.assertIsNotNone(self.submit(model, DOT, floor=floor,
                                                    alias="anthropic/" + HY, tier=tier))

    def test_submit_provider_boundaries_and_override(self):
        for provider in ("openai-codex", "openrouter", None):
            self.assertIsNone(self.submit(HY, DOT, provider))
        self.assertIsNone(self.submit("judge", DOT, "openrouter", alias="anthropic/" + HY))
        self.assertIsNone(self.submit("vendor-b/alpha", "vendor-a/alpha", "openrouter"))
        self.assertIsNone(self.submit(HY, "foreign/" + DOT, "anthropic"))
        self.assertIsNone(self.submit(HY + "(extra)", DOT, "anthropic"))

    def test_submit_existing_exact_and_tail_bans_survive(self):
        for requested, banned in ((HY, HY), ("anthropic/" + HY, HY), (HY, "anthropic/" + HY)):
            self.assertIsNotNone(self.submit(requested, banned, "anthropic"))
        self.assertIsNotNone(self.submit("judge", "judge", alias="anthropic/" + HY))

    def test_served_dotted_ban_cannot_be_dodged(self):
        for floor in (False, True):
            for banned, model in ((DOT, HY), (HY, DOT), ("anthropic/" + DOT, HY)):
                with self.subTest(floor=floor, banned=banned, model=model):
                    result = self.served(model, banned, "anthropic", floor=floor)
                    self.assertEqual(result.get("error_class"), "forbidden_model", result)
                    self.assertEqual(result["served_model"], model)
                    self.assertEqual(result["served_billing_provider"], "anthropic")

    def test_served_uses_actual_provider_not_requested_pin(self):
        self.assertEqual(self.served(HY, DOT, "anthropic", node={"provider": "openrouter"})
                         .get("error_class"), "forbidden_model")
        self.assertEqual(self.served(HY, DOT, "openrouter", node={"provider": "anthropic"})
                         ["status"], "done")

    def test_served_provider_boundaries_and_absence(self):
        for provider in ("openai-codex", "openrouter", None):
            self.assertEqual(self.served(HY, DOT, provider)["status"], "done")
        for model, banned, provider in (("vendor-b/alpha", "vendor-a/alpha", "openrouter"),
                                       (HY, "foreign/" + DOT, "anthropic"),
                                       (HY + "(extra)", DOT, "anthropic")):
            self.assertEqual(self.served(model, banned, provider)["status"], "done")
        self.assertEqual(self.served(None, DOT, "anthropic")["status"], "done")
        self.assertEqual(self.served(HY, DOT, "anthropic", metric=False)["status"], "done")

    def test_served_existing_exact_and_tail_bans_survive(self):
        for model, banned in ((HY, HY), ("foreign/" + HY, HY)):
            self.assertEqual(self.served(model, banned).get("error_class"), "forbidden_model")


if __name__ == "__main__":
    unittest.main(verbosity=2)
