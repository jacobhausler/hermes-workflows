#!/usr/bin/env python3
"""4052d57719653b1a: atomic library replay binding, no real runner."""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

BUILD = Path(__file__).parent
HOME = BUILD / "home_run_binding"
shutil.rmtree(HOME, ignore_errors=True)
os.environ["HERMES_HOME"] = str(HOME)
spec = importlib.util.spec_from_file_location("binding_door", str(BUILD.parent / "__init__.py"))
hw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw)
spawns = []
actual_spawn = hw._spawn_runner
hw._spawn_runner = lambda r: spawns.append(r)
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else " " + str(detail)))
    if not ok:
        failures.append(name)
_UNSET = object()
def run(graph=None, binding=_UNSET, **extra):
    args = {"action": "run", **extra}
    if graph is not None:
        args["graph"] = graph
    if binding is not _UNSET:
        args["run_context"] = binding
    return json.loads(hw.handle(args))
def snapshot(reply):
    return json.loads((HOME / "workflows" / reply["run_id"] / "graph.json").read_text())

graph = {"name": "bind-replay", "defaults": {"context": "Shared {run.key}"}, "nodes": [
    {"id": "first", "type": "agent", "goal": "key={run.key} branch={run.branch} argv={run.argv}; leave {item} and {other}", "context": "Target {run.key}"},
    {"id": "second", "type": "agent", "after": ["first"], "goal": "follow {run.branch}",
     "fanout": {"items": [{"goal": "item {run.key} {item}"}], "goal": "batch {run.argv} {item}"}},
    {"id": "gate", "type": "gate", "after": ["first"], "question": "ship {run.key}?", "options": ["yes", "no"]}]}
check("schema exposes run_context", "run_context" in hw.WORKFLOW_PARAMS["properties"])
assert run(graph=graph, **{})["run_id"]  # old unbound callers still launch
saved = HOME / "workflows" / "library" / "bind-replay.json"
saved.parent.mkdir(parents=True, exist_ok=True)
saved.write_text(json.dumps(graph))
original = saved.read_bytes()
replies = [run(binding={"key": key, "branch": branch, "argv": argv}, **{"from": "bind-replay"})
           for key, branch, argv in [("a1", "fix/a1", "pytest -k a1"), ("b2", "fix/b2", "pytest -k b2")]]
check("two bound replays launch", all("run_id" in r for r in replies), replies)
if all("run_id" in r for r in replies):
    a, b = map(snapshot, replies)
    check("resolved effective prompts and all first-wave roots", "key=a1 branch=fix/a1 argv=pytest -k a1" in a["nodes"][0]["goal"] and
          "Shared a1" in a["nodes"][0]["context"] and "Target a1" in a["nodes"][0]["context"] and
          "follow fix/a1" in a["nodes"][1]["goal"] and a["nodes"][2]["question"] == "ship a1?", a)
    check("fanout references only run bindings", a["nodes"][1]["fanout"]["items"][0]["goal"] == "item a1 {item}" and
          a["nodes"][1]["fanout"]["goal"] == "batch pytest -k a1 {item}" and "{other}" in a["nodes"][0]["goal"])
    check("different values yield different effective fingerprints", hw._common.efp({n["id"]: n for n in a["nodes"]}, a["nodes"][0]) !=
          hw._common.efp({n["id"]: n for n in b["nodes"]}, b["nodes"][0]))
check("library bytes unchanged", saved.read_bytes() == original)
for malformed in ({"key": 1}, {"bad-key": "x"}, {"key": "a"}, {}, [], "", 7, None):
    before = (len(spawns), set((HOME / "workflows").iterdir()))
    r = run(binding=malformed, **{"from": "bind-replay"})
    check("invalid binding fails atomically " + repr(malformed), "error" in r and
          (len(spawns), set((HOME / "workflows").iterdir())) == before, r)
check("missing reference names key", "missing key 'branch'" in run(binding={"key": "a"}, **{"from": "bind-replay"}).get("error", ""))
bad_ref = {"name": "bad-ref", "nodes": [{"id": "a", "type": "agent", "goal": "bad {run.bad-key}"}]}
before = (len(spawns), set((HOME / "workflows").iterdir()))
r = run(graph=bad_ref, binding={"key": "a"})
check("malformed placeholder rejects before spawn/write", "malformed reference" in r.get("error", "") and
      (len(spawns), set((HOME / "workflows").iterdir())) == before, r)
plain = {"name": "seed", "nodes": [{"id": "gate", "type": "gate", "question": "start?", "options": ["y"]},
        {"id": "a", "type": "agent", "after": ["gate"], "goal": "a"},
        {"id": "b", "type": "agent", "after": ["gate"], "goal": "b"}]}
r = run(graph=plain, binding="key=a1")
check("gate-first string reaches all eligible first-wave agents", "run_id" in r and
      all("key=a1" in n.get("context", "") for n in snapshot(r)["nodes"] if n["type"] == "agent"), r)
parallel = {"name": "parallel", "nodes": [{"id": x, "type": "agent", "goal": x} for x in ("a", "b")]}
r = run(graph=parallel, binding="note")
check("parallel roots both seeded", "run_id" in r and all("note" in n.get("context", "") for n in snapshot(r)["nodes"]), r)
r = run(graph=parallel)
check("no binding unchanged", "run_id" in r and all("context" not in n for n in snapshot(r)["nodes"]), r)
text = hw._wf_command("bind-replay key=a1")
check("/wf single atomic argument, no steer", 'run_context:"key=a1"' in text and 'from:"bind-replay"' in text and "steer" not in text, text)
# F6 (adversary, 2026-09-28): a bound value containing braces must NEVER land in
# a fan-out field — the runner re-renders fan-out goals per item with fmt_goal,
# which would interpolate the value a SECOND time against item fields.
braced = {"name": "brace-fan", "nodes": [{"id": "f", "type": "agent",
          "fanout": {"items": [{"item": "one"}], "goal": "do {run.tok} on {item}"}}]}
r = run(graph=braced, binding={"tok": "literal-with-{item}-inside"})
check("brace-valued binding into fan-out goal rejects before write", "must not contain braces" in r.get("error", "")
      and not (HOME / "workflows" / "brace-fan").exists(), r)
item_goal = {"name": "brace-item", "nodes": [{"id": "f", "type": "agent",
             "fanout": {"items": [{"item": "one", "goal": "i {run.tok} {item}"}], "goal": "g"}}]}
r = run(graph=item_goal, binding={"tok": "v{item}v"})
check("brace-valued binding into items[].goal rejects too", "must not contain braces" in r.get("error", ""), r)
plain_goal = {"name": "brace-plain", "nodes": [{"id": "a", "type": "agent", "goal": "go {run.tok}"}]}
r = run(graph=plain_goal, binding={"tok": "literal-{item}-inside"})
if "run_id" in r:
    check("brace value in a NON-fan-out goal is allowed (rendered once)", True, r)
    hw.act_stop({"run_id": r["run_id"]})
else:
    check("brace value in a NON-fan-out goal is allowed (rendered once)", False, r)
# Real runner + fake child: inspect the exact prompt file, not only graph.json.
hw._spawn_runner = actual_spawn
os.environ["HERMES_WF_HERMES_BIN"] = str(BUILD / "fake")  # operator-side launcher (122099)
live = {"name": "prompt-binding", "nodes": [{"id": "one", "type": "agent", "goal": "LIST: go {run.key}", "context": "branch={run.branch}"}]}
r = run(graph=live, binding={"key": "a1", "branch": "fix/a1"})
if "run_id" in r:
    hw.act_wait({"run_id": r["run_id"], "timeout": 30})
    prompts = list((HOME / "workflows" / r["run_id"] / "logs").glob("one.*.prompt.md"))
    check("bound graph reaches actual child prompt", bool(prompts) and
          "LIST: go a1" in prompts[0].read_text() and "branch=fix/a1" in prompts[0].read_text(), prompts)
else:
    check("bound graph reaches actual child prompt", False, r)
print("ALL PASS" if not failures else f"FAILURES PRESENT: {len(failures)}")
sys.exit(bool(failures))
