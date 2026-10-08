#!/usr/bin/env python3
"""Real runner admission: amendments made during a full-seat wait win."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf


class SeatAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wf-seat-admission-")
        self.home = Path(self.tmp.name)
        self.run_dirs = self.home / "runs"
        self.seats = self.home / "seats"
        self.capture = self.home / "children.jsonl"
        self.launcher = self.home / "child"
        self.launcher.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "prompt = Path(args[args.index('--query-file') + 1]).read_text()\n"
            "row = {'prompt': prompt, 'efp': os.environ['HERMES_WF_NODE_EFP']}\n"
            "with open(os.environ['ADMISSION_CAPTURE'], 'a') as f:\n"
            "    f.write(json.dumps(row) + '\\n')\n"
            "print('```json\\n{\"result\": \"ok\"}\\n```', flush=True)\n"
        )
        self.launcher.chmod(0o755)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(('WF_', 'HERMES_WF_', 'FAKE_'))}
        self.env.update(HERMES_HOME=str(self.home), WF_RUNS_ROOT=str(self.run_dirs),
                        WF_SEATS_DIR=str(self.seats), ADMISSION_CAPTURE=str(self.capture),
                        WORKFLOW_MAX_SEATS="2")
        self.tickets = [wf._seat_acquire(self.seats, f"holder-{i}", 2, 2)
                        for i in range(2)]
        self.assertTrue(all(isinstance(t, Path) and t.exists() for t in self.tickets))
        self.proc = None
        self.log = None

    def tearDown(self):
        for t in self.tickets:
            wf._seat_release(t)
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        if self.log is not None:
            self.log.close()
        self.assertEqual(list(self.seats.glob('*.json')), [], 'seat tickets leaked')
        self.tmp.cleanup()

    def rows(self, path):
        return [json.loads(s) for s in path.read_text().splitlines() if s.strip()] if path.exists() else []

    def graph(self, fanout=False, ancestor=False):
        node = {'id': 'work', 'type': 'agent', 'goal': 'OBSOLETE', 'timeout': 10}
        if fanout:
            node['fanout'] = {'items': ['a', 'b'], 'goal': 'OBSOLETE {item}'}
        nodes = [node]
        if ancestor:
            nodes = [{'id': 'root', 'type': 'echo', 'output': {'value': 'OBSOLETE'}},
                     {'id': 'parent', 'type': 'echo', 'after': ['root'], 'output': {'value': 'stable'}},
                     {**node, 'goal': 'stable', 'after': ['parent']}]
            if fanout:
                nodes[-1]['fanout']['goal'] = 'stable {item}'
        return {'name': 'admission', 'nodes': nodes}

    def start(self, graph, count=1):
        self.run_dir = self.run_dirs / 'admission'
        (self.run_dir / 'nodes').mkdir(parents=True)
        (self.run_dir / 'gates').mkdir()
        self.amend(graph, restart=False)
        (self.run_dir / 'run.json').write_text(json.dumps({
            'hermes_bin': str(self.launcher), 'max_seats': 2, 'concurrency': 2,
            'node_timeout': 10, 'first_message_s': 0, 'retry_budget': 0,
        }))
        self.log = (self.home / 'runner.log').open('w')
        self.proc = subprocess.Popen([sys.executable, str(ROOT / 'wf.py'), 'run', self.run_dir.name],
                                     env=self.env, stdout=self.log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            waits = [r for r in self.rows(self.run_dir / 'events.jsonl')
                     if r.get('event') == 'seat.wait' and r.get('node') == 'work']
            if len(waits) >= count:
                break
            self.assertIsNone(self.proc.poll(), 'runner exited before waiting')
            time.sleep(.02)
        else:
            self.fail('runner did not queue all old definitions')
        self.assertEqual(self.rows(self.capture), [], 'child launched while all seats held')

    def amend(self, graph, restart=True):
        tmp = self.run_dir / 'graph.json.tmp'
        tmp.write_text(json.dumps(graph))
        tmp.replace(self.run_dir / 'graph.json')
        if restart:
            (self.run_dir / 'restart.request').touch()

    def finish(self):
        for t in self.tickets:
            wf._seat_release(t)
        self.tickets.clear()
        self.assertEqual(self.proc.wait(timeout=15), 0,
                         (self.home / 'runner.log').read_text())
        self.assertEqual(list(self.seats.glob('*.json')), [], 'admission leaked a ticket')
        return self.rows(self.capture)

    def test_singleton_replacement(self):
        old = self.graph()
        self.start(old)
        current = copy.deepcopy(old)
        current['nodes'][-1]['goal'] = 'CURRENT'
        self.amend(current)
        children = self.finish()
        self.assertFalse(any('OBSOLETE' in r['prompt'] for r in children), children)
        self.assertEqual(len(children), 1, children)
        self.assertIn('CURRENT', children[0]['prompt'])
        byid = {n['id']: n for n in current['nodes']}
        expected = wf.efp(byid, byid['work'])
        self.assertEqual(children[0]['efp'], expected)
        rec = json.loads((self.run_dir / 'nodes' / 'work.json').read_text())
        self.assertEqual((rec['status'], rec['efp']), ('done', expected))


if __name__ == '__main__':
    unittest.main(verbosity=2)
