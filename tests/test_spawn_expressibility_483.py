#!/usr/bin/env python3
"""hermes-workflows#483 (est-8cs1o): a node whose pinned provider/model CANNOT be
expressed in the spawn argv must refuse BEFORE the child starts, never spawn bare,
silently serve the seat default, and die post-work at the _route_hold billing gate.

The door's liveness ping probes raw credentials; the child routes through the
spawn argv — two different routing surfaces. The two inexpressible faces this
gate must cover (row comment 2026-10-20, both re-measured live at the pinned
baselines):
  A the profile-less bare spawn: pin declared, no profile evidence (no -p);
  B the marker-stripped pin: the est-yq2xq omit override (env or marker file)
    consumes -m/--provider before Popen.
Since #709 the strip is UNCONDITIONAL (the marker is dead): no spawn argv can
carry -m/--provider on any host, so the only expressible pin faces are the
PROFILE face (-p survives — the supported route mechanism) and the
require_route: false opt-out (est-yq2xq's whole point). An unpinned node is
auto-route by contract; every drop is journaled (dispatch.warn, E2b2/funnel).

Law pinned:
  E1  marker armed + provider/model pin, no profile: typed refusal, ZERO
      attempts, ZERO billing, event dispatch.refused, and the error names the
      node, the pin (provider AND model), and the gap. RED at base: bare
      spawn, seat default billed, no refusal.
  E2  the SAME node on an un-armed host: runs, and the seat stub bills the
      pinned route verbatim (expressible path preserved).
  E3  marker armed + require_route: false ON THE NODE: runs (author accepted
      fallback — est-yq2xq behavior intact), seat default billed.
  E4  marker armed + graph `defaults.require_route: false`: runs (precedence
      matches the door's #25 law).
  E5  marker armed + provider-only pin with explicit require_route: true:
      refusal naming the provider (the issue's acceptance face: "names
      provider + gap").
  E6  marker armed + NO pin at all: runs (nothing pinned, nothing held).
  E7  the typed class is a member of the closed ERROR_CLASSES set.
  E8  PROFILE-carried pin (the estate shape, #709 truth): the profile face IS
      the expressible route — the child spawns on `-p`, the pin pair strips
      LOUD (dispatch.warn names it), and the billing hold stays the downstream
      gate. (The 72c2543 pass briefly pinned the opposite law; core_alias D2
      and the substrate suite contradict it — truth wins.)

Harness: the repo's own in-process run_child harness with a recording seat
stub (test_alias_receipt_respawn_318 shape), stdlib only, no network. The
strip is simulated with a MARKER under the test's own HERMES_HOME — never by
touching a real one.
"""
import json, os, sys, tempfile, threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label
          + (("" if cond else "  ") + str(detail)[:400] if detail and not cond else ""))
    ok = ok and bool(cond)

HOME = Path(tempfile.mkdtemp(prefix="wf-483-"))
RUNS = HOME / "runs"
STUB = HOME / "hermes_stub.py"
STUB.write_text(
    "#!/usr/bin/env python3\n"
    "import sys, os\n"
    "a = sys.argv[1:]\n"
    "m = a[a.index('-m') + 1] if '-m' in a else 'seat-default'\n"
    "p = a[a.index('--provider') + 1] if '--provider' in a else ''\n"
    "with open(os.environ['HERMES_WF_483_LEDGER'], 'a') as f:\n"  # HERMES_WF_ prefix survives the profile-spawn env scrub
    "    f.write(p + '/' + m + '\\n')\n"
    "print('```json\\n{\"result\": \"ok\"}\\n```')\n"
)
STUB.chmod(0o755)
LEDGER = HOME / "attempts.ledger"
os.environ["HERMES_WF_483_LEDGER"] = str(LEDGER)
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)
os.environ.pop("WF_OMIT_POLICY_FLAGS", None)   # the marker is the only actor here

MARKER = HOME / "workflows" / "omit-policy-flags.on"
MARKER.parent.mkdir(parents=True, exist_ok=True)
def armed(on):
    (MARKER.write_text("on") if on else MARKER.unlink(missing_ok=True))

def mkrun(name, graph_defaults=None):
    run = RUNS / name
    (run / "nodes").mkdir(parents=True)
    (run / "gates").mkdir()
    graph = {"name": name, "nodes": []}
    if graph_defaults:
        graph["defaults"] = graph_defaults
    (run / "graph.json").write_text(json.dumps(graph))
    return run

META = lambda run: {"_run": run, "hermes_bin": str(STUB), "_spawn_n": {},
                    "_procs_lock": threading.Lock(), "_procs": {},
                    "_stop": threading.Event(), "node_timeout": 15}

RUN_A, RUN_B = mkrun("ex483a"), mkrun("ex483b", {"require_route": False})
def node(nid, **f):
    return {"id": nid, "type": "agent", "goal": "do the work", **f}

def events(run):
    return [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines()]

def ledger_lines():
    try:
        return LEDGER.read_text().splitlines()
    except OSError:
        return []

PROV, MODEL = "example-provider", "example-model-7"

# ---- E1: armed strip + pinned lane with no profile -> refuse BEFORE child start
LEDGER.write_text("")
armed(True)
n1 = node("pinned", provider=PROV, model=MODEL)
r1 = wf.run_child(META(RUN_A), n1, {"pinned": n1}, "do the work", "", None,
                  skey="wf:ex483a:pinned")
check("E1 pinned lane under the armed strip: refused, typed",
      r1.get("status") == "failed" and r1.get("error_class") == "route_inexpressible", r1)
check("E1 ZERO attempts against the seat (refusal is pre-Popen, pre-seat)",
      ledger_lines() == [] and r1.get("ms") == 0, ledger_lines())
err1 = r1.get("error", "")
check("E1 the error names the node, the provider and the model",
      "pinned" in err1 and PROV in err1 and MODEL in err1, err1)
check("E1 the error names the gap and the require_route opt-out",
      "cannot express" in err1.lower() and "require_route" in err1, err1)
ev1 = [e for e in events(RUN_A) if e.get("event") == "dispatch.refused"]
check("E1 one dispatch.refused event carrying the typed class",
      len(ev1) == 1 and ev1[0].get("error_class") == "route_inexpressible"
      and ev1[0].get("node") == "pinned", ev1)

# ---- E2: the marker is DEAD (#709, owner order): a leftover marker file
# changes NOTHING - the same pinned lane refuses identically (strip is
# unconditional; the old "un-armed host runs expressible" world is gone).
LEDGER.write_text("")
armed(True)
r2 = wf.run_child(META(RUN_A), n1, {"pinned": n1}, "do the work", "", None,
                  skey="wf:ex483a:pinned#2")
check("E2 leftover marker inert: same pinned lane refuses identically",
      r2.get("status") == "failed" and r2.get("error_class") == "route_inexpressible", r2)
check("E2 the seat stub billed NOTHING (refusal stays pre-Popen)",
      ledger_lines() == [], ledger_lines())
check("E2 exactly one MORE refusal event, no new class",
      len([e for e in events(RUN_A) if e.get("event") == "dispatch.refused"
           and e.get("error_class") == "route_inexpressible"]) == 2, events(RUN_A)[-2:])

# ---- E2b: the pair-drop is exact (every frozen flag loses its value token;
# everything else rides byte-intact) - the behavior law for #709.
sample = ["hermes", "-p", "zap", "chat", "--query-file", "/tmp/-m", "--oneshot",
          "--max-turns", "9", "--run-budget", "5", "--reasoning", "high",
          "-t", "web", "-m", "some-model", "--provider", "some-prov", "extra"]
stripped = wf._strip_frozen_route_flags(sample)
check("E2b every frozen pair dropped with its value token",
      all(f not in stripped for f in ("--max-turns", "--run-budget",
                                      "--reasoning", "-t", "-m", "--provider"))
      and all(v not in stripped for v in ("9", "5", "high", "web",
                                          "some-model", "some-prov")), stripped)
check("E2b everything else byte-intact in order",
      stripped == ["hermes", "-p", "zap", "chat", "--query-file", "/tmp/-m",
                   "--oneshot", "extra"], stripped)
# ---- E2b2 (#709 review): the drop is LOUD — the collector form names exactly
# the pairs removed, in argv order, and its output is byte-identical to the
# silent form. This is the unit contract behind every dispatch.warn row: the
# funnel (run_child) passes a collector and journals it per spawn (e2e witnesses:
# test_failures_0923 Q1, test_turn_accounting_contract_lw1eh, test_routing_routes).
_dropped = []
_stripped2 = wf._strip_frozen_route_flags(sample, _dropped)
check("E2b2 collector names exactly the dropped pairs, flag+value, argv order",
      _dropped == [["--max-turns", "9"], ["--run-budget", "5"],
                   ["--reasoning", "high"], ["-t", "web"],
                   ["-m", "some-model"], ["--provider", "some-prov"]], _dropped)
check("E2b2 collector form byte-identical to the silent form",
      _stripped2 == stripped, _stripped2)

# ---- E3: armed + require_route:false on the node -> est-yq2xq legacy path ---
LEDGER.write_text("")
armed(True)
n3 = node("optout", provider=PROV, model=MODEL, require_route=False)
r3 = wf.run_child(META(RUN_A), n3, {"optout": n3}, "do the work", "", None,
                  skey="wf:ex483a:optout")
check("E3 opt-out rides the seat default (strip is unconditional)",
      r3.get("status") == "done" and ledger_lines() == ["/seat-default"], (r3, ledger_lines()))

# ---- E4: armed + graph defaults require_route:false -> precedence honored ---
LEDGER.write_text("")
n4 = node("graphopt", provider=PROV, model=MODEL)
r4 = wf.run_child(META(RUN_B), n4, {"graphopt": n4}, "do the work", "", None,
                  skey="wf:ex483b:graphopt")
check("E4 graph-defaults opt-out runs (door #25 precedence verbatim)",
      r4.get("status") == "done" and ledger_lines() == ["/seat-default"], (r4, ledger_lines()))

# ---- E5: provider-only pin, explicit require_route -> refusal names provider
LEDGER.write_text("")
n5 = node("provonly", provider=PROV, require_route=True)
r5 = wf.run_child(META(RUN_A), n5, {"provonly": n5}, "do the work", "", None,
                  skey="wf:ex483a:provonly")
check("E5 provider-only pin under the armed strip: refused, zero attempts",
      r5.get("status") == "failed" and r5.get("error_class") == "route_inexpressible"
      and ledger_lines() == [], (r5, ledger_lines()))
check("E5 the error names the provider and the --provider gap",
      PROV in r5.get("error", "") and "--provider" in r5.get("error", ""), r5)

# ---- E6: armed, nothing pinned -> auto-route untouched -----------------------
LEDGER.write_text("")
n6 = node("bare")
r6 = wf.run_child(META(RUN_A), n6, {"bare": n6}, "do the work", "", None,
                  skey="wf:ex483a:bare")
check("E6 armed + no pin at all: runs unchanged (auto-route is the ask)",
      r6.get("status") == "done", r6)

# ---- E7: the closed set carries the new class --------------------------------
check("E7 route_inexpressible is in ERROR_CLASSES",
      "route_inexpressible" in wf.ERROR_CLASSES)

# ---- E8 (#709 TRUTH, rewrote the E8 law the 72c2543 pass left in): a
# PROFILE-carried pin IS expressible. `-p zap` rides the argv and survives the
# strip — the strip block's own law: "Profiles (-p) are not creation overrides
# and survive — that is the supported route mechanism." The pin pair still dies
# at the funnel, LOUD (dispatch.warn names it); the served-route truth stays
# policed downstream by the route billing hold, the est-yq2xq legacy posture.
# What may NEVER happen again is E1: a bare, profile-less pin silently serving
# the seat default.
LEDGER.write_text("")
(HOME / "profiles" / "zap").mkdir(parents=True, exist_ok=True)
(HOME / "profiles" / "zap" / "config.yaml").write_text("model:\n  default: zap-default\n")
armed(True)
n8 = node("zapleg", profile="zap", provider=PROV, model=MODEL)
r8 = wf.run_child(META(RUN_A), n8, {"zapleg": n8}, "do the work", "", None,
                  skey="wf:ex483a:zapleg")
check("E8 profile-carried pin spawns on the profile face: done, seat stub billed",
      r8.get("status") == "done" and ledger_lines() == ["/seat-default"], (r8, ledger_lines()))
_ev8w = [e for e in events(RUN_A) if e.get("event") == "dispatch.warn"
         and e.get("kind") == "frozen_route_strip" and e.get("node") == "zapleg"]
check("E8 the pin pair drop is journaled LOUD, naming exactly -m and --provider",
      len(_ev8w) == 1 and _ev8w[0].get("stripped") == [["-m", MODEL], ["--provider", PROV]],
      _ev8w)
check("E8 the profile-carried leg is NOT refused (no dispatch.refused for this node)",
      not [e for e in events(RUN_A) if e.get("event") == "dispatch.refused"
           and e.get("node") == "zapleg"], events(RUN_A)[-3:])

print(f"{'FAILED' if not ok else 'OK'}: spawn-expressibility #483 suite")
sys.exit(1 if not ok else 0)
