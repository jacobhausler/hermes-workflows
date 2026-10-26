#!/usr/bin/env python3
"""#456 item2 (est-v367p): every allow-listed private-core import degrades, never
raises. The R2 companion of tests/test_private_core_imports.py (item1, the lint
allow-list): where item1 pins WHICH (file, target) rows the upstream
`hermes plugins validate` private-import lint may report, THIS test pins the
promise behind every row — under both failure shapes of each private module the
importing function returns its documented fallback, never an exception.

Issue #456 R2 probe-verified the table below once, by hand, against core
v0.22.2; this file re-runs the probe on every suite pass. Fallbacks pinned per
row (both modes):

| Site (function)                | Modules blocked            | Fallback under degradation          |
|--------------------------------|----------------------------|-------------------------------------|
| door _route_efforts            | agent.reasoning_effort     | wfcommon.reasoning_levels()         |
| door _nearest_effort           | agent.reasoning_effort     | None                                |
| door _alias_provider_pair      | hermes_cli.model_switch    | (None, None)                        |
| door _import_call_llm          | agent.auxiliary_client     | raises BY DESIGN (callers degrade)  |
|   caller _ping_route_once      |   "                        | liveness "unknown", note says so    |
|   caller _ping_reachable       |   "                        | False                               |
| door _ping_retry_after         | agent.retry_utils          | None                                |
| door _session_env              | gateway.session_context    | os.environ value ("" when unset)    |
| runner _resolve_child_reasoning| agent.reasoning_effort     | clamped on the wfcommon table       |
| runner _filter_child_toolsets  | toolsets + hermes_cli.plugins | names pass through verbatim      |
| wfcommon _yaml_load            | hermes_yaml                | ruamel, else PyYAML (chain verbatim)|
| string site _PING_SUBPROCESS   | agent.auxiliary_client     | guarded INSIDE the string: prints   |
|   (not visible to the lint)    |                            | {"unavailable": true}, exit 0       |

Line numbers from the issue's lint output are NOT keys — function names are
(they drifted once already between the probe and this commit).

Modes, exactly as the issue's probe ran them, per fresh subprocess (each site is
probed in a virgin interpreter so module-level state can neither poison the
next site nor hide a one-shot import failure):
  absent  — sys.modules[<mod>] = None          (import of X halted; None in sys.modules)
  renamed — module present, symbol gone        (ImportError: cannot import name)
Dotted fake parents are installed in BOTH modes: without them a core-less host
fails the PARENT import (ModuleNotFoundError, first) and the child-block leg is
never exercised — the fake parents make both modes arrive at the block itself
raising. The shape it raises is CPython-version-flavored (ImportError halted-None
vs ModuleNotFoundError), and for _ping_route_once the second shape legitimately
selects the core-less-cron-door leg (the subprocess ping). The probe STUBS
_ping_subprocess before the call — no leg of this test can ever launch the
subprocess ping or touch the network — and asserts the row's promise: the caller
never raises and answers liveness "unknown" whichever honest leg served.

Conventions (repo test style): stdlib only; PASS/FAIL lines; exit 0 = green;
runs with or without core on the host (that is the whole point); one SKIP-OK
leg (yaml_load on a host with neither ruamel nor PyYAML — the chain then raises
by design, which the probe asserts instead of the parse).

Run:  python3 tests/test_private_core_imports_softguard.py   (from the repo root)
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# the probe: runs ONE site in ONE mode, prints exactly one PROBE-OK/-FAIL line
# ---------------------------------------------------------------------------
PROBE = r'''
import contextlib
import importlib
import io
import json
import os
import sys
import types

SITE, MODE, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, REPO)

PRIVATE8 = ("agent.reasoning_effort", "agent.auxiliary_client", "agent.retry_utils",
            "hermes_cli.model_switch", "hermes_cli.plugins", "toolsets",
            "gateway.session_context", "hermes_yaml")
MODS = {
    "route_efforts":        ("agent.reasoning_effort",),
    "route_efforts_codex":  ("agent.reasoning_effort",),
    "nearest_effort":       ("agent.reasoning_effort",),
    "alias_pair":           ("hermes_cli.model_switch",),
    "call_llm_raises":      ("agent.auxiliary_client",),
    "ping_route_once":      ("agent.auxiliary_client",),
    "ping_reachable":       ("agent.auxiliary_client",),
    "retry_after":          ("agent.retry_utils",),
    "session_env":          ("gateway.session_context",),
    "resolve_reasoning":    ("agent.reasoning_effort",),
    "filter_toolsets":      ("toolsets", "hermes_cli.plugins"),
    "yaml_load":            ("hermes_yaml",),
    "ping_string":          ("agent.auxiliary_client",),
    "import_all":           PRIVATE8,
}

def _fake_mod(name):
    m = types.ModuleType(name)
    m.__path__ = []          # package-shaped: dotted lookups fail INSIDE the child,
                             # never on a missing parent, so the raise is the block
    return m

def block(mods):
    for parent in sorted({m.split(".")[0] for m in mods}):
        sys.modules.setdefault(parent, _fake_mod(parent))
    for m in mods:
        sys.modules[m] = None if MODE == "absent" else _fake_mod(m)

def leg(door):
    if SITE == "route_efforts":
        import wfcommon
        got = list(door._route_efforts("openai", "model-x"))
        exp = list(wfcommon.reasoning_levels())
        assert exp and got == exp, (got, exp)
    elif SITE == "route_efforts_codex":
        import wfcommon
        got = list(door._route_efforts("openai-codex", "model-x"))
        exp = list(wfcommon.reasoning_levels())
        assert exp and got == exp, (got, exp)
    elif SITE == "nearest_effort":
        assert door._nearest_effort("medium", ["low", "medium", "high"]) is None
    elif SITE == "alias_pair":
        assert door._alias_provider_pair("ghost-alias-zz", {}, {}, ()) == (None, None)
    elif SITE == "call_llm_raises":
        try:
            door._import_call_llm()
        except ImportError:
            return
        raise AssertionError("_import_call_llm raised NOTHING — the raise-by-design leg broke")
    elif SITE == "ping_route_once":
        served = []
        def _stub(p, m):
            served.append("subprocess-door")
            return {"liveness": "unknown", "note": "probe stub of _ping_subprocess (the real one spawns)"}
        door._ping_subprocess = _stub
        d = door._ping_route_once("openai-codex", "model-x")
        assert isinstance(d, dict) and d.get("liveness") == "unknown", d
        # row promise met: never raised, answered unknown; the generic note leg
        # and the stubbed subprocess-door leg are both honest answers.
    elif SITE == "ping_reachable":
        assert door._ping_reachable("model-x") is False
    elif SITE == "retry_after":
        assert door._ping_retry_after(RuntimeError("no headers here")) is None
    elif SITE == "session_env":
        os.environ["WF_SOFTGUARD_SE"] = "softguard-42"
        assert door._session_env("WF_SOFTGUARD_SE") == "softguard-42"
        assert door._session_env("WF_SOFTGUARD_UNSET_ZZ") == ""
    elif SITE == "resolve_reasoning":
        import wf as runner
        import wfcommon
        node = {"id": "n", "provider": "openai-codex", "model": "model-x", "reasoning": "high"}
        got = runner._resolve_child_reasoning(None, {}, node)
        sup = list(wfcommon.reasoning_levels())
        hit = runner._nearest_supported("high", sup)
        exp = hit if (hit is not None and hit != "high") else "high"
        assert isinstance(got, str) and got == exp, (got, exp)
    elif SITE == "filter_toolsets":
        import wf as runner
        names = ["read_file", "terminal"]
        assert runner._filter_child_toolsets(None, {}, {"id": "n", "toolsets": names}) == names
    elif SITE == "yaml_load":
        import wfcommon
        text = "a: 1\nb: two\n"
        got, raised = None, None
        try:
            got = wfcommon._yaml_load(text)
        except ImportError as e:
            raised = e
        exp = None
        try:
            from ruamel.yaml import YAML
            y = YAML(typ="safe", pure=True)
            y.version = (1, 1)
            exp = y.load(text)
        except ImportError:
            try:
                import yaml
                exp = yaml.safe_load(text)
            except ImportError:
                pass
        if exp is not None:
            assert isinstance(got, dict) and got == exp, (got, exp)
        else:
            # documented chain shape on a host with neither ruamel nor PyYAML:
            # hermes_yaml blocked -> last leg `import yaml` raises. Honest raise.
            assert raised is not None, "no yaml backend on host, yet _yaml_load neither returned nor raised"
    elif SITE == "ping_string":
        sys.argv[1:4] = ["openai-codex", "model-x", "1"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(door._PING_SUBPROCESS, "<_PING_SUBPROCESS>", "exec"), {"__name__": "__probe__"})
        lines = buf.getvalue().strip().splitlines()
        assert lines, "string site printed nothing"
        v = json.loads(lines[-1])
        assert v.get("unavailable") is True, v
    elif SITE == "import_all":
        import wf as runner
        import wfcommon
        assert callable(runner._resolve_child_reasoning) and callable(wfcommon._yaml_load)
    else:
        raise AssertionError("unknown site " + SITE)

block(MODS[SITE])
try:
    _door = importlib.import_module("__init__")
    try:
        leg(_door)
    except AssertionError as e:
        print("PROBE-FAIL " + (e.args[0] if e.args and isinstance(e.args[0], str) else repr(e.args)))
        sys.exit(1)
    print("PROBE-OK " + SITE)
except ImportError as e:
    # import-time safety is itself the contract (rule 7: host imports lazy);
    # a door/wf/wfcommon that cannot IMPORT under a blocked host is a real fail.
    print("PROBE-FAIL import-time ImportError: " + str(e)[:200])
    sys.exit(1)
'''

# one probe per (site, mode); modes are the issue's two block shapes
MODES = ("absent", "renamed")
SITES = ("route_efforts", "route_efforts_codex", "nearest_effort", "alias_pair",
         "call_llm_raises", "ping_route_once", "ping_reachable", "retry_after",
         "session_env", "resolve_reasoning", "filter_toolsets", "yaml_load",
         "ping_string", "import_all")

# ---------------------------------------------------------------------------
# static source pins: the table's sites still live in the functions that guard
# them (a moved/rewritten import out of its guarded function must re-probe the
# table, not silently pass). Substring, not line number — line drift is legal.
# ---------------------------------------------------------------------------
SRC_ROWS = (
    ("__init__.py", "_route_efforts", "from agent.reasoning_effort import route_supported_efforts"),
    ("__init__.py", "_route_efforts", "from agent.reasoning_effort import codex_supported_efforts"),
    ("__init__.py", "_nearest_effort", "from agent.reasoning_effort import EFFORT_LADDER"),
    ("__init__.py", "_alias_provider_pair", "from hermes_cli.model_switch import _ensure_direct_aliases, DIRECT_ALIASES"),
    ("__init__.py", "_import_call_llm", "from agent.auxiliary_client import call_llm"),
    ("__init__.py", "_ping_retry_after", "from agent.retry_utils import parse_retry_after_seconds"),
    ("__init__.py", "_session_env", "from gateway.session_context import get_session_env"),
    ("wf.py", "_resolve_child_reasoning", "from agent.reasoning_effort import route_supported_efforts"),
    ("wf.py", "_filter_child_toolsets", "from toolsets import validate_toolset"),
    ("wf.py", "_filter_child_toolsets", "from hermes_cli.plugins import get_plugin_toolset_keys_nowait"),
    ("wfcommon.py", "_yaml_load", "from hermes_yaml import safe_load"),
)

PING_STR_RE = re.compile(r"^_PING_SUBPROCESS = '''(.*?)'''", re.DOTALL | re.MULTILINE)


def func_body(src, name):
    m = re.search(rf"^def {re.escape(name)}\(", src, re.M)
    if not m:
        return None
    rest = src[m.start():]
    nxt = re.search(r"^def ", rest[5:], re.M)
    return rest[:5 + nxt.start()] if nxt else rest


def main():
    fails = []
    total = 0
    scratch = tempfile.TemporaryDirectory(prefix="tm-softguard-")
    env = dict(os.environ,
               HERMES_HOME=scratch.name,
               WF_RUNS_ROOT=os.path.join(scratch.name, "runs"))
    for mode in MODES:
        for site in SITES:
            total += 1
            label = f"softguard[{site}/{mode}]"
            p = subprocess.run([sys.executable, "-c", PROBE, site, mode, str(REPO)],
                               capture_output=True, text=True, timeout=120,
                               env=env, cwd=str(REPO))
            lines = [ln for ln in (p.stdout or "").strip().splitlines() if ln.strip()]
            last = lines[-1] if lines else ""
            if p.returncode == 0 and last.startswith("PROBE-OK"):
                print(f"PASS: {label}")
            else:
                tail = last or ((p.stderr or "").strip().splitlines() or ["no output"])[-1]
                print(f"FAIL: {label} — rc={p.returncode} {tail[:300]}")
                fails.append(label)

    # static legs: every table row still sits inside its guarded function
    for fname, func, needle in SRC_ROWS:
        total += 1
        label = f"source-pin[{fname}:{func}:{needle.split()[1]}]"
        try:
            src = (REPO / fname).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"FAIL: {label} — unreadable: {e}")
            fails.append(label)
            continue
        body = func_body(src, func)
        if body is None:
            print(f"FAIL: {label} — function {func} not found in {fname}")
            fails.append(label)
        elif needle not in body:
            print(f"FAIL: {label} — import moved out of the guarded function")
            fails.append(label)
        else:
            print(f"PASS: {label}")

    # static leg: the lint-invisible string site — documented, guarded inside
    total += 1
    src = (REPO / "__init__.py").read_text(encoding="utf-8", errors="replace")
    m = PING_STR_RE.search(src)
    s = m.group(1) if m else ""
    if m and "from agent.auxiliary_client import call_llm" in s and "except Exception" in s \
            and '"unavailable": True' in s:
        print("PASS: source-pin[__init__.py:_PING_SUBPROCESS — string-exec site present, guarded inside the string]")
    else:
        print("FAIL: source-pin[__init__.py:_PING_SUBPROCESS — the string-exec site vanished from the string or lost its inner guard]")
        fails.append("source-pin[_PING_SUBPROCESS]")

    print(f"{total} checks: {len(SITES)} site legs x {len(MODES)} modes (fresh subprocess each, "
          f"fake dotted parents so both modes exercise the block itself) + "
          f"{len(SRC_ROWS) + 1} source pins")
    print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): " + ", ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
