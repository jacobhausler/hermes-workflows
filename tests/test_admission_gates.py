#!/usr/bin/env python3
"""PR-3: zero-turn gate answers on the admission lane + dispatch witness.

Core contract (hermes-agent origin/main 20c9da14eb, gateway/run_inbound_consumer.py): the
post_gateway_admission callback gets kwargs session_key/platform/source/message_id/text and may
return {"action": "handled", "reply": <str>}; None / any other shape / a raise = ordinary turn.
Hook fires for NON-internal (human-typed) messages only — wake text never reaches it.
Callbacks are called directly; release is a recording stub.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

TMP = Path(tempfile.mkdtemp(prefix="admgate-", dir=str(ROOT / "tests")))
for k in [k for k in os.environ if k.startswith("HERMES_SESSION") or k == "HERMES_UI_SESSION_ID"]:
    os.environ.pop(k)                       # hostile session env stripped (house style)
os.environ["HERMES_HOME"] = str(TMP / "home")
os.environ["WF_RUNS_ROOT"] = str(TMP / "workflows")
os.environ["HERMES_WF_HERMES_BIN"] = "offline"

spec = importlib.util.spec_from_file_location("door_admgate", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)
gi = door._gate_index
RT = Path(os.environ["WF_RUNS_ROOT"])
RT.mkdir(parents=True, exist_ok=True)

fails = 0


def check(label, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail and not cond else ""))
    fails += 0 if cond else 1


FLAGS = {"admission_gates": True, "dispatch_witness": True}
_orig_setting = door._common.owner_setting
door._common.owner_setting = lambda key: FLAGS[key] if key in FLAGS else _orig_setting(key)

HELD = set()          # (run, gate) the stub read model reports as held
door._gate_still_held = lambda run, gate: (run, gate) in HELD
RELEASES = []


def stub_release(args):
    RELEASES.append(dict(args))
    return {"ok": True}


door.act_release = stub_release


def reset():
    for f in RT.glob("gate-index.jsonl*"):
        f.unlink()
    gi._SEEN.clear()
    HELD.clear()
    RELEASES.clear()
    FLAGS.update(admission_gates=True, dispatch_witness=True)


def opened(run, gate, options, key="sess-A"):
    HELD.add((run, gate))
    return gi.note_open(RT, run, gate, key, "sid", options)


def call(text, key="sess-A"):
    return door._admission_handler(session_key=key, platform="discord", source={}, message_id="m1", text=text)


# ---- index ----
reset()
check("index: first open appends", opened("r1", "g1", ["yes", "no"]) is True)
check("index: duplicate open deduped", gi.note_open(RT, "r1", "g1", "sess-A", "sid", ["yes", "no"]) is False)
gi._SEEN.clear()   # reload-tolerant: a fresh process still dedupes from the file
check("index: dedupe survives a cold cache", gi.note_open(RT, "r1", "g1", "sess-A", "sid", ["yes", "no"]) is False)
check("index: one row on disk", len((RT / gi.INDEX_NAME).read_text().splitlines()) == 1)
check("index: close removes from open set", gi.note_close(RT, "r1", "g1") == 1 and gi.open_rows(RT) == [])
check("index: reopen after close appends", gi.note_open(RT, "r1", "g1", "sess-A", "sid", ["a"]) is True)

reset()
for i in range(300):
    gi.note_open(RT, f"run{i}", "g", "sess-A", "sid", ["x"])
    if i % 2 == 0:
        gi.note_close(RT, f"run{i}", "g")      # 450 + 150... rows cross the 500 cap mid-way
before = {(r["run_id"], r["gate_id"]) for r in gi.open_rows(RT)}
n_lines_before = len((RT / gi.INDEX_NAME).read_text().splitlines())
gi.compact(RT)
after = {(r["run_id"], r["gate_id"]) for r in gi.open_rows(RT)}
lines_after = (RT / gi.INDEX_NAME).read_text().splitlines()
check("index: compaction preserves exactly the open set", before == after and len(after) == 150,
      f"{len(before)} vs {len(after)}")
check("index: compaction leaves only open rows", len(lines_after) == 150 and n_lines_before > 150)
reset()
for i in range(520):
    gi.note_open(RT, f"c{i}", "g", "sess-A", "sid", [])
    gi.note_close(RT, f"c{i}", "g")
check("index: auto-compaction bounds the file", len((RT / gi.INDEX_NAME).read_text().splitlines()) <= 501)

# ---- fail-open: corrupt index line skipped ----
reset()
opened("r1", "g1", ["yes", "no"])
with open(RT / gi.INDEX_NAME, "a") as f:
    f.write("{not json\n\n[1,2]\n")
r = call("yes")
check("corrupt index lines skipped, valid row still matches", isinstance(r, dict) and r.get("action") == "handled")

# ---- match matrix ----
reset()
opened("r1", "g1", ["Ship it", "Hold"])
r = call("  ship IT ")
check("bare option match is case-insensitive + trimmed", r is not None
      and RELEASES == [{"run_id": "r1", "gate_id": "g1", "answer": "Ship it"}], str(RELEASES))
check("handled directive matches core contract (exact keys, str reply)",
      set(r) == {"action", "reply"} and r["action"] == "handled" and isinstance(r["reply"], str))
check("reply line format",
      r["reply"] == 'Workflow "r1": gate "g1" released with "Ship it" (zero-turn admission path).', r["reply"])

reset(); opened("r1", "g1", ["yes", "no"])
r = call("2")
check("numeric match is 1-based", RELEASES == [{"run_id": "r1", "gate_id": "g1", "answer": "no"}], str(RELEASES))
reset(); opened("r1", "g1", ["yes", "no"])
check("numeric out of range -> None", call("3") is None and call("0") is None and not RELEASES)
check("non-match -> None, nothing released", call("maybe later?") is None and not RELEASES)
check("empty/whitespace -> None", call("   ") is None and door._admission_handler(session_key="sess-A") is None)
check("other session -> None", call("yes", key="sess-B") is None and not RELEASES)
check("no session_key -> None", door._admission_handler(text="yes") is None)

reset(); opened("r1", "g1", ["yes", "no"])
r = call("wf release r1 g1 yes, but only after the soak ends")
check("command form carries a multi-word answer",
      RELEASES == [{"run_id": "r1", "gate_id": "g1", "answer": "yes, but only after the soak ends"}]
      and r["action"] == "handled", str(RELEASES))
reset(); opened("r1", "g1", ["yes"])
check("command form for a gate not in this session -> None",
      call("wf release r9 g9 yes") is None and not RELEASES)

reset(); opened("r1", "g1", ["yes", "no"]); opened("r2", "g2", ["yes", "no"])
check("two open gates: bare answer -> None", call("yes") is None and not RELEASES)
r = call("wf release r2 g2 no")
check("two open gates: command form still works",
      r is not None and RELEASES == [{"run_id": "r2", "gate_id": "g2", "answer": "no"}], str(RELEASES))

reset(); opened("r1", "g1", ["yes", "no"])
HELD.clear()   # answered elsewhere (UI): read model no longer shows the hold
check("stale index row (no longer held) -> None and row closed",
      call("yes") is None and not RELEASES and gi.open_rows(RT) == [])
reset(); opened("r1", "g1", ["yes", "no"]); gi.note_open(RT, "rOld", "gOld", "sess-A", "sid", ["yes"])
check("stale second row does not create false ambiguity", call("yes") is not None and len(RELEASES) == 1)

# ---- flag-off: None and ZERO index reads ----
reset(); opened("r1", "g1", ["yes", "no"])
FLAGS["admission_gates"] = False
reads = []
_orig_rows, _orig_read = gi.open_rows, gi._read_rows
gi.open_rows = lambda *a, **k: (reads.append("open_rows"), _orig_rows(*a, **k))[1]
gi._read_rows = lambda *a, **k: (reads.append("_read_rows"), _orig_read(*a, **k))[1]
check("flag off -> None", call("yes") is None and call("wf release r1 g1 yes") is None and not RELEASES)
check("flag off -> zero index reads", reads == [], str(reads))
door._gi_note_open(RT / "r1", {"id": "g1", "options": ["yes"]})
door._gi_note_close(RT / "r1", "g1")
check("flag off -> status/release hooks touch no index", reads == [])
gi.open_rows, gi._read_rows = _orig_rows, _orig_read
FLAGS["admission_gates"] = True

# ---- fail-open: release failures ----
reset(); opened("r1", "g1", ["yes", "no"])


def boom(args):
    raise RuntimeError("release exploded")


door.act_release = boom
check("release raises -> None (ordinary turn)", call("yes") is None)
door.act_release = lambda args: {"ok": False, "error": "gate already answered (current graph)"}
check("release refused -> None", call("yes") is None)
door.act_release = lambda args: "garbage"
check("release returns junk -> None", call("yes") is None)
door.act_release = stub_release

# ---- /wf gates ----
reset(); opened("r1", "g1", ["yes", "no"])
os.environ["HERMES_SESSION_KEY"] = "sess-A"
out = door._wf_command("gates")
os.environ.pop("HERMES_SESSION_KEY")
check("/wf gates lists the session's open gate with options",
      'run "r1" gate "g1"' in out and "1) yes 2) no" in out, out)
FLAGS["admission_gates"] = False
check("/wf gates says off when flag off", "off" in door._wf_command("gates"))
FLAGS["admission_gates"] = True

# ---- status wiring (owner-gated open) ----
reset()
rd = RT / "run-own"
rd.mkdir()
(rd / "run.json").write_text(json.dumps({"owner": {"session_id": "sid-1"}}))
os.environ["HERMES_SESSION_ID"], os.environ["HERMES_SESSION_KEY"] = "sid-1", "sess-A"
door._gi_note_open(rd, {"id": "g", "options": ["a", "b"]})
check("status path opens a row for the owning session",
      [(x["run_id"], x["gate_id"], x["session_key"]) for x in gi.open_rows(RT)] == [("run-own", "g", "sess-A")])
os.environ["HERMES_SESSION_ID"] = "someone-else"
reset()
door._gi_note_open(rd, {"id": "g", "options": ["a", "b"]})
check("non-owner session never opens a row", gi.open_rows(RT) == [])
os.environ["HERMES_SESSION_ID"] = "sid-1"
door._gi_note_open(rd, {"id": "g", "options": ["a"]})
door._gi_note_close(rd, None)
check("stop/release path closes it", gi.open_rows(RT) == [])
for k in ("HERMES_SESSION_ID", "HERMES_SESSION_KEY"):
    os.environ.pop(k, None)

# ---- witness ----
reset()
ev = types.SimpleNamespace(
    source=types.SimpleNamespace(platform=types.SimpleNamespace(value="discord"), chat_id="c1", user_id="u1"),
    message_id="m9", internal=False, text="hello")
check("witness observer returns None (allow)", door._dispatch_witness(event=ev) is None)
rows = [json.loads(x) for x in (RT / gi.WITNESS_NAME).read_text().splitlines()]
check("witness row shape", len(rows) == 1 and rows[0]["platform"] == "discord" and rows[0]["chat_id"] == "c1"
      and rows[0]["user_id"] == "u1" and rows[0]["text_len"] == 5 and "ts" in rows[0]
      and "decision_allowed" in rows[0] and "hello" not in json.dumps(rows[0]), str(rows))
raised = False
try:
    for junk in (None, 42, object(), types.SimpleNamespace(source=7, text=b"x")):
        door._dispatch_witness(event=junk)
    door._dispatch_witness()
    door._dispatch_witness("positional", gateway=1, session_store=2, extra=3)
except Exception:
    raised = True
check("witness never raises on junk payload", not raised)
FLAGS["dispatch_witness"] = False
n0 = len((RT / gi.WITNESS_NAME).read_text().splitlines())
door._dispatch_witness(event=ev)
check("witness flag off -> no write", len((RT / gi.WITNESS_NAME).read_text().splitlines()) == n0)
# rotation at cap
small = 400
for f in RT.glob("dispatch-witness.jsonl*"):
    f.unlink()
for i in range(30):
    gi.witness_append(RT, gi.witness_row(ev), max_bytes=small)
cur = RT / gi.WITNESS_NAME
rot = RT / (gi.WITNESS_NAME + ".1")
check("witness rotates at cap (current stays under cap, .1 exists)",
      rot.exists() and cur.stat().st_size <= small, f"{cur.stat().st_size}")
check("witness unwritable root never raises", gi.witness_append("/proc/nope/x", {"a": 1}) is False)

# ---- registration ----
class Ctx:
    def __init__(self):
        self.hooks, self.cfg = {}, 0

    def register_hook(self, n, f): self.hooks[n] = f
    def register_tool(self, **k): pass
    def register_command(self, *a, **k): pass
    def register_skill(self, *a, **k): pass
    def get_config(self, k, d=None): return d


c = Ctx()
door.register(c)
check("register wires both hooks", c.hooks.get("post_gateway_admission") is door._admission_handler
      and c.hooks.get("pre_gateway_dispatch") is door._dispatch_witness)

shutil.rmtree(TMP, ignore_errors=True)
print("ALL PASS" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
