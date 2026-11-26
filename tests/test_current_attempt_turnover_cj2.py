"""bd_2026-11-25-cj2: a late execution turnover rebinds the recorded chat to the
attempt the PUBLISHED aggregate names — never to another generation's binding.

The exact-head challenge replay (receipts/ship20-recovery/
cj2-execution-be5576e0.uPnDNZ/case.log, red at be5576e08c5b2559dd7121ab7e44dc8aad0ac672)
witnessed two NodePanel paths where layout+outcome rode one execution while the
chat claim rode another, both invisible to the era law: efp fingerprints
definitions, not executions, so a restored ABA graph and a same-fingerprint
redrive certify BOTH generations against the published revision.

1. ABA (`dynamic/mixed`): a certified restore re-expands a dynamic fan-out
   between the metrics fold and the facts read inside one _view. The response
   publishes the NEW ordering (same efp as the old one) while the fold's claim
   still names the OLD attempt's chat — the painted new chip opened the old
   item's conversation.
2. Same-fingerprint redrive (`redrive/mixed-next-outcome`): the failed item's
   retry lands mid-view; the response's row outcome is the new `done` while the
   link opened the FAILED attempt's chat.

The law pinned here (the second half of the read boundary the era law opened):
layout, outcome and the recorded-chat claim of a projected fan-out item ride
ONE published record — the aggregate row's OWN full title. The binding is the
join of that row's recorded title (`skey` + the attempt it names, suffix
included) against the already-read home-scoped session rows — no pairing
heuristic against a second aggregate sample, no re-fold:
- a stamped row whose exact title landed in the read join binds that row's id
  verbatim; prior attempts stay inspectable in session_ids;
- a stamped row whose title the read join never saw (a superseded or not-yet-
  landed generation) binds the computed absence — ONLY that binding goes
  unavailable, ZERO host calls; label, outcome, counters and history ride
  untouched; the old generation never answers as a stand-in;
- settled, demoted and steady responses pay nothing (no extra fold, no second
  read loop): the claim path already bound what the fold observed, and the
  exact-title join agrees with it. A version/efp match alone is not execution
  identity — and neither is skey membership: a schema correction advances the
  attempt INSIDE one skey (tests/test_exact_attempt_bind_cj2.py).

The same real seams the challenge used are driven here: the real runner
(wf.main, only child results and session rows faked), the real act_amend and
act_redrive, the real dashboard _view interleaved at the metrics fold, and the
actual NodePanel render/click through the shipped plugin module (only test-only
visibility differs). Earlier wrong-chat controls (R1-R5, the witness replay)
stay green beside this — this test adds the identity join the era law cannot
make alone.
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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ok = 0


def sid(tag, index):
    return 'local-' + hashlib.sha256(f'{tag}:{index}'.encode()).hexdigest()


if len(sys.argv) > 4 and sys.argv[1] == '--engine':
    # Engine mode: the REAL runner with ONLY the child transport and session
    # rows faked (the same substitution the parent replay used).
    repo = Path(sys.argv[2]).resolve()
    sys.path.insert(0, str(repo))
    spec = importlib.util.spec_from_file_location('turnover_engine', repo / 'wf.py')
    wf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wf)
    run_name, tag = sys.argv[3], sys.argv[4]

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node['id'] == 'prep':
            labels = {'old': ['Amber', 'Quartz'], 'middle': ['Cobalt', 'Jade'],
                      'final': ['Quartz', 'Amber']}[tag]
            return dict(status='done', output={'items': labels}, skey=skey, spawn=0, ms=1)
        assert node['id'] == 'review' and index is not None, (node, goal)
        label = goal.split()[-1]
        with sqlite3.connect(Path(os.environ['HERMES_HOME']) / 'state.db') as c:
            row = (sid(tag, index), f'{skey}#a0', 'fake', 1, 1, 0, 0, 1, 1, 0, 1, 1,
                   'fixture', 2, 0)
            c.execute('insert into sessions values ('
                      + ','.join('?' for _ in row) + ')', row)
        attempt = dict(skey=skey, spawn=0, ms=1, attempts=1)
        if tag == 'fail' and index == 0:
            return dict(attempt, status='failed', error_class='declared_failure',
                        error='first attempt refused')
        return dict(attempt, status='done', output={'label': label})
    with patch.object(wf, 'run_child', child), patch.object(wf, 'notify', return_value=None):
        wf.main(run_name)
    sys.exit(0)


def check(cond, name):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        raise SystemExit(1)
    ok += 1


def expect_open(s):
    return {'unavailable': False, 'calls': [['openSession', s, '{"intent":"in-place"}']]}


CLOSED = {'unavailable': True, 'calls': []}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROBE = r"""
  {
    // bd_2026-11-25-cj2 turnover replay — the ACTUAL NodePanel, selection
    // atoms and all; only test-only visibility differs. Unlike the
    // sibling probe, the painted-label pick supports dynamic fan-outs
    // (no static def items): the published aggregate alone paints.
    const replay = JSON.parse(process.env.CJ2_TURNOVER_PANELS)
    const mat = n => n == null || typeof n !== 'object' ? n :
      Array.isArray(n) ? n.map(mat) :
      typeof n.type === 'function' ? mat(n.type(n.props)) :
      { ...n, props: { ...n.props, children: mat(n.props?.children) } }
    const verdicts = []
    const bad = []
    for (const o of replay) {
      remount()
      globalThis.__calls.length = 0
      globalThis.__si = 0
      globalThis.__effects = []
      markNavFocus(null) // one observation at a time: the one-shot token never rides over
      $selNode.set({ runId: o.view.id, nodeId: o.node })
      mod.$fanItem.set(o.index == null ? null : { runId: o.view.id, nodeId: o.node, index: o.index })
      if (o.pick) {
        const def = o.view.graph.nodes.find(n => n.id === o.node)
        const staticFirst = def && def.fanout && Array.isArray(def.fanout.items)
          ? def.fanout.items[0] : null
        mod.$fanItem.set(null)
        const initial = mat(mod.NodePanel({ detail: o.view }))
        const labels = o.chiplabels ?? (staticFirst == null ? [] : [staticFirst])
        const chips = buttons(initial).filter(x => labels.includes(textOf(x.children).trim().split(/\s+/)[0]))
        const painted = chips.length ? textOf(chips[0].children).trim().split(/\s+/)[0] : null
        if (chips.length) chips[0].onClick({ stopPropagation() {} })
        const sel = mod.$fanItem.get()
        if (!chips.length || painted !== o.paints
            || JSON.stringify(sel) !== JSON.stringify({ runId: o.view.id, nodeId: o.node, index: 0 }))
          bad.push({ name: o.name, reason: 'the first painted chip deviates', painted,
                     want: o.paints, sel })
        console.log('CJ2-TURNOVER-CHIP ' + JSON.stringify({ name: o.name, label: painted }))
      }
      const tree = mat(mod.NodePanel({ detail: o.view }))
      for (const f of globalThis.__effects) f()
      const button = buttons(tree).find(x => x.children === 'open recorded chat')
      if (button) await button.onClick({ preventDefault() {}, stopPropagation() {}, currentTarget: {} })
      const result = { unavailable: textOf(tree).includes('Session unavailable'), calls: [...globalThis.__calls] }
      const extras = result.calls.filter(c => ['submit', 'insert', 'notify', 'navigate'].includes(c[0]))
      const opens = result.calls.filter(c => c[0] === 'openSession')
      const mismatch = JSON.stringify(result) !== JSON.stringify(o.expect)
        || extras.length > 0 || opens.length > 1
      if (mismatch) bad.push({ name: o.name, expect: o.expect, got: result, extras, opens })
      verdicts.push({ name: o.name, result })
    }
    $selNode.set(null)
    mod.$fanItem.set(null)
    console.log('CJ2-TURNOVER-PANELS ' + JSON.stringify(verdicts))
    assert.deepEqual(bad, [], `${bad.length} panel observation(s) deviate — ${JSON.stringify(bad)}`)
  }
"""

tmp = tempfile.mkdtemp(prefix='cj2-turnover-')
try:
    home = Path(tmp) / 'home'
    runs = Path(tmp) / 'runs'
    home.mkdir()
    runs.mkdir()
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
    door = load('cj2_turnover_door', ROOT / '__init__.py')
    iso = load('cj2_turnover_iso71', ROOT / 'tests' / 'wf_test_isolation.py')
    iso.install(door)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT
    api = load('cj2_turnover_api', ROOT / 'dashboard' / 'plugin_api.py')
    wc = api._workflow_common()
    with sqlite3.connect(home / 'state.db') as c:
        c.execute('create table sessions (id text primary key, title text, model text, '
                  'input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, '
                  'api_call_count int, tool_call_count int, estimated_cost_usd real, started_at real, '
                  'last_activity_at real, last_activity_description text, ended_at real, expiry_finalized int)')

    observations = []

    def panel(name, view, node, index, expect, pick=None, paints=None, chiplabels=None):
        obs = {'name': name, 'view': view, 'node': node,
               'index': index, 'expect': expect, 'pick': pick}
        if paints is not None:
            obs['paints'] = paints
        if chiplabels is not None:
            obs['chiplabels'] = chiplabels
        observations.append(obs)

    def graph_doc(name, agent_prep):
        prep = ({'id': 'prep', 'type': 'agent', 'goal': 'list two colors',
                 'max_turns': 65, 'timeout': 1500} if agent_prep else
                {'id': 'prep', 'type': 'echo', 'output': {'items': ['Amber', 'Quartz']}})
        return {'name': name, 'nodes': [
            prep,
            {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'after': ['prep'],
             'max_turns': 65, 'timeout': 1500,
             'fanout': {'items_from': 'prep.items', 'goal': 'review {item}'}}]}

    def fixture(name, agent_prep):
        r = runs / name
        (r / 'nodes').mkdir(parents=True)
        (r / 'run.json').write_text(json.dumps({'name': name, 'item_concurrency': 1}))
        (r / 'graph.json').write_text(json.dumps(graph_doc(name, agent_prep)))
        return r

    def drive(r, tag, expected='done'):
        subprocess.run([sys.executable, '-B', __file__, '--engine', str(ROOT), r.name, tag],
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                       check=True, timeout=30)
        st = wc.run_state(r)
        assert st['status'] == expected, (tag, st['status'])
        recs = {stem: json.loads((r / 'nodes' / f'{stem}.json').read_text())
                for stem in ('prep', 'review', 'review.0', 'review.1')}
        return api._view(r, full=True), recs

    def amend(r, goal):
        with patch.object(door, '_respawn_runner', return_value=None) as handoff, \
                patch.object(door, '_route_liveness_ping', return_value=[]):
            ans = door.act_amend({'run_id': r.name, 'patch': {'nodes': {'prep': {'goal': goal}}}})
        assert ans.get('ok') and {'prep', 'review'} <= set(ans['will_rerun']), ans
        handoff.assert_called_once_with(r)

    real_metrics = wc.run_child_metrics

    def item(view, i=0):
        return view['nodes']['review']['item_metrics'][i]

    def painted_items(view):
        out = view['nodes']['review'].get('output')
        return [x.get('item') for x in out['all_results']] if isinstance(out, dict) else None

    # -- scenario 1: the ABA restore re-expands the dynamic fan-out mid-view -----
    r = fixture('dyn-turnover-aba', agent_prep=True)
    old, old_rec = drive(r, 'old')
    check(painted_items(old) == ['Amber', 'Quartz']
          and item(old)['session_current'] == sid('old', 0),
          'the settled original response paints and binds its own generation')
    panel('T1-aba-original-settled', old, 'review', 0, expect_open(sid('old', 0)),
          pick='first', paints='Amber', chiplabels=['Amber', 'Quartz'])

    def land_aba(run, *a, **k):
        assert run == r
        fold = real_metrics(run, *a, **k)
        with patch.object(wc, 'run_child_metrics', real_metrics):
            amend(r, 'list two other colors')
            drive(r, 'middle')
            amend(r, 'list two colors')
            drive(r, 'final')
        return fold
    with patch.object(wc, 'run_child_metrics', side_effect=land_aba):
        mixed = api._view(r, full=True)
    fresh, final_rec = None, None
    with patch.object(wc, 'run_child_metrics', real_metrics):
        fresh = api._view(r, full=True)
        final_rec = {stem: json.loads((r / 'nodes' / f'{stem}.json').read_text())
                     for stem in ('review', 'review.0', 'review.1')}
    check(old['graph'] == mixed['graph'] == fresh['graph']
          and old_rec['review']['efp'] == final_rec['review']['efp'],
          'setup: the restore publishes the byte-identical graph and efp — a version match '
          'is not execution identity')
    check(painted_items(mixed) == ['Quartz', 'Amber'],
          'the turnover response publishes the certified aggregate layout it read late')
    check(item(mixed)['session_current'] is None
          and sid('old', 0) in item(mixed)['session_ids'],
          'the restore\'s title was never in the read join: the binding fails closed — '
          'the old generation rides as history, untouched, and never answers for the new chip')
    check(item(mixed, 1)['session_current'] is None
          and sid('old', 1) in item(mixed, 1)['session_ids'],
          'the sibling index is adjudicated on its own merits — never a borrow')
    panel('T2-aba-mixed-published-new-label-closes-the-disputed-chat', mixed, 'review', 0,
          CLOSED, pick='first', paints='Quartz', chiplabels=['Quartz', 'Amber'])
    panel('T3-aba-mixed-sibling-disputed-closes', mixed, 'review', 1, CLOSED)
    check(item(fresh)['session_current'] == sid('final', 0)
          and sid('old', 0) in item(fresh)['session_ids'],
          'the settled response converges: the replacement chat, history retained')
    panel('T4-aba-fresh-settled-opens-exact', fresh, 'review', 0,
          expect_open(sid('final', 0)), pick='first', paints='Quartz',
          chiplabels=['Quartz', 'Amber'])
    panel('T5-aba-fresh-settled-sibling-opens-exact', fresh, 'review', 1,
          expect_open(sid('final', 1)))

    # -- scenario 2: same-fingerprint redrive — the outcome AND the chat move ------
    r2 = fixture('dyn-turnover-redrive', agent_prep=False)
    failed, fail_rec = drive(r2, 'fail', expected='failed')
    check(painted_items(failed) == ['Amber', 'Quartz']
          and item(failed)['session_current'] == sid('fail', 0),
          'the failed settled response binds the failed attempt exactly')
    panel('T6-redrive-failed-current-opens-own', failed, 'review', 0,
          expect_open(sid('fail', 0)), pick='first', paints='Amber',
          chiplabels=['Amber', 'Quartz'])

    def land_retry(run, *a, **k):
        assert run == r2
        fold = real_metrics(run, *a, **k)
        with patch.object(door, '_respawn_runner', return_value=None), \
                patch.object(wc, 'run_child_metrics', real_metrics):
            ans = door.act_redrive({'run_id': r2.name})
        assert ans.get('ok') and ans.get('re_drive') == ['review'], ans
        drive(r2, 'retry')
        return fold

    def once(run, *a, **k):
        with patch.object(wc, 'run_child_metrics', real_metrics):
            return land_retry(run, *a, **k)
    with patch.object(wc, 'run_child_metrics', side_effect=once):
        mixed2 = api._view(r2, full=True)
    with patch.object(wc, 'run_child_metrics', real_metrics):
        settled = api._view(r2, full=True)
    check(mixed2['nodes']['review']['output'] == settled['nodes']['review']['output'],
          'setup: the turnover response publishes the retried aggregate verbatim (the '
          'late facts read stands — the demotion law is untouched)')
    check(item(mixed2)['session_current'] is None
          and sid('fail', 0) in item(mixed2)['session_ids'],
          'the racing redrive response fails closed on the unread title — the published '
          'attempt\'s row is not in the fold this read already took, so no chat is offered, '
          'and the DONE outcome NEVER opens the failed attempt (the original negative)')
    panel('T7-redrive-mixed-successful-outcome-closes-unread-attempt', mixed2, 'review', 0,
          CLOSED, pick='first', paints='Amber', chiplabels=['Amber', 'Quartz'])
    check(item(settled)['session_current'] == sid('retry', 0)
          and sid('fail', 0) in item(settled)['session_ids'],
          'the settled redrive converges to the same binding')
    panel('T8-redrive-settled-opens-exact', settled, 'review', 0,
          expect_open(sid('retry', 0)), pick='first', paints='Amber',
          chiplabels=['Amber', 'Quartz'])
    panel('T9-redrive-settled-sibling-opens-own', settled, 'review', 1,
          expect_open(sid('retry', 1)))

    # -- the rendered/click path on the ACTUAL NodePanel -------------------------
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
                          env={**env, 'CJ2_TURNOVER_PANELS': json.dumps(observations)},
                          timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    line = next((l for l in proc.stdout.splitlines() if l.startswith('CJ2-TURNOVER-PANELS ')), None)
    check(proc.returncode == 0 and line is not None,
          f'panel path: every one of the {len(observations)} turnover observations '
          'renders/clicks exactly as the projection declares')
    verdicts = json.loads(line[len('CJ2-TURNOVER-PANELS '):])
    check([v['name'] for v in verdicts] == [o['name'] for o in observations],
          'the probe covered every observation through the actual NodePanel')
    for v in verdicts:
        opens = [c for c in v['result']['calls'] if c[0] == 'openSession']
        check(len(opens) <= 1 and all(c[2] == '{"intent":"in-place"}' for c in opens),
              f"{v['name']}: at most ONE openSession with the exact union options")
    # A REAL door write that resolves runs_root (the #71 S4/S5 shelf-save
    # shape): pinned it lands in the env-pinned root; an unpinned door lands
    # it in the owner-settings canary — the zero-write check bites at the
    # mechanism, not at the scanner.
    saved = door.act_save({'graph': graph_doc('turnover-canary', False), 'name': 'cj2-canary'})
    check(saved.get('saved') == 'cj2-canary' and (runs / 'library' / 'cj2-canary.json').exists(),
          'the real door shelf write through the pinned resolver lands in the env-pinned root')
    leaked = sorted(p.relative_to(canary).as_posix() for p in canary.rglob('*') if p.is_file())
    check(leaked == ['sentinel.txt'],
          'the hostile settings.runs_root canary saw ZERO writes through the pinned '
          f'door — the pin is the resolver wrap, not the source scanner: {leaked}')
    print(f"\nALL PASS ({ok}) test_current_attempt_turnover_cj2 — on a late execution "
          "turnover the layout, outcome and recorded-chat claim ride ONE published record: "
          "the published row's exact title binds verbatim when it landed in the read join, "
          "an unread title marks only the chat unavailable with ZERO calls, and settled "
          "reads converge without a re-read loop.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
