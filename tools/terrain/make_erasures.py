#!/usr/bin/env python3
"""Erasures for the 3D view's ground: where a map has a ground enemy's object painted into its
tiles (or the ground around it that the sprite carries too), under the enemy's model. For each place
a ground enemy stands (export/terrain/ground.txt), the ground sprites of the map's level are tried
there (+-2 pixels): the pixels of the best match that equal the map's are erased, filled with the
map's ground tile (the most common tile round each tile the object touches, from the nearest place
it is and no enemy stands; on the generated side columns, ground from nearby that matches best). The game copies those pixels into its ground texture
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


def colour_keys(pixels):
    """Colours, coarsely (so a palette's shades of one surface share keys)."""
    q = (np.asarray(pixels) // 12).astype(np.int32)
    return q[..., 0] * 4096 + q[..., 1] * 64 + q[..., 2]


def source_offset(m, alpha, mask, x0, y0, taken):
    """A tile-aligned offset whose ground continues the ground round the mask best."""
    h, w = mask.shape
    H, W = m.shape[:2]
    ring = ndimage.binary_dilation(mask, iterations=2) & ~mask
    ring_full = np.zeros((h + 4, w + 4), bool)
    ring_full[2:-2, 2:-2] = ring
    best = (1e9, None)
    # What the ground round the patch is like: the source's inside must be like it too (not only
    # its edge), so a shore or a road nearby isn't copied in.
    here_ring = m[y0 - 2:y0 + h + 2, x0 - 2:x0 + w + 2]
    if here_ring.shape[:2] != ring_full.shape or not ring_full.any():
        return None
    ring_pixels = here_ring[ring_full].astype(np.float32)
    ring_mean, ring_std = ring_pixels.mean(0), ring_pixels.std(0)
    wider = m[max(y0 - 8, 0):y0 + h + 8, max(x0 - 8, 0):x0 + w + 8]
    wider_ring = np.ones(wider.shape[:2], bool)
    wider_ring[8 if y0 >= 8 else y0:, 8 if x0 >= 8 else x0:][:h, :w] &= ~ndimage.binary_dilation(mask, iterations=1)
    ring_keys = np.unique(colour_keys(wider[wider_ring].astype(np.float32)))
    for oy in range(-4 * TILE_H, 4 * TILE_H + 1, TILE_H):
        for ox in range(-4 * TILE_W, 4 * TILE_W + 1, TILE_W):
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
            inside = there[2:-2, 2:-2][mask].astype(np.float32)
            likeness = np.abs(inside.mean(0) - ring_mean).sum() + np.abs(inside.std(0) - ring_std).sum()
            # Pixels in colours the ground round the patch doesn't have (another surface) count heavily.
            far = 1.0 - np.isin(colour_keys(inside), ring_keys).mean()
            score = np.abs(here[ring_full] - there[ring_full]).mean() + likeness + 400 * far
            if score < best[0]:
                best = (score, (ox, oy))
    return best[1]


def tile_fills(m, tiles, side_columns, taken, mask, x0, y0):
    """The mask cut by the map's tiles; for each tile it touches, the most common tile round it (the
    ground) where it is nearest and nothing stands: (x, y, mask part, offset to it)."""
    rows, columns = tiles.shape
    h, w = mask.shape
    out = []
    for r in range(y0 // TILE_H, (y0 + h - 1) // TILE_H + 1):
        for c in range(x0 // TILE_W - side_columns, (x0 + w - 1) // TILE_W - side_columns + 1):
            if not (0 <= r < rows and 0 <= c < columns):
                continue
            tx, ty = (c + side_columns) * TILE_W, r * TILE_H
            ax, ay = max(tx, x0), max(ty, y0)
            bx, by = min(tx + TILE_W, x0 + w), min(ty + TILE_H, y0 + h)
            part = mask[ay - y0:by - y0, ax - x0:bx - x0]
            if not part.any():
                continue
            # The ground: the most common tile among those round it where nothing stands.
            counts = {}
            for rr in range(max(r - 4, 0), min(r + 5, rows)):
                for cc in range(max(c - 4, 0), min(c + 5, columns)):
                    if (rr, cc) == (r, c):
                        continue
                    sx, sy = (cc + side_columns) * TILE_W, rr * TILE_H
                    if taken[sy:sy + TILE_H, sx:sx + TILE_W].any():
                        continue
                    counts[tiles[rr, cc]] = counts.get(tiles[rr, cc], 0) + 1
            if not counts:
                continue
            # Of those, the one the object was painted over: the most pixels alike (beside water, the
            # turret's own tile may be grass while the tiles round it are shore).
            here = m[ty:ty + TILE_H, tx:tx + TILE_W]
            def alike(t):
                rr, cc = np.argwhere(tiles == t)[0]
                there = m[rr * TILE_H:(rr + 1) * TILE_H, (cc + side_columns) * TILE_W:(cc + side_columns + 1) * TILE_W]
                return int((np.abs(there.astype(np.int32) - here).max(axis=2) <= 2).sum())
            ground = max(counts, key=lambda t: (alike(t), counts[t]))
            if ground == tiles[r, c]:
                continue  # the tile is the ground already: the object isn't painted into it
            best = None
            for rr in range(max(r - 6, 0), min(r + 7, rows)):
                for cc in range(columns):
                    if tiles[rr, cc] != ground:
                        continue
                    sx, sy = (cc + side_columns) * TILE_W, rr * TILE_H
                    if taken[sy:sy + TILE_H, sx:sx + TILE_W].any():
                        continue
                    d = abs(rr - r) * 2 + abs(cc - c)
                    if best is None or d < best[0]:
                        best = (d, (cc - c) * TILE_W, (rr - r) * TILE_H)
            if best is not None:
                out.append((ax, ay, part, best[1:]))
    return out


def side_mask(info, tiles, mask, x0, y0):
    """The part of a mask over the map's generated side columns."""
    h, w = mask.shape
    left = info["side_columns"] * TILE_W
    right = left + tiles.shape[1] * TILE_W
    xs = np.arange(x0, x0 + w)
    outside = (xs < left) | (xs >= right)
    return mask & outside[None, :]


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
    for x, y, size in standing:  # no ground is taken from where any enemy stands
        x, y = int(round(x)), int(round(y))
        taken[max(y - 16, 0):y + 16, max(x - 14, 0):x + 14] = True
    for x, y, size in standing:
        frac, at, eq = best_match(m, int(round(x)), int(round(y)), size, cells)
        if frac < MIN_MATCH:
            continue
        x0, y0 = at
        h, w = eq.shape
        mask = ndimage.binary_dilation(eq, iterations=1)  # and the outline's antialiasing
        found.append((x0, y0, mask))
    records = []
    tiles = np.array(info["shapes"])
    for x0, y0, mask in sorted(found, key=lambda f: f[1]):
        for rx, ry, part, offset in tile_fills(m, tiles, info["side_columns"], taken, mask, x0, y0):
            h, w = part.shape
            records.append(struct.pack("<HHBBhh", rx, ry, w, h, offset[0], offset[1]) + part.astype(np.uint8).tobytes())
        # (Off the map's own columns, the generated sides: ground from nearby, as it matches.)
        side = side_mask(info, tiles, mask, x0, y0)
        if side.any():
            offset = source_offset(m, alpha, side, x0, y0, taken)
            if offset is not None:
                h, w = side.shape
                records.append(struct.pack("<HHBBhh", x0, y0, w, h, offset[0], offset[1]) + side.astype(np.uint8).tobytes())
    records.sort(key=lambda r: struct.unpack("<H", r[2:4])[0])
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
