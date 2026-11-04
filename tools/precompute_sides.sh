#!/bin/bash
# Makes the generated map sides (src/background3d.c) for every level ahead of time, into
# assets/sides, so the game doesn't make them while loading: all of them anew, in place of what is
# there (the sides of maps no level has any more go). Run after changing the generator
# (SIDE_CACHE_VERSION) or the levels' maps. TYR3D_GAME_DIR: the game's folder (default build/game).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NEW="$ROOT/assets/sides.new"
rm -rf "$NEW"
mkdir -p "$NEW"
DIR="$NEW"
command -v cygpath > /dev/null && DIR="$(cygpath -m "$NEW")"  # (the game on Windows takes Windows paths)
"$ROOT/tools/each_level.sh" TYR3D_SIDES_DIR="$DIR" TYR3D_SIDES_WRITE="$DIR" | grep "sides generated"
if [ -n "$(ls "$NEW")" ]; then
	rm -rf "$ROOT/assets/sides"
	mv "$NEW" "$ROOT/assets/sides"
fi
ls "$ROOT/assets/sides" | wc -l | sed 's/^ */files: /'
