#!/usr/bin/env python3
"""hw-32b: SIGTERM sender attribution — the runner records the kernel-provided
sender (siginfo.si_pid resolved to pid/cmd/uid) at signal time, appended as
fields to the est-6226 class constant. The class constant stays the verbatim
prefix (every pre-32b reader keeps matching); 'gateway restart' is still never
claimed — the record names the MEASURED sender process, not an interpretation.

Rows (Linux only; the siginfo leg is linux):
  A  a SIGTERM from an identified live sender lands runner_exit.json whose
     reason keeps the class constant as prefix AND carries killer_pid,
     killer_cmd containing the sender's argv marker, killer_uid == ours; the
     process still dies the default SIGTERM (rc -15 — the door's reaper
     semantics unchanged).
  B  a clean exit writes no SIGTERM runner_exit record (atexit path untouched).

Run: cd tests && python3 test_killer_attribution_32b.py
"""
import json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

CLASS = "terminated: SIGTERM (external: source unknown)"

PROBE = """
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import wf
wf._install_runner_term_cleanup({"_run": Path(sys.argv[2])})
print("READY", flush=True)
time.sleep(30)
"""

def run_probe(tmp):
    run = Path(tmp) / "run"
    run.mkdir()
    (run / "graph.json").write_text(json.dumps({"name": "kill32b", "nodes": []}))
    p = subprocess.Popen([sys.executable, "-c", PROBE, str(BUILD), str(run)],
                         stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "READY", "probe never armed"
    return p, run

if sys.platform != "linux" or os.uname().machine not in ("x86_64", "aarch64"):
    print("SKIP (siginfo leg is linux x86_64/aarch64)")
    print("QH32B_OK"); sys.exit(0)

# The route is stdlib sigwaitinfo (no syscall-number games): available on
# every linux the door runs on. Degradation to the plain handler (no fields)
# only when signal.sigwaitinfo is missing — belt asserted, prefix+rc rows
# hold for BOTH routes on every host.
FIELDS = hasattr(signal, "sigwaitinfo")

with tempfile.TemporaryDirectory() as tmp:
    p, run = run_probe(tmp)
    # A sender that STAYS ALIVE while the runner records: /proc/<pid>/cmdline
    # is a race against a quick /bin/kill's reap, and the argv marker proves
    # the record names the measured sender, not a guess.
    sender = subprocess.Popen([sys.executable, "-c",
        "import os, signal, sys, time; os.kill(int(sys.argv[2]), signal.SIGTERM); time.sleep(10)",
        "kill32b_sender", str(p.pid)])
    rc = p.wait(timeout=15)
    sender.kill(); sender.wait()
    rec = json.loads((run / "runner_exit.json").read_text())
    reason = rec.get("reason", "")
    check("A still dies the default SIGTERM (rc -15, door reaper unchanged)", rc == -15, f"rc={rc}")
    check("A class constant stays the verbatim prefix", reason.startswith(CLASS), reason[:160])
    check("A no interpretation word", "gateway restart" not in reason, reason)
    if FIELDS:
        check("A reason names a numeric killer_pid", any(
            t.startswith("killer_pid=") and t.split("=", 1)[1].isdigit()
            for t in reason.split()), reason)
        check("A killer_cmd carries the sender's argv marker", "kill32b_sender" in reason, reason)
        check(f"A killer_uid matches this uid ({os.getuid()})",
              f"killer_uid={os.getuid()}" in reason, reason)
    else:
        print("SKIP-FIELDS (sigwaitinfo unavailable on this host — fallback handler row only)")

with tempfile.TemporaryDirectory() as tmp:
    run2 = Path(tmp) / "run2"
    subprocess.run([sys.executable, "-c", PROBE.replace("time.sleep(30)", "time.sleep(0.2)"),
                    str(BUILD), str(run2)], stdout=subprocess.DEVNULL, timeout=20)
    check("B clean exit writes no SIGTERM runner_exit record (atexit path untouched)",
          not (run2 / "runner_exit.json").exists())

print("QH32B_" + ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
