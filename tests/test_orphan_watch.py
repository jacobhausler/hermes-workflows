#!/usr/bin/env python3
"""PR-4: orphan-held awareness (orphan_watch.py + status flag + `/wf orphans`).

Synthetic runs-root fixtures only (hermetic env: HERMES_HOME + WF_RUNS_ROOT pinned,
resolver isolated via wf_test_isolation). Source files are never read.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

TMP = Path(tempfile.mkdtemp(prefix="home-orphan-", dir=str(ROOT)))
os.environ["HERMES_HOME"] = str(TMP)
os.environ["WF_RUNS_ROOT"] = str(TMP / "workflows")
os.environ["HERMES_WF_HERMES_BIN"] = "offline"
os.environ.pop("HERMES_SESSION_ID", None)

spec = importlib.util.spec_from_file_location("orphan_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)
ow = door._orphan_watch
RUNS = Path(os.environ["WF_RUNS_ROOT"])
RUNS.mkdir(parents=True, exist_ok=True)
OBSERVER = {"sid": None}
door._session_env = lambda name: (OBSERVER["sid"] or "") if name == "HERMES_SESSION_ID" else ""

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg} — {detail}" if detail else msg
    ok += 1
    print("PASS", msg)

GRAPH = {"name": "g", "nodes": [{"id": "approve", "type": "gate", "question": "publish?", "options": ["yes", "no"]}]}

def mk(rid, sid, events, status=None, graph=GRAPH, run_json=None):
    r = RUNS / rid
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps(graph))
    meta = {"name": rid, "hermes_bin": "/bin/true", "owner": {"session_id": sid}}
    if status:
        meta["status"] = status
    (r / "run.json").write_text(run_json if run_json is not None else json.dumps(meta))
    if events is not None:
        (r / "events.jsonl").write_text("".join(
            (e if isinstance(e, str) else json.dumps(e)) + "\n" for e in events))
    return r

HELD = [{"ts": "2026-10-15T10:00:00+00:00", "event": "run.started"},
        {"ts": "2026-10-15T10:00:05+00:00", "event": "gate.held", "node": "approve",
         "question": "publish?", "options": ["yes", "no"]}]

def rows():
    return ow.read_rows(RUNS / ow.INDEX_NAME)

try:
    class _Ctx:
        def __init__(self): self.hooks = {}
        def register_hook(self, n, f): self.hooks[n] = f
        def register_tool(self, **k): pass
        def register_command(self, *a, **k): pass
        def register_skill(self, *a, **k): pass
        def get_config(self, k, d): return d
    _c = _Ctx(); door.register(_c)
    check({"on_session_end", "on_session_finalize", "agent_loop_stopped"} <= set(_c.hooks),
          "register() wires the three orphan observers by default", str(sorted(_c.hooks)))

    # --- held gate + dead session -> index row + stamp -------------------------
    r1 = mk("o-held", "sess-dead-0001", HELD)
    got = door._orphan_watch.on_session_finalize(session_id="sess-dead-0001")
    rs = rows()
    check(len(rs) == 1 and rs[0]["run_id"] == "o-held" and rs[0]["gate_id"] == "approve"
          and rs[0]["session_id"] == "sess-dead-0001" and rs[0]["hook"] == "on_session_finalize"
          and rs[0]["question"] == "publish?", "held gate + finalized owner -> one index row", str(rs))
    check(json.loads((r1 / "run.json").read_text()).get("orphan_at") == rs[0]["ts"],
          "run.json stamped orphan_at")

    # --- idempotency ----------------------------------------------------------
    ow.on_session_finalize(session_id="sess-dead-0001")
    ow.on_agent_loop_stopped(session_key="agent:main:cli:sess-dead-0001")
    check(len(rows()) == 1, "same hook twice / other hook same gate -> still one row", str(rows()))

    # --- no-row cases ---------------------------------------------------------
    n0 = len(rows())
    mk("o-other", "sess-live-0002", HELD)
    mk("o-nogate", "sess-dead-0001", HELD[:1])
    mk("o-released", "sess-dead-0001", HELD + [{"event": "gate.released", "node": "approve"}])
    mk("o-stopped", "sess-dead-0001", HELD + [{"event": "run.stopped"}])
    mk("o-doneflag", "sess-dead-0001", HELD, status="done")
    mk("o-noevents", "sess-dead-0001", None)
    ow.on_session_finalize(session_id="sess-dead-0001")
    ids = {x["run_id"] for x in rows()}
    check(len(rows()) == n0 and ids == {"o-held"},
          "terminal / no gate / released / stopped / different session -> no rows", str(ids))

    # --- hook gating ----------------------------------------------------------
    mk("o-turn", "sess-turn-0003", HELD)
    ow.on_session_end(session_id="sess-turn-0003", interrupted=False, turn_exit_reason="completed")
    check("o-turn" not in {x["run_id"] for x in rows()},
          "on_session_end of a normally completed turn does NOT mark (live session)")
    ow.on_session_end(session_id="sess-turn-0003", interrupted=True, turn_exit_reason="interrupted_by_user")
    check("o-turn" in {x["run_id"] for x in rows()}, "on_session_end interrupted -> marked")
    mk("o-rot", "sess-old-00004", HELD)
    ow.on_session_finalize(session_id="sess-new-00005", old_session_id="sess-old-00004")
    check("o-rot" in {x["run_id"] for x in rows()}, "finalize rotation marks old_session_id")
    mk("o-short", "ab", HELD)
    ow.on_agent_loop_stopped(session_key="agent:main:xxab")
    check("o-short" not in {x["run_id"] for x in rows()}, "short ids never suffix-match (conservative)")

    # --- status flag ----------------------------------------------------------
    OBSERVER["sid"] = None
    st = door.act_status({"run_id": "o-held"})
    check(st.get("status") == "held" and st.get("orphan_held") is True
          and st["waiting_on"]["gate_id"] == "approve" and st["waiting_on"]["since"],
          "status reports orphan_held + waiting_on", json.dumps({k: st.get(k) for k in ("status", "orphan_held", "waiting_on")}))
    nx = st["next"]
    check(nx[0] == {"action": "stop", "note": "owner session died; stop or re-attach"}
          and any(x.get("action") == "release" for x in nx), "next: stop FIRST, release kept", json.dumps(nx))
    check("orphan_held" not in door.act_status({"run_id": "o-other"}), "non-orphan run carries no flag")

    # --- /wf orphans before ---------------------------------------------------
    txt = door._wf_command("orphans")
    check("o-held" in txt and "publish?" in txt, "/wf orphans lists the run with its question", txt)

    # --- revoke via release path ---------------------------------------------
    res = door._release_core(r1, "approve", "yes")
    check(res.get("ok"), "release core accepted", str(res))
    with open(r1 / "events.jsonl", "a") as f:
        f.write(json.dumps({"event": "gate.released", "node": "approve"}) + "\n")
    st2 = door.act_status({"run_id": "o-held"})
    check("orphan_held" not in st2, "after release: status no longer orphan_held", str({k: st2.get(k) for k in ("status", "orphan_held")}))
    check("o-held" not in door._wf_command("orphans"), "after release: /wf orphans no longer lists it")
    check("orphan_at" not in json.loads((r1 / "run.json").read_text()), "revoke clears run.json stamp")
    check(any(x.get("revoked") and x["reason"] == "release" for x in rows()), "revoke row logged (release)")

    # --- revoke via stop path (door act_stop, no runner spawn: stub the respawn) ----
    door._resume_after_action = lambda *a, **k: "noop"
    ow.on_session_finalize(session_id="sess-turn-0003")   # o-turn already unrevoked; idempotent
    door.act_stop({"run_id": "o-turn"})
    check("o-turn" not in door._wf_command("orphans"), "stop revokes the orphan row")

    # --- revoke via different live session (re-attach) ----------------------------
    mk("o-reatt", "sess-dead-0006", HELD)
    ow.on_session_finalize(session_id="sess-dead-0006")
    OBSERVER["sid"] = "sess-dead-0006"   # the owner itself looking: not a re-attach
    check(door.act_status({"run_id": "o-reatt"}).get("orphan_held") is True, "owner's own status read does not revoke")
    OBSERVER["sid"] = "sess-new-live-7"
    check("orphan_held" not in door.act_status({"run_id": "o-reatt"}), "different live session status -> re-attach, no flag")
    check(any(x.get("revoked") and x["reason"] == "reattach" and x["by"] == "sess-new-live-7" for x in rows()),
          "re-attach logged with observer id")
    OBSERVER["sid"] = None

    # --- disabled flag ----------------------------------------------------------
    mk("o-off", "sess-off-00008", HELD)
    _real_enabled = ow.enabled
    ow.enabled = lambda: False
    n1 = len(rows())
    ow.on_session_finalize(session_id="sess-off-00008")
    check(len(rows()) == n1, "orphan_watch:false -> observers are inert")
    ow.enabled = _real_enabled
    ow.on_session_finalize(session_id="sess-off-00008")
    check(len(rows()) == n1 + 1, "re-enabled -> marks again")

    n_set = door._common.owner_setting("orphan_watch")
    check(n_set is None and ow.enabled() is True, "default-ON: unset owner setting enables the watch")

    # --- fail-open --------------------------------------------------------------
    mk("o-garbage", "sess-fo-000009", HELD, run_json="{not json")
    mk("o-trunc", "sess-fo-000009", [HELD[0], '{"ts":"x","event":"gate.held","node":"appr'])
    mk("o-badowner", "sess-fo-000009", HELD, run_json=json.dumps({"owner": "oops"}))
    n2 = len(ow.read_rows(RUNS / ow.INDEX_NAME))
    try:
        ow.on_session_finalize(session_id="sess-fo-000009")
        ow.on_session_end(session_id="sess-fo-000009", interrupted=True)
        ow.on_agent_loop_stopped(session_key="x:sess-fo-000009")
        ow.on_session_finalize()           # no ids
        ow.on_session_end(**{"turn_exit_reason": None})
        raised = False
    except Exception as e:   # pragma: no cover
        raised = repr(e)
    check(raised is False, "garbage run.json / truncated events / no ids -> hooks never raise", str(raised))
    check(len(ow.read_rows(RUNS / ow.INDEX_NAME)) == n2,
          "garbage / truncated-mid-line / non-dict owner -> no row (deliberate: no gate evidence, no row)")
    # garbled index lines are skipped, not fatal
    with open(RUNS / ow.INDEX_NAME, "a") as f:
        f.write("{broken\n[]\n")
    check(isinstance(ow.read_rows(RUNS / ow.INDEX_NAME), list) and ow.render_orphans(), "garbled index lines skipped")
    # unbound/unwritable root: mark_session returns [] without raising
    ro = TMP / "ro"; ro.write_text("a file, not a dir")
    os.environ["WF_RUNS_ROOT"] = str(ro)
    check(ow.mark_session(lambda s: True, "t") == [] and ow.revoke_run("nope", "t") == 0,
          "runs root that is a file -> [] / 0, no raise")
    os.environ["WF_RUNS_ROOT"] = str(RUNS)
    # status never breaks on a corrupt stamp
    (RUNS / "o-garbage" / "graph.json").write_text(json.dumps(GRAPH))
    try:
        door.act_status({"run_id": "o-garbage"}); st_raised = False
    except Exception as e:   # pragma: no cover
        st_raised = repr(e)
    check(st_raised is False, "status on a run with corrupt run.json does not raise", str(st_raised))
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"ALL PASS ({ok} checks)")
