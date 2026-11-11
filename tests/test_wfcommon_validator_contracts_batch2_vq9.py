"""est-y5yon: direct contract pins for the five wfcommon callables at ZERO direct test references
at shipped tip cb1fd1e (on_exit_errors, params_errors, quote_json_parse_error, model_names_valid,
budget_tokens); every expectation MEASURED against that tip; pointer here (AGENTS.md hint cap full); house shape per merged #620. Stdlib, serial."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/.."); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
OE_MSG = lambda m: [{"node": None, "field": "on_exit", "msg": m}]
REF, DEAD = OE_MSG("on_exit must be a non-empty agent node id"), OE_MSG("on_exit 'x' must name an existing agent node")
DEP = {"node": None, "field": "on_exit", "msg": "ordinary node 'n' cannot depend on on_exit 'x'"}
AG = {"id": "x", "type": "agent"}; OE = lambda *ns: W.on_exit_errors({"on_exit": "x", "nodes": [AG, *ns]}); JDE = 0
N = lambda ref: [{"goal": ref, "id": "n"}]; TP = lambda node: {"params": {"t": {"kind": "tune", "domain": ["a"]}}, "nodes": [node]}
P1 = lambda g, f, s: len(e := W.params_errors(g)) == 1 and e[0]["field"] == f and s in e[0]["msg"]
check("models: [] vacuous-True, ['m'] True; blank/int/str/None False",
      W.model_names_valid([]) and W.model_names_valid(["m"]) and not W.model_names_valid(["m", " "]) and not W.model_names_valid(["m", 5]) and not W.model_names_valid("m") and not W.model_names_valid(None))
check("budget: 0/sum-18/'7' coerced/1.9 truncates/junk collapses/non-counters ignored/None 0",
      W.budget_tokens({}) == 0 and W.budget_tokens({"tokens_in": 3, "tokens_out": 4, "cache_read": 5, "reasoning": 6}) == 18
      and W.budget_tokens({"tokens_in": "7"}) == 7 and W.budget_tokens({"tokens_in": 1.9}) == 1 and W.budget_tokens({"tokens_in": "x"}) == 0
      and W.budget_tokens({"cost_usd": 99, "tokens_out": 2}) == 2 and W.budget_tokens({"tokens_in": None}) == 0)
try: json.loads('{"a": }')
except json.JSONDecodeError as e: JDE = e
Q = lambda pos: type("X", (), {"pos": pos})(); T = "y" * 60 + "x" * 80 + "y" * 60
check("qjson: clamped-full / no-pos and bad-pos 80 / exact +/-40 window",
      W.quote_json_parse_error('{"a": }', JDE) == '{"a": }' and all(W.quote_json_parse_error("y" * 100, o) == "y" * 80 for o in (object(), Q(-1), Q(999)))
      and W.quote_json_parse_error(T, Q(100)) == T[60:140] == "x" * 80)
check("on_exit: pass/blank+int refuse; dead target/nodes-str/fan-out/result clash",
      W.on_exit_errors({}) == [] == OE() and all(W.on_exit_errors({"on_exit": r, "nodes": [AG]}) == REF for r in ("  ", 5))
      and all(W.on_exit_errors({"on_exit": "x", "nodes": ns}) == DEAD for ns in ([{"id": "y"}], [{"id": "x"}], "zz"))
      and all(W.on_exit_errors(g) == OE_MSG(m) for g, m in (({"on_exit": "x", "nodes": [dict(AG, fanout={})]}, "on_exit must name a single agent, not a fan-out"),
          ({"on_exit": "x", "result": "x", "nodes": [AG]}, "on_exit cannot also be the ordinary run result"))))
check("on_exit: every depend surface flags (twins len 2); out.-head segment quirk saved",
      all(OE({"id": "n", s: v}) == [DEP] for s, v in [("after", ["x"]), ("requires", {"x": "d"}), ("inputs", ["x.f"]), ("when", "out.x.flag"), ("on_fail", "x")])
      and OE({"id": "n", "fanout": {"items_from": "x.items"}}) == [DEP] and len(OE({"id": "n", "after": ["x"]}, {"id": "m", "inputs": ["x.f"]})) == 2
      and OE({"id": "n", "inputs": ["out.x.answer"]}) == [])
check("params: absent/non-dict []; co-decl ordered-then-empty; {} refuse; totality pair at exact field params",
      W.params_errors({}) == [] == W.params_errors(5) and len(c := W.params_errors({"params": {}, "run_context": {}})) == 2 and all(x["field"] == "params" for x in c) and "one contract per graph" in c[0]["msg"]
      and c[1] == {"node": None, "field": "params", "msg": "params must be a non-empty object of slot -> declaration"}
      and len(t := W.params_errors({"params": {"p": {"kind": "pin"}}, "nodes": N("{run.q}")})) == 2 and all(x["field"] == "params" for x in t)
      and "bind what you declare" in t[0]["msg"] and "['p']" in t[0]["msg"] and "declare every binding the nodes consume" in t[1]["msg"] and "['q']" in t[1]["msg"])
check("params: declaration grammar (graphs balanced — the contract is TOTAL both ways)",
      all(P1(g, f, m) for g, f, m in [
          ({"params": {"a-b": {"kind": "pin"}}}, "params.a-b", "invalid slot name 'a-b': expected identifier"),
          ({"params": {"p": {"kind": "pin", "default": "d"}}, "nodes": N("{run.p}")}, "params.p", "pin slots carry run content: no default, no domain — a knob belongs in a tune slot"),
          ({"params": {"t": {"kind": "tune", "domain": ["a"], "default": "z"}}, "nodes": N("{run.t}")}, "params.t.default", "default 'z' is outside the domain ['a']"),
          ({"params": {"t": {"kind": "tune", "domain": ["a"], "zz": 1}}, "nodes": N("{run.t}")}, "params.t.zz", "unknown key; allowed: ['default', 'desc', 'domain', 'kind']")])
      and all(P1({"params": {"t": {"kind": "tune", "domain": d}}, "nodes": N("{run.t}")}, "params.t.domain", "tune needs a domain: non-empty list of distinct non-empty strings") for d in (None, [], ["a", "a"])))
check("params: gates fold into referenced; pin-gate, dead-domain branch, by-shape and patch-key refusals",
      W.params_errors({"params": {"t": {"kind": "tune", "domain": ["a"]}}, "nodes": [{"id": "n", "goal": "g", "where": {"param": "t", "in": ["a"]}}]}) == []
      and P1({"params": {"p": {"kind": "pin"}}, "nodes": [{"id": "n", "where": {"param": "p", "in": ["a"]}}]}, "nodes.n.where.param", "slot 'p' is a pin — where/by gate on tune slots only")
      and P1(TP({"id": "n", "where": {"param": "t", "in": ["z"]}}), "nodes.n.where.in", "value(s) ['z'] outside the domain — a presence gate can never fire nor pass as written")
      and P1(TP({"id": "n", "goal": "{run.t}", "by": {}}), "nodes.n.by", "by must be a non-empty object slot -> case -> patch")
      and P1(TP({"id": "n", "by": {"t": {"z": {"goal": "g"}}}}), "nodes.n.by.t.z", "case outside the domain — a patch that can never apply is a typo")
      and P1(TP({"id": "n", "by": {"t": {"a": {"zz": 1}}}}), "nodes.n.by.t.a.zz", "patch key not allowed on agent nodes"))
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
