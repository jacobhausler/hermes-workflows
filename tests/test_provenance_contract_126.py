#!/usr/bin/env python3
"""est-syim (#126) regression pins: DEFAULT-ON save provenance (owner ruling 2026-10-15
retires the RATIFY F5 opt-in) + the machine-readable graph-level `run_context` contract.

Pinned laws:
  T1 every save stamps provenance {owner, version, source, saved_at, source_digest} —
     the DEFAULT path (no source arg, default profile) lands all five keys.
  T2 contract shape validated at save: unknown key / bad identifier / declared-but-
     unreferenced required key -> refused, nothing shelved; well-formed contracts save.
  T3 contract enforced at run launch BEFORE any run write: missing required keys reject
     typed (error_type=missing_run_context_keys, missing_run_context_keys enumerated);
     a seed binding against a contract graph rejects typed (run_context_contract_seed).
  T4 contract defaults fill a silent launch (goal rendered); an explicit binding wins.
  T5 golden-solo stability: a pre-existing BARE entry (no provenance) loads and lists
     with the exact legacy row key-set — verbatim, unmigrated; a legacy four-key
     provenance entry lists without a fabricated `version`.
Standalone (no pytest), house style. #71 law: WF_RUNS_ROOT + wf_test_isolation pin the
shelf so nothing here can touch the real estate library.
"""
import importlib.util, json, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " if cond is False else "SKIP ") + label
          + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)


sys.path.insert(0, "/opt/hermes")
sys.path.insert(0, str(BUILD))
spec = importlib.util.spec_from_file_location("hw126", str(BUILD / "__init__.py"))
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso  # noqa: E402
_iso.install(door)

PROV_KEYS = {"owner", "version", "source", "saved_at", "source_digest"}
LANE_ENV_KEYS = ("WF_RUNS_ROOT", "HERMES_WF_RUN_ID", "HERMES_WF_RUN_DIR")

PLAIN = {"name": "plain-probe", "nodes": [
    {"id": "a", "type": "agent", "goal": "Read the target and return findings."}]}
CONTRACT = {"name": "contract-probe",
            "nodes": [{"id": "a", "type": "agent", "goal": "Process {run.target} and report."}]}


def contract_graph(**rc):
    return dict(CONTRACT, run_context=rc)


def lib_rows(resp):
    for v in resp.values():
        if isinstance(v, list) and all(isinstance(r, dict) for r in v) and any("name" in r for r in v):
            return v
    return []


with tempfile.TemporaryDirectory(prefix="prov126-") as td:
    sandbox = Path(td)
    saved_env = {k: os.environ.get(k) for k in LANE_ENV_KEYS}
    try:
        os.environ["WF_RUNS_ROOT"] = str(sandbox / "runs")
        os.environ.pop("HERMES_WF_RUN_ID", None)
        os.environ.pop("HERMES_WF_RUN_DIR", None)
        (sandbox / "runs" / "library").mkdir(parents=True)
        # T4 launches run the whole door+runner path against the hermetic fake.
        os.environ["HERMES_WF_HERMES_BIN"] = str(HERE / "fixtures" / "11-golden-fake.py")
        os.environ["GOLDEN_FAKE"] = str(HERE / "fake")
        (sandbox / "safe").mkdir()
        os.environ["HERMES_WRITE_SAFE_ROOT"] = str(sandbox / "safe")

        # ---- T1: default-path stamping (no source arg, default profile) ----
        r = json.loads(door.handle({"action": "save", "graph": PLAIN, "name": "plain-probe"}))
        check("T1a plain save lands", r.get("saved") == "plain-probe", json.dumps(r)[:200])
        entry = json.loads((sandbox / "runs" / "library" / "plain-probe.json").read_text())
        prov = entry.get("provenance") or {}
        check("T1b provenance stamped on a bare save (no source arg)",
              isinstance(entry.get("provenance"), dict), json.dumps(entry)[:160])
        check("T1c exact five keys", set(prov) == PROV_KEYS, json.dumps(sorted(prov)))
        check("T1d owner defaults to launcher profile",
              prov.get("owner") == door._common.launcher_profile(), repr(prov.get("owner")))
        check("T1e version always present (plugin release)",
              isinstance(prov.get("version"), str) and bool(prov.get("version").strip()),
              repr(prov.get("version")))
        check("T1f source null on the default path", prov.get("source") is None)
        check("T1g saved_at + source_digest present",
              bool(prov.get("saved_at")) and bool(prov.get("source_digest")))

        # ---- T2: contract validation at save ----
        b1 = json.loads(door.handle({"action": "save", "graph": contract_graph(required=["target"], bogus=1), "name": "c-bad"}))
        check("T2a unknown contract key refused at save",
              "error" in b1 and "run_context" in json.dumps(b1), json.dumps(b1)[:220])
        b2 = json.loads(door.handle({"action": "save", "graph": contract_graph(required=["9bad!"]), "name": "c-bad"}))
        check("T2b non-identifier required key refused",
              "error" in b2 and "run_context" in json.dumps(b2), json.dumps(b2)[:160])
        b3 = json.loads(door.handle({"action": "save", "graph": contract_graph(required=["nosuchkey"]), "name": "c-bad"}))
        check("T2c declared-but-unreferenced required key refused at save",
              "error" in b3 and "run_context" in json.dumps(b3), json.dumps(b3)[:240])
        check("T2e nothing shelved behind a refused contract",
              not (sandbox / "runs" / "library" / "c-bad.json").exists())
        g = json.loads(door.handle({"action": "save", "graph": contract_graph(required=["target"]), "name": "c-good"}))
        check("T2d well-formed contract saves", g.get("saved") == "c-good", json.dumps(g)[:160])

        # ---- T3: typed refusal at run launch, before any run write ----
        runs = lambda: {p.name for p in (sandbox / "runs").iterdir()
                        if p.is_dir() and p.name != "library"}
        before = runs()
        m = json.loads(door.handle({"action": "run", "from": "c-good"}))
        check("T3a missing required keys refuse the run (typed)",
              m.get("error_type") == "missing_run_context_keys", json.dumps(m)[:260])
        check("T3b missing keys enumerated",
              m.get("missing_run_context_keys") == ["target"], json.dumps(m)[:160])
        check("T3c refused launch wrote NO run dir", runs() == before)
        s = json.loads(door.handle({"action": "run", "from": "c-good", "run_context": "seed text"}))
        check("T3d seed binding cannot satisfy a contract (typed)",
              s.get("error_type") == "run_context_contract_seed", json.dumps(s)[:200])
        check("T3e seed refusal also wrote no run dir", runs() == before)

        # ---- T4: defaults fill a silent launch; binding overrides ----
        d = json.loads(door.handle({"action": "save",
                                    "graph": contract_graph(required=["target"], defaults={"target": "main"}),
                                    "name": "c-def"}))
        check("T4a contract+defaults saves", d.get("saved") == "c-def", json.dumps(d)[:160])
        started = json.loads(door.handle({"action": "run", "from": "c-def"}))
        rid = started.get("run_id")
        check("T4b defaults-satisfied launch lands", bool(rid), json.dumps(started)[:200])
        if rid:
            gj = json.loads((sandbox / "runs" / rid / "graph.json").read_text())
            goal = gj["nodes"][0]["goal"]
            check("T4c default rendered into goal",
                  "Process main" in goal and "{run.target}" not in goal, goal[:120])
            door.handle({"action": "stop", "run_id": rid})
        st2 = json.loads(door.handle({"action": "run", "from": "c-def",
                                      "run_context": {"target": "topic-branch"}}))
        rid2 = st2.get("run_id")
        check("T4d explicit binding accepted", bool(rid2), json.dumps(st2)[:200])
        if rid2:
            gj2 = json.loads((sandbox / "runs" / rid2 / "graph.json").read_text())
            check("T4e binding overrides the contract default",
                  "Process topic-branch" in gj2["nodes"][0]["goal"])
            door.handle({"action": "stop", "run_id": rid2})

        # ---- T5: golden-solo stability — pre-existing entries load verbatim ----
        legacy_bare = {"name": "legacy-entry", "description": "pre-1.4 bare entry",
                       "nodes": [{"id": "a", "type": "agent", "goal": "Legacy work."}]}
        (sandbox / "runs" / "library" / "legacy-entry.json").write_text(
            json.dumps(legacy_bare, indent=2))
        legacy_prov = json.loads(json.dumps(legacy_bare))
        legacy_prov["provenance"] = {"owner": "gh-dispatch", "source": "repo:old",
                                     "saved_at": "2026-10-01T00:00:00+00:00",
                                     "source_digest": "0" * 64}
        (sandbox / "runs" / "library" / "legacy-prov-entry.json").write_text(
            json.dumps(legacy_prov, indent=2))
        lib = json.loads(door.handle({"action": "library"}))
        rows = {r.get("name"): r for r in lib_rows(lib)}
        rb = rows.get("legacy-entry")
        check("T5a legacy bare entry lists with the exact legacy row key-set",
              rb is not None
              and set(rb) == {"name", "nodes", "gates", "fanouts", "description"},
              json.dumps(rb)[:220])
        rp = rows.get("legacy-prov-entry")
        check("T5b legacy four-key provenance entry lists without a fabricated version",
              rp is not None and "version" not in rp and rp.get("owner") == "gh-dispatch",
              json.dumps(rp)[:220])
        check("T5c entry bytes untouched by the read",
              json.loads((sandbox / "runs" / "library" / "legacy-entry.json").read_text())
              == legacy_bare)
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        for k in ("HERMES_WF_HERMES_BIN", "GOLDEN_FAKE", "HERMES_WRITE_SAFE_ROOT"):
            os.environ.pop(k, None)

print("test_provenance_contract_126:", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
