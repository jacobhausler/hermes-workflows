#!/usr/bin/env python3
"""Runner boot recovers missing install pins without replacing present launchers."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LauncherRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wf-launcher-recovery-')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.bin = self.home / 'bin'
        self.bin.mkdir()
        self.run_dir = self.home / 'workflows' / 'recovery'
        self.run_dir.mkdir(parents=True)
        self.log = self.home / 'launches.log'
        self.shim = self.launcher('hermes', 'path-shim')

    def launcher(self, name, marker):
        path = self.bin / name
        path.write_text(
            '#!' + sys.executable + '\n'
            'import json, os\n'
            'with open(os.environ["LAUNCH_LOG"], "a") as out:\n'
            '    out.write(' + repr(marker + '\n') + ')\n'
            'print("```json\\n" + json.dumps({"launcher": ' + repr(marker) + '}) + "\\n```")\n')
        path.chmod(0o755)
        return path

    def drive(self, pin, path=None):
        graph = {'name': 'recovery', 'nodes': [
            {'id': 'probe', 'type': 'agent', 'goal': 'return the launcher marker'}]}
        meta = {'name': 'recovery', 'hermes_bin': pin, 'concurrency': 1,
                'node_timeout': 10}
        (self.run_dir / 'graph.json').write_text(json.dumps(graph))
        (self.run_dir / 'run.json').write_text(json.dumps(meta))
        # Only the fixture's PATH can choose a launcher. Never inherit a real
        # seat's override, provider, settings home, session identity or shelf.
        env = {k: os.environ[k] for k in ('TMPDIR', 'SYSTEMROOT') if k in os.environ}
        env.update(HOME=str(self.home), HERMES_HOME=str(self.home),
                   WF_RUNS_ROOT=str(self.home / 'workflows'),
                   WF_SEATS_DIR=str(self.home / 'seats'), WORKFLOW_MAX_SEATS='0',
                   PATH=str(self.bin) if path is None else path,
                   LAUNCH_LOG=str(self.log), PYTHONPATH=str(ROOT))
        p = subprocess.run([sys.executable, str(ROOT / 'wf.py'), 'run', 'recovery'],
                           cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=30)
        rec = json.loads((self.run_dir / 'nodes' / 'probe.json').read_text())
        self.assertEqual(json.loads((self.run_dir / 'run.json').read_text()), meta,
                         'boot must not rewrite the durable owner metadata')
        return rec, p.stdout

    def done(self, rec, stdout, marker):
        self.assertEqual(rec.get('status'), 'done', (rec, stdout))
        self.assertEqual(rec['output'], {'launcher': marker})
        self.assertEqual(self.log.read_text().splitlines(), [marker])
        self.assertIn('WORKFLOW_DONE recovery', stdout)

    def failed(self, rec, stdout):
        self.assertEqual(rec.get('status'), 'failed', (rec, stdout))
        self.assertEqual(rec.get('error_class'), 'spawn', rec)
        self.assertIn('launcher spawn failed', rec.get('error', ''))
        self.assertEqual(rec.get('attempts'), 1, rec)
        self.assertFalse(self.log.exists(), 'no replacement launcher may run')
        self.assertIn('WORKFLOW_FAILED recovery', stdout)

    def test_absent_install_pin_uses_path_shim(self):
        missing = self.home / 'installs' / 'collected-env' / 'venv' / 'bin' / 'hermes'
        self.assertFalse(missing.exists())
        rec, stdout = self.drive(str(missing))
        self.done(rec, stdout, 'path-shim')

    def test_existing_pin_is_retained(self):
        valid = self.launcher('pinned-hermes', 'valid-pin')
        rec, stdout = self.drive(str(valid))
        self.done(rec, stdout, 'valid-pin')

    def test_absent_pin_without_replacement_fails_closed(self):
        rec, stdout = self.drive(str(self.home / 'collected-hermes'), path='')
        self.failed(rec, stdout)

    def test_existing_nonexecutable_pin_is_not_replaced(self):
        blocked = self.launcher('blocked-hermes', 'must-not-run')
        blocked.chmod(0o644)
        rec, stdout = self.drive(str(blocked))
        self.failed(rec, stdout)

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0,
                     'root bypasses fixture directory permissions')
    def test_inaccessible_pin_is_not_replaced(self):
        locked = self.home / 'locked'
        locked.mkdir()
        pin = locked / 'hermes'
        pin.write_text(self.shim.read_text())
        pin.chmod(0o755)
        locked.chmod(0o000)
        try:
            rec, stdout = self.drive(str(pin))
            self.failed(rec, stdout)
        finally:
            locked.chmod(0o700)

    def test_dangling_pin_symlink_uses_path_shim(self):
        link = self.bin / 'collected-link'
        link.symlink_to(self.home / 'gone-environment' / 'hermes')
        rec, stdout = self.drive(str(link))
        self.done(rec, stdout, 'path-shim')

    def test_bare_custom_path_command_is_retained(self):
        self.launcher('custom-hermes', 'custom-path-command')
        rec, stdout = self.drive('custom-hermes')
        self.done(rec, stdout, 'custom-path-command')

    def test_empty_pin_keeps_path_resolution(self):
        rec, stdout = self.drive('')
        self.done(rec, stdout, 'path-shim')


if __name__ == '__main__':
    unittest.main(verbosity=2)
