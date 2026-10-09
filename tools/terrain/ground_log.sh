#!/bin/bash
# Plays every level (tools/levels.py) fast with the autopilot, in a background window, and
# collects where the ground enemies stand on the ground maps (TYR3D_LOG_GROUND) into
# export/terrain/ground.txt, for make_terrain.py to keep the terrain under them at the ground.
# usage: tools/terrain/ground_log.sh [seconds per level, default 90] [sections, e.g. 1:3 4:8...]
# With sections (as tools/levels.py prints them), only those levels, added to ground.txt.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LIMIT="${1:-90}"
shift 2>/dev/null
ONLY="$*"
OUT="$ROOT/export/terrain"
mkdir -p "$OUT"
LOG="$OUT/ground_run.txt"
: > "$OUT/ground_all.txt"
cd "$ROOT/build/game"
python3 "$ROOT/tools/levels.py" | while read -r section name; do
	if [ -n "$ONLY" ] && ! printf '%s\n' $ONLY | grep -qxF "$section"; then
		continue
	fi
	env SDL_AUDIO_DRIVER=dummy TYR3D_WINDOWED=1 TYR3D_START="$section" TYR3D_AUTOPILOT=1 TYR3D_GODMODE=1 TYR3D_WINDOW_SIZE=320x180 \
		TYR3D_TURBO=32 TYR3D_LOG_GROUND=1 TYR3D_EXIT_AFTER=1000000 ./tyrian3d < /dev/null > "$LOG" 2>&1 &
	pid=$!
	i=0
	# Until the level is over (the next one starts) or the time is up.
	while [ $i -lt "$LIMIT" ] && kill -0 $pid 2>/dev/null && [ "$(grep -c '^level:' "$LOG")" -lt 2 ]; do
		sleep 1
		i=$((i + 1))
	done
	kill $pid 2>/dev/null
	wait $pid 2>/dev/null
	# Only the level's own part of the log.
	awk '/^level:/{n++} n==1 && /^ground:/' "$LOG" >> "$OUT/ground_all.txt"
	echo "$section $name: ${i}s, $(awk '/^level:/{n++} n==1 && /^ground:/' "$LOG" | wc -l | tr -d ' ') positions"
done
# In the order logged (make_terrain.py follows each enemy's slot to tell standing from moving).
if [ -n "$ONLY" ] && [ -f "$OUT/ground.txt" ]; then
	cat "$OUT/ground_all.txt" >> "$OUT/ground.txt"
	rm -f "$OUT/ground_all.txt"
else
	mv "$OUT/ground_all.txt" "$OUT/ground.txt"
fi
rm -f "$LOG"
echo "ground: $(wc -l < "$OUT/ground.txt" | tr -d ' ') positions"
