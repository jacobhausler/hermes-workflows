#!/usr/bin/env python3
"""wofify — the WOFification authoring-time seam (est-h0huv).

WOFification converts a *way-of-working repo* (a skills repo: SKILL.md trees,
playbooks, agent personas, automation packs, guide docs) into a *pack*: a
shelf-ready bundle of converted wf/1 workflow graphs, adapted skills, and
compact rules. The agent-side conversion work — classifying dispositions and
rewriting procedures as graphs — is graph-driven and stays with the factory
(see references/wofification.md). This tool owns the DETERMINISTIC seams only:

  inventory  walk a repo tree, classify units by path shape, write
             <pack>/inventory.json (the census), create the pack tree.
  scaffold   write pack.json skeleton + README.md stub. Never overwrites.
  validate   admission-validate every pack graph with the door's own
             wfcommon.validate_graph_full. Names every defect; exits 1.
  shelf      read pack.json units and emit the exact adoption commands —
             workflow save/run lines for graphs, cp lines for skills/rules —
             after re-hashing every artifact (drift is a refusal, not a note).

Mirroring the vaporized wf_dialect.py precedent, this is deliberately NOT a
`workflow` tool action: conversion is an authoring-time file operation and the
door's action set stays closed. Stdlib only; no subprocess, no network, no
door writes. Deterministic: same tree, same bytes (sorted walks, no clocks in
the census). The contract and the pack layout are specified in
references/wofification.md.

CLI:
  python3 scripts/wofify.py inventory <repo_dir> --out <pack_dir>
  python3 scripts/wofify.py scaffold  <pack_dir> [--source URL] [--commit SHA]
  python3 scripts/wofify.py validate  <pack_dir>
  python3 scripts/wofify.py shelf     <pack_dir> [--skills-dir DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

__all__ = ["classify", "inventory_tree", "scaffold_pack", "validate_pack", "shelf_lines"]

GENERATED_BY = "wofify"
PACK_TREE = ("skills", "workflows", "rules", "reports")
_ID_SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_PHASE = re.compile(r"(?i)^#{1,4}[^\n]*\b(?:phase|step)\s*\d+")
_WIKILINK = re.compile(r"\[\[([A-Za-z0-9][A-Za-z0-9_-]{1,63})\]\]")
_SKILLREF = re.compile(r"\bskills/([A-Za-z0-9][A-Za-z0-9_-]{1,63})/")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _summary(path: Path) -> str:
    """First substantive prose line: outside front-matter, not a heading."""
    body = _text(path)
    if body.startswith("---"):
        fence = body.find("\n---", 3)
        body = body[fence + 4:] if fence != -1 else body
    for line in body.splitlines():
        stripped = line.strip()
        if len(stripped) >= 12 and not stripped.startswith(("#", "|", ">", "-", "*", "!", "`")):
            return stripped[:100]
    return ""


def _phases(path: Path) -> list:
    return [line.lstrip("#").strip() for line in _text(path).splitlines() if _PHASE.match(line)]


def _calls(path: Path) -> list:
    body = _text(path)
    found = set(_WIKILINK.findall(body)) | set(_SKILLREF.findall(body))
    return sorted(name for name in found if _ID_SAFE.match(name))


def classify(repo: Path) -> list:
    """Every unit in a way-of-working repo that carries working method.

    Kinds come from PATH SHAPE, never from prose (deterministic census):
      skills/<n>/SKILL.md            skill   (principle* -> principle;
                                             a router-named tree -> mode)
      skills/<n>/playbooks/*.md      playbook
      agents/*.md                    agent
      automations/**.(md|json)       automation
      docs/**/*.md                   doc
      *plugin.json at root           manifest
    """
    units = []
    for skill_md in sorted((repo / "skills").glob("*/SKILL.md")) if (repo / "skills").is_dir() else []:
        name = skill_md.parent.name
        head = "\n".join(_text(skill_md).splitlines()[:20])
        if name.startswith("principle"):
            kind = "principle"
        elif re.search(r"(?i)\brouter\b", name + head):
            kind = "mode"
        else:
            kind = "skill"
        units.append({"id": name, "kind": kind,
                      "path": str(skill_md.relative_to(repo)),
                      "summary": _summary(skill_md),
                      "phases": _phases(skill_md), "calls": _calls(skill_md)})
    for sub in sorted((repo / "skills").glob("*/playbooks/*.md")) if (repo / "skills").is_dir() else []:
        units.append({"id": f"{sub.parent.parent.name}-{sub.stem}", "kind": "playbook",
                      "path": str(sub.relative_to(repo)), "summary": _summary(sub),
                      "phases": _phases(sub), "calls": _calls(sub)})
    agents_dir = repo / "agents"
    for agent_md in sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []:
        units.append({"id": agent_md.stem, "kind": "agent",
                      "path": str(agent_md.relative_to(repo)), "summary": _summary(agent_md),
                      "phases": [], "calls": _calls(agent_md)})
    auto_dir = repo / "automations"
    for auto in sorted(p for ext in ("*.md", "*.json") for p in auto_dir.glob(ext)) if auto_dir.is_dir() else []:
        units.append({"id": auto.stem, "kind": "automation",
                      "path": str(auto.relative_to(repo)),
                      "summary": _summary(auto) if auto.suffix == ".md" else "",
                      "phases": _phases(auto) if auto.suffix == ".md" else [], "calls": []})
    docs_dir = repo / "docs"
    for doc in sorted(docs_dir.rglob("*.md")) if docs_dir.is_dir() else []:
        units.append({"id": str(doc.relative_to(docs_dir)).replace("/", "-").removesuffix(".md"),
                      "kind": "doc", "path": str(doc.relative_to(repo)),
                      "summary": _summary(doc), "phases": _phases(doc), "calls": _calls(doc)})
    for manifest in sorted(repo.glob("*plugin.json")):
        units.append({"id": manifest.stem if manifest.stem != "plugin" else "plugin",
                      "kind": "manifest", "path": str(manifest.relative_to(repo)),
                      "summary": "", "phases": [], "calls": []})
    return units


def inventory_tree(repo_dir: Path, pack_dir: Path) -> dict:
    repo = Path(repo_dir)
    if not repo.is_dir():
        raise SystemExit(f"wofify inventory: not a directory: {repo}")
    units = classify(repo)
    if not units:
        raise SystemExit("wofify inventory: no units found — refusing an empty census "
                         "(fail-closed: a silent zero here hides a wrong repo path)")
    pack = Path(pack_dir)
    for sub in PACK_TREE:
        (pack / sub).mkdir(parents=True, exist_ok=True)
    counts = {}
    for u in units:
        counts[u["kind"]] = counts.get(u["kind"], 0) + 1
    census = {"repo": repo.name, "generated_by": GENERATED_BY,
              "counts": {k: counts[k] for k in sorted(counts)}, "units": units}
    (pack / "inventory.json").write_text(
        json.dumps(census, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return census


def scaffold_pack(pack_dir: Path, source_url: str, commit: str) -> dict:
    pack = Path(pack_dir)
    if not pack.is_dir():
        raise SystemExit(f"wofify scaffold: pack dir does not exist — run inventory first: {pack}")
    skeleton = {"pack": pack.name, "source": {"url": source_url, "commit": commit},
                "generated_by": GENERATED_BY, "units": [], "counts": {},
                "license": "declare before publishing"}
    _write_new(pack / "pack.json", json.dumps(skeleton, indent=2, sort_keys=True) + "\n")
    _write_new(pack / "README.md",
               f"# {pack.name} — WOFification pack\n\n"
               f"Source: {source_url or '<unknown>'}\n\n"
               "Fill pack.json units (id, disposition, artifact, sha256) from the convert\n"
               "results, then run `wofify validate` and `wofify shelf`.\n")
    return skeleton


def _write_new(path: Path, content: str) -> None:
    if path.exists():
        raise SystemExit(f"wofify scaffold: refusing to overwrite {path} (a census or a "
                         "filled pack.json is authored state — delete by hand to replace)")
    path.write_text(content, encoding="utf-8")


def validate_pack(pack_dir: Path) -> dict:
    pack = Path(pack_dir)
    graphs = sorted(p for p in ((pack / "workflows").glob("*.json")
                                if (pack / "workflows").is_dir() else [])
                    if not p.name.endswith(".cards.json"))  # desktop-card sidecars are not graphs
    if not graphs:
        raise SystemExit("wofify validate: no graphs under <pack>/workflows/ — refusing to "
                         "report green on nothing (zero graphs is a loud zero, not a pass)")
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import wfcommon  # same-repo sibling; stdlib-only (rule 7 holds)

    report = {"graphs": len(graphs), "valid": 0, "invalid": []}

    def reader(name):  # pack-local first, plugin examples second
        ex = root / "examples"
        cands = [pack / "workflows" / f"{name}.json"]
        if ex.is_dir():
            cands += sorted(ex.glob(f"*/{name}.json"))
        for cand in cands:
            if cand.is_file():
                return json.loads(cand.read_text(encoding="utf-8"))
        return None

    for g in graphs:
        try:
            graph = json.loads(g.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            report["invalid"].append({"file": str(g.relative_to(pack)), "errors": [str(exc)]})
            continue
        try:  # authored state compiles first: include bases expanded, then the door's own full validator
            graph, _notes = wfcommon.expand_includes(graph, reader)
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            report["invalid"].append({"file": str(g.relative_to(pack)), "errors": [str(exc)]})
            continue
        errs = wfcommon.validate_graph_full(graph)
        if errs:
            report["invalid"].append({"file": str(g.relative_to(pack)),
                                      "errors": [f"{e.get('field', '?')}: {e.get('msg', '?')}"
                                                 for e in errs]})
        else:
            report["valid"] += 1
    return report


def shelf_lines(pack_dir: Path, skills_dir: str) -> list:
    pack = Path(pack_dir)
    try:
        manifest = json.loads((pack / "pack.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"wofify shelf: unreadable pack.json ({exc}) — scaffold it first")
    units = manifest.get("units")
    if not isinstance(units, list) or not units:
        raise SystemExit("wofify shelf: pack.json carries no units — an empty shelf is a "
                         "refusal, not an empty script (honest loud zero)")
    lines = ["#!/bin/sh", f"# adoption commands for pack '{manifest.get('pack', pack.name)}'",
             f"# source: {(manifest.get('source') or {}).get('url', '<unknown>')}",
             "set -eu"]
    problems = []
    for unit in units:
        uid = unit.get("id", "<missing-id>")
        if not _ID_SAFE.match(str(uid)):
            problems.append(f"{uid!r}: id fails the safe-id grammar (no shell interpolation of it)")
            continue
        disp = unit.get("disposition", "skip")
        artifact = unit.get("artifact")
        if disp == "skip":
            lines.append(f"# {uid}: skipped — {unit.get('reason', 'already covered natively')}")
            continue
        if not artifact:
            problems.append(f"{uid}: disposition '{disp}' names no artifact")
            continue
        path = pack / artifact
        if not path.is_file():
            problems.append(f"{uid}: artifact missing on disk: {artifact}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if unit.get("sha256") and unit["sha256"] != digest:
            problems.append(f"{uid}: sha256 drift — pack.json says {unit['sha256']}, "
                            f"disk says {digest}")
            continue
        if disp == "wof":
            payload = json.dumps({"action": "save", "name": uid,
                                  "graph_path": str(path.resolve())}, sort_keys=True)
            lines.append(f"# {uid}: import to the library, then launch it")
            lines.append(f"hermes chat --query 'workflow {payload}' -Q || true")
            lines.append(f"# or in any session: {{\"action\": \"run\", \"name\": \"{uid}\"}}")
        elif disp in ("skill", "rule"):
            lines.append(f"mkdir -p {skills_dir}/{uid}")
            lines.append(f"cp {path.resolve()} {skills_dir}/{uid}/")
        else:
            problems.append(f"{uid}: unknown disposition '{disp}' "
                            "(closed set: skill|wof|rule|skip)")
    if problems:
        raise SystemExit("wofify shelf: refusing —\n  " + "\n  ".join(problems))
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="wofify",
        description="WOFification authoring-time seam: inventory / scaffold / validate / shelf "
                    "(contract: references/wofification.md)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory", help="census a way-of-working repo into <pack>/inventory.json")
    p.add_argument("repo_dir")
    p.add_argument("--out", required=True, dest="pack_dir")
    p = sub.add_parser("scaffold", help="write pack.json + README.md skeleton (never overwrites)")
    p.add_argument("pack_dir")
    p.add_argument("--source", default="")
    p.add_argument("--commit", default="")
    p = sub.add_parser("validate", help="admission-validate every pack graph")
    p.add_argument("pack_dir")
    p = sub.add_parser("shelf", help="emit adoption commands for the pack's units")
    p.add_argument("pack_dir")
    p.add_argument("--skills-dir", default="$HOME/.hermes/skills")
    args = ap.parse_args(argv)

    if args.cmd == "inventory":
        census = inventory_tree(Path(args.repo_dir), Path(args.pack_dir))
        print(json.dumps({"unit_count": len(census["units"]), "counts": census["counts"],
                          "out": str(Path(args.pack_dir) / "inventory.json")}, sort_keys=True))
        return 0
    if args.cmd == "scaffold":
        scaffold_pack(Path(args.pack_dir), args.source, args.commit)
        print(json.dumps({"scaffolded": str(args.pack_dir)}, sort_keys=True))
        return 0
    if args.cmd == "validate":
        report = validate_pack(Path(args.pack_dir))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["valid"] == report["graphs"] else 1
    lines = shelf_lines(Path(args.pack_dir), args.skills_dir)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
