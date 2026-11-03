#!/usr/bin/env python3
"""The 3D view's assets for episode 6's maps, made as the originals' are: the game exports each
level's maps (TYR3D_EXPORT_MAPS) and writes their side columns (TYR3D_SIDES_WRITE), the ground
enemies' places are collected (tools/terrain/ground_log.sh), the levels' terrain settings (their
"terrain" in levels/*.json) go into tools/terrain/levels.json under the maps' hashes, then the
clean ground (make_cleanground.py), terrain (make_terrain.py) and vegetation (make_vegetation.py)
are built. Maps of earlier versions of the levels (episode 6's entries no level uses any more) are
taken out, with their assets.

usage: <python with numpy, scipy and PIL> tools/content/episode6/terrain.py [level...]
       (the game built; levels by name, default all)
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME = os.path.join(ROOT, "build", "game")
SETTINGS = os.path.join(ROOT, "tools", "terrain", "levels.json")
sys.path.insert(0, HERE)
import build  # noqa: E402


def sections():
    """The levels' sections in episode 6's script: name -> 6:<section>."""
    out = {}
    lines = subprocess.check_output([sys.executable, os.path.join(ROOT, "tools", "levels.py")], text=True)
    for line in lines.splitlines():
        section, name = line.split(" ", 1)
        if section.startswith("6:"):
            out[name.strip()] = section
    return out


def export_maps(section):
    """The level's exported maps: background number -> map hash (side columns written too)."""
    env = dict(os.environ, SDL_AUDIO_DRIVER="dummy", TYR3D_WINDOWED="1", TYR3D_START=section, TYR3D_EXIT_AFTER="80",
               TYR3D_EXPORT_MAPS=os.path.join(ROOT, "export", "maps"),
               TYR3D_SIDES_WRITE=os.path.join(ROOT, "assets", "sides"))
    out = subprocess.run(["./tyrian3d"], cwd=GAME, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    return {int(b): h for b, h in re.findall(r"background (\d): map (?:written|already exported) to .*map_([0-9a-f]{16})\.json", out)}


def main(names):
    found = sections()
    levels = {}
    for stage in build.stages():
        level = json.load(open(os.path.join(build.LEVELS_DIR, f"{stage['level']}.json")))
        levels[level["name"]] = level
    names = names or list(levels)
    settings = json.load(open(SETTINGS))
    episode6 = {n for n in levels}
    keep = set()
    built = []
    for name in levels:
        if levels[name].get("shared_maps") or levels[name].get("sideways"):
            continue  # another level's maps (and terrain): INVADERS; open space, seen from the side
        maps = export_maps(found[name]) if name in names else {}
        if name not in names:
            # Not made again: its maps stay as they are.
            keep.update(h for h, s in settings.items() if s.get("level") == name)
            continue
        terrain = dict(levels[name].get("terrain") or {"classes": 6, "heights": {}})
        solid = terrain.pop("solid_upper", False)
        for background, h in maps.items():
            # A map an original level has too (an empty layer: the same hash) is the original's.
            exported = json.load(open(os.path.join(ROOT, "export", "maps", f"map_{h}.json")))
            if exported.get("level", "").strip() not in levels:
                continue
            if background == 1:
                settings[h] = dict(terrain, level=name)
            elif solid is True or background in (solid or ()):
                # Upper layers as solids (walls of ice, crust), as their originals have them (solid_upper
                # True, or the backgrounds that are: DEEP ICE's floating crystals on layer 3 are tiles).
                settings[h] = {"level": name, "background": background, "solid": True}
            else:
                continue
            keep.add(h)
            built.append(h)
        print(f"{name}: maps {maps}")
    # Earlier versions' maps out (their settings and assets).
    for h in [h for h, s in settings.items() if s.get("level") in episode6 and h not in keep]:
        del settings[h]
        for ext in ("ter", "veg", "era", "std"):
            path = os.path.join(ROOT, "assets", "terrain", f"{h}.{ext}")
            if os.path.exists(path):
                os.remove(path)
    json.dump(settings, open(SETTINGS, "w"), indent=1)
    if not built:
        return 0
    sections_ = " ".join(found[n] for n in names)
    subprocess.run([os.path.join(ROOT, "tools", "terrain", "ground_log.sh"), "60"] + sections_.split(), check=True,
                   stdout=subprocess.DEVNULL)
    ground = [h for h in built if settings[h].get("background", 1) == 1]
    if ground:  # (the clean ground first: the terrain and the vegetation are made on it)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_cleanground.py")] + ground, check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_terrain.py"), "build"] + built, check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_vegetation.py")] + ground, check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
