"""est-2tm8s: contract pins for the five wfcommon validators with ZERO direct test
references at tip b5988cd (nightly sweep-c); every expectation measured against the
shipped tip; pointer here (AGENTS.md has no hint headroom). Stdlib, serial."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import wfcommon as W

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

# grammar_errors: absent/known/non-dict -> []; any other value -> ONE fail-closed typed refusal
check("grammar: pass/non-dict/wf2-verbatim/non-string",
      W.grammar_errors({}) == [] == W.grammar_errors({"grammar": "wf/1"}) == W.grammar_errors(["wf/2"])
      and W.grammar_errors({"grammar": "wf/2"}) == [{"node": None, "field": "grammar",
          "msg": "unsupported grammar 'wf/2'; this reader supports: [\"wf/1\"] (absent = 'wf/1')"}]
      and len(W.grammar_errors({"grammar": 2})) == 1)
# budget_shape_errors: tokens-only object; the usd shape names the law ONCE, never stacked
check("budget: ok/non-dict/usd-single/empty/0,'500',True",
      W.budget_shape_errors({"tokens": 200000}, "root") == []
      and W.budget_shape_errors(5, "nodes.a") == ['budget at nodes.a must be an object like {"tokens": 200000}']
      and len(u := W.budget_shape_errors({"usd": 5}, "root")) == 1 and u[0].startswith("budget.usd at root unknown")
      and W.budget_shape_errors({}, "root") == ["budget at root must carry a positive integer tokens cap"]
      and all(any("positive integer" in m for m in W.budget_shape_errors({"tokens": v}, "root")) for v in (0, "500", True)))
# model_policy_errors: closed keys, typed values (PR#84 F-2: an OR-coerced require_model
# 'false' became True and passed — the string form must refuse)
check("policy: pass/non-dict/unknown-sorted/bool+list",
      W.model_policy_errors({}) == [] and W.model_policy_errors({"require_model": True, "forbidden_models": ["m1"]}) == []
      and W.model_policy_errors(5) == ["model_policy: model_policy must be an object"]
      and W.model_policy_errors({"zzz": 1, "prefer": 2}) == ["model_policy.prefer: unknown policy key", "model_policy.zzz: unknown policy key"]
      and W.model_policy_errors({"require_model": "false"}) == ["model_policy.require_model: require_model must be boolean"]
      and W.model_policy_errors({"forbidden_models": ["m1", "  "]})
          == ["model_policy.forbidden_models: forbidden_models must be a list of non-empty strings"])
# fingerprint_valid: OWN stamp authoritative (int, in FP_RULES); unstamped records match
# under ANY rule — fail-closed is ZERO matches
A = lambda rule: {1: "aaa", 2: "bbb"}[rule]
check("fingerprint: stamped m/M/99/'1'; unstamped 1-ok 0-None-closed",
      W.fingerprint_valid("aaa", A, 1) and not W.fingerprint_valid("aaa", A, 2)
      and not W.fingerprint_valid("aaa", A, 99) and not W.fingerprint_valid("aaa", A, "1")
      and W.fingerprint_valid("bbb", A, None) and not W.fingerprint_valid("zzz", A, None)
      and not W.fingerprint_valid(None, A, None))
# dead_end_forks: a done/partial node with >=2 consumers is dead only when EVERY edge ends
# terminal-skipped; an on_fail skip record means the edge WAS taken; a lone consumer never forks.
N = [{"id": "f"}, {"id": "c1", "after": ["f"]}, {"id": "c2", "after": ["f"]}]; S = {"f": "done", "c1": "skipped", "c2": "skipped"}
check("forks: all-skipped named; live/on_fail/lone-tail saved; other value/None dead",
      W.dead_end_forks(N, S) == ["f"] == W.dead_end_forks(N, dict(S, f="partial"))
      and W.dead_end_forks(N, dict(S, c2="done")) == []
      and W.dead_end_forks(N, S, lambda i: {"output": {"skipped": "on_fail"}} if i == "c1" else {}) == []
      and W.dead_end_forks(N, S, lambda i: {"output": {"skipped": "gate_hold"}}) == ["f"]
      and W.dead_end_forks(N[:2], {"f": "done", "c1": "skipped"}) == []
      and W.dead_end_forks(N, S, lambda i: None) == ["f"])
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
