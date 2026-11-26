"""bd_2026-11-13-cj2 (cj2-retention): stale fan-out dispatch-input keys die
at the canonical settlement transition — nowhere earlier, nowhere later.

This is the in-repo retention slice of the era stress (the narrow scheduler
and scaling controls): a dynamic fan-out wave re-expanding under a bumped
ancestor must PROTECT the labeled input of the still-current canonical while
the replacement is pending (the plan write carries old+new), and once every
dispatched item's record has committed — the settlement transition — the
carrier must hold EXACTLY the keys the on-disk canonical records still carry
at same-width turnover, shrink, empty and regrow. Obsolete keys surviving a
settle are the baseline red this test pins.

Write-shape laws asserted with it (bounded, one batch): every writing era
serializes its whole image once per write and lands each via tmp+replace
(serialize-image == temp-write == replace, zero fsync), at most one plan
write plus one bounded settlement-prune write per era, and the settlement
prune writes NOTHING when the plan image is already retained (first wave).
The zero-item expansion writes at most once (zero when already retained)
and never disturbs the settled failed record or any old canonical's bytes;
a replay of a settled run is a zero operation; a STATIC wave (items baked
into the def) writes zero carrier bytes end to end. Identity: each item's
prepare-key -> item.started -> transport -> item.finished chain shares one
base key (attempt suffix ignored, exact match) and the settled row keeps
THIS era's label — a settled failure is never permission to relabel old
chat, so the empty era must leave every previous record byte-identical.

Offline: run_child is substituted at the transport seam (the same seam the
era stress names), notify is a no-op, and the model never runs. Eras move
through the door's real act_amend (the sanctioned amendment writer, the
respawn hop stubbed exactly like the era stress stubs it).

Usage: python3.14 -B -IB tests/ship20-cj2-retention.py
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

TMP = Path(tempfile.mkdtemp(prefix="cj2-retention-"))
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


def record(op, **fields):
    with lock:
        rows.append(dict(phase=phase, op=op, **fields))


def scope(path):
    p = Path(path)
    return p.parent.name == "fanout-inputs"


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
    image = json.loads(Path(src).read_bytes())
    result = _orig_replace(src, dst, *a, **kw)
    record("replace", image=image)
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


wf = load("cj2_ret_runner", "wf.py")
door = load("cj2_ret_door", "__init__.py", package=True)


def keys_of(image):
    return {s["skey"] for entry in image["items"].values() for s in entry.values()}


def record_keys():
    out = {}
    for p in (run / "nodes").glob("review.*.json"):
        out[p.stem.rsplit(".", 1)[1]] = json.loads(p.read_text())["skey"]
    return out


carrier = None
run = None
NAME = "cj2-retention-eras"


def wave(gen, labels, amend=True):
    """One era: real door amend (gen>0), real runner under the substituted
    transport, returning the ops the era produced."""
    global phase
    phase = f"era{gen}"
    if gen and amend:
        with patch.object(door, "_respawn_runner", lambda _: None):
            resp = door.act_amend({"run_id": NAME,
                                   "patch": {"nodes": {"prep": {"goal": f"era {gen}"}}}})
        assert resp.get("ok") and {"prep", "review"} <= set(resp.get("will_rerun") or []), resp
    mark = len(rows)
    size = len(labels)

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node["id"] == "prep":
            output = {"items": labels}
        elif node["id"] == "empty":
            output = {"empty": True}
        else:
            assert node["id"] == "review" and goal == "review " + labels[index], (goal, index)
            record("transport", index=index, key=skey)
            output = {"result": "child output (no copied item)"}
        return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done", output=output)

    events = []

    def log(r, event, **kw):
        if r == run and kw.get("node") == "review" and event in ("item.started", "item.finished"):
            events.append((event, kw["index"], kw["skey"]))
        return original_log(r, event, **kw)

    original_log = wf.log
    original_key = wf.skey_for

    def key(r, byid, node, index=None):
        k = original_key(r, byid, node, index)
        if node["id"] == "review":
            record("prepare-key", index=index, key=k)
        return k

    with patch.object(wf, "run_child", child), patch.object(wf, "notify", lambda *a, **kw: None), \
            patch.object(wf, "log", log), patch.object(wf, "skey_for", key):
        try:
            wf.main(NAME)
        finally:
            wf._release_terminal_lock(run)
    return rows[mark:], events, size


def check_era(gen, wedge, events, size, old, labels):
    global carrier
    # PRIMARY: the retention law — no obsolete keys, exact settled key set,
    # and the peak bound, judged before any write-shape accounting.
    final = json.loads(carrier.read_text())
    fin = keys_of(final)
    anchored = set(record_keys().values())
    stale = sorted(fin - anchored)
    assert not stale, f"era{gen}: {len(stale)} obsolete keys after settle"
    assert fin == anchored, (gen, "settled carrier != currently required keys")
    ser = [r for r in wedge if r["op"] == "serialize-image"]
    tw = [r for r in wedge if r["op"] == "temp-write"]
    repl = [r for r in wedge if r["op"] == "replace"]
    assert len(ser) == len(tw) == len(repl), (gen, "write layers diverge",
                                              len(ser), len(tw), len(repl))
    assert not [r for r in wedge if r["op"] == "fsync"], (gen, "fsync entered the writer")
    # bounded: one plan write (+1 settlement prune when the plan was not
    # already retained); the first wave plans once, the empty wave at most once.
    assert len(repl) <= 2 and (len(repl) >= 1 if size else len(repl) <= 1), (gen, len(repl))
    expected = 1 if gen == 0 else (0 if size == 0 else 2)
    assert len(repl) == expected, (gen, "writer-count off the settlement law", len(repl), expected)
    counts = []
    pending_seen = False
    for r in repl:
        if not r["image"]:
            continue
        counts.append(len(keys_of(r["image"])))
        if size and old:
            if r is repl[0]:
                # pending protection: the plan image still carries every old
                # key — the old chat's label survives until its replacement
                # record settles, no earlier.
                assert old <= keys_of(r["image"]), (gen, "plan dropped a pending key")
                pending_seen = True
    assert (not old) or pending_seen or size == 0, (gen, "plan missing")
    peak = max(counts, default=len(fin))
    assert peak <= len(old) + size, (gen, "peak keys", peak, len(old) + size)
    # identity: one base key per item across the whole chain, THIS era's
    # label at the row and in the settled carrier slot.
    per = {}
    for ev, index, k in events:
        base = str(k).split("#a", 1)[0]
        seen = per.setdefault(index, set())
        assert base in seen or not seen, (gen, index, "chain split across bases")
        seen.add(base)
    assert sorted(per) == list(range(size)), (gen, "chain coverage")
    settled = {str(i): {s["skey"]: s["item"] for s in entry.values()}
               for i, entry in final["items"].items()}
    for i in range(size):
        base = per[i].pop()
        assert len(per[i]) == 0, (gen, i, "chain carried two bases")
        slot = settled.get(str(i))
        assert slot and base in slot, (gen, i, "settled key lost from the carrier")
        assert slot[base] == labels[i], (gen, i, "row relabeled under the settled key")
    assert sorted(carrier.parent.iterdir()) == [carrier], (gen, "temp residue")


def static_leg():
    """A STATIC wave (items baked into the def) writes zero carrier bytes —
    the settlement hook must not speak for waves that never captured."""
    global phase, run, carrier
    phase = "static"
    name = "cj2-retention-static"
    run = ROOT / name
    (run / "nodes").mkdir(parents=True)
    labels = ["STATIC_ITEM_%d_%s" % (i, "z" * 8) for i in range(3)]
    _orig_write(Path(run / "run.json"), json.dumps({"name": name, "item_concurrency": 2}))
    _orig_write(Path(run / "graph.json"), json.dumps({"name": name, "nodes": [
        {"id": "review", "type": "agent", "goal": "review {item}",
         "fanout": {"items": labels, "goal": "review {item}"}}]}))
    carrier = run / "fanout-inputs/review.json"

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                    output={"result": "ok"})

    mark = len(rows)
    with patch.object(wf, "run_child", child), patch.object(wf, "notify", lambda *a, **kw: None):
        try:
            wf.main(name)
        finally:
            wf._release_terminal_lock(run)
    wedge = rows[mark:]
    for op in ("serialize-slot", "serialize-image", "temp-write", "replace", "fsync"):
        assert not [r for r in wedge if r["op"] == op], ("static", op)
    assert not (run / "fanout-inputs").exists(), "static wave created a carrier"


def main():
    global phase, run, carrier
    phase = "build"
    run = ROOT / NAME
    (run / "nodes").mkdir(parents=True)
    carrier = run / "fanout-inputs/review.json"
    _orig_write(Path(run / "run.json"), json.dumps({"name": NAME, "item_concurrency": 4}))
    _orig_write(Path(run / "graph.json"), json.dumps({"name": NAME, "nodes": [
        {"id": "prep", "type": "agent", "goal": "era 0"},
        {"id": "review", "type": "agent", "goal": "review {item}", "after": ["prep"],
         "on_fail": "empty",
         "fanout": {"items_from": "prep.items", "goal": "review {item}"}},
        {"id": "empty", "type": "agent", "goal": "report empty"}]}))
    widths = [4, 4, 4, 2, 0, 4]     # first, same-width turnover x2, shrink, empty, regrow
    old = set()
    prev_bytes = {}
    with patch.object(json, "dumps", dumps), patch.object(Path, "write_text", write), \
            patch.object(os, "replace", replace), patch.object(os, "fsync", fsync):
        for gen, size in enumerate(widths):
            labels = [f"CJ2_ITEM_{i:04d}_" + chr(97 + gen) * 8 for i in range(size)]
            if gen % 2:
                labels.reverse()
            # snapshot every per-item record byte BEFORE each wave: the
            # empty era's law is that a zero-item settlement rewrites none
            # of them (compared immediately after that wave only).
            for p in (run / "nodes").glob("review.*.json"):
                prev_bytes[p.name] = p.read_bytes()
            wedge, events, size = wave(gen, labels)
            if size == 0:
                # the settled failure stands: an empty era may not rewrite an
                # old canonical's bytes (no relabeling of old chat).
                agg = json.loads((run / "nodes/review.json").read_text())
                assert agg["status"] == "skipped" and agg.get("caught_error_class") == "fanout_empty", agg
                for name_, blob in prev_bytes.items():
                    assert (run / "nodes" / name_).read_bytes() == blob, name_
            check_era(gen, wedge, events, size, old, labels)
            old = keys_of(json.loads(carrier.read_text()))
            # the wave that already holds its replacement keys settles with
            # the plan image retained: verify the next plan's pending window
            # before any prune is allowed to speak.
            assert sorted(carrier.parent.iterdir()) == [carrier]
        # replay/adoption no-mint: re-driving the settled run touches nothing.
        phase = "replay"
        mark = len(rows)
        wedge, _, _ = wave(len(widths), [f"CJ2_ITEM_{i:04d}_" + "r" * 8 for i in range(4)],
                           amend=False)
        assert not [r for r in wedge if r["op"] in
                    ("serialize-slot", "serialize-image", "temp-write", "replace")], \
            "replay of a settled run wrote the carrier"
        static_leg()
    print("cj2-retention: eras", widths, "green; replay and static legs zero;",
          len(rows), "operations", flush=True)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
