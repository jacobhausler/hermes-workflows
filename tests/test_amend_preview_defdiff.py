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

# ---- issue #18 (the un-fixed half): a node RUNNING when amended carries the
# spawn-time record (status="running", never a commit — node_rec reads it as
# pending). A model/provider-only edit to it must surface too: the re-driven
# runner spawns it with the NEW def, so preview must not read changed:[].
base_r = [agent("a", model="m-a", provider="p1"),
          agent("b", ["a"], model="m-b", provider="p2"),
          agent("c", ["b"])]
r2 = fresh("20991006-000001-amenddefdiff", base_r)
byid2 = {n["id"]: n for n in base_r}
(r2 / "nodes" / "a.json").write_text(json.dumps(
    {"status": "done", "efp": wfcommon.efp(byid2, byid2["a"]), "output": {"ok": True}}))
(r2 / "nodes" / "b.json").write_text(json.dumps(
    {"status": "running", "efp": wfcommon.efp(byid2, byid2["b"]), "pid": 999999,
     "spawn_cmd": ["fake"], "log_path": "logs/b.a1.log", "skey": "s", "attempt": 1}))
st_b_run, rec_b = wfcommon.node_rec(r2, byid2["b"], byid2)
check("fixture: b running reads pending with a spawn-time record",
      st_b_run == "pending" and (rec_b or {}).get("status") == "running",
      f"{st_b_run}/{(rec_b or {}).get('status')}")

new_r = [dict(n) for n in base_r]
new_r[1] = {**new_r[1], "model": "m-c", "provider": "p9"}
pv_r = wfcommon.amend_preview(r2, new_r)
check("def-edit to RUNNING never-committed b is flagged changed",
      "b" in pv_r["changed"], json.dumps(pv_r))
check("def-edit to RUNNING b propagates will_rerun to c",
      pv_r["will_rerun"] == ["b", "c"], json.dumps(pv_r))

pv_r_same = wfcommon.amend_preview(r2, [dict(n) for n in base_r])
check("untouched RUNNING node stays out of changed/will_rerun",
      pv_r_same["changed"] == [] and pv_r_same["will_rerun"] == [], json.dumps(pv_r_same))

# ============================ issue #366 ============================
# The class that response named NOWHERE: a node RUNNING when amended, def-identical,
# and NOT downstream of anything edited. node_rec reads its spawn record as pending,
# so the restart/reload the amend triggers RESETS it and the solo branch never adopts
# the live child (only the fan-out `_spawn` calls active_child) — the child dies and
# the work re-runs from zero while the response reads "1 changed / 1 will rerun".
base_x = [agent("a", model="m-a", provider="p1"),
          agent("b", model="m-b", provider="p2"),          # independent root, RUNNING
          agent("c", ["b"])]
r3 = fresh("20991006-000002-amenddefdiff", base_x)
byid3 = {n["id"]: n for n in base_x}
(r3 / "nodes" / "a.json").write_text(json.dumps(
    {"status": "done", "efp": wfcommon.efp(byid3, byid3["a"]), "output": {"ok": True}}))
(r3 / "nodes" / "b.json").write_text(json.dumps(
    {"status": "running", "efp": wfcommon.efp(byid3, byid3["b"]), "pid": 999999,
     "spawn_cmd": ["fake"], "log_path": "logs/b.a1.log", "skey": "s", "attempt": 1}))

new_x = [dict(n) for n in base_x]
new_x[0] = {**new_x[0], "goal": "say hi twice"}            # edit lands on a, not on b
pv_x = wfcommon.amend_preview(r3, new_x)
check("#366 def-identical RUNNING node named in will_reset_running",
      pv_x["will_reset_running"] == ["b"], json.dumps(pv_x))
check("#366 naming the reset does not invent a rerun for it (#18 semantics hold)",
      pv_x["changed"] == ["a"] and pv_x["will_rerun"] == ["a"] and pv_x["unchanged"] == [],
      json.dumps(pv_x))

# a pure no-op amend still destroys the live child: the key must not be def-drift-only
pv_x_same = wfcommon.amend_preview(r3, [dict(n) for n in base_x])
check("#366 no-def-change amend still names the RUNNING node it resets",
      pv_x_same["changed"] == [] and pv_x_same["will_rerun"] == []
      and pv_x_same["will_reset_running"] == ["b"], json.dumps(pv_x_same))

# the #18 def-drift class reports BOTH facts: it re-runs (changed) and its child dies
pv_both = wfcommon.amend_preview(r2, [dict(n) if i != 1 else {**n, "model": "m-c", "provider": "p9"}
                                     for i, n in enumerate(base_r)])
check("#366 a def-edited RUNNING node lands in changed AND will_reset_running",
      "b" in pv_both["changed"] and pv_both["will_reset_running"] == ["b"], json.dumps(pv_both))

# guard: no spawn record in flight -> the key is empty (no phantom warnings)
check("#366 a run with nothing running names nothing",
      pv_same["will_reset_running"] == [] and pv_b["will_reset_running"] == [],
      json.dumps({"pv_same": pv_same, "pv_b": pv_b}))

print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS)} ({15 - len(FAILS)}/15)")
sys.exit(1 if FAILS else 0)
