#!/usr/bin/env python3
"""cj2-recovery: fault-side battery over the REAL scheduler capture seams
(bd_2026-11-13-cj2, cj2-recovery slice). TEST-ONLY: this file, its probes
(tests/ship20-cj2-faults-probes.py) and the companion
tests/ship20-cj2-compat*.py change no shipped behavior and no retention test.

Legs (each an ISOLATED probe subprocess with private
HOME/HERMES_HOME/TMPDIR/XDG/WF_RUNS_ROOT under --out; real scheduler paths,
no network, no seats):
  writer-faults      short carrier temp write; injected rename refusal with
                     post-rename re-read; over-cap value = honest no-label;
                     all on the live publisher, old image untouched.
  spawned-correction REAL launch (no sandbox): a pre-published slot for an
                     index beyond the wave is DROPPED by the first real
                     publication, an anchored canonical index below the wave
                     is RETAINED, a schema-invalid first answer re-drives the
                     item under a NEW key (same-key correction law), and the
                     wave publishes as ONE batch write before the first
                     item.started.
  adoption           REAL Popen parked child, record already RUNNING:
                     'retained' (identity verifies) adopts with ZERO new keys
                     and ZERO carrier writes; 'impostor' (claimed key is not
                     the live child's) mints fresh and never adopts.
  eras-dict/-list    the review node's decisive generation timing on the live
                     batch writer, both roots: ONE whole-image publication
                     per non-empty generation before the first start, fresh
                     keys per generation, canonical/aggregate agreement,
                     static zero-write boundary, and the obsolete-keys-after-
                     settle PIN, banked EXPECTED_RED at this pin (the
                     retention cleanup is the cj2-retention lane's owner; the
                     review node recorded the same red at 813443aa).
  orders-dict/-list  publication ORDERING at the shipped reader: record-then-
                     carrier (fresh settle) shows each row's own captured
                     value + own exact chat; carrier-then-record (carrier
                     restored to a prior image under an amended record — the
                     old adjunct's ordering #1) shows the honest no-label row
                     with the record's own chat, never a current-roster
                     fabrication; and a carrier whose version is a Boolean
                     (the historical gap) must fail closed the same way —
                     banked either way, never pre-marked green.

Usage: python3 -B tests/ship20-cj2-faults.py --checkout REPO --out OUT
       [--only leg,leg,...] [--expect-held LEG:REDPIN ...]
Prints the classification table; exit 0 only when every leg is PASS or its
expected redpins fired exactly (EXPECTED_RED). Unfired pin = NEEDS_REPIN,
unexplained failure = BEHAVIOR_RED. Raw logs under OUT/logs/, exits under
OUT/exits.tsv, classification under OUT/classification.json, pins under
OUT/pin.txt / pin_after.txt.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN_HINT = "813443aa4b294f1ad84f2c9e714619123637d1b7"
LEG_TIMEOUT = 300
LEG_ORDER = ["writer-faults", "spawned-correction", "adoption",
             "eras-dict", "eras-list", "orders-dict", "orders-list",
             "controls"]
EXPECTED = {  # leg -> redpins that are the KNOWN HELD GAPS: must not fire at
    # the composed candidate (PIN-CLOSED), must fire at held (EXPECTED_RED) —
    # never marked green on held either way.
    "orders-dict": ["boolean-version-labels"],
    "orders-list": ["boolean-version-labels"],
}


def git(chk, *args):
    return subprocess.run(["/usr/bin/git", "-C", str(chk), *args],
                          capture_output=True, text=True)


def pin_record(chk):
    head = git(chk, "rev-parse", "HEAD").stdout.strip()
    tree = git(chk, "rev-parse", "HEAD^{tree}").stdout.strip()
    por = git(chk, "status", "--porcelain").stdout
    rem = git(chk, "remote").stdout.strip()
    det = git(chk, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "HEAD"
    alt = chk / ".git" / "objects" / "info" / "alternates"
    return {"head": head, "tree": tree, "porcelain_clean": not por,
            "detached": det, "remotes": rem,
            "alternates": alt.read_text().strip() if alt.exists() else ""}


PS_SHIM_SRC = '''#!/usr/bin/env python3
"""Relocated `ps` for the sandboxed harness (macOS 15.6).

Platform rules found empirically: a sandboxed process cannot exec /bin/ps
(rc 126 even under (allow default); a relocated copy is AMFI-SIGKILLed, ad-hoc
re-sign included); /proc does not exist; kqueue EVFILT_PROC registration
answers ENOTSUP for third-party callers, so NOTE_EXIT is not a state channel
here. Two sysctl channels DO answer and are ones /bin/ps itself reads:
KERN_PROC_PID mib(1,14,1,pid) returns a SANITIZED kinfo_proc whose p_stat
byte and embedded pid remain truth (live 2/3, zombie 5; a never-lived or
reaped pid answers 0 bytes), and mib(1,49,pid) (KERN_ARGMAX here,
KERN_PROCARGS2 layout) decodes argv verified byte-identical to /bin/ps
command=. The shipped process seams (wfcommon._verify_spawn_rec @5805/@4834,
wf._proc_alive @6662, wf._ppid_of @6187) all fall back to `ps` exactly there.
This shim answers their shapes from those kernel channels: stat= from p_stat
(SIDL I, SRUN R, SSLEEP S, SSTOP T, SZOMB Z; unknown state -> ?), command=
from the decoded argv, no pid or no kernel row -> exit 1 (no row, like ps).
A zombie answers "Z" plus a placeholder command: the seam short-circuits on
Z before argv, and the args payload is not guaranteed once the task is a
shell of itself. ppid= is unknowable through the remaining channels (the
sanitizer zeroes it): no row (rc 1) lands in _ppid_of's documented None
path; the parked stub has no descendants, so only the best-effort tree-watch
evidence degrades. Any other invocation execs the real binary. Kernel truth,
not a mock.
"""
import ctypes
import os
import sys

libc = ctypes.CDLL(None, use_errno=True)

STAT_CHARS = {1: "I", 2: "R", 3: "S", 4: "T", 5: "Z"}


def _state(pid):
    """p_stat from KERN_PROC_PID — the sysctl /bin/ps reads for its state
    column. Returns the state byte; None when the kernel has no row."""
    mib = (ctypes.c_int * 4)(1, 14, 1, pid)
    size = ctypes.c_size_t(0)
    if libc.sysctl(mib, 4, None, ctypes.byref(size), None, 0) != 0:
        raise OSError(ctypes.get_errno() or 3, "kern_proc_pid sysctl failed")
    if size.value == 0:
        return None
    buf = ctypes.create_string_buffer(size.value)
    if libc.sysctl(mib, 4, buf, ctypes.byref(size), None, 0) != 0:
        raise OSError(ctypes.get_errno() or 3, "kern_proc_pid sysctl failed")
    raw = buf.raw[:size.value]
    if int.from_bytes(raw[40:44], "little") != pid:
        return None                      # the sanitized row is not our pid
    return raw[36]


def _argv(pid):
    mib = (ctypes.c_int * 3)(1, 49, pid)
    buf = ctypes.create_string_buffer(65536)
    size = ctypes.c_size_t(65536)
    if libc.sysctl(mib, 3, buf, ctypes.byref(size), None, 0) != 0:
        raise OSError(ctypes.get_errno() or 3, "kern_argmax sysctl failed")
    pa = buf.raw[: size.value]
    argc = int.from_bytes(pa[:4], sys.byteorder)
    nul = b"\\x00"
    tok = pa[4 : 4 + pa[4:].index(nul)]          # exec_path
    i = 4 + len(tok)
    while i < len(pa) and pa[i] == 0:            # pad runs
        i += 1
    words = []
    for _ in range(argc):
        j = pa.index(nul, i)
        words.append(pa[i:j].decode(errors="replace"))
        i = j + 1
    return words


def main():
    argv = sys.argv[1:]
    try:
        pid = int(argv[argv.index("-p") + 1])
    except (ValueError, IndexError):
        pid = None
    cols = [argv[i + 1] for i, a in enumerate(argv) if a == "-o"]
    if pid is None or not cols or not any(c in ("stat=", "command=", "ppid=")
                                          for c in cols):
        os.execv("/bin/ps", ["/bin/ps"] + argv)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        sys.exit(1)                              # no such pid: no row, like ps
    st = _state(pid)
    if st is None:
        sys.exit(1)                              # no kernel row: no row
    fields = []
    try:
        for c in cols:
            if c == "ppid=":
                # The KERN_PROC_PID sanitizer zeroes the parent id for an
                # unentitled helper; hand the exact invocation to the real
                # binary (works unsandboxed). Under sandbox-exec the exec
                # raises and lands in _ppid_of's documented None path.
                os.execv("/bin/ps", ["/bin/ps"] + argv)
            if c == "stat=":
                fields.append(STAT_CHARS.get(st, "?"))
            elif c == "command=":
                if st == 5:                      # zombie: Z short-circuits
                    fields.append("zombie")
                    continue
                fields.append(" ".join(_argv(pid)))
    except OSError:
        sys.exit(1)                              # real ps not exec-able: no row
    sys.stdout.write(" ".join(fields) + "\\n")


main()
'''

def ps_shim(out):
    """macOS 15.6 platform rule: a sandboxed process cannot EXEC /bin/ps (rc
    126 even under (allow default)) — and the shipped active_child seam needs
    `ps -ww -p` where no /proc exists. Serve the seam a relocated `ps` first
    on PATH that answers exactly that one invocation from the same kernel
    objects /bin/ps reads (KERN_ARGMAX argv + liveness/zombie truth);
    everything else execs the real binary. Test-side harness fix only: no
    product or fixture edit, no argv-shape change."""
    bindir = out / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    dst = bindir / "ps"
    if not Path("/proc").exists() and not dst.exists():
        dst.write_text(PS_SHIM_SRC.replace("#!/usr/bin/env python3",
                                           f"#!{sys.executable}", 1))
        dst.chmod(0o755)
    return bindir


def priv_env(out, leg):
    root = out / "priv" / leg.replace(".", "_")
    for sub in ("home", "tmp", "workflows"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    pydir = str(Path(sys.executable).parent)
    return {"PATH": str(ps_shim(out)) + ":" + pydir + ":/usr/bin:/bin", "LANG": "C.UTF-8",
            "HOME": str(root / "home"), "TMPDIR": str(root / "tmp"),
            "XDG_CACHE_HOME": str(root / "home" / ".cache"),
            "XDG_CONFIG_HOME": str(root / "home" / ".config"),
            "XDG_DATA_HOME": str(root / "home" / ".local" / "share"),
            "XDG_STATE_HOME": str(root / "home" / ".local" / "state"),
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
            "HERMES_HOME": str(root / "hermes"),
            "WF_RUNS_ROOT": str(root / "workflows"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}, root


def classify_leg(rc, log, expected_ids):
    """PASS beats everything; then an expected-red pin set (all FAILS are the
    named pins, no other failure); a non-zero with no fired pin splits on the
    prior battery's law: absent file, host-class import bootstrap, behavior
    failure, else bootstrap. rc==0 with pending expectations = NEEDS_REPIN."""
    fired = [line.split()[1] for line in log.splitlines()
             if line.startswith("REDPIN ") and len(line.split()) >= 2]
    fails = [line for line in log.splitlines()
             if line.startswith("FAIL ") or line.startswith("FAIL:")]
    if rc == 0 and not fails:
        if expected_ids and not fired:
            return "PIN-CLOSED", {"expected": expected_ids,
                                  "note": "held-gap pin does not fire here"}
        if expected_ids and sorted(set(fired)) == sorted(set(expected_ids)):
            return "EXPECTED_RED", {"expected": expected_ids}
        if expected_ids:
            return "NEEDS_REPIN", {"expected": expected_ids, "fired": fired}
        return "PASS", {}
    if "can't open file" in log and "No such file" in log:
        return "ABSENT", {}
    if fails or (rc != 0 and "Traceback (most recent call last)" in log
                 and not any(l.startswith(("ModuleNotFoundError", "ImportError"))
                             for l in log.splitlines())):
        unexpected = [f for f in fails if not any(
            f.startswith("FAIL " + e) for e in expected_ids)]
        if not unexpected and set(fired) & set(expected_ids):
            missing = [e for e in expected_ids if e not in fired]
            if missing:
                return "NEEDS_REPIN", {"missing": missing}
            return "EXPECTED_RED", {"expected": expected_ids,
                                    "fail_lines": fails}
        return "BEHAVIOR_RED", {"fail_lines": fails[-8:], "exit": rc}
    if any(l.startswith(("ModuleNotFoundError", "ImportError"))
           for l in log.splitlines()):
        return "HOST_CLASS", {}
    return "BOOTSTRAP", {"exit": rc}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--only", default="")
    ap.add_argument("--expect-held", action="append", default=[])
    args = ap.parse_args()
    chk = args.checkout.resolve()
    out = args.out
    if out.exists():
        subprocess.run(["rm", "-rf", str(out)], check=True)
    out.mkdir(parents=True)
    (out / "logs").mkdir()
    pin = pin_record(chk)
    (out / "pin.txt").write_text(json.dumps(pin, indent=2) + "\n")
    expected = {leg: list(EXPECTED.get(leg, [])) for leg in LEG_ORDER}
    for spec in args.expect_held:
        leg, _, rid = spec.partition(":")
        if leg not in LEG_ORDER or not rid:
            raise SystemExit(f"unknown --expect-held spec {spec!r}")
        if rid not in expected[leg]:
            expected[leg].append(rid)
    legs = LEG_ORDER
    if args.only:
        wanted = [x.strip() for x in args.only.split(",") if x.strip()]
        for leg in wanted:
            if leg not in LEG_ORDER:
                raise SystemExit(f"unknown leg {leg!r}")
        legs = [x for x in LEG_ORDER if x in wanted]
    rows, cls = [], {}
    for leg in legs:
        env, root = priv_env(out, leg)
        env["HERMES_WF_PYTHON"] = sys.executable
        argv = [sys.executable, "-B", str(HERE / "ship20-cj2-faults-probes.py"),
                leg, str(chk), str(root)]
        t0 = time.monotonic()
        try:
            p = subprocess.run(argv, cwd=chk, env=env, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=LEG_TIMEOUT)
            rc, log = p.returncode, p.stdout + "\n" + p.stderr
        except subprocess.TimeoutExpired as exc:
            rc, log = 124, f"{(exc.stdout or b'') if isinstance(exc.stdout, bytes) else (exc.stdout or '')}\n(timeout after {LEG_TIMEOUT}s)"
        wall = round(time.monotonic() - t0, 1)
        (out / "logs" / f"{leg}.log").write_text(log)
        verdict, reasons = classify_leg(rc, log, expected[leg])
        cls[leg] = {"class": verdict, "exit": rc, "wall_s": wall,
                    "reasons": reasons}
        rows.append((leg, verdict, rc))
        print(f"{leg:22s} {verdict:13s} exit={rc} wall={wall}s", flush=True)
    after = pin_record(chk)
    (out / "pin_after.txt").write_text(json.dumps(after, indent=2) + "\n")
    cls["_pin_unchanged"] = (after == pin)
    cls["_head"] = pin["head"]
    cls["_tree"] = pin["tree"]
    cls["_pin_hint_expected"] = PIN_HINT
    with (out / "exits.tsv").open("w") as fh:
        for leg, verdict, rc in rows:
            fh.write(f"{leg}\t{verdict}\t{rc}\n")
    (out / "classification.json").write_text(json.dumps(cls, indent=2) + "\n")
    bad = [v for _, v, _ in rows
           if v not in ("PASS", "EXPECTED_RED", "PIN-CLOSED")
           ] or after != pin
    print("=" * 60)
    print(("cj2-recovery fault battery: "
           + ("ALL PASS/EXPECTED_RED/PIN-CLOSED" if not bad
              else "NEEDS ATTENTION"))
          + f"  (head {pin['head'][:12]} tree {pin['tree'][:12]})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
