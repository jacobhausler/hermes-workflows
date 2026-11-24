"""00e46adb (spool 5ff2806f359c16a1): a fresh verify node two hops under a go-gate
could not see the gate's committed answer — the binding release ("proceed despite C1,
owner override …") reached only the gate's DIRECT child via the auto parent-injection
loop, so the verify graded the deliberate override as 'C1 NOT met / authority
UNVERIFIED'. Law (build_inputs): every transitive ancestor gate whose answer is
COMMITTED (done via the gate_answer_valid efp law) is injected into every downstream
agent prompt, capped like any auto input; a skipped/unanswered gate has no done
record and injects NOTHING (fail-closed by construction); ids already covered by an
explicit `inputs:` ref or a direct-parent block are never duplicated. Solo graphs
with no released gate gain zero bytes (golden-solo EMPTY is the outer gate).
"""
import importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
home = HERE / "home19"
if home.exists():
    shutil.rmtree(home)
home.mkdir()
os.environ["HERMES_HOME"] = str(home)
os.environ["WF_RUNS_ROOT"] = str(Path(os.environ["HERMES_HOME"]) / "workflows")  # est-2ek.1.762 pin: HERMES_HOME alone is not a sandbox
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}"
    ok += 1; print("PASS", msg)

fake = str(HERE / "fake")

def run_graph(name, graph, gate_answers=None, seed=None):
    """Pre-answer gates (valid efp-stamped records in gates/<id>.json), optionally
    pre-commit nodes, run wf.py to completion; return (run_dir, prompts)."""
    runs = home / "workflows"; runs.mkdir(exist_ok=True)
    run = runs / name
    shutil.rmtree(run, ignore_errors=True)
    (run / "nodes").mkdir(parents=True); (run / "gates").mkdir()
    (run / "graph.json").write_text(json.dumps(graph))
    (run / "run.json").write_text(json.dumps({"name": name, "hermes_bin": fake,
                                              "concurrency": 4, "node_timeout": 30,
                                              "started": "2099-01-01T00:00:00+00:00"}))
    byid = {n["id"]: n for n in graph["nodes"]}
    for gid, ans in (gate_answers or {}).items():
        rec = {"answer": ans, "_def": wfcommon.efp(byid, byid[gid]),
               "fp_rule_version": wfcommon.FP_RULE_VERSION,
               "at": "2099-01-01T00:00:00+00:00"}
        (run / "gates" / f"{gid}.json").write_text(json.dumps(rec))
    for nid, rec in (seed or {}).items():
        (run / "nodes" / f"{nid}.json").write_text(
            json.dumps({**rec, "efp": wfcommon.efp(byid, byid[nid]),
                        "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    plog = home / f"{name}.prompts.log"
    if plog.exists():
        plog.unlink()
    p = subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", name],
                       capture_output=True, text=True, timeout=120,
                       env={**os.environ, "HERMES_HOME": str(home), "WF_RUNS_ROOT": str(runs),
                            "FAKE_LOG": str(home / f"{name}.fake.log"),
                            "FAKE_PROMPT_LOG": str(plog)})
    prompts = plog.read_text().split("\n=====PROMPT=====\n")[1:] if plog.exists() else []
    return run, prompts, p.stdout + p.stderr

OVERRIDE = "proceed despite C1 - owner override: ship window closes tonight"

# chain: plan -> go(gate) -> impl -> verify   (verify is TWO hops under the gate)
CHAIN = {"nodes": [
    {"id": "plan", "type": "agent", "goal": "JSON:{\"result\":\"planned\"}"},
    {"id": "go", "type": "gate", "after": ["plan"], "question": "Release?", "options": ["yes", "no"]},
    {"id": "impl", "type": "agent", "after": ["go"], "goal": "implement"},
    {"id": "verify", "type": "agent", "after": ["impl"], "goal": "verify the release decision"},
]}

# --- (1) the incident: verify sees the ancestor gate answer ----------------------
run, prompts, out = run_graph("gatechain", CHAIN, gate_answers={"go": OVERRIDE})
vpr = [p for p in prompts if "verify the release decision" in p]
check(len(vpr) == 1, "verify spawned once", str(len(vpr)))
check(OVERRIDE in vpr[0], "verify prompt carries the ancestor gate's committed answer", out[-400:])
check("(ancestor gate answer)" in vpr[0], "the block is labelled as an ancestor gate answer")

# --- (2) direct child of the gate: ONE block, never duplicated -------------------
ipr = [p for p in prompts if "implement" in p.splitlines()[0] or ("implement" in p and "## Inputs" in p)][0]
check(ipr.count(OVERRIDE) == 1, "direct child impl gets the answer exactly once (no ancestor duplication)")

# --- (3) fail-closed: an unanswered/skipped gate injects nothing ------------------
# when-false gate -> skipped (never done): the downstream agent must NOT gain a gate block.
SKIPG = {"nodes": [
    {"id": "a", "type": "agent", "goal": "JSON:{\"go\":false}"},
    {"id": "g", "type": "gate", "after": ["a"], "question": "Continue?",
     "options": ["yes"], "when": "out.a.go == True", "on_skip": "pass"},
    {"id": "b", "type": "agent", "after": ["g"], "goal": "downstream of a skipped gate"},
]}
run2, prompts2, out2 = run_graph("gate.skip", SKIPG)
bpr = [p for p in prompts2 if "downstream of a skipped gate" in p]
check(len(bpr) == 1, "downstream of skipped gate still runs (non-prune skip)")
check("(ancestor gate answer)" not in bpr[0], "a SKIPPED gate injects no answer block", out2[-300:])

# --- (4) explicit inputs: ref covering the gate head suppresses the auto block ----
EXPL = {"nodes": [
    {"id": "a", "type": "agent", "goal": "JSON:{\"result\":\"planned\"}"},
    {"id": "go", "type": "gate", "after": ["a"], "question": "Release?", "options": ["yes", "no"]},
    {"id": "impl", "type": "agent", "after": ["go"], "goal": "implement", "inputs": ["go.answer"]},
]}
_, prompts3, _ = run_graph("gate.explicit", EXPL, gate_answers={"go": OVERRIDE})
apr = [p for p in prompts3 if "implement" in p]
check(len(apr) == 1 and apr[0].count(OVERRIDE) == 1,
      "explicit inputs:[go.answer] keeps exactly one block (covered id not re-injected)")
check("(ancestor gate answer)" not in apr[0],
      "explicit coverage means no ancestor-labelled duplicate")

# --- (5) MUTATION CONTROL: the law is present and fail-closed ---------------------
src = (BUILD / "wf.py").read_text()
check("ancestor gate answer" in src, "the injection loop ships")
check("a in injected or a not in outputs" in src,
      "skip rule: non-gates, covered ids, and UNCOMMITTED answers never inject")

# --- (6) UI ANSWER DOOR (bd_2026-11-13-qri): the UI's POST records a _ui
# answer, the read model reads it back, and NOTHING resumes on this path.
# Isolated runner: this run dir has no live pid/lock and never spawns a child
# — "nothing restarted" is verified for the tested isolated runner, not
# claimed as a universal scheduler law.
import asyncio, hashlib, types
home20 = HERE / "home20"
if home20.exists():
    shutil.rmtree(home20)
home20.mkdir()
os.environ["HERMES_HOME"] = str(home20)
os.environ["WF_RUNS_ROOT"] = str(home20 / "workflows")  # est-2ek.1.762 pin again

# plugin_api guards its router import; feed it a stub fastapi so the route
# FUNCTIONS exist and are driven directly (no HTTP server, no dependency).
_fastapi = types.ModuleType("fastapi")
class _Router:
    def get(self, *a, **k): return lambda f: f
    def post(self, *a, **k): return lambda f: f
_fastapi.APIRouter = _Router
_fastapi.HTTPException = Exception
sys.modules.setdefault("fastapi", _fastapi)
api_spec = importlib.util.spec_from_file_location(
    "plugin_api_qri", BUILD / "dashboard" / "plugin_api.py")
api = importlib.util.module_from_spec(api_spec)
api_spec.loader.exec_module(api)

runs = home20 / "workflows"; runs.mkdir(exist_ok=True)
uir = runs / "gate.ui"
(uir / "nodes").mkdir(parents=True); (uir / "gates").mkdir()
UGRAPH = {"nodes": [
    {"id": "plan", "type": "agent", "goal": "plan"},
    {"id": "review", "type": "gate", "after": ["plan"],
     "question": "Save this review decision?",
     "options": ["Approve review", "Keep for revision"],
     "context": "Isolated review workflow"},
]}
uir_byid = {n["id"]: n for n in UGRAPH["nodes"]}
(uir / "graph.json").write_text(json.dumps(UGRAPH))
(uir / "run.json").write_text(json.dumps({"name": "gate.ui", "hermes_bin": fake,
                                          "concurrency": 4, "node_timeout": 30,
                                          "started": "2099-01-01T00:00:00+00:00"}))
(uir / "events.jsonl").write_text(json.dumps(
    {"ts": "2099-01-01T00:00:00+00:00", "event": "gate.held", "node": "review"}) + "\n")
(uir / "nodes" / "plan.json").write_text(json.dumps(
    {"status": "done", "output": {"result": "planned"},
     "efp": wfcommon.efp(uir_byid, uir_byid["plan"]),
     "fp_rule_version": wfcommon.FP_RULE_VERSION}))

UI_ANSWER = "Approve review"
sha_before = hashlib.sha256((uir / "events.jsonl").read_bytes()).hexdigest()

# held truth BEFORE the answer: question verbatim, declared requester, options.
v = api.get_run("gate.ui")
check(v.get("status") == "held", "isolated ready gate reads held")
check(v.get("held_gate", {}).get("question") == "Save this review decision?"
      and v["held_gate"]["options"] == ["Approve review", "Keep for revision"],
      "held_gate carries question + options verbatim")
check(v["held_gate"].get("context") == "Isolated review workflow",
      "the requester identity rides the read model (graph-declared, never invented)")
check("gates" not in v, "unanswered gate: no receipt block (honest absence)")

# warm the census cache, then the UI's POST — and the VERY NEXT read inside the
# TTL window must reflect it (proof the route invalidates BEFORE the read).
api.list_runs()
res = asyncio.run(api.release_gate("gate.ui", {"gate_id": "review", "answer": UI_ANSWER}))
rec = json.loads((uir / "gates" / "review.json").read_text())
check(res.get("ok") is True and res.get("at") == rec["at"],
      "UI door: release returns ok + the DURABLE receipt timestamp (response at == record at)",
      str(res))
check(rec["answer"] == UI_ANSWER, "the exact answer reads back from the record")
check(rec.get("_ui") is True, "the UI write stamps _ui provenance")
check("_def" in rec and rec.get("fp_rule_version") == wfcommon.FP_RULE_VERSION,
      "the answer carries the efp stamp the read model validates")
row = [x for x in api.list_runs()["runs"] if x["id"] == "gate.ui"][0]
check(row["status"] != "held" and "held_gate" not in row,
      "invalidate-before-read: the next GET reflects the answer inside one TTL window")
v2 = api.get_run("gate.ui")
check(v2.get("gates", {}).get("review", {}).get("answer") == UI_ANSWER
      and v2["gates"]["review"].get("_ui") is True,
      "full view exposes the durable gates block for the saved receipt")

# duplicate / conflict: a VALID answer is never silently overwritten.
res = asyncio.run(api.release_gate("gate.ui", {"gate_id": "review", "answer": "Keep for revision"}))
check(res == {"ok": False, "error": "gate already answered (current graph)"},
      "pending duplicate prevention at the API: second POST is a typed refusal, ok:false")
check(json.loads((uir / "gates" / "review.json").read_text())["answer"] == UI_ANSWER,
      "the refused second answer wrote nothing")

# stale answer (amend moved the def): overwrite is allowed, receipt re-records.
rec["answer"] = "stale seed"
rec["_def"] = "0000000000000000000000000000000000000000000000000000000000000000"
(uir / "gates" / "review.json").write_text(json.dumps(rec))
res = asyncio.run(api.release_gate("gate.ui", {"gate_id": "review", "answer": UI_ANSWER}))
check(res.get("ok") is True and res.get("at") == json.loads((uir / "gates" / "review.json").read_text())["at"],
      "a stale (amend-invalidated) answer is overwritable, re-stamped with a fresh receipt time", str(res))

# backend error classes: unknown run + stopped run, both ok:false, never ok:true.
res = asyncio.run(api.release_gate("nope-not-here", {"gate_id": "review", "answer": "x"}))
check(res == {"ok": False, "error": "unknown run"}, "unknown run answers ok:false")
(uir / "stop.request").write_text("")
res = asyncio.run(api.release_gate("gate.ui", {"gate_id": "review", "answer": "x"}))
check(res.get("ok") is False and "stopped" in res.get("error", ""),
      "a stopping run refuses the answer (nothing consumed)")
(uir / "stop.request").unlink()

# no resume, nothing restarted on this tested path: the event ledger is
# byte-identical, no gate.released event, no gate node record, no child log.
check(hashlib.sha256((uir / "events.jsonl").read_bytes()).hexdigest() == sha_before,
      "Nothing restarted (tested isolated runner): events.jsonl byte-identical after the UI answer")
check(not (uir / "nodes" / "review.json").exists(),
      "the UI answer did not consume the gate — no runner commit appeared")
check(not (uir / "logs").exists() or not list((uir / "logs").glob("*")),
      "zero spawns on the answer path: no child logs")

print(f"ALL PASS ({ok})")
