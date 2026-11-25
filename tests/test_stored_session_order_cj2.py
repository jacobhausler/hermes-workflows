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
     started-min, ended rules unchanged.
"""
import importlib.util
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
                         'the read model never repairs IDs; the UI shape gate drops the '
                         'runtime-shaped entry and re-lands on the newest STORED one')

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
