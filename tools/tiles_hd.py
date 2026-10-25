#!/usr/bin/env python3
"""HD background tiles that still tile: upscaled in context.

usage: <python with torch> tools/tiles_hd.py <model.pth> [--maps export/maps] [--out data/hd/tiles]
           [--work upscale/out/tiles] [--tilesets z,y] [--min 12] [--keep 24] [--tile 192] [--add]

A tile upscaled on its own gets edges that don't meet its neighbours'. Here whole maps
(tools/export_maps.sh: every level's maps in parts of 72 rows, with their shape grid) go through the
ESRGAN model (tools/upscale_sprites.py), so every tile is upscaled among its real neighbours. Each
tile (tileset, shape number) is then the per-pixel median of its upscales in different places
(inside a tile they hardly differ; on its edges the median over the neighbours it has), quantized to
the levels' palette: every pixel the nearest colour among all shades of the colour ramps the tile
uses (index >> 4), so the game's palette effects (water, lava, filters, fades) work on it as on the
original. A tile doesn't depend on the map it is in, so generated levels built from the same tiles
(episode 6, whose maps follow the originals' neighbours) get them too.

Parts are picked per tileset until every shape is seen --min times (every occurrence if it has
fewer) away from the parts' first and last rows (no neighbours across the cut); at most --keep
upscales of a shape are kept for its median. Writes <out>/<tileset>.hdt (what the game loads: data/hd, beside the game's
data and like it outside the repository) and, in the work folder, <work>/<tileset>.png (the tiles, to look at) and
<work>/<tileset>_median.npz (for --requantize); a tileset named by a symbol is written x<hex>, as the sprite sheets.
--add makes only the tiles a tileset's kept medians lack (shapes of maps exported since, such as a custom
episode's: src/episodes.h), from the parts that have them, and keeps the others as they are.

.hdt: "TYHT", then little-endian u16 version (1), scale, tile width, tile height, tile count, then
zlib-compressed: per tile its shape number (u16) and scale² · width · height palette indices, row by
row (index 0: transparent, as in the game's tiles).
"""
import argparse
import glob
import json
import os
import random
import struct
import sys
import zlib

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upscale_sprites as ups  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCALE = 4


def palette():
    return np.array([[int(v) for v in line.split()] for line in open(os.path.join(HERE, "blender", "palette_levels.txt"))
                     if line.strip()], np.float32)


def file_name(tileset):
    return tileset if tileset.isalnum() else "x%02x" % ord(tileset)


def parts_by_tileset(maps_dir):
    """tileset -> [(meta, part)] for every exported map part."""
    groups = {}
    for path in sorted(glob.glob(os.path.join(maps_dir, "map_*.json"))):
        meta = json.load(open(path))
        for part in meta["parts"]:
            if os.path.exists(os.path.join(maps_dir, part["file"])):
                groups.setdefault(meta["tileset"], []).append((meta, part))
    return groups


def part_cells(meta, part, rows_in_part):
    """(row in part, column, shape) of the map's own columns, skipping blanks."""
    out = []
    for r in range(rows_in_part):
        row = meta["shapes"][part["first_row"] + r] if part["first_row"] + r < len(meta["shapes"]) else None
        if row is None:
            break
        for c, shape in enumerate(row):
            if shape > 0:
                out.append((r, c, shape))
    return out


def pick_parts(parts, minimum, only=None):
    """Greedy: parts with the most still-needed occurrences first, until every shape (of only, if
    given) has enough."""
    usable = []
    totals = {}
    for meta, part in parts:
        rows = 72
        cells = [(r, c, s) for r, c, s in part_cells(meta, part, rows)]
        inner = [s for r, c, s in cells if 0 < r < rows - 1 and (only is None or s in only)]
        usable.append((meta, part, inner))
        for s in inner:
            totals[s] = totals.get(s, 0) + 1
    need = {s: min(minimum, n) for s, n in totals.items()}
    chosen = []
    while any(v > 0 for v in need.values()):
        best, gain = None, 0
        for i, (meta, part, inner) in enumerate(usable):
            g = 0
            left = dict()
            for s in inner:
                if need.get(s, 0) - left.get(s, 0) > 0:
                    g += 1
                    left[s] = left.get(s, 0) + 1
            if g > gain:
                best, gain = i, g
        if best is None:
            break
        meta, part, inner = usable.pop(best)
        for s in inner:
            if need.get(s, 0) > 0:
                need[s] -= 1
        chosen.append((meta, part))
    return chosen


def upscale_part(model, device, path, tile):
    img = np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255
    rgb, alpha = ups.bleed(img[..., :3], img[..., 3]), img[..., 3]
    colour = ups.run(model, device, rgb, tile)
    if alpha.min() < 1:
        alpha_up = ups.run(model, device, np.repeat(alpha[..., None], 3, 2), tile).mean(axis=2)
    else:
        alpha_up = np.ones(colour.shape[:2], np.float32)
    return np.asarray(Image.open(path).convert("RGBA")), np.dstack((colour, alpha_up))


def quantize(hd, tile_indices, pal):
    """hd: HxWx4 float 0..1 → HxW palette indices (0 where transparent)."""
    ramps = sorted({int(i) >> 4 for i in tile_indices.ravel() if i != 0})
    if not ramps:
        return np.zeros(hd.shape[:2], np.uint8)
    # Colour 0 is nothing (clear in backgrounds 2 and 3, a hole in the ground): only where the tile
    # has it, and then black pixels of the upscale become it.
    cand = np.array(([0] if (tile_indices == 0).any() else []) +
                    [r * 16 + s for r in ramps for s in range(16) if r * 16 + s != 0])
    colours = pal[cand]
    flat = hd[..., :3].reshape(-1, 3) * 255
    best = np.zeros(flat.shape[0], np.int64)
    best_d = np.full(flat.shape[0], np.inf, np.float32)
    for k, c in enumerate(colours):  # (one candidate at a time: little memory)
        d = ((flat - c) ** 2).sum(axis=1)
        closer = d < best_d
        best[closer], best_d[closer] = k, d[closer]
    out = cand[best].reshape(hd.shape[:2]).astype(np.uint8)
    out[hd[..., 3] < 0.5] = 0
    return out


def write_tileset(out_dir, work_dir, tileset, medians, indices, pal):
    """The .hdt and the look-at sheet from the tiles' medians (HxWx4 uint8) and 1x indices."""
    shapes = sorted(medians)
    tw, th = 24, 28
    blob = bytearray()
    sheet_cols = 12
    sheet = np.zeros((((len(shapes) + sheet_cols - 1) // sheet_cols) * th * SCALE, sheet_cols * tw * SCALE, 4), np.uint8)
    for k, shape in enumerate(shapes):
        q = quantize(medians[shape].astype(np.float32) / 255, indices[shape], pal)
        blob += struct.pack("<H", shape) + q.tobytes()
        y, x = (k // sheet_cols) * th * SCALE, (k % sheet_cols) * tw * SCALE
        rgba = np.zeros(q.shape + (4,), np.uint8)
        rgba[..., :3] = pal[q].astype(np.uint8)
        rgba[..., 3] = np.where(q > 0, 255, 0)
        sheet[y:y + th * SCALE, x:x + tw * SCALE] = rgba
    name = file_name(tileset)
    with open(os.path.join(out_dir, name + ".hdt"), "wb") as f:
        f.write(b"TYHT" + struct.pack("<5H", 1, SCALE, tw, th, len(shapes)) + zlib.compress(bytes(blob), 9))
    Image.fromarray(sheet).save(os.path.join(work_dir, name + ".png"))
    print(f"wrote {name}.hdt: {len(shapes)} tiles", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", nargs="?", default="")
    ap.add_argument("--maps", default=os.path.join(ROOT, "export", "maps"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "hd", "tiles"))
    ap.add_argument("--work", default=os.path.join(ROOT, "upscale", "out", "tiles"))
    ap.add_argument("--tilesets", default="")
    ap.add_argument("--min", type=int, default=12)
    ap.add_argument("--keep", type=int, default=24)
    ap.add_argument("--tile", type=int, default=192)
    ap.add_argument("--requantize", action="store_true",
                    help="only write the .hdt again from the medians kept in <work>/<tileset>_median.npz")
    ap.add_argument("--add", action="store_true",
                    help="only the shapes <work>/<tileset>_median.npz lacks; the kept tiles stay as they are")
    args = ap.parse_args()

    pal = palette()
    lut = {tuple(int(v) for v in c): i for i, c in enumerate(pal)}
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.work, exist_ok=True)
    groups = parts_by_tileset(args.maps)
    wanted = [t for t in args.tilesets.split(",") if t] or sorted(groups)
    if args.requantize:
        for tileset in wanted:
            cache = np.load(os.path.join(args.work, file_name(tileset) + "_median.npz"))
            medians = {int(k[1:]): cache[k] for k in cache.files if k[0] == "m"}
            indices = {int(k[1:]): cache[k] for k in cache.files if k[0] == "i"}
            write_tileset(args.out, args.work, tileset, medians, indices, pal)
        return 0

    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = ups.load_model(args.model, device)
    rng = random.Random(1)
    for tileset in wanted:
        kept_medians, kept_indices, only = {}, {}, None
        if args.add:
            cache = np.load(os.path.join(args.work, file_name(tileset) + "_median.npz"))
            kept_medians = {int(k[1:]): cache[k] for k in cache.files if k[0] == "m"}
            kept_indices = {int(k[1:]): cache[k] for k in cache.files if k[0] == "i"}
            used = {s for meta, part in groups[tileset] for r, c, s in part_cells(meta, part, 72)}
            only = used - set(kept_medians)
            print(f"tileset {tileset}: {len(kept_medians)} tiles kept, adding {sorted(only)}", flush=True)
            if not only:
                continue
        chosen = pick_parts(groups[tileset], args.min, only)
        print(f"tileset {tileset}: {len(chosen)} of {len(groups[tileset])} parts", flush=True)
        samples, seen, indices = {}, {}, {}
        for n, (meta, part) in enumerate(chosen):
            orig, up = upscale_part(model, device, os.path.join(args.maps, part["file"]), args.tile)
            tw, th = meta["tile"]
            side = meta.get("side_columns", 0)
            rows = orig.shape[0] // th
            for r, c, shape in part_cells(meta, part, rows):
                if only is not None and shape not in only:
                    continue
                edge_row = r == 0 or r == rows - 1
                x, y = (side + c) * tw, r * th
                if shape not in indices:
                    cell = orig[y:y + th, x:x + tw]
                    indices[shape] = np.array([[lut.get(tuple(int(v) for v in p[:3]), 0) if p[3] > 0 else 0
                                                for p in line] for line in cell], np.uint8)
                if edge_row and seen.get(shape, 0) >= 1:
                    continue  # (cut off from its neighbours: only if nothing better is had)
                hd = up[y * SCALE:(y + th) * SCALE, x * SCALE:(x + tw) * SCALE]
                hd8 = (hd * 255 + 0.5).astype(np.uint8)
                seen[shape] = seen.get(shape, 0) + 1
                bucket = samples.setdefault(shape, [])
                if len(bucket) < args.keep:
                    bucket.append(hd8)
                else:  # reservoir: every occurrence equally likely to be kept
                    j = rng.randrange(seen[shape])
                    if j < args.keep:
                        bucket[j] = hd8
            print(f"  part {n + 1}/{len(chosen)} {part['file']}: {len(samples)} shapes", flush=True)

        medians = {s: np.median(np.stack(v).astype(np.float32), axis=0).astype(np.uint8) for s, v in samples.items()}
        medians.update(kept_medians)
        indices.update(kept_indices)
        np.savez_compressed(os.path.join(args.work, file_name(tileset) + "_median.npz"),
                            **{f"m{s}": v for s, v in medians.items()}, **{f"i{s}": indices[s] for s in medians})
        write_tileset(args.out, args.work, tileset, medians, indices, pal)
    return 0


if __name__ == "__main__":
    sys.exit(main())
