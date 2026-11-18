"""est-4v1fi sweep-c: batch-8 direct contract pins for the when-expression parser family (_when_or/_when_and/_when_not/_when_cmp/_when_atom + when_expr_ok) — at tip a1383ff the five _when_* fns had ZERO direct test references and when_expr_ok appeared only as an oracle, never as pinned contract. Pins: precedence (or<and<not<cmp<atom), paren grouping, every literal form in _when_atom value mode, out-path resolution, the RAW TypeError propagating out of _when_cmp, and the when_expr_ok _SYNTAX-mode polarity — well-formed returns None (falsy) and malformed a truthy error str carrying the grammar pointer (POLARITY CORRECTION vs the wake line; callers do `err = when_expr_ok(w); if err:`, and test_engine_next_cut.py:105 assertIsNone agrees). WHY the pins run the raw fns: when_true itself does NOT catch the TypeError — the lazy one-op dispatch comment at wfcommon.py:5035-5037 is the why, and the fail-safe HOLD lives at the call site (wf.py:11610-11612, `_cond = True`, 'a broken when fails safe: held') — so the raw fn is the contract; pointer lives here because AGENTS.md sits at the hint-cap (test_docs_hint_cap_73c.py makes any addition born-red), batch-7 precedent; house shape per merged #620/#624/#635/#639/#640/#641/#645. Stdlib, serial, auto-discovered by scripts/suite.py; zero production lines touched."""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "..")); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def ev(expr, outs): return W._when_or(W._tok_when(expr), 0, outs)
def err(expr): return W.when_expr_ok(expr) or ""
def exc(fn):
    try: fn(); return ""
    except BaseException as e: return type(e).__name__
def AT(t): return W._when_atom([t], 0, {})
OPS = {"a": {"b": 7}, "xs": [10, 20], "n": 1}
check("precedence or<and<not<cmp<atom: 'not out.a == 1' with a=1 is False (cmp binds tighter than not — if not bound tighter this would be (not 1) == 1 -> False == 1 -> True); 'out.a == 1 or out.b == 2 and out.c == 3' is True with (a,b,c)=(5,2,3) and False with (9,2,9) (and binds tighter than or); each eval consumed every token (pos leg pins that)",
      ev("not out.a == 1", {"a": 1}) == (False, 4)
      and ev("out.a == 1 or out.b == 2 and out.c == 3", {"a": 5, "b": 2, "c": 3}) == (True, 11)
      and ev("out.a == 1 or out.b == 2 and out.c == 3", {"a": 9, "b": 2, "c": 9}) == (False, 11))
check("paren grouping overrides precedence: '(out.a == 1 or out.b == 2) and out.c == 3' with (1,9,9) is False (the parens force the or inside the and), while the same expression unparenthesized — 'out.a == 1 or out.b == 2 and out.c == 3' — is True on the same outputs",
      ev("(out.a == 1 or out.b == 2) and out.c == 3", {"a": 1, "b": 9, "c": 9}) == (False, 13)
      and ev("out.a == 1 or out.b == 2 and out.c == 3", {"a": 1, "b": 9, "c": 9}) == (True, 11))
check("_when_atom value-mode literal forms: quoted strings decode via unicode_escape ('\\u00a9' -> the copyright char, \"\\u00e9\" -> e-acute); the two-char source '' is an EMPTY STRING LITERAL yielding '' (not the empty expression); int vs float is decided by a dot: '42' -> int 42, '4.25' -> float 4.25, '-3' -> -3; True/False/None -> True/False/None and lowercase true/false -> True/False",
      AT("'\\u00a9'") == ("\u00a9", 1) and AT('"\\u00e9"') == ("\u00e9", 1) and AT("''") == ("", 1)
      and type(AT("42")[0]) is int and AT("42")[0] == 42
      and type(AT("4.25")[0]) is float and AT("4.25")[0] == 4.25
      and AT("-3") == (-3, 1)
      and (AT("True")[0], AT("False")[0], AT("None")[0]) == (True, False, None)
      and AT("true")[0] is True and AT("false")[0] is False)
check("out-path resolution in _when_atom: a dotted dict path hits (out.a.b -> 7), a list indexes by digits (out.xs.1 -> 20), and a missing dict path, an out-of-range list index, and a descent through a scalar all yield None — never a KeyError or IndexError",
      W._when_atom(W._tok_when("out.a.b"), 0, OPS)[0] == 7
      and W._when_atom(W._tok_when("out.xs.1"), 0, OPS)[0] == 20
      and W._when_atom(W._tok_when("out.a.zz"), 0, OPS)[0] is None
      and W._when_atom(W._tok_when("out.xs.9"), 0, OPS)[0] is None
      and W._when_atom(W._tok_when("out.n.deeper"), 0, OPS)[0] is None)
check("mismatched cmp operands PROPAGATE a raw TypeError out of _when_cmp (pin the TYPE, not the message — measured: \"'>' not supported between instances of 'str' and 'int'\"): 'out.a > 1' with outputs {'a': 'x'} raises at every level — _when_cmp direct, the _when_or entry, and when_true (which does NOT catch; the HOLD lives at the wf.py call site, see docstring)",
      exc(lambda: ev("out.a > 1", {"a": "x"})) == "TypeError"
      and exc(lambda: W._when_cmp(W._tok_when("out.a > 1"), 0, {"a": "x"})) == "TypeError"
      and exc(lambda: W.when_true({"when": "out.a > 1"}, {"a": "x"})) == "TypeError")
check("when_expr_ok polarity + _SYNTAX sentinel mode: well-formed returns None (falsy) — and syntax mode is VALUE-TOTAL, so a value-TypeError-prone cmp 'out.a > \"x\"' is still None (every atom a sentinel); malformed returns a truthy error str carrying the grammar pointer: '   ' and '' -> 'empty when expression'; 'out.a ==' -> 'unexpected end of expression'; '(out.a == 1' -> 'missing )'; \"out.a @ 1\" -> \"bad char '@' at 6\"; bare 'garbage' -> \"unexpected token 'garbage'\"",
      W.when_expr_ok('out.a > "x"') is None and W.when_expr_ok("out.a == 1 and out.b != 'x'") is None
      and "empty when expression" in err("   ") and "empty when expression" in err("")
      and "unexpected end of expression" in err("out.a ==")
      and "missing )" in err("(out.a == 1")
      and "bad char '@' at 6" in err("out.a @ 1")
      and "unexpected token 'garbage'" in err("garbage")
      and all("grammar: out.<node>" in err(x) for x in ("", "garbage", "out.a @ 1")))
check("trailing-token rejection names the offending token: 'out.a == 1 2' -> error naming '2'; '(out.a == 1) out.b == 2' -> error naming 'out.b' (when_expr_ok's unconsumed-pos leg); via when_true the same shape raises ValueError('when: trailing tokens') into the fail-safe hold",
      "unexpected token '2'" in err("out.a == 1 2")
      and "unexpected token 'out.b'" in err("(out.a == 1) out.b == 2")
      and exc(lambda: W.when_true({"when": "out.a == 1 2"}, {"a": 1})) == "ValueError")
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
