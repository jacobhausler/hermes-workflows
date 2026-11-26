"""bd_2026-11-13-s20-cj2-retention: prune-budget verifier (separately named).

The frozen cj2-recovery era matrix (tests/ship20-cj2-faults-probes.py, eras-*
legs) asserts ONE whole-image write per non-empty generation. That total is
incompatible with the published retention acceptance at this pin: with fresh
per-era keys, protecting the old canonical while its replacement is pending
requires the dispatch image to carry old+new, and "no obsolete keys at
settlement" requires the final image to carry only the record-anchored keys —
two different contents for one atomic file ⇒ AT LEAST two whole-image writes
for any non-first era. The published acceptance (tests/ship20-cj2-retention.py
docstring and check_era; the bead row's "bounded writes") therefore scopes the
count to ONE pre-start plan write PLUS AT MOST ONE bounded settlement-prune
write, zero when the plan image is already retained. This verifier pins that
scoped law directly; the frozen battery legs are NOT modified or re-called
green here (they stand banked red against this stricter-than-acceptance law).

Laws asserted, both roster forms (dict, list), eras first/turnover/empty/
shrink/regrow/fault-turnover/heal:
  * one atomic dispatch: the plan replace lands BEFORE the first item.started,
    and every item event lands between the plan and the prune;
  * the settlement prune replace lands AFTER the last item.finished (the prune
    fires only after final item completion), is the era's LAST writer act, and
    mints nothing: no prepare-key/transport/serialize-slot after it;
  * at most one plan + one prune (<= 2 whole-image writes per era); layers
    stay equal (serialize-image == temp-write == replace attempts, zero fsync);
  * the prune image is a STRICT SUBSET of the plan image (no remint, no new
    keys, never grows bytes), its slot values are byte-carried (no label
    drift), and it equals the record-anchored key set exactly (no obsolete
    keys at settlement);
  * real-fault control: an injected rename refusal at the prune leaves the
    carrier byte-identical to the plan image (unchanged-byte control), leaves
    no temp residue, completes the wave, and the obsolete keys are healed by
    the NEXT era's normal budget — bounded staleness, no extra state;
  * the empty era writes at most once (zero when already retained) and
    rewrites no record or carrier byte; replay of a settled run is a zero
    operation with unchanged carrier bytes (no extra publish).

Static-zero is the published test's remit and is not re-asserted here.
Offline: run_child substituted at the transport seam, notify no-op, door's
real act_amend with the respawn hop stubbed — identical seams to
ship20-cj2-retention.py.

Usage: python3.14 -B -IB tests/ship20-cj2-prune-budget.py
Exit: 0 only with every check green.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
from unittest.mock import patch

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo))

TMP = Path(tempfile.mkdtemp(prefix="cj2-prune-budget-"))
ROOT = TMP / "work"
ROOT.mkdir(parents=True)
os.environ["WF_RUNS_ROOT"] = str(ROOT)
os.environ["HERMES_HOME"] = str(TMP / "home")
os.environ["HERMES_QUIET"] = "1"

_orig_dump, _orig_write = json.dumps, Path.write_text
_orig_replace, _orig_fsync = os.replace, os.fsync
rows = []
phase = "boot"
lock = threading.Lock()
prune_fault = [False]      # when True: refuse the era's SECOND scope replace
scope_replaces = [0]       # successful scope replaces since the era started


def record(op, **fields):
    with lock:
        fields["seq"] = len(rows) + 1
        rows.append(dict(phase=phase, op=op, **fields))


def scope(path):
    return Path(path).parent.name == "fanout-inputs"


def dumps(obj, *a, **kw):
    caller = sys._getframe(1)
    carrier = (isinstance(obj, dict) and {"version", "items"} <= obj.keys()
               and caller.f_code.co_filename == str(repo / "wf.py"))
    slot = (caller.f_code.co_name in ("capture_fanout_input", "_publish_fanout_inputs")
            and isinstance(obj, dict) and set(obj) == {"skey", "item"})
    op = "serialize-image" if carrier else "serialize-slot" if slot else None
    text = _orig_dump(obj, *a, **kw)
    if op:
        record(op, bytes=len(text.encode("utf-8", errors="replace")))
    return text


def write(path, text, *a, **kw):
    if not scope(path):
        return _orig_write(path, text, *a, **kw)
    result = _orig_write(path, text, *a, **kw)
    record("temp-write", bytes=len(text.encode("utf-8", errors="replace")))
    return result


def replace(src, dst, *a, **kw):
    if not scope(dst):
        return _orig_replace(src, dst, *a, **kw)
    data = Path(src).read_bytes()
    if prune_fault[0] and scope_replaces[0] >= 1:
        prune_fault[0] = False                     # refuse this one prune only
        record("replace", ok=False, bytes=len(data), image=json.loads(data))
        raise OSError("cj2 prune-budget injected settlement-rename refusal")
    result = _orig_replace(src, dst, *a, **kw)
    scope_replaces[0] += 1
    record("replace", ok=True, bytes=len(data), image=json.loads(data),
           data=data)
    return result


def fsync(fd):
    if sys._getframe(1).f_code.co_name in ("capture_fanout_input",
                                           "_publish_fanout_inputs",
                                           "_settle_fanout_inputs"):
        record("fsync")
    return _orig_fsync(fd)


def load(name, rel, package=False):
    spec = importlib.util.spec_from_file_location(
        name, repo / rel,
        submodule_search_locations=[str(repo)] if package else None)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wf = load("cj2_pb_runner", "wf.py")
door = load("cj2_pb_door", "__init__.py", package=True)
# #71 r5: the env pin (assigned above) is NOT a sandbox — the owner's
# settings.runs_root outranks it (resolver precedence #42). Pin the door's
# resolver before any door write. install() is idempotent.
load("cj2_pb_iso71", "tests/wf_test_isolation.py").install(door)

run = None
carrier = None


def keys_of(image):
    return {s["skey"] for entry in image["items"].values() for s in entry.values()}


def slot_map(image):
    return {(i, s["skey"]): s["item"]
            for i, entry in image["items"].items() for s in entry.values()}


def record_keys():
    out = {}
    for p in (run / "nodes").glob("review.*.json"):
        if p.stem.count(".") == 1:
            out[p.stem.rsplit(".", 1)[1]] = json.loads(p.read_text())["skey"]
    return out


def wave(name, gen, labels, amend=True, faulted=False):
    """One era under the journal; returns the era's ordered wedge."""
    global phase
    phase = f"{name}/gen{gen}"
    if gen and amend:
        with patch.object(door, "_respawn_runner", lambda _: None):
            resp = door.act_amend({"run_id": name,
                                   "patch": {"nodes": {"prep": {"goal": f"era {gen}"}}}})
        assert resp.get("ok") and {"prep", "review"} <= set(resp.get("will_rerun") or []), resp
    prune_fault[0] = faulted
    scope_replaces[0] = 0
    mark = len(rows)
    size = len(labels)

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node["id"] == "prep":
            output = {"items": labels} if form == "dict" else [labels]
        elif node["id"] == "empty":
            output = {"empty": True}
        else:
            assert node["id"] == "review" and goal == "review " + labels[index], (goal, index)
            record("transport", index=index, key=skey)
            output = {"result": "child output (no copied item)"}
        return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done", output=output)

    original_log, original_key = wf.log, wf.skey_for

    def log(r, event, **kw):
        if Path(r) == run and kw.get("node") == "review" \
                and event in ("item.started", "item.finished"):
            record(event, index=kw["index"], key=kw.get("skey"))
        return original_log(r, event, **kw)

    def key(r, byid, node, index=None):
        k = original_key(r, byid, node, index)
        if node["id"] == "review" and Path(r) == run:
            record("prepare-key", index=index, key=k)
        return k

    with patch.object(wf, "run_child", child), \
            patch.object(wf, "notify", lambda *a, **kw: None), \
            patch.object(wf, "log", log), patch.object(wf, "skey_for", key):
        try:
            wf.main(name)
        finally:
            wf._release_terminal_lock(run)
    assert not (faulted and prune_fault[0]), "prune fault never armed"
    return rows[mark:]


def check_budget(gen, wedge, size, labels, old_keys, faulted):
    """The scoped write-shape law for one era; returns (plan_image, final_set)."""
    repl = [r for r in wedge if r["op"] == "replace"]
    repl_ok = [r for r in repl if r.get("ok")]
    repl_bad = [r for r in repl if not r.get("ok")]
    ser = [r for r in wedge if r["op"] == "serialize-image"]
    tw = [r for r in wedge if r["op"] == "temp-write"]
    assert len(ser) == len(tw) == len(repl), (gen, "write layers diverge",
                                              len(ser), len(tw), len(repl))
    assert not [r for r in wedge if r["op"] == "fsync"], (gen, "fsync entered the writer")
    assert len(repl_ok) + len(repl_bad) <= 2, (gen, "unbounded whole-image writes", len(repl))
    if faulted:
        assert (len(repl_ok), len(repl_bad)) == (1, 1), (gen, "fault-era write shape",
                                                         len(repl_ok), len(repl_bad))
    elif size:
        assert len(repl_ok) == (1 if not old_keys else 2), (gen, "writer-count off the "
                                                            "settlement law", len(repl_ok))
        assert not repl_bad, (gen, "unexplained failed replace")
    else:
        assert len(repl_ok) <= 1, (gen, "empty wave overwrote", len(repl_ok))
    if not size:
        return repl_ok[0]["image"] if repl_ok else None
    plan, prune = repl_ok[0], repl_ok[-1]
    starts = [r for r in wedge if r["op"] == "item.started"]
    fins = [r for r in wedge if r["op"] == "item.finished"]
    assert len(starts) == len(fins) == size, (gen, "event coverage")
    # one atomic dispatch: the plan precedes the first start; the live window
    # carries ZERO carrier writes; the prune follows the final completion.
    assert plan["seq"] < min(r["seq"] for r in starts), (gen, "plan landed after a start")
    live_end = max(r["seq"] for r in fins)
    assert not [r for r in repl if r is not plan and plan["seq"] < r["seq"] < live_end], \
        (gen, "carrier write inside the live wave window")
    assert len(repl_ok) == 1 or prune["seq"] > live_end, \
        (gen, "prune landed before final item completion")
    if len(repl_ok) == 2:
        k0, k1 = keys_of(plan["image"]), keys_of(prune["image"])
        anchored = set(record_keys().values())
        assert k1 < k0, (gen, "prune image is not a strict subset", sorted(k0), sorted(k1))
        assert k1 == anchored, (gen, "pruned image off the record-anchored key set")
        assert prune["bytes"] <= plan["bytes"], (gen, "prune grew the carrier",
                                                 plan["bytes"], prune["bytes"])
        assert slot_map(prune["image"]).items() <= slot_map(plan["image"]).items(), \
            (gen, "prune drifted a slot value")
        assert prune["seq"] == max(r["seq"] for r in repl), (gen, "writer act after the prune")
        assert not [r for r in wedge if r["op"] in ("prepare-key", "transport",
                                                    "serialize-slot")
                    and r["seq"] > prune["seq"]], (gen, "prune published/reminted")
    else:
        assert faulted or keys_of(plan["image"]) == set(record_keys().values()), \
            (gen, "retained plan image not exactly the anchored set")
    assert keys_of(json.loads(carrier.read_text())) == set(record_keys().values()) \
        or faulted, (gen, "settled carrier holds obsolete keys")
    assert sorted(carrier.parent.iterdir()) == [carrier], (gen, "temp residue")
    return plan["image"]


def run_form(f):
    global phase, run, carrier, form
    form = f
    name = f"cj2-prune-budget-{f}"
    run = ROOT / name
    (run / "nodes").mkdir(parents=True)
    carrier = run / "fanout-inputs/review.json"
    ref = "prep.items" if f == "dict" else "prep.0"
    _orig_write(Path(run / "run.json"), json.dumps({"name": name, "item_concurrency": 4}))
    _orig_write(Path(run / "graph.json"), json.dumps({"name": name, "nodes": [
        {"id": "prep", "type": "agent", "goal": "era 0"},
        {"id": "review", "type": "agent", "goal": "review {item}", "after": ["prep"],
         "on_fail": "empty",
         "fanout": {"items_from": ref, "goal": "review {item}"}},
        {"id": "empty", "type": "agent", "goal": "report empty"}]}))
    # first, turnover, empty, shrink, regrow, fault-turnover, heal
    plan = [(4, False), (4, False), (0, False), (2, False), (4, False), (4, True), (4, False)]
    old_keys: set = set()
    with patch.object(json, "dumps", dumps), patch.object(Path, "write_text", write), \
            patch.object(os, "replace", replace), patch.object(os, "fsync", fsync):
        for gen, (size, faulted) in enumerate(plan):
            labels = [f"PBJ_ITEM_{i:04d}_" + chr(97 + gen) * 32 for i in range(size)]
            if gen % 2:
                labels = list(reversed(labels))
            prev_records = {p.name: p.read_bytes() for p in (run / "nodes").glob("review.*.json")}
            carrier_before = carrier.read_bytes() if carrier.exists() else None
            wedge = wave(name, gen, labels, faulted=faulted)
            if size == 0:
                agg = json.loads((run / "nodes/review.json").read_text())
                assert agg["status"] == "skipped" and agg.get("caught_error_class") == "fanout_empty", agg
                assert {p.name: p.read_bytes() for p in (run / "nodes").glob("review.*.json")} \
                    == prev_records, (gen, "empty era rewrote a record")
                assert carrier.read_bytes() == carrier_before, (gen, "empty era touched the carrier")
                print(f"PASS {name}/gen{gen}: empty era zero-writes, records untouched",
                      flush=True)
                old_keys = keys_of(json.loads(carrier.read_text()))
                continue
            image = check_budget(gen, wedge, size, labels, old_keys, faulted)
            agg = json.loads((run / "nodes/review.json").read_text())
            assert agg["status"] == "done" and len(agg["output"]["all_results"]) == size, \
                (gen, "wave status/results")
            if faulted:
                # unchanged-byte control: the carrier still equals the PLAN image
                # byte-for-byte (the failed prune changed nothing on disk).
                plan_bytes = [r for r in wedge if r["op"] == "replace" and r.get("ok")][0]["data"]
                assert carrier.read_bytes() == plan_bytes, (gen, "faulted prune altered carrier bytes")
                fin = keys_of(json.loads(carrier.read_text()))
                assert old_keys <= fin and fin - set(record_keys().values()), \
                    (gen, "faulted prune did not degrade to stale-presentation")
                print(f"PASS {name}/gen{gen}: real prune fault — carrier bytes unchanged "
                      f"{len(plan_bytes)}B, no residue, wave done, obsolete keys stand", flush=True)
            else:
                n = len([r for r in wedge if r["op"] == "replace" and r.get("ok")])
                print(f"PASS {name}/gen{gen}: eras[{size}] budget green (writes={n}, "
                      + ("plan + strict-subset prune, no remint" if n == 2
                         else "plan retained, zero prune") + ")", flush=True)
            old_keys = keys_of(json.loads(carrier.read_text()))
        # heal leg: obsolete keys from the faulted era died within ONE era
        # (checked implicitly above: gen6 final == anchored, no obsolete).
        # replay no-extra-publish: re-driving the settled run touches nothing.
        phase = f"{name}/replay"
        mark = len(rows)
        wave(name, len(plan), [f"PBJ_ITEM_{i:04d}_" + "r" * 32 for i in range(4)], amend=False)
        wedge = rows[mark:]
        assert not [r for r in wedge if r["op"] in
                    ("serialize-slot", "serialize-image", "temp-write", "replace")], \
            (name, "replay of a settled run wrote the carrier")
        print(f"PASS {name}/replay: zero ops, no extra publish/remint", flush=True)


def main():
    global phase
    phase = "build"
    for f in ("dict", "list"):
        run_form(f)
    print("prune-budget: dict+list green — one plan write + at most one strict-subset "
          "settlement prune, real fault/unchanged-byte controls included;",
          len(rows), "operations", flush=True)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
