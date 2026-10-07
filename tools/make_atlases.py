#!/usr/bin/env python3
"""Groups the game's sprites into PNG atlases, for upscaling them or using them as references.

usage: tools/make_atlases.py <extract dir> <out dir>

<extract dir> is the output of TYR3D_EXTRACT (sheets in the levels' palette and catalog.json).
Writes to <out dir>:

  ships.png         every player ship sprite in its five banking frames (hard left .. hard right)
  sidekicks.png     every sidekick's animation frames
  enemies_e<N>.png  the enemy types of episode N, a row each with their animation frames
  powerups.png, coins.png, shots.png, shots2.png, explosions.png
                    whole sheets as exported (their 2x2 sprites span four 12x14 cells)
  atlases.json      what is in each cell: sheet, sprite index, size, and what it belongs to

The grouped atlases use the same grid: cells of 32x36 pixels, each sprite centred in its cell on
a transparent background (24x28 for 2x2 sprites, 12x14 for 1x1 ones), so an upscaled atlas maps
back cell by cell at any scale.
"""
import json
import os
import shutil
import struct
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender"))
from sprite_profile import sprite_pixels  # noqa: E402

CELL_W, CELL_H = 32, 36
MAX_ROWS = 56  # rows of cells per file (taller atlases are split into parts)


def write_png_rgba(path, width, height, pixels):
    """pixels: rows of (r, g, b, a)."""
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for p in row:
            raw += bytes(p)

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


class Atlas:
    def __init__(self, name, columns):
        self.name, self.columns = name, columns
        self.rows = []  # rows of cells: (sheet path, sprite, large, info) or None

    def add_row(self, cells):
        # Leave out sprites past the end of their sheet (some enemies point beyond it).
        cells = [c for c in cells if in_sheet(c[1], c[2])]
        for i in range(0, len(cells), self.columns):
            self.rows.append(cells[i:i + self.columns])

    def write(self, out_dir, index):
        parts = [self.rows[i:i + MAX_ROWS] for i in range(0, len(self.rows), MAX_ROWS)] or [[]]
        for p, rows in enumerate(parts):
            name = self.name if len(parts) == 1 else f"{self.name}_{p + 1}"
            self.write_part(out_dir, name, rows, index)

    def write_part(self, out_dir, name, rows, index):
        width, height = self.columns * CELL_W, max(1, len(rows)) * CELL_H
        image = [[(0, 0, 0, 0)] * width for _ in range(height)]
        cache = {}
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell is None:
                    continue
                sheet, sprite, large, info = cell
                key = (sheet, sprite, large)
                if key not in cache:
                    cache[key] = sprite_pixels(sheet, sprite, large)
                pixels = cache[key]
                h, w = len(pixels), len(pixels[0])
                x0, y0 = c * CELL_W + (CELL_W - w) // 2, r * CELL_H + (CELL_H - h) // 2
                for y, line in enumerate(pixels):
                    for x, p in enumerate(line):
                        if p is not None:
                            image[y0 + y][x0 + x] = (*p, 255)
                index.append({"atlas": f"{name}.png", "column": c, "row": r,
                              "sheet": os.path.splitext(os.path.basename(sheet))[0], "sprite": sprite,
                              "size": "2x2" if large else "1x1", **info})
        write_png_rgba(os.path.join(out_dir, f"{name}.png"), width, height, image)
        print(f"{name}.png: {width}x{height}")


def in_sheet(sprite, large):
    column, row = (sprite - 1) % 19, (sprite - 1) // 19
    return sprite >= 1 and row + (1 if large else 0) < 16 and column + (1 if large else 0) < 19


def main():
    extract, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    catalog = json.load(open(os.path.join(extract, "catalog.json")))
    sheet = lambda name: os.path.join(extract, "sheets", name + ".png")
    index = []

    # Player ships: the five banking frames, sprite - 4 .. sprite + 4 (ship_banking * 2 + shipGr).
    ships = Atlas("ships", 5)
    seen = set()
    for s in catalog["ships"]:
        key = (s["sheet"], s["index"])
        if s["index"] <= 1 or key in seen:  # the Nort Ship and the Dragonwing are drawn in parts
            continue
        seen.add(key)
        ships.add_row([(sheet(s["sheet"]), s["index"] + 2 * bank, True,
                        {"ship": s["id"], "name": s["name"].strip(), "banking": bank}) for bank in range(-2, 3)])
    ships.write(out_dir, index)

    sidekicks = Atlas("sidekicks", 10)
    seen = set()
    for k in catalog["sidekicks"]:
        frames = list(dict.fromkeys(k["frames"]))
        key = (k["sheet"], tuple(frames))
        if k["name"].strip() == "None" or key in seen:
            continue
        seen.add(key)
        large = k["size"] == "2x2"
        sidekicks.add_row([(sheet(k["sheet"]), f, large, {"sidekick": k["id"], "name": k["name"].strip(), "frame": i})
                           for i, f in enumerate(frames)])
    sidekicks.write(out_dir, index)

    by_episode = {}
    for e in catalog["enemies"]:
        by_episode.setdefault(e["episode"], []).append(e)
    for episode, enemies in sorted(by_episode.items()):
        atlas = Atlas(f"enemies_e{episode}", 20)
        seen = set()
        for e in enemies:
            frames = list(dict.fromkeys(f for f in e["frames"] if f > 0))
            key = (e["sheet_file"], tuple(frames), e["large"])
            if not frames or key in seen:
                continue
            seen.add(key)
            atlas.add_row([(sheet(e["sheet_file"]), f, e["large"],
                            {"enemy": e["id"], "episode": episode, "frame": i}) for i, f in enumerate(frames)])
        atlas.write(out_dir, index)

    # Sheets whose sprites are mixed 1x1 and 2x2 stay whole (a 2x2 sprite spans four cells).
    whole = {}
    for name in ("powerups", "coins", "shots", "shots2", "explosions"):
        if os.path.exists(sheet(name)):
            shutil.copyfile(sheet(name), os.path.join(out_dir, f"{name}.png"))
            whole[f"{name}.png"] = "the whole sheet: 19 columns of 12x14 cells, sprite i at column (i-1) % 19, row (i-1) // 19"

    with open(os.path.join(out_dir, "atlases.json"), "w") as f:
        json.dump({"cell": [CELL_W, CELL_H], "cells": index, "whole_sheets": whole}, f, indent=1)


if __name__ == "__main__":
    main()
