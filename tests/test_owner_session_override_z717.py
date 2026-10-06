#!/usr/bin/env python3
"""est-z717 ESTATE-SHAPE LAW pin: the door's owner stamp honors an explicit
WF_OWNER_SESSION env override, default behavior unchanged for interactive
chats.

The gap this pins: estate/dispatcher-launched runs inherit the DISPATCHER's
HERMES_SESSION_ID at the door, so the run impersonates the dispatcher's chat
in that chat's pillrail (an owner the launching context never was). The
honest rule (owner ruling 10-06): a launcher that knows it is NOT the chat
sets WF_OWNER_SESSION itself — EMPTY means "no chat owns this run" (owner
keys null -> pane-only, the blank-owner honest-absent law the rail already
enforces); NON-EMPTY stamps that session verbatim with ui/platform null (the
surrounding env ids belong to the launcher, not to the stamped owner); UNSET
is byte-identical today (interactive chats inherit HERMES_SESSION_ID).

RED-first (house law): the whole file is RED on base — base __init__.py has
no _owner_stamp(): WF_OWNER_SESSION is ignored, the override tests fail, the
inheritance test passes on base AND head (it is the unchanged-default guard).
Mutation proof for the override wiring lives beside it (see GATES.md).
"""
import importlib.util, json, os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_z717b", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
sys.path.insert(0, str(ROOT / "tests"))
import wf_test_isolation as _iso71; _iso71.install(door)
G = {"name": "z717-owner", "nodes": [{"id": "x", "type": "echo", "output": {"ok": True}}]}


class OwnerSessionOverride(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        base = {"WF_RUNS_ROOT": str(self.root),
                "HERMES_HOME": str(self.root / "home"),
                "HERMES_SESSION_ID": "dispatcher-sid",
                "HERMES_UI_SESSION_ID": "dispatcher-ui-sid",
                "HERMES_SESSION_PLATFORM": "dispatcher-platform"}
        env = patch.dict(os.environ, base, clear=False)
        env.start()
        self.addCleanup(env.stop)
        # The override key itself must never leak between cases.
        os.environ.pop("WF_OWNER_SESSION", None)
        self.addCleanup(os.environ.pop, "WF_OWNER_SESSION", None)
        spawn = patch.object(door, "_spawn_runner", side_effect=lambda r: None)
        spawn.start()
        self.addCleanup(spawn.stop)

    def _owner(self, extra_env=None):
        with patch.dict(os.environ, extra_env or {}):
            out = door.act_run({"graph": dict(G)})
        self.assertIn("run_id", out, out)
        meta = json.loads((self.root / out["run_id"] / "run.json").read_text())
        return meta.get("owner")

    def test_unset_inherits_the_session_env(self):
        """Default law (UNCHANGED): interactive chats inherit HERMES_SESSION_ID."""
        owner = self._owner()
        self.assertEqual(owner.get("session_id"), "dispatcher-sid",
            "WF_OWNER_SESSION unset => today's inheritance, byte-identical")
        self.assertEqual(owner.get("ui_session_id"), "dispatcher-ui-sid")
        self.assertEqual(owner.get("platform"), "dispatcher-platform")

    def test_blank_override_is_pane_only(self):
        """ESTATE-SHAPE LAW: WF_OWNER_SESSION='' (set BY THE LAUNCHER) => every
        owner key null => blank-owner honest-absent => pane-only, never a rail."""
        owner = self._owner({"WF_OWNER_SESSION": ""})
        self.assertEqual(owner.get("session_id"), None,
            "blank override => owner null (the dispatcher's chat is NOT impersonated)")
        self.assertEqual(owner.get("ui_session_id"), None)
        self.assertEqual(owner.get("platform"), None)

    def test_explicit_override_stamps_the_named_session(self):
        """Non-empty override stamps that session verbatim; ui/platform ride
        null (launcher env residue would be unverifiable impersonation)."""
        owner = self._owner({"WF_OWNER_SESSION": "on-behalf-of-sid"})
        self.assertEqual(owner.get("session_id"), "on-behalf-of-sid")
        self.assertEqual(owner.get("ui_session_id"), None)
        self.assertEqual(owner.get("platform"), None)

    def test_override_beats_the_gateway_reader_shape(self):
        """The override reads process env (the launcher contract), independent
        of the gateway session-context reader used for inheritance."""
        with patch.object(door, "_session_env", side_effect=lambda n: "gateway-sid"):
            base_owner = self._owner()
        self.assertEqual(base_owner.get("session_id"), "gateway-sid",
            "unset override still rides _session_env (gateway reader first)")
        with patch.object(door, "_session_env", side_effect=lambda n: "gateway-sid"):
            owner = self._owner({"WF_OWNER_SESSION": ""})
        self.assertEqual(owner.get("session_id"), None,
            "the override wins over the gateway reader when SET")


if __name__ == "__main__":
    unittest.main(verbosity=2)
