"""est-dv8q4 (PR-6 shelf tooling): the library digest re-check verb and the
shelf-census husks bucket, both pinned from the s3_engine council findings.

Door (`library check:true`) pins:
  D1  flag absent -> the listing carries NO `check` key (golden-bytes law:
      the response is byte-identical to the pre-feature shape);
  D2  a fresh save recomputes clean (checked/ok, drifted empty);
  D3  a hand-edit of the shelf bytes drifts: stored != recomputed, and
      source_digest_match stays null when no source-side measurement exists;
  D4  source drift: shelf matches its stamp but the author source file no
      longer does -> drifted with source_digest_match False (the shelf-vs-
      author verb — a re-save would have re-stamped it; a hand-touched
      source only this check finds);
  D5  a pre-provenance entry counts unstamped; a set-but-unreadable source
      counts unresolvable_source and is NEVER invented into a match (rule 8);
  D6  the check is read-only (entry bytes and the name-filtered entry
      branch included) and a non-boolean check refuses by name.

Census (`scripts/shelf-census.py`) pins (probe injected, no real pgrep):
  H1  an old, exit-less, unprobed run dir is a husk row {run_dir, age_s,
      last_log_age_s}; a live-probe match is never a husk, and the match is
      EXACT-argv-token (substring false-blames a run whose id prefixes a
      live one's); an inside-the-grace dir is in_grace, not a husk;
  H2  held verdicts count gate_held and stay open (a gate park is resumable);
  H3  the canonical counters block and the one-line fleet report agree, with
      every number defined by its exact query;
  H4  probe self-exclusion: the probe's own bash line is excluded; the /proc
      predicate matches the door's spawn argv shape only.

Stdlib only; no runner, no network.
"""
import atexit, io, importlib.util, json, os, shutil, sys, tempfile, time
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
tmp_dir = tempfile.TemporaryDirectory(prefix=".tmp-dv8q4-", dir=HERE / "tests",
                                      ignore_cleanup_errors=True)
atexit.register(lambda: shutil.rmtree(tmp_dir.name, ignore_errors=True))
os.environ["HERMES_HOME"] = tmp_dir.name
os.environ["WF_RUNS_ROOT"] = os.path.join(tmp_dir.name, "workflows")
door = importlib.import_module("__init__")
import wf_test_isolation as _iso; _iso.install(door)

fails = 0
def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  -- {detail}" if detail and not cond else ""))
    fails += 0 if cond else 1

def call(**a):
    return json.loads(door.handle(a))

LIB = Path(os.environ["WF_RUNS_ROOT"]) / "library"
NODES = [{"id": "a", "type": "agent", "goal": "LIST: go"}]

def lib_bytes():
    return {p.name: p.read_bytes() for p in sorted(LIB.glob("*.json"))}

# --- fixtures ----------------------------------------------------------------
check("D0 save returns", call(action="save", graph={"name": "dv-drift", "nodes": NODES},
                              description="drift lane entry").get("saved") == "dv-drift")
SRC = Path(tmp_dir.name) / "author-source.json"
SRC.write_text(json.dumps({"name": "dv-source", "nodes": NODES}), encoding="utf-8")
check("D0b save with local source returns",
      call(action="save", graph={"name": "dv-source", "nodes": NODES},
           source=str(SRC)).get("saved") == "dv-source")
check("D0c save with URL source returns",
      call(action="save", graph={"name": "dv-url", "nodes": NODES},
           source="https://example.invalid/g.json").get("saved") == "dv-url")
(LIB / "dv-legacy.json").write_text(
    json.dumps({"name": "dv-legacy", "nodes": NODES}), encoding="utf-8")  # pre-#126 bytes

before = lib_bytes()

# --- D1 golden bytes: flag absent, no check key anywhere ---------------------
plain = call(action="library")
check("D1 flag absent -> response carries no check key",
      "check" not in plain and all("check" not in json.dumps(r) for r in plain["library"]),
      json.dumps(plain)[:400])

# --- D2 clean shelf ----------------------------------------------------------
c = call(action="library", check=True)["check"]
check("D2 fresh shelf recomputes clean; URL source honestly unresolvable",
      c["checked"] == 3 and c["ok"] == 3 and c["drifted"] == [] and c["unstamped"] == 1
      and c["unresolvable_source"] == 1, json.dumps(c))
check("D2b check is read-only (entry bytes unchanged)", lib_bytes() == before)

# --- D3 shelf hand-edit drifts ------------------------------------------------
p = LIB / "dv-drift.json"
obj = json.loads(p.read_text(encoding="utf-8"))
obj["graph"]["nodes"][0]["goal"] = "LIST: go (hand-edited)"
p.write_text(json.dumps(obj), encoding="utf-8")
c = call(action="library", check=True)["check"]
row = next((d for d in c["drifted"] if d["id"] == "dv-drift.json"), None)
check("D3 hand-edited shelf drifts: stored != recomputed, match null (no source)",
      c["checked"] == 3 and c["ok"] == 2 and row is not None
      and row["stored"] != row["recomputed"] and row["source_digest_match"] is None,
      json.dumps(c))

# --- D4 author-source drift (shelf bytes still match the stamp) ---------------
SRC.write_text(json.dumps({"name": "dv-source",
                           "nodes": [dict(NODES[0], goal="LIST: go upstream-edited")]}),
               encoding="utf-8")
c = call(action="library", check=True)["check"]
row = next((d for d in c["drifted"] if d["id"] == "dv-source"), None)
check("D4 drifted-by-source row: shelf recompute == stored, source_digest_match False",
      c["ok"] == 1 and row is not None and row["stored"] == row["recomputed"]
      and row["source_digest_match"] is False, json.dumps(c))
ids = [d["id"] for d in c["drifted"]]
check("D4b drifted is name-ASC (collapse-to-one)", ids == sorted(ids), json.dumps(ids))

# --- D5/D6 entry branch, filter honesty, typed refusal ------------------------
e = call(action="library", name="dv-url", check=True)
check("D6 name-filtered entry branch echoes the check block for that one row",
      "entry" in e and e["check"] == {"checked": 1, "ok": 1, "drifted": [],
                                      "unstamped": 0, "unresolvable_source": 1},
      json.dumps(e.get("check")))
check("D6b non-boolean check refuses by name",
      call(action="library", check="yes") == {"error": "check must be a boolean"})
after = lib_bytes()
check("D6c the check never rewrites entry bytes (untouched entries identical)",
      after["dv-url.json"] == before["dv-url.json"]
      and after["dv-legacy.json"] == before["dv-legacy.json"],
      "only my D3/D4 edits moved bytes, no check call did")
check("D6d flag-off listing after all checks == flag-off listing before",
      call(action="library") == plain)

# ============================ census leg =====================================
spec = importlib.util.spec_from_file_location("shelf_census", HERE / "scripts" / "shelf-census.py")
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)
_real_probe = census.live_runner_cmdlines()  # BEFORE the seam is replaced: the real pgrep//proc path

root = Path(tmp_dir.name) / "wfroot"
NOW = time.time()

def run_dir(rid, exit_reason=None, age=0.0, log_age=None):
    d = root / rid
    d.mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"name": rid}), encoding="utf-8")
    if exit_reason is not None:
        (d / "runner_exit.json").write_text(json.dumps({"reason": exit_reason}), encoding="utf-8")
    if log_age is not None:
        (d / "runner.log").write_text("lap\n", encoding="utf-8")
        os.utime(d / "runner.log", (NOW - log_age, NOW - log_age))
    if age:
        os.utime(d, (NOW - age, NOW - age))
    return d

d_done = run_dir("r-done", exit_reason="done")
d_held = run_dir("r-held", exit_reason="held at g1")
d_husk = run_dir("r-husk", age=7200, log_age=3600)
d_live = run_dir("r-live", age=7200)          # prefix of the probed id: substring would false-blame
d_liveX = run_dir("r-liveX", age=7200)        # the probed run
d_young = run_dir("r-young")

census.live_runner_cmdlines = lambda: ["4242 python3 /opt/hw/wf.py run r-liveX"]

out = Path(tmp_dir.name) / "census.json"
argv = ["shelf-census.py", "--wf-root", str(root), "--out", str(out),
        "--no-refs", "--husk-grace", "3600"]
buf = io.StringIO()
_real_argv = sys.argv
sys.argv = argv
try:
    with redirect_stdout(buf):
        try:
            census.main()
            code = 0
        except SystemExit as e:
            code = e.code or 0
finally:
    sys.argv = _real_argv
res = json.loads(out.read_text(encoding="utf-8"))
cc = res["counters"]
check("H1 husk rows name the two dead no-exit dirs with age + log age",
      code == 0 and [h["run_dir"] for h in res["husks"]] == [str(d_husk), str(d_live)]
      and abs(res["husks"][0]["age_s"] - 7200) < 5
      and abs(res["husks"][0]["last_log_age_s"] - 3600) < 5, json.dumps(res["husks"]))
check("H2 gate park counts gate_held and stays open",
      cc["gate_held"] == 1 and "held" in cc["by_status"], json.dumps(cc))
check("H3 canonical counters block matches the exact-query definitions",
      cc["total"] == 6 and cc["by_status"] == {"done": 1, "held": 1, "husk": 2,
                                               "running": 1, "in_grace": 1}
      and cc["open_total"] == 5 and cc["live_runners"] == 1 and cc["husks"] == 2,
      json.dumps(cc))
check("H3b the one-line fleet report agrees with the block",
      "counters: open_total=5 live_runners=1 husks=2 gate_held=1" in buf.getvalue(),
      buf.getvalue())
check("H4 probe self-exclusion drops the probe's own shell line",
      census._is_probe_shell("bash -c pgrep -af wf.py run") and not
      census._is_probe_shell("python3 /opt/hw/wf.py run r-liveX"))
check("H4b /proc predicate matches the door's spawn argv shape only",
      census._runner_in_argv(["python3", "/opt/hw/wf.py", "run", "r1"]) and not
      census._runner_in_argv(["bash", "-c", "wf.py run"]) and not
      census._runner_in_argv(["python3", "/opt/hw/wf.py", "validate"]))
check("H4c the real probe path runs clean against the live system (list in, no crash)",
      isinstance(_real_probe, list))

print("FAIL" if fails else "ALL PASS")
sys.exit(1 if fails else 0)
