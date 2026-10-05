# Manual installation — Hermes Workflows 1.3.0

The catalog path (`hermes plugins install hermes-workflows`) is the recommended install; see [README.md](README.md). This file covers installing from a release zip, or by hand from a checkout. Backend and desktop app may be on different machines.

## Verify and unpack on each machine that needs a component

Place the ZIP and `.zip.sha256` sidecar together. Use `python3` (or an explicit Python 3 interpreter path) and `unzip`; on macOS `shasum -a 256` substitutes for `sha256sum`:

    cd "$HOME"
    if command -v sha256sum >/dev/null; then sha256sum -c hermes-workflows-1.3.0.zip.sha256; else shasum -a 256 -c hermes-workflows-1.3.0.zip.sha256; fi
    PACKAGE_STAGE="$(mktemp -d "$HOME/hermes-workflows.XXXXXX")"
    unzip -q "$HOME/hermes-workflows-1.3.0.zip" -d "$PACKAGE_STAGE"
    PACKAGE_DIR="$PACKAGE_STAGE/hermes-workflows-1.3.0"
    (cd "$PACKAGE_DIR" && if command -v sha256sum >/dev/null; then sha256sum -c SHA256SUMS; else shasum -a 256 -c SHA256SUMS; fi)

Use `unzip` rather than Python `ZipFile.extractall` when running the tests: the archive stores executable modes, but Python extraction may discard them. In particular, `tests/fake` — the fake Hermes launcher the hermetic tests use in place of a real install — must stay executable. Keep the staging tree until verification completes.

Hermes Agent v2026.9.21 or newer (package version >=0.21.4) is required for the measured stock quiet one-shot and turn-report contract. Older core versions may skip plugin admission.

## Backend host

Set `HERMES_HOME` to the active backend profile home; the default is `$HOME/.hermes`. If an older plugin directory already exists, stop and back it up rather than overlay it. Do not copy state or workflow runs into the package.

    HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
    test ! -e "$HERMES_HOME/plugins/hermes-workflows"
    mkdir -p "$HERMES_HOME/plugins"
    cp -R "$PACKAGE_DIR" "$HERMES_HOME/plugins/hermes-workflows"
    hermes plugins validate "$HERMES_HOME/plugins/hermes-workflows"
    hermes plugins enable hermes-workflows

The bundled skill is registered by the plugin as `hermes-workflows:workflow`; that registration is the skill's single source of truth. For direct CLI discovery outside plugin registration, link the INSTALLED plugin directory's skill into the active profile so it tracks every plugin update — do NOT maintain a copied fork (a copy silently freezes at the plugin version it was taken from and trains stale grammar), and do not link the temporary `$PACKAGE_DIR` staging tree (it vanishes when unpacked, leaving a dangling link):

    test ! -e "$HERMES_HOME/skills/workflow"
    mkdir -p "$HERMES_HOME/skills"
    ln -s "$HERMES_HOME/plugins/hermes-workflows" "$HERMES_HOME/skills/workflow"

If a symlink is impossible on the host, copy instead — but then re-copy after every plugin update, and treat drift as a bug. If a copied or hand-edited skill already exists where the link would go, stop and reconcile it with the package before linking; never silently discard local edits, upstream them (issue on the plugin repo) so the package can carry them.

Enablement and copied source are not proof the running gateway loaded them. Restart the backend after applying the verified plugin, then verify plugin admission, mounted API and tool registration in the new process. Dashboard registration is API-only with a hidden tab.

## Desktop app machine

Verify/unpack the same archive locally as above. Use that machine's `HERMES_HOME`, not the backend machine's. The app-level plugin is a separate file:

    HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
    mkdir -p "$HERMES_HOME/desktop-plugins/hermes-workflows"
    cp "$PACKAGE_DIR/desktop/plugin.js" "$HERMES_HOME/desktop-plugins/hermes-workflows/plugin.js"

The desktop plugin watcher loads the changed file. Enable/check it in Settings → Plugins or Capabilities → Plugins; use Reload desktop plugins if needed. Verify the app file checksum matches the archive and the backend API is mounted.

## Source-tree verification

Use the active host's Python 3 and Node.js, not a hard-coded installation path. Run in a disposable extracted checkout; the suite harness sandboxes `HERMES_HOME` itself, and the hermetic tests drive the bundled fake Hermes launcher (`tests/fake`, executable) instead of a real Hermes install.

The one canonical suite entry is the same command CI runs: it executes every Python and Node test serially, bounds each test with its own timeout, sandboxes `HERMES_HOME`, and writes a pass/fail ledger plus per-test logs into the output directory:

    cd "$PACKAGE_DIR"
    test -x tests/fake
    node --check desktop/plugin.js
    python3 scripts/suite.py . ci-out

`node --check desktop/plugin.js` is the quick syntax gate for the desktop half; `python3 scripts/suite.py . ci-out` is the full verification. Check `ci-out/exits.json` for the result: any non-zero exit row means a failing test, and its log file sits beside it.

## Removal

Before disabling, call `workflow {"action":"list"}` and stop every live run with `workflow {"action":"stop","run_id":"<id>"}`. Detached runners can survive session end, gateway restart and plugin disable; disable is not a stop command. Then disable the plugin, remove only its source directory and app-level plugin file, then restart the backend and reload desktop plugins. Remove the optional skill link (or copied skill, if this host could not symlink) only if you installed it. Workflow runs, the library, state.db, logs, existing profile data and archives are preserved, not uninstalled.

    hermes plugins disable hermes-workflows
    printf '%s\n' "$HERMES_HOME/plugins/hermes-workflows" "$HERMES_HOME/desktop-plugins/hermes-workflows" "$HERMES_HOME/skills/workflow"

After checking these paths, remove selected source directories manually. This candidate does not execute deletion, restart, publication or installation.
