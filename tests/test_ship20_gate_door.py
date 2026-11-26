"""bd_2026-11-13-s20-gate-product (ship-2.0 gate product, door half):
the SHIP-2.0 GATE ACCEPTANCE at the one existing answer door — independent of
any native app proof capture (the xow/native-gate driver proves the SAME
behavior in the real surface; this suite never needs it).

Pins, at exact hosted main, against the shipped FastAPI route driven directly
(stub fastapi, no server, no scheduler):
  - ONE existing `_release_core(ui=True)` door — the route is the only ui=True
    call site in shipped source; `_release_core` is defined exactly once; the
    tool path (act_release) calls it WITHOUT ui, so `_ui` provenance is the UI
    door's alone.
  - invalidate BEFORE read (route order + behavior inside one TTL window).
  - `ok:false` is an error, never a mutation: unknown run, unknown/non-gate
    node, duplicate valid answer, stopped run — every refusal writes NOTHING.
  - stale: an amend-invalidated record is overwritable and re-stamped.
  - the answer response carries `at` == the record's stamped at (the exact
    toast's time source; review-2 Q1/Q2 contract).
  - no scheduler changes: the UI answer leaves events.jsonl byte-identical,
    commits no node record, spawns nothing.
"""
import asyncio, hashlib, importlib.util, json, os, re, shutil, sys, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
home = HERE / "home-s20-door"
if home.exists():
    shutil.rmtree(home)
home.mkdir()
os.environ["HERMES_HOME"] = str(home)
os.environ["WF_RUNS_ROOT"] = str(home / "workflows")  # est-2ek.1.762 pin
for k in ("UI2_PROOF_GATE_FAIL_ONCE", "UI2_PROOF_GATE_POST_DELAY_MS"):
    os.environ.pop(k, None)
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}"
    ok += 1; print("PASS", msg)

# ---------------------------------------------------------------- ONE DOOR law
init_src = (BUILD / "__init__.py").read_text()
api_src = (BUILD / "dashboard" / "plugin_api.py").read_text()
check(len(re.findall(r"^def _release_core\b", init_src, re.M)) == 1,
      "(one-door) `_release_core` is defined exactly once")
shipped = [BUILD / "__init__.py", BUILD / "wf.py", BUILD / "wfcommon.py",
           BUILD / "dashboard" / "plugin_api.py"]
def call_sites(p):
    return [ln for ln in p.read_text().splitlines()
            if "ui=True" in ln and "_release_core(" in ln and not ln.lstrip().startswith(("#", "*"))]
sites = {p.relative_to(BUILD).as_posix(): len(call_sites(p))
         for p in shipped if call_sites(p)}
check(sites == {"dashboard/plugin_api.py": 1}
      and len(re.findall(r"ui=True", api_src)) == 1,
      "(one-door) the UI route is the ONLY ui=True call site in shipped source", str(sites))
js_src = (BUILD / "desktop" / "plugin.js").read_text()
ui_lines = [ln for ln in js_src.splitlines() if re.search(r"ui\s*=\s*True", ln)]
check(len(ui_lines) == 1 and re.match(r"^\s*\*", ui_lines[0]),
      "(one-door) the desktop half's single `ui=True` mention is docstring prose, never a call")
check(len(re.findall(r"api\(`", js_src)) >= 1
      and len(re.findall(r"/gate`", js_src)) == 1
      and "/release" not in js_src and "release_lock" not in js_src,
      "(one-door) exactly one gate-answer REST path in the desktop half; no other release door")
check(re.search(r"_release_core\(\s*r\s*,\s*gate_id\s*,\s*args\.get\(", init_src)
      and "ui=True" not in init_src,
      "(one-door) the tool path calls _release_core WITHOUT ui — `_ui` provenance is the door route's alone")
m = re.search(r"async def release_gate.*?\n(?=    @|    def |\Z)", api_src, re.S)
route_src = m.group(0)
check(route_src.index("_runs_cache_invalidate()") < route_src.index("_safe_run("),
      "(invalidate-before-read) the route drops the census snapshot BEFORE the run lookup")

_fastapi = types.ModuleType("fastapi")
class _Router:
    def get(self, *a, **k): return lambda f: f
    def post(self, *a, **k): return lambda f: f
_fastapi.APIRouter = _Router
_fastapi.HTTPException = Exception
sys.modules.setdefault("fastapi", _fastapi)
api_spec = importlib.util.spec_from_file_location("plugin_api_s20", BUILD / "dashboard" / "plugin_api.py")
api = importlib.util.module_from_spec(api_spec)
api_spec.loader.exec_module(api)

runs = home / "workflows"; runs.mkdir(exist_ok=True)
def mk_run(name, stop=False):
    r = runs / name
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    graph = {"nodes": [
        {"id": "plan", "type": "agent", "goal": "plan"},
        {"id": "review", "type": "gate", "after": ["plan"],
         "question": "Save this review decision?",
         "options": ["Approve review", "Keep for revision"],
         "context": "Isolated review workflow"},
    ]}
    (r / "graph.json").write_text(json.dumps(graph))
    (r / "run.json").write_text(json.dumps({"name": name, "hermes_bin": str(HERE / "fake"),
                                            "concurrency": 4, "node_timeout": 30,
                                            "started": "2099-01-01T00:00:00+00:00"}))
    (r / "events.jsonl").write_text(json.dumps(
        {"ts": "2099-01-01T00:00:00+00:00", "event": "gate.held", "node": "review"}) + "\n")
    byid = {n["id"]: n for n in graph["nodes"]}
    (r / "nodes" / "plan.json").write_text(json.dumps(
        {"status": "done", "output": {"result": "planned"},
         "efp": wfcommon.efp(byid, byid["plan"]),
         "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    if stop:
        (r / "stop.request").write_text("")
    return r

# ------------------------------------------------ the happy UI answer + at contract
r = mk_run("gate.s20")
sha_before = hashlib.sha256((r / "events.jsonl").read_bytes()).hexdigest()
api.list_runs()  # warm the census cache: the next read must be FRESH, not TTL-stale
res = asyncio.run(api.release_gate("gate.s20", {"gate_id": "review", "answer": "Approve review"}))
rec = json.loads((r / "gates" / "review.json").read_text())
check(res.get("ok") is True and res.get("at") == rec["at"],
      "(one-door) the UI answer resolves ok with `at` == the record's stamped at", str(res))
check(rec["answer"] == "Approve review" and rec.get("_ui") is True,
      "(one-door) the exact answer reads back with _ui provenance from the ui=True door")
row = [x for x in api.list_runs()["runs"] if x["id"] == "gate.s20"][0]
check(row["status"] != "held" and "held_gate" not in row,
      "(invalidate-before-read) the very next list read reflects the answer inside one TTL window")
v = api.get_run("gate.s20")
check(v.get("gates", {}).get("review", {}).get("_ui") is True,
      "(invalidate-before-read) the full view re-projects the durable gates block for the receipt")

# ------------------------------------------------ ok:false is an error, zero writes
res = asyncio.run(api.release_gate("no.such.run", {"gate_id": "review", "answer": "x"}))
check(res == {"ok": False, "error": "unknown run"},
      "(ok:false) an unknown run answers a typed refusal, not a success", str(res))
res = asyncio.run(api.release_gate("gate.s20", {"gate_id": "review", "answer": "Keep for revision"}))
check(res == {"ok": False, "error": "gate already answered (current graph)"},
      "(duplicate) a second POST over a VALID answer is a typed ok:false refusal", str(res))
check(json.loads((r / "gates" / "review.json").read_text())["answer"] == "Approve review",
      "(duplicate) the refused answer wrote nothing")
res = asyncio.run(api.release_gate("gate.s20", {"gate_id": "nope", "answer": "x"}))
check(res == {"ok": False, "error": "no such gate node in this run"},
      "(ok:false) an unknown gate id is a typed refusal, not a mutation", str(res))
res = asyncio.run(api.release_gate("gate.s20", {"gate_id": "plan", "answer": "x"}))
check(res == {"ok": False, "error": "no such gate node in this run"},
      "(ok:false) a non-gate node is refused the same typed error", str(res))
r2 = mk_run("gate.stopped", stop=True)
res = asyncio.run(api.release_gate("gate.stopped", {"gate_id": "review", "answer": "Approve review"}))
check(res.get("ok") is False and "stopped" in str(res.get("error")),
      "(ok:false) an answer on a stopping run is refused", str(res))
check(not (r2 / "gates" / "review.json").exists(),
      "(ok:false) the refused answer wrote nothing on the stopping run")

# ------------------------------------------------ stale: overwrite iff absent-or-stale
rec["answer"] = "stale seed"; rec["_def"] = "0" * 64
(r / "gates" / "review.json").write_text(json.dumps(rec))
res = asyncio.run(api.release_gate("gate.s20", {"gate_id": "review", "answer": "Approve review"}))
fresh = json.loads((r / "gates" / "review.json").read_text())
check(res.get("ok") is True and res.get("at") == fresh["at"]
      and fresh["answer"] == "Approve review" and fresh["_ui"] is True,
      "(stale) an amend-invalidated record is overwritable and re-stamped with a fresh receipt time", str(res))

# ------------------------------------------------ no scheduler change on this path
check(hashlib.sha256((r / "events.jsonl").read_bytes()).hexdigest() == sha_before,
      "(no-scheduler) events.jsonl byte-identical after the UI answers — the door released, never drove")
check(not (r / "logs").exists() or not any((r / "logs").iterdir()),
      "(no-scheduler) zero spawns on the answer path: no child logs")
check(not (r / "nodes" / "review.json").exists(),
      "(no-scheduler) the gate was not consumed by the UI — the owning runner commits when it wakes")

print(f"ALL PASS ship20-gate-door ({ok}) — one ui=True door; invalidate-before-read; ok:false matrix; stale/duplicate; no-scheduler (isolated runner)")
sys.exit(0)
