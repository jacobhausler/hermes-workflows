#!/usr/bin/env python3
"""sys-bknard — a COMPLETED child seat that exits rc=1 (the hermes CLI exit
path, not a crash) must not land as `error_class=unknown` with the #102
dead-session CLI line quoted back as its verdict.

Field shape (receipt 20261107-143106-b2p-sysggxeiu, claim-plan a0, pinned
byte-for-byte below): the capture opens with 'Session ... found but has no
messages. Starting fresh.', carries the finished answer prose, and CLOSES with
a fenced json answer that PARSES but misses required schema keys. The #4
harvest correctly declined it (schema miss), the death landed `unknown`, and
the node.failed error text was pure startup noise — the actual defect (which
keys the answer missed) was nowhere. The CLI rc=1 attribution lives as a bead
comment on sys-bknard; this file pins the RUNNER-side law:

 A  parseable-but-schema-invalid fenced answer over rc=1:
    A1 typed answer_schema_invalid (closed-set member), terminal (ONE spawn:
       outside both retry ladders, exactly like `schema`);
    A2 the error names the validate() misses (missing required keys);
    A3 the error does NOT quote the dead-session noise line (#102 law);
    A4 nothing harvested: status failed, no output, no harvest.
 B  noise-only capture (no fence) over rc=1:
    B1 stays `unknown` — no new class is invented for a capture with no answer;
    B2 the error names the noise-only shape instead of quoting the noise line.
 C  schema-VALID fenced answer over rc=1 (noise included): the #4 harvest accept rule
    is byte-unchanged — partial + output, not answer_schema_invalid.
 D-G est-fjac6 (#616 residuals 1+2): per-shape verdict quoting + adopted typing.
    D rc=1 malformed_turn over a banner-carrying capture (empty turn report):
      typed malformed_turn; the markup quoted; the #102 line NOT quoted.
    E adopted malformed_turn (rc unobservable), same capture shape: identical
      class and identical clean quoting — est-2ek.1.541 R8 extended to the QUOTE.
    F adopted schema-miss fence: answer_schema_invalid (the sys-bknard class is
      path-invariant, not the exit-0 `schema`); misses named; noise never quoted;
      the declined answer still rides `output`.
    G adopted prose-coercion (no valid last fence): keeps `schema` — the waiver
      shape pinned at the author note: a coercion is not a declined answer.

Style: PASS/FAIL lines + exit code (test_malformed_turn_541 house style); the
fake's DEADSEAT <path|NONE> mode replays a capture file and exits FAKE_RC.
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "homeBKNARD"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)   # est-2ek.1.762 pin: HERMES_HOME alone is not a sandbox
sys.path.insert(0, str(BUILD))
import wf as wfmod  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# a0's real fenced answer (claim-plan node, receipt 20261107-143106-b2p-sysggxeiu,
# logs/claim-plan.a0.log — the ONLY fence in that capture), embedded verbatim
# except personal home paths scrubbed to '~' (test_personal_path_scrub_867 ships
# the tree; the schema-miss pin rides the KEYS, so the scrub is shape-neutral).
A0_BODY = r"""{"bead_id":"sys-ggxeiu","branch":"sys-ggxeiu","destructive":false,"fleet_touching":false,"hosts":["devbox"],"premise_evidence":"grep -rqiE 'api_server.{0,160}flat|flat.{0,160}api_server' ~/.hermes/profiles/homelab/skills -> exit 1 (gap live); anchor at plugin-hooks.md:42 (API_SERVER_KEY bearer line); live flat shape at profiles/homelab/config.yaml:374-379 platforms.api_server{enabled,host,port,key}, nested extra: form seen on jetstream in same file; git rev-parse in skills dir = not a repo and system-wide find shows exactly one copy of plugin-hooks.md — no repo tracks it, so the PR carries no diff and the fix is a direct profile-file edit","roles":[],"summary_plan":"Apply one line to ~/.hermes/profiles/homelab/skills/autonomous-ai-agents/hermes-agent/references/plugin-hooks.md next to the line-42 API_SERVER_KEY bearer bullet, stating that api_server requires flat keys (enabled/host/port/key directly under platforms.api_server, not the nested extra: map other platforms use). The file is under no git, so expect an empty worktree and no PR; close with close_class=verified plus the acceptance grep exit-0 as cite, and do not let the stat-only incident-analysis.md phantom redden exit-check.","tests_run":[],"verdict":"ready"}"""

# The receipt graph's claim-plan answer shape: the probe reported the a0 answer
# missing exactly ['premise_verdict', 'sha']; the pinned schema keeps those two
# required so the validate() errors in the error text are the same facts.
SCHEMA = {"type": "object", "required": ["verdict", "premise_verdict", "sha"],
          "properties": {"verdict": {"type": "string"},
                         "premise_verdict": {"type": "string"},
                         "sha": {"type": "string"}}}

def mk(run_id, goal, schema):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": [
        {"id": "claim-plan", "type": "agent", "goal": goal, "schema": schema}]}))
    (r / "run.json").write_text(json.dumps(
        {"hermes_bin": FAKE, "concurrency": 1, "node_timeout": 30,
         "retry_backoff": [0.05, 0.05]}))
    return r

def wf(run_id, timeout=180):
    env = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(HOME / "fake.log"))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def rec_of(r):
    return json.loads((r / "nodes" / "claim-plan.json").read_text())

def spawns_of(run_id):
    return len(list((RUNS / run_id / "logs").glob("*.a*.log")))

def events(r):
    try:
        return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
    except FileNotFoundError:
        return []

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
(HOME / "fake.log").write_text("")

# the a0 capture as the fake replays it (the fake prints the noise line itself):
# finished-work prose + the schema-missing fence. HOME is gitignored (tests/home*/).
CAP = HOME / "bknard_a0_capture.txt"
CAP.write_text("plan.json written to the run dir; intake complete for sys-ggxeiu.\n"
               "```json\n" + A0_BODY + "\n```\n")

# ================= A: parseable fence fails the schema over rc=1 =================
r = mk("bknard-schema", f"DEADSEAT {CAP} bknard-schema claim-plan", SCHEMA)
wf("bknard-schema")
rec = rec_of(r)
err = rec.get("error") or ""
check("A1 rc=1 + schema-missing fence types answer_schema_invalid (closed set)",
      rec.get("status") == "failed" and rec.get("error_class") == "answer_schema_invalid"
      and rec.get("error_class") in wfmod.ERROR_CLASSES, json.dumps(rec)[:240])
check("A2 error names the validate() misses (missing required premise_verdict, sha)",
      "missing required" in err and "premise_verdict" in err and "sha" in err, err[:240])
check("A3 error does not quote the dead-session noise line (#102 law)",
      "found but has no messages" not in err, err[:240])
check("A4 nothing harvested: failed, no output, no harvest",
      "output" not in rec and "harvest" not in rec, json.dumps(rec)[:240])
check("A5 terminal: exactly one spawn (outside both retry ladders, like `schema`)",
      spawns_of("bknard-schema") == 1, f"spawns={spawns_of('bknard-schema')}")
check("A5 node.failed event typed from the closed set",
      any(e.get("event") == "node.failed" and e.get("error_class") in wfmod.ERROR_CLASSES
          for e in events(r)), json.dumps(events(r))[-240:])

# ================= B: noise-only capture over rc=1 =================
r = mk("bknard-noise", "DEADSEAT NONE bknard-noise claim-plan", SCHEMA)
wf("bknard-noise")
rec = rec_of(r)
err = rec.get("error") or ""
check("B1 noise-only death keeps the pre-existing class (unknown — no answer, no new label)",
      rec.get("status") == "failed" and rec.get("error_class") == "unknown", json.dumps(rec)[:240])
check("B2 error names the noise-only shape instead of quoting the noise line",
      "dead-session noise" in err and "found but has no messages" not in err, err[:240])
check("B2 no re-drive over absent api-call evidence (receipt attempts=1 shape)",
      spawns_of("bknard-noise") == 1, f"spawns={spawns_of('bknard-noise')}")

# ================= C: schema-VALID fence over rc=1 — #4 accept rule unchanged =========
GOOD = HOME / "bknard_good_capture.txt"
GOOD.write_text("```json\n" + json.dumps({"verdict": "ready", "premise_verdict": "valid",
                                           "sha": "0" * 40}) + "\n```\n")
r = mk("bknard-valid", f"DEADSEAT {GOOD} bknard-valid claim-plan", SCHEMA)
wf("bknard-valid")
rec = rec_of(r)
check("C harvest-on-death still accepts a valid fence over rc=1 (partial, not retyped)",
      rec.get("status") == "partial" and rec.get("error_class") != "answer_schema_invalid"
      and (rec.get("output") or {}).get("verdict") == "ready", json.dumps(rec)[:240])


# ============ D-G est-fjac6 (#616 residuals): per-shape quoting + adopted typing =========
# D is end-to-end over the real runner: the fake DEADSEAT mode prints the #102
# banner itself, replays the capture file, and writes NO turn report — so
# final_reply is empty and the capture is exactly what the verdict quotes.
# E/F/G drive wf._adopt_child at unit level (the jam8 T10/T11 form): child
# facts are injected, rc stays unobservable, classification is race-free.
import threading
from datetime import datetime, timezone

NL = chr(10)
LC, Q = chr(60), chr(34)
MARKUP = (LC + 'invoke name=' + Q + 'process_manage' + Q + '>' + NL
          + LC + 'parameter name=' + Q + 'action' + Q + '>poll' + LC + '/parameter>' + NL
          + LC + 'parameter name=' + Q + 'session_id' + Q + '>lane-7' + NL
          + LC + '/invoke>')
BANNER = 'Session wf:fjac6:fan:0:t.dead found but has no messages. Starting fresh.' + NL
MISS_ANS = {'bead_id': 'sys-ggxeiu', 'verdict': 'ready'}   # section A answer, minus 2 required keys
FENCE = '```json' + NL + json.dumps(MISS_ANS) + NL + '```' + NL

# ---- D: rc=1 malformed_turn, banner in the capture, empty turn report ----
MK = HOME / 'fjac6_markup.txt'
MK.write_text(MARKUP)
r = mk('fjac6-malformed', 'DEADSEAT ' + str(MK) + ' fjac6-malformed claim-plan', SCHEMA)
wf('fjac6-malformed')
rec = rec_of(r)
err = rec.get('error') or ''
check('D1 rc=1 tool-call-as-text death (no turn report) types malformed_turn',
      rec.get('status') == 'failed' and rec.get('error_class') == 'malformed_turn',
      json.dumps(rec)[:240])
check('D2 markup rides the verdict; the #102 line does NOT (wf.py:7789 quoting cure)',
      'tool-call-as-text' in err and 'invoke name=' in err
      and 'found but has no messages' not in err, err[:240])

# ---- unit harness for E/F/G: the jam8 _adopt_child form ----
def _adopt_meta(run):
    return {'_run': run, '_stop': threading.Event(), '_procs_lock': threading.Lock(),
            '_procs': {}, '_spawn_n': {}, '_retries_left': wfmod.DEFAULT_RETRY_BUDGET,
            'retry_backoff': [0.05]}

def _adopt(tag, cap, schema):
    r = RUNS / tag
    (r / 'nodes').mkdir(parents=True); (r / 'logs').mkdir(parents=True)
    lp = r / 'logs' / 'fan.0.a0.log'
    lp.write_text(cap)
    started = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    child = {'pid': 424242, 'skey': 'wf:' + tag + ':fan:0:t.dead', 'log_path': str(lp),
             'started': started, 'attempt': 0}
    node = {'id': 'fan', 'type': 'agent', 'goal': 'g'}
    return wfmod._adopt_child(_adopt_meta(r), node, {'fan': node}, 0, child, schema)

# ---- E: adopted malformed_turn, banner + markup, no schema (wf.py:6801 cure) ----
recE = _adopt('fjac6-e', BANNER + MARKUP, None)
errE = recE.get('error') or ''
check('E1 adopted malformed_turn: same class as the fresh path (est-2ek.1.541 R8)',
      recE.get('status') == 'failed' and recE.get('error_class') == 'malformed_turn',
      json.dumps(recE)[:240])
check('E2 adopted quoting is #102-clean too: markup rides the verdict, the banner does not',
      'invoke name=' in errE and 'found but has no messages' not in errE, errE[:240])

# ---- F: adopted schema-miss fence types answer_schema_invalid (residual 2 cure) ----
recF = _adopt('fjac6-f', BANNER + 'plan written to the run dir.' + NL + FENCE, SCHEMA)
errF = recF.get('error') or ''
check('F1 schema-miss fence on an adopted death lands answer_schema_invalid (A-parity class)',
      recF.get('status') == 'failed'
      and recF.get('error_class') == 'answer_schema_invalid'
      and recF.get('error_class') in wfmod.ERROR_CLASSES, json.dumps(recF)[:240])
check('F2 the error names the validate() misses (missing required premise_verdict, sha)',
      'missing required' in errF and 'premise_verdict' in errF and 'sha' in errF, errF[:240])
check('F3 the #102 line is never quoted on the adopted schema-miss shape',
      'found but has no messages' not in errF, errF[:240])
check('F4 the declined answer still rides the record (output kept on the adopted twin)',
      (recF.get('output') or {}).get('verdict') == 'ready', json.dumps(recF)[:240])

# ---- G: adopted prose-coercion keeps `schema` (author-note waiver shape) ----
recG = _adopt('fjac6-g', BANNER + 'plan written; no fenced answer anywhere.' + NL, SCHEMA)
check('G1 prose-coercion miss KEEPS schema — a coercion is not a declined answer (waiver pinned)',
      recG.get('status') == 'failed' and recG.get('error_class') == 'schema',
      json.dumps(recG)[:240])
print("RESULT " + ("ok" if ok else "FAILED"))
sys.exit(0 if ok else 1)
