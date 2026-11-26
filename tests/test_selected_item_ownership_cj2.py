"""Selected-item ownership (bd_2026-11-25-cj2 item-source lane): the actual
NodePanel must answer the selected item's OWN record for every presentation
field — label, goal/tooltip, badge/status, error/tone/refusal and the exact
chat — never the aggregate's or a sibling's, with or without a published
aggregate.

Four legs, all offline:

LEG A (real runner, dynamic items_from): the committed dynamic item keeps the
FROZEN per-item record shape — its resolved item is authentic execution
evidence the run already records: the head's committed roster joined at the
record's canonical index. While the sibling parks and NO aggregate exists,
the actual panel paints its real label and goal tooltip with
the exact chat — Amber's committed chat exposed under '#0' is the HOLD at
receipts/ship20-recovery/cj2-sourced-row-9c42abae (dynamic witness). An
unstarted/running dynamic membership stays a placeholder live chip.

LEG A2 (real runner, LIST-ROOT items_from): the SAME expansion where the
head's committed output IS a list and the ref indexes it ('prep.0' over
'[["Amber","Quartz"]]') — exactly the shape the runner's resolve_ref walked
at expansion time (the two walkers must agree: the red at
receipts/ship20-recovery/cj2-list-root-77a146fd painted '#0' / 'review '
pre-aggregate on a valid list root). The archival A2c control keeps an
ABSENT path an honest absence: no roster, no guessed name — never a default.

LEG B (real runner, static def): a settled successful Amber under a
forbidden-model aggregate shows NO foreign class and the item's own badge in
the selected header; failed Quartz keeps its own class (the header's
`?? shown.error_class` fallback is the second HOLD — selected-facts witness).

LEG C (archival inputs — hand-committed records under the shipped validity
law, never a normal-runner mutation): (C1) a status-bearing row under an
aggregate committed CANCELLED keeps its own red error tone, shows no node
refusal the row does not name, and its cancelled sibling wears its own word
(no aggregate tone, no borrowed badge); (C2) a claim-bearing legacy
status-bearing `output.items` row joins its OWN named attempt even when a
conflicting exact row is newer (sentinel), the exact row's deletion is an
explicit absence (never the last entry), and a genuinely claimless row keeps
the documented last-entry law — the three stay distinct.

Usage: python3.14 -B tests/test_selected_item_ownership_cj2.py [fresh-dir]
Only the model transport is substituted; the runner and the read model own
every record and journal write.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo))
LEGS = {'dyn', 'forb', 'lhead'}
OBSERVER = repo / 'tests/observe_outcome_cj2.mjs'


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, repo / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sid(leg, index):
    return 'local-' + hashlib.sha256(f'item-ownership:{leg}:{index}'.encode()).hexdigest()


def wait_for(predicate, proc=None, limit=12):
    end = time.monotonic() + limit
    while not predicate():
        assert time.monotonic() < end and (proc is None or proc.poll() is None)
        time.sleep(.02)


# ------------------------------------------------------------------ engine --
if len(sys.argv) > 2 and sys.argv[2] in LEGS:
    out, leg = Path(sys.argv[1]).resolve(), sys.argv[2]
    wf = load('ownership_engine', 'wf.py')

    def transport(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        assert node['id'] == 'review' and index in (0, 1)
        with sqlite3.connect(out / 'home/state.db') as db:
            # ONE spawn (attempt 0) per item — the record names `#a0`.
            row = (sid(leg, index), f'{skey}#a0', 'fake', 1, 1, 0, 0, 1, 1,
                   0, time.time(), 1, 'fixture', 2, 0)
            db.execute('insert into sessions values (' + ','.join('?' for _ in row) + ')', row)
        base = dict(skey=skey, spawn=0, ms=1, attempts=1)
        if leg == 'dyn':
            if index == 1:
                (out / 'quartz-parked').touch()
                wait_for((out / 'quartz-release').exists)
            return dict(base, status='done', output={'result': f'{goal} ok'})
        if leg == 'lhead':
            if index == 1:
                (out / 'lhead-parked').touch()
                wait_for((out / 'lhead-release').exists)
            return dict(base, status='done', output={'result': f'{goal} ok'})
        if index == 0:
            return dict(base, status='done', output={'result': 'Amber accepted'})
        return dict(base, status='failed', error_class='forbidden_model',
                    error='served a forbidden model')
    with patch.object(wf, 'run_child', transport), patch.object(wf, 'notify', return_value=None):
        wf.main('own-' + leg)
    sys.exit(0)

# ------------------------------------------------------------------ setup --
out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(
    tempfile.mkdtemp(prefix='cj2-item-ownership-'))
out.mkdir(exist_ok=True)
for key in tuple(os.environ):
    if key.startswith(('HERMES_', 'WF_', 'FAKE_', 'WORKFLOW_')):
        del os.environ[key]
home, runs = out / 'home', out / 'runs'
home.mkdir(exist_ok=True); runs.mkdir(exist_ok=True)
os.environ.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
                  TMPDIR=str(out), PYTHONDONTWRITEBYTECODE='1', WORKFLOW_MAX_SEATS='0')
with sqlite3.connect(home / 'state.db') as db:
    db.execute('create table sessions (id text primary key, title text, model text, input_tokens int, '
               'output_tokens int, cache_read_tokens int, reasoning_tokens int, '
               'api_call_count int, tool_call_count int, estimated_cost_usd real, started_at real, '
               'last_activity_at real, last_activity_description text, ended_at real, expiry_finalized int)')
api = load('ownership_api', 'dashboard/plugin_api.py')
wc = api._workflow_common()
failures = []


def check(ok, why):
    print(f'ok: {why}' if ok else f'FAIL: {why}')
    if not ok:
        failures.append(why)


def write(path, x):
    path.write_text(json.dumps(x, indent=2))


def sess(row_id, title, started):
    with sqlite3.connect(home / 'state.db') as db:
        db.execute('insert or replace into sessions values (' + ','.join('?' for _ in range(15)) + ')',
                   (row_id, title, 'fake', 1, 1, 0, 0, 1, 1, 0, started, 1, 'fixture', 2, 0))


def launch(leg, f):
    return subprocess.Popen([sys.executable, '-B', __file__, str(out), leg],
                            stdout=f, stderr=subprocess.STDOUT)


def record(r, stem):
    return json.loads((r / 'nodes' / f'{stem}.json').read_text())


def mk_run(name, graph_nodes):
    r = runs / name
    (r / 'nodes').mkdir(parents=True)
    write(r / 'run.json', {'name': name, 'item_concurrency': 1})
    write(r / 'graph.json', {'name': name, 'nodes': graph_nodes})
    return r


def expect(painted, outcome, title, classes, badge, refusal, error_tone, dest):
    """Field ORDER is the observer's actual-object order (strict JSON compare)."""
    return dict(painted=painted, outcome=outcome, title=title, classes=classes,
                badge=badge, refusal=refusal, errorTone=error_tone,
                unavailable=dest is None,
                calls=[] if dest is None else [['openSession', dest, {'intent': 'in-place'}]])


CASES = []


def case(name, view, index, *allowed):
    CASES.append(dict(name=name, view=view, node='review', index=index, allowed=allowed))


# ------------------------------------------------------------------- LEG A --
# A normal items_from expansion; the sibling parks while the new Amber is
# already committed. No roster/record/graph mutation by the harness.
dyn = mk_run('own-dyn', [
    {'id': 'prep', 'type': 'echo', 'output': {'items': ['Amber', 'Quartz']}},
    {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65, 'timeout': 1500,
     'after': ['prep'], 'fanout': {'items_from': 'prep.items', 'goal': 'review {item}'}}])
rdyn = dyn / 'nodes' / 'review.0.json'
with (out / 'dyn.engine.log').open('w') as f:
    proc = launch('dyn', f)
    try:
        wait_for(lambda: (out / 'quartz-parked').exists() and rdyn.is_file()
                 and json.loads(rdyn.read_text()).get('status') == 'done', proc)
        assert not (dyn / 'nodes/review.json').exists()
        mixed = api._view(dyn, full=True)
    finally:
        (out / 'quartz-release').touch()
        assert proc.wait(timeout=14) == 0
rec0 = record(dyn, 'review.0')
roster0 = record(dyn, 'prep')['output']['items']
check('item' not in rec0 and roster0 == ['Amber', 'Quartz'],
      'LEG A: the atomic item commit keeps the FROZEN record shape — the resolved item '
      'is the head\'s committed roster, joined at the record\'s canonical index')
im = mixed['nodes']['review']['item_metrics']
check('all_results' not in (mixed['nodes']['review'].get('output') or {}),
      'LEG A: the witness really is a pre-aggregate read')
check(im[0].get('item') == 'Amber' and im[0].get('session_display') == {'status': 'done'}
      and im[0].get('session_current') == sid('dyn', 0),
      'LEG A: the sourced decision ships the identity beside the same status/chat pair')
case('dyn/mixed-amber', mixed, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid('dyn', 0)))
case('dyn/mixed-sibling', mixed, 1,
     # membership without a committed record stays a PLACEHOLDER live chip —
     # no guessed name, no certified card; its own recorded chat is exact
     # (the substituted transport never finalizes this item's record)
     expect('#1', 'pending', 'review ', [], 'pending', None, None, sid('dyn', 1)))
settled = api._view(dyn, full=True)
check(settled['status'] == 'done'
      and [row.get('item') for row in settled['nodes']['review']['output']['all_results']]
          == ['Amber', 'Quartz'],
      'LEG A: the aggregate rows carry the same resolved items the records own')
case('dyn/settled-amber', settled, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid('dyn', 0)))

# ------------------------------------------------------------------ LEG A2 --
# The SAME dynamic expansion with a LIST-ROOT head: 'prep.0' indexes the
# head's committed output list exactly as the runner's resolve_ref walked it
# at expansion time. The pre-aggregate panel must still name the real item —
# the sibling park keeps the no-aggregate window observable.
lhead = mk_run('own-lhead', [
    {'id': 'prep', 'type': 'echo', 'output': [['Amber', 'Quartz']]},
    {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65, 'timeout': 1500,
     'after': ['prep'], 'fanout': {'items_from': 'prep.0', 'goal': 'review {item}'}}])
assert not wc.validate_graph_full(json.loads((lhead / 'graph.json').read_text())), \
    'LEG A2: a LIST-root items_from def must be a valid graph'
rl0 = lhead / 'nodes' / 'review.0.json'
with (out / 'lhead.engine.log').open('w') as f:
    proc = launch('lhead', f)
    try:
        wait_for(lambda: (out / 'lhead-parked').exists() and rl0.is_file()
                 and json.loads(rl0.read_text()).get('status') == 'done', proc)
        assert not (lhead / 'nodes/review.json').exists()
        lhead_mixed = api._view(lhead, full=True)
    finally:
        (out / 'lhead-release').touch()
        assert proc.wait(timeout=14) == 0
check('item' not in record(lhead, 'review.0')
      and record(lhead, 'prep')['output'][0] == ['Amber', 'Quartz'],
      'LEG A2: the atomic item commit keeps the FROZEN record shape — the resolved item '
      'is the head\'s committed LIST-root roster, joined at the canonical index')
lim = lhead_mixed['nodes']['review']['item_metrics']
check('all_results' not in (lhead_mixed['nodes']['review'].get('output') or {}),
      'LEG A2: the witness really is a pre-aggregate read')
check(lim[0].get('item') == 'Amber' and lim[0].get('session_display') == {'status': 'done'}
      and lim[0].get('session_current') == sid('lhead', 0),
      'LEG A2: the list-root join ships the identity beside the same status/chat pair')
case('lhead/mixed-amber', lhead_mixed, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid('lhead', 0)))
case('lhead/mixed-sibling', lhead_mixed, 1,
     expect('#1', 'pending', 'review ', [], 'pending', None, None, sid('lhead', 1)))
lhead_settled = api._view(lhead, full=True)
check(lhead_settled['status'] == 'done'
      and [row.get('item') for row in lhead_settled['nodes']['review']['output']['all_results']]
          == ['Amber', 'Quartz'],
      'LEG A2: the settled aggregate rows carry the same resolved items the records own')
case('lhead/settled-amber', lhead_settled, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid('lhead', 0)))

# ------------------------------------------------------------------- LEG B --
forb = mk_run('own-forb', [
    {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65, 'timeout': 1500,
     'fanout': {'items': ['Amber', 'Quartz'], 'goal': 'review {item}'}}])
with (out / 'forb.engine.log').open('w') as f:
    assert launch('forb', f).wait(timeout=18) == 0
fb = api._view(forb, full=True)
check(fb['nodes']['review']['error_class'] == 'forbidden_model',
      'LEG B: the aggregate still honestly names its own forbidden-model death (raw facts stay)')
check('error_class' not in record(forb, 'review.0'),
      'LEG B: the successful item record names no error class of its own')
case('fb/amber', fb, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid('forb', 0)))
case('fb/quartz', fb, 1,
     expect('Quartz', 'failed', 'served a forbidden model', ['forbidden_model'],
            'failed', None, 'red', sid('forb', 1)))


# ------------------------------------------------------------------- LEG C --
# Archival inputs: hand-committed records carrying the REAL fingerprint
# stamped by the shipped rule — archival shape, never a normal-runner mutation.
def arch(name, node_rec):
    nodes = [{'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65,
              'timeout': 1500, 'fanout': {'items': ['Amber', 'Quartz'], 'goal': 'review {item}'}}]
    r = mk_run(name, nodes)
    byid = {n['id']: n for n in nodes}
    node_rec = dict(node_rec)
    node_rec['efp'] = wc.efp(byid, byid['review'])
    node_rec['fp_rule_version'] = wc.FP_RULE_VERSION
    write(r / 'nodes' / 'review.json', node_rec)
    return r


def skey_of(run_name, index, fp):
    return f'wf:{run_name}:review:{index}:{fp[:8]}.c0ffee'


# ---- C1: cancellation tone and refusal never ride the aggregate ------------
tone = arch('arch-tone', {
    'status': 'failed', 'error': 'node cancelled by stop', 'error_class': 'cancelled',
    'refusal': 'lifetime_cap_spent',
    'output': {'items': [], 'all_results': [
        {'status': 'failed', 'error': 'lane died', 'error_class': 'timeout',
         'item': 'Amber', 'spawn': 0, 'ms': 1, 'attempts': 1, 'attempts_log': []},
        {'status': 'failed', 'error': 'stop hit', 'error_class': 'cancelled',
         'item': 'Quartz', 'spawn': 0, 'ms': 1, 'attempts': 1, 'attempts_log': []}]}})
raw = record(tone, 'review')
for i, row in enumerate(raw['output']['all_results']):
    row['skey'] = skey_of(tone.name, i, raw['efp'])
    sess(sid('arch', i), row['skey'] + '#a0', 1000 + i)
write(tone / 'nodes/review.json', raw)
tone_view = api._view(tone, full=True)
case('arch/timeout-under-cancelled', tone_view, 0,
     expect('Amber', 'failed', 'lane died', ['timeout'], 'failed', None, 'red',
            sid('arch', 0)))
case('arch/cancelled-sibling', tone_view, 1,
     expect('Quartz', 'pending', 'stop hit', ['cancelled'], 'cancelled', None, 'neutral',
            sid('arch', 1)))

# ---- C2: claim-bearing legacy status-bearing output.items ------------------
def legacy_rec(payload):
    return {'status': 'failed', 'error': 'legacy quorum death',
            'output': {'items': [payload]}}


leg2 = arch('arch-legacy', legacy_rec({
    'status': 'failed', 'error': 'lane died', 'error_class': 'timeout',
    'item': 'Amber', 'spawn': 0, 'ms': 1}))
K0 = skey_of(leg2.name, 0, record(leg2, 'review')['efp'])
rawL = record(leg2, 'review')
rawL['output']['items'][0]['skey'] = K0             # the row names its OWN generation
write(leg2 / 'nodes/review.json', rawL)
mine, later = ('local-' + hashlib.sha256(b'claim').hexdigest(),
               'local-' + hashlib.sha256(b'later').hexdigest())
sess(mine, K0 + '#a0', 1000)
sess(later, K0 + '#a1', 2000)                     # a CONFLICTING exact row, newer
v1 = api._view(leg2, full=True)
m1 = v1['nodes']['review']['item_metrics'][0]
check(m1.get('session_current') == mine
      and m1.get('session_display') == {'status': 'failed', 'error_class': 'timeout',
                                        'error': 'lane died'}
      and m1.get('item') == 'Amber',
      'LEG C2: the claim-bearing legacy row binds its OWN named title, not the newest fold entry')
case('arch/claim-opens-own', v1, 0,
     expect('Amber', 'failed', 'lane died', ['timeout'], 'failed', None, 'red', mine))

# exact named row deleted: the computed absence, never the surviving newer attempt
with sqlite3.connect(home / 'state.db') as db:
    db.execute('delete from sessions where title=?', (K0 + '#a0',))
v2 = api._view(leg2, full=True)
m2 = v2['nodes']['review']['item_metrics'][0]
check('session_current' in m2 and m2['session_current'] is None,
      'LEG C2: exact-row deletion is an EXPLICIT absence (distinct from the claimless fallback)')
case('arch/claim-row-deleted', v2, 0,
     expect('Amber', 'failed', 'lane died', ['timeout'], 'failed', None, 'red', None))

# genuinely claimless (no int attempt completes a title): last-entry stands
raw2 = record(leg2, 'review')
row = dict(raw2['output']['items'][0])
row.pop('spawn')
raw2['output']['items'] = [row]
write(leg2 / 'nodes/review.json', raw2)
sess(mine, K0 + '#a0', 1000)                      # restore the era for the fallback witness
v3 = api._view(leg2, full=True)
m3 = v3['nodes']['review']['item_metrics'][0]
check('session_current' not in m3 and m3.get('session_ids', [])[-1] == later,
      'LEG C2: a claimless legacy row keeps the documented last-entry law')
case('arch/claimless-last-entry', v3, 0,
     expect('Amber', 'failed', 'lane died', ['timeout'], 'failed', None, 'red', later))

# ---- A2c: an ABSENT items_from path is an honest absence (archival input) ---
# The head committed a dict output WITHOUT the indexed path: no roster
# authority exists, so the committed item stays UNNAMED (no guessed name, no
# default) while its own decision and exact chat still bind. Same join law
# as LEG A2 — absence, not rejection, keeps the placeholder. The hand-
# committed item.finished line mirrors the runner's journal shape (panel
# membership law: a finished index is an authoritative member); the archived
# record stands alone without one, exactly as on disk.
absent = mk_run('own-absent', [
    {'id': 'prep', 'type': 'echo', 'output': {}},
    {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65, 'timeout': 1500,
     'after': ['prep'], 'fanout': {'items_from': 'prep.0', 'goal': 'review {item}'}}])
a_byid = {n['id']: n for n in json.loads((absent / 'graph.json').read_text())['nodes']}
a_rec = {'status': 'done', 'output': {'result': 'review  ok'}, 'ms': 1, 'attempts': 1, 'spawn': 0}
a_rec['efp'] = wc.efp(a_byid, a_byid['review'])
a_rec['fp_rule_version'] = wc.FP_RULE_VERSION
a_rec['skey'] = skey_of(absent.name, 0, a_rec['efp'])
write(absent / 'nodes/prep.json', {'status': 'done', 'output': {'nothing': ['Amber']},
                                   'ms': 1, 'attempts': 1})
write(absent / 'nodes/review.0.json', a_rec)
(absent / 'events.jsonl').write_text(json.dumps(
    {'ts': '2026-11-25T00:00:00+00:00', 'event': 'item.finished', 'node': 'review', 'index': 0,
     'status': 'done', 'error': None, 'error_class': None, 'attempts': 1, 'attempts_log': [],
     'tail': None, 'log_path': None, 'child_log_path': None, 'skey': a_rec['skey'], 'ms': 1}
) + '\n')
sess(sid('absent', 0), a_rec['skey'] + '#a0', 1000)
absent_view = api._view(absent, full=True)
aim = absent_view['nodes']['review']['item_metrics'][0]
check('item' not in aim and aim.get('session_current') == sid('absent', 0),
      'LEG A2c: an absent path names NOTHING — the row keeps its own decision and exact '
      'chat without a guessed item (honest absence, never a new default)')
case('a2c/absent-path-unnamed', absent_view, 0,
     expect('#0', 'done', 'review ', [], 'Finished', None, None, sid('absent', 0)))

# ---------------------------------------------------------------- observer --
# Drive the checkout-local vendored observer (tests/observe_outcome_cj2.mjs —
# a byte-for-byte copy of the actual-NodePanel observer this lane grew),
# extended in memory ONLY to read the fields this lane names (title, header
# class words, header badge, error tone, refusal, running-chip membership).
# No absolute private path: the publish scrub and a fresh HOME can run the
# exported test as-is.
observer = OBSERVER.read_text()
for before, after in (
    ("const chips=list(show()).filter(p=>Array.isArray(p.children) && p.children[0]?.type==='StatusDot')",
     "const chips=list(show()).filter(p=>Array.isArray(p.children) && (p.children[0]?.type==='StatusDot' || (p.children[0]?.type==='span' && p.children[0]?.props?.['aria-hidden'])))"),
    ("const tones = {good:'done', bad:'failed', muted:'pending'}",
     "const tones = {good:'done', bad:'failed', muted:'pending', run:'running'}"),
    ("const tone=target.children[0].props.tone",
     "const tone=target.children[0].props.tone ?? (target.children[0].props['aria-hidden']?'run':'x')"),
    ("const actual={painted,outcome,unavailable:text(tree).includes('Session unavailable'),calls:[...calls]}",
     """const words=new Set()
 for (const n of walk(tree)) if (n.type==='span' && typeof n.props?.children==='string' && ['forbidden_model','cancelled','timeout'].includes(n.props.children)) words.add(n.props.children)
 const badges=[...walk(tree)].filter(n=>n.type==='Badge').map(n=>n.props?.children)
 const esect=[...walk(tree)].find(n=>n.type==='div'&&Array.isArray(n.props?.children)&&n.props.children[0]?.props?.children==='error'&&n.props.children[1]?.type==='pre')
 const errorTone=esect?(esect.props.children[1].props.style.color==='var(--ui-danger, var(--ui-text-tertiary))'?'red':'neutral'):null
 const actual={painted,outcome,title:target.title,classes:[...words].sort(),badge:badges[0]??null,refusal:text(tree).includes('lifetime_cap_spent')?'lifetime_cap_spent':null,errorTone,unavailable:text(tree).includes('Session unavailable'),calls:[...calls]}"""),
):
    assert observer.count(before) == 1, before
    observer = observer.replace(before, after)
(out / 'observe.mjs').write_text(observer)
write(out / 'cases.json', CASES)
rc = subprocess.run(['node', str(out / 'observe.mjs'), str(repo / 'desktop/plugin.js'),
                     str(out), str(out / 'cases.json')], timeout=30).returncode
if failures:
    print('\n'.join(failures), file=sys.stderr)
sys.exit(1 if failures or rc else 0)
