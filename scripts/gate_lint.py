#!/usr/bin/env python3
"""Gate-lint (#477): every gate option string must appear verbatim in its gate's doc text.

Symptom (issue #477): a human gate's question advertised "answer fix-round then
relaunch" while the option string was "fix-round: relaunch this WOF with findings"
— a releaser typing the short token shown in the question matched NO option and
the hold never released. Two independent fix crews codified "the question must
quote its option strings verbatim" into goal prose; this lint makes that a
machine-checked law instead of folklore.

Contract: for every human gate node that ships with an ``options`` list, EACH
option string must appear verbatim (exact substring, case-sensitive — the
executor matches the human's typed answer against the option string exactly, so
any softer match here would bless drift that bites at release time) somewhere in
that gate's own doc text: its ``question`` plus ``context``. The gate's doc text
IS the release instructions; drift between it and ``options`` is the bug.

Scope — everything a releaser can actually read as an example or doc:
  * JSON graphs under examples/, library/, docs/  (parsed; gate nodes at any depth)
  * fenced ``` blocks in AGENTS.md, README.md, SKILL.md, CONTRIBUTING.md,
    INSTALL.md, SECURITY.md, docs/**/*.md, references/**/*.md
    (each top-level JSON object in each block is linted if it is a gate node).
Machine/when gates (no ``options``) are pure routing — nothing for a human to
answer — and are skipped. receipts/ is a historical evidence ledger, not shipped
doc truth, and is deliberately out of scope.

Exit 1 lists every offender as file:line:<node-id>: option '<s>' not verbatim.
Import API: collect(root) -> Scan(gates, options_checked, violations). Stdlib only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

JSON_DIRS = ("examples", "library", "docs")
MD_FILES = ("AGENTS.md", "README.md", "SKILL.md", "CONTRIBUTING.md",
            "INSTALL.md", "SECURITY.md")
MD_DIRS = ("docs", "references")

_FENCE = re.compile(r"^```[ \t]*[A-Za-z0-9_-]*[ \t]*\n(.*?)^```[ \t]*$",
                    re.M | re.S)


class Violation:
    __slots__ = ("rel", "line", "node", "option", "kind")

    def __init__(self, rel, line, node, option, kind):
        self.rel, self.line, self.node, self.option, self.kind = \
            rel, line, node, option, kind

    def __str__(self):
        return (f"{self.rel}:{self.line}:{self.node}: option {self.option!r} "
                f"not verbatim in gate doc text (question+context)")


class Scan:
    def __init__(self, gates, options_checked, violations):
        self.gates = gates
        self.options_checked = options_checked
        self.violations = violations


def iter_gate_nodes(obj):
    """Yield every dict node with type == 'gate' anywhere in parsed JSON."""
    if isinstance(obj, dict):
        if obj.get("type") == "gate":
            yield obj
        for v in obj.values():
            yield from iter_gate_nodes(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_gate_nodes(v)


def human_options(node):
    """The options list of a human gate: list[str], or None (machine/routing)."""
    opts = node.get("options")
    if isinstance(opts, list) and opts and all(isinstance(o, str) for o in opts):
        return opts
    return None


def doc_text(node):
    return (node.get("question") or "") + "\n" + (node.get("context") or "")


def check_node(node):
    """Violating option strings of one gate node (empty list when clean)."""
    opts = human_options(node)
    if opts is None:
        return []
    text = doc_text(node)
    return [o for o in opts if o not in text]


def _top_level_json_objects(block):
    """Balanced-brace scan: yields each depth-0 {...} slice of a text block."""
    depth = 0
    start = None
    in_str = esc = False
    for i, ch in enumerate(block):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                yield block[start:i + 1]
                start = None


def _line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def lint_json_text(rel, raw):
    """Violations from one shipped graph file."""
    out = []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return out, 0, 0
    gates = opts_checked = 0
    for node in iter_gate_nodes(data):
        opts = human_options(node)
        if opts is None:
            continue
        gates += 1
        opts_checked += len(opts)
        for o in check_node(node):
            out.append(Violation(rel, 1, node.get("id", "?"), o, "json"))
    return out, gates, opts_checked


def lint_md_text(rel, raw):
    """Violations from gate snippets inside fenced blocks of one doc."""
    out = []
    gates = opts_checked = 0
    for m in _FENCE.finditer(raw):
        block, block_at = m.group(1), m.start(1)
        for slice_ in _top_level_json_objects(block):
            try:
                node = json.loads(slice_)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            for g in iter_gate_nodes(node):
                opts = human_options(g)
                if opts is None:
                    continue
                gates += 1
                opts_checked += len(opts)
                line = _line_of(raw, block_at + block.find(slice_))
                for o in check_node(g):
                    out.append(Violation(rel, line, g.get("id", "?"), o, "md"))
    return out, gates, opts_checked


def collect(root: "str | Path" = "."):
    root = Path(root)
    violations = []
    gates = opts_checked = 0
    seen = set()
    files = []
    for d in JSON_DIRS:
        base = root / d
        if base.is_dir():
            files += sorted(p for p in base.rglob("*.json") if p.is_file())
    for name in MD_FILES:
        p = root / name
        if p.is_file():
            files.append(p)
    for d in MD_DIRS:
        base = root / d
        if base.is_dir():
            files += sorted(p for p in base.rglob("*.md") if p.is_file())
    for p in files:
        rel = str(p.relative_to(root))
        if rel in seen:
            continue
        seen.add(rel)
        try:
            raw = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        v, g, o = (lint_json_text(rel, raw) if p.suffix == ".json"
                   else lint_md_text(rel, raw))
        violations += v
        gates += g
        opts_checked += o
    return Scan(gates, opts_checked, violations)


def main(argv):
    root = argv[1] if len(argv) > 1 else "."
    scan = collect(root)
    for v in sorted(scan.violations, key=lambda v: (v.rel, v.line, v.node)):
        print(v)
    print(f"GATE-LINT: {scan.gates} human gates / {scan.options_checked} "
          f"option strings checked — {len(scan.violations)} drift(s)")
    return 1 if scan.violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
