#!/bin/bash
# CI-parity gate: replicates ci.yml gates on the cluster (ubuntu:24.04 = py3.12+node22,
# closest image to ubuntu-latest). One job per lane HEAD; verdict cached.
# usage: ci-parity.sh <lane-dir> <bead>
# exit: 0 green | 1 red | 2 running | 3 submit-failed
set -u
WD="$1"; BEAD="$2"
VDIR=/home/claude/.hermes/profiles/homelab/ue/verdicts
mkdir -p "$VDIR"
SHA=$(git -C "$WD" rev-parse HEAD)
SHORT=${SHA:0:7}
VJ=$VDIR/$BEAD-$SHORT.json
NAME=ue-ci-$BEAD-$SHORT
LOG=/tmp/$NAME.log

if [ -f "$VJ" ]; then
  head -c 300 "$VJ" | tr '\n' ' ' >&2
  python3 -c "import json,sys; sys.exit(0 if json.load(open('$VJ'))['green'] else 1)"
fi

JOB=$WD/ci/$BEAD.sh
if [ ! -f "$JOB" ]; then
  echo "{\"state\":\"no-job-script\",\"path\":\"$JOB\"}" >&2
  exit 1
fi

if ! crun status "$NAME" --verdict >/dev/null 2>&1; then
  ( cd "$WD" && crun run --name "$NAME" --include-untracked --image ubuntu:24.04 --detach \
      --timeout 2400 -- bash "ci/$BEAD.sh" >/dev/null 2>&1 ) || true
  sleep 2
  echo "{\"state\":\"submitted\",\"job\":\"$NAME\"}" >&2
  exit 2
fi

RC=$(crun status "$NAME" --verdict 2>/dev/null || true)
case "$RC" in
  ""|retry|pending|running|queued)
    echo "{\"state\":\"running\",\"job\":\"$NAME\"}" >&2; exit 2 ;;
esac

crun logs "$NAME" > "$LOG" 2>/dev/null || : > "$LOG"
python3 - "$VJ" "$BEAD" "$SHORT" "$NAME" "$RC" <<'PY'
import json, sys
vj, bead, short, name, rc = sys.argv[1:6]
try:
    log = open("/tmp/%s.log" % name, errors="replace").read()
except Exception:
    log = ""
fails = [l.split()[1] for l in log.splitlines() if l.startswith("FAIL ")]
json.dump({"bead": bead, "sha": short, "job": name, "rc": rc,
           "green": rc == "0" and "CI PASS" in log, "fails": fails,
           "log_tail": log[-2500:]}, open(vj, "w"))
PY
head -c 300 "$VJ" | tr '\n' ' ' >&2
python3 -c "import json,sys; sys.exit(0 if json.load(open('$VJ')).get('green') else 1)"
