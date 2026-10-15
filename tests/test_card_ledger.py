#!/usr/bin/env python3
"""Hook-led card ledger: the per-turn runs-root scan is gone, hooks keep a pending ledger.

Contract (all legs call the registered callbacks directly; no source reads):
  * card_ledger: add -> file shape {session: {run: {state, ts, name}}} -> drop -> gone;
    a corrupt file reads as {} (never raises);
  * post_tool_call: a `workflow` run result adds the run; held updates state; a terminal
    status / stop drops it; any other tool touches nothing;
  * pre_llm_call: a {"context"} block naming the run id ONLY when something is pending;
  * transform_llm_output (the shipper) reads the ledger, appends cards, drops on selection;
  * fail-open: an unwritable ledger (a directory) makes every callback return None;
  * the scan entrypoints are gone by name (API shape, not grep).
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))


def _load_door():
    spec = importlib.util.spec_from_file_location("hw_card_ledger", ROOT / "__init__.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Ctx:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, name, fn):
        self.hooks[name] = fn

    def register_tool(self, **_):
        pass

    def register_command(self, *_, **__):
        pass

    def register_skill(self, *_, **__):
        pass

    def get_config(self, key, default):
        return default


def _run_result(rid, **extra):
    return json.dumps({"run_id": rid, **extra})


class CardLedger(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory(dir=ROOT / "tests")
        self.env = mock.patch.dict(os.environ, {
            "HERMES_HOME": self.home.name,
            "WF_RUNS_ROOT": str(Path(self.home.name) / "workflows"),
            "HERMES_WF_HERMES_BIN": "offline",
        })
        self.env.start()
        os.environ.pop("HERMES_SESSION_ID", None)
        self.hw = _load_door()
        import wf_test_isolation
        wf_test_isolation.install(self.hw)
        self.ctx = _Ctx()
        self.hw.register(self.ctx)
        self.post = self.ctx.hooks["post_tool_call"]
        self.pre = self.ctx.hooks["pre_llm_call"]
        self.ship = self.ctx.hooks["transform_llm_output"]
        self.led = self.hw._card_ledger
        self.runs = Path(os.environ["WF_RUNS_ROOT"])
        self.runs.mkdir(parents=True, exist_ok=True)
        self.file = self.runs / "card-ledger.json"

    def tearDown(self):
        self.env.stop()
        self.home.cleanup()

    def launch(self, rid, sid="S", name="g"):
        return self.post(tool_name="workflow", args={"action": "run", "graph": {"name": name}},
                         result=_run_result(rid), session_id=sid)

    def owed(self, sid="S"):
        return [r for r, _ in self.led.entries(sid)]

    def fire(self, text="All done.", sid="S", turn="t1", platform="desktop"):
        return self.ship(response_text=text, session_id=sid, turn_id=turn,
                         platform=platform, model="m")

    @staticmethod
    def select(result):
        return result if isinstance(result, str) and result else None

    @staticmethod
    def card(rid):
        return f'::workflow{{id="{rid}"}}'

    # ---- ledger round trip ----------------------------------------------------
    def test_roundtrip_file_shape_and_drop(self):
        self.assertTrue(self.led.add("S", "r1", "nm"))
        shape = json.loads(self.file.read_text())
        self.assertEqual(list(shape), ["S"])
        ent = shape["S"]["r1"]
        self.assertEqual((ent["state"], ent["name"]), ("pending", "nm"))
        self.assertTrue(ent["ts"])
        self.assertTrue(self.led.drop("S", "r1"))
        self.assertEqual(json.loads(self.file.read_text()), {})
        self.assertEqual(self.owed(), [])

    def test_corrupt_file_is_empty_never_raises(self):
        self.file.write_text("{not json at all")
        self.assertEqual(self.led.entries("S"), [])
        self.assertTrue(self.led.add("S", "r2", "n"))          # next write heals it
        self.assertEqual(self.owed(), ["r2"])
        self.file.write_text(json.dumps({"S": ["wrong", "shape"]}))
        self.assertEqual(self.led.entries("S"), [])

    def test_persists_across_a_process_restart(self):
        self.launch("r-keep")
        fresh = _load_door()                                  # a restarted gateway
        import wf_test_isolation
        wf_test_isolation.install(fresh)
        self.assertEqual([r for r, _ in fresh._card_ledger.entries("S")], ["r-keep"])

    # ---- post_tool_call -------------------------------------------------------
    def test_post_run_adds_and_terminal_drops(self):
        self.assertIsNone(self.launch("r-a"))
        self.assertEqual(self.owed(), ["r-a"])
        self.post(tool_name="workflow", args={"action": "wait", "run_id": "r-a"},
                  result=_run_result("r-a", status="running"), session_id="S")
        self.assertEqual(self.owed(), ["r-a"])
        for status in ("done", "failed", "stopped"):
            self.launch("r-a")
            self.post(tool_name="workflow", args={"action": "status", "run_id": "r-a"},
                      result=_run_result("r-a", status=status), session_id="S")
            self.assertEqual(self.owed(), [], status)

    def test_post_held_then_release_and_stop(self):
        self.launch("r-h")
        self.post(tool_name="workflow", args={"action": "wait"},
                  result=_run_result("r-h", status="held"), session_id="S")
        self.assertEqual(self.led.entries("S")[0][1]["state"], "held")
        self.post(tool_name="workflow", args={"action": "release", "run_id": "r-h"},
                  result=_run_result("r-h", released=True), session_id="S")
        self.assertEqual(self.led.entries("S")[0][1]["state"], "pending")
        self.post(tool_name="workflow", args={"action": "stop", "run_id": "r-h"},
                  result=_run_result("r-h"), session_id="S")
        self.assertEqual(self.owed(), [])

    def test_post_ignores_other_tools_errors_and_foreign_status(self):
        self.post(tool_name="terminal", args={"action": "run"}, result=_run_result("r-x"),
                  session_id="S")
        self.post(tool_name="workflow", args={"action": "run"},
                  result=json.dumps({"error": "bad graph", "run_id": "r-x"}), session_id="S")
        self.post(tool_name="workflow", args={"action": "run"}, result="not json", session_id="S")
        self.post(tool_name="workflow", args={"action": "status"},
                  result=_run_result("r-other", status="held"), session_id="S")
        self.assertFalse(self.file.exists())

    # ---- pre_llm_call ---------------------------------------------------------
    def test_pre_llm_context_only_when_pending(self):
        self.assertIsNone(self.pre(session_id="S"))
        self.launch("r-pre", name="nightly")
        out = self.pre(session_id="S")
        self.assertIn("r-pre", out["context"])
        self.assertIn("nightly", out["context"])
        self.assertIsNone(self.pre(session_id="OTHER"))
        self.led.drop("S", "r-pre")
        self.assertIsNone(self.pre(session_id="S"))

    # ---- shipper reads the ledger ---------------------------------------------
    def test_ship_appends_card_and_drops_on_selection(self):
        self.launch("r-ship")
        out = self.select(self.fire())
        self.assertTrue(out.startswith("All done."))
        self.assertTrue(out.rstrip().endswith(self.card("r-ship")), out)
        self.assertEqual(self.owed(), [], "selected text must drop the ledger entry")
        self.assertIsNone(self.fire(turn="t2"), "one-shot: never ships again")

    def test_unselected_proposal_replays(self):
        self.launch("r-lose")
        out = self.fire()
        self.assertIsNotNone(out)
        del out                                               # core discarded it unselected
        import gc
        gc.collect()
        self.assertEqual(self.owed(), ["r-lose"])
        self.assertIsNotNone(self.select(self.fire(turn="t2")))

    def test_pasted_directive_hands_off_and_retires_that_run(self):
        self.launch("r-p1")
        self.launch("r-p2")
        self.assertIsNone(self.fire(text=f"here {self.card('r-p1')}"))
        self.assertEqual(self.owed(), ["r-p2"])

    def test_fenced_directive_does_not_count(self):
        self.launch("r-f")
        out = self.select(self.fire(text=f"```\n{self.card('r-f')}\n```"))
        self.assertTrue(out.rstrip().endswith(self.card("r-f")))

    def test_unclosed_fence_still_ships_visible(self):
        self.launch("r-u")
        out = self.select(self.fire(text="see:\n```\ncode"))
        tail = out.rstrip()
        self.assertTrue(tail.endswith(self.card("r-u")))
        self.assertEqual(out.count("```") % 2, 0, out)

    def test_foreign_session_blank_platform_and_empty_text_ship_nothing(self):
        self.launch("r-own")
        self.assertIsNone(self.fire(sid="OTHER"))
        self.assertIsNone(self.fire(platform=""))
        self.assertIsNone(self.fire(text=""))
        self.assertEqual(self.owed(), ["r-own"])

    def test_ceiling_three_newest_first(self):
        import time
        for i in range(5):
            self.launch(f"r-{i}")
            time.sleep(1.1)                                   # ts is second-granular ISO
        out = self.select(self.fire())
        shipped = [i for i in range(5) if self.card(f"r-{i}") in out]
        self.assertEqual(shipped, [2, 3, 4])
        self.assertEqual(self.owed(), ["r-1", "r-0"])

    # ---- fail-open ------------------------------------------------------------
    def test_unwritable_ledger_every_callback_returns_none(self):
        self.file.mkdir()                                     # the ledger path is a directory
        self.assertIsNone(self.launch("r-dir"))
        self.assertIsNone(self.pre(session_id="S"))
        self.assertIsNone(self.fire())
        self.assertFalse(self.led.add("S", "r-dir", "n"))
        self.assertEqual(self.led.entries("S"), [])

    def test_broken_ledger_module_never_eats_the_reply(self):
        self.launch("r-boom")
        with mock.patch.object(self.led, "entries", side_effect=RuntimeError("boom")):
            self.assertIsNone(self.fire())
            self.assertIsNone(self.pre(session_id="S"))

    # ---- registration + scan is gone (API shape) ------------------------------
    def test_register_wires_three_hooks(self):
        # the ledger's three hooks are wired; PR-3's default-off admission/witness hooks
        # (post_gateway_admission, pre_gateway_dispatch) ride the same register() and are not this lane's.
        self.assertTrue({"post_tool_call", "pre_llm_call", "transform_llm_output"} <= set(self.ctx.hooks))

    def test_scan_entrypoints_are_gone(self):
        ce, cl = self.hw._card_enforcement, self.hw._card_ledger
        for name in ("_outstanding", "_roots", "_terminal_stale", "_events", "_age_minutes",
                     "_mark", "DEFAULT_WINDOW_MINUTES", "WINDOW_SETTING",
                     "TERMINAL_STALE_MINUTES"):
            self.assertFalse(hasattr(ce, name), f"card_enforcement.{name} must be deleted")
            self.assertFalse(hasattr(cl, name), f"card_ledger.{name} must not exist")


if __name__ == "__main__":
    unittest.main(verbosity=2)
