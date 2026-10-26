#!/usr/bin/env python3
"""Malformed {run.*} references are validate-time defects, not launch surprises.

Class bug (live receipt, two graphs in one wave): a prose token like
'{run.*}' or '{run.trunk-short or trunk}' in a render surface passes
validate_graph_full, then dies at EVERY launch with _bind_run_context's
ValueError('run_context malformed reference') — before any write. A
malformed key can never bind under ANY run_context, so the defect is
statically decidable and belongs in the door's errors[] envelope,
naming node and field, exactly like the include resolver already refuses
it for composite subtrees (wfcommon._include_render, same law).

Contract asserted here:
  1. a graph carrying a malformed {run.X} ref in goal, fan-out item goal,
     gate options, echo output, or defaults.context is REFUSED by
     validate_graph_full with one error per distinct occurrence, each
     naming the node (or 'defaults') and the offending literal;
  2. well-formed {run.IDENT} refs stay legal (no error added);
  3. a brace that is not a run ref ({item.id} fan-out placeholder,
     {notrun.x}) stays untouched by this check;
  4. PARITY (reconcile verdict @8cfcd7e): the live admission door
     (__init__._validation_error — the surface run/submit/save/amend actually
     route through) refuses the SAME fixture with the SAME run_ref defects,
     and act_run drops it before any spawn. The twins may never diverge in
     strictness (PR#84 F-2 law); pinning only validate_graph_full over-
     delivers while the door still admits the graph and it dies at bind time.
"""
import copy
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402


def _load_door():
    """The live admission door, sandboxed like tests/test_run_binding.py:
    HERMES_HOME + WF_RUNS_ROOT pinned to scratch BEFORE exec, owner settings
    reader neutralised at the resolver by wf_test_isolation."""
    scratch = Path(tempfile.mkdtemp(prefix="run_ref_door_"))
    os.environ["HERMES_HOME"] = str(scratch / "home")
    os.environ["WF_RUNS_ROOT"] = str(scratch / "workflows")
    spec = importlib.util.spec_from_file_location("wf_door_run_ref", ROOT / "__init__.py")
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)
    import wf_test_isolation as _iso
    _iso.install(door)
    return door


def _node(nid, goal, **kw):
    n = {"id": nid, "type": "agent", "goal": goal}
    n.update(kw)
    return n


def _errs(graph):
    return wfcommon.validate_graph_full(graph)


def _bad_literals(errs):
    joined = " || ".join(e["msg"] for e in errs if e.get("field") == "run_ref")
    return joined


def main():
    base_defaults = {"model": "tier:auto"}

    # 1. malformed refs in the four node surfaces + defaults.context
    graph = {
        "name": "ref-scan",
        "defaults": {**base_defaults, "context": "branch stack/{run.bad-key here}/x"},
        "nodes": [
            _node("a", "avoid the literal {run.*} token in prose"),
            _node("b", "clean", fanout={
                "items": [{"id": "i1", "goal": "token {run.a or b} here"}]}),
            {"id": "g", "type": "gate", "after": ["a"], "question": "q?",
             "options": ["proceed", "token {run.}empty"]},
            {"id": "e", "type": "echo", "after": ["a"],
             "output": "verdict {run.1nope}"},
        ],
    }
    errs = _errs(graph)
    ref_errs = [e for e in errs if e.get("field") == "run_ref"]
    assert len(ref_errs) == 5, f"expected 5 run_ref defects, got {len(ref_errs)}: {ref_errs}"
    named = {(e.get("node"), e["msg"]) for e in ref_errs}
    for node, lit in [("defaults", "{run.bad-key here}"),
                      ("a", "{run.*}"),
                      ("b", "{run.a or b}"),
                      ("g", "{run.}"),
                      ("e", "{run.1nope}")]:
        hits = [m for (n, m) in named if n == node and lit in m]
        assert hits, f"defect for node {node!r} must name {lit!r}: {sorted(named)}"
        assert "identifier" in hits[0], f"msg must name the identifier law: {hits[0]}"

    # 1b. PARITY: the live admission door refuses the SAME fixture with the
    # SAME run_ref defects (reconcile@8cfcd7e: at head the door returned None
    # for this exact graph and the launch died at bind time instead).
    door = _load_door()
    err = door._validation_error(copy.deepcopy(graph))
    assert err is not None, "the admission door must refuse the malformed-ref fixture"
    assert err.get("error_class") == "graph_invalid", err
    door_ref = [e for e in err["errors"] if e.get("field") == "run_ref"]
    assert {(e.get("node"), e["msg"]) for e in door_ref} == \
           {(e.get("node"), e["msg"]) for e in ref_errs}, \
        f"door and validate_graph_full diverge on run_ref defects: {door_ref}"

    # 1c. act_run end-to-end: refused at the door BEFORE any spawn — the
    # identical fixture must never reach _bind_run_context again.
    spawns = []
    door._spawn_runner = lambda r: spawns.append(r)
    out = door.act_run({"graph": copy.deepcopy(graph), "run_context": {"X": "v"}})
    assert out.get("error_class") == "graph_invalid", \
        f"act_run must refuse at the admission door, got: {out}"
    assert any(e.get("field") == "run_ref" for e in out.get("errors", [])), out
    assert not spawns, f"door refusal must precede any spawn: {spawns}"

    # 2. well-formed refs stay legal
    good = {
        "name": "ref-ok", "defaults": base_defaults,
        "nodes": [_node("a", "path {run.repo_path} brief {run.brief}"),
                  _node("b", "clean")],
    }
    assert not [e for e in _errs(good) if e.get("field") == "run_ref"], \
        "well-formed {run.IDENT} refs must not produce run_ref defects"

    # 3. non-run braces untouched
    other = {
        "name": "ref-other", "defaults": base_defaults,
        "nodes": [_node("b", "item {item.id} variant {variant.name} prose {notrun.x}"),
                  _node("a", "clean")],
    }
    assert not [e for e in _errs(other) if e.get("field") == "run_ref"], \
        "non-run braces must not produce run_ref defects"

    print("PASS: malformed run_context refs are validate-time defects")


if __name__ == "__main__":
    main()
