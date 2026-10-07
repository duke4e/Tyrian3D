#!/bin/bash
# Makes the generated map sides (src/background3d.c) for every level ahead of time, into
# assets/sides, so the game doesn't make them while loading. Levels whose sides are already
# there are quick. Run after changing the generator (SIDE_CACHE_VERSION).
# usage: tools/precompute_sides.sh [episode...]
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/assets/sides"
cd "$ROOT/build/game"
python3 "$ROOT/tools/levels.py" "$@" | while read -r section name; do
	TYR3D_WINDOWED=1 TYR3D_START="$section" TYR3D_EXIT_AFTER=80 TYR3D_SIDES_WRITE="$ROOT/assets/sides" \
		./tyrian3d < /dev/null 2>&1 | grep "sides generated" | sed "s/^/$section $name: /"
done
ls "$ROOT/assets/sides" | wc -l | sed 's/^ */files: /'
