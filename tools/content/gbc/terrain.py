#!/usr/bin/env python3
"""The 3D view's assets for episode 7's maps (the GBC levels), made as episode 6's are
(tools/content/episode6/terrain.py): the game exports each level's maps (TYR3D_EXPORT_MAPS) and writes
their side columns (TYR3D_SIDES_WRITE); the export is marked episode 7 (several GBC levels have an
original's name, and their maps mustn't teach the tilesets as the originals' do: make_cleanground.py);
each ground map gets its original's terrain settings, its surfaces' heights carried over by colour (the
original map's classes, each one's mean colour with its height, as make_terrain.py's "materials"), and
backgrounds 2 and 3 (made from an original's: tools/gbc/episode.py upper_layers) that original's (solids
where its are); then
the ground enemies' places are logged (tools/terrain/ground_log.sh) and the clean ground, terrain and
vegetation are built. Maps of earlier versions of these levels are taken out, with their assets.

usage: <python with numpy, scipy and PIL> tools/content/gbc/terrain.py [level...]
       (the game built with episode 7; levels by name, default all; TYR3D_GAME_DIR: the game's folder to run, default
       build/game)
       ... terrain.py --refresh   (the settings carried over again, terrain and vegetation rebuilt)
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME = os.environ.get("TYR3D_GAME_DIR") or os.path.join(ROOT, "build", "game")  # (the game's folder to run)
EXE = os.path.join(GAME, "tyrian3d.exe" if os.name == "nt" else "tyrian3d")
SETTINGS = os.path.join(ROOT, "tools", "terrain", "levels.json")
MAPS = os.path.join(ROOT, "export", "maps")
EPISODE = os.path.join(ROOT, "data", "gbc", "episode7", "episode.json")
sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
TAG = "gbc"  # settings entries of episode 7's maps carry "episode": 7


def sections():
    """The levels' sections in episode 7's script: name -> 7:<section>."""
    out = {}
    lines = subprocess.check_output([sys.executable, os.path.join(ROOT, "tools", "levels.py")], text=True)
    for line in lines.splitlines():
        section, name = line.split(" ", 1)
        if section.startswith("7:"):
            out[name.strip()] = section
    return out


def wait_for_game():
    """One game at a time: wait while another session's test run is going."""
    import time
    if os.name == "nt":
        # (another copy of this folder's game: tasklist names only the image, so the folder isn't told apart)
        running = lambda: os.path.basename(EXE).lower() in subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq tyrian3d.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout.lower()
        if GAME != os.path.join(ROOT, "build", "game"):
            return  # (a dev build's folder: the player's game in build/game doesn't hold it up)
    else:
        running = lambda: subprocess.run(["pgrep", "-x", "tyrian3d"], capture_output=True).returncode == 0
    while running():
        time.sleep(5)


def export_maps(section):
    """The level's exported maps: background number -> map hash (side columns written too); each
    export marked episode 7."""
    env = dict(os.environ, SDL_AUDIO_DRIVER="dummy", TYR3D_WINDOWED="1", TYR3D_START=section, TYR3D_EXIT_AFTER="80",
               TYR3D_EXPORT_MAPS=MAPS, TYR3D_SIDES_WRITE=os.path.join(ROOT, "assets", "sides"))
    wait_for_game()
    out = subprocess.run([EXE], cwd=GAME, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    maps = {int(b): h for b, h in re.findall(r"background (\d): map (?:written|already exported) to .*map_([0-9a-f]{16})\.json", out)}
    for h in maps.values():
        path = os.path.join(MAPS, f"map_{h}.json")
        info = json.load(open(path))
        if info.get("episode") != 7:
            info["episode"] = 7
            json.dump(info, open(path, "w"))
    return maps


def original_map(settings, name):
    """The original level's ground map (its hash) in the terrain settings."""
    for h, s in settings.items():
        if s.get("level", "").strip() == name and "background" not in s and s.get("episode") != 7:
            return h
    return None


def original_upper(settings, name, background):
    """The original level's settings for its background 2 or 3 (solids), None where it has none."""
    for s in settings.values():
        if s.get("level", "").strip() == name and s.get("background") == background and s.get("episode") != 7:
            return {k: v for k, v in s.items() if k != "level"}
    return None


def carried_settings(settings, original, fallback):
    """The original's settings for a GBC map: its own keys but the ones tied to its map (tiles by shape,
    a ceiling over its background 2), its surfaces' heights as colours ("materials")."""
    import numpy as np
    import make_terrain as mt
    h = original or fallback
    s = dict(settings[h])
    out = {k: v for k, v in s.items() if k not in ("heights", "tiles", "ceiling", "level", "materials")}
    out["heights"] = {}
    if s.get("heights"):
        info, rgb, opaque = mt.load_map(h)
        _, labels, _ = mt.classify(rgb, s["classes"], centroids=mt.frozen(h, s["classes"]))
        materials = {}
        for c in range(s["classes"]):
            height = s["heights"].get(str(c), 0)  # (the classes it doesn't list are ground, at 0)
            mask = labels == c
            if mask.any():
                mean = rgb[mask].mean(0)
                materials["#" + "".join(f"{int(round(v * 255)):02x}" for v in mean)] = height
        out["materials"] = materials
    return out


def refresh():
    """The settings carried over again from the originals, the terrain and vegetation built again (the maps,
    their export, ground log and clean ground as they are)."""
    episode = json.load(open(EPISODE))
    settings = json.load(open(SETTINGS))
    stages = {st["name"]: st for st in episode["stages"]}
    built = []
    for h, s in list(settings.items()):
        if s.get("episode") != 7:
            continue
        name = s["level"][:-len(f" ({TAG})")]
        if s.get("background"):
            upper = original_upper(settings, stages[name].get("layers", stages[name]["pc"])[1], s["background"])
            settings[h] = dict(upper or s, level=s["level"], episode=7)
            built.append(h)
            continue
        pc = stages[name].get("tiles", stages[name]["pc"])[1]
        fallback = original_map(settings, "DELIANI" if "Deli" in pc else "SQUADRON")
        settings[h] = dict(carried_settings(settings, original_map(settings, pc), fallback), level=s["level"], episode=7)
        built.append(h)
    json.dump(settings, open(SETTINGS, "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_terrain.py"), "build"] + built, check=True)
    ground = [h for h in built if not settings[h].get("background")]
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_vegetation.py")] + ground, check=True)
    return 0


def main(names):
    if names == ["--refresh"]:
        return refresh()
    episode = json.load(open(EPISODE))
    found = sections()
    settings = json.load(open(SETTINGS))
    stages = {st["name"]: st for st in episode["stages"]}
    names = names or list(stages)
    keep, built = set(), []
    for name, st in stages.items():
        if name not in names:
            keep.update(h for h, s in settings.items() if s.get("episode") == 7 and s.get("level") == f"{name} ({TAG})")
            continue
        maps = export_maps(found[name])
        ground = maps.get(1)
        print(f"{name}: maps {maps}")
        for background, h in maps.items():
            # (an upper layer as its original has it: solids where it has them; the original's own map, the same hash,
            # stays the original's)
            upper = background != 1 and original_upper(settings, st.get("layers", st["pc"])[1], background)
            if upper and not (h in settings and settings[h].get("episode") != 7):
                settings[h] = dict(upper, level=f"{name} ({TAG})", episode=7)
                keep.add(h)
                built.append(h)
        if ground is None or (ground in settings and settings[ground].get("episode") != 7):
            continue  # (a map an original has too, e.g. open space of one tile: the original's)
        # (the original whose tiles the map has: the stage's "tiles" where its map took another original's tile set,
        # DELICORE BRAINIAC's; its colours are those the heights go by)
        pc = st.get("tiles", st["pc"])[1]
        original = original_map(settings, pc)
        fallback = original_map(settings, "DELIANI" if "Deli" in pc else "SQUADRON")
        s = carried_settings(settings, original, fallback)
        settings[ground] = dict(s, level=f"{name} ({TAG})", episode=7)
        keep.add(ground)
        built.append(ground)
    # earlier versions' maps out (their settings and assets)
    for h in [h for h, s in settings.items() if s.get("episode") == 7 and h not in keep]:
        del settings[h]
        for ext in ("ter", "veg", "era", "std"):
            path = os.path.join(ROOT, "assets", "terrain", f"{h}.{ext}")
            if os.path.exists(path):
                os.remove(path)
    json.dump(settings, open(SETTINGS, "w"), indent=1)
    if not built:
        return 0
    secs = [found[n] for n in names if n in found]
    wait_for_game()
    # (bash by the PATH: on Windows CreateProcess finds System32's, WSL's, before Git's)
    subprocess.run([shutil.which("bash") or "bash", os.path.join(ROOT, "tools", "terrain", "ground_log.sh"), "60"] + secs, check=True,
                   stdout=subprocess.DEVNULL, env=dict(os.environ, TYR3D_GAME_DIR=GAME))
    ground = [h for h in built if not settings[h].get("background")]
    if ground:  # (the clean ground first: the terrain and the vegetation are made on it)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_cleanground.py")] + ground, check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_terrain.py"), "build"] + built, check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "terrain", "make_vegetation.py")] + ground, check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
