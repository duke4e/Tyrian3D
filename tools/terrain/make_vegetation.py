#!/usr/bin/env python3
"""Vegetation for the 3D view's ground: where a ground map (exported with TYR3D_EXPORT_MAPS) has
palms, trees and grass, found by their colour, stored as an asset (assets/terrain/<map>.veg) that
the game draws as models on the terrain (palms and trees standing, grass as blades in the wind).

- Palms: small green patches on other ground (desert maps; "palms": true in levels.json).
- Trees: large green areas of strong texture (canopies): a tree on each bright top (palms with
  "forest": "palm" in levels.json, for palm jungles).
- Grass: large smooth green areas: clumps of blades every few pixels.
No palms or trees where ground enemies stand (export/terrain/ground.txt; the game clears the plants
under the ones that move as they pass), and nothing over holes. "vegetation": false in a map's levels.json entry turns it off.

usage: <python with numpy, scipy and PIL> tools/terrain/make_vegetation.py <map hash>... | all

The asset: "TYVG", version, count, side columns; the kinds' colours (palm leaves and trunk, tree
leaves and highlights, grass base and tips: 6 x RGB); then, zlib-compressed and in order of y, a
record per plant: x, y (uint16, map pixels with the generated columns), kind (0 palm, 1 tree,
2 grass), size (eighths of a pixel), turn (1/256 of a full turn), shade (128 = as is).
"""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_terrain as mt  # noqa: E402

PALM, TREE, GRASS = 0, 1, 2
BIG_REGION = 1500      # pixels: a green area this large is a forest or a meadow
FOREST_TEXTURE = 0.09  # local brightness spread above which a green area is a forest


def peaks(field, mask, distance):
    """Local maxima of a field inside a mask, about `distance` apart (ties broken by a little
    noise, so flat areas don't give a peak per pixel)."""
    rng = np.random.default_rng(7)
    field = np.where(mask, field + rng.random(field.shape, np.float32) * 1e-4, -1)
    top = ndimage.maximum_filter(field, size=2 * distance + 1)
    ys, xs = np.nonzero((field == top) & mask)
    return list(zip(xs.tolist(), ys.tolist()))


def detect(name, rgb, s):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = (g > r * 1.12) & (g > b * 1.05) & (g > 0.12)
    green = ndimage.binary_closing(green, np.ones((3, 3), bool))
    labels, n = ndimage.label(green)
    sizes = ndimage.sum(green, labels, range(1, n + 1)) if n else np.zeros(0)
    big = np.isin(labels, 1 + np.nonzero(sizes >= BIG_REGION)[0])
    small = np.isin(labels, 1 + np.nonzero((sizes >= 12) & (sizes < BIG_REGION))[0])
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    mean = ndimage.uniform_filter(lum, 9)
    spread = np.sqrt(np.maximum(ndimage.uniform_filter(lum * lum, 9) - mean * mean, 0))
    texture = ndimage.uniform_filter(spread, 25)

    # Not where ground enemies stand, nor over space. (Where they pass, the game clears the plants
    # under them as they go; grass is low: kept clear a little less.)
    standing, _ = mt.ground_enemies(name)
    keep_clear = mt.footprint(lum.shape, standing, 5)
    keep_low = mt.footprint(lum.shape, standing, 2)
    if s.get("void") == "hole":
        keep_clear |= mt.void_mask(rgb)
        keep_low |= mt.void_mask(rgb)

    rng = np.random.default_rng(int(name[:8], 16))
    plants = []
    colours = np.zeros((6, 3), np.float32)

    if s.get("palms") and small.any():
        soft = ndimage.gaussian_filter(small.astype(np.float32), 3.0)
        for x, y in peaks(soft, small & ~keep_clear, 7):
            plants.append((x, y, PALM, 7.0 + rng.random() * 2.0, rng.random(), 0.85 + rng.random() * 0.3))
        colours[0] = rgb[small].mean(0)
        colours[1] = np.array([0.42, 0.30, 0.18]) * (0.6 + 0.8 * lum[~green].mean())

    forest = big & (texture > FOREST_TEXTURE)
    meadow = big & ~forest
    if forest.any():
        tops = ndimage.gaussian_filter(lum, 2.0)
        inside = ndimage.binary_erosion(forest, np.ones((5, 5), bool)) & ~keep_clear
        if s.get("forest") == "palm":
            # A palm jungle (SAVARA's): palms on the canopy's bright tops.
            for x, y in peaks(tops, inside, 6):
                plants.append((x, y, PALM, 6.0 + rng.random() * 2.5, rng.random(), 0.8 + rng.random() * 0.4))
            if not colours[0].any():
                colours[0] = np.percentile(rgb[forest], 70, axis=0)
                colours[1] = np.array([0.42, 0.30, 0.18]) * (0.6 + 0.8 * lum[~green].mean())
        else:
            for x, y in peaks(tops, inside, 5):
                plants.append((x, y, TREE, 4.5 + rng.random() * 2.5, rng.random(), 0.8 + rng.random() * 0.4))
            colours[2] = rgb[forest].mean(0)
            colours[3] = np.percentile(rgb[forest], 90, axis=0)
    if meadow.any():
        inside = ndimage.binary_erosion(meadow, np.ones((3, 3), bool)) & ~keep_low
        step = s.get("grass_step", 5)
        ys, xs = np.mgrid[0:lum.shape[0]:step, 0:lum.shape[1]:step]
        jx = xs + rng.integers(0, step, xs.shape)
        jy = ys + rng.integers(0, step, ys.shape)
        jx, jy = np.clip(jx, 0, lum.shape[1] - 1), np.clip(jy, 0, lum.shape[0] - 1)
        chosen = inside[jy, jx]
        average = max(float(lum[meadow].mean()), 0.05)
        for x, y in zip(jx[chosen].tolist(), jy[chosen].tolist()):
            plants.append((x, y, GRASS, 4.5 + rng.random() * 2.5, rng.random(), 0.75 + 0.5 * lum[y, x] / average))
        colours[4] = rgb[meadow].mean(0) * 0.8
        colours[5] = np.minimum(rgb[meadow].mean(0) * 1.6 + 0.04, 1.0)
    return plants, colours, (forest, meadow, small)


def cmd_build(name):
    info, rgb, _ = mt.load_map(name)
    s = mt.settings(name)
    path = os.path.join(mt.OUT, f"{name}.veg")
    if info["background"] != 1 or s.get("vegetation") is False:
        if os.path.exists(path):
            os.remove(path)
        return
    plants, colours, (forest, meadow, small) = detect(name, rgb, s)
    if not plants:
        if os.path.exists(path):
            os.remove(path)
        print(f"{name} ({info.get('level', '?').strip()}): no vegetation")
        return
    plants.sort(key=lambda p: p[1])
    records = b"".join(struct.pack("<HHBBBB", int(x), int(y), kind, min(255, int(size * 8)), int(turn * 255) & 255,
                                   min(255, int(shade * 128))) for x, y, kind, size, turn, shade in plants)
    header = struct.pack("<4sIII", b"TYVG", 1, len(plants), info["side_columns"])
    header += bytes(int(min(max(c, 0), 1) * 255) for c in colours.reshape(-1))
    with open(path, "wb") as f:
        f.write(header + zlib.compress(records, 9))
    # A review picture: the level's start with the plants marked.
    top = max(rgb.shape[0] - 1400, 0)
    image = Image.fromarray((rgb[top:] * 255).astype(np.uint8))
    draw = ImageDraw.Draw(image)
    marks = {PALM: (255, 0, 255), TREE: (255, 255, 0), GRASS: (0, 255, 255)}
    for x, y, kind, size, _, _ in plants:
        if y >= top:
            r = size if kind != GRASS else 0.7
            draw.ellipse((x - r, y - top - r, x + r, y - top + r), outline=marks[kind])
    image.save(os.path.join(mt.REVIEW, f"{name}_vegetation.png"))
    counts = [sum(1 for p in plants if p[2] == k) for k in (PALM, TREE, GRASS)]
    print(f"{name} ({info.get('level', '?').strip()}): {counts[0]} palms, {counts[1]} trees, {counts[2]} grass clumps")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    names = sys.argv[1:]
    if names == ["all"]:
        names = sorted(json.load(open(mt.LEVELS)).keys())
    mt.read_ground_log(names)  # (the log in one pass for all of them)
    for name in names:
        cmd_build(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
