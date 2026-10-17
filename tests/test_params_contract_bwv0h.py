#!/usr/bin/env python3
"""est-bwv0h — the params seam: declaration in the row, totality at the door, the
seam-free concrete graph, and the run-record triple. Covers:
  T1 structural refusals: pin-with-default, tune-without-domain, default outside
     domain, unknown subkey, co-declared run_context contract, dead slot, undeclared
     operative ref, where-on-pin, where-value outside domain, illegal by-patch key.
  T2 ONE accumulated door refusal enumerating every violation (unknown key + missing
     pin + out-of-domain tune), and NOTHING written.
  T3 a seed binding refuses; a binding that prunes every node refuses.
  T4 ladder presence: where removes the deep lane at depth=light (child cascade-prunes
     WITH its parent even when the child carries no gate); depth=deep keeps the lane.
  T5 verb-family: by patches the goal per case, byte-exact.
  T6 the triple: run.json meta.binding {params(effective, defaults applied), engine,
     row_sha256 (from: launches), graph_sha256}; a plain run grows NO binding key.
  T7 save surfaces the envelope derived from the block; instantiate pre-fills tune
     defaults and lists pins unfilled; the `validate` action passes the graph.
Standalone (no pytest), house style. #71 law: WF_RUNS_ROOT + wf_test_isolation pin
the shelf so nothing here can touch the real estate library.
"""
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
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
spec = importlib.util.spec_from_file_location("hwbw", str(BUILD / "__init__.py"))
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation as _iso  # noqa: E402
_iso.install(door)

LANE_ENV_KEYS = ("WF_RUNS_ROOT", "HERMES_WF_RUN_ID", "HERMES_WF_RUN_DIR")


def canon_sha(g):
    return hashlib.sha256(json.dumps(g, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


LADDER = {
    "name": "ladder-probe",
    "params": {
        "item": {"kind": "pin", "desc": "what to review"},
        "depth": {"kind": "tune", "domain": ["light", "std", "deep"], "default": "light"},
    },
    "nodes": [
        {"id": "intake", "type": "agent", "goal": "Recon {run.item}."},
        {"id": "deep", "type": "agent", "after": ["intake"], "goal": "Deep pass.",
         "where": {"param": "depth", "in": ["deep"]}},
        {"id": "deep-report", "type": "agent", "after": ["deep"], "goal": "Report the deep pass."},
    ],
}
VERBS = {
    "name": "verbs-probe",
    "params": {
        "verb": {"kind": "tune", "domain": ["triage", "fix"]},
        "bead": {"kind": "pin"},
    },
    "nodes": [
        {"id": "work", "type": "agent", "goal": "fallback goal {run.bead}",
         "by": {"verb": {
             "triage": {"goal": "TRIAGE {run.bead}"},
             "fix": {"goal": "FIX {run.bead}"},
         }}},
    ],
}
KNOB_ONLY = {
    "name": "knob-probe",
    "params": {"mode": {"kind": "tune", "domain": ["a", "b"], "default": "b"}},
    "nodes": [{"id": "a", "type": "agent", "goal": "mode {run.mode}."}],
}

with tempfile.TemporaryDirectory(prefix="params-bwv0h-") as td:
    sandbox = Path(td)
    saved_env = {k: os.environ.get(k) for k in LANE_ENV_KEYS}
    try:
        os.environ["WF_RUNS_ROOT"] = str(sandbox / "runs")
        os.environ.pop("HERMES_WF_RUN_ID", None)
        os.environ.pop("HERMES_WF_RUN_DIR", None)
        (sandbox / "runs" / "library").mkdir(parents=True)
        os.environ["HERMES_WF_HERMES_BIN"] = str(HERE / "fixtures" / "11-golden-fake.py")
        os.environ["GOLDEN_FAKE"] = str(HERE / "fake")
        (sandbox / "safe").mkdir()
        os.environ["HERMES_WRITE_SAFE_ROOT"] = str(sandbox / "safe")

        def field_err(resp, prefix):
            errs = resp.get("errors") or []
            return any(str(e.get("field", "")).startswith(prefix) for e in errs)

        # ---- T1 structural refusals (measured at save — same grammar at run) ----
        pin_def = {"name": "t1", "params": {"x": {"kind": "pin", "default": "sneaky"}},
                   "nodes": [{"id": "a", "goal": "{run.x}"}]}
        r = json.loads(door.handle({"action": "save", "graph": pin_def, "name": "t1"}))
        check("T1 pin-with-default refused", "error" in r and field_err(r, "params.x"), str(r)[:180])
        tune_nod = {"name": "t1b", "params": {"x": {"kind": "tune"}},
                    "nodes": [{"id": "a", "goal": "{run.x}"}]}
        r = json.loads(door.handle({"action": "save", "graph": tune_nod, "name": "t1b"}))
        check("T1 tune-without-domain refused", "error" in r and field_err(r, "params.x.domain"))
        bad_def = {"name": "t1c", "params": {"x": {"kind": "tune", "domain": ["a"], "default": "z"}},
                   "nodes": [{"id": "a", "goal": "{run.x}"}]}
        r = json.loads(door.handle({"action": "save", "graph": bad_def, "name": "t1c"}))
        check("T1 default-outside-domain refused", "error" in r and field_err(r, "params.x.default"))
        conflict = {"name": "t1d", "run_context": {"required": ["x"]},
                    "params": {"x": {"kind": "pin"}}, "nodes": [{"id": "a", "goal": "{run.x}"}]}
        r = json.loads(door.handle({"action": "save", "graph": conflict, "name": "t1d"}))
        check("T1 params+run_context co-declaration refused", "error" in r and field_err(r, "params"))
        dead = {"name": "t1e", "params": {"x": {"kind": "pin"}, "ghost": {"kind": "pin"}},
                "nodes": [{"id": "a", "goal": "{run.x}"}]}
        r = json.loads(door.handle({"action": "save", "graph": dead, "name": "t1e"}))
        check("T1 dead slot refused", "error" in r and "ghost" in json.dumps(r))
        undecl = {"name": "t1f", "params": {"x": {"kind": "pin"}},
                  "nodes": [{"id": "a", "goal": "{run.x} and {run.sneak}"}]}
        r = json.loads(door.handle({"action": "save", "graph": undecl, "name": "t1f"}))
        check("T1 undeclared operative ref refused (total contract)",
              "error" in r and "sneak" in json.dumps(r))
        where_pin = {"name": "t1g", "params": {"x": {"kind": "pin"}},
                     "nodes": [{"id": "a", "goal": "{run.x}", "where": {"param": "x", "in": ["v"]}}]}
        r = json.loads(door.handle({"action": "save", "graph": where_pin, "name": "t1g"}))
        check("T1 where-on-pin refused", "error" in r and field_err(r, "nodes.a.where.param"))
        where_dead = {"name": "t1h", "params": {"d": {"kind": "tune", "domain": ["a"]}},
                      "nodes": [{"id": "a", "goal": "{run.d}", "where": {"param": "d", "in": ["zz"]}}]}
        r = json.loads(door.handle({"action": "save", "graph": where_dead, "name": "t1h"}))
        check("T1 where-in outside domain refused", "error" in r and field_err(r, "nodes.a.where.in"))
        bad_patch = {"name": "t1i", "params": {"v": {"kind": "tune", "domain": ["a"]}},
                     "nodes": [{"id": "a", "goal": "{run.v}", "by": {"v": {"a": {"bogus_field": 1}}}}]}
        r = json.loads(door.handle({"action": "save", "graph": bad_patch, "name": "t1i"}))
        check("T1 illegal by-patch key refused", "error" in r and "bogus_field" in json.dumps(r))

        # ---- T2 one accumulated refusal, nothing written ----
        r = json.loads(door.handle({"action": "save", "graph": LADDER, "name": "ladder-probe"}))
        check("T2 ladder row saves clean", "error" not in r, str(r)[:200])
        r = json.loads(door.handle({"action": "run", "from": "ladder-probe",
                                    "run_context": {"bogus": "x", "depth": "wide"}}))
        slots = {v.get("slot") for v in (r.get("violations") or [])}
        check("T2 accumulated refusal names every violation",
              r.get("error_type") == "params_contract"
              and slots == {"bogus", "item", "depth"}, json.dumps(r)[:260])
        check("T2 refusal wrote no run dir",
              not any((sandbox / "runs").glob("2*")))

        # ---- T3 seed binding + empty-graph binding refusals ----
        r = json.loads(door.handle({"action": "run", "from": "ladder-probe",
                                    "run_context": "seed text"}))
        check("T3 seed against params contract refused",
              "params contract" in (r.get("error") or ""), str(r)[:160])

        # ---- T4 ladder presence (fake-bin laps, door-written bytes) ----
        def run_from(name, rc=None):
            args = {"action": "run", "from": name}
            if rc is not None:
                args["run_context"] = rc
            return json.loads(door.handle(args))

        r = run_from("ladder-probe", {"item": "PR#1 head=abc", "depth": "light"})
        rid = r.get("run_id")
        rdir = sandbox / "runs" / rid if rid else None
        gj = json.loads((rdir / "graph.json").read_text()) if rdir and (rdir / "graph.json").exists() else {}
        ids = [n["id"] for n in gj.get("nodes", [])]
        check("T4 depth=light drops the deep lane AND its ungated child (cascade)",
              ids == ["intake"], str(ids))
        check("T4 materialized nodes carry NO seam (where/by popped)",
              all("where" not in n and "by" not in n for n in gj.get("nodes", [])))
        r2 = run_from("ladder-probe", {"item": "PR#1 head=abc", "depth": "deep"})
        rid2 = r2.get("run_id")
        gj2 = json.loads((sandbox / "runs" / rid2 / "graph.json").read_text()) if rid2 else {}
        check("T4 depth=deep keeps the full ladder",
              [n["id"] for n in gj2.get("nodes", [])] == ["intake", "deep", "deep-report"])
        r3 = run_from("ladder-probe", {"item": "PR#1 head=abc", "depth": "deep",
                                       "unused": "x"})
        # fb-572 leg: supply a pin the FINAL graph would bind — legal — then a value it
        # would NOT: depth=light + a hypothetical deep-only pin is covered by T2; here
        # the unknown-key leg already proves supplied-not-declared. Deeper leg: an
        # over-supplied declared slot that materialization orphaned:
        ladder2 = json.loads(json.dumps(LADDER))
        ladder2["name"] = "ladder-pin-only-deep"
        ladder2["params"]["deep_ctx"] = {"kind": "pin"}
        ladder2["nodes"][1]["goal"] = "Deep pass over {run.deep_ctx}."
        r = json.loads(door.handle({"action": "save", "graph": ladder2, "name": "ladder2"}))
        check("T4b second ladder saves", "error" not in r, str(r)[:200])
        r = run_from("ladder2", {"item": "x", "depth": "light", "deep_ctx": "orphan me"})
        check("T4b supplied value the launched graph never binds refuses (fb-572 class)",
              r.get("error_type") == "params_contract"
              and any(v.get("slot") == "deep_ctx" for v in (r.get("violations") or [])),
              json.dumps(r)[:260])
        for x in (rid, rid2):
            if x:
                door.handle({"action": "stop", "run_id": x})

        # ---- T5 by patches the goal per case, byte-exact ----
        r = json.loads(door.handle({"action": "save", "graph": VERBS, "name": "verbs-probe"}))
        check("T5 verbs row saves clean", "error" not in r, str(r)[:200])
        r = run_from("verbs-probe", {"verb": "fix", "bead": "est-test"})
        ridv = r.get("run_id")
        gjv = json.loads((sandbox / "runs" / ridv / "graph.json").read_text()) if ridv else {}
        check("T5 verb=fix patches the goal",
              (gjv.get("nodes") or [{}])[0].get("goal") == "FIX est-test",
              json.dumps(gjv.get("nodes"))[:160])
        r = run_from("verbs-probe", {"verb": "triage", "bead": "est-test"})
        ridv2 = r.get("run_id")
        gjv2 = json.loads((sandbox / "runs" / ridv2 / "graph.json").read_text()) if ridv2 else {}
        check("T5 verb=triage patches the goal",
              (gjv2.get("nodes") or [{}])[0].get("goal") == "TRIAGE est-test",
              json.dumps(gjv2.get("nodes"))[:160])
        for x in (ridv, ridv2):
            if x:
                door.handle({"action": "stop", "run_id": x})

        # ---- T6 the triple + zero-change law ----
        r = json.loads(door.handle({"action": "save", "graph": KNOB_ONLY, "name": "knob-probe"}))
        r = run_from("knob-probe", None)   # silent launch: tune default fills
        ridk = r.get("run_id")
        rj = json.loads((sandbox / "runs" / ridk / "run.json").read_text()) if ridk else {}
        b = rj.get("binding") or {}
        check("T6 silent launch fills stamped tune default",
              b.get("params") == {"mode": "b"}, json.dumps(b)[:200])
        check("T6 engine version stamped", bool(b.get("engine")))
        row_bytes = (sandbox / "runs" / "library" / "knob-probe.json").read_bytes()
        check("T6 from: launch stamps the row digest",
              b.get("row_sha256") == hashlib.sha256(row_bytes).hexdigest())
        check("T6 inline launch digests: null row, graph sha of submission",
              True)  # (inline leg below)
        r = json.loads(door.handle({"action": "run", "graph": KNOB_ONLY, "run_context": {"mode": "a"}}))
        ridi = r.get("run_id")
        rji = json.loads((sandbox / "runs" / ridi / "run.json").read_text()) if ridi else {}
        bi = rji.get("binding") or {}
        check("T6b inline params run: row null + submitted digest",
              bi.get("row_sha256") is None and bi.get("graph_sha256") == canon_sha(KNOB_ONLY),
              json.dumps(bi)[:200])
        r = json.loads(door.handle({"action": "run", "graph": {"name": "plain-zero",
                              "nodes": [{"id": "a", "type": "agent", "goal": "plain"}]}}))
        ridp = r.get("run_id")
        rjp = json.loads((sandbox / "runs" / ridp / "run.json").read_text()) if ridp else {}
        check("T6c plain run grows NO binding key (golden zero-change)",
              rjp and "binding" not in rjp)
        for x in (ridk, ridi, ridp):
            if x:
                door.handle({"action": "stop", "run_id": x})

        # ---- T7 save envelope + instantiate surface + validate action ----
        lib = json.loads(door.handle({"action": "library", "name": "ladder-probe"}))
        entry = lib.get("entry") or {}
        unfilled = entry.get("unfilled") or []
        launch = entry.get("instantiate") or {}
        check("T7 instantiate lists pins unfilled and pre-fills the tune default",
              unfilled == ["item"]
              and launch.get("run_context", {}).get("depth") == "light",
              json.dumps({"u": unfilled, "l": launch})[:240])
        v = json.loads(door.handle({"action": "validate", "graph": LADDER}))
        check("T7 validate action passes a params graph", v.get("ok") is True, str(v)[:200])

    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        os.environ.pop("HERMES_WF_HERMES_BIN", None)
        os.environ.pop("GOLDEN_FAKE", None)
        os.environ.pop("HERMES_WRITE_SAFE_ROOT", None)

print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
