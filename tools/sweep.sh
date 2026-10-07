#!/bin/sh
# Plays every level briefly (autopilot, no damage) and saves a contact sheet per level.
#
# usage: tools/sweep.sh <out_dir> [episode...]
#   SWEEP_FRAMES  frames to run per level (default 800)
#   SWEEP_EVERY   dump every Nth frame (default 200)
#   SWEEP_SCALE   contact sheet scale (default 0.25)
# Other TYR3D_* variables in the environment apply to every run (e.g. TYR3D_2D=1).
set -eu
OUT="$1"; shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMES="${SWEEP_FRAMES:-800}"
EVERY="${SWEEP_EVERY:-200}"
SCALE="${SWEEP_SCALE:-0.25}"
mkdir -p "$OUT"

"$ROOT/tools/levels.py" "$ROOT/data/tyrian2000" "$@" | while read -r start name; do
	tag="e$(echo "$start" | tr ':' 's')"
	echo "== $start $name"
	"$ROOT/tools/capture_run.sh" "$OUT/$tag" "$EVERY" "$FRAMES" \
		TYR3D_START="$start" TYR3D_AUTOPILOT=1 TYR3D_GODMODE=1 > /dev/null 2>&1 || true
	frames=$(ls "$OUT/$tag"/frame_*.bmp 2>/dev/null | grep -v layer || true)
	if [ -n "$frames" ]; then
		# shellcheck disable=SC2086
		python3 "$ROOT/tools/montage.py" "$OUT/$tag.png" 4 "$SCALE" $frames
		echo "   $OUT/$tag.png"
	else
		echo "   no frames (see $OUT/$tag/log.txt)"
	fi
done
