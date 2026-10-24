#!/usr/bin/env python3
"""Sprite sheets at 4x from the upscaled atlases, for the 3D view's generated models (HD volumes):
each sheet in the game's layout (19 columns of 12 x 14 cells, so 48 x 56 at 4x), every sprite the
atlases hold put back in its place (a 2x2 sprite over four cells).

usage: <python with numpy and PIL> tools/hd_sheets.py [upscale dir, default upscale] [hd dir, default data/hd]

Reads <upscale>/in/atlases.json and the upscaled atlases in <upscale>/out (the work folder); writes what the game
loads into the HD folder: <hd>/sheets/<sheet>.hd ("TYHD", width, height, then zlib-compressed RGBA rows) and the
upscaled HUD panels <hd>/hud_1p.png, hud_2p.png; a <sheet>.png to look at goes to <upscale>/out/sheets. The
pictures are made from the game's data, so like it they stay out of the repository (data/ is not in it).
"""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image

SCALE = 4
CELL_W, CELL_H = 12, 14
COLUMNS, ROWS = 19, 16


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "upscale")
    hd_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "data", "hd")
    index = json.load(open(os.path.join(root, "in", "atlases.json")))
    cw, ch = index["cell"]
    out_dir = os.path.join(hd_dir, "sheets")
    look_dir = os.path.join(root, "out", "sheets")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(look_dir, exist_ok=True)
    width, height = COLUMNS * CELL_W * SCALE, ROWS * CELL_H * SCALE
    sheets = {}

    def sheet(name):
        if name not in sheets:
            sheets[name] = np.zeros((height, width, 4), np.uint8)
        return sheets[name]

    # Whole sheets upscaled as they are (power-ups, coins, shots): first, so that sprites upscaled
    # on their own (without their neighbours in the sheet) replace them.
    for file in index.get("whole_sheets", {}):
        path = os.path.join(root, "out", file)
        name = os.path.splitext(file)[0]
        if name.startswith("hud") or not os.path.exists(path):
            continue
        picture = np.asarray(Image.open(path).convert("RGBA"))
        if picture.shape[:2] == (height, width):
            sheet(name)[:] = picture

    atlases = {}
    placed = 0
    for c in index["cells"]:
        path = os.path.join(root, "out", c["atlas"])
        if not os.path.exists(path):
            continue
        if c["atlas"] not in atlases:
            atlases[c["atlas"]] = np.asarray(Image.open(path).convert("RGBA"))
        atlas = atlases[c["atlas"]]
        large = c["size"] == "2x2"
        w, h = (2 * CELL_W, 2 * CELL_H) if large else (CELL_W, CELL_H)
        x0 = (c["column"] * cw + (cw - w) // 2) * SCALE
        y0 = (c["row"] * ch + (ch - h) // 2) * SCALE
        picture = atlas[y0:y0 + h * SCALE, x0:x0 + w * SCALE]
        i = c["sprite"] - 1
        sx, sy = (i % COLUMNS) * CELL_W * SCALE, (i // COLUMNS) * CELL_H * SCALE
        target = sheet(c["sheet"])
        if sy + h * SCALE > height or sx + w * SCALE > width:
            continue
        target[sy:sy + h * SCALE, sx:sx + w * SCALE] = picture
        placed += 1

    for name, pixels in sheets.items():
        with open(os.path.join(out_dir, name + ".hd"), "wb") as f:
            f.write(struct.pack("<4sII", b"TYHD", width, height) + zlib.compress(pixels.tobytes(), 6))
        Image.fromarray(pixels).save(os.path.join(look_dir, name + ".png"))
    print(f"{len(sheets)} sheets, {placed} sprites placed, in {out_dir}")
    # The HUD panels, upscaled whole (render_gpu.c hud_panel_hd).
    for name in ("hud_1p.png", "hud_2p.png"):
        path = os.path.join(root, "out", name)
        if os.path.exists(path):
            Image.open(path).convert("RGBA").save(os.path.join(hd_dir, name))
            print(f"{name} in {hd_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
