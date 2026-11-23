#!/usr/bin/env python3
"""The #641 re-drive guard must speak the door's FULL alias vocabulary.

At admission the door resolves a node's bare model name through (in order) the
seat's `model.aliases` — read at the NODE's profile home for a `profile:`-routed
node — then the tiers, then core's built-in `DIRECT_ALIASES` table
(`wfcommon.alias_provider_pair`), and bakes what it proved alive into the run's
receipt. The re-drive guard `_route_substitution_refusal` expanded candidates
through the seat alias map ONLY — and read that map at the RUNNER's own home.
Two gates, two vocabularies: a profile-routed node whose alias lives in the
profile's seat got a receipt naming the resolved TARGET, then died typed
`route_substitution_denied` on EVERY re-drive (the denial is terminal, so the
node can never retry). The core-table leg is the same drift one layer deeper:
whatever the door's resolver can produce, the guard must consult the SAME
resolver — never a private subset (ONE judgment).

Law pinned here:
  A1  direct guard call, core-table alias: a receipt naming the resolver's
      target, node asking the alias -> NOT refused (vocabulary consistency).
  A2  the same spawn end-to-end through run_child (recording seat stub):
      respawn completes, the alias bills again, no route_substitution_denied.
  D   the reachable production shape, RED on base: a `profile:`-routed node
      (no provider) whose alias lives in the PROFILE's config.yaml; the receipt
      names the resolved target; base reads the runner's (empty) home and
      DENIES — the fix reads the node's profile home and accepts.
  B   green before AND after — the guard is not neutered: a receipt vs a model
      no alias resolves to stays DENIED with zero billing (full-route ledger
      count, the way test_route_substitution_641.py:90 counts).
  E   green before AND after — the widening cannot self-certify: an alias that
      DOES resolve, but to a target different from the receipt, stays DENIED.
  C   green before AND after — the literal verified TARGET ask still passes
      (the #25 identity law unchanged).

Harness: the repo's own in-process harness (tests/test_alias_receipt_respawn_318.py
shape, scrub-safe placeholders, no network). The RUNNER seat is deliberately
empty (fresh HERMES_HOME) so every alias under test comes from the profile seat
or the core table. The seat-config path at the runner's own home stays pinned by
test_alias_receipt_respawn_318.py.

Run:  python3 tests/test_route_substitution_core_alias.py   (from the repo root)
"""
import json, os, shutil, sys, tempfile, threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from hermes_cli.model_switch import DIRECT_ALIASES, _ensure_direct_aliases, DirectAlias
except ImportError:
    print("SKIP hermes_cli.model_switch is not importable in this environment")
    raise SystemExit(0)

import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " + label + ("  " + str(detail)[:400] if detail else "")))
    ok = ok and bool(cond)

HOME = Path(tempfile.mkdtemp(prefix="wf-corealias-"))
RUNS = HOME / "runs"
RUN = RUNS / "rcalias"
(RUN / "nodes").mkdir(parents=True)
(RUN / "gates").mkdir()

# The recording seat stub: every spawn appends the -m/--provider it billed.
STUB = HOME / "hermes_stub.py"
STUB.write_text(
    "#!/usr/bin/env python3\n"
    "import sys, os\n"
    "a = sys.argv[1:]\n"
    "m = a[a.index('-m') + 1] if '-m' in a else 'seat-default'\n"
    "p = a[a.index('--provider') + 1] if '--provider' in a else ''\n"
    "prof = a[a.index('-p') + 1] if '-p' in a else ''\n"
    "# #709: -m/--provider strip at the funnel; a profile-routed child bills @<profile>\n"
    "with open(os.environ['HERMES_WF_LEDGER'], 'a') as f:\n"
    "    f.write(p + '/' + m + ('@' + prof if prof else '') + '\\n')\n"
    "print('```json\\n{\"result\": \"ok\"}\\n```')\n"
)
STUB.chmod(0o755)
LEDGER = HOME / "attempts.ledger"

os.environ["HERMES_WF_LEDGER"] = str(LEDGER)   # HERMES_WF_ prefix survives the profile-spawn env scrub
os.environ["HERMES_HOME"] = str(HOME)          # empty RUNNER seat
os.environ["WF_RUNS_ROOT"] = str(RUNS)

ALIAS, TARGET = "bigseat", "example-provider/example-model-1"

def attempts_for(route):
    try:
        return LEDGER.read_text().splitlines().count(route)
    except OSError:
        return 0

# ---- setup: empty runner seat; one core-table alias; one PROFILE seat alias --
check("setup: the runner seat alias map is empty",
      wf._seat_alias_map(HOME) == {}, wf._seat_alias_map(HOME))
DIRECT_ALIASES[ALIAS] = DirectAlias(model="example-model-1", provider="example-provider",
                                    base_url="https://example.invalid/v1")
DIRECT_ALIASES["bigseat2"] = DirectAlias(model="other-model-9", provider="example-provider",
                                         base_url="https://example.invalid/v1")
_ensure_direct_aliases()   # preserves caller-seeded entries (core's own docstring)
check("setup: DIRECT_ALIASES keeps caller-seeded entries across _ensure_direct_aliases",
      DIRECT_ALIASES.get(ALIAS) is not None
      and DIRECT_ALIASES.get("bigseat2") is not None, DIRECT_ALIASES.get(ALIAS))

# A PROFILE seat that owns an alias: profiles/alt/config.yaml under the fresh
# HERMES_HOME (the door reads this home at admission for profile-routed nodes).
ALT = HOME / "profiles" / "alt"
ALT.mkdir(parents=True)
(ALT / "config.yaml").write_text(
    "model:\n"
    "  aliases:\n"
    "    bigseat: example-provider/example-model-1\n")
check("setup: the profile seat map reads the alias",
      wf._seat_alias_map(ALT) == {"bigseat": "example-provider/example-model-1"},
      wf._seat_alias_map(ALT))

# The door's bake: proved-alive receipts naming the RESOLVED TARGET.
(RUN / "route_receipts.json").write_text(json.dumps({"work": TARGET, "workp": TARGET}))
node = {"id": "work", "type": "agent", "goal": "do the work",
        "provider": "example-provider", "model": ALIAS,
        "require_route": False}   # #709: the alias pair strips at the funnel; the
                                  # guard below polices the DEF, the child bills seat-default
d_node = {"id": "workp", "type": "agent", "goal": "do the work",
          "model": ALIAS, "profile": "alt"}
(RUN / "graph.json").write_text(json.dumps({"name": "rcalias", "nodes": [node, d_node]}))
meta = {"_run": RUN, "hermes_bin": str(STUB), "_spawn_n": {},
        "_procs_lock": threading.Lock(), "_procs": {},
        "_stop": threading.Event(), "node_timeout": 15}

# ---- A1: direct guard call, core-direct alias vs its own receipt ------------
ref = wf._route_substitution_refusal(meta, node, 1)
check("A1 receipt for the core-direct-alias TARGET, node asks the alias: NOT refused",
      ref is None, ref)

# ---- A2: the same re-drive end-to-end through run_child ----------------------
r1 = wf.run_child(meta, node, {"work": node}, "do the work", "", None,
                  skey="wf:rcalias:work#2")
check("A2 core-direct-alias respawn runs to done, no typed denial",
      r1.get("status") == "done" and r1.get("error_class") != "route_substitution_denied",
      r1)
# #709: the alias never rides the child argv on a strip host — the stub bills
# the seat default it served; the alias-resolution contract lives in the door's
# guard (A1/D1/B/C/E judge the DEF, never argv).
check("A2 the alias spawn billed again (seat-default served; door still resolves the DEF)",
      attempts_for("/seat-default") == 1,
      LEDGER.read_text() if LEDGER.exists() else "<no ledger>")

# ---- D (RED on base): profile-routed node, alias lives in the PROFILE seat ---
# The reachable production shape: node carries `profile: alt` and a bare alias
# (no provider); the door resolved it through the profile seat and baked the
# target. Base reads the runner's empty home -> permanent terminal denial.
refd = wf._route_substitution_refusal(meta, d_node, 4)
check("D1 profile-seat alias vs its own receipt: NOT refused — RED on base",
      refd is None, refd)
r4 = wf.run_child(meta, d_node, {"workp": d_node}, "do the work", "", None,
                  skey="wf:rcalias:workp#1")
check("D2 profile-routed respawn runs to done — RED on base",
      r4.get("status") == "done" and r4.get("error_class") != "route_substitution_denied",
      r4)
check("D2 the profile-routed spawn billed with the PROFILE riding argv "
      "(the -p face is the expressible route under #709)",
      attempts_for("/seat-default@alt") == 1,
      LEDGER.read_text() if LEDGER.exists() else "<no ledger>")

# ---- B (green before AND after): a genuinely different model stays DENIED ---
b_node = dict(node, model="other-model-9")     # no resolution of the seeded aliases
refb = wf._route_substitution_refusal(meta, b_node, 2)
check("B receipt vs a model no alias resolves to: still DENIED (guard not neutered)",
      isinstance(refb, dict) and refb.get("error_class") == "route_substitution_denied", refb)
r2 = wf.run_child(meta, b_node, {"work": b_node}, "do the work", "", None,
                  skey="wf:rcalias:work#3")
check("B ZERO attempts against the substituted model",
      r2.get("status") == "failed"
      and r2.get("error_class") == "route_substitution_denied"
      and attempts_for("example-provider/other-model-9") == 0, r2)

# ---- E (green before AND after): the widening cannot self-certify ------------
# bigseat2 DOES resolve through the core table — to a target DIFFERENT from the
# receipt. The new leg may only promote a candidate when the resolved target
# matches the verified route; a mismatched resolution is still a substitution.
refe = wf._route_substitution_refusal(meta, dict(node, model="bigseat2"), 5)
check("E alias that resolves to a DIFFERENT target than the receipt: still DENIED",
      isinstance(refe, dict) and refe.get("error_class") == "route_substitution_denied", refe)

# ---- C (green before AND after): the literal verified TARGET still passes ----
refc = wf._route_substitution_refusal(meta, dict(node, model="example-model-1"), 3)
check("C spawn at the literal verified TARGET: NOT refused (#25 identity law intact)",
      refc is None, refc)

shutil.rmtree(HOME, ignore_errors=True)
print("RESULT", "GREEN" if ok else "RED")
raise SystemExit(0 if ok else 1)
