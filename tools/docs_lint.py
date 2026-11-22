#!/usr/bin/env python3
"""tools/docs_lint.py — dead-reference CI lint for docs/runtime (bd_2026-11-13-7m0).

DATA SHAPES (named before the logic; every structure this file reads or emits):

  Claim = {"file": str, "line": int, "kind": str, "ref": str, "ctx": dict}
    extracted from markdown backtick spans and fenced blocks of
    docs/runtime/**/*.md.  kinds:
      cmd     shell command mentioning `wf.py <verb> ...` (inline span or a
              fenced sh/bash block line) — verb liveness; executed against the
              fixture when the args are substitutable.
      action  door action reference: `action:"x"` / `action: "x"` — resolved
              against the door's ACTUAL dispatch keys (imported, not regexed).
      env     `$?WF_* / HERMES_* / WORKFLOW_*` env-var reference — resolved as
              a literal in shipped sources.
      path    run-dir / runs-root / seats-root relative path, placeholders
              allowed (`<id>`, `[.<i>]`, `<n>`) — resolved against the fixture
              tree (exercised), else the shipped-source literal pool.
      field   JSON field claim: a brace key-list (inline or fenced). Bound to
              an artifact by anchor (event name, parent field, fence variable)
              or by distinctive-key match against the fixture artifact registry;
              unbound lists fall back to per-key literal checks.
      cite    dotted module reference (`wfcommon.run_state`) anywhere, plus any
              bare identifier span inside a **Citations** bullet — resolved as a
              literal in the file(s) the bullet names, else the whole pool.
      word    a bare identifier span outside Citations — weak literal check
              (a claim gone entirely unrecognizable in code is a dead reference).

  Violation = {"file", "line", "kind", "ref", "why"}
    why ∈ {dead-verb, dead-command, dead-action, dead-env, dead-path,
           dead-field, drifted-field, dead-symbol, repo-path-missing,
           cmd-exec-fail, fixture-error}
    `drifted-field`: the bound artifact/container EXISTS, the claimed key is
    absent from it, and the key lives only in some OTHER artifact's shape
    (the field moved); `dead-field`: the key is nowhere in the pool.

  Fixture = one live door+runner run in a temp state dir under
    tests/fake children + tests/wf_test_isolation resolver pin (the repo's own
    test idiom, cf. tests/test_amendment_evidence_e18.py). The scenario
    exercises the six runtime surfaces: run-dir layout (01), dispositions (02),
    a timeout death with wall_account + banked corpse (03), a door amend
    consumed at the wave boundary with its evidence pair (04), a steer line
    baked at the target node's spawn (05), and a live seats read (06).

Resolution law per claim: fixture-evidence first, shipped-source literal
second, violation third. `--no-fixture` keeps the static half (verb/action
tables, literals, repo paths, cites) so mutation self-tests stay fast.

Exit: 0 with no violations; 1 otherwise. Every violation line names
`docs/runtime/<file>:<line>: <why> <kind> '<ref>'`.
"""
import argparse
import copy
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parent

# ---------------------------------------------------------------- static pool

POOL_GLOBS = ["*.py", "dashboard/*.py", "dashboard/*.js", "scripts/*.py",
              "desktop/*.js", "plugin.yaml"]
# markdown/docs files are NOT pool: a doc may never satisfy its own claim.

def load_pool(repo: Path):
    texts = {}
    for g in POOL_GLOBS:
        for p in sorted(repo.glob(g)):
            try:
                texts[str(p.relative_to(repo))] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass
    return texts


class Pool:
    def __init__(self, texts: dict):
        self.texts = texts
        self.all = "\n".join(texts.values())

    def has(self, needle: str, files=None) -> bool:
        if not needle:
            return False
        if files:
            for f in files:
                t = self.texts.get(f)
                if t is not None and needle in t:
                    return True
            return False
        return needle in self.all


# ------------------------------------------------------- live dispatch tables

def door_actions(repo: Path):
    """Actual door dispatch keys — import the isolated door (test_docs_surface_drift
    law: execute, never regex-scan)."""
    spec = importlib.util.spec_from_file_location(
        "_hw_docs_lint_door", repo / "__init__.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, set(mod.ACTIONS)


def cli_verbs(pool: Pool):
    src = pool.texts.get("wf.py", "")
    return set(re.findall(r'sys\.argv\[1\]\s*==\s*"([a-z][a-z_-]*)"', src))


# ------------------------------------------------------------------ extractor

SPAN = re.compile(r"`([^`\n]+)`")
CMD = re.compile(r'\b(?:python3\s+)?wf\.py\s+([a-z][a-z_-]*)((?:\s+[^\s`|]+)*)')
ACTION_REF = re.compile(r'"?action"?\s*:\s*\\?"?([a-z_]+)\\?"?')
ENV_REF = re.compile(r'^\$?((?:WF|HERMES|WORKFLOW)_[A-Z][A-Z0-9_]+)$')
EXTS = (".json", ".jsonl", ".log", ".pid", ".request", ".txt", ".unconsumed",
        ".md", ".py", ".mjs", ".js", ".yaml")
IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_.]*$')
DOTTED = re.compile(r'^[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+$')
WORD = re.compile(r'^[a-z_][a-z0-9_]{1,}$')
FENCE_LANG = re.compile(r'^```([a-zA-Z]*)\s*$')

# gate-option answers, statuses and other pure-value words that are prose,
# not references (the docs use backticks as typographic quotes for these).
WORD_STOPLIST = {
    "done", "failed", "stopped", "partial", "running", "interrupted",
    "registered", "skipped", "cancelled", "unknown", "open", "merged",
    "ship", "hold", "go", "true", "false", "null", "ids", "s", "int",
}

REPO_ROOTS = ("docs/", "tests/", "references/", "scripts/", "examples/",
              "dashboard/", "desktop/", "changelog.d/")


def is_repo_path(span: str) -> bool:
    return span.startswith(REPO_ROOTS) or span in ("plugin.yaml", "wf.py", "wfcommon.py",
                                                  "__init__.py", "SKILL.md", "README.md",
                                                  "CHANGELOG.md", "AGENTS.md")


def pathlike(span: str) -> bool:
    if not span or " " in span or "=" in span:
        return False
    if span.startswith("$") or re.match(r'^[.\w<>\[\]-]+/$', span):
        return True
    return bool(re.match(r'^[.\w<>\[\]$()-]+$', span)) and (
        "/" in span.rstrip("/") or span.endswith(EXTS))


def brace_claims(text: str):
    """Yield (anchor, keys, optionals) for every brace key-list in text, where
    keys are the leading-run identifiers before the first non-ident token
    (prose values stop the run); an `event: "x"` segment sets the anchor."""
    out = []
    i = 0
    while i < len(text):
        if text[i] != "{":
            i += 1
            continue
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= len(text):
            i += 1
            continue
        body = text[i + 1:j]
        keys, anchor, stop = [], None, False
        for seg in re.split(r",(?![^<>]*>)", body):
            seg = seg.strip()
            m = re.match(r'^event\s*:\s*"([a-z_][a-z0-9_.]*)"', seg)
            if m:
                anchor = m.group(1)
                continue
            m = re.match(r'^([a-z_][a-z0-9_]*)(\?)?\s*:?(?=$|\s|"(?![^"]*$))', seg)
            if stop or not m:
                stop = True    # lenient: keep the run before the first prose token
                continue
            keys.append(m.group(1))
        # an anchor may also sit right before the brace in the source text
        pre = text[:i]
        if anchor is None:
            m = re.search(r'([a-z_][a-z0-9_.]*)\s*[:=]?\s*$', pre)
            if m:
                anchor = m.group(1)
        if keys:
            out.append((anchor, keys))
        i = j + 1
    return out


def extract(docs_dir: Path):
    claims = []
    for md in sorted(docs_dir.rglob("*.md")):
        try:
            rel = str(md.relative_to(docs_dir.parent.parent))
        except ValueError:
            rel = str(md.relative_to(docs_dir))
        lines = md.read_text(encoding="utf-8").splitlines()
        in_citations = False
        fence = None            # (lang, start_line, buf)
        for ln, line in enumerate(lines, 1):
            fm = FENCE_LANG.match(line.strip())
            if fm:
                if fence is None:
                    fence = [fm.group(1), ln, []]
                else:
                    _fence_claims(claims, rel, fence, in_citations)
                    fence = None
                continue
            if fence is not None:
                fence[2].append(line)
                # fenced lines also carry cmd/action references
                _line_claims(claims, rel, ln, line, in_citations, fenced=True)
                continue
            if re.match(r'^#+\s+Citations\s*$', line):
                in_citations = True
                continue
            if re.match(r'^#+\s+', line) and in_citations:
                in_citations = False
            _line_claims(claims, rel, ln, line, in_citations, fenced=False)
    return claims


def _fence_claims(claims, rel, fence, in_citations):
    lang, start, buf = fence
    if lang in ("sh", "bash"):
        for k, bl in enumerate(buf):
            cmd = bl.strip().lstrip("$").strip()
            if cmd:
                claims.append({"file": rel, "line": start + k + 1, "kind": "cmd",
                               "ref": cmd, "ctx": {"fence": True, "fence_lang": lang}})
        return
    text = "\n".join(buf)
    anchor = None
    first = next((b.strip() for b in buf if b.strip()), "")
    m = re.match(r'^([a-z_][a-z0-9_]*)\s*=\s*\{', first)
    if m:
        anchor = m.group(1)
    keys = re.findall(r'"([a-z_][a-z0-9_]*)"\s*:', text)
    klines = {}
    for k, bl in enumerate(buf):
        for km in re.finditer(r'"([a-z_][a-z0-9_]*)"\s*:', bl):
            klines.setdefault(km.group(1), start + k + 1)
    evm = re.search(r'"event"\s*:\s*"([a-z_][a-z0-9_.]*)"', text)
    if evm:
        anchor = evm.group(1)
    am = re.search(r'"?action"?\s*:\s*"([a-z_]+)"', text)
    if am:
        # a CALL block: its keys claim fields of that action's RESPONSE payload;
        # the call's own discriminators (action, graph...) are not response keys.
        anchor = "response:" + am.group(1)
        keys = [k for k in keys if k not in ("action", "graph")]
        keys = keys or ["__call__"]
    if keys:
        claims.append({"file": rel, "line": start + 1, "kind": "field",
                       "ref": ",".join(keys), "ctx": {"fence": True, "anchor": anchor,
                                                      "klines": klines,
                                                      "block": text[:160]}})


def _line_claims(claims, rel, ln, line, in_citations, fenced):
    cited_files = [s for s in SPAN.findall(line) if s.endswith((".py", ".md", ".js", ".mjs", ".json"))]
    cited_files += re.findall(r'[\w/.\-]+\.(?:py|md|js|mjs)', line)
    for m in CMD.finditer(line):
        claims.append({"file": rel, "line": ln, "kind": "cmd",
                       "ref": ("wf.py " + m.group(1) + m.group(2)).strip(),
                       "ctx": {"verb": m.group(1)}})
    for m in ACTION_REF.finditer(line):
        claims.append({"file": rel, "line": ln, "kind": "action", "ref": m.group(1), "ctx": {}})
    for span in SPAN.findall(line):
        span = span.strip()
        if ENV_REF.match(span):
            claims.append({"file": rel, "line": ln, "kind": "env", "ref": ENV_REF.match(span).group(1),
                           "ctx": {}})
            continue
        if is_repo_path(span):
            claims.append({"file": rel, "line": ln, "kind": "repo", "ref": span,
                           "ctx": {"dir": span.endswith("/")}})
            continue
        if pathlike(span):
            claims.append({"file": rel, "line": ln, "kind": "path", "ref": span, "ctx": {}})
            continue
        if DOTTED.match(span):
            claims.append({"file": rel, "line": ln, "kind": "cite", "ref": span,
                           "ctx": {"files": sorted(set(cited_files))}})
            continue
        for anchor, keys in brace_claims(span):
            claims.append({"file": rel, "line": ln, "kind": "field",
                           "ref": ",".join(keys), "ctx": {"anchor": anchor}})
        qv = re.match(r'^([a-z_][a-z0-9_]*)\s*[:=]\s*("[^"]*"|[a-z_]+)$', span)
        if qv:
            claims.append({"file": rel, "line": ln, "kind": "word", "ref": qv.group(1), "ctx": {}})
            continue
        if IDENT.match(span) and not span.endswith(EXTS):
            if in_citations:
                claims.append({"file": rel, "line": ln, "kind": "cite", "ref": span,
                               "ctx": {"files": sorted(set(cited_files))}})
            elif WORD.match(span) and span not in WORD_STOPLIST and not span.isupper():
                claims.append({"file": rel, "line": ln, "kind": "word", "ref": span, "ctx": {}})


# -------------------------------------------------------------------- fixture

GATE_Q = "Lint probe: continue?"
SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}},
          "required": ["result"]}


def fixture_graph(late_goal="lint-late"):
    return {
        "name": "docs-lint-7m0",
        "nodes": [
            {"id": "g", "type": "gate", "question": GATE_Q, "options": ["go", "hold"]},
            {"id": "bad", "type": "agent", "after": ["g"], "goal": "FAILME", "schema": SCHEMA},
            {"id": "f", "type": "agent", "after": ["g"],
             "fanout": {"items": ["one", "two"], "goal": "lint item {item}"}},
            {"id": "wall", "type": "agent", "after": ["g"], "goal": "QSLEEP 30",
             "timeout": 2, "schema": SCHEMA},
            {"id": "slow", "type": "agent", "after": ["g"], "goal": "QSLEEP 6", "schema": SCHEMA},
            {"id": "late", "type": "agent", "after": ["slow"], "goal": late_goal, "schema": SCHEMA},
        ],
    }


def _jload(p: Path, default=None):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return default


def build_fixture(repo: Path, log, cmds=()):
    """Run the scenario; return (run_id, artifacts, relpaths, notes).

    `cmds` are doc command claims: the substitutable ones (placeholders the
    fixture can name — <run_id> and friends) are EXECUTED here, while the
    state dir is still alive, and land in artifacts under "cmd:"+ref.
    """
    notes = []
    tmp = Path(tempfile.mkdtemp(prefix="docs-lint-"))
    home = tmp / "home"
    runs = tmp / "runs"
    home.mkdir(); runs.mkdir()
    env = dict(os.environ)
    for k in [k for k in env if k.startswith("HERMES_WF_") and k != "HERMES_WF_HERMES_BIN"]:
        del env[k]
    for k in [k for k in env if k.startswith("HERMES_SESSION_") or k.startswith("HERMES_UI_SESSION_")]:
        del env[k]
    env.update(HERMES_HOME=str(home), WF_RUNS_ROOT=str(runs),
               HERMES_WF_HERMES_BIN=str(repo / "tests" / "fake"),
               FAKE_LOG=str(tmp / "fake.log"), WORKFLOW_MAX_SEATS="8")
    old = dict(os.environ)
    os.environ.update(env)
    sys.path.insert(0, str(repo / "tests"))
    door = None
    try:
        import wf_test_isolation as iso
        door, actions = door_actions(repo)
        iso.install(door)
        run_id, artifacts = None, {}

        resp = door.ACTIONS["run"]({"graph": fixture_graph()})
        run_id = resp.get("run_id")
        if not run_id:
            raise RuntimeError(f"fixture run refused: {resp}")
        artifacts["run_response"] = resp

        rdir = runs / run_id

        def status(seats=False, detail=""):
            a = {"run_id": run_id}
            if seats:
                a["seats"] = True
            if detail:
                a["detail"] = detail
            return door.ACTIONS["status"](a)

        # hold: gate parks the run
        t0 = time.time()
        while time.time() - t0 < 25 and not (rdir / "events.jsonl").exists():
            time.sleep(0.05)
        held = None
        t0 = time.time()
        while time.time() - t0 < 25:
            held = status()
            if (held.get("nodes", {}).get("g") or {}).get("status") in ("running", "pending") \
                    or held.get("status") in ("pending", "running", "held"):
                break
            time.sleep(0.05)
        rel = door.ACTIONS["release"]({"run_id": run_id, "gate_id": "g", "answer": "go"})
        artifacts["release_response"] = rel

        # live window: steer + amend + seats read while `slow` holds wave 2
        steer = door.ACTIONS["steer"]({"run_id": run_id, "node": "late", "text": "lint steer line"})
        artifacts["steer_response"] = steer
        g2 = fixture_graph(late_goal="lint-late AMENDED-7M0")
        amend = door.ACTIONS["amend"]({"run_id": run_id, "graph": g2})
        artifacts["amend_response"] = amend
        seats_seen = None
        t0 = time.time()
        while time.time() - t0 < 20:
            st = status(seats=True)
            if isinstance(st.get("seats"), dict):
                seats_seen = st
                if st["seats"].get("holders"):
                    break
            time.sleep(0.05)
        artifacts["status_live"] = seats_seen or status(seats=True)
        for _ in range(2):      # a second held read (holders may have drained)
            time.sleep(0.3)
            artifacts.setdefault("status_live2", status(seats=True))

        # terminal: the run has quiesced only when the verdict is terminal AND
        # the runner is gone (a `failed` verdict while siblings run is mid-flight)
        t0 = time.time()
        final = None
        while time.time() - t0 < 75:
            final = status()
            if (final.get("status") in ("done", "failed", "stopped", "partial")
                    and not final.get("runner_live")):
                break
            time.sleep(0.2)
        artifacts["status_final"] = final
        artifacts["status_response"] = artifacts.get("status_live") or final
        if final.get("status") not in ("done", "failed", "stopped", "partial"):
            notes.append(f"fixture: run {run_id} never went terminal (last {final.get('status')})")

        # recovery CLI (also an executed doc command)
        rc = subprocess.run([sys.executable, str(repo / "wf.py"), "recover", run_id],
                            env=os.environ, capture_output=True, text=True, timeout=30)
        artifacts["recover"] = _jloads(rc.stdout) if rc.returncode == 0 else None
        artifacts["recover_rc"] = rc.returncode

        # study quarantine + shelf: the door's other roots
        sub = door.ACTIONS["submit"]({
            "graph": {"name": "docs-lint-sub",
                      "nodes": [{"id": "solo", "type": "agent", "goal": "lint submit probe",
                                 "schema": SCHEMA}]},
            "why_not_library": "fixture for the runtime-docs dead-reference lint: the shelf "
                               "carries no docs-lint probe graph and none should.",
            "lane": "docs-lint"})
        artifacts["submit_response"] = sub
        artifacts["inbox_response"] = door.ACTIONS["inbox"]({"kind": "submissions"})
        artifacts["save_response"] = door.ACTIONS["save"]({"run_id": run_id, "name": "docs-lint-shelf"})
        artifacts["diff_response"] = door.ACTIONS["diff"]({"run_id": run_id})
        artifacts["list_response"] = door.ACTIONS["list"]({})

        # doc commands with substitutable args: executed against this live state
        sub = {"<run_id>": run_id, "<run>": run_id, "<id>": run_id}
        for ref in dict.fromkeys(cmds):
            parts = ref.split()[1:]
            vargs = [a for a in parts[1:] if not a.startswith("[")]
            if any(a.startswith("<") and a not in sub for a in vargs):
                continue
            argv = [sys.executable, str(repo / "wf.py")] + \
                   [parts[0]] + [sub.get(a, a) for a in vargs]
            try:
                rcx = subprocess.run(argv, env=os.environ, capture_output=True,
                                     text=True, timeout=30)
                artifacts["cmd:" + ref] = {"rc": rcx.returncode,
                                           "stdout": rcx.stdout,
                                           "json": _jloads(rcx.stdout) if rcx.returncode == 0 else None}
            except Exception as e:
                artifacts["cmd:" + ref] = {"rc": None, "error": str(e)}

        relpaths = []
        for p in runs.rglob("*"):
            r = str(p.relative_to(runs))
            if p.is_file():
                relpaths.append(r)
            elif p.is_dir():
                relpaths.append(r + "/")
        for label in ("run.json", "graph.json", "events.jsonl", "amends.jsonl", "inbox.jsonl",
                      "wake.jsonl", "side_effects.jsonl", "runner_exit.json"):
            if (rdir / label).exists():
                artifacts[label] = _jlines(rdir / label)
        for p in sorted((rdir / "nodes").rglob("*")):
            if p.is_file():
                artifacts["nodes:" + str(p.relative_to(rdir))] = _jlines(p)
        for p in sorted((rdir / "gates").glob("*")):
            artifacts["gates:" + p.name] = _jlines(p)
        for p in sorted((rdir / "steer").glob("*")) if (rdir / "steer").is_dir() else []:
            if p.suffix == ".jsonl":
                artifacts["steer:" + p.name] = _jlines(p)
        for p in sorted(runs.glob("inbox/*.json")):
            artifacts["submit-inbox:" + p.name] = _jlines(p)
        bnd = rdir / "logs" / "boundary.log"
        if bnd.exists():
            artifacts["boundary.log"] = _jlines(bnd)
        return run_id, artifacts, sorted(set(relpaths)), notes
    finally:
        os.environ.clear(); os.environ.update(old)
        shutil.rmtree(tmp, ignore_errors=True)


def _jloads(text):
    try:
        return json.loads(text.strip().splitlines()[0])
    except (OSError, ValueError, IndexError):
        return None


def _jlines(p: Path):
    out = []
    try:
        for ln in p.read_text().splitlines():
            if not ln.strip():
                continue
            try:
                out.append(json.loads(ln))
            except ValueError:
                out.append({"__torn__": ln})
    except OSError:
        pass
    return out


# ------------------------------------------------------------------- resolver

class Resolver:
    def __init__(self, pool: Pool, actions, verbs, run_id, artifacts, relpaths, notes):
        self.pool = pool
        self.actions = actions
        self.verbs = verbs
        self.run_id = run_id
        self.artifacts = artifacts or {}
        self.relpaths = relpaths or []
        self.notes = notes
        self.violations = []
        self.stats = {"exercised": 0, "literal": 0}

    # -------- helpers
    def containers(self):
        """Flatten every artifact (dicts / lists of dicts) into key-set containers,
        each with a label path and an optional `event` value."""
        seen = []

        def walk(obj, label):
            if isinstance(obj, dict):
                if "__torn__" in obj:
                    return
                seen.append((label, obj))
                for k, v in obj.items():
                    walk(v, f"{label}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    walk(v, f"{label}[{i}]")

        for name, art in self.artifacts.items():
            walk(art, name)
        return seen

    def bind(self, anchor, keys):
        """Return the artifact container a field claim binds to, or None."""
        conts = self.containers()
        if anchor:
            if anchor.startswith("response:"):
                act = anchor.split(":", 1)[1]
                art = self.artifacts.get(act + "_response") or self.artifacts.get("submit_response") \
                    if act == "submit" else self.artifacts.get(act + "_response")
                if isinstance(art, dict):
                    return art
                return None
            for label, d in conts:
                if anchor in ("events", ) and False:
                    continue
                if d.get("event") == anchor or label.endswith("." + anchor) or label == anchor:
                    return d
            # anchor as a parent FIELD name: find the dict under that key
            for label, d in conts:
                if label.endswith("." + anchor):
                    return d
        # distinctive-key match: any container covering the claimed keys
        for label, d in conts:
            if all(k in d for k in keys):
                return d
        return None

    @staticmethod
    def _seg_re(seg: str) -> str:
        """Compile one path-claim segment: `<ph>` -> a wildcard, `[...]` -> an
        optional group, everything else literal."""
        out, i = [], 0
        while i < len(seg):
            ch = seg[i]
            if ch == "<":
                j = seg.find(">", i)
                if j < 0:
                    out.append(re.escape(ch)); i += 1; continue
                out.append("[^/]+"); i = j + 1
            elif ch == "[":
                j = seg.find("]", i)
                if j < 0:
                    out.append(re.escape(ch)); i += 1; continue
                out.append("(?:" + Resolver._seg_re(seg[i + 1:j]) + ")?"); i = j + 1
            else:
                k = i
                while k < len(seg) and seg[k] not in "<[":
                    k += 1
                out.append(re.escape(seg[i:k])); i = k
        return "".join(out)

    def match_path(self, claim) -> bool:
        ref = claim["ref"]
        for junk in ("runs_root()/", "$HERMES_HOME/workflows/", "runs/<run>/", "runs/<id>/"):
            if ref.startswith(junk):
                ref = ref[len(junk):]
        root = None
        if ref.startswith("<seats>/"):
            root, ref = "seats", ref[len("<seats>/"):]
        is_dir = ref.endswith("/")
        segs = [s for s in ref.split("/") if s != ""]
        pat = "/".join(self._seg_re(s) for s in segs)
        if is_dir:
            pat += r"(/.*)?$"          # a dir claim is satisfied by any row under it
        else:
            pat += r"$"
        try:
            rx = re.compile(pat)
        except re.error:
            return False
        for rel in self.relpaths:
            if root == "seats" and "/.seats/" not in "/" + rel:
                continue
            cands = [rel]
            if "/" in rel:
                cands.append(rel.split("/", 1)[1])   # run-dir-relative vs runs-root-relative
            if any(rx.search(c) for c in cands):
                return True
        return False

    # -------- claim handlers
    def resolve(self, claim):
        k = claim["kind"]
        h = getattr(self, "_k_" + k)
        h(claim)

    def _k_cmd(self, claim):
        verb = claim["ctx"].get("verb") or claim["ref"].split()[1]
        if verb not in self.verbs:
            self.violations.append({**claim, "why": "dead-verb"})
            return
        res = self.artifacts.get("cmd:" + claim["ref"])
        if res is None:
            self.notes.append(f"{claim['file']}:{claim['line']}: cmd not executed "
                              f"(no fixture, or unsubstitutable arg) — verb liveness only")
            return
        if res.get("rc") != 0 or (verb == "recover" and not isinstance(res.get("json"), dict)):
            self.violations.append({**claim, "why": "cmd-exec-fail",
                                    "ref": claim["ref"] + f" (rc={res.get('rc')})"})
            return
        if isinstance(res.get("json"), dict):
            self.artifacts.setdefault("recover", res["json"])
        self.stats["exercised"] += 1

    def _k_action(self, claim):
        if claim["ref"] not in self.actions:
            self.violations.append({**claim, "why": "dead-action"})
        else:
            self.stats["exercised"] += 1

    def _k_env(self, claim):
        if self.pool.has(claim["ref"]):
            self.stats["literal"] += 1
        else:
            self.violations.append({**claim, "why": "dead-env"})

    def _k_repo(self, claim):
        p = claim["ref"]
        if (REPO / p).exists() or list(REPO.glob(p.rstrip("/"))):
            self.stats["literal"] += 1
        else:
            self.violations.append({**claim, "why": "repo-path-missing"})

    def _k_path(self, claim):
        if self.match_path(claim):
            self.stats["exercised"] += 1
            return
        base = claim["ref"].rstrip("/").split("/")[-1]
        # the concrete trailing literal after the last placeholder is the shipped
        # byte a reader can grep (`<id>.json.unconsumed` -> `.json.unconsumed`)
        probe = re.split(r"[>\]]", base)[-1] or base.replace("<", "").replace(">", "")
        for frag in ('"', "'"):
            if self.pool.has(frag + probe + frag) or self.pool.has(probe):
                self.notes.append(f"{claim['file']}:{claim['line']}: unexercised path "
                                  f"'{claim['ref']}' (literal in shipped sources)")
                self.stats["literal"] += 1
                return
        self.violations.append({**claim, "why": "dead-path"})

    def _k_field(self, claim):
        keys = claim["ref"].split(",")
        anchor = claim["ctx"].get("anchor")
        bound = self.bind(anchor, keys) if self.artifacts else None
        if bound is not None:
            missing = [k for k in keys if k not in bound and k != "__call__"]
            if not missing:
                self.stats["exercised"] += 1
                return
            for k in missing:
                if self.pool.has('"' + k + '"') or self.pool.has(k):
                    self.notes.append(f"{claim['file']}:{claim['line']}: conditional field "
                                      f"'{k}' not on this fixture read of '{anchor or bound_label(bound)}'")
                else:
                    self.violations.append({**claim, "why": "drifted-field", "ref": k,
                                            "line": claim["ctx"].get("klines", {}).get(k, claim["line"])})
            return
        # unbound: every key must at least live in the source pool
        for k in keys:
            if k == "__call__":
                continue
            if self.pool.has('"' + k + '"') or self.pool.has(k):
                self.notes.append(f"{claim['file']}:{claim['line']}: unbound field '{k}' "
                                  f"(literal in shipped sources)")
                self.stats["literal"] += 1
            else:
                self.violations.append({**claim, "why": "dead-field", "ref": k,
                                        "line": claim["ctx"].get("klines", {}).get(k, claim["line"])})

    def _k_cite(self, claim):
        ident = claim["ref"]
        files = claim["ctx"].get("files") or []
        head = tail = None
        if "." in ident:
            head, tail = ident.split(".", 1)
        cands = []
        if head and head + ".py" in self.pool.texts:
            cands.append((tail, [head + ".py"]))
        cands.append((ident, files))
        cands.append((ident or tail, None))
        for needle, filescope in cands:
            if not needle:
                continue
            if needle in self.actions or needle in self.verbs:
                self.stats["exercised"] += 1
                return
            if self.pool.has(needle, filescope) or self.pool.has(needle):
                self.stats["literal"] += 1
                return
        self.violations.append({**claim, "why": "dead-symbol"})

    def _k_word(self, claim):
        if claim["ref"] in self.actions or claim["ref"] in self.verbs:
            self.stats["exercised"] += 1
            return
        if self.pool.has('"' + claim["ref"] + '"') or self.pool.has(claim["ref"]):
            self.stats["literal"] += 1
        else:
            self.violations.append({**claim, "why": "dead-field"})


def bound_label(d):
    return "<bound>"


# ---------------------------------------------------------------------- main

def run(repo: Path, docs: Path, use_fixture: bool, quiet=False):
    global REPO
    REPO = repo
    pool = Pool(load_pool(repo))
    try:
        door, actions = door_actions(repo)
    except Exception as e:
        print(f"docs-lint: cannot load door for the action table: {e}", file=sys.stderr)
        return 2
    verbs = cli_verbs(pool)
    claims = extract(docs)
    notes = []
    run_id, artifacts, relpaths = None, {}, []
    if use_fixture:
        try:
            cmds = [c["ref"] for c in claims if c["kind"] == "cmd"]
            run_id, artifacts, relpaths, fx_notes = build_fixture(repo, sys.stderr, cmds)
            notes.extend(fx_notes)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"docs-lint: fixture build failed: {e}", file=sys.stderr)
            return 2
    rs = Resolver(pool, actions, verbs, run_id, artifacts, relpaths, notes)
    for c in claims:
        rs.resolve(c)
    kinds = {}
    for c in claims:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    for line in sorted(set(notes)) if not quiet else []:
        print("note: " + line)
    for v in sorted(rs.violations, key=lambda v: (v["file"], v["line"])):
        print(f"{v['file']}:{v['line']}: {v['why']} {v['kind']} "
              f"'{v['ref']}'" + (f" in {list(v['ctx'])[:4]}" if v.get("ctx") and not quiet else ""))
    print(f"docs-lint: files={len(list(docs.rglob('*.md')))} claims={len(claims)} "
          f"by-kind={kinds} exercised={rs.stats['exercised']} "
          f"literal-backed={rs.stats['literal']} violations={len(rs.violations)}")
    return 1 if rs.violations else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(REPO_DEFAULT))
    ap.add_argument("--docs", default=None, help="docs runtime root (default <repo>/docs/runtime)")
    ap.add_argument("--no-fixture", action="store_true",
                    help="static checks only (no fixture run): verbs, actions, envs, "
                         "literals, repo paths, cites")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    docs = Path(a.docs).resolve() if a.docs else repo / "docs" / "runtime"
    return run(repo, docs, not a.no_fixture, a.quiet)


if __name__ == "__main__":
    sys.exit(main())
