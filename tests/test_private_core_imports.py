#!/usr/bin/env python3
"""Private core import allow-list probe (issue #456 item 1, bead est-i3d1b).

hermes-agent >= v0.22.0 added an admission lint to ``hermes plugins validate``:
the static pass in ``hermes_cli.plugin_validate_private_imports`` lists every
import this plugin performs of a PRIVATE Hermes core module. Each such import
is a coupling that can break on any core release (catalog rule 9: public
surfaces only). This test runs upstream's own ``private_import_findings()``
against this repo and compares the result against the reasoned allow-list
below:

  - a NEW private import not in the allow-list   -> FAIL, naming file:line target
  - an allow-listed row the lint no longer reports -> FAIL (delete the row)
  - an installed core without the lint (< v0.22.0, e.g. the requires_hermes
    floor) ->
    prints SKIP-reason + exit 0 (the suite must run on checkouts without it)

Keys are ``(file, target)``, never line numbers: lines drift on every refactor
(11 of 12 cites in the #456 table already moved between v0.22.2 @ d003e47 and
v0.22.5 @ main), the coupling itself is file + imported target.

Every row is soft-guarded at its call site — #456's probe called each importing
function with the target module blocked two ways (absent via
``sys.modules[m] = None`` and renamed) and every site degraded, none raised.
The per-site soft-guard test is #456 item 2 (separate PR). When adding a row:
name the guard and the observed fallback, or replace the import with a public
surface (none of these has one today — #456 checked v0.22.2's ``_PUBLIC`` set).

This file is also the canonical home of the AGENTS.md 4c rule-7 pointer
("Stdlib-only Python; host imports lazy and guarded"). The rule-7 doc line
itself could not land: AGENTS.md sits at 31,956/32,000 chars under the
repo's own hint-cap gate (tests/test_docs_hint_cap_73c.py — 44 chars of
headroom) and even a terse pointer overflowed it (probed at 32,001), so
#456's doc-line requirement collides with that cap; see the PR body. If
the cap ever gains ~200 chars of room, restore the line at 4c rule 7:
core-internal imports surviving this rule must stay pinned here — add or
delete rows with their guard + fallback, never silently.

Conventions (repo test style, same contract-probe class as
tests/test_upstream_hook_contract.py):
  - stdlib only
  - prints one PASS line per allow-list row plus summary lines
  - exit 0 = green (also green on cores without the lint: SKIP + exit 0)
  - empty or unparseable findings are RED, never a silent pass (audit #112
    lesson: empty discovery is a failure, not an absence of findings)

Run:  python3 tests/test_private_core_imports.py   (from the repo root)
"""
import importlib
import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The lint reports ``<rel>:<line> <dotted.target>`` per site.
FINDING_RE = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+) (?P<target>\S+)$")

# (file, target) -> reason the coupling is tolerated. Reasons record the
# soft guard + observed fallback verified in the #456 probe; the 12 original
# rows plus cron_bridge.py (added by #534 after the issue's d003e47 snapshot,
# which is exactly the drift this probe exists to catch).
ALLOW_LIST = {
    # --- agent.reasoning_effort: core's route-effort tables. No public
    # plugin surface covers them (#456 checked _PUBLIC at v0.22.2).
    ("__init__.py", "agent.reasoning_effort.route_supported_efforts"):
        "_route_efforts: except Exception -> wfcommon.reasoning_levels() table fallback",
    ("__init__.py", "agent.reasoning_effort.codex_supported_efforts"):
        "_route_efforts: same guard, same fallback",
    ("__init__.py", "agent.reasoning_effort.EFFORT_LADDER"):
        "_nearest_effort: except Exception -> None (caller skips the ladder step)",
    ("wf.py", "agent.reasoning_effort.route_supported_efforts"):
        "_resolve_child_reasoning: except Exception -> wfcommon.reasoning_levels() table",
    # --- hermes_cli.model_switch: alias resolution mirrors the picker's.
    ("__init__.py", "hermes_cli.model_switch.DIRECT_ALIASES"):
        "_alias_provider_pair: except Exception -> (None, None) (alias treated as raw)",
    ("__init__.py", "hermes_cli.model_switch._ensure_direct_aliases"):
        "_alias_provider_pair: same guard, same fallback",
    # --- agent.auxiliary_client: liveness pings need call_llm's route_info;
    # the public ctx.llm (agent.plugin_llm) lacks it and gates provider
    # overrides behind trust flags — switching would change the #25
    # same-route liveness law, an engine-semantics change (#456).
    ("__init__.py", "agent.auxiliary_client.call_llm"):
        "_import_call_llm raises by design; callers _ping_route_once/_ping_reachable "
        "degrade to liveness: unknown / False",
    # --- agent.retry_utils: backoff parsing for liveness retries.
    ("__init__.py", "agent.retry_utils.parse_retry_after_seconds"):
        "_ping_retry_after: except Exception -> None (caller uses default backoff)",
    # --- gateway.session_context: per-session env overlay for lane scopes.
    ("__init__.py", "gateway.session_context.get_session_env"):
        "_session_env: except ImportError -> plain os.environ value",
    # --- toolsets / hermes_cli.plugins: child toolset name validation is an
    # optional garnish; pass-through is the guarded path.
    ("wf.py", "toolsets.validate_toolset"):
        "_filter_child_toolsets: except Exception -> toolset names pass through",
    ("wf.py", "hermes_cli.plugins.get_plugin_toolset_keys_nowait"):
        "_filter_child_toolsets: same guard, same fallback",
    # --- hermes_yaml: core's YAML policy (round-trip); ruamel/PyYAML are the
    # guarded fallbacks so the plugin still reads graphs without core.
    ("wfcommon.py", "hermes_yaml.safe_load"):
        "_yaml_load: except ImportError -> ruamel, then PyYAML",
    # --- cron.jobs: tick-job lifecycle (landed by #534 after #456's table).
    ("cron_bridge.py", "cron.jobs"):
        "_jobs: except Exception -> None + callable surface check, never a "
        "half-bound module; tests inject a fake at this seam",
    ("wake_native.py", "hermes_cli.gateway_runtime.discover_gateway_endpoint"):
        "discover: except ImportError -> native unavailable (legacy compatibility); "
        "missing module and missing symbol exercised in test_wake_native_identity",
    ("wake_native.py", "hermes_cli.gateway_client.connect_gateway"):
        "_connect import failure is caught by deliver -> retry/transport_error, "
        "never another transport; missing module and symbol both exercised",
}


def load_lint():
    """Return (module, None), or (None, reason) when the core here has no lint.

    Discovery mirrors tests/test_upstream_hook_contract.py: locate the
    installed ``hermes_cli`` WITHOUT importing anything heavy, check the lint
    module's file exists (= core >= v0.22.0), and only then import it. File
    absent is the documented SKIP case; a present-but-unimportable lint is
    drift and goes RED, never silently green.
    """
    try:
        spec = importlib.util.find_spec("hermes_cli")
    except (ImportError, ValueError, ModuleNotFoundError):
        spec = None
    if spec is None or not spec.submodule_search_locations:
        return None, "hermes_cli is not importable in this environment"
    for loc in spec.submodule_search_locations:
        if (Path(loc) / "plugin_validate_private_imports.py").is_file():
            mod = importlib.import_module("hermes_cli.plugin_validate_private_imports")
            if not hasattr(mod, "private_import_findings"):
                raise RuntimeError(
                    f"{loc}/plugin_validate_private_imports.py exists but has no "
                    "private_import_findings — upstream moved the lint; update this probe"
                )
            return mod, None
    return None, "installed core predates the private-import lint (< v0.22.0; the requires_hermes floor v2026.9.21 is such a core)"


def main():
    lint, skip_reason = load_lint()
    if lint is None:
        print(f"SKIP-reason: {skip_reason}; private-import contract check deferred "
              "(suite-runs-without-lint case)")
        sys.exit(0)

    findings = lint.private_import_findings(REPO_ROOT)
    if not findings:
        # Vacuity guard (audit #112): this repo is known to import private
        # core modules; zero findings means the probe harness broke, not
        # that every coupling vanished.
        print(f"FAIL: private_import_findings({REPO_ROOT}) returned nothing — "
              "empty discovery is a failure, not an absence of findings")
        sys.exit(1)

    reported = set()
    first_line = {}
    for text in findings:
        m = FINDING_RE.match(text)
        if m is None:
            print(f"FAIL: unparseable lint finding {text!r} — upstream changed "
                  "the output format; update this probe")
            sys.exit(1)
        key = (m.group("file"), m.group("target"))
        reported.add(key)
        first_line.setdefault(key, int(m.group("line")))

    bad = False
    for key in sorted(reported - set(ALLOW_LIST)):
        print(f"FAIL: new private core import {key[0]}:{first_line[key]} {key[1]} — "
              "use a public surface, or add a reasoned row to ALLOW_LIST "
              "(AGENTS.md 4c rule 7)")
        bad = True
    for key in sorted(set(ALLOW_LIST) - reported):
        print(f"FAIL: allow-listed row {key[0]} {key[1]} is no longer reported by "
              "the lint — the import is gone, delete this row")
        bad = True
    if bad:
        print(f"FAIL: private-import allow-list drifted ({len(reported)} reported, "
              f"{len(ALLOW_LIST)} allow-listed)")
        sys.exit(1)

    for key in sorted(ALLOW_LIST):
        print(f"PASS: {key[0]} -> {key[1]} allow-listed: {ALLOW_LIST[key]}")
    print(f"PASS: {len(reported)} reported private import(s) match "
          f"{len(ALLOW_LIST)} allow-listed row(s) exactly")
    sys.exit(0)


if __name__ == "__main__":
    main()
