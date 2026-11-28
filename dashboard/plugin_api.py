"""Dashboard backend for hermes-workflows — thin projection of the SHARED read model.

State truth lives in wfcommon.run_state (same function the door uses); gate release
shares the door's single answer path. Endpoints land under /api/plugins/hermes-workflows.
The UI does NOT resume runs — the owning agent does (philosophy: agent owns the run).
"""
import hashlib, importlib.util, json, os, sys, threading, time
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_COMMON_MODULE = "_hermes_workflows_wfcommon_" + hashlib.sha256(
    str(_PLUGIN_ROOT).encode("utf-8")).hexdigest()[:16]

def _workflow_common():
    """Load this plugin's sibling module without binding global ``wfcommon``."""
    module = sys.modules.get(_COMMON_MODULE)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(_COMMON_MODULE, _PLUGIN_ROOT / "wfcommon.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load workflow module from {_PLUGIN_ROOT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_COMMON_MODULE] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_COMMON_MODULE, None)
        raise
    return module

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None

def _root():
    """ONE resolver (wfcommon.runs_root): `settings.runs_root` (owner, #42) > `WF_RUNS_ROOT`
    > `<hermes_home>/workflows`. Read at call time — no restart."""
    return _workflow_common().runs_root()

def _safe_run(run_id):
    rid = (run_id or "").strip()
    if not rid or rid != "".join(c for c in rid if c.isalnum() or c in "-_.") \
            or rid.startswith("."):
        return None
    r = _workflow_common().find_run(rid)   # legacy-location fallback for pre-fix ids
    return r if r.is_dir() else None

def _events(r, limit=400):
    out = []
    try:
        lines = (r / "events.jsonl").read_text().splitlines()[-limit:]
    except FileNotFoundError:
        return out
    for l in lines:
        try: out.append(json.loads(l))
        except Exception: pass
    return out

LOG_TAIL = 16384  # O2: chosen constant, not a measured one and not a config.

# Process-scoped state for the bench fail-once knob (see release_gate): one
# refusal per (run, gate) per gateway process while the env is armed.
_PROOF_FAIL_ONCE_DONE = set()

def _node_log_tail(r, nid, index, attempt, kind, tail):
    """O2's single read-only log route core. The path comes ONLY from the record's
    log_path/prompt_path (the client never sends a path) and must resolve inside
    <run>/logs. Tails the last `tail` bytes by seek, never reads the whole file.
    Returns dict|None; None = 404-worthy (bad id, no record, escape, missing file)."""
    common = _workflow_common()
    if kind not in ("log", "prompt") or not common.ID_OK.match(nid or ""):
        return None
    try:
        tail = int(tail); attempt = None if attempt is None else int(attempt)
        index = None if index is None else int(index)
    except (TypeError, ValueError):
        return None
    if not 0 < tail <= LOG_TAIL or (attempt is not None and attempt < 0):
        return None
    name = nid + (f".{index}" if index is not None else "")
    rec = common.jload(r / "nodes" / f"{name}.json")
    if not isinstance(rec, dict):
        return None
    p = rec.get("prompt_path" if kind == "prompt" else "log_path")
    if not isinstance(p, str) or not p:
        return None
    lp = Path(p)
    if attempt is not None:  # sibling spawn log: same base, different .a<n>
        ext = ".prompt.md" if kind == "prompt" else ".log"
        lp = lp.with_name(f"{nid}" + (f".{index}" if index is not None else "") + f".a{attempt}{ext}")
    logs = (r / "logs").resolve()
    try:
        rp = lp.resolve()
        rp.relative_to(logs)  # containment; ValueError on escape
    except (OSError, ValueError):
        return None
    try:
        size = rp.stat().st_size
        with open(rp, "rb") as f:
            if size > tail:
                f.seek(-tail, os.SEEK_END)
            data = f.read()
    except OSError:
        return None
    return {"id": r.name, "node": name, "kind": kind, "size": size,
            "bytes": len(data), "content": data.decode("utf-8", errors="replace")}

def _view(r, full=False, lock_state=None):
    common = _workflow_common()
    # bd_2026-11-25-cj2: ONE fingerprint-memo pair for the whole response —
    # run_state, the claims pass, the facts join and the turnover adjudication
    # all walk this single stored revision (wfcommon.efp's documented sharing
    # law: memo values are pure functions of one byid table).
    fp_memo, legacy_memo = {}, {}
    st = (common.run_state(r, lock_state=lock_state, fp_memo=fp_memo, legacy_memo=legacy_memo)
          if full
          else common.run_state(r, telemetry=False, lock_state=lock_state,
                                fp_memo=fp_memo, legacy_memo=legacy_memo))
    if not st:
        return None
    view = {"id": st["run_id"], "name": st["name"], "status": st["status"],
            "started": st.get("started"), "owner": st.get("owner"),
            "nodes_done": st["done"], "nodes_skipped": st["skipped"], "nodes_total": st["total"],
            "updated": (r / "events.jsonl").stat().st_mtime if (r / "events.jsonl").exists() else 0}
    # l8i (instance-label-first law): the display-title resolver rides every
    # row — lane_key + description when the read model carries them (the door
    # stamps lane_key at launch; description rides the graph root). Honest
    # absence: an unlabeled legacy run gains no keys and the resolver falls to
    # name — the pre-2.0 rendering, never a fabricated label.
    if st.get("lane_key"):
        view["lane_key"] = st["lane_key"]
    if st.get("description"):
        view["description"] = st["description"]
    if st.get("runner_lock") and st["runner_lock"] not in ("busy", "free"):
        # #44: a wedge (or an EACCES-ambiguous lock) is visible on the card —
        # honest absence otherwise (golden key sets byte-unchanged for busy/free).
        view["runner_lock"] = st["runner_lock"]
        if st.get("runner_lock_detail"):
            view["runner_lock_detail"] = st["runner_lock_detail"]
    # Agent-first pane (2026-10-03): stamp WHO launched this run. The read model
    # resolves owner.session_id -> profile name via the profiles' own session
    # tables (wfcommon.profiles_by_session, read-only). Absent stays absent —
    # the UI falls back to the raw session id, never invents a bot.
    try:
        p = _workflow_common().profiles_by_session().get((st.get("owner") or {}).get("session_id"))
        if p:
            view["owner_profile"] = p
    except Exception:
        pass
    if st["held_gate"]:
        view["held_gate"] = st["held_gate"]
    if st.get("runner_exit"):
        view["runner_exit"] = st["runner_exit"]  # shared read model (wfcommon.run_state)
    if full:
        import time
        common = _workflow_common()
        # est-la8m: fold each node's children through its OWN child-DB home
        # (wfcommon.run_child_metrics, the fb-904f seam the door uses) — a bare
        # caller-home fold reads only the launcher's state.db and false-zeros
        # every profile-routed child in the dashboard's full view (issue #81).
        # bd_2026-11-13-cj2 (revision repair + late-boundary repair): EVERY
        # join that can confer a current chat rides the graph THIS very
        # response publishes. run_child_metrics takes it as its authority
        # revision (claims validate against the shipped snapshot, no graph
        # file is read) — and the facts join takes it too: the node_facts
        # aggregate re-read, made AFTER metrics, was the remaining raw
        # authority. A certified re-order landing mid-view repainted the
        # shipped layout (Case A: the visible new chip opened the OLD item's
        # chat), and a persistently stale aggregate kept being presented as
        # current beside the new binding (Case B: the visible old chip opened
        # the replacement's chat) — receipts/ship20-recovery/cj2-late-
        # boundary-db40b950/gap-replay.log, red at db40b950. With
        # the published revision handed in, `output` attests only a commit
        # the existing validity law honors; a demoted output rides the
        # established `unknown`, every other fact rides verbatim, history
        # stays inspectable. One response, one era. Amend-only half-demotions
        # and settled reads are unchanged: a revision-honored commit rides
        # verbatim and opens the exact ID.
        # bd_2026-11-25-cj2 (exact-attempt join): a version/efp match is not
        # execution identity — a same-efp ABA restore and a same-fingerprint
        # redrive certify BOTH generations against the published revision, and a
        # same-skey schema correction advances the attempt INSIDE one generation
        # key, so an era check alone can ship one response with the late
        # aggregate's layout over the fold's chat claim. EVERY join below
        # therefore rides ONE response-level byid table and ONE fingerprint-memo
        # pair (efp memo values are pure functions of this one revision). The
        # fan-out items' recorded-chat binding is the join of two facts this read
        # already holds: the published aggregate row's own full recorded title
        # (skey + the attempt it names, suffix included) and the already-read
        # home-scoped session rows — a landed title binds verbatim, an unread
        # title binds the computed absence (fail closed, zero host calls), and a
        # claimless legacy row keeps the documented last-entry law. Settled and
        # demoted responses pay nothing: no pre-fold aggregate capture, no
        # second fold, no pairing heuristic, no re-read loop, no per-node graph
        # maps.
        byid_pub = {n["id"]: n for n in st["graph"]["nodes"]}
        cm = common.run_child_metrics(r, graph=st["graph"],
                                      fp_memo=fp_memo, legacy_memo=legacy_memo)
        # bd_2026-11-25-cj2 (display authority): the timeline is read BEFORE the
        # chat join, and the join rides it — the bind-time item-record decision
        # (common.resolve_item_chat) adjudicates the racing generation against
        # the journal THIS response ships, so a commit landing mid-view ships
        # its COMPLETE display decision (`session_display`: the raw status plus
        # the error/refusal facts that normalize it) beside its exact chat,
        # instead of splitting paint and navigation across two read orders.
        # bd_2026-11-25-cj2 (item source, frozen-record repair): the same
        # adjudication also ships the fan-out row's identity beside the
        # pair. bd_2026-11-13-cj2 (input capture): a static def's own items
        # list joins positionally (a pure value of the captured revision);
        # a dynamic (`items_from`) fan-out resolves its item by matching
        # the record's own base execution key into the runner's
        # dispatch-time capture (fanout-inputs/<nid>.json) — at most ONE
        # lazy sidecar read per dynamic node, zero for static, aggregate and
        # legacy responses — instead of indexing the head's CURRENT output,
        # which a mid-view amend may have replaced. A legacy status-bearing
        # `output.items` aggregate is the SAME selection operation as a
        # certified `all_results` row and stays ahead of the capture.
        # The events themselves stay pure timeline: nothing here suppresses or
        # rewrites them.
        events = _events(r)
        nodes = {}
        for nid, v in st["nodes"].items():
            nodes[nid] = dict(v)
            # O2: ONE node truth — every node WITH a record gets the closed fact set
            # verbatim (was: done|failed only, which dropped `partial` output even
            # though the read model treats partial as output, wfcommon.run_state).
            facts = common.node_facts(r, nid, graph=st["graph"], byid=byid_pub,
                                      fp_memo=fp_memo, legacy_memo=legacy_memo)
            if facts is not None:
                facts = {k: x for k, x in facts.items() if k != "status"}
                nodes[nid].update(facts)
            # metrics: node-level = the node's own child, or the fold of its items' children.
            # Keys are prefix-matched (any efp suffix) so an amended re-run's fresh rows count.
            prefix = f"wf:{st['run_id']}:{nid}:"
            mine = {k: m for k, m in cm.items() if k.startswith(prefix)}
            active = v.get("active_spawns", [])
            if mine or active:
                groups = {}
                def item_index(key):
                    parts = key[len(prefix):].split(":")  # "<i>:<efp8>.<nonce>" | "<efp8>.<nonce>"
                    return int(parts[0]) if len(parts) == 2 and parts[0].isdigit() else None
                for k, m in mine.items():
                    groups.setdefault(item_index(k), {})[k] = m
                for spawn in active:
                    key = spawn["skey"].split("#a", 1)[0]
                    if key.startswith(prefix):
                        groups.setdefault(item_index(key), {})
                heartbeat = common.current_attempt(mine, active)
                nodes[nid]["metrics"] = _fold_metrics(mine.values()) or {}
                nodes[nid]["metrics"].update(heartbeat)
                nodes[nid]["metrics"]["scope"] = "cumulative"
                items = {}
                for i, ms in groups.items():
                    if i is not None:
                        items[i] = _fold_metrics(ms.values()) or {}
                        items[i].update(common.current_attempt(ms, [s for s in active
                            if s["skey"].split("#a", 1)[0].startswith(f"{prefix}{i}:")]))
                if items:
                    common.resolve_item_chat(
                        r, nid, facts.get("output") if isinstance(facts, dict) else None,
                        items, groups, byid=byid_pub,
                        fp_memo=fp_memo, legacy_memo=legacy_memo)
                if items:
                    nodes[nid]["item_metrics"] = items
        active = [s for v in st["nodes"].values() for s in v.get("active_spawns", [])]
        rollup = _fold_metrics(cm.values()) if cm else ({} if active else None)
        if rollup is not None:
            rollup.update(common.current_attempt(cm, active))
            rollup["scope"] = "cumulative"
            # #114: no local unknown-rule here — fold_child_metrics already
            # omitted api_calls for any unknown row (was: a per-copy pop, the
            # half of the divergence this fix removes).
        view.update({"graph": st["graph"], "nodes": nodes, "events": events,
                     "gate": dict(st["held_gate"] or {}), "metrics": rollup})
        # bd_2026-11-13-qri: the durable answer receipt for the gate cell. Every
        # gate whose COMMITTED answer carries an 'answer' field, verbatim minus
        # the efp stamp — gate_answer_valid is the law, so an answer invalidated
        # by an amend never renders as saved. Skipped/machine records without an
        # 'answer' field and unanswered gates stay absent (honest absence). The
        # release route invalidates the census BEFORE the write resolves, so this
        # block reflects the UI's own POST on the very next GET.
        gate_records = {}
        for n in st["graph"]["nodes"]:
            if n.get("type") != "gate":
                continue
            ans = common.gate_answer_valid(r, n, byid_pub, fp_memo, legacy_memo)
            if isinstance(ans, dict) and "answer" in ans:
                rec = {"answer": ans["answer"], "at": ans.get("at")}
                if ans.get("_ui") is True:
                    rec["_ui"] = True
                gate_records[n["id"]] = rec
        if gate_records:
            view["gates"] = gate_records
    return view

def _fold_metrics(ms):
    # #114 (WF-04): thin adapter — the ONE fold + known/unknown policy is
    # wfcommon.fold_child_metrics (AGENTS.md: the metrics join belongs to
    # wfcommon). Every level (node line, fanout item, rollup) omits api_calls
    # on ANY unknown child — the door and this surface cannot diverge.
    return _workflow_common().fold_child_metrics(ms)

def _scan_runs():
    """The full census: every de-duplicated run VIEW (uncapped), plus the
    whole-census summary. est-ey31s: split out of _list_runs so the route can
    slice pages from ONE scan; response keys are produced by _list_runs."""
    # F1 #14: merge the legacy launch root the way the door's act_list does — a
    # pre-fix run opens by URL via _safe_run's find_run fallback and must also
    # appear in the list. Resolved root wins on id collision.
    # est-2ek.1.762 census hygiene: enumerate through wfcommon.iter_run_dirs
    # (unique by REALPATH across every scanned root — a same-named torn stub
    # in one root no longer hides the valid run in another; est-7ps8), and
    # report how many rows EXECUTED (logs present).
    # executed counts ONLY rows that land in `runs` (a valid, de-duplicated
    # row) — dirs _view rejects never become rows, so they must not inflate
    # the counter (zap non-blocking note 2). This listing ALWAYS measures:
    # the actual count — including a measured zero — is supplied to
    # run_summary, which renders an omitted count as the absent key
    # (wfcommon.run_summary's supplied-versus-unmeasured contract).
    common = _workflow_common()
    roots = [_root()]
    legacy = common.launch_runs_root()
    if legacy != roots[0]:
        roots.append(legacy)
    runs, seen = [], set()
    executed = 0
    # #44 (PR #47 round-3 sibling gap): 50 rows used to spawn 50 probe children.
    # ONE batch probe child + ONE ledger read for the whole census now; _view
    # consumes the pre-observed per-dir lock state (zero extra probes).
    scanned = list(common.iter_run_dirs(roots, reverse=True))
    # est-1n7gx (collapse-to-one law): the row order and the by-id pick-one below
    # are TOTAL, not traversal luck: iter_run_dirs name-DESCs within each root
    # (names unique per root — the key cannot tie) and takes roots in argument
    # order (resolved first, legacy second), so `seen` first-seen dedupe always
    # keeps the resolved-root row when two physically-distinct dirs carry the
    # same view id. A torn dir never reaches `seen` (no row, no counter), so a
    # valid twin behind it still lands.
    _lock_states = common.runner_lock_states(scanned)
    for r in scanned:
        v = _view(r, lock_state=_lock_states.get(r))
        if v and v["id"] not in seen:
            seen.add(v["id"])
            # est-7ps8 (note 2): count EXECUTED only for rows that land in
            # `runs` — a torn dir that never reaches the list must not
            # inflate the counter (executed > total was the probe).
            if common.run_executed(r):
                executed += 1
            runs.append(v)
    summary = common.run_summary(runs, executed=executed)
    # _roots is the scan record's private key: _list_runs renders it as the
    # public `roots` ONLY on an empty census, exactly as before the split.
    return {"_roots": [str(x) for x in roots], "runs": runs, **summary}


def _list_runs(offset=0, limit=100, *, _record=None):
    """Public list response (contract unchanged since before est-ey31s):
    first page of 100 newest rows by default, whole-census summary, `roots`
    alongside the summary when the census is empty. Direct callers get a
    FRESH scan (no cache) unless they pass a scan record — the dashboard
    route below is the only cache consumer, so every existing in-process
    probe of _list_runs keeps seeing live truth."""
    rec = _record if _record is not None else _scan_runs()
    off = max(0, offset)
    page = rec["runs"][off:off + max(0, limit)]
    return {**({"roots": rec["_roots"]} if not rec["runs"] else {}),
            "runs": page,
            **{k: v for k, v in rec.items() if k not in ("_roots", "runs")}}


# est-ey31s (webui slowness at the hosted console): two changes keep the
# SHARED event loop responsive — the serve process hosts every agent lane's
# traffic:
#   (a) the GET routes are plain `def`, so Starlette dispatches them to a
#       worker thread; an `async def` calling this scan blocks the loop and
#       every other webui call queues behind it (the owner-visible "not
#       working"). Same dispatch the /api/sessions reads already use.
#   (b) scans collapse through a TTL snapshot cache with a lock — the shape
#       of hermes-agent's _TOPOLOGY_CACHE (web_server_gateway.py). The
#       collapse benefit is CONCURRENT-ONLY (est-fj629, census-staggered
#       finding w1-02): pollers inside one window pay ONE scan; a lone
#       active-mode poller pays one scan per max(TTL, its poll interval).
# Co-size (est-fj629): TTL = desktop live refetch (4000 ms,
# desktop/plugin.js) + the measured worst-case scan at the census bound,
# rounded up to the whole second. Artifact:
# docs/measurements/census-scan-latency.json (schema
# wf-census-scan-latency/v1; rerun scripts/bench_census_latency.py):
# linear ~0.5 ms/dir, warm median 1.50 s / max 1.63 s at the 3000-dir
# bound — the bound is the desktop's own walk cap, RUNS_MAX_PAGES(30) x
# RUNS_PAGE_SIZE(100) — and 3.36 s at 2x it, measured on the loaded serve
# host (load average ~17). 4.0 + 1.63 = 5.63 -> 6.0 s. The shipped 2.0 sat
# BELOW the 4.0 poll, so
# every live-mode poll cache-missed and the collapse bought nothing at the
# tuned cadence (est-ey31s' own 1.06-1.29 s @ ~560 dirs had never been
# carried to the 3000-dir bound). Duty cycle is now bounded by scan/TTL:
# <=27% of one worker thread at the bound.
# Freshness: ts stamps at scan START, so a snapshot is never older than TTL
# regardless of scan duration (was: stamped after, letting scan time pad
# the window). Run progress is polled data; 6 s staleness is at the
# poll's own granularity, and the gate-release POST invalidates so a UI
# action reflects on the very next read. The cache stores the full scan
# RECORD; responses are built per request, so no shared mutable payload.
RUNS_CACHE_TTL = 6.0
_monotonic = time.monotonic  # seam for time-free tests (behaviour, not source)
_RUNS_CACHE = {"ts": 0.0, "data": None}
_RUNS_CACHE_LOCK = threading.Lock()


def _runs_snapshot():
    c = _RUNS_CACHE
    now = _monotonic()
    if c["data"] is not None and now - c["ts"] < RUNS_CACHE_TTL:
        return c["data"]
    with _RUNS_CACHE_LOCK:
        now = _monotonic()
        if c["data"] is not None and now - c["ts"] < RUNS_CACHE_TTL:
            return c["data"]
        rec = _scan_runs()
        # est-fj629: stamp the WINDOW START (the `now` above, read before the
        # scan), not the scan's end — a snapshot must never be fresher than
        # its own age claims.
        _RUNS_CACHE.update(ts=now, data=rec)
        return rec


def _runs_cache_invalidate():
    _RUNS_CACHE["data"] = None


if router is not None:
    @router.get("/runs")
    def list_runs(offset: int = 0, limit: int = 100):
        # est-ey31s: sync def => threadpool (off the shared loop); the scan is
        # TTL-collapsed, pages slice from the ONE cached census. Plain int
        # defaults (not Query()): FastAPI reads them as query params, and
        # _list_runs clamps negatives — no new 422 class, no import growth.
        # Default call answers exactly the pre-est-ey31s payload (newest 100
        # + summary).
        return _list_runs(offset, limit, _record=_runs_snapshot())

    @router.get("/settings")
    def get_settings():
        """est-z717: the desktop's tray-gate bootstrap read. Answers ONLY the
        keys the desktop consumes — {tray: bool}. owner_setting('tray') is THE
        established settings shape (wfcommon: the door's plugin ctx reader when
        it has one, else the raw config of the resolved home; settings subtree
        wins over the legacy config subtree). EVERYTHING other than literal
        True — absent key, false, malformed, unreadable config — answers False:
        the tray gate is FAIL-CLOSED, default OFF, until NousResearch/hermes-
        agent#133724 lands the native tray SDK area (when it lands, default-
        on rides that mount). Read-only; never exposes any other setting."""
        try:
            v = _workflow_common().owner_setting("tray")
        except Exception:
            v = None
        return {"tray": v is True}

    @router.get("/runs/{run_id}")
    def get_run(run_id: str):  # est-ey31s: sync def — the detail view is FS I/O
        r = _safe_run(run_id)
        return (_view(r, full=True) if r else None) or {"error": "unknown run"}

    @router.get("/runs/{run_id}/nodes/{nid}/log")
    def get_node_log(run_id: str, nid: str, index: int | None = None,
                           attempt: int | None = None, kind: str = "log",
                           tail: int = LOG_TAIL):
        """O2's ONE tail (the desktop's `rec?.raw` plumbing dies with this route).
        Read-only; path from the record only; contained to <run>/logs."""
        r = _safe_run(run_id)
        if not r:
            raise HTTPException(status_code=404, detail="unknown run")
        out = _node_log_tail(r, nid, index, attempt, kind, tail)
        if out is None:
            raise HTTPException(status_code=404, detail="no such log")
        return out

    @router.post("/runs/{run_id}/gate")
    async def release_gate(run_id: str, body: dict):
        """UI door onto the SAME answer path the tool uses (incl. stale-answer
        overwrite). Does NOT resume the run — the owning agent does."""
        # est-ey31s: a gate answer changes the census — invalidate the snapshot
        # FIRST (even for an unknown id, where the next scan is free labour) so
        # the releasing UI's very next GET reflects the action inside one
        # response, not one TTL window.
        _runs_cache_invalidate()
        r = _safe_run(run_id)
        if not r:
            return {"ok": False, "error": "unknown run"}
        # Bench proof knobs (bd_2026-11-13-qri): the current desktop serves
        # plugin REST through the IPC bridge (remote method 'hermes:api'), so
        # an in-flight answer POST is INVISIBLE to CDP Fetch interception —
        # the pending/error capture frames must instead be REAL transport.
        # UI2_PROOF_GATE_FAIL_ONCE makes the first UI answer per (run, gate)
        # a typed ok:false refusal before the write; UI2_PROOF_GATE_POST_DELAY_MS
        # sleeps AFTER the durable write but BEFORE the response, so the UI's
        # pending frame rides a genuinely slow door, not a staged picture.
        # Env-gated: production traffic never sets them.
        if os.environ.get("UI2_PROOF_GATE_FAIL_ONCE"):
            _key = (run_id, str(body.get("gate_id")))
            if _key not in _PROOF_FAIL_ONCE_DONE:
                _PROOF_FAIL_ONCE_DONE.add(_key)
                return {"ok": False, "error": "proof: transient (bench fail-once)"}
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_hermes_workflows_door", Path(__file__).resolve().parent.parent / "__init__.py")
        door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(door)
        res = door._release_core(r, body.get("gate_id"), body.get("answer", ""), ui=True)
        try:
            _delay = int(os.environ.get("UI2_PROOF_GATE_POST_DELAY_MS", "0") or "0")
        except ValueError:
            _delay = 0
        if _delay and isinstance(res, dict) and res.get("ok") is True:
            import asyncio
            await asyncio.sleep(_delay / 1000.0)
        return res
