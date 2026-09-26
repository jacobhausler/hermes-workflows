#!/usr/bin/env python3
"""Integrated read-model and parser-valid card dedup checks."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('integrated_workflow', ROOT / '__init__.py')
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

class Integrated(unittest.TestCase):
    def test_steer_roundtrip(self):
        from unittest.mock import patch
        sys.path.insert(0, str(ROOT))
        import wf as engine
        with tempfile.TemporaryDirectory(dir=ROOT) as home:
            with patch.dict(os.environ, {'HERMES_HOME': home}), patch.object(wf, '_spawn_runner'):
                result = wf.act_run({'graph': {'name': 'steering', 'nodes': [
                    {'id': 'a', 'type': 'agent', 'goal': 'offline'}]}})
                rid = result['run_id']; run = Path(home) / 'workflows' / rid
                self.assertTrue(wf.act_steer({'run_id': rid, 'node': 'a', 'text': 'first'})['ok'])
                self.assertEqual(engine.drain_inbox(run, set()), {'a': ['first']})
                self.assertTrue(wf.act_steer({'run_id': rid, 'node': 'a', 'text': 'second'})['ok'])
                consumed = set()
                self.assertEqual(engine.drain_inbox(run, consumed), {'a': ['first', 'second']})
                self.assertEqual(engine.drain_inbox(run, consumed), {})

    def test_spawn_projection_is_read_only_and_identity_checked(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as td:
            r = Path(td) / 'run'; (r / 'nodes').mkdir(parents=True)
            graph = {'name': 'active', 'nodes': [{'id': 'a', 'type': 'agent', 'goal': 'offline'}]}
            (r / 'graph.json').write_text(json.dumps(graph))
            script = Path(td) / 'wf.py'
            script.write_text('import time\ntime.sleep(20)\n')
            runner = subprocess.Popen([sys.executable, str(script), 'run', r.name],
                                      env={**os.environ, 'HERMES_HOME': str(r.parent.parent)})
            (r / 'wf.pid').write_text(str(runner.pid))
            skey = 'wf:test:a:identity#a0'
            proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)', skey])
            try:
                rec = {'status': 'running', 'pid': proc.pid, 'skey': skey, 'attempt': 0,
                       'efp': wf.efp({'a': graph['nodes'][0]}, graph['nodes'][0])}
                (r / 'nodes/a.json').write_text(json.dumps(rec))
                st = wf.run_state(r)
                self.assertEqual(st['nodes']['a']['status'], 'running')
                self.assertEqual(st['nodes']['a']['active_spawn']['pid'], proc.pid)
                self.assertEqual(wf._common.node_rec(r, graph['nodes'][0], {'a': graph['nodes'][0]})[0], 'pending')
                # BSD/macOS has no procfs; exercise the real ps fallback on Linux too.
                from unittest.mock import patch
                read_text = Path.read_text
                def no_proc(path, *args, **kwargs):
                    if str(path).startswith('/proc/'):
                        raise FileNotFoundError(str(path))
                    return read_text(path, *args, **kwargs)
                with patch.object(Path, 'read_text', no_proc):
                    self.assertEqual(wf.run_state(r)['nodes']['a']['status'], 'running')
                rec['skey'] = 'wrong-identity'; (r / 'nodes/a.json').write_text(json.dumps(rec))
                with patch.object(Path, 'read_text', no_proc):
                    self.assertEqual(wf.run_state(r)['nodes']['a']['status'], 'pending')
            finally:
                proc.terminate(); proc.wait(timeout=5)
                runner.terminate(); runner.wait(timeout=5)

if __name__ == '__main__':
    unittest.main()
