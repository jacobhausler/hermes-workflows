"""est-vgxp2: batch-4 direct contract pins for the five sweep-c zero-direct-reference callables still un-pinned at shipped tip 1fd7d72 — node_telemetry.node_key, orphan_watch.session_matches, gate_index.index_path, wfcommon.quota_cache_path, wfcommon.stable_argv_roots; every expectation MEASURED against that tip; pointer here (AGENTS.md hint cap full); house shape per merged #620/#624/#635. Stdlib, serial."""
import os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import gate_index as GI, node_telemetry as NT, orphan_watch as OW, wfcommon as W
fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def _at(keys, env, call):
    saved = dict(os.environ)
    for k in keys: os.environ.pop(k, None)
    os.environ.update(env)
    try: return call()
    finally: os.environ.clear(); os.environ.update(saved)
QP = lambda env, arg=None: _at(("WF_QUOTA_CACHE", "HERMES_HOME"), env, lambda: W.quota_cache_path(arg))
AR = lambda env: _at(("WF_ARGV_STABLE_ROOTS", "HERMES_HOME"), env, W.stable_argv_roots)
FIX = [Path("/usr"), Path("/bin"), Path("/sbin"), Path("/opt")]
check("node_key: the prefix before the LAST colon is the fold key (colon-bearing prefixes survive, the per-spawn suffix drops); colonless passes through; falsy skey -> ''",
      NT.node_key("hermes:main:1234abcd.7") == "hermes:main" and NT.node_key("plain") == "plain" and NT.node_key(5) == "5"
      and NT.node_key("") == NT.node_key(None) == NT.node_key(0) == "")
check("session_matches: equality for any id; suffix ONLY for >=8-char owners behind one : - _ / |; short ids never suffix-match; falsy side never matches; non-str coerces",
      OW.session_matches("ab", "ab") and OW.session_matches("abcdef12", "abcdef12")
      and all(OW.session_matches("12345678", sep + "12345678") for sep in ":-_/|")
      and OW.session_matches("abcdef1234", "gw:team/abcdef1234") and OW.session_matches(12345678, "gw:12345678")
      and not OW.session_matches("abc", "gw:abc") and not OW.session_matches("abcdef1234", "xabcdef1234")
      and not OW.session_matches("", "x") and not OW.session_matches("x", "") and not OW.session_matches(None, None))
check("index_path: root joined to the ONE index file name gate-index.jsonl; str and Path roots agree",
      GI.index_path("/var/runs/r1") == Path("/var/runs/r1/gate-index.jsonl")
      and GI.index_path(Path("/tmp")) == Path("/tmp/gate-index.jsonl"))
check("quota_cache_path: the ONE precedence arg > WF_QUOTA_CACHE > HERMES_HOME cache > ~/.hermes default; an empty-string env counts as unset",
      QP({"WF_QUOTA_CACHE": "/env"}, "/arg") == Path("/arg") and QP({"WF_QUOTA_CACHE": "/env"}) == Path("/env")
      and QP({"WF_QUOTA_CACHE": "", "HERMES_HOME": "/hh"}) == QP({"HERMES_HOME": "/hh"}) == Path("/hh/cache/workflow-quota-cache.json")
      and QP({}) == Path.home() / ".hermes" / "cache" / "workflow-quota-cache.json")
check("stable_argv_roots: the four system roots come first always; WF_ARGV_STABLE_ROOTS replaces the tail (empty segments skipped, whitespace NOT trimmed, ~ expanded); no env -> HERMES_HOME scripts/plugins/installs + ~/.local/bin (8 rows)",
      AR({"WF_ARGV_STABLE_ROOTS": "/a:: /b:~/cx"}) == FIX + [Path("/a"), Path(" /b"), Path.home() / "cx"]
      and AR({"HERMES_HOME": "/hh"}) == FIX + [Path("/hh/scripts"), Path("/hh/plugins"), Path("/hh/installs"), Path.home() / ".local" / "bin"]
      and AR({})[:4] == FIX and len(AR({})) == 8)
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
