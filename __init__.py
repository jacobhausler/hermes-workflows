"""hermes-workflows plugin — the `workflow` tool: agent-owned graph runs.

The engine (wf.py) is a separate process per run; this module is the door:
launch it, read its run-dir via the SHARED read model (wfcommon.run_state), drop
its input files. No daemon, no control plane, no second opinion on run state.
"""
import importlib.util, json, os, re, shutil, stat, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

# Bind our sibling by path, never another plugin's already-imported wfcommon.
_COMMON_PATH = Path(__file__).resolve().parent / "wfcommon.py"
_spec = importlib.util.spec_from_file_location("_hermes_workflows_wfcommon", _COMMON_PATH)
_common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_common)
run_state = _common.run_state
validate_graph = _common.validate_graph
validate_graph_errors = _common.validate_graph_errors
efp = _common.efp
jload = _common.jload
amend_preview = _common.amend_preview
quote_json_parse_error = _common.quote_json_parse_error

def _coerce_graph(graph):
    """The door only ever sees `graph` as a parsed object from the tool schema, but a
    model CAN hand the string form; parse it and, on malformed JSON, quote ±40 chars
    around the error offset. Returns (graph_or_None, error_response_or_None)."""
    if isinstance(graph, str):
        try:
            graph = json.loads(graph)
        except json.JSONDecodeError as e:
            return None, {"error": f"graph is not valid JSON: {e}",
                          "near": "…" + quote_json_parse_error(graph, e) + "…"}
    if not isinstance(graph, dict):
        return None, {"error": "graph must be an object {name, nodes:[...]}"}
    return graph, None

GRAPH_MAX_BYTES = 1024 * 1024
GRAPH_KEYS = {"name", "nodes", "description", "defaults"}

def _input_graph(args, *, run_id=False, library=False):
    """Choose one explicitly supplied source; never discover files on the caller's behalf."""
    supplied = [key for key in ("graph", "graph_path") if args.get(key) is not None]
    supplied += [key for key, enabled in (("run_id", run_id), ("from", library))
                 if enabled and args.get(key)]
    if len(supplied) > 1:
        return None, {"error": f"choose one graph source, not {', '.join(supplied)}"}
    if args.get("graph_path") is not None:
        path = args["graph_path"]
        if not isinstance(path, str) or not path or not os.path.isabs(path):
            return None, {"error": "graph_path must be an absolute local file path"}
        try:
            # O_NONBLOCK makes a hostile FIFO/device non-blocking; fstat checks the
            # opened descriptor, not a path that could be replaced between checks.
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as source:
                info = os.fstat(source.fileno())
                if not stat.S_ISREG(info.st_mode):
                    return None, {"error": "graph_path must name a regular file"}
                if info.st_size > GRAPH_MAX_BYTES:
                    return None, {"error": f"graph_path exceeds {GRAPH_MAX_BYTES} bytes"}
                raw = source.read(GRAPH_MAX_BYTES + 1)
            if len(raw) > GRAPH_MAX_BYTES:
                return None, {"error": f"graph_path exceeds {GRAPH_MAX_BYTES} bytes"}
            graph = raw.decode("utf-8")
        except (OSError, UnicodeError) as e:
            return None, {"error": f"graph_path cannot be read as UTF-8 JSON: {e}"}
        return _coerce_graph(graph)
    if args.get("graph") is not None:
        return _coerce_graph(args["graph"])
    return None, None

def _validation_error(graph):
    """Return graph-level and node-level defects together, before any write/spawn."""
    errs = []
    for key in sorted(set(graph) - GRAPH_KEYS):
        errs.append({"node": None, "field": key,
                     "msg": f"unknown graph key; allowed: {sorted(GRAPH_KEYS)}"})
    if "defaults" in graph:
        # ONE truth: the same per-key rules a node key gets; apply_graph_defaults
        # bakes this block into the agent defs before graph.json is written.
        errs.extend(_common._defaults_errors(graph["defaults"]))
    for key in ("name", "description"):
        if key in graph and (not isinstance(graph[key], str) or not graph[key].strip()):
            errs.append({"node": None, "field": key, "msg": f"{key} must be a non-empty string"})
    nodes = graph.get("nodes")
    # The shared validator assumes hashable ids and iterable dependency lists.
    # Normalize only those invalid shapes in a copy, collecting their errors while
    # still letting the shared validator report unrelated defects in the same call.
    safe = [] if isinstance(nodes, list) else nodes
    if isinstance(nodes, list):
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                safe.append(node)  # shared validator identifies the first non-object
                continue
            item = dict(node)
            nid = node.get("id")
            if isinstance(nid, (dict, list)):
                errs.append({"node": None, "field": f"nodes[{index}].id",
                             "msg": "node id must be a string"})
                item["id"] = f"__invalid_id_{index}__"
            deps = node.get("after", [])
            if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
                errs.append({"node": nid if isinstance(nid, str) else None,
                             "field": "after", "msg": "after must be a list of node id strings"})
                item["after"] = []
            safe.append(item)
    errs.extend(validate_graph_errors(safe))
    if not errs:
        return None
    first = errs[0]
    head = first["msg"] if first["node"] is None else f"node {first['node']}: {first['msg']}"
    return {"error": f"graph invalid: {head}", "errors": errs}

HERE = Path(__file__).resolve().parent

def _hermes_bin():
    """Absolute launcher path — background runners do NOT inherit an interactive PATH."""
    w = shutil.which("hermes")
    if w:
        return w
    for c in (Path.home() / ".local/bin/hermes", runs_root().parent / ".local/bin/hermes",
              Path("/usr/local/bin/hermes"), Path("/opt/hermes/bin/hermes")):
        if c.exists():
            return str(c)
    return "hermes"

runner_alive = _common.runner_alive

def _spawn_runner(r):
    """Append mode: runner.log keeps crash diagnostics across respawns.
    Stamp wf.pid ourselves — the door never races the runner's own pid write.
    Single-runner admission is enforced by the runner's flock (kernel-owned) admission lock, so racing
    door spawns are harmless (the loser exits WORKFLOW_BUSY)."""
    log = open(r / "runner.log", "a")
    proc = subprocess.Popen([sys.executable, str(HERE / "wf.py"), "run", r.name],
                            stdout=log, stderr=log, stdin=subprocess.DEVNULL,
                            start_new_session=True, cwd=str(HERE))
    (r / "wf.pid").write_text(str(proc.pid))

# ---------- tool schema ----------

WORKFLOW_PARAMS = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["run", "status", "wait", "release", "steer", "inbox", "amend", "stop", "list", "save", "library"],
            "description": "run=launch a graph; wait=read state, RESPAWNING an idle runner if work is pending (blocks to the next boundary when one is live); status=read-model of a run; release=answer a held human gate; steer=queue steering text for a node; inbox=(child-side, cooperative) pull late steering lines baked for THIS spawn — call once at a natural seam; amend=replace the graph (invalidates changed nodes + all downstream by fingerprint); stop=request stop; list=all runs; save=shelve a graph in the library under a name (from run_id or inline graph); library=list shelved graphs. run from=<name> replays a shelved graph.",
        },
        "run_id": {"type": "string", "description": "Run id (required for every action except run/list)."},
        "name": {"type": "string", "description": "run: overrides graph.name (default workflow); save: library name overrides graph.name (lowercase, [-_.]). amend: set graph.name in the replacement graph; omitting it retains the run name."},
        "from": {"type": "string", "description": "run: library graph name to replay (instead of graph or graph_path)."},
        "description": {"type": "string", "description": "save: one-line purpose shown by library/list."},
        "graph_path": {"type": "string", "description": "run/save/amend: absolute path to a caller-supplied local regular UTF-8 JSON graph file (max 1 MiB, no final symlink). Choose exactly one of graph, graph_path, or run's from / save's run_id. Validated before any write or spawn."},
        "graph": {
            "type": "object",
            "description": "For run/amend: {name, nodes:[...], defaults:{schema, timeout, max_turns, reasoning, provider, model, context}} where `defaults` fills agent node keys the author left unset (explicit node keys always win; defaults.context is the shared preamble prepended once to each agent's own context) and where node = {id, type:'agent'|'gate'|'echo', after:[node ids], goal, context, schema (json-schema for child output), model, provider (optional explicit Hermes provider paired with model; passed as --provider; when unset it is INHERITED from a provider-qualified model alias/tier), toolsets, max_turns, timeout (s wall-clock kill, default 900), shape (recon|build|review|publish — fills max_turns/timeout from the measured p95 census presets when the author left them unset; explicit keys win), run_budget (s, child's own budget), reasoning (a hermes reasoning effort: none|minimal|low|medium|high|xhigh|max|ultra — passed to the child as --reasoning; levels are validated PER ROUTE at the door against the resolved (provider, model) route's supported set, with the supported list and nearest level in the error — no silent downgrade), inputs:['<ancestor>' | '<ancestor>.<dotted.path>', ...] (inject a committed upstream output into the prompt as a labelled json block under '## Inputs'; unresolvable ref fails the node at spawn; DIRECT parents from `after` are auto-injected capped at 8KB with a truncation marker — use inputs only to pick a dotted path or a non-parent ancestor; a parent listed in both appears once), fanout:{items | items_from:'<node_id>.<dotted.path>', goal (OPTIONAL template; an item's own `goal` key overrides it — when items carry their own goals the shared node goal prefixes each item prompt, so no placeholder template is ever needed), schema, quorum (default = majority, floor(n/2)+1; once quorum is reached the remaining stragglers are cancelled with error_class 'cancelled' and excluded from the failure math)}} — agent node. A provider requires a non-empty model; model aliases and literal IDs are preserved (tiers resolve explicitly, and a matching provider/model prefix is removed for the CLI). Run/amend responses include requested/resolved provider/model routes. Gate node: {id, type:'gate', after, question, options, context, when (bounded expr: out.<node>.<dotted.path> with == != > >= < <=, and/or/not, parens; malformed when is rejected at run/amend validation and holds the gate at fire — never a silent skip), wait:{wait_s, until_argv:[fixed argv, no shell], every_s (default 60), timeout_s (default 3600)} (machine-answered gate: parks the run at zero tokens — wait_s alone = timer; until_argv re-runs until exit 0; timeout → gate fails; its last stdout/stderr tail is the gate's output, usable via inputs). A human release pre-empts a park), on_skip:'pass'|'prune' (with when: prune commits the gate `skipped` and every node whose deps are ALL skipped is skipped too — terminal, not a failure; a join with one live dep runs; default pass = the arm still runs)}. Echo node: {id, type:'echo', after, output} — commits its `output` verbatim as the node result with zero tokens and no child spawn; downstream nodes consume it via after/inputs like any done node. Any key outside these closed sets is rejected at run/amend with errors:[{node, field, msg}] for EVERY defect.",
        },
        "answer": {"type": "string", "description": "release: the human's answer text (from clarify)."},
        "gate_id": {"type": "string", "description": "release: gate node id."},
        "node": {"type": "string", "description": "steer: target node id (pending node picks it up at spawn; a LIVE child pulls it at its next seam via its own inbox call — the prompt is never rewritten)."},
        "text": {"type": "string", "description": "steer: the steering message."},
        "dry_run": {"type": "boolean", "description": "amend: true = validate + preview {added, removed, changed, will_rerun, unchanged} ONLY — nothing is written, the runner is not touched. Normal amends echo the same lists."},
        "timeout": {"type": "number", "description": "wait: max seconds to block while a runner is live (default 600, capped 1800). Self-yields ~330s segments under the harness tool deadline with status+note — call wait again until terminal."},
        "detail": {"type": "string", "enum": ["full"], "description": "status/wait: 'full' attaches every committed node output and full spawn argv; the default is compact — mid-run waits carry output pointers (keys+bytes) only, terminal payloads always include outputs."},
        "hermes_bin": {"type": "string", "description": "run: override the child launcher binary (advanced/testing; default auto-resolved 'hermes')."},
    },
    "required": ["action"],
}

# Registry shape = {description, parameters}; a bare JSON-schema object registers fine but
# tool_describe reads fn["parameters"] and hands the model {} (papercut 2026-09-22).
WORKFLOW_SCHEMA = {
    "description": (
        "Multi-agent workflow graphs: run a DAG of agent/gate nodes (fan-out, human gates, replay-skip resume, "
        "steering, amend, per-node model tiers) as a background runner owned by this session. "
        "Argument shapes are in parameters; the `workflow` skill has the grammar and examples."
    ),
    "parameters": WORKFLOW_PARAMS,
}

# ---------- model tiers ----------
# User-owned vocabulary: plugins.entries.hermes-workflows.settings.models is a dict
# {tier: model} with ARBITRARY keys ("worker"/"frontier", "1".."5", whatever the
# owner thinks in). node.model accepts a literal model id OR one of those keys.
# Resolution happens HERE at run/amend and the literal is BAKED into the node def:
# it lands in the fingerprint (replay-deterministic), run.json shows what actually
# ran, and remapping a tier later never retroacts onto a live run. A provider field
# is kept explicit and passed to the CLI; no model id is rewritten to an alias.
# Unknown tier keys fail-closed with the valid list.
_CTX = None

def model_tiers():
    tiers = {}
    try:
        tiers = _CTX.get_config("models", {}) if _CTX else {}
    except Exception:
        tiers = {}
    return {str(k): str(v) for k, v in (tiers or {}).items() if v}

_PREFLIGHT_NOT_LIVENESS = ("preflight proves RESOLUTION, not liveness — a literal model id "
                           "is never checked for reachability and is left as-is.")

import difflib

def _route_efforts(provider, model):
    """Reasoning levels the (provider, model) route accepts; the global set when the
    route is unknown or core is not importable (bare CLI / non-core hosts)."""
    if provider or model:
        try:
            from agent.reasoning_effort import route_supported_efforts
            sup = tuple(route_supported_efforts(provider, model))
            if sup:
                return sup
        except Exception:
            pass
    return _common.reasoning_levels()

def _nearest_effort(level, supported):
    """Nearest supported ladder level (weaker first — never an escalation), or None."""
    try:
        from agent.reasoning_effort import EFFORT_LADDER
    except Exception:
        return None
    if level not in EFFORT_LADDER:
        return None
    idx = EFFORT_LADDER.index(level)
    pool = [l for l in supported if l in EFFORT_LADDER and l != "none"]
    below = [l for l in pool if EFFORT_LADDER.index(l) < idx]
    if below:
        return max(below, key=EFFORT_LADDER.index)
    above = [l for l in pool if EFFORT_LADDER.index(l) > idx]
    return min(above, key=EFFORT_LADDER.index) if above else None

def _alias_provider_pair(requested, seat_raw, tiers, known_names=()):
    """(provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat
    aliases/tier targets and the core model_aliases (DIRECT_ALIASES) table; provider None
    when the target is bare (the seat default route stays authoritative), model = the
    bare target itself so the reasoning route table still speaks the real model id.
    Names the SEAT already owns (seat aliases/default/tiers) never consult the core
    table — the seat config is authoritative for its own names."""
    name = str(requested or "").strip()
    for target in ((dict((seat_raw or {}).get("aliases") or {}).get(name) or "").strip(),
                   str((tiers or {}).get(name) or "").strip()):
        if "/" in target:
            p, _, m = target.partition("/")
            if p.strip() and m.strip():
                return p.strip(), m.strip()
        elif target:
            return None, target
    if name.lower() in {str(k).strip().lower() for k in known_names}:
        return None, None
    try:
        from hermes_cli.model_switch import _ensure_direct_aliases, DIRECT_ALIASES
        _ensure_direct_aliases()
        da = DIRECT_ALIASES.get(name.lower())
        if da and da.provider and da.model:
            return da.provider, da.model
    except Exception:
        pass
    return None, None

def model_preflight(requests, tiers, seat_raw):
    """Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time
    after the route table is computed and before the first wave (spawn).

    Every requested name that claims to be an alias must resolve to a non-empty target
    in the SAME seat config the CLI uses (``seat_raw`` = the unfiltered
    ``{"default", "aliases"}``); an empty/blank target resolves to nothing and is
    REJECTED, listing which nodes share the dead model. Tier keys were already resolved
    against a non-empty target by ``model_tiers()`` (empty targets are filtered there,
    which makes such a key surface as an unknown model). Literal ids pass through: this
    proves RESOLUTION, not liveness — a literal model id is never checked for
    reachability and is left as-is. The error text states this verbatim.

    `requests` = [(node_id, requested_model, provider), ...]; the tail of
    ``_resolve_models`` passes the extended shape (..., node, eff_provider,
    eff_model) so the PER-ROUTE reasoning check validates the resolved route
    (inherited provider included) without a second resolution pass. Returns an
    error string or None. Exactly one call site (no duplicate resolution logic).
    """
    aliases = dict((seat_raw or {}).get("aliases") or {})
    default = (seat_raw or {}).get("default")
    dead = {}
    route_errs = []
    for req in requests:
        nid, m, _provider = req[0], req[1], req[2]
        node = req[3] if len(req) > 3 else None
        if not m:
            continue
        if m in aliases and not str(aliases[m]).strip():
            dead.setdefault(m, []).append(nid)
        if node is not None:
            lv = node.get("reasoning")
            pp = req[4] if len(req) > 4 else node.get("provider")
            mm = req[5] if len(req) > 5 else node.get("model")
            if lv and (mm or pp):
                sup = _route_efforts(pp, mm)
                if lv not in sup:
                    near = _nearest_effort(lv, sup)
                    route = f"{pp}/{mm}" if pp and mm else (pp or mm)
                    suggest = (f" — nearest supported level: {near!r}" if near else "")
                    route_errs.append(
                        f"node {nid!r}: reasoning {lv!r} is not supported by route {route!r} "
                        f"(supported: {list(sup)}){suggest} — pick a supported level; the door "
                        f"never silently downgrades reasoning.")
    if dead:
        listed = "; ".join(f"{m!r} (nodes: {', '.join(ids)})" for m, ids in sorted(dead.items()))
        return (f"model preflight: {listed} — dead seat alias: the name resolves to nothing "
                f"(empty alias target in the seat config). Fix the seat's model.aliases or "
                f"repoint these nodes. Note: {_PREFLIGHT_NOT_LIVENESS}")
    if route_errs:
        return "model preflight: " + " | ".join(route_errs)
    return None

def _resolve_models(nodes) -> tuple[str | None, dict | None, dict | None]:
    """Resolve tier keys in place and return (error, model_table, routes).

    Explicit aliases and literal ids stay unchanged. If a provider is supplied and the
    model is prefixed by that same provider, strip the redundant prefix for the CLI's
    ``-m`` value. `routes` contains requested and effective provider/model pairs only;
    no credentials or config values. At the tail, the FEEDBACK #43 ``model_preflight``
    rejects names that resolve to nothing (fail-closed at submit, never at spawn).
    """
    tiers = model_tiers()
    table, routes = {}, {}
    known = set(_seat_aliases()) | ({_seat_default()} - {None})
    requests = []
    for n in nodes:
        if n.get("type") in ("gate", "echo"):
            continue
        requested_model = n.get("model")
        provider = n.get("provider")
        m = requested_model
        tier = None
        display = "(seat default)"
        if not m:
            pass
        elif m in tiers:
            tier = m
            n["model"] = m = tiers[m]
            n["tier"] = tier
        elif "/" in m or m in known or provider:
            pass
        else:
            near = difflib.get_close_matches(m, sorted(set(tiers) | known), n=3)
            hint = f" — did you mean {near}?" if near else ""
            return (f"node {n['id']!r}: unknown model {m!r}{hint} — not a tier, alias, or "
                    f"provider/model id; tiers: {sorted(tiers)}; aliases: {sorted(known)}", None, None)
        # provider INHERITED from the model's alias when the node sets model but not
        # provider: a 'provider/model'-prefixed seat alias, a tier target, or a core
        # model_aliases entry carries its own route (the 19 "model X not supported when
        # using Codex" provider_400s were nodes that left provider unset). [N]-tier: the
        # author never writes the provider the alias already names. The model string
        # itself stays verbatim (house contract: aliases are preserved); only the
        # provider is baked so the runner's --provider matches the alias's own route.
        ip = im = None
        if m and not provider and (tier or m in known):
            ip, im = _alias_provider_pair(requested_model, _seat_model_cfg(), tiers, known)
            if ip:
                n["provider"] = ip
        eff_provider = provider or ip
        if m and provider:
            prefix, sep, remainder = m.partition("/")
            if sep and prefix == provider and remainder:
                n["model"] = m = remainder
        if m:
            # display: author-explicit provider names the route (base semantics);
            # an inherited provider shows in `routes` only.
            display = f"{provider}/{m}" if provider else str(m)
            if tier:
                display += f"  ({tier})"
        table[n["id"]] = display
        routes[n["id"]] = {
            # requested = what the AUTHOR wrote (an inherited provider is not a request);
            # resolved = the effective route (node def after resolution, base semantics).
            "requested": {"provider": provider or None, "model": requested_model or None},
            "resolved": {"provider": n.get("provider") or None, "model": n.get("model") or None},
        }
        # route for the PER-ROUTE reasoning check: the alias/tier TARGET's model when the
        # name is an alias (the CLI resolves it; the route table speaks the real model id),
        # else the baked literal.
        requests.append((n["id"], requested_model, provider, n,
                         eff_provider, (im if (tier or m in known) and im else m)))
    pf_err = model_preflight(requests, tiers, _seat_model_cfg())
    if pf_err:
        return pf_err, None, None
    return None, table, routes

def resolve_models(nodes):
    """Compatibility wrapper: resolve models and return the historical (error, table) pair."""
    err, table, _routes = _resolve_models(nodes)
    return err, table

def _seat_model_cfg():
    """The seat's `model:` block ({default, aliases}) — hermes_cli when importable, else a
    stdlib-only read of config.yaml (tests, bare CLI: no hermes_cli, maybe no PyYAML)."""
    try:
        from hermes_cli.config import load_config_readonly
        cfg = load_config_readonly()
        if cfg:
            mc = cfg.get("model") or {}
            al = {str(k): (v if isinstance(v, str) else (v or {}).get("model") or "") for k, v in (mc.get("aliases") or {}).items()}
            # Keep EMPTY targets in what we return: the FEEDBACK #43 preflight must see an
            # alias that declares itself but resolves to nothing. Resolution consumers
            # derive their known-name sets via _seat_model_names(), which filters there.
            return {"default": str(mc["default"]) if mc.get("default") else None, "aliases": al}
    except Exception:
        pass
    out = {"default": None, "aliases": {}}
    try:
        home = os.environ.get("HERMES_HOME") or (Path.home() / ".hermes")
        section = None; in_aliases = False
        for line in (Path(home) / "config.yaml").read_text().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            key, _, val = line.strip().partition(":")
            if indent == 0:
                section, in_aliases = key, False
                continue
            if section != "model":
                continue
            if indent == 2:
                in_aliases = key == "aliases"
                if key == "default" and val.strip():
                    out["default"] = val.strip().strip("'\"")
            elif indent > 2 and in_aliases and val.strip():
                out["aliases"][key.strip()] = val.strip().strip("'\"")
    except Exception:
        pass
    return out

def _seat_aliases():
    return _seat_model_cfg()["aliases"]

def _seat_default():
    return _seat_model_cfg()["default"]

def _seat_model_names():
    """Names the seat itself resolves for -m: model aliases + the default model."""
    return set(_seat_aliases()) | ({_seat_default()} - {None})

# ---------- run-dir plumbing ----------

def runs_root():
    home = os.environ.get("HERMES_HOME") or (Path.home() / ".hermes")
    return Path(home) / "workflows"

def run_dir(run_id):
    """Strict: no silent normalization — ids double as directory names."""
    rid = (run_id or "").strip()
    if not rid or rid != "".join(c for c in rid if c.isalnum() or c in "-_.") \
            or rid.startswith(".") or set(rid) == {"."}:
        raise ValueError(f"invalid run_id {run_id!r}")
    return runs_root() / rid

# ---------- graph library (named, re-runnable graphs) ----------

def library_root():
    return runs_root() / "library"

LIB_OK = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")

def _lib_path(name):
    n = str(name or "").strip().lower()
    if not LIB_OK.match(n):
        raise ValueError(f"invalid library name {name!r} (lowercase alnum, [-_.], <=64)")
    return library_root() / f"{n}.json"

def act_save(args):
    """Shelve a graph under a name: from an existing run (`run_id`) or an inline `graph`.
    Overwrites — a library entry is the CURRENT best version of that graph."""
    graph, bad = _input_graph(args, run_id=True)
    if bad:
        return bad
    if graph is None and args.get("run_id"):
        graph = jload(run_dir(args["run_id"]) / "graph.json")
    if graph is None:
        return {"error": "save needs graph, graph_path or run_id of an existing run"}
    bad = _validation_error(graph)
    if bad:
        return bad
    try:
        p = _lib_path(args.get("name") or graph.get("name"))
    except ValueError as e:
        return {"error": str(e)}
    p.parent.mkdir(parents=True, exist_ok=True)
    graph = dict(graph, name=p.stem)
    if args.get("description"):
        graph["description"] = args["description"]
    p.write_text(json.dumps(graph, ensure_ascii=False, indent=2))
    return {"saved": p.stem, "nodes": len(graph["nodes"]),
            "hint": f"re-run any time: workflow run from={p.stem}  |  /wf {p.stem}"}

def act_library(_args):
    root = library_root()
    out = []
    if root.exists():
        for p in sorted(root.glob("*.json")):
            g = jload(p) or {}
            nodes = g.get("nodes") or []
            out.append({"name": p.stem, "nodes": len(nodes),
                        "gates": sum(1 for n in nodes if n.get("type") == "gate"),
                        "fanouts": sum(1 for n in nodes if n.get("fanout")),
                        "description": g.get("description")})
    return {"library": out, "hint": "workflow run from=<name> replays one; workflow save graph=... shelves a new one"}

# ---------- actions ----------

def _session_env(name):
    """Use the tool worker's task-local session, not another turn's process env."""
    try:
        from gateway.session_context import get_session_env
    except ImportError:  # standalone plugin host without Hermes gateway
        return os.environ.get(name, "")
    return get_session_env(name, "")

def _card(rid):
    return f'::workflow{{id="{rid}"}}'

def act_run(args):
    graph, bad = _input_graph(args, library=True)
    if bad:
        return bad
    if graph is None and args.get("from"):
        try:
            graph = jload(_lib_path(args["from"]))
        except ValueError as e:
            return {"error": str(e)}
        if graph is None:
            return {"error": f"no library graph named {args['from']!r}",
                    "library": [x["name"] for x in act_library({})["library"]]}
    if graph is None:
        return {"error": "run needs graph, graph_path or from=<library name>"}
    bad = _validation_error(graph)
    if bad:
        return bad
    name = args.get("name", graph.get("name", "workflow"))
    if not isinstance(name, str) or not name.strip():
        return {"error": "run name must be a non-empty string"}
    graph = dict(graph, name=name)
    # Bake `defaults` + shape presets into the node defs BEFORE graph.json: the
    # runner and every fingerprint then see ONE resolved truth (#8/#11).
    try:
        graph = _common.apply_graph_defaults(graph)
    except ValueError as e:
        return {"error": f"graph invalid: defaults/shape: {e}"}
    err, models, routes = _resolve_models(graph["nodes"])
    if err:
        return {"error": err}
    assert models is not None and routes is not None
    base = time.strftime("%Y%m%d-%H%M%S") + "-" + "".join(
        c for c in name.lower() if c.isalnum() or c in "-_")[:24]
    rid, n = base, 0
    root = runs_root()
    root.mkdir(parents=True, exist_ok=True)
    while True:  # collision-resistant exclusive create
        r = root / (rid if n == 0 else f"{rid}-{n}")
        try:
            (r / "nodes").mkdir(parents=True, exist_ok=False)
            rid = r.name
            break
        except FileExistsError:
            n += 1
    (r / "gates").mkdir(exist_ok=True)
    (r / "graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2))
    meta = {"name": graph.get("name", "workflow"), "hermes_bin": args.get("hermes_bin") or _hermes_bin(),
            "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            # OWNER = the agent session that spawned the run. The desktop uses it to
            # route a UI gate answer back to THIS chat (host.openSession + hidden turn),
            # never to whichever chat happens to be open. Env is the only truth the
            # tool handler has; absent (tests, CLI) => no owner => UI falls back.
            "owner": {"session_id": _session_env("HERMES_SESSION_ID") or None,
                      "ui_session_id": _session_env("HERMES_UI_SESSION_ID") or None,
                      "platform": _session_env("HERMES_SESSION_PLATFORM") or None}}
    (r / "run.json").write_text(json.dumps(meta))
    _spawn_runner(r)
    return {"run_id": rid, "models": models, "routes": routes, "hint":
            # Copy-exact inducement (papercut #70): the hint IS the paste line —
            # no paraphrase, no fallback. The card is agent-authored by ruling.
            f'PASTE this line alone in your reply, then call wait: {_card(rid)}',
            "card": _card(rid)}

def _steer_event(r, ev, **kw):
    """#17: steer is only real if it lands in events.jsonl — the 45 real steers
    across 16 runs that were invisible are the bug being fixed."""
    with open(r / "events.jsonl", "a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "event": ev, **kw}, ensure_ascii=False) + "\n")

_steer_state = _common._steer_state  # O2 re-export alias (moved to wfcommon): act_status keeps resolving via the door; bound via _common so a foreign `wfcommon` on sys.path can never hijack it

def _output_pointer(rec):
    """Compact stand-in for a committed node output: enough to DECIDE to pay for
    detail=full (shape + size + where the bytes live), never the bytes."""
    out = rec.get("output")
    try:
        size = len(json.dumps(out, ensure_ascii=False))
    except (TypeError, ValueError):
        size = -1
    keys = sorted(out.keys())[:12] if isinstance(out, dict) else (
        [f"items:{len(out)}"] if isinstance(out, list) else [type(out).__name__])
    return {"output_ptr": "nodes (detail=\"full\")", "output_keys": keys, "output_bytes": size}

def act_status(args):
    r = run_dir(args.get("run_id"))
    st = run_state(r)
    if not st:
        return {"error": f"no run at {r}"}
    full = str(args.get("detail") or "").lower() == "full"
    alive = runner_alive(r)
    out = {"run_id": st["run_id"], "name": st["name"], "status": st["status"],
           "runner_live": alive, "nodes": {k: {kk: v[kk] for kk in ("type", "status", "fanout")}
                                           for k, v in st["nodes"].items()},
           "done": st["done"], "skipped": st["skipped"], "total": st["total"],
           # O1: the card to paste into the report rides on EVERY status (and via
           # act_wait, every wait) — the inducement never depends on the agent recalling it.
           "card": _card(st["run_id"])}
    # Tier self-report (2026-09-24): a failed child's core -Q turn report carried
    # its typed verdict key ("typed") or not ("untyped"); absent = never noted.
    tier_rec = jload(r / "turn_report.tier")
    if isinstance(tier_rec, dict) and tier_rec.get("tier"):
        out["turn_report"] = str(tier_rec["tier"])
    if st.get("runner_exit"):
        out["runner_exit"] = st["runner_exit"]  # <run>/runner_exit.json or the dead-pid crash note
    if st["held_gate"]:
        out["gate"] = st["held_gate"]
    for nid, v in st["nodes"].items():
        rec = jload(r / "nodes" / f"{nid}.json")
        if v.get("active_spawn"):
            def _trim(sp):
                return sp if full else {k: x for k, x in sp.items()
                                        if k not in ("argv", "spawn_cmd")}
            out["nodes"][nid]["active_spawn"] = _trim(v["active_spawn"])
            out["nodes"][nid]["active_spawns"] = [_trim(sp) for sp in v.get("active_spawns") or []]
        if v.get("blocked_by"):
            out["nodes"][nid]["blocked_by"] = v["blocked_by"]
        if v.get("parked"):
            out["nodes"][nid]["parked"] = v["parked"]
        sm = _steer_state(r, nid)
        if sm:
            out["nodes"][nid]["steer"] = sm
        # mid-run repeat waits were re-shipping every committed output each tick
        # (feedback #76: 91% of a real wait payload). Terminal payload always full;
        # running payload compact unless detail=full.
        show_out = full or st["status"] not in ("running", "pending")
        if rec and v["status"] in ("done", "partial"):   # #4: partial output ships like done (harvest carries the death cause)
            out["nodes"][nid]["output"] = rec.get("output") if show_out else _output_pointer(rec)
            out["nodes"][nid]["ms"] = rec.get("ms")
            if v["status"] == "partial":
                out["nodes"][nid]["error"] = rec.get("error")
                out["nodes"][nid]["harvest"] = rec.get("harvest")
        elif rec and v["status"] == "failed":
            out["nodes"][nid]["error"] = rec.get("error")
            out["nodes"][nid]["output"] = rec.get("output") if show_out else _output_pointer(rec)
        # A2: a failed/partial node also ships the child's last words and the
        # failure facts — pure passthrough through the ONE node-truth read (O2),
        # so the parent never tails logs to learn why a child died.
        if rec and v["status"] in ("failed", "partial"):
            nf = _common.node_facts(r, nid)
            if nf:
                out["nodes"][nid]["node_facts"] = {
                    k: nf[k] for k in ("error_class", "attempts", "attempts_log",
                                       "final", "log_path", "prompt_path")}
    # Cumulative spend is independent of heartbeat. Only a verified spawn's exact
    # session title can supply current activity; historical unended rows are not live.
    try:
        cm = _common.child_metrics(st["run_id"])
    except Exception:
        cm = {}
    if cm or any(v.get("active_spawn") for v in st["nodes"].values()):
        import time as _t
        tot = {"tokens_in": 0, "tokens_out": 0, "api_calls": 0, "tool_calls": 0, "cost": 0.0}
        for nid in out["nodes"]:
            mine = {k: m for k, m in cm.items() if k.startswith(f"wf:{st['run_id']}:{nid}:")}
            active = st["nodes"][nid].get("active_spawns", [])
            if not mine and not active:
                continue
            f = {k: sum((m.get(k) or 0) for m in mine.values()) for k in tot}
            current = _common.current_attempt(mine, active)
            line = {"tokens": f"{f['tokens_in']}▸{f['tokens_out']}", "api_calls": f["api_calls"],
                    "tool_calls": f["tool_calls"], "children": len(mine), "scope": "cumulative"}
            if any(not m.get("api_calls_known", True) for m in mine.values()):
                line.pop("api_calls")
            if f["cost"]:
                line["cost_usd"] = round(f["cost"], 4)
            if current["live"]:
                la = current["last_activity"]
                line["live"] = current["live"]
                line["idle_s"] = int(_t.time() - la) if la is not None else None
                line["last"] = current["last_desc"]
                line["last_tool_at"] = la  # #18: the epoch of the last verified activity
            out["nodes"][nid]["metrics"] = line
            for k in tot: tot[k] += f[k]
        out["metrics"] = {"tokens": f"{tot['tokens_in']}▸{tot['tokens_out']}", "api_calls": tot["api_calls"],
                          "tool_calls": tot["tool_calls"], **({"cost_usd": round(tot["cost"], 4)} if tot["cost"] else {})}
    # A3: derived "what next?" — computed ONLY from the run_state fields already in
    # hand (derive-only, never a guess; an unreadable state yields no `next` at all).
    # The agent does what `next` says; an empty `next` means the run is terminal.
    s = st["status"]
    if s == "held" and st.get("held_gate"):
        hg = st["held_gate"]
        out["next"] = [{"action": "release", "gate_id": hg.get("id"),
                       "options": hg.get("options") or []}]
    elif s in ("running", "pending", "interrupted"):
        out["next"] = [{"action": "wait"}]
    elif s == "failed":
        rows = [{"action": "amend", "node": nid, "error_class":
                 (out["nodes"][nid].get("node_facts")
                  or _common.node_facts(r, nid) or {}).get("error_class", "unknown")}
                for nid, v in st["nodes"].items() if v["status"] == "failed"]
        # failed with no failed node visible (e.g. a recorded crashed runner): amend the run.
        out["next"] = rows or [{"action": "amend", "node": None, "error_class": "unknown"}]
    elif s in ("done", "stopped"):
        out["next"] = []
    return out

def act_wait(args):
    """Explicit resume/watch verb. Read-only status/list never spawn; wait may
    resume pending or interrupted work, then block while a verified runner lives."""
    r = run_dir(args.get("run_id"))
    st = run_state(r)
    if not st:
        return {"error": "unknown run_id"}
    if st["status"] in ("running", "pending", "interrupted") and not runner_alive(r):
        _spawn_runner(r)  # only this explicit wait resumes unfinished work
    cap = min(float(args.get("timeout", 600)), 1800)
    # fb-validator-duo (2026-09-26): the clamp stays (harness deadline guard), but a
    # silent cut is a papercut — echo it in the result when it bites.
    raw_timeout = args.get("timeout", 600)
    clamp_note = (f"timeout clamped to 1800s (requested {raw_timeout})"
                  if float(raw_timeout) > 1800 else None)
    def _echo(out):
        if clamp_note and isinstance(out, dict) and "error" not in out:
            out["timeout_note"] = clamp_note
        return out
    # The harness kills any tool call at its own concurrent-batch deadline (default
    # 420s). Yield at 330s with a clean "wait again" so the parent is never left with
    # a client-side "timed out after 420.0s" error mid-sleep (papercut 2026-09-22).
    seg = min(cap, 330)
    t0 = time.time()
    while True:
        st = run_state(r)
        alive = runner_alive(r)
        # Version-skew guard (burned 2026-09-23): a runner spawned fresh from disk may
        # commit statuses this door's read model predates; its own verdict is the truth.
        rx = (st.get("runner_exit") or {}).get("reason")
        if rx == "done" and not alive:
            return _echo(act_status(args))
        if st["status"] not in ("running", "pending") or not alive:
            return _echo(act_status(args))
        if time.time() - t0 > cap:
            return _echo({**act_status(args), "note": f"still running after {cap}s (wait again)"})
        if time.time() - t0 > seg:
            return _echo({**act_status(args), "note": f"still running after {int(time.time()-t0)}s — call wait again (self-yield at {int(seg)}s keeps us under the harness tool deadline)"})
        time.sleep(2)

def _release_core(r, gate_id, answer, ui=False):
    """ONE gate-answer path for tool and UI. Stale answers never block: the answer
    file is overwritten iff absent-or-stale; the gate re-holds unless the efp
    matches. An answer NEVER lands on a run that is stopped or being stopped —
    stop→release is serialized (test-locked), re-run/amend instead."""
    graph = jload(r / "graph.json")
    if not graph:
        return {"ok": False, "error": "unknown run"}
    if (r / "stop.request").exists() or run_state(r)["status"] == "stopped":
        return {"ok": False, "error": "run is stopped/stop pending — answer refused; amend or re-run to continue"}
    byid = {n["id"]: n for n in graph["nodes"]}
    gate = byid.get(gate_id)
    if not gate or gate.get("type") != "gate":
        return {"ok": False, "error": "no such gate node in this run"}
    old = jload(r / "gates" / f"{gate_id}.json")
    if old is not None and old.get("_def") == efp(byid, gate):
        return {"ok": False, "error": "gate already answered (current graph)"}
    rec = {"answer": answer, "_def": efp(byid, gate),
           "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if ui: rec["_ui"] = True
    (r / "gates").mkdir(exist_ok=True)
    p = r / "gates" / f"{gate_id}.json"
    tmp = p.with_name(f"{gate_id}.json.{os.getpid()}.tmp"); tmp.write_text(json.dumps(rec, ensure_ascii=False))
    os.replace(tmp, p)
    return {"ok": True}

def act_release(args):
    r = run_dir(args.get("run_id"))
    if not (r / "graph.json").exists():
        return {"error": "unknown run_id"}
    if (r / "stop.request").exists() or run_state(r)["status"] == "stopped":
        # serialize stop→release: an answer must not land on a run that is being
        # (or already was) stopped — amend or re-run instead.
        return {"error": "run is stopped/stop pending — answer refused; amend or re-run to continue"}
    res = _release_core(r, args.get("gate_id"), args.get("answer", ""))
    if not res.get("ok"):
        return res
    if not runner_alive(r):
        _spawn_runner(r)
        res["auto_resumed"] = True
    res["hint"] = "workflow wait to follow the next boundary"
    return res

def act_steer(args):
    r = run_dir(args.get("run_id"))
    graph = jload(r / "graph.json")
    if not graph:
        return {"error": "unknown run_id"}
    byid = {n["id"]: n for n in graph["nodes"]}
    node = byid.get(args.get("node"))
    if not node:
        return {"error": "no such node"}
    st = run_state(r)
    if not st:
        return {"error": "unknown run_id"}
    run_status = st["status"]
    node_status = (st.get("nodes", {}).get(node["id"]) or {}).get("status")
    if node["type"] != "agent":
        return {"ok": False, "error": "gate nodes do not accept steering; use release for a held gate"}
    if run_status in ("done", "failed", "stopped"):
        # Feedback #68: a terminal run has NO runner that will ever spawn that node —
        # reporting ok here made steering text vanish silently. An interrupted run
        # is NOT refused: wait/release/amend resume its runner, which then consumes
        # the inbox (the delivery line below says so). Refuse honestly and name the
        # correct verb.
        return {"ok": False,
                "error": f"run is {run_status} — steering not queued: no live runner will spawn that node, "
                         "so the text would never be delivered; amend is the correct verb (or re-run)"}
    if node_status in ("done", "partial", "failed", "skipped"):   # #4: a harvested partial never re-spawns either
        return {"ok": False,
                "error": f"node is {node_status} — steering not queued: a {node_status} node never spawns again, "
                         "so the text would never be delivered; amend is the correct verb to make it eligible again"}
    with open(r / "inbox.jsonl", "a") as f:
        f.write(json.dumps({"node": node["id"], "text": args.get("text", ""),
                            "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
    _steer_event(r, "steer.queued", node=node["id"],
                 chars=len(args.get("text", "") or ""))  # #17: the door logs the queue
    if node_status == "running":
        # A verified live child pulls at its NEXT inbox call; lines it never
        # pulled are still baked into the node's next spawn. Both facts, no hedging.
        delivery = (f"queued; the running child will pull it at its next inbox call "
                    f"— no delivery guarantee; anything it does not pull is baked "
                    f"into the next spawn of {node['id']}")
    elif run_status == "held":
        delivery = f"queued; baked into the next spawn of {node['id']} when the held gate releases"
    elif runner_alive(r):
        delivery = (f"queued; baked into the next spawn of {node['id']} — a running "
                    f"child's prompt is never rewritten")
    else:
        delivery = (f"queued; baked into the next spawn of {node['id']} when the runner "
                    f"resumes — call wait to resume it")
    return {"ok": True, "delivery": delivery}

def _steer_lines(path, cursor, hwm):
    """Return (texts, n_pulled) for baked steering lines beyond this spawn's
    cursor, capped at the spawn's HWM; advance the cursor file atomically.
    Honesty law: a line counts as delivered ONLY after this function advances
    the cursor — never claim applied without that evidence."""
    try:
        seen = int(Path(cursor).read_text().strip() or "0")
    except (OSError, ValueError):
        seen = 0
    try:
        lines = [l for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    except OSError:
        return [], 0
    recs, out = [], []
    for l in lines:
        try:
            r = json.loads(l)
        except Exception:
            continue
        recs.append(r)
    todo = [r for r in recs[seen:] if int(r.get("i", -1)) < hwm]
    if not todo:
        return [], 0
    out = [r.get("text", "") for r in todo]
    new_seen = seen + len(todo)
    tmp = Path(cursor + f".{os.getpid()}.tmp")
    tmp.write_text(str(new_seen), encoding="utf-8")
    os.replace(tmp, cursor)
    return out, len(todo)

def act_inbox(args):
    """B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE
    CHILD (env baked at spawn by wf.run_child): it never guesses — the file it
    can see is exactly what its spawn baked (HWM), and the cursor makes delivery
    exactly-once per spawn. A child that never calls this gets the same lines
    via the runner's next-spawn prompt injection: nothing is lost, only delayed.
    No run_id needed: the env is the authority (anti-spoof: a stranger session
    without the env simply has nothing to pull)."""
    f, c = os.environ.get("HERMES_WF_STEER_FILE"), os.environ.get("HERMES_WF_STEER_CURSOR")
    if not f or not c:
        return {"ok": False,
                "error": "not a workflow child spawn (no baked steer env): the inbox tool is for workflow children"}
    try:
        hwm = int(os.environ.get("HERMES_WF_STEER_HWM", "0"))
    except ValueError:
        hwm = 0
    texts, n = _steer_lines(f, c, hwm)
    if n:  # #17: the pull is a fact — log it beside the cursor advance
        try:
            _steer_event(Path(f).parent.parent, "steer.consumed",
                         node=os.environ.get("HERMES_WF_STEER_NODE"),
                         spawn=os.environ.get("HERMES_WF_STEER_SPAWN"), pulled=n)
        except OSError:
            pass
    return {"ok": True, "steering": texts, "pulled": n,
            "node": os.environ.get("HERMES_WF_STEER_NODE"),
            "spawn": os.environ.get("HERMES_WF_STEER_SPAWN")}

def act_amend(args):
    r = run_dir(args.get("run_id"))
    if not (r / "graph.json").exists():
        return {"error": "unknown run_id"}
    new, bad = _input_graph(args)
    if bad:
        return bad
    if new is None:
        return {"error": "amend needs full replacement graph or graph_path"}
    bad = _validation_error(new)
    if bad:
        return bad
    old = jload(r / "graph.json") or {}
    new = dict(new, name=new.get("name", old.get("name", "workflow")))
    # Same resolved-truth rule as run: bake defaults/shape before the write, so
    # the preview, the fingerprints, and the runner all see the resolved defs.
    try:
        new = _common.apply_graph_defaults(new)
    except ValueError as e:
        return {"error": f"graph invalid: defaults/shape: {e}"}
    err, _models, _routes = _resolve_models(new["nodes"])
    if err:
        return {"error": err}
    assert _models is not None and _routes is not None
    # Q3 preview — the same replay-skip law the runner applies (wfcommon.efp +
    # node_rec), computed on the RESOLVED defs (what lands in graph.json), read-only.
    # dry_run returns here WITHOUT touching graph.json, amends.jsonl, or the runner.
    preview = amend_preview(r, new["nodes"])
    if args.get("dry_run"):
        return {"ok": True, "dry_run": True, "models": _models, "routes": _routes, **preview,
                "hint": "nothing written — re-run without dry_run to apply"}
    (r / "amends.jsonl").open("a").write(
        json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "old": jload(r / "graph.json"), "new": new}) + "\n")
    tmp = r / f"graph.json.{os.getpid()}.tmp"
    tmp.write_text(json.dumps(new, ensure_ascii=False, indent=2))
    os.replace(tmp, r / "graph.json")
    meta = jload(r / "run.json", {}) or {}
    if meta.get("name") != new["name"]:
        meta["name"] = new["name"]
        mtmp = r / f"run.json.{os.getpid()}.tmp"
        mtmp.write_text(json.dumps(meta, ensure_ascii=False))
        os.replace(mtmp, r / "run.json")
    with open(r / "events.jsonl", "a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "event": "graph.amended"}) + "\n")
    if runner_alive(r):
        (r / "restart.request").write_text("1")
        applies = "live runner hot-reloads at its next wave boundary; call wait (it will resume as needed)"
    else:
        _spawn_runner(r)
        applies = "runner respawned; efp replay-skip re-runs changed nodes and everything downstream"
    return {"ok": True, "models": _models, "routes": _routes, "applies": applies,
            "hint": "workflow wait to follow", **preview}

def act_stop(args):
    r = run_dir(args.get("run_id"))
    if not (r / "graph.json").exists():
        return {"error": "unknown run_id"}
    st = run_state(r)
    if st and st["status"] in ("done", "failed", "stopped"):
        return {"ok": True, "already": st["status"]}
    (r / "stop.request").write_text(datetime.now(timezone.utc).isoformat(timespec="seconds"))
    if not runner_alive(r):
        _spawn_runner(r)  # consume the marker even from an idle/held run
        return {"ok": True, "note": "was idle — runner spawned just to honour the stop"}
    return {"ok": True, "note": "stop lands at the next boundary; in-flight children are killed"}

def act_list(_args):
    root = runs_root()
    runs = []
    if root.exists():
        for r in sorted(root.iterdir(), reverse=True):
            st = run_state(r)
            if st:
                runs.append({"run_id": st["run_id"], "name": st["name"], "status": st["status"],
                             "gate": (st["held_gate"] or {}).get("id"),
                             "nodes_done": st["done"], "nodes_skipped": st["skipped"], "nodes_total": st["total"],
                             "runner_live": runner_alive(r)})
    return {"runs": runs[:50], **_common.run_summary(runs)}

ACTIONS = {"run": act_run, "status": act_status, "wait": act_wait, "release": act_release,
           "steer": act_steer, "inbox": act_inbox, "amend": act_amend, "stop": act_stop, "list": act_list,
           "save": act_save, "library": act_library}

def handle(args, **kwargs):
    try:
        fn = ACTIONS.get(args.get("action"))
        if not fn:
            return json.dumps({"error": f"unknown action {args.get('action')!r}", "actions": sorted(ACTIONS)})
        return json.dumps(fn(args), ensure_ascii=False, default=str)
    except Exception as e:
        import traceback
        return json.dumps({"error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-800:]})

def _wf_command(raw_args):
    """`/wf` — the library front door. `/wf` lists; `/wf <name> [note]` tells the agent to
    replay <name> (with the note as steering context). The command output is shown to the
    human, so it doubles as the instruction the agent will act on next turn."""
    arg = (raw_args or "").strip()
    lib = act_library({})["library"]
    if not arg or arg in ("list", "ls"):
        if not lib:
            return ("Workflow library is empty. Shelve one: `workflow save run_id=<run> name=<name>` "
                    "or ask the agent to save a graph it just ran.")
        rows = "\n".join(f"- **{x['name']}** — {x['nodes']} nodes, {x['gates']} gate(s), {x['fanouts']} fan-out(s)"
                          + (f": {x['description']}" if x.get('description') else "") for x in lib)
        return f"Workflow library:\n{rows}\n\nRun one: `/wf <name> [note for the run]`"
    name, _, note = arg.partition(" ")
    try:
        p = _lib_path(name)
    except ValueError as e:
        return f"{e}"
    if not p.exists():
        names = ", ".join(x["name"] for x in lib) or "(empty)"
        return f"No library graph named `{name}`. Available: {names}"
    g = jload(p) or {}
    return (f"Replay the shelved workflow **{p.stem}** ({len(g.get('nodes') or [])} nodes)"
            + (f" — operator note: {note}" if note else "") + ".\n"
            f"Agent: call `workflow{{action:\"run\", from:\"{p.stem}\"}}`"
            + (f", then `workflow{{action:\"steer\", run_id, node:<first pending node>, text:{json.dumps(note)}}}`" if note else "")
            + ", emit `::workflow{id=\"<run_id>\"}` on its own line, then `wait` and answer gates via clarify.")

def register(ctx):
    global _CTX
    _CTX = ctx
    ctx.register_skill("workflow", HERE / "SKILL.md", description="Run and orchestrate agent workflows.")
    tiers = model_tiers()
    if tiers:
        WORKFLOW_PARAMS["properties"]["graph"]["description"] += (
            " node.model: a literal model id OR one of the owner's tiers " + json.dumps(tiers) +
            " — pick per node by how hard the step is. "
            "Unset = seat default. run echoes the resolved {node: model} table.")
    ctx.register_tool(name="workflow", toolset="workflows", schema=WORKFLOW_SCHEMA, handler=handle)
    ctx.register_command("wf", _wf_command, description="Workflow library: `/wf` lists, `/wf <name> [note]` replays a shelved graph",
                         args_hint="[name] [note]", argument_mode="text")
