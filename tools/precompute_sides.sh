#!/bin/bash
# Makes the generated map sides (src/background3d.c) for every level ahead of time, into
# assets/sides, so the game doesn't make them while loading. Levels whose sides are already
# there are quick. Run after changing the generator (SIDE_CACHE_VERSION).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/assets/sides"
"$ROOT/tools/each_level.sh" TYR3D_SIDES_WRITE="$ROOT/assets/sides" | grep "sides generated"
ls "$ROOT/assets/sides" | wc -l | sed 's/^ */files: /'
