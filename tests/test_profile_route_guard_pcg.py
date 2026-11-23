#!/usr/bin/env python3
"""Papercut 2026-11-23 — a profile-carried route must be COMPLETE before the
door lets its node spawn.

The incident: a seat's profile config.yaml carried only `model: {default: ...}`
(the codex route). Nothing pre-spawn named the missing half; the child died at
connection start with `Hermes couldn't start the model connection:
invalid_params`. The measured faces (2026-11-23, this estate): bare
`model.default` -> "not connected to any AI provider"; default+provider ->
the invalid_params copy itself (agent-init refusal, locales/en.yaml
`agent_init_failed`). A provider-less node's spawn argv carries no --provider
(wf.py builds it from node["provider"]), so the profile FILE is the sole route
source — the door can read it and refuse there.

The guard (profile_errors, rule slug `profile_route_incomplete`): consent-clean
target + provider-less node + config.yaml that claims a model without naming a
provider -> one typed row, pre-spawn, carrying the #708 fix-shape example
(RULE_EXAMPLES["profile_route_incomplete"] = the estate's working stanza).
Boundaries pinned below: an explicit provider (config OR node) passes — the
door refuses MISSING decisions, never express ones (auto included); no model
stanza / empty default = no claim; `provider/model` string form carries the
provider; a consent failure still yields exactly one row (route check runs
only after clean consent); unparseable config stays silent for this rule;
the example config itself passes the rule (golden); the row rides the door
envelope with the example; mutating a row never scribbles the table.

Run:  python3 tests/test_profile_route_guard_pcg.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon as W

FAILS = []
N = 0

def check(name, cond, detail=""):
    global N
    N += 1
    if not cond:
        FAILS.append(f"FAIL {name} {detail}")
        print(f"FAIL {name} {detail}")
    else:
        print(f"ok   {name}")


BASE = Path(tempfile.mkdtemp(prefix="pcg-home-"))
PROOT = BASE / "root" / "profiles"

def mkprofile(name, cfg_text, consent=("repo-bot",)):
    ph = PROOT / name
    ph.mkdir(parents=True)
    (ph / "config.yaml").write_text(cfg_text)
    if consent is not None:
        (ph / "workflow_team.json").write_text(
            json.dumps({"accept_from": list(consent)}))
    return ph

def nodes(**over):
    base = {"id": "review", "type": "agent", "goal": "g", "after": ["fix"]}
    base.update(over)
    return [dict(base), {"id": "fix", "type": "agent", "goal": "g"}]

def PE(name, **over):
    return W.profile_errors(nodes(profile=name, **over), launcher="repo-bot",
                            profiles_dir=PROOT)

# ---------- the refusal ----------
mkprofile("bare", "model:\n  default: my-codex-model\n")
e = PE("bare")
check("bare model.default refuses exactly one typed row",
      len(e) == 1 and e[0]["node"] == "review" and e[0]["field"] == "profile",
      json.dumps(e))
check("msg names the file, the missing key, and the death it prevents",
      all(s in e[0]["msg"] for s in ("config.yaml", "model.provider",
                                     "my-codex-model", "connection start")), e[0]["msg"])
check("row carries the #708 fix-shape example (deep-equal to the bank)",
      e[0].get("example") == W.RULE_EXAMPLES["profile_route_incomplete"], json.dumps(e))
check("example is the accepting config: model.default + model.provider",
      e[0]["example"] == {"model": {"default": "my-codex-model",
                                    "provider": "openai-codex"}})

# mutating a row's example never scribbles on the table (z79 law, new row type too)
e[0]["example"]["model"]["provider"] = "scribbled"
check("the table is immutable through the row (deep copy per rejection)",
      W.RULE_EXAMPLES["profile_route_incomplete"]["model"]["provider"] == "openai-codex")

# ---------- the accepting shape passes (golden: the example itself) ----------
mkprofile("fixshape", json.dumps(W.RULE_EXAMPLES["profile_route_incomplete"]))
check("GOLDEN: the banked example written as config.yaml passes the rule",
      PE("fixshape") == [], json.dumps(PE("fixshape")))

# ---------- express decisions are never refused ----------
mkprofile("explicit", "model:\n  default: my-codex-model\n  provider: openai-codex\n")
check("complete config passes (the estate's working profile-carried shape)",
      PE("explicit") == [])
mkprofile("autochoice", "model:\n  default: fake\n  provider: auto\n")
check("explicit `provider: auto` is a decision, not a hole — passes",
      PE("autochoice") == [])
mkprofile("bare2", "model:\n  default: my-codex-model\n")
check("node declaring provider completes the route — passes",
      PE("bare2", provider="openai-codex") == [])
check("node provider must be a non-empty string (blank = no claim)",
      len(PE("bare2", provider="   ")) == 1)

# ---------- no claim, no refusal ----------
mkprofile("nostanza", "terminal:\n  backend: local\n")
check("config without a model stanza makes no claim — passes", PE("nostanza") == [])
mkprofile("empty", "model:\n  default: ''\n  aliases: {}\n")
check("empty model.default declares nothing — passes", PE("empty") == [])
mkprofile("aliaskey", "model:\n  model: my-codex-model\n  provider: openai-codex\n")
check("core's documented `model` alias key + provider passes", PE("aliaskey") == [])
mkprofile("aliasbare", "model:\n  model: my-codex-model\n")
e = PE("aliasbare")
check("`model` alias key WITHOUT provider refuses like default",
      len(e) == 1 and "my-codex-model" in e[0]["msg"], json.dumps(e))
mkprofile("stringroute", "model: openai-codex:my-codex-model\n")
check("provider:model string form carries the provider — passes",
      PE("stringroute") == [])
mkprofile("stringslash", "model: openai-codex/my-codex-model\n")
check("provider/model string form passes", PE("stringslash") == [])
mkprofile("stringbare", "model: my-codex-model\n")
check("bare string model value without provider refuses", len(PE("stringbare")) == 1)
mkprofile("unparse", "model: [unclosed\n  :::\n")
check("unparseable config stays silent for THIS rule (no new trap)",
      PE("unparse") == [])

# ---------- ordering law: consent first, at most one row per node ----------
mkprofile("noc", "model:\n  default: my-codex-model\n", consent=None)
e = PE("noc")
check("missing consent is still THE row (route check never doubles it)",
      len(e) == 1 and "workflow_team.json" in e[0]["msg"], json.dumps(e))
mkprofile("wrong", "model:\n  default: my-codex-model\n", consent=("someone-else",))
e = PE("wrong")
check("unaccepted launcher is still THE row (one row per node preserved)",
      len(e) == 1 and "delegation" in e[0]["msg"], json.dumps(e))
mkprofile("nolist", "model:\n  default: my-codex-model\n", consent=None)
(PROOT / "nolist" / "workflow_team.json").write_text('{"accept_from": "repo-bot"}')
e = PE("nolist")
check("non-list accept_from is still THE row", len(e) == 1 and "accept_from" in e[0]["msg"],
      json.dumps(e))

# ---------- non-spawning / keyless nodes stay silent ----------
gate = [{"id": "g", "type": "gate", "question": "?", "profile": "bare"},
        {"id": "a", "type": "agent", "goal": "g"}]
check("gate nodes carry no route: profile_errors silent as before",
      W.profile_errors(gate, launcher="repo-bot", profiles_dir=PROOT) == [])

# ---------- the door envelope stamps the key universally over these rows ----------
# door._profile_error resolves the launcher from HERMES_HOME: a profile-home-shaped
# HERMES_HOME == launcher "repo-bot" (the fixture consent lists), and profiles_root
# lands back on PROOT either way.
os.environ["HERMES_HOME"] = str(PROOT / "repo-bot")
os.environ["WF_RUNS_ROOT"] = str(BASE / "wf")
os.makedirs(PROOT / "repo-bot", exist_ok=True)
import importlib.util
_spec = importlib.util.spec_from_file_location("door_pcg", ROOT / "__init__.py")
assert _spec is not None and _spec.loader is not None
door = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(door)
graph = {"name": "pcg", "nodes": [{"id": "solo", "type": "agent", "goal": "say hi",
                                    "profile": "bare"}]}
bad = door._profile_error(graph)
check("door._profile_error refuses the bare-profile graph",
      bad is not None and "connection start" in bad["error"], json.dumps(bad)[:300])
assert bad is not None
check("envelope: the row rides errors[] with example + msg (stamp kept it)",
      any(r.get("example") == W.RULE_EXAMPLES["profile_route_incomplete"]
          and "example" in r for r in bad["errors"]), json.dumps(bad["errors"]))
gp = BASE / "bare.workflow.json"
gp.write_text(json.dumps(graph))
import subprocess
env = dict(os.environ, HERMES_HOME=str(PROOT / "repo-bot"),
           WF_RUNS_ROOT=str(BASE / "wf"))
r = subprocess.run([sys.executable, str(ROOT / "wf.py"), "validate", str(gp)],
                   capture_output=True, text=True, env=env, timeout=120)
check("wf.py validate: red verdict exits 1 on the bare route",
      r.returncode == 1, f"rc={r.returncode} out={r.stdout[:300]}")
check("wf.py validate: human channel names the defect and prints the fix shape",
      "connection start" in r.stdout and "openai-codex" in r.stdout, r.stdout[:500])

print(f"{'FAILED' if FAILS else 'OK'}: {len(FAILS)} failure(s) across {N} checks")
sys.exit(1 if FAILS else 0)
