#!/usr/bin/env python3
"""Stub hermes_bin for test_runner_orphan_666 — the runner-death-orphan repro child.

The witnessed shape (est-2ek.1.666, fb-closeout 2026-10-04 15:32Z): a terminating
runner leaves its agent-node child running unsupervised. This stub reproduces it
faithfully: it prints a progress line (never a silent spawn), detaches a
grandchild into its OWN session (double-fork + setsid — the escape shape the
killpg of the child's group cannot reach), and the grandchild APPENDS a
heartbeat line every 0.2 s while it lives.

The child-side belt (est-2ek.1.666): a cooperating child calls
wf.child_parent_watch() — it self-exits non-zero the instant its runner is gone
(getppid() reparented away from the runner-pinned pid AND that pid is dead).
On base the helper does not exist: the watch is a no-op, the heartbeat advances
forever, and the test is RED. That is the point.
"""
import os
import sys
import time

args = sys.argv[1:]
q = ""
if "--query-file" in args:
    try:
        q = open(args[args.index("--query-file") + 1]).read()
    except OSError:
        q = ""

HB = os.environ.get("FAKE_HB_666", os.devnull)
GC_LOG = os.environ.get("FAKE_GC_666", os.devnull)


def _detach_heartbeat():
    """Double-fork + setsid: the heartbeat writer escapes BOTH our process group
    and (once we exit) our session — the exact unsupervised-survivor shape."""
    pid = os.fork()
    if pid > 0:
        return
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    # grandchild: independent session. Announce, then heartbeat until killed or
    # (on the branch) the parent-liveness belt cuts it.
    try:
        with open(GC_LOG, "a") as f:
            f.write(str(os.getpid()) + "\n")
            f.flush()
    except OSError:
        pass
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import wf as _wf
        watch = getattr(_wf, "child_parent_watch", None)
        if callable(watch):
            watch(interval=0.15)          # belt-braces: die with the runner
    except Exception:
        pass                              # base: no helper -> pure orphan (RED)
    n = 0
    while True:
        n += 1
        try:
            with open(HB, "a") as f:
                f.write(f"beat {n} pid={os.getpid()} t={time.time()}\n")
                f.flush()
        except OSError:
            pass
        time.sleep(0.2)


with open(os.environ.get("FAKE_LOG", os.devnull), "a") as f:
    f.write(str(os.getpid()) + "\n")
print("stub 666 child cooking", flush=True)   # log exists -> not a silent spawn
_detach_heartbeat()
time.sleep(float(os.environ.get("STUB_SLEEP", "120")))
item = ""
for line in (q or "").splitlines():
    if line.strip():
        item = line.strip()[:80]
        break
print("```json\n" + "{\"result\": \"done:" + item.replace('"', "'") + "\"}\n```")
sys.exit(0)
