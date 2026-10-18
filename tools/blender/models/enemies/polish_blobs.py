"""Three red enemies, polished (2026-10-19; they replace later_episodes.py's blobs() and wave3_l.py's
ember()): the big blob of BRAINIAC and NOSE DRIP, the molten drops of STARGATE and BRAINIAC's ember.

- blob_big: sheet 5 sprite 121 (2x2; BRAINIAC and NOSE DRIP on the ground and in the sky, DREAD-NOT and
  NOSE DRIP on the top layer, UNDERDELI; about 95 of them), its animation 121 123 125 123, three game
  frames each. As the sprite and its 4x upscale draw it: a dark red fleshy blob (ramp 7, shades 0-5)
  whose middle is a glossy whorl like an eye: a raised knob on the upper left with an orange-yellow
  glint (columns 7-8, rows 7-9 of 121), a dark groove curling round it from above, down its right side
  and under it, a ridge outside that, a second groove and ridge outside those on the right and the lower
  right, the lower left lit, a short stem with two small nubs on top, the edge dark. Its frames pulse:
  121 is wide (columns 1-22, rows 2-23), 123 and 125 narrower and taller (125: columns 3-20, rows 0-25),
  the coils squeezed together and the groove under the knob opening into a dark hollow. A model per
  frame (models.cfg: sprite 5 121 blob_big yaw=0, frame 5 123 blob_big_123, frame 5 125 blob_big_125),
  each drawn after its sprite: the outline (its distance from the middle every 10 degrees), the knob,
  the glint and the grooves and ridges as curves through the sprite's pixels. The grooves are carved,
  the knob and the ridges raised; the shades are the sprite's, from bands of a shade field cut along
  their contours, glowing a little in their own colour (the dark red reads black in the game's slanted
  light otherwise), the glint more. All three are equally high.

- drops: sheet E sprite 277 (2x2; STARGATE on the ground (about 110) and in the sky, ** ALE ** on the
  top layer), its animation 277 279 281 283, two game frames each: three molten drops round the
  sprite's middle, their triangle turned 30 degrees clockwise every frame while each drop stays
  upright. Each drop (9 x 12 pixels) is drawn the same: a round head with a white-hot core on its upper
  left (palette 0x1f) in rings of yellow, orange and red, narrowing to a blunt tip below, a bright streak
  running down its right side into the tip, a dark gap between that and the core. A model per
  arrangement (models.cfg: sprite e 277 drops yaw=0 glow=26:0.3:121, frame e 279 drops_279, frame e 281
  drops_281, frame e 283 drops_283), the same drop at the sprite's places: a glossy drop lying on the
  ground (its underside flat), the core and the streak glowing; an orange glow (palette 121) round the
  three, which turn about the sprite's middle.

- ember: sheet 5 sprite 76 (1x1; BRAINIAC on the ground and the top layer, GRAVITRON; about 90): a
  lumpy ember (columns 1-9, rows 2-10) with four short spikes (up, down, left and right), white-hot
  (0x1f) above its middle with glowing cracks running from there to its left, up into the top spike and
  to its upper right, a dark crust across its middle, a dark pit and warm spots below. The model is a
  crusted lump with the spikes grown out of it at mid-height, the cracks carved into it and glowing
  (models.cfg: sprite 5 76 ember yaw=0 glow=12:0.25).

Origin at the sprite's centre (2x2: pixel 12, 14; 1x1: pixel 6, 7); +Y up the screen, +Z towards the
camera; the models stand on z = 0.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette of each model against its sprite), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_balls import preview, triangles  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402


# --- Fields over the top view (numpy, a value per point) ------------------------------------------

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def spot(xy, centre, radii, power=2.0):
    """A soft spot: 1 at its centre, falling off over radii (x, y)."""
    u = np.abs(xy[:, 0] - centre[0]) / radii[0]
    v = np.abs(xy[:, 1] - centre[1]) / radii[1]
    return np.exp(-(u ** power + v ** power))


def catmull_rom(points, samples=8):
    """A smooth open curve through the points (rows whose first two values are x, y; the others are
    interpolated along), each span in `samples` steps."""
    pts = [np.array(p, float) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for s in range(samples):
            t = s / samples
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return np.array(out)


class Line:
    """A groove, ridge, crack or streak: a smooth curve through (x, y, half-width, strength) points;
    its field is the strength times a Gaussian of the distance to the curve over the half-width, both
    interpolated along it (a strength of 0 at the ends fades it out)."""

    def __init__(self, points):
        self.curve = catmull_rom(points)

    def field(self, xy):
        a, b = self.curve[:-1, :2], self.curve[1:, :2]
        ab = b - a
        out = np.empty(len(xy))
        for lo in range(0, len(xy), 4096):
            p = xy[lo:lo + 4096]
            ap = p[:, None, :] - a[None]
            t = np.clip((ap * ab[None]).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-9)[None], 0.0, 1.0)
            d = np.linalg.norm(ap - t[..., None] * ab[None], axis=-1)
            j = d.argmin(1)
            rows = np.arange(len(p))
            tt = t[rows, j]
            width = self.curve[j, 2] * (1 - tt) + self.curve[j + 1, 2] * tt
            strength = self.curve[j, 3] * (1 - tt) + self.curve[j + 1, 3] * tt
            out[lo:lo + 4096] = strength * np.exp(-(d[rows, j] / width) ** 2)
        return out


def lines(xy, items):
    """The sum of several lines' fields: items [(Line, scale)]."""
    total = np.zeros(len(xy))
    for line, scale in items:
        total += scale * line.field(xy)
    return total


def lumps(p, scale, seed):
    """Organic swelling: smooth noise over the surface's points (about -1..1)."""
    offset = Vector((seed * 3.1, seed * 7.7, seed * 1.3))
    return np.array([noise.noise(Vector(q) * scale + offset) for q in p])


# --- Shapes: the unit sphere's directions mapped onto a body ---------------------------------------

def unit(v):
    return v / np.linalg.norm(v, axis=1, keepdims=True)


class Shape:
    def points(self, d):
        raise NotImplementedError

    def normals(self, d, eps=1e-3):
        """Outward normals, from the mapped surface's tangents."""
        up = np.where(np.abs(d[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
        t1 = unit(np.cross(d, up))
        t2 = np.cross(d, t1)
        g1 = self.points(unit(d + eps * t1)) - self.points(unit(d - eps * t1))
        g2 = self.points(unit(d + eps * t2)) - self.points(unit(d - eps * t2))
        n = unit(np.cross(g1, g2))
        inward = (n * (self.points(d) - self.inside(d))).sum(1) < 0
        n[inward] *= -1
        return n


class Star(Shape):
    """A body whose top view is a closed outline given as its distance from the middle every
    360 / len(radii) degrees counter-clockwise from +X (a periodic cubic between them), `top` high
    above the outline's plane (z = bottom) and `bottom` below it, standing on z = 0."""

    def __init__(self, middle, radii, top, bottom):
        self.middle = np.array([middle[0], middle[1], bottom], float)
        self.radii = np.array(radii, float)
        self.top, self.bottom = top, bottom

    def radius(self, a):
        n = len(self.radii)
        u = (a / (2 * math.pi) * n) % n
        i = np.floor(u).astype(int)
        f = u - i
        r = self.radii
        p0, p1, p2, p3 = r[(i - 1) % n], r[i % n], r[(i + 1) % n], r[(i + 2) % n]
        return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f +
                      (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)

    def points(self, d):
        r = self.radius(np.arctan2(d[:, 1], d[:, 0]))
        h = np.where(d[:, 2] > 0, self.top, self.bottom)
        return self.middle + np.stack([d[:, 0] * r, d[:, 1] * r, d[:, 2] * h], 1)

    def inside(self, d):
        return np.broadcast_to(self.middle, d.shape)


class Drop(Shape):
    """A drop lying along Y on the ground, its head up the screen: the top view's half-width is a circle's
    of head_radius round the head's middle (y = head_y) and narrows below it to the tip (y = tip_y) as
    head_radius * (1 - u^a)^b (taper (a, b); u: 0 at the head's middle, 1 at the tip); each cross-section
    is an ellipse as wide and `above` / `below` times as high above and below its axis, which sinks with
    the width so the underside lies on z = 0."""

    def __init__(self, head_y, head_radius, tip_y, taper=(1.6, 0.5), above=0.85, below=0.55):
        self.head_y, self.head_radius, self.tip_y = head_y, head_radius, tip_y
        self.taper, self.above, self.below = taper, above, below

    def width(self, s):
        r = self.head_radius
        upper = np.sqrt(np.clip(r * r - (s - self.head_y) ** 2, 0.0, None))
        u = np.clip((self.head_y - s) / (self.head_y - self.tip_y), 0.0, 1.0)
        lower = r * (1 - u ** self.taper[0]) ** self.taper[1]
        return np.where(s >= self.head_y, upper, lower)

    def points(self, d):
        top, tip = self.head_y + self.head_radius, self.tip_y
        s = tip + (top - tip) * (d[:, 1] + 1) / 2
        rho = self.width(s)
        ring = np.sqrt(np.clip(1 - d[:, 1] ** 2, 1e-12, None))
        c, z = d[:, 0] / ring, d[:, 2] / ring
        h = np.where(z > 0, self.above, self.below)
        return np.stack([rho * c, s, rho * (self.below + z * h)], 1)

    def inside(self, d):
        top, tip = self.head_y + self.head_radius, self.tip_y
        s = tip + (top - tip) * (d[:, 1] + 1) / 2
        rho = self.width(s)
        return np.stack([np.zeros(len(d)), s, rho * self.below], 1)


# --- Painted bodies ----------------------------------------------------------------------------------

def painted(name, shape, shade, bands, relief=None, subdivisions=5, refine=None, smooth_angle=70):
    """A body of `shape` (an icosphere mapped onto it) whose faces take the material of their band of
    shade(points, normals) (bands: [(lowest shade, material)] ascending), the faces cut along the
    bands' borders so colours meet along smooth contours; relief(points, normals) moves the points
    out along their normals (pixels). refine: tests of the directions (unit vectors), each making the
    sphere twice as fine where it holds (where the game's camera sees the details), in turn."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for test in refine or ():
        fine = {v for v in bm.verts if test(Vector(v.co).normalized())}
        bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if all(v in fine for v in e.verts)], cuts=1,
                                  use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for v in bm.verts:
            v.co = Vector(v.co).normalized()
    verts = list(bm.verts)
    d = unit(np.array([v.co[:] for v in verts]))
    values = dict(zip(verts, shade(shape.points(d), shape.normals(d)).tolist()))
    borders = [lowest for lowest, _ in bands[1:]]
    for t in borders:
        split_along(bm, values, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = []
    for f in bm.faces:
        mean = sum(values[v] for v in f.verts) / len(f.verts)
        kinds.append(sum(mean > t for t in borders))
    verts = list(bm.verts)
    d = unit(np.array([v.co[:] for v in verts]))
    p, n = shape.points(d), shape.normals(d)
    if relief is not None:
        p = p + n * relief(p, n)[:, None]
    for v, q in zip(verts, p.tolist()):
        v.co = q
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    used = sorted(set(kinds))
    for i in used:
        mesh.materials.append(bands[i][1])
    for poly, kind in zip(mesh.polygons, kinds):
        poly.material_index = used.index(kind)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def band_materials(prefix, levels, roughness):
    """[(lowest shade, palette index, emission strength in the palette colour)] -> bands."""
    pal = k.level_palette()
    return [(lowest, k.material(f"{prefix}_{index:02x}", palette=index, metallic=0.0, roughness=roughness(index),
                                emission=pal[index] if glow > 0 else None, emission_strength=glow))
            for lowest, index, glow in levels]


# --- blob_big (5 121, 123, 125) ---------------------------------------------------------------------

BLOB_MIDDLE = (0.0, 1.0)      # the outlines' middle (the sprites' columns 1-22 of 121, 3-20 of 125)
BLOB_TOP, BLOB_BOTTOM = 7.6, 3.2

# The sprite's light on the blob: from the left (the lit lower left), fading out towards the dark edge
# (where the normal's z drops below RIM).
BLOB_LIGHT = np.array([-0.72, -0.1, 0.69])
RIM = (0.06, 0.6)

# The shades: ramp 7, 0x70 (the edge) to 0x7c (the glint's core); each band glows a little in its colour.
BLOB_BANDS = [(-99.0, 0x70, 0.12), (0.5, 0x71, 0.13), (1.5, 0x72, 0.14), (2.5, 0x73, 0.16), (3.5, 0x74, 0.18),
              (4.5, 0x75, 0.2), (5.5, 0x76, 0.28), (6.5, 0x77, 0.45), (7.5, 0x78, 0.7), (8.5, 0x79, 0.95),
              (9.8, 0x7a, 1.1), (10.8, 0x7b, 1.3), (11.6, 0x7c, 1.5)]

# The frames: the outline (from the middle every 10 degrees), the stem and the nubs on top ((x, half-width,
# how far out)), the knob ((x, y), radii), the glint ((x, y), half-sizes), the grooves and ridges
# ((x, y, half-width, strength) through the sprite's pixels), the hollow under the knob ((x, y), radii,
# depth) and a small swelling in it.
BLOB_FRAMES = [
    dict(name="blob_big", sprite=121,
         outline=(10.53, 10.86, 10.74, 10.51, 10.37, 10.33, 10.19, 9.97, 9.99, 10.03, 9.88, 9.87, 10.16, 10.33,
                  10.37, 10.51, 10.74, 10.99, 11.08, 11.17, 11.32, 11.47, 11.64, 11.80, 11.87, 11.65, 11.00,
                  10.07, 9.29, 8.82, 8.42, 8.16, 8.16, 8.42, 9.04, 9.84),
         stem=[(0.5, 2.2, 1.0), (-3.4, 0.8, 0.8), (4.5, 0.8, 0.8)],
         knob=((-4.4, 5.0), (3.4, 2.8)), glint=((-3.8, 5.4), (1.45, 1.1)),
         groove=[(0.0, 6.9, 0.45, 0.0), (0.0, 6.5, 0.6, 0.7), (1.1, 5.4, 0.7, 1.0), (1.3, 3.6, 0.75, 1.0),
                 (0.6, 2.0, 0.75, 1.1), (-1.0, 1.3, 0.75, 1.1), (-3.0, 1.2, 0.7, 0.8), (-4.8, 1.3, 0.5, 0.0)],
         ridge=[(1.4, 7.8, 0.5, 0.0), (1.6, 7.4, 0.6, 0.6), (2.8, 6.4, 0.8, 1.0), (3.1, 5.0, 0.8, 1.0),
                (3.2, 3.5, 0.8, 1.0), (2.8, 2.0, 0.8, 1.0), (1.6, 0.6, 0.8, 1.0), (0.4, -0.6, 0.8, 0.8),
                (-1.2, -1.6, 0.8, 0.0)],
         groove2=[(4.3, 8.9, 0.4, 0.0), (4.6, 8.3, 0.45, 0.5), (5.3, 7.0, 0.55, 0.9), (5.5, 5.5, 0.6, 1.0),
                  (5.8, 3.5, 0.65, 0.9), (5.6, 1.5, 0.6, 0.9), (5.4, -0.5, 0.6, 1.0), (4.5, -1.6, 0.6, 1.0),
                  (3.4, -2.6, 0.6, 1.0), (2.3, -3.6, 0.6, 1.0), (0.9, -4.6, 0.6, 0.8), (-0.6, -5.4, 0.5, 0.3),
                  (-1.6, -5.8, 0.4, 0.0)],
         ridge2=[(6.0, 7.2, 0.45, 0.0), (6.4, 6.3, 0.5, 0.6), (6.8, 5.0, 0.6, 0.8), (7.2, 3.5, 0.65, 1.0),
                 (7.3, 1.5, 0.65, 1.0), (7.0, -0.5, 0.65, 1.0), (6.5, -1.5, 0.6, 1.0), (5.5, -2.6, 0.6, 1.0),
                 (4.4, -3.6, 0.6, 0.9), (3.0, -4.5, 0.5, 0.6), (2.0, -5.0, 0.4, 0.0)],
         hollow=None, swelling=None),
    dict(name="blob_big_123", sprite=123,
         outline=(9.56, 9.45, 9.36, 9.38, 9.44, 9.77, 10.31, 10.49, 10.23, 10.07, 10.21, 10.41, 10.41, 10.13,
                  9.64, 9.41, 9.68, 9.99, 10.03, 9.88, 9.75, 9.92, 10.35, 11.03, 11.93, 12.43, 12.03, 11.04,
                  9.80, 8.55, 7.80, 7.56, 7.56, 7.93, 8.59, 9.25),
         stem=[(0.0, 1.9, 1.7), (-3.5, 0.6, 1.0), (3.5, 0.6, 1.0)],
         knob=((-4.0, 5.9), (3.0, 2.6)), glint=((-3.7, 6.5), (1.4, 1.1)),
         groove=[(-0.8, 8.0, 0.4, 0.0), (-0.6, 7.6, 0.55, 0.6), (0.4, 6.5, 0.65, 1.0), (0.6, 4.5, 0.7, 1.0),
                 (0.4, 3.0, 0.7, 1.0), (-0.3, 1.6, 0.7, 1.1), (-0.7, 0.4, 0.65, 1.1), (-2.0, -0.5, 0.6, 1.0),
                 (-3.3, 0.2, 0.6, 0.9), (-3.4, 1.4, 0.5, 0.5), (-3.0, 2.0, 0.4, 0.0)],
         ridge=[(0.4, 8.9, 0.45, 0.0), (0.6, 8.5, 0.55, 0.6), (2.0, 7.4, 0.7, 1.0), (2.5, 6.0, 0.75, 1.0),
                (2.6, 4.0, 0.75, 1.0), (2.8, 2.6, 0.75, 1.0), (2.0, 1.4, 0.75, 1.0), (1.4, -0.2, 0.75, 1.0),
                (0.4, -1.5, 0.75, 0.8), (-1.0, -2.0, 0.7, 0.0)],
         groove2=[(4.6, 8.8, 0.4, 0.0), (4.6, 8.3, 0.45, 0.5), (4.6, 6.5, 0.55, 1.0), (4.8, 4.5, 0.6, 0.9),
                  (4.8, 2.5, 0.6, 0.9), (4.6, 0.5, 0.6, 0.9), (4.4, -1.5, 0.6, 1.0), (3.5, -2.6, 0.6, 1.0),
                  (2.5, -3.6, 0.6, 1.0), (1.5, -4.6, 0.6, 0.9), (0.4, -5.5, 0.5, 0.4), (-0.6, -6.0, 0.4, 0.0)],
         ridge2=[(5.5, 6.8, 0.45, 0.0), (5.8, 6.0, 0.5, 0.6), (6.5, 4.5, 0.6, 0.8), (6.6, 2.5, 0.65, 1.0),
                 (6.5, 0.5, 0.65, 1.0), (6.1, -1.0, 0.6, 1.0), (5.5, -2.5, 0.6, 1.0), (4.5, -3.6, 0.6, 0.9),
                 (3.5, -4.5, 0.55, 0.8), (2.2, -5.4, 0.45, 0.4), (1.2, -5.9, 0.4, 0.0)],
         hollow=((-2.6, 0.6), (1.3, 0.9), 0.6), swelling=((-1.6, 0.5), (0.7, 0.6))),
    dict(name="blob_big_125", sprite=125,
         outline=(8.81, 8.91, 8.81, 8.99, 9.23, 9.54, 10.22, 10.97, 11.17, 11.08, 11.17, 11.10, 10.49, 9.67,
                  9.23, 9.26, 9.35, 9.20, 9.06, 9.04, 9.04, 9.22, 9.64, 10.54, 12.00, 13.15, 13.02, 11.79,
                  10.18, 8.81, 7.93, 7.56, 7.56, 7.80, 8.09, 8.39),
         stem=[(-0.5, 1.6, 2.2), (-3.5, 0.6, 1.1), (2.5, 0.6, 1.1)],
         knob=((-3.6, 7.0), (2.6, 2.6)), glint=((-3.9, 7.5), (1.35, 1.1)),
         groove=[(-0.6, 9.1, 0.4, 0.0), (-0.5, 8.6, 0.5, 0.7), (-0.1, 7.0, 0.6, 0.9), (0.0, 5.0, 0.65, 0.9),
                 (0.0, 3.6, 0.65, 1.0), (-0.6, 2.3, 0.7, 1.1), (-2.0, 1.8, 0.75, 1.1), (-3.5, 1.4, 0.7, 1.0),
                 (-3.8, 0.5, 0.6, 0.8), (-3.4, -0.3, 0.45, 0.0)],
         ridge=[(0.9, 9.0, 0.45, 0.0), (1.0, 8.6, 0.55, 0.6), (1.5, 7.0, 0.65, 1.0), (1.6, 5.0, 0.7, 1.0),
                (2.0, 3.0, 0.7, 0.9), (2.0, 0.5, 0.7, 0.9), (1.6, -1.0, 0.7, 0.9), (0.6, -2.5, 0.7, 0.8),
                (-0.8, -3.2, 0.65, 0.0)],
         groove2=[(4.1, 9.1, 0.4, 0.0), (4.0, 8.6, 0.45, 0.6), (3.6, 7.0, 0.55, 1.0), (4.0, 5.0, 0.55, 0.9),
                  (4.0, 1.0, 0.55, 0.9), (3.6, -1.0, 0.55, 1.0), (3.0, -2.5, 0.55, 1.0), (2.5, -3.6, 0.55, 1.0),
                  (1.5, -4.6, 0.55, 0.9), (0.8, -5.5, 0.5, 0.5), (0.0, -6.2, 0.4, 0.0)],
         ridge2=[(5.0, 7.4, 0.45, 0.0), (5.2, 6.5, 0.5, 0.7), (5.5, 4.5, 0.55, 1.0), (5.5, 0.0, 0.55, 1.0),
                 (5.4, -1.5, 0.55, 1.0), (5.0, -2.6, 0.55, 1.0), (4.5, -3.6, 0.55, 0.9), (3.5, -4.6, 0.5, 0.8),
                 (2.5, -5.5, 0.45, 0.4), (1.6, -6.0, 0.4, 0.0)],
         hollow=((-2.5, 1.9), (1.9, 1.0), 1.0), swelling=((-1.0, -0.1), (0.8, 0.8))),
]


def blob(frame):
    shape = Star(BLOB_MIDDLE, frame["outline"], BLOB_TOP, BLOB_BOTTOM)
    grooves = [(Line(frame["groove"]), 1.0), (Line(frame["groove2"]), 0.95)]
    ridges = [(Line(frame["ridge"]), 1.0), (Line(frame["ridge2"]), 1.0)]
    knob_at, knob_size = frame["knob"]
    glint_at, glint_size = frame["glint"]
    seen = lambda n: smoothstep(0.15, 0.5, n[:, 2])  # noqa: E731  the relief fades out down the sides

    def hollow(xy):
        if frame["hollow"] is None:
            return np.zeros(len(xy)), np.zeros(len(xy))
        (at, size, depth), (sw_at, sw_size) = frame["hollow"], frame["swelling"]
        return depth * spot(xy, at, size, 2.4), spot(xy, sw_at, sw_size)

    def shade(p, n):
        xy = p[:, :2]
        lit = np.clip(n @ (BLOB_LIGHT / np.linalg.norm(BLOB_LIGHT)), -1.0, 1.0)
        rim = smoothstep(RIM[0], RIM[1], n[:, 2])
        hole, swell = hollow(xy)
        value = 0.3 + rim * (1.9 + 2.2 * lit)
        value += rim * (1.5 * spot(xy, knob_at, knob_size) - 2.6 * lines(xy, grooves) + 1.0 * lines(xy, ridges)
                        - 2.6 * hole + 1.3 * swell)
        value += 8.6 * spot(xy, glint_at, glint_size, 2.4) * smoothstep(0.3, 0.6, n[:, 2])
        return value

    def relief(p, n):
        xy = p[:, :2]
        hole, swell = hollow(xy)
        out = seen(n) * (0.85 * spot(xy, knob_at, knob_size) - 0.55 * lines(xy, grooves) +
                         0.22 * lines(xy, ridges) - 0.5 * hole + 0.15 * swell)
        out += 0.18 * lumps(p, 0.22, 3) * smoothstep(-0.6, -0.2, n[:, 2])
        # The stem and the nubs on top: bumps out of the top edge (headings 60-120 degrees from the middle,
        # near the outline, a little above its plane).
        a = np.degrees(np.arctan2(p[:, 1] - BLOB_MIDDLE[1], p[:, 0] - BLOB_MIDDLE[0]))
        r = np.hypot(p[:, 0] - BLOB_MIDDLE[0], p[:, 1] - BLOB_MIDDLE[1])
        top_edge = (smoothstep(60.0, 80.0, a) * smoothstep(120.0, 100.0, a) *
                    smoothstep(0.6, 0.95, r / shape.radius(np.radians(a))) *
                    np.exp(-((p[:, 2] - BLOB_BOTTOM - 1.2) / 2.2) ** 2))
        for x, half_width, out_by in frame["stem"]:
            out += out_by * top_edge * np.exp(-(np.abs(p[:, 0] - x) / half_width) ** 2.5)
        return out

    bands = band_materials(frame["name"], BLOB_BANDS,
                           lambda index: 0.62 if index < 0x73 else 0.45 if index < 0x76 else 0.2)
    painted(frame["name"], shape, shade, bands, relief, subdivisions=4,
            refine=(lambda d: d.z > -0.3, lambda d: d.z > 0.66))


# --- drops (E 277, 279, 281, 283) -------------------------------------------------------------------

# A drop, round its 9 x 12 box's middle: the head's middle and radius, the tip.
DROP = dict(head_y=1.6, head_radius=4.5, tip_y=-6.0)
DROP_CORE, DROP_CORE_SIZE = (-1.0, 1.5), (1.25, 1.25)
# The streak down its right side into the tip, and the dark gap between it and the core.
DROP_STREAK = [(3.0, 4.2, 0.5, 0.0), (3.1, 3.4, 0.65, 0.25), (3.1, 2.0, 0.75, 0.45), (3.0, 0.6, 0.8, 0.75),
               (2.5, -0.6, 0.85, 0.9), (1.9, -1.6, 0.85, 1.0), (1.3, -2.6, 0.85, 0.95), (0.6, -3.5, 0.8, 1.0),
               (0.0, -4.4, 0.7, 0.9), (-0.3, -5.1, 0.5, 0.5), (-0.4, -5.6, 0.4, 0.0)]
DROP_GAP = [(1.9, 4.4, 0.4, 0.0), (2.0, 3.4, 0.5, 0.8), (2.0, 2.2, 0.5, 1.0), (1.9, 1.2, 0.45, 0.6),
            (1.6, 0.4, 0.4, 0.0)]
# The heat shades: ramp 7 and the white core (0x1f), glowing more the hotter.
DROP_BANDS = [(-99.0, 0x70, 0.25), (1.0, 0x72, 0.3), (2.5, 0x73, 0.35), (3.5, 0x74, 0.4), (4.5, 0x75, 0.5),
              (6.0, 0x77, 0.7), (7.5, 0x78, 0.9), (8.5, 0x79, 1.1), (9.5, 0x7a, 1.3), (10.5, 0x7b, 1.5),
              (12.0, 0x7e, 1.8), (13.8, 0x1f, 2.2)]
# The sprite's drops: the top left corner of each 9 x 12 box (columns, rows) in each frame.
DROP_FRAMES = [
    ("drops", 277, [(2, 4), (14, 4), (8, 15)]),
    ("drops_279", 279, [(4, 2), (15, 8), (5, 14)]),
    ("drops_281", 281, [(8, 0), (2, 12), (14, 12)]),
    ("drops_283", 283, [(12, 2), (1, 8), (11, 14)]),
]


def drop(name):
    shape = Drop(**DROP)
    streak, gap = Line(DROP_STREAK), Line(DROP_GAP)

    def shade(p, n):
        xy = p[:, :2]
        rim = smoothstep(0.05, 0.55, n[:, 2])
        r = np.hypot(xy[:, 0] - DROP_CORE[0], (xy[:, 1] - DROP_CORE[1]) * 1.05)
        core = np.exp(-(r / 1.3) ** 2) * 10.5 + np.exp(-(r / 2.6) ** 2) * 4.4
        value = 0.4 + rim * (1.2 + core + 8.6 * streak.field(xy) - 1.7 * gap.field(xy))
        # The head's top edge and the tip's sides are darker, as drawn.
        value -= 0.8 * smoothstep(3.6, 5.6, xy[:, 1])
        return value

    def relief(p, n):
        return 0.12 * lumps(p, 0.35, 11) * smoothstep(-0.2, 0.3, n[:, 2])  # (the underside stays flat)

    bands = band_materials(name, DROP_BANDS, lambda index: 0.4 if index < 0x74 else 0.22)
    return painted(name, shape, shade, bands, relief, subdivisions=4)


def drops(name, boxes):
    """The drop at each box (the top left corner of its 9 x 12 pixels in the sprite), joined."""
    obj = drop(name)
    parts = [obj] + [obj.copy() for _ in boxes[1:]]
    for part in parts[1:]:
        part.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(part)
    for part, (col, row) in zip(parts, boxes):
        part.data.transform(Matrix.Translation((col + 4.5 - 12.0, 14.0 - row - 6.0, 0.0)))
    with bpy.context.temp_override(selected_editable_objects=parts, active_object=parts[0], object=parts[0]):
        bpy.ops.object.join()
    parts[0].name = name
    return parts[0]


# --- ember (5 76) -----------------------------------------------------------------------------------

EMBER_MIDDLE = (-0.5, 0.5)    # the sprite's columns 1-9, rows 2-10
EMBER_HALF, EMBER_POWER = 4.75, 3.4
EMBER_TOP, EMBER_BOTTOM = 3.4, 1.3
# The spikes: the direction (degrees from +X), how far they reach out of the body, their base's half-angle.
EMBER_SPIKES = [(90.0, 2.3, 22.0), (270.0, 2.1, 22.0), (180.0, 1.4, 21.0), (0.0, 1.4, 21.0)]
EMBER_CORE, EMBER_CORE_SIZE = (-0.4, 1.6), (1.0, 0.95)
EMBER_WARMTH, EMBER_WARMTH_SIZE = (-0.6, 2.2), (4.2, 2.8)   # the hot upper half round the core
# The glowing cracks from the core: to the left, up into the top spike and to the upper right; the
# fainter ones below; the dark crust across the middle and the pit.
EMBER_CRACKS = [
    [(-0.4, 1.6, 0.6, 1.0), (-1.6, 1.8, 0.55, 0.95), (-3.0, 1.6, 0.5, 0.9), (-4.3, 1.3, 0.45, 0.75),
     (-5.2, 1.0, 0.4, 0.0)],
    [(-0.4, 1.6, 0.55, 1.0), (-0.5, 3.0, 0.5, 0.85), (-0.5, 4.6, 0.45, 0.8), (-0.5, 5.8, 0.4, 0.75),
     (-0.5, 6.6, 0.35, 0.0)],
    [(-0.4, 1.6, 0.55, 1.0), (0.6, 2.6, 0.5, 0.8), (1.6, 3.4, 0.45, 0.85), (2.6, 3.6, 0.4, 0.7),
     (3.4, 3.8, 0.35, 0.0)],
    [(-1.9, 2.2, 0.4, 0.0), (-2.8, 3.2, 0.45, 0.75), (-3.4, 3.9, 0.4, 0.0)],
]
# The warm spots below the crust ((x, y), radius, heat: the sprite's 0x75-0x77 pixels there).
EMBER_WARM = [((-2.6, -1.6), 0.75, 0.8), ((-3.5, -2.6), 0.6, 0.65), ((2.4, -2.4), 0.7, 0.8), ((1.4, -1.4), 0.55, 0.5),
              ((-1.2, -2.6), 0.65, 0.55), ((-0.5, -4.4), 0.5, 0.4)]
EMBER_CRUST = [(-5.4, -0.3, 0.5, 0.0), (-4.0, -0.4, 0.6, 1.0), (-1.5, -0.6, 0.6, 1.0), (1.5, -0.4, 0.6, 1.0),
               (4.3, -0.5, 0.5, 0.0)]
EMBER_PIT, EMBER_PIT_SIZE = (-0.5, -1.6), (0.6, 0.55)
EMBER_BANDS = [(-99.0, 0x70, 0.2), (1.0, 0x72, 0.25), (2.5, 0x73, 0.3), (3.5, 0x74, 0.35), (4.5, 0x75, 0.45),
               (5.5, 0x76, 0.55), (6.5, 0x77, 0.7), (7.5, 0x78, 0.85), (8.5, 0x79, 1.0), (9.5, 0x7a, 1.2),
               (10.5, 0x7b, 1.4), (11.5, 0x7c, 1.6), (13.0, 0x1f, 2.2)]


def ember(name):
    a = np.radians(np.arange(0, 360, 10))
    c, s = np.abs(np.cos(a)), np.abs(np.sin(a))
    outline = EMBER_HALF / (c ** EMBER_POWER + s ** EMBER_POWER) ** (1 / EMBER_POWER)
    shape = Star(EMBER_MIDDLE, outline, EMBER_TOP, EMBER_BOTTOM)
    cracks = [(Line(c), 1.0) for c in EMBER_CRACKS]
    crust = Line(EMBER_CRUST)

    def warm(xy):
        return sum(heat * spot(xy, at, (radius, radius)) for at, radius, heat in EMBER_WARM)

    def spikes(p):
        """How far each point is pushed out into a spike (pixels): a cone round each spike's direction
        from the middle, a little above the outline's plane."""
        d = p - shape.middle
        heading = np.degrees(np.arctan2(d[:, 1], d[:, 0]))
        elevation = np.degrees(np.arctan2(d[:, 2] - 0.4, np.hypot(d[:, 0], d[:, 1])))
        push = np.zeros(len(p))
        for at, reach, half in EMBER_SPIKES:
            off = np.hypot((heading - at + 180.0) % 360.0 - 180.0, elevation)
            push += reach * np.clip(1 - off / half, 0.0, 1.0) ** 1.25
        return push

    def shade(p, n):
        xy = p[:, :2]
        rim = smoothstep(0.0, 0.5, n[:, 2])
        value = 1.2 + rim * (1.4 + 4.8 * spot(xy, EMBER_WARMTH, EMBER_WARMTH_SIZE) +
                             8.5 * spot(xy, EMBER_CORE, EMBER_CORE_SIZE) + 6.0 * lines(xy, cracks) +
                             5.2 * warm(xy) - 1.6 * crust.field(xy) - 2.4 * spot(xy, EMBER_PIT, EMBER_PIT_SIZE))
        value += 1.1 * lumps(p, 0.6, 5)
        return value

    def relief(p, n):
        xy = p[:, :2]
        return (spikes(p) + 0.35 * lumps(p, 0.45, 9) * smoothstep(-0.6, -0.2, n[:, 2]) - 0.3 * lines(xy, cracks) -
                0.25 * crust.field(xy) - 0.25 * spot(xy, EMBER_PIT, EMBER_PIT_SIZE))

    bands = band_materials(name, EMBER_BANDS, lambda index: 0.7 if index < 0x74 else 0.45)
    painted(name, shape, shade, bands, relief, subdivisions=4, refine=(lambda d: d.z > 0.3,), smooth_angle=60)


# --- Build ------------------------------------------------------------------------------------------------

def models():
    out = []
    for frame in BLOB_FRAMES:
        out.append((frame["name"], "5", frame["sprite"], True, lambda f=frame: blob(f)))
    for name, sprite, boxes in DROP_FRAMES:
        out.append((name, "E", sprite, True, lambda n=name, b=boxes: drops(n, b)))
    out.append(("ember", "5", 76, False, lambda: ember("ember")))
    return out


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sheet, sprite, large, make in models():
        if only is not None and name not in only:
            continue
        k.reset()
        make()
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (%s %d): %d triangles, %d materials: %s" % (name, sheet, sprite, triangles(), len(used),
                                                              ", ".join(sorted(used))))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_%s.png" % sheet), sprite, large=large)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            preview(options["preview"] + name, size=(24, 28) if large else (12, 14), distance=1.0 if large else 0.5)


if __name__ == "__main__":
    build()
