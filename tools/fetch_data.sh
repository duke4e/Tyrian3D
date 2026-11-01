#!/bin/sh
# Downloads the freeware Tyrian 2000 data the game runs on into data/tyrian2000 (not in git), from
# camanis.net, and checks each file against tools/tyrian2000.sha256. The remastered sound effects
# beside it (data/tyrian2000/sfx) are in the repository and are left as they are.
# Not downloaded: the GBC ROM (data/gbc/Tyrian.gb), needed only to make episode 7's levels again
# (tools/gbc; the levels themselves are in the repository), and Camanis 2 (data/custom/camanis2):
# copy them there by hand.
# usage: tools/fetch_data.sh   (TYR3D_DATA_URL: another copy of the zip)
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/data/tyrian2000"
URL="${TYR3D_DATA_URL:-https://www.camanis.net/tyrian/tyrian2000.zip}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -fL "$URL" -o "$TMP/tyrian2000.zip"
mkdir "$TMP/x"
unzip -q "$TMP/tyrian2000.zip" -d "$TMP/x"
# (the files are in a folder of the zip; the game wants their names in lower case)
HDT="$(find "$TMP/x" -type f -iname tyrian.hdt | head -n 1)"
[ -n "$HDT" ] || { echo "$URL: no tyrian.hdt in it" >&2; exit 1; }
mkdir -p "$DIR"
find "$(dirname "$HDT")" -maxdepth 1 -type f | while IFS= read -r f; do
	cp "$f" "$DIR/$(basename "$f" | tr '[:upper:]' '[:lower:]')"
done
(cd "$DIR" && shasum -a 256 -c "$ROOT/tools/tyrian2000.sha256" > /dev/null) || {
	echo "$DIR: files differ from tools/tyrian2000.sha256" >&2
	exit 1
}
echo "$DIR"
