# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities **privately** via GitHub's
[Vulnerability Reporting](https://github.com/jacobhausler/hermes-workflows/security/advisories/new)
(private vulnerability reporting). Do **not** open a public issue for a
security problem — it is routed here instead:
[.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
links security reports to this document and public issues carry no security
section.

Include, as best you can:

- The affected plugin version (`plugin.yaml` `version`) and the commit SHA
  you installed from, if not a tagged release.
- The Hermes version (`hermes --version`) and OS.
- A minimal reproduction (the exact `wf` / graph invocation that triggers it).

## Supported versions

Security fixes are accepted against the **latest release only** — currently
`v1.3.2` (see [`CHANGELOG.md`](CHANGELOG.md) and the tags). Fixes ship in the
next release cut; older tags are not patched retroactively.

## Response time

You will get an initial human response to a private vulnerability report
within **3 business days**. If the report is confirmed, we aim to publish a
patch release and a security advisory within **30 days**, and we will credit
you in the advisory unless you ask us not to.
