"""est-qohvi: {run.KEY} refs bound at launch were NEVER re-bound at amend — a wake
recovery re-submitting RAW binder output committed literal tokens into a bound
run's live graph (wake-31 lived it: ra-pr deep run 20261027-072003, review.a1 and
reconcile.a0 rendered {run.ITEM} after the 07:41:10 amend, bead= suffix stripped,
BEAD LAW file-one-first fallback fired, nodes re-paid via fresh GET).

This test pins the cure shape named in the row:
  launch(run_context bound) -> amend with raw {run.ITEM} text -> the committed
  graph goals are bound again; and where no persisted binding exists, the amend is
  REFUSED and the run is untouched. Stdlib only; _spawn_runner stubbed (no runner).
"""
import atexit, copy, importlib, json, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-qohvi-", dir=HERE / "tests")
atexit.register(tmp_dir.cleanup)
home = Path(tmp_dir.name)
os.environ["HERMES_HOME"] = str(home)
os.environ["WF_RUNS_ROOT"] = str(home / "workflows")
ALIASES = ("  aliases:\n    fable: anthropic/claude-fable-5.1\n    opus: anthropic/claude-opus-5-5\n"
           "    sol: openai-codex/gpt-6-sol\n")
(home / "config.yaml").write_text("model:\n  default: qwen38-next\n" + ALIASES)
door = importlib.import_module("__init__")
import wf_test_isolation as _iso; _iso.install(door)
door._ping_route_once = lambda p, m: {"liveness": "unknown"}   # no network
door._spawn_runner = lambda r: None                             # no runner

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

class Ctx:
    def get_config(self, k, d=None):
        return {"worker": "qwen38-next", "manager": "fable", "frontier": "sol"} if k == "models" else d
door._CTX = Ctx()

# The wake-31 payload shape: an operative ITEM line carrying the concrete record.
ITEM = ('PR hermes-workflows#566 by jacobhausler profile=human? blast=deep author=human '
        'reviewer=- "feat(park-watch): persisted watchdog" head=7ef5bdb ci=fail:diagram-check '
        'bead=est-qohvi')
BIND = {"ITEM": ITEM}

def author():
    """The RAW binder output — exactly what the lane script re-renders."""
    return {"name": "ra-pr-probe", "nodes": [
        {"id": "review", "type": "agent", "model": "worker",
         "goal": "ITEM: {run.ITEM}\n\nRun the repo-admin pr-review lane — DEEP."},
        {"id": "reconcile", "type": "agent", "model": "worker", "after": ["review"],
         "goal": "ITEM: {run.ITEM}\n\nUnder ## Inputs are the reads. You are the SOLE writer."},
    ]}

def meta_of(rid):
    return json.loads((home / "workflows" / rid / "run.json").read_text())

def graph_of(rid):
    return json.loads((home / "workflows" / rid / "graph.json").read_text())

def goals_bound(g):
    return all("{run." not in n.get("goal", "") and (n.get("goal", "").count("ITEM") == 0
            or ITEM in n["goal"]) for n in g["nodes"])

# ---------------------------------------------------------------- cure (a): launch persists the binding
run1 = door.act_run({"graph": author(), "run_context": BIND})
check("launch with run_context ok", run1.get("error") is None, run1.get("error"))
rid = run1.get("run_id")
check("cure(a): run.json persists run_context_binding == the effective map",
      meta_of(rid).get("run_context_binding") == BIND, meta_of(rid).get("run_context_binding"))
check("launch bound every goal (no residue)", goals_bound(graph_of(rid)))

run2 = door.act_run({"graph": {"name": "plain", "nodes": [
    {"id": "a", "type": "agent", "model": "worker", "goal": "plain goal"}]}},)
check("golden bytes: a no-run_context run grows no run_context_binding key",
      "run_context_binding" not in meta_of(run2["run_id"]), sorted(meta_of(run2["run_id"])))
run3 = door.act_run({"graph": {"name": "seeded", "nodes": [
    {"id": "a", "type": "agent", "model": "worker", "goal": "seed target"}]},
    "run_context": "SEED: claim your bead before writing"})
check("a seed launch persists NOTHING (seeds cannot re-bind refs)",
      "run_context_binding" not in meta_of(run3["run_id"]), sorted(meta_of(run3["run_id"])))

# ---------------------------------------------------------------- cure (b): raw resubmit re-binds
out = door.act_amend({"run_id": rid, "graph": author()})
check("wake-31 shape: raw binder resubmit ACCEPTED via re-bind",
      out.get("ok") is True and out.get("error") is None, out.get("error"))
check("committed goals bound again (concrete ITEM, no {run. token)", goals_bound(graph_of(rid)))
check("re-bind kept the bound value intact (bead= suffix present)",
      "bead=est-qohvi" in graph_of(rid)["nodes"][0]["goal"],
      graph_of(rid)["nodes"][0]["goal"][:140])
check("re-bind is byte-identity for unchanged nodes (replay-skip, no re-pay)",
      out.get("changed") == [], {"changed": out.get("changed"), "unchanged": out.get("unchanged")})
rows = [json.loads(l) for l in (home / "workflows" / rid / "amends.jsonl").read_text().splitlines()]
check("amends.jsonl records the BOUND new-side (the archive stays truthful)",
      "{run." not in rows[-1]["new"]["nodes"][0]["goal"])

# ---------------------------------------------------------------- refuse: pre-fix run, untouched
m = meta_of(rid); m.pop("run_context_binding", None)   # tolerate: on main the key never existed
(home / "workflows" / rid / "run.json").write_text(json.dumps(m))
gbytes = (home / "workflows" / rid / "graph.json").read_text()
nrows = len(rows)
out4 = door.act_amend({"run_id": rid, "graph": author()})
check("pre-fix bound run (no persisted binding): raw resubmit REFUSED",
      out4.get("error") is not None and out4.get("error_type") == "amend_run_context_unbound",
      out4.get("error_type"))
check("refusal names the surviving token", out4.get("surviving_run_refs") == ["ITEM"], out4.get("surviving_run_refs"))
check("refusal lands before any write: graph.json bytes stand",
      (home / "workflows" / rid / "graph.json").read_text() == gbytes)
check("refusal writes no amends row",
      len((home / "workflows" / rid / "amends.jsonl").read_text().splitlines()) == nrows)

# ---------------------------------------------------------------- refuse: ref the map lacks
m = meta_of(rid); m["run_context_binding"] = BIND
(home / "workflows" / rid / "run.json").write_text(json.dumps(m))
g5 = author(); g5["nodes"].append({"id": "tail", "type": "agent", "model": "worker",
                                   "after": ["reconcile"], "goal": "{run.OTHER} tail"})
out5 = door.act_amend({"run_id": rid, "graph": g5})
check("a ref absent from the persisted map refuses as amend_run_context_rebind",
      out5.get("error_type") == "amend_run_context_rebind" and "OTHER" in (out5.get("error") or ""),
      {k: out5.get(k) for k in ("error_type", "error")})
check("missing-key refusal also lands before any write",
      (home / "workflows" / rid / "graph.json").read_text() == gbytes)

# ---------------------------------------------------------------- plain-lenient law unchanged
run6 = door.act_run({"graph": author()})          # refs, no run_context: today's leniency
check("plain-lenient launch still launches (literal seats, unchanged law)",
      run6.get("error") is None, run6.get("error"))
check("plain-lenient committed graph carries the literal",
      "{run.ITEM}" in graph_of(run6["run_id"])["nodes"][0]["goal"])
out7 = door.act_amend({"run_id": run6["run_id"], "graph": author()})
check("plain-lenient raw resubmit PASSES untouched (no bound run to un-bind)",
      out7.get("ok") is True and out7.get("error") is None,
      {k: out7.get(k) for k in ("error", "error_type")})

# ---------------------------------------------------------------- seed run carrying a fresh ref
out8 = door.act_amend({"run_id": run3["run_id"], "graph": author()})
check("seed-launched run + ref-carrying amend REFUSES fail-closed",
      out8.get("error_type") == "amend_run_context_unbound",
      {k: out8.get(k) for k in ("error", "error_type")})

print(("ALL PASS: amend re-binds {run.KEY} from the persisted launch binding"
       if fails == 0 else f"{fails} FAILURE(S)") + f" ({20 - fails}/{20} checks)")
sys.exit(1 if fails else 0)
