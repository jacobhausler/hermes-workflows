#!/usr/bin/env python3
"""Wake-burst coalescer with trailing re-check (est-zmizd).

Peer graft (atbrace:hjs-epl, SYNTHESIS.md #12): a cross-process debounce on the
wake path so a fan-out/straggler wake burst collapses to a bounded number of
owner turns. The audited shape (iw-recon hermes_workflows/hooks.py:50-179)
DROPS every suppressed event: the last wake of a burst can be the only wake
that names a state the owner has not yet seen, so a dropped tail is a lost
transition. This port fixes the flaw: a suppressed wake records a PENDING
TRAILING RE-CHECK due one window after the burst's leading wake; the runner
drains due re-checks at the wave boundary and finalize() flushes them before
the terminal wake, so the final event always lands. Ledger dedupe keeps the
re-check free when the leading wake already delivered.

Laws pinned here:
  * SCOPE: only the repeat-prone mid-flight class coalesces; every terminal or
    gate wake is unchanged (a non-coalesced notify writes no marker).
  * COALESCE: a burst inside one window advances exactly twice — the leading
    wake plus one trailing re-check — never once (the peer flaw), never N.
  * TRAILING: the re-check names the LAST suppressed key, so the final event
    of the burst is the one that lands.
  * QUIET PATH: an isolated wake fires and schedules zero re-checks.
  * FAIL-OPEN: a broken marker store fires the wake (a double wake is
    harmless, a lost transition is not).
  * END TO END: through notify() + the loopback sink, a two-wake burst is one
    POST; the due re-check makes it exactly two, and the second POST carries
    the trailing instance's Idempotency-Key.

Synthetic session ids; real run dirs; the WF_WAKE_SINK_PORT loopback the
sibling wake suites already use. Stdlib only.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
for _k in ("WF_WAKE_SINK_PORT", "API_SERVER_KEY", "API_SERVER_HOST", "API_SERVER_PORT",
           "WF_RUNS_ROOT"):
    os.environ.pop(_k, None)  # hermetic: no inherited endpoint may steal the wake
import wf  # noqa: E402

checks = 0
failures = 0


def check(label, cond, detail=""):
    global checks, failures
    checks += 1
    if cond:
        print(f"PASS {label}")
    else:
        failures += 1
        print(f"FAIL {label}: {detail}")


sinks = []


class _Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(n)
        sinks.append({"idem": self.headers.get("Idempotency-Key", "")})
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ["WF_WAKE_SINK_PORT"] = str(srv.server_address[1])

tmp = Path(tempfile.mkdtemp(prefix="wf-zmizd-"))
OWNER = {"session_id": "zmizd-session", "ui_session_id": "zmizd-ui", "platform": "api_server"}


def mk_run(run_id):
    r = tmp / run_id
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "run.json").write_text(json.dumps(
        {"concurrency": 1, "node_timeout": 60, "owner": OWNER}))
    return r


def marker(r, event):
    p = wf._wake_marker_path(r, event)
    return json.loads(p.read_text()) if p.exists() else None


def ledger(r):
    p = r / "wake.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


HAVE_API = all(hasattr(wf, n) for n in
               ("_WAKE_COALESCE", "_wake_coalesce_check", "_wake_drain_rechecks",
                "_wake_marker_path", "_wake_refire_pending"))
if not HAVE_API:
    check("coalescer API present", False,
          "wf lacks _WAKE_COALESCE/_wake_coalesce_check/_wake_drain_rechecks/"
          "_wake_marker_path/_wake_refire_pending")
else:
    try:
        CO = "fanout.stragglers"

        # 1. SCOPE registry: the mid-flight repeat class coalesces; terminal and
        #    gate wakes do not.
        reg = wf._WAKE_COALESCE
        check("registry is a set/frozenset", isinstance(reg, (frozenset, set)), str(type(reg)))
        check("straggler class coalesces", CO in set(reg), str(reg))
        check("terminal/gate classes do NOT coalesce",
              not (set(reg) & {"gate.held", "run.done", "run.failed", "run.partial"}), str(reg))

        # 2. QUIET PATH: an isolated wake fires and schedules zero re-checks.
        r = mk_run("quiet-1")
        check("quiet: first wake fires",
              wf._wake_coalesce_check(r, CO, "w1", now=100.0) is True)
        m = marker(r, CO)
        check("quiet: marker records no pending re-check",
              isinstance(m, dict) and m.get("pending") is False, str(m))
        check("quiet: drain inside window yields none",
              wf._wake_drain_rechecks(r, now=101.0) == [])
        check("quiet: drain past window yields none (zero re-check cost)",
              wf._wake_drain_rechecks(r, now=200.0) == [])

        # 3. COALESCE: a five-wake burst advances exactly 2 — leading + trailing.
        r = mk_run("burst-2")
        advances = 0
        if wf._wake_coalesce_check(r, CO, "w1", now=100.0):
            advances += 1
        for i, t in enumerate((100.5, 101.0, 101.5, 101.9), start=2):
            fired = wf._wake_coalesce_check(r, CO, f"w{i}", now=t)
            check(f"burst: w{i} inside window suppresses", fired is False, str(fired))
            if fired:
                advances += 1
        check("burst: no advance before the window closes",
              wf._wake_drain_rechecks(r, now=101.95) == [])
        due = wf._wake_drain_rechecks(r, now=102.0)   # due = fire_ts + window (100+2)
        advances += len(due)
        check("burst collapses to 2 advances, not 1 (and not 5)",
              advances == 2, f"advances={advances} due={due}")

        # 4. TRAILING: the re-check names the LAST suppressed key, never the first.
        check("trailing event names the last key",
              len(due) == 1 and due[0] == (CO, "w5"), str(due))
        r2 = mk_run("burst-3")
        wf._wake_coalesce_check(r2, CO, "a1", now=100.0)
        wf._wake_coalesce_check(r2, CO, "a2", now=100.5)
        due2 = wf._wake_drain_rechecks(r2, now=102.5)
        check("trailing key survives a later suppressed wake",
              due2 == [(CO, "a2")], str(due2))
        check("drain is read-only: re-drain still offers the re-check (at-least-once)",
              wf._wake_drain_rechecks(r2, now=102.5) == [(CO, "a2")])

        # 5. A refire (force) always fires and re-arms the window fresh.
        check("refire fires inside an open window",
              wf._wake_coalesce_check(r2, CO, "a2", now=102.5, refire=True) is True)
        check("refire clears the pending re-check",
              wf._wake_drain_rechecks(r2, now=102.5) == [])

        # 6. FAIL-OPEN: a broken marker store fires the wake, never swallows it.
        r3 = mk_run("failopen-1")
        (r3 / "wake-debounce").write_text("not a dir")   # path collision: mkdir must fail
        check("fail-open: unreadable marker store fires",
              wf._wake_coalesce_check(r3, CO, "x1", now=100.0) is True)
        check("fail-open: drain of a broken store yields none",
                wf._wake_drain_rechecks(r3, now=999.0) == [])

        # 7. SCOPE at the notify boundary: a gate wake writes no marker at all.
        r = mk_run("scope-1")
        before = len(sinks)
        wf.notify(r, "gate.held", key="g1:def")
        check("non-coalesced wake POSTs unchanged", len(sinks) - before == 1, str(len(sinks)))
        check("non-coalesced wake writes no debounce marker",
              marker(r, "gate.held") is None and not (r / "wake-debounce").exists())

        # 8. END TO END: a two-wake straggler burst is ONE POST; the due re-check
        #    fires the trailing instance for exactly TWO, ledger-deduped after.
        r = mk_run("e2e-1")
        before = len(sinks)
        wf.notify(r, CO, key="wave-1")
        wf.notify(r, CO, key="wave-2")          # within the window: suppressed
        burst_posts = sinks[before:]
        check("e2e burst: suppressed wake costs zero POSTs",
              len(burst_posts) == 1, str(burst_posts))
        wf._wake_refire_pending(r, now=time.time() + wf.WAKE_DEBOUNCE_WINDOW_S + 1)
        all_posts = sinks[before:]
        check("e2e: burst + trailing re-check is exactly 2 POSTs",
              len(all_posts) == 2, str(all_posts))
        rows = ledger(r)
        check("e2e: trailing wake delivered and ledgered",
              len(rows) == 2 and all(x.get("delivered") for x in rows)
              and {x["event"] for x in rows} == {CO}, str(rows))
        want = wf._wake_tid(r.name, CO, wf._wake_identity(r, CO, "wave-2"))
        check("e2e: re-check names the trailing instance's Idempotency-Key",
              len(all_posts) == 2 and all_posts[1]["idem"] == want, str(all_posts))
        check("e2e: re-check schedules no further re-check",
              marker(r, CO) is not None
              and wf._wake_drain_rechecks(r, now=time.time() + 10) == [])
        before = len(sinks)
        wf.notify(r, CO, key="wave-2")          # already delivered: dedupe wins
        check("e2e: repeat of a delivered instance writes no new POST",
              len(sinks) - before == 0, str(len(sinks)))

        # 9. finalize flush: due re-checks drain before the terminal wake.
        r = mk_run("flush-1")
        before = len(sinks)
        wf.notify(r, CO, key="s1")
        wf.notify(r, CO, key="s2")              # suppressed, pending
        wf._wake_refire_pending(r, now=time.time() + wf.WAKE_DEBOUNCE_WINDOW_S + 1)
        check("flush: trailing wake lands before the run goes terminal",
              len(sinks) - before == 2, str(len(sinks)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

print(f"{checks - failures}/{checks} checks passed")
sys.exit(1 if failures else 0)
