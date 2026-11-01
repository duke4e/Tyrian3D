#!/bin/sh
# Downloads what the offline tools start from, from the repository's devtools release (made once on the
# Mac, too slow or paid to make again), and puts each where the tools look for it. None of it is needed
# to build or play the game:
#   models   the ESRGAN models (134 MB), in ~/Library/Caches/Tyrian3D/esrgan: 4x-Fatality by twittman
#            (CC BY-NC-SA 4.0) and 4x-BigFArt-Detail by DinJerr (CC BY-NC 4.0), both from OpenModelDB;
#   terrain  the ground logs (28 MB, 728 MB unpacked), in export/terrain: tools/terrain/ground_log.sh's
#            plays of every level, the input of make_terrain.py, make_cleanground.py, make_vegetation.py;
#   tiles    the HD tiles' saved upscales (91 MB), in upscale/out/tiles and tiles_bigfart: with them
#            tools/tiles_hd.py --add upscales only new maps' tiles;
#   voices   the voices' render cache (358 MB, 425 MB unpacked), in data/voices/cache: with it
#            tools/voices/generate.py renders again only the lines that changed (ElevenLabs credits).
# usage: tools/fetch_devtools.sh [models] [terrain] [tiles] [voices]   (default: all four;
#        TYR3D_DEVTOOLS_URL: another copy of the release's files)
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$HOME/Library/Caches/Tyrian3D"
URL="${TYR3D_DEVTOOLS_URL:-https://github.com/duke4e/Tyrian3D/releases/download/devtools}"
WANT="${*:-models terrain tiles voices}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

get() {  # <file> <sha256>: downloads a release file into $TMP and checks it
	curl -fL --retry 3 "$URL/$1" -o "$TMP/$1"
	echo "$2  $TMP/$1" | shasum -a 256 -c - > /dev/null || { echo "checksum mismatch: $1" >&2; exit 1; }
}

for part in $WANT; do
	case "$part" in
	models)
		mkdir -p "$CACHE/esrgan"
		get 4x-Fatality.pth fde2299d8c98794e5fa36669978e6b69cce6fd7390ec6fe3a30d39da71ce5f30
		get 4x-BigFArt-Detail.pth 0f8007e6a5ee9b08567c1219def8c13fc2b902f1cfc5f4d6fa17103b69c06002
		mv "$TMP/4x-Fatality.pth" "$TMP/4x-BigFArt-Detail.pth" "$CACHE/esrgan/"
		echo "$CACHE/esrgan"
		;;
	terrain)
		get terrain-logs.tar.zst d704500da5cbd07f3f5b431b37b4ee967c07cbf57bb3f4978476eb5dddef63cc
		zstd -dc "$TMP/terrain-logs.tar.zst" | tar -C "$ROOT" -xf -
		echo "$ROOT/export/terrain"
		;;
	tiles)
		get upscale-tiles.tar 9f69a0e61748c4520cb4fc57d339ac609c937fa83f6b763a67ab36e0249adc35
		tar -C "$ROOT" -xf "$TMP/upscale-tiles.tar"
		echo "$ROOT/upscale/out"
		;;
	voices)
		get voices-cache.tar.zst 88d452d064879ff18ef42b4e26afab499c8155ca32fa2270aba194c3d2559a7e
		zstd -dc "$TMP/voices-cache.tar.zst" | tar -C "$ROOT" -xf -
		echo "$ROOT/data/voices/cache"
		;;
	*)
		echo "unknown part: $part (models, terrain, tiles, voices)" >&2
		exit 1
		;;
	esac
done
