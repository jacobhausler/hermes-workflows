# Manifest decisions (publish pass, 2026-09-24)

Decisions for plugin.yaml in this lane. Evidence is file:line from INSTALLED upstream
source (/opt/hermes/hermes_cli/plugins_manifest.py, /opt/hermes/hermes_cli/plugin_validate.py)
plus ONE network fetch (pinned-folders.yaml from raw.githubusercontent.com) as a real
capabilities example. Version bump and requires_hermes floor are owned by other lanes —
not touched here.

## (a) requires_env semantics — VERDICT: user-provided env, prompted at install

- `/opt/hermes/hermes_cli/plugins_cmd.py:328-338` — `_missing_env_specs()` treats every
  `requires_env` entry as a variable looked up in the USER's `~/.hermes/.env`
  (`get_env_value(s["name"])`); unset ones are collected as "missing".
- `/opt/hermes/hermes_cli/plugins_cmd.py:385-400` — the install flow
  prompts: "plugin X requires the following environment variables" and saves answers via
  `save_env_value` into the user's `.env`. So requires_env == a secret/config the USER
  must supply, never a plugin-internal runtime variable.
- `/opt/hermes/hermes_cli/plugin_validate.py:159-180` — validation only checks the FORMAT:
  a list of strings/mappings, each UPPER_SNAKE_CASE ("all entries UPPER_SNAKE").
- `/opt/hermes/hermes_cli/plugin_packs.py:97` — "Secrets are prompted (requires_env), never
  carried by the pack" — same consent model, config is the user's to provide.

## (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized

- Catalog side: `/opt/hermes/hermes_cli/plugin_catalog.py:68` (CatalogCapabilities) and
  `:143-167` parse a catalog entry's `capabilities:` block (provides_tools/hooks/
  middleware, requires_env) purely as listing metadata for badges/search — plugin_validate
  never reads the catalog block; no enforcement against code.
- Manifest side: `/opt/hermes/hermes_cli/plugins_manifest.py:479` normalizes
  `capabilities:` via `parse_declared_capabilities`
  (`/opt/hermes/hermes_cli/plugin_capabilities.py:58-80`): ids are checked against the
  fixed `VALID_CAPABILITY_IDS` registry (tools.override, llm.*_override,
  gateway.platform_actions); unknown ids are dropped fail-closed. Declaration is consent
  metadata, NOT a grant (plugins_manifest.py:348-350).
- What IS validated against code: `provides_tools`/`provides_hooks` —
  `/opt/hermes/hermes_cli/plugin_validate.py:373-424` imports the plugin in a probe and
  diffs actual registrations against declared lists (undeclared = FAIL, declared-but-
  unregistered = warn).
- Network example: `raw.githubusercontent.com/NousResearch/hermes-agent/main/plugin-catalog/
  pinned-folders.yaml` returned HTTP 404 on main (one allowed fetch spent); the catalog
  capabilities schema above is taken from the installed `plugin_catalog.py` instead.

## HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: []

The five HERMES_WF_STEER_{FILE,CURSOR,HWM,NODE,SPAWN} vars are baked by the runner INTO
child spawns (`wf.py:331-335` sets them in the run_child env; `__init__.py:752-763` —
act_inbox — reads them from the child's environment). They are plugin-internal IPC set by
our own runner, never typed or stored by the user, so per (a) they must NOT be declared in
requires_env (an install-time prompt for them would be a lie). The plugin needs no
user-provided env: **requires_env: []** (omitted entirely from plugin.yaml — the parser
defaults to `[]` at plugins_manifest.py:475).

## Author

author: "Jacob Hausler" (set in plugin.yaml, last edit after this file's evidence
sections are committed).
