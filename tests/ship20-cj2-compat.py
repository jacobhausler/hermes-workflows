#!/usr/bin/env python3
"""cj2-compat: frozen publication-ordering battery over the shipped reader
(bd_2026-11-13-s20-cj2-recovery). TEST-ONLY: this file and its probes
(tests/ship20-cj2-compat-probes.py) change no shipped behavior, no
historical fixture byte and no writer probe.

Legs (each an ISOLATED probe subprocess with private
HOME/HERMES_HOME/TMPDIR/XDG/WF_RUNS_ROOT under --out; no network, no seats):
  ordering-views     record-first vs carrier-behind-record at the shipped
                     reader; a wrong/stale carrier input never supplies
                     another label (pin: stale-carrier-supplies-label);
                     chats ride the record exactly on every world.
  version-shape      the Boolean/float version kept STRICTLY DISTINGUISHED
                     from missing legitimate metadata (pins:
                     boolean-version-labels, float-version-labels).
  unnamed-history    the pre-bounditem shape: label absent, never re-derived;
                     every unnamed history keeps its OWN chat (pin:
                     unnamed-history-loses-chat).
  control-static-roster / control-writer-probes
                     the POSITIVE controls: the static positional roster
                     keeps painting under the identical mutations and the
                     capture seam round-trips through the product's own
                     writer — at every root, or the battery is BEHAVIOR_RED.
  legacy-orders-dict / legacy-orders-list
                     the committed battery's own orders legs, re-driven
                     UNCHANGED against this checkout (no era re-runs, no
                     controls legs, no writer-fault re-run): the child
                     battery's own classification is passed through.

Usage: python3 -B tests/ship20-cj2-compat.py --checkout REPO --out OUT
       [--only leg,leg,...] [--expect-held LEG:REDPIN ...]
--expect-held names the pins that are the KNOWN HISTORICAL (held-pin) gaps:
they must fire at the held root (then classify EXPECTED_RED — a banked red,
never green) and must NOT fire at a fixed root (then the leg classifies
PIN-CLOSED). An unexplained failure is BEHAVIOR_RED, an expected pin that
did not fire is NEEDS_REPIN; both fail the battery. Exit 0 only when every
leg is PASS/EXPECTED_RED/PIN-CLOSED. Raw logs under OUT/logs/, exits under
OUT/exits.tsv, classification under OUT/classification.json, pin under
OUT/pin.txt / pin_after.txt, per-world view-row evidence under OUT/banks/,
the child battery's own artifacts under OUT/legacy/.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEG_TIMEOUT = 300
LEG_ORDER = ["ordering-views", "version-shape", "unnamed-history",
             "control-static-roster", "control-writer-probes",
             "legacy-orders-dict", "legacy-orders-list"]
NEW_LEGS = LEG_ORDER[:5]
LEGACY = {"legacy-orders-dict": "orders-dict",
          "legacy-orders-list": "orders-list"}
PINNED = {  # redpin ids the battery knows as held-gap pins (opt-in via
            # --expect-held; never auto-expected on a fixed root).
    "ordering-views": ["stale-carrier-supplies-label"],
    "version-shape": ["boolean-version-labels", "float-version-labels"],
    "unnamed-history": ["unnamed-history-loses-chat"],
    "legacy-orders-dict": ["boolean-version-labels"],
    "legacy-orders-list": ["boolean-version-labels"],
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


def priv_env(out, leg):
    root = out / "priv" / leg.replace(".", "_")
    for sub in ("home", "tmp", "workflows"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    pydir = str(Path(sys.executable).parent)
    return {"PATH": pydir + ":/usr/bin:/bin", "LANG": "C.UTF-8",
            "HOME": str(root / "home"), "TMPDIR": str(root / "tmp"),
            "XDG_CACHE_HOME": str(root / "home" / ".cache"),
            "XDG_CONFIG_HOME": str(root / "home" / ".config"),
            "XDG_DATA_HOME": str(root / "home" / ".local" / "share"),
            "XDG_STATE_HOME": str(root / "home" / ".local" / "state"),
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
            "HERMES_HOME": str(root / "hermes"),
            "WF_RUNS_ROOT": str(root / "workflows"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "WORKFLOW_MAX_SEATS": "0",
            "http_proxy": "http://127.0.0.1:1", "https_proxy": "http://127.0.0.1:1",
            "HTTP_PROXY": "http://127.0.0.1:1", "HTTPS_PROXY": "http://127.0.0.1:1",
            "no_proxy": "", "NO_PROXY": ""}, root


def classify_leg(rc, log, expected_ids):
    """PASS beats everything; then an expected-red pin set (all FAILS are the
    named pins, no other failure); a non-zero with no fired pin splits on the
    prior battery's law: absent file, host-class import bootstrap, behavior
    failure, else bootstrap. rc==0 with pending expectations = PIN-CLOSED."""
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
        if fired:
            return "BEHAVIOR_RED", {"unexpected_pins": sorted(set(fired))}
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


def run_child_battery(chk, out, form, expect_ids):
    """Re-drive the committed battery's orders leg UNCHANGED (same
    classifier, same pins, same priv env under OUT/legacy)."""
    child_out = out / "legacy" / form
    env, _ = priv_env(out, "legacy-" + form)
    argv = [sys.executable, "-B", str(chk / "tests" / "ship20-cj2-faults.py"),
            "--checkout", str(chk), "--out", str(child_out),
            "--only", form]
    for rid in expect_ids:
        argv += ["--expect-held", f"{form}:{rid}"]
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, cwd=chk, env=env, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=LEG_TIMEOUT)
        rc, log = p.returncode, p.stdout + "\n" + p.stderr
    except subprocess.TimeoutExpired as exc:
        rc = 124
        log = f"{(exc.stdout or b'') if isinstance(exc.stdout, bytes) else (exc.stdout or '')}\n(timeout after {LEG_TIMEOUT}s)"
    wall = round(time.monotonic() - t0, 1)
    (out / "logs" / f"{form}.child.log").write_text(log)
    cls_file = child_out / "classification.json"
    if not cls_file.exists():
        return "BEHAVIOR_RED", rc, wall, {"note": "child battery wrote no "
                                          "classification", "tail": log[-400:]}
    child = json.loads(cls_file.read_text())
    verdict = (child.get(form) or {}).get("class", "BEHAVIOR_RED")
    # the child never sees a dirty tree from us: untracked compat files only
    if verdict == "BEHAVIOR_RED" and child.get("_pin_unchanged") is False:
        verdict = "BEHAVIOR_RED"
    return verdict, rc, wall, {"child_head": child.get("_head"),
                               "child_reasons": (child.get(form) or {}).get("reasons"),
                               "child_pin_unchanged": child.get("_pin_unchanged")}


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
    expected = {leg: [] for leg in LEG_ORDER}
    for spec in args.expect_held:
        leg, _, rid = spec.partition(":")
        if leg not in LEG_ORDER or not rid or rid not in PINNED.get(leg, []):
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
        if leg in LEGACY:
            verdict, rc, wall, reasons = run_child_battery(
                chk, out, LEGACY[leg], expected[leg])
            cls[leg] = {"class": verdict, "exit": rc, "wall_s": wall,
                        "reasons": reasons, "expected_pins": expected[leg]}
            rows.append((leg, verdict, rc))
            print(f"{leg:24s} {verdict:24s} exit={rc} wall={wall}s", flush=True)
            continue
        env, root = priv_env(out, leg)
        env["HERMES_WF_PYTHON"] = sys.executable
        argv = [sys.executable, "-B", str(HERE / "ship20-cj2-compat-probes.py"),
                leg, str(chk), str(root)]
        t0 = time.monotonic()
        try:
            p = subprocess.run(argv, cwd=chk, env=env, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=LEG_TIMEOUT)
            rc, log = p.returncode, p.stdout + "\n" + p.stderr
        except subprocess.TimeoutExpired as exc:
            rc = 124
            log = f"{(exc.stdout or b'') if isinstance(exc.stdout, bytes) else (exc.stdout or '')}\n(timeout after {LEG_TIMEOUT}s)"
        wall = round(time.monotonic() - t0, 1)
        (out / "logs" / f"{leg}.log").write_text(log)
        verdict, reasons = classify_leg(rc, log, expected[leg])
        cls[leg] = {"class": verdict, "exit": rc, "wall_s": wall,
                    "reasons": reasons, "expected_pins": expected[leg]}
        rows.append((leg, verdict, rc))
        print(f"{leg:24s} {verdict:24s} exit={rc} wall={wall}s", flush=True)
    banks = out / "priv" / "banks-merged"
    banks.mkdir(exist_ok=True)
    for d in (out / "priv").glob("*/banks"):
        for f in d.glob("*.json"):
            (banks / f"{d.parent.name}-{f.name}").write_bytes(f.read_bytes())
    (out / "banks").symlink_to("priv/banks-merged") if not (out / "banks").exists() else None
    after = pin_record(chk)
    (out / "pin_after.txt").write_text(json.dumps(after, indent=2) + "\n")
    cls["_pin_unchanged"] = (after == pin)
    cls["_head"] = pin["head"]
    cls["_tree"] = pin["tree"]
    with (out / "exits.tsv").open("w") as fh:
        for leg, verdict, rc in rows:
            fh.write(f"{leg}\t{verdict}\t{rc}\n")
    (out / "classification.json").write_text(json.dumps(cls, indent=2) + "\n")
    bad = [v for _, v, _ in rows
           if v not in ("PASS", "EXPECTED_RED", "PIN-CLOSED")
           ] or after != pin
    print("=" * 64)
    print(("cj2-compat battery: "
           + ("ALL PASS/EXPECTED_RED/PIN-CLOSED" if not bad
              else "NEEDS ATTENTION"))
          + f"  (head {pin['head'][:12]} tree {pin['tree'][:12]})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
