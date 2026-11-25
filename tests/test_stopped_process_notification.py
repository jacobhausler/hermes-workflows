#!/usr/bin/env python3
"""WOF's persisted stop lineage policy, through the registered hook."""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def test_stop_notification(root):
    os.environ['WF_RUNS_ROOT'] = str(root)
    os.environ['HERMES_HOME'] = str(root / 'home')
    spec = importlib.util.spec_from_file_location('workflow_door', ROOT / '__init__.py')
    assert spec is not None and spec.loader is not None
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    hook = dict(door._hook_surface())['pre_process_notification']
    run = root / 'sample-run'
    run.mkdir()
    old = 'wf:sample-run:worker:deadbeef.abcdef'
    new = 'wf:sample-run:worker:deadbeef.123456'

    def append(file, row):
        with (run / file).open('a') as out:
            out.write(json.dumps(row) + '\n')

    def spawn(skey, ts, **fields):
        append('spawn-ledger.jsonl', dict(skey=skey, ts=ts, role='child', purpose='workflow-runner', **fields))

    def notify(title):
        return asyncio.run(hook(session_title=title))

    spawn(old, '2026-11-24T20:00:00+00:00')
    assert notify(old + '#a0') is None
    (run / 'stop.request').touch()
    assert notify(old + '#a0') == {'action': 'drop'}, 'notice escaped the pending stop'
    append('events.jsonl', dict(event='run.stopped', ts='2026-11-24T20:01:00+00:00'))
    (run / 'stop.request').unlink()
    assert notify(old + '#a0') == {'action': 'drop'}, 'notice escaped the committed stop'
    assert notify('ordinary chat') is None
    assert notify('wf:sample-run:unowned:deadbeef.abcdef#a0') is None
    append('events.jsonl', dict(event='run.resumed', ts='2026-11-24T20:02:00+00:00'))
    spawn(new, '2026-11-24T20:03:00+00:00')
    assert notify(new + '#a0') is None, 'a manually resumed workflow lost notifications'
    assert notify(old + '#a0') == {'action': 'drop'}, 'resume re-enabled a revoked worker'

    # Real writers stamp subsecond order, so a same-second fresh dispatch stays live.
    same_second = '2026-11-24T20:03:00+00:00'
    append('events.jsonl', dict(event='run.stopped', ts=same_second, stopped_ns=1795550580100000000))
    fresh = 'wf:sample-run:worker:deadbeef.123abc'
    spawn(fresh, same_second, started_ns=1795550580200000000)
    assert notify(fresh + '#a0') is None
    assert notify(new + '#a0') == {'action': 'drop'}
    print('PASS: pending/committed stop, exact ownership, fresh dispatch after resume')


if __name__ == '__main__':
    with TemporaryDirectory() as directory:
        test_stop_notification(Path(directory))
