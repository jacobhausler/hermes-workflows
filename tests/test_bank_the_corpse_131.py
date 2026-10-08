#!/usr/bin/env python3
"""#131 — bank-the-corpse on wall-kill.

A child killed at its wall (`timeout`) used to leave its work only in the
durable work dir, with the integrator hand-banking each dead lane. Now the
runner deterministically writes `nodes/<node>[.<i>].corpus/` on EVERY wall-kill
(both wait paths: the spawn path in run_child and the adopted-orphan path in
_adopt_child): `work/` (snapshot of the child's durable work dir), `stdout_tail.txt`
(last 4000 chars of the capture) and `manifest.json` (every file with size +
mtime, newest first; `last_written` = the newest). One `node.banked` event, and a
`banked` pointer on the timed-out death record.

  N  spawn path: a stub child writes two files, prints, then sleeps past its wall
     -> corpus contents, manifest last_written, one node.banked line, verdict
     unchanged (failed/timeout), record carries banked.
  H  healthy spawn: no corpus, no node.banked, no `banked` key (byte-identity law).
  E  OSError (a regular file squats on the corpus path): honest-empty — node.banked
     with error=, files=0, no pointer, verdict still failed/timeout, squatter intact.
  U  OSError inside the copy (in-process): the helper never raises, returns None.
  A  adopted path: an orphan past its re-armed wall is killed and banked the same way.

Run: python3 tests/test_bank_the_corpse_131.py
"""
import json, os, shutil, subprocess, sys, tempfile, threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and bool(cond)

HOME = Path(tempfile.mkdtemp(prefix="wf-bank131-"))
RUNS = HOME / "workflows"
RUNS.mkdir()
STUB = HOME / "stub_corpse.py"
STUB.write_text(f"#!{sys.executable}\n" + r'''
import json, os, sys, time
a = sys.argv[1:]
if "--query-file" not in a:
    sys.exit(0)
q = open(a[a.index("--query-file") + 1]).read()
if "HEALTHY131" in q:
    print("```json\n" + json.dumps({"result": "ok"}) + "\n```", flush=True)
    sys.exit(0)
open("first.txt", "w").write("first banked line\n")
time.sleep(0.3)
os.makedirs("sub", exist_ok=True)
open("sub/second.txt", "w").write("second, the newest write\n")
print("CORPSE131 stdout tail marker", flush=True)
time.sleep(60)
''')
STUB.chmod(0o755)

def mk(run_id, nodes):
    r = RUNS / run_id
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"hermes_bin": str(STUB), "concurrency": 1,
                                            "node_timeout": 30}))
    return r

def wfrun(run_id):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id], env=env,
                          capture_output=True, text=True, timeout=120).stdout.strip()

def rec_of(r, name):
    return json.loads((r / "nodes" / f"{name}.json").read_text())

def banked(r):
    return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()
            if json.loads(l).get("event") == "node.banked"]

try:
    # ============ N: spawn-path wall-kill banks the corpse ============
    r = mk("b131-wall", [{"id": "w", "type": "agent", "goal": "wall-kill me", "timeout": 2}])
    out = wfrun("b131-wall")
    rec, corpus = rec_of(r, "w"), r / "nodes" / "w.corpus"
    check("N verdict unchanged: failed / timeout",
          rec.get("status") == "failed" and rec.get("error_class") == "timeout",
          json.dumps({k: rec.get(k) for k in ("status", "error_class", "error")}) + out[-200:])
    check("N death record carries the banked pointer",
          rec.get("banked") == str(corpus) and corpus.is_dir(), str(rec.get("banked")))
    check("N work dir snapshotted (both files, nested path kept)",
          (corpus / "work" / "first.txt").read_text() == "first banked line\n"
          and (corpus / "work" / "sub" / "second.txt").read_text() == "second, the newest write\n"
          if corpus.is_dir() else False)
    tail = (corpus / "stdout_tail.txt").read_text() if corpus.is_dir() else ""
    check("N stdout_tail.txt holds the capture tail", "CORPSE131" in tail and len(tail) <= 4000)
    man = json.loads((corpus / "manifest.json").read_text()) if corpus.is_dir() else {}
    rows = man.get("files") or []
    check("N manifest last_written = newest-mtime file",
          man.get("last_written") == "sub/second.txt", str(man.get("last_written")))
    check("N manifest lists files newest-first with sizes + mtimes",
          [x.get("path") for x in rows] == ["sub/second.txt", "first.txt"]
          and [x.get("size") for x in rows] == [25, 18]
          and all(isinstance(x.get("mtime"), float) for x in rows), str(rows)[:300])
    bk = banked(r)
    check("N exactly one node.banked line with node/index/spawn/files/bytes/corpus",
          len(bk) == 1 and bk[0].get("node") == "w" and bk[0].get("index") is None
          and isinstance(bk[0].get("spawn"), int) and bk[0].get("files") == 2
          and bk[0].get("bytes") == 43 and bk[0].get("corpus") == str(corpus)
          and "error" not in bk[0], str(bk)[:300])

    # ============ H: healthy spawn stays byte-identical ============
    r = mk("b131-ok", [{"id": "h", "type": "agent", "goal": "HEALTHY131 answer"}])
    wfrun("b131-ok")
    rec = rec_of(r, "h")
    check("H healthy node done, no banked key, no corpus, no node.banked",
          rec.get("status") == "done" and "banked" not in rec
          and not list((r / "nodes").glob("*.corpus")) and banked(r) == [],
          json.dumps(rec)[:200])

    # ============ E: OSError on the bank -> honest-empty, verdict untouched ============
    r = mk("b131-oserr", [{"id": "w", "type": "agent", "goal": "wall-kill me", "timeout": 2}])
    squat = r / "nodes" / "w.corpus"
    squat.write_text("not a dir")
    wfrun("b131-oserr")
    rec, bk = rec_of(r, "w"), banked(r)
    check("E verdict unchanged by a failed bank",
          rec.get("status") == "failed" and rec.get("error_class") == "timeout",
          json.dumps({k: rec.get(k) for k in ("status", "error_class")}))
    check("E honest-empty: one node.banked with error=, files=0, no pointer",
          len(bk) == 1 and bk[0].get("error") and bk[0].get("files") == 0
          and bk[0].get("bytes") == 0 and bk[0].get("corpus") is None
          and "banked" not in rec, str(bk)[:300])
    check("E squatter untouched, no tmp left behind",
          squat.read_text() == "not a dir"
          and not [p for p in (r / "nodes").iterdir() if ".tmp" in p.name])

    # ============ U: OSError mid-copy never escapes the helper ============
    r = mk("b131-unit", [{"id": "u", "type": "agent", "goal": "x"}])
    (wf.child_work_dir(r, {"id": "u"}, None) / "f.txt").write_text("x")
    real = shutil.copy2
    def _boom(*a, **k): raise PermissionError("injected")
    shutil.copy2 = _boom
    try:
        got = wf._bank_the_corpse(r, {"id": "u"}, None, 0, "tail")
        raised = None
    except Exception as e:   # noqa: BLE001 — the law under test is "never raises"
        got, raised = None, e
    finally:
        shutil.copy2 = real
    check("U helper returns None and never raises on a mid-copy OSError",
          got is None and raised is None and banked(r)[-1:] and "injected" in banked(r)[-1]["error"],
          repr(raised))

    # ============ A: adopted-orphan path banks the same way ============
    r = mk("b131-adopt", [{"id": "f", "type": "agent", "goal": "x", "timeout": 1}])
    node = {"id": "f", "type": "agent", "goal": "x", "timeout": 1}
    (wf.child_work_dir(r, node, 0) / "a.txt").write_text("adopted work\n")
    lp = r / "logs" / "f.0.a0.log"
    lp.parent.mkdir(exist_ok=True); lp.write_text("ADOPT131 tail\n")
    kid = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                           start_new_session=True)
    meta = {"_run": r, "_stop": threading.Event(), "_procs_lock": threading.Lock(),
            "_procs": {}, "node_timeout": 1}
    started = (datetime.now(timezone.utc) - timedelta(seconds=100)).isoformat()
    child = {"pid": kid.pid, "log_path": str(lp), "started": started, "attempt": 0, "skey": "s#a0"}
    threading.Thread(target=kid.wait, daemon=True).start()   # reap: zombie = dead
    res = wf._adopt_child(meta, node, {"f": node}, 0, child, None)
    corpus = r / "nodes" / "f.0.corpus"
    man = json.loads((corpus / "manifest.json").read_text()) if corpus.is_dir() else {}
    bk = banked(r)
    check("A adopted wall-kill: verdict timeout + banked pointer",
          res.get("error_class") == "timeout" and res.get("banked") == str(corpus),
          json.dumps({k: res.get(k) for k in ("status", "error_class", "banked")}))
    check("A corpus: work snapshot + stdout tail + manifest",
          corpus.is_dir() and (corpus / "work" / "a.txt").read_text() == "adopted work\n"
          and "ADOPT131" in (corpus / "stdout_tail.txt").read_text()
          and man.get("last_written") == "a.txt")
    check("A one node.banked line (index=0, spawn=0)",
          len(bk) == 1 and bk[0].get("index") == 0 and bk[0].get("spawn") == 0
          and bk[0].get("files") == 1, str(bk)[:300])
finally:
    shutil.rmtree(HOME, ignore_errors=True)

print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
