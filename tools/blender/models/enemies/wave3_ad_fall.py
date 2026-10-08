"""Batch AD of wave 3 (sheet H), the waterfall of TORM and BONUS, modelled as the sprites look (models.cfg:
yaw=0); the kit is wave3_ad_kit.py, the pixels wave3_ad_art.py.

- torm_fall_tl, torm_fall_tm, torm_fall_tr above torm_fall_bl, torm_fall_bm, torm_fall_br (H 165, 167, 169
  above 203, 205, 207; enemies 739-741 above 742-744, the events put the bottom row at (x + 24 i, y) and the
  top row 28 pixels above it, on the ground): the waterfall, 72 x 56: a curtain of water pouring over a lip
  at the back and sloping down towards the camera (so that the top view sees it) into a churning pool,
  between grey rock pillars with a dark cleft at the right, leaves at the pool's corners. The levels make
  it wider by repeating the middle column (740 and 743 side by side), so the middle pieces are built to
  tile: at their sides the shapes depend on y only. Its frames (165, 234, 240, 117 and so on) make the water
  flow; the model is still: streaks raised on the curtain, light ones glinting, foam on the pool.
  Built whole and cut into its six sprites (origin).

usage: Blender -b --factory-startup -P wave3_ad_fall.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import random
import sys

import numpy as np
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ad_kit as kit  # noqa: E402
from wave3_ad_kit import k, sh, w, pal, Painter  # noqa: E402

FALL = kit.frame("FALL", 72, (36, 28))
LIP = 19.0          # the height of the lip the water pours over (the back, y = 28)
POOL = 1.4          # the pool's surface
CURTAIN_FOOT = -9.0  # where the curtain meets the pool
SEAMS = (-12.0, 12.0)  # the middle column's sides: shapes there depend on y only (it tiles)
WATER_COLUMNS = (12, 56)  # the curtain's pixel columns (the rest is rock)
GAP_COLUMNS = (56, 60)    # the dark cleft between the water and the right-hand rocks


def curtain_z(y):
    """The curtain's height: the lip at the back, rounding over, falling, easing into the pool."""
    t = min(1.0, max(0.0, (y - CURTAIN_FOOT) / (28.0 - CURTAIN_FOOT)))
    s = t * t * (3 - 2 * t)
    return POOL + (LIP - POOL) * (0.25 * t + 0.75 * s)


def gaussian(field, sx, sy):
    """A separable gaussian blur of a 2D array (sigmas in pixels along x and y; edges clamped)."""
    out = field.copy()
    for axis, sigma in ((1, sx), (0, sy)):
        if sigma <= 0:
            continue
        r = int(math.ceil(3 * sigma))
        kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
        kern /= kern.sum()
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        padded = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, kv in enumerate(kern):
            sl = [slice(None), slice(None)]
            sl[axis] = slice(i, i + out.shape[axis])
            acc += kv * padded[tuple(sl)]
        out = acc
    return out


def bilinear(field, ox, oy):
    """(x, y) -> the field (one value per pixel, rows down) between pixel centres."""
    h, wd = field.shape

    def at(x, y):
        c, r = x + ox - 0.5, oy - y - 0.5
        c = min(max(c, 0.0), wd - 1.0)
        r = min(max(r, 0.0), h - 1.0)
        c0, r0 = min(int(c), wd - 2), min(int(r), h - 2)
        fc, fr = c - c0, r - r0
        return ((1 - fr) * ((1 - fc) * field[r0, c0] + fc * field[r0, c0 + 1]) +
                fr * ((1 - fc) * field[r0 + 1, c0] + fc * field[r0 + 1, c0 + 1]))
    return at


def pixel_kind(v, c, r):
    """'w' curtain, 'p' pool, 'r' rock, 'd' the cleft, 'g' leaves."""
    ramp = v >> 4
    if ramp in (2, 0xc):
        return "g"
    if WATER_COLUMNS[0] <= c < WATER_COLUMNS[1] or (ramp == 3):
        return "w" if r < 37 else "p"
    if GAP_COLUMNS[0] <= c < GAP_COLUMNS[1] and r < 40:
        return "d"
    return "r"


def fields():
    """The heights over the curtain's slope, per pixel: the base (by kind, blurred) and the detail (the
    streaks, blurred down the curtain), and the shades the faces are painted with."""
    g = FALL.g
    h, wd = len(g), len(g[0])
    masks = {kind: np.zeros((h, wd)) for kind in "wprdg"}
    water, pool, rock = np.zeros((h, wd)), np.zeros((h, wd)), np.zeros((h, wd))
    for r in range(h):
        for c in range(wd):
            v = g[r][c]
            kind = pixel_kind(v, c, r)
            masks[kind][r, c] = 1.0
            shade = v & 15
            water[r, c] = (shade - 5.5) * 0.22 if v >> 4 == 3 else -0.45
            pool[r, c] = max(-0.4, (shade - 6.0) * 0.3) if v >> 4 == 3 else -0.3
            rock[r, c] = (shade - 4.0) * 0.55
    # The kinds' heights over the slope, their borders soft (no pixel steps): the rocks stand higher than
    # the water, the cleft sinks, the leaves' ground a little up.
    soft = {kind: gaussian(m, 1.1, 1.1) for kind, m in masks.items()}
    rows = np.arange(h)[:, None] * np.ones((1, wd))
    base = soft["r"] * np.where(rows < 40, 3.2, 2.6) - 1.4 * soft["d"] + 1.5 * soft["g"]
    # The detail of each kind (streaks blurred much more down the curtain than across), blended by the kinds'
    # soft masks.
    detail = (soft["w"] * gaussian(water, 0.45, 1.6) + soft["p"] * gaussian(pool, 0.6, 0.6) +
              soft["r"] * gaussian(rock, 0.55, 0.8))
    kinds = {kind: bilinear(gaussian(m, 0.7, 0.7), FALL.ox, FALL.oy) for kind, m in masks.items()}
    return bilinear(base, FALL.ox, FALL.oy), bilinear(detail, FALL.ox, FALL.oy), kinds


def seam_fade(x):
    """1 away from the middle column's sides, 0 on them (the detail fades there, so the pieces tile)."""
    d = min(abs(x - s) for s in SEAMS)
    return min(1.0, d / 1.4) ** 1.5


def fall_whole():
    f = FALL
    base, detail, kinds = fields()

    def z_top(x, y):
        return curtain_z(y) + base(x, y) + detail(x, y) * seam_fade(x)

    painter = Painter("fall", shades={3: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe),
                                      0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa),
                                      2: (1, 2, 3, 4, 5, 6, 7), 0xc: (1, 2, 3, 4, 5)},
                      metallic=0.15, roughness=0.18,
                      glow={0x3b: 0.15, 0x3c: 0.3, 0x3d: 0.45, 0x3e: 0.6},
                      finish={0: (0.05, 0.75), 2: (0.0, 0.6), 0xc: (0.0, 0.55)})
    body = kit.field_slab("fall_body", -36.0, 36.0, -28.0, 28.0, z_top, painter(0x34), step=(0.5, 1.0))
    # Painted by the pixels: the water by its shade smoothed down the curtain (streaks, not pixels), the
    # rocks and leaves by theirs.
    g = f.g
    h, wd = len(g), len(g[0])
    water = np.full((h, wd), np.nan)
    for r in range(h):
        for c in range(wd):
            if g[r][c] >> 4 == 3:
                water[r, c] = g[r][c] & 15
    filled = np.where(np.isnan(water), 0.0, water)
    weight = gaussian(np.where(np.isnan(water), 0.0, 1.0), 0.35, 1.0)
    streak = bilinear(np.where(weight > 0.05, gaussian(filled, 0.35, 1.0) / np.maximum(weight, 1e-3), 3.0), f.ox, f.oy)
    rock_shade = f.shade(0, 1)

    def pick(c, nrm):
        x, y = c.x, c.y
        steep = abs(nrm.z) < 0.5
        if steep:
            x += nrm.x * 0.6
            y += nrm.y * 0.6
        index = f.at(x, y)
        if index is None:
            return painter(0x02)
        ramp = index >> 4
        # The kind by the soft masks (smooth borders between water, rock and leaves, not pixel steps).
        kind = max("wprdg", key=lambda kd: kinds[kd](x, y))
        if steep and kind in ("w", "p"):  # the wet rock walls of the channel
            return painter(0x03)
        if kind in ("w", "p"):
            s = streak(x, y)
            if kind == "p" and ramp == 3:
                s = 0.5 * s + 0.5 * (index & 15)
            s = int(round(s - (1.5 if steep else 0)))
            return painter(0x30 + max(1, min(14, s)))
        if kind == "d":
            return painter(0x01)
        if kind == "r":
            px_shade = (index & 15) if ramp == 0 else rock_shade(x, y)
            s = int(round(0.5 * px_shade + 0.5 * rock_shade(x, y) - 0.6 - (1.5 if steep else 0)))
            return painter(max(1, min(10, s)))
        return painter.shifted(index if ramp in (2, 0xc) else 0x23, -1 if steep else 0)
    w.paint_faces(body, pick)
    kit.merge_flat(body, 0.5)

    # Foam on the pool where the splash is lightest: small glinting bubbles.
    foam = Painter("fall_foam", shades={3: (0xa, 0xc, 0xe)}, metallic=0.1, roughness=0.2,
                   glow={0x3c: 0.3, 0x3e: 0.55})
    rnd = random.Random(7)
    spots = kit.blobs(g, lambda v: v is not None and v >> 4 == 3 and (v & 15) >= 0xa, min_size=1)
    count = 0
    for i, (c, r, size, index) in enumerate(spots):
        if not (36 <= r <= 50):
            continue
        x, y = f.X(c - 0.5), f.Y(r - 0.5)
        if any(abs(x - s) < 1.2 for s in SEAMS):
            continue
        rad = min(1.1, 0.45 + 0.22 * size) * rnd.uniform(0.85, 1.15)
        z = z_top(x, y)
        w.sphere(f"fall_foam{i}", (x, y, z - rad * 0.3), (rad, rad, rad * 0.75), foam(index), 8, 3)
        count += 1

    # Leaves at the pool's corners: clumps of broad leaves over the green pixels.
    leaf = [pal(f"fall_leaf{s:x}", 0x20 + s, metallic=0.0, roughness=0.55) for s in (2, 3, 5, 6)]
    bright = pal("fall_leaf_c3", 0xc3, metallic=0.0, roughness=0.5)
    clumps = [(-34.2, -23.5, 3.0), (-33.0, -16.5, 2.6), (-30.5, -26.0, 2.4), (33.5, -16.0, 3.0), (31.0, -24.5, 3.2),
              (34.6, -25.8, 2.2), (28.2, -27.0, 1.8)]
    for i, (x, y, rad) in enumerate(clumps):
        z = z_top(x, y)
        for j in range(5):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0.2, 0.8) * rad
            lx, ly = x + d * math.cos(a), y + d * math.sin(a)
            lx = max(-35.6, min(35.6, lx))
            ly = max(-27.6, ly)
            mat = leaf[min(3, max(0, int(rnd.uniform(0, 4))))] if j else bright
            obj = w.sphere(f"fall_leaf{i}_{j}", (lx, ly, z + 0.6), (rad * 0.55, rad * 0.32, 0.55), mat, 8, 4)
            centre = (lx, ly, z + 0.6)
            obj.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(a, 4, "Z") @
                               Matrix.Translation(tuple(-v for v in centre)))


kit.PROTECT.append("fall_body")
kit.pieced("torm_fall", fall_whole, (72, 56),
           kit.grid_pieces("torm_fall_", FALL, ["tl", "tm", "tr", "bl", "bm", "br"], 3, 2))


if __name__ == "__main__":
    kit.run()
