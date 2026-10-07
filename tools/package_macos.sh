#!/bin/bash
# Builds Tyrian3D.app for macOS: a Release build with the 3D view's resources (shaders, models,
# map sides) and the libraries it needs (SDL3, assimp) inside, ad-hoc signed.
#
# The game's data (Tyrian 2000) is not included. The app finds it in
#   ~/Library/Application Support/Tyrian3D/data   or   a folder named data beside the app
# (or anywhere, with: open Tyrian3D.app --args -t <folder>).
#
# usage: tools/package_macos.sh [out dir]   (default: build/package)
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/build/package}"
BUILD="$ROOT/build/release"

cmake -S "$ROOT" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release > /dev/null
cmake --build "$BUILD" -j 10

APP="$OUT/Tyrian3D.app"
mkdir -p "$OUT"
if [ -d "$APP" ]; then
	rm -r "$APP"
fi
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/shaders" "$APP/Contents/Frameworks"

cp "$BUILD/tyrian3d" "$APP/Contents/MacOS/tyrian3d"
cp "$BUILD"/shaders/*.metallib "$BUILD"/shaders/*.raw "$APP/Contents/Resources/shaders/"
cp -R "$ROOT/assets/models" "$APP/Contents/Resources/models"
cp -R "$ROOT/assets/sides" "$APP/Contents/Resources/sides"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleExecutable</key><string>tyrian3d</string>
	<key>CFBundleIdentifier</key><string>local.tyrian3d</string>
	<key>CFBundleName</key><string>Tyrian3D</string>
	<key>CFBundleDisplayName</key><string>Tyrian3D</string>
	<key>CFBundlePackageType</key><string>APPL</string>
	<key>CFBundleShortVersionString</key><string>0.1</string>
	<key>CFBundleVersion</key><string>1</string>
	<key>LSMinimumSystemVersion</key><string>13.0</string>
	<key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

# The libraries the program links from outside the system go into Frameworks, and the program
# looks for them there.
for lib in $(otool -L "$APP/Contents/MacOS/tyrian3d" | awk '/\/opt\/|\/usr\/local\//{print $1}'); do
	name="$(basename "$lib")"
	cp "$lib" "$APP/Contents/Frameworks/$name"
	chmod u+w "$APP/Contents/Frameworks/$name"
	install_name_tool -id "@executable_path/../Frameworks/$name" "$APP/Contents/Frameworks/$name"
	install_name_tool -change "$lib" "@executable_path/../Frameworks/$name" "$APP/Contents/MacOS/tyrian3d"
done
for lib in "$APP"/Contents/Frameworks/*.dylib; do
	codesign --force --sign - "$lib" > /dev/null
done
codesign --force --sign - "$APP" > /dev/null

echo "$APP"
otool -L "$APP/Contents/MacOS/tyrian3d" | tail -n +2
