#!/usr/bin/env python3
"""#509 — door UX: name the door version + nearest-key hint when graph keys
are refused (the wave-9 shelf-audit tax: `params` on a 1.3.9 door whose files
on disk were 1.4.0 cost three round-trips under the bare allowed-list refusal).

Law implemented (issue #509, docs/UX only — no semantics change):
  (a) every graph_invalid refusal banner names the door's own version, and the
      refusal payload carries machine field `door_version`;
  (b) a refused top-level key that has a row in GRAPH_KEY_MIN_VERSION is named
      as a grammar-layer key with its floor; when the floor exceeds THIS
      process the text says requires >=X (this door: Y) and points at the
      requires_plugin handshake; when the plugin.yaml on disk and CODE_VERSION
      diverge the banner carries the RELOAD BOUNDARY note;
  (c) near-miss keys get difflib's nearest accepted key(s).
  (d) RELEASE LAW gates: plugin.yaml version == CODE_VERSION at HEAD, and
      every STRUCTURAL_GRAPH_KEYS member carries a registry row.

Table re-derive recipe (audit the floors, don't trust them):
  for t in $(git tag); do git show $t:wfcommon.py | grep -A40 STRUCTURAL_GRAPH_KEYS; done
  — first TAG at which the key is proven in the set (or its predecessor
  allowed-literal); never earlier than proven.
"""
import importlib.util
import re
import sys
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import wfcommon  # noqa: E402

spec = importlib.util.spec_from_file_location("wf_door_509", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)

FAILS = []
N = 0

def check(name, cond, detail=""):
    global N
    N += 1
    if not cond:
        FAILS.append(f"FAIL {name} {detail}")
        print(f"FAIL {name} {detail}")
    else:
        print(f"ok   {name}")

LEGACY_PREFIX = "unknown graph key; allowed: "

# --- (d) release-law gates at HEAD ------------------------------------------
check("D1 plugin.yaml == CODE_VERSION",
      wfcommon.plugin_version() == wfcommon.CODE_VERSION,
      f"file={wfcommon.plugin_version()!r} code={wfcommon.CODE_VERSION!r}")
check("D2 every STRUCTURAL_GRAPH_KEYS member has a registry row",
      set(wfcommon.STRUCTURAL_GRAPH_KEYS) <= set(wfcommon.GRAPH_KEY_MIN_VERSION),
      f"missing: {sorted(set(wfcommon.STRUCTURAL_GRAPH_KEYS) - set(wfcommon.GRAPH_KEY_MIN_VERSION))}")
check("D3 registry rows are dot-integer versions",
      all(re.fullmatch(r"\d+(\.\d+){1,3}", v) for v in wfcommon.GRAPH_KEY_MIN_VERSION.values()),
      str({k: v for k, v in wfcommon.GRAPH_KEY_MIN_VERSION.items()
           if not re.fullmatch(r"\d+(\.\d+){1,3}", v)}))

# --- (c) nearest-key hint ----------------------------------------------------
msg = wfcommon.unknown_graph_key_msg("parmas", wfcommon.STRUCTURAL_GRAPH_KEYS)
check("C1 legacy prefix byte-identical", msg.startswith(LEGACY_PREFIX), msg[:120])
check("C2 typo 'parmas' gets 'params' suggested",
      "nearest accepted key(s)" in msg and "params" in msg.split("nearest accepted key(s)")[1],
      msg)
msg2 = wfcommon.unknown_graph_key_msg("zzz_totally_unknown", wfcommon.STRUCTURAL_GRAPH_KEYS)
check("C3 junk key gets no suggestion (never a lie)",
      "nearest" not in msg2, msg2)

# --- (b) grammar-layer hint --------------------------------------------------
# 'params' row is 1.4.0: while this branch's CODE_VERSION is 1.3.9 the REQUIRES
# branch fires; on a >=1.4.0 door it flips to the layer-known branch. Force the
# stale-door shape deterministically:
with patch.object(wfcommon, "CODE_VERSION", "1.3.9"):
    m = wfcommon.unknown_graph_key_msg("params", set())
check("B1 floor>door names requires >=1.4.0 and both versions",
      "requires plugin >=1.4.0" in m and "(this door: 1.3.9)" in m
      and "requires_plugin handshake" in m, m)
with patch.object(wfcommon, "CODE_VERSION", "1.5.0"):
    m2 = wfcommon.unknown_graph_key_msg("params", set())
check("B2 floor<=door says layer-known, refuses anyway",
      "known grammar-layer key" in m2 and "requires plugin >=" not in m2, m2)
check("B4 rowless key carries no layer hint",
      "grammar-layer" not in wfcommon.unknown_graph_key_msg("bogus_key", set()))

# --- (b) reload-boundary note -------------------------------------------------
# The door binds its OWN wfcommon copy (#157); patches must hit that instance.
wfc = door._common
check("R1 clean checkout: no note (file == code at HEAD)",
      wfc.door_reload_note() == "", wfc.door_reload_note())
with patch.object(wfc, "plugin_version", lambda: "9.9.9"):
    note = wfc.door_reload_note()
check("R2 divergent file: note names both versions + reload verb",
      "RELOAD BOUNDARY" in note and "9.9.9" in note
      and wfc.CODE_VERSION in note and "restart" in note, note)
with patch.object(wfc, "plugin_version", lambda: ""):
    check("R3 unreadable file version: silent (absence is not a death)",
          wfc.door_reload_note() == "")

# --- (a) the banner ------------------------------------------------------------
bad = {"name": "x", "nodes": [], "parmas": {}}
res = door._validation_error(bad)
check("A1 banner carries [door <code_version>]",
      f"[door {wfcommon.code_version()}]" in res["error"], res["error"][:200])
check("A2 machine field door_version",
      res.get("door_version") == wfcommon.code_version(), str(res.get("door_version")))
check("A3 banner keeps 'graph invalid:' prefix",
      res["error"].startswith("graph invalid:"), res["error"][:80])
with patch.object(wfc, "plugin_version", lambda: "9.9.9"):
    res2 = door._validation_error(bad)
check("A4 reload note rides the banner on divergence",
      "RELOAD BOUNDARY" in res2["error"], res2["error"][:300])

# --- refusal path through the shared structural validator (include fuse uses
# the same text law). A registry row is refused only when the key is NOT in
# the accepted set, so the check withholds the key from the set -------------
_without = wfc.STRUCTURAL_GRAPH_KEYS - {"on_exit"}
with patch.object(wfc, "STRUCTURAL_GRAPH_KEYS", _without):
    errs = wfc.structural_graph_errors({"name": "x", "nodes": [], "on_exit": "a"})
umsg = [e["msg"] for e in errs if e["field"] == "on_exit" and "unknown graph key" in e["msg"]]
check("S1 structural validator emits the layer hint inline",
      bool(umsg) and "grammar-layer" in umsg[0], str(errs))

print(f"\n{N - len(FAILS)}/{N} checks pass")
sys.exit(1 if FAILS else 0)
