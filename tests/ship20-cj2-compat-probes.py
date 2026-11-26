#!/usr/bin/env python3.14
"""Frozen compatibility probes for the CJ2 publication-ordering battery
(bd_2026-11-13-s20-cj2-recovery). TEST-ONLY.

Every substrate fact here is IMPORTED, not reimplemented: the committed
battery (ship20-cj2-faults-probes.py, historical bytes) is loaded as a
library, which pins — for this checkout or for nothing — that the runner
(wf.main over a patched wf.run_child, make_run, prep_output,
capture_fanout_input, skey_for, _release_terminal_lock), the shared
substrate (wfcommon.fanout_inputs_read / fanout_input_value), the carrier
layout (fanout-inputs/<nid>.json, {"version":N,"items":{i:{k:{skey,item}}}}),
the dashboard (plugin_api._view item_metrics extraction, session_id_for era
oracle) and the session fixture schema still work exactly as historical. A
product change to any of these fails THIS file before any verdict is
computed. Legs then only mutate DATA (the carrier bytes, the aggregate's
item facts, claim metadata presence) and read the shipped reader.

Vocabulary is the committed battery's: check(ok, note) records an
unexplained law break; redpin(rid, note) fires a named historical-gap pin;
okline(note) records a law that held. Exit 1 when any failure was recorded.
"""
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

_a = sys.argv[1:]


def _flag(name):
    if name in _a:
        return _a[_a.index(name) + 1]
    pos = {"--leg": 0, "--checkout": 1, "--out": 2}[name]
    if len(_a) > pos:
        return _a[pos]
    raise SystemExit(f"missing {name}")


LEG = _flag("--leg")
REPO = Path(_flag("--checkout")).resolve()
ROOT = Path(_flag("--out")).resolve()
ROOT.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location(
    "cj2_hist_probes", REPO / "tests" / "ship20-cj2-faults-probes.py")
CB = importlib.util.module_from_spec(_spec)
_saved = sys.argv
sys.argv = [_saved[0], "compat", str(REPO), str(ROOT)]
_spec.loader.exec_module(CB)
sys.argv = _saved

wf, wc, door, API = CB.wf, CB.wc, CB.door, CB.API
RUNS, make_run, prep_output, dump, read = CB.RUNS, CB.make_run, CB.prep_output, CB.dump, CB.read
seed_db, insert_session, session_id_for, view_rows = (
    CB.seed_db, CB.insert_session, CB.session_id_for, CB.view_rows)
check, redpin, okline = CB.check, CB.redpin, CB.okline
failures, bank = CB.failures, CB.bank

ROSTER = ["Alpha", "Bravo"]
SENTINEL = "cj2-compat-sentinel-0000"
STALE = "cj2-compat-stale-0000000000"


def settle_wave(name):
    """One settled two-item dynamic fan-out (dict form), the committed
    launch: make_run + patched run_child that inserts the generation's chat
    and returns the claim shape. Returns (run, [record skeys])."""
    run, ref = make_run(name, ROSTER, "dict", node_extra={"timeout": 20}, width=2)
    graph = read(run / "graph.json")
    graph["nodes"] = [n for n in graph["nodes"] if n["id"] != "empty"]
    graph["nodes"][1].pop("on_fail", None)
    dump(run / "graph.json", graph)
    seed_db()
    labels = list(ROSTER)

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node["id"] == "prep":
            return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                        output=prep_output(labels, "dict"))
        insert_session(skey + "#a0")
        return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                    output={"result": "ok"})

    with patch.object(wf, "run_child", child), \
            patch.object(wf, "notify", lambda *a, **kw: None):
        wf.main(name)
        wf._release_terminal_lock(run)
    skeys = [read(run / "nodes" / f"review.{i}.json")["skey"]
             for i in range(len(ROSTER))]
    return run, skeys


def side_path(run):
    return run / "fanout-inputs" / "review.json"


def image_of(run):
    return read(side_path(run))


def put_image(run, image):
    p = side_path(run)
    p.chmod(0o644)
    dump(p, image)


def with_items(run, value):
    """Every capture slot's item set to `value` (keys and shape preserved)."""
    img = image_of(run)
    for entry in img["items"].values():
        for slot in entry.values():
            slot["item"] = value
    put_image(run, img)


def with_suffixed(run):
    """Each slot's skey carries a bogus attempt suffix — a WRONG-attempt key
    that must never answer for the record's base."""
    img = image_of(run)
    for entry in img["items"].values():
        for slot in entry.values():
            slot["skey"] = slot["skey"] + "#a9"
    put_image(run, img)


def with_version(run, value):
    img = image_of(run)
    if value == "drop":
        img.pop("version", None)
    else:
        img["version"] = value
    put_image(run, img)


def strip_agg_item_facts(run):
    out = read(run / "nodes" / "review.json")
    for r in (out.get("output", {}).get("all_results") or []):
        r.pop("item", None)
    out["output"].pop("items", None)
    dump(run / "nodes" / "review.json", out)


def row_items(rows):
    return [rows[i].get("item") for i in sorted(rows)]


def row_chats(rows):
    return [rows[i].get("session_current") for i in sorted(rows)]


# ---------------------------------------------------------------- ordering views
def leg_ordering_views():
    """The publication-ordering law at the shipped reader, plus the
    record-first vs carrier-first classification it implements.

    With the aggregate's own item facts INTACT, mutating the dispatch
    capture (sentinel value, wrong-attempt keys, stale value, version
    shapes, absence) may never change what the view answers: the reader is
    RECORD-FIRST iff the roster's own label survives, CARRIER-FIRST iff the
    mutated value answers — and either way a wrong-attempt key or a vanished
    capture must supply absence, never ANOTHER label (pin:
    stale-carrier-supplies-label). With the item facts STRIPPED from the
    aggregate, the classification completes: a reader with a live capture
    path paints the EXACT-key dispatch value (proven by a sentinel) and
    stays silent for every wrong shape; a reader with no capture path at
    all is record-only and honest absence is its answer. Both are lawful
    worlds; a third label from history is neither. Every world keeps its
    own chat adjacency."""
    run, skeys = settle_wave("compat-ordering")
    good = side_path(run).read_bytes()
    own = [session_id_for(s + "#a0") for s in skeys]
    base = view_rows(run)
    bank("ordering-intact-baseline", base)
    if row_items(base) != ROSTER:
        check(False, f"baseline: settled labels {row_items(base)} != {ROSTER}")
    if row_chats(base) != own:
        check(False, f"baseline: settled chats {row_chats(base)} != {own}")

    def world(label, strip, mut):
        side_path(run).write_bytes(good)
        side_path(run).chmod(0o644)
        mut(run)
        if strip:
            strip_agg_item_facts(run)
        rows = view_rows(run)
        bank(f"ordering-{label}", rows)
        got = row_items(rows)
        if row_chats(rows) != own:
            check(False, f"{label}: mutation lost chat adjacency: {row_chats(rows)}")
        return got

    def m_none(r):
        pass

    def m_sentinel(r):
        with_items(r, SENTINEL)

    def m_stale(r):
        with_items(r, STALE)

    def m_suffixed(r):
        with_suffixed(r)

    def m_absent(r):
        p = side_path(r)
        if p.exists():
            p.chmod(0o644)
            p.unlink()

    # -- intact-aggregate worlds: no carrier mutation may change the answer
    paints = world("intact-sentinel", False, m_sentinel)
    world("intact-stale", False, m_stale)
    world("intact-suffixed", False, m_suffixed)
    world("intact-absent", False, m_absent)
    world("intact-restored", False, m_none)

    if paints == ROSTER:
        ordering = "record-first"
        okline("record-first: the aggregate's own item facts answer ahead of "
               "the capture (no carrier mutation painted)")
    elif paints == [SENTINEL, SENTINEL]:
        ordering = "carrier-first"
        okline("carrier-first: the dispatch capture answers ahead of the "
               "aggregate (its own era's value, proven by a sentinel)")
    else:
        ordering = "mixed"
        redpin("stale-carrier-supplies-label",
               f"intact-era sentinel mutation answered {paints!r} — neither "
               f"the record's labels {ROSTER!r} nor the capture's own value")

    # -- stripped-aggregate worlds: classify the capture path
    sent = world("stripped-sentinel", True, m_sentinel)
    if sent == [SENTINEL, SENTINEL]:
        capture_path = True
        okline("stripped-era: the EXACT-key capture paints the dispatched "
               "value (live capture path at the view)")
    elif all(g in (None, "") for g in sent):
        capture_path = False
        okline("record-only at the view: with the aggregate's item facts "
               "stripped the capture does not answer; honest absence")
    else:
        capture_path = None
        check(False, f"stripped-era sentinel answered {sent!r} — a partial "
                     "capture path painting a third label")

    suf = world("stripped-suffixed", True, m_suffixed)
    if any(g not in (None, "") for g in suf):
        redpin("stale-carrier-supplies-label",
               f"a wrong-attempt (suffixed) key answered for its base: {suf!r}")
    stale = world("stripped-stale", True, m_stale)
    if capture_path is True and stale != [STALE, STALE]:
        check(False, f"live capture path ignored the exact-key stale value: {stale!r}")
    if capture_path is False and any(g not in (None, "") for g in stale):
        redpin("stale-carrier-supplies-label",
               f"the record-only reader painted {stale!r} from a mutated capture")
    ab = world("stripped-absent", True, m_absent)
    if any(g not in (None, "") for g in ab):
        redpin("stale-carrier-supplies-label",
               f"a vanished capture supplied a label from history: {ab!r}")
    if row_chats(view_rows(run)) != own:
        check(False, f"chat adjacency did not survive the worlds: {row_chats(view_rows(run))}")
    side_path(run).write_bytes(good)
    side_path(run).chmod(0o600)
    return (f"world={ordering}, capture-path-at-view={capture_path}; "
            "wrong/stale inputs supplied absence, never another label")


# -------------------------------------------------------------- version shape
def leg_version_shape():
    """A Boolean (or False, or float) version is never legitimate
    metadata-absence. At the reader seam (fanout_inputs_read) a malformed
    version must fail closed EXACTLY like a doc with no version key, and at
    the view the two worlds must be indistinguishable in every field the
    join answers (pins: boolean-version-labels / float-version-labels, the
    committed ids)."""
    run, skeys = settle_wave("compat-version")
    good = side_path(run).read_bytes()
    own = [session_id_for(s + "#a0") for s in skeys]

    def world(value):
        side_path(run).write_bytes(good)
        side_path(run).chmod(0o644)
        with_version(run, value)
        seam = bool(wc.fanout_inputs_read(run, "review"))
        rows = view_rows(run)
        bank(f"version-{value!r}", {"seam": seam, "rows": rows})
        return seam, row_items(rows), row_chats(rows)

    ref = world("drop")          # legitimate metadata-absence is the reference
    check(ref[0] is False, f"legitimate metadata-absence was NOT accepted at "
                           f"the seam: {ref[0]}")
    for value, rid in ((True, "boolean-version-labels"),
                       (False, "boolean-version-labels"),
                       (1.5, "float-version-labels")):
        got = world(value)
        if got != ref:
            redpin(rid, f"version={value!r} is distinguishable from "
                        f"metadata-absence: {got} vs reference {ref}")
        else:
            okline(f"version={value!r} fails closed exactly like metadata-absence")
    side_path(run).write_bytes(good)
    side_path(run).chmod(0o600)
    return "malformed version shapes vs metadata-absence compared at seam and view"


# ------------------------------------------------------------ unnamed history
def leg_unnamed_history():
    """A history record with no claim (skey/attempt stripped) keeps the
    documented last-entry law byte-identically and keeps its OWN chat: a
    foreign run's session in the same home must never answer for the
    unnamed member (pin: unnamed-history-loses-chat). The item label is
    aggregate data, not claim metadata, so it may stand — the chat is the
    law."""
    import sqlite3
    run, skeys = settle_wave("compat-unnamed")
    own = [session_id_for(s + "#a0") for s in skeys]
    foreign = insert_session("wf:not-my-run:review:0#0")
    home = Path(os.environ["HERMES_HOME"])
    now = time.time()
    with sqlite3.connect(home / "state.db") as c, c:
        for sid in own:                       # each row's OWN chat is the latest
            c.execute("UPDATE sessions SET last_activity_at=?, started_at=? WHERE id=?",
                      (now + 100, now + 100, sid))
        c.execute("UPDATE sessions SET last_activity_at=?, started_at=? WHERE id=?",
                  (now - 100, now - 100, foreign))   # the foreign chat is older
    for i in range(len(ROSTER)):
        rec = read(run / "nodes" / f"review.{i}.json")
        rec.pop("skey", None)
        rec.pop("attempt", None)
        rec.pop("spawn", None)
        dump(run / "nodes" / f"review.{i}.json", rec)
    rows = view_rows(run)
    bank("unnamed-history", rows)
    for i in sorted(rows):
        cur = rows[i].get("session_current")
        ids = rows[i].get("session_ids") or []
        if cur == foreign or foreign in ids:
            redpin("unnamed-history-loses-chat",
                   f"unnamed row {i} answered with the foreign chat: {cur!r} {ids}")
        elif cur != own[i]:
            redpin("unnamed-history-loses-chat",
                   f"unnamed row {i} did not keep its own chat: {cur!r} "
                   f"(own last entry = {own[i]})")
    okline("unnamed history: last-entry law stands, each row kept its own chat")
    return "unnamed rows keep last-entry law and their own chat"


# ---------------------------------------------------------------- controls
def leg_control_static_roster():
    """POSITIVE control at every root: a STATIC def roster is a pure value
    of the captured revision — with the dispatch capture DELETED the view
    must still answer its own labels (they are the record's, never a
    borrowed dynamic label). If the dynamic legs fail while this passes,
    the defect is the dynamic capture's join, not the view."""
    run, ref = make_run("compat-static", ROSTER, "dict", node_extra={"timeout": 20},
                        width=2)
    graph = read(run / "graph.json")
    graph["nodes"] = [n for n in graph["nodes"] if n["id"] != "empty"]
    graph["nodes"][1].pop("on_fail", None)
    graph["nodes"][1]["fanout"] = {"items": list(ROSTER), "goal": "review {item}"}
    dump(run / "graph.json", graph)
    seed_db()

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node["id"] == "prep":
            return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                        output={"items": list(ROSTER)})
        insert_session(skey + "#a0")
        return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                    output={"result": "ok"})

    with patch.object(wf, "run_child", child), \
            patch.object(wf, "notify", lambda *a, **kw: None):
        wf.main("compat-static")
        wf._release_terminal_lock(run)
    p = side_path(run)
    if p.exists():
        p.chmod(0o644)
        p.unlink()
    rows = view_rows(run)
    got = row_items(rows)
    check(got == ROSTER, f"static-roster control lost its own label without "
                         f"a capture: {got}")
    okline("static def roster keeps its label with the capture deleted")
    return f"static control: {got}"


def leg_control_writer_probes():
    """POSITIVE control at every root — the capture seam through the
    product's own writer (wf.capture_fanout_input, the committed probe's
    own call shape): round-trip, and wrong-attempt silence at the decoder."""
    run = RUNS / "compat-writer"
    (run / "nodes").mkdir(parents=True)
    node = {"id": "review", "type": "agent", "goal": "review {item}",
            "fanout": {"items_from": "prep.items"}}
    byid = {"review": node}
    guard = CB.threading.Lock()
    key = wf.skey_for(run, byid, node, 0)
    wf.capture_fanout_input(run, guard, node, 0, key, ROSTER[0], 2)
    img = wc.fanout_inputs_read(run, "review")
    check(img is not None and bool(img), "writer: capture did not read back")
    ok, val = wc.fanout_input_value(img, 0, key)
    check(ok and val == ROSTER[0], f"decoder: exact key lost the item: {ok} {val!r}")
    ok, val = wc.fanout_input_value(img, 0, key + "#a9")
    check(not ok and val is None,
          f"decoder: wrong-attempt key answered for its base: {ok} {val!r}")
    ok, val = wc.fanout_input_value(img, 7, key)
    check(not ok and val is None, f"decoder: out-of-range index answered: {ok} {val!r}")
    okline("capture seam round-trips; wrong-attempt keys stay silent")
    return "capture seam probes complete"


LEGS = {"ordering-views": leg_ordering_views,
        "version-shape": leg_version_shape,
        "unnamed-history": leg_unnamed_history,
        "control-static-roster": leg_control_static_roster,
        "control-writer-probes": leg_control_writer_probes}

if __name__ == "__main__":
    if LEG not in LEGS:
        raise SystemExit(f"unknown leg {LEG!r}")
    note = LEGS[LEG]()
    print(f"LEG {LEG}: {note}", flush=True)
    sys.exit(1 if failures else 0)
