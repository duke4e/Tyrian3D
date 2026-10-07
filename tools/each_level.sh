#!/bin/bash
# Starts every level (tools/levels.py) in a background window for a moment, with the given
# environment variables, and prints what the game reports about its background maps.
# usage: tools/each_level.sh [VAR=value...]
# e.g.   tools/each_level.sh TYR3D_EXPORT_MAPS=$PWD/export/maps
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/build/game"
python3 "$ROOT/tools/levels.py" | while read -r section name; do
	env TYR3D_WINDOWED=1 TYR3D_START="$section" TYR3D_EXIT_AFTER=80 "$@" ./tyrian3d < /dev/null 2>&1 |
		grep "^background" | sed "s/^/$section $name: /"
done
