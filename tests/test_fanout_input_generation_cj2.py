"""GENERATION LAW (bd_2026-11-13-cj2, CJ2 product writer): the value a fan-out
child is DISPATCHED with is captured at spawn under its own fresh execution key,
and a pre-aggregate row's identity resolves by matching the record's OWN base
key into that capture — never by re-walking the ancestor's current output.

Ported writer legs (choose_cj2_generation_law/probe.py 'writer-*' and
samedef_cj2.py legs D/R, as CANDIDATE greens — the original drivers pinned the
defect, this one pins the fix). All offline; only the model transport is
substituted (AGENTS.md: transport substitution lives in the bench). Real
runners (wf.main), real door amend/redrive writers, the real dashboard
_view(full=True), and the UNCHANGED vendored panel observer (tests/
observe_outcome_cj2.mjs, in-memory-extended by the committed four-field
harness) as judge.

Legs:
  writer-<form>   agent producer, A→B→A through REAL door amendments:
                  A commits Amber/Quartz; B returns the empty roster plus an
                  on_fail fallback (old item record byte-identical across B);
                  A' restores the producer def — matched producer EFP,
                  UNEQUAL full producer skeys — and re-expands Quartz/Amber,
                  whose aggregate (the fanout_empty death) is UNUSABLE.
                  Pre-aggregate at A' the retained capture paints Amber and
                  opens ONLY the old exact chat; releasing only item 0 yields
                  Quartz/'review Quartz'/done/one new id with the sibling
                  still parked and the stale old chat still landable.
  own-delete      the runner's own named same-definition recovery (delete the
                  producer record, wait to re-drive): re-expansion rides R2
                  while the old capture keeps the old record Amber; settled
                  rows carry R2.
  own-redrive     ordinary act_redrive preserves the partial producer; the
                  re-drive rides the PRESERVED roster with its exact old pair.
  seam-dict       timing NEGATIVE: an injected mid-view head/graph swap at the
                  _events seam may not relabel (capture law) and may not
                  damage the shipped revision; restoring disk reads verbatim.
  corrupt         fresh runner-written evidence, then carriers removed or
                  corrupted with the exact record intact: mismatched key,
                  wrong index, foreign run, malformed version, item:null vs
                  missing, ordinal/blank tooltip beside the independently
                  proven chat; a same-key correction (#a0 older, #a1 the
                  record's attempt): deleting the exact current title is
                  ZERO calls (no escalation to the older row), restoring it
                  is ONE call; the parked sibling keeps its own binding.
  pubfail         simulated publication failure (read-only capture dir): the
                  spawn and every canonical fact land; only the label is lost.
  adopt-ev/-no    verified adoption (active_child/_adopt_child seams stand in
                  for the live-orphan process management the orphan fixture
                  pins) under a bench-swapped same-EFP R2 roster: with
                  retained evidence the adopted aggregate row rides its
                  CAPTURED input, never the newly enumerated value; without,
                  the item stands unproved — and adoption writes no new key.
  unit            the writer law called directly: same-key re-drive reuses
                  the capture; a fresh nonce captures separately; at most two
                  keys per index (retained record + pending launch); out of
                  scope, unrepresentable/over-cap, malformed and
                  wrong-version are absent, never reassigned; keys are
                  bounded by retained canonical indices plus live width.

Usage: python3.14 -B tests/test_fanout_input_generation_cj2.py [fresh-dir]
Exit 0 only with every wrapper check green AND the observer behavior-green
(`observer exit <rc>` printed, distinct from this wrapper's exit).
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / 'tests'))
OBSERVER = repo / 'tests/observe_outcome_cj2.mjs'
TICK = 0.02
WAIT_S = 40

R1 = ['Amber', 'Quartz']
R2 = ['Quartz', 'Amber']


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, repo / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sid(run, phase, nid, index):
    return 'local-' + hashlib.sha256(
        f'cj2-gen-law:{run}:{phase}:{nid}:{index}'.encode()).hexdigest()


def shaped(form, colors):
    return {'items': colors} if form == 'dict' else [colors]


def wait_for(predicate, proc=None, limit=WAIT_S):
    end = time.monotonic() + limit
    while not predicate():
        assert time.monotonic() < end and (proc is None or proc.poll() is None), 'bounded wait expired'
        time.sleep(TICK)


def raw_json(path):
    return json.loads(Path(path).read_text())


# ------------------------------------------------------------------ engine --
# ONE spawn (attempt 0) per item except the corrupt leg, whose record names
# `#a1` (a correction advanced the attempt INSIDE one skey) while both exact
# rows exist — the capture law covers a key, not an attempt. Park markers are
# RUN-SCALED: <run>.<tag>.parked / <run>.<tag>.rel.
if len(sys.argv) > 3 and sys.argv[2] == 'engine':
    out, runname, form, phase = Path(sys.argv[1]).resolve(), sys.argv[3], sys.argv[4], sys.argv[5]
    wf = load('gen_law_engine', 'wf.py')

    def transport(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        nid = node['id']
        with sqlite3.connect(out / 'home/state.db') as db:
            db.execute('insert or replace into sessions values ('
                       + ','.join('?' for _ in range(15)) + ')',
                       (sid(runname, phase, nid, index), f'{skey}#a0', 'fake',
                        1, 1, 0, 0, 1, 1, 0, time.time(), 1, 'fixture', 2, 0))

        def park(tag):
            (out / f'{runname}.{tag}.parked').touch()
            wait_for((out / f'{runname}.{tag}.rel').exists)

        if nid == 'prep':
            assert index is None
            if phase == 'redriven':
                (out / f'{runname}.prep-re-ran').touch()   # must NOT happen (leg R)
                return dict(skey=skey, spawn=0, ms=1, attempts=1, status='partial',
                            output=shaped(form, R1), error_class='timeout')
            if phase == 'failA':                    # harvest-bearing partial (the #4/#256 shape)
                return dict(skey=skey, spawn=0, ms=1, attempts=1, status='partial',
                            output=shaped(form, R1), error_class='timeout')
            colors = {'old': R1, 'delA': R1, 'delB': R2, 'restored': R2, 'middle': []}[phase]
            return dict(skey=skey, spawn=0, ms=1, attempts=1, status='done',
                        output=shaped(form, colors))
        if nid == 'fallback':
            return dict(skey=skey, spawn=0, ms=1, attempts=1, status='done',
                        output={'result': 'fallback handled'})
        assert node['id'] == 'review' and index in (0, 1)
        if phase == 'failA':                      # the redrive fixture's death era
            if index == 1:
                return dict(skey=skey, spawn=0, ms=1, attempts=1, status='failed',
                            error_class='forbidden_model', error='served a forbidden model')
            return dict(skey=skey, spawn=0, ms=1, attempts=1, status='done',
                        output={'result': f'{goal} ok'})
        want = R1 if phase in ('old', 'delA', 'redriven', 'corrupt') else R2
        assert goal == f'review {want[index]}', \
            f'{phase} item{index} goal {goal!r} — expansion rode a foreign roster'
        if phase == 'corrupt':
            with sqlite3.connect(out / 'home/state.db') as db:
                db.execute('insert or replace into sessions values ('
                           + ','.join('?' for _ in range(15)) + ')',
                           (sid(runname, phase + 'x', nid, index), f'{skey}#a1', 'fake',
                            1, 1, 0, 0, 1, 1, 0, time.time() + 10, 1, 'fixture', 2, 0))
            if index == 1:
                park('item1')
            return dict(skey=skey, spawn=1, ms=1, attempts=2, status='done',
                        output={'result': f'{goal} ok'})
        if (phase, index) in (('old', 1), ('delA', 1), ('delB', 0),
                              ('restored', 0), ('restored', 1),
                              ('redriven', 0), ('adopt-ev', 1), ('adopt-no', 1)):
            park(f'{phase}.item{index}')
        return dict(skey=skey, spawn=0, ms=1, attempts=1, status='done',
                    output={'result': f'{goal} ok'})

    if phase in ('adopt-ev', 'adopt-no'):
        live_pid = int(sys.argv[6])

        def active_child(run, node, byid, i):
            if node['id'] == 'review' and i == 0:
                rec = raw_json(run / 'nodes' / 'review.0.json')
                return {'pid': live_pid, 'skey': rec['skey'] + '#a0',
                        'started': rec.get('started', 'now'),
                        'log_path': rec.get('log_path', str(run / 'x.log'))}
            return None

        def adopt(meta, node, byid, i, child, schema, fo_cancel=None):
            return dict(status='done', output={'result': 'adopted harvest'},
                        skey=child['skey'].split('#a', 1)[0], spawn=0, attempts=1,
                        ms=1, adopted=True, harvested=True)
        wf.active_child = active_child
        wf._adopt_child = adopt

    with patch.object(wf, 'run_child', transport), patch.object(wf, 'notify', return_value=None):
        wf.main(runname)
    sys.exit(0)

# ------------------------------------------------------------------ setup --
out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(
    tempfile.mkdtemp(prefix='cj2-input-generation-'))
out.mkdir(exist_ok=True)
for key in tuple(os.environ):
    if key.startswith(('HERMES_', 'WF_', 'FAKE_', 'WORKFLOW_')):
        del os.environ[key]
home, runs = out / 'home', out / 'runs'
home.mkdir(exist_ok=True); runs.mkdir(exist_ok=True)
os.environ.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
                  TMPDIR=str(out), PYTHONDONTWRITEBYTECODE='1', WORKFLOW_MAX_SEATS='0')
# The alias/tier values are INERT fixture payload — the behavior under test
# reads none of them — so they carry a public-neutral stub model instead of a
# vendor route (Core-10 model-alias law: shipped examples name no vendor).
(home / 'config.yaml').write_text('model:\n  default: stub-model\n'
                                  '  aliases:\n    stub: stub-model\n')
with sqlite3.connect(home / 'state.db') as db:
    db.execute('create table sessions (id text primary key, title text, model text, input_tokens int, '
               'output_tokens int, cache_read_tokens int, reasoning_tokens int, '
               'api_call_count int, tool_call_count int, estimated_cost_usd real, started_at real, '
               'last_activity_at real, last_activity_description text, ended_at real, expiry_finalized int)')
api = load('gen_law_api', 'dashboard/plugin_api.py')
wc = api._workflow_common()
door = load('gen_law_door', '__init__.py')
import wf_test_isolation as _iso
_iso.install(door)
import wf as wfmod          # in-process writer for the unit leg (same files)


class Ctx:
    def __init__(self, t): self.t = t
    def get_config(self, k, d=None): return self.t if k == 'models' else d


door._CTX = Ctx({'worker': 'stub-model', 'manager': 'stub-model', 'frontier': 'stub-model'})
door._ping_route_once = lambda provider, model: {'liveness': 'unknown'}
door._route_liveness_ping = lambda *a, **k: []
failures = []


def check(ok, why):
    print(f'ok: {why}' if ok else f'FAIL: {why}')
    if not ok:
        failures.append(why)


def write(path, x):
    path.write_text(json.dumps(x, indent=2))


def mk_run(name, graph_nodes, conc=1):
    r = runs / name
    (r / 'nodes').mkdir(parents=True)
    write(r / 'run.json', {'name': name, 'item_concurrency': conc})
    write(r / 'graph.json', {'name': name, 'nodes': graph_nodes})
    return r


def launch(runname, form, phase, extra=()):
    log = open(out / f'{runname}.{phase}.engine.log', 'w')
    return subprocess.Popen([sys.executable, '-B', __file__, str(out), 'engine',
                             runname, form, phase, *extra], stdout=log, stderr=subprocess.STDOUT)


PRODUCER = {'id': 'prep', 'type': 'agent', 'goal': 'list two colors', 'max_turns': 65, 'timeout': 1500}
REVIEW = {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65,
          'timeout': 1500, 'after': ['prep']}


def amend(runname, goal):
    with patch.object(door, '_respawn_runner', lambda r: None):
        res = door.act_amend({'run_id': runname, 'patch': {'nodes': {'prep': {'goal': goal}}}})
    check(res.get('ok') and {'prep', 'review'} <= set(res.get('will_rerun') or []),
          f'{runname}: the door committed the amend (will_rerun {res.get("will_rerun")})')


def sidecar(r, nid='review'):
    return raw_json(r / 'fanout-inputs' / f'{nid}.json')


def slots_of(doc, index):
    entry = (doc.get('items') or {}).get(str(index)) or {}
    return [s for s in (entry.get('current'), entry.get('pending')) if s]


CASES = []


def expect(painted, outcome, title, classes, badge, refusal, error_tone, dest):
    return dict(painted=painted, outcome=outcome, title=title, classes=classes,
                badge=badge, refusal=refusal, errorTone=error_tone,
                unavailable=dest is None,
                calls=[] if dest is None else [['openSession', dest, {'intent': 'in-place'}]])


def case(name, view, index, *allowed):
    CASES.append(dict(name=name, view=view, node='review', index=index, allowed=allowed))


def row0(view):
    return view['nodes']['review']['item_metrics'][0]


# ======================================================== leg 1: writer A→B→A
for form in ('dict', 'list'):
    ref = 'prep.items' if form == 'dict' else 'prep.0'
    r = mk_run('writer-' + form, [
        PRODUCER,
        dict(REVIEW, on_fail='fallback', fanout={'items_from': ref, 'goal': 'review {item}'}),
        {'id': 'fallback', 'type': 'agent', 'goal': 'handle empty fanout', 'after': ['review']}],
        conc=2)                       # era A' parks BOTH items — a serial wave would serialize parks
    item0, head = r / 'nodes/review.0.json', r / 'nodes/prep.json'
    p = launch(r.name, form, 'old')
    old_id = sid(r.name, 'old', 'review', 0)
    wait_for(lambda: (out / f'{r.name}.old.item1.parked').exists() and item0.is_file()
             and raw_json(item0).get('status') == 'done', p)
    check(not (r / 'nodes/review.json').exists(), f'{form}: the era-A witness is pre-aggregate')
    vA = api._view(r, full=True)
    check(row0(vA).get('item') == 'Amber' and row0(vA).get('session_current') == old_id,
          f'{form}: era A names the dispatched value from the runner-written capture')
    docA = sidecar(r)
    rec0 = raw_json(item0)
    s0 = slots_of(docA, 0)
    check(len(s0) == 1 and s0[0]['skey'] == rec0['skey'] and s0[0]['item'] == 'Amber',
          f"{form}: the capture is keyed by the record's OWN full base skey")
    case(f'{form}/writer-A-parked', vA, 0,
         expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, old_id))
    case(f'{form}/writer-A-sibling', vA, 1,
         expect('#1', 'pending', 'review ', [], 'pending', None, None, sid(r.name, 'old', 'review', 1)))
    (out / f'{r.name}.old.item1.rel').touch()
    assert p.wait(timeout=20) == 0
    old_head = raw_json(head)
    old_item = item0.read_bytes()                      # the B-barrier comparator

    amend(r.name, 'list two other colors')             # B: empty roster + named fallback
    check(launch(r.name, form, 'middle').wait(timeout=25) in (0, 1), f'{form}: the B boot ended')
    check(item0.read_bytes() == old_item,
          f'{form}: B (zero-item expansion) left the old item record byte-identical')
    check('fanout_empty' in (r / 'events.jsonl').read_text(),
          f'{form}: B died typed fanout_empty and the named fallback owned the death')
    check(not (r / 'abort.json').exists(), f'{form}: an else-arm expansion sets no run flag')
    mid = raw_json(r / 'nodes/review.json')
    check(mid['status'] == 'skipped' and mid.get('caught_error_class') == 'fanout_empty'
          and (mid.get('output') or {}).get('all_results') is None,
          f'{form}: the B aggregate names no rows (on_fail translated the zero-item death)')

    amend(r.name, 'list two colors')                   # A': def restored, output swapped
    p2 = launch(r.name, form, 'restored')
    wait_for(lambda: (out / f'{r.name}.restored.item0.parked').exists()
             and (out / f'{r.name}.restored.item1.parked').exists(), p2)
    g = raw_json(r / 'graph.json')
    byid = {n['id']: n for n in g['nodes']}
    fresh_head = raw_json(head)
    check(wc.node_rec(r, byid['review'], byid)[0] == 'pending',
          f"{form}: the B aggregate is UNUSABLE under A' — the record join is the only authority")
    check(fresh_head['efp'] == old_head['efp'] and fresh_head['skey'] != old_head['skey'],
          f'{form}: A-restored MATCHES the producer EFP while its full skey is unequal')
    check(item0.read_bytes() == old_item,
          f"{form}: the old item is byte-identical across B up to the A' barrier")
    vP = api._view(r, full=True)
    check(row0(vP).get('item') == 'Amber' and row0(vP).get('session_current') == old_id,
          f'{form}: the retained pre-aggregate capture paints Amber and opens ONLY the old exact chat')
    sP = slots_of(sidecar(r), 0)
    vals = {s['skey']: s['item'] for s in sP}
    check(len(sP) == 2 and vals.get(rec0['skey']) == 'Amber'
          and any(k != rec0['skey'] and v == 'Quartz' for k, v in vals.items()),
          f"{form}: A' captured separately under the fresh key; ≤2 slots, the OLD key never reassigned")
    case(f'{form}/writer-Aprime-parked', vP, 0,
         expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, old_id))
    (out / f'{r.name}.restored.item0.rel').touch()
    wait_for(lambda: item0.read_bytes() != old_item and raw_json(item0).get('status') == 'done', p2)
    rowF = row0(api._view(r, full=True))
    new_id = sid(r.name, 'restored', 'review', 0)
    check(rowF.get('item') == 'Quartz' and rowF.get('session_current') == new_id
          and rowF.get('session_display') == {'status': 'done'}
          and (rowF.get('session_ids') or [new_id])[-1] == new_id,
          f'{form}: the released item 0 names ONLY its own new exact id (chronology: newest last)')
    with sqlite3.connect(home / 'state.db') as db:
        stale = db.execute('select count(*) from sessions where id=?', (old_id,)).fetchone()[0]
    check(stale == 1, f'{form}: the stale old chat remains landable history (absence legs stay separate)')
    case(f'{form}/writer-Aprime-fresh-item', api._view(r, full=True), 0,
         expect('Quartz', 'done', 'review Quartz', [], 'Finished', None, None, new_id))
    # The sibling's OWN era-A row: its committed record (item 1 of era A was
    # Quartz) keeps its captured label and era-A chat under A' — no sibling
    # knowledge transfer, no borrowed new-era label.
    case(f'{form}/writer-Aprime-sibling-parked', api._view(r, full=True), 1,
         expect('Quartz', 'done', 'review Quartz', [], 'Finished', None, None,
                sid(r.name, 'old', 'review', 1)))
    (out / f'{r.name}.restored.item1.rel').touch()
    assert p2.wait(timeout=20) == 0
    settled = raw_json(r / 'nodes/review.json')
    check([x.get('item') for x in settled['output']['all_results']] == ['Quartz', 'Amber'],
          f'{form}: the settled aggregate publishes the roster the records expanded from')

# ==================================================== leg 2: same-def delete-and-wait
r = mk_run('own-delete', [PRODUCER, dict(REVIEW, fanout={'items_from': 'prep.items', 'goal': 'review {item}'})])
item0 = r / 'nodes/review.0.json'
p = launch(r.name, 'dict', 'delA')
old_id = sid(r.name, 'delA', 'review', 0)
wait_for(lambda: (out / f'{r.name}.delA.item1.parked').exists() and item0.is_file(), p)
V0 = api._view(r, full=True)
check(row0(V0).get('item') == 'Amber', 'leg D: the positive control ships its coherent pair before the recovery')
case('samedef/v0-boot-positive', V0, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, old_id))
p.send_signal(signal.SIGKILL); assert p.wait(timeout=10) != 0
gsha = (r / 'graph.json').read_bytes()
d_pre = raw_json(r / 'nodes/prep.json')
(r / 'nodes/prep.json').unlink()                                   # the recovery the runner names
p = launch(r.name, 'dict', 'delB')
wait_for(lambda: (out / f'{r.name}.delB.item0.parked').exists(), p)
VD1 = api._view(r, full=True)
check(row0(VD1).get('item') == 'Amber' and row0(VD1).get('session_current') == old_id,
      "leg D: the re-drive replaced the PRODUCER, not the old record's captured input")
check((r / 'graph.json').read_bytes() == gsha, 'leg D: the same-def re-drive moved no def bytes')
case('samedef/vd1-delete-and-wait-must-not-relabel', VD1, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, old_id))
(out / f'{r.name}.delB.item0.rel').touch()
assert p.wait(timeout=25) == 0
prep2 = raw_json(r / 'nodes/prep.json')
check(prep2['efp'] == d_pre['efp'] and prep2['output'] == shaped('dict', R2)
      and prep2['skey'] != d_pre['skey'],
      'leg D: the producer OUTPUT was replaced under byte-identical EFP and a fresh skey')
VD2 = api._view(r, full=True)
case('samedef/vd2-settled-own-record-owns-pair', VD2, 0,
     expect('Quartz', 'done', 'review Quartz', [], 'Finished', None, None, sid(r.name, 'delB', 'review', 0)))

# ==================================================== leg 3: ordinary act_redrive preserve
r = mk_run('own-redrive', [PRODUCER, dict(REVIEW, after_partial=True,
                                          fanout={'items_from': 'prep.items', 'goal': 'review {item}'})])
check(launch(r.name, 'dict', 'failA').wait(timeout=25) in (0, 1), 'leg R: the fixture run ended failed')
check(api._view(r, full=True)['status'] == 'failed', 'leg R: one forbidden leg failed the run')
prep_r = r / 'nodes/prep.json'
prep_sha = prep_r.read_bytes()
respawner = []
door._respawn_runner = lambda run: respawner.append(run)
resp = door.act_redrive({'run_id': r.name})
check(resp.get('ok') and resp.get('mode') == 'same-fingerprint-resume'
      and resp.get('re_drive') == ['review'],
      f'leg R: the door re-drives only the failed lane ({resp.get("re_drive")})')
check(prep_r.read_bytes() == prep_sha, 'leg R: act_redrive PRESERVES the partial producer receipt byte-identical')
p = launch(r.name, 'dict', 'redriven')
wait_for(lambda: (out / f'{r.name}.redriven.item0.parked').exists(), p)
RV1 = api._view(r, full=True)
check(row0(RV1).get('item') == 'Amber' and row0(RV1).get('session_current') == sid(r.name, 'failA', 'review', 0),
      'leg R: the ordinary re-drive rides the preserved roster — coherent old pair, no relabel')
case('samedef/legR-redrive-preserved-coherent', RV1, 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid(r.name, 'failA', 'review', 0)))
(out / f'{r.name}.redriven.item0.rel').touch()
assert p.wait(timeout=25) == 0
check(not (out / f'{r.name}.prep-re-ran').exists(), 'leg R: the producer was never re-driven')

# ==================================================== leg 4: injected _events timing negative
r = mk_run('seam-dict', [
    {'id': 'prep', 'type': 'echo', 'output': shaped('dict', R1)},
    dict(REVIEW, fanout={'items_from': 'prep.items', 'goal': 'review {item}'})])
item0, head = r / 'nodes/review.0.json', r / 'nodes/prep.json'
p = launch(r.name, 'dict', 'old')
wait_for(lambda: (out / f'{r.name}.old.item1.parked').exists() and item0.is_file(), p)
item_bytes, head_bytes = item0.read_bytes(), head.read_bytes()
a_graph = raw_json(r / 'graph.json')
orig_events = api._events


def inject_mid_view(run):
    assert run == r and not (r / 'nodes/review.json').exists()
    swapped = {**raw_json(head), 'output': shaped('dict', R2)}   # bench write, labeled
    b = json.loads(json.dumps(a_graph)); b['nodes'][0]['output'] = shaped('dict', R2)
    tmp = (r / 'graph.json').with_name('g.tmp'); tmp.write_text(json.dumps(b)); tmp.replace(r / 'graph.json')
    tmp = head.with_name('h.tmp'); tmp.write_text(json.dumps(swapped)); tmp.replace(head)
    return orig_events(run)


with patch.object(api, '_events', inject_mid_view):
    VJ = api._view(r, full=True)
check(row0(VJ).get('item') == 'Amber' and row0(VJ).get('session_current') == sid(r.name, 'old', 'review', 0),
      'seam: an INJECTED mid-view head swap may not relabel the frozen record — timing alone proves nothing')
check(VJ['graph']['nodes'][0]['output'] == shaped('dict', R1),
      'seam: the shipped revision is the captured one regardless of the mid-view swap')
(r / 'graph.json').write_text(json.dumps(a_graph)); head.write_bytes(head_bytes)
check(row0(api._view(r, full=True)).get('item') == 'Amber',
      'seam: after restoring disk the same pair stands — the negative injected nothing durable')
(out / f'{r.name}.old.item1.rel').touch()
assert p.wait(timeout=20) == 0

# ==================================================== leg 5: corrupt carriers on fresh evidence
r = mk_run('corrupt', [
    {'id': 'prep', 'type': 'echo', 'output': shaped('dict', R1)},
    dict(REVIEW, fanout={'items_from': 'prep.items', 'goal': 'review {item}'})])
item0 = r / 'nodes/review.0.json'
p = launch(r.name, 'dict', 'corrupt')
wait_for(lambda: (out / f'{r.name}.item1.parked').exists() and item0.is_file(), p)
rec = raw_json(item0)
side_path = r / 'fanout-inputs/review.json'
good = side_path.read_bytes()
base_key = rec['skey']
att1 = sid(r.name, 'corruptx', 'review', 0)          # the record's attempt (#a1)
att0 = sid(r.name, 'corrupt', 'review', 0)           # the superseded (#a0) — never escalates

side_path.write_bytes(json.dumps({'version': 1, 'items': {'0': {'current': {
    'skey': base_key.rsplit('.', 1)[0] + '.ffffff', 'item': 'Amber'}}}}).encode())
check('item' not in row0(api._view(r, full=True)), 'corrupt: a mismatched key is UNPROVED, not a label')
side_path.write_bytes(json.dumps({'version': 1, 'items': {'1': {'current': {'skey': base_key, 'item': 'Amber'}}}}).encode())
check('item' not in row0(api._view(r, full=True)), 'corrupt: a wrong index proves nothing for this claim')
side_path.write_bytes(json.dumps({'version': 1, 'items': {'0': {'current': {
    'skey': base_key.replace(f'wf:{r.name}:', 'wf:other-run:'), 'item': 'Amber'}}}}).encode())
check('item' not in row0(api._view(r, full=True)), "corrupt: a foreign run's key is not this run's evidence")
side_path.write_bytes(json.dumps({'version': 2, 'items': {'0': {'current': {'skey': base_key, 'item': 'Amber'}}}}).encode())
check('item' not in row0(api._view(r, full=True)), 'corrupt: a malformed version reads as absence')
side_path.write_text(json.dumps({'version': 1, 'items': {'0': {'current': {'skey': base_key, 'item': None}}}}))
rn = row0(api._view(r, full=True))
check('item' in rn and rn['item'] is None and rn.get('session_current') == att1,
      'corrupt: a captured JSON null IS a present item: null, bound to its exact chat')
side_path.unlink()
V = api._view(r, full=True)
check('item' not in row0(V) and row0(V).get('session_current') == att1,
      'corrupt: no carrier, no label — the independently proven chat still binds '
      '(A2c absence law on fresh evidence: ordinal chip, blank item tooltip)')
case('corrupt/carrier-gone-ordinal-tooltip-exact-chat', V, 0,
     expect('#0', 'done', 'review ', [], 'Finished', None, None, att1))
case('corrupt/sibling-keeps-own-binding', V, 1,
     # the parked sibling has no record — the fold's own last-entry law names
     # its chat; the #a1 corruptx row (started later) is the last entry.
     expect('#1', 'pending', 'review ', [], 'pending', None, None, sid(r.name, 'corruptx', 'review', 1)))
with sqlite3.connect(home / 'state.db') as db:
    db.execute('delete from sessions where title=?', (f'{base_key}#a1',))
V = api._view(r, full=True)
check(row0(V).get('session_current') is None,
      'corrupt: the exact current row is gone — the older #a0 does NOT escalate (no legacy fallback)')
case('corrupt/exact-row-deleted-zero-calls', V, 0,
     expect('#0', 'done', 'review ', [], 'Finished', None, None, None))
side_path.write_bytes(good)
with sqlite3.connect(home / 'state.db') as db:
    db.execute('insert into sessions values (' + ','.join('?' for _ in range(15)) + ')',
               (att1, f'{base_key}#a1', 'fake', 1, 1, 0, 0, 1, 1, 0, time.time() + 10, 1, 'fixture', 2, 0))
case('corrupt/restored-one-call', api._view(r, full=True), 0,
     expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, att1))
(out / f'{r.name}.item1.rel').touch()
assert p.wait(timeout=20) == 0
check('Amber' not in (r / 'events.jsonl').read_text(),
      'journal hygiene: no captured value ever entered the event stream')

# ==================================================== leg 6: publication failure loses evidence
r = mk_run('pubfail', [PRODUCER, dict(REVIEW, fanout={'items_from': 'prep.items', 'goal': 'review {item}'})])
(r / 'fanout-inputs').mkdir()
os.chmod(r / 'fanout-inputs', 0o500)
p = launch(r.name, 'dict', 'old')
wait_for(lambda: (out / f'{r.name}.old.item1.parked').exists(), p)
check(not (r / 'fanout-inputs/review.json').exists(),
      'pubfail: the capture failed loudly-quiet — every bail path cleaned up its tmp')
VP = api._view(r, full=True)
check('item' not in row0(VP)
      and row0(VP).get('session_current') == sid(r.name, 'old', 'review', 0),
      'pubfail: pre-aggregate the row reads unproved, never guessed, beside its exact chat')
case('pubfail/preaggregate-unproved', VP, 0,
     expect('#0', 'done', 'review ', [], 'Finished', None, None, sid(r.name, 'old', 'review', 0)))
(out / f'{r.name}.old.item1.rel').touch()
check(p.wait(timeout=25) == 0, 'pubfail: the runner completed despite the unwritable capture')
os.chmod(r / 'fanout-inputs', 0o755)
check(raw_json(r / 'nodes/review.0.json')['status'] == 'done',
      'pubfail: an unwritable capture lost LABEL evidence only — the record and the verdict stand')
agg_rows = raw_json(r / 'nodes/review.json')['output']['all_results']
check([x.get('item') for x in agg_rows] == ['Amber', 'Quartz'],
      'pubfail: the settled first-wave aggregate stays canonical (its rows were materialized WITH the records)')

# ==================================================== leg 7: adoption, ±retained evidence
for keep, tag in ((True, 'adopt-ev'), (False, 'adopt-no')):
    r = mk_run(tag, [PRODUCER, dict(REVIEW, fanout={'items_from': 'prep.items', 'goal': 'review {item}'})])
    p = launch(tag, 'dict', 'old')
    wait_for(lambda: (out / f'{tag}.old.item1.parked').exists() and (r / 'nodes/review.0.json').is_file(), p)
    (out / f'{tag}.old.item1.rel').touch()
    assert p.wait(timeout=20) == 0
    rec = raw_json(r / 'nodes/review.0.json')
    base_key, era_chat = rec['skey'], sid(tag, 'old', 'review', 0)
    (r / 'nodes/review.json').unlink()                              # bench: pre-aggregate again
    prep_rec = raw_json(r / 'nodes/prep.json')
    tmp = (r / 'nodes/prep.json').with_name('prep.tmp')             # same-EFP roster replacement
    tmp.write_text(json.dumps({**prep_rec, 'output': shaped('dict', R2)}))
    tmp.replace(r / 'nodes/prep.json')
    item0 = r / 'nodes/review.0.json'
    orphan = {k: v for k, v in rec.items() if k not in ('output', 'committed_at', 'receipt_vs_parent')}
    orphan.update(status='running', pid=os.getpid(), started='2026-11-25T00:00:00+00:00',
                  log_path=str(r / 'logs/legacy.log'), spawn_cmd=['true'])
    item0.write_text(json.dumps(orphan))
    side = r / 'fanout-inputs/review.json'
    if not keep:
        side.unlink()                                               # simulated capture loss
    launch_pid = os.getpid()                                        # verified-live stand-in pid
    p = launch(tag, 'dict', tag, (str(launch_pid),))
    wait_for(lambda: (out / f'{tag}.{tag}.item1.parked').exists()
             and raw_json(item0).get('status') == 'adopted', p)
    vA = api._view(r, full=True)
    rowA = row0(vA)
    doc = raw_json(side) if side.is_file() else {'items': {}}
    check(len(slots_of(doc, 0)) == (1 if keep else 0),
          f'{tag}: adoption recorded no new key under the adopted claim')
    if keep:
        check(rowA.get('item') == 'Amber' and rowA.get('session_current') == era_chat,
              f'{tag}: the adopted pre-aggregate row rides its RETAINED capture and exact chat')
    else:
        check('item' not in rowA and rowA.get('session_current') == era_chat,
              f'{tag}: without retained capture the adopted row is unnamed beside its proven chat')
    (out / f'{tag}.{tag}.item1.rel').touch()
    assert p.wait(timeout=25) == 0
    rows = raw_json(r / 'nodes/review.json')['output']['all_results']
    if keep:
        check(rows[0].get('item') == 'Amber',
              f'{tag}: the adopted aggregate row rode the CAPTURE, never the newly enumerated value')
        case(f'{tag}/settled-adopted-row-keeps-captured-label', api._view(r, full=True), 0,
             expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, era_chat))
    else:
        check('item' not in rows[0],
              f'{tag}: with no retained capture the adopted item stands UNPROVED in the aggregate')
        case(f'{tag}/settled-adopted-row-unproved', api._view(r, full=True), 0,
             expect('#0', 'done', 'review ', [], 'Finished', None, None, era_chat))
    check(rows[1].get('item') == 'Amber',
          f'{tag}: the freshly spawned sibling rides ITS OWN capture (index 1 of the replaced roster)')
    check(raw_json(r / 'nodes/review.0.json')['status'] == 'adopted',
          f'{tag}: the adopted item record retired to adopted — no re-adoption window')

# ==================================================== leg 8: the writer law, called directly
unit = out / 'unit-run'
unit.mkdir()
(unit / 'nodes').mkdir()
u_lock = threading.Lock()
unode = {'id': 'review'}


def key_at(index, nonce):
    return f'wf:unit-run:review:{index}:{nonce}'


def cap(index, skey, item, width=2):
    wfmod.capture_fanout_input(unit, u_lock, unode, index, skey, item, width)


cap(0, key_at(0, 'aaa111'), 'Amber')
cap(0, key_at(0, 'aaa111'), 'Quartz')                                # same-key retry
doc = sidecar(unit)
check(len(slots_of(doc, 0)) == 1 and slots_of(doc, 0)[0]['item'] == 'Amber',
      'unit: a same-key re-drive reuses the captured input (spawn numbers are not input identities)')
write(unit / 'nodes/review.0.json', {'skey': key_at(0, 'aaa111'), 'status': 'done'})
cap(0, key_at(0, 'bbb222'), 'Quartz')
vals = {s['skey']: s['item'] for s in slots_of(sidecar(unit), 0)}
check(vals == {key_at(0, 'aaa111'): 'Amber', key_at(0, 'bbb222'): 'Quartz'},
      'unit: replacement kept exactly the retained record key plus the pending launch (≤2)')
cap(0, key_at(0, 'ccc333'), 'Onyx')
vals = {s['skey']: s['item'] for s in slots_of(sidecar(unit), 0)}
check(vals == {key_at(0, 'aaa111'): 'Amber', key_at(0, 'ccc333'): 'Onyx'},
      'unit: the superseded key was DISCARDED — no retry/era history')
cap(0, key_at(0, 'ddd444'), 'x' * 200_000)                           # clips past the slot cap
vals = {s['skey']: s['item'] for s in slots_of(sidecar(unit), 0)}
check(set(vals) == {key_at(0, 'aaa111'), key_at(0, 'ccc333')},
      'unit: an unrepresentable/over-cap value is absent; the artifact otherwise stands')
cap(0, key_at(0, 'eee555'), None)
vals = {s['skey']: s['item'] for s in slots_of(sidecar(unit), 0)}
check(vals.get(key_at(0, 'eee555')) is None and key_at(0, 'aaa111') in vals,
      'unit: a captured null is present-null; the retained key survives beside it')
cap(9, key_at(9, 'fff666'), 'Wide')                                  # width 2: own index always admissible
check('9' in sidecar(unit)['items'], 'unit: the pending launch index is captured')
cap(7, key_at(7, 'ggg777'), 'Retained')
write(unit / 'nodes/review.7.json', {'skey': key_at(7, 'ggg777'), 'status': 'done'})
cap(0, key_at(0, 'hhh888'), 'Fresh0')
check('7' in sidecar(unit)['items'] and '9' not in sidecar(unit)['items'],
      'unit: keys are bounded by retained canonical indices plus the current width')
(unit / 'nodes/review.7.json').unlink()
cap(0, key_at(0, 'iii999'), 'Fresh0b')
check('7' not in sidecar(unit)['items'],
      'unit: once the record is gone the orphan index is pruned (no era history)')
before = json.dumps(sidecar(unit), sort_keys=True)
cap(0, 'wf:OTHER:review:0:zzz', 'Foreign')
cap(1, key_at(9, 'jjj000'), 'ForeignIdx')                            # key's own index disagrees
check(json.dumps(sidecar(unit), sort_keys=True) == before,
      'unit: out-of-scope keys (wrong run, wrong index) are never captured')
(unit / 'fanout-inputs/review.json').write_text('{ not json')
cap(1, key_at(1, 'kkk111'), 'Fresh')
check(set(sidecar(unit)['items']) == {'1'},
      'unit: a malformed artifact is replaced fresh — lost evidence, never reassigned onto old keys')
got, val = wc.fanout_input_value(wc.fanout_inputs_read(unit, 'review'), 1, key_at(1, 'kkk111'))
check(got and val == 'Fresh', 'unit: the reader validates exactly what the writer wrote')
got, _ = wc.fanout_input_value({'1': [{'skey': key_at(1, 'x'), 'item': 'A'},
                                      {'skey': key_at(1, 'x'), 'item': 'B'}]}, 1, key_at(1, 'x'))
check(not got, 'unit: one key carrying two values is not evidence — fail closed')

# ---------------------------------------------------------------- observer --
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
                     str(out), str(out / 'cases.json')], timeout=60).returncode
print(f'observer exit {rc}', flush=True)
if failures:
    print('\n'.join(failures), file=sys.stderr)
sys.exit(1 if failures or rc else 0)
