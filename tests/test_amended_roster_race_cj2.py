"""AMENDED-graph roster race (bd_2026-11-13-cj2, which-fan lane): a real
graph amendment may not let the PRE-AGGREGATE panel label a still-valid old
item from the newer roster while the click still opens the old exact chat.

selected-item-proof.md item 4: "In both root forms, also publish the
reordered ancestor after the view captures its graph, while leaving the
selected item valid for that captured graph. The label and tooltip must not
follow the newer roster while the click still opens the older item's exact
chat." Item 2 adds the AMENDED shape: the reorder reaches the roster through
a REAL amendment that rekeys the execution — the door's own writer commits
it (amends.jsonl row + graph.json + graph.amended event + restart.request),
the real runner re-drive commits the new head — plus the INERT amendment as
a positive and the post-rekey selection as "a stale old chat must not open
under a genuinely newer selection".

Two legs per root form (all offline):
  dict root — echo commits {'items': [...]} under 'prep.items';
  list root — echo commits [[...]] under 'prep.0'.

WHAT IS REAL RUNNER SETUP (no patch except the model transport, the same
substitution the committed harness names — AGENTS.md: model transport and
control read timing live in the test bench, never in product code):
  * both runner generations run through wf.main in a subprocess; sessions
    rows, per-item records, journals and the aggregate are product writes;
  * the amendment is applied by the door itself: act_amend(dry_run=False) —
    the same path `workflow amend` takes — so the new graph revision and its
    efp bump are committed by the product writer, not by a hand-rolled
    {**old, 'efp': ...} replacement;
  * the CONTROL, RE-KEYED, SETTLED and INERT views are UNPATCHED real
    api._view reads, and every observer case is judged by the ACTUAL
    NodePanel through the checkout-local vendored observer
    (tests/observe_outcome_cj2.mjs, file bytes unchanged, extended in memory
    ONLY by the four field patches the committed harness applies).

WHAT IS THE DETERMINISTIC PLACEMENT SEAM (race leg only): the bench wraps
the response's _events read — the surviving bind boundary that lands AFTER
this response captured its graph and metrics and BEFORE any item record
binds — so the door's commit and the real re-drive fire AT that seam
INSIDE one _view call, pinning the commit between the response's captured
revision and its per-item bind. (bd_2026-11-13-cj2 input capture retired
the dynamic live-ancestor _fanout_roster lookup this witness first hooked;
the handoff directs this relocation.) The seam controls WHEN the view sees
the commit, never WHO commits it or WHAT is committed; the window it pins
is the production race (owner/queue lane may amend a live run at any
moment), not a harness-only artifact. The door's respawn hop is stubbed
(door._respawn_runner — otherwise the door Popens a detached runner
without the substituted transport) and the harness re-drives the exact
entrypoint that hop execs (wf.main on the same run), so the re-drive stays
the product's.

Expectation at 05ff750e (test-first, red pinned by receipts/ship20-recovery/
cj2-parent-roster-race-05ff750e.hbo_ikq3): the race case is the ONLY red —
the panel paints the newer roster's label ('Quartz' / 'review Quartz') while
the click opens the old item's exact chat, which the observer's allowed set
forbids. Both coherent shapes are accepted and NO particular implementation
is required: the old roster riding the captured revision, or the honest
placeholder label beside the same exact chat.

Usage: python3.14 -B tests/test_amended_roster_race_cj2.py [fresh-dir]
Exit: 0 only with every check green and the observer behavior-green; the
observer's behavior exit is printed as `observer exit <rc>` — it is distinct
from this wrapper's exit.
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

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / 'tests'))
OBSERVER = repo / 'tests/observe_outcome_cj2.mjs'
TICK = 0.02
WAIT_S = 20


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, repo / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sid(form, gen, index):
    return 'local-' + hashlib.sha256(
        f'amended-roster-race:{form}:{gen}:{index}'.encode()).hexdigest()


def wait_for(predicate, proc=None, limit=WAIT_S):
    end = time.monotonic() + limit
    while not predicate():
        assert time.monotonic() < end and (proc is None or proc.poll() is None), 'bounded wait expired'
        time.sleep(TICK)


def raw_json(path):
    # NEVER the patched module jload: seam-internal peeks must see the disk.
    return json.loads(Path(path).read_text())


# ------------------------------------------------------------------ engine --
# The substituted transport: ONE spawn (attempt 0) per item; it lands the
# era's own session row (title is the runner-minted skey + '#a0') and parks
# per policy. Era 0 parks the sibling (the committed harness's parked
# sibling); era 1 parks BOTH items so no aggregate can hide a live label
# failure: item 0 parks through the race and the re-keyed view, item 1 parks
# through the re-keyed view so the per-item join — not the aggregate — is
# what the observer judges there.
if len(sys.argv) > 3 and sys.argv[2] == 'engine':
    out, runname, form, era0_8 = Path(sys.argv[1]).resolve(), sys.argv[3], sys.argv[4], sys.argv[5]
    wf = load('amend_race_engine', 'wf.py')

    def transport(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        assert node['id'] == 'review' and index in (0, 1)
        gen = 0 if era0_8 in skey else 1
        with sqlite3.connect(out / 'home/state.db') as db:
            row = (sid(form, gen, index), f'{skey}#a0', 'fake', 1, 1, 0, 0, 1, 1,
                   0, time.time(), 1, 'fixture', 2, 0)
            db.execute('insert into sessions values (' + ','.join('?' for _ in row) + ')', row)
        if gen == 0 and index == 1:
            (out / f'{form}-gen0-park-1').touch()
            wait_for((out / f'{form}-gen0-release-1').exists)
        if gen == 1:
            (out / f'{form}-gen1-park-{index}').touch()
            wait_for((out / f'{form}-gen1-release-{index}').exists)
        return dict(skey=skey, spawn=0, ms=1, attempts=1, status='done',
                    output={'result': f'{goal} ok'})

    with patch.object(wf, 'run_child', transport), patch.object(wf, 'notify', return_value=None):
        wf.main(runname)
    sys.exit(0)

# ------------------------------------------------------------------ setup --
out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(
    tempfile.mkdtemp(prefix='cj2-amended-roster-'))
out.mkdir(exist_ok=True)
for key in tuple(os.environ):
    if key.startswith(('HERMES_', 'WF_', 'FAKE_', 'WORKFLOW_')):
        del os.environ[key]
home, runs = out / 'home', out / 'runs'
home.mkdir(exist_ok=True); runs.mkdir(exist_ok=True)
os.environ.update(HOME=str(home), HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
                  TMPDIR=str(out), PYTHONDONTWRITEBYTECODE='1', WORKFLOW_MAX_SEATS='0')
# The door's seat, shaped like tests/test_amend_rebake_034849a2.py: act_amend
# re-resolves models for non-frozen nodes; no network is taken anywhere.
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
api = load('amend_race_api', 'dashboard/plugin_api.py')
wc = api._workflow_common()
door = load('amend_race_door', '__init__.py')
import wf_test_isolation as _iso71
_iso71.install(door)                  # #71 r5: door and env resolve the SAME scratch root


class Ctx:                            # model tiers for the door's resolver (rebake pattern)
    def __init__(self, t): self.t = t
    def get_config(self, k, d=None): return self.t if k == 'models' else d


door._CTX = Ctx({'worker': 'stub-model', 'manager': 'stub-model', 'frontier': 'stub-model'})
door._ping_route_once = lambda provider, model: {'liveness': 'unknown'}   # no network
respawns = []
door._respawn_runner = lambda r: respawns.append(Path(r).name)            # harness re-drives wf.main

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


def launch(runname, form, era0_8, era1_8):
    log = open(out / f'{runname}.{era1_8}.engine.log', 'w')
    return subprocess.Popen([sys.executable, '-B', __file__, str(out), 'engine', runname,
                             form, era0_8, era1_8], stdout=log, stderr=subprocess.STDOUT)


def mk_run(name, graph_nodes):
    r = runs / name
    (r / 'nodes').mkdir(parents=True)
    write(r / 'run.json', {'name': name, 'item_concurrency': 1})
    write(r / 'graph.json', {'name': name, 'nodes': graph_nodes})
    return r


def expect(painted, outcome, title, classes, badge, refusal, error_tone, dest):
    """Field ORDER is the observer's actual-object order (strict JSON compare),
    copied from the committed harness so the shapes stay comparable."""
    return dict(painted=painted, outcome=outcome, title=title, classes=classes,
                badge=badge, refusal=refusal, errorTone=error_tone,
                unavailable=dest is None,
                calls=[] if dest is None else [['openSession', dest, {'intent': 'in-place'}]])


CASES = []


def case(name, view, index, *allowed):
    CASES.append(dict(name=name, view=view, node='review', index=index, allowed=allowed))


REVIEW_DEF = {'id': 'review', 'type': 'agent', 'goal': 'review {item}', 'max_turns': 65,
              'timeout': 1500, 'after': ['prep']}
# The amendment: same graph with the ancestor's committed roster REVERSED —
# a definition change B with a different materialized roster (equal defs
# would not establish equal executions; proof matrix item 3).
FORMS = {
    'dict': ({'items': ['Amber', 'Quartz']}, {'items': ['Quartz', 'Amber']}, 'prep.items'),
    'list': ([['Amber', 'Quartz']], [['Quartz', 'Amber']], 'prep.0'),
}

for form, (out0, out1, ref) in FORMS.items():
    runname = f'amend-{form}'
    r = mk_run(runname, [{'id': 'prep', 'type': 'echo', 'output': out0},
                         dict(REVIEW_DEF, fanout={'items_from': ref, 'goal': 'review {item}'})])
    head = r / 'nodes/prep.json'
    item0 = r / 'nodes/review.0.json'
    g0 = raw_json(r / 'graph.json')
    assert not wc.validate_graph_full(g0), f'{form}: gen0 graph must be valid'
    # The era-0 skey names the era-0 fingerprint — computed HERE from the same
    # graph bytes the runner will hash, so the substituted transport can tell
    # generations apart by the skey the PRODUCT minted.
    g0_byid = {n['id']: n for n in g0['nodes']}
    era0_8 = wc.efp(g0_byid, g0_byid['review'])[:8]

    # ---- TRUE RUNNER SETUP, era 0: item 0 commits, sibling parks, NO aggregate.
    p1 = launch(runname, form, era0_8, '-')
    wait_for(lambda: (out / f'{form}-gen0-park-1').exists() and item0.is_file()
             and raw_json(item0).get('status') == 'done', p1)
    assert not (r / 'nodes/review.json').exists()
    old_bytes = item0.read_bytes()
    rec0 = raw_json(item0)
    era0_8 = rec0['efp'][:8]
    control = api._view(r, full=True)
    crows = control['nodes']['review']['item_metrics']
    check('all_results' not in (control['nodes']['review'].get('output') or {}),
          f'{form}: CONTROL witness is a real pre-aggregate read')
    check(crows[0].get('item') == 'Amber' and crows[0].get('session_display') == {'status': 'done'}
          and crows[0].get('session_current') == sid(form, 0, 0),
          f'{form}: CONTROL ships the valid old pair — label, status and the exact chat')
    case(f'{form}/control-amber', control, 0,
         expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid(form, 0, 0)))
    case(f'{form}/control-sibling', control, 1,
         expect('#1', 'pending', 'review ', [], 'pending', None, None, sid(form, 0, 1)))

    # The owner stopped the parked runner; the amendment is now durable truth
    # waiting for its re-drive (act_amend's documented interrupted-run shape).
    p1.kill()
    assert p1.wait(timeout=10) != 0

    new_graph = raw_json(r / 'graph.json')
    for n in new_graph['nodes']:
        if n['id'] == 'prep':
            n['output'] = out1
    assert not wc.validate_graph_full(new_graph), f'{form}: amended graph must be valid'

    # ---- DETERMINISTIC PLACEMENT SEAM: one _view call; at ITS events read
    # (after the graph/metrics capture) the real door commits the amendment
    # and the real runner re-drive lands the new head — before the old
    # item binds. The seam replaces read TIMING only; writers are the product's.
    era0_head_fp = raw_json(head)['efp'][:8]
    orig_events = api._events
    state = {'armed': True, 'proc': None, 'era1_8': None}

    def seam_events(r_):
        if state['armed']:
            state['armed'] = False
            resp = door.act_amend({'run_id': runname, 'graph': json.loads(json.dumps(new_graph)),
                                   'dry_run': False})
            assert resp.get('ok'), f'{form}: the door refused its own amend: {resp}'
            disk = raw_json(r / 'graph.json')
            byid = {n['id']: n for n in disk['nodes']}
            state['era1_8'] = wc.efp(byid, byid['review'])[:8]
            state['proc'] = launch(runname, form, era0_8, state['era1_8'])
            # The re-drive's OWN echo commit must be on disk before the seam
            # falls through to the real events read — bounded, and it fails
            # the wrapper (never the observation) if the product writer stalls.
            wait_for(lambda: head.is_file() and raw_json(head)['efp'][:8] != era0_head_fp,
                     state['proc'])
            assert item0.read_bytes() == old_bytes, f'{form}: the re-drive must leave the old item untouched'
        return orig_events(r_)

    with patch.object(api, '_events', seam_events):
        raced = api._view(r, full=True)
    p2 = state['proc']
    rows = raced['nodes']['review']['item_metrics']
    check(raced['graph']['nodes'][0]['output'] == out0,
          f'{form}: the race view captured the OLD graph — the newer ancestor landed AFTER the capture')
    check('all_results' not in (raced['nodes']['review'].get('output') or {}),
          f'{form}: RACE witness is a real pre-aggregate read')
    check(item0.read_bytes() == old_bytes, f'{form}: the exact old item is UNCHANGED across the amend')
    check(not wc.record_efp_valid(rec0, {n['id']: n for n in raw_json(r / 'graph.json')['nodes']},
                                  {n['id']: n for n in raw_json(r / 'graph.json')['nodes']}['review']),
          f'{form}: the amendment genuinely REKEYS the execution (old record invalid on the new revision)')
    amends = (r / 'amends.jsonl').read_text().splitlines()
    check(len(amends) == 1 and json.loads(amends[0])['new']['nodes'] and '"graph.amended"' in (r / 'events.jsonl').read_text(),
          f'{form}: the amendment is a REAL door commit (amends.jsonl row + graph.amended event)')
    mixed_row = rows[0]
    print(f'{form}: race row 0 -> item={mixed_row.get("item")!r} '
          f'session_current={mixed_row.get("session_current")!r}', flush=True)
    # The forbidden pair, phrased as the law (no implementation named): a
    # NEWER-generation label bound to the OLD exact chat. The observer is the
    # judge; both coherent shapes are allowed — old roster riding the
    # captured revision, or the honest placeholder beside the same exact chat.
    case(f'{form}/race-newer-label-must-not-pair-the-old-chat', raced, 0,
         expect('Amber', 'done', 'review Amber', [], 'Finished', None, None, sid(form, 0, 0)),
         expect('#0', 'done', 'review ', [], 'Finished', None, None, sid(form, 0, 0)))
    sib_allowed = [expect('#1', 'pending', 'review ', [], 'pending', None, None, sid(form, 0, 1)),
                   expect('#1', 'running', 'review ', [], 'running', None, None, sid(form, 0, 1))]
    case(f'{form}/race-sibling-stays-unnamed', raced, 1, *sib_allowed)

    # ---- TRUE RUNNER SETUP, era 1: release item 0, let its record commit —
    # a GENUINELY newer selection under the amended revision.
    (out / f'{form}-gen1-release-0').touch()
    wait_for(lambda: item0.read_bytes() != old_bytes and raw_json(item0).get('efp')[:8] == state['era1_8'], p2)
    rekeyed = api._view(r, full=True)
    krows = rekeyed['nodes']['review']['item_metrics']
    with sqlite3.connect(home / 'state.db') as db:
        stale = db.execute('select count(*) from sessions where id=?', (sid(form, 0, 0),)).fetchone()[0]
    check(stale == 1, f'{form}: the stale old chat is STILL LANDABLE history (this tests stale-vs-newer, not absence)')
    check(krows[0].get('item') == 'Quartz' and krows[0].get('session_current') == sid(form, 1, 0),
          f'{form}: under the amended revision the row binds the NEW era exact chat')
    # The stale old chat must not open: one call, the NEW session, in-place.
    case(f'{form}/rekeyed-stale-old-chat-must-not-open', rekeyed, 0,
         expect('Quartz', 'done', 'review Quartz', [], 'Finished', None, None, sid(form, 1, 0)))

    (out / f'{form}-gen1-release-1').touch()
    assert p2.wait(timeout=30) == 0
    settled = api._view(r, full=True)
    check(settled['status'] == 'done'
          and [row.get('item') for row in settled['nodes']['review']['output']['all_results']]
              == ['Quartz', 'Amber'],
          f'{form}: the settled aggregate rows carry the amended roster the records expanded from')
    case(f'{form}/settled-exact-open', settled, 0,
         expect('Quartz', 'done', 'review Quartz', [], 'Finished', None, None, sid(form, 1, 0)))

    # ---- INERT amendment as a POSITIVE (proof matrix item 2): resubmitting
    # the CURRENT committed graph rekeys nothing; the settled exact open and
    # the aggregate rows must stand byte-for-byte.
    agg_bytes = (r / 'nodes/review.json').read_bytes()
    rec0_bytes = item0.read_bytes()
    resp = door.act_amend({'run_id': runname, 'graph': raw_json(r / 'graph.json'), 'dry_run': False})
    check(resp.get('ok') and not resp.get('will_rerun'),
          f'{form}: inert amendment previewed as no re-run ({resp.get("applies")})')
    check(len((r / 'amends.jsonl').read_text().splitlines()) == 2,
          f'{form}: the door ledger shows BOTH revisions (race amend + inert), rekeyed nothing extra')
    inert = api._view(r, full=True)
    check((r / 'nodes/review.json').read_bytes() == agg_bytes and item0.read_bytes() == rec0_bytes,
          f'{form}: the inert amendment moves no record byte')
    case(f'{form}/inert-amend-positive', inert, 0,
         expect('Quartz', 'done', 'review Quartz', [], 'Finished', None, None, sid(form, 1, 0)))

# ---------------------------------------------------------------- observer --
# The UNCHANGED vendored panel observer, in-memory-extended by the EXACT four
# field patches of the committed harness (tests/test_selected_item_ownership_cj2.py)
# — the observer file itself is never rewritten.
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
print(f'observer exit {rc}', flush=True)          # BEHAVIOR exit, distinct from this wrapper's
if failures:
    print('\n'.join(failures), file=sys.stderr)
sys.exit(1 if failures or rc else 0)
