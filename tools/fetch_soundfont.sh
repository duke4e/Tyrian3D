#!/bin/sh
# Downloads the GeneralUser GS SoundFont (S. Christian Collins; free to use, see its license) the
# game plays its music through as MIDI, into data/soundfonts (not in git).
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/data/soundfonts"
mkdir -p "$DIR"
BASE="https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main"
curl -fL "$BASE/GeneralUser-GS.sf2" -o "$DIR/GeneralUser-GS.sf2"
curl -fL "$BASE/documentation/LICENSE.txt" -o "$DIR/GeneralUser-GS-LICENSE.txt"
echo "$DIR/GeneralUser-GS.sf2"
