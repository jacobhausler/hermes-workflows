#!/usr/bin/env python3
"""#24 — subscription-quota 429s are NOT transient transport.

(a) a marker carrying a reset horizon (or a quota-exhaustion phrase) classifies
    fatal_quota: fails on the FIRST attempt (no retry ladder), error names the model;
(b) the runner remembers an exhausted resolved model (seat-local cache);
(c) the door refuses to launch a node whose explicit model is cache-exhausted
    (advisory: a liveness ping that answers recovers the model).
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
HOME = BUILD / "home-fq24"
RUNS = HOME / "workflows"
sys.path.insert(0, str(BUILD.parent))
import wf, wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " + label + (f"  {detail}" if detail else "")))
    if not cond: ok = False

# ---------- (a) classifier ----------
QUOTA_MARK = ("Warning: x\n"
              "Provider said: HTTP 429: {\"error\": {\"message\": \"ChatGPT or Codex "
              "Subscription usage limit reached, resets in ~109 hours\"}}\n")
ec, marker = wf._classify_rc_output(QUOTA_MARK)
check("quota phrase + horizon -> fatal_quota", ec == "fatal_quota", f"{ec}/{marker}")
check("marker preserved", marker and "resets in" in marker, str(marker))

PLAIN_429 = "hermes -z: agent failed: Error code: 429 - {'error': 'slow down'}"
ec2, _ = wf._classify_rc_output(PLAIN_429)
check("plain 429 stays transport (transient rate limit)", ec2 == "transport", ec2)

RATE_LIMIT_LONG = ("Provider said: HTTP 429: Too Many Requests. "
                   "Please retry later to avoid rate limiting")
ec3, _ = wf._classify_rc_output(RATE_LIMIT_LONG)
check("'rate limiting' prose alone is NOT quota", ec3 == "transport", ec3)

check("fatal_quota is in the closed set", "fatal_quota" in wf.ERROR_CLASSES)
check("fatal_quota is never retryable", "fatal_quota" not in wf._RETRYABLE_CLASSES
      and "fatal_quota" not in wf._BOUNDED_RETRY_CLASSES)

# ---------- (a) end-to-end: one attempt only, error names the model ----------
if HOME.exists(): shutil.rmtree(HOME)
RUNS.mkdir(parents=True)
FAKE = str(BUILD / "fake-fq24"); shutil.copy(BUILD / "fake_hermes.py", FAKE); os.chmod(FAKE, 0o755)
LOG = HOME / "fake.log"

def mk(run_id, nodes):
    r = RUNS / run_id
    if r.exists(): shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": "fq", "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"hermes_bin": FAKE, "concurrency": 2, "node_timeout": 30}))
    return r

env = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(LOG),
           FAKE_MODE="quota", WF_QUOTA_CACHE=str(HOME / "quota-cache.json"))
node = [{"id": "a", "type": "agent", "goal": "GO", "model": "sol"}]
r = mk("fq-e2e", node)
for line in open(FAKE): pass  # noop; fake reads env at spawn
subprocess.run([sys.executable, str(BUILD.parent / "wf.py"), "run", str(r)],
               env=env, capture_output=True, timeout=120)
rec = json.loads((r / "nodes" / "a.json").read_text())
check("e2e: node failed", rec.get("status") == "failed", str(rec.get("status")))
check("e2e: class fatal_quota", rec.get("error_class") == "fatal_quota", str(rec.get("error_class")))
check("e2e: ONE attempt (no ladder)", (rec.get("attempts_log") or [0]) and len(rec.get("attempts_log") or []) <= 1
      and rec.get("attempts", 1) <= 1, f"attempts={rec.get('attempts')} log={len(rec.get('attempts_log') or [])}")
spawns = LOG.read_text().count("GO") if LOG.exists() else 0
check("e2e: exactly 1 spawn", spawns == 1, f"spawned {spawns}x")
check("e2e: error names the model", "sol" in (rec.get("error") or ""), str(rec.get("error"))[:120])

# ---------- (b) the seat-local cache got written ----------
qc = HOME / "quota-cache.json"
check("cache written", qc.exists())
if qc.exists():
    cache = json.loads(qc.read_text())
    hit = [k for k in cache if "sol" in k]
    check("cache keys the resolved model", bool(hit), str(list(cache)))
    if hit:
        reset = cache[hit[0]].get("resets_epoch", 0)
        check("cache carries the reset horizon (≈109h out)",
              reset > time.time() + 100 * 3600, f"reset={reset}")

# ---------- (c) the door refuses a launch on a cache-exhausted model ----------
sys.path.insert(0, str(BUILD.parent.parent))          # plugin dir parent for __init__ import
import importlib.util
spec = importlib.util.spec_from_file_location("wfdoor", BUILD.parent / "__init__.py")
assert spec is not None and spec.loader is not None
door = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(door)
except SystemExit:
    pass  # module-level guards; handler is what we need
graph = {"name": "fq-refuse", "nodes": [{"id": "x", "type": "agent", "goal": "GO", "model": "sol"}]}
res = door._quota_refusal(graph, cache_path=qc)
check("door refuses exhausted model before any write", res and "sol" in str(res), str(res))
res2 = door._quota_refusal({"name": "n", "nodes": [{"id": "x", "type": "agent", "goal": "GO"}]},
                           cache_path=qc)
check("door never refuses an unpinned node", res2 is None, str(res2))

print("ALL PASS" if ok else "FAILURES"); sys.exit(0 if ok else 1)
