#!/usr/bin/env python3
"""The map's planets as 3D spheres turning: for each turning planet of PLANET_SHAPES (15 frames of a turn, the
store's map and the rogue run's map show them), its surface is put together from the frames (each frame's middle,
the meridian facing the viewer, a slice of the turn), its painted light and shade evened out, and the sphere is
rendered anew turning under a light from the upper left, its night side dark, its atmosphere's rim and halo round
it, in FRAMES frames: data/hd/planets/planet3d_<first sprite>.png, a sheet of COLUMNS x ROWS frames of SIZE pixels
(the disc RADIUS of the frame's half, room for the halo). The game draws a planet's frame by the time
(render_gpu.c rgpu_ui_table_sprite). Also writes each surface as surface_<first sprite>.png, for looking at.

usage: <python with numpy, scipy and PIL> tools/planets3d.py [data/hd/icons] [data/hd/planets]
"""
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

GROUPS = [3, 19, 35, 51, 67, 83, 99, 115, 131]  # the turning planets' first sprites (PGR - 1), 15 frames each
TURN = 15             # frames of a turn in the original
SIZE = 256            # a frame of the sheet (pixels)
RADIUS = 0.78         # the disc's radius, of the frame's half
FRAMES = 48           # frames of a turn rendered
COLUMNS = 8
TEX_W, TEX_H = 1024, 512
LIGHT = np.array([-0.55, 0.45, 0.7])  # towards the light: from the upper left, in front


def load(path):
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255
    return im


def disc(im):
    """The planet's disc in a frame: its middle and its radii across and up (by its opaque pixels; some are drawn a
    little wide), inside the dark outline the sprites have."""
    a = im[..., 3] > 0.5
    ys, xs = np.nonzero(a)
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    rx, ry = (xs.max() + 1 - xs.min()) / 2, (ys.max() + 1 - ys.min()) / 2
    return cx, cy, rx * 0.9, ry * 0.88


def sample(im, x, y):
    """Bilinear sample of an image (H x W x 4) at float pixel coordinates."""
    h, w = im.shape[:2]
    x = np.clip(x - 0.5, 0, w - 1.001)
    y = np.clip(y - 0.5, 0, h - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    a = im[y0, x0] * (1 - fx) + im[y0, x0 + 1] * fx
    b = im[y0 + 1, x0] * (1 - fx) + im[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def surface(frames, direction):
    """The planet's surface (equirectangular, TEX_W x TEX_H RGB) from the frames of its turn: every texel from the
    frames whose facing meridian is nearest its longitude, weighted by nearness; and how well the frames agree."""
    lon = (np.arange(TEX_W) + 0.5) / TEX_W * 2 * math.pi
    lat = (0.5 - (np.arange(TEX_H) + 0.5) / TEX_H) * math.pi
    LON, LAT = np.meshgrid(lon, lat)
    step = 2 * math.pi / len(frames)
    acc = np.zeros((TEX_H, TEX_W, 3))
    wsum = np.zeros((TEX_H, TEX_W))
    disagreement = 0.0
    prev = None
    for f, (im, (cx, cy, rx, ry)) in enumerate(frames):
        facing = (direction * f * step) % (2 * math.pi)
        d = (LON - facing + math.pi) % (2 * math.pi) - math.pi  # longitude from the facing meridian
        w = np.clip(1 - np.abs(d) / (step * 1.5), 0, 1)
        x = cx + rx * np.cos(LAT) * np.sin(d)
        y = cy - ry * np.sin(LAT)
        c = sample(im, x, y)[..., :3]
        acc += c * w[..., None]
        wsum += w
        if prev is not None:
            both = (w > 0) & (prev[1] > 0)
            if both.any():
                disagreement += float(np.abs(c - prev[0])[both].mean())
        prev = (c, w)
    tex = np.nan_to_num(acc / np.maximum(wsum, 1e-6)[..., None])
    return np.clip(tex, 0, 1), disagreement


def even_light(tex):
    """The painted light and shade evened out: each texel's lightness against the lightness round it (a broad blur)
    pulled most of the way to the surface's mean."""
    lum = tex @ np.array([0.299, 0.587, 0.114])
    broad = ndimage.gaussian_filter(lum, sigma=(TEX_H / 10, TEX_W / 14), mode=("nearest", "wrap"))
    mean = lum.mean()
    k = (mean + 0.75 * (broad - mean)) / np.maximum(broad, 0.03)
    return np.clip(tex * (0.35 + 0.65 * k)[..., None], 0, 1)


def polar_caps(tex):
    """Near the poles (where the frames show little but their dark outline) the surface fades into the colour round
    the latitudes it is sure of, keeping a little of its own detail."""
    lat = (0.5 - (np.arange(TEX_H) + 0.5) / TEX_H) * 180
    out = tex.copy()
    for sign in (1, -1):
        sure = int(round((0.5 - sign * 50 / 180) * TEX_H))
        band = tex[max(sure - 4, 0):sure + 4].reshape(-1, 3).mean(axis=0)
        for y in range(TEX_H):
            l = lat[y] * sign
            if l > 50:
                w = min((l - 50) / 30, 1) * 0.75
                out[y] = tex[y] * (1 - w) + band * w
    return out


def render(tex, turn):
    """A frame: the sphere turned by `turn` (radians), lit, its rim and halo; RGBA SIZE x SIZE."""
    s = SIZE
    c = (np.arange(s) + 0.5) / s * 2 - 1
    X, Y = np.meshgrid(c, -c)
    R = RADIUS
    rr = (X * X + Y * Y) / (R * R)
    inside = rr < 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    nx, ny, nz = X / R, Y / R, z
    lat = np.arcsin(np.clip(ny, -1, 1))
    lon = (np.arctan2(nx, nz) + turn) % (2 * math.pi)
    u = lon / (2 * math.pi) * TEX_W
    v = (0.5 - lat / math.pi) * TEX_H
    teximg = np.concatenate([tex, np.ones(tex.shape[:2] + (1,))], axis=2)
    col = sample(teximg, u, v)[..., :3]
    L = LIGHT / np.linalg.norm(LIGHT)
    d = nx * L[0] + ny * L[1] + nz * L[2]
    t = np.clip((d + 0.12) / 0.55, 0, 1)
    lit = 0.06 + 0.94 * t * t * (3 - 2 * t)
    # A soft highlight, the limb a little darker (the air's depth).
    half = L + np.array([0, 0, 1.0])
    half /= np.linalg.norm(half)
    spec = np.clip(nx * half[0] + ny * half[1] + nz * half[2], 0, 1) ** 40 * 0.18 * t
    limb = 0.75 + 0.25 * z
    rgb = col * (lit * limb)[..., None] + spec[..., None]
    # The atmosphere: the rim lit in the surface's own colour, a halo fading out past the disc, on the lit side.
    tint = np.clip(tex.reshape(-1, 3).mean(axis=0) * 1.6 + 0.15, 0, 1)
    dist = np.sqrt(X * X + Y * Y) / R
    sun_side = np.clip((X * L[0] + Y * L[1]) / np.maximum(np.sqrt(X * X + Y * Y), 1e-6) * 0.5 + 0.6, 0.15, 1)
    rim = np.clip((dist - 0.82) / 0.18, 0, 1) ** 2 * inside * 0.5 * sun_side
    rgb = rgb * (1 - rim[..., None]) + tint * rim[..., None]
    halo = np.clip(1 - (dist - 1) / 0.22, 0, 1) ** 2 * (dist >= 1) * 0.55 * sun_side
    edge = np.clip((1 - dist) * s * R / 1.5, 0, 1)  # (the disc's edge, a pixel and a half soft)
    alpha = np.maximum(edge * inside, halo)
    out = np.where(inside[..., None], rgb, tint[None, None, :] * np.ones_like(rgb))
    rgba = np.concatenate([np.clip(out, 0, 1), alpha[..., None]], axis=2)
    return (rgba * 255).round().astype(np.uint8)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "data", "hd", "icons")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "data", "hd", "planets")
    os.makedirs(dst, exist_ok=True)
    rows = (FRAMES + COLUMNS - 1) // COLUMNS
    for first in GROUPS:
        frames = []
        for f in range(TURN):
            path = os.path.join(src, f"planet_{first + f}.png")
            if not os.path.exists(path):
                break
            im = load(path)
            frames.append((im, disc(im)))
        if len(frames) < TURN:
            print(f"planet {first}: only {len(frames)} frames, left as it is")
            continue
        # Which way it turns: the way its frames agree with each other best.
        best = None
        for direction in (1, -1):
            tex, err = surface(frames, direction)
            if best is None or err < best[1]:
                best = (tex, err, direction)
        tex = polar_caps(even_light(best[0]))
        Image.fromarray((tex * 255).round().astype(np.uint8)).save(os.path.join(dst, f"surface_{first}.png"))
        sheet = Image.new("RGBA", (COLUMNS * SIZE, rows * SIZE), (0, 0, 0, 0))
        for k in range(FRAMES):
            img = Image.fromarray(render(tex, best[2] * 2 * math.pi * k / FRAMES), "RGBA")
            sheet.paste(img, ((k % COLUMNS) * SIZE, (k // COLUMNS) * SIZE))
        sheet.save(os.path.join(dst, f"planet3d_{first}.png"))
        print(f"planet {first}: turning {'+' if best[2] > 0 else '-'} (frames disagree {best[1]:.2f}), {FRAMES} frames")


if __name__ == "__main__":
    main()
