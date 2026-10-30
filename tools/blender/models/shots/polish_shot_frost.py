"""The Dragon Frost's drops of ice (shots2 sheet sprites 21, 22, 23, 40, 41, 42, 27 and 46, all 1x1: 12 x 14 cells),
modelled (2026-10-30, round 3 of the energy shots' models; until then each was drawn as its sprite with volume, flat,
from the 4x sheets, with the automatic glow).

Who fires them: the Dragon Frost (front weapon port 45, first sold in episode 5's first shop, 700; weapons 806-816 for
power levels 1-11, poweruse 50, a volley every 8-20 frames), each drop flying 5-8 pixels a frame up the screen, fanned
out (sx -7 .. 7), with trail 11 (the game's own frost puffs behind it); none is animated (weapani 0):
  power  1: 22                      power  5: 40 42 (sx -4, 4) + 22      power  9: 40 42 + the large drop 27/46
  power  2: 21 23 (sx -4, 4)        power  6: 40 42 + 41                 power 10: 40 42 + 27/46 + 21 23 (sx -5, 5)
  power  3: 21 23 + 22              power  7: 40 42 41 + 21 23 (sx -5, 5) power 11: 40 42 + 27/46 + 40 42 (sx -5, 5)
  power  4: 21 23 + 41              power  8: 40 42 + 40 42 (sx -5, 5) + 41          + 21 23 (sx -7, 7)
27 and 46 are fired together (by -6 and +8: 46 fourteen pixels below 27, both at sy 7) and draw one large drop; their
damage is 251 (over 250: they pierce, flying on through what they hit). Nothing else fires these sprites.

As the sprites draw them: drops of ice flying up the screen, a round head at the front and a tail tapering behind,
white-hot at heart and blue at their rims: the head and the tail's middle ramp 13's white (0xdf, its edges 0xdd 0xdc
0xdb), the rims ramp 9's blues (0x9c 0x9a and the darker 0x96 0x98 round the outline). 22 is the small drop straight
up (a head 8 pixels across, columns 2-9, rows 1-6, its middle at row 4; the tail down the middle column to row 13; 13
pixels long); 21 and 23 the same drop leaning about 40 degrees left and right; 41 the large drop straight up (a head
12 pixels across, columns 0-11, rows 0-8, squatter than 22's: 9 rows high; the tail to row 13); 40 and 42 the large
drop leaning (their hearts drawn in ramp 14's 0xef, which the default palette makes cream: the model keeps 41's white);
27 a long drop's head and body (10 pixels across, columns 1-10, its nose at row 0) and 46 its tail (rows 0-10 of the
cell below, narrowing to a pixel half a pixel right of the middle): one drop 25 pixels long.

The models: each drop a crystal of ice, round on top and flat underneath (the game's camera only ever sees shots from
above), cut in facets like a gem: its section a half-polygon of FACETS facets (a ridge along its top), lofted along
the screen's y from the sprite's outline (a round head, a tapering tail to a point), so that the facets run the drop's
length, curved, and catch the sun each its own way (the facets' edges are kept sharp, each facet smooth along its
length). Its colours in bands of the sprites' ramps (13's pale 0xde 0xdd, 9's blues 0x9e 0x9c 0x9a 0x96) from the
head's white to the tail's deep blue, lying in chevrons: the facets nearer the rim a shade (the next two) or three (the
rim's) bluer than those along the top (the sprites' blue rims; a shade less read too pale over white clouds, where the
sprites' dark rims stood out), and reaching each colour CHEVRON nearer the head; each band a ring of the mesh (no face
is cut), each glowing in its own colour, more the paler (0.22-0.38: more burned the heads white in the game's bloom
and hid the facets). Along the top of the head a core of frozen white stands out of it (a smaller faceted crystal, its
own ridge on top, 0xdf, 0.48), the head round it a shade cooler. One
model per look: the small drop (22, turned onto 21 and 23 with yaw= and at=), the large drop (41; 40 and 42), the long
drop built whole and cut at the sprites' border into its head (27) and its tail (46), each drawn at its own origin
("origin") and lowered by half the drop's height (height=), so that the two meet as one drop centred on the player's
layer. 354, 354, 234 and 160 triangles; 7 materials (46: 6).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
the drops stand on z = 0 (the game centres shot models in height on the player's layer).

models.cfg (the shots section): the build prints the model and shot lines (SHOTS below: yaw= and at= turn the drops
onto the leaning sprites, fitted with --fit; glow= a halo of light blue round the head).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_frost.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprites
     in <dir>/shots2.png, from TYR3D_EXTRACT, turned and moved as their shot lines say) [--fit <sheets dir>] (the yaw
     and at= that lay each drop best on its leaning sprites) [--preview <prefix>] (top, three-quarter and game-camera
     views)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
from polish_launched_flames import lit, check_frames, turn  # noqa: E402
from polish_shot_starburst import game_camera  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")

# --- The sprites (palette indices, '..' transparent): the upright drops, for reference and the docstring ------------

SPRITES = {
    22: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. 96 9a 9c 9c 9a 96 .. .. ..
.. .. 96 9c df df df df 9c 96 .. ..
.. .. 9a dd df df df df dd 9a .. ..
.. .. 9c df df df df df df 9c .. ..
.. .. 9a dd df df df df dd 9a .. ..
.. .. 96 9c df df df df 9c 96 .. ..
.. .. .. 9a dd df df dd 9a .. .. ..
.. .. .. 96 9c df df 9e 96 .. .. ..
.. .. .. .. 9a dd df 9c .. .. .. ..
.. .. .. .. 96 9c df 99 .. .. .. ..
.. .. .. .. .. 99 9f .. .. .. .. ..
.. .. .. .. .. 96 9c .. .. .. .. ..
.. .. .. .. .. .. 96 .. .. .. .. ..
""",
    41: """
.. .. .. 96 98 9a 9a 98 96 .. .. ..
.. .. 9a 9d dc df df dc 9d 9a .. ..
.. 9a dd df df df df df df dd 9a ..
96 9e df df df df df df df df 9e 96
99 dc df df df df df df df df dc 99
96 9e df df df df df df df df 9e 96
.. 9a dc df df df df df df dc 9a ..
.. 96 9a dc df df df df dc 9a .. ..
.. .. 96 9d df df df df 9d 96 .. ..
.. .. .. 9a dc df df dc 9a .. .. ..
.. .. .. 96 9d dc df 9d 96 .. .. ..
.. .. .. .. 9a 9d dc 9a .. .. .. ..
.. .. .. .. .. 9a 9d 95 .. .. .. ..
.. .. .. .. .. 95 9b .. .. .. .. ..
""",
    27: """
.. .. .. 94 95 96 96 95 94 .. .. ..
.. .. 94 98 9b 9d 9d 9b 98 94 .. ..
.. 94 98 9f df df df df 9f 98 94 ..
.. 98 9f df df df df df df 9f 98 ..
.. 9a df df df df df df df df 9b ..
.. 9d df df df df df df df df 9d ..
.. 9d df df df df df df df df 9e ..
.. 9d df df df df df df df df 9f ..
.. 9a df df df df df df df df 9e ..
.. 98 9f df df df df df df df 9c ..
.. 95 9c df df df df df df df 9b ..
.. .. 9c df df df df df df 9f 98 ..
.. .. 98 df df df df df df 9c 95 ..
.. .. 95 9f df df df df 9f 9b .. ..
""",
    46: """
.. .. .. 9d df df df df 9d 98 .. ..
.. .. .. 9c df df df df 9c 95 .. ..
.. .. .. 98 9f df df df 9b .. .. ..
.. .. .. 95 9c df df df 9a .. .. ..
.. .. .. .. 98 9f df df 98 .. .. ..
.. .. .. .. 95 9c df 9f 95 .. .. ..
.. .. .. .. .. 98 df 9c .. .. .. ..
.. .. .. .. .. 95 9f 98 .. .. .. ..
.. .. .. .. .. .. 9c 95 .. .. .. ..
.. .. .. .. .. .. 98 .. .. .. .. ..
.. .. .. .. .. .. 95 .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
}

# --- The drops --------------------------------------------------------------------------------------------------------
# A drop: its outline as (y, half-width) points from the nose (half-width 0) to the tail's tip (0), smoothed (a monotone
# curve through them, the nose's and the tail's ends rounded by the points near them), the x of its middle line at the
# head and at the tail's tip (a lean), the height of its section over its half-width (DEPTH: round on top), and its
# core's extent along it (t, 0 the nose, 1 the tail's tip), half-width (times the drop's there) and lift (pixels).


class Drop:
    def __init__(self, outline, middle=(0.0, 0.0), depth=0.82, core=(0.1, 0.55, 0.36, 0.4)):
        ys = [p[0] for p in outline]
        self.nose, self.tail = ys[0], ys[-1]
        self.length = self.nose - self.tail
        ts = [(self.nose - y) / self.length for y in ys]
        self._half = monotone(ts, [p[1] for p in outline])
        self.middle = middle
        self.depth = depth
        self.core = core

    def half(self, t):
        return max(self._half(min(max(t, 0.0), 1.0)), 0.0)

    def y(self, t):
        return self.nose - t * self.length

    def x(self, t):
        head, tip = self.middle
        return head + (tip - head) * max(0.0, (t - 0.45) / 0.55) ** 1.5

    def top(self, t, u):
        """The body's height at t, u across (-1..1: the rim, 0 the middle line): the faceted section's."""
        w = self.half(t)
        theta = math.acos(min(max(u, -1.0), 1.0))
        return facet_height(theta, w * self.depth)


# The section: FACETS facets over the top half (FACETS + 1 points from the right rim over the top to the left rim; an
# even count leaves a ridge along the top); each facet flat across, curved along the drop.
FACETS = 6
# The rings along the drop (t, 0 the nose, 1 the tail's tip): in the head (closer at the nose for its roundness),
# between the bands' borders where they lie further apart than GAP, and in the tail (fractions of the way from the last
# border to the tip).
HEAD_RINGS = (0.012, 0.035, 0.07, 0.115, 0.17)
GAP = 0.12
TAIL_RINGS = (0.4, 0.75, 0.93)
# The colours: a level along the drop (the head the palest, the tail the deepest blue: (from t, level)) less one or
# three shades on the facets nearer the rim (by facet from the top), which reach each level CHEVRON nearer the head, as
# palette indices by level (deep blue to white); the core's bands along it ((from t of the core, palette index)). The
# emission strength by palette index (pale ice glows most).
LEVELS = ((0.0, 5), (0.42, 4), (0.58, 3), (0.72, 2), (0.86, 1))
FACET_DROP = (0, 1, 3)  # (the two top facets, the next two, the rim's two)
CHEVRON = 0.06  # (each facet further from the top reaches each colour this much nearer the head: chevrons)
PALETTE = (0x96, 0x9a, 0x9c, 0x9e, 0xdd, 0xde)
CORE_BANDS = ((0.0, 0xdf),)
GLOW = {0x96: 0.22, 0x9a: 0.26, 0x9c: 0.3, 0x9e: 0.32, 0xdd: 0.34, 0xde: 0.38, 0xdf: 0.48}  # (by palette index)
ROUGHNESS, CORE_ROUGHNESS = 0.3, 0.25
CORE_FACETS = 4
CORE_RINGS = (0.0, 0.04, 0.12, 0.24, 0.4, 0.6, 0.8, 1.0)


def facet_height(theta, height):
    """The top of a half-polygon section of FACETS facets (points every pi / FACETS round a half-ellipse of that height)
    at the angle theta (0 the right rim, pi the left): straight between its points."""
    step = math.pi / FACETS
    j = min(int(theta / step), FACETS - 1)
    a0, a1 = j * step, (j + 1) * step
    x0, z0 = math.cos(a0), math.sin(a0)
    x1, z1 = math.cos(a1), math.sin(a1)
    x = math.cos(theta)
    f = (x - x0) / (x1 - x0) if abs(x1 - x0) > 1e-9 else 0.0
    return height * (z0 + (z1 - z0) * f)


def level_at(t):
    """The level along the top at t: the last border's that t has passed."""
    return [level for start, level in LEVELS if t >= start - 1e-9][-1]


def facet_rank(j, count=FACETS):
    """How far facet j (0 the right rim's) is from the top: 0 the top two, 1 the next, 2 the rim's."""
    middle = (count - 1) / 2.0
    return min(int(abs(j - middle)), len(FACET_DROP) - 1)


def ring_ts():
    """The rings along the drop (t): the head's, the bands' borders (each facet rank's, CHEVRON apart) with fillers
    between them where they lie further apart than GAP, the tail's."""
    points = list(HEAD_RINGS)
    previous = HEAD_RINGS[-1]
    borders = sorted({round(start - rank * CHEVRON, 6) for start, _ in LEVELS[1:] for rank in range(len(FACET_DROP))})
    for b in [b for b in borders if b > previous + 0.01]:
        extra = int((b - previous) / GAP)
        points += [previous + (b - previous) * (i + 1) / (extra + 1) for i in range(extra)]
        points.append(b)
        previous = b
    return points + [previous + (1.0 - previous) * f for f in TAIL_RINGS]


def palette_material(prefix, index, glow, roughness):
    return lit(f"{prefix}_{index:02x}", index, glow, roughness=roughness)


def faceted_loft(name, rings, bands, tips, materials, under):
    """A closed mesh through rings of points (each the upper half of a section: FACETS + 1 points from the right rim
    over the top to the left rim, the rims at z = 0), fans to the tip points at either end and a flat underside;
    bands[i][j]: the material slot of the faces between ring i and i + 1 on facet j (the last two rows: the nose's fan
    and the tail's), the underside materials[under]."""
    count = len(rings[0])
    verts = [tuple(p) for ring in rings for p in ring] + [tuple(tips[0]), tuple(tips[1])]
    nose, tail = len(verts) - 2, len(verts) - 1
    faces, mats = [], []
    for i in range(len(rings) - 1):
        a, b = i * count, (i + 1) * count
        for j in range(count - 1):
            faces.append((a + j, a + j + 1, b + j + 1, b + j))
            mats.append(bands[i][j])
        faces.append((a + count - 1, a, b, b + count - 1))  # (the underside)
        mats.append(under)
    last = (len(rings) - 1) * count
    for j in range(count - 1):
        faces.append((j + 1, j, nose))
        mats.append(bands[-2][j])
        faces.append((last + j, last + j + 1, tail))
        mats.append(bands[-1][j])
    faces.append((0, count - 1, nose))
    mats.append(under)
    faces.append((last + count - 1, last, tail))
    mats.append(under)
    obj = k.mesh_object(name, verts, faces)
    slots = []
    for m in materials:
        if m not in slots:
            slots.append(m)
            obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, mats):
        poly.material_index = slots.index(materials[m])
    k.recalc_normals(obj)
    return obj


def section(x, y, w, height, count):
    return [Vector((x + w * math.cos(math.pi * j / count), y, height * math.sin(math.pi * j / count)))
            for j in range(count + 1)]


def body(name, drop, materials):
    """The drop's ice: rings along it (the bands' borders and the head's roundness), each a faceted half-section."""
    ts = ring_ts()
    rings = [section(drop.x(t), drop.y(t), max(drop.half(t), 0.02), max(drop.half(t), 0.02) * drop.depth, FACETS)
             for t in ts]
    bands = []
    for i in range(len(ts) - 1):
        t = (ts[i] + ts[i + 1]) / 2
        bands.append([max(level_at(t + facet_rank(j) * CHEVRON) - FACET_DROP[facet_rank(j)], 0)
                      for j in range(FACETS)])
    bands.append([max(level_at(0.0) - FACET_DROP[facet_rank(j)], 0) for j in range(FACETS)])
    bands.append([max(level_at(1.0) - FACET_DROP[facet_rank(j)], 0) for j in range(FACETS)])
    obj = faceted_loft(name, rings, bands, ((drop.x(0.0), drop.nose, 0.0), (drop.x(1.0), drop.tail, 0.0)),
                       materials, 0)
    return k.smooth(obj, 22)


def core(name, drop, materials):
    """The core: a smaller faceted crystal along the head's top, its nose rounded, its tail a point, standing out of the
    ridge (its rims sunk a little into the body)."""
    t0, t1, width, lift = drop.core
    rings = []
    ts = []
    for f in CORE_RINGS[1:-1]:
        t = t0 + (t1 - t0) * f
        u = f / 0.3
        shape = math.sqrt(max(0.0, 1.0 - (1.0 - u) ** 2)) if f < 0.3 else ((1.0 - f) / 0.7) ** 0.85
        w = max(drop.half(t) * width * shape, 0.02)
        base = drop.top(t, 0.0)
        x, y = drop.x(t), drop.y(t)
        ring = []
        for j in range(CORE_FACETS + 1):
            a = math.pi * j / CORE_FACETS
            sink = drop.top(t, (w * math.cos(a)) / max(drop.half(t), 0.05)) - 0.06
            z = sink + (base + lift * shape - sink) * math.sin(a)
            ring.append(Vector((x + w * math.cos(a), y, z)))
        rings.append(ring)
        ts.append(f)
    bands = []
    for i in range(len(ts) - 1):
        f = (ts[i] + ts[i + 1]) / 2
        bands.append([max(b for b, (start, _) in enumerate(CORE_BANDS) if f >= start) for _ in range(CORE_FACETS)])
    bands.append([0] * CORE_FACETS)
    bands.append([len(CORE_BANDS) - 1] * CORE_FACETS)
    tips = ((drop.x(t0), drop.y(t0), drop.top(t0, 0.0) - 0.05), (drop.x(t1), drop.y(t1), drop.top(t1, 0.0) - 0.05))
    obj = faceted_loft(name, rings, bands, tips, materials, len(materials) - 1)
    return k.smooth(obj, 22)


def build_drop(name, drop):
    body_mats = [palette_material("frost", i, GLOW[i], ROUGHNESS) for i in PALETTE]
    core_mats = [palette_material("frost", i, GLOW[i], CORE_ROUGHNESS) for _, i in CORE_BANDS]
    return [body(name + "_ice", drop, body_mats), core(name + "_core", drop, core_mats)]


# The drops' outlines (y, half-width), from the sprites' rows (each row's middle at y = 6.5 - row, its pixels'
# half-width), smoothed: the small drop (22: head 8 across round row 4, the tail to row 13), the large one (41: head
# 12 across, squat), the long one (27 above 46: built round 27's centre, 46's 14 pixels below; its tail half a pixel
# right of the middle).
SMALL = Drop([(6.3, 0.0), (6.0, 1.9), (5.4, 3.0), (4.5, 3.75), (3.2, 4.05), (1.6, 4.0), (0.2, 3.55), (-1.3, 2.9),
              (-2.9, 2.05), (-4.4, 1.25), (-5.7, 0.6), (-6.9, 0.0)], depth=0.85, core=(0.08, 0.6, 0.42, 0.45))
LARGE = Drop([(7.2, 0.0), (6.9, 2.6), (6.2, 4.3), (5.0, 5.5), (3.6, 6.05), (2.2, 6.1), (0.8, 5.6), (-0.8, 4.6),
              (-2.4, 3.5), (-3.9, 2.4), (-5.3, 1.35), (-6.4, 0.6), (-7.2, 0.0)], depth=0.78,
             core=(0.07, 0.58, 0.4, 0.5))
LONG = Drop([(7.2, 0.0), (6.8, 2.6), (6.0, 4.1), (4.6, 4.95), (2.5, 5.05), (-1.5, 5.05), (-4.5, 4.75), (-7.0, 4.1),
             (-9.5, 3.3), (-12.0, 2.3), (-14.5, 1.35), (-16.5, 0.65), (-18.0, 0.0)], middle=(0.0, 0.5), depth=0.8,
            core=(0.05, 0.62, 0.4, 0.55))
PIECE = 14.0  # 46's centre below 27's
CUT = -7.0  # the sprites' border (y, round 27's centre)

# name: (the sprite it is authored as, the drop, the piece (None: whole; "head": above CUT; "tail": below it, moved
# up to its own centre), what it is)
MODELS = [
    ("shot_frost", 22, SMALL, None, "the small drop of ice (straight up)"),
    ("shot_frost_2", 41, LARGE, None, "the large drop of ice (straight up)"),
    ("shot_frost_27", 27, LONG, "head", "the long drop's head and body (origin)"),
    ("shot_frost_46", 46, LONG, "tail", "the long drop's tail (origin)"),
]

# The shot lines: (sprite, model, yaw (degrees clockwise from up), at (dx, dy: game pixels, dy down the screen), height
# (None, or "half": half the long drop's height down, for its pieces drawn at their origin), glow (size, strength,
# palette index; it is put on the model's head, turned and moved as the line says), comment). The leaning drops' yaw=
# and at= from --fit (the yaw within 3 degrees of the main axis of the sprites' pixels, 43.5 and 39.2 degrees off the
# vertical).
GLOW_COLOUR = 0x9e
HEAD = {"shot_frost": (0.0, 2.4), "shot_frost_2": (0.0, 2.6), "shot_frost_27": (0.0, 1.5), "shot_frost_46": (0.4, 4.0)}
SHOTS = [
    (22, "shot_frost", 0, None, None, (13, 0.4, GLOW_COLOUR), "the small drop, straight up"),
    (21, "shot_frost", 319, (0.8, 0.7), None, (13, 0.4, GLOW_COLOUR), "... leaning left"),
    (23, "shot_frost", 41, (-0.8, 0.7), None, (13, 0.4, GLOW_COLOUR), "... leaning right"),
    (41, "shot_frost_2", 0, None, None, (16, 0.4, GLOW_COLOUR), "the large drop, straight up"),
    (40, "shot_frost_2", 322, (0.45, 0.4), None, (16, 0.4, GLOW_COLOUR), "... leaning left"),
    (42, "shot_frost_2", 38, (-0.45, 0.4), None, (16, 0.4, GLOW_COLOUR), "... leaning right"),
    (27, "shot_frost_27", 0, None, "half", (15, 0.4, GLOW_COLOUR), "the long drop's head and body"),
    (46, "shot_frost_46", 0, None, "half", (9, 0.25, GLOW_COLOUR), "... its tail"),
]


def piece(parts, which, cap_material):
    """The long drop's part above the sprites' border (27) or below it (46, moved up to its own centre); the cuts
    closed in the middle blue."""
    box = (-20.0, 20.0, CUT, 40.0) if which == "head" else (-20.0, 20.0, -40.0, CUT)
    out = []
    for p in parts:
        cut = mk.cut(p, box, cap_material)
        if cut is not None:
            cut.name = p.name + ("_head" if which == "head" else "_tail")
            out.append(cut)
    for p in parts:
        mesh = p.data
        bpy.data.objects.remove(p)
        bpy.data.meshes.remove(mesh)
    if which == "tail":
        mk.transform(out, Matrix.Translation((0.0, PIECE, 0.0)))
    return out


def build_model(name, drop, which):
    parts = build_drop(name, drop)
    if which is not None:
        cap = next(m for m in parts[0].data.materials if m.name.endswith(f"@{0x9c}"))
        parts = piece(parts, which, cap)
    return triangulate(parts)


def heights():
    """The long drop's whole height (its pieces are drawn at their origin: height= half of it down)."""
    k.reset()
    parts = build_drop("long", LONG)
    zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
    return max(zs)


# --- Checks, fits and the models.cfg lines ----------------------------------------------------------------------------

def placement(yaw, at):
    """The shot line's turn and offset as one matrix (model coordinates: at's dy is down the screen)."""
    dx, dy = at if at is not None else (0.0, 0.0)
    return Matrix.Translation((dx, -dy, 0.0)) @ turn(yaw)


def fit(sheets, sprite, yaw0):
    """The yaw (whole degrees, within 3 of yaw0: the sprite's main axis) and at= (0.05 pixels) that lay the scene's
    model best on the sprite (outline and colours: shot_kit's top-view raster), and the overlap."""
    import numpy as np
    import shot_kit as sk
    tris, colours = sk.top_triangles()
    target = sk.sprite_image(sheets, "shots2", sprite)

    def score(yaw, dx, dy):
        t = math.radians(yaw)
        c, s = math.cos(t), math.sin(t)
        moved = tris.copy()
        moved[..., 0] = tris[..., 0] * c + tris[..., 1] * s + dx
        moved[..., 1] = -tris[..., 0] * s + tris[..., 1] * c - dy
        cov, rgb = sk.raster((moved, colours), 0)
        return sk.overlap(cov, target[0]) - 0.6 * sk.colour_distance(cov, rgb, target), sk.overlap(cov, target[0])
    best = None
    for yaw in range(yaw0 - 3, yaw0 + 4, 3):
        for dx in np.arange(-1.2, 1.21, 0.2):
            for dy in np.arange(-1.2, 1.21, 0.2):
                sc, ov = score(yaw, dx, dy)
                if best is None or sc > best[0]:
                    best = (sc, ov, yaw, dx, dy)
    _, _, yaw1, dx1, dy1 = best
    for yaw in range(max(yaw1 - 1, yaw0 - 3), min(yaw1 + 2, yaw0 + 4)):
        for dx in np.arange(dx1 - 0.2, dx1 + 0.21, 0.05):
            for dy in np.arange(dy1 - 0.2, dy1 + 0.21, 0.05):
                sc, ov = score(yaw, dx, dy)
                if sc > best[0]:
                    best = (sc, ov, yaw, dx, dy)
    sc, ov, yaw, dx, dy = best
    return yaw % 360, (round(dx * 20) / 20, round(dy * 20) / 20), sc, ov


def cfg_lines(half_height, only=None):
    """The models.cfg lines: the model lines, then the shot lines, their options in aligned columns."""
    names = [m[0] for m in MODELS if only is None or m[0] in only]
    width = max(len(n) for n in names)
    lines = [f"model {n.ljust(width)} shots/{n}.glb" + (" origin" if m[3] is not None else "")
             for m in MODELS for n in [m[0]] if n in names]
    rows = []
    for sprite, name, yaw, at, height, glow, comment in SHOTS:
        if name not in names:
            continue
        size, strength, colour = glow
        head = placement(yaw, at) @ Vector((HEAD[name][0], HEAD[name][1], 0.0))
        gx, gy = round(head.x * 20) / 20 + 0.0, round(-head.y * 20) / 20 + 0.0
        rows.append([f"shot shots2 {str(sprite).ljust(2)} {name.ljust(width)}",
                     f"yaw={yaw:g}" if yaw else "", f"at={at[0]:g}:{at[1]:g}" if at is not None else "",
                     f"height={-half_height:g}" if height == "half" else "",
                     f"glow={size:g}:{strength:g}:{colour}:{gx:g}:{gy:g}", comment])
    widths = [max(len(r[i]) for r in rows) for i in range(5)]
    out = []
    for r in rows:
        cells = [r[0]] + [r[i].ljust(widths[i]) for i in range(1, 5) if widths[i]]
        out.append(" ".join(cells) + " # " + r[5])
    return lines + out


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_view(prefix, objects, size=(12, 14), centre=(0.0, 0.0)):
    """The model as the game's camera sees it (20 degrees from straight down, from the bottom of the screen), lit by the
    game's sun, with mk.preview's top and three-quarter views."""
    mk.preview(prefix, objects, size=size, scale=32, distance=0.42, centre=centre)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0 * max(size[0] / 12.0, size[1] / 14.0), (512, 512))
    cam.location.x += centre[0]
    cam.location.y += centre[1]
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    half_height = round(heights() / 2, 2)
    for name, sprite, drop, which, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, drop, which)
        bpy.context.view_layer.update()
        print(f"== {name} (shots2 {sprite}): {what}")
        if "check" in options:
            for s, model, yaw, at, _, _, _ in SHOTS:
                if model == name:
                    check_frames(parts, os.path.join(options["check"], "shots2.png"),
                                 [(s, placement(yaw, at), f"shots2 {s}")], move_to_frame=False)
        if "fit" in options:
            for s, model, yaw, at, _, _, _ in SHOTS:
                if model == name and yaw:
                    fy, fat, sc, ov = fit(options["fit"], s, yaw)
                    print(f"   fit shots2 {s}: yaw={fy} at={fat[0]:g}:{fat[1]:g} (score {sc:.3f}, overlap {ov:.3f})")
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    print(f"the long drop's height {2 * half_height:.2f}: its pieces height={-half_height:g}")
    print("models.cfg:")
    for line in cfg_lines(half_height, only):
        print("  " + line)


if __name__ == "__main__":
    build()
