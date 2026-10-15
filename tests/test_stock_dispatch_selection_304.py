#!/usr/bin/env python3
"""#304 peer-review regressions (findings 2 & 3): the card ledger follows
GENUINE SELECTION — never reference liveness, never arbitrary attribute access.

Stock upstream v2026.9.24 / v0.21.5 resolves EVERY callback result through
``resolve_plugin_command_result`` (hermes_cli/plugins.py, reached from
plugins_dispatch._invoke_hook_callback), whose first move is
``inspect.isawaitable(result)`` — that hasattr/``__class__`` touch lands on
EVERY non-None result long before winner selection. And core keeps only the
FIRST non-empty string (agent/turn_finalizer.apply_llm_output_transform)
while the dispatch results list RETAINS every non-None result until the call
returns. So:

* attribute access is not delivery proof (finding 3): a resolved-but-losing
  result must write ZERO card.echoed markers;
* a still-referenced proposal at the next call is not delivery proof either
  (finding 2): the results list may retain losing proposals, and an
  abandoned worker's reconcile can run mid-dispatch before selection. Only
  the selection witness (bool coercion at first-non-empty selection) or the
  ``_witness`` seam may vouch; the unselected card stays replayable.

All cases run the REAL resolver semantics via a verbatim mirror of
apply_llm_output_transform, under the shipped default (no witness bound).
"""
import gc
import importlib.util
import inspect
import json
import os
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))


def _load_door():
    spec = importlib.util.spec_from_file_location("hw_stock_dispatch", ROOT / "__init__.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolve_result(result):
    """Behavioural mirror of hermes_cli/plugins.py resolve_plugin_command_result
    (v2026.9.24) for hook returns: EVERY result passes through
    ``inspect.isawaitable`` — the real stdlib predicate, so the resolver's
    hasattr/``__class__`` touches on a str subclass are the production ones."""
    if not inspect.isawaitable(result):
        return result
    raise AssertionError("coroutine results are out of scope for this plugin")


def dispatch_and_select(hook_results):
    """Verbatim shape of agent/turn_finalizer.py apply_llm_output_transform
    (v2026.9.24): results are resolved as they're appended, then the FIRST
    non-empty string wins (``isinstance(r, str) and r``). Returns
    (winner, retained) — core's results list keeps EVERY resolved non-None
    result, winners and losers alike, until the call returns."""
    results = []
    for hr in hook_results:
        ret = resolve_result(hr)
        if ret is not None:
            results.append(ret)
    winner = next((r for r in results if isinstance(r, str) and r), None)
    return winner, results


class _Ctx:
    def __init__(self):
        self.hooks, self.tools, self.config_reads = {}, [], 0

    def register_hook(self, name, fn):
        self.hooks[name] = fn

    def register_tool(self, **kw):
        self.tools.append(kw)

    def register_command(self, *_, **__):
        pass

    def register_skill(self, *_, **__):
        pass

    def get_config(self, key, default):
        self.config_reads += 1
        return default


class StockDispatchSelection(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory(dir=ROOT / "tests")
        self.env = mock.patch.dict(os.environ, {
            "HERMES_HOME": self.home.name,
            "WF_RUNS_ROOT": str(Path(self.home.name) / "workflows"),
            "HERMES_WF_HERMES_BIN": "offline",
        })
        self.env.start()
        os.environ.pop("HERMES_SESSION_ID", None)
        self.hw = _load_door()
        self.ce = self.hw._card_enforcement
        import wf_test_isolation
        wf_test_isolation.install(self.hw)
        self.ctx = _Ctx()
        self.hw.register(self.ctx)
        self.hook = self.ctx.hooks["transform_llm_output"]
        self.runs = Path(os.environ["WF_RUNS_ROOT"])
        self.assertIsNone(self.ce._witness, "shipped default: no witness seam bound")

    def tearDown(self):
        self.env.stop()
        self.home.cleanup()

    def mk_run(self, rid, sid="S"):
        r = self.runs / rid
        (r / "nodes").mkdir(parents=True)
        started = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(timespec="seconds")
        (r / "run.json").write_text(json.dumps(
            {"name": "t", "started": started, "owner": {"session_id": sid}}))
        return r

    def markers(self, r):
        p = r / "events.jsonl"
        if not p.exists():
            return 0
        return sum(1 for ln in p.read_text().splitlines()
                   if ln.strip() and json.loads(ln).get("event") == "card.echoed")

    def fire(self, turn, text="All done."):
        return self.hook(response_text=text, session_id="S", turn_id=turn,
                         platform="desktop", model="m")

    # ---- finding 3: the REAL resolver must not confirm a losing proposal ------
    def test_resolver_access_on_losing_result_writes_no_marker(self):
        r = self.mk_run("r-lose")
        ours = self.fire("t1")
        self.assertIsNotNone(ours)
        peer_text = "peer answer (wins first)"
        winner, retained = dispatch_and_select([peer_text, ours])
        self.assertEqual(winner, peer_text)                  # earlier peer wins
        self.assertIn(ours, retained)                        # core retained the loser
        # The resolver already touched our text (isawaitable -> hasattr chain).
        # That is NOT delivery: zero markers, and the card must replay next turn.
        del ours, retained, winner
        gc.collect()
        self.assertEqual(self.markers(r), 0,
                         "losing result confirmed the card — resolver access is not delivery")
        again = self.fire("t2")
        w2, _ = dispatch_and_select([again])
        self.assertIsNotNone(w2, "owed card was lost, not replayed")
        self.assertIn('::workflow{id="r-lose"}', w2)
        self.assertEqual(self.markers(r), 1, "delivered card must be ledgered exactly once")
        self.assertIsNone(self.fire("t3"), "ledgered card must never ship again")

    # ---- finding 2: a retained-but-never-selected proposal is not shipped -----
    def test_retained_unselected_proposal_drops_and_replays(self):
        r = self.mk_run("r-live")
        ours = self.fire("t1")
        self.assertIsNotNone(ours)
        winner, retained = dispatch_and_select(["earlier peer wins", ours])
        self.assertEqual(winner, "earlier peer wins")
        self.assertIn(ours, retained)          # results list holds the loser alive
        # Next call's reconcile runs with our text ALIVE the whole time.
        nxt = self.fire("t2")
        self.assertEqual(self.markers(r), 0,
                         "a still-referenced unselected proposal was stamped shipped")
        self.assertIsNotNone(nxt, "owed card was treated as shipped; it must replay")
        w2, _ = dispatch_and_select([nxt])
        self.assertIn('::workflow{id="r-live"}', w2)
        self.assertEqual(self.markers(r), 1)
        self.assertIsNone(self.fire("t3"))

    # ---- finding 2 (event-controlled): parked worker's reconcile mid-dispatch --
    def test_parked_worker_reconcile_never_confirms_unselected_fresh_proposal(self):
        # Deterministic repro from the review: worker A parks in _reconcile; a
        # fresh proposal is taken and retained in the dispatch results list;
        # worker A resumes BEFORE selection runs and then an earlier peer wins.
        # The abandoned reconciliation must not write card.echoed for the
        # unselected fresh text — the owed card stays replayable, shipped once.
        r = self.mk_run("r-evt")
        real_reconcile = self.ce._reconcile
        parked, release = threading.Event(), threading.Event()

        def gated_reconcile(sid, turn):
            if threading.current_thread().name == "hermes-hook-A":
                parked.set()
                self.assertTrue(release.wait(5))
            return real_reconcile(sid, turn)

        outcome = {}

        def runner():                                        # core's bounded worker
            outcome["value"] = self.fire("tA")

        with mock.patch.object(self.ce, "_reconcile", gated_reconcile):
            worker = threading.Thread(target=runner, name="hermes-hook-A", daemon=True)
            worker.start()
            self.assertTrue(parked.wait(5))                  # abandoned mid-reconcile
            fresh = self.fire("tB")                          # fresh call id proposes
            self.assertIsNotNone(fresh)
            release.set()                                    # worker A resumes...
            worker.join(5)                                   # (test-only; core never joins)
            winner, retained = dispatch_and_select(["earlier peer wins", fresh, None])
            # worker A already reconciled while `fresh` was retained unselected.
            self.assertEqual(winner, "earlier peer wins")
            self.assertIn(fresh, retained)
        self.assertEqual(self.markers(r), 0,
                         "abandoned reconcile stamped an unselected proposal shipped")
        del fresh, winner, retained, outcome
        gc.collect()
        nxt = self.fire("tC")
        self.assertIsNotNone(nxt, "owed card lost — parked reconcile treated it shipped")
        w3, _ = dispatch_and_select([nxt])
        self.assertIn('::workflow{id="r-evt"}', w3)
        self.assertEqual(self.markers(r), 1)


if __name__ == "__main__":
    unittest.main()
