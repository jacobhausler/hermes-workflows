#!/usr/bin/env python3
"""Regression: launch a run in the tool's session, deliver one parser-valid card."""
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
spec = importlib.util.spec_from_file_location("workflow_card_backend", ROOT / "__init__.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)
# Load the host's real stdlib-only ContextVars module without importing the
# unrelated gateway configuration/dependency stack (minimal macOS test Python).
gateway_spec = importlib.util.find_spec('gateway')
if gateway_spec is None or not gateway_spec.origin:
    raise RuntimeError('Tests require the Hermes source checkout on PYTHONPATH')
context_spec = importlib.util.spec_from_file_location('gateway.session_context',
    Path(gateway_spec.origin).with_name('session_context.py'))
assert context_spec is not None and context_spec.loader is not None
context = importlib.util.module_from_spec(context_spec)
sys.modules['gateway.session_context'] = context
context_spec.loader.exec_module(context)
set_session_vars, clear_session_vars = context.set_session_vars, context.clear_session_vars

# Desktop transcript-directives.ts SHA256 48cdf5a1083c0c6b9b2c815719942b6071c1e6291d697c55e2f2814e714aa9da
# The real parser extracts `key="value"` from braces; bare run ids yield attrs={}
# and desktop/plugin.js:1059 consumes attrs.id. This regex is NOT a substitute
# for the frontend lane's actual TypeScript parser test.
CARD = re.compile(r'^::workflow\{id="([A-Za-z0-9._-]+)"\}$')
GRAPH = {"name": "card-backend", "nodes": [{"id": "one", "type": "agent", "goal": "offline"}]}


class CardBackend(unittest.TestCase):
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
        return set_session_vars(platform="desktop", source="desktop", session_id=sid, ui_session_id="tab-" + sid)

    def launch(self):
        return json.loads(wf.handle({"action": "run", "graph": json.loads(json.dumps(GRAPH)), "hermes_bin": "offline"}))

    def test_tool_context_is_owner_and_wrong_hook_session_cannot_consume(self):
        tokens = self.bind("session-a")
        try:
            out = self.launch()
            rid = out["run_id"]
            meta = json.loads((Path(self.home.name) / "workflows" / rid / "run.json").read_text())
            self.assertEqual(meta["owner"]["session_id"], "session-a")
            self.assertEqual(meta["owner"]["ui_session_id"], "tab-session-a")
            self.assertEqual(out["card"], f'::workflow{{id="{rid}"}}')
            self.assertIsNone(wf._auto_card(response_text="not yours", session_id="session-b"))
            result = wf._auto_card(response_text="done", session_id="session-a")
            self.assertEqual(CARD.fullmatch(result.strip().splitlines()[-1]).group(1), rid)
            self.assertEqual(result.count('::workflow{id='), 1)
            self.assertIsNone(wf._auto_card(response_text="later", session_id="session-a"))
        finally:
            clear_session_vars(tokens)

    def test_two_launches_manual_card_and_invalid_bare_text(self):
        tokens = self.bind("session-a")
        try:
            a, b = self.launch(), self.launch()
            manually_emitted = a["card"]
            result = wf._auto_card(response_text="progress\n\n" + manually_emitted, session_id="session-a")
            self.assertNotIn(b["run_id"], manually_emitted)
            self.assertEqual(result.count(manually_emitted), 1)
            self.assertEqual(result.count(b["card"]), 1)
            self.assertEqual([CARD.fullmatch(x).group(1) for x in result.splitlines() if CARD.fullmatch(x)],
                             [a["run_id"], b["run_id"]])
            c = self.launch()
            bare = f"::workflow{{{c['run_id']}}}"
            result = wf._auto_card(response_text=bare, session_id="session-a")
            self.assertEqual(result.count(c["card"]), 1, result)
        finally:
            clear_session_vars(tokens)

    def test_inline_manual_card_is_not_duplicated(self):
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            response = "Started " + a["card"] + " now"
            self.assertIsNone(wf._auto_card(response_text=response, session_id="session-a"))
        finally:
            clear_session_vars(tokens)

    def test_blank_final_and_fenced_mention_still_emit(self):
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            self.assertEqual(wf._auto_card(response_text="", session_id="session-a"), a["card"] + "\n")
            b = self.launch()
            result = wf._auto_card(response_text="```text\n" + b["card"] + "\n```", session_id="session-a")
            self.assertEqual(result.count(b["card"]), 2, result)  # fenced mention not a rendered card
        finally:
            clear_session_vars(tokens)

    def test_registration_wires_transform_and_end_cleanup(self):
        class Context:
            hooks = {}
            def register_hook(self, name, fn): self.hooks[name] = fn
            def register_tool(self, **_): pass
            def register_command(self, *_, **__): pass
            def register_skill(self, name, path, **_):
                assert name == 'workflow' and path.is_file()
            def get_config(self, _, default): return default
        ctx = Context()
        wf.register(ctx)
        self.assertIn("transform_llm_output", ctx.hooks)
        self.assertIn("on_session_end", ctx.hooks)
        tokens = self.bind("session-a")
        try:
            a = self.launch()
            ctx.hooks["on_session_end"](session_id="session-b", interrupted=True)
            self.assertEqual(ctx.hooks["transform_llm_output"](response_text="x", session_id="session-a").count(a["card"]), 1)
            held = self.launch()
            ctx.hooks["on_session_end"](session_id="session-a", interrupted=True)
            replay = ctx.hooks["transform_llm_output"](response_text="next turn", session_id="session-a")
            self.assertEqual(replay.count(held["card"]), 1)
            self.assertIsNone(ctx.hooks["transform_llm_output"](response_text="again", session_id="session-a"))
        finally:
            clear_session_vars(tokens)


if __name__ == "__main__":
    unittest.main(verbosity=2)
