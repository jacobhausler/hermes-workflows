#!/usr/bin/env python3
"""est-fj629 — rerunnable census scan-latency measurement (>=3000 run dirs).

Gauntlet #1 line 9 (w1-02): RUNS_CACHE_TTL and the desktop refetch cadence
shipped as intent, with one in-file number (1.06-1.29s over ~560 dirs,
est-ey31s) and no artifact. This script is that artifact's machine:

  seeds synthetic valid run dirs (the 7ps8 trio: graph.json + run.json +
  nodes/<id>.json, a share with logs/ so `executed` is non-zero) at two
  census sizes, times the dashboard's own _scan_runs() cold + warm, and
  writes a JSON report the shipped constants cite.

The trio shape and the dual-root env (owner setting runs_root + a separate
legacy WF_RUNS_ROOT) mirror tests/test_runs_offloop_ey31s.py, so what is
measured is the exact walk production serves.

Run (from the repo root):
    python3 scripts/bench_census_latency.py --json docs/measurements/census-scan-latency.json

Flags: --sizes 600,3000,6000 (default) --reps 5 --logs-ratio 0.35 --keep
(leave the seed tree). The committed artifact at the 3000-dir bound is what
the shipped constants cite; the 6000 row is the linearity control (2x bound).
"""
import argparse, json, os, platform, shutil, statistics, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def seed_run(root: Path, name: str, *, logs: bool, idx: int) -> None:
    """The smallest shape run_state accepts (tests/test_runs_offloop_ey31s)."""
    r = root / name
    (r / "nodes").mkdir(parents=True)
    if logs:
        (r / "logs").mkdir()
        (r / "logs" / "a.log").write_text("line\n")
    (r / "graph.json").write_text(json.dumps({"name": name[-4:], "nodes": [
        {"id": "a", "type": "agent", "goal": "x"}]}))
    (r / "run.json").write_text(json.dumps({"run_id": name, "name": name[-4:],
                                            "started": "2099-01-01T00:00:00+00:00",
                                            "seq": idx}))
    sys.path.insert(0, str(ROOT))
    import wfcommon
    (r / "nodes" / "a.json").write_text(json.dumps(
        {"status": "done", "output": {"answer": "ok"}, "efp": "",
         "fp_rule_version": wfcommon.FP_RULE_VERSION}))


def seed_census(root: Path, n: int, logs_ratio: float) -> int:
    for i in range(n):
        seed_run(root, "2099%02d%02d-%06d-bench" % (1 + i // 28 % 12,
                                                    1 + i // 340 % 28, i),
                 logs=(i % 100 < int(logs_ratio * 100)), idx=i)
    return n


def load_dashboard():
    import importlib.util
    os.environ["WF_RUNS_ROOT"] = str(Path(os.environ["_BENCH_LEGACY"]))
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "dashBench", str(ROOT / "dashboard" / "plugin_api.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def measure(n: int, reps: int, logs_ratio: float, base: Path):
    resolved = base / ("seed-%d" % n)
    resolved.mkdir(parents=True)
    os.environ["_BENCH_SEED"] = str(resolved)
    seed_census(resolved, n, logs_ratio)
    dash = load_dashboard()
    dash._workflow_common().set_owner_setting_reader(
        lambda key: (str(resolved) if key == "runs_root" else None))
    # cold: first scan after seeding (dentries not hot)
    t0 = time.perf_counter()
    rec = dash._scan_runs()
    cold = time.perf_counter() - t0
    assert rec["total"] == n, "census lost rows: %r" % rec["total"]
    assert rec["counts"]["executed"] > 0, "no executed rows seeded"
    warm = []
    for _ in range(reps):
        t0 = time.perf_counter()
        dash._scan_runs()
        warm.append(time.perf_counter() - t0)
    return {"n_dirs": n,
            "rows_total": rec["total"],
            "rows_executed": rec["counts"]["executed"],
            "cold_s": round(cold, 4),
            "warm_s": [round(w, 4) for w in warm],
            "warm_min_s": round(min(warm), 4),
            "warm_median_s": round(statistics.median(warm), 4),
            "warm_max_s": round(max(warm), 4),
            "median_ms_per_dir": round(1000.0 * statistics.median(warm) / n, 3)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sizes", default="600,3000,6000")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--logs-ratio", type=float, default=0.35)
    ap.add_argument("--json", default=None, help="write report here")
    ap.add_argument("--keep", action="store_true", help="keep the seed tree")
    a = ap.parse_args()

    base = Path(tempfile.mkdtemp(prefix="wf-census-bench-",
                                 dir=os.environ.get("TMPDIR", "/tmp")))
    legacy = base / "legacy"
    legacy.mkdir()
    os.environ["_BENCH_LEGACY"] = str(legacy)
    os.environ["HERMES_HOME"] = str(base / "home")

    try:
        results = [measure(int(n), a.reps, a.logs_ratio, base)
                   for n in a.sizes.split(",")]
        msd = [r["median_ms_per_dir"] for r in results]
        report = {
            "schema": "wf-census-scan-latency/v1",
            "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "git_sha": os.popen("git -C %s rev-parse HEAD" % ROOT).read().strip()
                       or "unknown",
            "machine": {"system": platform.system(), "machine": platform.machine(),
                        "cores": os.cpu_count(),
                        "python": platform.python_version()},
            "seed": {"shape": "graph.json + run.json + nodes/<id>.json",
                     "logs_ratio": a.logs_ratio, "reps": a.reps},
            "results": results,
            "linearity_ms_per_dir": {"small": msd[0], "large": msd[-1],
                                     "slope_small_over_large": round(msd[0] / msd[-1], 3)},
        }
        if a.json:
            out = Path(a.json)
            if not out.is_absolute():
                out = ROOT / out
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    finally:
        if not a.keep:
            shutil.rmtree(base, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
