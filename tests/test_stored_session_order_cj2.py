"""bd_2026-11-13-cj2 (Wave A review counterexample): the conversation-link
session_ids must land in CHRONOLOGY order so the selector (last entry) opens
the NEWEST recorded attempt.

Astra's reproduction (additional-boundaries.py): one skey with attempts #a2 at
time 2 and #a10 at time 10 folded to [newer, older] because the metrics SELECT
ordered by `title` first — and `...#a10` sorts lexicographically BEFORE
`...#a2`. The UI (desktop/plugin.js latestStoredSessionId) takes the last
entry, so the click opened the OLDER durable session.

Pinned here at the production seam — wfcommon.child_metrics feeding
fold_child_metrics (THE ONE fold the dashboard/door projections serialize):
  1. counterexample: out-of-order rows land chronological, newest LAST,
     independent of insertion (rowid) order;
  2. same-time ties: rowid breaks the tie deterministically and the later
     INSERT (a real re-attempt) still wins the last slot;
  3. absent id column (minimal historical schema): the fold gains no ids and
     THE ONE fold drops the key entirely — serialized payload unchanged;
  4. unverified/runtime-shaped id: recorded verbatim at its chronological
     position (the read model never repairs; the UI shape gate drops it,
     pinned in test_stored_session_nav.mjs);
  5. additive metrics behavior survives: sums, attempts, first-wins model,
     started-min, ended rules unchanged;
  6. (Wave D, captain counterexample) the shipped LAST entry is the current
     attempt's identity: an unrecorded rotation fabricates nothing and re-lands
     when the row lands; a removed row removes the destination (the state.db row
     IS the authoritative expiry lookup); an expiry_finalized row keeps its
     chronological slot and rides the additive `session_ids_expired` flag —
     dropping it would promote the older attempt;
  7. profile transition: the same skey across two homes merges additively in
     run_child_metrics with the LAST slot owned by the globally-newest row,
     whichever scan direction the node records present (stamp sort keyed to the
     row's own (started-known, started_at, rowid) — never node-name scan order);
     the stamp map is private to the read model and never serialized;
  8. (Wave E, captain missing-current counterexample) the CURRENT attempt is
     the exact title the run's own node/item records name (skey + the
     wf.py:8826 `#a<attempt>` contract — spawn records for running children,
     committed records via their `spawn` attempt), NOT the last surviving DB
     row: rows alone cannot tell "the last row IS current" from "the newest
     row was already expunged" (captain review: deleting the #a10 row promoted
     #a2, and the click opened the OLDER chat — the author's own deletion test
     removed ALL rows and missed it). run_child_metrics binds
     `_session_current` (recorded id verbatim, or the computed absence null)
     and THE ONE fold serializes it as `session_current`; a fold over rows no
     record claims (pre-contract fixtures, historical payloads) gains no key
     and the selector's last-entry law stands unchanged.

The Wave E bindings live in CurrentAttemptBinding below.
"""
import importlib.util
import json
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


wc = load('stored_session_order_wfcommon', ROOT / 'wfcommon.py')

A_ID = 'local-' + 'a' * 64          # attempt #a2
B_ID = 'local-' + 'b' * 64          # attempt #a10 (newer)
RUNTIME_ID = '20260923_143041_27e8d2'
KEY = 'wf:orderfix:node:12345678.123456'

FULL_SCHEMA = ('create table sessions (id text, title text, model text, '
               'input_tokens int, output_tokens int, cache_read_tokens int, reasoning_tokens int, '
               'api_call_count int, tool_call_count int, estimated_cost_usd real, '
               'last_activity_at real, last_activity_description text, ended_at real, started_at real)')


class StoredSessionOrder(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cj2-order-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.db = self.home / 'state.db'

    def seed(self, rows, schema=FULL_SCHEMA):
        marks = ','.join('?' * len(rows[0]))
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute(schema)
            c.executemany(f'insert into sessions values ({marks})', rows)

    def row(self, sid, attempt, started, model='fake'):
        title = f'{KEY}#a{attempt}'
        return (sid, title, model, 10, 5, 1, 0, 2, 3, 0.5, started, 'tick', None, started)

    def exp_row(self, sid, attempt, started, expired):
        return self.row(sid, attempt, started) + (expired,)

    def ids(self):
        metrics = wc.child_metrics('orderfix', home=self.home)
        self.assertIn(KEY, metrics, 'the skey fold must exist for its own rows')
        return metrics[KEY]

    # -- 1. the reproduced counterexample: chronological, newest LAST ---------
    def test_out_of_order_rows_fold_chronologically(self):
        # #a10 inserted FIRST (smaller rowid) so neither insertion order nor a
        # lexical title sort can masquerade as the repair.
        self.seed([self.row(B_ID, 10, 10.0), self.row(A_ID, 2, 2.0)])
        m = self.ids()
        self.assertEqual(m['session_ids'], [A_ID, B_ID],
                         'attempts land oldest-first: #a2@2 then #a10@10, newest LAST')
        # through the ONE fold the surfaces actually serialize:
        folded = wc.fold_child_metrics([m])
        self.assertEqual(folded['session_ids'], [A_ID, B_ID],
                         'the additive fold is a dedup passthrough — order survives')
        self.assertEqual(folded['session_ids'][-1], B_ID,
                         'the open target is the NEWER durable id, not the lexically-first one')

    def test_insertion_order_does_not_steal_the_last_slot(self):
        # The same facts inserted the other way around: identical output.
        self.seed([self.row(A_ID, 2, 2.0), self.row(B_ID, 10, 10.0)])
        self.assertEqual(self.ids()['session_ids'], [A_ID, B_ID])

    # -- 2. same-time tie: deterministic rowid break, later attempt wins ------
    def test_same_time_tie_breaks_by_rowid(self):
        self.seed([self.row(A_ID, 2, 7.0), self.row(B_ID, 10, 7.0)])
        m = self.ids()
        self.assertEqual(m['session_ids'], [A_ID, B_ID],
                         'tied started_at breaks by rowid (insertion): the re-attempt '
                         'lands LAST, so the selector rides the fresh session — never '
                         'lexicon, never dict-insertion luck')

    # -- 3. absent id: honest absence, metrics intact --------------------------
    def test_id_less_schema_keeps_metrics_without_the_key(self):
        legacy = FULL_SCHEMA.replace('id text, ', '')
        sid, title, *rest = self.row(A_ID, 2, 2.0)
        self.seed([tuple([title] + rest)], schema=legacy)
        m = self.ids()
        self.assertEqual(m.get('session_ids') or [], [], 'no id column -> no ids, never an invented one')
        folded = wc.fold_child_metrics([m])
        self.assertNotIn('session_ids', folded,
                         'THE ONE fold keeps the key absent on empty (ee14242a honest-absence law): '
                         'the serialized payload stays byte-identical to pre-cj2 shapes')
        self.assertEqual((folded['tokens_in'], folded['attempts']), (10, 1), 'metrics behavior unchanged')

    # -- 4. runtime-shaped id rides verbatim at its chronological slot ---------
    def test_unverified_shape_recorded_verbatim_in_order(self):
        self.seed([self.row(RUNTIME_ID, 10, 10.0), self.row(A_ID, 2, 2.0)])
        m = self.ids()
        self.assertEqual(m['session_ids'], [A_ID, RUNTIME_ID],
                         'the read model never repairs IDs; the UI selector validates the '
                         'LAST shipped entry it is given — a runtime-shaped current attempt '
                         'renders UNAVAILABLE and never promotes the older stored id '
                         '(captain counterexample, test_stored_session_nav.mjs)')

    # -- 5. metrics aggregation behavior preserved -----------------------------
    def test_metrics_totals_and_boundary_facts_unchanged(self):
        self.seed([self.row(B_ID, 10, 10.0), self.row(A_ID, 2, 2.0)])
        m = self.ids()
        self.assertEqual(m['tokens_in'], 20)
        self.assertEqual(m['tokens_out'], 10)
        self.assertEqual(m['attempts'], 2)
        self.assertEqual(m['started'], 2.0, 'started stays the MINIMUM across attempts')
        self.assertEqual(m['api_calls'], 4)
        self.assertTrue(m['api_calls_known'])
        self.assertIsNone(m['ended'])   # both rows unended

    def test_fold_omission_policy_unchanged(self):
        self.seed([self.row(B_ID, 10, 10.0), self.row(A_ID, 2, 2.0)])
        m = self.ids()
        m['api_calls_known'] = False
        folded = wc.fold_child_metrics([m])
        self.assertNotIn('api_calls', folded, 'unknown count stays absent through the fold')
        self.assertNotIn('session_ids_expired', folded,
                         'no expired row -> no flag key (common payloads stay byte-identical)')
        self.assertNotIn('_session_id_at', folded,
                         'merge stamps are private to the read model — never serialized')

    # -- 6. a new rotation whose row is NOT YET recorded ------------------------
    def test_unrecorded_rotation_never_fabricates_then_relands(self):
        self.seed([self.row(A_ID, 2, 2.0)])
        self.assertEqual(self.ids()['session_ids'], [A_ID],
                         'no row for the new attempt = no fabricated id; the last '
                         'RECORDED fact is the destination until the row lands')
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute('insert into sessions values (' + ','.join(['?'] * len(self.row(B_ID, 3, 30.0))) + ')',
                      self.row(B_ID, 3, 30.0))
        self.assertEqual(self.ids()['session_ids'], [A_ID, B_ID],
                         'the next fetch re-lands the LAST slot on the fresh attempt')

    # -- 7. expiry by removal: the row IS the authoritative lookup --------------
    def test_row_removal_drops_the_destination(self):
        self.seed([self.row(A_ID, 2, 2.0)])
        self.assertEqual(self.ids()['session_ids'], [A_ID])
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute('delete from sessions')
        self.assertNotIn(KEY, wc.child_metrics('orderfix', home=self.home),
                         'a removed row removes the fold: the destination goes absent, '
                         'never stale — the nav link renders unavailable')

    # -- 8. expiry observed at the column: flagged IN its slot, not dropped -----
    def test_expired_current_attempt_flagged_not_dropped(self):
        exp = FULL_SCHEMA[:-1] + ', expiry_finalized int)'
        self.seed([self.exp_row(A_ID, 2, 2.0, 0), self.exp_row(B_ID, 3, 30.0, 1)], schema=exp)
        m = self.ids()
        self.assertEqual(m['session_ids'], [A_ID, B_ID],
                         'the expired id keeps its chronological slot — dropping it would '
                         'promote the older attempt into the current-attempt position')
        folded = wc.fold_child_metrics([m])
        self.assertEqual(folded['session_ids_expired'], [B_ID],
                         'the flag rides as a session_ids subsequence (total order, no '
                         'set-iteration luck): the selector reads a flagged LAST entry '
                         'as absence')
        self.assertEqual((folded['attempts'], folded['tokens_in']), (2, 20),
                         'metrics of an expired row stay counted — only navigation gates')

    # -- 9. profile transition: the same skey across two homes ------------------
    def test_profile_transition_cross_home_merge_lands_newest_last(self):
        import json
        homes = {}
        for tag in ('homeA', 'homeB'):
            h = self.home / tag
            h.mkdir()
            with closing(sqlite3.connect(h / 'state.db')) as c, c:
                c.execute(FULL_SCHEMA)
            homes[tag] = h

        def put(tag, r):
            with closing(sqlite3.connect(homes[tag] / 'state.db')) as c, c:
                c.execute('insert into sessions values (' + ','.join(['?'] * len(r)) + ')', r)

        run = self.home / 'orderfix'
        (run / 'nodes').mkdir(parents=True)
        # Per-home child_metrics folds ONLY that home's rows — the same skey in
        # the other home is never appended (no cross-home leak at the seam).
        put('homeA', self.row(A_ID, 2, 2.0))
        put('homeB', self.row(RUNTIME_ID, 3, 30.0))
        self.assertEqual(wc.child_metrics('orderfix', home=homes['homeA'])[KEY]['session_ids'], [A_ID])
        self.assertEqual(wc.child_metrics('orderfix', home=homes['homeB'])[KEY]['session_ids'], [RUNTIME_ID])
        # Both routed homes merge additively through run_child_metrics. Node-record
        # names (the scan order) are NOT chronology, so the merge sorts by each
        # id's own (started-known, started_at, rowid) stamp: the LAST slot must be
        # the globally-newest row's id whichever home it came from.
        (run / 'nodes' / 'one.json').write_text(json.dumps({'profile_home': str(homes['homeA'])}))
        (run / 'nodes' / 'two.json').write_text(json.dumps({'profile_home': str(homes['homeB'])}))
        merged = wc.run_child_metrics(run)[KEY]
        self.assertEqual(merged['session_ids'], [A_ID, RUNTIME_ID],
                         'newest (RUNTIME@30) LAST regardless of scan order')
        # The other scan direction: NEWER home scanned FIRST must still lose the
        # last slot to the newer ROW, not to scan order (the wrong-current-attempt
        # trap the kickoff names — merging/deduping cannot make it win).
        with closing(sqlite3.connect(homes['homeA'] / 'state.db')) as c, c:
            c.execute('delete from sessions')
            c.execute('insert into sessions values (' + ','.join(['?'] * len(self.row(RUNTIME_ID, 3, 30.0))) + ')',
                      self.row(RUNTIME_ID, 3, 30.0))
        with closing(sqlite3.connect(homes['homeB'] / 'state.db')) as c, c:
            c.execute('delete from sessions')
            c.execute('insert into sessions values (' + ','.join(['?'] * len(self.row(A_ID, 2, 2.0))) + ')',
                      self.row(A_ID, 2, 2.0))
        merged = wc.run_child_metrics(run)[KEY]
        self.assertEqual(merged['session_ids'], [A_ID, RUNTIME_ID],
                         'flipped scan: stamp order survives, the superseded older '
                         'attempt never steals the last slot')
        self.assertEqual(merged['attempts'], 2, 'metrics merge additively across homes')
        folded = wc.fold_child_metrics([merged])
        self.assertEqual(folded['session_ids'], [A_ID, RUNTIME_ID],
                         'THE ONE fold passes the merged chronology through verbatim')
        self.assertNotIn('_session_id_at', folded,
                         'the stamp map is private to the read model — payloads unchanged')


class CurrentAttemptBinding(unittest.TestCase):
    """Wave E (captain missing-current counterexample): the CURRENT attempt is
    the exact title the run's own records name — never the last surviving DB
    row. Deleting the #a10 row must NOT promote #a2: an independently known
    newer attempt with no verified stored row renders `Session unavailable`
    with zero navigation calls (click path pinned end-to-end by
    tests/test_current_attempt_replay_cj2.py and the plugin selector pins in
    tests/test_stored_session_nav.mjs)."""

    RUN = 'bindfix'
    KEY = f'wf:{RUN}:node:12345678.123456'
    A_ID = 'local-' + 'a' * 64      # attempt #a2
    B_ID = 'local-' + 'b' * 64      # attempt #a10 / #a3 (the newer one)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cj2-bind-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.db = self.home / 'state.db'
        self.run_dir = self.home / self.RUN
        (self.run_dir / 'nodes').mkdir(parents=True)

    def row(self, sid, attempt, started, key=None, model='fake'):
        title = f'{key or self.KEY}#a{attempt}'
        return (sid, title, model, 10, 5, 1, 0, 2, 3, 0.5, started, 'tick', None, started)

    def seed(self, rows, schema=FULL_SCHEMA, db=None):
        marks = ','.join('?' * len(rows[0]))
        with closing(sqlite3.connect(db or self.db)) as c, c:
            c.execute(schema)
            c.executemany(f'insert into sessions values ({marks})', rows)

    def record(self, name, db_home=None, **facts):
        rec = {'profile_home': str(db_home or self.home)}
        rec.update(facts)
        (self.run_dir / 'nodes' / f'{name}.json').write_text(json.dumps(rec))

    def fold(self):
        merged = wc.run_child_metrics(self.run_dir)
        self.assertIn(self.KEY, merged, 'the skey fold must exist for its own rows')
        return wc.fold_child_metrics([merged[self.KEY]])

    # -- the exact current row IS the destination ------------------------------
    def test_bound_destination_is_the_exact_current_attempt_row(self):
        self.seed([self.row(self.B_ID, 10, 10.0), self.row(self.A_ID, 2, 2.0)])
        self.record('one', status='done', skey=self.KEY, spawn=10)
        folded = self.fold()
        self.assertEqual(folded['session_ids'], [self.A_ID, self.B_ID])
        self.assertEqual(folded['session_current'], self.B_ID,
                         'the record names #a10; the #a10 row answers — the destination is that id')
        self.assertNotIn('_session_current', folded, 'the binding stamp is private; only the fold key serializes')

    # -- a known spawn whose row has not landed: computed absence --------------
    def test_known_spawn_missing_row_fails_closed(self):
        self.seed([self.row(self.A_ID, 2, 2.0)])
        self.record('one', status='running', skey=self.KEY, attempt=3, pid=None)
        folded = self.fold()
        self.assertEqual(folded['session_ids'], [self.A_ID], 'the older row stays inspectable')
        self.assertIn('session_current', folded, 'a claim computes the destination — presence is the signal')
        self.assertIsNone(folded['session_current'],
                          'spawn #a3 known, its row not yet present: ABSENT, never the older survivor')

    # -- the captain counterexample: newest row removed, older survives --------
    def test_removed_current_attempt_never_promotes_the_survivor(self):
        self.seed([self.row(self.A_ID, 2, 2.0), self.row(self.B_ID, 10, 10.0)])
        self.record('one', status='done', skey=self.KEY, spawn=10)
        before = self.fold()
        self.assertEqual(before['session_current'], self.B_ID)
        with closing(sqlite3.connect(self.db)) as c, c:
            removed = c.execute('delete from sessions where id=?', (self.B_ID,))
            self.assertEqual(removed.rowcount, 1)
        after = self.fold()
        self.assertEqual(after['session_ids'], [self.A_ID], 'the fold keeps the surviving row for inspection')
        self.assertIsNone(after['session_current'],
                          'the known current #a10 has no verified stored row: the older attempt is NOT current')

    # -- a survivor the record actually proves current --------------------------
    def test_proven_current_survivor_binds(self):
        self.seed([self.row(self.A_ID, 2, 2.0)])
        self.record('one', status='done', skey=self.KEY, spawn=2)
        self.assertEqual(self.fold()['session_current'], self.A_ID,
                         'the record names #a2 and the #a2 row answers — a positive exact binding')

    # -- honest absence: no claim, no key (historical payloads byte-identical) --
    def test_claimless_records_gain_no_key(self):
        self.seed([self.row(self.A_ID, 2, 2.0), self.row(self.B_ID, 10, 10.0)])
        self.record('one', status='done')   # a pre-cj2 fixture shape: profile_home only (test 9 pattern)
        folded = self.fold()
        self.assertEqual(folded['session_ids'], [self.A_ID, self.B_ID])
        self.assertNotIn('session_current', folded,
                         'no attempt claim = the documented last-entry fallback, no new key')

    def test_legacy_idless_schema_gains_no_key(self):
        legacy = FULL_SCHEMA.replace('id text, ', '')
        sid, title, *rest = self.row(self.A_ID, 2, 2.0)
        self.seed([tuple([title] + rest)], schema=legacy)
        self.record('one', status='done', skey=self.KEY, spawn=2)
        folded = self.fold()
        self.assertNotIn('session_current', folded,
                         'id-less historical rows cannot bind — the selector keeps its documented fallback')

    # -- expiry is the selector\'s business: the binding rides verbatim ---------
    def test_expired_current_attempt_binds_and_flags(self):
        exp = FULL_SCHEMA[:-1] + ', expiry_finalized int)'
        self.seed([(self.row(self.A_ID, 2, 2.0) + (0,)), (self.row(self.B_ID, 10, 10.0) + (1,))], schema=exp)
        self.record('one', status='done', skey=self.KEY, spawn=10)
        folded = self.fold()
        self.assertEqual(folded['session_current'], self.B_ID,
                         'the binding selects the exact current row VERBATIM; select-before-validate '
                         'still drops a flagged entry — no promotion of the older attempt')
        self.assertEqual(folded['session_ids_expired'], [self.B_ID])

    # -- an amended history: the surviving newer row is NOT the current attempt --
    def test_amended_superseded_skey_never_wins_the_destination(self):
        stale_key = f'wf:{self.RUN}:node:aaaaaaaa.aaaaaa'
        self.seed([self.row(self.A_ID, 2, 10.0),                   # the CURRENT skey: started earlier
                   self.row(self.B_ID, 4, 30.0, key=stale_key)])   # superseded skey, later row
        self.record('one', status='done', skey=self.KEY, spawn=2)
        merged = wc.run_child_metrics(self.run_dir)
        folded = wc.fold_child_metrics([merged[self.KEY], merged[stale_key]])
        self.assertEqual(folded['session_ids'], [self.A_ID, self.B_ID],
                         'chronology puts the superseded later-started row last')
        self.assertEqual(folded['session_current'], self.A_ID,
                         'the record claims only the live skey — its last-surviving row is the destination, '
                         'never the superseded spawn that merely started later')

    # -- profile rotation: the claim binds across homes ------------------------
    def test_cross_home_claim_binds_the_exact_owner(self):
        homes = {}
        for tag in ('hA', 'hB'):
            h = self.home / tag
            h.mkdir()
            with closing(sqlite3.connect(h / 'state.db')) as c:
                c.execute(FULL_SCHEMA)
            homes[tag] = h
        r = self.row(self.A_ID, 2, 2.0)
        with closing(sqlite3.connect(homes['hA'] / 'state.db')) as c, c:
            c.execute('insert into sessions values (' + ','.join(['?'] * len(r)) + ')', r)
        r3 = self.row(self.B_ID, 3, 30.0)
        with closing(sqlite3.connect(homes['hB'] / 'state.db')) as c, c:
            c.execute('insert into sessions values (' + ','.join(['?'] * len(r3)) + ')', r3)
        self.record('one', db_home=homes['hA'], status='done', skey=self.KEY, spawn=3)
        self.record('two', db_home=homes['hB'])
        self.assertEqual(self.fold()['session_current'], self.B_ID,
                         'the child rotated to another profile home: the exact #a3 title binds through '
                         'the merged rows whichever home holds it')
        # The claim rides the OTHER record file — same verdict, never scan order.
        (self.run_dir / 'nodes' / 'one.json').write_text(json.dumps({'profile_home': str(homes['hA'])}))
        (self.run_dir / 'nodes' / 'two.json').write_text(
            json.dumps({'profile_home': str(homes['hB']), 'status': 'done', 'skey': self.KEY, 'spawn': 3}))
        self.assertEqual(self.fold()['session_current'], self.B_ID)


if __name__ == '__main__':
    unittest.main(verbosity=2)
