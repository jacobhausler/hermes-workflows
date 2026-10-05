"""est-2mhl: the child's work-dir write grant must survive the SERVED estate.

Under ``multiplex_profiles: true`` the child agent is served by the gateway
under its routed profile's bound secret scope. Core's
``agent.file_safety.get_safe_write_roots()`` reads ``HERMES_WRITE_SAFE_ROOT``
from that scope and REPLACES (never unions) the process-env value
(file_safety.py, the ``scope.get(name)`` branch). So the grant run_child
appends at spawn (``sr + os.pathsep + wd``) is silently dropped the moment
the served profile's ``.env`` carries its own value — the child is denied
writing into the very dir WORK_DIR_NOTE advertises as durable.

This is the failing repro for the issue: it asserts the DESIRED behaviour and
is RED against core today. The green half (what the plugin already controls)
is that run_child carries the grant in ``HERMES_WRITE_SAFE_ROOT_EXTRA``, the
deployment-scoped variable this PR proposes core to union unconditionally
(see the PR analysis).

Plain script: exit non-zero on any red; SKIP (exit 0) when core is not
importable so a CI runner without /opt/hermes does not false-fail.
"""
import os
import sys

try:
    from agent import file_safety, secret_scope
except Exception as exc:  # core not importable in this environment
    print("SKIP: core agent modules unavailable (%s)" % exc)
    sys.exit(0)

FAILS = []


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:400]))
    if not cond:
        FAILS.append(name)


BASE = "/srv/profile/base"
WD = "/srv/runs/est-2mhl/work/recon"


def served_roots(child_env_value, scope_value, multiplex=True):
    """Call core's resolver the way a served turn does: multiplex on, the
    profile's .env-derived scope bound, process env as run_child set it."""
    tok = secret_scope.set_multiplex_context(True) if multiplex else None
    stok = secret_scope.set_secret_scope(
        {"HERMES_WRITE_SAFE_ROOT": scope_value} if scope_value is not None else {},
        profile_home="/srv/profiles/worker",
    )
    try:
        return file_safety.get_safe_write_roots()
    finally:
        secret_scope.reset_secret_scope(stok)
        if tok is not None:
            secret_scope.reset_multiplex_context(tok)


def main():
    merged = BASE + os.pathsep + WD

    # --- legacy standalone case (multiplex off): works today, keep it green --
    os.environ["HERMES_WRITE_SAFE_ROOT"] = merged
    roots = served_roots(merged, None, multiplex=False)
    check("LEGACY process-env grant honored (multiplex off)",
          os.path.realpath(WD) in roots, roots)

    # --- THE BUG: served profile's scope REPLACES the runner's grant ---------
    os.environ["HERMES_WRITE_SAFE_ROOT"] = merged
    roots = served_roots(merged, BASE)
    check("MULTIPLEX work-dir grant survives the bound scope (est-2mhl)",
          os.path.realpath(WD) in roots,
          "core returned %r — process-env work-dir entry was replaced away" % (roots,))

    # --- proposal probe: a deployment-scoped EXTRA var core would union -----
    # RED today (core ignores the name); turns green with the proposed
    # core-side change (union os.environ[HERMES_WRITE_SAFE_ROOT_EXTRA]).
    os.environ["HERMES_WRITE_SAFE_ROOT"] = BASE
    os.environ["HERMES_WRITE_SAFE_ROOT_EXTRA"] = WD
    roots = served_roots(BASE, BASE)
    check("MULTIPLEX EXTRA grant honored (needs core change; expected RED pre-fix)",
          os.path.realpath(WD) in roots, roots)
    del os.environ["HERMES_WRITE_SAFE_ROOT_EXTRA"]

    # --- plugin-side invariant, green with this PR: run_child sets EXTRA ---
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import wf
    src = (wf.__file__ and open(wf.__file__, encoding="utf-8").read()) or ""
    check("RUNNER wf.py propagates the work-dir grant via HERMES_WRITE_SAFE_ROOT_EXTRA",
          "HERMES_WRITE_SAFE_ROOT_EXTRA" in src, "run_child must set EXTRA")
    check("RUNNER route keep-set forwards EXTRA under delegation",
          "HERMES_WRITE_SAFE_ROOT_EXTRA" in src.split("keep = {")[1].split("}")[0]
          if "keep = {" in src else False, "keep set must carry EXTRA")

    print(("\nRED: " if FAILS else "\n") + "%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
