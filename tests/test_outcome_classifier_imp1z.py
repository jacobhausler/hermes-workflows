#!/usr/bin/env python3
"""est-imp1z (WF-GRAFT-2) — exit-0-is-not-success: the PURE output classifier.

Evidence (bead + audit est-ll0nn, iw-recon hermes_workflows/executor/outcome.py:33-131):
the agent CLI exits 0 even when its LLM call exhausted retries on a transient
provider error — it prints `API call failed after N retries: HTTP 429 …` as its
final message and returns cleanly. wf.py's harvest-once coercion
(extract_json -> {result: prose}) then launders that text into a schema-valid
`done`: the graph advances on garbage.

The law this pin enforces (bead acceptance, authority order FIXED):
    node_outcome token  >  transient sentinels  >  exit code
- the classifier is PURE: (returncode, output, token) in, one Verdict out, no I/O;
- sentinels are LINE-SCOPED so prose cannot trip them (a node mentioning
  "429 lines" or "HTTP-429 handling" stays success);
- the TAIL token wins over earlier tokens (the agent's final declaration rules);
- Verdict.kind ∈ {success, transient, deterministic}; kind=transient is the ONLY
  kind allowed to feed the bounded transient retry ladder (mapped to
  error_class `transport`, the ladder's gate class); a token-declared failure is
  deterministic — terminal, in NEITHER ladder.

Run: python3 tests/test_outcome_classifier_imp1z.py
"""
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402  — the runner binds outcome.py privately as wf._outcome (spec-load)

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

oc = getattr(wf, "_outcome", None)
check("the runner binds the classifier module (wf._outcome)", oc is not None,
      "wf._outcome missing — outcome.py not spec-loaded")
if oc is None:
    print("RED: no classifier bound; every downstream check would crash — stopping.")
    raise SystemExit(1)

# ---------- signature law: classify(returncode, output, token) ----------
params = list(inspect.signature(oc.classify).parameters)
check("classify(returncode, output, token) — the acceptance signature",
      params[:3] == ["returncode", "output", "token"], str(params))

# ---------- the table (bead: >=5 rows; every row a full Verdict pin) ----------
LIE = "API call failed after 3 retries: HTTP 429 Too Many Requests"
TABLE = [
    # (label, returncode, output, token, expected (outcome, kind, detail))
    ("token-over-exit-0-failure",
     0, "Work done, committed at abc1234, tests green.\n", "failure",
     ("failure", "deterministic", None)),
    ("token-over-transient-success",
     0, LIE + "\nrecovered on the last turn and the work landed\n", "success",
     ("success", "success", None)),
    ("sentinel-on-exit-0",
     0, LIE + "\n", None,
     ("failure", "transient", LIE)),
    ("prose-mention-does-not-trip",
     0, "The log names 429 lines of output and mentions HTTP-429 handling twice.\n", None,
     ("success", "success", None)),
    ("exit-code-fallback-success",
     0, "quiet deterministic work, banked at refs/heads/fix\n", None,
     ("success", "success", None)),
    ("exit-code-fallback-failure",
     1, "a deterministic grief with no machine sentinel line\n", None,
     ("failure", "deterministic", None)),
    ("sentinel-beats-nonzero-exit",
     1, "HTTP 503 Service Unavailable\n", None,
     ("failure", "transient", "HTTP 503 Service Unavailable")),
    ("overloaded-sentinel-on-exit-0",
     0, "Provider said: temporarily overloaded, try again later.\n", None,
     ("failure", "transient", "Provider said: temporarily overloaded, try again later.")),
]
for label, rc, out, tok, want in TABLE:
    v = oc.classify(rc, out, token=tok)
    got = (v.get("outcome"), v.get("kind"), v.get("detail"))
    check(f"classify row: {label}", got == want, f"got {got} want {want}")

# ---------- tail token wins (parse law, then authority through the full gate) ----------
dual = ('mid-run {"node_outcome": "failure"}\n'
        'final answer here\n'
        '{"node_outcome": "success"}\n')
check("parse_node_outcome: the TAIL token wins over earlier tokens",
      oc.parse_node_outcome(dual) == "success", str(oc.parse_node_outcome(dual)))
v = oc.classify(0, dual, oc.parse_node_outcome(dual))
check("classify: tail-success token outranks both the mid-run failure token and the exit code",
      (v.get("outcome"), v.get("kind")) == ("success", "success"), str(v))
check("parse_node_outcome: prose-shaped mentions do not parse as tokens",
      oc.parse_node_outcome('He wrote: node_outcome: success (no braces, no quotes)\n') is None)
check("parse_node_outcome: empty capture parses to None", oc.parse_node_outcome("") is None)

# ---------- Verdict domain law ----------
check("Verdict domain: outcome ∈ {success, failure} and kind ∈ {success, transient, deterministic}",
      all(oc.classify(rc, o, token=t).get("outcome") in ("success", "failure")
          and oc.classify(rc, o, token=t).get("kind") in ("success", "transient", "deterministic")
          for rc, o, t in [(0, "", None), (1, "", None), (7, LIE, None), (0, "", "failure")]))

# ---------- ladder law: kind=transient feeds ONLY the transient ladder ----------
check("declared_failure is a member of the closed ERROR_CLASSES set",
      "declared_failure" in wf.ERROR_CLASSES)
check("declared_failure (token-declared deterministic death) is in NEITHER ladder",
      "declared_failure" not in wf._RETRYABLE_CLASSES
      and "declared_failure" not in wf._BOUNDED_RETRY_CLASSES)
check("transport (the transient-kind hand-off class) stays the transient ladder's gate class",
      "transport" in wf._RETRYABLE_CLASSES)

# ---------- prompt contract: the build-shape preamble mirrors the token grammar ----------
pre = wf._outcome_token_preamble({"id": "x", "shape": "build"})
check("build-shape spawn carries the node-outcome token contract",
      wf.OUTCOME_TOKEN_PREAMBLE_TOKEN in pre
      and '{"node_outcome": "success"}' in pre and '{"node_outcome": "failure"}' in pre,
      pre[:120])
check("undeclared shape pays ZERO token-contract bytes (golden prompt law)",
      wf._outcome_token_preamble({"id": "x"}) == "")

print("OVERALL", "GREEN" if ok else "RED")
raise SystemExit(0 if ok else 1)
