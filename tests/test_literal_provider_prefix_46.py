#!/usr/bin/env python3
"""est-2ek.1.46: a literal node.model 'provider/model' with no node.provider reached the
child as a bare `-m provider/model` (no --provider), so the child spoke to the seat's
DEFAULT route with the prefixed id and died HTTP 400, while the alias for the same model
worked (aliases bake their provider at submit). The door now bakes the provider for a
literal whose prefix is a provider the seat itself routes through (the 'provider/' prefix
of a seat alias or tier target, or a configured `providers:` key).

Pinned here:
  (1) alias 'sol' and the literal 'openai-codex/gpt-6-sol' resolve to the SAME route
      (provider openai-codex, model gpt-6-sol / alias target) in routes.resolved;
  (2) the author's request is preserved in routes.requested (provider None, literal model);
  (3) a vendor-namespaced id whose prefix the seat does not route through is left
      alone (an aggregator route's 'vendor/model' is not a provider claim);
  (4) an explicit node.provider is never overridden; re-resolving a baked node is a no-op.

Run (stdlib only): python3 tests/test_literal_provider_prefix_46.py
"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_46", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)

SEAT = {"default": "seat-default", "aliases": {"sol": "openai-codex/gpt-6-sol"}}


def node(nid, **kw):
    return {"id": nid, "type": "agent", "goal": "route", **kw}


class LiteralProviderPrefix46(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="wf46-")
        self.addCleanup(tmp.cleanup)
        env = patch.dict(os.environ, {"HERMES_HOME": tmp.name})
        env.start()
        self.addCleanup(env.stop)
        for target, value in (("_seat_model_cfg", lambda: SEAT), ("model_tiers", lambda: {})):
            p = patch.object(door, target, value)
            p.start()
            self.addCleanup(p.stop)

    def resolve(self, *nodes):
        err, _table, routes = door._resolve_models(list(nodes))
        self.assertIsNone(err, err)
        return routes

    def test_alias_and_literal_resolve_to_the_same_route(self):
        alias, literal = node("alias", model="sol"), node("literal", model="openai-codex/gpt-6-sol")
        routes = self.resolve(alias, literal)
        self.assertEqual(routes["alias"]["resolved"]["provider"], "openai-codex")
        self.assertEqual(routes["literal"]["resolved"],
                         {"provider": "openai-codex", "model": "gpt-6-sol"})
        self.assertEqual(literal["provider"], "openai-codex")
        self.assertEqual(literal["model"], SEAT["aliases"]["sol"].partition("/")[2])

    def test_request_is_preserved_in_routes(self):
        routes = self.resolve(node("literal", model="openai-codex/gpt-6-sol"))
        self.assertEqual(routes["literal"]["requested"],
                         {"provider": None, "model": "openai-codex/gpt-6-sol"})

    def test_literal_equal_to_a_tier_target_still_bakes(self):
        # the seat-owned name set (tier targets) is where the literal usually lives
        with patch.object(door, "model_tiers", lambda: {"sol-tier": "openai-codex/gpt-6-sol"}):
            n = node("literal", model="openai-codex/gpt-6-sol")
            routes = self.resolve(n)
        self.assertEqual(routes["literal"]["resolved"],
                         {"provider": "openai-codex", "model": "gpt-6-sol"})

    def test_unrouted_vendor_prefix_is_left_literal(self):
        n = node("vendor", model="vendor-a/alpha")
        routes = self.resolve(n)
        self.assertNotIn("provider", n)
        self.assertEqual(n["model"], "vendor-a/alpha")
        self.assertEqual(routes["vendor"]["resolved"], {"provider": None, "model": "vendor-a/alpha"})

    def test_explicit_provider_wins_and_rebake_is_a_noop(self):
        explicit = node("explicit", provider="other-prov", model="openai-codex/gpt-6-sol")
        self.resolve(explicit)
        self.assertEqual(explicit["provider"], "other-prov")
        literal = node("literal", model="openai-codex/gpt-6-sol")
        self.resolve(literal)
        baked = dict(literal)
        self.resolve(literal)
        self.assertEqual(literal, baked)


if __name__ == "__main__":
    unittest.main()
