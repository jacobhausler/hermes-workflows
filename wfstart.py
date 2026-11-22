"""wfstart.py — the `start` verb's synthesizer (bd_2026-11-13-9i1).

THE DATA SHAPE, BEFORE THE LOGIC
  StartSpec  = {name: str?, goal: str? XOR nodes: [NodeSpec], shape: str?}
  NodeSpec   = {id: str, goal: str, items_from: str?, after: [str]?, shape: str?}
  GraphOut   = the plain wf/1 graph dict the door already admits:
               {grammar: "wf/1", name: <slug>, description: <goal>,
                nodes: [{id, type: "agent", shape, goal,
                         fanout?: {items_from}, after?: [...]}]}

SMART DEFAULTS (v1 — exactly two shapes are synthesized):
  * single node:  one agent node named `work` carrying the goal verbatim.
  * fixed fan-out from a json path: the nodes form; a node with `items_from`
    gets `fanout: {items_from: <node_id>.<dotted.path>}` — the grammar's own
    channel. Plural-prose fan-out inference is NOT v1 scope.
  * provider = the seat's own route: model/provider stay ABSENT on every
    synthesized node, so the door routes it exactly as an unset `model` does
    (seat default; the SKILL law "an unset model rides the seat default").
  * timeout + budgets from the shape census: nodes carry only a `shape`; the
    door's apply_graph_defaults bakes max_turns/timeout from
    wfcommon.SHAPE_PRESETS — the measured-p95 table (census of successful
    agent nodes per shape, measured 2026-09-25 over 80 runs / 219 nodes).
    No second budget table: SHAPE_PRESETS IS the census. A RunBudget
    (budget.tokens) is deliberately left unset — an author may add one to
    the graph later; the synthesizer never invents a cap it did not measure.
  * lane-key: "<team>/start-<slug>" when a team is given, else
    "start-<slug>" — so a second start of the same goal while the first run
    is unfinished DEDUPES through the door's existing lane registry instead
    of double-dispatching (idempotent by construction).

REFUSALS (the two misuse paths) carry `example`: the minimal accepting input,
rendered by this module. When the door-side example channel (bd_2026-11-13-z79,
structured examples on validation rules) lands, START_EXAMPLE may re-route
through it; until then this module's static string IS the teach example.

Stdlib-only besides the door's own `_yaml_load` policy (hermes_yaml / ruamel /
pyyaml, whichever the seat has); a seat without any YAML loader keeps working
for plain-language goals and refuses the spec form loudly, never silently.
"""
import re

# The door binds its OWN path-loaded wfcommon into this module at import
# (bind_wfcommon below) — one YAML policy, no second sys.path import that
# could land on another plugin's wfcommon. A bare direct import (tests/CI
# with the repo root on sys.path) works as the fallback.
_wfcommon = None


def bind_wfcommon(mod):
    global _wfcommon
    _wfcommon = mod


def _yaml_module():
    global _wfcommon
    if _wfcommon is None:
        import wfcommon as _wfcommon  # noqa: F811 — fallback for direct module use
    return _wfcommon

SHAPES = ("recon", "build", "review", "publish")
MAX_SLUG = 40

# The static teach example: five-line YAML, spec-compliant BY CONSTRUCTION
# (test_start_verb round-trips it through parse_input).
START_EXAMPLE = (
    "name: charter-review\n"
    "nodes:\n"
    "  - {id: load, goal: 'Read charter.json and answer with exactly {\"items\": [one string per open item]}'}\n"
    "  - {id: review, goal: 'Review this item and report the finding', items_from: load.items, after: [load]}\n"
    "# shape per node: recon|build|review|publish (defaults to review for review-phrased goals)"
)
PLAIN_EXAMPLE = (
    'workflow {"action": "start", "goal": "audit the requirements file and report every gap"}\n'
    "# or the five-line form:\n" + START_EXAMPLE
)


class Refusal(Exception):
    """Raised with the human line; parse_input renders it with the example."""
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


def _spec_error(msg):
    return {"error": f"start: {msg}", "usage": PLAIN_EXAMPLE, "example": START_EXAMPLE}


def _looks_like_spec(text):
    """A spec is a mapping whose top level opens with a known key on its own
    line; anything else (including one-sentence prose) is a plain goal. A
    sentence that merely contains a colon mid-line never matches (the line
    must START with the bare key)."""
    for line in text.splitlines()[:8]:
        if re.match(r"^(name|goal|nodes|shape)\s*:", line):
            return True
    return False


def _load_yaml(text):
    try:
        return _yaml_module()._yaml_load(text)
    except Refusal:
        raise
    except Exception as e:
        raise Refusal(f"input looks like a spec but did not parse as YAML ({type(e).__name__}: {e})")


def _valid_id(s):
    return isinstance(s, str) and re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$", s) is not None


def _check_shape(v, where):
    if v not in SHAPES:
        raise Refusal(f"{where}.shape {v!r} invalid; allowed: {list(SHAPES)}")


def _normalize_nodes(raw):
    if not isinstance(raw, list) or not raw:
        raise Refusal("nodes must be a non-empty list of {id, goal, [items_from], [after], [shape]}")
    seen, out = set(), []
    for i, n in enumerate(raw):
        if not isinstance(n, dict):
            raise Refusal(f"nodes[{i}] must be an object, got {n!r}")
        bad = set(n) - {"id", "goal", "items_from", "after", "shape"}
        if bad:
            raise Refusal(f"nodes[{i}] unknown key(s) {sorted(bad)}; allowed: id, goal, items_from, after, shape")
        nid = n.get("id")
        goal = n.get("goal")
        if not _valid_id(nid):
            raise Refusal(f"nodes[{i}].id {nid!r} invalid (alnum start, [A-Za-z0-9_.-], <=64)")
        if nid in seen:
            raise Refusal(f"nodes[{i}].id {nid!r} declared twice")
        seen.add(nid)
        if not isinstance(goal, str) or not goal.strip():
            raise Refusal(f"nodes[{i}].goal must be a non-empty string")
        after = n.get("after", [])
        if not isinstance(after, list) or any(not isinstance(a, str) for a in after):
            raise Refusal(f"nodes[{i}].after must be a list of node id strings")
        items_from = n.get("items_from")
        if items_from is not None and (not isinstance(items_from, str)
                                       or re.match(r"^[A-Za-z0-9_.-]+\.[A-Za-z0-9_.[\]-]+$", items_from) is None):
            raise Refusal(f"nodes[{i}].items_from {items_from!r} must look like '<node_id>.<dotted.path>'")
        if "shape" in n:
            _check_shape(n["shape"], f"nodes[{i}]")
        out.append({"id": nid, "goal": goal, "items_from": items_from,
                    "after": after, "shape": n.get("shape")})
    # after-refs must name sibling ids (the door's edge law re-measures this;
    # refusing here keeps the teach on THIS boundary's own vocabulary)
    for i, n in enumerate(out):
        missing = [a for a in n["after"] if a not in seen]
        if missing:
            raise Refusal(f"nodes[{i}].after names unknown id(s) {missing}")
    return out


def parse_input(raw):
    """raw (str | None) -> (StartSpec | None, refusal-payload | None).
    Exactly one return is None. Refusal payloads carry the example."""
    if not isinstance(raw, str) or not raw.strip():
        return None, _spec_error(
            "needs one plain-language goal string OR a five-line yaml spec; got nothing")
    text = raw.strip()
    if not _looks_like_spec(text):
        return {"name": None, "goal": text, "nodes": None, "shape": None}, None
    loaded = _load_yaml(text)
    if not isinstance(loaded, dict):
        # e.g. a prose goal whose first line happened to read like a key —
        # if it still parses to a scalar, honor the plain channel.
        return {"name": None, "goal": text, "nodes": None, "shape": None}, None
    bad = set(loaded) - {"name", "goal", "nodes", "shape"}
    if bad:
        raise Refusal(f"spec unknown key(s) {sorted(bad)}; allowed: name, goal, nodes, shape")
    name, goal, nodes, shape = loaded.get("name"), loaded.get("goal"), loaded.get("nodes"), loaded.get("shape")
    if goal and nodes:
        raise Refusal("goal and nodes are one channel each — declare only one")
    if goal is not None and nodes is None:
        if not isinstance(goal, str) or not goal.strip():
            raise Refusal("goal must be a non-empty string")
        if shape is not None:
            _check_shape(shape, "spec")
        return {"name": name if isinstance(name, str) and name.strip() else None,
                "goal": goal.strip(), "nodes": None, "shape": shape}, None
    if nodes is not None and goal is None:
        norm = _normalize_nodes(nodes)
        if shape is not None:
            _check_shape(shape, "spec")
        if name is not None and (not isinstance(name, str) or not name.strip()):
            raise Refusal("name must be a non-empty string")
        return {"name": name or None, "goal": None, "nodes": norm, "shape": shape}, None
    raise Refusal("spec carries neither goal nor nodes")


# goal-verb -> shape (keyword table; miss = DEFAULT_SHAPE floor via infer).
_SHAPE_HINTS = (("recon", ("survey", "find", "list", "enumerate", "read", "scout", "inventory", "census")),
                ("review", ("review", "audit", "check", "verify", "judge", "inspect", "triage", "assess")),
                ("publish", ("publish", "deploy", "release", "ship", "merge", "post", "upload")))


def infer_shape(goal):
    words = set(re.findall(r"[a-z]+", goal.lower()))
    for shape, kws in _SHAPE_HINTS:
        if words & set(kws):
            return shape
    return "build"


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:MAX_SLUG].rstrip("-")
    return slug or "task"


def lane_key(graph_name, team=None):
    slug = slugify(graph_name)
    return f"{team}/start-{slug}" if team else f"start-{slug}"


def synthesize(spec):
    """StartSpec -> graph dict (NOT yet door-validated: act_start feeds the
    result through the existing door, so every door law still applies)."""
    top_shape = spec.get("shape")
    if spec["nodes"] is None:
        shape = top_shape or infer_shape(spec["goal"])
        nodes = [{"id": "work", "type": "agent", "shape": shape, "goal": spec["goal"]}]
        description = spec["goal"]
    else:
        nodes = []
        for n in spec["nodes"]:
            node = {"id": n["id"], "type": "agent",
                    "shape": n["shape"] or top_shape or infer_shape(n["goal"]),
                    "goal": n["goal"]}
            if n["after"]:
                node["after"] = list(n["after"])
            if n["items_from"]:
                node["fanout"] = {"items_from": n["items_from"]}
            nodes.append(node)
        description = nodes[0]["goal"]
    name = spec.get("name") or slugify(description)
    return {"grammar": "wf/1", "name": name, "description": description, "nodes": nodes}


def parse_start(raw):
    """parse_input + Refusal rendering: (spec | None, refusal | None)."""
    try:
        return parse_input(raw)
    except Refusal as r:
        return None, _spec_error(r.msg)
