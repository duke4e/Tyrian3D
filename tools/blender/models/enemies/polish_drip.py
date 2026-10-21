"""NOSE DRIP's drip of fire, drawn from two sprites of sheet 5: 53 above 91 (2x2 each; a 17 x 54 drip in the 24 x 56
picture; not animated, each one frame: enemies 784 and 785, 28 of each, top layer; models.cfg: model drip_top /
drip_bottom ... origin; sprite 5 53 drip_top yaw=0 glow=20:0.25, sprite 5 91 drip_bottom yaw=0 glow=20:0.25),
polished (2026-10-21; it replaces wave3_l_parts.py's drip, two tubes round a lumpy core in flat heat bands). The
level places them as one picture: every drip is a pair of events at the same time and x, 784 (53) with its y 28
pixels up (dat5 -28) over 785 (91), linked (NOSE DRIP's events 130-200, 3230-3335, 3600-3615 ...), so they fall
together. No other sprite has their pixels (mirrored, turned or in other ramps).

As the sprites and their 4x upscales draw it, in the fire's ramp 7 (0x70 its dark red outline, 0x72-0x76 reds,
0x77-0x79 oranges, 0x7a-0x7d yellows): a flame's tip at the top (row 0 of the 56) twisting down into two strands
of fire that wind round each other, crossing five times: where they cross the drip is narrow (rows 5-7, 12-13,
24-25, 37-38, 47-50), where they swing apart it is wide, with the dark showing between them at first (a pixel at
row 10, three across rows 16-19), then, thicker and lumpier, round a molten core (rows 28-46, two lobes 17 and 15
wide), into the drop's point (row 53). At every crossing the strand in front runs from the upper left to the lower
right. The heat: yellow and orange along the strands' crests and in the core's blobs, red down their sides, the
dark red outline round everything.

The model: the drip is built whole, a double helix of two tubes (STRANDS: their phase, the helix's radius and the
tubes' thickness along y, fitted to the rows' widths, the holes and the crossings) about the drip's axis (the rows'
middles, about the middle of column 12: x 0.5), lumpy in the bulb, round a lumpy molten core (CORE) filling the bulb
between them. Their surfaces are painted with the sprites' heat (their shades smoothed, as the upscales soften them;
polish_flame_drop.py's method and its Heat), cooler where they turn away from the camera, in bands of the ramp cut
along smooth borders, each band glowing a little in its own colour, more the hotter, but low (0.08-0.55:
models.cfg's glow halo adds its light on top); the hottest parts swell out a little, so that the sun glints on them
as on molten glass. Then it is cut along the sprites' edge (y = 0) into the two pieces (polish_machine_kit's cut(),
polish_redjet.py's method: the pieces keep the whole's shading across the cut, the cut closed with flat caps which
meet), each moved so that its sprite's centre is its origin: drawn at their own origins (origin), they meet. The
pieces stand on the layer (origin: their base on it): the drip's lowest point at z = 0.2.

Coordinates of the whole: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
middle of the sprites' common edge (row r of the 56 rows is y = 27.5 - r, column c is x = c - 11.5).

Replaces wave3_l_parts.py's drip: DRIP, DRIP_PIECES, build_drip(), drip_piece(), its two PIECES entries and its
w.whole("drip", ...) registration, and the drip lines of its docstring; wave3_l_art.py's DRIP (read only by them).
NOT drip_bands(): wave3_l_parts.py's fire bowl (build_fire_bowl) uses it.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
pieces and of the whole against enemy_5.png), --preview <prefix> (each piece's top and 3/4 views, and the whole's),
--only <name,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402

# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)
PIECES = [("drip_top", 53, (-12.0, 12.0, 0.0, 28.0)),
          ("drip_bottom", 91, (-12.0, 12.0, -28.0, 0.0))]

# The sprites' shades (palette index - 0x70: the fire's ramp), 53 above 91; '.' transparent.
DRIP = """
............1...........
...........10...........
...........21...........
..........0220..........
..........1230..........
..........02430.........
.........0004511........
.........0103730........
........032125601.......
........033114630.......
........0251.3520.......
........115624420.......
.........12575400.......
.........0035850........
........022115830.......
.......02443215950......
.......03530.11770......
......02752...06831.....
......13741...15b41.....
......248400.017a41.....
......1497310049840.....
......0489630047620.....
......1379753135320.....
.......14698642320......
........047a95621.......
........0058b8682.......
.......024349c8681......
......02564259a6851.....
......04693428a9792.....
.....0369939429a5852....
.....0489a3742596552....
.....158aa2442487642....
....0259ca23223665232...
....025a9368763542562...
....0135346a824325591...
....01228b57433276771...
.....013baa448b94831....
......01599948a9700.....
.......10479958860......
......2212589731000.....
......223347b974210.....
.....226974ac9654121....
.....237b97da8652472....
.....23466b967525792....
.....223379874356b51....
......2235774356661.....
.......22379847931......
........239cb77a4.......
........136aa87a3.......
........1357879a1.......
........213456951.......
.........1126852........
..........24752.........
...........221..........
........................
........................
"""


# --- Curves -------------------------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic)."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2 if d[i - 1] * d[i] > 0 else 0.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a * a + b * b > 9:
            t = 3 / math.sqrt(a * a + b * b)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def f(x):
        x = min(max(x, xs[0]), xs[-1])
        i = max(0, min(n - 2, next((j for j in range(n - 1) if x <= xs[j + 1]), n - 2)))
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        return ((2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h * m[i] +
                (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h * m[i + 1])
    return f


class Curve:
    """Smooth curves through table rows (x, value, ...), one per value column: called with x, it returns the value
    (one column) or the list of values."""

    def __init__(self, rows):
        rows = sorted(rows)
        columns = list(zip(*rows))
        self.functions = [monotone(columns[0], c) for c in columns[1:]]

    def __call__(self, x):
        values = [f(x) for f in self.functions]
        return values if len(values) > 1 else values[0]


# --- The sprites' heat ---------------------------------------------------------------------------------------------

def grid(art):
    return [[None if ch == "." else int(ch, 16) for ch in line] for line in art.strip("\n").splitlines()]


class Heat:
    """The sprites' shades smoothed (a Gaussian sigma (across, along y) wide over the drip's own pixels; outside them,
    a wider blur of the nearest ones, so the field runs on smoothly into the holes), read anywhere: pixel (c, r) is
    at x = c - 11.5, y = 27.5 - r (polish_flame_drop.py's)."""

    def __init__(self, rows, sigma=(0.85, 1.0)):
        self.h, self.w = len(rows), len(rows[0])
        value = np.array([[0.0 if s is None else float(s) for s in line] for line in rows])
        mask = np.array([[0.0 if s is None else 1.0 for s in line] for line in rows])

        def blur(a, sx, sy):
            for axis, s in ((1, sx), (0, sy)):
                radius = int(math.ceil(s * 3))
                kernel = np.exp(-np.arange(-radius, radius + 1) ** 2 / (2 * s * s))
                pad = [(0, 0), (0, 0)]
                pad[axis] = (radius, radius)
                a = np.apply_along_axis(lambda line: np.convolve(line, kernel, "valid"), axis, np.pad(a, pad))
            return a
        weight = blur(mask, *sigma)
        near = blur(value * mask, *sigma) / np.maximum(weight, 1e-6)
        far = blur(value * mask, 2.0, 2.0) / np.maximum(blur(mask, 2.0, 2.0), 1e-6)
        self.field = np.where(weight > 0.25, near, far)

    def __call__(self, x, y):
        c = min(max(x + 11.5, 0.0), self.w - 1.001)
        r = min(max(27.5 - y, 0.0), self.h - 1.001)
        c0, r0 = int(c), int(r)
        fc, fr = c - c0, r - r0
        f = self.field
        return ((f[r0, c0] * (1 - fc) + f[r0, c0 + 1] * fc) * (1 - fr) +
                (f[r0 + 1, c0] * (1 - fc) + f[r0 + 1, c0 + 1] * fc) * fr)


def row_middles(rows):
    """The rows' middles (x), smoothed: the drip's axis."""
    ys, xs = [], []
    for r, line in enumerate(rows):
        cols = [c for c, s in enumerate(line) if s is not None]
        if cols:
            ys.append(27.5 - r)
            xs.append((cols[0] + cols[-1] + 1) / 2 - 12.0)
    ys, xs = ys[::-1], xs[::-1]
    smooth = [sum(xs[max(0, i - 2):i + 3]) / len(xs[max(0, i - 2):i + 3]) for i in range(len(xs))]
    return monotone(ys, smooth)


# --- The strands and the core -------------------------------------------------------------------------------------
# The double helix along y (top to bottom): the phase of the first strand (degrees; the second's is half a turn on),
# the helix's radius and the strands' radius. The strands cross where the phase is 90 + 180 k (the drip's waists: y
# 22.3, 15, 3, -10.2, -21.2) and lie farthest apart at 180 k (y 17.6 and 10, the holes, R - s their half-widths;
# -6 and -15, the bulb's lobes, where the core fills between them). The flame's tip (y above 22.5): both strands on
# the axis, one body.
STRANDS = Curve([
    (27.85, 30.0, 0.0, 0.3), (27.0, 45.0, 0.05, 0.62), (25.5, 60.0, 0.15, 1.0), (24.0, 72.0, 0.3, 1.6),
    (22.5, 85.0, 0.75, 1.95), (21.0, 115.0, 1.4, 2.0), (19.4, 152.0, 2.05, 1.92), (17.6, 180.0, 2.55, 1.84),
    (16.3, 225.0, 2.65, 1.85), (15.0, 270.0, 2.75, 1.95), (12.5, 320.0, 3.4, 2.25), (10.0, 360.0, 3.9, 2.35),
    (6.5, 410.0, 4.05, 2.85), (3.0, 450.0, 3.65, 3.25), (-1.5, 500.0, 4.15, 3.45), (-6.0, 540.0, 4.75, 3.65),
    (-10.2, 630.0, 4.2, 3.45), (-15.0, 720.0, 3.9, 3.25), (-18.5, 770.0, 3.35, 2.95), (-21.2, 810.0, 2.5, 2.6),
    (-22.6, 830.0, 1.9, 2.3), (-23.8, 848.0, 1.0, 2.1), (-24.8, 860.0, 0.25, 1.7), (-25.5, 868.0, 0.0, 1.0),
    (-25.95, 872.0, 0.0, 0.3)])
Y_TOP, Y_BOTTOM = 27.85, -25.95
SQUASH = 0.85      # the helix flattened a little towards the camera
LUMPS = (5.0, -1.0, 0.24)   # the strands lumpy below y (fading in to the second y), by this fraction of their radius
# The molten core between the strands in the bulb: y, its radius; hotter than the sprite's shades by CORE_HEAT.
CORE = Curve([(2.6, 0.0), (1.2, 1.2), (-1.0, 2.4), (-3.5, 3.2), (-6.0, 3.5), (-8.5, 3.25), (-10.2, 2.9),
              (-12.5, 3.05), (-15.0, 3.2), (-18.0, 2.7), (-20.5, 2.05), (-22.8, 1.4), (-24.2, 0.7), (-24.9, 0.0)])
CORE_TOP, CORE_BOTTOM = 2.6, -24.9
CORE_HEAT = 1.5
SEGMENTS, CORE_SEGMENTS = 12, 12   # round the strands and the core
BASE = 0.2   # the drip's lowest point above the layer (origin pieces stand on it)


def axis_z():
    """The axis' height: about the drip's lowest point above the layer (the whole is then moved onto it)."""
    return max(SQUASH * STRANDS(y)[1] + STRANDS(y)[2] for y in np.linspace(Y_BOTTOM, Y_TOP, 400))


def strand_points(k_, middle, zc, rng):
    """The k-th strand's path and radii, top to bottom."""
    lumps = [(rng.uniform(0.7, 1.6), rng.uniform(0, 2 * math.pi), rng.uniform(0.5, 1.0)) for _ in range(3)]
    ys = []
    y = Y_TOP - 0.02
    while y > Y_BOTTOM + 0.02:
        ys.append(y)
        y -= 0.42 if Y_BOTTOM + 2.0 < y < 1.0 else 0.36 if Y_BOTTOM + 2.0 < y < Y_TOP - 1.2 else 0.16
    ys.append(Y_BOTTOM + 0.02)
    points, radii = [], []
    for y in ys:
        phase, r, s = STRANDS(y)
        a = math.radians(phase) + math.pi * k_
        points.append(Vector((middle(y) - r * math.cos(a), y, zc + SQUASH * r * math.sin(a))))
        lump = sum(w * math.sin(f * y + p) for f, p, w in lumps) / 2.0
        fade = smoothstep(LUMPS[0], LUMPS[1], y) * smoothstep(Y_BOTTOM + 1.0, Y_BOTTOM + 5.0, y)
        radii.append(s * (1.0 + LUMPS[2] * lump * fade))
    return points, radii


def tube(name, points, radii):
    """A round tube through the points (Vectors), closed with rounded ends: rings across the path (their side kept
    horizontal, so each ring's first point faces the same way)."""
    rings = []
    for i, p in enumerate(points):
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / SEGMENTS) + up * math.sin(2 * math.pi * j / SEGMENTS)) *
                      radii[i] for j in range(SEGMENTS)])
    t0 = (points[1] - points[0]).normalized()
    t1 = (points[-1] - points[-2]).normalized()
    return k.loft(name, rings, None, start_point=points[0] - t0 * radii[0] * 0.7,
                  end_point=points[-1] + t1 * radii[-1] * 0.7)


def core(middle, zc, rng):
    """The molten core: a lumpy round body along the axis in the bulb."""
    bumps = [(Vector((rng.uniform(-1, 1), rng.uniform(CORE_BOTTOM + 3, CORE_TOP - 2), rng.uniform(-1, 1))),
              rng.uniform(1.4, 2.4), rng.uniform(0.25, 0.5)) for _ in range(9)]
    ys = [CORE_TOP - (CORE_TOP - CORE_BOTTOM) * i / 36 for i in range(1, 36)]
    rings = []
    for y in ys:
        r = CORE(y)
        ring = []
        for j in range(CORE_SEGMENTS):
            a = 2 * math.pi * j / CORE_SEGMENTS
            d = Vector((math.cos(a), 0.0, math.sin(a)))
            p = Vector((middle(y), y, zc)) + d * r
            lump = sum(h * math.exp(-((p - Vector((middle(y), 0, zc)) - Vector((c.x * r, c.y, c.z * r))).length /
                                      w) ** 2) for c, w, h in bumps)
            ring.append(p + d * lump)
        rings.append(ring)
    return k.loft("core", rings, None, start_point=(middle(CORE_TOP), CORE_TOP, zc),
                  end_point=(middle(CORE_BOTTOM), CORE_BOTTOM, zc))


# --- The heat painted on ------------------------------------------------------------------------------------------
# The bands: (lowest heat, palette index, emission strength in the palette colour), ramp 7 from the outline's dark
# red to yellow; the hotter, the more it glows, but low (models.cfg's glow halo adds on top).
BANDS = [(-99.0, 0x70, 0.08), (1.7, 0x72, 0.12), (3.4, 0x74, 0.18), (5.0, 0x76, 0.25), (6.5, 0x78, 0.33),
         (8.0, 0x79, 0.4), (9.3, 0x7a, 0.46), (10.6, 0x7c, 0.55)]
HEAT = (1.08, 0.4)     # the sprites' shades scaled and raised (the upscales' fire is brighter than the pixels)
FACING = (2.6, 0.5)    # heat added per unit of the normal's z above FACING[1] (the sides turning away cooler)
SWELL, SWELL_FROM = 0.7, 7.0   # the hottest parts swell out along their normals by up to SWELL


def band_materials():
    pal = k.level_palette()
    return [(lowest, k.material(f"drip_{index:02x}", palette=index, metallic=0.0,
                                roughness=0.4 if index < 0x74 else 0.3 if index < 0x78 else 0.24,
                                emission=pal[index], emission_strength=glow))
            for lowest, index, glow in BANDS]


def paint_heat(obj, heat, bands, extra=0.0):
    """The object's faces in the bands of the heat (the sprites' under each point, cooler where the surface turns
    away from the camera), cut along the bands' borders, then swollen where hot."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    values = {v: HEAT[0] * heat(v.co.x, v.co.y) + HEAT[1] + extra + FACING[0] * (v.normal.z - FACING[1])
              for v in bm.verts}
    normals = {v: v.normal.copy() for v in bm.verts}
    borders = [lowest for lowest, _ in bands[1:]]
    for t in borders:
        # New points on an edge: the normals of the points it joins that had one before this border's cut (not
        # its new neighbours', which come in no fixed order), so that every run swells them alike.
        known = dict(normals)
        for v in mk.split_along(bm, values, t):
            n = sum((known[e.other_vert(v)] for e in v.link_edges if e.other_vert(v) in known), Vector())
            normals[v] = n.normalized() if n.length > 1e-6 else Vector((0, 0, 1))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = [sum(sum(values[v] for v in f.verts) / len(f.verts) > t for t in borders) for f in bm.faces]
    for v in bm.verts:
        lift = SWELL * max(0.0, (values[v] - SWELL_FROM) / (13.0 - SWELL_FROM))
        v.co = v.co + normals[v] * lift
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    used = sorted(set(kinds))
    for i in used:
        obj.data.materials.append(bands[i][1])
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = used.index(kind)
    k.recalc_normals(obj)
    return k.smooth(obj, 70)


def build_whole():
    rows = grid(DRIP)
    heat = Heat(rows)
    middle = row_middles(rows)
    zc = axis_z()
    rng = random.Random(5391)
    bands = band_materials()
    for i in range(2):
        points, radii = strand_points(i, middle, zc, rng)
        paint_heat(tube(f"strand{i}", points, radii), heat, bands)
    paint_heat(core(middle, zc, rng), heat, bands, extra=CORE_HEAT)
    # Standing on the layer: the lowest point BASE above it.
    whole = mk.meshes()
    low = mk.bounds(whole)[0].z
    mk.transform(whole, Matrix.Translation((0.0, 0.0, BASE - low)))
    return whole, bands


# --- Checks, pieces and export ------------------------------------------------------------------------------------

def triangulate(objects):
    """Every face split into triangles (the same split every run, the custom normals kept), so that the export
    doesn't split them itself (polish_k_pod.py's)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)


def whole_mask():
    rows = grid(DRIP)
    return [[s is not None for s in line] for line in rows]


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else [p[0] for p in PIECES]
    k.reset()
    whole, bands = build_whole()
    print("whole drip: %d triangles (%s)" % (mk.triangles(whole),
                                             ", ".join("%s %d" % (o.name, mk.triangles([o])) for o in whole)))
    sheet = options.get("check")
    if sheet:
        sheet = os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet
        mk.compare("whole (53 above 91)", mk.coverage(whole, 24, 56), whole_mask())
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "drip_whole", whole, size=(24, 56), scale=10, distance=1.1)
    cap = bands[2][1]
    for name, sprite, box in PIECES:
        if name not in only:
            continue
        pieces = [p for p in (mk.cut(src, box, cap) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        triangulate(pieces)
        if sheet:
            mk.compare("%s (5 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces, distance=0.8)
        for obj in pieces:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
