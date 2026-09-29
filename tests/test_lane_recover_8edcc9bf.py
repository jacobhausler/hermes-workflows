#!/usr/bin/env python3
"""#37 lane hygiene — scripts/lane_recover.py replays a dead lane's journaled
write_file/patch calls from a SYNTHETIC state.db (never a live one).

Schema mirrors the real core sessions/messages tables (confirmed read-only on
2026-09-29): sessions(id, title, started_at, ...) with title = the runner's
`wf:<run>:<node>[:<i>]:<efp8>.<nonce>#a<n>` key; messages(session_id, role,
tool_name, tool_calls, content, timestamp, ...) where the ASSISTANT row's
`tool_calls` is a JSON list of {id, type:'function', function:{name,
arguments:<JSON STRING>}} and the following role='tool' row carries tool_name.

Seeds 6 calls: write_file x2 (incl. one re-write of the same path), patch x2
(one exact-matching, one intentionally unmatched), one whitespace-drifted patch
(fuzzy), plus a bash/terminal call that must be ignored. Plain script, no pytest:
exits non-zero on the first red.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lane_recover.py"
FAILS = []


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:600]))
    if not cond:
        FAILS.append(name)


SESSIONS_DDL = """CREATE TABLE sessions (
    id TEXT PRIMARY KEY, source TEXT NOT NULL, session_key TEXT, model TEXT,
    started_at REAL NOT NULL, ended_at REAL, message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0, title TEXT, last_activity_at REAL,
    last_activity_description TEXT, api_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0, reasoning_tokens INTEGER DEFAULT 0,
    estimated_cost_usd REAL, billing_provider TEXT)"""
MESSAGES_DDL = """CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL REFERENCES sessions(id),
    role TEXT NOT NULL, content TEXT, tool_call_id TEXT, tool_calls TEXT, tool_name TEXT,
    timestamp REAL NOT NULL)"""

SKEY = "wf:20260929-000000-synthetic:build:0123abcd.abcdef"
TITLE = SKEY + "#a0"

BASE_A = "def f():\n    return 1\n\n\ndef g():\n    return 2\n"


def seed(db):
    c = sqlite3.connect(str(db))
    c.execute(SESSIONS_DDL)
    c.execute(MESSAGES_DDL)
    c.execute("insert into sessions(id, source, started_at, title, tool_call_count) values (?,?,?,?,?)",
              ("sess_synth_1", "workflow", 1000.0, TITLE, 6))
    # a decoy session with the same bare key but an OLDER attempt: latest must win
    c.execute("insert into sessions(id, source, started_at, title) values (?,?,?,?)",
              ("sess_synth_0", "workflow", 900.0, SKEY + "#a-old"))
    ts = [1001.0]

    def call(name, args, content="ok"):
        ts[0] += 1
        cid = f"call_{len(str(ts[0]))}_{int(ts[0])}"
        tc = [{"id": cid, "call_id": cid, "type": "function",
               "function": {"name": name, "arguments": json.dumps(args)}}]
        c.execute("insert into messages(session_id, role, content, tool_calls, timestamp) values (?,?,?,?,?)",
                  ("sess_synth_1", "assistant", "", json.dumps(tc), ts[0]))
        ts[0] += 0.5
        c.execute("insert into messages(session_id, role, content, tool_call_id, tool_name, timestamp) "
                  "values (?,?,?,?,?,?)",
                  ("sess_synth_1", "tool", json.dumps({"output": content}), cid, name, ts[0]))

    c.execute("insert into messages(session_id, role, content, timestamp) values (?,?,?,?)",
              ("sess_synth_1", "user", "build the thing", 1000.5))
    call("write_file", {"path": "/lane/src/a.py", "content": BASE_A})                      # 0
    call("terminal", {"command": "git status --short"}, "M src/a.py")                       # ignored
    call("patch", {"path": "/lane/src/a.py", "old_string": "    return 1\n",
                   "new_string": "    return 10\n"})                                        # 1 exact
    call("write_file", {"path": "/lane/tests/test_a.py", "content": "print('v1')\n"})       # 2
    call("write_file", {"path": "/lane/tests/test_a.py", "content": "print('v2')\n"})       # 3 re-write
    call("patch", {"path": "/lane/src/a.py", "old_string": "    return 999\n",
                   "new_string": "    return 0\n"})                                         # 4 unmatched
    call("patch", {"path": "/lane/src/a.py", "old_string": "def g():\n        return 2\n",
                   "new_string": "def g():\n    return 20\n"})                              # 5 fuzzy (ws drift)
    # an empty session: no journaled calls at all (exit 3)
    c.execute("insert into sessions(id, source, started_at, title) values (?,?,?,?)",
              ("sess_synth_2", "workflow", 1100.0, "wf:20260929-000000-synthetic:empty:0123abcd.000000#a0"))
    c.execute("insert into messages(session_id, role, content, timestamp) values (?,?,?,?)",
              ("sess_synth_2", "user", "nothing", 1100.5))
    c.commit()
    c.close()


def run(*argv, env=None):
    p = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True,
                       timeout=60, env=env or dict(os.environ))
    return p.returncode, p.stdout, p.stderr


def main():
    with tempfile.TemporaryDirectory(prefix="lane37-recover-") as t:
        tmp = Path(t)
        # the profile-home layout the read model maps: <root>/profiles/<name>/state.db
        root = tmp / "hermes"
        launcher = root / "profiles" / "launcher"
        target = root / "profiles" / "lanebot"
        launcher.mkdir(parents=True); target.mkdir(parents=True)
        db = target / "state.db"
        seed(db)
        mtime0 = db.stat().st_mtime_ns
        env = dict(os.environ, HERMES_HOME=str(launcher))
        env.pop("WF_RUNS_ROOT", None)

        # ---- triage view (default mode): ordered list, bash ignored ----
        rc, out, err = run("--profile", "lanebot", "--skey", SKEY, env=env)
        check("triage: exit 0", rc == 0, (rc, out, err))
        lines = [l for l in out.splitlines() if l.strip() and l.strip()[0].isdigit()]
        check("triage: exactly 6 write_file/patch rows (terminal ignored)", len(lines) == 6, out)
        check("triage: order is write_file, patch, write_file, write_file, patch, patch",
              [l.split()[1] for l in lines] == ["write_file", "patch", "write_file", "write_file", "patch", "patch"], lines)
        check("triage: bare key resolves to the LATEST attempt (#a0, not #a-old)", "#a0 (sess_synth_1)" in out, out)
        check("triage: rows name the target path", all("/lane/" in l for l in lines), lines)
        check("triage: no 'terminal' row", "terminal" not in out, out)

        # ---- restore (--out): contents + unmatched report ----
        outd = tmp / "restore"
        rc, out, err = run("--profile", "lanebot", "--skey", TITLE, "--out", str(outd), env=env)
        check("restore: exit 0 (recovered > 0)", rc == 0, (rc, out, err))
        a = outd / "lane" / "src" / "a.py"
        ta = outd / "lane" / "tests" / "test_a.py"
        check("restore: absolute target path lands under --out (root stripped)", a.exists() and ta.exists(),
              sorted(str(p.relative_to(outd)) for p in outd.rglob("*") if p.is_file()))
        want_a = "def f():\n    return 10\n\n\ndef g():\n    return 20\n"
        check("restore: write_file + exact patch + fuzzy patch accumulate in order",
              a.exists() and a.read_text() == want_a, a.read_text() if a.exists() else None)
        check("restore: a re-written file holds the LAST write_file content",
              ta.exists() and ta.read_text() == "print('v2')\n", ta.read_text() if ta.exists() else None)
        rep_p = outd / "lane_recover_report.json"
        rep = json.loads(rep_p.read_text()) if rep_p.exists() else {}
        check("report: exactly one unmatched patch, index 4, with the reason",
              len(rep.get("unmatched", [])) == 1 and rep["unmatched"][0]["index"] == 4
              and "not found" in rep["unmatched"][0]["reason"], rep.get("unmatched"))
        check("report: applied lists exact (#1) and fuzzy (#5) matches",
              sorted((x["index"], x["match"]) for x in rep.get("applied", [])) == [(1, "exact"), (5, "fuzzy")],
              rep.get("applied"))
        check("report: written lists the three write_file calls",
              [x["index"] for x in rep.get("written", [])] == [0, 2, 3], rep.get("written"))
        check("restore stdout names the UNMATCHED patch for the operator", "UNMATCHED #4" in out, out)

        # ---- --attempt picks a specific attempt; --db overrides the mapping ----
        rc, out, err = run("--profile", "lanebot", "--skey", SKEY, "--attempt", "0", env=env)
        check("--attempt 0 resolves the #a0 session", rc == 0 and "#a0" in out, (rc, out, err))
        rc, out, err = run("--profile", "whatever", "--db", str(db), "--skey", SKEY, env=env)
        check("--db overrides the profile mapping", rc == 0 and "6 journaled" in out, (rc, out, err))

        # ---- exit codes: 2 no session, 3 no journaled calls ----
        rc, out, err = run("--profile", "lanebot", "--skey", "wf:20260929-000000-synthetic:ghost:00000000.000000", env=env)
        check("exit 2: unknown session key", rc == 2 and "no session" in err, (rc, out, err))
        rc, out, err = run("--profile", "nosuch", "--skey", SKEY, env=env)
        check("exit 2: profile without a state.db", rc == 2 and "no state.db" in err, (rc, out, err))
        rc, out, err = run("--profile", "lanebot", "--skey", "wf:20260929-000000-synthetic:empty:0123abcd.000000", env=env)
        check("exit 3: session with no journaled write_file/patch calls", rc == 3 and "no write_file/patch" in err, (rc, out, err))

        # ---- --run reads the key from the run dir's node record (no key needed) ----
        run_id = "20260929-000000-synthetic"
        r = launcher / "workflows" / run_id
        (r / "nodes").mkdir(parents=True)
        (r / "graph.json").write_text(json.dumps({"name": "s", "nodes": [{"id": "build", "type": "agent", "goal": "x"}]}))
        (r / "nodes" / "build.json").write_text(json.dumps({"status": "failed", "skey": SKEY, "attempt": 0,
                                                            "profile": "lanebot", "profile_home": str(target)}))
        rc, out, err = run("--run", run_id, "--node", "build", env=env)
        check("--run/--node: key + db resolved from the node record (profile_home)", rc == 0 and "6 journaled" in out, (rc, out, err))
        rc, out, err = run("--run", run_id, "--node", "nope", env=env)
        check("--run with an unknown node exits 2", rc == 2 and "no node record" in err, (rc, out, err))
        rc, out, err = run("--run", "20260101-000000-nope", "--node", "build", env=env)
        check("--run with an unknown run exits 2", rc == 2 and "no run dir" in err, (rc, out, err))

        # ---- hermetic: the db is opened read-only and never mutated ----
        check("state.db untouched (mtime unchanged after every invocation)", db.stat().st_mtime_ns == mtime0)
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        n = c.execute("select count(*) from messages").fetchone()[0]; c.close()
        check("state.db row count unchanged", n == 1 + 2 * 7 + 1, n)

    print(("ALL PASS" if not FAILS else f"FAILED: {FAILS}"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
