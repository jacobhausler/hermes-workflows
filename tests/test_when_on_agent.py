"""when + on_skip ON AGENT NODES (issue #132, jam-h26): the gate-as-branch rejection
is retired. An agent node takes the SAME bounded `when` grammar as a gate
(when_expr_ok / when_true / prune_states UNCHANGED) and the SAME on_skip enum —
false predicate + prune (default) = terminal skip with zero spawns, honored by the
runner slice merged in the same plan. The fail-closed refusals carry over verbatim:
a malformed when is refused at the door naming node+field; a non-ancestor when head
(sibling, ghost, self) is refused exactly like a gate's; on_skip without when is
refused; a bad enum is refused. Echo/join keep rejecting BOTH keys through their
closed key sets (acceptance (b)); the gate look-alike misuse errors (agent.wait,
gate.inputs, join.keys) are unchanged. Validator only — no spawn, no network.

Pattern: tests/test_when_ancestry_0930.py (validate_graph_errors + check()).
"""
import os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
os.environ.setdefault("HERMES_HOME", str(HERE / ".suite-home"))
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

V = wfcommon.validate_graph_errors
fails = []
def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + (f"  << {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(msg)

def agent(id, after=(), **extra):
    n = {"id": id, "type": "agent", "after": list(after), "goal": "x"}
    n.update(extra)
    return n

# 1. agent + valid when (direct after head) accepted — validate_graph_errors returns []
ok = [agent("a"), agent("b", ["a"], when="out.a.verdict == 'go'")]
errs = V(ok)
check(errs in ([], None), "agent + valid when accepted", str(errs))

# 2. agent + valid when + on_skip prune / pass accepted
os_prune = [agent("a"), agent("b", ["a"], when="out.a.verdict == 'go'", on_skip="prune")]
os_pass = [agent("a"), agent("b", ["a"], when="out.a.verdict == 'go'", on_skip="pass")]
check(V(os_prune) in ([], None), "agent + when + on_skip:prune accepted", str(V(os_prune)))
check(V(os_pass) in ([], None), "agent + when + on_skip:pass accepted", str(V(os_pass)))

# 3. malformed when on an agent is refused naming node + field (same parser error as a gate)
bad = [agent("a"), agent("b", ["a"], when="garbage =")]
errs = V(bad)
check(any(e["node"] == "b" and e["field"] == "when" for e in errs),
      "malformed agent when refused naming node+field", str(errs))
check(any(e["field"] == "when" and e["msg"] == wfcommon.when_expr_ok("garbage =")
          for e in errs),
      "agent when reports the when_expr_ok syntax error verbatim", str(errs))

# 4. non-ancestor when head on an agent: PARALLEL SIBLING refused (the ancestry law
#    that gates already enforce extends to agents unchanged).
sib = [agent("producer_a"), agent("producer_b"),
       agent("branch", ["producer_a"], when="out.producer_b.verdict == 'go'")]
errs = V(sib)
check(any(e["node"] == "branch" and e["field"] == "when" and "ancestry" in e["msg"]
          for e in errs),
      "non-ancestor (sibling) when-head refused on an agent", str(errs))

# 5. ghost head (nonexistent node) refused on an agent
ghost = [agent("a"), agent("b", ["a"], when="out.nonexistent.zzz == 1")]
errs = V(ghost)
check(any(e["node"] == "b" and e["field"] == "when" for e in errs),
      "nonexistent agent when-head refused at submit", str(errs))

# 6. self-reference is not a strict ancestor (mirrors the gate rule)
self_ref = [agent("a", when="out.a.ok == True")]
errs = V(self_ref)
check(any(e["node"] == "a" and e["field"] == "when" for e in errs),
      "self-referencing agent when-head refused at submit", str(errs))

# 7. transitive ancestor head accepted (ancestry closure, not just direct after)
trans = [agent("a"), agent("b", ["a"]), agent("c", ["b"], when="out.a.verdict == 'go'")]
check(V(trans) in ([], None), "transitive-ancestor agent when-head accepted", str(V(trans)))

# 8. multiple heads in one expr: the bad one named, the good one not flagged
multi = [agent("a"), agent("sib"), agent("b", ["a"],
               when="out.a.ok == True or out.sib.ok == True")]
errs = V(multi)
check(len(errs) == 1 and errs[0]["node"] == "b" and errs[0]["field"] == "when"
      and "sib" in errs[0]["msg"],
      "multi-head agent when names only the offending ref", str(errs))

# 9. on_skip without when refused on an agent (same law as gates)
osk_nowhen = [agent("a"), agent("b", ["a"], on_skip="prune")]
errs = V(osk_nowhen)
check(any(e["node"] == "b" and e["field"] == "on_skip" and "needs a `when`" in e["msg"]
          for e in errs),
      "on_skip without when refused on an agent", str(errs))

# 10. on_skip bad enum refused on an agent (when present)
osk_bad = [agent("a"), agent("b", ["a"], when="out.a.ok", on_skip="nope")]
errs = V(osk_bad)
check(any(e["node"] == "b" and e["field"] == "on_skip"
          and "allowed: ['pass', 'prune']" in e["msg"] for e in errs),
      "on_skip bad enum refused on an agent", str(errs))

# 11. acceptance (b): echo/join keep rejecting both keys via their closed sets
echo_when = [{"id": "e", "type": "echo", "after": [], "output": {}, "when": "out.x.ok"}]
errs = V(echo_when)
check(any(e["field"] == "when" and "unknown key" in e["msg"] for e in errs),
      "echo + when still 'unknown key'", str(errs))
echo_osk = [{"id": "e", "type": "echo", "after": [], "output": {}, "on_skip": "prune"}]
errs = V(echo_osk)
check(any(e["field"] == "on_skip" and "unknown key" in e["msg"] for e in errs),
      "echo + on_skip still 'unknown key'", str(errs))
join_when = [agent("a"), {"id": "j", "type": "join", "after": ["a"],
                         "keys": {"x": "a.ok"}, "when": "out.a.ok"}]
errs = V(join_when)
check(any(e["node"] == "j" and e["field"] == "when" and "unknown key" in e["msg"]
          for e in errs),
      "join + when still 'unknown key'", str(errs))
join_osk = [agent("a"), {"id": "j", "type": "join", "after": ["a"],
                        "keys": {"x": "a.ok"}, "on_skip": "prune"}]
errs = V(join_osk)
check(any(e["node"] == "j" and e["field"] == "on_skip" and "unknown key" in e["msg"]
          for e in errs),
      "join + on_skip still 'unknown key'", str(errs))

# 12. gate look-alike misuse errors UNCHANGED
w_errs = V([agent("a", wait={"wait_s": 1})])
check(any(e["field"] == "wait" and "only gate nodes take wait" in e["msg"]
          for e in w_errs),
      "agent + wait still 'only gate nodes take wait'", str(w_errs))
gin_nodes = [agent("a"), {"id": "g", "type": "gate", "after": ["a"],
                          "question": "q", "inputs": ["a.x"]}]
gin_errs = V(gin_nodes)
check(any(e["field"] == "inputs" and "gates cannot have inputs" in e["msg"]
          for e in gin_errs),
      "gate + inputs misuse error unchanged", str(gin_errs))

# 13. gate paths untouched: the same grammar accepts/refuses gates exactly as before
gate_ok = [agent("a"), {"id": "g", "type": "gate", "after": ["a"], "question": "q",
                        "when": "out.a.verdict == 'go'", "on_skip": "prune"}]
check(V(gate_ok) in ([], None), "gate + when + on_skip unchanged (accepted)", str(V(gate_ok)))
gate_bad = [agent("a"), {"id": "g", "type": "gate", "after": ["a"], "question": "q",
                         "when": "garbage ="}]
errs = V(gate_bad)
check(any(e["node"] == "g" and e["field"] == "when"
          and e["msg"] == wfcommon.when_expr_ok("garbage =") for e in errs),
      "gate malformed when unchanged (syntax error verbatim)", str(errs))

# 14. a non-str `when` is refused by NAME on both types, never a validator crash
for t, node in (("agent", agent("a", when=123)),
                ("gate", {"id": "g", "type": "gate", "after": [], "question": "q", "when": 123})):
    try:
        errs = V([agent("x"), node] if t == "agent" else [agent("x"), node])
    except Exception as e:
        check(False, f"non-str when refused by name on a {t} (no crash)", f"{type(e).__name__}: {e}")
        continue
    check(any(e["field"] == "when" and "string" in e["msg"] for e in errs),
          f"non-str when refused by name on a {t}", str(errs))

# 15. when/on_skip never ride graph-level defaults (closed DEFAULTS_KEYS untouched)
import wfcommon as _w
check("when" not in _w.DEFAULTS_KEYS and "on_skip" not in _w.DEFAULTS_KEYS,
      "defaults stays closed against when/on_skip", str(sorted(_w.DEFAULTS_KEYS)))

# 16. the js-dialect exporter never SILENTLY drops an agent `when`: their runtime has
#     no bounded branch, so the export would run an arm the graph skips — REFUSED by
#     name (any on_skip: a `pass` agent still never spawns), mirroring the prune gate.
import wf_dialect  # noqa: E402
for osk in (None, "prune", "pass"):
    b = agent("b", ["a"], when="out.a.verdict == 'go'")
    if osk:
        b["on_skip"] = osk
    rep = wf_dialect.export_report({"name": "t", "nodes": [agent("a"), b]})
    check(rep.get("ok") is False and rep.get("node") == "b" and "when" in rep.get("refuse", ""),
          f"js export refuses an agent when (on_skip={osk})", str(rep)[:300])

print(f"\nRESULT: {'ALL PASS' if not fails else str(len(fails)) + ' FAIL'}")
raise SystemExit(1 if fails else 0)
