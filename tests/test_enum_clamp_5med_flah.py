#!/usr/bin/env python3
"""est-flah — unknown enum values clamp at RESOLVE time, never a hard child death.

Verified shapes (haus-keeper report 2026-10-02T16:41Z):
  (1) reasoning:high on a qwen-relay lane hard-400s ("Supported types are xhigh,
      medium, low") — provider_400 is permfail, the node died with zero recourse;
  (2) `hermes chat -t none` warns "Unknown toolsets: none" (and the -z path exits 2
      when EVERY name is invalid) instead of no-op.

The runner law pinned here: at spawn, an unknown reasoning-effort clamps to the
nearest supported value (core clamp_effort's weaker-first law) with ONE warning
naming lane / requested / supported set; an unknown toolset name is dropped with
one warning, and an all-unknown list omits -t entirely (the clean no-op). When the
SERVER's own enum-gate 400 names the vocabulary the lane accepts, the runner
re-drives ONCE with the clamped value instead of a permfail (escape hatch).

CLI-side half (boundary, recorded not patched): the warn+continue lives in core
model_tools._apply_toolset_selection, and the all-invalid -z hard error lives in
hermes_cli/oneshot.py _validate_explicit_toolsets — this repo clamps on the runner
side so the child never spawns into a known death.

Run: PYTHONPATH=/opt/hermes /opt/hermes/.venv/bin/python tests/test_enum_clamp_5med_flah.py
Standalone without core on the path, the toolsets pins assert the documented
pass-through instead (honest degradation — the runner cannot judge what it cannot
import; it never hard-fails).
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
HOME = BUILD / "home-flah"
RUNS = HOME / "workflows"
sys.path.insert(0, str(BUILD.parent))
import wf, wfcommon  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " + label + (f"  {detail}" if detail else "")))
    if not cond: ok = False

CORE = os.path.isdir("/opt/hermes")   # validator availability decides toolsets expectations

# ---------- (a) _nearest_supported: core clamp_effort's law, weaker-first ----------
NS = wf._nearest_supported
check("high on {xhigh,medium,low} -> medium (nearest weaker, never xhigh)",
      NS("high", ["xhigh", "medium", "low"]) == "medium")
check("ultra on {xhigh,medium,low} -> xhigh",
      NS("ultra", ["xhigh", "medium", "low"]) == "xhigh")
check("minimal on {xhigh,medium,low} -> low (supported floor; never escalates up)",
      NS("minimal", ["xhigh", "medium", "low"]) == "low")
check("supported value passes (None = no clamp happened)",
      NS("medium", ["xhigh", "medium", "low"]) is None)
check("bespoke name passes through at resolve (custom providers use them)",
      NS("turbo", ["xhigh", "medium", "low"]) is None)
check("explicit none never clamps (clamping up would switch thinking ON)",
      NS("none", ["xhigh", "medium", "low"]) is None)
check("none excluded as a clamp TARGET (never switches thinking off)",
      NS("high", ["none", "low"]) == "low")
check("empty supported set: no verdict invented",
      NS("high", []) is None and NS("high", None) is None)
check("monotonic: a stronger request never resolves weaker than a weaker one",
      [NS("high", ["low", "medium"]), NS("ultra", ["low", "medium"])]
      == ["medium", "medium"] and NS("medium", ["low", "medium"]) is None)
check("gate-400 marker parses (requested, supported) from the server's own words",
      wf._gate400_parse("hermes -z: agent failed: Error code: 400 - {{'error': {{'message': "
                        "\"Unsupported type: high. Supported types are xhigh, medium, low\", "
                        "'type': 'invalid_request_error'}}}}") == ("high", ["xhigh", "medium", "low"]),
      str(wf._gate400_parse("Unsupported type: high. Supported types are xhigh, medium, low")))
check("non-enum 400 is NOT a gate (no parse)",
      wf._gate400_parse("Error code: 400 - bad request") is None)

# ---------- harness ----------
FAKE = str(BUILD / "fake-flah"); shutil.copy(BUILD / "fake_hermes.py", FAKE); os.chmod(FAKE, 0o755)

def mk(run_id, nodes, meta_extra=None):
    r = RUNS / run_id
    if r.exists(): shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    meta = {"hermes_bin": FAKE, "concurrency": 2, "node_timeout": 60}
    meta.update(meta_extra or {})
    (r / "run.json").write_text(json.dumps(meta))
    return r

def drive(run, env_extra):
    env = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(HOME / f"fake-{run.name}.log"), **env_extra)
    p = subprocess.run([sys.executable, str(BUILD.parent / "wf.py"), "run", str(run)],
                       env=env, capture_output=True, timeout=180, text=True)
    return p

def events(run):
    return [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines() if l.strip()] \
        if (run / "events.jsonl").exists() else []

def record(run, nid):
    return json.loads((run / "nodes" / f"{nid}.json").read_text())

# ---------- (b) e2e resolve-time clamp: lane table (reasoning_lanes) narrower than declared ----------
if HOME.exists(): shutil.rmtree(HOME)
HOME.mkdir(parents=True); RUNS.mkdir(parents=True)
argv_log = HOME / "argv-lane.log"
r = mk("flah-lane", [{"id": "a", "type": "agent", "goal": "GO lane",
                      "model": "qwen38-next", "provider": "qwen", "reasoning": "high"}],
       {"reasoning_lanes": {"qwen": ["xhigh", "medium", "low"]}})
p = drive(r, {"FAKE_ARGV_LOG": str(argv_log), "FAKE_MODE": ""})
rec = record(r, "a")
argv_lines = argv_log.read_text().splitlines() if argv_log.exists() else []
check("e2e resolve: node DONE (never a permfail death)", rec.get("status") == "done",
      f"{rec.get('status')}/{rec.get('error')}")
check("e2e resolve: ONE spawn — clamp happened before the first Popen, no gate-400 round-trip",
      len(argv_lines) == 1, f"{len(argv_lines)} spawns: {argv_lines}")
check("e2e resolve: --reasoning high became --reasoning medium on the child argv",
      argv_lines and "--reasoning medium" in argv_lines[0]
      and "--reasoning high" not in argv_lines[0], str(argv_lines))
cl = [e for e in events(r) if e.get("event") == "node.clamped"]
check("e2e resolve: exactly ONE warning event", len(cl) == 1, str(cl))
if cl:
    check("warning names kind/requested/clamped", cl[0].get("kind") == "reasoning"
          and cl[0].get("requested") == "high" and cl[0].get("clamped") == "medium", str(cl[0]))
    check("warning names the lane and the supported set",
          "model=qwen38-next" in (cl[0].get("lane") or "")
          and "provider=qwen" in (cl[0].get("lane") or "")
          and cl[0].get("supported") == ["xhigh", "medium", "low"], str(cl[0]))
    check("warning is human-readable on the runner stdout too",
          "CLAMP" in p.stdout and "high" in p.stdout and "medium" in p.stdout, p.stdout[:200])

# ---------- (c) e2e escape hatch: the SERVER names the vocabulary, one re-drive ----------
argv_log2 = HOME / "argv-gate.log"
r2 = mk("flah-gate", [{"id": "a", "type": "agent", "goal": "GO gate",
                       "model": "qwen38-next", "reasoning": "high"}])
p2 = drive(r2, {"FAKE_ARGV_LOG": str(argv_log2), "FAKE_MODE": "reasoning_gate400",
                "FAKE_SUPPORTED_EFFORTS": "xhigh,medium,low", "FAKE_REJECT_EFFORT": "high"})
rec2 = record(r2, "a")
lines2 = argv_log2.read_text().splitlines() if argv_log2.exists() else []
check("e2e gate400: node DONE — the enum-gate 400 was survived, not a permfail",
      rec2.get("status") == "done", f"{rec2.get('status')}/{rec2.get('error')} {rec2.get('error_class')}")
check("e2e gate400: attempt 1 asked high (honest first try), attempt 2 asked medium",
      len(lines2) == 2 and "--reasoning high" in lines2[0] and "--reasoning medium" in lines2[1],
      str(lines2))
check("e2e gate400: exactly ONE re-drive (no loop)", len(lines2) == 2, str(lines2))
cl2 = [e for e in events(r2) if e.get("event") == "node.clamped"]
check("e2e gate400: ONE warning naming requested/clamped/lane/supported",
      len(cl2) == 1 and cl2[0].get("kind") == "reasoning_gate400"
      and cl2[0].get("requested") == "high" and cl2[0].get("clamped") == "medium"
      and cl2[0].get("supported") == ["xhigh", "medium", "low"], str(cl2))
check("e2e gate400: the record carries the clamp evidence",
      rec2.get("reasoning_gate400") == {"requested": "high", "clamped": "medium",
                                        "supported": ["xhigh", "medium", "low"]},
      str(rec2.get("reasoning_gate400")))
check("e2e gate400: attempts_log tells the story (dead gate400 attempt logged)",
      any((e.get("gate400_clamp") == "medium") for e in (rec2.get("attempts_log") or [])),
      str(rec2.get("attempts_log")))
# an ungated 400 must STILL be a permfail — the hatch never widens provider_400
argv_log3 = HOME / "argv-plain400.log"
r3 = mk("flah-plain", [{"id": "a", "type": "agent", "goal": "GO plain", "reasoning": "high"}])
drive(r3, {"FAKE_ARGV_LOG": str(argv_log3), "FAKE_MODE": "provider400"})
rec3 = record(r3, "a")
lines3 = argv_log3.read_text().splitlines() if argv_log3.exists() else []
check("plain provider_400 stays permfail (no enum words: no re-drive)",
      rec3.get("status") == "failed" and rec3.get("error_class") == "provider_400"
      and len(lines3) == 1, f"{rec3.get('error_class')} spawns={len(lines3)}")

# ---------- (d) e2e toolsets: unknown names are a clean no-op, never a child death ----------
def toolsets_run(run_id, toolsets_value, argv_log_path):
    r = mk(run_id, [{"id": "a", "type": "agent", "goal": f"GO {run_id}", "toolsets": toolsets_value}])
    p = drive(r, {"FAKE_ARGV_LOG": str(argv_log_path), "FAKE_MODE": "toolset_warn_ok"})
    return r, p, record(r, "a"), (argv_log_path.read_text().splitlines() if argv_log_path.exists() else [])

if CORE:
    r4, p4, rec4, lines4 = toolsets_run("flah-ts-none", ["none"], HOME / "argv-ts-none.log")
    check("e2e toolsets: -t none is a CLEAN no-op (flag omitted), child DONE",
          rec4.get("status") == "done" and lines4 and " -t " not in (" " + lines4[0] + " ")
          and not lines4[0].endswith("-t"), f"{rec4.get('status')} argv={lines4}")
    cl4 = [e for e in events(r4) if e.get("event") == "node.clamped"]
    check("e2e toolsets: ONE warning naming requested 'none'",
          len(cl4) == 1 and cl4[0].get("kind") == "toolsets"
          and cl4[0].get("requested") == "none", str(cl4))

    r5, _, rec5, lines5 = toolsets_run("flah-ts-mixed", ["web", "bogus"], HOME / "argv-ts-mixed.log")
    check("e2e toolsets: mixed list keeps the valid name, drops the bogus one",
          rec5.get("status") == "done" and lines5 and "-t web" in lines5[0]
          and "bogus" not in lines5[0], f"{rec5.get('status')} argv={lines5}")
    cl5 = [e for e in events(r5) if e.get("event") == "node.clamped"]
    check("e2e toolsets: ONE warning names requested 'web,bogus' -> kept 'web'",
          len(cl5) == 1 and cl5[0].get("requested") == "web,bogus"
          and cl5[0].get("clamped") == "web", str(cl5))

    # an unknown reasoning value against an unknown lane table still rides the
    # gate400 hatch (no table invented): fake rejects what core's widest table
    # DOES contain but a narrow relay would not (FAKE_REJECT_EFFORT drives it).
    r6, _, rec6, lines6 = toolsets_run("flah-ts-none-ok", ["web"], HOME / "argv-ts-ok.log")
    check("e2e toolsets: all-valid list passes through byte-identical (-t web)",
          rec6.get("status") == "done" and lines6 and "-t web" in lines6[0], str(lines6))
    check("e2e toolsets: all-valid list logs NO clamp",
          not [e for e in events(r6) if e.get("event") == "node.clamped"], "")
else:
    # honest degradation documented: without the core validator importable the
    # runner passes names through (warn+continue is core's job on the chat path)
    # and never hard-fails the spawn.
    r4, _, rec4, lines4 = toolsets_run("flah-ts-none", ["none"], HOME / "argv-ts-none.log")
    check("no-core: unknown toolset passes through and the child still runs",
          rec4.get("status") == "done" and lines4 and "-t none" in lines4[0],
          f"{rec4.get('status')} argv={lines4}")

print("DONE enum_clamp_5med_flah", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
