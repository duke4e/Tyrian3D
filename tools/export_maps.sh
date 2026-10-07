#!/bin/bash
# Writes every level's background maps as images (in parts of 72 rows) with a JSON index of
# their tiles, into export/maps, for upscaling the tiles in context.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/export/maps"
"$ROOT/tools/each_level.sh" TYR3D_EXPORT_MAPS="$ROOT/export/maps" | grep -c "map written" | sed 's/^/maps: /'
