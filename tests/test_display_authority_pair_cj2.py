"""bd_2026-11-25-cj2 (display authority): the displayed outcome and the chat
attempt are ONE decision — no read order can separate them.

A third leg replays an UNCHANGED-DEFINITION REDRIVE with an authentic stale
finish under the same index (the same-shape trap a raw status/id pair cannot
answer): the real runner commits old Amber as raw failed+`cancelled`, a real
redrive door admits the same-definition re-drive, the new Amber fails
`declared_failure` while the new Quartz parks and no aggregate exists — and
the racing response retains the OLD journal. One decision must answer chip
outcome, tooltip and chat together; at b445a972 this tuple was red (a neutral
cancelled chip wearing the old journal's tooltip opened the NEW failed chat,
because `session_outcome` shipped only a raw status while error_class and
tooltip rode the independently captured timeline).

The paired schedules replay the real schema-correction race twice at the real
`_events` read:

- settled-events leg: the metrics fold was captured pre-race and the response
  ships the journal AFTER the correction settled (no aggregate — the sibling
  stays parked). The done chip must open the accepted `#a1` or nothing; the
  superseded `#a0` is never a destination under a settled paint (red at
  ca5f30f9: the paint rode the new events while the chat rode the old fold).
- old-events leg: same race, but the response ships the journal captured
  BEFORE the release — the running stamp legitimately survives this response.
  An old coherent pair (running + `#a0`) or the settled pair (done + `#a1`)
  stand; a rebind under the still-painted running chip (done-chip classes
  (running + `#a1`)) does not (red at b6abba5f: the post-events rebind moved
  the chat without moving the paint).

Backend-side the same law is asserted directly: every racing response ships
`session_current` and its partner key `session_display` bound together on the
selected item's row — a COMPLETE decision (status plus the error/refusal facts
the record names), because a bare status still leaves error_class and tooltip
to a second selector. An item row without a paired decision cannot open a
chat, and the pending sibling row never appears. After the aggregate
exists the same view opens the exact settled chats; live/freshly-settled
navigation is
never blanket-suppressed. Driven through the real `wf.py run` CLI, the real
`_view`, and the actual NodePanel (test-only visibility shim over the shipped
module; the observer only clicks what it sees).
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


def sid(tag, index, attempt):
    return 'local-' + hashlib.sha256(f'pair:{tag}:{index}:{attempt}'.encode()).hexdigest()


CHILD = r'''#!/usr/bin/env python3
import hashlib, json, os, sqlite3, sys, time
from pathlib import Path
out = Path(os.environ['CJ2_PAIR_PROBE'])
if '--continue' not in sys.argv:
    raise SystemExit(2)
title = sys.argv[sys.argv.index('--continue') + 1]
key, attempt = title.rsplit('#a', 1)
index = int(key.split(':')[-2])
sid = 'local-' + hashlib.sha256(f'pair:{os.environ["CJ2_PAIR_TAG"]}:{index}:{attempt}'.encode()).hexdigest()
with sqlite3.connect(out / 'home' / 'state.db') as db:
    row = (sid, title, 'fixture', 1, 1, 0, 0, 1, 1, 0, int(attempt) + 1, 1, 'fixture', 2, 0)
    db.execute('insert into sessions values (' + ','.join('?' for _ in row) + ')', row)
if index == 1:
    (out / f'quartz-ready-{attempt}').touch()
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
    // bd_2026-11-25-cj2 display-authority pair — the ACTUAL NodePanel.
    // STRICT allowed sets pin label, visible outcome, exact selected index and
    // the WHOLE SDK effect array; a paint without its attempt's evidence may
    // render but must produce zero effects.
    const replay = JSON.parse(process.env.CJ2_PAIR_PANELS)
    const mat = n => n == null || typeof n !== 'object' ? n :
      Array.isArray(n) ? n.map(mat) :
      typeof n.type === 'function' ? mat(n.type(n.props)) :
      { ...n, props: { ...n.props, children: mat(n.props?.children) } }
    const isRunning = x => x?.type === 'span' && x.props.className?.split(' ').includes('animate-pulse')
      && x.props.style?.background === 'var(--ui-accent)'
    const tones = { good: 'done', bad: 'failed', muted: 'pending' }
    const bad = []
    for (const o of replay) {
      remount()
      globalThis.__calls.length = 0
      globalThis.__si = 0
      globalThis.__effects = []
      markNavFocus(null)
      $selNode.set({ runId: o.view.id, nodeId: o.node })
      mod.$fanItem.set(null)
      const tree = mat(mod.NodePanel({ detail: o.view }))
      const chips = buttons(tree).filter(p => Array.isArray(p.children)
        && (p.children[0]?.type === 'StatusDot' || isRunning(p.children[0]))
        && textOf(p.children[1]).trim().split(/\s+/)[0] === o.label)
      if (!chips.length) bad.push({ name: o.name, reason: 'no selectable status-bearing chip' })
      chips[0].onClick({ stopPropagation() {} })
      const sel = mod.$fanItem.get()
      const tree2 = mat(mod.NodePanel({ detail: o.view }))
      const painted = textOf(chips[0].children).trim().split(/\s+/)[0]
      // bd_2026-11-25-cj2 (display authority, complete): cancelled is muted +
      // the neutral (tertiary, unstruck) chip + the exact SOURCED tooltip —
      // declared only by cases carrying a cancelled_title witness, so the
      // historical observations keep their tuples byte-identically.
      const chipStyle = chips[0].style || {}
      const neutral = String(chipStyle.border || '').includes('var(--ui-text-tertiary)')
        && chipStyle.textDecoration === 'none'
      const outcome = isRunning(chips[0].children[0]) ? 'running'
        : (tones[chips[0].children[0].props.tone] === 'pending' && neutral
           && o.cancelled_title != null && chips[0].title === o.cancelled_title) ? 'cancelled'
        : tones[chips[0].children[0].props.tone]
      const link = buttons(tree2).find(x => x.children === 'open recorded chat')
      if (link) await link.onClick({ preventDefault() {}, stopPropagation() {}, currentTarget: {} })
      const result = { painted, outcome, unavailable: textOf(tree2).includes('Session unavailable'),
                       calls: [...globalThis.__calls] }
      if (o.titled) result.title = chips[0].title
      if (JSON.stringify(sel) !== JSON.stringify({ runId: o.view.id, nodeId: o.node, index: o.index }))
        bad.push({ name: o.name, reason: 'selection moved off the exact index', sel })
      const opens = result.calls.filter(c => c[0] === 'openSession')
      const extras = result.calls.filter(c => ['submit', 'insert', 'notify', 'navigate'].includes(c[0]))
      const hit = o.allowed.some(x => JSON.stringify(x) === JSON.stringify(result))
      if (!hit || extras.length || opens.length > 1)
        bad.push({ name: o.name, allowed: o.allowed, got: result, extras, opens })
      console.log('CJ2-PAIR-OBS ' + JSON.stringify({ name: o.name, ...result }))
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


REDRIVE_RUN = 'pair-redrive'


def _pair_transport(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
    """The redrive leg's child seam (the same substitution surface the offline
    witnesses use): the call persists one child session row in the run's own
    home and returns the child's verdict — the REAL runner classifies, writes
    every record and journal line, and owns the redrive."""
    tag = os.environ['CJ2_PAIR_REDRIVE_TAG']
    probe = Path(os.environ['CJ2_PAIR_PROBE'])
    assert node['id'] == 'review' and index in (0, 1), (node.get('id'), index)
    with sqlite3.connect(probe / 'home' / 'state.db') as db:
        db.execute('insert into sessions values (' + ','.join('?' for _ in range(15)) + ')',
                   (sid(tag, index, 0), f'{skey}#a0', 'fixture', 1, 1, 0, 0, 1, 1, 0,
                    time.time(), 1, 'fixture', 2, 0))
    base = dict(skey=skey, spawn=0, ms=1, attempts=1)
    if tag == 'redrive-retry' and index == 1:
        (probe / 'redrive-parked').touch()
        deadline = time.monotonic() + 30
        while not (probe / 'redrive-release').exists():
            if time.monotonic() > deadline:
                raise TimeoutError('Quartz was not released')
            time.sleep(.02)
        return dict(base, status='done', output={'result': 'Quartz accepted'})
    cls = 'cancelled' if tag == 'redrive-old' and index == 0 else 'declared_failure'
    return dict(base, status='failed', error_class=cls, error=f'{tag} {cls} at {index}')


# Self-child dispatch: one process runs the real `wf.py` engine end to end with
# ONLY the child transport substituted (records, journal, verdicts are all the
# runner's own writes).
if sys.argv[1:2] == ['child']:
    sys.path.insert(0, str(ROOT))
    _engine = load('cj2_pair_child_engine', ROOT / 'wf.py')
    with patch.object(_engine, 'run_child', _pair_transport), \
            patch.object(_engine, 'notify', return_value=None):
        _engine.main(os.environ['CJ2_PAIR_REDRIVE_RUN'])
    sys.exit(0)


tmp = Path(tempfile.mkdtemp(prefix='cj2-pair-'))
try:
    base = tmp / 'out'
    home, runs, out = base / 'home', tmp / 'runs', base
    home.mkdir(parents=True)
    runs.mkdir()
    base.mkdir(exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('HERMES_', 'WF_', 'FAKE_'))}
    env.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
               TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE='1', CJ2_PAIR_PROBE=str(out),
               WORKFLOW_MAX_SEATS='0')
    os.environ.clear()
    os.environ.update(env)
    sys.path.insert(0, str(ROOT))
    with sqlite3.connect(home / 'state.db') as c:
        c.execute('create table sessions (id text primary key, title text, model text, '
                  'input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, '
                  'api_call_count int, tool_call_count int, estimated_cost_usd real, started_at real, '
                  'last_activity_at real, last_activity_description text, ended_at real, expiry_finalized int)')
    api = load('cj2_pair_api', ROOT / 'dashboard' / 'plugin_api.py')
    wc = api._workflow_common()
    child = out / 'hermes-child'
    child.write_text(CHILD)
    child.chmod(0o755)

    def expect(schedule, name, view, index, label, allowed):
        return {'name': f'{schedule}/{name}', 'view': view, 'node': 'review', 'index': index,
                'label': label, 'allowed': allowed}

    def open_expect(dest, painted):
        return {'painted': painted, 'outcome': 'done', 'unavailable': False,
                'calls': [['openSession', dest, '{"intent":"in-place"}']]}

    observations = []
    for schedule in ('settled-events', 'old-events'):
        env['CJ2_PAIR_TAG'] = schedule
        r = runs / f'pair-{schedule}'
        (r / 'nodes').mkdir(parents=True)
        (r / 'run.json').write_text(json.dumps({'hermes_bin': str(child), 'item_concurrency': 1}))
        schema = {'type': 'object', 'properties': {'result': {'type': 'string'}}, 'required': ['result']}
        (r / 'graph.json').write_text(json.dumps({'name': r.name, 'nodes': [
            {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'timeout': 30,
             'fanout': {'items': ['Amber', 'Quartz'], 'goal': 'review {item}', 'schema': schema}}]}))

        def readrec(stem):
            return json.loads((r / 'nodes' / f'{stem}.json').read_text())

        engine_log = (out / f'{schedule}.engine.log').open('w')
        header_before = wc.run_state(r)
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
            header_live = wc.run_state(r)
            assert header_live['nodes']['review']['status'] == 'running'
            assert header_live['nodes']['review'].get('active_spawns'), header_live

            real_metrics = wc.run_child_metrics
            real_events = api._events

            def observe_fold(*args, **kwargs):
                fold = real_metrics(*args, **kwargs)
                assert fold[old_key]['_session_current'] == sid(schedule, 0, 0), fold
                assert sid(schedule, 0, 1) not in fold[old_key]['session_ids']
                return fold

            def race_events(*args, **kwargs):
                assert not (r / 'nodes' / 'review.json').exists()
                old_journal = real_events(*args, **kwargs)
                assert [e for e in old_journal if e.get('event') == 'item.started'
                        and e.get('node') == 'review' and e.get('index') == 0], old_journal
                assert not [e for e in old_journal if e.get('event') == 'item.finished'], old_journal
                (out / 'release').touch()
                deadline = time.monotonic() + 12
                while True:
                    events = real_events(*args, **kwargs)
                    done = [e for e in events if e.get('event') == 'item.finished'
                            and e.get('node') == 'review' and e.get('index') == 0]
                    if done and (out / 'quartz-ready-0').exists():
                        break
                    assert proc.poll() is None and time.monotonic() < deadline, events
                    time.sleep(.02)
                assert len(done) == 1 and done[0]['status'] == 'done', done
                rec = readrec('review.0')
                assert rec['spawn'] == rec['attempt'] == 1 and rec['status'] == 'done', rec
                assert not (r / 'nodes' / 'review.json').exists()
                return events if schedule == 'settled-events' else old_journal

            pinned = header_before if schedule == 'settled-events' else header_live
            with patch.object(wc, 'run_state', return_value=pinned), \
                    patch.object(wc, 'run_child_metrics', side_effect=observe_fold), \
                    patch.object(api, '_events', side_effect=race_events):
                racing = api._view(r, full=True)
        finally:
            (out / 'release').touch()
        row = racing['nodes']['review']['item_metrics'][0]
        check(row.get('session_current') == sid(schedule, 0, 1)
              and row.get('session_display') == {'status': 'done'}
              and 'session_outcome' not in row,
              f'{schedule}: the selected row ships ONE complete decision — the accepted #a1 '
              'with its full presentation (status and the error facts the record names) bound '
              'from the same read, never a bare status riding a separately-captured journal')
        check('1' not in racing['nodes']['review']['item_metrics']
              and 1 not in racing['nodes']['review']['item_metrics'],
              f'{schedule}: the in-flight sibling gains no fabricated destination')
        check(racing['nodes']['review'].get('output', {}).get('all_results') is None
              if isinstance(racing['nodes']['review'].get('output'), dict) else True,
              f'{schedule}: the racing response carries no aggregate')
        # The observer only ever sees the pre-race running stamp or the
        # settled journal — the pair law must hold under both.
        settled_allowed = [dict(painted='Amber', outcome=o, unavailable=s is None,
                                calls=[] if s is None else [['openSession', s, '{"intent":"in-place"}']])
                           for o, s in ((('done', sid(schedule, 0, 1)), ('done', None),
                                         ('running', sid(schedule, 0, 0)), ('pending', None))
                                        if schedule == 'settled-events'
                                        else (('running', sid(schedule, 0, 0)), ('running', None),
                                              ('done', sid(schedule, 0, 1)), ('done', None)))]
        observations.append(expect(schedule, 'racing-chip', racing, 0, 'Amber', settled_allowed))
        observations.append(expect(schedule, 'in-flight-sibling', racing, 1, 'Quartz',
                                   [{'painted': 'Quartz', 'outcome': 'pending',
                                     'unavailable': True, 'calls': []}]))
        (out / 'quartz-release').touch()
        try:
            assert proc.wait(timeout=30) == 0
        finally:
            engine_log.close()
        fresh = api._view(r, full=True)
        check(fresh['status'] == 'done', f'{schedule}: the released run settles for real')
        observations.append(expect(schedule, 'settled-opens-exact', fresh, 0, 'Amber',
                                   [open_expect(sid(schedule, 0, 1), 'Amber')]))
        observations.append(expect(schedule, 'settled-sibling-opens-own', fresh, 1, 'Quartz',
                                   [open_expect(sid(schedule, 1, 0), 'Quartz')]))
        check((out / 'release').exists(), 'harness: the release marker is not reused across legs')
        for marker in ('old-ready', 'release', 'quartz-ready-0', 'quartz-release'):
            (out / marker).unlink(missing_ok=True)

    # -- redrive leg: an unchanged-definition redrive under a retained old ----
    # journal. The old generation fails Amber (cancelled) and Quartz
    # (declared_failure) under the real runner; the REAL redrive door drops
    # the failed lanes (only the detached respawn handoff is stubbed); the
    # retry generation fails Amber as declared_failure while Quartz parks —
    # no aggregate exists while the racing response ships the OLD snapshot.
    env['CJ2_PAIR_REDRIVE_RUN'] = REDRIVE_RUN
    r2 = runs / REDRIVE_RUN
    (r2 / 'nodes').mkdir(parents=True)
    (r2 / 'run.json').write_text(json.dumps({'name': REDRIVE_RUN, 'item_concurrency': 1}))
    (r2 / 'graph.json').write_text(json.dumps({'name': REDRIVE_RUN, 'nodes': [
        {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65, 'timeout': 1500,
         'fanout': {'items': ['Amber', 'Quartz'], 'goal': 'review {item}'}}]}))
    graph2_bytes = (r2 / 'graph.json').read_bytes()

    def rec2(stem):
        return json.loads((r2 / 'nodes' / f'{stem}.json').read_text())

    def finish2(events, rec):
        return [e for e in events if e.get('event') == 'item.finished' and e.get('node') == 'review'
                and e.get('index') == 0 and e.get('skey') == rec['skey']]

    def launch_gen(tag):
        env['CJ2_PAIR_REDRIVE_TAG'] = tag
        f = (out / f'{tag}.engine.log').open('w')
        return subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), 'child', tag],
                                stdout=f, stderr=subprocess.STDOUT, env=env), f

    def rexpect(painted, outcome, dest, title):
        return {'painted': painted, 'outcome': outcome, 'unavailable': dest is None,
                'calls': [] if dest is None else [['openSession', dest, '{"intent":"in-place"}']],
                'title': title}

    def rcase(name, view, index, label, allowed, cancelled_title=None):
        case = {'name': f'redrive/{name}', 'view': view, 'node': 'review', 'index': index,
                'label': label, 'allowed': allowed, 'titled': True}
        if cancelled_title is not None:
            case['cancelled_title'] = cancelled_title
        return case

    old_title, new_title = 'redrive-old cancelled at 0', 'redrive-retry declared_failure at 0'
    old_pair = rexpect('Amber', 'cancelled', sid('redrive-old', 0, 0), old_title)
    new_pair = rexpect('Amber', 'failed', sid('redrive-retry', 0, 0), new_title)
    p_old, log_old = launch_gen('redrive-old')
    try:
        check(p_old.wait(timeout=20) == 0,
              'redrive: the old generation runs to its failed verdict under the real runner')
    finally:
        log_old.close()
    check(wc.run_state(r2)['status'] == 'failed',
          'redrive: the failed run stands — a cancelled straggler never reads stopped')
    old_rec = rec2('review.0')
    check(old_rec['status'] == 'failed' and old_rec['error_class'] == 'cancelled',
          'redrive: old Amber is recorded raw failed under class cancelled')
    old_view = api._view(r2, full=True)
    door = load('cj2_pair_door', ROOT / '__init__.py')
    real_events2 = api._events
    raced2, retry_box = [], {}

    def boundary2(*args, **kwargs):
        assert not raced2
        raced2.append(True)
        old_events = real_events2(*args, **kwargs)
        assert len(finish2(old_events, old_rec)) == 1, old_events
        with patch.object(door, '_respawn_runner', return_value=None) as handoff:
            redrive = door.act_redrive({'run_id': REDRIVE_RUN})
        assert redrive.get('ok') and redrive['re_drive'] == ['review'], redrive
        handoff.assert_called_once_with(r2)
        assert not (r2 / 'nodes/review.0.json').exists() and not (r2 / 'nodes/review.json').exists()
        p_retry, log_retry = launch_gen('redrive-retry')
        retry_box['p'], retry_box['log'] = p_retry, log_retry
        deadline = time.monotonic() + 12
        while not (out / 'redrive-parked').is_file():
            assert p_retry.poll() is None and time.monotonic() < deadline
            time.sleep(.02)
        new_rec = rec2('review.0')
        new_events = real_events2(*args, **kwargs)
        assert len(finish2(new_events, new_rec)) == 1 and not finish2(old_events, new_rec)
        assert new_rec['status'] == old_rec['status'] == 'failed'
        assert new_rec['efp'] == old_rec['efp'] and new_rec['skey'] != old_rec['skey']
        assert new_rec['error_class'] == 'declared_failure'
        assert not (r2 / 'nodes/review.json').exists() and not (r2 / 'nodes/review.1.json').exists()
        assert (r2 / 'graph.json').read_bytes() == graph2_bytes
        return old_events

    try:
        with patch.object(api, '_events', side_effect=boundary2):
            mixed2 = api._view(r2, full=True)
        check(bool(raced2) and not finish2(mixed2['events'], rec2('review.0')),
              'redrive: the racing response retains the pre-turnover journal while the new '
              'record already committed — stale metadata beside a fresh execution')
        parked2 = api._view(r2, full=True)
        check(not (r2 / 'nodes/review.json').exists(),
              'redrive: the sibling still parks — no aggregate to certify anything')
    finally:
        (out / 'redrive-release').touch()
        if 'p' in retry_box:
            try:
                assert retry_box['p'].wait(timeout=15) == 0
            finally:
                retry_box['log'].close()
    settled2 = api._view(r2, full=True)
    check(old_view['graph'] == mixed2['graph'] == parked2['graph'] == settled2['graph']
          and (r2 / 'graph.json').read_bytes() == graph2_bytes,
          'redrive: every response publishes the same untouched graph')
    check(rec2('review')['output']['all_results'][0]['skey'] == rec2('review.0')['skey'],
          'redrive: the settled aggregate certifies the NEW attempt')
    for marker in ('redrive-parked', 'redrive-release'):
        (out / marker).unlink(missing_ok=True)

    observations.append(rcase('old-response-retained', old_view, 0, 'Amber',
                              [old_pair], cancelled_title=old_title))
    observations.append(rcase('mixed', mixed2, 0, 'Amber',
                              [old_pair, new_pair,
                               rexpect('Amber', 'cancelled', None, old_title),
                               rexpect('Amber', 'failed', None, new_title)],
                              cancelled_title=old_title))
    observations.append(rcase('parked-new', parked2, 0, 'Amber', [new_pair]))
    observations.append(rcase('aggregate-new', settled2, 0, 'Amber', [new_pair]))
    observations.append(rcase('aggregate-quartz', settled2, 1, 'Quartz',
                              [rexpect('Quartz', 'done', sid('redrive-retry', 1, 0),
                                       'review Quartz')]))

    work = tmp / 'probe'
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
                                env={**env, 'CJ2_PAIR_PANELS': json.dumps(observations)},
                                timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc_panel.stdout)
    sys.stderr.write(proc_panel.stderr)
    obs = [json.loads(l[len('CJ2-PAIR-OBS '):]) for l in proc_panel.stdout.splitlines()
           if l.startswith('CJ2-PAIR-OBS ')]
    check(proc_panel.returncode == 0
          and [v['name'] for v in obs] == [o['name'] for o in observations],
          f'panel path: every one of the {len(observations)} observations renders/clicks '
          'exactly as the one decision declares')
    for v in obs:
        opens = [c for c in v['calls'] if c[0] == 'openSession']
        check(len(opens) <= 1 and all(c[2] == '{"intent":"in-place"}' for c in opens),
              f"{v['name']}: at most ONE openSession with the exact union options")
    print(f"\nALL PASS ({ok}) test_display_authority_pair_cj2 — paint and chat ride the exact "
          "selected execution in BOTH read orders: the settled leg never opens the superseded "
          "attempt under the done paint, the old-journal leg never rebinds the chat under the "
          "running paint, and the settled pairs keep opening their own exact chats.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
