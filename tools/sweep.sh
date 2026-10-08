#!/bin/sh
# Plays every section of the episodes with the autopilot, one run after another in a small
# window, and reports per run the level, whether it ran to the end and its warnings (plan M9).
# usage: tools/sweep.sh <out dir> [episodes, e.g. "1 2 3 4 5"] [sections, e.g. "1 2 ... 40"] [extra env...]
# Each run's log is <out dir>/<episode>_<section>.log; the summary is <out dir>/summary.txt.
set -u
OUT="$1"; EPISODES="${2:-1 2 3 4 5}"; SECTIONS="${3:-$(seq 1 40)}"
shift 3 2>/dev/null || shift $#
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$OUT"
: > "$OUT/summary.txt"
for e in $EPISODES; do
	for s in $SECTIONS; do
		run="$OUT/run"
		rm -rf "$run"
		"$ROOT/tools/capture_run.sh" "$run" 100000 "${SWEEP_FRAMES:-700}" TYR3D_START="$e:$s" TYR3D_AUTOPILOT=1 \
			TYR3D_GODMODE=1 TYR3D_WINDOW_SIZE=480x270 "$@" > /dev/null 2>&1
		cp "$run/log.txt" "$OUT/${e}_${s}.log"
		level=$(grep -m1 '^level:' "$run/log.txt" | sed 's/^level: //')
		if grep -q 'exiting after' "$run/log.txt"; then status=ok; else status=FAILED; fi
		warnings=$(grep -ci 'warning\|error' "$run/log.txt")
		echo "$e:$s $status warnings=$warnings level=${level:-none}" | tee -a "$OUT/summary.txt"
		rm -rf "$run"
	done
done
