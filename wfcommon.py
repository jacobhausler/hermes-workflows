"""hermes-workflows shared semantics — ONE validator, ONE fingerprint rule, ONE read model.

Imported by wf.py (runner), __init__.py (tool door), dashboard/plugin_api.py (UI API).
Everything that decides "is this result still trustworthy" or "what state is this run
in" lives here, so the three readers can never disagree.
"""
import hashlib, json, os, re, shlex, subprocess, sys
from pathlib import Path

def jload(p, default=None):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return default

def def_hash(node):
    return hashlib.sha256(json.dumps(node, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]

_EFP_SEP = "\u241f"

def efp(byid, node, _seen=None):
    """Effective fingerprint: own def + every ancestor's effective fingerprint.
    An amended node (or any ancestor) changes the efp of everything downstream, so
    downstream results are stale and nodes downstream re-run or re-hold — transitively."""
    _seen = _seen or set()
    nid = node["id"]
    if nid in _seen:
        return "?"  # unreachable for validated (acyclic) graphs
    _seen = _seen | {nid}
    parts = [def_hash(node)]
    for a in sorted(node.get("after", [])):
        if a in byid:
            parts.append(efp(byid, byid[a], _seen))
    return hashlib.sha256(_EFP_SEP.join(parts).encode()).hexdigest()[:16]


def graph_fingerprint(graph):
    """Stable signature of the node definitions that a runner verdict describes."""
    nodes = (graph or {}).get("nodes")
    if not isinstance(nodes, list) or any(not isinstance(n, dict) or not n.get("id") for n in nodes):
        return None
    try:
        byid = {n["id"]: n for n in nodes}
        facts = {str(n["id"]): efp(byid, n) for n in nodes}
        raw = json.dumps(facts, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    except Exception:
        return None

ID_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")

# Closed grammar (Q2): an unknown key is a REJECTED key, never a silently ignored one.
# `tier` is in the agent set because resolve_models stamps it at run/amend (test_tiers
# locks it) and the runner re-validates saved graphs — the door must never reject a
# graph it baked itself. `reasoning` is validated per node (Q5).
AGENT_KEYS = {"id", "type", "after", "goal", "context", "schema", "model", "provider", "toolsets",
              "max_turns", "timeout", "run_budget", "inputs", "fanout", "reasoning",
              "tier"}
GATE_KEYS = {"id", "type", "after", "question", "options", "context", "when", "wait", "on_skip"}
FANOUT_KEYS = {"items", "items_from", "goal", "schema", "quorum"}

REASONING_FALLBACK = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")
REASONING_IMPORT_PATH = [None]  # "hermes_constants" | "fallback-literal" — which tuple validated

def reasoning_levels():
    """Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.
    Import INSIDE the function (the module must import on hosts without core on
    sys.path); on import failure fall back to that exact tuple literal and log one
    line. REASONING_IMPORT_PATH records which path served (the test reports it)."""
    try:
        import hermes_constants
        allowed = ("none",) + tuple(hermes_constants.VALID_REASONING_EFFORTS)
        REASONING_IMPORT_PATH[0] = "hermes_constants"
    except Exception:
        allowed = REASONING_FALLBACK
        REASONING_IMPORT_PATH[0] = "fallback-literal"
        print("wfcommon: hermes_constants import failed — using the reasoning-level "
              "fallback literal (keep it in sync with core).", file=sys.stderr)
    return allowed

def validate_graph_errors(nodes):
    """Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:
    node ids double as filenames."""
    errs = []
    def E(nid, field, msg):
        errs.append({"node": nid, "field": field, "msg": msg})

    def schema_check(nid, field, schema):
        # Runner's validator consumes only this subset; description is prompt-only
        # annotation. Never accept a constraint such as enum that cannot be enforced.
        for k in sorted(set(schema) - {"type", "required", "properties", "items", "description"}):
            E(nid, f"{field}.{k}", "unsupported schema keyword; supported: type, required, properties, items, description")
        if "type" in schema and schema["type"] not in ("object", "array", "string", "number", "integer", "boolean"):
            E(nid, f"{field}.type", "unsupported schema type")
        if "required" in schema and (not isinstance(schema["required"], list)
                                      or not all(isinstance(x, str) for x in schema["required"])):
            E(nid, f"{field}.required", "required must be a list of strings")
        props = schema.get("properties")
        if props is not None:
            if not isinstance(props, dict):
                E(nid, f"{field}.properties", "properties must be an object")
            else:
                for k, sub in props.items():
                    if not isinstance(sub, dict):
                        E(nid, f"{field}.properties.{k}", "property schema must be an object")
                    else:
                        schema_check(nid, f"{field}.properties.{k}", sub)
        if "items" in schema:
            if not isinstance(schema["items"], dict):
                E(nid, f"{field}.items", "items schema must be an object")
            else:
                schema_check(nid, f"{field}.items", schema["items"])

    if not isinstance(nodes, list) or not nodes:
        return [{"node": None, "field": "nodes", "msg": "nodes must be a non-empty list"}]
    bad_el = [i for i, n in enumerate(nodes) if not isinstance(n, dict)]
    if bad_el:
        return [{"node": None, "field": f"nodes[{bad_el[0]}]",
                 "msg": f"nodes[{bad_el[0]}] is not an object"}]
    ids = [n.get("id") for n in nodes]
    if not all(ids):
        E(None, "nodes", "missing node ids")
    if len(set(ids)) != len(ids):
        E(None, "nodes", "duplicate node ids")
    if not all(ids):
        return errs  # per-node checks below need real ids
    for i in ids:
        if not isinstance(i, str) or not ID_OK.match(i):
            E(i, "id", f"invalid node id {i!r} (alnum start, [A-Za-z0-9_.-], <=64)")
        if not isinstance(i, str):
            return errs  # non-string ids cannot key the ancestry maps safely
    idset = set(ids)
    parents = {n["id"]: [a for a in n.get("after", []) if a in idset] for n in nodes}
    for n in nodes:
        nid = n["id"]
        if n.get("type") not in ("agent", "gate"):
            E(nid, "type", "type must be agent|gate")
            continue  # per-type key grammar is undefined without a type
        for k in sorted(set(n) - (AGENT_KEYS if n["type"] == "agent" else GATE_KEYS)):
            # dedicated errors below own these keys (clearer messages, no double-report)
            if n["type"] == "agent" and k == "wait":
                continue
            if n["type"] == "gate" and k == "inputs":
                continue
            if n["type"] == "agent" and k == "when":
                E(nid, "when", "only gate nodes take when; use a gate with on_skip:prune to branch")
                continue
            E(nid, k, "unknown key; allowed: "
                      + json.dumps(sorted(AGENT_KEYS if n["type"] == "agent" else GATE_KEYS)))
        for a in n.get("after", []):
            if a not in idset:
                E(nid, "after", f"references unknown 'after': {a}")
        for k, hi in (("timeout", 86400), ("max_turns", 200), ("run_budget", 86400)):
            v = n.get(k)
            if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0 or v > hi):
                E(nid, k, f"{k} must be a number in (0, {hi}]")
        if n.get("reasoning") is not None:
            lv = n["reasoning"]
            if lv not in reasoning_levels():
                E(nid, "reasoning", f"reasoning {lv!r} invalid; allowed: "
                                    f"{list(reasoning_levels())}")
        if n["type"] == "agent":
            if n.get("model") is not None and not isinstance(n.get("model"), str):
                E(nid, "model", "model must be a string")
            if "provider" in n:
                provider = n.get("provider")
                if not isinstance(provider, str) or not provider or provider.strip() != provider:
                    E(nid, "provider", "provider must be a non-empty provider id without surrounding whitespace")
                model = n.get("model")
                if not isinstance(model, str) or not model.strip():
                    E(nid, "provider", "provider requires a non-empty model")
            fo = n.get("fanout")
            if fo is not None:
                if not isinstance(fo, dict):
                    E(nid, "fanout", "fanout must be an object")
                else:
                    for k in sorted(set(fo) - FANOUT_KEYS):
                        E(nid, f"fanout.{k}", "unknown key; allowed: "
                                              + json.dumps(sorted(FANOUT_KEYS)))
                    if fo.get("items") is None and not fo.get("items_from"):
                        E(nid, "fanout", "fanout needs items or items_from")
                    if fo.get("items") is not None and not isinstance(fo["items"], list):
                        E(nid, "fanout.items", "fanout.items must be a list")
                    items = fo.get("items") if isinstance(fo.get("items"), list) else []
                    for i, it in enumerate(items):
                        if isinstance(it, dict) and "goal" in it and not (isinstance(it["goal"], str) and it["goal"].strip()):
                            E(nid, f"fanout.items[{i}].goal", f"fanout.items[{i}].goal must be a non-empty string (it overrides fanout.goal)")
                    if items and not (fo.get("goal") or n.get("goal")) \
                            and not all(isinstance(it, dict) and isinstance(it.get("goal"), str) for it in items):
                        E(nid, "fanout.goal", "fanout needs a goal template or a goal on every item")
                    q = fo.get("quorum")
                    if q is not None and (not isinstance(q, int) or isinstance(q, bool) or q < 1):
                        E(nid, "fanout.quorum", "fanout.quorum must be a positive int")
                    fsc = fo.get("schema")
                    if fsc is not None:
                        if not isinstance(fsc, dict):
                            E(nid, "fanout.schema", "fanout.schema must be an object")
                        else:
                            schema_check(nid, "fanout.schema", fsc)
            elif not n.get("goal"):
                E(nid, "goal", "agent node has no goal")
            if n.get("schema") is not None:
                if not isinstance(n["schema"], dict):
                    E(nid, "schema", "schema must be an object")
                else:
                    schema_check(nid, "schema", n["schema"])
        osk = n.get("on_skip")
        if osk is not None and n.get("type") == "gate":   # non-gate: closed-key check already rejected it
            if osk not in ("pass", "prune"):
                E(nid, "on_skip", f"on_skip {osk!r} invalid; allowed: ['pass', 'prune']")
            elif n.get("when") is None:
                E(nid, "on_skip", "on_skip needs a `when` (nothing else can skip a gate)")
        w = n.get("wait")
        if w is not None:
            if n["type"] != "gate":
                E(nid, "wait", "only gate nodes take wait")
            else:
                for e in wait_spec_ok(w):
                    field = "wait" if e["field"] is None else f"wait.{e['field']}"
                    E(nid, field, f"gate node wait: {e['msg']}")
        if n.get("when") is not None and n["type"] == "gate":
            err = when_expr_ok(n["when"])
            if err:
                E(nid, "when", err)
        ins = n.get("inputs")
        if ins is not None:
            if n["type"] == "gate":
                E(nid, "inputs", "gates cannot have inputs")
            elif not isinstance(ins, list) or not all(isinstance(x, str) and x.strip() for x in ins):
                E(nid, "inputs", "inputs must be a list of non-empty ref strings")
            else:
                anc = set()
                stack = list(n.get("after", []))
                while stack:
                    a = stack.pop()
                    if a in anc or a not in idset:
                        continue
                    anc.add(a)
                    stack.extend(parents[a])
                for ref in ins:
                    head = ref.split(".")[0]
                    if head not in anc:
                        E(nid, "inputs", f"inputs ref {ref!r} head {head!r} is not an existing "
                                         f"node in its `after` ancestry (inputs must descend from it)")
    indeg = {i: 0 for i in idset}
    kids = {i: [] for i in idset}
    for n in nodes:
        for a in n.get("after", []):
            if a not in idset:
                continue  # unknown after already reported; can't key the topo maps
            indeg[n["id"]] += 1
            kids[a].append(n["id"])
    queue, seen = [i for i, d in indeg.items() if d == 0], 0
    while queue:
        x = queue.pop(); seen += 1
        for k in kids[x]:
            indeg[k] -= 1
            if indeg[k] == 0:
                queue.append(k)
    if seen != len(idset):
        E(None, "after", "cycle in graph")
    return errs

def validate_graph(nodes):
    """Old signature — the FIRST error as a string ("node X: ...") or None. Callers
    that want every defect use validate_graph_errors; the runner (wf.py) keeps this."""
    errs = validate_graph_errors(nodes)
    if not errs:
        return None
    e = errs[0]
    return (e["msg"] if e["node"] is None else f"node {e['node']}: {e['msg']}")

def quote_json_parse_error(text, exc):
    """±40 chars of the source around the offset of a JSONDecodeError — what the
    door shows when a graph ever arrives as a malformed JSON string."""
    t = str(text)
    off = getattr(exc, "pos", None)
    if not isinstance(off, int) or off < 0 or off > len(t):
        return t[:80]
    return t[max(0, off - 40):off + 40]

# ---------- runner identity and exit record (Lane A writes, this side ONLY reads) ----------

def runner_alive(r, pid_path=None):
    """A pid is not ownership: verify a live, non-zombie `wf.py run <id>`.
    /proc gives argv and (when readable) HERMES_HOME; ps supplies macOS/BSD.
    Unknown identity is NOT evidence of a running workflow."""
    r = Path(r)
    try:
        pid = int(Path(pid_path or r / "wf.pid").read_text().strip())
        if pid <= 0:
            return False
        os.kill(pid, 0)
        try:
            os.waitpid(pid, os.WNOHANG)  # our own zombie, if still unreaped
        except (ChildProcessError, OSError, AttributeError):
            pass
        try:
            state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
            argv = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="replace").split("\0")
            argv = [a for a in argv if a]
            try:
                environ = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
                homes = [v[12:].decode(errors="replace") for v in environ if v.startswith(b"HERMES_HOME=")]
                if homes and Path(homes[0]).resolve() != r.parent.parent.resolve():
                    return False
            except OSError:
                pass
        except OSError:  # macOS/BSD: ps gives state AND full command
            row = subprocess.run(["ps", "-ww", "-p", str(pid), "-o", "stat=", "-o", "command="],
                                 capture_output=True, text=True, check=True, timeout=2).stdout.strip()
            state, cmd = row.split(None, 1)
            argv = shlex.split(cmd)
        return not state.startswith("Z") and len(argv) >= 3 and Path(argv[-3]).name == "wf.py" \
            and argv[-2:] == ["run", r.name]
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return False

def runner_exit_read(r, pid_path=None):
    """Graph-bound runner verdict, or a crash when a previous pid lacks identity.
    No pid file means a fresh, not-yet-spawned run, not a crash."""
    rec = jload(Path(r) / "runner_exit.json")
    if isinstance(rec, dict) and rec.get("reason"):
        current_graph = jload(Path(r) / "graph.json")
        current_fp = graph_fingerprint(current_graph)
        if rec.get("graph_fingerprint") != current_fp:
            return {"reason": "stale", "previous_reason": rec.get("reason"), "at": rec.get("at")}
        return {k: v for k, v in rec.items()
                if k in ("reason", "at", "detail", "graph_fingerprint")}
    path = Path(pid_path) if pid_path is not None else Path(r) / "wf.pid"
    if not path.exists():
        return None
    return None if runner_alive(r, path) else {"reason": "crashed (no exit record)"}

# ---------- node state (the ONE validity rule: stored efp == current efp) ----------

def _legacy_chain_unchanged(r, n, byid):
    """A pre-efp record is valid ONLY if the stored def_hash matches AND every
    ancestor was itself committed in the legacy era (its record also lacks efp)
    with a matching def_hash — chain-checked recursively. 'Done right now' is NOT
    proof of 'unchanged since this commit': an amended ancestor that re-ran must
    NOT resurrect stale downstream records or gate answers (MF2)."""
    rec = jload(r / "nodes" / f"{n['id']}.json")
    if not rec or "efp" in rec or rec.get("def_hash") != def_hash(n):
        return False
    return all(a not in byid or _legacy_chain_unchanged(r, byid[a], byid)
               for a in n.get("after", []))

def node_rec(r, n, byid):
    """Return (status, rec): done|failed|pending. Stale (efp mismatch after an
    amend) == pending — its stored result must never be presented as current.
    Legacy (pre-efp) records carried def_hash only; a bare stamp is a downgrade
    attack on the validity law, so the whole ancestor chain must be proven
    unchanged legacy commits."""
    rec = jload(r / "nodes" / f"{n['id']}.json")
    st = (rec or {}).get("status")
    if st in ("done", "failed", "skipped"):
        if rec.get("efp") == efp(byid, n):
            return st, rec
        if "efp" not in rec and _legacy_chain_unchanged(r, n, byid):
            return st, rec
        return "pending", rec
    return "pending", rec

def gate_answer_valid(r, gate, byid):
    ans = jload(r / "gates" / f"{gate['id']}.json")
    if ans is None:
        return None
    if ans.get("_def") == efp(byid, gate):
        return ans
    gate_rec = jload(r / "nodes" / f"{gate['id']}.json", {}) or {}
    if "efp" not in gate_rec and "efp" not in ans:
        # legacy answer: same law as node records — the gate def AND its whole
        # ancestor chain must be proven unchanged legacy commits, not merely done.
        if ans.get("_def") != def_hash(gate):
            return None
        return ans if all(a not in byid or _legacy_chain_unchanged(r, byid[a], byid)
                          for a in gate.get("after", [])) else None
    return None

WHEN_TOKEN = re.compile(r"\s*(?:(==|!=|>=|<=|>|<|\(|\)|,|[A-Za-z_][A-Za-z0-9_.]*|'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|-?\d+(?:\.\d+)?|\bTrue\b|\bFalse\b|\bNone\b|and\b|or\b|not\b))")

def _tok_when(s):
    toks, i = [], 0
    while i < len(s):
        m = WHEN_TOKEN.match(s, i)
        if not m or m.end() == i:
            if s[i].isspace(): i += 1; continue
            raise ValueError(f"bad char {s[i]!r} at {i}")
        toks.append(m.group(1)); i = m.end()
    return toks

def _when_expr(toks, pos, outputs, allow_or=True):
    """Tiny recursive-descent evaluator: or > and > not > comparison > value.
    Values: out.<node>.dotted.path | string/number/bool/None literals."""
    val, pos = _when_or(toks, pos, outputs) if allow_or else _when_cmp(toks, pos, outputs)
    return val, pos

def _when_or(toks, pos, outputs):
    val, pos = _when_and(toks, pos, outputs)
    while pos < len(toks) and toks[pos] == "or":
        rhs, pos = _when_and(toks, pos + 1, outputs)
        val = val or rhs
    return val, pos

def _when_and(toks, pos, outputs):
    val, pos = _when_not(toks, pos, outputs)
    while pos < len(toks) and toks[pos] == "and":
        rhs, pos = _when_not(toks, pos + 1, outputs)
        val = val and rhs
    return val, pos

def _when_not(toks, pos, outputs):
    if pos < len(toks) and toks[pos] == "not":
        val, pos = _when_not(toks, pos + 1, outputs)
        return (not val), pos
    return _when_cmp(toks, pos, outputs)

class _SV:
    """Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises
    on value semantics — structural errors surface, value errors cannot mask them."""
    def __eq__(self, o): return True
    def __ne__(self, o): return False
    def __lt__(self, o): return True
    def __le__(self, o): return True
    def __gt__(self, o): return True
    def __ge__(self, o): return True
    def __bool__(self): return True
_SYNTAX = _SV()

def _when_atom(toks, pos, outputs):
    if pos >= len(toks):
        raise ValueError("unexpected end of expression")
    t = toks[pos]
    if t == "(":
        val, pos = _when_or(toks, pos + 1, outputs)
        if pos >= len(toks) or toks[pos] != ")":
            raise ValueError("missing )")
        return val, pos + 1
    if outputs is _SYNTAX:  # syntax mode: EVERY atom is a sentinel — literals can
        if t.startswith("'") or t.startswith('"') or re.fullmatch(r"-?\d+(?:\.\d+)?", t) \
                or t in ("True", "False", "true", "false", "None"):
            return _SV(), pos + 1     # never carry real values that TypeError mid-parse
    if t.startswith("'") or t.startswith('"'):
        return t[1:-1].encode().decode("unicode_escape"), pos + 1
    if re.fullmatch(r"-?\d+(?:\.\d+)?", t):
        return (float(t) if "." in t else int(t)), pos + 1
    if t in ("True", "False", "true", "false", "None"):
        return {"True": True, "False": False, "true": True, "false": False, "None": None}[t], pos + 1
    if t == "out" or t.startswith("out."):
        if outputs is _SYNTAX:
            return _SV(), pos + 1
        path = t.split(".")
        cur = outputs
        for p in path[1:]:
            if isinstance(cur, list):
                try: cur = cur[int(p)]
                except (ValueError, IndexError): return None, pos + 1
            elif isinstance(cur, dict): cur = cur.get(p)
            else: return None, pos + 1
        return cur, pos + 1
    raise ValueError(f"unexpected token {t!r}")

def _when_cmp(toks, pos, outputs):
    lhs, pos = _when_atom(toks, pos, outputs)
    if pos < len(toks) and toks[pos] in ("==", "!=", ">", ">=", "<", "<="):
        op = toks[pos]; pos += 1
        rhs, pos = _when_atom(toks, pos, outputs)
        # TypeError (comparing mismatched types) PROPAGATES — when_true turns it
        # into a HOLD. A gate must never be skipped by a failing assumption.
        # Lazy dispatch: evaluating all operators eagerly would raise on the
        # unchosen ones (None > True) and poison valid == comparisons.
        if op == "==":   return lhs == rhs, pos
        elif op == "!=": return lhs != rhs, pos
        elif op == ">":  return lhs > rhs, pos
        elif op == ">=": return lhs >= rhs, pos
        elif op == "<":  return lhs < rhs, pos
        else:            return lhs <= rhs, pos
    return lhs, pos

def when_expr_ok(expr):
    """Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands),
    so a value TypeError can never short-circuit the structural pass and mask a
    trailing token. Malformed syntax is REJECTED at submit and at runner startup;
    value errors against live data surface at fire time as a HOLD (fail-safe)."""
    toks = None
    try:
        toks = _tok_when(expr)
    except ValueError as e:
        return f"when: {e}"
    if not toks:
        return "empty when expression"
    try:
        _, pos = _when_or(toks, 0, _SYNTAX)
    except ValueError as e:
        return f"when: {e}"
    except Exception as e:  # syntax mode must be total: ANY raise = malformed
        return f"when: {type(e).__name__}: {e}"
    if pos != len(toks):
        return f"when: unexpected token {toks[pos]!r}"
    return None

def when_true(gate, outputs):
    """Conditional-gate predicate over a BOUNDED grammar (out paths, literals,
    comparisons, and/or/not, parens) — never Python eval. A broken 'when' FAILS
    SAFE to hold (a typo must never silently skip a human gate): both value
    errors AND unconsumed trailing tokens raise into the hold path."""
    w = gate.get("when")
    if not w:
        return True
    val, pos = _when_or(_tok_when(w), 0, outputs)
    if pos != len(_tok_when(w)):
        raise ValueError("when: trailing tokens")
    return bool(val)

# ---------- the ONE read model ----------

WAIT_KEYS = {"wait_s", "until_argv", "every_s", "timeout_s"}

def wait_spec_ok(w):
    """gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered gate.
    wait_s alone = timer. until_argv = a fixed argv list (never a shell string) re-run
    every every_s until exit 0. At least one of wait_s/until_argv. timeout_s bounds the
    whole park (default 3600, max 86400). Returns a LIST of {field, msg} dicts (empty
    = ok); field None names the wait block itself, else a sub-key."""
    out = []
    def E(field, msg):
        out.append({"field": field, "msg": msg})
    if not isinstance(w, dict):
        return [{"field": None, "msg": "must be an object"}]
    for k in sorted(set(w) - WAIT_KEYS):
        E(k, f"unknown key {k!r}; allowed: {sorted(WAIT_KEYS)}")
    if w.get("wait_s") is None and not w.get("until_argv"):
        E(None, "needs wait_s and/or until_argv")
    for k, hi in (("wait_s", 86400), ("every_s", 3600), ("timeout_s", 86400)):
        v = w.get(k)
        if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0 or v > hi):
            E(k, f"{k} must be a number in (0, {hi}]")
    argv = w.get("until_argv")
    if argv is not None and (not isinstance(argv, list) or not argv
                             or not all(isinstance(a, str) and a for a in argv)):
        E("until_argv", "until_argv must be a non-empty list of strings (fixed argv, no shell)")
    return out

def blocked_by(n, states, nodes_meta=None):
    """P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with its
    state, computed at query time and never persisted. nodes_meta may carry per-node
    liveness ({id: {"idle_s": .., "parked": {...}}}) to enrich the state word."""
    out = []
    for a in n.get("after", []):
        st = states.get(a)
        if st in ("done", "skipped"):
            continue
        m = (nodes_meta or {}).get(a) or {}
        if st == "failed":
            word = "failed"
        elif m.get("held"):
            word = "held at gate"
        elif m.get("parked"):
            pk = m["parked"]
            word = f"parked ({pk.get('kind')}, attempt {pk.get('attempt', 0)})"
        elif m.get("running"):
            idle = m.get("idle_s")
            word = f"running idle {int(idle)}s" if idle is not None else "running"
        else:
            word = "pending"
        out.append(f"{a}: {word}")
    return out

def prune_states(nodes, states):
    """ONE derivation shared by runner and read model (no second store). A gate skipped
    with on_skip:'prune' commits `skipped`; a node whose `after` deps are ALL skipped is
    itself `skipped` (terminal, non-failure). A join with >=1 live dep runs normally —
    skipped deps count as satisfied. Mutates `states`; returns ids newly derived skipped
    (pending before) so the runner can commit them as efp-stamped facts."""
    derived, changed = set(), True
    while changed:
        changed = False
        for n in nodes:
            deps = n.get("after", [])
            if states.get(n["id"]) == "pending" and deps and all(states.get(a) == "skipped" for a in deps):
                states[n["id"]] = "skipped"; derived.add(n["id"]); changed = True
    return derived

def dep_satisfied(states, a):
    return states.get(a) in ("done", "skipped")

def _active_spawns(r, n, byid):
    """All verified uncommitted child identities, never historical DB liveness."""
    records = [r / "nodes" / f"{n['id']}.json"]
    if n.get("fanout"):
        records.extend(sorted((r / "nodes").glob(f"{n['id']}.[0-9]*.json")))
    active = []
    for path in records:
        rec = jload(path) or {}
        if rec.get("status") != "running" or rec.get("efp") != efp(byid, n):
            continue
        pid, skey = rec.get("pid"), rec.get("skey")
        if not isinstance(pid, int) or pid <= 0 or not isinstance(skey, str) or not skey:
            continue
        title = skey if "#a" in skey or not isinstance(rec.get("attempt"), int) else f"{skey}#a{rec['attempt']}"
        try:
            os.kill(pid, 0)
            try:
                stat_text = Path(f"/proc/{pid}/stat").read_text()
                state = stat_text.rsplit(")", 1)[1].split()[0]
                cmd = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="replace").replace("\0", " ")
            except OSError:  # macOS/BSD: verify state and identity without procfs.
                row = subprocess.run(["ps", "-ww", "-p", str(pid), "-o", "stat=", "-o", "command="],
                                     capture_output=True, text=True, check=True, timeout=2).stdout
                state, cmd = row.strip().split(None, 1)
            if state.startswith("Z") or title not in cmd.split():
                continue
        except (OSError, IndexError, ValueError, subprocess.SubprocessError):
            continue  # unknown identity is not proof of an active child
        active.append({**{k: rec[k] for k in ("pid", "started", "attempt", "log_path") if k in rec},
                       "skey": title})
    return active

def _active_spawn(r, n, byid):
    """Compatibility: first verified spawn for existing blocked-by consumers."""
    return next(iter(_active_spawns(r, n, byid)), None)

def run_state(r):
    """Derived truth of a run dir: status, per-node status, held gate meta.
    status: pending|running|interrupted|held|done|failed|stopped.
    'interrupted' has unfinished work but NO verified runner; only wait/release/amend
    explicitly resume it. A later amend demotes a stopped run to interrupted."""
    graph = jload(r / "graph.json")
    if not graph or not graph.get("nodes"):
        return None
    byid = {n["id"]: n for n in graph["nodes"]}
    live = runner_alive(r)
    outputs, states, nodes, recs = {}, {}, {}, {}
    for n in graph["nodes"]:
        st, rec = node_rec(r, n, byid)
        states[n["id"]] = st; recs[n["id"]] = rec
        if st == "done":
            outputs[n["id"]] = (rec or {}).get("output")
    prune_states(graph["nodes"], states)   # derived view: pruned-but-uncommitted read as skipped
    for n in graph["nodes"]:
        st, rec = states[n["id"]], recs[n["id"]]
        active = _active_spawns(r, n, byid) if live and st == "pending" and n["type"] == "agent" else []
        nodes[n["id"]] = {"type": n["type"], "status": "running" if active else st, "after": n.get("after", []),
                          "fanout": bool(n.get("fanout")),
                          "stale_of_amend": bool(rec) and st == "pending" and rec.get("status") in ("done", "failed", "skipped") or None}
        if active:
            nodes[n["id"]]["active_spawn"] = active[0]
            nodes[n["id"]]["active_spawns"] = active
    def deps_ok(n):
        return all(dep_satisfied(states, a) for a in n.get("after", []))
    last = None
    try:
        for line in (r / "events.jsonl").read_text().splitlines()[-20:]:
            try:
                last = json.loads(line)
            except Exception:
                continue
    except FileNotFoundError:
        pass
    status = "running" if live else "interrupted"
    held = None
    if (last or {}).get("event") == "run.stopped":
        status = "stopped"
    elif any(s == "failed" for s in states.values()):
        status = "failed"
    elif all(s in ("done", "skipped") for s in states.values()):
        status = "done"
    else:
        gate = next((n for n in graph["nodes"] if n["type"] == "gate"
                     and states[n["id"]] == "pending" and deps_ok(n)), None)
        if gate and gate.get("wait") and gate_answer_valid(r, gate, byid) is None:
            # machine-answered gate: the runner is polling it — 'running', never 'held'.
            # Its blockage is self-explaining via nodes[id].parked (P4 + jury tweak).
            pk = jload(r / "gates" / f"{gate['id']}.parked.json", {}) or {}
            if live and pk.get("_def") == efp(byid, gate):
                nodes[gate["id"]]["parked"] = {k: v for k, v in pk.items() if k != "_def"}
            elif live:
                nodes[gate["id"]]["parked"] = {"kind": "timer" if not gate["wait"].get("until_argv") else "check", "attempt": 0}
            gate = None
        if gate and gate_answer_valid(r, gate, byid) is None:
            try:
                cond = when_true(gate, outputs)
                held = {"id": gate["id"], "question": gate.get("question"),
                        "options": gate.get("options"), "context": gate.get("context")}
            except Exception as e:
                # Fail-safe law applies to the READ MODEL too: a broken 'when'
                # shows as HELD (with the error surfaced), never a silent skip —
                # and NEVER raises into status/wait/list/release/stop/dashboard.
                cond = True
                held = {"id": gate["id"], "question": gate.get("question"),
                        "options": gate.get("options"), "context": gate.get("context"),
                        "when_error": str(e)}
            if cond:
                status = "held"
            else:
                held = None
        elif not (r / "events.jsonl").exists() and not (r / "wf.pid").exists():
            status = "pending"
    # P1: nearest unfinished ancestors with their state, derived here, never stored.
    meta = {}
    for n in graph["nodes"]:
        nid = n["id"]
        if held and held.get("id") == nid:
            meta[nid] = {"held": True}
        elif nodes[nid].get("parked"):
            meta[nid] = {"parked": nodes[nid]["parked"]}
        elif states[nid] == "pending" and n["type"] == "agent" and deps_ok(n) and nodes[nid].get("active_spawn"):
            meta[nid] = {"running": True}
    for n in graph["nodes"]:
        if states[n["id"]] == "pending" and not deps_ok(n):
            nodes[n["id"]]["blocked_by"] = blocked_by(n, states, meta)
    exit_state = runner_exit_read(r)
    if status == "interrupted" and str((exit_state or {}).get("reason", "")).startswith("crashed:"):
        status = "failed"  # a recorded fatal error needs an amend, not a wait/respawn loop
    return {"run_id": r.name, "name": graph.get("name"), "status": status,
            "held_gate": held, "nodes": nodes, "graph": graph,
            "runner_exit": exit_state,
            "started": (jload(r / "run.json", {}) or {}).get("started"),
            "owner": (jload(r / "run.json", {}) or {}).get("owner"),
            "done": sum(1 for s in states.values() if s in ("done", "skipped")),
            "skipped": sum(1 for s in states.values() if s == "skipped"), "total": len(graph["nodes"])}

def run_summary(runs):
    """Counts cover the complete census, even when a caller returns a recent page."""
    counts = {"running": 0}
    for run in runs:
        status = run["status"]
        counts[status] = counts.get(status, 0) + 1
    return {"total": len(runs), "counts": counts}

# ---------- amend preview (the replay-skip law the runner applies, computed ahead) ----------

def _downstream(byid):
    kids = {i: [] for i in byid}
    for n in byid.values():
        for a in n.get("after", []):
            if a in kids:
                kids[a].append(n["id"])
    return kids

def amend_preview(r, new_nodes):
    """{added, removed, changed, will_rerun, unchanged} for a proposed graph
    against the run dir's committed graph and node records. Added nodes are work;
    changed committed records plus their downstream nodes also rerun. Unchanged
    done records replay-skip. Other never-committed nodes stay out unless they
    descend from added/changed work. Read-only."""
    old_nodes = (jload(r / "graph.json", {}) or {}).get("nodes", [])
    old_ids = {n["id"] for n in old_nodes
               if isinstance(n, dict) and isinstance(n.get("id"), str)}
    byid = {n["id"]: n for n in new_nodes}
    new_ids = set(byid)
    added = [n["id"] for n in new_nodes if n["id"] not in old_ids]
    removed = [n["id"] for n in old_nodes
               if isinstance(n, dict) and isinstance(n.get("id"), str)
               and n["id"] not in new_ids]
    kids = _downstream(byid)
    status, committed_mismatch = {}, set()
    for n in new_nodes:
        st, rec = node_rec(r, n, byid)
        status[n["id"]] = st
        if st == "pending" and (rec or {}).get("status") in ("done", "failed", "skipped"):
            committed_mismatch.add(n["id"])  # committed but efp-stale
    changed = sorted(committed_mismatch)
    will = set()
    stack = changed + added
    while stack:
        x = stack.pop()
        if x in will:
            continue
        will.add(x)
        stack.extend(kids.get(x, []))
    will_rerun = [n["id"] for n in new_nodes if n["id"] in will]
    unchanged = [n["id"] for n in new_nodes
                 if status[n["id"]] in ("done", "skipped") and n["id"] not in will]
    return {"added": added, "removed": removed, "changed": changed,
            "will_rerun": will_rerun, "unchanged": unchanged}

# ---------- live child metrics (state.db join) ----------
# Children run with `--continue wf:<run>:<node>[:<i>]:<efp8>#a<attempt>`, so each child's
# sessions row carries that key as its title. One read-only query per view returns every
# row for the run; rows fold per node/item across attempts. Deterministic liveness: a
# running child's api_call_count / tool_call_count / last_activity_at move while it cooks.
_METRIC_COLS = ("input_tokens", "output_tokens", "cache_read_tokens", "reasoning_tokens",
                "api_call_count", "tool_call_count", "estimated_cost_usd")

def child_metrics(run_id, home=None):
    """{skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls, cost,
    model, last_activity, last_desc, attempts, ended}} for every child of the run, or {}."""
    import os, sqlite3
    home = Path(home or os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))
    db = home / "state.db"
    if not db.exists():
        return {}
    out = {}
    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=0.5)
        try:
            rows = c.execute(
                "select title, model, input_tokens, output_tokens, cache_read_tokens, reasoning_tokens, "
                "api_call_count, tool_call_count, estimated_cost_usd, last_activity_at, "
                "last_activity_description, ended_at, started_at from sessions where title like ? "
                "order by title, started_at, rowid",
                (f"wf:{run_id}:%",)).fetchall()
        finally:
            c.close()
    except Exception:
        return {}
    for (title, model, ti, to, cr, rs, api, tools, cost, last, desc, ended, started) in rows:
        key = title.split("#a", 1)[0]
        m = out.setdefault(key, {"tokens_in": 0, "tokens_out": 0, "cache_read": 0, "reasoning": 0,
                                 "api_calls": 0, "api_calls_known": True,
                                 "tool_calls": 0, "cost": 0.0, "attempts": 0,
                                 "model": None, "last_activity": None, "last_desc": None,
                                 "ended": None, "started": None, "sessions": {}})
        m["sessions"][title] = {"last_activity": last or started,
                                "last_desc": desc or None}
        if api is None:
            m["api_calls_known"] = False
        m["tokens_in"] += ti or 0; m["tokens_out"] += to or 0; m["cache_read"] += cr or 0
        m["reasoning"] += rs or 0; m["api_calls"] += api or 0; m["tool_calls"] += tools or 0
        m["cost"] += cost or 0.0; m["attempts"] += 1
        m["model"] = model or m["model"]
        la = last or started
        if la and (m["last_activity"] is None or la > m["last_activity"]):
            m["last_activity"], m["last_desc"] = la, desc or None
        if m["started"] is None or (started and started < m["started"]):
            m["started"] = started
        m["ended"] = (ended if m["attempts"] == 1 else
                      max(m["ended"], ended) if m["ended"] is not None and ended is not None else None)
    return out

def current_attempt(cm, spawns):
    """Activity only for verified spawn session titles; DB rows alone prove no liveness."""
    live = {}
    for spawn in spawns:
        title = (spawn or {}).get("skey")
        if title:
            live[title] = cm.get(title.split("#a", 1)[0], {}).get("sessions", {}).get(title, {})
    recent = [(row["last_activity"], title, row.get("last_desc"))
              for title, row in live.items() if row.get("last_activity") is not None]
    last, _, desc = max(recent) if recent else (None, None, None)
    return {"live": len(live), "last_activity": last, "last_desc": desc}
