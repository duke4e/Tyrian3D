#!/bin/sh
# Downloads the freeware data the game runs on (not in git) from the archive of the old Tyrian fan
# site's downloads page (jkdf2.net/JKBot/JKArchive/JKDF2/JKDF2/Websites/Tyrian/downloads.html), and
# checks each file by SHA-256 before it replaces anything:
#   tyrian2000  Tyrian 2000 (TyrianFull.zip) into data/tyrian2000, against tools/tyrian2000.sha256; the
#               remastered sound effects beside it (data/tyrian2000/sfx) are in the repository and stay;
#   camanis2    Camanis 2 (KFH.zip: Kenneth Frank Henderson Jr.'s level in place of episode 4's, 2005)
#               into data/custom/camanis2;
#   gbc         the Game Boy Color ROM (TyrianGB.zip) into data/gbc/Tyrian.gb, needed only to make
#               episode 7's levels again (tools/gbc; the levels themselves are in the repository).
# usage: tools/fetch_data.sh [tyrian2000] [camanis2] [gbc]   (default: tyrian2000 camanis2;
#        TYR3D_DATA_URL: another copy of the zips)
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URL="${TYR3D_DATA_URL:-https://jkdf2.net/JKBot/JKArchive/JKDF2/JKDF2/Websites/Tyrian}"
WANT="${*:-tyrian2000 camanis2}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

unpack() {  # <zip>: downloads it and unpacks it into $TMP/<zip>.d
	curl -fL --retry 3 "$URL/$1" -o "$TMP/$1"
	mkdir "$TMP/$1.d"
	unzip -q "$TMP/$1" -d "$TMP/$1.d"
}
found() {  # <zip> <name>: the file of that name in the unpacked zip, in any case
	f="$(find "$TMP/$1.d" -type f -iname "$2" | head -n 1)"
	[ -n "$f" ] || { echo "$URL/$1: no $2 in it" >&2; exit 1; }
	echo "$f"
}
check() {  # <sha256> <file>
	echo "$1  $2" | shasum -a 256 -c - > /dev/null || { echo "checksum mismatch: $2" >&2; exit 1; }
}

for part in $WANT; do
	case "$part" in
	tyrian2000)
		unpack TyrianFull.zip
		HDT="$(found TyrianFull.zip tyrian.hdt)"
		# (only the files the game reads, those of tools/tyrian2000.sha256: the zip's copies differ in
		# their DOS programs, icons and readme; the game wants the names in lower case)
		mkdir "$TMP/t2k"
		cut -c 67- "$ROOT/tools/tyrian2000.sha256" | while IFS= read -r name; do
			f="$(find "$(dirname "$HDT")" -maxdepth 1 -type f -iname "$name" | head -n 1)"
			if [ -n "$f" ]; then cp "$f" "$TMP/t2k/$name"; fi
		done
		(cd "$TMP/t2k" && shasum -a 256 -c "$ROOT/tools/tyrian2000.sha256" > /dev/null) || {
			echo "TyrianFull.zip: files differ from tools/tyrian2000.sha256" >&2
			exit 1
		}
		mkdir -p "$ROOT/data/tyrian2000"
		cp "$TMP/t2k/"* "$ROOT/data/tyrian2000/"
		echo "$ROOT/data/tyrian2000"
		;;
	camanis2)
		unpack KFH.zip
		LEVELS="$(found KFH.zip levels4.dat)"
		LVL="$(found KFH.zip tyrian4.lvl)"
		check df76c1323c541da30c5c0a3acb50279dd7ca09a59b43734d75289af0e240fe31 "$LEVELS"
		check 54fda4d0ebdb97d94140aef4d83adfc9f7ff6429f90491ab61283b83d518cb14 "$LVL"
		mkdir -p "$ROOT/data/custom/camanis2"
		cp "$LEVELS" "$ROOT/data/custom/camanis2/levels4.dat"
		cp "$LVL" "$ROOT/data/custom/camanis2/tyrian4.lvl"
		# (the name the episode menu shows: src/episodes.c)
		echo "Camanis 2" > "$ROOT/data/custom/camanis2/name.txt"
		echo "$ROOT/data/custom/camanis2"
		;;
	gbc)
		unpack TyrianGB.zip
		ROM="$(found TyrianGB.zip '*.gb')"
		check 85056bbeae007e00bc42c6654a67637ce6c154750bd004ed8df33e07a4eb4d99 "$ROM"
		mkdir -p "$ROOT/data/gbc"
		cp "$ROM" "$ROOT/data/gbc/Tyrian.gb"
		echo "$ROOT/data/gbc/Tyrian.gb"
		;;
	*)
		echo "unknown part: $part (tyrian2000, camanis2, gbc)" >&2
		exit 1
		;;
	esac
done
