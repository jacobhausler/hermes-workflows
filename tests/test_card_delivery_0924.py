#!/usr/bin/env python3
"""Regression: a launch whose turn ends blank/interrupted replays its card
exactly once at the session's next transform, and never past the hold bound.
Item: automatic workflow-card delivery lost on blank/interrupted final turns.
"""
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/opt/hermes")
spec = importlib.util.spec_from_file_location("workflow_card_delivery", ROOT / "__init__.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)
gateway_spec = importlib.util.find_spec('gateway')
if gateway_spec is None or not gateway_spec.origin:
    raise RuntimeError('Tests require the Hermes source checkout on PYTHONPATH')
if 'gateway.session_context' not in sys.modules:
    # Standalone run: load the host's real stdlib-only ContextVars module without
    # importing the unrelated gateway configuration/dependency stack. When another
    # test file already registered it, reuse that exact module object so every
    # party (this file, the sibling tests, and wf._session_env) shares one
    # ContextVar; bind()/teardown resolve it via sys.modules at call time.
    context_spec = importlib.util.spec_from_file_location('gateway.session_context',
        Path(gateway_spec.origin).with_name('session_context.py'))
    assert context_spec is not None and context_spec.loader is not None
    context = importlib.util.module_from_spec(context_spec)
    sys.modules['gateway.session_context'] = context
    context_spec.loader.exec_module(context)

CARD = re.compile(r'^::workflow\{id="([A-Za-z0-9._-]+)"\}$')
GRAPH = {"name": "card-delivery", "nodes": [{"id": "one", "type": "agent", "goal": "offline"}]}


def clear_session_vars(tokens):
    # Resolve at call time: shares the ContextVar the sibling test file registered.
    sys.modules['gateway.session_context'].clear_session_vars(tokens)


class CardDelivery(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory(dir=ROOT)
        self.env = patch.dict(os.environ, {"HERMES_HOME": self.home.name, "HERMES_SESSION_ID": "stale-process"})
        self.env.start()
        self.spawn = patch.object(wf, "_spawn_runner")
        self.spawn.start()
        with wf._LAUNCH_LOCK:
            wf._LAUNCHED.clear()
            wf._HELD.clear()

    def tearDown(self):
        self.spawn.stop()
        self.env.stop()
        self.home.cleanup()

    def bind(self, sid):
        ctx = sys.modules['gateway.session_context']
        return ctx.set_session_vars(platform="desktop", source="desktop", session_id=sid, ui_session_id="tab-" + sid)

    def launch(self):
        return json.loads(wf.handle({"action": "run", "graph": json.loads(json.dumps(GRAPH)), "hermes_bin": "offline"}))

    def test_interrupted_turn_replays_card_once_on_next_transform(self):
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            # The interrupted turn never transforms; it only fires session-end.
            wf._clear_launch(session_id="session-a", interrupted=True)
            with wf._LAUNCH_LOCK:
                self.assertIn("session-a", wf._HELD)  # held, not dropped
            first = wf._auto_card(response_text="retry answer", session_id="session-a")
            self.assertEqual(first.count(a["card"]), 1, first)
            self.assertEqual(CARD.fullmatch(first.strip().splitlines()[-1]).group(1), a["run_id"])
            # Exactly once: the replay consumed the held entry.
            self.assertIsNone(wf._auto_card(response_text="later turn", session_id="session-a"))
        finally:
            clear_session_vars(tokens)

    def test_two_interrupted_launches_replay_in_order_deduped(self):
        tokens = self.bind("session-a")
        try:
            a, b = self.launch(), self.launch()
            manual = self.launch()
            wf._clear_launch(session_id="session-a", interrupted=True)
            # Held manual run carded by the text must be deduped, not doubled:
            # its own line leads, then the appended missing cards in launch order.
            text = "progress\n\n" + manual["card"]
            result = wf._auto_card(response_text=text, session_id="session-a")
            self.assertEqual([CARD.fullmatch(x).group(1) for x in result.splitlines() if CARD.fullmatch(x)],
                             [manual["run_id"], a["run_id"], b["run_id"]])
            self.assertEqual(result.count(manual["card"]), 1)
            self.assertIsNone(wf._auto_card(response_text="next", session_id="session-a"))
        finally:
            clear_session_vars(tokens)

    def test_expired_hold_is_dropped_not_replayed(self):
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            wf._clear_launch(session_id="session-a", interrupted=True)
            with wf._LAUNCH_LOCK:
                ts, rid = wf._HELD["session-a"][0]
                wf._HELD["session-a"][0] = (ts - wf._HELD_TTL_SECONDS - 1, rid)  # backdate deterministically
            self.assertIsNone(wf._auto_card(response_text="much later turn", session_id="session-a"))
            with wf._LAUNCH_LOCK:
                self.assertNotIn("session-a", wf._HELD)  # consumed by the drop, cannot leak later
        finally:
            clear_session_vars(tokens)

    def test_hold_never_crosses_sessions(self):
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            wf._clear_launch(session_id="session-a", interrupted=True)
            self.assertIsNone(wf._auto_card(response_text="other session", session_id="session-b"))
            result = wf._auto_card(response_text="right session", session_id="session-a")
            self.assertEqual(result.count(a["card"]), 1, result)
        finally:
            clear_session_vars(tokens)

    def test_fresh_relaunch_after_hold_survives_another_session_end(self):
        # A held run and a same-session relaunch both ride out a second
        # interrupted turn, each delivered exactly once.
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            wf._clear_launch(session_id="session-a", interrupted=True)
            b = self.launch()
            wf._clear_launch(session_id="session-a", interrupted=True)
            result = wf._auto_card(response_text="finally", session_id="session-a")
            self.assertEqual([CARD.fullmatch(x).group(1) for x in result.splitlines() if CARD.fullmatch(x)],
                             [a["run_id"], b["run_id"]])
            self.assertIsNone(wf._auto_card(response_text="done", session_id="session-a"))
        finally:
            clear_session_vars(tokens)


if __name__ == "__main__":
    unittest.main(verbosity=2)
