"""Self-terminating watchdog tick: a NAME-KEYED SINGLETON cron job (dormant until PR-3).

Dead runners — a spawner killed before it wrote ``runner_exit.json`` — sit
``interrupted`` until some later mutation or resume path notices them. The tick
closes that gap on the scheduler's own cadence: one core cron job,
``no_agent=True`` (its stdout IS the job; zero agent wakes), armed idempotently
by launch and torn down BY THE TICK ITSELF once no active run remains. This
module is the lifecycle half only: arm, find, teardown, and the shim the job
runs. The tick body (revive + drain-self-delete) and the boot-time arm land
in the follow-on PRs; nothing here calls this module yet.

Singleton law (why no tick table, no per-run jobs, no counters): the job is
keyed BY NAME (``TICK_NAME``), so arming is find-then-create — a re-arm on
every launch converges on exactly one row, and teardown is DELETION, never a
disable. Disabled-but-kept jobs accumulate as zombie rows; a deleted job is
physically absent while the active-run set is empty, which is what makes
"zero idle wakes" a structural fact rather than a polling promise.

Script law: core's scheduler only executes job scripts that resolve inside
``<HERMES_HOME>/scripts/`` (``cron/scheduler_script.py`` validates the path and
blocks traversal/symlink escapes), and it invokes them with no arguments — so
each purpose gets a generated executable bash shim that execs this plugin's
absolute ``wf.py`` entrypoint with its subcommand baked in.

Launcher law (P41). Baked data shape — ``<HERMES_HOME>/scripts/<name>.sh``::

    #!/usr/bin/env bash
    exec <INTERPRETER> <WF_PY> <arg>...

``<INTERPRETER>`` is absolute (``WF_TICK_PYTHON`` > ``sys.executable``, the
bundled python that ran the bake) and the entrypoint rides as an ARGUMENT, so
the launch depends on neither ``wf.py``'s exec bit (the interpreter reads it)
nor its ``#!/usr/bin/env python3`` shebang (never resolved) — a plugin
reinstall that lands ``wf.py`` as 0644, or resolves ``env python3`` to the
macOS 3.9.6 system python, cannot silently revert the tick. The shim re-bakes
on every ``ensure_tick`` and ``selfcheck_tick`` call and rewrites only on
drift (content or exec mode), so a clobbered launcher converges back at the
next launch/tick/selfcheck and a settled one is left byte- and mtime-stable.

Degradation is SILENT (AGENTS.md 4c rules 7-8): a host with no importable core
cron (system Python on a local-backend Mac) gets ``ensure_tick() -> None`` and
``teardown_tick() -> False``; the launcher it serves never fails over the tick.
"""
import os
import shlex
import subprocess
import sys
from pathlib import Path

TICK_NAME = "hermes-workflows-tick"
DEFAULT_TICK_SCHEDULE = "every 2m"

PLUGIN_ROOT = Path(__file__).resolve().parent
WF_PY = PLUGIN_ROOT / "wf.py"


def _jobs():
    """The core ``cron.jobs`` module, or None where no core is importable.

    THE test seam: tests inject a fake jobs module here — the live cron store
    is never touched. Host import stays lazy + guarded (AGENTS.md 4c rule 7);
    a core whose surface moved is honestly None, never a half-bound module."""
    try:
        import importlib
        cj = importlib.import_module("cron.jobs")
    except Exception:
        return None
    if not all(callable(getattr(cj, a, None))
               for a in ("list_jobs", "create_job", "remove_job")):
        return None
    return cj


def _home():
    """The hermes home the scripts dir lives under — core-resolved when
    importable, else ``$HERMES_HOME``, else ``$HOME/.hermes`` (the one law
    wfcommon's resolvers use, kept stdlib-only here)."""
    try:
        from hermes_constants import get_hermes_home
        return Path(get_hermes_home())
    except Exception:
        return Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))


def _config_tick_schedule(core_config=None):
    """``workflows.tick_schedule`` from config: the caller-injected mapping,
    else a core-first read (``load_config_readonly``), then a lite top-level
    scan of ``<home>/config.yaml`` for bare hosts (the seat_max_seats shape —
    resolved at every use, never baked). A provided ``core_config`` mapping IS
    the config answer: no scan behind a caller's back."""
    raw = None
    if core_config is None:
        try:
            from hermes_cli.config import load_config_readonly
            cfg = load_config_readonly()
            if cfg:
                w = cfg.get("workflows")
                if isinstance(w, dict):
                    raw = w.get("tick_schedule")
        except Exception:
            raw = None
        if raw is None:
            try:
                lines = (_home() / "config.yaml").read_text().splitlines()
            except OSError:
                lines = []
            section = None
            for line in lines:
                line = line.split(" #", 1)[0]
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                indent = len(line) - len(line.lstrip())
                text = line.strip()
                if indent == 0:
                    section = text.partition(":")[0]
                elif section == "workflows" and indent == 2:
                    key, _, scalar = text.partition(":")
                    if key == "tick_schedule" and scalar.strip():
                        raw = scalar.strip().strip("'\"")
                        break
    elif isinstance(core_config, dict):
        w = core_config.get("workflows")
        if isinstance(w, dict):
            raw = w.get("tick_schedule")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def tick_schedule(core_config=None):
    """The tick cadence: WF_TICK_SCHEDULE env > config workflows.tick_schedule
    > DEFAULT_TICK_SCHEDULE. Validity of the string is core's law —
    ``create_job`` parses the schedule and refuses what it cannot parse."""
    env = (os.environ.get("WF_TICK_SCHEDULE") or "").strip()
    if env:
        return env
    return _config_tick_schedule(core_config) or DEFAULT_TICK_SCHEDULE


def _launcher_line(*args):
    """The P41 exec line: absolute interpreter, entrypoint as argument."""
    interp = (os.environ.get("WF_TICK_PYTHON") or "").strip() or sys.executable
    parts = ["exec", str(interp), str(WF_PY)] + [str(a) for a in args]
    return " ".join(shlex.quote(p) for p in parts) + "\n"


def write_shim(name, *args):
    """Write ``<HERMES_HOME>/scripts/<name>.sh``: an executable bash shim whose
    body is the P41 interpreter-pinned launcher line (the core scheduler runs
    job scripts argument-free, and only inside that dir). Rewrites only on
    drift (content or exec mode) — a re-bake converges and leaves a settled
    launcher byte- and mtime-stable, so re-runs never clobber it.
    Refuse a nonresident entrypoint before creating or changing any file."""
    from wfcommon import entrypoint_residency
    status, detail = entrypoint_residency(str(WF_PY))
    if status != "resident":
        raise ValueError(f"refusing to bake {WF_PY} into a persisted cron shim: {status} "
                         f"({detail}); a cron entrypoint must live at a stable install root")
    scripts = _home() / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    path = scripts / f"{name}.sh"
    body = "#!/usr/bin/env bash\n" + _launcher_line(*args)
    try:
        settled = path.read_text() == body and path.stat().st_mode & 0o111
    except OSError:
        settled = False
    if not settled:
        path.write_text(body)
        path.chmod(0o755)
    return path


def find_tick():
    """The tick job record (disabled ones included — deletion is the only
    egress), or None. Honest None on a cron-less host."""
    cj = _jobs()
    if cj is None:
        return None
    for job in cj.list_jobs(include_disabled=True):
        if job.get("name") == TICK_NAME:
            return job
    return None


def ensure_tick(core_config=None):
    """Arm the singleton: return the existing job id, else create exactly one
    no_agent job and return its id. Double-arm is idempotent BY NAME. On a
    host without core cron this is a silent no-op returning None — a launch
    must never fail because of the tick. When the job already exists the
    launcher is re-baked before returning the id (P41: a plugin update that
    cleared the exec bit or baked a stale interpreter is repaired by the
    next arm; a nonresident entrypoint leaves the settled launcher honestly
    untouched)."""
    cj = _jobs()
    if cj is None:
        return None
    existing = find_tick()
    if existing is not None:
        try:
            write_shim(TICK_NAME, "tick")
        except ValueError:
            pass
        return existing["id"]
    shim = write_shim(TICK_NAME, "tick")
    job = cj.create_job(prompt=None, schedule=tick_schedule(core_config),
                        name=TICK_NAME, script=str(shim), no_agent=True)
    return job["id"]


def teardown_tick():
    """Delete the tick job; True when a job was removed, False when absent.
    Deletion, never disable — while the active-run set is empty no row is
    left behind to wake anything."""
    cj = _jobs()
    if cj is None:
        return False
    existing = find_tick()
    if existing is None:
        return False
    return bool(cj.remove_job(existing["id"]))


def selfcheck_tick(run=None):
    """Post-update self-check (P41): re-pin the launcher, run the tick once
    through the baked shim exactly as the scheduler will, and report its rc.
    ``run(argv) -> rc`` is the test seam; the default runs under bash, the
    same interpreter the core scheduler picks for a ``.sh`` job script.
    Honest on any host: with no active runs the tick drains (deletes its own
    job) and still exits 0 — that is the singleton's designed behavior."""
    shim = write_shim(TICK_NAME, "tick")
    if run is None:
        run = lambda argv: subprocess.run(argv, capture_output=True,
                                          text=True, timeout=120).returncode
    rc = int(run(["/bin/bash", str(shim)]))
    return {"rc": rc, "shim": str(shim), "ok": rc == 0}


if __name__ == "__main__":
    # Operator one-liner after `hermes plugins update`: run the tick once and
    # report it. Exit code IS the tick's exit code; the line names the shim.
    if (sys.argv[1] if len(sys.argv) > 1 else "") != "selfcheck":
        print("usage: python3 cron_bridge.py selfcheck")
        raise SystemExit(2)
    _report = selfcheck_tick()
    print(f"TICK SELFCHECK rc={_report['rc']} shim={_report['shim']}")
    raise SystemExit(_report["rc"])
