#!/usr/bin/env python3
"""The picture the store's portrait window shows for a data cube without a face (a message, a guide): a data
cube drawn as an amber hologram over a faint grid, with scanlines, in the store's brass and gold. Written as
face_none.png into the given directory (default: export/legacy, beside the faces drawn anew), for
tools/hd_pictures.py to fit into the portrait window as it fits the faces.
usage: <python with PIL and numpy> tools/make_empty_face.py [out dir]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 720, 860   # about the window's shape (taller than wide), larger than it is drawn
S = 3             # supersampling of the line drawing


def project(p, yaw, pitch):
    x, y, z = p
    cx, sx = math.cos(yaw), math.sin(yaw)
    x, z = x * cx - z * sx, x * sx + z * cx
    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = y * cp - z * sp, y * sp + z * cp
    k = 7.0 / (7.0 + z)   # a little perspective
    return x * k, y * k


def lines(draw, segments, scale, cx, cy, colour, width):
    for a, b in segments:
        draw.line([(cx + a[0] * scale, cy - a[1] * scale), (cx + b[0] * scale, cy - b[1] * scale)], fill=colour,
                  width=width)


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                                  "export", "legacy")
    yaw, pitch = math.radians(35), math.radians(-24)
    corners = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = [(a, b) for i, a in enumerate(corners) for b in corners[i + 1:] if sum(u != v for u, v in zip(a, b)) == 1]
    cube = [(project(a, yaw, pitch), project(b, yaw, pitch)) for a, b in edges]
    inner = [(project(tuple(c * 0.45 for c in a), yaw, pitch), project(tuple(c * 0.45 for c in b), yaw, pitch))
             for a, b in edges]
    spokes = [(project(a, yaw, pitch), project(tuple(c * 0.45 for c in a), yaw, pitch)) for a in corners]

    big = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(big)
    cx, cy, scale = W * S / 2, H * S * 0.45, W * S * 0.19
    lines(d, cube, scale, cx, cy, 235, 4 * S)
    lines(d, inner, scale, cx, cy, 200, 3 * S)
    lines(d, spokes, scale, cx, cy, 120, 2 * S)
    # Rings round it, as of a projector's beam, and a base ellipse it floats over.
    for r, v in ((2.25, 70), (2.5, 40)):
        d.ellipse([cx - r * scale, cy - r * scale, cx + r * scale, cy + r * scale], outline=v, width=2 * S)
    base_y = cy + scale * 2.0
    d.ellipse([cx - scale * 1.3, base_y - scale * 0.22, cx + scale * 1.3, base_y + scale * 0.22], outline=150, width=3 * S)
    shape = np.asarray(big.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255

    glow = np.asarray(Image.fromarray((shape * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
    halo = np.asarray(Image.fromarray((shape * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))).astype(np.float32) / 255

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # The window's dark: brown-black, a little lighter in the middle; a faint grid; the beam rising from below.
    r = np.hypot((xx - W / 2) / W, (yy - H * 0.5) / H)
    background = 0.05 + 0.06 * np.clip(1 - r * 1.8, 0, 1)
    grid = ((np.abs(((xx - W / 2) % 48) - 24) > 23) | (np.abs(((yy) % 48) - 24) > 23)).astype(np.float32) * 0.035
    beam = np.clip(1 - np.abs(xx - W / 2) / (W * 0.32 + (base_y / S - yy) * 0.25), 0, 1) * (yy < base_y / S) * \
        np.clip((yy - H * 0.1) / (H * 0.8), 0, 1) * 0.07
    light = background + grid + beam + glow * 0.8 + halo * 0.45 + shape * 0.75
    # Scanlines, as a hologram's.
    light *= 0.86 + 0.14 * (np.sin(yy * math.pi / 3) ** 2)

    amber = np.array([1.0, 0.72, 0.32], dtype=np.float32)
    white = np.array([1.0, 0.95, 0.85], dtype=np.float32)
    hot = np.clip(shape * 1.1 - 0.45, 0, 1)[..., None]
    rgb = light[..., None] * (amber * (1 - hot) + white * hot)
    rgb = np.clip(rgb, 0, 1) ** (1 / 1.1)
    Image.fromarray((rgb * 255).astype(np.uint8), "RGB").save(os.path.join(out_dir, "face_none.png"))
    print(os.path.join(out_dir, "face_none.png"))


if __name__ == "__main__":
    main()
