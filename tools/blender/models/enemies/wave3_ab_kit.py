"""Helpers once of the batch AB models of wave 3 (sheet 4: TYRIAN, TYRIAN X, HOLES and ASSASSIN), whose models are all
polish_*.py now (the tusked boss, its small copy and the two long arms: polish_tusk_boss*.py, polish_tusk_arms.py);
kept for wave3_ai_gryphon.py and wave3_ai_kit.py, which use its fields over a sprite's pixels, outlines, painting
and wall sharpening, built on the pixel frames, sprite painting and shapes of batch S (wave3_s_kit), the limbs and
lofts of batch Y (wave3_y_kit), the parts of batch J (wave3_j_kit) and the heightfields of batch Q (wave3_q_kit).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_y_kit as y  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, lathe_axis, tube, catmull, sphere,  # noqa: E402,F401
                         rounded_box, meshes, bake, triangles, simplify_bottom, decimate, sampler)
from wave3_s_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, slab, mirror_copies,  # noqa: E402,F401
                         smoothstep)
from wave3_y_kit import loft_path, resample, loft_y, smooth_sections, interp  # noqa: E402,F401

def lowpass(poly, sigma=1.0, spacing=0.4):
    """A closed outline resampled every `spacing` and smoothed with a Gaussian of `sigma` pixels along it: the
    pixels' staircases (which shade as streaks on the walls) are ironed out, corners rounded a little."""
    pts = np.array(poly + poly[:1], dtype=float)
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    total = seg.sum()
    count = max(8, int(total / spacing))
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    ts = np.linspace(0.0, total, count, endpoint=False)
    xs = np.interp(ts, cum, pts[:, 0])
    ys = np.interp(ts, cum, pts[:, 1])
    half = int(math.ceil(3 * sigma / spacing))
    offs = np.arange(-half, half + 1)
    wts = np.exp(-0.5 * (offs * spacing / sigma) ** 2)
    wts /= wts.sum()
    sx = sum(wt * np.roll(xs, -o) for o, wt in zip(offs, wts))
    sy = sum(wt * np.roll(ys, -o) for o, wt in zip(offs, wts))
    return [(float(a), float(b)) for a, b in zip(sx, sy)]


def polys_of(fr, keep, smooth=2, epsilon=0.4, min_area=0.5, grow=0.0, sigma=0.0):
    """The outlines of the frame's pixels keep(index, column, row) accepts (model coordinates); sigma > 0
    smooths them (lowpass)."""
    rows = regions(fr.g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    polys = sh.outlines(rows, "#", (fr.ox, fr.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)
    if sigma:
        polys = [lowpass(p, sigma) for p in polys]
    if grow:
        polys = [sh.inset(p, -grow) for p in polys]
    return polys


# --- Fields over the pixels ------------------------------------------------------------------------

def field(fr, value, blur=1):
    """A function (x, y) -> value(index, column, row) over the frame's pixels (None: no value there),
    blurred `blur` times and bilinear between pixel centres; elsewhere the nearest pixel's value."""
    h, wd = len(fr.g), fr.width
    data = np.full((h, wd), np.nan)
    for r in range(h):
        for c in range(wd):
            v = fr.g[r][c]
            if v is None:
                continue
            got = value(v, c, r)
            if got is not None:
                data[r, c] = got
    for _ in range(blur):
        out = data.copy()
        for r in range(h):
            for c in range(wd):
                if np.isnan(data[r, c]):
                    continue
                vals, wts = [], []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < wd and not np.isnan(data[rr, cc]):
                            vals.append(data[rr, cc])
                            wts.append(2.0 if dr == dc == 0 else 1.0 if dr == 0 or dc == 0 else 0.5)
                out[r, c] = np.average(vals, weights=wts)
        data = out
    known = np.argwhere(~np.isnan(data)).astype(float)

    def at(x, yy):
        c, r = x + fr.ox - 0.5, fr.oy - yy - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        total = weight = 0.0
        for rr, cc, wt in ((r0, c0, (1 - (r - r0)) * (1 - (c - c0))), (r0, c0 + 1, (1 - (r - r0)) * (c - c0)),
                           (r0 + 1, c0, (r - r0) * (1 - (c - c0))), (r0 + 1, c0 + 1, (r - r0) * (c - c0))):
            if 0 <= rr < h and 0 <= cc < wd and not np.isnan(data[rr, cc]):
                total += data[rr, cc] * wt
                weight += wt
        if weight > 0.05:
            return total / weight
        if not len(known):
            return 0.0
        i = int(np.argmin((known[:, 0] - r) ** 2 + (known[:, 1] - c) ** 2))
        return float(data[int(known[i, 0]), int(known[i, 1])])
    return at


def brightness(index):
    """A palette index's brightness (0-1), as the sprite shades it."""
    r, g, b = k.level_palette()[index]
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255.0


# --- Painting ---------------------------------------------------------------------------------------------

def paint(obj, fr, painter, wall_steps=2, wall_blur=2, under=None, wall_z=0.45, inset=0.7, top_blur=0):
    """Gives each face the colour of the sprite's pixel under its centre (painter: index -> material), as
    wave3_s_kit.paint_sprite; walls (steeper than wall_z) take the smoothed shade of the pixel's ramp a little
    inside them (`inset` against their normal: a wall's centre lies on the outline), `wall_steps` darker, so
    that the sides of the plates are even rather than striped by the pixels at the edge; faces looking down
    take `under`. top_blur > 0 gives the other faces the shade of their pixel's ramp smoothed that many times
    (smooth gradients on round parts rather than the pixels' blocks)."""
    def pick(c, nrm):
        if nrm.z < -0.5:
            return under
        if abs(nrm.z) >= wall_z:
            index = fr.at(c.x, c.y)
            if index is None or not top_blur:
                return None if index is None else painter(index)
            ramp = index >> 4
            shade = int(round(fr.shade(ramp, top_blur)(c.x, c.y)))
            return painter(ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade)))
        flat = math.hypot(nrm.x, nrm.y) or 1.0
        x, yy = c.x - nrm.x / flat * inset, c.y - nrm.y / flat * inset
        index = fr.at(x, yy)
        if index is None:
            index = fr.at(c.x, c.y)
        if index is None:
            return under
        ramp = index >> 4
        shade = int(round(fr.shade(ramp, wall_blur)(x, yy))) - wall_steps
        return painter(ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade)))
    return paint_faces(obj, pick)


def sharpen_walls(obj, wall_nz=0.03, angle=45):
    """Marks the edges where a part's straight sides meet its top as sharp (and smooths the rest by angle), so
    that the sides shade evenly instead of in streaks where some of their top edges were smoothed and some
    not."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        a, b = (abs(f.normal.z) < wall_nz for f in e.link_faces)
        if a != b:
            e.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return k.smooth(obj, angle)
