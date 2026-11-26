"""bd_2026-11-13-cj2: selection identity determines the destination BEFORE metrics.

The captain solo-to-fanout counterexample (receipts/ship20-recovery/
cj2-solo-to-fan-92a38d4a.log; independent replay
~/.hermes/workflows/20261124-232724-ship20-cj2-current-graph/work/
verify_current_graph/panel_review.py --solo-to-fan, red at BOTH shipped heads):
a real act_amend turns a legacy solo agent into a fan-out; before the
replacement spawns, the node reads pending and item_metrics is absent, while
the solo history rides on. NodePanel's link then substituted the NODE's
metrics for the SELECTED item and opened the obsolete solo chat — a chosen
item without its own row inherited the node's (and could inherit a sibling's)
history as a destination. The law this pins: for a selected item, an absent
item map/row reads `Session unavailable` with ZERO host calls — legitimate
aggregate/cost/attempt display, claimless legacy node fallback (NO item
selection) and named item/node positives stand unchanged.

Deterministic read-boundary proof (no snapshot system added): session
authority rides the EXACT committed revision the response publishes — one
response, one revision. The mixed-revision counterexample
(receipts/ship20-recovery/cj2-mixed-revision-4abf5a7c.log, red at 4abf5a7c)
shows why the former (b)/(c) demote-only claim was misleading: with an
independent second graph read inside run_child_metrics, an amend that
re-orders a fan-out and lands its replacement record+row between the state
and metrics reads PROMOTES the newer era's chat onto the superseded layout
the same response ships — the visible old label `p` opens replacement `q`'s
chat. The dashboard therefore hands _view's published graph to
run_child_metrics; this suite replays both sides of that read at the REAL
seams: (a) an amend landing after the layout read, before the metrics read —
demote-only and reorder-with-replacement; (b) an amend landing after the
metrics snapshot, before the response finalizes. An in-flight response is
coherent at one revision (never half of one era, half of the next); the
mixed fan-out response ships every affected modern link UNAVAILABLE with
ZERO calls; the settled graph-aligned read opens the exact replacement ID
exactly once; the next fetch converges. A standalone run_child_metrics call
(door shape) still consults EXACTLY ONE graph snapshot (jload counter).

Covered at the real seam (actual door act_amend, actual dashboard _view,
actual NodePanel render/click through the shipped plugin module): old row
retained before replacement (O3-O5), named replacement with row absent (O9)
then present (O10-O12), untouched sibling (O6), inert amend (O7), claimless
legacy positive and its expired variant (O2, O5, O8), changed item (O3-O13),
same-key retry (O13), read-boundary interleaves R1/R2/R3 — the chip-click
path proving the visible label never opens another item's conversation.
Cross-home merge and the
bound-era expiry select-before-validate are unchanged wfcommon seams already
pinned by tests/test_current_attempt_replay_cj2.py (obs6/obs7) and
tests/test_stored_session_order_cj2.py, replayed green at this head.

Phase 7 owns the OTHER half of the boundary — the facts join. _view merges
node_facts AFTER the metrics call, and node_facts re-read the aggregate
without consulting the revision the response publishes: a certified
re-order landing between the two reads repaints the shipped layout (Case A,
the challenge witness's after-fold-before-facts/mixed: the visible new chip
opened the OLD item's chat), and a persistently stale aggregate keeps being
presented as current layout next to the new binding (Case B,
stale-aggregate-gap: the visible old chip opened the replacement's chat).
The law node_rec already states — a stale commit "must never be presented
as current" — is applied at that join with the SAME validity check the claim
pass uses, against the published revision: a response attests no ordering
its own published revision does not honor; the demoted output rides the
established `unknown` and every other fact (history, harvest, log paths,
stale_because) rides verbatim as inspection; the settled re-certified era
attests itself and still opens the exact ID. The chip-click mismatch itself
was replayed red at db40b950 through the independent witness harness
(receipts/ship20-recovery/cj2-late-boundary-db40b950/gap-replay.log).
"""
import importlib.util
import inspect
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

A_ID = 'local-' + 'a' * 64
B_ID = 'local-' + 'b' * 64
C_ID = 'local-' + 'c' * 64
E_ID = 'local-' + 'e' * 64
D_ID = 'local-' + 'd' * 64
G_ID = 'local-' + '6' * 64
I_ID = 'local-' + '7' * 64
J_ID = 'local-' + '8' * 64
K_ID = 'local-' + '9' * 64
OPEN_OK = '{"intent":"in-place"}'
CLOSED = {'unavailable': True, 'calls': []}
SCHEMA = ('create table if not exists sessions (id text, title text, model text, input_tokens int, '
          'output_tokens int, cache_read_tokens int, reasoning_tokens int, api_call_count int, '
          'tool_call_count int, estimated_cost_usd real, last_activity_at real, '
          'last_activity_description text, ended_at real, started_at real)')
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
    cols = ('(id, title, model, input_tokens, output_tokens, cache_read_tokens, '
            'reasoning_tokens, api_call_count, tool_call_count, estimated_cost_usd, '
            'last_activity_at, last_activity_description, ended_at, started_at)')
    marks = ','.join('?' * len(rows[0]))
    with sqlite3.connect(db) as c, c:
        c.execute(SCHEMA)
        c.executemany(f'insert into sessions {cols} values ({marks})', rows)


def node_metrics(view, nid):
    return view['nodes'][nid]['metrics']


PROBE = r"""
  {
    // bd_2026-11-13-cj2 selected-item identity replay — the ACTUAL NodePanel,
    // selection atoms and all; only test-only visibility differs. The
    // observation payload crosses as a TEST-OWNED FILE read from argv[2]: the
    // full payload exceeds the per-string exec limit on Linux
    // (MAX_ARG_STRLEN — admission red: OSError [Errno 7] Argument list too
    // long for CJ2_ITEM_PANELS), so no env var may carry it; the bytes and
    // every assertion below are unchanged.
    const replay = JSON.parse(readFileSync(process.argv[2], 'utf8'))
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
        // Selection identity through the REAL click: the FIRST chip the shipped
        // response itself paints (DOM order, among the observation's published
        // labels) sets the selection. A response painting a different item
        // first than the revision it publishes IS the mixed-era bug — recorded
        // as a structured mismatch, never a thrown harness. The chat button
        // then addresses exactly that index.
        const first = o.view.graph.nodes.find(n => n.id === o.node).fanout.items[0]
        mod.$fanItem.set(null)
        const initial = mat(mod.NodePanel({ detail: o.view }))
        const labels = o.chiplabels ?? [first]
        const chips = buttons(initial).filter(x => labels.includes(textOf(x.children).trim().split(/\s+/)[0]))
        const painted = chips.length ? textOf(chips[0].children).trim().split(/\s+/)[0] : null
        if (chips.length) chips[0].onClick({ stopPropagation() {} })
        const sel = mod.$fanItem.get()
        if (!chips.length || painted !== (o.paints ?? first)
            || JSON.stringify(sel) !== JSON.stringify({ runId: o.view.id, nodeId: o.node, index: 0 }))
          bad.push({ name: o.name, reason: 'the first painted chip deviates from the published era',
                     painted, want: o.paints ?? first, sel })
        console.log('CJ2-ITEM-CHIP ' + JSON.stringify({ name: o.name, label: painted }))
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
    console.log('CJ2-ITEM-PANELS ' + JSON.stringify(verdicts))
    assert.deepEqual(bad, [], `${bad.length} panel observation(s) deviate — ${JSON.stringify(bad)}`)
  }
"""


tmp = tempfile.mkdtemp(prefix='cj2-item-identity-')
try:
    home = Path(tmp) / 'home'
    runs = Path(tmp) / 'runs'
    r = runs / 'itemidentity'
    (r / 'nodes').mkdir(parents=True)
    home.mkdir()
    # #71 r5 hostile-settings canary: an owner settings.runs_root pointed at
    # THIS home outranks the env pin at the raw resolver — an unpinned in-
    # process door writer would land every write under it. The door is
    # pinned through the repository's wf_test_isolation.install below, and
    # the final check asserts the canary saw zero writes (the mechanism,
    # not the text scanner).
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
    door = load('cj2_item_door', ROOT / '__init__.py')
    iso = load('cj2_item_iso71', ROOT / 'tests' / 'wf_test_isolation.py')
    iso.install(door)  # #71 r5: pin settings.runs_root alongside WF_RUNS_ROOT
    api = load('cj2_item_view', ROOT / 'dashboard' / 'plugin_api.py')
    wc = api._workflow_common()
    db = home / 'state.db'

    node_a = {'id': 'a', 'type': 'agent', 'goal': 'old a'}
    node_b = {'id': 'b', 'type': 'agent', 'goal': 'keep'}
    node_c = {'id': 'c', 'type': 'agent', 'goal': 'legacy era'}
    byid = {n['id']: n for n in (node_a, node_b, node_c)}
    (r / 'graph.json').write_text(json.dumps(
        {'name': 'itemidentity', 'nodes': [node_a, node_b, node_c]}))
    (r / 'run.json').write_text(json.dumps({'name': 'itemidentity'}))
    k_a = 'wf:itemidentity:a:11111111.111111'
    k_b = 'wf:itemidentity:b:22222222.222222'
    k_c = 'wf:itemidentity:c:44444444.444444'
    put(db, [row(A_ID, k_a + '#a0', 10.0), row(B_ID, k_b + '#a0', 11.0),
             row(E_ID, k_c + '#a0', 14.0)])

    def stamp(skey, spawn, node, graph_byid):
        return {'status': 'done', 'skey': skey, 'spawn': spawn,
                'efp': wc.efp(graph_byid, node), 'fp_rule_version': wc.FP_RULE_VERSION,
                'profile_home': str(home)}

    (r / 'nodes' / 'a.json').write_text(json.dumps(stamp(k_a, 0, node_a, byid)))
    (r / 'nodes' / 'b.json').write_text(json.dumps(stamp(k_b, 0, node_b, byid)))
    (r / 'nodes' / 'c.json').write_text(json.dumps(
        {'status': 'done', 'def_hash': wc.def_hash(node_c, wc.FP_RULE_LEGACY),
         'profile_home': str(home)}))   # claimless legacy (pre-efp def_hash) shape

    observations = []

    def panel(name, view, node, index, expect, pick=None, paints=None, chiplabels=None):
        obs = {'name': name, 'view': view, 'node': node,
               'index': index, 'expect': expect, 'pick': pick}
        if paints is not None:
            obs['paints'] = paints
        if chiplabels is not None:
            obs['chiplabels'] = chiplabels
        observations.append(obs)

    def amend(patch_nodes):
        with patch.object(door, '_resume_after_action', return_value='live'), \
                patch.object(door, '_route_liveness_ping', return_value=[]):
            return door.act_amend({'run_id': r.name, 'patch': {'nodes': patch_nodes}})

    # -- phase 0: both legacy destinations are open at the actual panel ------
    view0 = api._view(r, full=True)
    panel('O1-bound-node-opens-own', view0, 'a', None, expect_open(A_ID))
    panel('O2-claimless-legacy-node-opens-last-entry', view0, 'c', None, expect_open(E_ID))
    check('session_current' not in node_metrics(view0, 'c'),
          'setup: the claimless legacy node carries no binding key')

    # -- phase 1: the REAL act_amend turns the solo agent into a fan-out -----
    c_bytes_before = (r / 'nodes' / 'c.json').read_bytes()
    res = amend({'c': {'goal': 'do {item}', 'fanout': {'items': ['p', 'q']}}})
    check(res.get('ok') is True and 'c' in (res.get('will_rerun') or []),
          f'the real act_amend re-queues the solo agent ({res})')
    check((r / 'nodes' / 'c.json').read_bytes() == c_bytes_before,
          'act_amend never rewrites the old record — the solo era survives byte-identical')
    view1 = api._view(r, full=True)
    c1 = view1['nodes']['c']
    check(c1['status'] == 'pending' and 'item_metrics' not in c1
          and node_metrics(view1, 'c')['session_ids'] == [E_ID]
          and 'session_current' not in node_metrics(view1, 'c'),
          'pending before replacement: no item map at all, solo history inspectable, no binding')
    # THE counterexample: a selected item must not inherit the node's history.
    panel('O3-selected-item0-absent-map-never-inherits-node', view1, 'c', 0, CLOSED)
    panel('O4-selected-item1-absent-map-never-inherits-node', view1, 'c', 1, CLOSED)
    panel('O5-claimless-legacy-node-without-item-still-opens', view1, 'c', None, expect_open(E_ID))
    panel('O6-untouched-sibling-opens-own', view1, 'b', None, expect_open(B_ID))

    # -- phase 2: inert edit at a sibling keeps its binding usable -----------
    inert = amend({'b': {'timeout': 500}})
    check(inert.get('ok') is True and 'b' in (inert.get('unchanged') or [])
          and 'b' not in (inert.get('will_rerun') or []),
          f'the inert (fingerprint-unchanged) amend re-runs nothing ({inert})')
    view2 = api._view(r, full=True)
    check(view2['nodes']['b']['status'] == 'done'
          and node_metrics(view2, 'b')['session_current'] == B_ID,
          'an inert edit keeps the previously valid record usable')
    panel('O7-inert-amend-sibling-binding-survives', view2, 'b', None, expect_open(B_ID))

    # -- phase 3: expiry is select-before-validate even on the legacy fallback
    with sqlite3.connect(db) as c, c:
        c.execute('alter table sessions add column expiry_finalized integer')
        c.execute('update sessions set expiry_finalized=1 where id=?', (E_ID,))
    view3 = api._view(r, full=True)
    check(node_metrics(view3, 'c')['session_ids_expired'] == [E_ID],
          'the authoritative lookup flags the expired legacy row')
    panel('O8-expired-claimless-fallback-is-absent', view3, 'c', None, CLOSED)

    # -- phase 4: the named replacement — record first (row absent), then row -
    graph_now = json.loads((r / 'graph.json').read_text())
    byid_now = {n['id']: n for n in graph_now['nodes']}
    c_def = byid_now['c']
    k_c0 = 'wf:itemidentity:c:0:66666666.666666'
    (r / 'nodes' / 'c.0.json').write_text(json.dumps(stamp(k_c0, 0, c_def, byid_now)))
    view4 = api._view(r, full=True)
    check('item_metrics' not in view4['nodes']['c'],
          'a named replacement claim with no row ships no item row (no synthetic metrics)')
    panel('O9-named-replacement-row-absent', view4, 'c', 0, CLOSED)
    put(db, [row(C_ID, k_c0 + '#a0', 30.0)])
    view5 = api._view(r, full=True)
    m5 = view5['nodes']['c']['item_metrics']
    check(m5[0]['session_ids'] == [C_ID] and m5[0]['session_current'] == C_ID
          and 1 not in m5,
          'the replacement row lands bound: item 0 names itself, item 1 has no row')
    panel('O10-named-replacement-row-present-opens-own', view5, 'c', 0, expect_open(C_ID))
    panel('O11-item1-cannot-borrow-item0-destination', view5, 'c', 1, CLOSED)
    panel('O12-node-fold-current-beats-legacy-survivor', view5, 'c', None, expect_open(C_ID))

    # -- phase 5: same-key retry — the named title moves, the destination moves
    (r / 'nodes' / 'c.0.json').write_text(json.dumps(stamp(k_c0, 1, c_def, byid_now)))
    put(db, [row(D_ID, k_c0 + '#a1', 40.0)])
    view6 = api._view(r, full=True)
    m6 = view6['nodes']['c']['item_metrics']
    check(m6[0]['session_ids'] == [C_ID, D_ID] and m6[0]['session_current'] == D_ID,
          'the same-key retry re-binds to the named newer attempt, chronology intact')
    panel('O13-same-key-retry-opens-newest-named', view6, 'c', 0, expect_open(D_ID))

    # -- phase 6: one response, one revision — real _view interleaved at the ----
    # authority/read boundary. The mixed-revision counterexample
    # (receipts/ship20-recovery/cj2-mixed-revision-4abf5a7c.log, red at 4abf5a7c):
    # a SECOND, later graph read inside run_child_metrics validated claims against
    # an amendment the response never published — a re-order that landed its
    # replacement record+row mid-read bound q's fresh chat to the superseded
    # [p,q] layout the same response shipped, and the visible p chip opened q.
    # Demote-only was the wrong law; the right one is coherent authority: claims
    # validate against the very revision the response ships.
    st_old = wc.run_state(r)
    check(st_old['nodes']['b']['status'] == 'done'
          and not st_old['nodes']['b'].get('stale_of_amend'),
          'the pre-interleave state read still says the sibling is done and fresh')
    graph_reads = []
    real_jload = wc.jload
    real_metrics = wc.run_child_metrics

    def counting_jload(p, *a, **k):
        if str(p).endswith('graph.json'):
            graph_reads.append(str(p))
        return real_jload(p, *a, **k)

    def lands_between_reads(patch_nodes, land=None):
        """A REAL act_amend landing after one _view's layout read and before its
        metrics read, then THAT call's own arguments forwarded — after the fix
        the seam receives the published graph and authority rides it; before,
        the metrics pass re-reads a newer file (the artifact being replaced)."""
        def seam(run, *a, **k):
            assert run == r
            res = amend(patch_nodes)
            assert res.get('ok') is True, res
            if land is not None:
                land(res)
            return real_metrics(run, *a, **k)
        return seam

    # -- side A, amend-only (no replacement row): the in-flight response is one --
    # revision end to end. An era the PUBLISHED revision still honors is not
    # half-demoted by an amendment that revision never saw. (The former O14
    # pinned the split-read artifact: status done from the old read, binding
    # gone by the new one — half of one era, half of the next.)
    with patch.object(wc, 'run_child_metrics', lands_between_reads({'a': {'goal': 'a new'}})):
        snap_a = api._view(r, full=True)
    check(snap_a['nodes']['a']['status'] == 'done'
          and node_metrics(snap_a, 'a')['session_current'] == A_ID,
          'an amend landing mid-response cannot half-demote an era its own published revision '
          'still honors — session authority rides the graph the response ships')
    panel('R1-amend-before-metrics-keeps-published-revision', snap_a, 'a', None, expect_open(A_ID))
    conv_a = api._view(r, full=True)
    check(conv_a['nodes']['a']['status'] == 'pending'
          and node_metrics(conv_a, 'a')['session_current'] is None,
          'the next full read converges: the amended era demotes — history rides, the old chat '
          'is never revived as current')
    panel('R1b-fresh-read-demotes-amended-era', conv_a, 'a', None, CLOSED)

    # -- side B: an amend landing AFTER the metrics snapshot, before the response --
    # finalizes, cannot reach back into it: the finalized response keeps its own
    # revision's layout AND binding together (bound old data is never attached to
    # a layout that superseded it) and the settled read demotes.
    real_events = api._events

    def after_metrics_b(run):
        assert run == r
        res = amend({'b': {'goal': 'b new'}})
        assert res.get('ok') is True and 'b' in (res.get('will_rerun') or []), res
        return real_events(run)
    with patch.object(api, '_events', after_metrics_b):
        snap_b = api._view(r, full=True)
    check(snap_b['nodes']['b']['status'] == 'done'
          and node_metrics(snap_b, 'b')['session_current'] == B_ID,
          'an amend landing after the metrics snapshot cannot attach the finalized response to '
          'a layout it never read — the response stays one revision')
    panel('R2-amend-after-metrics-keeps-published-revision', snap_b, 'b', None, expect_open(B_ID))
    conv_b = api._view(r, full=True)
    check(conv_b['nodes']['b']['status'] == 'pending'
          and node_metrics(conv_b, 'b')['session_current'] is None,
          'the settled read of the after-metrics amend demotes — never revived as current')
    panel('R2b-fresh-read-demotes-amended-era', conv_b, 'b', None, CLOSED)

    # -- side A WITH a replacement: the reproduced failure. The re-order plus its --
    # fingerprint-valid record and exact SQLite row land mid-read; the response
    # still publishes the [p,q] layout it started with, so the amended item's
    # modern link is UNAVAILABLE with ZERO calls — the old label p opens nothing,
    # never q's chat — and the settled graph-aligned read opens exact q once.
    new_id = 'local-' + 'f' * 64
    new_key = 'wf:itemidentity:c:0:77777777.777777'

    def land_replacement(res):
        assert 'c' in (res.get('will_rerun') or []), res
        new_defs = {n['id']: n for n in json.loads((r / 'graph.json').read_text())['nodes']}
        assert new_defs['c']['fanout']['items'] == ['q', 'p']
        (r / 'nodes' / 'c.0.json').write_text(json.dumps(stamp(new_key, 0, new_defs['c'], new_defs)))
        put(db, [row(new_id, new_key + '#a0', 50.0)])
    with patch.object(wc, 'run_child_metrics',
                      lands_between_reads({'c': {'fanout': {'items': ['q', 'p']}}}, land_replacement)):
        mixed = api._view(r, full=True)
    fresh = api._view(r, full=True)

    def summarize(view):
        defs = {n['id']: n for n in view['graph']['nodes']}
        return {'layout': defs['c']['fanout']['items'], 'status': view['nodes']['c']['status'],
                'row': view['nodes']['c']['item_metrics'][0]}

    m_sum, f_sum = summarize(mixed), summarize(fresh)
    check(m_sum['layout'] == ['p', 'q'],
          'the mid-read re-order publishes the layout the response started with')
    check(m_sum['row']['session_current'] is None and D_ID in m_sum['row']['session_ids']
          and new_id in m_sum['row']['session_ids'],
          'the deliberately mixed response fail-closes the amended item: the old rows and the '
          'amendment row ride as inspection, nothing is bound')
    check(f_sum['layout'] == ['q', 'p'] and f_sum['row']['session_current'] == new_id,
          'the settled graph-aligned response names the replacement at the label it moved to')
    check({k: m_sum['row'][k] for k in ('tokens_in', 'tokens_out', 'api_calls', 'tool_calls',
                                        'attempts', 'children')}
          == {k: f_sum['row'][k] for k in ('tokens_in', 'tokens_out', 'api_calls', 'tool_calls',
                                           'attempts', 'children')},
          'prior rows and counters are unchanged across the amendment boundary')
    panel('R3-mixed-view-old-p-must-not-open-new-q', mixed, 'c', 0, CLOSED, pick='first')
    panel('R3-positive-fresh-q-opens-new-q', fresh, 'c', 0, expect_open(new_id), pick='first')

    # -- phase 7: the facts join — one response, one era (late-boundary replay) ----
    # The independent challenge (gap-replay.log, red at db40b950) witnessed the
    # two real NodePanel paths the metrics seam does not cover: _view merges
    # node_facts AFTER the metrics call and node_facts re-reads the aggregate
    # raw. (A) A certified re-order + item records + rows landing between the
    # two reads ships flipped labels over the era-bound bindings the response
    # publishes — the visible new chip opens the OLD item's chat. (B) With no
    # race at all: the re-order amended and its replacement record+row landed,
    # the aggregate not yet re-certified — the persistently stale aggregate
    # ships its old ordering as current layout over the NEW binding, and the
    # visible old chip opens the replacement's chat. A permitted response keeps
    # ONE valid era — painted label and bound ID agree with the revision it
    # publishes — or fails the ambiguous chat closed; history rides as
    # inspection; settled positives still open the exact ID.
    g_now = {n['id']: n for n in json.loads((r / 'graph.json').read_text())['nodes']}
    k3_1 = 'wf:itemidentity:c:1:33333331.333333'
    (r / 'nodes' / 'c.1.json').write_text(json.dumps(stamp(k3_1, 0, g_now['c'], g_now)))
    put(db, [row(G_ID, k3_1 + '#a0', 60.0)])

    def certify(labels, graph_byid):
        # The runner's aggregate-commit shape: a done record whose output
        # attests `labels`, efp-stamped for THAT revision (wf.save_node's
        # certified save_node output, minus the item-record side files).
        cdef = graph_byid['c']
        return json.dumps({'status': 'done',
                           'efp': wc.efp(graph_byid, cdef), 'fp_rule_version': wc.FP_RULE_VERSION,
                           'profile_home': str(home),
                           'output': {'items': list(labels),
                                      'all_results': [{'item': x, 'status': 'done',
                                                       'output': x, 'ms': 15} for x in labels]}})

    (r / 'nodes' / 'c.json').write_text(certify(['q', 'p'], g_now))

    def attest(view):
        out = view['nodes']['c'].get('output')
        return [x.get('item') for x in out['all_results']] if isinstance(out, dict) else None

    def item_counters(row):
        return {k: row.get(k) for k in ('tokens_in', 'tokens_out', 'api_calls', 'tool_calls',
                                        'attempts', 'children', 'cost')}

    pre7 = api._view(r, full=True)
    check(pre7['nodes']['c']['status'] == 'done' and attest(pre7) == ['q', 'p']
          and pre7['nodes']['c']['item_metrics'][0]['session_current'] == new_id
          and pre7['nodes']['c']['item_metrics'][1]['session_current'] == G_ID,
          'a settled certified era attests itself: response labels match the published graph, '
          'each item bound to its own chat')

    def flip_lands(res):
        assert 'c' in (res.get('will_rerun') or []), res
        g_new = {n['id']: n for n in json.loads((r / 'graph.json').read_text())['nodes']}
        assert g_new['c']['fanout']['items'] == ['p', 'q']
        held['g_new'] = g_new
        for i, (sid_, era) in enumerate(((I_ID, '44444440.444440'), (J_ID, '44444441.444441'))):
            key = f'wf:itemidentity:c:{i}:{era}'
            (r / 'nodes' / f'c.{i}.json').write_text(json.dumps(stamp(key, 0, g_new['c'], g_new)))
            put(db, [row(sid_, key + '#a0', 70.0 + i)])
        (r / 'nodes' / 'c.json').write_text(certify(['p', 'q'], g_new))
    held = {}

    def metrics_then_lands(patch_nodes, land):
        """The witness's after-fold ordering: the REAL metrics fold completes on
        the published revision, THEN the re-order + records + rows + certified
        aggregate land — the facts read that follows is the seam under test."""
        def seam(run, *a, **k):
            assert run == r
            cm = real_metrics(run, *a, **k)
            res = amend(patch_nodes)
            assert res.get('ok') is True, res
            land(res)
            return cm
        return seam
    with patch.object(wc, 'run_child_metrics',
                      metrics_then_lands({'c': {'fanout': {'items': ['p', 'q']}}}, flip_lands)):
        mixed7 = api._view(r, full=True)
    check(next(n for n in mixed7['graph']['nodes'] if n['id'] == 'c')['fanout']['items'] == ['q', 'p'],
          'the racing re-order cannot reach back: the response publishes the layout it read')
    check(attest(mixed7) != ['p', 'q'],
          'Case A — an aggregate certified after the metrics read may keep its coherent old '
          'attestation or ride demoted, but it may NOT attest a later ordering this response '
          'never published')
    check(item_counters(mixed7['nodes']['c']['item_metrics'][0])
          == item_counters(pre7['nodes']['c']['item_metrics'][0])
          and item_counters(mixed7['nodes']['c']['item_metrics'][1])
          == item_counters(pre7['nodes']['c']['item_metrics'][1]),
          'the interleave moves no counters: every row present before it rides identically')
    panel('R4-late-aggregate-cannot-repaint-the-published-era', mixed7, 'c', 0,
          expect_open(new_id), pick='first', paints='q', chiplabels=['q', 'p'])

    # Case B — no race: the re-order amended, the replacement record+row landed,
    # the aggregate NOT yet re-certified. node_rec says pending; the stale
    # commit must not be presented as current layout beside the new binding.
    res_b = amend({'c': {'fanout': {'items': ['q', 'p']}}})
    assert res_b.get('ok') is True and 'c' in (res_b.get('will_rerun') or []), res_b
    g_after = {n['id']: n for n in json.loads((r / 'graph.json').read_text())['nodes']}
    k5 = 'wf:itemidentity:c:0:55555550.555555'
    (r / 'nodes' / 'c.0.json').write_text(json.dumps(stamp(k5, 0, g_after['c'], g_after)))
    put(db, [row(K_ID, k5 + '#a0', 80.0)])
    viewB = api._view(r, full=True)
    check(viewB['nodes']['c']['status'] == 'pending' and viewB['nodes']['c'].get('stale_because'),
          'post-amend pending is legitimate and explainable — fact inspection survives the demotion')
    check(attest(viewB) != ['p', 'q'],
          'Case B — a persistently stale aggregate is history, never current layout authority')
    mB = viewB['nodes']['c']['item_metrics']
    check(mB[0]['session_current'] == K_ID and I_ID in mB[0]['session_ids']
          and mB[1]['session_current'] is None and G_ID in mB[1]['session_ids'],
          'historical records survive as inspection; item 0 binds its own replacement, '
          'item 1 demotes with its own era and borrows nothing')
    panel('R5-stale-aggregate-never-attests-current-layout', viewB, 'c', 0,
          expect_open(K_ID), pick='first', paints='q', chiplabels=['q', 'p'])
    panel('R5-item1-demoted-era-opens-nothing', viewB, 'c', 1, CLOSED)

    # The late aggregate lands for the new era: the settled response attests
    # its own ordering and the positive still opens the exact ID.
    (r / 'nodes' / 'c.json').write_text(certify(['q', 'p'], g_after))
    viewC = api._view(r, full=True)
    check(viewC['nodes']['c']['status'] == 'done' and attest(viewC) == ['q', 'p'],
          'the re-certified era attests itself against the revision it publishes')
    panel('R5-positive-settled-era-opens-exact', viewC, 'c', 0,
          expect_open(K_ID), pick='first', paints='q', chiplabels=['q', 'p'])

    # The demotion is a property of the PUBLISHED response, not the store: the
    # standalone (door-shaped) facts read still serves the record verbatim,
    # and the join now takes the published revision as an argument — the same
    # canonical identity boundary, no second validator.
    check('graph' in inspect.signature(wc.node_facts).parameters,
          'node_facts takes the published revision as an argument — the facts join rides '
          'the same canonical identity boundary as the claim pass')
    (r / 'nodes' / 'c.json').write_text(certify(['p', 'q'], held['g_new']))   # era-4 commit: persistently stale
    check(wc.node_facts(r, 'c')['output'] == json.loads((r / 'nodes' / 'c.json').read_text())['output'],
          'the standalone facts read still serves the raw record verbatim — inspection untouched')
    # the seam argument is the graph DOCUMENT — the exact shape _view publishes
    # and run_child_metrics already takes (st["graph"]), not a byid map.
    doc_now = json.loads((r / 'graph.json').read_text())
    check(wc.node_facts(r, 'c', graph=doc_now)['output'] == 'unknown',
          'with the published revision handed in, a stale commit attests nothing: the '
          'established unknown rides, no era is fabricated')
    (r / 'nodes' / 'c.json').write_text(certify(['q', 'p'], g_after))
    check(wc.node_facts(r, 'c', graph=doc_now)['output']
          == json.loads((r / 'nodes' / 'c.json').read_text())['output'],
          'with the published revision handed in, a current-era commit rides verbatim')

    # -- the rendered/click path on the ACTUAL NodePanel -----------------------
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
    (work / 'panels.json').write_text(json.dumps(observations))
    proc = subprocess.run(['node', '--experimental-strip-types', str(driver),
                           str(work / 'panels.json')],
                          env=env,
                          timeout=60, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    line = next((l for l in proc.stdout.splitlines() if l.startswith('CJ2-ITEM-PANELS ')), None)
    check(proc.returncode == 0 and line is not None,
          f'panel path: every one of the {len(observations)} selection-identity observations '
          'renders/clicks exactly as the projection declares')
    verdicts = json.loads(line[len('CJ2-ITEM-PANELS '):])
    check([v['name'] for v in verdicts] == [o['name'] for o in observations],
          'the probe covered every observation through the actual NodePanel')
    for v in verdicts:
        opens = [c for c in v['result']['calls'] if c[0] == 'openSession']
        check(len(opens) <= 1 and all(c[2] == OPEN_OK for c in opens),
              f"{v['name']}: at most ONE openSession with the exact union options")

    # -- the boundary itself: ONE identity, no independent second read -----------
    # The behavior interleaves above can only be coherent because the claim pass
    # takes the published revision as its argument — this pins the seam, not a
    # framework: no new parser, no wire field, no retry loop, no lock.
    check('graph' in inspect.signature(real_metrics).parameters,
          'run_child_metrics takes the published revision as an argument — one canonical '
          'identity boundary replaces the second, later graph read')
    published = api._view(r, full=True)
    graph_reads.clear()
    with patch.object(wc, 'jload', counting_jload):
        wc.run_child_metrics(r, graph=published['graph'])
    check(graph_reads == [],
          'with the published snapshot handed in, the claim pass reads NO graph file — '
          'authority IS that exact revision')
    graph_reads.clear()
    cm_direct = None
    with patch.object(wc, 'jload', counting_jload):
        cm_direct = wc.run_child_metrics(r)   # the door shape: no graph passed
    check(len(graph_reads) == 1,
          'the standalone (door-shaped) claim pass still consults EXACTLY ONE graph snapshot')
    check(cm_direct[k5]['_session_current'] == K_ID,
          'the settled standalone read binds the exact replacement chat')
    # A REAL door write that resolves runs_root (the shelf save the #71 S4/S5
    # legs prove): through the pinned resolver it lands in the env-pinned
    # root; an unpinned door would land it in the owner-settings canary — so
    # the zero-write check below bites at the mechanism, not at the scanner.
    saved = door.act_save({'graph': {'name': 'itemidentity-canary', 'nodes': [node_b]},
                           'name': 'cj2-canary'})
    check(saved.get('saved') == 'cj2-canary' and (runs / 'library' / 'cj2-canary.json').exists(),
          'the real door shelf write through the pinned resolver lands in the env-pinned root')
    leaked = sorted(p.relative_to(canary).as_posix() for p in canary.rglob('*') if p.is_file())
    check(leaked == ['sentinel.txt'],
          'the hostile settings.runs_root canary saw ZERO writes through the pinned '
          f'door — the pin is the resolver wrap, not the source scanner: {leaked}')
    print(f"\nALL PASS ({ok}) test_selected_item_identity_cj2 — for a selected fan-out item, "
          "the destination is that item's own recorded row and nothing else: an absent item "
          "map/row renders `Session unavailable` with ZERO host calls; claimless legacy, "
          "named-item, sibling, inert, expiry, same-key-retry, the one-response-one-revision "
          "read-boundary interleaves and the facts-join era law (R4/R5: neither a late-"
          "certified nor a persistently stale aggregate attests a layout the response does "
          "not publish; settled eras open the exact ID) hold — session authority and layout "
          "attestation both ride the exact committed revision each response publishes.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
