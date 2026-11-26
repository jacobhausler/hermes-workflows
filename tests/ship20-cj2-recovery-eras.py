#!/usr/bin/env python3
"""cj2-recovery successor: phase-aware width-four era assertions.

Explicit admission (2026-11-26, bead bd_2026-11-13-s20-cj2-recovery): a NEW
version of the publication assertion for the retention acceptance published in
tests/ship20-cj2-retention.py (lines 13-19, 205-208): exactly ONE atomic
pre-start whole-image dispatch plus AT MOST ONE strict-subset settlement prune
per generation. The frozen battery (tests/ship20-cj2-faults-probes.py era legs
and tests/ship20-cj2-faults.py) is untouched byte-for-byte, and its raw red
outcomes at the composed pin stay banked exactly as measured; this file does
not relabel that run, it re-admits the era matrix under the stated rule.

The successor asserts against the LEDGER AND THE IMAGES, never aggregate call
counts alone: one atomic dispatch before the first start (no second dispatch,
no remint), old canonical slots byte-intact while the replacement is pending
(observed from inside live children), zero carrier bytes inside the live wave
window, a prune only after the final completion, prune as a strict subset with
no value drift and no new keys, settled keys exactly the record-anchored set,
zero on empty / static / no-change / replay, prior carrier bytes unchanged
under an injected real prune-write fault (healed within one era), per-index
prepare-key/transport/started/finished identity chains, both actual roster
forms (dict prep.items and list prep.0), and per-write layer equality
(serialize-image == temp-write == replace, no fsync) with sha-paired
temp/replaced byte streams.

The historical width-four fixture shape is preserved: sizes [4,4,0,2] (then
regrow 4, fault-turnover 4, heal 4), labels CJ2_ITEM_{index:04d}_{g*32} with
odd-generation reversal, the real act_amend seam with the respawn hop stubbed,
the on_fail="empty" fallback node, and the prior process witness (the ps shim
and private env are imported from tests/ship20-cj2-faults.py — the pinned
battery — not recopied).

Decisive negatives are real, not mocked: run the same legs with --repo at a
stale-retention checkout (the pre-CJ2 base) and the ledger assertions fire on
obsolete keys / live-window publication; the --battery wrapper turns that into
a must-fire control (NEEDS_REPIN if the negative goes green).

Usage (probe, one leg per isolated process):
    python3 -B tests/ship20-cj2-recovery-eras.py eras-dict [REPO] [ROOT]
    python3 -B tests/ship20-cj2-recovery-eras.py eras-list [REPO] [ROOT]
    python3 -B tests/ship20-cj2-recovery-eras.py both     [REPO] [ROOT]
Portability: the probe is stdlib-only, self-locates its repo, defaults every
case-write under ROOT (tempfile-mkdtemp when omitted), and opens no sockets
and no subprocesses — it runs from a stock export with no platform-specific
dependency. Platform-specific proof lives in the wrapper: the ps-shim process
witness only materializes where /proc is absent, and the offline sandbox
(network-deny + write-fence) is sandbox-exec, i.e. macOS.
    python3 -B tests/ship20-cj2-recovery-eras.py --battery --repo REPO \
        [--battery-out OUT] [--negative STALE_REPO] \
        [--match-compat-exits BANKED_EXITS_TSV]
Exit 0 only with every check green (wrapper: positives green, negative fired,
compat exits.tsv byte-identical to the banked witness when asked).
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

_failures = []


def check(ok, note):
    if not ok:
        _failures.append(note)
        print("FAIL", note, flush=True)
    return ok


def sha256(b):
    return hashlib.sha256(b).hexdigest()[:16]


# ---- the frozen battery as reusable witness (ps shim, private env, pins) ----
def battery_module(repo):
    spec = importlib.util.spec_from_file_location(
        "cj2_frozen_battery", Path(repo) / "tests" / "ship20-cj2-faults.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================== probe ==============================
class Era:
    """One roster form driving the width-four era matrix against REPO."""

    PLAN = [(4, False), (4, False), (0, False), (2, False),
            (4, False), (4, True), (4, False)]

    def __init__(self, repo, root, form):
        self.repo = Path(repo).resolve()
        self.root = Path(root).resolve()
        self.form = form
        self.name = f"cj2-recovery-eras-{form}"
        self.rows = []
        self.lock = threading.Lock()
        self.phase = "boot"
        self.prune_fault = [False]        # refuse the era's SECOND scope replace
        self.scope_replaces = [0]         # successful scope replaces since era start
        self._orig = (json.dumps, Path.write_text, os.replace, os.fsync)
        os.chdir(self.repo)
        sys.path.insert(0, str(self.repo))

        def load(mod_name, rel, package=False):
            spec = importlib.util.spec_from_file_location(
                mod_name, self.repo / rel,
                submodule_search_locations=[str(self.repo)] if package else None)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod

        self.wf = load("cj2_rec_runner", "wf.py")
        self.door = load("cj2_rec_door", "__init__.py", package=True)
        # #71 r5: the env pin (read below) is NOT a sandbox — the owner's
        # settings.runs_root outranks it (resolver precedence #42). Pin the
        # door's resolver before any door write; the per-Era re-install is an
        # idempotent no-op.
        load("cj2_rec_iso71", "tests/wf_test_isolation.py").install(self.door)
        self.wc = load("cj2_rec_wfcommon", "wfcommon.py")
        # the runner resolves bare run names under WF_RUNS_ROOT
        self.runs = Path(os.environ["WF_RUNS_ROOT"])
        self.run = self.runs / self.name
        (self.run / "nodes").mkdir(parents=True, exist_ok=True)
        self.carrier = self.run / "fanout-inputs/review.json"
        self._seed_case()

    # ---- case fixture: historical width-four shape, both roster forms ----
    def _seed_case(self):
        ref = "prep.items" if self.form == "dict" else "prep.0"
        w = {"name": self.name, "item_concurrency": 4}
        (self.run / "run.json").write_text(json.dumps(w))
        graph = {"name": self.name, "nodes": [
            {"id": "prep", "type": "agent", "goal": "era 0"},
            {"id": "review", "type": "agent", "goal": "review {item}",
             "after": ["prep"], "on_fail": "empty",
             "fanout": {"items_from": ref, "goal": "review {item}"}},
            {"id": "empty", "type": "agent", "goal": "report empty"}]}
        (self.run / "graph.json").write_text(json.dumps(graph))

    # ---- instrumentation: ledger rows with images, bytes, and sha pairing ----
    def record(self, op, **fields):
        with self.lock:
            fields["seq"] = len(self.rows) + 1
            self.rows.append(dict(phase=self.phase, op=op, **fields))

    @staticmethod
    def _scope(path):
        return Path(path).parent.name == "fanout-inputs"

    # ---- helpers over images/records ----
    def keys_of(self, image):
        return {s["skey"] for entry in image["items"].values()
                for s in entry.values()}

    def slot_map(self, image):
        return {(i, s["skey"]): s["item"]
                for i, entry in image["items"].items() for s in entry.values()}

    def record_keys(self):
        out = {}
        for p in (self.run / "nodes").glob("review.*.json"):
            if p.stem.count(".") == 1:
                out[p.stem.rsplit(".", 1)[1]] = json.loads(p.read_text())["skey"]
        return out

    def snapshot(self):
        b = self.carrier.read_bytes()
        return json.loads(b)

    # ---- one era: real amend, real scheduler, live threaded children ----
    def wave(self, gen, labels, amend=True, faulted=False):
        self.phase = f"{self.name}/gen{gen}"
        if gen and amend:
            with patch.object(self.door, "_respawn_runner", lambda _: None):
                resp = self.door.act_amend(
                    {"run_id": self.name,
                     "patch": {"nodes": {"prep": {"goal": f"era {gen}"}}}})
            check(resp.get("ok") and {"prep", "review"} <= set(resp.get("will_rerun") or []),
                  f"{self.phase}: amend refused {json.dumps(resp)[:200]}")
        self.prune_fault[0] = faulted
        self.scope_replaces[0] = 0
        mark = len(self.rows)
        carrier_before = (self.carrier.read_bytes()
                          if self.carrier.exists() else None)

        def child(meta, node, byid, goal, context, schema, *, skey, index=None, **kw):
            if node["id"] == "prep":
                output = ({"items": labels} if self.form == "dict" else [labels]) \
                    if labels else ({"items": []} if self.form == "dict" else [[]])
            elif node["id"] == "empty":
                output = {"empty": True}
            else:
                check(node["id"] == "review" and goal == "review " + labels[index],
                      f"{self.phase}: fan-out goal drifted off the label")
                # mid-live witness: read the carrier AS THE WAVE SEES IT.
                img = self.snapshot()
                self.record("midwave-view", index=index, key=skey,
                            bytes=len(self.carrier.read_bytes()),
                            sha=sha256(self.carrier.read_bytes()),
                            keys=sorted(self.keys_of(img)), image=img)
                time.sleep(0.25 + 0.05 * (index or 0))
                output = {"result": "child output (no copied item)"}
            return dict(skey=skey, spawn=0, attempts=1, ms=1, status="done",
                        output=output)

        wf, original_log, original_key = self.wf, self.wf.log, self.wf.skey_for

        def log(r, event, **kw):
            if Path(r) == self.run and kw.get("node") == "review" \
                    and event in ("item.started", "item.finished"):
                self.record(event, index=kw["index"], key=kw.get("skey"))
            return original_log(r, event, **kw)

        def key(r, byid, node, index=None):
            k = original_key(r, byid, node, index)
            if node["id"] == "review" and Path(r) == self.run:
                self.record("prepare-key", index=index, key=k)
            return k

        # plain nested closures, not bound methods: patch.object stores them
        # on the class (Path instances bind them as methods themselves), and
        # the caller-frame sniffing below must see the product's own frame
        # one level up (the frozen fixtures patch with module-level
        # functions for the same two reasons).
        def dump_hook(obj, *a, **kw):
            text = self._orig[0](obj, *a, **kw)
            caller = sys._getframe(1)
            inwf = caller.f_code.co_filename == str(self.repo / "wf.py")
            carrier_row = (isinstance(obj, dict)
                           and {"version", "items"} <= obj.keys() and inwf)
            slot_row = (caller.f_code.co_name in ("capture_fanout_input",
                                                  "_publish_fanout_inputs")
                        and isinstance(obj, dict) and set(obj) == {"skey", "item"})
            if carrier_row:
                self.record("serialize-image", bytes=len(text.encode("utf-8")),
                            sha=sha256(text.encode("utf-8")))
            elif slot_row:
                self.record("serialize-slot")
            return text

        def write_hook(path, text, *a, **kw):
            if not self._scope(path):
                return self._orig[1](path, text, *a, **kw)
            result = self._orig[1](path, text, *a, **kw)
            self.record("temp-write", bytes=len(text.encode("utf-8")),
                        sha=sha256(text.encode("utf-8")))
            return result

        def replace_hook(src, dst, *a, **kw):
            if not self._scope(dst):
                return self._orig[2](src, dst, *a, **kw)
            data = Path(src).read_bytes()
            if self.prune_fault[0] and self.scope_replaces[0] >= 1:
                self.prune_fault[0] = False
                self.record("replace", ok=False, bytes=len(data),
                            sha=sha256(data), image=json.loads(data))
                raise OSError("cj2 recovery-eras injected settlement-rename refusal")
            result = self._orig[2](src, dst, *a, **kw)
            self.scope_replaces[0] += 1
            self.record("replace", ok=True, bytes=len(data), sha=sha256(data),
                        image=json.loads(data), data=data)
            return result

        def fsync_hook(fd):
            if sys._getframe(1).f_code.co_name in ("capture_fanout_input",
                                                   "_publish_fanout_inputs",
                                                   "_settle_fanout_inputs"):
                self.record("fsync")
            return self._orig[3](fd)

        with patch.object(json, "dumps", dump_hook), \
                patch.object(Path, "write_text", write_hook), \
                patch.object(os, "replace", replace_hook), \
                patch.object(os, "fsync", fsync_hook), \
                patch.object(wf, "run_child", child), \
                patch.object(wf, "notify", lambda *a, **kw: None), \
                patch.object(wf, "log", log), patch.object(wf, "skey_for", key):
            try:
                wf.main(self.name)
            finally:
                wf._release_terminal_lock(self.run)
        check(not (faulted and self.prune_fault[0]),
              f"{self.phase}: prune fault never armed")
        return self.rows[mark:], carrier_before

    # ---- the phase-aware era law ----
    def check_era(self, gen, wedge, size, labels, old_image, faulted):
        phase = f"{self.name}/gen{gen}"
        repl = [r for r in wedge if r["op"] == "replace"]
        repl_ok = [r for r in repl if r.get("ok")]
        repl_bad = [r for r in repl if not r.get("ok")]
        ser = [r for r in wedge if r["op"] == "serialize-image"]
        tw = [r for r in wedge if r["op"] == "temp-write"]
        # per-write layer equality + no fsync entered the writer
        check(len(ser) == len(tw) == len(repl),
              f"{phase}: write layers diverge {len(ser)}/{len(tw)}/{len(repl)}")
        check(not [r for r in wedge if r["op"] == "fsync"],
              f"{phase}: fsync entered the writer")
        # every successful replace's bytes equal its temp write (atomic pairing)
        pairs_ok = [r for r in repl if r.get("ok") and
                    any(t["sha"] == r["sha"] and t["seq"] < r["seq"] for t in tw)]
        check(len(pairs_ok) == len(repl_ok),
              f"{phase}: a replace did not carry its temp-write's exact bytes")
        if not size:
            check(len(repl_ok) <= 1,
                  f"{phase}: empty wave re-published an already-retained image")
            if old_image is not None:
                check(self.carrier.read_bytes() == old_image[1],
                      f"{phase}: empty era touched the carrier bytes")
            return
        starts = [r for r in wedge if r["op"] == "item.started"]
        fins = [r for r in wedge if r["op"] == "item.finished"]
        check(len(starts) == len(fins) == size, f"{phase}: event coverage")
        check(len(repl_ok) + len(repl_bad) <= 2,
              f"{phase}: unbounded whole-image writes ({len(repl)} attempts)")
        check(not repl_bad or faulted, f"{phase}: unexplained failed replace")
        plan = repl_ok[0]
        first_start = min(r["seq"] for r in starts)
        live_end = max(r["seq"] for r in fins)
        # one atomic dispatch PRE-START; a second dispatch before the first
        # start is the forbidden remint shape.
        check(plan["seq"] < first_start, f"{phase}: dispatch landed after a start")
        pre = [r for r in repl if r["seq"] < first_start]
        check(len(pre) == 1, f"{phase}: {len(pre)} dispatches before the first start")
        # no write AT ALL (attempt or success) inside the live wave window
        mid = [r for r in repl if plan["seq"] < r["seq"] < live_end]
        check(not mid, f"{phase}: carrier write inside the live wave window "
                      f"(seqs {[r['seq'] for r in mid]})")
        # old canonical while pending: mid-live children saw the prior image's
        # keys with byte-identical slot values, and the carrier never moved.
        views = [r for r in wedge if r["op"] == "midwave-view"]
        check(len(views) == size, f"{phase}: {len(views)} mid-live carrier views "
                                  f"for {size} live items")
        shas = {v["sha"] for v in views}
        check(len(shas) == 1, f"{phase}: live-window carrier bytes shifted {shas}")
        if views:
            live_keys = set(views[0]["keys"])
            check(live_keys == set(self.keys_of(plan["image"])),
                  f"{phase}: live carrier keys differ from the dispatch image")
            if old_image is not None:
                old_img, _ = old_image
                live_map = self.slot_map(views[0]["image"])
                for (i, k), v in self.slot_map(old_img).items():
                    if k in live_keys:
                        check(live_map.get((i, k)) == v,
                              f"{phase}: pending view lost old canonical slot {i}")
        # prune: only after the FINAL completion; strict subset; no value
        # drift; no remint/transport/serialize after it.
        if len(repl_ok) == 2:
            prune = repl_ok[-1]
            k0, k1 = self.keys_of(plan["image"]), self.keys_of(prune["image"])
            check(prune["seq"] > live_end,
                  f"{phase}: prune landed before the final item completion")
            check(k1 < k0, f"{phase}: prune image is not a strict subset")
            check(k1 == set(self.record_keys().values()),
                  f"{phase}: pruned image off the record-anchored key set")
            check(prune["bytes"] <= plan["bytes"], f"{phase}: prune grew the carrier")
            check(self.slot_map(prune["image"]).items()
                  <= self.slot_map(plan["image"]).items(),
                  f"{phase}: prune drifted a slot value")
            check(prune["seq"] == max(r["seq"] for r in repl),
                  f"{phase}: writer act after the prune")
            check(not [r for r in wedge if r["op"] in
                       ("prepare-key", "transport", "serialize-slot",
                        "serialize-image", "temp-write")
                       and r["seq"] > prune["seq"]],
                  f"{phase}: prune published or reminted after itself")
        else:
            check(faulted or self.keys_of(plan["image"])
                  == set(self.record_keys().values()),
                  f"{phase}: retained plan image is not exactly the anchored set "
                  f"(stale retention)")
        # settled keys exact (faulted era: the failed prune leaves the PLAN
        # bytes standing — prior bytes unchanged by the failed write).
        final_bytes = self.carrier.read_bytes()
        if faulted:
            check(final_bytes == plan["data"],
                  f"{phase}: failed prune altered carrier bytes")
            fin = self.keys_of(json.loads(final_bytes))
            check(old_image is not None and set(old_image[0] and
                  self.keys_of(old_image[0])) <= fin and
                  fin - set(self.record_keys().values()),
                  f"{phase}: faulted era degraded without obsolete keys standing")
        else:
            check(self.keys_of(json.loads(final_bytes))
                  == set(self.record_keys().values()),
                  f"{phase}: settled carrier holds obsolete keys "
                  f"{sorted(self.keys_of(json.loads(final_bytes)) - set(self.record_keys().values()))}")
        check(sorted(self.carrier.parent.iterdir()) == [self.carrier],
              f"{phase}: temp residue {sorted(p.name for p in self.carrier.parent.iterdir())}")
        # per-index identity chain + label landed on its own era key
        for i in range(size):
            bases = set()
            for r in wedge:
                if r["op"] in ("prepare-key", "transport") and r.get("index") == i:
                    bases.add(r["key"].split("#a")[0])
                if r["op"] in ("item.started", "item.finished") \
                        and r.get("index") == i and r.get("key"):
                    bases.add(r["key"].split("#a")[0])
            rec = json.loads((self.run / f"nodes/review.{i}.json").read_text())
            bases.add(rec["skey"].split("#a")[0])
            check(len(bases) == 1, f"{phase}/{i}: identity chain spans {len(bases)} keys")
            base = bases.pop()
            smap = self.slot_map(json.loads(final_bytes))
            landed = {sk: v for (ix, sk), v in smap.items() if ix == str(i)}
            check(any(sk.split("#a")[0] == base and v == labels[i]
                      for sk, v in landed.items()),
                  f"{phase}/{i}: label not on its own era key in the settled image")
        agg = json.loads((self.run / "nodes/review.json").read_text())
        check(agg["status"] == "done" and
              len(agg["output"]["all_results"]) == size,
              f"{phase}: wave status/results")

    # ---- the full matrix for one roster form ----
    def run_form(self):
        t0 = time.monotonic()
        old = None
        for gen, (size, faulted) in enumerate(self.PLAN):
            check(time.monotonic() - t0 < 240, f"{self.name}: leg timeout")
            fails_before = len(_failures)
            char = chr(97 + gen) * 32
            labels = [f"CJ2_ITEM_{i:04d}_{char}" for i in range(size)]
            if gen % 2:
                labels = list(reversed(labels))
            carrier_bytes_before = (self.carrier.read_bytes()
                                    if self.carrier.exists() else None)
            old_image = (json.loads(carrier_bytes_before), carrier_bytes_before) \
                if carrier_bytes_before else None
            wedge, _ = self.wave(gen, labels, amend=True, faulted=faulted)
            if not size:
                self.phase = f"{self.name}/gen{gen}"
                check(not [r for r in wedge if r["op"] in
                           ("serialize-slot", "prepare-key", "transport")],
                      f"{self.name}/gen{gen}: empty era launched review work")
                self.check_era(gen, wedge, size, labels, old_image, faulted)
                agg = json.loads((self.run / "nodes/review.json").read_text())
                check(agg["status"] in ("skipped", "done") and
                      (agg["status"] != "skipped" or
                       agg.get("caught_error_class") == "fanout_empty"),
                      f"{self.name}/gen{gen}: empty-wave fallback {agg.get('status')}")
                if len(_failures) == fails_before:
                    print(f"PASS {self.name}/gen{gen}: empty era — zero writer "
                          f"ops, carrier bytes untouched", flush=True)
                continue
            self.check_era(gen, wedge, size, labels, old_image, faulted)
            n = len([r for r in wedge if r["op"] == "replace" and r.get("ok")])
            kind = ("plan + strict-subset prune, no remint" if n == 2 else
                    "plan retained, zero prune")
            if faulted:
                kind = "prune fault — prior(plan) bytes unchanged, healed next era"
            if len(_failures) == fails_before:
                print(f"PASS {self.name}/gen{gen}: size {size} green "
                      f"writes={n} ({kind})", flush=True)
        # heal: obsolete keys from the faulted era died within ONE era.
        final = self.keys_of(json.loads(self.carrier.read_text()))
        check(final == set(self.record_keys().values()),
              f"{self.name}: obsolete keys survived past the heal era")
        # replay: re-driving the settled run with no change is zero-op.
        mark = len(self.rows)
        self.wave(len(self.PLAN), [f"CJ2_ITEM_{i:04d}_" + "g" * 32
                                   for i in range(4)], amend=False)
        replay = self.rows[mark:]
        check(not [r for r in replay if r["op"] in ("serialize-slot",
                                                    "serialize-image",
                                                    "temp-write", "replace")],
              f"{self.name}: replay of the settled run wrote the carrier")
        print("PASS " + self.name + "/replay: no-change replay is zero-op", flush=True)
        # static boundary: an inline-items def writes ZERO carrier bytes.
        sname = self.name + "-static"
        srun = self.runs / sname
        (srun / "nodes").mkdir(parents=True, exist_ok=True)
        (srun / "run.json").write_text(json.dumps({"name": sname,
                                                   "item_concurrency": 4}))
        (srun / "graph.json").write_text(json.dumps({"name": sname, "nodes": [
            {"id": "review", "type": "agent", "goal": "review {item}",
             "fanout": {"items": ["CJ2_ITEM_0000_s", "CJ2_ITEM_0001_s"]}}]}))
        mark = len(self.rows)
        with patch.object(self.wf, "notify", lambda *a, **kw: None):
            self.wf.main(sname)
            self.wf._release_terminal_lock(srun)
        static = self.rows[mark:]
        check(not [r for r in static if r["op"] in ("serialize-slot",
                                                    "serialize-image",
                                                    "temp-write", "replace")],
              f"{self.name}: static boundary wrote the carrier")
        check(not (srun / "fanout-inputs").exists(),
              f"{self.name}: static boundary created fanout-inputs/")
        print("PASS " + self.name + "/static: zero carrier bytes", flush=True)
        (self.root / "ops-rows.json").write_text(
            json.dumps(self.rows, indent=2, default=repr))

    def instrumented_run(self):
        try:
            self.run_form()
        finally:
            pass
        return 1 if _failures else 0


def probe_main(leg, repo, root):
    form = {"eras-dict": "dict", "eras-list": "list"}[leg]
    root = Path(root or Path(tempfile.mkdtemp(prefix="cj2-recovery-eras-"))).resolve()
    (root / "runs").mkdir(parents=True, exist_ok=True)
    (root / "home").mkdir(parents=True, exist_ok=True)
    # #71 r5: a stale/inherited pin must not redirect the door's writes
    # outside the private root we were handed — ASSIGN, never setdefault.
    os.environ["WF_RUNS_ROOT"] = str(root / "runs")
    os.environ["HERMES_HOME"] = str(root / "home")
    os.environ.setdefault("HERMES_QUIET", "1")
    repo = repo or Path(__file__).resolve().parents[1]
    era = Era(repo, root, form)
    rc = era.instrumented_run()
    print(("PROBE-EXIT", rc, leg), flush=True)
    return rc


# ============================== battery wrapper ==============================
EXPECTED_NEGATIVE = ("settled carrier holds obsolete keys",
                     "retained plan image is not exactly the anchored set",
                     "live-window carrier bytes shifted",
                     "carrier write inside the live wave window",
                     "dispatches before the first start",
                     "prune image is not a strict subset",
                     "re-published an already-retained image")


def battery_main(argv):
    args = list(argv)

    def flag(name):
        if name in args:
            v = args[args.index(name) + 1]
            del args[args.index(name):args.index(name) + 2]
            return v
        return None

    out = Path(flag("--battery-out") or tempfile.mkdtemp(prefix="cj2-rec-battery-")).resolve()
    repo_arg = flag("--repo")
    if not repo_arg:
        raise SystemExit("--battery requires --repo CHECKOUT")
    repo = Path(repo_arg).resolve()
    negative = flag("--negative")
    match_compat = flag("--match-compat-exits")
    out.mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(exist_ok=True)
    bat = battery_module(repo)          # the pinned battery = the witness
    pins_before = bat.pin_record(repo)
    py = sys.executable
    legs = {}

    def spawn(leg_name, command):
        env, slot = bat.priv_env(out, leg_name)
        env["HERMES_WF_PYTHON"] = py
        env["WORKFLOW_MAX_SEATS"] = "0"
        with (out / "logs" / (leg_name + ".log")).open("wb") as fh:
            rc = subprocess.run(command, cwd=str(slot), env=env,
                                stdout=fh, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL).returncode
        log = (out / "logs" / (leg_name + ".log")).read_text(errors="replace")
        fails = [l for l in log.splitlines() if l.startswith("FAIL")]
        return rc, fails, log

    probes = [("successor-eras-dict", "eras-dict", repo),
              ("successor-eras-list", "eras-list", repo)]
    if negative:
        probes += [("negative-stale-dict", "eras-dict", Path(negative).resolve()),
                   ("negative-stale-list", "eras-list", Path(negative).resolve())]
    for leg_name, leg, target in probes:
        must = leg_name.startswith("negative")
        rc, fails, _log = spawn(leg_name,
                                [py, "-B", str(Path(__file__).resolve()),
                                 leg, str(target), str(out / "priv" / leg_name)])
        if not must:
            legs[leg_name] = ("PASS" if rc == 0 else "BEHAVIOR_RED", rc)
        else:
            fired = [f for f in fails if any(p in f for p in EXPECTED_NEGATIVE)]
            if rc == 0:
                legs[leg_name] = ("NEEDS_REPIN (negative went green: the law "
                                  "cannot reject stale retention)", rc)
            elif fired:
                legs[leg_name] = ("PASS (EXPECTED_RED fired: "
                                  + fired[0][:160] + ")", rc)
            else:
                legs[leg_name] = ("NEEDS_REPIN (negative died outside the "
                                  "decisive classes)", rc)
    if match_compat:
        banked = Path(match_compat).read_bytes()
        slot_rc, _f, _l = spawn("compat-control",
                                [py, "-B", str(repo / "tests" / "ship20-cj2-compat.py"),
                                 "--checkout", str(repo), "--out",
                                 str(out / "priv" / "compat-control")])
        got = (out / "priv" / "compat-control" / "exits.tsv")
        if slot_rc != 0:
            legs["compat-match"] = (f"NEEDS_REPIN (compat battery exit {slot_rc})",
                                    slot_rc)
        else:
            same = got.read_bytes() == banked
            legs["compat-match"] = (("PASS (exits.tsv byte-identical to the "
                                     "banked witness)" if same else
                                     "NEEDS_REPIN (exits.tsv differs from banked)"), 0)
    pins_after = bat.pin_record(repo)
    (out / "pin.txt").write_text(json.dumps({"before": pins_before,
                                             "after": pins_after}, indent=2))
    lines = []
    ok = True
    for leg_name, (verdict, rc) in legs.items():
        lines.append(f"{leg_name}\t{verdict}\t{rc}")
        ok = ok and verdict.startswith("PASS")
    ok = ok and pins_after["porcelain_clean"] and pins_before == pins_after \
        and pins_after["detached"] and not pins_after["remotes"] \
        and not pins_after["alternates"]
    (out / "exits.tsv").write_text("\n".join(lines) + "\n")
    (out / "classification.json").write_text(json.dumps(
        dict(legs=legs, pins=pins_after, witness="ps shim imported from the "
             "pinned battery PS_SHIM_SRC"), indent=2) + "\n")
    print("\n".join(lines), flush=True)
    print("BATTERY-EXIT", 0 if ok else 1, flush=True)
    return 0 if ok else 1


def main():
    if not sys.argv[1:]:
        sys.exit(probe_main("eras-dict", None, None))
    a = sys.argv[1:]
    if a[0] == "--battery":
        sys.exit(battery_main(a[1:]))
    leg = a[0]
    if leg == "both":
        rc1 = probe_main("eras-dict", a[1] if len(a) > 1 else None,
                         a[2] if len(a) > 2 else None)
        sys.exit(rc1 or probe_main("eras-list", a[1] if len(a) > 1 else None,
                                   a[2] if len(a) > 2 else None))
    if leg in ("eras-dict", "eras-list"):
        sys.exit(probe_main(leg, a[1] if len(a) > 1 else None,
                            a[2] if len(a) > 2 else None))
    raise SystemExit("unknown mode " + leg)


if __name__ == "__main__":
    main()
