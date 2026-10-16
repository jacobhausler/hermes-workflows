#!/usr/bin/env python3
"""Tree quarantine distinguishes unreadable proof and reaps adopted children."""
import itertools
import os
import signal
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

BUILD = Path(os.environ.get('WF_TEST_BUILD') or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(BUILD))
import wf

passed = True

def check(label, good, detail):
    global passed
    print(('PASS ' if good else 'FAIL ') + label, detail, flush=True)
    passed = passed and good

# Unreadability is not evidence that any known PID is still alive. Drive each
# observation boundary through the real helper; never signal fixture PIDs.
fake_pid = 987654321
phases = (
    ('initial-empty', [], [None], 0, 0),
    ('initial-known', [fake_pid], [None], 0, 0),
    ('drain', [fake_pid], [[fake_pid], None], 1, 0),
    ('term-grace', [fake_pid], [[fake_pid], None], 0, 1),
    ('kill-proof', [fake_pid], [[fake_pid], None], 0, 0),
    ('later-proof', [fake_pid], [[fake_pid], [fake_pid], None], 0, 0),
)
for phase, known, snapshots, hold, grace in phases:
    ticks = itertools.count(0, 0.01)
    with patch.object(wf, '_proc_pids_by_pgid', side_effect=snapshots), \
         patch.object(wf, '_proc_alive', return_value=True), \
         patch.object(wf, '_reap_zombie'), \
         patch.object(wf.time, 'time', side_effect=lambda: next(ticks)), \
         patch.object(wf.time, 'sleep'), \
         patch.object(wf.os, 'kill'), patch.object(wf.os, 'killpg'):
        result = wf._tree_quiesce(known, fake_pid, hold, 1, term_grace_s=grace)
    check('unreadable ' + phase, result == ('unknown', known), result)

# A readable, still-live table retains its distinct stuck diagnostic. Empty
# and proven-dead controls prevent the label fix from weakening fail-closed.
for label, snapshots, expected in (
    ('still-live', [[fake_pid], [fake_pid]], ('stuck', [fake_pid])),
    ('already-empty', [set()], ('', [])),
    ('killed-dead', [[fake_pid], set()], ('dead', [])),
):
    alive_checks = iter([True, True, False]) if label == 'killed-dead' else itertools.repeat(label != 'already-empty')
    with patch.object(wf, '_proc_pids_by_pgid', side_effect=snapshots), \
         patch.object(wf, '_proc_alive', side_effect=lambda p: next(alive_checks)), \
         patch.object(wf, '_reap_zombie'), \
         patch.object(wf.os, 'kill'), patch.object(wf.os, 'killpg'):
        result = wf._tree_quiesce(set() if label == 'already-empty' else {fake_pid},
                                 fake_pid, 0, 0, term_grace_s=0)
    check('readable ' + label, result == expected, result)

# Exercise every caller, including unreadability that begins only AFTER the
# caller's readable pre-check. Events and terminal records must stay unknown;
# answer harvesting and retries may not mistake this for dead-or-empty.
with tempfile.TemporaryDirectory(prefix='wf-tree-unknown-') as tmp:
    for caller in ('account', 'isolate', 'final'):
        meta = {'_run': Path(tmp), 'proctree_hold_s': 0,
                'proctree_kill_proof_s': 0}
        node = {'id': 'probe'}
        source = {'status': 'done', 'pid': fake_pid, 'spawn': 2, 'attempts': 3,
                  'tree_pids': [fake_pid], 'log_path': 'probe.log',
                  'prompt_path': 'probe.prompt', 'skey': 'probe-key',
                  'attempts_log': [{'attempt': 1, 'error_class': 'timeout'}]}
        events = []
        with patch.object(wf, '_proc_pids_by_pgid', side_effect=[[fake_pid], None]), \
             patch.object(wf, '_proc_alive', return_value=True), \
             patch.object(wf, '_sidecar_live_registered', return_value=set()), \
             patch.object(wf, '_survivors', return_value=set()), \
             patch.object(wf, 'log', side_effect=lambda *a, **kw: events.append(kw)):
            if caller == 'account':
                outcome, record = wf._account_tree(meta, node, None, 2, fake_pid, set(), True) or ('none', None)
                check('account refuses unknown answer', outcome == 'fail', outcome)
            elif caller == 'isolate':
                record = wf._isolate_prior(meta, source, 'node.retrying', {'node': 'probe'})
            else:
                record = wf._final_quiesce(meta, source, 'node', {'node': 'probe'})
        assert isinstance(record, dict), (caller, record)
        check(caller + ' unknown record',
              record['status'] == 'failed' and record['tree_proof'] == 'unknown'
              and record['error_class'] == 'left_live_descendants'
              and 'proc-unreadable:' in record['error']
              and 'live process tree' not in record['error'], record)
        check(caller + ' unknown event', bool(events) and events[-1]['proof'] == 'unknown', events)
        if caller != 'account':
            check(caller + ' carries attempt evidence',
                  all(record.get(k) == source[k] for k in
                      ('attempts', 'attempts_log', 'log_path', 'prompt_path', 'skey', 'pid', 'spawn')),
                  record)

assert wf._set_subreaper(), 'Linux subreaper prerequisite'
for mode in ('kill', 'already-dead'):
    with tempfile.TemporaryDirectory(prefix='wf-tree-reap-') as tmp:
        pid_file = Path(tmp) / 'child.pid'
        parent = os.fork()
        if parent == 0:
            os.setsid()
            child = os.fork()
            if child == 0:
                time.sleep(30 if mode == 'kill' else 0.1)
                os._exit(0)
            pid_file.write_text(str(child))
            os._exit(0)
        os.waitpid(parent, 0)
        child = int(pid_file.read_text())
        try:
            if mode == 'already-dead':
                deadline = time.monotonic() + 5
                while wf._proc_alive(child) and time.monotonic() < deadline:
                    time.sleep(0.005)
                assert not wf._proc_alive(child), 'child must have exited'
            proof, stuck = wf._tree_quiesce({child}, parent, 0, 2, term_grace_s=0)
            try:
                os.kill(child, 0)
                reaped = False
            except ProcessLookupError:
                reaped = True
            good = proof == ('dead' if mode == 'kill' else '') and not stuck and reaped
            check(mode + ': adopted child absent at quarantine return', good,
                  {'proof': proof, 'stuck': stuck, 'reaped': reaped})
        finally:
            if wf._proc_alive(child):
                os.kill(child, signal.SIGKILL)
            try:
                os.waitpid(child, 0)
            except ChildProcessError:
                pass
print('RESULT', 'PASS' if passed else 'FAIL')
sys.exit(0 if passed else 1)
