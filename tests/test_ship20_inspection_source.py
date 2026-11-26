#!/usr/bin/env python3
"""bd_2026-11-13-s20-jtf-source: node inspection sources and bounds (Ship 2.0).

Behavior-level proof of the SOURCE side of Node inspection — the ONE existing
16 KiB backend log/prompt tail and the read-model clocks the panel consumes.
This file adds no new surface: it exercises `dashboard/plugin_api.py`'s route
core `_node_log_tail` + its registered route, and `wfcommon.node_facts` /
`run_state` through `_view(full=True)`, against a hand-seeded run dir written
the way wf.py commits it (same shape tests/test_node_facts.py establishes).

What is proven (the bead's acceptance words, each named in a check below):
  1. EXISTING 16KiB TAIL ONLY — one registered tail route, LOG_TAIL == 16384
     caps the served bytes; over-cap and zero/negative tails are REFUSED,
     never clamped into a surprise.
  2. ID-ONLY REQUEST — the endpoint's whole input surface is
     {run_id, nid, index, attempt, kind, tail}: no path parameter exists; the
     file path comes only from the record and stays contained to <run>/logs.
  3. REFUSE OUT-OF-ATTEMPT/INDEX — an attempt (or item index) the node never
     had answers 404, not an empty 200: the sibling `.a<n>` file's own presence
     is the evidence an attempt ran.
  4. ABSENT SENTINELS NOT ZEROS — no log = 404; an empty log is a REAL zero
     (200, size 0); an absent fact reads "unknown"; a node that never spawned
     carries NO metrics key; an api-call count with unknown rows OMITS
     api_calls instead of summing a partial to a zero-shaped truth.
  5. SEPARATE RUN/ITEM CLOCKS — the run clock (run.json started + events
     mtime) and each item's clock (its own record started, its own DB rows)
     are sourced independently: verbatim per record, never borrowed across
     levels, and closed items report last_activity=None, not the run's clock.
  6. SEED TRUE ZERO-SPAWN AND REFUSAL — a precondition-failed node with no
     spawn evidence at all, and the spent-cap refusal record
     (wf.py _window_spent_record's verbatim shape, as
     tests/fixtures/refusal_capture.py pins it), both ride the read model
     honestly: facts verbatim, no metrics key, tail 404.

CJ2 record bindings are NOT changed: FACT_KEYS / node_facts / the record keys
consumed by the composed renderer are asserted verbatim (the `refusal`,
`error_class`, `attempts_log` and superseded-aggregate rows below are exactly
the binding CJ2 renders; this lane only proves the source feeds them).

Stdlib + fastapi (for HTTPException), same as tests/test_node_facts.py.
Run: python3 tests/ship20-inspection-source.py   (exit 0 = green)
"""
import importlib.util, inspect, json, os, shutil, sqlite3, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HOME = Path(tempfile.mkdtemp(prefix="home-insp-src-", dir=str(ROOT)))
os.environ["HERMES_HOME"] = str(HOME)

def _load_pin():
    # est-2ek.1.762: the shared launch-env pin helper, exec-loaded by path
    # (repo convention for tests/fixtures modules).
    spec = importlib.util.spec_from_file_location(
        "wf_spawn_isolation_762", Path(__file__).parent / "fixtures" / "wf_spawn_isolation_762.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

pin_env = _load_pin().pin_env
# A hostile lane env (this very workflow exports WF_RUNS_ROOT) must not steer
# the resolvers: pin_env REPLACES the run root and strips API_SERVER_*.
os.environ.update(pin_env(dict(os.environ), HOME / "workflows", home=HOME))

import wfcommon

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

api = load("insp_src_dashboard", ROOT / "dashboard" / "plugin_api.py")
assert api.router is not None, "fastapi is required to prove the route surface (same gate as test_node_facts.py)"

ok = 0
def check(cond, msg):
    global ok
    assert cond, msg
    ok += 1
    print("PASS", msg)

def call(route_fn, **kw):
    out = route_fn(**kw)
    if hasattr(out, "__await__"):
        import asyncio
        return asyncio.get_event_loop_policy().new_event_loop().run_until_complete(out)
    return out

def route_for(path):
    for rt in api.router.routes:
        if getattr(rt, "path", None) == path:
            return rt
    raise AssertionError(f"route {path} not registered")

from fastapi import HTTPException
def expect404(fn, *a, **kw):
    try:
        call(fn, *a, **kw)
    except HTTPException as e:
        return e.status_code == 404
    return False

# ---------- 1) the ONE 16 KiB tail route, requested by IDs only ----------
TAIL_PATH = "/runs/{run_id}/nodes/{nid}/log"
tail_routes = [rt for rt in api.router.routes
               if str(getattr(rt, "path", "")).endswith("/log")]
check(len(tail_routes) == 1 and tail_routes[0].path == TAIL_PATH,
      "exactly ONE tail route is registered (the existing /runs/{id}/nodes/{nid}/log — no second surface)")
check(api.LOG_TAIL == 16384, "the tail cap is the existing LOG_TAIL = 16KiB constant")
get_log = route_for(TAIL_PATH).endpoint
params = tuple(inspect.signature(get_log).parameters)
check(set(params) == {"run_id", "nid", "index", "attempt", "kind", "tail"},
      f"ID-only request: the endpoint takes ONLY ids/bounded ints {sorted(params)} — no path parameter")
check(inspect.signature(get_log).parameters["tail"].default == api.LOG_TAIL,
      "the default request is the existing 16KiB tail itself")
for rt in api.router.routes:
    for p in inspect.signature(rt.endpoint).parameters:
        assert p not in ("path", "file", "filename"), f"route {rt.path} takes a caller-supplied {p!r}"
check(True, "no dashboard route accepts a caller-supplied path/file parameter")

# ---------- seed one run dir, written the way wf.py commits it ----------
RUN = "s20-insp-src"
r = HOME / "workflows" / RUN
(r / "nodes").mkdir(parents=True)
(r / "logs").mkdir()
(r / "gates").mkdir()
TS_RUN = "2026-02-01T00:00:00+00:00"          # the RUN clock (run.json)
TS_SOLO = "2026-02-01T00:05:00+00:00"         # item clocks (records) — all distinct
TS_F0 = "2026-02-01T00:10:00+00:00"
TS_F1 = "2026-02-01T00:11:00+00:00"
EPOCH_EVENTS = time.time()
graph = {"name": "s20-insp-src", "nodes": [
    {"id": "solo", "type": "agent", "goal": "one big log"},
    {"id": "fan", "type": "agent", "goal": "two lanes", "after": ["solo"],
     "fanout": {"items": ["a", "b"], "goal": "lane {item}"}},
    {"id": "dead", "type": "agent", "goal": "needs a pr", "after": ["solo"]},
    {"id": "never", "type": "agent", "goal": "cap spent", "after": ["solo"]}]}
byid = {n["id"]: n for n in graph["nodes"]}
(r / "graph.json").write_text(json.dumps(graph))
(r / "run.json").write_text(json.dumps({"name": "s20-insp-src", "started": TS_RUN}))

def rec(nid, **kw):
    (r / "nodes" / f"{nid}.json").write_text(
        json.dumps({**kw, "fp_rule_version": wfcommon.FP_RULE_VERSION}))

big = bytes((i * 7 + 3) % 251 + 1 for i in range(40000))   # deterministic 40 KB, no zeros
(r / "logs" / "solo.a0.log").write_bytes(big)
(r / "logs" / "solo.a0.prompt.md").write_text("# prompt\n## Inputs\nparent output here\n")
(r / "logs" / "fan.0.a0.log").write_bytes(b"A0-attempt-zero\n" + b"0" * 300)
(r / "logs" / "fan.0.a1.log").write_bytes(b"A1-attempt-one\n" + b"1" * 300)
(r / "logs" / "fan.1.a0.log").write_bytes(b"")             # a REAL zero: spawned, wrote nothing
rec("solo", status="done", output={"result": "fine"}, ms=100,
    efp=wfcommon.efp(byid, byid["solo"]), attempts=1, attempts_log=[], final="",
    harvest=None, error=None, error_class=None, started=TS_SOLO,
    log_path=str(r / "logs" / "solo.a0.log"), prompt_path=str(r / "logs" / "solo.a0.prompt.md"))
# fan: COMMITTED aggregate (done) + leftover running item spawn records — the
# supersede law CJ2 renders (outcome from the aggregate, spawn provenance kept).
(r / "logs" / "fan.a0.log").write_bytes(b"aggregate-era bytes\n")
rec("fan", status="done", ms=200,
    efp=wfcommon.efp(byid, byid["fan"]),
    output={"all_results": [{"status": "done", "item": "a"}, {"status": "done", "item": "b"}]})
rec("fan.0", status="running", attempt=0, started=TS_F0,
    efp=wfcommon.efp(byid, byid["fan"]), skey=f"wf:{RUN}:fan:0:abcd1234.111111",
    log_path=str(r / "logs" / "fan.0.a0.log"))
rec("fan.1", status="running", attempt=0, started=TS_F1,
    efp=wfcommon.efp(byid, byid["fan"]), skey=f"wf:{RUN}:fan:1:abcd1234.222222",
    log_path=str(r / "logs" / "fan.1.a0.log"))
# TRUE zero-spawn: a precondition failure that never spawned — no log_path key,
# no attempt files, no child DB rows anywhere below.
rec("dead", status="failed", error_class="precondition",
    error="precondition unmet: pr#1", output={"missing": ["pr#1"]}, ms=0,
    efp=wfcommon.efp(byid, byid["dead"]), started=TS_RUN)
# REFUSAL: wf.py _window_spent_record's committed shape VERBATIM (the shape
# tests/fixtures/refusal_capture.py pins for the panel): refused this boot.
rec("never", status="failed",
    error=("transient-retry lifetime bound spent before this boot: "
           "2 persisted re-spawn grant(s) against the node transient "
           "cap (3) — spawn refused"),
    error_class="transport_exhausted", ms=0, attempts=3, spawn=2,
    refusal="lifetime_cap_spent",
    attempts_log=[{"attempt": 0, "error_class": "transport"},
                  {"attempt": 1, "error_class": "transport"},
                  {"attempt": 2, "error_class": "transport_exhausted"}],
    final="", efp=wfcommon.efp(byid, byid["never"]), started=TS_RUN)
(r / "events.jsonl").write_text(json.dumps({"event": "run.start", "at": TS_RUN}) + "\n"
                                + json.dumps({"event": "node.settled", "node": "solo",
                                              "status": "done", "at": TS_SOLO}) + "\n")
os.utime(r / "events.jsonl", (EPOCH_EVENTS + 300, EPOCH_EVENTS + 300))

# child telemetry: state.db in the resolved home, exact schema child_metrics reads.
home = Path(wfcommon.hermes_home())
assert home == HOME, f"hermetic home drifted: {home} != {HOME}"
db = sqlite3.connect(home / "state.db")
db.execute("""create table sessions(
    title text, model text, billing_provider text,
    input_tokens integer, output_tokens integer, cache_read_tokens integer,
    reasoning_tokens integer, api_call_count integer, tool_call_count integer,
    estimated_cost_usd real, last_activity_at real, last_activity_description text,
    ended_at real, started_at real)""")
def srow(title, tok_in, api_calls, started, last):
    db.execute("insert into sessions values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               (title, "m-a", "prov", tok_in, 10, 0, 0, api_calls, 2, 0.01,
                last, "working", last + 5, started))
srow(f"wf:{RUN}:fan:0:abcd1234.111111#a0", 100, 3, time.mktime((2026, 2, 1, 0, 10, 0, 0, 0, 0)),
     time.mktime((2026, 2, 1, 0, 11, 0, 0, 0, 0)))
srow(f"wf:{RUN}:fan:1:abcd1234.222222#a0", 7, None, time.mktime((2026, 2, 1, 0, 11, 0, 0, 0, 0)),
     time.mktime((2026, 2, 1, 0, 11, 30, 0, 0, 0)))       # unknown api-call count
srow(f"wf:{RUN}:solo:beef0000.333333#a0", 1000, 4, time.mktime((2026, 2, 1, 0, 5, 0, 0, 0, 0)),
     time.mktime((2026, 2, 1, 0, 6, 0, 0, 0, 0)))
db.commit(); db.close()

view = call(route_for("/runs/{run_id}").endpoint, run_id=RUN)
nodes = view["nodes"]

# ---------- 2) the 16 KiB boundary: cap, refusal, small tails ----------
res = call(get_log, run_id=RUN, nid="solo")            # default = the existing full tail
check(res["bytes"] == api.LOG_TAIL and res["content"] == big[-16384:].decode("utf-8", "replace"),
      "default tail serves EXACTLY the last 16 KiB of a 40 KiB log (never the whole file)")
check(res["size"] == 40000, "size reports the file's true size while bytes reports the served window")
check(expect404(get_log, run_id=RUN, nid="solo", tail=16385),
      "tail=16385 (beyond the existing 16 KiB) is REFUSED, not clamped")
check(expect404(get_log, run_id=RUN, nid="solo", tail=0) and expect404(get_log, run_id=RUN, nid="solo", tail=-1),
      "zero/negative tail is REFUSED (no unbounded read sneaks through)")
res = call(get_log, run_id=RUN, nid="solo", kind="prompt")
check("## Inputs" in res["content"], "kind=prompt serves the record's prompt_path through the SAME tail")
check(expect404(get_log, run_id=RUN, nid="solo", kind="bogus"), "unknown kind = 404")

# containment: the path is the RECORD's, never the caller's
rec("liar", status="done", log_path="/etc/passwd", prompt_path=str(r / ".." / "outside.md"))
check(api._node_log_tail(r, "liar", None, None, "log", 16) is None
      and api._node_log_tail(r, "liar", None, None, "prompt", 16) is None,
      "a record whose paths escape <run>/logs = 404 (containment holds both kinds)")
check(expect404(get_log, run_id=RUN, nid="../solo", tail=16), "crafted nid escaping the record dir = 404")

# ---------- 3) out-of-attempt / out-of-index are REFUSED ----------
res = call(get_log, run_id=RUN, nid="fan", index=0, attempt=0)
check(res["content"].startswith("A0-attempt-zero"), "attempt=0 reads the attempt-0 sibling log")
res = call(get_log, run_id=RUN, nid="fan", index=0, attempt=1)
check(res["content"].startswith("A1-attempt-one"), "attempt=1 reads the attempt-1 sibling, never the merged base")
check(expect404(get_log, run_id=RUN, nid="fan", index=0, attempt=2),
      "attempt=2 (never spawned) = 404 — out-of-attempt REFUSED, not an empty 200")
check(expect404(get_log, run_id=RUN, nid="fan", index=0, attempt=99)
      and expect404(get_log, run_id=RUN, nid="fan", index=0, attempt=-1),
      "absurd and negative attempts = 404")
check(expect404(get_log, run_id=RUN, nid="fan", index=1, attempt=0, kind="prompt"),
      "attempt on a kind the record never carried (no prompt_path) = 404")
check(expect404(get_log, run_id=RUN, nid="fan", index=2, tail=16),
      "fan.2 has no record: out-of-index = 404")
check(expect404(get_log, run_id=RUN, nid="fan", index=-1, tail=16)
      and expect404(get_log, run_id=RUN, nid="fan", index=100000, tail=16),
      "negative / absurd index = 404 (int coercion invents no record)")
check(expect404(get_log, run_id=RUN, nid="solo", index=0, tail=16),
      "a non-fanout node gains no item-0 record: solo.0 = 404 (never fabricated)")

# ---------- 4) absent sentinels, not zeros ----------
res = call(get_log, run_id=RUN, nid="fan", index=1)
check(res["size"] == 0 and res["bytes"] == 0 and res["content"] == "",
      "an EMPTY log is a real zero: 200 with size 0 (distinct class from absent)")
check(expect404(get_log, run_id=RUN, nid="never") and expect404(get_log, run_id=RUN, nid="dead"),
      "zero-spawn/refused nodes have NO log: 404 sentinel, never a 200 of zeros")
bare = wfcommon.node_facts(r, "never")
check(bare["log_path"] == "unknown" and bare["prompt_path"] == "unknown",
      "absent record paths read 'unknown' (the sentinel), not '' / None / 0")

# ---------- 5) TRUE zero-spawn + refusal ride the read model verbatim ----------
check(nodes["dead"]["status"] == "failed" and nodes["dead"]["error_class"] == "precondition",
      "true zero-spawn precondition failure commits verbatim")
check(nodes["dead"].get("fact") == "failed (precondition: pr#1)",
      "the precondition fact renders the runner-committed missing list")
check(nodes["never"]["refusal"] == "lifetime_cap_spent"
      and nodes["never"]["error_class"] == "transport_exhausted"
      and nodes["never"]["attempts"] == 3 and len(nodes["never"]["attempts_log"]) == 3,
      "spent-cap refusal rides verbatim: refusal + error_class + attempts + attempts_log (the CJ2 binding)")
check("metrics" not in nodes["never"] and "metrics" not in nodes["dead"],
      "zero-spawn nodes carry NO metrics key — honest absence, never fabricated zeros")
check(view["status"] == "failed", "the run verdict reflects the failed nodes (read model, not the tail)")

# ---------- 6) separate run/item clocks + no borrowing across levels ----------
check(view["started"] == TS_RUN, "run clock: view.started is run.json's stamp, verbatim")
check(view["updated"] == EPOCH_EVENTS + 300,
      "run activity clock: view.updated is the events.jsonl mtime — its OWN source")
f0 = wfcommon.node_facts(r, "fan", index=0)
f1 = wfcommon.node_facts(r, "fan", index=1)
check(f0["started"] == TS_F0 and f1["started"] == TS_F1 and nodes["solo"]["started"] == TS_SOLO,
      "each item carries ITS OWN started from its own record (verbatim)")
check(len({TS_RUN, TS_SOLO, TS_F0, TS_F1}) == 4
      and f0["started"] != view["started"] and f1["started"] != view["started"],
      "run clock and item clocks are distinct seeds and stay distinct in the view (no borrowing)")
check(f0["status"] == "done" and f0.get("superseded_by_aggregate") == "fan.json"
      and f1["status"] == "done",
      "leftover running items read done FROM the committed aggregate (supersede law CJ2 renders)")
im = nodes["fan"]["item_metrics"]
check(im[0]["tokens_in"] == 100 and im[1]["tokens_in"] == 7,
      "item metrics fold ONLY that item's child rows")
check(nodes["fan"]["metrics"]["tokens_in"] == 107,
      "node metrics fold = the sum of its items (107), not a per-item value")
check(view["metrics"]["tokens_in"] == 1107,
      "run rollup = every child of the run (1000 + 107), its own level")
check(im[0]["api_calls"] == 3 and "api_calls" not in im[1] and "api_calls" not in nodes["fan"]["metrics"]
      and "api_calls" not in view["metrics"],
      "one unknown row OMITS api_calls at every level it touches (absent, never a partial-sum zero)")
check(nodes["fan"]["metrics"]["last_activity"] is None
      and im[0]["last_activity"] is None and view["metrics"]["last_activity"] is None,
      "closed items report last_activity=None — the run's nonzero clock is NOT borrowed into item clocks")
check(nodes["fan"]["metrics"]["scope"] == view["metrics"]["scope"] == "cumulative",
      "folded counters are labelled cumulative (what a node line totals)")

# ---------- 7) bounds hold under the read model's own re-read (idempotence) ----------
again = call(route_for("/runs/{run_id}").endpoint, run_id=RUN)
check(again == view, "the whole inspection view is a pure read: re-answer byte-identical (no write-on-read)")
check(api._node_log_tail(r, "solo", None, "../../etc/pa", "log", 16) is None,
      "crafted attempt string that could escape is refused at the core")

print(f"OK {ok} checks")
shutil.rmtree(HOME, ignore_errors=True)
