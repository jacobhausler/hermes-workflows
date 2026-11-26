"""bd_2026-11-25-cj2: a same-skey schema correction rebinds the recorded chat to
the EXACT ATTEMPT the published row names — skey membership is neither a claim
nor proof of a matching attempt.

The exact-head challenge replay (receipts/ship20-recovery/
cj2-exact-attempt-e7d521c6.OL0zC8/candidate.log, red AT e7d521c6ec67300e550dcfc68646bcf591e06c8e)
holds the graph, the item label and the skey all fixed and moves only the
attempt INSIDE the skey: the runner's schema correction recurses under the same
skey at `#a1` (wf.py run_child), the aggregate certifies `#a1` done, and the
NodePanel opens the schema-invalid `#a0`. The era/efp law cannot see this (one
definition, one generation key), and the fold observed only `#a0` before the
correction landed — so every authority the response CAN name is unchanged while
the destination moved.

The law pinned here: for a projected fan-out item under a published certified
aggregate, the current chat is the join of the published row's own recorded
title (`skey` + the attempt it names, suffix included) against the home-scoped
session rows this read already folded — one in-memory join, no second fold, no
graph re-walk. A racing mid-view response either binds the published attempt or
fails CLOSED (unavailable, zero host calls); it NEVER opens the superseded
attempt. The settled read converges to the published attempt exactly; prior
attempts stay inspectable in session_ids; history and cumulative counters are
untouched by a binding. A row with no recorded title (legacy claimless) gains no
claim — the documented last-entry law stands there.

Driven through the real seams: the real `wf.py run` CLI (only the model child is
the offline stand-in below, which persists REAL sessions rows under the exact
`--continue` title the runner supplies), the real dashboard `_view` interleaved
at the actual metrics fold, and the actual NodePanel render/click through the
shipped plugin module (only test-only visibility differs — the same driver
seam the sibling turnover test uses).
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
    return 'local-' + hashlib.sha256(f'exact:{index}:{attempt}'.encode()).hexdigest()


CHILD = r'''#!/usr/bin/env python3
import hashlib, json, os, sqlite3, sys, time
from pathlib import Path
out = Path(os.environ['CJ2_EXACT_PROBE'])
if '--continue' not in sys.argv:
    raise SystemExit(2)
title = sys.argv[sys.argv.index('--continue') + 1]
key, attempt = title.rsplit('#a', 1)
index = int(key.split(':')[-2])
sid = 'local-' + hashlib.sha256(f'exact:{index}:{attempt}'.encode()).hexdigest()
with sqlite3.connect(out / 'home' / 'state.db') as db:
    row = (sid, title, 'fixture', 1, 1, 0, 0, 1, 1, 0, int(attempt) + 1, 1, 'fixture', 2, 0)
    db.execute('insert into sessions values (' + ','.join('?' for _ in row) + ')', row)
if index == 0 and attempt == '0':
    (out / 'old-ready').touch()
    deadline = time.monotonic() + 20
    while not (out / 'release').is_file():
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
    // bd_2026-11-25-cj2 exact-attempt replay — the ACTUAL NodePanel. The
    // observation pins the rendered label, the exposed StatusDot outcome and
    // the WHOLE SDK effect array against an allowed set; the superseded
    // attempt's id is never an allowed destination.
    const replay = JSON.parse(process.env.CJ2_EXACT_PANELS)
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
        && [o.label, ...(o.alternatives ?? [])].includes(textOf(p.children[1]).trim().split(/\s+/)[0]))
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
      console.log('CJ2-EXACT-OBS ' + JSON.stringify({ name: o.name, ...result }))
    }
    $selNode.set(null)
    mod.$fanItem.set(null)
    assert.deepEqual(bad, [], `${bad.length} panel observation(s) deviate — ${JSON.stringify(bad)}`)
  }
"""


def check(cond, name):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        raise SystemExit(1)
    ok += 1


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tmp = tempfile.mkdtemp(prefix='cj2-exact-')
try:
    home = Path(tmp) / 'out' / 'home'
    runs = Path(tmp) / 'runs'
    out = Path(tmp) / 'out'
    out.mkdir()
    home.mkdir()
    runs.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('HERMES_', 'WF_', 'FAKE_'))}
    env.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
               TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE='1', CJ2_EXACT_PROBE=str(out),
               WORKFLOW_MAX_SEATS='0')
    os.environ.clear()
    os.environ.update(env)
    sys.path.insert(0, str(ROOT))
    with sqlite3.connect(home / 'state.db') as c:
        c.execute('create table sessions (id text primary key, title text, model text, '
                  'input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, '
                  'api_call_count int, tool_call_count int, estimated_cost_usd real, started_at real, '
                  'last_activity_at real, last_activity_description text, ended_at real, expiry_finalized int)')
    api = load('cj2_exact_api', ROOT / 'dashboard' / 'plugin_api.py')
    wc = api._workflow_common()

    r = runs / 'exact-attempt'
    (r / 'nodes').mkdir(parents=True)
    child = out / 'hermes-child'
    child.write_text(CHILD)
    child.chmod(0o755)
    (r / 'run.json').write_text(json.dumps({'hermes_bin': str(child), 'item_concurrency': 1}))
    schema = {'type': 'object', 'properties': {'result': {'type': 'string'}}, 'required': ['result']}
    (r / 'graph.json').write_text(json.dumps({'name': r.name, 'nodes': [
        {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'timeout': 30,
         'fanout': {'items': ['Amber', 'Quartz'], 'goal': 'review {item}', 'schema': schema}}]}))

    engine_log = (out / 'engine.log').open('w')
    proc = subprocess.Popen([sys.executable, '-B', str(ROOT / 'wf.py'), 'run', r.name],
                            stdout=engine_log, stderr=subprocess.STDOUT, env=env)
    try:
        deadline = time.monotonic() + 12
        while not (out / 'old-ready').is_file():
            assert proc.poll() is None and time.monotonic() < deadline, 'first spawn never reached transport'
            time.sleep(.02)
        early = json.loads((r / 'nodes' / 'review.0.json').read_text())
        old_key = early['skey']
        assert early['status'] == 'running' and early['attempt'] == 0, early
        assert not (r / 'nodes' / 'review.json').exists()

        real_metrics = wc.run_child_metrics

        def settle_after_fold(*args, **kwargs):
            fold = real_metrics(*args, **kwargs)
            assert fold[old_key]['_session_current'] == sid(0, 0), fold[old_key]
            assert sid(0, 1) not in fold[old_key]['session_ids']
            (out / 'release').touch()
            assert proc.wait(timeout=25) == 0
            return fold

        with patch.object(wc, 'run_child_metrics', side_effect=settle_after_fold):
            mixed = api._view(r, full=True)
    finally:
        (out / 'release').touch()
        if proc.poll() is None:
            try:
                proc.wait(timeout=6)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        engine_log.close()
    fresh = api._view(r, full=True)

    aggregate = json.loads((r / 'nodes' / 'review.json').read_text())
    late = json.loads((r / 'nodes' / 'review.0.json').read_text())
    rows = aggregate['output']['all_results']
    with sqlite3.connect(home / 'state.db') as c:
        sessions = dict(c.execute('select id,title from sessions').fetchall())

    def item(view, i):
        return view['nodes']['review']['item_metrics'][i]

    check(fresh['status'] == 'done' and aggregate['status'] == 'done',
          'setup: the real runner exits 0 and the real aggregate certifies done')
    check(rows[0]['skey'] == late['skey'] == old_key and 'skey' in rows[0],
          'setup: the whole graph is unchanged and the published row names the SAME skey')
    check(rows[0].get('attempt') == 1 or rows[0].get('spawn') == 1,
          'setup: the published row names attempt 1 — the schema correction advanced '
          'the attempt INSIDE the skey')
    check(sessions.get(sid(0, 0)) == f'{old_key}#a0' and sessions.get(sid(0, 1)) == f'{old_key}#a1',
          'setup: SQLite holds both exact distinct titles under the one skey')
    check(rows[0]['status'] == 'done' and rows[0]['output'] == {'result': 'index 0 attempt 1 accepted'},
          'the published outcome is the ACCEPTED correction, not the invalid first answer')
    check(mixed['graph'] == fresh['graph'], 'setup: one revision across the racing and settled reads')
    bound = item(mixed, 0).get('session_current', 'ABSENT')
    check(bound in (sid(0, 1), None, 'ABSENT'),
          'the racing response binds the published attempt or fails closed — the superseded '
          '#a0 is never the destination of a done row')
    check(item(fresh, 0)['session_current'] == sid(0, 1),
          'the settled response opens the exact published attempt #a1')
    check(sid(0, 0) in item(fresh, 0)['session_ids'],
          'the superseded attempt stays inspectable in history')
    check(item(fresh, 1)['session_current'] == sid(1, 0),
          'the untouched sibling opens its own exact session')

    def open_expect(s):
        return {'painted': None, 'outcome': 'done', 'unavailable': False,
                'calls': [['openSession', s, '{"intent":"in-place"}']]}

    closed = {'painted': 'Amber', 'outcome': 'done', 'unavailable': True, 'calls': []}
    observations = []

    def panel(name, view, index, label, allowed):
        observations.append({'name': name, 'view': view, 'node': 'review', 'index': index,
                             'label': label, 'allowed': allowed})

    panel('X1-mixed-never-superseded', mixed, 0, 'Amber',
          [dict(closed, painted='Amber'), dict(open_expect(sid(0, 1)), painted='Amber')])
    panel('X2-fresh-opens-published-attempt', fresh, 0, 'Amber',
          [dict(open_expect(sid(0, 1)), painted='Amber')])
    panel('X3-fresh-sibling-opens-own', fresh, 1, 'Quartz',
          [dict(open_expect(sid(1, 0)), painted='Quartz')])

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
    proc = subprocess.run(['node', '--experimental-strip-types', str(driver)],
                          env={**env, 'CJ2_EXACT_PANELS': json.dumps(observations)},
                          timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    obs = [json.loads(l[len('CJ2-EXACT-OBS '):]) for l in proc.stdout.splitlines()
           if l.startswith('CJ2-EXACT-OBS ')]
    check(proc.returncode == 0 and [v['name'] for v in obs] == [o['name'] for o in observations],
          f'panel path: every one of the {len(observations)} observations renders/clicks '
          'exactly as the projection declares')
    for v in obs:
        opens = [c for c in v['calls'] if c[0] == 'openSession']
        check(len(opens) <= 1 and all(c[2] == '{"intent":"in-place"}' for c in opens),
              f"{v['name']}: at most ONE openSession with the exact union options")
    print(f"\nALL PASS ({ok}) test_exact_attempt_bind_cj2 — a same-skey attempt advance "
          "rebinds the recorded chat to the exact attempt the published row names: the "
          "racing response binds it or fails closed (never the superseded #a0), and the "
          "settled response opens it once.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
