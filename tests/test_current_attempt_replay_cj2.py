"""bd_2026-11-13-cj2 (Wave E): RED/GREEN replay of the captain's
missing-current counterexample — actual SQLite -> THE production read-model
projection (run_child_metrics + fold_child_metrics, the seam both dashboard
_view and door act_status serialize) -> the rendered/click path on the REAL
candidate module through the stub-host harness.

The captain review (receipts/ship20-recovery/cj2-missing-current-review.py at
27d2afbd, exit 1) folded through a BARE child_metrics call, which has no run
records in view; the live navigation surfaces never fold there — every
conversation-link payload ships from run_child_metrics, where the run's own
node/item records name the exact current attempt (the wf.py spawn contract
`--continue <skey>#a<attempt>` — the session-title contract). This replay
carries that SAME authoritative current attempt through those seams:

  obs1 present-new-B        rows #a2 + #a10, record names #a10  -> opens ONLY B
  obs2 known-spawn-no-row   record names #a3, no #a3 row         -> unavailable, ZERO calls
  obs3 removed-current      #a10 row deleted, #a2 survives       -> unavailable, ZERO calls
  obs4/obs5 fan-out items   each item binds its own current      -> exact-owner routing, no sibling id
  obs6 profile rotation     claim #a3, row lives in the OTHER home -> binds through the merge
  obs7 expiry-marked        bound #a3 row carries expiry_finalized -> unavailable, ZERO calls
  obs8 proven-current       record names #a2, #a2 row survives   -> opens A (positive legacy)
  obs9/obs10/obs11 (Wave F) amended skey, asserted on THE REAL dashboard
  projection (dashboard/plugin_api._view, the seam the pane fetches): amendment
  pre-row, valid-present opening exactly once, then the captain's amended-generation
  counterexample — deleting the SOLE row of the record-named new skey must never
  hand the click to a superseded key's survivor (receipts/ship20-recovery/
  cj2-amend-missing-current-review.py, exit 1 at 5c08216c, green at this head)
  obs12 amended fan-out     an item's new skey has zero rows     -> that item CLOSED,
  its sibling keeps its OWN binding — absence never crosses item lines
  obs13 zero rows           claim names a skey, telemetry absent -> NO metrics, no
  fabricated destination or counters; the click renders unavailable, zero calls

Every observation additionally asserts ZERO composer submit/insert, notify and
navigate calls — read-only viewing sends no message and resumes nothing.
"""
import importlib.util
import json
import os
from contextlib import closing
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('replay_wfcommon', ROOT / 'wfcommon.py')
wc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc)

A_ID = 'local-' + 'a' * 64
B_ID = 'local-' + 'b' * 64
C_ID = 'local-' + 'c' * 64
FULL = ('create table sessions (id text, title text, model text, '
        'input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, '
        'api_call_count int, tool_call_count int, estimated_cost_usd real, '
        'last_activity_at real, last_activity_description text, ended_at real, started_at real)')
EXP_SCHEMA = FULL[:-1] + ', expiry_finalized int)'
OPEN_OK = '{"intent":"in-place"}'

ok = 0


def check(cond, name):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        raise SystemExit(1)
    ok += 1


def mkhome(tmp, tag):
    h = Path(tmp) / tag
    h.mkdir(parents=True)
    return h


def mkrun(tmp, run_id, home):
    r = Path(tmp) / run_id
    (r / 'nodes').mkdir(parents=True)
    return r


def put(db, rows):
    marks = ','.join(['?'] * len(rows[0]))
    with closing(sqlite3.connect(db)) as c, c:
        c.executemany(f'insert into sessions values ({marks})', rows)


def row(sid, key, attempt, started, expired=None, schema_has_exp=False):
    r = (sid, f'{key}#a{attempt}', 'fake', 10, 5, 1, 0, 2, 3, 0.5, started, 'tick', None, started)
    return r + (expired,) if schema_has_exp else r


def record(run, name, home, **facts):
    rec = {'profile_home': str(home)}
    rec.update(facts)
    (run / 'nodes' / f'{name}.json').write_text(json.dumps(rec))


def fold(run, *keys):
    merged = wc.run_child_metrics(run)
    rows = [merged[k] for k in keys]
    return wc.fold_child_metrics(rows), merged


OPEN = {'unavailable': False, 'calls': []}


def expect_open(sid):
    return {'unavailable': False, 'calls': [['openSession', sid, OPEN_OK]]}


CLOSED = {'unavailable': True, 'calls': []}

observations = []
tmp = tempfile.mkdtemp(prefix='cj2-replay-')
try:
    # -- obs1/2/3: one node, three states of the SAME run --------------------
    h1 = mkhome(tmp, 'home1')
    run1 = mkrun(tmp, 'replaynav', h1)
    key1 = 'wf:replaynav:node:12345678.123456'
    db1 = h1 / 'state.db'
    with closing(sqlite3.connect(db1)) as c, c:
        c.execute(FULL)
    put(db1, [row(A_ID, key1, 2, 2.0)])
    record(run1, 'one', h1, status='running', skey=key1, attempt=3, pid=None)
    f2, _ = fold(run1, key1)
    check(f2['session_ids'] == [A_ID] and f2['session_current'] is None,
          'obs2 fold: known spawn #a3 with no row yet — the older survivor stays inspectable, destination absent')
    observations.append({'name': 'obs2-known-spawn-no-row', 'metrics': f2, 'expect': CLOSED})

    put(db1, [row(B_ID, key1, 10, 10.0)])
    record(run1, 'one', h1, status='done', skey=key1, spawn=10)
    f1, _ = fold(run1, key1)
    check(f1['session_ids'] == [A_ID, B_ID] and f1['session_current'] == B_ID,
          'obs1 fold: #a2 then #a10 chronological (Wave A chronology stands) and the record-named #a10 binds')
    check('_session_current' not in f1, 'obs1 fold: the private binding stamp never serializes')
    observations.append({'name': 'obs1-present-new-attempt', 'metrics': f1, 'expect': expect_open(B_ID)})

    with closing(sqlite3.connect(db1)) as c, c:
        gone = c.execute('delete from sessions where id=?', (B_ID,))
        check(gone.rowcount == 1, 'obs3 setup: ONLY the current #a10 row is removed from actual SQLite')
    f3, _ = fold(run1, key1)   # RE-READ through the production projection, no process restart
    check(f3['session_ids'] == [A_ID] and f3['session_current'] is None,
          'obs3 fold: current row gone, older survivor remains — computed absence, never a promotion')
    observations.append({'name': 'obs3-removed-current', 'metrics': f3, 'expect': CLOSED})

    # -- obs4: fan-out items bind their OWN current attempts ------------------
    h2 = mkhome(tmp, 'home2')
    run2 = mkrun(tmp, 'replayfan', h2)
    db2 = h2 / 'state.db'
    k0 = 'wf:replayfan:fan:0:12345678.123456'
    k1 = 'wf:replayfan:fan:1:12345678.123456'
    with closing(sqlite3.connect(db2)) as c, c:
        c.execute(FULL)
    put(db2, [row(A_ID, k0, 1, 5.0), row(C_ID, k1, 1, 7.0)])
    record(run2, 'fan.0', h2, status='done', skey=k0, spawn=1)
    record(run2, 'fan.1', h2, status='done', skey=k1, spawn=1)
    f0, fitem1 = fold(run2, k0), fold(run2, k1)
    check(f0[0]['session_current'] == A_ID and f0[0]['session_ids'] == [A_ID],
          'obs4 fold: picked item 0 binds its own recorded current attempt')
    check(fitem1[0]['session_current'] == C_ID and fitem1[0]['session_ids'] == [C_ID],
          'obs4 fold: picked item 1 binds its OWN current — the sibling never lends an id')
    observations.append({'name': 'obs4-fanout-item0-exact-owner', 'metrics': f0[0], 'expect': expect_open(A_ID)})
    observations.append({'name': 'obs5-fanout-item1-exact-owner', 'metrics': fitem1[0], 'expect': expect_open(C_ID)})

    # -- obs6: profile rotation — the claim binds the row in the NEWER home ---
    h3a, h3b = mkhome(tmp, 'home3a'), mkhome(tmp, 'home3b')
    run3 = mkrun(tmp, 'replayrot', h3a)
    key3 = 'wf:replayrot:node:12345678.123456'
    with closing(sqlite3.connect(h3a / 'state.db')) as c:
        c.execute(FULL)
    with closing(sqlite3.connect(h3b / 'state.db')) as c:
        c.execute(FULL)
    put(h3a / 'state.db', [row(A_ID, key3, 2, 2.0)])
    put(h3b / 'state.db', [row(B_ID, key3, 3, 30.0)])
    record(run3, 'one', h3a, status='done', skey=key3, spawn=3)
    record(run3, 'two', h3b)
    f6, _ = fold(run3, key3)
    check(f6['session_ids'] == [A_ID, B_ID] and f6['session_current'] == B_ID,
          'obs6 fold: the child rotated homes; the exact #a3 title binds through the cross-home merge')
    observations.append({'name': 'obs6-profile-rotation-exact-owner', 'metrics': f6, 'expect': expect_open(B_ID)})

    # -- obs7: the bound row is expiry-marked -> unavailable, zero calls ------
    h4 = mkhome(tmp, 'home4')
    run4 = mkrun(tmp, 'replayexp', h4)
    key4 = 'wf:replayexp:node:12345678.123456'
    with closing(sqlite3.connect(h4 / 'state.db')) as c:
        c.execute(EXP_SCHEMA)
    with closing(sqlite3.connect(h4 / 'state.db')) as c, c:
        c.executemany('insert into sessions values (' + ','.join('?' * 15) + ')',
                      [row(A_ID, key4, 2, 2.0, 0, True), row(B_ID, key4, 10, 10.0, 1, True)])
    record(run4, 'one', h4, status='done', skey=key4, spawn=10)
    f7, _ = fold(run4, key4)
    check(f7['session_current'] == B_ID and f7['session_ids_expired'] == [B_ID],
          'obs7 fold: the binding selects the exact current row VERBATIM; the expiry flag rides (select-before-validate)')
    observations.append({'name': 'obs7-expiry-marked-current', 'metrics': f7, 'expect': CLOSED})

    # -- obs8: the record PROVES the surviving row current -> positive reuse --
    record(run4, 'one', h4, status='done', skey=key4, spawn=2)
    with closing(sqlite3.connect(h4 / 'state.db')) as c, c:
        c.execute('delete from sessions')
        c.executemany('insert into sessions values (' + ','.join('?' * 15) + ')',
                      [row(A_ID, key4, 2, 2.0, 0, True)])
    f8, _ = fold(run4, key4)
    check(f8['session_current'] == A_ID,
          'obs8 fold: A independently proven current — the positive legacy reuse stands')
    observations.append({'name': 'obs8-proven-current-positive', 'metrics': f8, 'expect': expect_open(A_ID)})

    # -- obs9/obs10/obs11: amended skey, through THE REAL dashboard projection --
    # Wave F (bd_2026-11-13-cj2, captain amended-generation review at 5c08216c):
    # an amendment moves the node's skey; the canonical record names the NEW key
    # and spawn. The claim must stay authoritative even when its key has no row
    # at all — a survivor under a SUPERSEDED key is inspection data only. These
    # fixtures read the dashboard seam itself (dashboard/plugin_api._view, full)
    # — the exact payload the pane fetches — not a hand-fed fold.
    dash_spec = importlib.util.spec_from_file_location('replay_view_api', ROOT / 'dashboard/plugin_api.py')
    assert dash_spec is not None and dash_spec.loader is not None
    dash = importlib.util.module_from_spec(dash_spec)
    dash_spec.loader.exec_module(dash)
    h5 = mkhome(tmp, 'home5')
    run5 = mkrun(tmp, 'replayamend', h5)
    k_old, k_new = 'wf:replayamend:node:11111111.111111', 'wf:replayamend:node:22222222.222222'
    node5 = {'id': 'node', 'type': 'agent', 'goal': 'amended goal'}
    (run5 / 'graph.json').write_text(json.dumps({'name': 'replayamend', 'nodes': [node5]}))
    (run5 / 'run.json').write_text('{}')
    rec5 = {'status': 'done', 'skey': k_new, 'spawn': 0,
            'efp': wc.efp({'node': node5}, node5), 'profile_home': str(h5)}
    (run5 / 'nodes' / 'node.json').write_text(json.dumps(rec5))
    with closing(sqlite3.connect(h5 / 'state.db')) as c, c:
        c.execute(FULL)
    put(h5 / 'state.db', [row(A_ID, k_old, 4, 10.0)])
    prev_home = os.environ.get('HERMES_HOME')
    os.environ['HERMES_HOME'] = str(h5)
    try:
        m9 = dash._view(run5, full=True)['nodes']['node']['metrics']
        check(m9['session_ids'] == [A_ID] and m9['session_current'] is None
              and '_session_current' not in m9 and '_session_id_at' not in m9,
              'obs9 view: amended skey named by the record, row not yet landed — the superseded key never lends')
        observations.append({'name': 'obs9-amended-pre-row-absence', 'metrics': m9, 'expect': CLOSED})
        put(h5 / 'state.db', [row(B_ID, k_new, 0, 20.0)])
        m10 = dash._view(run5, full=True)['nodes']['node']['metrics']
        check(m10['session_ids'] == [A_ID, B_ID] and m10['session_current'] == B_ID,
              'obs10 view: the new generation row landed — the record-named exact title is the destination')
        observations.append({'name': 'obs10-amended-present-exactly-once', 'metrics': m10, 'expect': expect_open(B_ID)})
        with closing(sqlite3.connect(h5 / 'state.db')) as c, c:
            gone = c.execute('delete from sessions where id=?', (B_ID,))
            check(gone.rowcount == 1, 'obs11 setup: ONLY the row of the new generation is expunged')
        m11 = dash._view(run5, full=True)['nodes']['node']['metrics']
        check(m11['session_ids'] == [A_ID] and m11['session_current'] is None,
              'obs11 view: captain amended-generation counterexample — sole row deleted, the survivor under '
              'the superseded key is NEVER promoted into the destination slot')
        check(json.loads((run5 / 'nodes' / 'node.json').read_text()) == rec5,
              'obs11 view: the projection is read-only — the canonical record rides untouched')
        observations.append({'name': 'obs11-amended-missing-current', 'metrics': m11, 'expect': CLOSED})

        # -- obs12: fan-out item across a new generation with zero rows -------
        h6 = mkhome(tmp, 'home6')
        run6 = mkrun(tmp, 'replayamfan', h6)
        fan6 = {'id': 'fan', 'type': 'agent', 'goal': 'fan goal', 'fanout': {'items': ['x', 'y']}}
        (run6 / 'graph.json').write_text(json.dumps({'name': 'replayamfan', 'nodes': [fan6]}))
        (run6 / 'run.json').write_text('{}')
        k0_old, k1_old, k0_new = ('wf:replayamfan:fan:0:11111111.111111',
                                  'wf:replayamfan:fan:1:11111111.111111',
                                  'wf:replayamfan:fan:0:99999999.999999')
        with closing(sqlite3.connect(h6 / 'state.db')) as c, c:
            c.execute(FULL)
        put(h6 / 'state.db', [row(A_ID, k0_old, 1, 5.0), row(C_ID, k1_old, 1, 7.0)])
        efp6 = wc.efp({'fan': fan6}, fan6)
        record(run6, 'fan', h6, status='done', efp=efp6,
               output={'items': [], 'all_results': [{'status': 'done'}, {'status': 'done'}]})
        record(run6, 'fan.0', h6, status='done', skey=k0_old, spawn=1, efp=efp6)
        record(run6, 'fan.1', h6, status='done', skey=k1_old, spawn=1, efp=efp6)
        m12 = dash._view(run6, full=True)['nodes']['fan']['item_metrics']
        check(m12[0]['session_current'] == A_ID and m12[1]['session_current'] == C_ID,
              'obs12 setup: both items independently bound pre-amendment')
        record(run6, 'fan.0', h6, status='done', skey=k0_new, spawn=0, efp=efp6)   # the amend
        m12 = dash._view(run6, full=True)['nodes']['fan']['item_metrics']
        check(m12[0]['session_ids'] == [A_ID] and m12[0]['session_current'] is None,
              'obs12 view: amended item has a zero-row new skey — that item keeps the absence destination')
        check(m12[1]['session_current'] == C_ID,
              'obs12 view: absence never crosses item lines — the sibling keeps its OWN bound destination')
        observations.append({'name': 'obs12-fanout-amended-item-closed', 'metrics': m12[0], 'expect': CLOSED})
        observations.append({'name': 'obs12-fanout-sibling-keeps-own', 'metrics': m12[1], 'expect': expect_open(C_ID)})

        # -- obs13: claim present, telemetry absent entirely -------------------
        run7 = mkrun(tmp, 'replayzero', h6)
        node7 = {'id': 'node', 'type': 'agent', 'goal': 'never persisted'}
        (run7 / 'graph.json').write_text(json.dumps({'name': 'replayzero', 'nodes': [node7]}))
        (run7 / 'run.json').write_text('{}')
        (run7 / 'nodes' / 'node.json').write_text(json.dumps(
            {'status': 'done', 'skey': 'wf:replayzero:node:33333333.333333', 'spawn': 0,
             'efp': wc.efp({'node': node7}, node7), 'profile_home': str(h6)}))
        v13 = dash._view(run7, full=True)['nodes']['node']
        check('session_ids' not in v13.get('metrics', {}) and 'session_current' not in v13.get('metrics', {}),
              'obs13 view: no telemetry — no synthetic row, no fabricated destination, no counters')
        observations.append({'name': 'obs13-zero-rows-honest-absence', 'metrics': {}, 'expect': CLOSED})
    finally:
        if prev_home is None:
            os.environ.pop('HERMES_HOME', None)
        else:
            os.environ['HERMES_HOME'] = prev_home

    # -- the rendered/click path on the REAL candidate module -----------------
    work = Path(tmp) / 'probe'
    (work / 'desktop').mkdir(parents=True)
    (work / 'tests').mkdir()
    shutil.copyfile(ROOT / 'desktop/plugin.js', work / 'desktop/plugin.js')
    test = (ROOT / 'tests/test_stored_session_nav.mjs').read_text()
    seam = '  // -- 1b. fan-out scoping'
    assert test.count(seam) == 1
    probe = """
  {
    const replay = JSON.parse(process.env.CJ2_REPLAY_METRICS)
    const click = async metrics => {
      remount()
      globalThis.__calls.length = 0
      const tree = render({ storedId: latestStoredSessionId(metrics) })
      const button = buttons(tree).find(x => x.children === 'open recorded chat')
      if (button) await button.onClick({ preventDefault() {}, stopPropagation() {}, currentTarget: {} })
      return { unavailable: textOf(tree).includes('Session unavailable'), calls: globalThis.__calls.map(x => [...x]) }
    }
    const verdicts = []
    for (const o of replay) {
      const r = await click(o.metrics)
      assert.deepEqual(r, o.expect, `${o.name}: ${JSON.stringify(r)}`)
      assert.equal(r.calls.filter(c => ['submit', 'insert', 'notify', 'navigate'].includes(c[0])).length, 0,
        `${o.name}: read-only — zero composer/notify/navigate calls`)
      verdicts.push({ name: o.name, result: r })
    }
    console.log('CJ2-REPLAY ' + JSON.stringify(verdicts))
  }
"""
    driver = work / 'tests/probe.mjs'
    driver.write_text(test.replace(seam, probe + seam))
    env = {**os.environ, 'CJ2_REPLAY_METRICS': json.dumps(observations)}
    proc = subprocess.run(['node', '--experimental-strip-types', str(driver)],
                          env=env, timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    line = next((l for l in proc.stdout.splitlines() if l.startswith('CJ2-REPLAY ')), None)
    check(proc.returncode == 0 and line is not None,
          f'replay click path: SQLite -> run_child_metrics -> fold -> render/click, all {len(observations)} observations')
    verdicts = json.loads(line[len('CJ2-REPLAY '):])
    check([v['name'] for v in verdicts] == [o['name'] for o in observations],
          'replay covered every observation through the rendered/click path')
    print(f'\nALL PASS ({ok}) test_current_attempt_replay_cj2 — the current-attempt binding rides the run\'s own records '
          'through the ONE projection into the click path; known-newer-without-row NEVER opens the older survivor')
finally:
    shutil.rmtree(tmp, ignore_errors=True)
