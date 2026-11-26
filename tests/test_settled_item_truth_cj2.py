"""bd_2026-11-25-cj2: an item settled BEFORE any aggregate exists binds its
recorded chat to the item's OWN committed record — one request-local decision.

Red at ca5f30f9 (replayed at c8b9ffa3; the independent event-boundary witness is
receipts/ship20-recovery/cj2-event-boundary-c8b9ffa3.Lrd56n/source-only.log):
the real runner commits item `#a1` done and journals `item.finished` while the
parked sibling keeps the aggregate unpublished. The response publishes the
settled chip (event branch) but the recorded-chat binding still rides the
metrics fold captured before the correction — so the done chip opens the
schema-invalid `#a0`. The displayed execution moved before the aggregate did;
the chat must move with it, from the same provenance that certified the settle.

The law pinned here: for a fan-out item projected while NO certified aggregate
is published, the current chat joins the item's own committed record — the full
recorded title (skey + the attempt it names, suffix included) validated by the
existing published-revision validity law — against that record's child-home
session rows, resolved at bind time (captured fold first, then one exact-title
read). A landed title binds verbatim; an absent row binds the computed
absence — explicit unavailable, ZERO host effects, never the superseded chat.
A claimless record gains no claim and the documented last-entry law stands.
The published-aggregate branch is untouched. Timeline events and the raw
log/facts contract ride independently of navigation, and the parked sibling's
pending chip makes no call.

Driven through the real seams: the real `wf.py run` CLI (only the model child
is the offline stand-in below, persisting REAL sessions rows under the exact
`--continue` title the runner supplies), the real dashboard `_view` interleaved
at the actual metrics fold and the actual `_events` read, and the real NodePanel
render/click through the shipped plugin module (test-only visibility shim).
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ok = 0


def sid(index, attempt):
    return 'local-' + hashlib.sha256(f'truth:{index}:{attempt}'.encode()).hexdigest()


CHILD = r'''#!/usr/bin/env python3
import hashlib, json, os, sqlite3, sys, time
from pathlib import Path
out = Path(os.environ['CJ2_TRUTH_PROBE'])
if '--continue' not in sys.argv:
    raise SystemExit(2)
title = sys.argv[sys.argv.index('--continue') + 1]
key, attempt = title.rsplit('#a', 1)
index = int(key.split(':')[-2])
sid = 'local-' + hashlib.sha256(f'truth:{index}:{attempt}'.encode()).hexdigest()
with sqlite3.connect(out / 'home' / 'state.db') as db:
    row = (sid, title, 'fixture', 1, 1, 0, 0, 1, 1, 0, int(attempt) + 1, 1, 'fixture', 2, 0)
    db.execute('insert into sessions values (' + ','.join('?' for _ in row) + ')', row)
if index == 1:
    (out / 'quartz-ready').touch()
    deadline = time.monotonic() + 30
    while not (out / 'quartz-release').exists():
        if time.monotonic() > deadline:
            raise TimeoutError('Quartz was not released')
        time.sleep(.02)
    answer = {'result': f'index {index} attempt {attempt} accepted'}
elif index == 0 and attempt == '0':
    (out / 'old-ready').touch()
    deadline = time.monotonic() + 20
    while not (out / 'release').exists():
        if time.monotonic() > deadline:
            raise TimeoutError('review did not release the first transport')
        time.sleep(.02)
    answer = {'intentionally_missing_required_result': True}
else:
    answer = {'result': f'index {index} attempt {attempt} accepted'}
print('```json\n' + json.dumps(answer) + '```', flush=True)
'''

PROBE = r"""
  {
    // bd_2026-11-25-cj2 settled-before-aggregate replay — the ACTUAL NodePanel.
    // STRICT allowed sets: every observation pins the rendered label, the
    // exposed StatusDot outcome, the exact selection index and the WHOLE SDK
    // effect array. The superseded attempt's id is never an allowed
    // destination, and an unlanded exact title must paint zero effects.
    const replay = JSON.parse(process.env.CJ2_TRUTH_PANELS)
    const mat = n => n == null || typeof n !== 'object' ? n :
      Array.isArray(n) ? n.map(mat) :
      typeof n.type === 'function' ? mat(n.type(n.props)) :
      { ...n, props: { ...n.props, children: mat(n.props?.children) } }
    const tones = { good: 'done', bad: 'failed', muted: 'pending' }
    const bad = []
    for (const o of replay) {
      remount()
      globalThis.__calls.length = 0
      globalThis.__si = 0
      globalThis.__effects = []
      markNavFocus(null) // one observation at a time: the one-shot token never rides over
      $selNode.set({ runId: o.view.id, nodeId: o.node })
      mod.$fanItem.set(null)
      const tree = mat(mod.NodePanel({ detail: o.view }))
      const chips = buttons(tree).filter(p => Array.isArray(p.children)
        && p.children[0]?.type === 'StatusDot'
        && textOf(p.children[1]).trim().split(/\s+/)[0] === o.label)
      if (!chips.length) bad.push({ name: o.name, reason: 'no selectable status-bearing chip' })
      chips[0].onClick({ stopPropagation() {} })
      const sel = mod.$fanItem.get()
      const tree2 = mat(mod.NodePanel({ detail: o.view }))
      const painted = textOf(chips[0].children).trim().split(/\s+/)[0]
      const outcome = tones[chips[0].children[0].props.tone]
      const link = buttons(tree2).find(x => x.children === 'open recorded chat')
      if (link) await link.onClick({ preventDefault() {}, stopPropagation() {}, currentTarget: {} })
      const result = { painted, outcome, unavailable: textOf(tree2).includes('Session unavailable'),
                       calls: [...globalThis.__calls] }
      if (JSON.stringify(sel) !== JSON.stringify({ runId: o.view.id, nodeId: o.node, index: o.index }))
        bad.push({ name: o.name, reason: 'selection moved off the exact index', sel })
      const opens = result.calls.filter(c => c[0] === 'openSession')
      const extras = result.calls.filter(c => ['submit', 'insert', 'notify', 'navigate'].includes(c[0]))
      const hit = o.allowed.some(x => JSON.stringify(x) === JSON.stringify(result))
      if (!hit || extras.length || opens.length > 1)
        bad.push({ name: o.name, allowed: o.allowed, got: result, extras, opens })
      console.log('CJ2-TRUTH-OBS ' + JSON.stringify({ name: o.name, ...result }))
    }
    $selNode.set(null)
    mod.$fanItem.set(null)
    assert.deepEqual(bad, [], `${bad.length} panel observation(s) deviate — ${JSON.stringify(bad)}`)
  }
"""


def check(cond, name):
    global ok
    if not cond:
        print('FAIL ' + name)
        raise SystemExit(1)
    print('PASS ' + name)
    ok += 1


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tmp = tempfile.mkdtemp(prefix='cj2-truth-')
try:
    home = Path(tmp) / 'out' / 'home'
    runs = Path(tmp) / 'runs'
    out = Path(tmp) / 'out'
    out.mkdir()
    home.mkdir()
    runs.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('HERMES_', 'WF_', 'FAKE_'))}
    env.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
               TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE='1', CJ2_TRUTH_PROBE=str(out),
               WORKFLOW_MAX_SEATS='0')
    os.environ.clear()
    os.environ.update(env)
    sys.path.insert(0, str(ROOT))
    with sqlite3.connect(home / 'state.db') as c:
        c.execute('create table sessions (id text primary key, title text, model text, '
                  'input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, '
                  'api_call_count int, tool_call_count int, estimated_cost_usd real, started_at real, '
                  'last_activity_at real, last_activity_description text, ended_at real, expiry_finalized int)')
    api = load('cj2_truth_api', ROOT / 'dashboard' / 'plugin_api.py')
    wc = api._workflow_common()

    r = runs / 'settled-truth'
    (r / 'nodes').mkdir(parents=True)
    child = out / 'hermes-child'
    child.write_text(CHILD)
    child.chmod(0o755)
    (r / 'run.json').write_text(json.dumps({'hermes_bin': str(child), 'item_concurrency': 1}))
    schema = {'type': 'object', 'properties': {'result': {'type': 'string'}}, 'required': ['result']}
    (r / 'graph.json').write_text(json.dumps({'name': r.name, 'nodes': [
        {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'timeout': 30,
         'fanout': {'items': ['Amber', 'Quartz'], 'goal': 'review {item}', 'schema': schema}}]}))

    def readrec(stem):
        return json.loads((r / 'nodes' / f'{stem}.json').read_text())

    engine_log = (out / 'engine.log').open('w')
    proc = subprocess.Popen([sys.executable, '-B', str(ROOT / 'wf.py'), 'run', r.name],
                            stdout=engine_log, stderr=subprocess.STDOUT, env=env)
    try:
        deadline = time.monotonic() + 12
        while not (out / 'old-ready').is_file():
            assert proc.poll() is None and time.monotonic() < deadline, 'first spawn never reached transport'
            time.sleep(.02)
        early = readrec('review.0')
        old_key = early['skey']
        assert early['status'] == 'running' and early['attempt'] == 0, early
        assert not (r / 'nodes' / 'review.json').exists()

        real_metrics = wc.run_child_metrics
        real_events = api._events

        def observe_fold(*args, **kwargs):
            fold = real_metrics(*args, **kwargs)
            assert fold[old_key]['_session_current'] == sid(0, 0), fold
            assert sid(0, 1) not in fold[old_key]['session_ids']
            return fold

        def settle_before_events(*args, **kwargs):
            assert not (r / 'nodes' / 'review.json').exists()
            (out / 'release').touch()
            deadline = time.monotonic() + 12
            while True:
                events = real_events(*args, **kwargs)
                done = [e for e in events if e.get('event') == 'item.finished'
                        and e.get('node') == 'review' and e.get('index') == 0]
                if done and (out / 'quartz-ready').exists():
                    break
                assert proc.poll() is None and time.monotonic() < deadline, events
                time.sleep(.02)
            assert len(done) == 1 and done[0]['status'] == 'done' and done[0]['skey'] == old_key, done
            late = readrec('review.0')
            assert late['spawn'] == 1 and late['skey'] == old_key and late['status'] == 'done', late
            assert not (r / 'nodes' / 'review.json').exists()  # the sibling is still parked
            return events

        with patch.object(wc, 'run_child_metrics', side_effect=observe_fold), \
                patch.object(api, '_events', side_effect=settle_before_events):
            mixed = api._view(r, full=True)
        # Still parked: every pre-aggregate read below happens while the
        # sibling holds the aggregate back — the displayed execution and its
        # chat must already agree BEFORE any certified aggregate exists.
        check(mixed['graph'] == json.loads((r / 'graph.json').read_text()),
              'setup: one unchanged revision rides the racing response')
        check([e for e in mixed['events'] if e.get('event') == 'item.started'] and
              [e for e in mixed['events'] if e.get('event') == 'item.finished'
               and e.get('node') == 'review' and e.get('index') == 0],
              'timeline events ride the racing response verbatim — navigation binds nothing away')
        check(readrec('review.0').get('log_path') and readrec('review.0').get('spawn') == 1,
              'raw facts contract intact: the committed item record names attempt 1 with its own log path')
        check(mixed['nodes']['review']['item_metrics'].get('1') is None,
              'the parked pending sibling gains no fabricated destination')
        check(mixed['nodes']['review']['item_metrics'][0].get('session_current') == sid(0, 1),
              'settled-before-aggregate: the done chip binds the ACCEPTED #a1, never the superseded #a0')
        check(sid(0, 0) in mixed['nodes']['review']['item_metrics'][0]['session_ids'],
              'the superseded attempt stays inspectable in history')

        def item(view, i):
            return view['nodes']['review']['item_metrics'][i]

        # Absence while the aggregate is still unpublished: delete ONLY the
        # exact #a1 row (#a0 survives; the sibling and its row are untouched).
        with sqlite3.connect(home / 'state.db') as c:
            assert c.execute('delete from sessions where id=? and title=?',
                             (sid(0, 1), f'{old_key}#a1')).rowcount == 1
            survivors = c.execute('select id,title from sessions order by title').fetchall()
        assert (sid(0, 0), f'{old_key}#a0') in survivors
        assert sid(1, 0) in {i for i, _ in survivors}
        assert not (r / 'nodes' / 'review.json').exists()
        mixed_absent = api._view(r, full=True)
        check(item(mixed_absent, 0).get('session_current') is None,
              'computed absence before the aggregate: the expunged exact title binds None — '
              'never a walk-back to the superseded #a0')
        with sqlite3.connect(home / 'state.db') as c:
            c.execute('insert into sessions values (' + ','.join('?' for _ in range(15)) + ')',
                      (sid(0, 1), f'{old_key}#a1', 'fixture', 1, 1, 0, 0, 1, 1, 0, 2, 1, 'fixture', 2, 0))
        mixed_landed = api._view(r, full=True)
        check(item(mixed_landed, 0).get('session_current') == sid(0, 1),
              'the same pre-aggregate read converges to #a1 once its row is visible again')
    finally:
        (out / 'release').touch()
        (out / 'quartz-release').touch()
        if proc.poll() is None:
            try:
                proc.wait(timeout=25)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        engine_log.close()

    assert proc.returncode == 0, proc.returncode
    fresh = api._view(r, full=True)
    aggregate = readrec('review')
    check(fresh['status'] == 'done' and aggregate['status'] == 'done',
          'setup: the released sibling settles the real aggregate')
    check(item(fresh, 0)['session_current'] == sid(0, 1),
          'after the aggregate exists the same settled chat still opens the exact #a1')
    check(item(fresh, 1)['session_current'] == sid(1, 0),
          'the untouched sibling opens its own exact session')
    with sqlite3.connect(home / 'state.db') as c:
        assert c.execute('delete from sessions where id=? and title=?',
                         (sid(0, 1), f'{old_key}#a1')).rowcount == 1
    deleted = api._view(r, full=True)
    check(item(deleted, 0)['session_current'] is None,
          'aggregate-era absence stays the computed absence (unchanged branch)')

    def open_expect(s):
        return {'painted': None, 'outcome': 'done', 'unavailable': False,
                'calls': [['openSession', s, '{"intent":"in-place"}']]}

    closed = {'painted': None, 'outcome': 'done', 'unavailable': True, 'calls': []}
    observations = []

    def panel(name, view, index, label, outcome, allowed):
        observations.append({'name': name, 'view': view, 'node': 'review', 'index': index,
                             'label': label,
                             'allowed': [dict(allowed, outcome=outcome, painted=label)]})

    panel('T1-settled-before-aggregate-opens-accepted-attempt', mixed, 0, 'Amber', 'done',
          open_expect(sid(0, 1)))
    panel('T2-parked-sibling-pending-makes-no-call', mixed, 1, 'Quartz', 'pending', closed)
    panel('T3-absence-before-aggregate-zero-effects', mixed_absent, 0, 'Amber', 'done', closed)
    panel('T4-landed-pre-aggregate-converges', mixed_landed, 0, 'Amber', 'done',
          open_expect(sid(0, 1)))
    panel('T5-settled-aggregate-opens-accepted-attempt', fresh, 0, 'Amber', 'done',
          open_expect(sid(0, 1)))
    panel('T6-settled-sibling-opens-own', fresh, 1, 'Quartz', 'done', open_expect(sid(1, 0)))
    panel('T7-aggregate-absence-explicit-unavailable', deleted, 0, 'Amber', 'done', closed)
    panel('T8-aggregate-absence-sibling-still-opens', deleted, 1, 'Quartz', 'done',
          open_expect(sid(1, 0)))

    work = Path(tmp) / 'probe'
    (work / 'desktop').mkdir(parents=True)
    (work / 'tests').mkdir()
    shutil.copyfile(ROOT / 'desktop/plugin.js', work / 'desktop/plugin.js')
    shim = (ROOT / 'tests/test_stored_session_nav.mjs').read_text()
    js_seam = '''.replaceAll("'react/jsx-runtime'", JSON.stringify(pathToFileURL(jsxPath).href)))'''
    assert shim.count(js_seam) == 1
    shim = shim.replace(js_seam, js_seam[:-1] + ' + "\\nexport { NodePanel, $fanItem }\\n")')
    seam = '  // -- 1b. fan-out scoping'
    assert shim.count(seam) == 1
    driver = work / 'tests/probe.mjs'
    driver.write_text(shim.replace(seam, PROBE + seam))
    proc_panel = subprocess.run(['node', '--experimental-strip-types', str(driver)],
                                env={**env, 'CJ2_TRUTH_PANELS': json.dumps(observations)},
                                timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc_panel.stdout)
    sys.stderr.write(proc_panel.stderr)
    obs = [json.loads(l[len('CJ2-TRUTH-OBS '):]) for l in proc_panel.stdout.splitlines()
           if l.startswith('CJ2-TRUTH-OBS ')]
    check(proc_panel.returncode == 0 and [v['name'] for v in obs] == [o['name'] for o in observations],
          f'panel path: every one of the {len(observations)} observations renders/clicks '
          'exactly as the projection declares')
    for v in obs:
        opens = [c for c in v['calls'] if c[0] == 'openSession']
        check(len(opens) <= 1 and all(c[2] == '{"intent":"in-place"}' for c in opens),
              f"{v['name']}: at most ONE openSession with the exact union options")
    print(f"\nALL PASS ({ok}) test_settled_item_truth_cj2 — one item projection decides together: "
          "a settled-before-aggregate chip binds its own record's exact attempt (landed row opens "
          "it once; an expunged row is an explicit unavailable with zero effects), and the "
          "published-aggregate branch is untouched.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
