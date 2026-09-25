# Manual installation — Hermes Workflows 0.9.0

The catalog path (`hermes plugins install hermes-workflows`) is the recommended install; see [README.md](README.md). This file covers installing from a release zip, or by hand from a checkout. Backend and desktop app may be on different machines.

## Verify and unpack on each machine that needs a component

Place the ZIP and `.zip.sha256` sidecar together. Use `python3` (or an explicit Python 3 interpreter path) and `unzip`; on macOS `shasum -a 256` substitutes for `sha256sum`:

    cd "$HOME"
    if command -v sha256sum >/dev/null; then sha256sum -c hermes-workflows-0.9.0.zip.sha256; else shasum -a 256 -c hermes-workflows-0.9.0.zip.sha256; fi
    PACKAGE_STAGE="$(mktemp -d "$HOME/hermes-workflows.XXXXXX")"
    unzip -q "$HOME/hermes-workflows-0.9.0.zip" -d "$PACKAGE_STAGE"
    PACKAGE_DIR="$PACKAGE_STAGE/hermes-workflows-0.9.0"
    (cd "$PACKAGE_DIR" && if command -v sha256sum >/dev/null; then sha256sum -c SHA256SUMS; else shasum -a 256 -c SHA256SUMS; fi)

Use `unzip` rather than Python `ZipFile.extractall` when running the tests: the archive stores executable modes, but Python extraction may discard them. Check `tests/fake` is executable. Keep the staging tree until verification completes.

## Backend host

Set `HERMES_HOME` to the active backend profile home; the default is `$HOME/.hermes`. If an older plugin directory already exists, stop and back it up rather than overlay it. Do not copy state or workflow runs into the package.

    HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
    test ! -e "$HERMES_HOME/plugins/hermes-workflows"
    mkdir -p "$HERMES_HOME/plugins"
    cp -R "$PACKAGE_DIR" "$HERMES_HOME/plugins/hermes-workflows"
    hermes plugins validate "$HERMES_HOME/plugins/hermes-workflows"
    hermes plugins enable hermes-workflows

The bundled skill is registered by the plugin as `hermes-workflows:workflow`. For direct CLI discovery outside plugin registration, install a separate copy of the bundled authoring skill in the active profile (do not overwrite an existing skill):

    test ! -e "$HERMES_HOME/skills/workflow"
    mkdir -p "$HERMES_HOME/skills/workflow"
    cp "$PACKAGE_DIR/SKILL.md" "$HERMES_HOME/skills/workflow/SKILL.md"
    cp -R "$PACKAGE_DIR/references" "$HERMES_HOME/skills/workflow/references"

Enablement and copied source are not proof the running gateway loaded them. Restart the backend after applying the verified plugin, then verify plugin admission, mounted API and tool registration in the new process. Dashboard registration is API-only with a hidden tab.

## Desktop app machine

Verify/unpack the same archive locally as above. Use that machine's `HERMES_HOME`, not the backend machine's. The app-level plugin is a separate file:

    HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
    mkdir -p "$HERMES_HOME/desktop-plugins/hermes-workflows"
    cp "$PACKAGE_DIR/desktop/plugin.js" "$HERMES_HOME/desktop-plugins/hermes-workflows/plugin.js"

The desktop plugin watcher loads the changed file. Enable/check it in Settings → Plugins or Capabilities → Plugins; use Reload desktop plugins if needed. Verify the app file checksum matches the archive and the backend API is mounted.

## Source-tree verification

Use the active host's Python 3 and Node.js, not a hard-coded installation path. Run in a disposable extracted checkout with an isolated `HERMES_HOME`; test scripts need an executable `tests/fake`. The suite is serial and should be bounded by an operator-supplied per-test timeout. `tests/test_papercuts_0922b.py` produces the `home6` fixture consumed by `test_fanout_ui.mjs`.

    cd "$PACKAGE_DIR"
    test -x tests/fake
    for test in tests/test_*.py; do python3 "$test" || exit $?; done
    node --check desktop/plugin.js
    for test in tests/test_*.mjs; do node --experimental-strip-types "$test" || exit $?; done

## Removal

Disable the plugin, remove only its source directory and app-level plugin file, then restart the backend and reload desktop plugins. Remove the optional copied skill only if it is the copy you installed. Workflow runs, the library, state.db, logs, existing profile data and archives are preserved, not uninstalled.

    hermes plugins disable hermes-workflows
    printf '%s\n' "$HERMES_HOME/plugins/hermes-workflows" "$HERMES_HOME/desktop-plugins/hermes-workflows" "$HERMES_HOME/skills/workflow"

After checking these paths, remove selected source directories manually. This candidate does not execute deletion, restart, publication or installation.
