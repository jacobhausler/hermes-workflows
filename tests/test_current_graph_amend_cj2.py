"""bd_2026-11-13-cj2 (Wave G): the CURRENT chat's authority is the committed graph.

The captain pending-amend review (receipts/ship20-recovery/cj2-pending-amend-review.py,
RED at 559ae1fe) ran the ACTUAL act_amend write, suspended the continuation before
the replacement spawn, kept the old record byte-identical, and re-read the live
dashboard._view: the node read pending/stale_of_amend, yet the pane still offered
the old session and the click invoked openSession. The disproven premise was that
stamping existing metrics rows or RAW record skeys can identify the current chat —
a raw skey names only the generation the record was written against. This test
pins the replacement law at the same seam the pane fetches (dashboard/plugin_api._view
-> wfcommon.run_child_metrics -> fold_child_metrics) and on the rendered/click path:

  1. pending after a REAL fingerprint-changing act_amend (only provider pings and
     continuation timing are mocked), old rows retained: the node's history stays
     inspectable but session_current is null -> `Session unavailable`, ZERO
     host/composer/notify/navigate calls — while an UNTOUCHED SIBLING node keeps
     its own binding and opens exactly once (no effect at a distance).
  2. fan-out item amendment: the amended fan-out node's items read CLOSED (both
     item eras invalidated together), each item keeps its OWN historical rows;
     absence never borrows a sibling node's binding.
  3. post-spawn, no-row then present: the record re-committed under the NEW efp
     with no row yet -> absent; the moment the new generation's row lands -> the
     new id opens exactly once. (The invalidated era's old row never returns.)
  4. INERT edit control: an amend that does not change the fingerprint (budget
     knob — `timeout` is not work under rule 2) leaves the previously valid
     record USABLE — the binding survives unchanged. This is the amendment
     distinction: invalidate-by-fingerprint vs inert-and-kept.
  5. claimless legacy control: a record without skey/attempt gains NO binding
     key — the documented last-entry law still navigates it (positive fallback).

Controls already committed and replayed by the sibling suites: same-key retry and
same-key missing (tests/test_current_attempt_replay_cj2.py obs1/obs3), cross-home
rotation (obs6), expiry select-before-validate (obs7), proven-current positive
(obs8), amended-generation zero-row and fan-out sibling scoping (obs9-obs12),
honest zero-telemetry (obs13); selector-level pins in
tests/test_stored_session_nav.mjs and tests/test_stored_session_order_cj2.py.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

C_ID = 'local-' + 'c' * 64
A_ID = 'local-' + 'a' * 64
B_ID = 'local-' + 'b' * 64
D_ID = 'local-' + 'd' * 64
E_ID = 'local-' + 'e' * 64
F1_ID = 'local-' + '1' * 64
F2_ID = 'local-' + '2' * 64
SCHEMA = ('create table if not exists sessions (id text, title text, model text, input_tokens int, '
          'output_tokens int, cache_read_tokens int, reasoning_tokens int, api_call_count int, '
          'tool_call_count int, estimated_cost_usd real, last_activity_at real, '
          'last_activity_description text, ended_at real, started_at real)')
OPEN_OK = '{"intent":"in-place"}'
CLOSED = {'unavailable': True, 'calls': []}
ok = 0


def check(cond, name):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        raise SystemExit(1)
    ok += 1


def expect_open(sid):
    return {'unavailable': False, 'calls': [['openSession', sid, OPEN_OK]]}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(sid, title, started):
    return (sid, title, 'fixture', 1, 1, 0, 0, 1, 1, 0.0, float(started), 'fixture',
            float(started) + 1, float(started))


def put(db, rows):
    marks = ','.join('?' * len(rows[0]))
    with sqlite3.connect(db) as c, c:
        c.execute(SCHEMA)
        c.executemany(f'insert into sessions values ({marks})', rows)


def node_metrics(view, nid):
    return view['nodes'][nid]['metrics']


def item_metrics(view, nid, index):
    return view['nodes'][nid]['item_metrics'][index]


def observe(observations, name, metrics, expect):
    observations.append({'name': name, 'metrics': metrics or {}, 'expect': expect})


tmp = tempfile.mkdtemp(prefix='cj2-graph-amend-')
try:
    home = Path(tmp) / 'home'
    runs = Path(tmp) / 'runs'
    r = runs / 'graphamend'
    (r / 'nodes').mkdir(parents=True)
    home.mkdir()
    # #71 r5 hostile-settings canary: an owner settings.runs_root outranks the
    # env pin at the raw resolver, so this in-process door writer must pin it
    # through wf_test_isolation.install — the final check asserts the canary
    # saw zero writes (the mechanism, not the text scanner).
    canary = home / 'owner-canary'
    canary.mkdir()
    (canary / 'sentinel.txt').write_bytes(b'owner canary: unchanged\n')
    (home / 'config.yaml').write_text(
        'plugins:\n  entries:\n    hermes-workflows:\n      settings:\n'
        f'        runs_root: "{canary}"\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('HERMES_', 'WF_', 'FAKE_'))}
    env.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
               TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE='1')
    os.environ.clear()
    os.environ.update(env)
    sys.path.insert(0, str(ROOT))
    door = load('cj2_graph_door', ROOT / '__init__.py')
    iso = load('cj2_graph_iso71', ROOT / 'tests' / 'wf_test_isolation.py')
    iso.install(door)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT
    api = load('cj2_graph_view', ROOT / 'dashboard' / 'plugin_api.py')
    wc = api._workflow_common()

    node_a = {'id': 'a', 'type': 'agent', 'goal': 'old goal'}
    node_b = {'id': 'b', 'type': 'agent', 'goal': 'keep'}
    node_f = {'id': 'fan', 'type': 'agent', 'goal': 'f {item}',
              'fanout': {'items': ['x', 'y']}}
    node_c = {'id': 'c', 'type': 'agent', 'goal': 'legacy era'}
    byid = {n['id']: n for n in (node_a, node_b, node_f, node_c)}
    (r / 'graph.json').write_text(json.dumps(
        {'name': 'graphamend', 'nodes': [node_a, node_b, node_f, node_c]}))
    (r / 'run.json').write_text(json.dumps({'name': 'graphamend'}))
    k_a = 'wf:graphamend:a:11111111.111111'
    k_b = 'wf:graphamend:b:22222222.222222'
    k_f0 = 'wf:graphamend:fan:0:33333333.333333'
    k_f1 = 'wf:graphamend:fan:1:33333333.333333'
    k_c = 'wf:graphamend:c:44444444.444444'
    put(home / 'state.db', [
        row(A_ID, k_a + '#a4', 10.0), row(B_ID, k_b + '#a0', 11.0),
        row(F1_ID, k_f0 + '#a0', 12.0), row(F2_ID, k_f1 + '#a0', 13.0),
        row(E_ID, k_c + '#a0', 14.0)])

    def stamp(nid, skey, spawn, node):
        return {'status': 'done', 'skey': skey, 'spawn': spawn,
                'efp': wc.efp(byid, node), 'fp_rule_version': wc.FP_RULE_VERSION,
                'profile_home': str(home)}

    (r / 'nodes' / 'a.json').write_text(json.dumps(stamp('a', k_a, 4, node_a)))
    (r / 'nodes' / 'b.json').write_text(json.dumps(stamp('b', k_b, 0, node_b)))
    (r / 'nodes' / 'fan.0.json').write_text(json.dumps(stamp('fan', k_f0, 0, node_f)))
    (r / 'nodes' / 'fan.1.json').write_text(json.dumps(stamp('fan', k_f1, 0, node_f)))
    (r / 'nodes' / 'fan.json').write_text(json.dumps(
        {'status': 'done', 'efp': wc.efp(byid, node_f), 'fp_rule_version': wc.FP_RULE_VERSION,
         'profile_home': str(home),
         'output': {'items': [], 'all_results': [{'status': 'done'}, {'status': 'done'}]}}))
    (r / 'nodes' / 'c.json').write_text(json.dumps(
        {'status': 'done', 'def_hash': wc.def_hash(node_c, wc.FP_RULE_LEGACY),
         'profile_home': str(home)}))   # claimless legacy (pre-efp def_hash) shape

    observations = []
    before = api._view(r, full=True)
    check(node_metrics(before, 'a')['session_current'] == A_ID
          and node_metrics(before, 'b')['session_current'] == B_ID
          and item_metrics(before, 'fan', 0)['session_current'] == F1_ID
          and item_metrics(before, 'fan', 1)['session_current'] == F2_ID,
          'setup: every node/item binds its exact efp-valid record era pre-amend')
    observe(observations, 'setup-a-opens-old', node_metrics(before, 'a'), expect_open(A_ID))
    observe(observations, 'setup-b-opens-own', node_metrics(before, 'b'), expect_open(B_ID))
    observe(observations, 'setup-fanitem0-opens-own', item_metrics(before, 'fan', 0), expect_open(F1_ID))
    observe(observations, 'setup-fanitem1-opens-own', item_metrics(before, 'fan', 1), expect_open(F2_ID))
    observe(observations, 'claimless-legacy-last-entry', node_metrics(before, 'c'), expect_open(E_ID))
    check('session_current' not in node_metrics(before, 'c'),
          'claimless legacy gains no binding key — the documented last-entry fallback stands')
    a_bytes_before = (r / 'nodes' / 'a.json').read_bytes()
    b_bytes_before = (r / 'nodes' / 'b.json').read_bytes()

    # The ONE fingerprint-changing amend, through the ACTUAL door write. Mocked
    # seams ONLY: provider liveness pings and the continuation handoff timing.
    with patch.object(door, '_resume_after_action', return_value='live'), \
            patch.object(door, '_route_liveness_ping', return_value=[]):
        result = door.act_amend({'run_id': r.name,
                                 'patch': {'nodes': {'a': {'goal': 'new goal'},
                                                     'fan': {'goal': 'f2 {item}'}}}})
    check(result.get('ok') is True and sorted(result.get('will_rerun') or []) == ['a', 'fan'],
          f'the real act_amend re-queues exactly the fingerprint-touched nodes ({result})')
    check((r / 'nodes' / 'a.json').read_bytes() == a_bytes_before
          and (r / 'nodes' / 'b.json').read_bytes() == b_bytes_before,
          'act_amend never rewrites the committed records — the old era survives byte-identical')

    after = api._view(r, full=True)
    check(after['nodes']['a']['status'] == 'pending'
          and after['nodes']['a']['stale_of_amend'] is True,
          'the amended node reads pending/stale_of_amend (the read model already knew)')
    m_a = node_metrics(after, 'a')
    check(m_a['session_ids'] == [A_ID] and m_a['session_current'] is None,
          'pending after a real amend, retained old row: history inspectable, destination ABSENT — '
          'a record invalidated by the committed graph cannot keep the current chat')
    m_f = after['nodes']['fan']['item_metrics']
    check(m_f[0]['session_ids'] == [F1_ID] and m_f[0]['session_current'] is None
          and m_f[1]['session_ids'] == [F2_ID] and m_f[1]['session_current'] is None,
          'item amendment invalidates BOTH item eras together — each keeps its own history, '
          'absence never borrows another era binding')
    check(node_metrics(after, 'b')['session_current'] == B_ID
          and after['nodes']['b']['status'] == 'done',
          'untouched sibling / no effect: the bound sibling survives the amendment at a distance')
    observe(observations, 'pending-amend-absent', m_a, CLOSED)
    observe(observations, 'amended-fanitem0-closed', m_f[0], CLOSED)
    observe(observations, 'amended-fanitem1-closed', m_f[1], CLOSED)
    observe(observations, 'sibling-still-opens-own', node_metrics(after, 'b'), expect_open(B_ID))

    # Inert edit control on the untouched sibling: a budget knob is not work
    # (rule 2 excludes it), so the previously valid record stays usable.
    with patch.object(door, '_resume_after_action', return_value='live'), \
            patch.object(door, '_route_liveness_ping', return_value=[]):
        inert = door.act_amend({'run_id': r.name, 'patch': {'nodes': {'b': {'timeout': 500}}}})
    check(inert.get('ok') is True and 'b' in (inert.get('unchanged') or [])
          and 'b' not in (inert.get('will_rerun') or []),
          f'the inert (fingerprint-unchanged) amend re-runs nothing for the edited node ({inert})')
    inert_view = api._view(r, full=True)
    check(inert_view['nodes']['b']['status'] == 'done'
          and node_metrics(inert_view, 'b')['session_current'] == B_ID,
          'an inert edit does not invalidate: the valid previous record stays usable')

    # Post-spawn on the amended node: new-era record first WITHOUT its row ->
    # still absent; the moment the row lands -> the new id, exactly once.
    amended = json.loads((r / 'graph.json').read_text())
    node_a2 = next(n for n in amended['nodes'] if n['id'] == 'a')
    k_a2 = 'wf:graphamend:a:55555555.555555'
    (r / 'nodes' / 'a.json').write_text(json.dumps(
        {'status': 'done', 'skey': k_a2, 'spawn': 0,
         'efp': wc.efp({**byid, 'a': node_a2}, node_a2),
         'fp_rule_version': wc.FP_RULE_VERSION, 'profile_home': str(home)}))
    m2 = node_metrics(api._view(r, full=True), 'a')
    check(m2['session_ids'] == [A_ID] and m2['session_current'] is None,
          'post-spawn new era with no row yet: absent — the invalidated old chat never returns')
    observe(observations, 'post-spawn-no-row-absent', m2, CLOSED)
    put(home / 'state.db', [row(D_ID, k_a2 + '#a0', 30.0)])
    m3 = node_metrics(api._view(r, full=True), 'a')
    check(m3['session_ids'] == [A_ID, D_ID] and m3['session_current'] == D_ID,
          'the replacement generation lands: the record-named exact title is the destination')
    observe(observations, 'post-spawn-present-opens-new', m3, expect_open(D_ID))

    # -- the rendered/click path on the REAL candidate module -----------------
    work = Path(tmp) / 'probe'
    (work / 'desktop').mkdir(parents=True)
    (work / 'tests').mkdir()
    shutil.copyfile(ROOT / 'desktop/plugin.js', work / 'desktop/plugin.js')
    shim = (ROOT / 'tests/test_stored_session_nav.mjs').read_text()
    seam = '  // -- 1b. fan-out scoping'
    assert shim.count(seam) == 1
    probe = """
  {
    const replay = JSON.parse(process.env.CJ2_GRAPH_AMEND)
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
      assert.equal(r.calls.filter(c => c[0] === 'openSession').length <= 1, true,
        `${o.name}: at most ONE openSession call, never a walk-back`)
      verdicts.push({ name: o.name, result: r })
    }
    console.log('CJ2-GRAPH-AMEND ' + JSON.stringify(verdicts))
  }
"""
    driver = work / 'tests/probe.mjs'
    driver.write_text(shim.replace(seam, probe + seam))
    proc = subprocess.run(['node', '--experimental-strip-types', str(driver)],
                          env={**env, 'CJ2_GRAPH_AMEND': json.dumps(observations)},
                          timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    line = next((l for l in proc.stdout.splitlines() if l.startswith('CJ2-GRAPH-AMEND ')), None)
    check(proc.returncode == 0 and line is not None,
          f'click path: every one of the {len(observations)} graph-authority observations '
          'renders/clicks exactly as the projection declares')
    verdicts = json.loads(line[len('CJ2-GRAPH-AMEND '):])
    check([v['name'] for v in verdicts] == [o['name'] for o in observations],
          'the probe covered every observation through the rendered/click path')
    # A REAL door write that resolves runs_root (the #71 S4/S5 shelf-save
    # shape): pinned it lands in the env-pinned root; an unpinned door lands
    # it in the owner-settings canary — the zero-write check bites at the
    # mechanism, not at the scanner.
    saved = door.act_save({'graph': {'name': 'graphamend-canary', 'nodes': [node_b]},
                           'name': 'cj2-canary'})
    check(saved.get('saved') == 'cj2-canary' and (runs / 'library' / 'cj2-canary.json').exists(),
          'the real door shelf write through the pinned resolver lands in the env-pinned root')
    leaked = sorted(p.relative_to(canary).as_posix() for p in canary.rglob('*') if p.is_file())
    check(leaked == ['sentinel.txt'],
          'the hostile settings.runs_root canary saw ZERO writes through the pinned '
          f'door — the pin is the resolver wrap, not the source scanner: {leaked}')
    print(f"\nALL PASS ({ok}) test_current_graph_amend_cj2 — current-chat authority is the "
          "committed graph revision and its valid node/item facts: a fingerprint-changing amend "
          "invalidates the old era to null with ZERO host calls; an inert edit keeps the record "
          "usable; untouched siblings are unaffected; the replacement generation re-opens once.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
