#!/usr/bin/env python3
"""est-z717: the dashboard's GET /settings answers ONLY {tray: <bool>} with
the owner-setting truth, FAIL-CLOSED - everything other than literal True
(absent key, false, a malformed value, an unreadable config) answers False
(default OFF until hermes-agent#133724 lands the native tray SDK area).
The desktop consumes it once at register() to resolve $trayGate.

RED on base for the gate contract: base plugin_api.py has no /settings route
at all (AttributeError below fails every case).
"""
import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("hwapi_z717", ROOT / "dashboard" / "plugin_api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class SettingsRoute(unittest.TestCase):
    def _settings(self, value, raises=False):
        def reader(k):
            if raises:
                raise ValueError("boom")
            return value
        fake = types.SimpleNamespace(owner_setting=reader)
        with patch.object(api, "_workflow_common", return_value=fake):
            return asyncio.run(api.get_settings())

    def test_true_enables(self):
        self.assertEqual(self._settings(True), {"tray": True},
                         "settings.tray=true (literal True) => the gate opens")

    def test_absent_false_malformed_fail_closed(self):
        for bad in (None, False, "true", 1, {}):
            self.assertEqual(self._settings(bad), {"tray": False},
                             f"{bad!r} is NOT literal True => fail-closed hidden (default OFF)")
        self.assertEqual(self._settings(None, raises=True), {"tray": False},
                         "an unreadable owner setting fails CLOSED, never opens the tray")

    def test_reads_the_established_owner_setting_shape(self):
        seen = []

        def reader(k):
            seen.append(k)
            return True
        fake = types.SimpleNamespace(owner_setting=reader)
        with patch.object(api, "_workflow_common", return_value=fake):
            asyncio.run(api.get_settings())
        self.assertEqual(seen, ["tray"],
                         "the read rides wfcommon.owner_setting - THE established settings shape "
                         "(ctx reader else raw config, settings>legacy)")

    def test_route_registered(self):
        paths = {(r.path, tuple(sorted(r.methods))) for r in api.router.routes}
        self.assertIn(("/settings", ("GET",)), paths,
                      "GET /settings is registered beside /runs (the desktop api('/settings') bootstrap)")

    def test_no_other_setting_leaks(self):
        fake = types.SimpleNamespace(owner_setting=lambda k: True)
        with patch.object(api, "_workflow_common", return_value=fake):
            out = asyncio.run(api.get_settings())
        self.assertEqual(set(out.keys()), {"tray"},
                         "the route answers ONLY the tray key - never a settings dump")


if __name__ == "__main__":
    unittest.main(verbosity=2)
