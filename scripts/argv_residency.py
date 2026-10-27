#!/usr/bin/env python3
"""Read-only audit of persisted launch locations (provenance atbrace:hw-cxk).

Scan cron scripts, job stores, workflow gates, and post-exit registrations.
Exit 0 means no findings, 1 means findings. --guard uses the same checks and
exits silently when clean. Dynamic shell paths are unresolved, not certified.
No mode executes commands, changes a job, or repairs the estate.
"""
import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wfcommon


def _finding(source, entrypoint, status, detail, **extra):
    return dict(extra, source=str(source), entrypoint=str(entrypoint), status=status, detail=detail)


def _classify(source, token, roots, **extra):
    status, detail = wfcommon.entrypoint_residency(token, roots)
    return [] if status == "resident" else [_finding(source, token, status, detail, **extra)]


def _argv(source, argv, roots, **extra):
    return [dict(f, source=str(source), **extra) for f in wfcommon.argv_residency(argv, roots)]


def _findings_for_shim(path, roots):
    out = _classify(path, str(path), roots)
    try:
        text = path.read_text(errors="replace")
    except OSError as exc:
        return out + [_finding(path, "-", "unreadable", str(exc))]
    for line in text.replace("\\\n", "").splitlines():
        if line.lstrip().startswith("#"):
            continue
        try:
            tokens = shlex.split(line, comments=True)
        except ValueError as exc:
            if line.lstrip().startswith("exec "):
                out.append(_finding(path, "-", "unresolved", str(exc)))
            continue
        clean = []
        skip = False
        for token in tokens:
            if skip:
                skip = False
                continue
            redirect = re.match(r"^\d*(?:>>?|<<?|<>|>&|<&)(.*)$", token)
            if redirect:
                skip = not redirect[1]
            else:
                clean.append(token)
        tokens = clean
        while tokens and "=" in tokens[0] and tokens[0].partition("=")[0].isidentifier():
            if tokens[0].startswith("PATH="):
                out.append(_finding(path, "PATH", "unresolved", "shell PATH changes require an explicit resident argv"))
            tokens = tokens[1:]
        if not tokens:
            continue
        if tokens[0] == "exec":
            tokens = tokens[1:]
            if tokens and tokens[0] == "--":
                tokens = tokens[1:]
            if tokens:
                out += _argv(path, tokens, roots)
        elif tokens[0] in {"source", "."} and len(tokens) > 1:
            out += _classify(path, tokens[1], roots)
        elif tokens[0].startswith("/") or Path(tokens[0]).name in {
                "python", "python3", "bash", "sh", "env", "node", "ruby", "perl"}:
            out += _argv(path, tokens, roots)
    return out


def _resolve_store_script(store, script):
    p = Path(script)
    if p.is_absolute():
        return p
    home = store.parent.parent if store.parent.name == "cron" else store.parent
    return home / "scripts" / p


def _findings_for_store(store, roots):
    try:
        data = json.loads(store.read_text())
    except (OSError, ValueError) as exc:
        return [_finding(store, "-", "unreadable", str(exc))]
    jobs = data.get("jobs") if isinstance(data, dict) else data
    if not isinstance(jobs, list):
        return [_finding(store, "-", "invalid", "cron store must contain a jobs list")]
    out = []
    for job in jobs:
        if not isinstance(job, dict):
            out.append(_finding(store, "-", "invalid", "cron job must be an object"))
            continue
        extra = {"job": job.get("name") or job.get("id")}
        script = job.get("script")
        if script:
            if not isinstance(script, str):
                out.append(_finding(store, "-", "invalid", "script must be a string", **extra))
                continue
            resolved = _resolve_store_script(store, script)
            findings = _classify(store, str(resolved), roots, **extra)
            out += findings
            if not findings and resolved.is_file() and resolved.suffix in {".sh", ".bash"}:
                out += _findings_for_shim(resolved, roots)
        for key in ("argv", "command"):
            if job.get(key):
                argv = job[key]
                if isinstance(argv, str):
                    try:
                        argv = shlex.split(argv)
                    except ValueError as exc:
                        out.append(_finding(store, "-", "unresolved", str(exc), **extra))
                        continue
                out += _argv(store, argv, roots, **extra)
    return out


def _findings_for_run(run, roots):
    out = []
    hook = run / "post_exit_hook.json"
    if hook.is_file():
        try:
            data = json.loads(hook.read_text())
            script = data.get("script") if isinstance(data, dict) else None
            if not isinstance(script, str) or not script:
                raise ValueError("hook registration must name a script")
            out += _classify(hook, script, roots)
        except (OSError, ValueError) as exc:
            out.append(_finding(hook, "-", "invalid", str(exc)))
    graph = run / "graph.json"
    if graph.is_file():
        try:
            data = json.loads(graph.read_text())
            nodes = data.get("nodes") if isinstance(data, dict) else None
            if not isinstance(nodes, list):
                raise ValueError("graph must contain a nodes list")
            for node in nodes:
                if not isinstance(node, dict):
                    raise ValueError("graph node must be an object")
                wait = node.get("wait")
                if isinstance(wait, dict) and "until_argv" in wait:
                    out += _argv(graph, wait["until_argv"], roots, node=node.get("id"))
        except (OSError, ValueError) as exc:
            out.append(_finding(graph, "-", "invalid", str(exc)))
    return out


def collect(homes, stores, runs, roots):
    if roots is None:
        roots = wfcommon.stable_argv_roots()
        if not os.environ.get("WF_ARGV_STABLE_ROOTS"):
            scopes = [*homes, *(p.parent.parent for p in stores if p.parent.name == "cron")]
            scopes += [p for home in homes for p in (home / "profiles").glob("*") if p.is_dir()]
            roots += [scope / name for scope in scopes for name in ("scripts", "plugins", "installs")]
    findings = []
    for home in homes:
        if not home.is_dir():
            findings.append(_finding(home, "-", "missing", "audit home does not exist"))
            continue
        for scope in [home, *sorted((home / "profiles").glob("*"))]:
            for shim in sorted((scope / "scripts").rglob("*.sh")):
                findings += _findings_for_shim(shim, roots)
            store = scope / "cron" / "jobs.json"
            if store.is_file():
                findings += _findings_for_store(store, roots)
            runs += sorted(p for p in (scope / "workflows").glob("*") if p.is_dir())
    for store in stores:
        findings += _findings_for_store(store, roots)
    for run in sorted(set(runs)):
        if not run.is_dir():
            findings.append(_finding(run, "-", "missing", "run directory does not exist"))
        else:
            findings += _findings_for_run(run, roots)
    seen, unique = set(), []
    for finding in findings:
        key = (finding["source"], finding["entrypoint"], finding["status"],
               finding.get("job"), finding.get("node"))
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--home", action="append", type=Path, help="home to audit, including profiles and runs")
    ap.add_argument("--cron-store", action="append", type=Path)
    ap.add_argument("--run-dir", action="append", type=Path)
    ap.add_argument("--runs-root", action="append", type=Path)
    ap.add_argument("--stable-root", action="append", type=Path,
                    help="declared stable root for fixtures or custom installs, repeatable")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--guard", action="store_true", help="same audit, silent when clean")
    args = ap.parse_args(argv)
    explicit = args.home or args.cron_store or args.run_dir or args.runs_root
    home = Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))
    homes = args.home or ([] if explicit else [home])
    run_roots = args.runs_root or []
    if not explicit and os.environ.get("WF_RUNS_ROOT"):
        run_roots.append(Path(os.environ["WF_RUNS_ROOT"]))
    runs = list(args.run_dir or [])
    for root in run_roots:
        runs += sorted(p for p in root.glob("*") if p.is_dir()) if root.is_dir() else [root]
    findings = collect(homes, args.cron_store or [], runs, args.stable_root)
    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
    elif findings or not args.guard:
        for finding in findings:
            print(f"{finding['status'].upper()} {finding['source']} {finding['entrypoint']} ({finding['detail']})")
        print(f"argv-residency: {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
