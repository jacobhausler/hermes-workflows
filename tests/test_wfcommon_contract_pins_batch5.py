"""est-77m53: batch-5 direct contract pins for the five sweep-c zero-direct-reference `wfcommon` callables at shipped tip 886a88b — settings_runs_root, settings_profile, dead_set, substrate_disclosure_text, strip_engine_disclosure; every expectation MEASURED against that tip; pointer here (AGENTS.md hint cap full); house shape per merged #620/#624/#635/#639. Stdlib, serial."""
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/.."); import wfcommon as W; fails = 0
def check(label, cond):
    global fails; print(("PASS " if cond else "FAIL ") + label); fails += 0 if cond else 1
def raises(fn):
    try: fn(); return False
    except ValueError: return True
_TD = tempfile.TemporaryDirectory(prefix="b5-pins-"); EST = Path(_TD.name); MINE = EST / "profiles" / "mine"; MINE.mkdir(parents=True)
(EST / "profiles" / "exists").mkdir(); (EST / "via").symlink_to(EST)
def own(key, value, call):
    saved = (W.owner_setting, W.profile_home)
    W.owner_setting = lambda k, _v=value: _v if k == key else None
    W.profile_home = lambda name, home=None: EST / "profiles" / str(name)
    try: return call()
    finally: W.owner_setting, W.profile_home = saved
RR = lambda v, home=MINE: own("runs_root", v, lambda: W.settings_runs_root(home=home))
SP = lambda v: own("profile", v, lambda: W.settings_profile())
N = lambda i, after=(), oo=(): {"id": i, "after": list(after), "order_only": list(oo)}
S = {"from": "opus", "to": "sonnet", "reason": "billing gate"}
TXT = ("SUBSTRATE DISCLOSURE (engine-stamped, not author-written): this node was pinned 'opus'; "
       "the estate confidence_substrate policy served 'sonnet' (billing gate).")
KEY = W.SUBSTRATE_DISCLOSURE_KEY
SCH = {"type": "object", "properties": {KEY: {"type": "string"}, "answer": {"type": "string"}}, "required": [KEY, "answer"]}
ONLY = {"type": "object", "properties": {KEY: {"type": "string"}}, "required": [KEY]}
BEFORE = json.dumps(SCH)
check("settings_runs_root: unset/whitespace -> None; non-str, a surviving ${...} and a relative path each raise (FAIL-CLOSED, never a silent fallback); `~` expands; the estate's profiles ROOT and any path inside ANOTHER profile's home are refused while the caller's OWN profile home and a foreign `profiles` segment stay legal; the answer is the RESOLVED path (a symlinked root is seen for what it is)",
      RR(None) is None and RR("   ") is None and raises(lambda: RR(5)) and raises(lambda: RR("${B5_UNSET}/wf"))
      and raises(lambda: RR("wf/rel")) and raises(lambda: RR(str(EST / "profiles"))) and raises(lambda: RR(str(MINE.parent / "other" / "wf")))
      and RR("~/wf-b5") == Path.home() / "wf-b5" and RR(str(MINE)) == MINE.resolve()
      and RR(str(EST / "elsewhere" / "profiles" / "x")) == (EST / "elsewhere" / "profiles" / "x").resolve()
      and RR(str(EST / "via" / "wf")) == (EST / "wf").resolve())
check("settings_profile: unset/whitespace -> None; non-str raises; the SAME unsafe-name law as `profile:` node keys (leading / ~ ., any separator, any '..', control chars); a surviving ${...} raises; FAIL-CLOSED on a GHOST — a named profile with no profile home is refused at the door; whitespace around a real name is stripped",
      SP(None) is None and SP("  ") is None and raises(lambda: SP(7)) and raises(lambda: SP("${B5_UNSET}"))
      and all(raises(lambda: SP(b)) for b in ("/x", "~x", ".hidden", "a/b", "a\\b", "..", "a..b", "a\x01b"))
      and raises(lambda: SP("ghost")) and SP(" exists ") == "exists")
check("dead_set: `failed` is dead; a `pending` node behind a dead DATA after-edge is dead transitively down the chain; the SAME edge declared order_only never kills (the convoy splice); done/skipped/running predecessors are alive; an after-ref to an id not in the node list is no death; a cycle cannot hang; falsy inputs -> empty set",
      W.dead_set([N("a")], {"a": "failed"}) == {"a"}
      and W.dead_set([N("a"), N("b", ["a"])], {"a": "failed", "b": "pending"}) == {"a", "b"}
      and W.dead_set([N("a"), N("b", ["a"], ["a"])], {"a": "failed", "b": "pending"}) == {"a"}
      and W.dead_set([N("a"), N("b", ["a"]), N("c", ["b"]), N("d", ["c"], ["c"])], {"a": "failed", "b": "pending", "c": "pending", "d": "pending"}) == {"a", "b", "c"}
      and W.dead_set([N("a"), N("b", ["a"])], {"a": "skipped", "b": "pending"}) == W.dead_set([N("a"), N("b", ["a"])], {"a": "done", "b": "running"}) == set()
      and W.dead_set([N("b", ["zz"])], {"b": "pending"}) == W.dead_set([N("a", ["b"]), N("b", ["a"])], {"a": "pending", "b": "pending"}) == W.dead_set([N("a")], {}) == set())
check("substrate_disclosure_text: the ONE verbatim engine sentence, built ONLY from the stamp dict — from/to repr'd, missing keys print None, a missing or empty reason falls back to the named unavailable-at-submit clause; and it is byte-for-byte what apply_substrate_disclosure writes into the schema property description",
      W.substrate_disclosure_text(S) == TXT and W.substrate_disclosure_text({"from": "a", "to": "b"}).endswith("(route proved unavailable at submit).")
      and "pinned None" in W.substrate_disclosure_text({}) == W.substrate_disclosure_text({"reason": ""})
      and W.apply_substrate_disclosure(_NODE := {"schema": {"type": "object", "properties": {}}}, S) is None
      and _NODE["schema"]["properties"][KEY]["description"] == TXT and _NODE["schema"]["required"] == [KEY])
check("strip_engine_disclosure (the validation view): a falsy stamp or a non-dict schema returns the SAME object; with a stamp the engine-owned key leaves BOTH `required` and `properties` on a copy, so the committed record keeps its clause and the input schema is byte-untouched; a list/dict emptied by the strip is dropped, not left empty; a schema without the key comes back equal",
      W.strip_engine_disclosure(SCH, None) is SCH and W.strip_engine_disclosure(SCH, {}) is SCH and W.strip_engine_disclosure(SCH, "") is SCH
      and W.strip_engine_disclosure("junk", S) == "junk" and W.strip_engine_disclosure(None, S) is None
      and W.strip_engine_disclosure(SCH, S) == {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
      and W.strip_engine_disclosure(ONLY, S) == {"type": "object"} and W.strip_engine_disclosure({"type": "object", "properties": {KEY: {}, "x": {}}}, S) == {"type": "object", "properties": {"x": {}}}
      and json.dumps(SCH) == BEFORE and W.strip_engine_disclosure({"type": "object", "properties": {"x": {}}, "required": ["x"]}, S) == {"type": "object", "properties": {"x": {}}, "required": ["x"]})
print(f"{'FAILED' if fails else 'OK'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
