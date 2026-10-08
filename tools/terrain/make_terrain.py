#!/usr/bin/env python3
"""Terrain for the 3D view's ground (background 1): heights for a whole map, computed offline from
the map's surfaces and stored as an asset (assets/terrain/<map>.ter), which the game loads.

The tiles only say what surface is where; the terrain doesn't follow them. Each pixel of the map
(exported with TYR3D_EXPORT_MAPS, with the generated columns beside it) is sorted into surface
classes by its brightness, texture and colour (k-means, the same every run); each class has a
height (tools/terrain/levels.json, by map; "~" takes the nearest other surface's height, for rims
and edges), and the heights are softened into slopes and cliffs,
with a little relief of the surface's own detail on top.

usage: <python with numpy, scipy and PIL> tools/terrain/make_terrain.py classify <map hash>...
       ... make_terrain.py build <map hash>...      (or "all": every map in levels.json)

classify writes export/terrain/<map>_classes.png (the map beside its classes, numbered, and a
legend) for choosing the heights; build writes the asset. The game's ground stands at height 0:
classes where ground enemies stand stay at 0; raised ground (plateaus, mountains, walls) goes up to
TERRAIN_MAX, chasms down to -TERRAIN_MAX.
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
LEVELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "levels.json")

SAMPLE = 2           # game pixels per height sample
TERRAIN_MAX = 60     # heights are stored as signed bytes, in game pixels
COLOURS = np.array([[230, 60, 60], [60, 200, 60], [60, 90, 230], [230, 200, 40], [200, 60, 200], [40, 200, 200],
                    [240, 240, 240], [140, 100, 60]], np.float32) / 255


def load_map(name):
    info = json.load(open(os.path.join(MAPS, f"map_{name}.json")))
    parts = [np.asarray(Image.open(os.path.join(MAPS, p["file"])).convert("RGB")) for p in info["parts"]]
    return info, np.concatenate(parts, 0).astype(np.float32) / 255


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


def settings(name):
    levels = json.load(open(LEVELS)) if os.path.exists(LEVELS) else {}
    return levels.get(name, {"classes": 5, "heights": {}})


def cmd_classify(name):
    info, rgb = load_map(name)
    s = settings(name)
    lum, labels, centroids = classify(rgb, s["classes"])
    os.makedirs(REVIEW, exist_ok=True)
    # The map's first 1500 rows of pixels (the level's end) and its last 1500 (its start), shrunk.
    h = rgb.shape[0]
    view = np.concatenate([rgb[h - 2100:], COLOURS[labels[h - 2100:]] * 0.65 + rgb[h - 2100:] * 0.35], 1)
    image = Image.fromarray((view * 255).astype(np.uint8)).resize((view.shape[1] // 2, view.shape[0] // 2))
    draw = ImageDraw.Draw(image)
    for i in range(s["classes"]):
        draw.rectangle((4, 4 + i * 16, 16, 16 + i * 16), fill=tuple(int(c * 255) for c in COLOURS[i]))
        draw.text((20, 4 + i * 16), f"{i}: {100 * (labels == i).mean():.0f}%  h={s['heights'].get(str(i), 0)}",
                  fill=(255, 255, 255))
    path = os.path.join(REVIEW, f"{name}_classes.png")
    image.save(path)
    print(f"{name} ({info.get('level', '?').strip()}): {path}")


def cmd_build(name):
    info, rgb = load_map(name)
    s = settings(name)
    lum, labels, _ = classify(rgb, s["classes"])
    target = np.zeros(labels.shape, np.float32)
    inherit = np.zeros(labels.shape, bool)
    for c, height in s["heights"].items():
        if height == "~":  # the height of the nearest other surface (rims, edges)
            inherit |= labels == int(c)
        else:
            target[labels == int(c)] = float(height)
    if inherit.any():
        _, (iy, ix) = ndimage.distance_transform_edt(inherit, return_indices=True)
        target = target[iy, ix]
    # Slopes and cliffs: the classes' heights softened a little; the surface's own detail on top,
    # more of it on raised ground.
    h = ndimage.gaussian_filter(target, s.get("softness", 2.5))
    detail = ndimage.gaussian_filter(lum, 1.0) - ndimage.gaussian_filter(lum, 4.0)
    h += s.get("detail", 5.0) * detail * (0.5 + np.clip(h / 30.0, 0, 1))
    # Samples every SAMPLE pixels, at the samples' corners (the grid the game builds meshes on).
    rows, width = h.shape
    grid = h[::SAMPLE, ::SAMPLE]
    grid = np.pad(grid, ((0, 1), (0, 1)), mode="edge")
    data = np.clip(np.round(grid), -TERRAIN_MAX, TERRAIN_MAX).astype(np.int8)
    os.makedirs(OUT, exist_ok=True)
    header = struct.pack("<4sIIIII", b"TYTR", 1, data.shape[1], data.shape[0], SAMPLE, info["side_columns"])
    with open(os.path.join(OUT, f"{name}.ter"), "wb") as f:
        f.write(header + zlib.compress(data.tobytes(), 9))
    print(f"{name} ({info.get('level', '?').strip()}): {data.shape[1]} x {data.shape[0]} samples, "
          f"heights {data.min()}..{data.max()}")


def main():
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
