#!/usr/bin/env python3
"""#129: exit-agent grammar, terminal Inputs/receipt, once-only and recovery.

Runs as a stdlib serial script or under pytest. All children are fixture CLIs;
no provider, live run store, or user session is used.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest

BUILD = Path(os.environ.get('WF_TEST_BUILD') or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(BUILD))
import wfcommon

STUB = r'''
import json, os, re, sys, time
args = sys.argv[1:]
if '--query-file' not in args:
    sys.exit(0)
prompt = open(args[args.index('--query-file') + 1]).read()
if 'EXIT129' in prompt:
    match = re.search(r'on_exit \(run facts\)\n```json\n(.*?)\n```', prompt, re.S)
    facts = json.loads(match.group(1)) if match else {'missing_inputs': True}
    if 'DIE_EXIT129' in prompt:
        print('exit agent failed deliberately', flush=True)
        sys.exit(9)
    print('```json\n' + json.dumps({'exit': facts}) + '\n```', flush=True)
    if 'SLOW_EXIT129' in prompt:
        open('exit-ready', 'w').write('ready')
        time.sleep(60)
else:
    if 'FAIL129' in prompt:
        print("Unknown provider 'invalid_fixture_route'", flush=True)
        sys.exit(1)
    print('```json\n{"result":"ok"}\n```', flush=True)
'''


class OnExit129(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wf-exit129-')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.runs = self.home / 'runs'
        self.stub = self.home / 'stub.py'
        self.stub.write_text(f'#!{sys.executable}\n' + STUB)
        self.stub.chmod(0o755)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(('HERMES_WF_', 'HERMES_SESSION_', 'HERMES_UI_SESSION_'))
                    and k != 'WF_TEST_BUILD'}
        self.env.update(HERMES_HOME=str(self.home), WF_RUNS_ROOT=str(self.runs),
                        HERMES_WF_HERMES_BIN=str(self.stub), WORKFLOW_MAX_SEATS='0')

    def graph(self, goal='OK129', exit_goal='EXIT129'):
        return {'name': 'exit129', 'on_exit': 'post', 'nodes': [
            {'id': 'work', 'type': 'agent', 'goal': goal, 'timeout': 5},
            {'id': 'post', 'type': 'agent', 'after': ['work'],
             'goal': exit_goal, 'timeout': 5}]}

    def make(self, graph=None, rid='fixture'):
        r = self.runs / rid
        (r / 'nodes').mkdir(parents=True)
        (r / 'gates').mkdir()
        (r / 'graph.json').write_text(json.dumps(graph or self.graph()))
        (r / 'run.json').write_text(json.dumps({'hermes_bin': str(self.stub),
            'concurrency': 1, 'node_timeout': 5, 'retry_backoff': [0], 'retry_budget': 0}))
        return r

    def command(self, r):
        return [sys.executable, str(BUILD / 'wf.py'), 'run', r.name]

    def drive(self, r):
        p = subprocess.run(self.command(r), env=self.env, capture_output=True,
                           text=True, timeout=35)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def events(self, r, name):
        return [e for e in (json.loads(s) for s in (r / 'events.jsonl').read_text().splitlines())
                if e.get('event') == name]

    def assert_exit(self, r, status, failed=None):
        failed = failed or []
        self.assertEqual(len(self.events(r, 'on_exit.spawned')), 1)
        self.assertEqual(len(self.events(r, 'on_exit.finished')), 1)
        self.assertTrue((r / 'on_exit_receipt.md').is_file())
        receipt = (r / 'on_exit_receipt.md').read_text()
        rec = json.loads((r / 'nodes/post.json').read_text())
        facts = rec['output']['exit']
        self.assertEqual(facts['run_status'], status)
        self.assertEqual(facts['failed_node_ids'], failed)
        self.assertIn(json.dumps(status), receipt)
        self.assertEqual(wfcommon.run_state(r)['status'], 'failed' if status == 'crashed' else status)
        return facts

    def test_grammar_and_all_doors(self):
        g = self.graph()
        self.assertEqual(wfcommon.validate_graph_full(g), [])
        spec = importlib.util.spec_from_file_location('exit129_door', BUILD / '__init__.py')
        door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(door)
        sys.path.insert(0, str(BUILD / 'tests'))
        import wf_test_isolation
        wf_test_isolation.install(door)
        with unittest.mock.patch.dict(os.environ, self.env, clear=True):
            self.assertIsNone(door._validation_error(g))
            saved = door.act_save({'name': 'exit129', 'graph': g})
            self.assertNotIn('error', saved, saved)
            for ref in ('missing', 'work_gate', 7, None):
                bad = copy.deepcopy(g)
                bad['nodes'].append({'id': 'work_gate', 'type': 'gate', 'question': 'q'})
                bad['on_exit'] = ref
                err = door._validation_error(bad)
                self.assertTrue(err, bad)
                self.assertIn('on_exit', json.dumps(err))
                self.assertIn('error', door.act_save({'name': 'bad-exit129', 'graph': bad}))
                self.assertIn('error', door.act_run({'graph': bad, 'dry_run': True}))
        old = {'name': 'old', 'nodes': [g['nodes'][0]]}
        self.assertEqual(wfcommon.validate_graph_full(old), [])
        for kind in ('echo', 'join', 'gate'):
            bad = copy.deepcopy(g)
            bad['nodes'][1] = {'id': 'post', 'type': kind}
            self.assertTrue(wfcommon.structural_graph_errors(bad))
        bad = copy.deepcopy(g)
        bad['nodes'][1]['fanout'] = {'items': [1], 'goal': 'exit'}
        self.assertTrue(wfcommon.structural_graph_errors(bad))
        bad = copy.deepcopy(g)
        bad['nodes'][0]['after'] = ['post']
        self.assertTrue(wfcommon.structural_graph_errors(bad))

    def test_done_failed_stopped_inputs_once(self):
        for status in ('done', 'failed', 'stopped'):
            with self.subTest(status=status):
                r = self.make(self.graph('FAIL129' if status == 'failed' else 'OK129'), status)
                if status == 'stopped':
                    (r / 'stop.request').write_text('1')
                self.drive(r)
                facts = self.assert_exit(r, status, ['work'] if status == 'failed' else [])
                self.assertEqual(facts['error_classes'], {'work': 'config_input'} if status == 'failed' else {})
                receipt = (r / 'on_exit_receipt.md').read_bytes()
                self.drive(r)
                self.assertEqual(len(self.events(r, 'on_exit.spawned')), 1)
                self.assertEqual(len(self.events(r, 'on_exit.finished')), 1)
                self.assertEqual((r / 'on_exit_receipt.md').read_bytes(), receipt)
                self.assertEqual(len(list((r / 'logs').glob('post.a*.prompt.md'))), 1)

    def test_exit_failure_does_not_poison_done_or_stopped(self):
        for status in ('done', 'stopped'):
            with self.subTest(status=status):
                r = self.make(self.graph(exit_goal='DIE_EXIT129'), status)
                if status == 'stopped':
                    (r / 'stop.request').write_text('1')
                self.drive(r)
                self.assertEqual(json.loads((r / 'runner_exit.json').read_text())['reason'], status)
                self.assertEqual(wfcommon.run_state(r)['status'], status)
                self.assertEqual(wfcommon.run_state(r)['failed_nodes'], [])
                self.assertEqual(json.loads((r / 'nodes/post.json').read_text())['status'], 'failed')
                self.assertTrue((r / 'on_exit_receipt.md').is_file())
                self.drive(r)
                self.assertEqual(len(self.events(r, 'on_exit.spawned')), 1)

    def test_crash_receipt_on_respawn_preserves_original_verdict(self):
        r = self.make()
        graph = json.loads((r / 'graph.json').read_text())
        prior = {'reason': 'crashed: RuntimeError: fixture',
                 'graph_fingerprint': wfcommon.graph_fingerprint(graph),
                 'fp_rule_version': wfcommon.FP_RULE_VERSION}
        (r / 'runner_exit.json').write_text(json.dumps(prior))
        self.drive(r)
        self.assert_exit(r, 'crashed')
        self.assertEqual(json.loads((r / 'runner_exit.json').read_text()), prior)
        self.assertFalse((r / 'nodes/work.json').exists())
        self.drive(r)
        self.assertEqual(len(self.events(r, 'on_exit.spawned')), 1)
        self.assertEqual(json.loads((r / 'runner_exit.json').read_text()), prior)

    def test_interrupted_exit_is_harvested_not_spawned_again(self):
        r = self.make(self.graph(exit_goal='SLOW_EXIT129'))
        p = subprocess.Popen(self.command(r), env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 20
            while not (r / 'work/post/exit-ready').exists() and p.poll() is None and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertTrue((r / 'work/post/exit-ready').exists())
        finally:
            if p.poll() is None:
                p.kill()
            p.communicate(timeout=10)
        self.drive(r)
        self.assert_exit(r, 'done')
        self.assertEqual(len(list((r / 'logs').glob('post.a*.prompt.md'))), 1)
        self.drive(r)
        self.assertEqual(len(self.events(r, 'on_exit.finished')), 1)

    def test_publisher_guard_is_not_bypassed_by_exit(self):
        g = self.graph()
        g['nodes'][1]['publishes'] = True
        r = self.make(g)
        self.drive(r)
        self.assertFalse(list((r / 'logs').glob('post.a*.prompt.md')))
        self.assertEqual(json.loads((r / 'nodes/post.json').read_text())['error_class'], 'precondition')
        self.assertEqual(wfcommon.run_state(r)['status'], 'done')
        self.assertEqual(len(self.events(r, 'on_exit.finished')), 1)


# unittest.mock is explicitly imported for standalone Python as well as pytest.
import unittest.mock
if __name__ == '__main__':
    unittest.main()
