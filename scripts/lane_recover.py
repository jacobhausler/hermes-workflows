#!/usr/bin/env python3
"""Rebuild a dead lane's working tree from its journaled tool calls (#37).

A build lane that wipes its own uncommitted work (a base checkout over a dirty
tree for a RED run) or dies at the turn cap with an unbanked tree still leaves
one durable trace: every tool call it made is journaled in the profile's
`state.db` (sessions row keyed by the runner's session key, messages in order).
This replays the write_file / patch calls into a restore dir so the recovery is
one command instead of a hand replay. Stdlib only (sqlite3, argparse); the db
is opened READ-ONLY (`mode=ro`) and never mutated.

Usage:
  python3 scripts/lane_recover.py --profile <name> --skey <session-key> [--out <restore-dir>]
  python3 scripts/lane_recover.py --run <run-id> [--node <id>] [--index <i>] [--attempt <n>] [--out <restore-dir>]

The session key is what the runner writes into the spawn record / node record
(`nodes/<node>[.<i>].json` -> `skey`): `wf:<run>:<node>[:<i>]:<efp8>.<nonce>`;
the child's sessions row carries `<skey>#a<attempt>` as its title. `--skey`
accepts either form (a bare key resolves to its latest attempt unless
`--attempt` is given). `--run` reads the key from the run dir instead (the run
dir resolves the way the read model does: `WF_RUNS_ROOT`, else
`$HERMES_HOME/workflows`; the db home is the node's own child home for
profile-routed nodes, else the launcher's).

Default mode (no --out): the triage view — the ordered call list
(index, tool, target path; `[REFUSED]` when the live tool answered with an
error). With --out: emit `<out>/<relpath>` for each touched file (write_file
replays the content; patch applies old_string -> new_string to the
accumulated text — exact first, then whitespace-flexible) and write
`<out>/lane_recover_report.json`: `written`, `applied`, `unmatched` (anchor not
found / no path / arguments not JSON), `skipped` (the joined role='tool' result
carried an error — a refused write is not a write — or the anchor is ambiguous
without replace_all, the same refusal core `patch` makes), `unconfirmed` (no
result row at all: replayed, flagged).

Exit codes: 0 recovered > 0 (or a non-empty triage list), 2 no session / no
db / db locked by a live writer, 3 no journaled write_file/patch calls.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

REPLAY_TOOLS = ("write_file", "patch")


class Bail(Exception):
    """A typed early exit: message + process exit code (2 = no session/run/db)."""
    def __init__(self, msg, code=2):
        super().__init__(msg)
        self.code = code
REPORT_NAME = "lane_recover_report.json"


# ---------- HOME -> state.db (the read model's mapping, reused not re-derived) ----------

def _wfcommon():
    """wfcommon when importable (plugin checkout beside this script), else None."""
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        import wfcommon  # noqa: E402
        return wfcommon
    except Exception:
        return None


def _hermes_home():
    wc = _wfcommon()
    if wc is not None:
        return Path(wc.hermes_home())
    return Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))


def profile_db(profile, home=None):
    """`<profiles_root>/<profile>/state.db` via wfcommon.profile_home (the door's own
    mapping: `<root>/profiles/<name>` where root = HERMES_HOME.parent.parent when
    HERMES_HOME is itself a named profile home). `--profile default` (or empty) is
    the launcher home itself."""
    home = Path(home) if home else _hermes_home()
    if not profile or profile == "default":
        return home / "state.db"
    wc = _wfcommon()
    if wc is not None:
        return Path(wc.profile_home(profile, home)) / "state.db"
    root = home.parent.parent if home.parent.name == "profiles" else home
    return root / "profiles" / str(profile) / "state.db"


# ---------- run-dir lookup (--run): the spawn record names the key ----------

def run_lookup(run_id, node, index=None, home=None):
    """(skey, db_path) from the run dir's node record. Raises SystemExit(2) with a
    message when the run/record/key is missing."""
    wc = _wfcommon()
    if wc is not None:
        r = Path(wc.find_run(run_id))
    else:
        root = os.environ.get("WF_RUNS_ROOT") or str(_hermes_home() / "workflows")
        r = Path(root) / run_id
    if not (r / "graph.json").exists():
        raise Bail(f"no run dir for {run_id!r} at {r}")
    if not node:
        raise Bail("--run needs --node <id> (the node whose child tree to rebuild)")
    name = str(node) + (f".{index}" if index is not None else "")
    rec_path = r / "nodes" / f"{name}.json"
    try:
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise Bail(f"no node record at {rec_path}")
    skey = rec.get("skey") if isinstance(rec, dict) else None
    if not isinstance(skey, str) or not skey:
        raise Bail(f"node record {rec_path} carries no skey")
    db_home = None
    if wc is not None:
        db_home = wc.node_child_home(r, node, index)
    elif isinstance(rec.get("profile_home"), str):
        db_home = Path(rec["profile_home"])
    db = (Path(db_home) if db_home else _hermes_home()) / "state.db"
    return skey, db


# ---------- the journal ----------

def open_ro(db):
    db = Path(db)
    if not db.exists():
        raise Bail(f"no state.db at {db}")
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=1.0)


def find_session(conn, skey, attempt=None):
    """The sessions row for a child key. `skey` may already carry `#a<n>`; a bare
    key picks `--attempt` when given, else the LATEST attempt (max started_at,
    rowid). Returns (id, title) or None."""
    if "#a" in skey:
        row = conn.execute("select id, title from sessions where title = ? "
                           "order by started_at desc, rowid desc limit 1", (skey,)).fetchone()
        return tuple(row) if row else None
    if attempt is not None:
        row = conn.execute("select id, title from sessions where title = ? "
                           "order by started_at desc, rowid desc limit 1",
                           (f"{skey}#a{attempt}",)).fetchone()
        return tuple(row) if row else None
    rows = conn.execute("select id, title from sessions where title = ? or title like ? "
                        "order by started_at desc, rowid desc",
                        (skey, skey + "#a%")).fetchall()
    return tuple(rows[0]) if rows else None


# Plain-text tool results (non-JSON) that core emits when it REFUSES a write. The
# JSON form (`{"error": ...}`, what tools/file_tools.py returns) is the primary
# signal; these phrases catch a result that was flattened to text.
_REFUSAL_TEXT = re.compile(r"^\s*error\b|\bFound \d+ (?:approximate )?matches\b|"
                           r"\bCould not find\b|\bold_string not found\b|\bpermission denied\b",
                           re.IGNORECASE)


def result_error(content):
    """The error text carried by a role='tool' result row, or None when the call
    succeeded. Core file tools answer with a JSON object whose `error` key is set
    on refusal (ambiguous anchor, anchor not found, denied path, stale write);
    a non-JSON body is checked against the known refusal phrases."""
    if content is None:
        return None
    if isinstance(content, (bytes, bytearray)):
        content = content.decode("utf-8", "replace")
    if not isinstance(content, str):
        return None
    s = content.strip()
    if not s:
        return None
    parsed = None
    if s[:1] in "{[":
        try:
            parsed = json.loads(s)
        except ValueError:
            parsed = None
    if isinstance(parsed, dict):
        err = parsed.get("error")
        return str(err) if err else None
    if parsed is not None:
        return None
    if _REFUSAL_TEXT.search(s):
        return s
    return None


def tool_results(conn, session_id):
    """{tool_call_id: content} for every role='tool' row of the session — the
    result side of the journal, joined to the assistant side by tool_call_id.
    The FIRST result per id wins (a duplicated id keeps its original answer)."""
    res = {}
    rows = conn.execute("select id, tool_call_id, content from messages where session_id = ? "
                        "and role = 'tool' and tool_call_id is not null order by id",
                        (session_id,)).fetchall()
    for _mid, cid, content in rows:
        if cid and cid not in res:
            res[cid] = content
    return res


def journaled_calls(conn, session_id):
    """Ordered [{index, tool, args, call_id, msg_id, error}] of write_file/patch
    calls. The assistant row's `tool_calls` column is a JSON list of
    {id, type:'function', function:{name, arguments:<JSON string>}}; the tool
    result row (role='tool') that follows carries `tool_call_id` + `tool_name`
    and the tool's answer. We read the assistant side (it holds the arguments)
    and JOIN the result row by tool_call_id: a call whose result carries an
    error is kept in the list (the triage view still shows it) but flagged with
    `error` so replay SKIPS it — a refused write is not a write. A call with no
    result row at all (the lane died mid-call) is replayed but `confirmed`
    is False and the report lists it under `unconfirmed`."""
    out = []
    results = tool_results(conn, session_id)
    rows = conn.execute("select id, role, tool_calls from messages where session_id = ? "
                        "and tool_calls is not null order by id", (session_id,)).fetchall()
    for mid, role, tc in rows:
        try:
            calls = json.loads(tc) if isinstance(tc, str) else tc
        except ValueError:
            continue
        if not isinstance(calls, list):
            continue
        for c in calls:
            fn = (c or {}).get("function") if isinstance(c, dict) else None
            if not isinstance(fn, dict):
                continue
            name = fn.get("name")
            if name not in REPLAY_TOOLS:
                continue
            args = fn.get("arguments")
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = {"_unparsed": args}
            if not isinstance(args, dict):
                args = {}
            cid = c.get("id") or c.get("call_id")
            confirmed = cid in results
            error = result_error(results[cid]) if confirmed else None
            out.append({"index": len(out), "tool": name, "args": args,
                        "call_id": cid, "msg_id": mid, "error": error, "confirmed": confirmed})
    return out


def target_path(call):
    return str(call["args"].get("path") or call["args"].get("file_path") or "")


# ---------- replay ----------

def _ws_flex(s):
    """Whitespace-flexible regex for a patch anchor: every INNER run of whitespace
    matches any run of whitespace (indent / trailing-space drift), literal
    otherwise; a leading indent matches any indent and a trailing newline still
    consumes through the end of that line, so the replacement keeps line shape."""
    parts = [re.escape(p) for p in re.split(r"\s+", s.strip()) if p]
    if not parts:
        return None
    head = r"[ \t]*" if s[:1] in (" ", "\t") else ""
    tail = r"[ \t]*\n" if s.endswith("\n") else (r"[ \t]*" if s[-1:] in (" ", "\t") else "")
    return re.compile(head + r"\s+".join(parts) + tail)


def apply_patch(text, old, new, replace_all=False):
    """(new_text, how) — how in {'exact', 'fuzzy', 'ambiguous:<n>', None}. Exact
    substring first; then whitespace-flexible; None leaves the text untouched.
    An anchor with more than one hit and no replace_all is REFUSED (text
    untouched, how = 'ambiguous:<n>') — the same rule core `patch` applies
    (fuzzy_match.py: "Found N matches … use replace_all=True"); never the first."""
    if old is None:
        return text, None
    if old == "":
        return text + new, "exact"           # empty anchor: append (an insert)
    n = text.count(old)
    if n:
        if replace_all:
            return text.replace(old, new), "exact"
        if n > 1:
            return text, f"ambiguous:{n}"
        return text.replace(old, new, 1), "exact"
    rx = _ws_flex(old)
    if rx is not None:
        hits = list(rx.finditer(text))
        if hits:
            if replace_all:
                return rx.sub(lambda _m: new, text), "fuzzy"
            if len(hits) > 1:
                return text, f"ambiguous:{len(hits)}"
            m = hits[0]
            return text[:m.start()] + new + text[m.end():], "fuzzy"
    return text, None


def _rel(p):
    """A safe restore-relative path: absolute paths lose their root, `..` is dropped."""
    parts = [x for x in Path(p).parts if x not in ("/", "..", "")]
    if parts and re.match(r"^[A-Za-z]:\\?$", parts[0]):
        parts = parts[1:]
    return Path(*parts) if parts else Path("_unnamed")


def replay(calls, out_dir, seed_root=None):
    """Replay into out_dir. Files are accumulated in memory per target path
    (write_file sets, patch edits) then flushed. A patch whose file has no prior
    write in the journal seeds from `seed_root/<rel>` when that exists (the lane's
    committed base), else from the target path itself if readable, else ''."""
    out_dir = Path(out_dir)
    files, seeded_from = {}, {}
    report = {"unmatched": [], "applied": [], "written": [], "skipped": [], "unconfirmed": []}
    for c in calls:
        p = target_path(c)
        if "_unparsed" in c["args"]:
            # corrupt payload: nothing to replay, distinct from a well-formed pathless call
            report["unmatched"].append({"index": c["index"], "tool": c["tool"], "path": "",
                                        "reason": "arguments not JSON",
                                        "arguments_head": str(c["args"]["_unparsed"])[:200]})
            continue
        if c.get("error"):
            # the live tool REFUSED this call (joined role='tool' row carries the error):
            # a refused write is not a write — never replay it.
            report["skipped"].append({"index": c["index"], "tool": c["tool"], "path": p,
                                      "reason": "tool result carries an error: " + str(c["error"])[:300]})
            continue
        if not p:
            report["unmatched"].append({"index": c["index"], "tool": c["tool"], "path": "",
                                        "reason": "no path argument"})
            continue
        if not c.get("confirmed", True):
            report["unconfirmed"].append({"index": c["index"], "tool": c["tool"], "path": p,
                                          "reason": "no tool result journaled (lane died mid-call?)"})
        rel = _rel(p)
        if c["tool"] == "write_file":
            files[rel] = str(c["args"].get("content", ""))
            report["written"].append({"index": c["index"], "path": p})
            continue
        if rel not in files:
            seed = None
            for cand in ((Path(seed_root) / rel) if seed_root else None, Path(p)):
                if cand is not None and cand.is_file():
                    try:
                        seed = cand.read_text(encoding="utf-8")
                        seeded_from[rel] = str(cand)
                        break
                    except OSError:
                        pass
            files[rel] = seed if seed is not None else ""
        a = c["args"]
        new_text, how = apply_patch(files[rel], a.get("old_string"), str(a.get("new_string", "")),
                                    bool(a.get("replace_all")))
        if how is None:
            report["unmatched"].append({"index": c["index"], "tool": "patch", "path": p,
                                        "reason": "old_string not found (exact or whitespace-flexible)",
                                        "old_string_head": str(a.get("old_string", ""))[:200]})
        elif how.startswith("ambiguous:"):
            n_hits = how.split(":", 1)[1]
            report["skipped"].append({"index": c["index"], "tool": "patch", "path": p,
                                      "reason": f"ambiguous ({n_hits} matches)",
                                      "old_string_head": str(a.get("old_string", ""))[:200]})
        else:
            files[rel] = new_text
            report["applied"].append({"index": c["index"], "path": p, "match": how})
    out_dir.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
    report["files"] = sorted(str(k) for k in files)
    report["seeded_from"] = {str(k): v for k, v in seeded_from.items()}
    (out_dir / REPORT_NAME).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    return report


# ---------- cli ----------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_argument_group("journal source")
    src.add_argument("--profile", help="profile whose state.db holds the child session "
                                       "('default' = the launcher home)")
    src.add_argument("--skey", help="child session key (with or without #a<n>)")
    src.add_argument("--run", help="run id; the key is read from nodes/<node>[.<i>].json")
    src.add_argument("--node", help="node id (with --run)")
    src.add_argument("--index", type=int, help="fan-out item index (with --run)")
    src.add_argument("--attempt", type=int, help="attempt number (#a<n>); default: latest")
    ap.add_argument("--db", help="explicit state.db path (overrides --profile / --run mapping)")
    ap.add_argument("--home", help="HERMES_HOME to resolve profiles/runs from (default: env)")
    ap.add_argument("--out", help="restore dir; omit for the triage view")
    ap.add_argument("--seed", help="tree to seed patched-but-never-written files from "
                                   "(e.g. the lane's committed base checkout)")
    args = ap.parse_args(argv)
    if args.home:   # the read model resolves runs/profiles from HERMES_HOME; honor the flag
        os.environ["HERMES_HOME"] = str(Path(args.home).expanduser())

    if args.run:
        skey, db = run_lookup(args.run, args.node, args.index, args.home)
    elif args.skey:
        skey, db = args.skey, profile_db(args.profile, args.home)
    else:
        ap.error("need --skey (with --profile) or --run --node")
    if args.db:
        db = Path(args.db)

    try:
        conn = open_ro(db)
    except sqlite3.OperationalError as e:
        raise Bail(f"state.db not readable right now ({e}) at {db}")
    try:
        sess = find_session(conn, skey, args.attempt)
        if sess is None:
            print(f"no session for {skey!r} in {db}", file=sys.stderr)
            return 2
        sid, title = sess
        calls = journaled_calls(conn, sid)
    except sqlite3.OperationalError as e:
        # a live writer holding EXCLUSIVE (or a corrupt/odd file): a clean bail, no traceback
        raise Bail(f"state.db not readable right now ({e}) at {db} — retry when the lane's "
                   f"writer releases it")
    finally:
        conn.close()
    if not calls:
        print(f"session {title!r} ({sid}) journaled no write_file/patch calls", file=sys.stderr)
        return 3

    if not args.out:
        print(f"session {title} ({sid}) — {len(calls)} journaled write_file/patch call(s):")
        for c in calls:
            flag = "  [REFUSED]" if c.get("error") else ("  [no result]" if not c.get("confirmed", True) else "")
            print(f"{c['index']:4d}  {c['tool']:<10}  {target_path(c)}{flag}")
        return 0

    rep = replay(calls, args.out, args.seed)
    n_files = len(rep["files"])
    print(f"session {title} ({sid}): {len(rep['written'])} write_file, "
          f"{len(rep['applied'])} patch applied, {len(rep['unmatched'])} unmatched, "
          f"{len(rep['skipped'])} skipped "
          f"-> {n_files} file(s) under {args.out} (report: {Path(args.out) / REPORT_NAME})")
    for u in rep["unmatched"]:
        print(f"  UNMATCHED #{u['index']} {u['tool']} {u['path']}: {u['reason']}")
    for u in rep["skipped"]:
        print(f"  SKIPPED #{u['index']} {u['tool']} {u['path']}: {u['reason']}")
    for u in rep["unconfirmed"]:
        print(f"  UNCONFIRMED #{u['index']} {u['tool']} {u['path']}: {u['reason']}")
    return 0 if n_files > 0 else 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Bail as e:
        print(str(e), file=sys.stderr)
        sys.exit(e.code)
