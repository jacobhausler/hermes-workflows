#!/usr/bin/env python3
"""Engine seed launcher for the ui2-proof capture driver (stdlib only, source-only).

Launches a zero-token graph through the SAME door the tool uses (spec-loads
<repo>/__init__.py, calls handle({"action": "run", ...})) under an isolated
runs root (WF_RUNS_ROOT wins per wfcommon), waits until the held gate is
proven (gate.held in events.jsonl), and prints the run id on stdout.

A door {\"error\": ...} payload is a hard failure (exit 1) — never a silent
launch that nobody proved. This mirrors the `wf.py redrive` precedent: the
runner ships the door call, one door, one mode law.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, help="plugin repo checkout (holds __init__.py, wf.py)")
    ap.add_argument("--runs-root", required=True, help="absolute test runs root (isolated)")
    ap.add_argument("--graph-file", required=True, help="JSON graph file to launch")
    ap.add_argument("--wait-held-s", type=float, default=25.0,
                    help="seconds to wait for the gate.held event (0 skips the proof wait)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    runs_root = Path(args.runs_root).resolve()
    if not runs_root.is_absolute():
        print("REFUSED: --runs-root must be absolute", file=sys.stderr)
        return 1
    graph = json.loads(Path(args.graph_file).read_text(encoding="utf-8"))
    if not graph.get("nodes"):
        print("REFUSED: graph has no nodes", file=sys.stderr)
        return 1

    os.environ["WF_RUNS_ROOT"] = str(runs_root)   # shared-team-root override wins (wfcommon)
    spec = importlib.util.spec_from_file_location("ui2_proof_door", repo / "__init__.py")
    if spec is None or spec.loader is None:
        print(f"REFUSED: no door module beside {repo}", file=sys.stderr)
        return 2
    door = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(door)

    payload = json.loads(door.handle({"action": "run", "graph": graph}))
    if "error" in payload and not payload.get("run_id"):
        print(f"DOOR_ERROR: {json.dumps(payload)[:800]}", file=sys.stderr)
        return 1
    run_id = payload.get("run_id")
    if not run_id:
        print(f"DOOR_ERROR: no run_id in {json.dumps(payload)[:800]}", file=sys.stderr)
        return 1

    run = runs_root / run_id
    if args.wait_held_s > 0:
        deadline = time.monotonic() + args.wait_held_s
        held = False
        while time.monotonic() < deadline and not held:
            events = run / "events.jsonl"
            if events.is_file():
                held = any('"gate.held"' in line for line in
                           events.read_text(encoding="utf-8", errors="replace").splitlines())
            if not held:
                time.sleep(0.3)
        if not held:
            print(f"HOLD_NOT_PROVEN: {run_id} (no gate.held within "
                  f"{args.wait_held_s}s)", file=sys.stderr)
            return 1
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
