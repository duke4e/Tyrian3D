#!/usr/bin/env python3
"""Erasures for the 3D view's ground: where a map has a ground enemy's object painted into its
tiles (or the ground around it that the sprite carries too), under the enemy's model. For each place
a ground enemy stands (export/terrain/ground.txt), the ground sprites of the map's level are tried
there (+-2 pixels): the pixels of the best match that equal the map's are erased, filled with the
map's own ground from a nearby place a whole number of tiles away (where the ground around matches
best and no other enemy stands). The game copies those pixels into its ground texture
(render_gpu.c, terrain_ring_row), so the model stands on clean ground.

usage: <python with numpy, scipy and PIL> tools/terrain/make_erasures.py <TYR3D_EXTRACT dir> [map hash...]

The asset (assets/terrain/<map>.era): "TYER", version, count; then, zlib-compressed and in order of
y, per erasure: x, y (uint16, the map's pixels, the generated columns included), w, h (uint8), the
source's offset dx, dy (int16), then w x h mask bytes (1: erase).
"""
import glob
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_terrain as mt  # noqa: E402

MIN_MATCH = 0.3   # of the sprite's pixels equal to the map's, for the sprite to be the one standing there
TOLERANCE = 6     # per channel, for pixels to be equal (exported colours round a little)
TILE_W, TILE_H = 24, 28


def sprite_cells(extract):
    """The ground enemies' first frames by level: (key, RGBA cell)."""
    cat = json.load(open(os.path.join(extract, "catalog.json")))
    sheets, by_level = {}, {}
    for e in cat["enemies"]:
        if not e.get("frames") or "ground" not in e.get("layers", []):
            continue
        name = e["sheet_file"]
        if name not in sheets:
            path = os.path.join(extract, "sheets", name + ".png")
            sheets[name] = np.asarray(Image.open(path).convert("RGBA")).astype(np.int16) if os.path.exists(path) else None
        img = sheets[name]
        if img is None:
            continue
        i = e["frames"][0] - 1
        c, r = i % 19, i // 19
        w, h = (24, 28) if e["large"] else (12, 14)
        cell = img[r * 14:r * 14 + h, c * 12:c * 12 + w]
        if cell.shape[:2] != (h, w) or not (cell[..., 3] > 0).any():
            continue
        for level in str(e.get("levels", "")).split(","):
            if level:
                by_level.setdefault(level.strip(), {})[(name, e["frames"][0])] = cell
    return by_level


def best_match(m, x, y, size, cells):
    H, W = m.shape[:2]
    best = (0.0, None, None)
    for cell in cells.values():
        h, w = cell.shape[:2]
        if w != size:
            continue
        opaque = cell[..., 3] > 0
        n = opaque.sum()
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x0, y0 = x - w // 2 + dx, y - h // 2 + dy
                if x0 < 0 or y0 < 0 or x0 + w > W or y0 + h > H:
                    continue
                eq = (np.abs(m[y0:y0 + h, x0:x0 + w] - cell[..., :3]).max(axis=2) <= TOLERANCE) & opaque
                frac = eq.sum() / n
                if frac > best[0]:
                    best = (frac, (x0, y0), eq)
    return best


def source_offset(m, alpha, mask, x0, y0, taken):
    """A tile-aligned offset whose ground continues the ground round the mask best."""
    h, w = mask.shape
    H, W = m.shape[:2]
    ring = ndimage.binary_dilation(mask, iterations=2) & ~mask
    ring_full = np.zeros((h + 4, w + 4), bool)
    ring_full[2:-2, 2:-2] = ring
    best = (1e9, None)
    for oy in (-56, -28, 0, 28, 56):
        for ox in (-48, -24, 0, 24, 48):
            if ox == 0 and oy == 0:
                continue
            sx, sy = x0 + ox, y0 + oy
            if sx - 2 < 0 or sy - 2 < 0 or sx + w + 2 > W or sy + h + 2 > H:
                continue
            if taken[sy:sy + h, sx:sx + w].any() or not alpha[sy:sy + h, sx:sx + w].all():
                continue
            here = m[y0 - 2:y0 + h + 2, x0 - 2:x0 + w + 2]
            there = m[sy - 2:sy + h + 2, sx - 2:sx + w + 2]
            if here.shape != there.shape or here.shape[:2] != ring_full.shape:
                continue
            score = np.abs(here[ring_full] - there[ring_full]).mean() if ring_full.any() else 0
            if score < best[0]:
                best = (score, (ox, oy))
    return best[1]


def build(name, by_level):
    info, rgb, alpha = mt.load_map(name)
    path = os.path.join(mt.OUT, f"{name}.era")
    standing, _ = mt.ground_enemies(name)
    cells = by_level.get(info.get("level", "").strip(), {})
    if not standing or not cells:
        if os.path.exists(path):
            os.remove(path)
        return
    m = (rgb * 255 + 0.5).astype(np.int16)
    found = []
    taken = np.zeros(m.shape[:2], bool)
    for x, y, size in standing:
        frac, at, eq = best_match(m, int(round(x)), int(round(y)), size, cells)
        if frac < MIN_MATCH:
            continue
        x0, y0 = at
        h, w = eq.shape
        mask = ndimage.binary_dilation(eq, iterations=1)  # and the outline's antialiasing
        found.append((x0, y0, mask))
        taken[y0:y0 + h, x0:x0 + w] = True
    records = []
    for x0, y0, mask in sorted(found, key=lambda f: f[1]):
        offset = source_offset(m, alpha, mask, x0, y0, taken)
        if offset is None:
            continue
        h, w = mask.shape
        records.append(struct.pack("<HHBBhh", x0, y0, w, h, offset[0], offset[1]) + mask.astype(np.uint8).tobytes())
    if not records:
        if os.path.exists(path):
            os.remove(path)
        return
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"TYER", 1, len(records)) + zlib.compress(b"".join(records), 9))
    print(f"{name} ({info.get('level', '?').strip()}): {len(records)} erasures")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    by_level = sprite_cells(sys.argv[1])
    names = sys.argv[2:] or sorted(os.path.basename(f)[4:-5] for f in glob.glob(os.path.join(mt.MAPS, "map_*.json")))
    for name in names:
        build(name, by_level)
    return 0


if __name__ == "__main__":
    sys.exit(main())
