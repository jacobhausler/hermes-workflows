#!/usr/bin/env python3
"""est-37d74 (#453) — fanout.precheck_argv: a per-fanout custody probe evaluated
before each item's child spawn. Exit 0 -> the item spawns; non-zero -> the item
commits `skipped` with the precheck output tail as its reason, NEVER failed,
zero tokens spent, and the fan-out's failure math EXCLUDES the skipped row
(same treatment as stop-cancelled bookkeeping).

The fake precheck is /bin/cat of a custody note that rides in the item's own
work dir (fixed argv, no shell — the same no-shell law as gate wait.until_argv):
  item A  work dir seeded with custody.note -> cat rc=0 -> SPAWNS,
  item B  dir purged                        -> cat rc=1 (stderr names the file)
                                              -> committed skipped, reason
                                              carries rc + the stderr tail.
The failure-math exclusion is proven on the IMPLICIT majority quorum: a 2-item
fan-out without `quorum` needs 2/2; without the exclusion item B would darken
the node (quorum death). With it, quorum_req shrinks to 1, the single merged
output certifies the aggregate, and the node commits DONE with skipped_items=1.

RED-proof (pre-fix engine): the runner ignores the unknown fanout key entirely
— BOTH items spawn (fake log 2 lines), no record ever says skipped, and
skipped_items is absent; the door-side refusals below FAIL because pre-fix
FANOUT_KEYS rejects `precheck_argv` as an unknown key.

Runnable two ways (repo convention):
  PYTHONPATH=/opt/hermes:.. python3 tests/test_fanout_precheck_453.py
prints PASS/FAIL lines + a TOTAL/PASS/FAIL summary, exit 0 = green; pytest can
also collect the test_* functions directly.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wf            # noqa: E402
import wfcommon      # noqa: E402

FAKE = str(HERE / "fake")
NOTE = "custody.note"
SCHEMA = {"type": "object", "required": ["result"],
          "properties": {"result": {"type": "string"}}}

fails = total = 0


def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not ok else ""),
          flush=True)
    if not ok:
        fails += 1


# ---- isolated harness (empty HERMES_HOME + mktemp WF_RUNS_ROOT; hostile WF_*/
# FAKE_*/HERMES_WF_* stripped so an inherited env can never steer the engine) ----
_scratch = Path(tempfile.mkdtemp(prefix="wf453-"))
BASE_ENV = {k: v for k, v in os.environ.items()
            if not k.startswith("WF_") and not k.startswith("FAKE_")
            and not k.startswith("HERMES_WF_")
            and k not in ("HERMES_HOME",)}
BASE_ENV["HERMES_HOME"] = str(_scratch / "home")
BASE_ENV["WF_RUNS_ROOT"] = str(_scratch / "runs")
BASE_ENV["FAKE_LOG"] = str(_scratch / "fake.log")
os.makedirs(BASE_ENV["HERMES_HOME"], exist_ok=True)


def fan_graph(precheck, quorum=None):
    fo = {"items": [{"id": "A"}, {"id": "B"}],
          "goal": "PROCESS roster {item} reply", "precheck_argv": precheck}
    if quorum is not None:
        fo["quorum"] = quorum
    return {"name": "est-453-precheck", "nodes": [
        {"id": "fan", "type": "agent", "goal": "PROCESS roster reply", "fanout": fo}]}


def mk(run_id, graph, seed_a_note=True, seed_b_note=False):
    r = Path(BASE_ENV["WF_RUNS_ROOT"]) / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    # Seed the per-item custody notes BEFORE the runner starts: child_work_dir's
    # mkdir(exist_ok=True) preserves them, /bin/cat reads them as the fake probe.
    for idx, seeded in ((0, seed_a_note), (1, seed_b_note)):
        wd = r / "work" / f"fan.{idx}"
        wd.mkdir(parents=True)
        if seeded:
            (wd / NOTE).write_text(f"roster row {idx} still live in the tracker\n")
    (r / "graph.json").write_text(json.dumps(graph))
    (r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "item_concurrency": 2}))
    # ONE fake-log per run: spawn counting never bleeds across scenarios.
    BASE_ENV["FAKE_LOG"] = str(_scratch / f"fake-{run_id}.log")
    return r


def wf_cmd(run_id, timeout=120):
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                          env=dict(BASE_ENV), capture_output=True, text=True, timeout=timeout)


def item_rec(r, i):
    p = r / "nodes" / f"fan.{i}.json"
    return json.loads(p.read_text()) if p.exists() else None


def agg_rec(r):
    p = r / "nodes" / "fan.json"
    return json.loads(p.read_text()) if p.exists() else None


def events(r):
    p = r / "events.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def fake_log_lines():
    p = Path(BASE_ENV["FAKE_LOG"])
    return p.read_text().splitlines() if p.exists() else []


# ---------------------------------------------------------------- door ----

def test_door_accepts_good_shape_and_refuses_shell_shapes():
    """Shape law mirrors gate wait.until_argv EXACTLY: non-empty list of
    non-empty strings; anything else refused naming fanout.precheck_argv."""
    ns = lambda argv: [{"id": "fan", "type": "agent", "goal": "g {item}",
                        "fanout": {"goal": "t {item}", "items": [{"a": 1}],
                                  **({"precheck_argv": argv} if argv is not ... else {})}}]
    errs = wfcommon.validate_graph_errors(ns(["/bin/cat", NOTE]))
    check("door: good fixed-argv shape accepted",
          not [e for e in errs if "precheck" in str(e.get("field", "")) + str(e.get("msg", ""))],
          str(errs))
    for bad in ("/bin/cat custody.note || true", [], ["/bin/cat", ""], [1], {"argv": ["/bin/cat"]}):
        errs = wfcommon.validate_graph_errors(ns(bad))
        hits = [e for e in errs if "fanout.precheck_argv" == e.get("field")]
        check(f"door: refuses non-list/non-string-shape {type(bad).__name__}:{str(bad)[:24]}",
              bool(hits) and "fixed argv, no shell" in hits[0]["msg"], str(errs)[:200])
    # the closed set itself carries the new key
    check("door: precheck_argv is a member of FANOUT_KEYS", "precheck_argv" in wfcommon.FANOUT_KEYS)
    # unknown-key message enumerates the sorted set including the new key
    e = wfcommon.validate_graph_errors([
        {"id": "fan", "type": "agent", "goal": "g {item}",
         "fanout": {"goal": "t {item}", "items": [{"a": 1}], "precheck_nope": ["/bin/true"]}}])
    msg = next((x["msg"] for x in e if x.get("field") == "fanout.precheck_nope"), "")
    check("door: unknown-key message names the set WITH precheck_argv (sorted)",
          '"precheck_argv"' in msg, msg)


def test_door_refuses_surviving_run_ref_in_precheck_argv():
    """#792 carry-over: a {run.KEY} surviving run_context rendering in a fixed
    argv surface refuses at the door — now on fanout.precheck_argv too."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("wfdoor453", ROOT / "__init__.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        refusal = mod._unbound_gate_argv_refs(
            {"nodes": [{"id": "fan", "type": "agent", "goal": "g {item}",
                        "fanout": {"goal": "t {item}", "items": [{"a": 1}],
                                   "precheck_argv": ["/bin/cat", "{run.NOTE_FILE}"]}}]})
        check("door: {run.KEY} survivor in precheck_argv refused before any write",
              refusal is not None and "fanout.precheck_argv[1]" in refusal.get("error", ""),
              str(refusal))
        clean = mod._unbound_gate_argv_refs(
            {"nodes": [{"id": "fan", "type": "agent", "goal": "g {item}",
                        "fanout": {"goal": "t {item}", "items": [{"a": 1}],
                                   "precheck_argv": ["/bin/cat", "custody.note"]}}]})
        check("door: literal precheck_argv passes the unbound-ref scan", clean is None, str(clean))
    except Exception as e:
        check("door module importable for the unbound-argv refusal", False,
              f"{type(e).__name__}: {e}")


# ------------------------------------------------------------- engine ----

def test_item_a_spawns_item_b_committed_skipped_with_reason():
    """THE acceptance run: A precheck rc=0 -> spawns and commits done; B rc=1 ->
    committed skipped whose reason carries the precheck rc and the stderr tail
    naming the purged custody note; B spent ZERO tokens (never spawned)."""
    graph = fan_graph(["/bin/cat", NOTE])
    r = mk("est453-core", graph, seed_a_note=True, seed_b_note=False)
    out = wf_cmd("est453-core").stdout
    check("core: run finishes done", "WORKFLOW_DONE" in out, out[-200:])
    rec_a, rec_b = item_rec(r, 0), item_rec(r, 1)
    agg = agg_rec(r)
    check("core: item A spawned and committed done with output",
          rec_a and rec_a.get("status") == "done" and rec_a.get("output") is not None
          and rec_a.get("spawn_cmd") and rec_a.get("skey"),
          json.dumps(rec_a)[:200] if rec_a else "missing")
    check("core: item B committed SKIPPED (never failed)",
          rec_b and rec_b.get("status") == "skipped"
          and rec_b.get("error_class") == "precheck_skipped",
          json.dumps(rec_b)[:200] if rec_b else "missing")
    reason = (rec_b or {}).get("reason") or (rec_b or {}).get("error") or ""
    check("core: B's reason carries the precheck rc and the stderr tail",
          "rc=1" in reason and NOTE in reason, reason[:200])
    check("core: the reason is mirrored into the record's error field",
          (rec_b or {}).get("error") == (rec_b or {}).get("reason"),
          json.dumps({k: (rec_b or {}).get(k) for k in ("reason", "error")})[:200])
    evs = events(r)
    fin_b = [e for e in evs if e["event"] == "item.finished" and e.get("index") == 1]
    check("core: item.finished(1) says skipped, names the reason, NO skey (zero tokens)",
          len(fin_b) == 1 and fin_b[0]["status"] == "skipped"
          and fin_b[0].get("error_class") == "precheck_skipped"
          and "rc=1" in (fin_b[0].get("error") or "")
          and fin_b[0].get("skey") is None and fin_b[0].get("child_log_path") is None,
          json.dumps(fin_b)[:250])
    check("core: item 1 NEVER started",
          not [e for e in evs if e["event"] == "item.started" and e.get("index") == 1])
    check("core: ZERO tokens for B — exactly one child spawned in total",
          len(fake_log_lines()) == 1, str(fake_log_lines()))


def test_failure_math_excludes_skipped_items():
    """No explicit quorum: implicit majority of 2 items is 2/2 — WITHOUT the
    exclusion B's skip would darken the node (quorum death). WITH it the
    denominator shrinks, the lone merged output certifies the aggregate, and
    the node commits done naming skipped_items — no failure anywhere."""
    graph = fan_graph(["/bin/cat", NOTE])          # same run dir as above, fresh id
    r = mk("est453-math", graph, seed_a_note=True, seed_b_note=False)
    out = wf_cmd("est453-math").stdout
    check("math: run done", "WORKFLOW_DONE" in out, out[-200:])
    agg = agg_rec(r) or {}
    check("math: aggregate DONE (not a quorum death over the skipped row)",
          agg.get("status") == "done", f"{agg.get('status')}/{agg.get('error_class')}")
    o = agg.get("output") or {}
    check("math: failed_items is 0 and skipped_items is 1",
          o.get("failed_items") == 0 and o.get("skipped_items") == 1, json.dumps(o)[:220])
    ar = o.get("all_results") or []
    check("math: all_results[1] is the skipped row carrying its item back",
          len(ar) == 2 and ar[1]["status"] == "skipped" and ar[1].get("item") == {"id": "B"},
          json.dumps(ar[1:])[:220])
    evs = events(r)
    nf = [e for e in evs if e["event"] == "node.failed"]
    done_ev = [e for e in evs if e["event"] == "node.finished"]
    check("math: node.finished event, NO node.failed for the fan node",
          len(nf) == 0 and len(done_ev) == 1
          and done_ev[0].get("node") == "fan" and done_ev[0].get("skipped") == 1,
          json.dumps(nf or done_ev)[:220])
    # 765 law holds across the skip: done aggregate backed by committed per-item
    # facts — A done+output, B skipped, BOTH efp-valid committed records.
    byid = {n["id"]: n for n in graph["nodes"]}
    ok_pairs = []
    for i, want in ((0, "done"), (1, "skipped")):
        rec = item_rec(r, i) or {}
        ok_pairs.append(rec.get("status") == want
                        and wfcommon.record_efp_valid(rec, byid, graph["nodes"][0]))
    check("math: per-item canonical records are efp-valid committed facts (A done, B skipped)",
          ok_pairs == [True, True], str(ok_pairs))
    check("math: read model agrees — run status done",
          wfcommon.run_state(r)["status"] == "done")


def test_all_items_purged_commits_done_with_zero_spawn():
    """A fully-stale roster: every row prechecks dead. The node does NOT fail —
    it commits done over a zero-item harvest, both rows skipped, zero tokens."""
    graph = fan_graph(["/bin/cat", NOTE])
    r = mk("est453-purged", graph, seed_a_note=False, seed_b_note=False)
    out = wf_cmd("est453-purged").stdout
    check("purged: run finishes done", "WORKFLOW_DONE" in out, out[-200:])
    agg = agg_rec(r) or {}
    check("purged: node done with failed_items 0, skipped_items 2, zero merged",
          agg.get("status") == "done" and (agg.get("output") or {}).get("failed_items") == 0
          and (agg.get("output") or {}).get("skipped_items") == 2
          and (agg.get("output") or {}).get("items") == [],
          json.dumps(agg)[:250])
    check("purged: no child ever spawned", len(fake_log_lines()) == 0, str(fake_log_lines()))


def test_probe_that_cannot_run_skips_with_typed_reason():
    """A precheck binary that cannot exec (missing file) is a non-live verdict,
    not a node crash: both items commit skipped with the exception named."""
    graph = fan_graph([str(_scratch / "no-such-probe")])
    r = mk("est453-nobin", graph)
    out = wf_cmd("est453-nobin").stdout
    check("nobin: run finishes done", "WORKFLOW_DONE" in out, out[-200:])
    recs = [item_rec(r, i) or {} for i in (0, 1)]
    check("nobin: both rows skipped, reason names the failure honestly",
          all(x.get("status") == "skipped" for x in recs)
          and all("precheck rc=" in (x.get("reason") or "") for x in recs),
          json.dumps([{k: x.get(k) for k in ("status", "reason")} for x in recs])[:300])
    check("nobin: zero tokens spent", len(fake_log_lines()) == 0)


def main():
    for fn in (test_door_accepts_good_shape_and_refuses_shell_shapes,
               test_door_refuses_surviving_run_ref_in_precheck_argv,
               test_item_a_spawns_item_b_committed_skipped_with_reason,
               test_failure_math_excludes_skipped_items,
               test_all_items_purged_commits_done_with_zero_spawn,
               test_probe_that_cannot_run_skips_with_typed_reason):
        try:
            fn()
        except Exception as e:
            import traceback
            traceback.print_exc()
            check(fn.__name__ + " (raised)", False, f"{type(e).__name__}: {e}")
    print(f"TOTAL {total} PASS {total - fails} FAIL {fails}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
