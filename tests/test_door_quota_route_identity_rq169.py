#!/usr/bin/env python3
"""#24 quota gate + est-699 route identity: a cost stamp marks ONE subscription.

The seat quota cache is the submit-time cost gate: an entry marks a model known
exhausted until the provider's own reset horizon. A subscription is a ROUTE, not a
name — the same model id under two providers is two subscriptions. So the cache
seam obeys the same provider-aware identity contract (route_ids_equal) the
forbidden-model gate obeys. Two laws, one per direction:

(1) false refusal: a provider-BLANK stamp (bare model key — today's shape for every
    stamp, and tomorrow's shape for seat-default deaths) never refuses a node that
    pins an explicit provider: the death that wrote it may have been a different
    subscription, and refusing a live route costs the whole submit.
(2) false admit: a qualified stamp binds its own route across provider spelling
    (Anthropic dotted id == the folded id core bills) — spelling never evades.

Plus the stamp side: a provider-pinned death stamps the QUALIFIED id, so the mark
names the subscription that died (and binds it again on re-pin).
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get("QUOTA_ID_TEST_REPO", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))
agent = types.ModuleType("agent")
agent.__path__ = []
retry = types.ModuleType("agent.retry_utils")
retry.parse_retry_after_seconds = lambda value: None
sys.modules.setdefault("agent", agent)
sys.modules.setdefault("agent.retry_utils", retry)
import wf  # noqa: E402

spec = importlib.util.spec_from_file_location("quota_identity_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)

TMP = tempfile.mkdtemp(prefix="quota-id-169.")
CACHE = Path(TMP) / "quota-cache.json"
_env_saved = os.environ.get("WF_QUOTA_CACHE")
# Test-seated: the env names our cache file, so the door runs OFFLINE (pings
# nothing) and wf._quota_note stamps land where we read them. Ping paths are
# exercised with explicit stubs after popping the seat.
os.environ["WF_QUOTA_CACHE"] = str(CACHE)

DOT, HY = "claude-model-5.1", "claude-model-5-1"


def tearDownModule():
    if _env_saved is None:
        os.environ.pop("WF_QUOTA_CACHE", None)
    else:
        os.environ["WF_QUOTA_CACHE"] = _env_saved


def seed(**entries):
    CACHE.write_text(json.dumps(entries))


def future():
    return {"resets_epoch": time.time() + 3600, "at": time.time(), "marker": "x"}


def node(model=None, provider=None, nid="lane"):
    n = {"id": nid, "type": "agent", "goal": "GO"}
    if model:
        n["model"] = model
    if provider:
        n["provider"] = provider
    return n


def refusal(nodes, routes=None, **kw):
    return door._quota_refusal({"name": "q", "nodes": nodes}, routes=routes,
                               cache_path=CACHE, **kw)


class QuotaRouteIdentity(unittest.TestCase):
    def test_bare_stamp_admits_explicit_provider_route(self):
        # The false refusal: a bare stamp (provider-blank) must not refuse a live
        # route that pins a DIFFERENT explicit provider.
        seed(**{"m-zeta": future()})
        self.assertIsNone(refusal([node("m-zeta", "openrouter")]))

    def test_bare_stamp_admits_explicit_provider_route_via_routes(self):
        seed(**{"m-zeta": future()})
        routes = {"lane": {"requested": {"provider": "openrouter", "model": "m-zeta"},
                           "resolved": {"provider": "openrouter", "model": "m-zeta"}}}
        self.assertIsNone(refusal([node("m-zeta", "openrouter")], routes=routes))

    def test_bare_stamp_still_refuses_seat_default_route(self):
        # Same subscription (seat default, provider-blank): the refusal stands.
        seed(**{"m-zeta": future()})
        res = refusal([node("m-zeta")])
        self.assertIsNotNone(res)
        self.assertIn("m-zeta", str(res))

    def test_bare_stamp_still_refuses_author_alias_pin(self):
        # An author-pinned alias inherits its provider at resolve; the author never
        # wrote a provider, so a bare stamp on the alias name still binds (the
        # test_fatal_quota_24 A1/d2 law).
        seed(**{"zeta": future()})
        routes = {"lane": {"requested": {"provider": None, "model": "zeta"},
                           "resolved": {"provider": "openai-codex", "model": "zeta-9"}}}
        res = refusal([node("zeta")], routes=routes)
        self.assertIsNotNone(res)
        self.assertIn("zeta", str(res))

    def test_qualified_stamp_binds_own_route(self):
        # #291 F3 kept: a provider-qualified stamp binds the {provider, model} node.
        seed(**{"openai/m-zeta": future()})
        res = refusal([node("m-zeta", "openai")])
        self.assertIsNotNone(res)
        self.assertIn("openai/m-zeta", str(res))

    def test_qualified_stamp_anthropic_spelling_fold_refuses(self):
        # The false admit: the dotted id is what the stamp records; core bills the
        # folded id. On Anthropic these are ONE route — spelling never evades.
        seed(**{"anthropic/" + DOT: future()})
        res = refusal([node(HY, "anthropic")])
        self.assertIsNotNone(res)

    def test_qualified_stamp_foreign_provider_admits(self):
        seed(**{"openrouter/" + DOT: future()})
        self.assertIsNone(refusal([node(HY, "anthropic")]))

    def test_qualified_stamp_other_subscription_admits(self):
        seed(**{"openai/m-zeta": future()})
        self.assertIsNone(refusal([node("m-zeta", "openrouter")]))

    def test_expired_entry_never_binds(self):
        seed(**{"m-zeta": {"resets_epoch": time.time() - 1, "at": time.time(), "marker": "x"}})
        self.assertIsNone(refusal([node("m-zeta")]))

    def test_frozen_skip_never_refuses(self):
        # A1 kept: a replay-skip node never spawns, so its mark never refuses.
        seed(**{"m-zeta": future()})
        self.assertIsNone(refusal([node("m-zeta")], skip={"lane"}))

    def test_providerless_recovery_ping_still_clears(self):
        # A5 kept: provider-less stamp recovers on an answered same-model ping —
        # the identity rework must not break the weak-law recovery.
        seed(**{"m-rec": future()})
        seat = os.environ.pop("WF_QUOTA_CACHE")
        try:
            with patch.object(door, "_ping_reachable", lambda m: True):
                self.assertIsNone(refusal([node("m-rec")]))
            self.assertNotIn("m-rec", json.loads(CACHE.read_text()))
        finally:
            os.environ["WF_QUOTA_CACHE"] = seat

    def test_explicit_provider_recovery_ping_clears(self):
        # A node with an explicit provider recovers on the STRONGER
        # alive-attribution ping — the stamp must not wedge it past the ping.
        seed(**{"openrouter/m-zeta": future()})
        seat = os.environ.pop("WF_QUOTA_CACHE")
        try:
            routes = {"lane": {"requested": {"provider": "openrouter", "model": "m-zeta"},
                               "resolved": {"provider": "openrouter", "model": "m-zeta"}}}
            with patch.object(door, "_ping_route_once", lambda p, m: {"liveness": "alive"}):
                self.assertIsNone(refusal([node("m-zeta", "openrouter")], routes=routes))
            self.assertNotIn("openrouter/m-zeta", json.loads(CACHE.read_text()))
        finally:
            os.environ["WF_QUOTA_CACHE"] = seat


class QuotaStampCarriesProvider(unittest.TestCase):
    def test_provider_pinned_death_stamps_qualified_id(self):
        CACHE.unlink(missing_ok=True)
        wf._quota_note("m-zeta", "usage limit reached, resets in ~3 hours", "openai")
        self.assertIn("openai/m-zeta", json.loads(CACHE.read_text()))

    def test_providerless_death_stays_bare(self):
        CACHE.unlink(missing_ok=True)
        wf._quota_note("m-min", "usage limit reached, resets in ~30 minutes")
        self.assertIn("m-min", json.loads(CACHE.read_text()))

    def test_qualified_model_is_not_double_prefixed(self):
        CACHE.unlink(missing_ok=True)
        wf._quota_note("vendor-a/alpha", "usage limit reached", "openrouter")
        self.assertIn("vendor-a/alpha", json.loads(CACHE.read_text()))

    def test_stamp_then_door_roundtrip(self):
        # The two seams agree: the qualified stamp refuses its own route and
        # admits the same model on a different provider.
        CACHE.unlink(missing_ok=True)
        wf._quota_note("m-zeta", "usage limit reached, resets in ~3 hours", "openai")
        self.assertIsNotNone(refusal([node("m-zeta", "openai")]))
        self.assertIsNone(refusal([node("m-zeta", "openrouter")]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
