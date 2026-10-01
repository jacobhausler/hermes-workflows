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

_BUDGET_KEYS = ("max_turns", "timeout", "run_budget", "shape")
# #100: scheduling limits are policy, not a change to committed node work.
_CONCURRENCY_KEYS = ("concurrency", "item_concurrency")
# #24/#25 (A3): route POLICY (require_route) and the door's proof ANNOTATION
# (route_verified) are not work either — like budgets they must not participate in
# def_hash: the door bakes route_verified into graph.json after validation, and the
# runner computes efp on the baked node; an author amend that flips
# defaults.require_route would otherwise un-freeze every committed node and re-run
# it. Nodes without these keys hash byte-identically to before (no legacy drift).
_POLICY_KEYS = ("require_route", "route_verified")
FP_RULE_LEGACY = 1  # before b79fa21: budgets participated in def_hash
FP_RULE_VERSION = 2  # b79fa21: exclude budgets
FP_RULES = (FP_RULE_LEGACY, FP_RULE_VERSION)

def def_hash(node, rule=FP_RULE_VERSION):
    # Budgets are not work: raising a wall or naming a shape must not invalidate a
    # committed node (and apply_graph_defaults baking budgets into an old run's
    # frozen graph at amend must not re-run everything it already finished).
    if rule not in FP_RULES:
        raise ValueError(f"unknown fingerprint rule: {rule!r}")
    if rule == FP_RULE_VERSION:
        node = {k: v for k, v in node.items()
                if k not in _BUDGET_KEYS and k not in _CONCURRENCY_KEYS and k not in _POLICY_KEYS}
    return hashlib.sha256(json.dumps(node, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]

_EFP_SEP = "\u241f"

def efp(byid, node, _seen=None, *, rule=FP_RULE_VERSION):
    """Effective fingerprint: own def + every ancestor's effective fingerprint.
    An amended node (or any ancestor) changes the efp of everything downstream, so
    downstream results are stale and nodes downstream re-run or re-hold — transitively."""
    _seen = _seen or set()
    nid = node["id"]
    if nid in _seen:
        return "?"  # unreachable for validated (acyclic) graphs
    _seen = _seen | {nid}
    parts = [def_hash(node, rule)]
    for a in sorted(node.get("after", [])):
        if a in byid:
            parts.append(efp(byid, byid[a], _seen, rule=rule))
    return hashlib.sha256(_EFP_SEP.join(parts).encode()).hexdigest()[:16]


def graph_fingerprint(graph, *, rule=FP_RULE_VERSION):
    """Stable signature of the node definitions that a runner verdict describes."""
    nodes = (graph or {}).get("nodes")
    if not isinstance(nodes, list) or any(not isinstance(n, dict) or not n.get("id") for n in nodes):
        return None
    try:
        byid = {n["id"]: n for n in nodes}
        facts = {str(n["id"]): efp(byid, n, rule=rule) for n in nodes}
        raw = json.dumps(facts, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    except Exception:
        return None

def source_digest(graph):
    """1.1 (RATIFY F5): sha256 hex over the canonical `nodes` JSON of a graph — the
    provenance identity of a shelved graph. NOT the effective fingerprint:
    graph_fingerprint() keeps its name and meaning (per-node efp facts, 16 hex);
    this is the whole node list, budgets included, full 64-hex digest. None when the
    graph has no node list."""
    nodes = (graph or {}).get("nodes") if isinstance(graph, dict) else None
    if not isinstance(nodes, list):
        return None
    try:
        raw = json.dumps(nodes, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(raw.encode()).hexdigest()

# ---------- runs root + launcher identity (1.1, RATIFY F1/F2) ----------
# ONE resolver for "where do runs live": the runner, the door and the dashboard used to
# compute `$HERMES_HOME/workflows` inline in four places. `WF_RUNS_ROOT` (absolute dir)
# overrides so a team can share one root that survives any profile's deletion; unset or
# empty = the 1.0.15 default, byte-identical.

def hermes_home():
    """Core's resolution when importable, else the raw env (1.0.15 semantics, unchanged).

    ``hermes_constants.get_hermes_home`` is context-local override -> HERMES_HOME env ->
    platform default. A profile-scoped/embedding host (gateway ``-p`` under a supervisor,
    multiplexed dashboard ``--open-profile``) keeps ``os.environ["HERMES_HOME"]`` at the
    LAUNCH root and serves the profile through that override — reading the env alone
    hands the door, the runner, and every child the BASE profile: seat config invisible,
    profile-defined providers die 'Unknown provider', and run dirs land under the wrong
    home. Core's own #18594 warning instructs subprocess spawners to pass HERMES_HOME
    explicitly; the door honours that by stamping the resolved home into the runner env.
    """
    try:
        from hermes_constants import get_hermes_home
        return get_hermes_home()
    except Exception:
        return Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))


# ---------- owner settings (#41/#42: tool-bridge first-class) ----------
# `plugins.entries.hermes-workflows.settings.{runs_root,profile}` are OWNER vocabulary,
# read at CALL time (no restart) through the same plugin-scoped helper `_hermes_bin`
# uses (PluginContext.get_config). The door installs that helper via
# `set_owner_setting_reader`; a process without a plugin ctx (runner, dashboard API,
# standalone tests) falls back to a side-effect-free raw read of the resolved
# `<hermes_home>/config.yaml` — the SAME file core's loader resolves for the
# profile, never core's load_config (which materialises a home skeleton on read).
# Unset keys = byte-identical to the resolver before owner settings shipped. The model is never told to
# set these; a graph/run argument can never substitute for them.
PLUGIN_ID = "hermes-workflows"
NO_READER = object()   # a reader answers this when it has no plugin ctx to ask
_OWNER_SETTING_READER = None
_RAW_SETTINGS_CACHE = {}  # path -> (mtime_ns, size, settings dict)

def set_owner_setting_reader(fn):
    """Install the door's plugin-scoped reader: fn(key) -> value | None | NO_READER."""
    global _OWNER_SETTING_READER
    _OWNER_SETTING_READER = fn

def _yaml_load(text):
    """Core's own YAML policy when importable (hermes_yaml: ruamel, YAML 1.1 booleans),
    else ruamel/pyyaml directly — the config file must parse the way core parses it."""
    try:
        from hermes_yaml import safe_load
        return safe_load(text)
    except ImportError:
        pass
    try:
        from ruamel.yaml import YAML
        y = YAML(typ="safe", pure=True)
        y.version = (1, 1)
        return y.load(text)
    except ImportError:
        import yaml
        return yaml.safe_load(text)

# ---- `${VAR}` / `${env:VAR}` expansion, ported from core's loader ----
# hermes_cli/config.py `_expand_env_vars` / `_env_expand_match` / `_env_ref_var_name`
# / `_env_ref_lookup` (rules copied verbatim, no core import): a raw reader that skips
# this makes the door (core loader, expanded) and the runner/dashboard (raw read)
# disagree on the SAME key — the door creates a run under the expanded path, the runner
# refuses the literal `${HOME}/...` as non-absolute and the run is invisible (F2f).
_ENV_REF_RE = re.compile(r"\${([^}]+)}")

def _is_non_env_secret_ref(ref):
    """True for a SecretRef body with a non-`env` source (`bitwarden:FOO`, `vault:...`)."""
    return ":" in ref and re.match(r"^[a-z][a-z0-9_-]*:", ref) is not None

def _env_ref_var_name(ref):
    """Env-var name a `${VAR}` / `${env:VAR}` ref reads, or None for a non-env source / empty `env:`."""
    ref = ref.strip()
    if ref.startswith("env:"):
        return ref[len("env:"):].strip() or None
    if _is_non_env_secret_ref(ref):
        return None
    return ref

def _env_ref_lookup(name):
    """Core's policy verbatim: the profile secret scope when one is active, else plain os.environ."""
    try:
        from agent.secret_scope import current_secret_scope, get_secret as _get_secret
    except Exception:
        return os.environ.get(name)
    if current_secret_scope() is None:
        return os.environ.get(name)
    return _get_secret(name)

def _expand_config_value(raw):
    """Expand one `${VAR}` (legacy bare name) or `${env:VAR}` (Cursor-style SecretRef) string.
    Non-env sources and UNRESOLVED refs stay verbatim (exactly like core); the validators
    below then refuse a surviving `${` on EVERY reader, so no path ever resolves a run
    against a half-expanded value."""
    def _m(m):
        inner = m.group(1).strip()
        name = _env_ref_var_name(inner)
        if name is None:
            return m.group(0)          # non-env source or empty `env:` — keep verbatim
        val = _env_ref_lookup(name)
        return val if val is not None else m.group(0)   # unset var — keep verbatim (core)
    return _ENV_REF_RE.sub(_m, raw)

def _expand_config_values(obj):
    """Recursive `${VAR}`/`${env:VAR}` expansion over a settings mapping (keys/non-strings untouched)."""
    if isinstance(obj, str):
        return _expand_config_value(obj)
    if isinstance(obj, dict):
        return {k: _expand_config_values(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_config_values(item) for item in obj]
    return obj

def _no_unresolved_ref(label, raw):
    """A surviving `${...}` after expansion means the referenced var is unset (or a
    non-env source): core keeps such templates verbatim, so EVERY reader must refuse
    them with the same error — never let the door alone see a value."""
    if isinstance(raw, str) and _ENV_REF_RE.search(raw):
        raise ValueError(f"{label} has an unresolved ${{...}} reference: {raw!r} "
                         "— set the referenced environment variable or use a literal absolute path")

def _raw_owner_settings():
    """`plugins.entries.hermes-workflows` raw read from the resolved home's config.yaml
    (no core import, no skeleton side effects): returns `(settings, legacy_config)` —
    two dicts, either empty when absent/unparseable. Values come back EXPANDED with
    core's `${VAR}` / `${env:VAR}` semantics (`_expand_config_value` mirrors
    hermes_cli/config.py), so a raw read answers exactly what core's loader hands the
    door's plugin ctx. Unresolved refs stay verbatim HERE and are refused downstream
    (`_no_unresolved_ref`), identically on every reader."""
    p = hermes_home() / "config.yaml"
    try:
        st = p.stat()
        sig = (st.st_mtime_ns, st.st_size)
    except OSError:
        return {}, {}
    hit = _RAW_SETTINGS_CACHE.get(str(p))
    if hit and hit[0] == sig:
        return hit[1]
    settings, legacy = {}, {}
    try:
        cfg = _yaml_load(p.read_text()) or {}
        entry = ((cfg.get("plugins") or {}).get("entries") or {}).get(PLUGIN_ID) or {}
        found = entry.get("settings")
        settings = found if isinstance(found, dict) else {}
        conf = entry.get("config")
        legacy = conf if isinstance(conf, dict) else {}
        settings = _expand_config_values(settings)
        legacy = _expand_config_values(legacy)
    except Exception:
        settings, legacy = {}, {}
    _RAW_SETTINGS_CACHE[str(p)] = (sig, (settings, legacy))
    return settings, legacy

_UNSET = object()   # THE missing-key sentinel — one instance, compared by identity

def _nested(mapping, key):
    cur = mapping
    for seg in key.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            return _UNSET
        cur = cur[seg]
    return cur

def owner_setting(key):
    """One owner-settings read: the door's plugin ctx when it has one (its answer is
    final, unset included), else the raw config file of the resolved home. The raw
    fallback is PER KEY, mirroring core's `PluginContext.get_config`
    (hermes_cli/plugins.py): `settings.<key>` wins when present, else the legacy
    `config.<key>` subtree, else unset — never whole-mapping substitution, or the
    door (core reader) and the runner/dashboard (raw reader) disagree on WHICH value
    a key holds and the door creates runs the runner cannot find."""
    if _OWNER_SETTING_READER is not None:
        try:
            v = _OWNER_SETTING_READER(key)
        except Exception:
            v = NO_READER
        if v is not NO_READER:
            return v
    settings, legacy = _raw_owner_settings()
    v = _nested(settings, key)
    if v is _UNSET:
        v = _nested(legacy, key)
    return None if v is _UNSET else v

def settings_runs_root(home=None):
    """`settings.runs_root` as a validated absolute Path, or None when unset/empty.
    FAIL-CLOSED: a malformed value raises ValueError (the door surfaces it as the
    action's error) — it is never silently ignored, because a silent fallback would
    re-create exactly the invisible door-vs-tab divergence #42 describes.
      * expanduser applied; the result MUST be absolute (a relative root would be
        cwd-dependent: a different root per process = invisible runs).
      * MUST NOT resolve inside another profile's home under the caller's estate
        (`<hermes_root>/profiles/<name>/`, the directory core's `-p` names live in)
        unless that home IS the caller's own resolved home — a typo pinning the shared
        estate to one profile's private dir would make every other profile's runs
        vanish into it; the caller's own profile home is the ordinary per-profile
        default and stays legal. Only the estate's profiles root counts: a path that
        merely contains a `profiles` segment elsewhere on disk is not a Hermes profile."""
    raw = owner_setting("runs_root")
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValueError("settings.runs_root must be a string (absolute directory path)")
    raw = raw.strip()
    if not raw:
        return None
    _no_unresolved_ref("settings.runs_root", raw)   # an unset ${VAR} stays verbatim in core
    p = Path(raw).expanduser()
    if not p.is_absolute():
        raise ValueError(f"settings.runs_root must be an absolute path, got {raw!r}")
    own = Path(home) if home is not None else hermes_home()
    def _res(x):
        try:
            return x.resolve()
        except OSError:
            return x
    own_r, p_r = _res(own), _res(p)
    profiles = _res(profiles_root(own))
    if p_r == profiles:
        raise ValueError(
            f"settings.runs_root {raw!r} IS the estate's profiles root — refused: it would "
            "mix every seat's namespace into one runs dir and collide with profile homes "
            "(pick a dedicated directory, e.g. <estate>/workflows)")
    if len(p_r.parts) > len(profiles.parts) and p_r.parts[:len(profiles.parts)] == profiles.parts:
        prof_home = Path(*p_r.parts[:len(profiles.parts) + 1])
        if prof_home != own_r:
            raise ValueError(
                f"settings.runs_root {raw!r} resolves inside profile home {prof_home} — "
                "refused: a runs root inside another profile's private dir pins the estate to "
                "that profile (only the launcher's own profile home is allowed)")
    return p_r

def settings_profile():
    """`settings.profile` validated with the same rules `profile:` node keys use
    (_PROFILE_NAME_BAD); None when unset/empty; ValueError on an unsafe name.
    FAIL-CLOSED on a GHOST (#46 R1): the named profile home `<hermes_root>/profiles/
    <name>/` must EXIST — a stamped `dispatched_by` nobody can verify poisons the
    consent model (targets list the ghost, team readmodel resolves nothing) and is
    exactly the silent divergence #42 was about. Applies to the RESOLVED value
    whatever subtree it came from (settings or legacy `config`), identically on every
    reader, so a typo says 'does not exist' at the door instead of inventing an
    identity. The 'default' fallback (nothing configured) is untouched."""
    raw = owner_setting("profile")
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValueError("settings.profile must be a string (a profile directory name)")
    raw = raw.strip()
    if not raw:
        return None
    if _PROFILE_NAME_BAD.search(raw):
        raise ValueError(f"settings.profile {raw!r} is not a safe profile directory name "
                         "(no separators, no '..', no leading dot)")
    _no_unresolved_ref("settings.profile", raw)   # unset ${VAR} stays verbatim in core
    ph = profile_home(raw)
    if not ph.is_dir():
        raise ValueError(f"settings.profile {raw!r} does not exist: no profile home at {ph} "
                         "(create the profile or fix plugins.entries.hermes-workflows.settings.profile)")
    return raw


def launch_runs_root():
    """Runs root of the RAW process environment (never the context-resolved home).

    ONLY for legacy-location lookup: runs created before the profile-home fix live
    under the launch root on a profile-scoped host and stay resolvable by run_id.
    New runs never land here. `WF_RUNS_ROOT` still wins (shared team root).
    """
    override = os.environ.get("WF_RUNS_ROOT", "")
    if override:
        return Path(override)
    return Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes")) / "workflows"


def find_run(rid):
    """Locate a run dir by id: resolved runs_root() first; legacy launch root only
    for an EXISTING run (pre-fix ids stay resumable, new ids never land there)."""
    root = runs_root()
    legacy = launch_runs_root()
    if legacy != root and (legacy / rid).is_dir() and not (root / rid).exists():
        return legacy / rid
    return root / rid


def runs_root():
    """ONE resolver. Precedence (#42): `settings.runs_root` (owner, validated,
    fail-closed) > `WF_RUNS_ROOT` env (non-empty) > `<hermes_home>/workflows`
    (core-resolved home when importable, else `$HERMES_HOME`, else `$HOME/.hermes`)."""
    configured = settings_runs_root()
    if configured is not None:
        return configured
    override = os.environ.get("WF_RUNS_ROOT", "")
    if override:
        return Path(override)
    return hermes_home() / "workflows"

def effective_runs_root(environ):
    """The runs root a process RUNS UNDER, from its environment mapping (str->str, e.g. a
    parsed /proc/<pid>/environ). `settings.runs_root` (this process's owner setting)
    first — an owner-pinned root applies to every process of the estate, so a sibling
    runner's env is judged against the same single root runs_root() answers; else
    `WF_RUNS_ROOT` if set, else `HERMES_HOME/workflows`, else None (nothing to compare —
    legacy `if homes:` guard)."""
    try:
        configured = settings_runs_root()
    except ValueError:
        configured = None   # liveness is a read path: a bad setting is the door's error, not ours
    if configured is not None:
        return configured
    override = environ.get("WF_RUNS_ROOT", "")
    if override:
        return Path(override)
    home = environ.get("HERMES_HOME", "")
    if home:
        return Path(home) / "workflows"
    return None

def hermes_root(home=None):
    """The non-secret Hermes ROOT: `HERMES_HOME.parent.parent` when HERMES_HOME is a
    named profile home (`<root>/profiles/<name>`), else HERMES_HOME itself."""
    home = Path(home) if home is not None else hermes_home()
    return home.parent.parent if home.parent.name == "profiles" else home

def launcher_profile(home=None):
    """Launcher identity — NEVER from a graph/run arg. Ranked (#41):
      1. the process's own resolved HERMES_HOME when it is `<root>/profiles/<name>` -> name
      2. else `settings.profile` (owner-declared fallback for env-blind gateways: the
         desktop bridge / a gateway that launches the door without a profile home)
      3. else "default" (byte-identical to the stamp before owner settings shipped)
    Env wins whenever present: an owner setting can only fill the identity the process
    could not carry, never override one it does. An explicit `home=` is an env-shaped
    caller (tests, runner_alive) and follows the same ranking."""
    home = Path(home) if home is not None else hermes_home()
    if home.parent.name == "profiles":
        return home.name
    configured = settings_profile()
    return configured if configured else "default"

def profiles_root(home=None):
    return hermes_root(home) / "profiles"

def profile_home(name, home=None):
    return profiles_root(home) / str(name)

_PROFILE_NAME_BAD = re.compile(r"(^[/~.]|[\\/]|\.\.|[\x00-\x1f])")

def profile_errors(nodes, launcher=None, profiles_dir=None):
    """1.1 (RATIFY F2/B1) door-level validation of agent `profile:` keys, run AFTER the
    door rendered `{run.KEY}` bindings and BEFORE any run write. Returns [{node,
    field:'profile', msg}]. Rules: non-empty string (a safe directory name); name !=
    "default" (default is never a target); `<profiles_dir>/<name>/config.yaml` exists;
    `<profiles_dir>/<name>/workflow_team.json` exists and its `accept_from` list contains
    `launcher` ("default" is a legal launcher name). DELEGATION, NOT ISOLATION: consent is
    TARGET-owned — the target profile lists who may launch it; the launcher identity is
    resolved from the door's own HERMES_HOME (never a graph arg) via launcher_profile()."""
    launcher = launcher if launcher is not None else launcher_profile()
    profiles_dir = Path(profiles_dir) if profiles_dir is not None else profiles_root()
    errs = []
    def E(nid, msg):
        errs.append({"node": nid, "field": "profile", "msg": msg})
    for n in nodes or []:
        if not isinstance(n, dict) or "profile" not in n or n.get("type", "agent") != "agent":
            continue  # non-agent profile keys die on the closed-key grammar
        nid = n.get("id")
        prof = n["profile"]
        if not isinstance(prof, str) or not prof.strip():
            E(nid, "profile must be a non-empty string (the teammate's profile DIRECTORY name)")
            continue
        if _PROFILE_NAME_BAD.search(prof):
            E(nid, f"profile {prof!r} is not a safe profile directory name "
                   "(no separators, no '..', no leading dot)")
            continue
        if prof == "default":
            E(nid, "profile 'default' is never a target — 'default' is only a legal launcher name")
            continue
        ph = profiles_dir / prof
        if not (ph / "config.yaml").is_file():
            E(nid, f"profile {prof!r} does not exist: no config.yaml at {ph / 'config.yaml'}")
            continue
        consent = jload(ph / "workflow_team.json")
        if consent is None:
            E(nid, f"profile {prof!r} has no consent file: write {ph / 'workflow_team.json'} "
                   f'with {{"accept_from": ["{launcher}"]}} from the TARGET side '
                   "(profile: is delegation, not isolation — the target must opt in)")
            continue
        accept_from = consent.get("accept_from") if isinstance(consent, dict) else None
        if not isinstance(accept_from, list):
            E(nid, f"profile {prof!r}: workflow_team.json needs an 'accept_from' list of "
                   f"launcher profile names; launcher {launcher!r} is not accepted")
        elif launcher not in accept_from:
            E(nid, f"profile {prof!r} does not accept launcher {launcher!r}: its "
                   f"workflow_team.json accept_from is {json.dumps(accept_from)} "
                   "(the TARGET profile must list its launcher — delegation, not isolation)")
    return errs

def requires_errors(nodes, parents=None):
    """1.1 (RATIFY F4) structural validation of `requires` on agent/gate nodes, called by
    validate_graph_errors for every typed agent/gate node that carries the key. Returns
    [{node, field, msg}]. Rules: value is an object `{"<ancestor>": ["field",
    "dotted.path", ...]}`; every key must be in the node's `after` closure (transitive;
    `parents` = {id: [direct parent ids]} — built from the nodes' own `after` lists when
    omitted); every entry of the path list a non-empty string (and the list non-empty).
    A graph that WANTS skip-on-missing uses the `when` gate + on_skip:prune, not requires."""
    errs = []
    def E(nid, field, msg):
        errs.append({"node": nid, "field": field, "msg": msg})
    nodes = [n for n in (nodes or []) if isinstance(n, dict)]
    idset = {n.get("id") for n in nodes if n.get("id")}
    if parents is None:
        parents = {n["id"]: [a for a in n.get("after", []) if a in idset]
                   for n in nodes if n.get("id")}
    else:
        # validate_graph_errors passes ALL nodes' ancestry, including echo nodes:
        # an echo between a producer and consumer is still part of the closure.
        idset.update(parents)
    for n in nodes:
        if "requires" not in n:
            continue
        nid = n.get("id")
        req = n["requires"]
        if not isinstance(req, dict) or not req:
            E(nid, "requires", "requires must be a non-empty object "
                               '{"<ancestor>": ["field", "dotted.path", ...]}')
            continue
        closure, stack = set(), list(parents.get(nid) or n.get("after") or [])
        while stack:
            a = stack.pop()
            if a in closure or a not in idset:
                continue
            closure.add(a)
            stack.extend(parents.get(a, []))
        for anc, paths in req.items():
            if not isinstance(anc, str) or anc not in closure:
                E(nid, "requires", f"requires key {anc!r} is not an ancestor in this node's "
                                   "`after` closure (requires is an input edge: only committed "
                                   "upstream outputs may be required)")
                continue
            if not isinstance(paths, list) or not paths:
                E(nid, f"requires.{anc}", f"requires[{anc!r}] must be a non-empty list of "
                                           "field path strings (\"field\" or \"dotted.path\")")
                continue
            for i, p in enumerate(paths):
                if not isinstance(p, str) or not p.strip():
                    E(nid, f"requires.{anc}", f"requires[{anc!r}][{i}] {p!r} must be a "
                                               "non-empty field path string")
    return errs

ID_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")

# Closed grammar (Q2): an unknown key is a REJECTED key, never a silently ignored one.
# `tier` is in the agent set because resolve_models stamps it at run/amend (test_tiers
# locks it) and the runner re-validates saved graphs — the door must never reject a
# graph it baked itself. `reasoning` is validated per node (Q5).
AGENT_KEYS = {"id", "type", "after", "goal", "context", "schema", "model", "provider", "toolsets",
              "max_turns", "timeout", "run_budget", "inputs", "fanout", "reasoning",
              "tier", "shape", "repo",
              # #24/#25: fail-closed pinned routes. Default TRUE for nodes
              # that pin an explicit model — a submit ping that AFFIRMATIVELY proves
              # the pinned route dead or answering from the fallback ladder refuses the
              # launch; `false` = explicit opt-in to the ladder. (The door's
              # `route_verified` proof-annotation is door-baked AFTER validation; it
              # lives in the validator's set so the runner accepts the committed
              # graph, but _resolve_models drops any author/pre-submit value — only
              # this submit's ping (or a frozen committed restore) can prove a route.)
              "require_route", "route_verified",
              # 1.1 (RATIFY F2/F4): OPTIONAL team keys. `profile` = run this node AS a named
              # teammate profile (consent-gated, node-level only); `requires` = output
              # preconditions on ancestors ({"<ancestor>": ["field", "dotted.path", ...]}).
              # e68544a37be37657: `after_partial` (bool) opts this node INTO consuming a
              # harvest-on-death `partial` ancestor — a plain after-edge blocks on one
              # (typed fail at the wave boundary, never a silent release, never a spawn).
              "profile", "requires", "after_partial"}
GATE_KEYS = {"id", "type", "after", "question", "options", "context", "when", "wait", "on_skip",
             "default_option", "hold_timeout",
             # 1.1 (RATIFY F4): gates take output preconditions too; gates obey the same
             # after_partial law as agents (e68544a37be37657).
             "requires", "after_partial"}
ECHO_KEYS = {"id", "type", "after", "output"}
# 1.1 (RATIFY F5): opt-in library provenance block, written by the door's `save` ONLY when
# `source` is supplied or the saving door runs under a named profile. Top-level graph key.
PROVENANCE_KEYS = {"owner", "source", "saved_at", "source_digest"}

# ---------- library entry normalizer (#50, R10 migration law) ----------
# A library file is either the 1.1 BARE form (the graph object itself — the bytes
# every pre-#50 `save` wrote, which must keep loading and listing verbatim) or the
# #50 ENVELOPE {"meta": {description?, tags?}, "graph": {...}}. Anything else is an
# UNKNOWN shape: the door QUARANTINES the entry — listed with a typed refusal reason,
# never a crash, never replayable (F-2 #62: one corrupt file must not take discovery,
# the typo nudge, or /wf down with it). Returns {meta, graph, description, tags,
# envelope} for a usable entry, or {"invalid": "invalid: <why>"} for a refused one —
# always a dict, callers key on the "invalid" marker / the presence of "graph".
def library_entry(data):
    if not isinstance(data, dict):
        return {"invalid": "invalid: not a JSON object"}
    if isinstance(data.get("graph"), dict):
        if isinstance(data.get("nodes"), list):
            return {"invalid": "invalid: ambiguous file — carries both envelope"
                               " (graph:) and bare (nodes:) markers"}
        meta = data.get("meta")
        meta = meta if isinstance(meta, dict) else {}
        graph = data["graph"]
        envelope = True
    elif isinstance(data.get("nodes"), list):
        meta, graph, envelope = {}, data, False
    else:
        return {"invalid": "invalid: neither a bare graph (no nodes[] list)"
                           " nor a {meta, graph} envelope"}
    if not graph.get("nodes") or not isinstance(graph.get("nodes"), list):
        return {"invalid": "invalid: graph has no non-empty nodes[] list"}
    for i, n in enumerate(graph["nodes"]):
        if not isinstance(n, dict):
            return {"invalid": f"invalid: nodes[{i}] is not an object"}
    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        description = graph.get("description")
    tags = meta.get("tags")
    tags = [t for t in tags if isinstance(t, str) and t.strip()] \
        if isinstance(tags, list) else []
    return {"meta": meta, "graph": graph, "description": description,
            "tags": tags, "envelope": envelope}
# #32 (publish-as-file): top-level `grammar` names the dialect a shared file was written
# in. Absent = "wf/1" (every pre-#32 file is a wf/1 file); unknown = fail-closed with the
# reader's supported list, so a newer dialect is refused honestly instead of misrun.
# An ANNOTATION like `provenance`: top-level only, never part of any node, so def_hash /
# efp / graph_fingerprint / source_digest are untouched (golden-solo bytes unchanged).
GRAMMAR_DEFAULT = "wf/1"
GRAMMAR_SUPPORTED = (GRAMMAR_DEFAULT,)

def grammar_errors(graph):
    """Return [{node:None, field:'grammar', msg}] for a top-level `grammar` value this
    reader cannot run; [] when absent (back-compat wf/1) or supported."""
    if not isinstance(graph, dict) or "grammar" not in graph:
        return []
    value = graph["grammar"]
    if not isinstance(value, str) or value not in GRAMMAR_SUPPORTED:
        return [{"node": None, "field": "grammar",
                 "msg": f"unsupported grammar {value!r}; this reader supports: "
                        + json.dumps(list(GRAMMAR_SUPPORTED))
                        + f" (absent = {GRAMMAR_DEFAULT!r})"}]
    return []
FANOUT_KEYS = {"items", "items_from", "goal", "schema", "quorum"}
DEFAULTS_KEYS = {"schema", "timeout", "max_turns", "reasoning", "provider", "model", "context",
                 "require_route"}   # #25: bool — fail-closed pinned routes (see AGENT_KEYS)
# Shape presets (sprint101 #11): max_turns/timeout per rough node shape = the p95 of
# SUCCESSFUL agent nodes per shape, measured 2026-09-25 over the run dirs behind
# census.json (80 runs, 219 committed-success agent nodes; shape classified from
# node id/goal keywords). The table IS the measured p95 per shape
# (max_turns / timeout_s); samples: recon 97, build 62, review 57,
# publish 3 (thin sample — keep an eye on it).
# Explicit per-node keys always win; the preset only fills what the author left unset.
SHAPE_PRESETS = {
    "recon":   {"max_turns": 100, "timeout": 2400},
    "build":   {"max_turns": 65,  "timeout": 1500},
    "review":  {"max_turns": 65,  "timeout": 2400},
    "publish": {"max_turns": 75,  "timeout": 1500},
}
DEFAULT_SHAPE = "build"

def _defaults_errors(d):
    """Per-key rules for a graph-level `defaults:` block — the SAME checks a node key
    gets (numbers in range, reasoning from the enum, schema subset, provider needs
    model, strings for model/context). Returns [{node:None, field, msg}]."""
    errs = []
    def E(field, msg):
        errs.append({"node": None, "field": field, "msg": msg})
    if not isinstance(d, dict):
        return [{"node": None, "field": "defaults", "msg": "defaults must be an object"}]
    for k in sorted(set(d) - DEFAULTS_KEYS):
        E(f"defaults.{k}", "unknown key; allowed: " + json.dumps(sorted(DEFAULTS_KEYS)))
    for k, hi in (("timeout", 86400), ("max_turns", 200)):
        v = d.get(k)
        if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool)
                              or v <= 0 or v > hi):
            # fb-validator-duo (2026-09-26): name the offending value AND the cap — the
            # old message cited only the cap, so 'max_turns 240 vs 200' read as a riddle.
            E(f"defaults.{k}", f"{k} {v!r} exceeds cap {hi} (must be a number in (0, {hi}])")
    if d.get("reasoning") is not None and d["reasoning"] not in reasoning_levels():
        E("defaults.reasoning", f"reasoning {d['reasoning']!r} invalid; allowed: "
                                f"{list(reasoning_levels())}")
    if d.get("schema") is not None and not isinstance(d["schema"], dict):
        E("defaults.schema", "schema must be an object")
    if d.get("model") is not None and not isinstance(d.get("model"), str):
        E("defaults.model", "model must be a string")
    if d.get("require_route") is not None and not isinstance(d.get("require_route"), bool):
        E("defaults.require_route", f"require_route {d['require_route']!r} must be a boolean")
    if "provider" in d:
        p = d.get("provider")
        if not isinstance(p, str) or not p or p.strip() != p:
            E("defaults.provider", "provider must be a non-empty provider id without "
                                   "surrounding whitespace")
        m = d.get("model")
        if not isinstance(m, str) or not m.strip():
            E("defaults.provider", "provider requires a non-empty model")
    if d.get("context") is not None and not isinstance(d["context"], str):
        E("defaults.context", "context must be a string")
    return errs

def apply_graph_defaults(graph):
    """Bake run-level `defaults` + per-node `shape` presets into the agent node defs,
    called by the door BEFORE graph.json is written: the runner and every fingerprint
    then see ONE resolved truth (no second resolution path to drift). Precedence:
    explicit node key > node shape preset > graph defaults. `defaults.context` is the
    shared preamble, prepended once to each agent node's own context. Returns the new
    graph (defaults key stays on it; it is idempotent to re-apply). Raises ValueError
    with the error list on invalid shape/defaults (door validates first; this is the
    runner's load-time net)."""
    graph = graph if isinstance(graph, dict) else {"nodes": graph}
    defaults = graph.get("defaults") or {}
    errs = _defaults_errors(defaults)
    if errs:
        raise ValueError(json.dumps(errs))
    nodes = []
    for n in graph.get("nodes", []):
        n = dict(n)
        if n.get("type", "agent") == "agent":
            if n.get("shape") is not None and n["shape"] not in SHAPE_PRESETS:
                raise ValueError(json.dumps(
                    [{"node": n.get("id"), "field": "shape",
                      "msg": f"shape {n['shape']!r} invalid; allowed: "
                             f"{sorted(SHAPE_PRESETS)}"}]))
            preset = SHAPE_PRESETS.get(n.get("shape", DEFAULT_SHAPE), {})
            for k in ("max_turns", "timeout"):
                if n.get(k) is None:
                    # precedence: an author-named shape preset is per-node
                    # intent and wins; otherwise graph defaults fill, with the
                    # DEFAULT_SHAPE preset as the floor ([D] smart default).
                    v = preset.get(k) if n.get("shape") is not None else \
                        defaults.get(k, preset.get(k))
                    if v is not None:
                        n[k] = v
            for k in ("schema", "reasoning", "provider", "model"):
                if n.get(k) is None and defaults.get(k) is not None:
                    n[k] = defaults[k]
            # #25: `require_route` fills from defaults like any defaults key, but is
            # NEVER baked when both author and defaults left it unset — the runner
            # treats absent as the effective default (True on pinned nodes). Baking
            # it would move solo user-visible bytes on every graph.json.
            if n.get("require_route") is None and "require_route" in defaults:
                n["require_route"] = defaults["require_route"]
            pre = defaults.get("context") or ""
            if pre and not str(n.get("context") or "").startswith(pre):
                n["context"] = pre + ("\n\n" + n["context"] if n.get("context") else "")
        nodes.append(n)
    return dict(graph, nodes=nodes)

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
    node ids double as filenames.
    #32: accepts a whole graph object too — `{grammar?, nodes:[...]}` — in which case
    the top-level `grammar` tag is checked first (absent = wf/1; unknown = refused,
    listing the supported values) and then its `nodes`. A bare node list is unchanged."""
    errs = []
    if isinstance(nodes, dict):
        errs.extend(grammar_errors(nodes))
        nodes = nodes.get("nodes")
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
        return errs + [{"node": None, "field": "nodes", "msg": "nodes must be a non-empty list"}]
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
        if n.get("type") not in ("agent", "gate", "echo"):
            E(nid, "type", "type must be agent|gate|echo")
            continue  # per-type key grammar is undefined without a type
        _type_keys = {"agent": AGENT_KEYS, "gate": GATE_KEYS, "echo": ECHO_KEYS}[n["type"]]
        for k in sorted(set(n) - _type_keys):
            # dedicated errors below own these keys (clearer messages, no double-report)
            if n["type"] == "agent" and k == "wait":
                continue
            if n["type"] == "gate" and k == "inputs":
                continue
            if n["type"] == "agent" and k == "when":
                E(nid, "when", "only gate nodes take when; use a gate with on_skip:prune to branch")
                continue
            if k == "after_partial":
                continue  # the dedicated block below names the key (echo-meaningless / bool)
            E(nid, k, "unknown key; allowed: " + json.dumps(sorted(_type_keys)))
        for a in n.get("after", []):
            if a not in idset:
                E(nid, "after", f"references unknown 'after': {a}")
        if "after_partial" in n:
            # e68544a37be37657: agent/gate-only key; bool only — an unvalidated
            # truthy is never enough to open a harvest edge. Echo rejects it
            # explicitly (its closed set also flags it unknown) so the error
            # NAMES the key, per the issue's validation contract.
            if n["type"] == "echo":
                E(nid, "after_partial", "after_partial is meaningless on echo "
                                        "nodes (agent/gate only)")
            elif not isinstance(n["after_partial"], bool):
                E(nid, "after_partial", "after_partial must be a boolean "
                                        "(true = this node consumes a partial ancestor's harvest)")
        for k, hi in (("timeout", 86400), ("max_turns", 200), ("run_budget", 86400)):
            v = n.get(k)
            if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0 or v > hi):
                # fb-validator-duo (2026-09-26): value AND cap in every numeric-bound
                # rejection; the parenthetical is kept for substring-matchers.
                E(nid, k, f"{k} {v!r} exceeds cap {hi} (must be a number in (0, {hi}])")
        if n.get("reasoning") is not None:
            lv = n["reasoning"]
            if lv not in reasoning_levels():
                E(nid, "reasoning", f"reasoning {lv!r} invalid; allowed: "
                                    f"{list(reasoning_levels())}")
        if n["type"] == "gate" and n.get("options") is not None:
            opts = n["options"]
            if not isinstance(opts, list) or not opts \
                    or not all(isinstance(o, str) and o.strip() for o in opts):
                E(nid, "options", "gate options must be a non-empty list of non-empty strings "
                                  "(or omit the key for a free-form answer)")
        if n["type"] == "gate":
            # sprint101 #14: gate defaults are validated at the door, never discovered at the wall.
            dopt = n.get("default_option")
            if dopt is not None:
                opts = n.get("options")
                if not isinstance(dopt, str) or not dopt.strip():
                    E(nid, "default_option", "default_option must be a non-empty string")
                elif not isinstance(opts, list) or dopt not in opts:
                    E(nid, "default_option", f"default_option {dopt!r} must be one of the gate's options")
                if n.get("wait") is not None:
                    E(nid, "default_option", "default_option applies to human gates, not machine wait-gates")
            hto = n.get("hold_timeout")
            if hto is not None and (not isinstance(hto, (int, float)) or isinstance(hto, bool) or hto <= 0):
                E(nid, "hold_timeout", "hold_timeout must be a positive number of seconds")
            # #59 (fb-fix ledger 97e90c2205f17fb0): string-typed gate keys are
            # TYPE-checked at submit, never discovered at the wall — a dict/list
            # question reached the held-card and desktop as a React child crash, and
            # a non-str context reached the event line and downstream concat. The
            # optional keys stay OPTIONAL (absent or '' legal) but a key that is
            # PRESENT must be a str — explicit null is a present non-str, rejected
            # like the rest (ra-59 review finding 2: string-when-present contract).
            if "question" in n and not isinstance(n["question"], str):
                E(nid, "question", f"question {n['question']!r} must be a string")
            if "context" in n and not isinstance(n["context"], str):
                E(nid, "context", f"context {n['context']!r} must be a string")
        if n["type"] == "agent":
            # #59 (fb-fix ledger 97e90c2205f17fb0): the string-typed agent keys
            # are TYPE-checked at submit — a list/dict `context` or non-str `goal`
            # passed the truthy-only check and died at FIRST spawn in run_child's
            # prompt concat ('TypeError: can only concatenate str', error_class
            # 'crashed', burned gate release). Mirror the fanout item-goal law
            # (:592): named-node errors, no coercion at resolve (closed-grammar law,
            # :274). PRESENT non-str (incl. [], {}, 0, False, None) is rejected
            # independently of truthiness — the ra-59 review found the first cut
            # still let falsy goals through to a created run dir. ABSENT goal keeps
            # the exact legacy 'agent node has no goal' message below; a present
            # str that is empty/whitespace keeps that legacy message too (absent-
            # equivalent), preserving test_validate_0923's pin.
            if "goal" in n:
                g = n["goal"]
                if not isinstance(g, str):
                    E(nid, "goal", f"goal {g!r} must be a non-empty string")
                elif n.get("fanout") is None and not g.strip():
                    # empty/whitespace-only str on a PLAIN agent is an absent goal:
                    # '' keeps the exact legacy message (test_validate_0923 pin);
                    # whitespace-only is the same non-empty law. A fan-out node's
                    # own goal may legally stay empty when fo.goal or every item
                    # carries the real text (spawn: `fo.get("goal") or n.goal`).
                    E(nid, "goal", "agent node has no goal" if not g
                                   else f"goal {g!r} must be a non-empty string")
            ctx = n.get("context")
            if "context" in n and not isinstance(ctx, str):
                # explicit null is a present non-str: the string-when-present
                # contract admits only absent or str (review finding 2)
                E(nid, "context", f"context {ctx!r} must be a string")
            shp = n.get("shape")
            if shp is not None and shp not in SHAPE_PRESETS:
                E(nid, "shape", f"shape {shp!r} invalid; allowed: {sorted(SHAPE_PRESETS)}")
            rp = n.get("repo")
            # deep review #29 F3: a mistyped `repo` must never silently disable the
            # lane-clean gate it opts into (123/["x"]/{...}/"" all read as no-declaration
            # downstream and the node commits `done` over a dirty lane, fail-open).
            if rp is not None and (not isinstance(rp, str) or not rp.strip()
                                   or rp.strip() != rp):
                E(nid, "repo", "repo must be a non-empty path string without surrounding whitespace")
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
                    elif fo.get("items") is None and not isinstance(fo.get("items_from"), str):
                        E(nid, "fanout.items_from", "fanout.items_from must be a "
                                                    "'<node_id>.<dotted.path>' string")
                    if fo.get("items") is not None and not isinstance(fo["items"], list):
                        E(nid, "fanout.items", "fanout.items must be a list")
                    items = fo.get("items") if isinstance(fo.get("items"), list) else []
                    for i, it in enumerate(items):
                        if isinstance(it, dict) and "goal" in it and not (isinstance(it["goal"], str) and it["goal"].strip()):
                            E(nid, f"fanout.items[{i}].goal", f"fanout.items[{i}].goal must be a non-empty string (it overrides fanout.goal)")
                    # #59: the goal TEMPLATE is rendered by fmt_goal (re.sub over the
                    # text) and prefixed onto the node goal per item — a truthy
                    # non-str here is the same first-spawn TypeError class as the
                    # item-goal law directly above; mirror that style (R8 sibling).
                    # A PRESENT key must be a str regardless of truthiness; '' /
                    # absent remain the documented "fall back to the node goal"
                    # shape (run_child: `fo.get("goal") or node.get("goal")`).
                    if "goal" in fo and not isinstance(fo["goal"], str):
                        E(nid, "fanout.goal", f"fanout.goal {fo['goal']!r} must be a "
                                              "non-empty string (the item goal template)")
                    if items and not (fo.get("goal") or n.get("goal")) \
                            and not all(isinstance(it, dict) and isinstance(it.get("goal"), str) for it in items):
                        E(nid, "fanout.goal", "fanout needs a goal template or a goal on every item")
                    # (moved above: the template type check sits with the other
                    # fanout checks; this block only reports the missing-goal law)
                    q = fo.get("quorum")
                    if q is not None and (not isinstance(q, int) or isinstance(q, bool) or q < 1):
                        E(nid, "fanout.quorum", "fanout.quorum must be a positive int")
                    if fo.get("items") is None and isinstance(fo.get("items_from"), str):
                        head = fo["items_from"].split(".")[0]
                        if head == nid or head not in idset or head not in n.get("after", []):
                            E(nid, "fanout.items_from",
                              f"fanout.items_from ref {fo['items_from']!r} head {head!r} must be an "
                              f"ancestor — a node in this node's `after` list "
                              f"(its committed output feeds the fan-out)")
                    fsc = fo.get("schema")
                    if fsc is not None:
                        if not isinstance(fsc, dict):
                            E(nid, "fanout.schema", "fanout.schema must be an object")
                        else:
                            schema_check(nid, "fanout.schema", fsc)
            elif "goal" not in n:
                # #59: present-but-bad goals are reported by the typed check above
                # (one named error per defect); this legacy branch owns only the
                # ABSENT goal on a non-fan-out agent, message pinned by
                # test_validate_0923 / test_string_type_validation_59.
                E(nid, "goal", "agent node has no goal")
            if n.get("require_route") is not None and not isinstance(n.get("require_route"), bool):
                # #25: boolean only — an unknown truthy value must not silently
                # disable (or enable) the fail-closed route gate.
                E(nid, "require_route", f"require_route {n['require_route']!r} must be a boolean")
            if n.get("schema") is not None:
                if not isinstance(n["schema"], dict):
                    E(nid, "schema", "schema must be an object")
                else:
                    schema_check(nid, "schema", n["schema"])
        if n["type"] == "echo":
            # #59: echo commits `output` VERBATIM (the documented contract). The
            # shapes downstream consumes are JSON values (fixtures and examples
            # author dicts/lists — a str-only law would kill the feature), so the
            # submit law is JSON-typed: anything json.dumps cannot encode (a set,
            # a custom object) crashes the door's own graph.json write or the
            # runner's node commit as an unclassified crash — refuse it here,
            # named-node, like every other defect.
            o = n.get("output")
            try:
                json.dumps(o)
            except (TypeError, ValueError):
                E(nid, "output", f"echo output {o!r} must be a JSON-serialisable "
                                 f"value ({type(o).__name__} cannot be committed verbatim)")
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
        anc = set()
        if (n.get("when") is not None and n["type"] == "gate") or n.get("inputs") is not None:
            stack = list(n.get("after", []))
            while stack:
                a = stack.pop()
                if a in anc or a not in idset:
                    continue
                anc.add(a)
                stack.extend(parents[a])
        if n.get("when") is not None and n["type"] == "gate":
            err = when_expr_ok(n["when"])
            if err:
                E(nid, "when", err)   # parse-only (syntax mode is total): NO head check on a broken expr
            else:
                # `when` reads out.<ancestor>.<path> (references/grammar.md). Parse-only
                # when_expr_ok cannot see heads (sentinel operands), so a non-ancestor
                # head — sibling, typo, ghost — would validate clean and resolve to
                # None at fire time: False ⇒ silent skip (default on_skip:prune = dead
                # branch), True ⇒ holds, depending on unrelated commit order. Validate
                # the ref heads against the SAME ancestry closure `inputs` uses below.
                for tok in _tok_when(n["when"]):
                    if tok.startswith("out."):
                        head = tok.split(".")[1]
                        if head not in anc:
                            E(nid, "when", f"when ref {tok!r} head {head!r} is not an existing "
                                           f"node in its `after` ancestry (when must descend from it)")
        ins = n.get("inputs")
        if ins is not None:
            if n["type"] == "gate":
                E(nid, "inputs", "gates cannot have inputs")
            elif not isinstance(ins, list) or not all(isinstance(x, str) and x.strip() for x in ins):
                E(nid, "inputs", "inputs must be a list of non-empty ref strings")
            else:
                for ref in ins:
                    head = ref.split(".")[0]
                    if head not in anc:
                        E(nid, "inputs", f"inputs ref {ref!r} head {head!r} is not an existing "
                                         f"node in its `after` ancestry (inputs must descend from it)")
    # 1.1 (RATIFY F4): output preconditions — structural check, ancestry via `parents`.
    # Only typed agent/gate nodes reach here (echo's closed key set already rejected it).
    errs.extend(requires_errors([n for n in nodes if n.get("type") in ("agent", "gate")], parents))
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

def runner_lock_held(r):
    """91b9a3de: cross-container liveness truth. The runner takes an exclusive
    blocking flock on <run>/runner.lock for its whole life (wf.py acquire_lock)
    — and flock is enforced by the KERNEL across every pid namespace that shares
    the mount, so it holds even when the runner lives in a sibling container (our
    fleet: shared ~/.hermes volume, separate pid namespaces). os.kill(pid, 0)
    CANNOT see those pids: the same pid reads as dead here while it is very much
    alive next door, and a wait-based caller respawns a second runner over live
    children (the fb-squad false-'interrupted' class). Probe: LOCK_EX|LOCK_NB on
    the lock file; getting the lock means nobody holds it (the fd closes on return
    and the kernel releases it). Deliberately NO O_CREAT: a read path (act_list
    probes every run dir) must never litter empty lock files into historical runs
    — a missing file is exactly as honest an absence of a holder as an
    uncontended one. Missing file / unknown errors are honest ABSENCE of a holder
    (False), never a liveness claim."""
    try:
        import fcntl
        fd = os.open(os.path.join(str(r), "runner.lock"), os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return False
        except OSError:
            return True
        finally:
            os.close(fd)
    except OSError:
        return False

def _runner_pid_alive(r, pid_path=None):
    """A pid is not ownership: verify a live, non-zombie `wf.py run <id>`.
    /proc gives argv and (when readable) the runner's environment; ps supplies macOS/BSD.
    Unknown identity is NOT evidence of a running workflow.
    1.1 (RATIFY F1/B3): the environment check compares the runner's EFFECTIVE runs root
    with this run's parent: `WF_RUNS_ROOT` (when the runner has one) must equal `r.parent`;
    otherwise the 1.0.15 comparison `HERMES_HOME == r.parent.parent` applies verbatim."""
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
                env = {}
                for entry in environ:   # first occurrence wins (as the legacy homes[0] did)
                    k, sep, v = entry.partition(b"=")
                    if sep and k in (b"HERMES_HOME", b"WF_RUNS_ROOT") and k not in env:
                        env[k.decode()] = v.decode(errors="replace")
                # #42: an owner-pinned settings.runs_root is the ONE root every process of
                # the estate runs under — the runner's env is judged against it. Otherwise
                # the 1.1 / 1.0.15 comparisons apply VERBATIM.
                try:
                    pinned = settings_runs_root()
                except ValueError:
                    pinned = None   # liveness is a read path: a bad setting is the door's error
                if pinned is not None:
                    if pinned.resolve() != r.parent.resolve():
                        return False
                elif env.get("WF_RUNS_ROOT"):
                    # the runner runs under an explicit runs root: it must BE this run's parent
                    if Path(env["WF_RUNS_ROOT"]).resolve() != r.parent.resolve():
                        return False
                elif env.get("HERMES_HOME"):
                    # legacy env: the 1.0.15 comparison, unchanged (effective root is
                    # HERMES_HOME/workflows, i.e. HERMES_HOME == r.parent.parent)
                    if Path(env["HERMES_HOME"]).resolve() != r.parent.parent.resolve():
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

def runner_alive(r, pid_path=None):
    """91b9a3de: ONE liveness law, cross-container safe. The runner holds an
    exclusive flock on <run>/runner.lock for its whole life, and flock is
    kernel-enforced across every pid namespace sharing the mount — so the probe
    reads a sibling-container runner (our fleet: shared ~/.hermes volume, separate
    pid namespaces) as LIVE where os.kill(pid, 0) alone sees a ghost and a
    next=wait would spawn a second runner over live children. Law: HELD lock =>
    live, unconditionally (the holder proved itself by taking the lock, whatever
    its pid namespace). Otherwise fall back to the ORIGINAL pid-identity law
    verbatim (argv `wf.py run <id>` + effective-root match), so a lock file no
    one holds, or a foreign/crashed pid, behaves exactly as before. The flock
    half fails CLOSED: a held probe can only ever ADD liveness, never remove it."""
    if runner_lock_held(r):
        return True
    return _runner_pid_alive(r, pid_path)

def fingerprint_valid(stored, actual, rule):
    """A record's own rule is authoritative; an unstamped record matches ANY rule.

    A run-level stamp cannot attest to commits after a mixed-version resume, so
    only a record's OWN stamp is trusted outright. For unstamped (pre-1.0.12)
    records, a match under ANY rule proves the definition is unchanged in that
    rule's view (rule 1 = fully unchanged; rule 2 = unchanged modulo budgets,
    which def_hash treats as not-work). Fail-closed is ZERO matches: an
    ambiguity where two rules AGREE on the same stored hash re-spawns 25
    committed nodes and buys no safety (a real definition change matches none).
    """
    if rule is not None:
        return type(rule) is int and rule in FP_RULES and stored == actual(rule) and stored is not None
    matches = [v for v in FP_RULES if stored is not None and stored == actual(v)]
    return len(matches) >= 1

def record_efp_valid(rec, byid, node, field="efp"):
    return isinstance(rec, dict) and ("fp_rule_version" not in rec or
                                      (type(rec["fp_rule_version"]) is int and rec["fp_rule_version"] in FP_RULES)) and fingerprint_valid(
        rec.get(field), lambda rule: efp(byid, node, rule=rule), rec.get("fp_rule_version"))

def runner_exit_read(r, pid_path=None):
    """Graph-bound runner verdict, or a crash when a previous pid lacks identity.
    No pid file means a fresh, not-yet-spawned run, not a crash."""
    rec = jload(Path(r) / "runner_exit.json")
    if isinstance(rec, dict) and rec.get("reason"):
        current_graph = jload(Path(r) / "graph.json")
        if ("fp_rule_version" in rec and rec["fp_rule_version"] not in FP_RULES) or not fingerprint_valid(rec.get("graph_fingerprint"),
                                 lambda rule: graph_fingerprint(current_graph, rule=rule),
                                 rec.get("fp_rule_version")):
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
    if not rec or "efp" in rec or not fingerprint_valid(
            rec.get("def_hash"), lambda rule: def_hash(n, rule), rec.get("fp_rule_version")):
        return False
    return all(a not in byid or _legacy_chain_unchanged(r, byid[a], byid)
               for a in n.get("after", []))

def node_rec(r, n, byid):
    """Return (status, rec): done|partial|failed|pending. Stale (efp mismatch after an
    amend) == pending — its stored result must never be presented as current.
    Legacy (pre-efp) records carried def_hash only; a bare stamp is a downgrade
    attack on the validity law, so the whole ancestor chain must be proven
    unchanged legacy commits. `partial` (#4 harvest-on-death) IS a commit:
    partial output is committed output, downstream may consume it."""
    rec = jload(r / "nodes" / f"{n['id']}.json")
    st = (rec or {}).get("status")
    if st == "failed" and (rec or {}).get("error_class") == "cancelled":
        return "pending", rec   # stop != failure (#7): a resume re-drives cancelled work
    if st in ("done", "partial", "failed", "skipped"):
        if record_efp_valid(rec, byid, n):
            return st, rec
        if "efp" not in rec and _legacy_chain_unchanged(r, n, byid):
            return st, rec
        return "pending", rec
    return "pending", rec

def gate_answer_valid(r, gate, byid):
    ans = jload(r / "gates" / f"{gate['id']}.json")
    if ans is None:
        return None
    if record_efp_valid(ans, byid, gate, "_def"):
        return ans
    if "fp_rule_version" in ans:
        return None
    gate_rec = jload(r / "nodes" / f"{gate['id']}.json", {}) or {}
    if "efp" not in gate_rec and "efp" not in ans:
        # Pre-efp answers require a uniquely attributable historical definition
        # and a chain of equally verified pre-efp ancestor commits.
        if not fingerprint_valid(ans.get("_def"), lambda rule: def_hash(gate, rule), None):
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
        if st == "partial" and n.get("after_partial"):   # the opt-in consumes the harvest
            continue                                     # e68544a37be37657
        if st in ("done", "skipped"):
            continue
        m = (nodes_meta or {}).get(a) or {}
        if st == "failed":
            word = "failed"
        elif st == "partial":
            # #4 + e68544a37be37657: a harvest does NOT satisfy a plain after-edge —
            # it is an unfinished ancestor until the descendant opts in.
            word = "partial (harvested; needs after_partial)"
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

def dep_satisfied(states, a, allow_partial=False):
    """After-edge release law. #4 (harvest-on-death) keeps a `partial` ancestor's
    OUTPUT committed and consumable, but e68544a37be37657 ends the equivalence
    with `done` for RELEASE: a plain after-edge is NOT satisfied by a `partial`
    (the child died mid-work — releasing verify/suite onto an incomplete
    candidate is the false-green class). A descendant that genuinely wants the
    harvest opts in per-node with `after_partial: true` (agent/gate key)."""
    st = states.get(a)
    if st == "partial":
        return bool(allow_partial)
    return st in ("done", "skipped")

def _verify_spawn_rec(r, n, byid, rec):
    """ONE verification law for a spawn record (790c6ad): status=running + efp
    match + pid alive (non-zombie) + the recorded skey title present in the
    process's argv. Returns the verified identity
    {pid, skey, started, attempt, log_path} or None. The skey-in-cmdline check
    is the PID-reuse guard and is NEVER relaxed: unknown identity is not proof
    of an active child. Shared by _active_spawns (display path) and
    active_child (runner adoption) so runner and read model can never disagree.
    """
    if not isinstance(rec, dict) or rec.get("status") != "running" \
            or not record_efp_valid(rec, byid, n):
        return None
    pid, skey = rec.get("pid"), rec.get("skey")
    if not isinstance(pid, int) or pid <= 0 or not isinstance(skey, str) or not skey:
        return None
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
            return None
    except (OSError, IndexError, ValueError, subprocess.SubprocessError):
        return None  # unknown identity is not proof of an active child
    return {**{k: rec[k] for k in ("pid", "started", "attempt", "log_path") if k in rec},
            "skey": title}

def _active_spawns(r, n, byid):
    """All verified uncommitted child identities, never historical DB liveness."""
    records = [r / "nodes" / f"{n['id']}.json"]
    if n.get("fanout"):
        records.extend(sorted((r / "nodes").glob(f"{n['id']}.[0-9]*.json")))
    active = []
    for path in records:
        v = _verify_spawn_rec(r, n, byid, jload(path))
        if v:
            active.append(v)
    return active

def active_child(r, n, byid, index=None):
    """Per-item entry point to the verification law (790c6ad): the runner's
    fan-out branch calls this BEFORE Popen on a resumed runner — a verified live
    orphan (status=running record + efp match + pid alive + skey in argv) is
    ADOPTED, never re-spawned; a dead or unverifiable record returns None and
    the item spawns fresh. The display path (_active_spawns → run_state) shares
    the same law through _verify_spawn_rec. Returns {pid, skey, started,
    attempt, log_path} or None."""
    fname = f"{n['id']}" + (f".{index}" if index is not None else "")
    return _verify_spawn_rec(r, n, byid, jload(r / "nodes" / f"{fname}.json"))

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
        if st in ("done", "partial"):   # #4: partial output IS output for when/refs
            outputs[n["id"]] = (rec or {}).get("output")
    prune_states(graph["nodes"], states)   # derived view: pruned-but-uncommitted read as skipped
    for n in graph["nodes"]:
        st, rec = states[n["id"]], recs[n["id"]]
        active = _active_spawns(r, n, byid) if live and st == "pending" and n["type"] == "agent" else []
        nodes[n["id"]] = {"type": n["type"], "status": "running" if active else st, "after": n.get("after", []),
                          "fanout": bool(n.get("fanout")),
                          "stale_of_amend": bool(rec) and st == "pending" and rec.get("status") in ("done", "partial", "failed", "skipped") or None}
        if active:
            nodes[n["id"]]["active_spawn"] = active[0]
            nodes[n["id"]]["active_spawns"] = active
    def deps_ok(n):
        # e68544a37be37657: mirror the runner law — a plain after-edge is not
        # satisfied by a `partial`; the after_partial opt-in consumes the harvest.
        return all(dep_satisfied(states, a, allow_partial=bool(n.get("after_partial"))) for a in n.get("after", []))
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
    elif all(s in ("done", "partial", "skipped") for s in states.values()):   # #4: partial closes the run
        status = "done"
    else:
        gate = next((n for n in graph["nodes"] if n["type"] == "gate"
                     and states[n["id"]] == "pending" and deps_ok(n)), None)
        if gate and gate.get("wait") and gate_answer_valid(r, gate, byid) is None:
            # machine-answered gate: the runner is polling it — 'running', never 'held'.
            # Its blockage is self-explaining via nodes[id].parked (P4 + jury tweak).
            pk = jload(r / "gates" / f"{gate['id']}.parked.json", {}) or {}
            if live and record_efp_valid(pk, byid, gate, "_def"):
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
            # 91b9a3de companion: publish the ONE liveness read this state was
            # derived from — a second runner_alive() call a few microseconds
            # later can flip across a dying runner's kernel-released flock, and
            # status vs a re-probed alive disagreeing sent act_wait spinning a
            # respawn it then abandoned (the R6 regression shape). Consumers
            # that need liveness use THIS field.
            "runner_live": live,
            "runner_exit": exit_state,
            "started": (jload(r / "run.json", {}) or {}).get("started"),
            "owner": (jload(r / "run.json", {}) or {}).get("owner"),
            "done": sum(1 for s in states.values() if s in ("done", "skipped", "partial")),   # #4: a harvest counts done
            "skipped": sum(1 for s in states.values() if s == "skipped"), "total": len(graph["nodes"])}

# ---------- O2: the ONE node-truth read (1.1) ----------
# Closed key set read verbatim from nodes/<id>[.<i>].json. Two readers (dashboard
# _view, the door's A2 facts) share it so they can never disagree. Absent keys read
# `unknown`, never 0 (AGENTS.md rule 8). `steer` rides along from _steer_state,
# which moved here from the door — the door re-imports it (move, not copy).

FACT_KEYS = ("status", "error_class", "error", "attempts", "attempts_log", "final",
             "harvest", "output", "ms", "started", "log_path", "prompt_path", "efp", "skey")
# No-team FACT_KEYS and node_facts shape stay byte-identical. Profile facts are
# appended only when routed children actually carry them in a spawn/result record.

def precondition_facts(rec):
    """1.1 (RATIFY F4) fact rendering for a precondition failure: the string
    'failed (precondition: fix.pr_url)' listing the missing refs, or None when the record
    is not a precondition failure. The refs come from the runner-committed
    `output.missing` list; a record missing that list falls back to the text after
    'precondition unmet: ' in the error. Read model only — the runner owns the commit."""
    if not isinstance(rec, dict) or rec.get("error_class") != "precondition":
        return None
    out = rec.get("output")
    missing = out.get("missing") if isinstance(out, dict) else None
    if not (isinstance(missing, list) and missing):
        tail = str(rec.get("error") or "").split("precondition unmet:", 1)
        missing = [s.strip() for s in tail[1].split(",")] if len(tail) > 1 else []
        missing = [m for m in missing if m]
    if not missing:
        return None
    return "failed (precondition: " + ", ".join(str(m) for m in missing) + ")"

def node_child_home(r, nid, index=None):
    """The state.db HOME a node's children ran under (1.1 RATIFY F2/B7): the record's
    `profile_home` when the node was profile-routed (deriving `<profiles_root>/<profile>`
    when only `profile` survived), else None = the caller's hermes_home() — byte-identical
    for no-team runs. Absent/unreadable record → None (never guess a teammate DB)."""
    name = str(nid) + (f".{index}" if index is not None else "")
    rec = jload(Path(r) / "nodes" / f"{name}.json")
    if not isinstance(rec, dict):
        return None
    ph = rec.get("profile_home")
    if isinstance(ph, str) and ph.strip():
        return Path(ph)
    prof = rec.get("profile")
    if isinstance(prof, str) and prof.strip() and prof != "default":
        return profile_home(prof)
    return None

def node_child_metrics(r, nid, index=None):
    """Profile-aware per-node child_metrics (1.1 RATIFY F2): the SAME fold as
    child_metrics, read from the node's OWN child DB home (the target profile's state.db
    for profile-routed nodes — the launcher's DB never holds a teammate's sessions rows).
    Committed coordination seam for the runner's harvest/retry/metric sites: it is the
    one place home resolution lives (wf.py must not re-derive it). Unreadable target DB →
    {} via child_metrics — the api_calls_known:false UNKNOWN path, never zero."""
    home = node_child_home(r, nid, index)
    return child_metrics(Path(r).name, home=home)

def node_facts(r, nid, index=None):
    """Record facts for one node (fan-out item via `index`), plus its steer truth.
    None when the node has no record at all (never fabricate a record)."""
    name = str(nid) + (f".{index}" if index is not None else "")
    rec = jload(Path(r) / "nodes" / f"{name}.json")
    if not isinstance(rec, dict):
        return None
    facts = {k: (rec[k] if k in rec and rec[k] is not None else "unknown")
             for k in FACT_KEYS}
    facts["steer"] = _steer_state(Path(r), str(nid))
    if rec.get("profile"):
        facts["profile"] = rec["profile"]
        facts["profile_home"] = rec.get("profile_home") or "unknown"
    pf = precondition_facts(rec)
    if pf:
        facts["fact"] = pf
    return facts

def _steer_state(r, nid):
    """B1 + #17 evidence read model for one node: queued = lines addressed to the
    node in the run inbox; baked = how many its LATEST spawn copied into its bake
    file; consumed = how far the spawn's cursor advanced (inbox pulls; also
    echoed as `delivered` for existing readers). All derived from files only —
    no model self-report is trusted."""
    try:
        raw = [l for l in (r / "inbox.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    except OSError:
        return None
    addressed = 0
    for l in raw:
        try:
            m = json.loads(l)
        except Exception:
            continue
        if m.get("node") == nid and m.get("text") is not None and m.get("cmd") != "kill":
            addressed += 1
    rec = jload(r / "nodes" / f"{nid}.json") or {}
    baked = delivered = 0
    if (r / "steer").is_dir():
        files = sorted((r / "steer").glob(f"{nid}.a*.jsonl"),
                       key=lambda p: int(p.name[len(nid) + 2:-len(".jsonl")] or 0))
        spawn_rec = files[-1] if files else None
    else:
        spawn_rec = None
    if spawn_rec is not None:
        try:
            baked = len([l for l in spawn_rec.read_text(encoding="utf-8").splitlines() if l.strip()])
        except OSError:
            baked = 0
        cur = spawn_rec.with_name(spawn_rec.name.replace(".jsonl", ".cursor"))
        try:
            delivered = min(int(cur.read_text().strip() or "0"), baked)
        except (OSError, ValueError):
            delivered = 0
    if not addressed and not baked:
        return None
    return {"queued": addressed, "baked": baked, "consumed": delivered}

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

def blocked_legibility(nodes, states, blocked):
    """Read-only context for run.blocked: finished work that cannot converge and
    the failed roots upstream of each blocked-pending node. Reuse the same
    dependency adjacency as amend_preview; preserve graph order in every list."""
    byid = {n["id"]: n for n in nodes}
    kids = _downstream(byid)
    blocked_set = set(blocked)
    failed = [n["id"] for n in nodes if states[n["id"]] == "failed"]
    blockers = {nid: [] for nid in blocked}
    unconverged = []
    for n in nodes:
        nid = n["id"]
        if states[nid] not in ("failed", "done", "partial"):
            continue
        seen, stack = set(), list(kids[nid])
        while stack:
            child = stack.pop()
            if child in seen:
                continue
            seen.add(child)
            stack.extend(kids[child])
        hits = blocked_set & seen
        if states[nid] in ("done", "partial") and hits:
            unconverged.append(nid)
        elif nid in failed:
            for target in blocked:
                if target in hits:
                    blockers[target].append(nid)
    return unconverged, blockers

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
        if st == "pending" and (rec or {}).get("status") in ("done", "partial", "failed", "skipped"):
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
                 if status[n["id"]] in ("done", "skipped", "partial") and n["id"] not in will]
    return {"added": added, "removed": removed, "changed": changed,
            "will_rerun": will_rerun, "unchanged": unchanged}

# ---------- seat-level model floor (stdlib-only when core isn't importable) ----------

def seat_forbidden_models():
    """Read model.workflows_forbidden_models on the child seat, including bare CLI hosts.

    A malformed configured floor is not an empty ban: reject it at the door and
    fail closed at the runner. Missing config is the only opt-out.
    """
    try:
        from hermes_cli.config import load_config_readonly
        cfg = load_config_readonly()
        if cfg:
            return (cfg.get("model") or {}).get("workflows_forbidden_models", [])
    except Exception:
        pass
    home = hermes_home()
    try:
        lines = (home / "config.yaml").read_text().splitlines()
    except OSError:
        return []
    section = key = None
    values = []
    for raw in lines:
        line = raw.split(" #", 1)[0]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        text = line.strip()
        if indent == 0:
            section, key = text.partition(":")[0], None
        elif section == "model" and indent == 2:
            key, _, scalar = text.partition(":")
            if key == "workflows_forbidden_models" and scalar.strip():
                # Simple flow list is supported; malformed scalar remains malformed.
                try:
                    import json
                    return json.loads(scalar.strip())
                except (ValueError, TypeError):
                    return scalar.strip()
        elif section == "model" and key == "workflows_forbidden_models" and indent > 2:
            if text.startswith("- "):
                values.append(text[2:].strip().strip("'\""))
            else:
                return text  # malformed list, not an empty ban
    return values

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
    import sqlite3
    home = Path(home) if home else hermes_home()
    db = home / "state.db"
    if not db.exists():
        return {}
    out = {}
    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=0.5)
        try:
            have_bp = any(r[1] == "billing_provider" for r in c.execute("pragma table_info(sessions)"))
            bp_sel = "billing_provider, " if have_bp else ""
            rows = c.execute(
                f"select title, model, {bp_sel}input_tokens, output_tokens, cache_read_tokens, reasoning_tokens, "
                "api_call_count, tool_call_count, estimated_cost_usd, last_activity_at, "
                "last_activity_description, ended_at, started_at from sessions where title like ? "
                "order by title, started_at, rowid",
                (f"wf:{run_id}:%",)).fetchall()
        finally:
            c.close()
    except Exception:
        return {}
    for (title, model, *rest) in rows:
        billing_provider = None
        if len(rest) == 11:   # legacy schema (no billing_provider column): honest unknown
            (ti, to, cr, rs, api, tools, cost, last, desc, ended, started) = rest
        else:
            (billing_provider, ti, to, cr, rs, api, tools, cost, last, desc, ended, started) = rest
        key = title.split("#a", 1)[0]
        m = out.setdefault(key, {"tokens_in": 0, "tokens_out": 0, "cache_read": 0, "reasoning": 0,
                                 "api_calls": 0, "api_calls_known": True,
                                 "tool_calls": 0, "cost": 0.0, "attempts": 0,
                                 "model": None, "billing_provider": None, "last_activity": None, "last_desc": None,
                                 "ended": None, "started": None, "sessions": {}})
        m["sessions"][title] = {"last_activity": last or started,
                                "last_desc": desc or None}
        if api is None:
            m["api_calls_known"] = False
        m["tokens_in"] += ti or 0; m["tokens_out"] += to or 0; m["cache_read"] += cr or 0
        m["reasoning"] += rs or 0; m["api_calls"] += api or 0; m["tool_calls"] += tools or 0
        m["cost"] += cost or 0.0; m["attempts"] += 1
        m["model"] = model or m["model"]
        m["billing_provider"] = billing_provider or m["billing_provider"]
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
