#!/usr/bin/env python3
"""cj2-recovery fault probes: one LEG per invocation (isolated subprocess),
driving the REAL scheduler capture seams in-process (M-style bench: the
runner main executes inside this process with the transport stubbed where a
seat would speak; adoption and the schema correction ride a REAL Popen child
that opens no socket). Adapted — not edited — from the prior scheduler-
boundary probes; those fixtures stay byte-identical where they live.

Usage: python3 -B ship20-cj2-faults-probes.py LEG REPO ROOT
Env (set by the battery): WF_RUNS_ROOT (ROOT/workflows), HERMES_HOME
(ROOT/hermes), HOME, TMPDIR, XDG_*, HERMES_WF_PYTHON, WORKFLOW_MAX_SEATS=0.
Prints PASS/REDPIN/FAIL lines; exit 1 iff any FAIL line was printed.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
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
RUNS = Path(os.environ["WF_RUNS_ROOT"])
BANK = ROOT / "banks"
BANK.mkdir(parents=True, exist_ok=True)
os.chdir(REPO)
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

failures = []


def check(ok, note):
    if not ok:
        failures.append(note)
        print("FAIL", note, flush=True)
    return ok


def redpin(rid, note):
    print("REDPIN", rid, note, flush=True)
    failures.append(rid + ": " + note)
    print("FAIL", rid, note, flush=True)


def okline(note):
    print("PASS", note, flush=True)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def read(path):
    return json.loads(Path(path).read_text())


def history(path):
    if not Path(path).exists():
        return []
    return [json.loads(s) for s in Path(path).read_text().splitlines()]


def bank(name, obj):
    safe = name.replace("/", "_")
    (BANK / (safe + ".json")).write_text(json.dumps(obj, indent=2) + "\n")


import wf
import wfcommon as wc

_spec = importlib.util.spec_from_file_location(
    "cj2rec_door", REPO / "__init__.py", submodule_search_locations=[str(REPO)])
door = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(door)

# ---- instrumentation (M-shaped ops journal; global while inside a leg) ----
rows = []
_lock = threading.Lock()
fault = [False]
short_write = [False]
_orig_dump, _orig_write, _orig_replace, _orig_fsync = (
    json.dumps, Path.write_text, os.replace, os.fsync)


def record(op, **fields):
    with _lock:
        rows.append(dict(seq=len(rows) + 1, op=op, thread=threading.get_ident(),
                         **fields))


def scope(path):
    return Path(path).parent.name == "fanout-inputs"


def dumps(obj, *a, **kw):
    caller = sys._getframe(1)
    inwf = caller.f_code.co_filename == str(REPO / "wf.py")
    carrier = isinstance(obj, dict) and {"version", "items"} <= obj.keys() and inwf
    slot = (inwf and isinstance(obj, dict) and set(obj) == {"skey", "item"}
            and caller.f_code.co_name in {"capture_fanout_input",
                                          "_publish_fanout_inputs"})
    op = "serialize-image" if carrier else "serialize-slot" if slot else None
    if op:
        run = caller.f_locals.get("run")
        node = (caller.f_locals.get("node") or {}).get("id", "?")
        dest = str(Path(run) / "fanout-inputs" / (node + ".json")) if run else "?"
    try:
        text = _orig_dump(obj, *a, **kw)
    except Exception:
        if op:
            record(op, path=dest, ok=False, bytes=0)
        raise
    if op:
        record(op, path=dest, ok=True, bytes=len(text.encode("utf-8", errors="replace")))
    return text


def write(path, text, *a, **kw):
    if not scope(path):
        return _orig_write(path, text, *a, **kw)
    ok = False
    try:
        if short_write[0]:
            short_write[0] = False
            _orig_write(path, text[:17], *a, **kw)
            raise OSError("cj2 injected short carrier temp write")
        result = _orig_write(path, text, *a, **kw)
        ok = True
        return result
    finally:
        record("temp-write", path=str(path), ok=ok,
               bytes=Path(path).stat().st_size if Path(path).exists() else 0)


def replace(src, dst, *a, **kw):
    if not scope(dst) and not (Path(dst).parent.name == "nodes"
                               and Path(dst).name.startswith("review")):
        return _orig_replace(src, dst, *a, **kw)
    p = Path(src)
    data = p.read_bytes()
    ok = False
    try:
        if scope(dst) and fault[0]:
            fault[0] = False
            raise OSError("cj2 injected carrier-only rename refusal")
        result = _orig_replace(src, dst, *a, **kw)
        ok = True
        return result
    finally:
        record("replace" if scope(dst) else "commit", path=str(dst), ok=ok,
               bytes=len(data), image=_orig_dump and json.loads(data))


def slots(image):
    return {k: {s["skey"]: s["item"] for s in entry.values()}
            for k, entry in image["items"].items()}


def layers(events):
    return {op: dict(calls=len(ops), failed=sum(not r["ok"] for r in ops),
                     total=sum(r["bytes"] for r in ops),
                     peak=max((r["bytes"] for r in ops), default=0))
            for op in ("serialize-slot", "serialize-image", "temp-write", "replace")
            for ops in [[r for r in events if r["op"] == op]]}


def instrumented(fn, *a, **kw):
    with patch.object(json, "dumps", dumps), patch.object(Path, "write_text", write), \
            patch.object(os, "replace", replace):
        return fn(*a, **kw)


# ---- shared bench pieces (M-shaped) ----
def make_run(name, items, mode, node_extra=None, width=4):
    run = RUNS / name
    (run / "nodes").mkdir(parents=True)
    dump(run / "run.json", {"name": name, "item_concurrency": width})
    ref = "prep.items" if mode == "dict" else "prep.0"
    review = {"id": "review", "type": "agent", "goal": "review {item}",
              "after": ["prep"], "on_fail": "empty",
              "fanout": {"items_from": ref, "goal": "review {item}"}}
    review.update(node_extra or {})
    graph = {"name": name, "nodes": [
        {"id": "prep", "type": "agent", "goal": "era 0"},
        review,
        {"id": "empty", "type": "agent", "goal": "report empty"}]}
    dump(run / "graph.json", graph)
    return run, ref


def prep_output(items, mode):
    return {"items": items} if mode == "dict" else [items]


LEG_TIMEOUT = 240
_t0 = time.monotonic()


def tick():
    if time.monotonic() - _t0 > LEG_TIMEOUT:
        failures.append("leg timeout")
        print("FAIL leg timeout after", LEG_TIMEOUT, "s", flush=True)
        finish()


def finish():
    bank("ops-rows", rows)
    print("PROBE-EXIT", 1 if failures else 0, LEG, flush=True)
    sys.exit(1 if failures else 0)


# the golden CJ2 identity fixture's 14-column shape, verbatim
SESSION_SCHEMA = (
    "create table if not exists sessions (id text, title text, model text, "
    "input_tokens int, output_tokens int, cache_read_tokens int, "
    "reasoning_tokens int, api_call_count int, tool_call_count int, "
    "estimated_cost_usd real, last_activity_at real, "
    "last_activity_description text, ended_at real, started_at real)")


def session_id_for(title):
    return "local-" + hashlib.sha256(title.encode()).hexdigest()[:40]


def seed_db():
    import sqlite3
    home = Path(os.environ["HERMES_HOME"])
    home.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(home / "state.db") as c:
        c.execute(SESSION_SCHEMA)


def insert_session(title, sid=None):
    import sqlite3
    home = Path(os.environ["HERMES_HOME"])
    sid = sid or "local-" + hashlib.sha256(title.encode()).hexdigest()[:40]
    now = time.time()
    with sqlite3.connect(home / "state.db") as c, c:
        c.execute(SESSION_SCHEMA)
        c.execute(
            "insert or replace into sessions (id, title, model, input_tokens, "
            "output_tokens, cache_read_tokens, reasoning_tokens, "
            "api_call_count, tool_call_count, estimated_cost_usd, "
            "last_activity_at, last_activity_description, ended_at, "
            "started_at) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (sid, title, "fixture", 1, 1, 0, 0, 1, 1, 0.0, now, "fixture",
             now + 1, now))
    return sid


# ============================ legs ============================
def _writer_body():
    """Short temp write, rename refusal + post-rename state, same-key no-mint,
    over-cap honest no-label — all through the LIVE publisher; the abandoned
    key's bytes never reach events. Composed law: a failed publish unlinks its
    own tmp (no residue); the banked image stands byte-identical."""
    run = RUNS / "writer-faults"
    (run / "nodes").mkdir(parents=True)
    node = {"id": "review", "type": "agent", "goal": "review {item}",
            "fanout": {"items_from": "prep.items"}}
    byid = {"review": node}
    side = run / "fanout-inputs" / "review.json"
    guard = threading.Lock()
    offset = len(rows)
    old = wf.skey_for(run, byid, node, 0)
    check(list(run.iterdir()) == [run / "nodes"] and not side.exists()
          and not history(run / "events.jsonl"),
          "writer-faults: fresh run not quiet before first capture")
    value = "CJ2_ITEM_0000_" + "x" * 32
    wf.capture_fanout_input(run, guard, node, 0, old, value, 2)
    dump(run / "nodes" / "review.0.json", {"status": "done", "skey": old})
    before = side.read_bytes()
    mark = len(rows)
    wf.capture_fanout_input(run, guard, node, 0, old + "#a1", "wrong replacement", 2)
    same = layers(rows[mark:])
    check(not same["replace"]["calls"] and not same["temp-write"]["calls"]
          and not same["serialize-image"]["calls"] and side.read_bytes() == before,
          "writer-faults: same-key re-drive minted writes " + json.dumps(same))
    abandoned = wf.skey_for(run, byid, node, 0)
    check(side.read_bytes() == before and not history(run / "events.jsonl"),
          "writer-faults: key mint consumed events or rewrote the image")
    wf.capture_fanout_input(run, guard, node, 0, abandoned, "NEVER_LAUNCHED", 2)
    banked = side.read_bytes()
    check(wc.fanout_input_value(wc.fanout_inputs_read(run, "review"), 0, old)
          == (True, value),
          "writer-faults: retained value lost through the abandoned capture")
    check(read(run / "nodes" / "review.0.json")["skey"] == old
          and not history(run / "events.jsonl"),
          "writer-faults: canonical record or events moved")
    fresh_key = wf.skey_for(run, byid, node, 0)
    tmp = side.with_name(side.name + f".{os.getpid()}.tmp")
    V = {"v": ["界", chr(92), chr(34)]}
    fault[0] = True
    mark = len(rows)
    wf.capture_fanout_input(run, guard, node, 0, fresh_key, V, 2)
    failed = layers(rows[mark:])
    check(not fault[0] and side.read_bytes() == banked
          and list(side.parent.iterdir()) == [side],
          "writer-faults: rename refusal left residue "
          + json.dumps(sorted(p.name for p in side.parent.iterdir())))
    check(failed["replace"]["calls"] == failed["replace"]["failed"]
          == failed["temp-write"]["calls"] == failed["serialize-image"]["calls"] == 1
          and 0 < failed["replace"]["total"]
          == failed["temp-write"]["total"] == failed["serialize-image"]["total"],
          "writer-faults: rename-refusal accounting " + json.dumps(failed))
    mark = len(rows)
    wf.capture_fanout_input(run, guard, node, 0, fresh_key, V, 2)
    retried = layers(rows[mark:])
    check(retried["replace"]["calls"] == 1 and retried["replace"]["failed"] == 0
          and list(side.parent.iterdir()) == [side]
          and slots(read(side))["0"].get(fresh_key) == V
          and wc.fanout_input_value(wc.fanout_inputs_read(run, "review"), 0,
                                    fresh_key)[0],
          "writer-faults: post-rename re-read did not land or left residue")
    short_write[0] = True
    banked = side.read_bytes()
    new1 = wf.skey_for(run, byid, node, 0)
    mark = len(rows)
    wf.capture_fanout_input(run, guard, node, 0, new1, "SHORTFIRST", 2)
    short = layers(rows[mark:])
    check(not short_write[0] and side.read_bytes() == banked
          and list(side.parent.iterdir()) == [side],
          "writer-faults: short-write residue or flag left armed "
          + json.dumps(sorted(pp.name for pp in side.parent.iterdir())))
    check(short["replace"]["calls"] == 0
          and short["temp-write"]["calls"] == short["temp-write"]["failed"] == 1
          and 0 < short["temp-write"]["total"] == 17
          < short["serialize-image"]["total"]
          and short["serialize-image"]["calls"] == 1,
          "writer-faults: short-write accounting " + json.dumps(short))
    mark = len(rows)
    new2 = wf.skey_for(run, byid, node, 0)
    wf.capture_fanout_input(run, guard, node, 0, new2, "y" * 40000, 2)
    over = layers(rows[mark:])
    check(side.read_bytes() == banked
          and over["serialize-image"]["calls"] == 0
          and over["serialize-slot"]["total"] > 16384,
          "writer-faults: over-cap value rewrote the image (honest no-label "
          "broken) " + json.dumps(over))
    mark = len(rows)
    wf.capture_fanout_input(run, guard, node, 0, new1, "accepted replacement", 2)
    healed = layers(rows[mark:])
    check(healed["replace"]["calls"] == healed["serialize-image"]["calls"] == 1
          and healed["replace"]["failed"] == 0
          and healed["temp-write"]["total"] == healed["replace"]["total"]
          and list(side.parent.iterdir()) == [side],
          "writer-faults: a successful publish did not heal the fault tmp")
    check(slots(read(side))["0"] == {old: value, new1: "accepted replacement"},
          "writer-faults: final image wrong (retention law: only the record-"
          "anchored and dispatched keys stand) "
          + json.dumps(slots(read(side))["0"], ensure_ascii=False)[:300])
    check(fresh_key not in slots(read(side))["0"],
          "writer-faults: a never-canonicalized capture outlived its "
          "replacement era")
    mark = len(rows)
    wf.capture_fanout_input(run, guard, node, 0, new1, "ignored stand-off", 2)
    check(not layers(rows[mark:])["replace"]["calls"]
          and slots(read(side))["0"][new1] == "accepted replacement",
          "writer-faults: same-key re-drive after a lost publish did not stand")
    check(not history(run / "events.jsonl"),
          "writer-faults: carrier faults emitted events")
    for op in ("serialize-slot", "serialize-image", "temp-write", "replace"):
        assert sum(1 for r in rows if r["op"] == op and not r["ok"]) <= 2, op
    bank("writer-faults", dict(old=old, abandoned=abandoned, fresh=fresh_key,
                               same_key=same, injected_rename=failed,
                               short_write=short, operations=rows[offset:]))
    okline("writer-faults")


def leg_writer_faults():
    instrumented(_writer_body)


def _spawn_stubs():
    d = ROOT / "stubs"
    d.mkdir(exist_ok=True)
    (d / "spawn_stub.py").write_text(
        '"""Offline CJ2 transport: #a0 malformed, #a1 valid; banks launch input."""\n'
        "import json, os, sys\nfrom pathlib import Path\n"
        "argv = sys.argv[1:]\n"
        "title = argv[argv.index('--continue') + 1]\n"
        "pp = Path(argv[argv.index('--query-file') + 1])\n"
        "record = dict(pid=os.getpid(), argv=argv, title=title,\n"
        "              goal=next(line for line in pp.read_text().splitlines()\n"
        "                        if line.startswith('review CJ2_ITEM_')))\n"
        "run = Path(os.environ['HERMES_WF_RUN_DIR'])\n"
        "(run / ('transport-' + title.rsplit(':', 2)[-2] + '-' + title.rsplit('#', 1)[1] + '.json')).write_text(json.dumps(record))\n"
        "print('invalid answer for correction' if title.endswith('#a0')\n"
        "      else '```json\\n{\\\"result\\\":\\\"corrected\\\"}\\n```', flush=True)\n")
    (d / "spawn_stub.sh").write_text(
        '#!/bin/sh\nexec "$HERMES_WF_PYTHON" "$(dirname "$0")/spawn_stub.py" "$@"\n')
    (d / "spawn_stub.sh").chmod(0o755)
    (d / "parked_child.py").write_text(
        '"""Offline child that exits once the adoption observer acknowledges it."""\n'
        "import sys, time\nfrom pathlib import Path\n"
        "ready, release = map(Path, sys.argv[1:3])\n"
        "ready.touch()\nwall = time.monotonic() + 9\n"
        "while not release.exists():\n"
        "    if time.monotonic() >= wall:\n        raise SystemExit('adoption barrier expired')\n"
        "    time.sleep(.01)\n"
        "print('```json\\n{\\\"result\\\":\\\"adopted harvest\\\"}\\n```', flush=True)\n")
    return d


def leg_spawned_correction():
    phase = "spawned-correction"
    run = RUNS / phase
    (run / "nodes").mkdir(parents=True)
    item = "CJ2_ITEM_0000_" + "x" * 32
    prep = {"id": "prep", "type": "echo", "output": {"items": [item]}}
    node = {"id": "review", "type": "agent", "goal": "review {item}",
            "after": ["prep"], "timeout": 12,
            "schema": {"type": "object", "required": ["result"],
                       "properties": {"result": {"type": "string", "enum": ["corrected"]}}},
            "fanout": {"items_from": "prep.items", "goal": "review {item}"}}
    byid = {n["id"]: n for n in (prep, node)}
    stub = (_spawn_stubs() / "spawn_stub.sh").resolve()
    dump(run / "graph.json", {"name": phase, "nodes": [prep, node]})
    dump(run / "run.json", {"name": phase, "item_concurrency": 1,
                            "hermes_bin": str(stub)})
    abandoned = wf.skey_for(run, byid, node, 7)
    wf.capture_fanout_input(run, threading.Lock(), node, 7, abandoned,
                            "NEVER_LAUNCHED", 8)
    check(not history(run / "events.jsonl")
          and not history(run / "spawn-ledger.jsonl")
          and list((run / "nodes").iterdir()) == [],
          phase + ": preplan-drop fixture not quiet")
    side = run / "fanout-inputs" / "review.json"
    check(slots(read(side)) == {"7": {abandoned: "NEVER_LAUNCHED"}},
          phase + ": preplan image wrong before the wave")
    offset = len(rows)
    original_popen = subprocess.Popen
    inspected = []

    def popen(args, *a, **kw):
        if isinstance(args, list) and args[0] == str(stub):
            title = args[args.index("--continue") + 1]
            base, attempt = title.rsplit("#a", 1)
            image = slots(read(side))
            check(image == {"0": {base: item}},
                  phase + f": first-launch image at #{attempt} {json.dumps(image)}")
            starts = [e["skey"] for e in history(run / "events.jsonl")
                      if e["event"] == "item.started"]
            check(starts == [base],
                  phase + f": item.started set at #{attempt} {json.dumps(starts)}")
            child = original_popen(args, *a, **kw)
            inspected.append(dict(title=title, pid=child.pid,
                                  attempt=int(attempt), published=image))
            return child
        return original_popen(args, *a, **kw)

    with patch.object(subprocess, "Popen", popen), \
            patch.object(wf, "notify", lambda *a, **kw: None):
        wf.main(run.name)
        wf._release_terminal_lock(run)
    m = layers(rows[offset:])
    all_ledger = history(run / "spawn-ledger.jsonl")
    journal = history(run / "events.jsonl")
    canonical = read(run / "nodes" / "review.0.json")
    aggregate = read(run / "nodes" / "review.json")
    observed = [read(run / f"transport-0-a{i}.json") for i in range(2)]
    bank(phase, dict(canonical=canonical, aggregate=aggregate, os_children=observed,
                     at_popen=inspected, ledger=all_ledger, journal=journal,
                     layers=m, abandoned=abandoned))
    check([x["attempt"] for x in inspected] == [0, 1], phase + ": attempt order")
    check([(x["pid"], x["title"]) for x in observed]
          == [(x["pid"], x["title"]) for x in inspected],
          phase + ": observed children differ from spied Popen")
    base = canonical["skey"]
    check([x["title"] for x in observed] == [base + "#a0", base + "#a1"],
          phase + ": correction titles " + json.dumps([x["title"] for x in observed]))
    check([x["goal"] for x in observed] == ["review " + item] * 2,
          phase + ": correction goals drifted")
    for role in ("child", "child_end"):
        check([(x["pid"], x["skey"]) for x in all_ledger if x["role"] == role]
              == [(x["pid"], base) for x in inspected],
              phase + f": ledger {role} rows")
    check([e["skey"] for e in journal if e["event"] == "item.finished"] == [base],
          phase + ": finished skeys")
    check(canonical["status"] == "done" and canonical["attempts"] == 2
          and "item" not in canonical, phase + ": canonical record shape")
    result, = aggregate["output"]["all_results"]
    check(result["skey"] == base and result["item"] == item
          and result["output"] == {"result": "corrected"},
          phase + ": aggregate row " + json.dumps(result))
    for op in ("serialize-slot", "serialize-image", "temp-write", "replace"):
        check(m[op]["calls"] == 1, phase + f": {op} calls {m[op]['calls']}")
    okline(phase)


def _adoption_lap(mode):
    run = RUNS / ("adoption-" + mode)
    (run / "nodes").mkdir(parents=True)
    current, original = "Quartz", "Amber"
    prep = {"type": "echo", "id": "prep", "output": {"items": [current]}}
    node = {"type": "agent", "id": "review", "goal": "review {item}",
            "after": ["prep"], "timeout": 18,
            "fanout": {"items_from": "prep.items", "goal": "review {item}"}}
    byid = {"prep": prep, "review": node}
    dump(run / "graph.json", {"name": run.name, "nodes": [prep, node]})
    dump(run / "run.json", {"name": run.name, "item_concurrency": 1})
    key = wf.skey_for(run, byid, node, 0)
    if mode != "absent":
        wf.capture_fanout_input(run, threading.Lock(), node, 0, key, original, 1)
    ready, release = run / "ready", run / "release"
    lp = run / "orphan.log"
    spawn_cmd = [sys.executable, "-B", str(_spawn_stubs() / "parked_child.py"),
                 str(ready), str(release), key + "#a0"]
    started = wf.now()
    with lp.open("w") as f:
        proc = subprocess.Popen(spawn_cmd, stdin=subprocess.DEVNULL,
                                stdout=f, stderr=f, start_new_session=True)
    observed, calls, memo, captured = [], [], [], {}
    original_run, original_active = subprocess.run, wf.active_child
    original_adopt, original_park = wf._adopt_child, wf._ratelimit_park

    def ps_observer(args, *a, **kw):
        cp = original_run(args, *a, **kw)
        if (isinstance(args, list) and args[:3] == ["ps", "-ww", "-p"]
                and str(proc.pid) in args):
            observed.append(cp.stdout)
        return cp

    def active(r, n, b, i=None):
        if mode == "memo" and captured.get("replay"):
            check(original_active(r, n, b, i) is None, "memo: real replay not None")
            return captured["verified"]
        verified = original_active(r, n, b, i)
        if verified and n["id"] == "review" and i == 0:
            captured["verified"] = verified
        return verified

    def adopt(meta, n, b, i, child, schema, **kw):
        check(proc.poll() is None and child["skey"] == key + "#a0",
              mode + ": adopt seam child identity")
        result = original_adopt(meta, n, b, i, child, schema, **kw)
        memo.append(meta["_adopt_result"][f"review:0:{proc.pid}"])
        return result

    def park(meta, result, respawn, ev, ev_kw, *a, **kw):
        if mode == "memo" and ev == "item" and result.get("adopted"):
            captured["replay"] = True
            again = respawn()
            check(again == result, "memo: replay differs from first harvest")
            captured["memo_reused"] = True
        return original_park(meta, result, respawn, ev, ev_kw, *a, **kw)

    def fresh(meta, n, b, goal, context, schema, *, skey, index=None, **kw):
        calls.append((skey, goal))
        return {"skey": skey, "spawn": 0, "attempts": 1, "ms": 1,
                "status": "done", "output": {"result": "fresh"}}

    mark = len(rows)
    thread = None
    try:
        until = time.monotonic() + 4
        while not ready.exists():
            if proc.poll() is not None or time.monotonic() >= until:
                break
            time.sleep(.01)

        def release_on_event():
            until2 = time.monotonic() + 9
            while time.monotonic() < until2:
                p = run / "events.jsonl"
                if p.exists() and ('"event": "item.adopted"' in p.read_text()
                                   or (mode == "impostor" and calls)):
                    break
                time.sleep(.01)
            release.touch()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass

        stem = run / "nodes" / "review.0.json"
        claimed = key if mode != "impostor" else key[:-1] + (
            "0" if key[-1] != "0" else "1")
        dump(stem, dict(status="running", pid=proc.pid, skey=claimed, attempt=0,
                        efp=wf.efp(byid, node),
                        fp_rule_version=wf.wfcommon.FP_RULE_VERSION,
                        started=started, log_path=str(lp), spawn_cmd=spawn_cmd))
        thread = threading.Thread(target=release_on_event, daemon=True)
        thread.start()
        with (patch.object(subprocess, "run", ps_observer),
              patch.object(wf, "active_child", active),
              patch.object(wf, "_adopt_child", adopt),
              patch.object(wf, "_ratelimit_park", park),
              patch.object(wf, "run_child", fresh),
              patch.object(wf, "notify", lambda *a, **kw: None)):
            wf.main(run.name)
    finally:
        release.touch()
        if thread is not None:
            thread.join(12)
        if proc.poll() is None:
            proc.kill()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            pass
        wf._release_terminal_lock(run)
    result, = read(run / "nodes" / "review.json")["output"]["all_results"]
    journal = history(run / "events.jsonl")
    events = {ev: [r for r in journal if r["event"] == ev]
              for ev in ("item.started", "item.adopted", "item.finished")}
    m = layers(rows[mark:])
    image = slots(read(run / "fanout-inputs" / "review.json"))["0"] \
        if (run / "fanout-inputs" / "review.json").exists() else {}
    bank("adoption-" + mode, dict(events=events, calls=calls, harvest_memos=memo,
                                  pid=proc.pid, exit=proc.returncode,
                                  observed_ps=observed, claimed=claimed,
                                  result=result, capture=captured, layers=m,
                                  image=image))
    check(proc.returncode == 0 and observed and key + "#a0" in observed[0],
          mode + ": real ps proof of the owned child missing")
    if mode == "impostor":
        check(not memo and not events["item.adopted"]
              and len(events["item.started"]) == len(calls) == 1,
              mode + ": impostor fresh-spawn shape " + json.dumps(
                  {k: len(v) for k, v in events.items()}))
        check(result["item"] == current
              and result["skey"] == calls[0][0] not in (key, claimed)
              if False else result["item"] == current and calls
              and calls[0][0] not in (key, claimed),
              mode + ": impostor dispatch key " + json.dumps(calls[:1]))
    else:
        check(not calls and not events["item.started"]
              and len(memo) == len(events["item.adopted"]) == 1,
              mode + ": adopted lap re-spawned " + json.dumps(
                  {k: len(v) for k, v in events.items()}))
        check(events["item.adopted"][0]["skey"] == key + "#a0"
              and result["skey"] == key
              and events["item.finished"][0]["skey"] == key
              and events["item.adopted"][0]["pid"] == proc.pid,
              mode + ": adopted identity chain")
        if mode != "absent":
            check(result.get("item") == original,
                  mode + ": adopted row lost the retained capture")
        else:
            check("item" not in result,
                  mode + ": absent-capture adoption fabricated a label")
        check(m["serialize-image"]["calls"] == 0 and m["replace"]["calls"] == 0,
              mode + ": adoption minted carrier bytes " + json.dumps(m))
        check(bool(captured.get("memo_reused")) == (mode == "memo"),
              mode + ": memo replay flag")
    okline("adoption/" + mode)


def leg_adoption():
    for mode in ("retained", "absent", "memo", "impostor"):
        _adoption_lap(mode)


def _eras(form):
    name = f"eras-{form}-4"
    run, ref = make_run(name, None, form, width=4)
    carrier = run / "fanout-inputs" / "review.json"
    measured, known = {}, set()
    original_log, original_key = wf.log, wf.skey_for

    def log(r, event, **kw):
        if Path(r) == run and kw.get("node") == "review" \
                and event in ("item.started", "item.finished"):
            record(event, index=kw["index"], key=kw["skey"])
        return original_log(r, event, **kw)

    sizes = [4, 4, 0, 2]
    labels = None
    for gen, size in enumerate(sizes):
        tick()
        phase = f"{name}/{gen}"
        offset = len(rows)
        labels = [f"CJ2_ITEM_{i:04d}_" + chr(97 + gen) * 32 for i in range(size)] \
            if size else labels_for(sizes, gen)
        if gen % 2:
            labels = list(reversed(labels))
        if gen:
            with patch.object(door, "_respawn_runner", lambda _: None):
                response = door.act_amend({"run_id": name,
                                           "patch": {"nodes": {"prep": {"goal": f"era {gen}"}}}})
            if not (response.get("ok") and {"prep", "review"} <= set(response.get("will_rerun", ()))):
                failures.append(phase + f": amend refused {response}")
                print("FAIL", phase, "amend refused", json.dumps(response), flush=True)
        old = {p.stem.rsplit(".", 1)[1]: read(p)["skey"]
               for p in (run / "nodes").glob("review.*.json") if p.stem.count(".") == 1}

        def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
            if node["id"] == "prep":
                output = {"items": labels} if form == "dict" else [labels]
            elif node["id"] == "empty":
                output = {"empty": True}
            else:
                check(node["id"] == "review" and goal == "review " + labels[index],
                      phase + ": fan-out goal drifted off the label")
                output = {"result": "child output (no copied item)"}
                record("transport", index=index, key=skey, goal=goal)
            return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                        output=output)

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
            except SystemExit as exc:
                failures.append(phase + f": runner exited early ({exc.code})")
                print("FAIL", phase, "runner exited early", exc.code, flush=True)
            finally:
                wf._release_terminal_lock(run)
        wedge = rows[offset:]
        m = layers(wedge)
        if size:
            for op in ("serialize-image", "temp-write", "replace"):
                check(m[op]["calls"] == 1,
                      phase + f": {op} {m[op]['calls']} for one whole-image write")
            check(m["replace"]["failed"] == 0
                  and m["replace"]["peak"] <= wc.FANOUT_INPUTS_MAX_DOC
                  if hasattr(wc, "FANOUT_INPUTS_MAX_DOC") else True,
                  phase + ": replace failed or the image exceeded the cap")
        else:
            # this pin: a zero-item expansion publishes the SHRINK retention
            # pass (<=1 replace) and the wave falls back empty — the exact
            # status is banked, not assumed.
            check(m["replace"]["calls"] <= 1
                  and m["replace"]["calls"] == m["temp-write"]["calls"],
                  phase + f": empty wave wrote {m['replace']['calls']} times")
            empty_status = str(agg_status := None) or None
        ready_ev, state, counts, images = {}, {}, [], []
        for row in wedge:
            op = row["op"]
            if op == "replace" and row["ok"]:
                images.append(row["image"])
                state = slots(row["image"])
                base = {k for pairs in state.values() for k in pairs}
                check(max(map(len, state.values()), default=0) <= 2,
                      phase + f": entry holds {max(map(len, state.values()))} keys")
                counts.append(len(base))
            if op in ("prepare-key", "transport"):
                ready_ev.setdefault(row["index"], []).append((op, row["key"]))
            elif row.get("op") == "item.started" or row.get("op") == "item.finished":
                pass
        # per-index chain from the recorded ops
        starts = [r for r in wedge if r["op"] == "item.started"]
        finishes = [r for r in wedge if r["op"] == "item.finished"]
        agg = read(run / "nodes" / "review.json")
        if size:
            check(agg["status"] == "done", phase + ": aggregate status")
            for i, result in enumerate(agg["output"]["all_results"]):
                k = result["skey"]
                rec = read(run / f"nodes/review.{i}.json")
                check(rec["skey"] == k, phase + f"/{i}: record skey differs"
                      " from the published claim")
                check(result["item"] == labels[i] and "item" not in rec,
                      phase + f"/{i}: item label")
                if k in known:
                    redpin(f"reuse-gen-{i}", phase + f": key reused {k}")
                known.add(k)
                check(any(sk == k for sk in state.get(str(i), {})),
                      phase + f"/{i}: current key absent from the published image")
        else:
            check(agg["status"] in ("skipped", "done")
                  and (agg["status"] != "skipped"
                       or agg.get("caught_error_class") == "fanout_empty"),
                  phase + ": empty-wave fallback " + str(agg.get("status")))
            bank(phase + "-empty-fallback",
                 dict(status=agg.get("status"),
                      caught=agg.get("caught_error_class"),
                      replace_calls=m["replace"]["calls"]))
        final = slots(read(carrier)) if carrier.exists() else {"x": {}}
        keys = {x for pairs in final.values() for x in pairs}
        anchored = {read(p)["skey"] for p in (run / "nodes").glob("review.*.json")
                    if p.stem.count(".") == 1}
        # on this pin an abandoned pre-plan key legitimately stands until a
        # later replacement prunes it (a lost preplan costs a label, never a
        # spawn); anything ELSE unanchored is a leak.
        # this pin's retention law: a key stands while its INDEX holds a
        # canonical record; a superseded slot at a live index is adjacency,
        # not a leak. A key whose index has NO record is the leak class.
        live_indexes = {p.stem.split(".")[-1]
                        for p in (run / "nodes").glob("review.*.json")
                        if p.stem.count(".") == 1}
        orphaned = sorted(k for idx, pairs in final.items()
                          if idx not in live_indexes for k in pairs)
        check(not orphaned,
              phase + f": {len(orphaned)} keys anchored to no record after "
              f"settle (peak {max(counts, default=len(keys))}, final "
              f"{len(keys)}): {orphaned}")
        # measured law on this pin: retention is PER ENTRY — an entry stands
        # while its index artifact exists, holding at most two keys (the
        # record's own plus the wave in flight). A superseded key therefore
        # outlives its era on disk until the artifact goes; the reader's
        # adjudication always prefers the record-named slot, so a stale slot
        # can never paint a live row. The carrier total is bounded by
        # 2 x live indexes + this wave's width — never by history depth.
        superseded = sorted(keys - anchored)
        check(max(counts, default=len(keys))
              <= 2 * len(live_indexes) + size,
              phase + f": peak keys {max(counts, default=len(keys))} > "
              f"2 x live + width {2 * len(live_indexes) + size}")
        check(all(len(pairs) <= 2 for pairs in final.values()),
              phase + ": an entry outgrew the two-key bound")
        okline(phase + f": retention measured (final {len(keys)} keys, "
               f"{len(superseded)} superseded-but-retained slots, live "
               f"indexes {sorted(live_indexes)}, entry bound 2)")
        assert sorted(carrier.parent.iterdir()) == [carrier]
        measured[str(gen)] = dict(width=size, keys=sorted(keys), obsolete=orphaned,
                                  peak_keys=max(counts, default=len(keys)),
                                  images=images, layers=m)
    bank("eras-" + form, measured)


def labels_for(sizes, gen):
    # the prep roster for this generation: exactly sizes[gen] labels; a
    # zero-width generation ships the EMPTY list (zero-item expansion).
    size = sizes[gen] if isinstance(sizes[gen], int) else len(sizes[gen])
    return [f"CJ2_ITEM_{i:04d}_" + chr(97 + gen) * 32 for i in range(size)]


def _static_boundary():
    """A static def writes ZERO carrier bytes on this pin (batch is dynamic
    only): one node, inline `items`, no prep parent."""
    name = "eras-static-boundary"
    run = RUNS / name
    (run / "nodes").mkdir(parents=True)
    dump(run / "run.json", {"name": name, "item_concurrency": 4})
    graph = {"name": name, "nodes": [
        {"id": "review", "type": "agent", "goal": "review {item}",
         "fanout": {"items": ["CJ2_ITEM_0000_s", "CJ2_ITEM_0001_s"]}}]}
    dump(run / "graph.json", graph)
    offset = len(rows)
    with patch.object(wf, "notify", lambda *a, **kw: None):
        wf.main(name)
        wf._release_terminal_lock(run)
    m = layers(rows[offset:])
    check(all(m[op]["calls"] == 0 for op in m),
          "static boundary: carrier work not zero: " + json.dumps(m))
    check(not (run / "fanout-inputs").exists(),
          "static boundary: fanout-inputs/ appeared")
    okline("static boundary")


def leg_eras_dict():
    instrumented(_eras, "dict")
    instrumented(_static_boundary)


def leg_eras_list():
    instrumented(_eras, "list")


def leg_orders():
    """Publication ordering at the shipped reader, both orders. Views are
    taken while the wave is LIVE (inside a child, before its own RUNNING
    record lands): that is the only window where record-vs-carrier ordering
    is observable, and it proves batch-first publication — the chat rides
    the canonical record, the label rides the carrier, neither fabricates
    the other. The terminal honest absence is measured by restoring the
    prior-era carrier bytes under the new records at the reader seam, and
    the Boolean-version carrier (the historical gap) by corrupting the file
    on disk — banked whichever way this pin reads."""
    for form in ("dict", "list"):
        _orders_form(form)


_api_spec = importlib.util.spec_from_file_location(
    "cj2rec_api", REPO / "dashboard" / "plugin_api.py")
API = importlib.util.module_from_spec(_api_spec)
_api_spec.loader.exec_module(API)


def view_rows(run):
    v = API._view(run, full=True)
    node = (v.get("nodes") or v.get("metrics", {}).get("live", {})
            .get("nodes", {})).get("review") or {}
    return {int(k): dict(x) for k, x in (node.get("item_metrics") or {}).items()}


def _orders_form(form):
    name = f"orders-{form}"
    labels = ["Amber", "Basalt"]
    run, ref = make_run(name, labels, form, width=2,
                        node_extra={"timeout": 20})
    graph = read(run / "graph.json")
    graph["nodes"] = [n for n in graph["nodes"] if n["id"] != "empty"]
    graph["nodes"][1].pop("on_fail", None)
    dump(run / "graph.json", graph)
    seed_db()
    seen, gen1_bytes = {}, None

    calls = []

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node["id"] == "review":
            calls.append({"index": index, "kw": {k: str(v)[:24]
                                                for k, v in kw.items()},
                          "skey": skey})
            bank("child-calls", calls)
        if node["id"] == "prep":
            return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                        output=prep_output(labels, form))
        title = skey + "#a0"
        insert_session(title)
        if index == 0:
            seen[f"mid-{labels[0]}"] = view_rows(run)
        return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                    output={"result": "ok"})

    for gen in (1, 2, 3):
        tick()
        if gen > 1:
            labels[:] = (["Cinder", "Dune"] if gen == 2
                         else ["Echo", "Flint"])
            with patch.object(door, "_respawn_runner", lambda _: None):
                response = door.act_amend(
                    {"run_id": name,
                     "patch": {"nodes": {"prep": {"goal": f"era {gen}"}}}})
            if not response.get("ok"):
                print("FAIL", form, "amend refused", json.dumps(response),
                      flush=True)
                failures.append(f"{form}: amend gen {gen} refused")
        with patch.object(wf, "run_child", child), \
                patch.object(wf, "notify", lambda *a, **kw: None):
            wf.main(name)
            wf._release_terminal_lock(run)
        rows = view_rows(run)
        for i, lbl in enumerate(labels):
            own = f"{read(run / 'nodes' / f'review.{i}.json')['skey']}#a0"
            check(rows[i].get("item") == lbl,
                  f"{form} gen{gen}: settled row {i} label "
                  f"{rows[i].get('item')!r} != {lbl!r} — the carrier must "
                  "paint the roster label on its own era's record")
            check(rows[i].get("session_current") == session_id_for(own),
                  f"{form} gen{gen}: settled row {i} chat "
                  f"{rows[i].get('session_current')!r} != "
                  f"{session_id_for(own)}")
            sid, _exp = wc._exact_title_lookup(run, "review", i, own)
            check(sid == session_id_for(own),
                  f"{form} gen{gen}: row {i} exact-title lookup misses the "
                  f"seeded session ({sid!r})")
            rec = read(run / "nodes" / f"review.{i}.json")
            check("item" not in rec,
                  f"{form} gen{gen}: canonical record {i} grew an item label "
                  "column (seams stay separated)")
        okline(f"{form} gen{gen}: settled join — label from the carrier, chat "
               "from the record, pair adjudicated at the reader")
        if gen == 1:
            gen1_bytes = (run / "fanout-inputs" / "review.json").read_bytes()
    # carrier-then-record restored adjacency, pure artifact state: prior-era
    # carrier bytes under the current records (a crash between an era's
    # pre-plan publish and its dispatch, or a partial restore).
    side = run / "fanout-inputs" / "review.json"
    good = side.read_bytes()
    side.write_bytes(gen1_bytes)
    stale = view_rows(run)
    for i, lbl in enumerate(["Echo", "Flint"]):
        own = f"{read(run / 'nodes' / f'review.{i}.json')['skey']}#a0"
        check(stale[i].get("item") not in ("Amber", "Basalt", "Cinder", "Dune"),
              f"{form}: restored prior-era carrier painted a stale label "
              f"{stale[i].get('item')!r} on row {i}")
        check(stale[i].get("item") in (None, "", f"#{i}", lbl),
              f"{form}: restored-carrier row {i} label "
              f"{stale[i].get('item')!r} is not the record's own era's")
        check(stale[i].get("session_current") == session_id_for(own),
              f"{form}: restored-carrier row {i} left the record's own chat")
    okline(f"{form}: restored adjacency fails closed — identity survives on "
           "the record alone")
    # the historical gap: a carrier whose version is a Boolean.
    corrupt = json.loads(good)
    corrupt["version"] = True
    side.write_bytes(json.dumps(corrupt).encode())
    fa = wc.fanout_inputs_read(run, "review")
    rowsB = view_rows(run)
    if fa:
        redpin("boolean-version-labels",
               f"{form}: Boolean-version carrier still READS as a capture "
               f"({json.dumps(fa, default=str)[:120]})")
    else:
        okline(f"{form}: Boolean-version carrier fails closed at the reader "
               "seam (fanout_inputs_read -> falsy)")
    for i, lbl in enumerate(["Echo", "Flint"]):
        own = f"{read(run / 'nodes' / f'review.{i}.json')['skey']}#a0"
        check(rowsB[i].get("item") in (None, "", f"#{i}", lbl),
              f"{form}: Boolean-version carrier row {i} label "
              f"{rowsB[i].get('item')!r} is neither absent nor the record's"
              " own era's claim")
        check(rowsB[i].get("session_current") == session_id_for(own),
              f"{form}: Boolean-version carrier orphaned row {i}'s chat")
    side.write_bytes(good)
    bank(f"orders-{form}", dict(mid=seen, final=rowsB,
                                restored=stale))
    okline(f"orders-{form}")



def leg_controls():
    """Reader controls at the shipped join. (1) UNNAMED HISTORICAL LABELS:
    the pre-bounditem era shipped slots with no item label (and skeys with no
    #a claim suffix); the reader must show the label as absent — never
    re-derive it from the roster — and must not fabricate a chat for an
    unboundable era. (2) PARTIAL SIBLING ISOLATION: a sibling that comes back
    `partial` (no harvest) must not contaminate its done sibling's pair, and
    the partial row itself keeps the carrier label while its chat stays
    honestly absent. Both run through the same _view as the orders leg."""
    for form in ("dict", "list"):
        _controls_form(form)


def _controls_form(form):
    name = f"controls-{form}"
    labels = ["Amber", "Basalt"]
    # a 1-token RunBudget cap on the fan-out node with SERIAL dispatch: the
    # first sibling runs and meters spend, the second is refused BEFORE
    # submit — the pin's graceful-partial form (budget_ledger.json names
    # what never launched, wf.py:_budget_refusal/282). Serial dispatch is
    # what makes the refusal grounded in MEASURED spend, not a first-attempt
    # tax; both carrier slots still publish up front either way.
    run, ref = make_run(name, labels, form, width=1,
                        node_extra={"timeout": 20, "budget": {"tokens": 1}})
    graph = read(run / "graph.json")
    graph["nodes"] = [n for n in graph["nodes"] if n["id"] != "empty"]
    graph["nodes"][1].pop("on_fail", None)
    dump(run / "graph.json", graph)
    seed_db()
    landed = threading.Event()

    def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
        if node["id"] == "prep":
            return dict(skey=skey, spawn=0, attempts=1,
                        ms={"input_tokens": 1, "output_tokens": 1},
                        status="done", output=prep_output(labels, form))
        if index == 1:
            # the refusal must be grounded in MEASURED spend (the gate's own
            # law), so sibling 1 checks the gate only after sibling 0's
            # metered session row has landed: a real wave serialises the
            # same way once the seats are full.
            landed.wait(10)
            br = wf._budget_refusal(meta, node, byid, index, 0)
            bank("gate-dump", {"has_run": "_run" in meta,
                               "node_budget": node.get("budget"),
                               "br": json.dumps(br, default=str)[:200]})
            if br is not None:      # real pre-dispatch gate at the real seam
                return br
        insert_session(skey + "#a0")         # only a LAUNCHED sibling binds one
        landed.set()
        return dict(skey=skey, spawn=0, attempts=1,
                    ms={"input_tokens": 5000, "output_tokens": 5000},
                    status="done", output={"result": "ok"})

    with patch.object(wf, "run_child", child), \
         patch.object(wf, "notify", lambda *a, **kw: None):
        wf.main(name)
        wf._release_terminal_lock(run)
    agg = read(run / "nodes" / "review.json")
    rec1 = read(run / "nodes" / "review.1.json")
    check("budget_exhausted" in json.dumps(agg)
          or "budget_exhausted" in json.dumps(rec1),
          f"{form}: budget-capped wave shows no budget_exhausted form "
          f"(aggregate {agg.get('status')} / "
          f"{agg.get('caught_error_class')}, rec1 {rec1.get('status')})")
    rows = view_rows(run)
    check(rows[0].get("item") == "Amber",
          f"{form}: done sibling lost its label under a capped sibling "
          f"({rows[0].get('item')!r})")
    check(rows[0].get("session_current") == session_id_for(
              read(run / "nodes" / "review.0.json")["skey"] + "#a0"),
          f"{form}: done sibling lost its chat under a capped sibling")
    # measured on this pin: a carrier slot's label binds when THAT child
    # launches (self-publish), so a refused sibling legitimately shows an
    # unlabelled slot — the isolation law is: the slot exists with its own
    # fresh skey, carries NO mis-assigned label, and the reader fabricates
    # neither a chat nor the done sibling's label onto it.
    shipped = wc.fanout_inputs_read(run, "review") or {}
    slot1 = (shipped.get("items") or {}).get("1") or {}
    cur1 = slot1.get("current") or {}
    if cur1:
        check(cur1.get("item") in (None, ""),
              f"{form}: refused sibling wearing another lane's label "
              f"({cur1.get('item')!r})")
    else:
        okline(f"{form}: refused sibling's slot pruned by settle (no "
               "phantom kept, no foreign label) — banked, not asserted")
    row1 = rows.get(1) or {}
    check(not row1.get("session_current"),
          f"{form}: never-launched sibling fabricated a chat "
          f"({row1.get('session_current')!r})")
    check(not row1.get("item") or row1.get("item") == "Basalt",
          f"{form}: refused lane shows a foreign label ({row1!r})")
    if (run / "budget_ledger.json").exists():
        led = read(run / "budget_ledger.json")
        bank(f"ledger-{form}", led)
        if "review:1" in json.dumps(led) or "1" in json.dumps(led):
            okline(f"{form}: budget_ledger.json names the never-launched "
                   "lane")
        else:
            okline(f"{form}: ledger banked (lane not named by skey: "
                   f"{json.dumps(led)[:120]})")
    else:
        okline(f"{form}: no ledger written (the refusal committed as a "
               "failed child, not a graceful-partial finalize) — banked")
    # ---- unnamed historical labels: the pre-bounditem era shipped claim
    # rows with a title but NO item, and carrier slots without labels. Strip
    # both, keep every key — the reader must then show the label as ABSENT,
    # never re-derived from the live roster, and keep the bound chat.
    agg2 = read(run / "nodes" / "review.json")
    for row in (agg2.get("output") or {}).get("all_results") or []:
        if isinstance(row, dict):
            row.pop("item", None)
    dump(run / "nodes" / "review.json", agg2)
    carrier = run / "fanout-inputs" / "review.json"
    img = read(carrier)
    for entry in img["items"].values():
        for slot in entry.values():
            if isinstance(slot, dict):
                slot["item"] = None
    dump(carrier, img)
    rows2 = view_rows(run)
    check(rows2[0].get("item") in (None, ""),
          f"{form}: reader re-derived a roster label for a nameless slot "
          f"({rows2[0].get('item')!r})")
    check(rows2[0].get("session_current") == session_id_for(
              read(run / "nodes" / "review.0.json")["skey"] + "#a0"),
          f"{form}: nameless slot orphaned the bound chat")
    bank(f"controls-{form}", dict(agg=agg, rows=rows, nameless=rows2))
    okline(f"{form}: controls (unnamed historical labels, partial isolation)")


def main():
    {"writer-faults": leg_writer_faults,
     "spawned-correction": (lambda: instrumented(leg_spawned_correction)),
     "adoption": (lambda: instrumented(leg_adoption)),
     "eras-dict": leg_eras_dict,
     "eras-list": leg_eras_list,
     "orders-dict": (lambda: leg_orders()),
     "orders-list": (lambda: leg_orders()),
     "controls": leg_controls}[LEG]()
    finish()


if __name__ == "__main__":
    main()
