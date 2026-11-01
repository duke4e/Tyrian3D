#!/bin/sh
# Sets up what the offline tools need, outside the repository (it can be deleted and made again):
# - a Python with numpy, scipy, Pillow and torch in ~/Library/Caches/Tyrian3D/tools-venv (tools/terrain,
#   tools/hd_sheets.py, tools/upscale_sprites.py, tools/tiles_hd.py, tools/sprite_reference.py ...);
# - the ESRGAN model the HD tiles, sprites and HUD panels are upscaled with, 4x-Fatality by twittman
#   (OpenModelDB, CC BY-NC-SA 4.0), in ~/Library/Caches/Tyrian3D/esrgan. The other, 4x-BigFArt-Detail,
#   is not in OpenModelDB's storage: tools/fetch_devtools.sh models brings both from the devtools release.
# It downloads from PyPI (~110 MB) and OpenModelDB's storage (67 MB): ask the user before running it.
# usage: tools/setup_tools_venv.sh   (PYTHON=<python 3.10+> to pick the interpreter)
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$HOME/Library/Caches/Tyrian3D"
VENV="$CACHE/tools-venv"
PY="${PYTHON:-python3.10}"

if [ ! -x "$VENV/bin/python" ]; then
	"$PY" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --upgrade pip > /dev/null
"$VENV/bin/python" -m pip install numpy scipy pillow torch
# pip's scipy (and other wheels with thread-local storage) don't load on recent macOS: dyld refuses a
# zero-fill __thread_bss section with a file offset. Patch the wheels' Mach-O files in place.
SITE="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
"$VENV/bin/python" "$ROOT/tools/fix_macho_tls.py" "$SITE"
"$VENV/bin/python" -c 'import numpy, scipy.ndimage, PIL, torch; print("tools venv ok: torch", torch.__version__, "mps", torch.backends.mps.is_available())'

MODEL="$CACHE/esrgan/4x-Fatality.pth"
SHA=fde2299d8c98794e5fa36669978e6b69cce6fd7390ec6fe3a30d39da71ce5f30
mkdir -p "$CACHE/esrgan"
if [ ! -f "$MODEL" ] || [ "$(shasum -a 256 "$MODEL" | cut -d' ' -f1)" != "$SHA" ]; then
	curl -fL --retry 3 -o "$MODEL.part" \
		https://objectstorage.us-phoenix-1.oraclecloud.com/n/ax6ygfvpvzka/b/open-modeldb-files/o/4x-Fatality.pth
	[ "$(shasum -a 256 "$MODEL.part" | cut -d' ' -f1)" = "$SHA" ] || { echo "4x-Fatality.pth: wrong checksum" >&2; exit 1; }
	mv "$MODEL.part" "$MODEL"
fi
echo "model ok: $MODEL"
