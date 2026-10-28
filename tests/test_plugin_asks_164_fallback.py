#!/usr/bin/env python3
"""est-2ek.1.164: per-node `fallback_models` — a transport_exhausted death tries
the declared models IN ORDER before the run blocks; every other error class never
falls back.

Shape (spool key 217839b445203623): a node whose provider dies with
transport_exhausted (Codex 429, retry-after days) blocked the WHOLE run — the Q4
ladder respawns the same model twice, converts the final retryable death to
error_class=transport_exhausted, and run.blocked follows. Node/defaults key
`fallback_models: [...]` makes the runner, at that exact point, re-spawn the node
once per declared model IN ORDER. Gates, tested here:
  * only transport_exhausted enters the ladder (a quota-class 429 with a reset
    horizon never respawns at all — #24 law intact);
  * order is respected; the first rung that answers commits;
  * every rung is ONE spawn (no ladder recursion), and each rung consumes the
    run's shared retry budget — the ladder can never bill unboundedly;
  * no `fallback_models` key => byte-identical old behavior (the ladder runs
    exactly as before and the node lands transport_exhausted);
  * est-mqp1f (the #579 residual): a SPENT-CAP boot refuses at the est-9qhpf
    gate BEFORE any spawn, and that refusal — transport_exhausted stamped
    `refusal` — never enters the ladder either: zero rung spawns, zero
    node.fallback events, the seeded verdict commits untouched (est-ja41
    refusal-is-final). A rung death may only RAISE `attempts` against the
    merged ledger, never re-break the record-vs-ledger agreement.
Engine-driven with the fake hermes (FAKE_MODE=fallback_ladder): a child whose -m
is not $FAKE_OK_MODEL dies with the transport marker and 0 api calls (the Q4
replay-safe shape); the ok model answers with a fenced json block, exit 0.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))

ROOT = BUILD.parent
sys.path.insert(0, str(ROOT))
# est-2ek.1.762 (zap CHANGES 6030355791): the shared launch-env pin helper is
# exec-loaded by file path — a top-level import of a tests/fixtures module is
# NOT in the shipped import closure (test_packaging #105 probe resolves only
# root/tests/dashboard) and REDs the unpacked-package gate.
_spec_iso762 = importlib.util.spec_from_file_location(
    "wf_spawn_isolation_762", Path(__file__).parent / "fixtures" / "wf_spawn_isolation_762.py")
assert _spec_iso762 and _spec_iso762.loader
_iso762 = importlib.util.module_from_spec(_spec_iso762)
_spec_iso762.loader.exec_module(_iso762)
pin_env = _iso762.pin_env
HOME = BUILD / "home_164"
env = pin_env(dict(os.environ, HERMES_HOME=str(HOME),
                   FAKE_LOG=str(BUILD / "fake_164.log")),
              HOME / "workflows", home=HOME)
FAKE = str(BUILD / "fake")

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1

def mk(run_id, nodes, extra=None):
    r = RUNS / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    cfg = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 60,
           "retry_backoff": [0.05, 0.05]}
    cfg.update(extra or {})
    (r / "run.json").write_text(json.dumps(cfg))
    return r

def wf(run_id, extra_env=None):
    e = dict(env)
    for k in ("FAKE_MODE", "FAKE_API_CALLS", "FAKE_OK_MODEL", "FAKE_ARGV_LOG"):
        e.pop(k, None)
    e.update(extra_env or {})
    p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                       env=e, capture_output=True, text=True, timeout=180)
    return p.stdout.strip()

def argv_models(argv_log):
    """The -m value the fake was spawned with, one entry per child spawn."""
    if not argv_log.exists():
        return []
    out = []
    for line in argv_log.read_text().splitlines():
        parts = line.split()
        out.append(parts[parts.index("-m") + 1] if "-m" in parts else None)
    return out

def events(r):
    p = r / "events.jsonl"
    if not p.exists():
        return []
    out = []
    for l in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(l))
        except Exception:
            pass
    return out

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True)
RUNS = HOME / "workflows"
RUNS.mkdir()

# ---- (1) RED core: transport_exhausted walks fallback_models[0] then [1],
#      the second rung answers, the node commits done on that route ----
r = mk("asks164-fallback", [{
    "id": "a", "type": "agent", "goal": "GO asks164",
    "model": "m0", "fallback_models": ["m1", "m2"],
}])
argv_log = BUILD / "argv_164_fallback.log"
argv_log.unlink(missing_ok=True)
out = wf("asks164-fallback", {"FAKE_MODE": "fallback_ladder", "FAKE_API_CALLS": "0",
                              "FAKE_OK_MODEL": "m2", "FAKE_ARGV_LOG": str(argv_log)})
models = argv_models(argv_log)
rec = json.loads((r / "nodes" / "a.json").read_text())
check("(1) run lands done (fallback rung answered)", "WORKFLOW_DONE" in out, out)
check("(1) fallback_models tried IN ORDER after the same-model ladder",
      models == ["m0", "m0", "m0", "m1", "m2"], f"spawned -m sequence: {models}")
check("(1) committed record is done on the answering rung",
      rec.get("status") == "done" and rec.get("fallback_model_used") == "m2",
      json.dumps({k: rec.get(k) for k in ("status", "error_class", "fallback_model_used")}))
evs = [e for e in events(r) if e.get("event") == "node.fallback"]
check("(1) one node.fallback event per rung, named",
      [e.get("to_model") for e in evs] == ["m1", "m2"], json.dumps(evs)[:300])

# ---- (2) first rung answers -> the second is NEVER spawned ----
r2 = mk("asks164-first", [{
    "id": "a", "type": "agent", "goal": "GO asks164-first",
    "model": "m0", "fallback_models": ["m1", "m2"],
}])
argv_log2 = BUILD / "argv_164_first.log"
argv_log2.unlink(missing_ok=True)
out2 = wf("asks164-first", {"FAKE_MODE": "fallback_ladder", "FAKE_API_CALLS": "0",
                            "FAKE_OK_MODEL": "m1", "FAKE_ARGV_LOG": str(argv_log2)})
models2 = argv_models(argv_log2)
check("(2) first answering rung stops the ladder",
      models2 == ["m0", "m0", "m0", "m1"] and "WORKFLOW_DONE" in out2, f"sequence: {models2}")

# ---- (3) other error classes NEVER fall back: a quota-class 429 (reset
# ---- horizon) is terminal at ONE attempt, zero fallback spawns ----
r3 = mk("asks164-quota", [{
    "id": "a", "type": "agent", "goal": "GO asks164-quota",
    "model": "m0", "fallback_models": ["m1"],
}])
argv_log3 = BUILD / "argv_164_quota.log"
argv_log3.unlink(missing_ok=True)
out3 = wf("asks164-quota", {"FAKE_MODE": "quota", "FAKE_ARGV_LOG": str(argv_log3)})
models3 = argv_models(argv_log3)
rec3 = json.loads((r3 / "nodes" / "a.json").read_text())
check("(3) quota 429 stays one-attempt fatal_quota — no fallback spawn",
      models3 == ["m0"] and rec3.get("error_class") == "fatal_quota",
      f"spawned {models3}, class {rec3.get('error_class')}")

# ---- (4) no fallback_models key: byte-identical old ladder — same model
# ---- thrice, transport_exhausted, run blocked, ZERO extra spawns ----
r4 = mk("asks164-plain", [{"id": "a", "type": "agent", "goal": "GO asks164-plain",
                          "model": "m0"}])
argv_log4 = BUILD / "argv_164_plain.log"
argv_log4.unlink(missing_ok=True)
out4 = wf("asks164-plain", {"FAKE_MODE": "fallback_ladder", "FAKE_API_CALLS": "0",
                           "FAKE_OK_MODEL": "zzz", "FAKE_ARGV_LOG": str(argv_log4)})
models4 = argv_models(argv_log4)
rec4 = json.loads((r4 / "nodes" / "a.json").read_text())
check("(4) absent key = old behavior: 3 spawns all m0, transport_exhausted",
      models4 == ["m0", "m0", "m0"] and rec4.get("error_class") == "transport_exhausted"
      and "WORKFLOW_FAILED" in out4, f"spawned {models4}, out {out4[:80]}")

# ---- (5) validation: fallback_models must be a list of non-empty strings,
# ---- <=8 entries (billing guard); bad shapes rejected at the door ----
import importlib.util
spec = importlib.util.spec_from_file_location("asks164_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)

def run_err(graph):
    e = door._validation_error(dict(graph, name="v"))
    return (e or {}).get("error", "")

check("(5) valid list accepted",
      run_err({"nodes": [{"id": "a", "type": "agent", "goal": "g",
                          "fallback_models": ["m1", "m2"]}]}) == "")
check("(5) dict entry rejected by name",
      "fallback_models" in run_err({"nodes": [{"id": "a", "type": "agent", "goal": "g",
                                               "fallback_models": [{"m": 1}]}]}))
check("(5) bare string rejected",
      "fallback_models" in run_err({"nodes": [{"id": "a", "type": "agent", "goal": "g",
                                               "fallback_models": "m1"}]}))
check("(5) >8 rungs rejected",
      "fallback_models" in run_err({"nodes": [{"id": "a", "type": "agent", "goal": "g",
                                               "fallback_models": [f"m{i}" for i in range(9)]}]}))
check("(5) defaults.fallback_models validated too",
      "fallback_models" in run_err({"defaults": {"fallback_models": "m1"},
                                    "nodes": [{"id": "a", "type": "agent", "goal": "g"}]}))

# ---- (6) graph defaults fill: a node without the key inherits the defaults list ----
g6 = door._common.apply_graph_defaults({"nodes": [{"id": "a", "type": "agent", "goal": "g"}],
                                        "defaults": {"fallback_models": ["m1", "m2"]}})
check("(6) defaults.fallback_models bakes into the agent node def",
      g6["nodes"][0].get("fallback_models") == ["m1", "m2"], g6["nodes"][0])


# ---- (7) est-mqp1f: a SPENT-CAP boot (est-9qhpf refusal) never walks rungs.
# ---- The refusal is the lifetime cap speaking BEFORE this boot spawned — the
# ---- est-ja41 refusal-is-final law outranks #164 over this verdict too: RED
# ---- at the base, the two declared rungs spawn (billed) and the record's
# ---- attempts is re-derived from the boot-local rung spawn.
import time as _t7
import threading as _th7
r7 = mk("asks164-spent", [{
    "id": "a", "type": "agent", "goal": "GO asks164-spent",
    "model": "m0", "fallback_models": ["m1", "m2"],
}])
(r7 / "retry-window.json").write_text(json.dumps(
    {"a": {"deadline": _t7.time() - 1.0, "attempts": 2,
           "log": [{"attempt": 0, "error_class": "transport"},
                   {"attempt": 1, "error_class": "transport"}]}}))
argv_log7 = BUILD / "argv_164_spent.log"
argv_log7.unlink(missing_ok=True)
out7 = wf("asks164-spent", {"FAKE_MODE": "fallback_ladder", "FAKE_API_CALLS": "0",
                            "FAKE_OK_MODEL": "zzz", "FAKE_ARGV_LOG": str(argv_log7)})
models7 = argv_models(argv_log7)
rec7 = json.loads((r7 / "nodes" / "a.json").read_text())
check("(7) spent-cap boot spawns NOTHING — the refusal bypasses the ladder",
      models7 == [], f"spawned {models7}")
check("(7) no node.fallback event on a refusal boot",
      not [e for e in events(r7) if e.get("event") == "node.fallback"],
      json.dumps([e.get("event") for e in events(r7)]))
check("(7) the refusal record commits: transport_exhausted, seeded count, "
      "persisted log, refusal-stamped, run failed",
      rec7.get("status") == "failed" and rec7.get("error_class") == "transport_exhausted"
      and rec7.get("attempts") == 3 and rec7.get("spawn") == 2
      and rec7.get("refusal") == "lifetime_cap_spent"
      and len(rec7.get("attempts_log") or []) == 2
      and "WORKFLOW_FAILED" in out7,
      json.dumps({k: rec7.get(k) for k in ("error_class", "attempts", "spawn", "refusal")}))
check("(7) the spent cap STAYS persisted (the refusal clears no ledger)",
      json.loads((r7 / "retry-window.json").read_text())["a"]["attempts"] == 2)

# ---- (8) unit seams (est-mqp1f): (A) refusal-stamped bypass, (B) the rung-death
# ---- recompute is MONOTONIC — spawn+1 lives in a boot-local (log-floored)
# ---- domain while attempts_log is the merged lifetime ledger, so the merge may
# ---- only raise the count, never drop below the ledger it carries (est-ja41).
import wf as wf8
node8 = {"id": "n8", "fallback_models": ["m1"]}
run8 = RUNS / "u8-fallback-refusal"
run8.mkdir(parents=True, exist_ok=True)
meta8 = {"_run": run8, "_stop": _th7.Event(), "_procs_lock": _th7.Lock(),
         "_retries_left": 6, "_procs": {}, "_spawn_n": {}}

class _Resp8:
    def __init__(self, rec):
        self.rec = rec
        self.calls = []
    def __call__(self, model, resume_preamble=""):
        self.calls.append(model)
        return dict(self.rec)

refusal8 = {"status": "failed", "error": "lifetime bound spent before this boot",
            "error_class": "transport_exhausted", "ms": 0,
            "attempts": 3, "spawn": 2, "refusal": "lifetime_cap_spent",
            "attempts_log": [{"attempt": 0, "error_class": "transport"},
                             {"attempt": 1, "error_class": "transport"}]}
rs8 = _Resp8(refusal8)
out8 = wf8._fallback_ladder(meta8, dict(refusal8), rs8, "node", {"node": "n8"}, node=node8)
check("(8A) refusal-stamped record bypasses: identical verdict back, zero rung calls",
      rs8.calls == [] and out8.get("refusal") == "lifetime_cap_spent"
      and out8.get("attempts") == 3 and len(out8.get("attempts_log") or []) == 2,
      json.dumps({k: out8.get(k) for k in ("attempts", "refusal")}))

_orig_iso8 = wf8._isolate_prior
wf8._isolate_prior = lambda *a, **k: None   # no prior tree to quarantine in a unit
try:
    # (8B) RED at base: the rung death lands spawn=1 (boot-local domain, logs/
    # empty in this stub) while the merged ledger has 3 entries — base stamps
    # attempts=2, re-breaking record-vs-ledger agreement.
    boot_local_death = {"status": "failed", "error_class": "transport",
                        "error": "boom", "ms": 9, "attempts": 1, "spawn": 1}
    base8 = {"status": "failed", "error_class": "transport_exhausted", "ms": 5,
             "error": "same-model ladder spent", "attempts": 1, "spawn": 1,
             "attempts_log": [{"attempt": 0, "error_class": "transport"},
                              {"attempt": 1, "error_class": "transport"}]}
    outB = wf8._fallback_ladder(meta8, dict(base8), _Resp8(boot_local_death),
                                "node", {"node": "n8"}, node=node8)
    check("(8B) out-of-domain rung death may not drop attempts below its own ledger",
          outB.get("attempts") == 3 and len(outB.get("attempts_log") or []) == 3,
          json.dumps({"attempts": outB.get("attempts"),
                      "log_len": len(outB.get("attempts_log") or [])}))
    # (8C) aligned-domain rung death (spawn continues the merged lifetime count):
    # spawn+1 arithmetic stays EXACTLY as before — the floor never overwrites
    # a truthful higher count.
    outC = wf8._fallback_ladder(meta8, dict(base8),
                                _Resp8({**boot_local_death, "spawn": 4}),
                                "node", {"node": "n8"}, node=node8)
    check("(8C) aligned rung death keeps spawn+1 (no-regression pin)",
          outC.get("attempts") == 5 and outC.get("spawn") == 4,
          json.dumps({"attempts": outC.get("attempts"), "spawn": outC.get("spawn")}))
finally:
    wf8._isolate_prior = _orig_iso8

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
