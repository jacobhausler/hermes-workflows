#!/bin/bash
# In-lane CI-parity: replicates ci.yml gates on ubuntu:24.04 python3.12.
# usage: bash ci/<bead>.sh   (run from lane root by crun; /ci is lane root)
set -u
export DEBIAN_FRONTEND=noninteractive
export PIP_BREAK_SYSTEM_PACKAGES=1
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq -t noble python3.12 python3.12-venv nodejs git curl ca-certificates >/dev/null 2>&1 || \
  apt-get install -y -qq python3 python3-venv nodejs git curl ca-certificates >/dev/null 2>&1
PY=python3.12; command -v python3.12 >/dev/null || PY=python3
$PY -c "import yaml" 2>/dev/null || $PY -m pip install -q pyyaml >/dev/null 2>&1 || true
RC=0
gate() {
  local name=$1; shift
  if "$@" >/tmp/g-$name.log 2>&1; then echo "GATE $name pass"; else echo "FAIL $name"; tail -30 /tmp/g-$name.log; RC=1; fi
}
cd "$(dirname "$0")/.."
gate node-check bash -c 'cp desktop/plugin.js /tmp/plugin.check.mjs && node --check /tmp/plugin.check.mjs'
gate suite $PY scripts/suite.py . /tmp/ci-out
gate scrub $PY scripts/make_public.py /tmp/public-tree
echo "CI-EXIT $RC"
[ "$RC" = 0 ] && echo "CI PASS" || echo "CI FAIL"
exit $RC
