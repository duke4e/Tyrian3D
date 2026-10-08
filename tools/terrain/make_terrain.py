#!/usr/bin/env python3
"""Terrain for the 3D view's ground (background 1): heights for a whole map, computed offline from
the map's surfaces and stored as an asset (assets/terrain/<map>.ter), which the game loads.

The tiles only say what surface is where; the terrain doesn't follow them. Each pixel of the map
(exported with TYR3D_EXPORT_MAPS, with the generated columns beside it) is sorted into surface
classes by its brightness, texture and colour (k-means, the same every run); each class has a
height (tools/terrain/levels.json, by map; "~" takes the nearest other surface's height, for rims
and edges), and the heights are softened into slopes and cliffs, with a little relief of the
surface's own detail on top. Black space ("void", for the levels over space) can sink into a chasm
below the platforms.

The game lifts ground enemies onto the terrain; where they stand (export/terrain/ground.txt, from
tools/terrain/ground_log.sh) the terrain is level, so they stand flat.

usage: <python with numpy, scipy and PIL> tools/terrain/make_terrain.py classify <map hash>...
       ... make_terrain.py build <map hash>...      (or "all": every map in levels.json)
       ... make_terrain.py sheets                   (contact sheets of the built terrain)

classify writes export/terrain/<map>_classes.png (the map beside its classes, numbered, with how
many standing enemies each holds) for choosing the heights; build writes the asset and
export/terrain/<map>_relief.png (the map lit by its terrain). The game's ground stands at height 0:
classes where ground enemies stand stay at 0; raised ground (plateaus, mountains, walls) goes up to
TERRAIN_MAX, chasms down to -TERRAIN_MAX.

levels.json, by map: "classes" (how many), "heights" ({class: height or "~"}), and optionally
"softness" (how far cliffs spread, pixels), "detail" (relief of the surface's detail), "rolling"
(the height of gentle hills and hollows over the whole map, for a map of one surface), "void"
(the height of black space, e.g. -40, or "hole": nothing there, the platforms' walls going down
into the dark, and the stars far below where the level has them; "rim" and "rim_depth" round the
platforms' edges off).

Backgrounds 2 and 3 (their maps' entries with "solid": true) become solids: their plane on top,
rounded off over "bevel" pixels at the edges, walls down to the ground where they are clear or
where ground enemies are under them (the game only makes them solid where they are drawn over the
ground's enemies, and keeps their tops below what flies).
"""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.cluster.vq import kmeans2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = os.path.join(ROOT, "export", "maps")
OUT = os.path.join(ROOT, "assets", "terrain")
REVIEW = os.path.join(ROOT, "export", "terrain")
GROUND = os.path.join(REVIEW, "ground.txt")
LEVELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "levels.json")

SAMPLE = 2           # game pixels per height sample
TERRAIN_MAX = 60     # heights are stored as signed bytes, in game pixels
HOLE = -128          # a sample with nothing there (B3D_TERRAIN_HOLE)
REVIEW_ROWS = 2100   # the map's rows shown for review: its last (the level's start)
COLOURS = np.array([[230, 60, 60], [60, 200, 60], [60, 90, 230], [230, 200, 40], [200, 60, 200], [40, 200, 200],
                    [240, 240, 240], [140, 100, 60]], np.float32) / 255


def load_map(name):
    """The map's colours (RGBA, 0-1: backgrounds 2 and 3 are clear where they have nothing)."""
    info = json.load(open(os.path.join(MAPS, f"map_{name}.json")))
    parts = [np.asarray(Image.open(os.path.join(MAPS, p["file"])).convert("RGBA")) for p in info["parts"]]
    rgba = np.concatenate(parts, 0).astype(np.float32) / 255
    return info, rgba[..., :3], rgba[..., 3] > 0.5


def features(rgb):
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    mean = ndimage.uniform_filter(lum, 7)
    texture = np.sqrt(np.maximum(ndimage.uniform_filter(lum * lum, 7) - mean * mean, 0))
    chroma = ndimage.gaussian_filter(rgb, (2, 2, 0)) - ndimage.gaussian_filter(lum, 2)[..., None]
    return lum, np.dstack([ndimage.gaussian_filter(lum, 2) * 2, texture * 6, chroma[..., 0] * 4, chroma[..., 2] * 4,
                           ndimage.gaussian_filter(lum, 6) * 1.5])


def classify(rgb, k):
    lum, feat = features(rgb)
    flat = feat.reshape(-1, feat.shape[2])
    np.random.seed(1)
    centroids, _ = kmeans2(flat[::13], k, seed=1, minit="++")
    labels = np.empty(flat.shape[0], np.int32)
    for start in range(0, flat.shape[0], 1 << 20):  # in chunks: the distances are k times the map
        chunk = flat[start:start + (1 << 20)]
        labels[start:start + len(chunk)] = ((chunk[:, None, :] - centroids[None]) ** 2).sum(2).argmin(1)
    labels = labels.reshape(lum.shape)
    # Smooth the classes (a vote over 5 x 5 pixels).
    votes = np.stack([ndimage.uniform_filter((labels == i).astype(np.float32), 5) for i in range(k)])
    return lum, votes.argmax(0), centroids


def void_mask(rgb):
    """Black space: black pixels in areas wider than a few pixels (not a dark line or speck)."""
    black = rgb.max(2) < 0.045
    return ndimage.binary_opening(black, np.ones((5, 5), bool))


def settings(name):
    levels = json.load(open(LEVELS)) if os.path.exists(LEVELS) else {}
    return levels.get(name, {"classes": 5, "heights": {}})


_ground = None


def ground_enemies(name):
    """Where the map's ground enemies stand ((x, y, size), in its pixels) and the points they pass
    while moving over it, from the log. Each enemy slot's points in order: a new enemy where the
    slot's position jumps; one that stays within a few pixels stands."""
    global _ground
    if _ground is None:
        _ground = {}
        if os.path.exists(GROUND):
            last = {}
            for line in open(GROUND):
                parts = line.split()
                if len(parts) != 6 or not all(p.isdigit() for p in parts[2:]):
                    continue  # mixed up with another message
                key, x, y, size, slot = parts[1], int(parts[2]), int(parts[3]), int(parts[4]), parts[5]
                tracks = _ground.setdefault(key, [])
                track = last.get((key, slot))
                if track is None or abs(track[-1][0] - x) + abs(track[-1][1] - y) > 40:
                    track = []
                    tracks.append(track)
                    last[(key, slot)] = track
                track.append((x, y, size))
    standing, moving = [], []
    for track in _ground.get(name, []):
        xs, ys = [p[0] for p in track], [p[1] for p in track]
        if max(xs) - min(xs) <= 10 and max(ys) - min(ys) <= 10:
            standing.append((sum(xs) / len(xs), sum(ys) / len(ys), track[0][2]))
        else:
            moving.extend(track)
    return standing, moving


def footprint(shape, points, extra):
    """The pixels within each point's size (plus extra) of it."""
    mask = np.zeros(shape, bool)
    for x, y, size in points:
        r = size / 2 + extra
        y0, y1 = int(max(y - r, 0)), int(min(y + r + 1, shape[0]))
        x0, x1 = int(max(x - r, 0)), int(min(x + r + 1, shape[1]))
        if y0 < y1 and x0 < x1:
            mask[y0:y1, x0:x1] = True
    return mask


def cmd_classify(name):
    info, rgb, _ = load_map(name)
    s = settings(name)
    lum, labels, centroids = classify(rgb, s["classes"])
    standing, _ = ground_enemies(name)
    on = np.zeros(s["classes"], int)
    for x, y, _ in standing:
        if 0 <= int(y) < labels.shape[0] and 0 <= int(x) < labels.shape[1]:
            on[labels[int(y), int(x)]] += 1
    os.makedirs(REVIEW, exist_ok=True)
    h = rgb.shape[0]
    top = max(h - REVIEW_ROWS, 0)
    view = np.concatenate([rgb[top:], COLOURS[labels[top:]] * 0.65 + rgb[top:] * 0.35], 1)
    image = Image.fromarray((view * 255).astype(np.uint8)).resize((view.shape[1] // 2, view.shape[0] // 2))
    draw = ImageDraw.Draw(image)
    for x, y, _ in standing:
        if y >= top:
            px, py = (x + rgb.shape[1]) / 2, (y - top) / 2
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), outline=(255, 255, 255))
    for i in range(s["classes"]):
        draw.rectangle((4, 4 + i * 16, 16, 16 + i * 16), fill=tuple(int(c * 255) for c in COLOURS[i]))
        draw.text((20, 4 + i * 16), f"{i}: {100 * (labels == i).mean():.0f}%  h={s['heights'].get(str(i), 0)}"
                  f"  stand {on[i]}", fill=(255, 255, 255))
    path = os.path.join(REVIEW, f"{name}_classes.png")
    image.save(path)
    print(f"{name} ({info.get('level', '?').strip()}): {path}; standing enemies by class {list(on)}")


def solid_heights(rgb, opaque, s):
    """Background 2 or 3 as a solid: its plane on top, rounded off at the edges, where it is clear
    a hole (the walls go down to the ground)."""
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    opaque = ndimage.binary_opening(opaque, np.ones((3, 3), bool))  # not single pixels
    inside = ndimage.distance_transform_edt(opaque)
    bevel = s.get("bevel", 4.0)
    h = -s.get("bevel_depth", 4.0) * np.clip(1 - inside / bevel, 0, 1) ** 2
    detail = ndimage.gaussian_filter(lum, 1.0) - ndimage.gaussian_filter(lum, 4.0)
    h += s.get("detail", 4.0) * detail
    return h, ~opaque


def heights(name, rgb, opaque, info, s):
    """The heights (game pixels) and where there is nothing (holes)."""
    if info["background"] > 1:
        h, hole = solid_heights(rgb, opaque, s)
        # Clear where ground enemies are under it (in the game hidden under the background): they
        # stand or move in notches and trenches rather than inside the rock.
        standing, moving = ground_enemies(name)
        hole |= footprint(h.shape, standing + moving, 4)
        return h, hole, standing
    lum, labels, _ = classify(rgb, s["classes"])
    target = np.zeros(labels.shape, np.float32)
    inherit = np.zeros(labels.shape, bool)
    for c, height in s["heights"].items():
        if height == "~":  # the height of the nearest other surface (rims, edges)
            inherit |= labels == int(c)
        else:
            target[labels == int(c)] = float(height)
    hole = np.zeros(labels.shape, bool)
    if "void" in s:
        space = void_mask(rgb)
        if s["void"] == "hole":  # nothing there: chasms with walls down into the dark
            hole = space
        else:
            target[space] = float(s["void"])
        inherit &= ~space
    if inherit.any():
        _, (iy, ix) = ndimage.distance_transform_edt(inherit, return_indices=True)
        target = target[iy, ix]
    # Slopes and cliffs: the classes' heights softened a little; the surface's own detail on top,
    # more of it on raised ground.
    h = ndimage.gaussian_filter(target, s.get("softness", 2.5))
    if s.get("rolling"):  # gentle hills and hollows (the same every run)
        rng = np.random.default_rng(int(name[:8], 16))
        noise = ndimage.gaussian_filter(rng.standard_normal(h.shape).astype(np.float32), 28, mode="wrap")
        h += s["rolling"] * noise / (np.abs(noise).max() + 1e-6)
    detail = ndimage.gaussian_filter(lum, 1.0) - ndimage.gaussian_filter(lum, 4.0)
    h += s.get("detail", 5.0) * detail * (0.5 + np.clip(h / 30.0, 0, 1))
    if hole.any():
        # The platforms' edges rounded off down into the chasms, as rocks' are.
        inside = ndimage.distance_transform_edt(~hole)
        rim = s.get("rim", 6.0)
        h -= s.get("rim_depth", 8.0) * np.clip(1 - inside / rim, 0, 1) ** 2

    # The ground under its enemies (the game lifts them onto the terrain): where they stand, level
    # (the terrain's mean height there), blending into the terrain around.
    standing, _ = ground_enemies(name)
    if standing:
        under = footprint(h.shape, standing, 3)
        keep = np.clip(ndimage.gaussian_filter(under.astype(np.float32), 3.0) * 2.0, 0, 1)
        level = ndimage.uniform_filter(h, 30)
        h = h * (1 - keep) + level * keep
    return h, hole, standing


def relief_image(rgb, h, hole, standing, top):
    """The map lit by its terrain from the top left, deeper ground darker, holes blue-black,
    standing enemies ringed."""
    h = np.where(hole, -TERRAIN_MAX, h)[top:]
    gy, gx = np.gradient(h)
    light = np.clip(1.0 + (-gx - gy) * 0.18, 0.35, 1.6)
    depth = np.clip(1.0 + h / 80.0, 0.35, 1.3)
    image = np.clip(rgb[top:] * (light * depth)[..., None], 0, 1)
    image[hole[top:]] = (0.05, 0.05, 0.12)
    out = Image.fromarray((image * 255).astype(np.uint8))
    draw = ImageDraw.Draw(out)
    for x, y, _ in standing:
        if y >= top:
            draw.ellipse((x - 6, y - 6 - top, x + 6, y + 6 - top), outline=(255, 255, 0), width=2)
    return out.resize((out.width // 2, out.height // 2))


def cmd_build(name):
    info, rgb, opaque = load_map(name)
    s = settings(name)
    h, hole, standing = heights(name, rgb, opaque, info, s)
    # Samples every SAMPLE pixels, at the samples' corners (the grid the game builds meshes on).
    grid = np.pad(h[::SAMPLE, ::SAMPLE], ((0, 1), (0, 1)), mode="edge")
    holes = np.pad(hole[::SAMPLE, ::SAMPLE], ((0, 1), (0, 1)), mode="edge")
    data = np.clip(np.round(grid), -TERRAIN_MAX, TERRAIN_MAX).astype(np.int8)
    data[holes] = HOLE
    os.makedirs(OUT, exist_ok=True)
    version = 2 if holes.any() else 1
    header = struct.pack("<4sIIIII", b"TYTR", version, data.shape[1], data.shape[0], SAMPLE, info["side_columns"])
    with open(os.path.join(OUT, f"{name}.ter"), "wb") as f:
        f.write(header + zlib.compress(data.tobytes(), 9))
    os.makedirs(REVIEW, exist_ok=True)
    relief_image(rgb, h, hole, standing, max(rgb.shape[0] - REVIEW_ROWS, 0)).save(
        os.path.join(REVIEW, f"{name}_relief.png"))
    surface = data[~holes]
    print(f"{name} ({info.get('level', '?').strip()} bg{info['background']}): {data.shape[1]} x {data.shape[0]} samples, "
          f"heights {surface.min() if surface.size else 0}..{surface.max() if surface.size else 0}, "
          f"{100 * holes.mean():.0f}% holes, {len(standing)} standing enemies")


def cmd_sheets():
    """The built reliefs four to a sheet (export/terrain/sheets/relief_NN.png), by level name."""
    levels = json.load(open(LEVELS))
    names = sorted((v.get("level", "?").strip(), k) for k, v in levels.items()
                   if os.path.exists(os.path.join(REVIEW, f"{k}_relief.png")))
    os.makedirs(os.path.join(REVIEW, "sheets"), exist_ok=True)
    for n in range(0, len(names), 4):
        images = [(level, key, Image.open(os.path.join(REVIEW, f"{key}_relief.png"))) for level, key in names[n:n + 4]]
        width = sum(i.width for _, _, i in images) + 8 * len(images)
        height = max(i.height for _, _, i in images) + 18
        sheet = Image.new("RGB", (width, height), (20, 20, 24))
        draw = ImageDraw.Draw(sheet)
        x = 0
        for level, key, image in images:
            sheet.paste(image, (x, 18))
            draw.text((x + 4, 3), f"{level} {key[:6]}", fill=(255, 230, 80))
            x += image.width + 8
        sheet.save(os.path.join(REVIEW, "sheets", f"relief_{n // 4:02d}.png"))
    print(f"{(len(names) + 3) // 4} sheets")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "sheets":
        cmd_sheets()
        return 0
    if len(sys.argv) < 3 or sys.argv[1] not in ("classify", "build"):
        print(__doc__)
        return 1
    names = sys.argv[2:]
    if names == ["all"]:
        names = sorted(json.load(open(LEVELS)).keys())
    for name in names:
        (cmd_classify if sys.argv[1] == "classify" else cmd_build)(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
