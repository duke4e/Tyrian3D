#!/bin/sh
# Runs the game into demo mode and dumps presented frames for inspection.
# usage: tools/capture_run.sh <out_dir> [dump_every] [exit_after_frames] [extra env...]
set -eu
OUT="$1"; EVERY="${2:-100}"; FRAMES="${3:-1500}"
shift 3 2>/dev/null || shift $#
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$OUT"
cd "$ROOT/build/game"
env TYR3D_DEMO_IDLE_MS="${TYR3D_DEMO_IDLE_MS:-300}" TYR3D_DUMP_DIR="$OUT" TYR3D_DUMP_EVERY="$EVERY" TYR3D_EXIT_AFTER="$FRAMES" "$@" ./tyrian3d > "$OUT/log.txt" 2>&1 &
PID=$!
i=0
while [ $i -lt 120 ] && kill -0 $PID 2>/dev/null; do sleep 1; i=$((i+1)); done
kill $PID 2>/dev/null || true
tail -3 "$OUT/log.txt"
ls "$OUT" | tr '\n' ' '
