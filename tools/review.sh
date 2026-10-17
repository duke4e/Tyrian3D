#!/bin/sh
# Visual review: plays each level briefly (autopilot, no damage) in a background window and keeps
# a few frames per level as PNGs (the BMP dumps are deleted right away: they are big).
# usage: tools/review.sh <out dir> [episode[:section]...] [extra env...]
#   tools/review.sh /tmp/review 1 2      every level of episodes 1 and 2
#   tools/review.sh /tmp/review 4:12     one level
#   REVIEW_SIZE   window size (default 1280x720)
#   REVIEW_EVERY  frames between the kept frames (default 400)
#   REVIEW_FRAMES frames per level (default 1300)
#   REVIEW_WIDTH  width of the kept PNGs (default 1600)
set -u
OUT="$1"; shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SIZE="${REVIEW_SIZE:-1280x720}"
EVERY="${REVIEW_EVERY:-400}"
FRAMES="${REVIEW_FRAMES:-1300}"
WIDTH="${REVIEW_WIDTH:-1600}"
mkdir -p "$OUT"

# Levels: arguments up to the first VAR=value are episodes or episode:section.
LEVELS=""
while [ $# -gt 0 ]; do
	case "$1" in
		*=*) break ;;
		*:*) LEVELS="$LEVELS $1" ;;
		*) LEVELS="$LEVELS $(python3 "$ROOT/tools/levels.py" "$ROOT/data/tyrian2000" "$1" | cut -d' ' -f1 | tr '\n' ' ')" ;;
	esac
	shift
done
[ -z "$LEVELS" ] && LEVELS="$(python3 "$ROOT/tools/levels.py" | cut -d' ' -f1 | tr '\n' ' ')"

for start in $LEVELS; do
	tag="e$(echo "$start" | tr ':' 's')"
	run="$OUT/$tag.run"
	rm -rf "${run:?}"
	"$ROOT/tools/capture_run.sh" "$run" "$EVERY" "$FRAMES" TYR3D_START="$start" TYR3D_AUTOPILOT=1 TYR3D_GODMODE=1 \
		TYR3D_WINDOW_SIZE="$SIZE" "$@" > /dev/null 2>&1
	level=$(grep -m1 '^level:' "$run/log.txt" 2>/dev/null | sed 's/^level: //')
	n=0
	for bmp in "$run"/frame_*.bmp; do
		[ -f "$bmp" ] || continue
		frame=$(basename "$bmp" .bmp | sed 's/frame_0*//')
		sips -s format png -Z "$WIDTH" "$bmp" --out "$OUT/${tag}_f${frame}.png" > /dev/null 2>&1
		rm -f "$bmp"
		n=$((n + 1))
	done
	cp "$run/log.txt" "$OUT/$tag.log" 2>/dev/null
	rm -rf "${run:?}"
	echo "$start ${level:-?}: $n frames"
done
