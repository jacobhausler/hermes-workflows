#!/bin/bash
# Batch CI-parity driver: one crun job per lane at its current HEAD, report per lane.
# usage: fanout-ci.sh <bead...>
set -u
REPO=/home/claude/Developer/hermes-workflows
TPL=$REPO/ue/ci-template.sh
OUT=$REPO/ue/logs; mkdir -p "$OUT"
for B in "$@"; do
  WD=/home/claude/Developer/wt/ue-hw-$B
  [ -d "$WD" ] || { echo "$b no-lane"; continue; }
  HEAD=$(git -C "$WD" rev-parse --short HEAD)
  mkdir -p "$WD/ci"; cp "$TPL" "$WD/ci/$B.sh"
  NAME=ue-ci-$B-$HEAD
  crun status "$NAME" --verdict >/dev/null 2>&1 && { echo "$B $NAME exists"; continue; }
  ( cd "$WD" && crun run --name "$NAME" --include-untracked --image ubuntu:24.04 --detach \
      --timeout 2400 -- bash "ci/$B.sh" >/dev/null 2>&1 ) && echo "$B submitted $NAME" || echo "$B submit-FAILED"
done
