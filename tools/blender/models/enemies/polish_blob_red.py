"""The molten blob of GYGES and MISTAKES (sheet G sprite 1, 2x2: 24 x 28 pixels), polished
(2026-10-18; it replaces later_episodes.py's plain red balls).

A lumpy ball of molten rock, as round as the sprite (it spans its columns 2-19 and rows 4-20): a
dark red crust, cooler and raised in lumps, broken by glowing streaks that swirl round it (the
sprite's bright crescents along its left side and its lower right, a duller one at its upper
right), and a white-hot spot on its upper left where the sprite has its blazing highlight in every
frame. The heat is a field over the ball's surface; the faces are cut along its contours into bands
of the sprite's ramp (palette 112-127, black-red to white), each hotter band glowing more, the
hottest past white so the game's bloom spreads them; the underside is crust.

usage: Blender -b --python polish_blob_red.py -- [--out <file.glb>] [--preview <prefix>]
       [--sheets <TYR3D_EXTRACT sheets directory>]   (--sheets: print the silhouette overlap)
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

CENTRE = Vector((-1.0, 1.5, 0.0))   # the sprite's columns 2-19, rows 4-20
RADII = Vector((8.75, 8.35, 7.4))

# The hot spot and the streaks, as directions from the ball's middle given by where they show from
# above: (x, y) relative to CENTRE, and how far round the side they go (0: on top; > 1: under it).
HOT_SPOT = (-1.5, 4.6)
COOL_PLATE = (1.2, -0.6)
STREAKS = [
    # (heat, width in radians, path [(x, y, below)]): the bright crescent along the left side,
    (0.8, 0.17, [(-5.5, 5.5, 0.0), (-7.0, 3.0, 0.0), (-7.4, 0.3, 0.0), (-6.8, -2.2, 0.0), (-5.6, -4.2, 0.2),
                  (-3.6, -6.0, 0.6)]),
    # the one along the lower right,
    (0.82, 0.17, [(-0.5, -7.0, 0.5), (1.5, -6.2, 0.0), (3.4, -5.0, 0.0), (5.2, -3.4, 0.0), (6.4, -1.4, 0.0),
                 (7.4, 1.0, 0.5)]),
    # a duller one over the upper right,
    (0.44, 0.18, [(1.0, 7.6, 0.2), (3.4, 6.2, 0.0), (5.4, 4.0, 0.0), (6.6, 1.0, 0.2)]),
    # a thread of it running into the middle, and two crescents low round the far sides.
    (0.34, 0.12, [(-5.0, 1.2, 0.0), (-3.0, -0.8, 0.0), (-0.6, -1.6, 0.0), (1.6, -1.0, 0.0)]),
    (0.55, 0.17, [(7.4, 3.4, 0.7), (6.6, -1.0, 1.1), (4.6, -4.6, 1.4), (1.0, -6.8, 1.7)]),
    (0.5, 0.16, [(-7.6, -1.4, 1.5), (-7.4, 2.4, 1.2), (-5.4, 5.6, 0.9), (-2.0, 7.4, 0.6)]),
]

# The bands of heat: (lowest heat, palette index, emission strength in the palette colour): most of
# the ramp's shades, so the heat shades smoothly from the crust to the white-hot spot.
BANDS = [
    (-9.0, 0x70, 0.0),
    (0.13, 0x72, 0.05),
    (0.25, 0x74, 0.12),
    (0.35, 0x75, 0.2),
    (0.44, 0x76, 0.3),
    (0.52, 0x77, 0.45),
    (0.6, 0x78, 0.65),
    (0.67, 0x79, 0.85),
    (0.74, 0x7a, 1.0),
    (0.81, 0x7b, 1.2),
    (0.88, 0x7c, 1.4),
    (0.95, 0x7e, 1.7),
    (1.03, 0x7f, 2.2),
]


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def direction(x, y, below=0.0):
    """The direction from the ball's middle to the point that shows at (x, y) from above (on top,
    or `below` that far round the side: 1 at the equator, 2 at the bottom)."""
    u, v = x / RADII.x, y / RADII.y
    flat = math.hypot(u, v)
    if flat > 0.999:
        u, v, flat = u / flat * 0.999, v / flat * 0.999, 0.999
    w = math.sqrt(1 - flat * flat)
    if below > 0:
        # Turn on down the side: the angle from the top grows by `below` quarter turns past the point.
        angle = math.atan2(flat, w) + below * (math.pi / 2 - math.atan2(flat, w))
        angle = min(angle, math.pi * 0.98)
        h = (u / max(flat, 1e-6), v / max(flat, 1e-6))
        return Vector((h[0] * math.sin(angle), h[1] * math.sin(angle), math.cos(angle)))
    return Vector((u, v, w)).normalized()


def path_points(path, step=0.04):
    """A streak's path as (direction, how far along it 0..1), every `step` radians or so."""
    dirs = [direction(*p) for p in path]
    pieces = []
    for a, b in zip(dirs, dirs[1:]):
        count = max(1, int(a.angle(b) / step))
        pieces += [a.slerp(b, i / count) for i in range(count)]
    pieces.append(dirs[-1])
    return [(d, i / (len(pieces) - 1)) for i, d in enumerate(pieces)]


def heat_at(d):
    """The heat (0: dark crust, 1 and more: white hot) where the ball's surface faces d (a unit
    vector)."""
    a = d.angle(direction(*HOT_SPOT))
    feature = 1.05 * math.exp(-(a / 0.3) ** 2) + 0.3 * math.exp(-(a / 0.6) ** 2)
    for peak, width, points in STREAK_POINTS:
        for p, t in points:
            taper = math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.7  # crescents: full in the middle, thin at the ends
            n = d.angle(p) / (width * (0.45 + 0.55 * taper))
            if n < 4.0:
                value = peak * taper * (0.75 * math.exp(-n * n) + 0.35 * math.exp(-(n / 2.4) ** 2))
                feature = max(feature, value)
    # The crust between: warmer and cooler patches, darkest round the rim (seen from above) and
    # under the ball, where the melt fades too.
    patches = noise.noise(d * 2.3 + Vector((5.2, 1.3, 7.7))) + 0.5 * noise.noise(d * 4.7 + Vector((1.7, 6.1, 3.3)))
    cool = math.exp(-(d.angle(direction(*COOL_PLATE)) / 0.4) ** 2)  # the dark plate amid the streaks
    crust = (0.23 + 0.2 * patches - 0.16 * cool) * (0.35 + 0.65 * smoothstep(-0.2, 0.55, d.z))
    return crust + feature * (0.25 + 0.75 * smoothstep(-0.65, 0.05, d.z))


STREAK_POINTS = [(peak, width, path_points(path)) for peak, width, path in STREAKS]


def band_split(obj, values, bands):
    """Gives the faces of obj the material of their band of a value per vertex, cutting faces along
    the bands' borders so the borders are smooth contours (bands: [(lowest value, material)],
    ascending)."""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = list(values)
    thresholds = [b[0] for b in bands]
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina, inb = (vals[a] >= t) == above, (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    faces, materials = [], []
    for poly in mesh.polygons:
        indices = list(poly.vertices)
        low, high = min(vals[i] for i in indices), max(vals[i] for i in indices)
        for b in range(len(bands)):
            lo = thresholds[b] if b > 0 else -1e9
            hi = thresholds[b + 1] if b + 1 < len(bands) else 1e9
            if high < lo or low >= hi:
                continue
            piece = indices
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(bands) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                materials.append(b)
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for _, mat in bands:
        new.materials.append(mat)
    for poly, m in zip(new.polygons, materials):
        poly.material_index = m
    new.validate()
    obj.data = new
    bm = bmesh.new()
    bm.from_mesh(new)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.to_mesh(new)
    bm.free()
    k.recalc_normals(obj)
    return obj


def build():
    k.reset()
    # A dull sheen (the sun's highlight on the crust); the hotter bands glow in their own colour.
    mats = [k.material(f"blob_{index:x}", palette=index, metallic=0.0, roughness=0.65,
                       emission=k.level_palette()[index] if glow > 0 else None, emission_strength=glow)
            for _, index, glow in BANDS]

    ball = k.ellipsoid("blob", tuple(CENTRE), tuple(RADII), mats[0], segments=34, rings_count=19)
    values = []
    for v in ball.data.vertices:
        rel = v.co - CENTRE
        d = Vector((rel.x / RADII.x, rel.y / RADII.y, rel.z / RADII.z)).normalized()
        heat = heat_at(d)
        # Lumps: the crust swells in rounded lumps; the hot melt sits a little lower, the hot spot
        # bulges.
        lump = (0.08 * noise.noise(d * 1.7 + Vector((3.1, 8.4, 2.2))) +
                0.035 * noise.noise(d * 3.6 + Vector((9.0, 4.0, 1.0))))
        sink = -0.04 * smoothstep(0.45, 0.9, heat)
        bulge = 0.05 * math.exp(-(d.angle(direction(*HOT_SPOT)) / 0.35) ** 2)
        scale = 1.0 + lump + sink + bulge
        v.co = CENTRE + Vector((d.x * RADII.x, d.y * RADII.y, d.z * RADII.z)) * scale
        values.append(heat)
    band_split(ball, values, [(lowest, m) for (lowest, _, _), m in zip(BANDS, mats)])
    k.smooth(ball, 80)

    options = k.args()
    if "sheets" in options:
        k.check_silhouette(os.path.join(options["sheets"], "enemy_G.png"), 1)
    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "blob_red.glb"))


build()
