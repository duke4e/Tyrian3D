#!/bin/sh
# Makes a fresh clone ready to play, as TYRIAN3D.md's "Build (macOS)" does by hand: the renderer's
# submodule, the shader compiler (SDL_shadercross, built once: long the first time), the Tyrian 2000
# data (tools/fetch_data.sh, when data/tyrian2000 has none) and the game, in build/game. With
# --devtools also what the offline tools start from (tools/fetch_devtools.sh) and their Python
# (tools/setup_tools_venv.sh). It downloads (the submodules, the data, with --devtools ~1 GB more).
# usage: tools/bootstrap.sh [--devtools]
set -eu
# (a number of jobs: without one, make starts them all at once, and DXC's LLVM fills the memory)
CPUS="$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
for tool in git cmake curl unzip shasum python3; do
	command -v "$tool" > /dev/null || { echo "$tool is missing (brew install sdl3 assimp cmake)" >&2; exit 1; }
done
if [ "${1:-}" = "--devtools" ]; then
	command -v zstd > /dev/null || { echo "zstd is missing (brew install zstd)" >&2; exit 1; }
fi

# (of the renderer's own submodules only these two: SDL and assimp come from Homebrew)
git submodule update --init external/btbh-renderer
git -C external/btbh-renderer submodule update --init external/raylib
git -C external/btbh-renderer submodule update --init --recursive external/SDL_shadercross
if [ ! -x build/shadercross/shadercross ]; then
	cmake -S external/btbh-renderer/external/SDL_shadercross -B build/shadercross -DCMAKE_BUILD_TYPE=Release \
		-DSDLSHADERCROSS_DXC=ON -DSDLSHADERCROSS_VENDORED=ON -DSDLSHADERCROSS_SHARED=OFF \
		-DSDLSHADERCROSS_STATIC=ON -DSDLSHADERCROSS_SPIRVCROSS_SHARED=OFF -DSDLSHADERCROSS_CLI=ON \
		-DSDLSHADERCROSS_CLI_STATIC=OFF -DSDLSHADERCROSS_INSTALL=OFF -DSDLSHADERCROSS_TESTS=OFF -DSPIRV_SKIP_TESTS=ON
	cmake --build build/shadercross --target shadercross -j "$(( (CPUS + 1) / 2 ))"
fi
# (before the game: episodes 6 and 7 are made from the data at build time)
[ -f data/tyrian2000/tyrian.hdt ] || tools/fetch_data.sh
cmake -S . -B build/game
cmake --build build/game -j "$CPUS"
if [ "${1:-}" = "--devtools" ]; then
	tools/fetch_devtools.sh
	tools/setup_tools_venv.sh
fi
echo "ready: build/game/tyrian3d"
