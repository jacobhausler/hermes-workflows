#!/usr/bin/env python3
"""#41 / #42 — owner settings `runs_root` + `profile` (tool-bridge first-class).

Subprocess-launched resolver matrix: every case is a FRESH interpreter with its own
environment and its own fake estate, so nothing leaks between cases and the door
module's import-time state is exactly what a real host would see. Cases:

  (a) no settings, no env            -> byte-identical to the pre-fix resolver (main's
                                        wfcommon run in the same env answers the same path)
  (b) settings.runs_root             -> door runs_root(), act_list (handle('list')) and
                                        run_state all resolve the SAME root, via the
                                        plugin ctx (door) AND via the raw config fallback
  (c) settings + WF_RUNS_ROOT        -> settings wins
  (d) relative runs_root             -> fail-closed error on every action, no fallback
  (e) profiles/<other>/workflows     -> refused (own profile home stays legal)
  (f) env profile + settings.profile -> env wins
  (g) no env + settings.profile      -> consent gate accepts a target that lists it
  (h) no env, no setting             -> 'default', byte-identical
  (+) no model-settable launcher arg exists on the tool schema

Stdlib-only, prints PASS/FAIL lines, exit 0 = green.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
failures = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)[:600]))
    if not ok:
        failures.append(name)

# ---------------------------------------------------------------- harness ----
PROBE = r'''
import importlib.util, json, os, sys
from pathlib import Path
ROOT = Path(sys.argv[1]); MODE = sys.argv[2]; SETTINGS = json.loads(sys.argv[3])
spec = importlib.util.spec_from_file_location("tb_door", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
common = door._common

RESERVED = {"model", "plugins", "security", "settings"}
class CoreFaithfulCtx:
    """PluginContext.get_config with core's exact plugin-relative key rules."""
    def __init__(self, settings): self.settings = settings
    def get_config(self, key, default=None):
        if not isinstance(key, str) or "/" in key or key.split(".")[0].lower() in RESERVED:
            raise ValueError("Expected a plugin-relative config key")
        cur = self.settings
        for seg in key.split("."):
            if not isinstance(cur, dict) or seg not in cur:
                return default
            cur = cur[seg]
        return cur
if MODE == "ctx":
    door._CTX = CoreFaithfulCtx(SETTINGS)          # the live door: settings via plugin ctx
# MODE == "raw": no ctx; settings (if any) sit in <hermes_home>/config.yaml on disk

out = {}
def _try(name, fn):
    try:
        v = fn(); out[name] = str(v) if isinstance(v, Path) else v
    except ValueError as e:
        out[name] = {"error": str(e)}
_try("runs_root", door.runs_root)
_try("common_runs_root", common.runs_root)
_try("effective", lambda: common.effective_runs_root({k: v for k, v in os.environ.items()
                                                       if k in ("HERMES_HOME", "WF_RUNS_ROOT")}))
_try("launcher", common.launcher_profile)
_try("hermes_bin", door._hermes_bin)
out["list"] = json.loads(door.handle({"action": "list"}))
out["status_missing"] = json.loads(door.handle({"action": "status", "run_id": "nope"}))
if os.environ.get("TB_PROFILE_GATE"):
    # (g): drive profile_errors the way the door does — launcher from launcher_profile(),
    # profiles dir = the fake estate's profiles/ — no graph arg anywhere.
    nodes = [{"id": "n", "type": "agent", "prompt": "x", "after": [], "profile": os.environ["TB_PROFILE_GATE"]}]
    out["gate"] = common.profile_errors(nodes, launcher=common.launcher_profile(),
                                        profiles_dir=common.profiles_root())
out["schema_props"] = sorted(door.WORKFLOW_PARAMS["properties"])
print("@@" + json.dumps(out, default=str))
'''

def yaml_settings(settings):
    lines = ["plugins:", "  entries:", "    hermes-workflows:", "      settings:"]
    for k, v in settings.items():
        lines.append(f"        {k}: {json.dumps(v)}")
    return "\n".join(lines) + "\n"

def probe(home, settings=None, mode="ctx", env=None, root=ROOT):
    """Fresh interpreter. mode 'ctx' -> settings through a core-faithful plugin ctx;
    mode 'raw' -> settings written to <home>/config.yaml, no ctx at all."""
    settings = settings or {}
    home = Path(home)
    if mode == "raw":
        home.mkdir(parents=True, exist_ok=True)
        (home / "config.yaml").write_text(yaml_settings(settings) if settings else "{}\n")
    e = {k: v for k, v in os.environ.items()
         if k not in ("HERMES_HOME", "WF_RUNS_ROOT", "HERMES_WF_HERMES_BIN", "TB_PROFILE_GATE")}
    e["HERMES_HOME"] = str(home)
    e.update(env or {})
    if e.get("HERMES_HOME") is None:
        e.pop("HERMES_HOME", None)
    p = subprocess.run([PY, "-c", PROBE, str(root), mode, json.dumps(settings if mode == "ctx" else {})],
                       capture_output=True, text=True, env=e, timeout=60, cwd=str(home))
    line = [l for l in p.stdout.splitlines() if l.startswith("@@")]
    if p.returncode != 0 or not line:
        raise AssertionError(f"probe died rc={p.returncode}\n{p.stdout[-1500:]}\n{p.stderr[-1500:]}")
    return json.loads(line[0][2:])

def fake_run(root, rid):
    r = Path(root) / rid
    (r / "nodes").mkdir(parents=True, exist_ok=True)
    (r / "graph.json").write_text(json.dumps({"name": "tb", "nodes": [
        {"id": "a", "type": "echo", "output": "ok", "after": []}]}))
    (r / "run.json").write_text(json.dumps({"name": "tb"}))
    return r

TMP = Path(tempfile.mkdtemp(prefix="tb-4142-", dir=str(ROOT / "tests")))
try:
    # ---- (a) no settings, no env: today's bytes ----------------------------
    # Reference = main's UNPATCHED wfcommon resolving in the identical env.
    ref_dir = TMP / "ref"; ref_dir.mkdir()
    base = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD~0:wfcommon.py"],
                          capture_output=True, text=True)
    try:
        # prefer the merge-base main copy when this is a branch; fall back to HEAD
        mb = subprocess.run(["git", "-C", str(ROOT), "merge-base", "HEAD", "origin/main"],
                            capture_output=True, text=True)
        ref = mb.stdout.strip() or "HEAD"
        base = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:wfcommon.py"],
                              capture_output=True, text=True)
    except Exception:
        pass
    have_ref = base.returncode == 0 and "def runs_root" in base.stdout
    if have_ref:
        (ref_dir / "wfcommon.py").write_text(base.stdout)
    home_a = TMP / "a-home"; home_a.mkdir()
    fake_home = TMP / "a-HOME"; fake_home.mkdir()
    env_a = {"HERMES_HOME": None, "HOME": str(fake_home)}
    got = probe(home_a, mode="ctx", env=env_a)
    exp_default = str(Path(fake_home) / ".hermes" / "workflows")
    if have_ref:
        rp = subprocess.run([PY, "-c",
            "import importlib.util,sys;s=importlib.util.spec_from_file_location('c',sys.argv[1]);"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "print(m.runs_root());print(m.launcher_profile())", str(ref_dir / "wfcommon.py")],
            capture_output=True, text=True, timeout=60,
            env={k: v for k, v in os.environ.items() if k not in ("HERMES_HOME", "WF_RUNS_ROOT")} | {"HOME": str(fake_home)})
        ref_root, ref_launch = rp.stdout.strip().splitlines()[-2:]
        check("(a) no settings/no env: runs_root == pre-fix resolver's answer (today's bytes)",
              got["runs_root"] == ref_root == got["common_runs_root"], (got["runs_root"], ref_root))
        check("(a) launcher == pre-fix 'default'", got["launcher"] == ref_launch == "default", (got["launcher"], ref_launch))
    else:
        check("(a) no settings/no env: $HOME/.hermes/workflows", got["runs_root"] == exp_default, got["runs_root"])
        check("(a) launcher 'default'", got["launcher"] == "default", got["launcher"])
    check("(a) no settings: list is the plain empty answer", got["list"].get("runs") == [], got["list"])

    # ---- (b) settings.runs_root -> door, act_list, run_state agree ---------
    shared = TMP / "shared-runs"
    rid = "20260929-000000-tb"
    fake_run(shared, rid)
    for mode in ("ctx", "raw"):
        home_b = TMP / f"b-home-{mode}"; home_b.mkdir()
        (home_b / "workflows").mkdir()
        fake_run(home_b / "workflows", "20260929-000000-wrongroot")   # must NOT be listed
        got = probe(home_b, {"runs_root": str(shared)}, mode=mode)
        check(f"(b/{mode}) runs_root() == settings.runs_root", got["runs_root"] == str(shared), got["runs_root"])
        check(f"(b/{mode}) wfcommon.runs_root agrees with door.runs_root", got["common_runs_root"] == got["runs_root"])
        check(f"(b/{mode}) effective_runs_root(env) agrees (single root)", got["effective"] == got["runs_root"], got["effective"])
        listed = [r["run_id"] for r in got["list"].get("runs", [])]
        check(f"(b/{mode}) handle('list') lists the run under settings.runs_root (resolver root first)",
              listed and listed[0] == rid, listed)
        check(f"(b/{mode}) legacy launch-root run stays listed (F1 #14 merge law unchanged)",
              "20260929-000000-wrongroot" in listed, listed)
        check(f"(b/{mode}) run_state read the run (status derived, not None)",
              got["list"]["runs"][0].get("status") in ("pending", "interrupted", "done", "running", "held"), got["list"])
    # no restart: same process, setting appears mid-life -> resolver follows at call time
    home_b2 = TMP / "b-home-live"; home_b2.mkdir()
    live = subprocess.run([PY, "-c", r'''
import importlib.util, sys, json
from pathlib import Path
ROOT = Path(sys.argv[1]); shared = sys.argv[2]
spec = importlib.util.spec_from_file_location("tb_live", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
class Ctx:
    s = {}
    def get_config(self, k, d=None): return self.s.get(k, d)
door._CTX = Ctx()
before = str(door.runs_root())
Ctx.s["runs_root"] = shared
after = str(door.runs_root())
print("@@" + json.dumps({"before": before, "after": after}))
''', str(ROOT), str(shared)], capture_output=True, text=True, timeout=60,
        env={**{k: v for k, v in os.environ.items() if k not in ("WF_RUNS_ROOT",)}, "HERMES_HOME": str(home_b2)})
    lv = json.loads([l for l in live.stdout.splitlines() if l.startswith("@@")][0][2:])
    check("(b) call-time read: setting appearing mid-process flips the resolver without restart",
          lv["before"] == str(home_b2 / "workflows") and lv["after"] == str(shared), lv)

    # ---- (c) settings + WF_RUNS_ROOT -> settings wins -----------------------
    envroot = TMP / "env-runs"; envroot.mkdir()
    for mode in ("ctx", "raw"):
        home_c = TMP / f"c-home-{mode}"; home_c.mkdir()
        got = probe(home_c, {"runs_root": str(shared)}, mode=mode, env={"WF_RUNS_ROOT": str(envroot)})
        check(f"(c/{mode}) settings.runs_root beats WF_RUNS_ROOT", got["runs_root"] == str(shared), got["runs_root"])
        check(f"(c/{mode}) effective_runs_root also prefers settings", got["effective"] == str(shared), got["effective"])
    # and WF_RUNS_ROOT still wins over the home default when no setting (precedence tail intact)
    home_c2 = TMP / "c-home-tail"; home_c2.mkdir()
    got = probe(home_c2, {}, mode="ctx", env={"WF_RUNS_ROOT": str(envroot)})
    check("(c) no setting: WF_RUNS_ROOT > HERMES_HOME/workflows (unchanged)", got["runs_root"] == str(envroot), got["runs_root"])

    # ---- (d) relative runs_root -> fail-closed -----------------------------
    for mode in ("ctx", "raw"):
        home_d = TMP / f"d-home-{mode}"; home_d.mkdir()
        got = probe(home_d, {"runs_root": "relative/runs"}, mode=mode)
        check(f"(d/{mode}) resolver raises (no silent fallback)",
              isinstance(got["runs_root"], dict) and "absolute" in got["runs_root"]["error"], got["runs_root"])
        check(f"(d/{mode}) handle('list') is an error naming the setting",
              "error" in got["list"] and "runs_root" in got["list"]["error"] and "absolute" in got["list"]["error"], got["list"])
        check(f"(d/{mode}) every action fails closed (status too)",
              "error" in got["status_missing"] and "runs_root" in got["status_missing"]["error"], got["status_missing"])
    # expanduser: '~/x' is accepted as absolute after expansion
    home_d2 = TMP / "d-home-tilde"; home_d2.mkdir()
    fake_home2 = TMP / "d-HOME"; fake_home2.mkdir()
    got = probe(home_d2, {"runs_root": "~/wf-runs"}, mode="ctx", env={"HOME": str(fake_home2)})
    check("(d) '~/x' expands to an absolute root", got["runs_root"] == str(fake_home2 / "wf-runs"), got["runs_root"])

    # ---- (e) profiles/<other>/workflows -> refused --------------------------
    estate = TMP / "estate"
    for n in ("p1", "other"):
        (estate / "profiles" / n).mkdir(parents=True)
        (estate / "profiles" / n / "config.yaml").write_text("{}\n")
    for mode in ("ctx", "raw"):
        got = probe(estate / "profiles" / "p1", {"runs_root": str(estate / "profiles" / "other" / "workflows")}, mode=mode)
        check(f"(e/{mode}) another profile's home is refused",
              isinstance(got["runs_root"], dict) and "other" in got["runs_root"]["error"], got["runs_root"])
        check(f"(e/{mode}) door action errors, never falls back", "error" in got["list"] and "profile" in got["list"]["error"], got["list"])
    got = probe(estate, {"runs_root": str(estate / "profiles" / "other" / "workflows")}, mode="ctx")
    check("(e) base home: any profiles/<name>/ subtree refused", isinstance(got["runs_root"], dict), got["runs_root"])
    got = probe(estate / "profiles" / "p1", {"runs_root": str(estate / "profiles" / "p1" / "workflows")}, mode="ctx")
    check("(e) own profile home stays legal", got["runs_root"] == str(estate / "profiles" / "p1" / "workflows"), got["runs_root"])
    got = probe(estate / "profiles" / "p1", {"runs_root": str(estate / "shared")}, mode="ctx")
    check("(e) estate-level shared dir legal from a profile", got["runs_root"] == str(estate / "shared"), got["runs_root"])

    # ---- (f) env profile + settings.profile -> env wins ----------------------
    for mode in ("ctx", "raw"):
        got = probe(estate / "profiles" / "p1", {"profile": "other"}, mode=mode)
        check(f"(f/{mode}) env-derived identity wins over settings.profile", got["launcher"] == "p1", got["launcher"])

    # ---- (g) no env + settings.profile -> consent gate sees the real launcher --
    tgt = estate / "profiles" / "target"
    tgt.mkdir()
    (tgt / "config.yaml").write_text("{}\n")
    (tgt / "workflow_team.json").write_text(json.dumps({"accept_from": ["bridge-seat"]}))
    for mode in ("ctx", "raw"):
        got = probe(estate, {"profile": "bridge-seat"}, mode=mode, env={"TB_PROFILE_GATE": "target"})
        check(f"(g/{mode}) env-blind launch: launcher_profile() == settings.profile", got["launcher"] == "bridge-seat", got["launcher"])
        check(f"(g/{mode}) consent gate accepts (target lists bridge-seat, not default)", got["gate"] == [], got["gate"])
    got = probe(estate, {}, mode="ctx", env={"TB_PROFILE_GATE": "target"})
    check("(g) same gate WITHOUT the setting rejects 'default' (the #41 repro)",
          len(got["gate"]) == 1 and "default" in got["gate"][0]["msg"], got["gate"])
    for bad in ("../evil", "a/b", ".hidden", "x\x01y"):
        got = probe(estate, {"profile": bad}, mode="ctx")
        check(f"(g) unsafe settings.profile {bad!r} fails closed",
              isinstance(got["launcher"], dict) and "error" in got["list"], (got["launcher"], got["list"]))

    # ---- (h) no env, no setting -> 'default' byte-identical -----------------
    for mode in ("ctx", "raw"):
        home_h = TMP / f"h-home-{mode}"; home_h.mkdir()
        got = probe(home_h, {}, mode=mode)
        check(f"(h/{mode}) launcher 'default'", got["launcher"] == "default", got["launcher"])
        check(f"(h/{mode}) runs_root = HERMES_HOME/workflows", got["runs_root"] == str(home_h / "workflows"), got["runs_root"])

    # ---- (+) no model-settable launcher/root arg ----------------------------
    check("(+) tool schema exposes no launcher/profile/runs_root argument",
          not ({"launcher", "profile", "runs_root", "dispatched_by", "hermes_home"} & set(got["schema_props"])),
          got["schema_props"])
    # hermes_bin still reads through the same helper (ctx path)
    home_i = TMP / "i-home"; home_i.mkdir()
    got = probe(home_i, {"hermes_bin": "/cfg/hermes"}, mode="ctx")
    check("(+) hermes_bin reads through the same owner-settings helper", got["hermes_bin"] == "/cfg/hermes", got["hermes_bin"])
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(("ALL PASS" if not failures else f"FAILED {len(failures)}: {failures}") + " test_tool_bridge_settings_9c41e2b7")
sys.exit(1 if failures else 0)
