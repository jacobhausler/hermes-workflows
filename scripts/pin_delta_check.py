#!/usr/bin/env python3
"""pin_delta_check.py — the vendor/catalog re-pin gate: scan the CODE DELTA between
the old pin and the new pin for NEW host effects, fail closed, abort unless an
explicit allowlist evidence file names every finding.

Context (revalidation dossier 133387 rv3): the catalog entry pins a commit SHA; a
re-pin moves it old->new via a PR, and today nothing reads the code the new pin
installs — the diff between the two pins is never scanned. A post-exit hook that
handes a node-registered shell script to launchd (launchctl submit / bootstrap /
load -w, RunAtLoad plist, no teardown leg) rode into the pinned tree through our
own re-pin and was waved through, costing a full maintainer round. The re-pin lane
must answer one question mechanically: what does the NEW pin ship to the host that
the OLD pin did not?

The scan: `git diff -z --name-status old..new` parsed with the est-gbim walker
(R/C records take BOTH endpoints; -z output is raw bytes, never quoted), code-
suffixed files only (.py/.pyi/.sh/.bash/.zsh/.js/.mjs/.cjs — docs prose is not
scanned). For every changed path both endpoints resolve to, the added lines are
computed from the real diff (never raw file text, so unchanged bytes of a touched
file raise nothing); a pure rename yields zero added lines — moving a file is not
a new effect, content that survived byte-identically is not NEW. Detectors:

  launchctl_submit            launchctl submit|bootstrap|load( -w)|kickstart
  launchd_plist_persistence   RunAtLoad / KeepAlive plist keys
  systemd_unit                systemctl enable|start|unmask / unit-file install
  cron_install                crontab piping, cron.{d,daily,hourly,daily}, /etc/cron
  detach_or_daemonize         setsid / double-fork / nohup / start_new_session —
                              detached spawns have no teardown leg; the finding
                              row says so (the hook that shipped had none either)
  out_of_band_write           fixed paths outside the run dir or HERMES_HOME:
                              /tmp/<x> literals, ~/Library/LaunchAgents,
                              .config/autostart, /etc/<x>, shell rc files
  syspath_import_time         AST-proven module-level (import-time) sys.path /
                              sys.meta_path mutation — insert/append/extend/
                              remove/pop/clear or reassignment OUTSIDE a
                              `if __name__ == "__main__"` body (function and
                              class bodies never count; the else-branch of the
                              main-guard is import-time code)

Allowlist: findings ABORT (exit 1) unless an evidence file (--allowlist <path>)
names every finding id "<path>:<rule>" verbatim on its own line (blank lines and
# comments ignored). The allowlist only excuses; it can never green a scan that
could not run — an unreadable file, or an entry that names an id the delta no
longer contains (stale evidence = evidence drift), fails closed. A binary payload
in a scanned suffix cannot be grepped at all: it BLOCKS as a
"<path>:binary_unscanned" finding and must be allowlisted with named evidence
(a byte-identical relocation is not new payload and is not blocked).

Fail-closed law (mirrors scripts/graph_path_ban.py): git failure, an
unresolvable sha, unparsable status output, truncated rename records, a changed
.py whose new content no longer parses, or any allowlist inconsistency =>
exit 2 with a loud FAIL-CLOSED row, never green.

  exit 0  no new host effects in the delta (or every finding allowlisted)
  exit 1  findings not covered by the allowlist evidence — the bump aborts
  exit 2  the scan itself could not be trusted — fail closed

The core is split from argv (build_parser / _git / _git_bytes / changed_files /
line_findings / import_time_syspath_mutations / scan / main) so
tests/test_pin_delta_check_133387.py can unit-test the semantics directly and
drive the CLI against synthetic before/after trees. Stdlib only. CI wiring is
deliberately not part of this change — the caller (the re-pin lane) invokes:

  python3 scripts/pin_delta_check.py <old-sha> <new-sha> <repo-dir> \
      [--allowlist <evidence-file>]
"""
import argparse
import ast
import re
import subprocess
import sys

# Only code can install a host effect; markdown/docs prose is not scanned (it is
# scrubbed and reviewed elsewhere). Suffix set is deliberately small and loud.
SCANNED_SUFFIXES = (".py", ".pyi", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs")

_STATUS_RE = re.compile(r"^[A-Z]{1,2}[0-9]{0,3}!?$")  # git name-status: A M D T U X B, R100/C75, optional ! (unmerged)
_HEX_RE = re.compile(r"^[0-9a-fA-F]{4,64}$")

# Line-level detectors: (rule id, regex, why it matters). Comment lines (the
# first non-space character is #) do not fire — prose in a code file is not an
# effect; the import-time AST probe below has no such exemption.
LINE_RULES = (
    ("launchctl_submit",
     re.compile(r"\blaunchctl\b[^\n]*"
                r"(?:\b(?:submit|bootstrap|kickstart)\b|\bload\b[^\n]*-w)"),
     "hands a script to launchd (persistence across logout; `load -w` writes the "
     "persistent overrides database)"),
    ("launchd_plist_persistence",
     re.compile(r"\bRunAtLoad\b|\bKeepAlive\b", re.I),
     "launchd plist persistence keys (start at load / relaunch on death)"),
    ("systemd_unit",
     re.compile(r"\bsystemctl\b[^\n]*(enable|start|unmask)|/etc/systemd/system/"),
     "installs or enables a systemd unit"),
    ("cron_install",
     re.compile(r"\bcrontab\b|/etc/cron\.(d|daily|hourly)|/etc/cron\.(weekly|monthly)"),
     "installs scheduled execution"),
    ("detach_or_daemonize",
     re.compile(r"\bos\.setsid\b|\bsetsid\b|\bos\.fork\b|\bos\.execv\w*\b"
                r"|\bnohup\b|start_new_session\s*=\s*True"),
     "detached/daemonized spawn — no teardown leg seen in the delta"),
    ("out_of_band_write",
     re.compile(r"/tmp/|/etc/\S|Library/LaunchAgents|\.config/autostart"
                r"|\.(bashrc|bash_profile|zshrc|profile|zprofile)\b"),
     "writes to a fixed path outside the run dir or HERMES_HOME"),
)

_SYSPATH_MUTATORS = {"insert", "append", "extend", "remove", "pop", "clear"}


def _git(repo_dir, *args):
    return subprocess.run(["git", "-C", str(repo_dir), *args],
                          capture_output=True, text=True)


def _git_bytes(repo_dir, *args):
    return subprocess.run(["git", "-C", str(repo_dir), *args],
                          capture_output=True)


def resolve_sha(repo_dir, sha):
    """Resolve a revision to a full sha (None if git cannot — bad repo, bad rev)."""
    if not _HEX_RE.match(sha or ""):
        return None
    r = _git(repo_dir, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}")
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    return out if _HEX_RE.match(out) else None


def changed_files(repo_dir, old_sha, new_sha):
    """Records of `git diff -z --name-status old..new` as (status, path,
    new_path|None).

    est-gbim (shared law with scripts/graph_path_ban.py): rename/copy records
    carry TWO paths and BOTH endpoints are part of the change — parsing only the
    post image lets a rename smuggle effects in or out of a path the scanner
    would otherwise read. -z mode is raw bytes: never octal-quoted, and fields
    split on NUL so an embedded newline cannot forge an entry.

    Fail-closed: git failure, a status token we cannot recognise, or a rename
    record truncated to one path => None; main() must exit 2, never green."""
    r = _git_bytes(repo_dir, "diff", "-z", "--name-status",
                   f"{old_sha}..{new_sha}")
    if r.returncode != 0:
        return None
    if (getattr(r, "stderr", None) or b"").strip():
        return None  # git warned (broken refs in the range, damaged objects) — untrusted
    fields = r.stdout.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()  # trailing NUL terminator
    records = []
    i = 0
    while i < len(fields):
        status = fields[i].decode("utf-8", "surrogateescape")
        if not _STATUS_RE.match(status):
            return None  # output shape we cannot trust → fail closed
        i += 1
        if status[0] in "RC":
            if i + 1 >= len(fields):
                return None  # truncated rename record → fail closed
            records.append((status,
                            fields[i].decode("utf-8", "surrogateescape"),
                            fields[i + 1].decode("utf-8", "surrogateescape")))
            i += 2
        else:
            if i >= len(fields):
                return None
            records.append((status,
                            fields[i].decode("utf-8", "surrogateescape"), None))
            i += 1
    return records


def _added_lines(repo_dir, before_rev, after_rev, path):
    """True added lines (line_no, text) of `path` between two revisions — from
    git's own diff, not raw text. None on any git failure or unparsable hunk
    header (fail closed upstream)."""
    r = _git_bytes(repo_dir, "diff", "--unified=0", "--no-color", "--no-ext-diff",
                   "--no-renames",
                   f"{before_rev}..{after_rev}", "--", path)
    if r.returncode != 0:
        return None
    added = []
    in_hunk = False
    new_ln = 0
    for raw in r.stdout.split(b"\n"):
        line = raw.decode("utf-8", "surrogateescape")
        if line.startswith("@@"):
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if not m:
                return None  # hunk header we cannot read → fail closed
            in_hunk = True
            new_ln = int(m.group(1))
            continue
        if not in_hunk or line.startswith(("++", "--")):
            continue
        if line.startswith("-"):
            continue
        if line.startswith("\\"):  # "\ No newline at end of file"
            continue
        if line.startswith("+"):
            added.append((new_ln, line[1:]))
            new_ln += 1
    return added


def _show_blob(repo_dir, rev, path):
    """Raw bytes of `path` at `rev` (None if git cannot produce it)."""
    r = _git_bytes(repo_dir, "show", f"{rev}:{path}")
    return r.stdout if r.returncode == 0 else None


def _is_main_guard(node_test):
    """True when a comparison is the `__name__ == "__main__"` idiom (either
    order, == or !=). Returns (is_main_idiom, is_equality)."""
    if not isinstance(node_test, ast.Compare) or len(node_test.ops) != 1:
        return False, False
    left, right = node_test.left, node_test.comparators[0]
    names = set()
    vals = set()
    for side in (left, right):
        if isinstance(side, ast.Name):
            names.add(side.id)
        elif isinstance(side, ast.Constant) and isinstance(side.value, str):
            vals.add(side.value)
    is_main = "__name__" in names and vals == {"__main__"}
    return is_main, isinstance(node_test.ops[0], ast.Eq)


def _dotted(node):
    """Full dotted name of an attribute chain rooted at a plain Name, else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def import_time_syspath_mutations(src):
    """Line numbers of module-level (import-time) sys.path / sys.meta_path
    mutation in the given python source. None if the source does not parse —
    the caller must fail closed, never treat unparseable as clean.

    Import-time means: executed by the bare act of importing the module.
    Function and class bodies never count; neither does the body of a
    `if __name__ == "__main__":` guard — but its else-branch and the body of an
    inverted `if __name__ != "__main__":` guard DO (they run on import);
    top-level try/with/for/while/if wrappers all count."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    hits = []

    def check_stmt(stmt):
        d = None
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            fn = stmt.value.func
            if isinstance(fn, ast.Attribute) and fn.attr in _SYSPATH_MUTATORS:
                d = _dotted(fn.value)
        elif isinstance(stmt, ast.Assign):
            d = _dotted(stmt.targets[0]) if len(stmt.targets) == 1 else None
        elif isinstance(stmt, ast.AugAssign):
            d = _dotted(stmt.target)
        if d in ("sys.path", "sys.meta_path"):
            hits.append(getattr(stmt, "lineno", 0))

    def walk_body(body):
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue  # definitions do not execute their body at import
            if isinstance(stmt, ast.If):
                is_main, is_eq = _is_main_guard(stmt.test)
                if is_main:
                    if is_eq:            # `if __name__ == "__main__":` — guarded
                        if stmt.orelse:
                            walk_body(stmt.orelse)   # the else runs on import
                    else:                # `if __name__ != "__main__":` — import-time code
                        walk_body(stmt.body)
                        if stmt.orelse:
                            walk_body(stmt.orelse)
                else:
                    walk_body(stmt.body)
                    if stmt.orelse:
                        walk_body(stmt.orelse)
            elif isinstance(stmt, ast.Try):
                walk_body(stmt.body)
                for h in stmt.handlers:
                    walk_body(h.body)
                walk_body(stmt.orelse)
                walk_body(stmt.finalbody)
            elif isinstance(stmt, (ast.With, ast.AsyncWith)):
                walk_body(stmt.body)
            elif isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
                walk_body(stmt.body)
                if stmt.orelse:
                    walk_body(stmt.orelse)
            else:
                check_stmt(stmt)

    walk_body(tree.body)
    return sorted(set(hits))


def line_findings(added):
    """Pure detectors over added lines [(line_no, text)] → [(rule, line_no,
    text)]. Comment lines (leading #) do not fire — prose in a code file is not
    an effect."""
    out = []
    for ln, text in added:
        if text.lstrip().startswith("#"):
            continue
        for rule, rx, _why in LINE_RULES:
            if rx.search(text):
                out.append((rule, ln, text))
    return out


def _load_allowlist(path):
    """(ids, error): a set of finding ids, or a fail-closed reason."""
    try:
        raw = open(str(path), "r", encoding="utf-8").read()
    except OSError as exc:
        return None, f"allowlist evidence file unreadable: {path} ({exc})"
    ids = set()
    for line in raw.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            ids.add(s)
    return ids, None


def _scan_side(repo_dir, before_rev, after_rev, before_path, after_path, state):
    """Scan one endpoint of a diff record. state collects findings/blocked/
    errors. Returns None on success, or a fail-closed error string."""
    if not after_path.endswith(SCANNED_SUFFIXES):
        return None
    after = _show_blob(repo_dir, after_rev, after_path)
    if after is None:
        # The diff NAMES this path as living at the new pin; if git cannot show
        # it the tree/refpair is damaged beyond trust — fail closed.
        return (f"cannot read {after_path} at {after_rev[:12]} — the diff names "
                f"a path git cannot show; the scan cannot be trusted")
    # A missing pre-image is a NEW file (status A / rename post image of a
    # smuggle): empty before is honest. If the repo were damaged, changed_files
    # would already have failed — erring to empty over-reports (safe side).
    before = _show_blob(repo_dir, before_rev, before_path) or b""
    if before == after:
        return None  # byte-identical relocation (pure rename) — nothing new ships
    if b"\0" in after:
        _add_finding(state, f"{after_path}:binary_unscanned", after_path, 0,
                     "binary_unscanned", "<binary payload — cannot be scanned>")
        return None
    added = _added_lines(repo_dir, before_rev, after_rev, after_path)
    if added is None:
        return f"git diff for {after_path} failed — the scan cannot be trusted"
    for rule, ln, text in line_findings(added):
        _add_finding(state, f"{after_path}:{rule}", after_path, ln, rule, text)
    if after_path.endswith(".py"):
        src_text = after.decode("utf-8", "replace")
        src_lines = src_text.splitlines()
        muts = import_time_syspath_mutations(src_text)
        if muts is None:
            return (f"changed .py does not parse at the new pin: {after_path} — "
                    f"a shipped module that cannot even be parsed cannot be "
                    f"trusted to be inert; failing closed")
        for ln in muts:
            _add_finding(state, f"{after_path}:syspath_import_time", after_path,
                         ln, "syspath_import_time",
                         (src_lines[ln - 1].strip()
                          if 0 < ln <= len(src_lines) else "sys.path mutation"))
    return None


def _add_finding(state, fid, path, line, rule, text):
    """Findings are grouped per id: one allowlist id, one printed row, every
    firing line kept as evidence under it. Same (line, text) twice is one hit."""
    entry = state["by_id"].get(fid)
    if entry is None:
        entry = state["by_id"][fid] = {"id": fid, "path": path, "line": line,
                                       "rule": rule, "text": text,
                                       "hits": [(line, text)]}
    elif (line, text) not in entry["hits"]:
        entry["hits"].append((line, text))


def scan(old_sha, new_sha, repo_dir, allowlist=None):
    """The plain callable the re-pin lane imports. Returns
    {"error": str|None, "findings": [ {id,path,line,rule,text} ],
     "blocked": set(ids unallowlisted findings incl. binary blocks),
     "allowlist": {"path","count"}|None}.

    error set  => exit 2 (fail closed). blocked non-empty => exit 1 (abort).
    Nothing left => exit 0. The allowlist only excuses findings; it can never
    green a scan that could not run."""
    state = {"by_id": {}, "errors": []}
    old = resolve_sha(repo_dir, old_sha)
    if old is None:
        return {"error": f"old pin sha does not resolve: {old_sha!r}",
                "findings": [], "blocked": set(), "allowlist": None}
    new = resolve_sha(repo_dir, new_sha)
    if new is None:
        return {"error": f"new pin sha does not resolve: {new_sha!r}",
                "findings": [], "blocked": set(), "allowlist": None}
    records = changed_files(repo_dir, old, new)
    if records is None:
        return {"error": "git diff -z --name-status failed or its output could "
                        "not be parsed into well-formed records — failing closed",
                "findings": [], "blocked": set(), "allowlist": None}

    allow_meta = None
    for status, path, new_path in records:
        if status[0] == "D":
            continue  # deletions remove effects, they do not introduce them
        first = status[0]
        endpoints = [(path, new_path)] if first in "RC" else [(path, path)]
        for before_path, after_path in endpoints:
            err = _scan_side(repo_dir, old, new, before_path, after_path, state)
            if err:
                return {"error": err, "findings": list(state["by_id"].values()),
                        "blocked": set(state["by_id"]), "allowlist": None}

    # one finding entry per id (insertion order); `hits` carries every firing
    # line so the printed row shows full evidence under a single id.
    findings = list(state["by_id"].values())
    ids = set(findings and [f["id"] for f in findings])

    blocked = set(ids)
    if allowlist is not None:
        allow_ids, allow_err = _load_allowlist(allowlist)
        if allow_err:
            return {"error": allow_err, "findings": findings, "blocked": blocked,
                    "allowlist": None}
        allow_ids = allow_ids if allow_ids is not None else set()
        allow_meta = {"path": str(allowlist), "count": len(allow_ids)}
        stale = sorted(allow_ids - ids)
        if stale:
            return {"error": f"allowlist evidence drift — {len(stale)} entr"
                            f"{'y' if len(stale) == 1 else 'ies'} name finding"
                            f"{'s' if len(stale) > 1 else ''} the delta no longer "
                            f"contains ({', '.join(stale[:5])}): the evidence file "
                            f"was not written for THIS delta; failing closed",
                    "findings": findings, "blocked": blocked,
                    "allowlist": allow_meta}
        blocked = ids - allow_ids
    return {"error": None, "findings": findings, "blocked": blocked,
            "allowlist": allow_meta}


WHY_HINT = {rule: why for rule, _rx, why in LINE_RULES}
WHY_HINT["syspath_import_time"] = ("pollutes the host interpreter's module "
                                   "search path at import time")
WHY_HINT["binary_unscanned"] = ("binary payload in a scanned suffix — the gate "
                                "cannot read it; name it in the allowlist "
                                "evidence with a reason")


def build_parser():
    ap = argparse.ArgumentParser(
        description="vendor/catalog re-pin gate: scan old-pin..new-pin for NEW "
                    "host effects; fail closed; abort unless an allowlist "
                    "evidence file names every finding")
    ap.add_argument("old_sha", help="the sha currently pinned by the catalog entry")
    ap.add_argument("new_sha", help="the sha the re-pin would install")
    ap.add_argument("repo_dir", nargs="?", default=".",
                    help="repository holding both commits (default: cwd)")
    ap.add_argument("--allowlist", default=None,
                    help="evidence file naming each finding id '<path>:<rule>' "
                         "verbatim (one per line; blank/# ignored). Findings "
                         "abort without it.")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    result = scan(args.old_sha, args.new_sha, args.repo_dir,
                  allowlist=args.allowlist)
    for f in result["findings"]:
        why = WHY_HINT.get(f["rule"], "")
        print(f"pin_delta_check: {f['id']} — {why}")
        for ln, text in f.get("hits") or [(f["line"], f["text"])]:
            print(f"    line {ln}: {text[:110]}")
        if f["rule"] == "detach_or_daemonize":
            print("    the detached spawn has no teardown leg in the delta: a "
                  "persistence mechanism without a bootout/unload/uninstall path "
                  "is exactly what burned revalidation-133387")
    if result["allowlist"]:
        print(f"pin_delta_check: allowlist evidence {result['allowlist']['path']} "
              f"({result['allowlist']['count']} ids)")
    if result["error"]:
        print(f"pin_delta_check: FAIL-CLOSED — {result['error']} — the re-pin "
              f"bump does NOT proceed; a scan that cannot be trusted is never "
              f"green")
        return 2
    blocked = result["blocked"]
    if blocked:
        print(f"pin_delta_check: ABORT — {len(blocked)} finding(s) not covered "
              f"by allowlist evidence (ids printed above)")
        print("the re-pin bump is blocked. Resolve each finding (strip, "
              "document with teardown, or relocate under the run dir / "
              "HERMES_HOME), or name every id verbatim in an allowlist "
              "evidence file and pass --allowlist <path>.")
        return 1
    print(f"pin_delta_check: OK — {len(result['findings'])} finding(s) in the "
          f"pin delta, none unresolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
