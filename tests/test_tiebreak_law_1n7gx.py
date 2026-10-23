#!/usr/bin/env python3
"""est-1n7gx — WF-GRAFT-7: deterministic tie-break law on every collapse-to-one row.

Peer law (iw-recon, live at write): packages/core/src/runtime/db/runRepository.ts
:143/:413 — `ORDER BY COALESCE(started_at, -1) DESC, id DESC`: every collapse-to-one
query names a TOTAL order, because the primary key ties at timestamp granularity
(their tests: packages/core/tests/db.test.ts:273-284 and :467-483; the seq-variant
is seq DESC, node_id ASC). Our side had pick-one sites whose only tie-break was
filesystem walk order — same-second mtime granularity is routine on coarsely-
timestamped filesystems, so the head of those lists was directory-traversal luck.

Site census at base ddc30ec (anchors re-pinned against that head — the bead's
wake-time line numbers had drifted):
  S1 wf._work_files         — THE ONE mtime walk (banked manifest + harvest share
                              it): must be a TOTAL order mtime DESC, relpath ASC.
  S2 wf._bank_the_corpse    — pick-one = manifest last_written = rows[0]; inherits
                              S1's total order and must show it deterministically.
  S3 wf._resume_hint_block  — dead-attempt inventory: the work pick must ride S1's
                              ONE walk; the attempt-log pick is mtime DESC with the
                              spawn index (attempt number) as tie-break.
  S4 wfcommon.iter_run_dirs — enumeration whose pick-one is first-seen: the NAME is
                              the total order (dir-entry names are unique per root),
                              cross-root order is the roots-arg order. Already
                              total — pinned, not changed.
  S5 dashboard _list_runs   — row order = S4 name DESC; the by-id `seen` dedupe is
                              a pick-one (first valid row wins). Pinned.
  S6 door._library_rows     — name pick-one = first-seen: roots-arg order (resolved
                              before legacy, F1 #14), general/ group before the
                              bare-root group, name ASC within a group. Pinned.
  S7 door._lane_entry       — incumbent pick = resolved-root entry wins over the
                              legacy twin; one file per key by hash, so no
                              within-root tie exists. Pinned.
  S8 wfcommon.find_run      — run-by-name pick = roots [resolved, legacy], first
                              dir that yields a view; twin id across roots
                              resolves to the resolved side. Pinned.
  S9 wfcommon.seat_wait_view— oldest-wait pick over one node's open waits: bare
                              min(since) let same-stamp ties fall to dict-insertion
                              (ledger-scan) order; the fix is since ASC, str(idx)
                              ASC (index unique within the node, key cannot tie).
  S10 wfcommon.current_attempt — max(recent) over (last_activity, title, desc):
                              already total — the session title is dict-unique —
                              pinned so a future key edit can't reintroduce a tie.
  S11 door.act_library hint — "drop the rarest term (X)": bare min(counts) broke
                              ties on the caller's query-term order (same corpus,
                              different ask, different advice); count ASC, term ASC
                              makes the advice query-order-invariant.
  S12 door.act_status seat_wait row cap — first-non-None cap over a dict's values
                              was insertion order; the fix scans sorted(sw) (node
                              ids unique). The line is exercised verbatim by
                              tests/test_seat_wait_status_833.py S1 (row.cap==4),
                              which pins it in the suite; no duplicate fixture here.

Graph-declaration-order scheduler picks (wf.py gate next(), the dashboard's
pending-gate next(), the consolidate-partner next()) are deterministic in the
graph bytes — the DAG executes the graph's own enumeration — so they are NOT
data-collapses under this law; each carries a because-comment naming the
declaration-order contract instead of a synthetic fixture.

S1-S3, S9 and S11 are RED at base (traversal/insertion/query-order tiebreak
under adversarial order) and flip with the fix; S4-S8, S10 and S12 pin contracts
that are already total — the AGENTS.md rule line (4c rule 12) is what keeps them
that way.

Standalone script (NOT pytest). Run: python3 tests/test_tiebreak_law_1n7gx.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import importlib
from pathlib import Path
from unittest.mock import patch

_tmp = tempfile.TemporaryDirectory()
ROOT = Path(_tmp.name) / "estate"
HOME, RES, LEG = ROOT / "home", ROOT / "resolved", ROOT / "legacy"
for d in (HOME, RES, LEG):
    d.mkdir(parents=True)
# #71 law: sandboxed homes only — the shelf is live production. settings.runs_root
# (config.yaml) splits the RESOLVED root from the RAW-env legacy launch root, the
# same profile-scoped-host shape F1 #14 made every pick-one read model cross-root.
(HOME / "config.yaml").write_text(
    "plugins:\n  entries:\n    hermes-workflows:\n      settings:\n        runs_root: %s\n" % RES)
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(LEG)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import wf                     # noqa: E402
import wfcommon as C          # noqa: E402
door = importlib.import_module("__init__")   # noqa: E402
import importlib.util         # noqa: E402
_spec = importlib.util.spec_from_file_location(
    "hwapi_tiebreak_1n7gx", Path(__file__).resolve().parent.parent / "dashboard" / "plugin_api.py")
api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api)

ok, checks = True, []
def check(label, cond, detail=""):
    global ok
    checks.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and bool(cond)

T0, T1 = 1700000000.0, 1700000001.0
def stamp(p, t):
    p.write_text(p.name)
    os.utime(p, (t, t))

def adversarial_rglob(order):
    """Return a Path.rglob replacement that yields the fixture files in `order`
    (the filesystem's own readdir order is not reproducible; the LAW under test
    must not depend on it either — so the input order is forced adversarially:
    reverse of the expected output among the mtime ties)."""
    def patched(self, pattern):
        for name in order:
            p = self / name
            if p.is_file():
                yield p
    return patched


# ---------------------------------------------------------------- S1 _work_files
def s1():
    run = RES / "s1"
    wd = wf.child_work_dir(run, {"id": "solo"}, None)
    stamp(wd / "b.txt", T0)
    (wd / "sub").mkdir()
    stamp(wd / "sub" / "z.txt", T0)
    stamp(wd / "a.txt", T0)
    stamp(wd / "new.txt", T1)
    adv = adversarial_rglob(["b.txt", "sub/z.txt", "a.txt", "new.txt"])
    with patch.object(Path, "rglob", adv):
        wd2, files = wf._work_files(run, {"id": "solo"}, None)
    got = [f.relative_to(wd2).as_posix() for f in files]
    want = ["new.txt", "a.txt", "b.txt", "sub/z.txt"]   # as_posix string ASC: b < sub
    check("S1 wf._work_files total order (mtime DESC, relpath ASC)",
          got == want, f"got {got} want {want}")


# ------------------------------------------------------------ S2 _bank_the_corpse
def s2():
    run = RES / "s2"
    (run / "nodes").mkdir(parents=True)
    wd = wf.child_work_dir(run, {"id": "banked"}, None)
    stamp(wd / "b.txt", T0)
    stamp(wd / "a.txt", T0)
    stamp(wd / "fresh.txt", T1)
    adv = adversarial_rglob(["b.txt", "a.txt", "fresh.txt"])
    with patch.object(Path, "rglob", adv):
        corpus = wf._bank_the_corpse(run, {"id": "banked"}, None, 0, "tail")
    man = json.loads((Path(corpus) / "manifest.json").read_text()) if corpus else {}
    got = [row["path"] for row in man.get("files", [])]
    want = ["fresh.txt", "a.txt", "b.txt"]
    check("S2 banked manifest rows + last_written follow the ONE total order",
          got == want and man.get("last_written") == "fresh.txt",
          f"got {got} last_written={man.get('last_written')} want {want}")


# ---------------------------------------------------------- S3 _resume_hint_block
def s3():
    run = RES / "s3"
    (run / "logs").mkdir(parents=True)
    wd = wf.child_work_dir(run, {"id": "hint"}, None)
    stamp(wd / "b.txt", T0)
    stamp(wd / "a.txt", T0)
    stamp(run / "logs" / "hint.a1.log", T0)
    stamp(run / "logs" / "hint.a2.log", T0)
    adv = adversarial_rglob(["b.txt", "a.txt"])
    real_glob = Path.glob
    def logs_ascending_glob(self, pattern):
        out = list(real_glob(self, pattern))
        out.sort(key=lambda p: p.name)   # a1 before a2: adversarial vs the law
        return iter(out)
    with patch.object(Path, "rglob", adv), patch.object(Path, "glob", logs_ascending_glob):
        block = wf._resume_hint_block(run, {"id": "hint"}, None)
    entries = [l[2:].split(" size=")[0] for l in block.splitlines()
               if l.startswith("- ") and " size=" in l]
    work_heads = [e for e in entries if e.endswith((".txt",))]
    log_heads = [e for e in entries if ".a" in Path(e).name and Path(e).name.endswith(".log")]
    check("S3 resume inventory: work pick rides the ONE walk, attempt-log pick is mtime DESC,attempt DESC",
          work_heads[:1] == [str(wd / "a.txt")] and log_heads == [str(run / "logs" / "hint.a2.log"),
                                                                  str(run / "logs" / "hint.a1.log")],
          f"work_heads={work_heads[:1]} log_heads={log_heads} (a.txt first; a2 before a1)")


# --------------------------------------------------------------- S4 iter_run_dirs
def s4():
    ra, rb = RES / "s4a", RES / "s4b"
    for root, names in ((ra, ["z1", "m5", "a2"]), (rb, ["b0"])):
        for n in names:
            (root / n).mkdir(parents=True)
    (ra / ".seats").mkdir()
    (ra / "notadir").write_text("x")
    asc = [p.name for p in C.iter_run_dirs([ra, rb])]
    desc = [p.name for p in C.iter_run_dirs([ra, rb], reverse=True)]
    cross = [p.name for p in C.iter_run_dirs([rb, ra], reverse=True)]
    check("S4 iter_run_dirs: name is the total order within a root; roots-arg order across roots",
          asc == ["a2", "m5", "z1", "b0"] and desc == ["z1", "m5", "a2", "b0"]
          and cross == ["b0", "z1", "m5", "a2"],
          f"asc={asc} desc={desc} cross={cross}")
    # first-seen wins across mirror roots (same realpath), and the surviving
    # path is the FIRST root's — the dedupe pick is roots-arg order, never
    # readdir luck (name order within each root is total: dir-entry names are
    # unique per root, so the sort key has no ties).
    mirror = RES / "s4-mirror"
    mirror.symlink_to(ra.resolve())
    out_paths = list(C.iter_run_dirs([mirror, ra]))
    z1s = [p for p in out_paths if p.name == "z1"]
    check("S4b iter_run_dirs dedupes same realpath; the surviving path is the first root's",
          len(z1s) == 1 and z1s[0] == mirror / "z1", f"z1s={[str(p) for p in z1s]}")


# ---------------------------------------------------------- S5 dashboard _list_runs
def mkrun(root, rid, nodes=1):
    r = root / rid
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps(
        {"name": rid, "nodes": [{"id": f"n{i}", "type": "agent", "goal": "g"} for i in range(nodes)]}))
    (r / "run.json").write_text(json.dumps({"concurrency": 1}))
    (r / "events.jsonl").write_text(json.dumps(
        {"ts": "2026-10-23T00:00:00Z", "event": "run.start"}) + "\n")
    return r

def s5():
    mkrun(RES, "run-z", 1)
    mkrun(RES, "run-a", 2)          # the incumbent twin (resolved root) — 2 nodes
    mkrun(LEG, "run-a", 5)          # same-id twin under the legacy root — 5 nodes
    (RES / "run-m").mkdir()         # torn dir: no graph.json -> never a row
    out = api._list_runs()
    ids = [r["id"] for r in out["runs"]]
    row_a = [r for r in out["runs"] if r["id"] == "run-a"]
    check("S5 dashboard run list: rows name-DESC; same-id twin dedupes to one row",
          ids == ["run-z", "run-a"], f"ids={ids}")
    check("S5b same-id twin: first-seen (resolved root) wins, exactly one row",
          len(row_a) == 1 and row_a[0]["nodes_total"] == 2,
          f"rows={[(r['id'], r['nodes_total']) for r in out['runs']]}")
    check("S5c torn dir never lands a row", "run-m" not in ids, f"ids={ids}")


# ------------------------------------------------------------- S6 _library_rows
def s6():
    lib_r, lib_l = RES / "library", LEG / "library"
    (lib_r / "general").mkdir(parents=True)
    lib_l.mkdir(parents=True)
    def g(name, nodes):
        return {"name": name, "nodes": [{"id": f"n{i}", "type": "agent", "goal": "g"} for i in range(nodes)]}
    (lib_r / "alpha.json").write_text(json.dumps(g("RES-alpha", 2)))
    (lib_r / "beta.json").write_text(json.dumps(g("beta", 1)))
    (lib_r / "general" / "gamma.json").write_text(json.dumps(g("gamma", 1)))
    (lib_l / "alpha.json").write_text(json.dumps(g("LEG-alpha", 7)))   # twin: must LOSE
    (lib_l / "delta.json").write_text(json.dumps(g("delta", 1)))
    rows, skipped, quarantined = door._library_rows()
    names = [r["name"] for r in rows]
    alpha = [r for r in rows if r["name"] == "alpha"]
    check("S6 library pick-one: general group first, then name ASC; resolved root wins the twin name",
          names == ["general/gamma", "alpha", "beta", "delta"]
          and len(alpha) == 1 and alpha[0]["nodes"] == 2,
          f"names={names} alpha={alpha}")


# ---------------------------------------------------------------- S7 _lane_entry
def s7():
    key = "tiebreak/lane"
    stem = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    (RES / "lanes").mkdir(parents=True)
    (LEG / "lanes").mkdir(parents=True)
    (RES / "lanes" / f"{stem}.json").write_text(json.dumps({"lane_key": key, "run_id": "RES-run"}))
    (LEG / "lanes" / f"{stem}.json").write_text(json.dumps({"lane_key": key, "run_id": "LEG-run"}))
    entry, err = door._lane_entry(key)
    check("S7 lane incumbent pick: resolved-root entry beats the legacy twin; no error",
          err is None and (entry or {}).get("run_id") == "RES-run", f"{entry} {err}")
    (RES / "lanes" / f"{stem}.json").write_text(json.dumps({"lane_key": "evil", "run_id": "X"}))
    entry2, err2 = door._lane_entry(key)
    check("S7b mismatched lane_key in the winning row refuses, never falls through",
          entry2 is None and err2 == {"error": "lane_key hash collision"}, f"{entry2} {err2}")
    (RES / "lanes" / f"{stem}.json").unlink()
    entry3, err3 = door._lane_entry(key)
    check("S7c legacy-only twin stays visible (F1 #14)",
          err3 is None and (entry3 or {}).get("run_id") == "LEG-run", f"{entry3} {err3}")


# -------------------------------------------------------------------- S8 find_run
def s8():
    mkrun(RES, "rf-twin", 1)
    mkrun(LEG, "rf-twin", 2)
    check("S8 find_run twin: resolved root wins",
          C.find_run("rf-twin") == RES / "rf-twin", str(C.find_run("rf-twin")))
    shutil.rmtree(RES / "rf-twin")
    (RES / "rf-twin").mkdir()                       # torn: no state to yield
    check("S8b find_run twin, resolved side torn: first dir that YIELDS A VIEW wins (legacy)",
          C.find_run("rf-twin") == LEG / "rf-twin", str(C.find_run("rf-twin")))
    check("S8c unknown id answers the resolved path (create/resume shape)",
          C.find_run("rf-nope") == RES / "rf-nope", str(C.find_run("rf-nope")))


# ------------------------------------------------------------ S9 seat_wait_view
def s9():
    T = "2026-10-23T00:00:00+00:00"
    # Two open waits with the SAME since stamp (same-second events are routine):
    # the dict is written idx-2-first so insertion order and the law DISAGREE —
    # insertion would show idx 2's cap/spawn, the total order shows idx 0's.
    per = {2: {"since": T, "cap": 9, "spawn": 7},
           0: {"since": T, "cap": 4, "spawn": 1},
           1: {"since": "2026-10-23T00:00:05+00:00", "cap": 4, "spawn": 2}}
    v = C.seat_wait_view(per, now_s=1761177660.0)
    check("S9 seat_wait_view oldest pick: since ASC, str(idx) ASC (never dict-insertion)",
          v["since"] == T and v["cap"] == 4 and v["spawn"] == 1 and v["waiting"] == [0, 1, 2],
          str(v))


# ------------------------------------------------------------ S10 current_attempt
def s10():
    # The max key (last_activity, title, desc): title is the live-dict key, so
    # it is unique and the key cannot tie. Same-activity twins resolve to the
    # lexically-greater title deterministically — pinned so a future key edit
    # (e.g. dropping title from the tuple) trips a test, not a flapping card.
    cm = {"s": {"sessions": {"s#a1": {"last_activity": 100, "last_desc": "d-s"}}},
          "t": {"sessions": {"t#a1": {"last_activity": 100, "last_desc": "d-t"}}}}
    out = C.current_attempt(cm, [{"skey": "t#a1"}, {"skey": "s#a1"}])
    check("S10 current_attempt max is total by construction (unique session title in key)",
          out["live"] == 2 and out["last_activity"] == 100 and out["last_desc"] == "d-t",
          str(out))


# ------------------------------------------------------------- S11 act_library
def s11():
    # Same corpus as S6's root; two tagged entries, alpha and beta, count 1 each,
    # never co-occurring. The rarest-term advice must NOT depend on the order the
    # caller typed its tags: both queries answer with the SAME term, and the law
    # says which (term ASC).
    lib_r = RES / "library"
    def tagged(name, tag):
        (lib_r / f"{name}.json").write_text(json.dumps(
            {"meta": {"tags": [tag]},
             "graph": {"name": name, "nodes": [{"id": "n0", "type": "agent", "goal": "g"}]}}))
    tagged("tie-alpha", "alpha")
    tagged("tie-beta", "beta")
    h1 = door.act_library({"tags": ["beta", "alpha"]}).get("hint", "")
    h2 = door.act_library({"tags": ["alpha", "beta"]}).get("hint", "")
    check("S11 library rarest-term advice: count ASC, term ASC — query-order invariant",
          h1 == h2 and "rarest term (alpha)" in h1, f"h1={h1!r} h2={h2!r}")


for fn in (s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11):
    fn()
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
