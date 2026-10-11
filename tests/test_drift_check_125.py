#!/usr/bin/env python3
"""#125 slice 3: real offline repositories, digest/exits, and git argv boundary."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon as wc


class DriftCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='drift-125-')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.manifest('1.0.0')
        self.commit('release #125')
        self.git('tag', 'v1.0.0')

    def git(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        return subprocess.run(['git', *args], cwd=self.repo, env=env,
                              capture_output=True, text=True, check=True).stdout

    def manifest(self, version):
        (self.repo / 'plugin.yaml').write_text('version: ' + version + '\n')
        (self.repo / 'CHANGELOG.md').write_text('## ' + version + ' — test\n')

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-qm', message)

    def assert_report(self, verdict, rc, local=0, missing=0, script=None):
        report = wc.drift_report(self.repo)
        self.assertEqual(report['verdict'], verdict, report)
        if rc != 2:
            self.assertEqual(report['local_only_commits'], local)
            self.assertEqual(report['trailers_missing'], missing)
        proc = subprocess.run([sys.executable, str(script or ROOT / 'scripts/drift_check.py'),
                               '--repo', str(self.repo)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, rc, proc.stderr + proc.stdout)
        self.assertRegex(proc.stdout.splitlines()[-1],
                         r'^installed_version=\S+ upstream_latest=\S+ local_only_commits=\S+ '
                         r'trailers_missing=\S+ verdict=' + verdict + '$')
        return report

    def test_clean_and_allowlist(self):
        real = subprocess.run
        with patch.object(wc.subprocess, 'run', wraps=real) as spy:
            self.assertEqual(wc.drift_report(self.repo)['verdict'], 'clean')
        self.assertEqual([c.args[0][1] for c in spy.call_args_list],
                         ['describe', 'rev-list', 'log'])
        for call in spy.call_args_list:
            self.assertEqual(call.args[0][0], 'git')
            self.assertEqual(call.kwargs['env']['GIT_NO_LAZY_FETCH'], '1')
            self.assertNotIn('shell', call.kwargs)
        self.assert_report('clean', 0)

    def test_version_mismatch(self):
        self.manifest('2.0.0')
        report = self.assert_report('version_mismatch', 1)
        self.assertEqual(report['installed_version'], '2.0.0')
        self.assertEqual(report['upstream_latest'], '1.0.0')

    def test_local_only_with_each_tracker_form(self):
        for i, msg in enumerate(('tracked (est-b994)', 'tracked #125')):
            (self.repo / 'extra').write_text(str(i))
            self.commit(msg)
        self.assert_report('local_only', 1, local=2)

    def test_missing_trailers_and_precedence(self):
        (self.repo / 'extra').write_text('untracked')
        self.commit('no tracker')
        self.assert_report('trailers_missing', 1, local=1, missing=1)
        self.manifest('2.0.0')
        self.assert_report('version_mismatch', 1, local=1, missing=1)

    def test_new_local_release_tag(self):
        self.manifest('2.0.0')
        self.commit('release #125')
        self.git('tag', '-am', 'release', 'v2.0.0')
        self.assertEqual(self.assert_report('clean', 0)['upstream_latest'], '2.0.0')

    def test_changelog_heading_missing(self):
        (self.repo / 'CHANGELOG.md').write_text('## 10.0.0\n')
        self.assertIn('changelog_heading_missing', self.assert_report('error', 2)['error'])

    def test_broken_state(self):
        for filename in ('plugin.yaml', 'CHANGELOG.md'):
            with self.subTest(filename=filename):
                p = self.repo / filename
                text = p.read_text()
                p.unlink()
                self.assert_report('error', 2)
                p.write_text(text)
        (self.repo / 'plugin.yaml').write_text('version: nonsense\n')
        self.assert_report('error', 2)
        self.manifest('1.0.0')
        self.git('tag', '-d', 'v1.0.0')
        self.assert_report('error', 2)
        shutil.rmtree(self.repo / '.git')
        self.assert_report('error', 2)

    def test_git_failure_timeout_and_foreign_env(self):
        for error in (FileNotFoundError('git'), subprocess.TimeoutExpired(['git'], 15)):
            with patch.object(wc.subprocess, 'run', side_effect=error):
                self.assertEqual(wc.drift_report(self.repo)['verdict'], 'error')
        with patch.dict(os.environ, GIT_DIR='/does/not/exist', GIT_WORK_TREE='/wrong'):
            self.assert_report('clean', 0)

    def test_invalid_args_keep_error_digest(self):
        for args in (['--repo'], ['--unknown']):
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/drift_check.py'), *args],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertTrue(proc.stdout.rstrip().endswith('verdict=error'))

    def test_default_repo_is_script_parent(self):
        (self.repo / 'scripts').mkdir()
        shutil.copyfile(ROOT / 'scripts/drift_check.py', self.repo / 'scripts/drift_check.py')
        shutil.copyfile(ROOT / 'wfcommon.py', self.repo / 'wfcommon.py')
        proc = subprocess.run([sys.executable, str(self.repo / 'scripts/drift_check.py')],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertTrue(proc.stdout.rstrip().endswith('verdict=clean'))


if __name__ == '__main__':
    unittest.main()
