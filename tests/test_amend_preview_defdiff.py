"""amend preview flags NEVER-COMMITTED nodes whose def differs from the frozen
graph (est-c9is): a model/provider-only edit to a node that has no committed
record (pending, or running when amended) must surface in `changed`/`will_rerun`
so the preview matches what the runner will actually spawn (issue #18 part 2).

Pure read-model test: no runner spawn. Records are written directly with the
correct efp stamps the runner would write."""
import json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(PLUGIN))
import wfcommon  # noqa: E402

RUNS = HERE / "home-amenddefdiff" / "workflows"
FAILS = []

def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)

def fresh(run_id, nodes):
    r = RUNS / run_id
    if r.exists():
        shutil.rmtree(r)
    for d in ("nodes", "gates", "logs"):
        (r / d).mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": "t", "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"name": "t", "hermes_bin": "fake", "concurrency": 4,
                                            "started": "2026-10-06T00:00:00+00:00", "owner": "test"}))
    return r

def agent(id, after=(), **kw):
    n = {"id": id, "type": "agent", "after": list(after), "timeout": 30, "goal": "say hi"}
    n.update(kw)
    return n

# ---- baseline: a done-committed, b never-committed (pending) with an explicit pin ----
base = [agent("a", model="m-a", provider="p1"),
        agent("b", ["a"], model="m-b", provider="p2"),
        agent("c", ["b"])]
r = fresh("20991006-000000-amenddefdiff", base)
byid = {n["id"]: n for n in base}
(r / "nodes" / "a.json").write_text(json.dumps(
    {"status": "done", "efp": wfcommon.efp(byid, byid["a"]), "output": {"ok": True}}))

# sanity: node_rec sees a committed, b pending
st_a, _ = wfcommon.node_rec(r, byid["a"], byid)
st_b, _ = wfcommon.node_rec(r, byid["b"], byid)
check("fixture: a committed done, b pending", st_a == "done" and st_b == "pending", f"{st_a}/{st_b}")

# ---- RED: amend b's model only (provider follows via _alias_provider_pair) ----
new = [dict(n) for n in base]
new[1] = {**new[1], "model": "m-c", "provider": "p9"}
pv = wfcommon.amend_preview(r, new)
check("def-edit to never-committed b is flagged changed",
      "b" in pv["changed"], json.dumps(pv))
check("def-edit to never-committed b propagates will_rerun to c",
      pv["will_rerun"] == ["b", "c"], json.dumps(pv))
check("unchanged never lists the def-edited pending node",
      "b" not in pv["unchanged"] and pv["unchanged"] == ["a"], json.dumps(pv))

# ---- guard: an untouched pending node must NOT be flagged (no phantom reruns) ----
pv_same = wfcommon.amend_preview(r, [dict(n) for n in base])
check("untouched pending node stays out of changed",
      pv_same["changed"] == [] and pv_same["will_rerun"] == []
      and pv_same["unchanged"] == ["a"], json.dumps(pv_same))

# ---- guard: budget-only edit to a pending node is NOT a def change (budgets are not work) ----
budge = [dict(n) for n in base]
budge[1] = {**budge[1], "max_turns": 99, "timeout": 999}
pv_b = wfcommon.amend_preview(r, budge)
check("budget-only edit to pending node is not changed",
      pv_b["changed"] == [] and pv_b["will_rerun"] == [], json.dumps(pv_b))

print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS)} ({6 - len(FAILS)}/6)")
sys.exit(1 if FAILS else 0)
