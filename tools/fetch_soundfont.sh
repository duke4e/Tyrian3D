#!/bin/sh
# Downloads the SoundFonts the game can play its music through as MIDI (Sound -> SoundFont), into
# data/soundfonts (not in git):
#   GeneralUser GS (S. Christian Collins; free to use, see its license): the default.
#   FluidR3 GM (Frank Wen; MIT), from Debian's fluid-soundfont-gm package.
#   Arachno SoundFont 1.0 (Maxime Abbey; freeware for private, non-commercial use only: the macOS app
#   leaves it out, tools/package_macos.sh), from its author's mirror.
# usage: tools/fetch_soundfont.sh [generaluser] [fluid] [arachno]   (default: all three)
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/data/soundfonts"
mkdir -p "$DIR"
WANT="${*:-generaluser fluid arachno}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

check() {  # <file> <sha256>
	echo "$2  $1" | shasum -a 256 -c - > /dev/null || { echo "checksum mismatch: $1" >&2; exit 1; }
}

for font in $WANT; do
	case "$font" in
	generaluser)
		BASE="https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main"
		curl -fL "$BASE/GeneralUser-GS.sf2" -o "$DIR/GeneralUser-GS.sf2"
		curl -fL "$BASE/documentation/LICENSE.txt" -o "$DIR/GeneralUser-GS-LICENSE.txt"
		echo "$DIR/GeneralUser-GS.sf2"
		;;
	fluid)
		mkdir "$TMP/fluid"
		curl -fL "https://deb.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont-gm_3.1-6_all.deb" -o "$TMP/fluid/gm.deb"
		(cd "$TMP/fluid" && ar x gm.deb && mkdir x && tar -xf data.tar.xz -C x)
		check "$TMP/fluid/x/usr/share/sounds/sf2/FluidR3_GM.sf2" 74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0
		cp "$TMP/fluid/x/usr/share/sounds/sf2/FluidR3_GM.sf2" "$DIR/FluidR3_GM.sf2"
		cp "$TMP/fluid/x/usr/share/doc/fluid-soundfont-gm/copyright" "$DIR/FluidR3_GM-LICENSE.txt"
		echo "$DIR/FluidR3_GM.sf2"
		;;
	arachno)
		mkdir "$TMP/arachno"
		# (The author's mirror serves plain HTTP only; the checksum below vouches for the file.)
		curl -fL "http://maxime.abbey.free.fr/mirror/arachnosoft/files/soundfonts/arachno-soundfont-10-sf2.zip" \
			-o "$TMP/arachno/arachno.zip"
		(cd "$TMP/arachno" && unzip -q arachno.zip "Arachno SoundFont - Version 1.0.sf2" \
			"Documentation/Arachno SoundFont Documentation - Version 1.2 - English.html")
		check "$TMP/arachno/Arachno SoundFont - Version 1.0.sf2" 9a57fb3b6714e69dda12390e351b087e81fc3b1eca15c6b4bbe172799f4cf3cd
		cp "$TMP/arachno/Arachno SoundFont - Version 1.0.sf2" "$DIR/Arachno.sf2"
		cp "$TMP/arachno/Documentation/Arachno SoundFont Documentation - Version 1.2 - English.html" "$DIR/Arachno-Documentation.html"
		echo "$DIR/Arachno.sf2"
		;;
	*)
		echo "unknown SoundFont: $font (generaluser, fluid, arachno)" >&2
		exit 1
		;;
	esac
done
