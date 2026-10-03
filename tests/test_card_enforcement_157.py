#!/usr/bin/env python3
"""#157 (MACHINERY rung, backend half): card enforcement via transform_llm_output.

core fires the 'transform_llm_output' hook once per turn BEFORE the final assistant
row is persisted (hermes_cli/plugins.py VALID_HOOKS; agent/turn_finalizer.py
apply_llm_output_transform — first hook returning a non-empty string wins and that
string becomes the persisted+streamed text). The hook must:
  (a) append the missing ::workflow card as new lines for a launch this session
      made inside the window, and stamp card.echoed into the run's events.jsonl;
  (b) never ship the same run's card twice (the marker is the ledger);
  (c) leave a response that already carries the bare directive untouched;
  (d) NOT count a directive that sits only inside a code fence (fences are dead
      text to the directive renderer, so the card is still owed);
  (e) never ship another session's runs (owner.session_id gate);
  (f) fail-open: any discovery/parse error returns None, never raises;
  (g) cap at 3 cards per turn, newest launches first;
  (h) skip runs outside the recency window (default 30 min, owner-setting).
desktop/plugin.js is untouched: the directive renderer already turns the persisted
card line into a DirectiveCard — this rung only guarantees the line lands.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_door():
    spec = importlib.util.spec_from_file_location("hw_card157", ROOT / "__init__.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Ctx:
    """Minimal PluginContext stand-in (same shape as the O1 register-surface test)."""
    def __init__(self):
        self.hooks = {}
    def register_hook(self, name, fn):
        self.hooks[name] = fn
    def register_tool(self, **_):
        pass
    def register_command(self, *_, **__):
        pass
    def register_skill(self, name, path, **_):
        pass
    def get_config(self, key, default):
        return default


def _iso(minutes_ago):
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")


class CardEnforcement(unittest.TestCase):
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
        wf_test_isolation.install(self.hw)  # #71 r5: pin settings.runs_root to WF_RUNS_ROOT
        ctx = _Ctx()
        self.hw.register(ctx)
        self.assertIn("transform_llm_output", ctx.hooks,
                      "register() must wire the card-enforcement hook (#157)")
        self.hook = ctx.hooks["transform_llm_output"]
        self.runs = Path(os.environ["WF_RUNS_ROOT"])

    def tearDown(self):
        self.env.stop()
        self.home.cleanup()

    # ---- helpers --------------------------------------------------------
    def mk_run(self, rid, sid="S", minutes_ago=1.0, events=(), bad_json=False,
               root=None):
        r = (root or self.runs) / rid
        (r / "nodes").mkdir(parents=True)
        if bad_json:
            (r / "run.json").write_text("{not json")
        else:
            (r / "run.json").write_text(json.dumps(
                {"name": "t", "started": _iso(minutes_ago), "owner": {"session_id": sid}}))
        if events:
            with (r / "events.jsonl").open("a") as f:
                for e in events:
                    f.write(json.dumps(e) + "\n")
        return r

    def card(self, rid):
        return f'::workflow{{id="{rid}"}}'

    def call(self, text="All done.", sid="S", turn="t1", platform="desktop"):
        return self.hook(response_text=text, session_id=sid, turn_id=turn,
                         platform=platform, model="m")

    def echoed(self, r):
        p = r / "events.jsonl"
        if not p.exists():
            return []
        out = []
        for line in p.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("event") == "card.echoed":
                out.append(e)
        return out

    # ---- (a) launch turn, no directive in text: card ships + marker ----------
    def test_a_appends_card_and_stamps_marker(self):
        r = self.mk_run("r-one")
        out = self.call()
        self.assertIsNotNone(out)
        self.assertTrue(out.startswith("All done."))
        self.assertTrue(out.rstrip().endswith(self.card("r-one")), out)
        marked = self.echoed(r)
        self.assertEqual(len(marked), 1)
        self.assertEqual(marked[0]["session_id"], "S")
        self.assertEqual(marked[0]["turn_id"], "t1")
        self.assertIn("ts", marked[0])

    # ---- (b) second call same turn/next turn: nothing left outstanding ------
    def test_b_marker_makes_it_one_shot(self):
        self.mk_run("r-two")
        first = self.call()
        self.assertIsNotNone(first)
        self.assertIsNone(self.call())            # retry, same turn
        self.assertIsNone(self.call(turn="t2"))   # next turn

    # ---- (c) model already pasted the bare directive: hands off --------------
    def test_c_bare_directive_present_no_append(self):
        r = self.mk_run("r-three")
        out = self.call(text=f"Shipped.\n\n{self.card('r-three')}")
        self.assertIsNone(out)
        self.assertEqual(self.echoed(r), [])

    # ---- (d) directive only inside a fence: dead text, card still owed -------
    def test_d_fenced_directive_does_not_count(self):
        self.mk_run("r-four")
        out = self.call(text="Shipped:\n```\n" + self.card("r-four") + "\n```\n")
        self.assertIsNotNone(out)
        self.assertTrue(out.rstrip().endswith(self.card("r-four")), out)

    def test_d2_inline_code_directive_does_not_count(self):
        self.mk_run("r-fourb")
        out = self.call(text="paste `" + self.card("r-fourb") + "` now")
        self.assertIsNotNone(out)
        self.assertTrue(out.rstrip().endswith(self.card("r-fourb")), out)

    # ---- (e) foreign session: never another session's cards ------------------
    def test_e_foreign_session_gets_nothing(self):
        self.mk_run("r-five", sid="OTHER")
        self.assertIsNone(self.call())

    # ---- unknown surface: falsy platform never appends ----------------------
    def test_blank_platform_or_empty_text_never_appends(self):
        self.mk_run("r-six")
        self.assertIsNone(self.call(platform=""))
        self.assertIsNone(self.call(platform=None))  # type: ignore[arg-type]
        self.mk_run("r-sixb")
        self.assertIsNone(self.hook(response_text="", session_id="S", turn_id="t1",
                                    platform="desktop", model="m"))

    # ---- (f) fail-open: torn run.json and exploding discovery -> None --------
    def test_f_bad_run_json_no_raise(self):
        self.mk_run("r-seven", bad_json=True)
        self.assertIsNone(self.call())  # unreadable = not discoverable, never raises

    def test_f_exception_in_discovery_returns_none(self):
        self.mk_run("r-eight")
        common = self.hw._common
        with mock.patch.object(common, "runs_root", side_effect=RuntimeError("boom")):
            self.assertIsNone(self.call())

    def test_f_marker_write_failure_still_ships_text(self):
        r = self.mk_run("r-eightb")
        target = r / "events.jsonl"
        target.write_text("]\n")  # torn tail line
        target.chmod(0o444)       # marker append will fail
        try:
            out = self.call()
        finally:
            target.chmod(0o644)
        self.assertIsNotNone(out)
        self.assertTrue(out.rstrip().endswith(self.card("r-eightb")), out)

    # ---- (g) five launches one turn: max 3, newest first ---------------------
    def test_g_ceiling_three_newest_first(self):
        dirs = {}
        for i in range(1, 6):
            dirs[f"r-{i}"] = self.mk_run(f"r-{i}", minutes_ago=float(i))
        out = self.call()
        self.assertIsNotNone(out)
        lines = [ln for ln in out.splitlines() if ln.startswith("::workflow{")]
        self.assertEqual(lines, [self.card(f"r-{i}") for i in (1, 2, 3)], out)
        for i in (4, 5):  # the two oldest stay outstanding (unmarked)
            self.assertEqual(self.echoed(dirs[f"r-{i}"]), [])
        for i in (1, 2, 3):
            self.assertEqual(len(self.echoed(dirs[f"r-{i}"])), 1)

    # ---- (h) outside the recency window --------------------------------------
    def test_h_outside_window(self):
        self.mk_run("r-nine", minutes_ago=31.0)
        self.assertIsNone(self.call())

    def test_h_window_is_owner_settings_configurable(self):
        self.mk_run("r-ten", minutes_ago=3.0)
        real = self.hw._common.owner_setting
        def fake(key):
            return 2 if key == "card_window_minutes" else real(key)
        with mock.patch.object(self.hw._common, "owner_setting", side_effect=fake):
            self.assertIsNone(self.call())
        with mock.patch.object(self.hw._common, "owner_setting", side_effect=fake):
            self.mk_run("r-tenb", minutes_ago=1.0)
            self.assertIsNotNone(self.call(turn="t9"))

    # ---- discovery covers EVERY profile runs root ----------------------------
    def test_i_profile_runs_root_is_scanned(self):
        # A profile-scoped gateway resolves runs_root() to <profile_home>/workflows
        # (no env pin, no owner pin — the #41/#42 measured host shape). Drop the
        # WF_RUNS_ROOT pin so the resolver takes that branch for real.
        prof_runs = Path(self.home.name) / "profiles" / "p2" / "workflows"
        self.mk_run("r-prof", root=prof_runs)
        os.environ.pop("WF_RUNS_ROOT", None)
        out = self.call()
        self.assertIsNotNone(out)
        self.assertTrue(out.rstrip().endswith(self.card("r-prof")), out)

    # ---- malformed run ids (a hand-typed/foreign directive) don't count as shipped
    def test_j_malformed_directive_does_not_suppress(self):
        self.mk_run("r-eleven")
        out = self.call(text="done ::workflow{id=\"has space!\"} over")
        self.assertIsNotNone(out)
        self.assertTrue(out.rstrip().endswith(self.card("r-eleven")), out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
