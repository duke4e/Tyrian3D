"""Helpers for the batch Q models of wave 3 (sheet A: wave3_q.py, the fire gates' housings, the small
hinged pod and the MISSILE SHIPS sign; wave3_q_mace.py, the mace, its chain and anchor, and the skull
chest; wave3_q_bronze.py, SOH JIN's bronze pieces): the sprites' pixels (wave3_q_art.py), the part
builders of batches J and O (wave3_j_kit, wave3_o_kit: palette materials, turned parts, tubes, painting
faces, cutting a whole object into its sprites' pieces, the build loop), and a few of its own: parts
whose top is a height function over an outline, ribs and grooves that follow a surface, and the half
dome of the gates' housings.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre. Pixel (column c, row r) of an art with origin (ox, oy) covers
x = c - ox .. c + 1 - ox, y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_o_kit as o  # noqa: E402,F401
import wave3_q_art as art  # noqa: E402,F401
from wave3_j_kit import (bake, block, catmull, grid, hoop, lathe_axis, meshes, outlines, paint_faces, pal,  # noqa: E402,F401
                         part, regions, rounded_box, sampler, sphere, transform, triangles, tube)
from wave3_o_kit import cut, merge, mirror_x, mirror_y, move, paint_bands, smoothstep, budget, decimate  # noqa: E402,F401

A = "enemy_A"


def model(name, sprites, size=(24, 28)):
    """Registers a builder (wave3_j_kit.model); sprites: sheet A sprites [(sprite, large)]."""
    return w.model(name, [(A, s, large) for s, large in sprites], size)


whole = w.whole
run = w.run


# --- Pixels --------------------------------------------------------------------------------------

def at(g, c, r):
    if 0 <= r < len(g) and 0 <= c < len(g[r]):
        return g[r][c]
    return None


def shades(g, origin, keep, blur=1):
    """(x, y) -> the shade (0-15) of the pixels keep(index) accepts, bilinear and blurred."""
    return sampler(g, origin, value=lambda v: v & 15, blur=blur, keep=lambda v: v is not None and keep(v))


def pixel_polys(g, keep, origin, smooth=2, epsilon=0.4, min_area=0.5):
    """The outlines of the pixels keep(index, column, row) accepts."""
    rows = regions(g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    return sh.outlines(rows, "#", origin, smooth=smooth, epsilon=epsilon, min_area=min_area)


def clamp_poly(poly, x_max=None, x_min=None):
    """The polygon with its x clamped (a flat side), consecutive duplicates dropped."""
    out = []
    for x, y in poly:
        if x_max is not None:
            x = min(x, x_max)
        if x_min is not None:
            x = max(x, x_min)
        if not out or abs(out[-1][0] - x) > 1e-4 or abs(out[-1][1] - y) > 1e-4:
            out.append((x, y))
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-4 and abs(out[0][1] - out[-1][1]) < 1e-4:
        out.pop()
    return out


# --- Parts ---------------------------------------------------------------------------------------

def heightfield(name, polys, z_of, mat=None, spacing=0.5, smooth_angle=50, edge=None):
    """A closed part filling the polygons, its top at z_of(x, y), its bottom flat at z = 0 (sides
    straight down from the top's outline). With `edge` (pixels), z_of(x, y, e) also gets e, 0 on the
    outline rising to 1 `edge` inside it (for rounded edges)."""
    if edge:
        rounding = lambda d, wd: np.sqrt(np.clip(d / edge, 0.0, 1.0) * (2.0 - np.clip(d / edge, 0.0, 1.0)))
        obj = sh.inflate(name, polys, mat, profile=rounding, bottom=0.0, base=0.0, rim=0.0, spacing=spacing,
                         z_fn=z_of, sigma=1.0)
    else:
        obj = sh.inflate(name, polys, mat, profile=lambda d, wd: 0.0 * d, bottom=0.0, base=0.0, rim=0.0,
                         spacing=spacing, z_fn=lambda x, y, z: z_of(x, y), sigma=1.0)
    return k.smooth(obj, smooth_angle)


def torus(name, centre, major, minor, mat, segments=40, sides=12, squash=1.0, scale_y=1.0):
    """A ring lying flat round a vertical axis (a chain link, a collar): `major` to its tube's middle,
    the tube `minor` thick (its height scaled by squash)."""
    section = [(major + minor * math.cos(2 * math.pi * i / sides), minor * squash * math.sin(2 * math.pi * i / sides))
               for i in range(sides)]
    return hoop(name, centre, section, mat, segments, smooth_angle=60, scale_y=scale_y)


def cone(name, start, direction, length, base, mat, tip=0.12, segments=16, collar=None):
    """A spike from `start` along `direction`: `base` radius at its foot tapering to a point."""
    profile = [(0.0, base * 1.02), (0.12 * length, base), (0.55 * length, base * 0.55), (0.92 * length, base * 0.14),
               (length, tip * 0.5)]
    return lathe_axis(name, profile, mat, start, direction, segments, smooth_angle=55)


def rib(name, x0, x1, y0, y1, surface, lift, mat, step=0.5, sink=0.8, round_ends=0.8, columns=7):
    """A rib along y (y0 < y1) from x0 to x1 standing `lift` above surface(x, y) (its top rounded across),
    sunk `sink` into it; its ends round off over `round_ends`."""
    rings = []
    count = max(2, int(math.ceil((y1 - y0) / step)))
    for i in range(count + 1):
        y = y0 + (y1 - y0) * i / count
        end = min(y - y0, y1 - y) / max(round_ends, 1e-3)
        f = math.sqrt(max(0.0, min(1.0, end) * (2 - min(1.0, end))))  # a quarter circle
        f = 0.25 + 0.75 * f
        cx, hw = (x0 + x1) / 2, (x1 - x0) / 2 * (0.6 + 0.4 * f)
        pts = []
        for j in range(columns):  # the top, right to left
            t = 1 - 2 * j / (columns - 1)
            x = cx + t * hw
            pts.append(Vector((x, y, surface(x, y) + lift * f * math.sqrt(max(0.0, 1 - t ** 4)))))
        for j in range(columns):  # the bottom, left to right
            t = -1 + 2 * j / (columns - 1)
            x = cx + t * hw
            pts.append(Vector((x, y, surface(x, y) - sink)))
        rings.append(pts)
    obj = k.loft(name, rings, mat)
    return k.smooth(obj, 50)


def groove(name, points2d, surface, mat, radius=0.45, sink=0.15, step=0.4):
    """A dark seam along a smooth path over a surface: a thin tube through the points (x, y), sunk into
    surface(x, y) so that a narrow line shows."""
    path = catmull([(x, y, 0.0) for x, y in points2d], step)
    pts = [(p.x, p.y, surface(p.x, p.y) - sink) for p in path]
    return tube(name, pts, radius, mat, 10, squash=0.7)


# --- The half dome -------------------------------------------------------------------------------

class HalfDome:
    """The shell of the fire gates' housings: a dome over a superellipse (power p) centred on its flat
    side x = xf, lying at x < xf (rx across, ry along y), `height` high at the flat side's middle; its
    cross-sections fall as (1 - r^q)^e."""

    def __init__(self, xf, yc, rx, ry, height, p=2.5, q=2.4, e=0.55, rim=0.35):
        self.xf, self.yc, self.rx, self.ry, self.height = xf, yc, rx, ry, height
        self.p, self.q, self.e, self.rim = p, q, e, rim

    def r(self, x, y):
        u = max(self.xf - x, 0.0) / self.rx
        v = abs(y - self.yc) / self.ry
        return (u ** self.p + v ** self.p) ** (1.0 / self.p)

    def __call__(self, x, y):
        r = min(self.r(x, y), 1.0)
        return self.rim + self.height * max(0.0, 1.0 - r ** self.q) ** self.e


def ellipse_dent(x, y, cx, cy, rx, ry, depth, soft=0.35):
    """How much an elliptical dent (centre, radii) lowers a surface at (x, y): `depth` inside, easing
    out over the last `soft` of its radius."""
    r = math.hypot((x - cx) / rx, (y - cy) / ry)
    return depth * smoothstep(1.0, 1.0 - soft, r)
