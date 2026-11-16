#!/usr/bin/env python3
"""est-c4wx4 — answer-first closing: adopt <child_work_dir>/answer.json at death.

The disease (ra-work 20261023-142210 fix node 4x, ra-pr 20261023-202025 review
node 2x): a suite-bearing lane commits all its work, has its complete answer
on disk, and dies at the wall before emitting the fenced block — the runner
dead-lettered an answer that was already written. The cure: at the deaths that
consult _harvest_death (wall / cap_exhausted / rc!=0, spawn AND adopted paths;
NEVER cancelled), when stdout carries no fence the runner adopts
<child_work_dir>/answer.json under _harvest_death's EXACT gate (parses to a
dict + validate() passes against the node schema), committing `partial` with
the death class unchanged and `harvest.source: "workdir"` so provenance is
machine-visible. Guards: the mtime anchor is NANOSECOND-exact (st_mtime_ns
against the attempt's ns anchor — cert R4), regular file only (no symlink/dir),
unreadable/oversized/UNDECODABLE (strict UTF-8, U+FFFD refused — cert R5) or
schema-invalid = the death stands unchanged; a `## Remaining` block the dead
capture declared on stdout rides the adoption and merges into `remaining`
(cert R1); coerced unfenced chatter never outranks a fresh disk answer
(cert R3); the silent zero-stdout shape consults the disk fallback before the
empty-log guard (cert R2). Writer half: the reply CONTRACT and WORK_DIR_NOTE
carry the answer-first sentence.

Cert R6: every law below is asserted EXECUTABLY — by running the helper, the
adopted-death classifier, or a whole run — never by regex census over source
(the old W4/W5 source census is deleted: it passed with every defect present).

  U1  fresh valid object        -> {output, remaining, harvest.source=workdir}
  U2  fenced file content       -> same adoption (same fence law as stdout)
  U3  mtime_ns < ns anchor      -> None (stale across attempts, never adopted)
  U4  mtime_ns == ns anchor     -> adopted (the gate is >=)
  U4b mtime_ns 50ms < anchor    -> None (same-second staleness: ns precision)
  U5  schema violation          -> None
  U6  unparseable file          -> None
  U7  symlink                   -> None (regular-file-only)
  U8  a directory squats        -> None
  U9  oversized file            -> None (death unchanged)
  U10 spawn anchor unknown      -> None (fail-closed)
  U11 no schema                 -> adopted (validate() passes, same as stdout law)
  U12 undecodable bytes / U+FFFD glyph -> None (R5: refuse, never repair)
  U13 dead capture's ## Remaining merges into the adopted `remaining` (R1)
  U14 _adopt_harvest_anchor: started_ns trusted; second-precision start fails
      closed; fractional ISO round-trips to ns (R4)
  W1  CONTRACT carries the answer-first writer sentence; WORK_DIR_NOTE names
      {WORK_DIR}/answer.json (the per-item path rides the GOAL half — the
      fan-out byte-identity law forbids per-item interpolation after Inputs)
  W2  fan-out prompt tail after ## Inputs stays byte-identical across items
      (the writer sentence must not break the identity law)
  W3  a live prompt carries the ABSOLUTE <work_dir>/answer.json path
  I1  wall death: stub banks answer.json then sleeps past its wall
      -> nodes/lane.json partial, error_class=timeout, harvest.source=workdir,
         the output committed, the corpse still banked (#131 untouched)
  I2  quorum straggler with a fresh answer.json -> cancelled, never adopted
  I3  SILENT rc=17 (zero stdout) + fresh answer.json -> partial, source=workdir
      (R2: the empty-log guard consults disk BEFORE calling early_death)
  I4  validate policy + capture-declared ## Remaining -> the adoption cannot
      clamp done; the record stays partial with the merged remaining (R1)
  I5  direct _adopt_child: unfenced coerced chatter does NOT outrank the disk
      answer (partial, source=workdir — R3); a config-error capture still
      ranks first (failed, no adoption); a set stop flag still ranks first
      (cancelled, no adoption)
  I6  every record that dies after a spawn carries the Popen-instant started_ns
      anchor (R4's trust anchor is stamped, not inferred)

Run: python3 tests/test_harvest_workdir_c4wx4.py
"""
import json, os, subprocess, sys, tempfile, threading, time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)

sys.path.insert(0, str(BUILD))
import wf  # noqa: E402

NS = 1_000_000_000
ok, checks = True, []
def check(label, cond, detail=""):
    global ok
    checks.append(bool(cond))
    print(("PASS " if cond else "FAIL " ) + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and bool(cond)

# ---------- unit: the pure helper ----------
HW = getattr(wf, "_harvest_workdir", None)
check("U0 wf._harvest_workdir exists", HW is not None)

if HW is not None:
    UTMP = Path(tempfile.mkdtemp(prefix="wf-hwdir-"))
    SCHEMA = {"type": "object", "required": ["result"]}
    ANS = {"result": "answer-first", "notes": "written before the wall"}

    def mkfile(nid, content, index=None):
        run = UTMP / f"run-{nid}"
        wd = wf.child_work_dir(run, {"id": nid}, index)
        p = wd / "answer.json"
        if isinstance(content, bytes):
            p.write_bytes(content)
        elif content == "DIR":
            p.mkdir()
        elif content == "SYMLINK":
            target = wd.parent / "elsewhere.json"
            target.write_text(json.dumps(ANS))
            p.symlink_to(target)
        else:
            p.write_text(content)
        return run, p

    def harvest(nid, schema, anchor_ns, index=None, out=None):
        run = UTMP / f"run-{nid}"
        return HW(run, {"id": nid}, index, schema, anchor_ns, out)

    # U1 fresh valid object
    now_ns = time.time_ns()
    run, p = mkfile("u1", json.dumps(ANS))
    os.utime(p, ns=(now_ns, now_ns))
    hv = harvest("u1", SCHEMA, now_ns - 5 * NS)
    check("U1 fresh valid object adopts", bool(hv) and hv.get("output") == ANS
          and (hv.get("harvest") or {}).get("source") == "workdir"
          and hv.get("remaining") == [], json.dumps(hv)[:300] if hv else "None")
    check("U1 shape carries the three keys", bool(hv) and set(hv) == {"output", "remaining", "harvest"})

    # U2 fenced file content (the child wrote the fence itself)
    now_ns = time.time_ns()
    run, p = mkfile("u2", "prelude prose\n```json\n" + json.dumps(ANS) + "\n```\ntrailing")
    os.utime(p, ns=(now_ns, now_ns))
    hv = harvest("u2", SCHEMA, now_ns - 5 * NS)
    check("U2 fenced file content adopts (same fence law as stdout)",
          bool(hv) and hv.get("output") == ANS
          and (hv.get("harvest") or {}).get("source") == "workdir")

    # U3 stale: written 100 s BEFORE the dead attempt's spawn anchor
    run, p = mkfile("u3", json.dumps(ANS))
    os.utime(p, ns=(now_ns - 100 * NS, now_ns - 100 * NS))
    check("U3 stale answer.json (mtime_ns < spawn anchor) never adopted",
          harvest("u3", SCHEMA, time.time_ns()) is None)

    # U4 equality edge: mtime_ns == anchor passes (>=)
    run, p = mkfile("u4", json.dumps(ANS))
    mt = p.stat().st_mtime_ns
    check("U4 mtime_ns == spawn anchor adopts (gate is >=)", harvest("u4", SCHEMA, mt) is not None)

    # U4b R4 precision: a PREVIOUS attempt's file written 50 ms before this
    # attempt's Popen is same-second-stale — a second-granular gate adopts it,
    # the ns gate must not.
    run, p = mkfile("u4b", json.dumps(ANS))
    mt = p.stat().st_mtime_ns
    check("U4b same-second stale (mtime_ns + 50ms < anchor) never adopted",
          harvest("u4b", SCHEMA, mt + 50_000_000) is None)

    # U5 schema violation
    run, p = mkfile("u5", json.dumps({"verdict": "no-result-key"}))
    check("U5 schema violation -> death unchanged", harvest("u5", SCHEMA, 0) is None)

    # U6 unparseable
    run, p = mkfile("u6", "this is not json at all\nand no fence either")
    check("U6 unparseable file -> death unchanged", harvest("u6", SCHEMA, 0) is None)

    # U7 symlink (target is a perfect answer — regular-file-only still refuses)
    run, p = mkfile("u7", "SYMLINK")
    check("U7 symlink never adopted", harvest("u7", SCHEMA, 0) is None)

    # U8 directory squat
    run, p = mkfile("u8", "DIR")
    check("U8 a directory squatting answer.json never adopted", harvest("u8", SCHEMA, 0) is None)

    # U9 oversized (over the est-gg96 scan cap)
    big = json.dumps({"result": "x" * (wf.HARVEST_SCAN_MAX_BYTES + 4096)})
    run, p = mkfile("u9", big)
    check("U9 oversized file -> death unchanged", harvest("u9", SCHEMA, 0) is None)

    # U10 unknown spawn anchor fails closed
    run, p = mkfile("u10", json.dumps(ANS))
    check("U10 unknown spawn anchor -> no adoption (fail-closed)", harvest("u10", SCHEMA, None) is None)

    # U11 no schema on the node: validate() passes, adoption rides
    run, p = mkfile("u11", json.dumps(ANS))
    check("U11 schemaless node adopts (same bar as the stdout law)",
          harvest("u11", None, 0) is not None)

    # U12 R5: undecodable bytes are REFUSED, not repaired-and-adopted.
    run, p = mkfile("u12", b'{"result": "corrupt \xff\xfe bytes"}')
    check("U12 undecodable bytes -> death unchanged (strict UTF-8)",
          harvest("u12", SCHEMA, 0) is None)
    run, p = mkfile("u12g", '{"result": "repair glyph \ufffd sits here"}')
    check("U12b a U+FFFD replacement glyph in the text -> refused (not the child's bytes)",
          harvest("u12g", SCHEMA, 0) is None)

    # U13 R1: the dead capture is the completion authority — its declared
    # ## Remaining rides the adoption and merges with the file's own tail.
    run, p = mkfile("u13a", json.dumps(ANS))
    hv = harvest("u13a", SCHEMA, 0, out="progress\n## Remaining\n- run the suite\n")
    check("U13 capture-declared ## Remaining reaches the adopted remaining",
          bool(hv) and hv.get("remaining") == ["run the suite"], json.dumps(hv)[:300] if hv else "None")
    run, p = mkfile("u13b", "```json\n" + json.dumps(ANS) + "\n```\n## Remaining\n- run the suite\n")
    hv = harvest("u13b", SCHEMA, 0, out="## Remaining\n- run the suite\n")
    check("U13b a step declared on BOTH sides is merged once (dedup)",
          bool(hv) and hv.get("remaining") == ["run the suite"], json.dumps(hv) if hv else "None")
    run, p = mkfile("u13c", "```json\n" + json.dumps(ANS) + "\n```\n## Remaining\n- beta step\n")
    hv = harvest("u13c", SCHEMA, 0, out="## Remaining\n- alpha step\n")
    check("U13c capture steps first, file-only steps appended",
          bool(hv) and hv.get("remaining") == ["alpha step", "beta step"], json.dumps(hv) if hv else "None")

# ---------- U14: the adopted path's anchor law (R4) ----------
AA = getattr(wf, "_adopt_harvest_anchor", None)
check("U14 wf._adopt_harvest_anchor exists", AA is not None)
if AA is not None:
    check("U14a started_ns stamped at Popen is the trusted anchor",
          AA({"started_ns": 1_700_000_000_123456789,
              "started": "2026-11-15T12:00:00"}) == 1_700_000_000_123456789)
    check("U14b second-precision start FAILS CLOSED (cannot prove same-second freshness)",
          AA({"started": "2026-11-15T12:00:00"}) is None)
    check("U14c fractional-seconds ISO round-trips to ns",
          AA({"started": "2026-11-15T12:00:00.123456"})
          == int(round(datetime.fromisoformat("2026-11-15T12:00:00.123456").timestamp() * NS)))
    check("U14d unparseable/missing start fails closed",
          AA({"started": "garbage"}) is None and AA({}) is None and AA(None) is None)
    check("U14e a non-int or bool started_ns is not trusted",
          AA({"started_ns": "1700000000123456789", "started": "2026-11-15T12:00:00"}) is None
          and AA({"started_ns": True}) is None)

# ---------- writer half: the prompt law ----------
check("W1 CONTRACT carries the answer-first writer sentence",
      "answer.json" in wf.CONTRACT and "durable" in wf.CONTRACT, wf.CONTRACT[:200])
check("W1b WORK_DIR_NOTE names the absolute answer path token",
      "{WORK_DIR}/answer.json" in wf.WORK_DIR_NOTE, wf.WORK_DIR_NOTE)

# ---------- integration harness (same shape as test_bank_the_corpse_131) ----------
HOME = Path(tempfile.mkdtemp(prefix="wf-hwdir-int-"))
RUNS = HOME / "workflows"
RUNS.mkdir()
STUB = HOME / "stub_answer_first.py"
STUB.write_text(f"#!{sys.executable}\n" + r'''
import json, os, sys, time
a = sys.argv[1:]
if "--query-file" not in a:
    sys.exit(0)
q = open(a[a.index("--query-file") + 1]).read()
ANS = {"result": "answer-first", "status": "done"}
Q = q.upper()
if "AF_SLOW" in Q:
    open("answer.json", "w").write(json.dumps(ANS))   # cwd IS the child work dir
    print("progress line: answer banked", flush=True)
    time.sleep(60)
elif "AF_SILENT" in Q:
    open("answer.json", "w").write(json.dumps(ANS))   # the SILENT exit-17 shape
    sys.exit(17)
elif "AF_REM" in Q:
    open("answer.json", "w").write(json.dumps(ANS))   # disk says done...
    print("progress line", flush=True)                # ...the capture declares unfinished work
    print("## Remaining", flush=True)
    print("- run the suite", flush=True)
    sys.exit(17)
elif "AF_FAST" in Q:
    time.sleep(1.0)
    print("```json\n" + json.dumps(ANS) + "\n```", flush=True)
else:
    print("```json\n" + json.dumps({"result": "ok"}) + "\n```", flush=True)
''')
STUB.chmod(0o755)

def mk(run_id, nodes):
    r = RUNS / run_id
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"hermes_bin": str(STUB), "concurrency": 4}))
    return r

def wfrun(run_id):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, text=True, capture_output=True, timeout=120)

# I1 — the disease itself: answer on disk, wall death, no stdout fence.
run = mk("af-i1", [{"id": "lane", "type": "agent", "goal": "AF_SLOW run the whole suite",
                   "schema": {"type": "object", "required": ["result"]}, "timeout": 4}])
wfrun("af-i1")
try:
    rec = json.loads((run / "nodes" / "lane.json").read_text())
except Exception:
    rec = {}
check("I1 wall death with answer.json commits partial (was: failed dead-letter)",
      rec.get("status") == "partial", json.dumps(rec)[:300])
check("I1 the death class stands unchanged", rec.get("error_class") == "timeout", str(rec.get("error_class")))
check("I1 harvest provenance names the workdir",
      (rec.get("harvest") or {}).get("source") == "workdir", json.dumps(rec.get("harvest")))
check("I1 the answer is the committed output", rec.get("output") == {"result": "answer-first", "status": "done"},
      json.dumps(rec.get("output"))[:200])
check("I1 the error names the harvest source", "harvested from workdir" in str(rec.get("error")), str(rec.get("error"))[:200])
check("I1 the corpse is still banked (#131 law untouched)", bool(rec.get("banked")))

# I6 — R4's trust anchor is STAMPED at the Popen instant and rides the commit.
check("I6 the death record carries the Popen-instant started_ns anchor (R4)",
      isinstance(rec.get("started_ns"), int) and rec.get("started_ns") > 0, str(rec.get("started_ns")))

# I2 — cancelled never adopts: quorum straggler banks answer.json, gets killed.
run = mk("af-i2", [{"id": "fo", "type": "agent",
                   "fanout": {"items": ["fast", "slow"], "goal": "{item} — AF_{item} the work",
                              "quorum": 1}}])
wfrun("af-i2")
recs = []
for f in (run / "nodes").glob("*.json"):
    try:
        recs.append(json.loads(f.read_text()))
    except Exception:
        pass
canx = [r for r in recs if r.get("error_class") == "cancelled"]
check("I2 the straggler died cancelled (harness alive)", bool(canx), json.dumps(recs)[:300])
check("I2 cancelled NEVER adopts the fresh answer.json",
      all((r.get("harvest") or {}).get("source") != "workdir" for r in recs))

# I3 — R2: the SILENT exit-17 shape. Zero stdout used to hit the empty-log
# guard and return WITHOUT ever consulting the disk fallback.
run = mk("af-i3", [{"id": "sil", "type": "agent", "goal": "AF_SILENT no chatter at all",
                    "schema": {"type": "object", "required": ["result"]}, "timeout": 30}])
wfrun("af-i3")
try:
    rec3 = json.loads((run / "nodes" / "sil.json").read_text())
except Exception:
    rec3 = {}
check("I3 silent rc=17 + fresh answer.json -> partial (was: dead-letter before disk was read)",
      rec3.get("status") == "partial", json.dumps(rec3)[:300])
check("I3 the silent adoption names the workdir",
      (rec3.get("harvest") or {}).get("source") == "workdir", json.dumps(rec3.get("harvest")))
check("I3 the silent adoption commits the disk answer",
      rec3.get("output") == {"result": "answer-first", "status": "done"}, json.dumps(rec3.get("output"))[:200])

# I4 — R1: a capture-declared ## Remaining cannot be laundered by a disk
# adoption: harvest_policy=validate must REFUSE the done clamp.
run = mk("af-i4", [{"id": "val", "type": "agent", "goal": "AF_REM declares remaining work",
                    "schema": {"type": "object", "required": ["result"]},
                    "harvest_policy": "validate", "timeout": 30}])
wfrun("af-i4")
try:
    rec4 = json.loads((run / "nodes" / "val.json").read_text())
except Exception:
    rec4 = {}
check("I4 validate policy refuses the done clamp when the capture declared ## Remaining",
      rec4.get("status") == "partial" and "clamped" not in rec4, json.dumps(rec4)[:400])
check("I4 the declared remaining step is visible on the committed record",
      "run the suite" in json.dumps(rec4), json.dumps(rec4)[:400])

# I5 — R3 executed against the adopted-death classifier itself: a live pid
# dies mid-watch, its log holds ONLY unfenced chatter that extract_json
# coerces and the schema declines, and a fresh answer.json sits on disk.
def adopt_probe(tag, log_text, stop_set=False):
    run = RUNS / f"af-i5-{tag}"
    (run / "nodes").mkdir(parents=True); (run / "gates").mkdir()
    (run / "graph.json").write_text(json.dumps({"name": tag, "nodes": []}))
    (run / "run.json").write_text(json.dumps({"hermes_bin": str(STUB)}))
    (run / "nodes" / "ad.json").write_text(json.dumps({"id": "ad", "status": "pending"}))
    lp = run / "logs" / "ad.a0.log"
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(log_text)
    started_ns = time.time_ns()          # the simulated Popen instant — BEFORE the write
    # The kernel stamps file mtimes from its COARSE clock, which lags the fine
    # time_ns() clock by up to one tick: a write microseconds after the anchor
    # can carry st_mtime_ns < started_ns (measured ~10% of immediate writes,
    # max lag ~1.4 ms) and the gate then correctly refuses it as stale. A real
    # child writes long after its Popen; the probe sleeps past one tick so the
    # simulated child does too. The assertion is unchanged.
    time.sleep(0.02)
    wd = wf.child_work_dir(run, {"id": "ad"}, None)
    (wd / "answer.json").write_text(json.dumps({"result": "answer-first", "status": "done"}))
    kid = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.3)"])
    node = {"id": "ad", "type": "agent", "goal": "probe"}
    meta = {"_run": run, "_procs": {}, "_procs_lock": threading.Lock(),
            "_stop": threading.Event(), "node_timeout": 30}
    if stop_set:
        meta["_stop"].set()
    kid.wait()                                        # the orphan dies while unwatched
    child = {"pid": kid.pid, "log_path": str(lp), "skey": "sk-a0", "attempt": 0,
             "started": datetime.fromtimestamp(started_ns / NS).isoformat(timespec="microseconds"),
             "started_ns": started_ns}
    return wf._adopt_child(meta, node, {"ad": node}, None, child,
                            {"type": "object", "required": ["result"]})

CHATTER = json.dumps({"note": "progress only"})        # unfenced: a coercion, not an answer
rec5 = adopt_probe("chatter", CHATTER)
check("I5 coerced chatter does not outrank a fresh disk answer (R3)",
      rec5.get("status") == "partial" and (rec5.get("harvest") or {}).get("source") == "workdir"
      and (rec5.get("output") or {}).get("result") == "answer-first", json.dumps(rec5)[:300])
cfg_tok = (getattr(wf, "_CONFIG_INPUT_TOKENS", None) or ["no models accessible"])[0].lower()
rec5b = adopt_probe("config", f"{cfg_tok}: fix your config")
check("I5b config-death still outranks the disk answer (no adoption)",
      rec5b.get("status") == "failed" and (rec5b.get("harvest") or {}).get("source") != "workdir"
      and rec5b.get("error_class") == "config_input", json.dumps(rec5b)[:300])
rec5c = adopt_probe("cancel", CHATTER, stop_set=True)
check("I5c a set stop flag still outranks the disk answer (cancelled never adopts)",
      rec5c.get("error_class") == "cancelled"
      and (rec5c.get("harvest") or {}).get("source") != "workdir", json.dumps(rec5c)[:300])

# W2/W3 — live prompts: identity law holds, absolute path lands.
run = mk("af-w3", [{"id": "gen", "type": "agent", "goal": "GEN the list"},
                   {"id": "fw", "type": "agent", "after": ["gen"], "inputs": ["gen.result"],
                    "fanout": {"items": ["p", "q"], "goal": "{item} plain work"}}])
wfrun("af-w3")
pps = sorted((run / "logs").glob("fw.*.a0.prompt.md"))
check("W2 both fan-out prompts exist (harness alive)", len(pps) == 2, str([p.name for p in pps]))
if len(pps) == 2:
    tails = [p.read_text().split("## Inputs")[-1] for p in pps]
    check("W2 fan-out tail after ## Inputs stays byte-identical (identity law)",
          tails[0] == tails[1])
pp = run / "logs" / "gen.a0.prompt.md"
if pp.exists():
    wd = str((run / "work" / "gen").resolve())
    check("W3 the live prompt carries the ABSOLUTE <work_dir>/answer.json path",
          f"{wd}/answer.json" in pp.read_text(), pp.read_text()[-300:])
else:
    check("W3 the live prompt carries the ABSOLUTE <work_dir>/answer.json path", False, "prompt missing")

print("HARVEST-WORKDIR est-c4wx4:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
