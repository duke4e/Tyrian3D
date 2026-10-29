"""The Pulse-Cannon's shots (shots sheet sprites 58, 59, 60, 165 and 62, all 1x1: 12 x 14 cells), modelled (2026-10-29,
the pilot of the energy shots' models: until then every shot without a "shot" line, pulses, lasers, plasma, waves and
the enemies' bullets, was drawn as its sprite with volume, flat, from the 4x sheets, with the automatic glow).

Who fires them: the Pulse-Cannon (weapon port 1, the front gun every ship starts with; weapons 155-165 for power levels
1-11), straight up the screen at 10 pixels a game frame, a volley every 3-5 frames; none of them is animated (weapani 0)
and none picks its sprite by direction:
  power  1: 59             power  5: 60 + 58 58 (8 out, 4 behind)   power  9: 60 + 59 59 + 58 58
  power  2: 60             power  6: 165 + 58 58 (9 out)              power 10: 60 + 59 59 + 59 59
  power  3: 165            power  7: 59 + 59 59 (10 out, 4 behind)    power 11: 62 + 59 59 + 59 59
  power  4: 59 59 (6 out)  power  8: 60 + 59 59                       (the outer pairs 18-24 out, 8 behind)
The sprite grows with the shot's damage (58: 1, 59: 2, 60: 3, 165: 4, 62: 5). Also: the Multi-Cannon (port 2: 59 at
power 1, then 58 or 59 straight up in the middle of its fan from power 3), the Hyper Pulse (port 27: 58 at every power,
59 from power 6, 60 at power 10), the second player's guns in two-player games: the linked turret (weapons 445 and 451,
whose shots take their sprite by heading from shots.c's linkMultiGr and linkMult2Gr: 58 and 59 are the headings
straight up) and the charge cannon (weapons 458-461, charge levels 0-3: 58, 59, 60, 59), and enemies: weapons 125 and
126 (58, falling down the screen with its head up, as the sprite is drawn) and 81 (58 in a burst of pulses flying
every way) of TYRIAN's, ASSASSIN's, HOLES', TYRIAN X's, SAVARA's and NOSE DRIP's turrets, once an Enemy Fire Override
event gives them a frequency (weapon 9, 60 in episodes 4 and 5's data, no enemy of the levels fires).

As the sprites draw them: each is small bolts of fire (the fire's ramp 7) flying up the screen side by side. A bolt is
4 pixels wide and 11 rows long, its head a rounded cap a row deep, its hottest pixels just behind it (0x7c, 0x7b at
rows 1-2, then 0x7a, 0x79 down its middle: in the 4x upscale a yellow wedge pointing back), orange down its body (0x77,
0x78), its sides and tail dark red (0x72-0x75), the tail narrowing to a pixel at row 10. 58 is one bolt (columns 4-7);
59 two (columns 1-4 and 7-10, their hot columns on their inner sides); 60 three, the outer two 2 rows behind (columns
0-3 and 8-11, mirror images); 165 four narrower bolts, 3 pixels wide with a hot spine down their middle column (in the
upscale bright yellow streaks), the inner pair touching (columns 3-5 and 6-8, rows 0-10), the outer pair 3 rows behind
(columns 0-2 and 9-11, rows 3-13); 62 five, an arrowhead: a 4-pixel bolt in the middle (rows 0-10) between 3-pixel
bolts a row behind it (columns 2-4 and 7-9, rows 1-11) and three rows behind it (columns 0-2 and 9-11, rows 3-13), their
edges overlapping.

The models: every bolt is a body of fire round on top and flat underneath (a half-body: the game's camera only ever
sees shots from above, and their shadows fall from above, so the underside is a flat face no one sees: a third of the
triangles saved), lofted along the screen's y from a teardrop outline (an elliptical cap for the head, full width down
the body, a tail tapering to a point where the sprite's tail ends). Its fire is in bands of ramp 7's palette indices
(0x73 at the tail's tip to 0x7a round the core; palette materials, so the bands follow the level's palette and fades),
each glowing in its own colour, more the hotter (0.24-0.5), by a heat that falls along the bolt as the sprite's middle
columns do and falls faster at its sides, so that the colours lie in chevrons pointing back, their borders waving a
little (tongues of flame licking back). The mesh is built on the bands: its rings are the bands' borders (each point of
a ring at its own place along the bolt), with rings between them only where they lie far apart, so no face is cut
along a border (cutting faces along the borders, as polish_orb_red.band_split does, tripled the triangles). In each
4-pixel bolt's head a core of plasma stands out of the fire, a smaller teardrop pointing back, round on top, pale yellow
at its front and yellow behind (0x7e, 0x7d, glowing 0.6-0.62: the sprite's hot wedge, raised); each 3-pixel bolt has a
long thin spine of the same instead (its hot middle column). Each model's models.cfg line gives it a glow (glow=, in
place of the automatic one, 13 pixels at 0.7 in the sprite's brightest colour, which washed the bands out into one
yellow-orange): a yellow halo (0x7b at 0.5) round the bolts' heads, as large as the bolts are wide.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
the bolts stand on z = 0 (the game centres shot models in height on the player's layer). 332-1 424 triangles, 10
materials (each material is one more draw of the model in every pass).

models.cfg (the shots section; dy of the glow moves it up the screen to the heads):
    model shot_pulse   shots/shot_pulse.glb      shot shots 58  shot_pulse   glow=10:0.5:123:0:-2.5
    model shot_pulse_2 shots/shot_pulse_2.glb    shot shots 59  shot_pulse_2 glow=13:0.5:123:0:-2.5
    model shot_pulse_3 shots/shot_pulse_3.glb    shot shots 60  shot_pulse_3 glow=15:0.5:123:0:-1.5
    model shot_pulse_4 shots/shot_pulse_4.glb    shot shots 165 shot_pulse_4 glow=15:0.5:123:0:-1
    model shot_pulse_5 shots/shot_pulse_5.glb    shot shots 62  shot_pulse_5 glow=16:0.5:123:0:-1.5

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_pulse.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprite in
     <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views)
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import Heat, monotone  # noqa: E402
from polish_launched_flames import grid, shades, lit, smoothstep, check_frames, turn  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
TOP = 7.0  # the y of a 1x1 sprite's top edge

# --- The sprites (palette indices, '..' transparent) ----------------------------------------------------------------

SPRITES = {
    58: """
.. .. .. .. .. 75 76 .. .. .. .. ..
.. .. .. .. 75 7c 7b 76 .. .. .. ..
.. .. .. .. 76 7b 7a 77 .. .. .. ..
.. .. .. .. 78 7a 79 78 .. .. .. ..
.. .. .. .. 78 77 78 77 .. .. .. ..
.. .. .. .. 75 76 77 75 .. .. .. ..
.. .. .. .. 74 77 77 74 .. .. .. ..
.. .. .. .. 73 75 75 73 .. .. .. ..
.. .. .. .. 72 73 72 72 .. .. .. ..
.. .. .. .. .. 72 71 .. .. .. .. ..
.. .. .. .. .. 71 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    59: """
.. .. 76 75 .. .. .. .. 75 76 .. ..
.. 76 7b 7c 75 .. .. 75 7c 7b 76 ..
.. 77 7a 7b 76 .. .. 76 7b 7a 77 ..
.. 78 79 7a 78 .. .. 78 7a 79 78 ..
.. 77 78 77 78 .. .. 78 77 78 77 ..
.. 75 77 76 75 .. .. 75 76 77 75 ..
.. 74 77 77 74 .. .. 74 77 77 74 ..
.. 73 75 75 73 .. .. 73 75 75 73 ..
.. 72 72 73 72 .. .. 72 73 72 72 ..
.. .. 71 72 .. .. .. .. 72 71 .. ..
.. .. .. 71 .. .. .. .. 71 .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    60: """
.. .. .. .. .. 75 76 .. .. .. .. ..
.. .. .. .. 75 7c 7b 76 .. .. .. ..
.. 75 76 .. 76 7b 7a 77 .. 76 75 ..
75 7c 7b 76 78 7a 79 78 76 7b 7c 75
76 7b 7a 77 78 77 78 77 77 7a 7b 76
78 7a 79 78 75 76 77 75 78 79 7a 78
78 77 78 77 74 77 77 74 77 78 77 78
75 76 77 75 73 75 75 73 75 77 76 75
74 77 77 74 72 73 72 72 74 77 77 74
73 75 75 73 .. 72 71 .. 73 75 75 73
72 73 72 72 .. 71 .. .. 72 72 73 72
.. 72 71 .. .. .. .. .. .. 71 72 ..
.. 71 .. .. .. .. .. .. .. .. 71 ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    165: """
.. .. .. .. 75 .. .. 75 .. .. .. ..
.. .. .. 76 7c 75 75 7c 76 .. .. ..
.. .. .. 77 7b 76 76 7b 77 .. .. ..
.. 75 .. 78 7a 78 78 7a 78 .. 75 ..
76 7c 75 76 79 76 76 79 76 75 7c 76
77 7b 76 75 78 74 74 78 75 76 7b 77
78 7a 78 74 77 74 74 77 74 78 7a 78
76 79 76 73 75 73 73 75 73 76 79 76
75 78 74 72 73 72 72 73 72 74 78 75
74 77 74 .. 72 .. .. 72 .. 74 77 74
73 75 73 .. 71 .. .. 71 .. 73 75 73
72 73 72 .. .. .. .. .. .. 72 73 72
.. 72 .. .. .. .. .. .. .. .. 72 ..
.. 71 .. .. .. .. .. .. .. .. 71 ..
""",
    62: """
.. .. .. .. .. 75 76 .. .. .. .. ..
.. .. .. 75 75 7c 7b 76 75 .. .. ..
.. .. 76 7c 75 7b 7a 75 7c 76 .. ..
.. 75 77 7b 76 7a 79 76 7b 77 75 ..
76 7c 78 7a 78 77 78 78 7a 78 7c 76
77 7b 76 79 76 76 77 76 79 76 7b 77
78 7a 75 78 74 77 77 74 78 75 7a 78
76 79 74 77 74 75 75 74 77 74 79 76
75 78 73 75 73 73 72 73 75 73 78 75
74 77 72 73 72 72 71 72 73 72 77 74
73 75 73 72 .. 71 .. .. 72 73 75 73
72 73 72 71 .. .. .. .. 71 72 73 72
.. 72 .. .. .. .. .. .. .. .. 72 ..
.. 71 .. .. .. .. .. .. .. .. 71 ..
""",
}

# --- The bolts --------------------------------------------------------------------------------------------------------
# A bolt: its middle x, the y of its head's tip (the top edge of its first row) and of its tail's tip (the bottom edge
# of its last row), its half-width, and its core: "wedge" (a 4-pixel bolt's plasma in its head) or "spine" (a 3-pixel
# bolt's bright middle).


class Bolt:
    def __init__(self, x, nose, tail, half_width, core):
        self.x, self.nose, self.tail, self.w, self.core = x, nose, tail, half_width, core


def wide(x, first_row, last_row):
    return Bolt(x, TOP - first_row, TOP - last_row - 1, 2.0, "wedge")


def narrow(x, first_row, last_row):
    return Bolt(x, TOP - first_row, TOP - last_row - 1, 1.5, "spine")


# name: (sprite, its bolts, what it is)
MODELS = [
    ("shot_pulse", 58, [wide(0.0, 0, 10)], "one bolt"),
    ("shot_pulse_2", 59, [wide(-3.0, 0, 10), wide(3.0, 0, 10)], "two bolts side by side"),
    ("shot_pulse_3", 60, [wide(0.0, 0, 10), wide(-4.0, 2, 12), wide(4.0, 2, 12)], "three bolts, the outer two behind"),
    ("shot_pulse_4", 165, [narrow(-1.5, 0, 10), narrow(1.5, 0, 10), narrow(-4.5, 3, 13), narrow(4.5, 3, 13)],
     "four narrow bolts, the outer pair behind"),
    ("shot_pulse_5", 62, [Bolt(0.0, TOP, TOP - 11, 1.75, "wedge"), narrow(-2.5, 1, 11), narrow(2.5, 1, 11),
                          narrow(-4.5, 3, 13), narrow(4.5, 3, 13)], "five bolts in an arrowhead"),
]

# The body: its height over its half-width (round on top), where along it (t: 0 the head's tip, 1 the tail's) the
# head's cap ends and the tail begins to taper, the taper's power (under 1: fuller), the width just behind the head and
# where the taper begins (fractions of the half-width), and the points round its upper half (a 4-pixel bolt's; a
# 3-pixel bolt's).
DEPTH = 0.92
CAP, TAPER, TAPER_POWER = 0.12, 0.64, 0.85
SWELL = (0.24, 1.0, 0.94)  # (where, width there, width where the taper begins)
SEGMENTS = {"wedge": 8, "spine": 6}
# The fire's heat (in shades of ramp 7): along the bolt's middle line (the head hottest, cooling down the body to the
# tail's dark red, as the sprite's middle columns go; never rising towards the tail), less towards its sides (minus
# ACROSS(t) times the square of the way out: the sprite's edge columns are cooler down the body, so the colours lie in
# chevrons pointing back), its middle line on the sprite's hottest column.
ALONG = ((0.0, 10.2), (0.15, 10.2), (0.3, 9.3), (0.45, 8.0), (0.6, 6.8), (0.72, 5.4), (0.84, 3.9), (0.93, 2.6),
         (1.0, 1.2))
ACROSS = ((0.0, 0.6), (0.15, 1.2), (0.35, 2.6), (0.6, 2.6), (0.85, 1.6), (1.0, 0.6))
# The fire's bands: (lowest heat, palette index, emission strength in the palette colour), ramp 7 from the dark red of
# the tail's tip to the orange-yellow round the core (the flat underside, never seen, the darkest's); low glows (the
# bloom and the glow add on top). The surface is built so that the bands' borders are rings of its mesh (no face is
# cut). Every band is a material, and every material of a model a draw of its own: keep them few.
FIRE_BANDS = [(-99.0, 0x73, 0.24), (2.8, 0x74, 0.28), (4.0, 0x75, 0.31), (5.0, 0x76, 0.34), (6.0, 0x77, 0.38),
              (7.0, 0x78, 0.42), (7.9, 0x79, 0.46), (8.9, 0x7a, 0.5)]
FIRE_ROUGHNESS = 0.5
# The flame tongues along the borders: how many across the top, how far they reach back and forth (t), how much each
# border's are turned against the one before (radians).
TONGUES, TONGUE_REACH, TONGUE_TURN = 2.5, 0.03, 1.9
# Rings between the bands' borders: how many in the head (before the first border; fractions of the way, closer at the
# tip for the cap's roundness), between borders further apart than GAP (t), and in the tail after the last border.
HEAD_RINGS = (0.05, 0.18, 0.45)
GAP = 0.17
TAIL_RINGS = (0.45, 0.8)
# The cores: where the tip is behind the head's tip, the length, the half-width (for a bolt of half-width 2 or 1.5) and
# how far it stands out of the fire's top (pixels), the rings along it and its points round; its bands along it
# ((from t, palette index, emission strength)): pale yellow at its front, yellow behind, hotter than the fire.
WEDGE = (0.4, 3.9, 1.3, 0.42)
SPINE = (0.45, 6.4, 0.58, 0.26)
WEDGE_BANDS = ((0.0, 0x7e, 0.62), (0.4, 0x7d, 0.6))
SPINE_BANDS = ((0.0, 0x7e, 0.62), (0.3, 0x7d, 0.6))
CORE_ROUGHNESS = 0.4
CORE_SEGMENTS, CORE_RINGS = 6, (0.04, 0.15, 0.32, 0.5, 0.66, 0.85)


# --- Building ---------------------------------------------------------------------------------------------------------

def half_width(bolt, t):
    """The bolt's half-width at t (0 the head's tip, 1 the tail's)."""
    where, top, taper_start = SWELL
    t = min(max(t, 0.0), 1.0)
    if t < CAP:
        u = t / CAP
        f = math.sqrt(max(0.0, 1.0 - (1.0 - u) ** 2)) * top
    elif t < where:
        f = top
    elif t < TAPER:
        f = top + (taper_start - top) * smoothstep(where, TAPER, t)
    else:
        f = taper_start * ((1.0 - t) / (1.0 - TAPER)) ** TAPER_POWER
    return bolt.w * f


def top_height(bolt, x, y):
    """The height of the bolt's fire over z = 0 at (x, y) (0 outside it)."""
    t = (bolt.nose - y) / (bolt.nose - bolt.tail)
    if not 0.0 <= t <= 1.0:
        return 0.0
    w = half_width(bolt, t)
    u = (x - bolt.x) / w if w > 1e-6 else 2.0
    return w * DEPTH * math.sqrt(1.0 - u * u) if abs(u) < 1.0 else 0.0


def hot_x(bolt, heat):
    """The x of the bolt's hottest line: the sprite's hottest column a pixel and a half behind the head, most of the
    way."""
    y = bolt.nose - 1.5
    xs = [bolt.x + bolt.w * (i / 10.0 - 0.5) for i in range(11)]
    best = max(xs, key=lambda x: heat(x, y))
    return bolt.x + 0.6 * (best - bolt.x)


_along = monotone([p[0] for p in ALONG], [p[1] for p in ALONG])
_across = monotone([p[0] for p in ACROSS], [p[1] for p in ACROSS])


def fire_heat(bolt, middle, angle, t):
    """The fire's heat at the angle round the top (0 the right side, pi / 2 the top, pi the left side) and t."""
    w = max(half_width(bolt, t), 0.25)
    u = min(abs(w * math.cos(angle) + bolt.x - middle) / w, 1.3)
    return _along(t) - _across(t) * u * u


def border(bolt, middle, angle, value, steps=400):
    """Where along the bolt (t) the heat at that angle first falls below value (the heat never rises towards the
    tail); 1 if it never does."""
    previous = 0.0
    for i in range(1, steps + 1):
        t = i / steps
        if fire_heat(bolt, middle, angle, t) < value:
            lo, hi = previous, t
            for _ in range(30):
                mid = (lo + hi) / 2
                if fire_heat(bolt, middle, angle, mid) < value:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2
        previous = t
    return 1.0


def tongues(bolt, k, angle):
    """How far (t) the k-th border reaches back at the angle: flames licking back down the body, TONGUES across the
    top, each border's a little turned against the one before (and each bolt's against its neighbours)."""
    phase = TONGUE_TURN * k + bolt.x * 1.3 + bolt.nose * 0.7
    return TONGUE_REACH * math.sin(TONGUES * angle + phase) * math.sin(angle) ** 0.5


def ring_curves(bolt, middle, angles):
    """The rings of the bolt's mesh as curves t(angle): its bands' borders (with their flame tongues), rings between
    them and in the head (from the tip to the first border) and the tail (from the last border to the tip). Returns
    [(t per angle, band of the faces after it)]: the head's band is the hottest."""
    borders = [[border(bolt, middle, a, lowest) for a in angles] for lowest, _, _ in reversed(FIRE_BANDS[1:])]
    for k, line in enumerate(borders):
        for j, a in enumerate(angles):
            line[j] = min(max(line[j] + tongues(bolt, k, a), 0.02), 0.985)
    # (each border behind the one before it at every angle)
    for k in range(1, len(borders)):
        for j in range(len(angles)):
            borders[k][j] = max(borders[k][j], borders[k - 1][j] + 0.012)
    hottest = len(FIRE_BANDS) - 1
    curves = []
    first = borders[0]
    for f in HEAD_RINGS:
        curves.append(([f * t for t in first], hottest))
    for i, line in enumerate(borders):
        band = hottest - 1 - i
        curves.append((line, band))
        following = borders[i + 1] if i + 1 < len(borders) else None
        if following is not None:
            gap = max(b - a for a, b in zip(line, following))
            extra = int(gap / GAP)
            for j in range(1, extra + 1):
                f = j / (extra + 1)
                curves.append(([a + (b - a) * f for a, b in zip(line, following)], band))
    last = borders[-1]
    for f in TAIL_RINGS:
        curves.append(([a + (1.0 - a) * f for a in last], 0))
    return curves


def mesh_from_rings(name, rings, faces_material, tips, materials, under):
    """A closed mesh through rings of points (each the upper half of a section, from +x over the top to -x, closed along
    the bottom), fans to the tip points at either end; faces_material[i]: the material of the faces between ring i and
    i + 1 (the next to last: the head's fan, the last: the tail's), the flat underside's faces materials[under]."""
    count = len(rings[0])
    verts = [tuple(p) for ring in rings for p in ring] + [tuple(tips[0]), tuple(tips[1])]
    first_tip, last_tip = len(verts) - 2, len(verts) - 1
    faces, mats = [], []
    for i in range(len(rings) - 1):
        a0, b0 = i * count, (i + 1) * count
        for j in range(count):
            jj = (j + 1) % count
            faces.append((a0 + j, a0 + jj, b0 + jj, b0 + j))
            mats.append(under if jj == 0 else faces_material[i])
    for j in range(count):
        jj = (j + 1) % count
        faces.append((jj, j, first_tip))
        mats.append(under if jj == 0 else faces_material[-2])
        base = (len(rings) - 1) * count
        faces.append((base + j, base + jj, last_tip))
        mats.append(under if jj == 0 else faces_material[-1])
    obj = k.mesh_object(name, verts, faces)
    for m in materials:
        obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, mats):
        poly.material_index = m
    k.recalc_normals(obj)
    return obj


def sheath(name, bolt, heat, materials):
    """The bolt's fire: rings along it on the bands' borders, each point at its own t round the section."""
    count = SEGMENTS[bolt.core]
    angles = [math.pi * j / count for j in range(count + 1)]
    middle = hot_x(bolt, heat)
    length = bolt.nose - bolt.tail
    curves = ring_curves(bolt, middle, angles)
    rings = []
    for ts, _ in curves:
        ring = []
        for a, t in zip(angles, ts):
            w = max(half_width(bolt, t), 0.03)
            ring.append(Vector((bolt.x + w * math.cos(a), bolt.nose - t * length, w * DEPTH * math.sin(a))))
        rings.append(ring)
    # The band of the faces after each ring, then of the head's fan (the hottest) and of the tail's (the coolest).
    bands = [curves[i][1] for i in range(len(curves) - 1)] + [len(FIRE_BANDS) - 1, 0]
    obj = mesh_from_rings(name, rings, bands, ((bolt.x, bolt.nose, 0.0), (bolt.x, bolt.tail, 0.0)), materials, 0)
    return k.smooth(obj, 70)


def core(name, bolt, heat, materials):
    """The wedge (a 4-pixel bolt's) or the spine (a 3-pixel bolt's): a teardrop along the bolt, round at its front,
    pointing back, standing out of the fire's top, its middle on the bolt's hottest line; its bands along it."""
    behind, length, w0, lift = WEDGE if bolt.core == "wedge" else SPINE
    bands = WEDGE_BANDS if bolt.core == "wedge" else SPINE_BANDS
    w0 *= bolt.w / (2.0 if bolt.core == "wedge" else 1.5)
    front = bolt.nose - behind
    cx = hot_x(bolt, heat)
    ts = sorted(set(CORE_RINGS) | {b[0] for b in bands[1:]})
    rings = []
    for t in ts:
        y = front - t * length
        u = t / 0.3
        f = math.sqrt(max(0.0, 1.0 - (1.0 - u) ** 2)) if t < 0.3 else ((1.0 - t) / 0.7) ** 0.9
        w = max(w0 * f, 0.03)
        h = top_height(bolt, cx, y) + lift * f
        angles = [math.pi * j / CORE_SEGMENTS for j in range(CORE_SEGMENTS + 1)]
        rings.append([Vector((cx + w * math.cos(a), y, h * math.sin(a))) for a in angles])

    def band_at(t):
        return max(i for i, b in enumerate(bands) if t >= b[0] - 1e-9)
    faces = [band_at(t) for t in ts[:-1]] + [0, len(bands) - 1]
    obj = mesh_from_rings(name, rings, faces, ((cx, front, 0.0), (cx, front - length, 0.0)), materials,
                          len(materials) - 1)
    return k.smooth(obj, 80)


def build_model(name, sprite, bolts):
    rows = grid(SPRITES[sprite])
    heat = Heat(shades(rows, 7), TOP, sigma=(0.55, 0.7))
    fire = [lit(f"pulse_fire_{index:02x}", index, glow, roughness=FIRE_ROUGHNESS) for _, index, glow in FIRE_BANDS]
    parts = []
    for i, bolt in enumerate(bolts):
        parts.append(sheath(f"{name}_bolt{i}", bolt, heat, fire))
        bands = WEDGE_BANDS if bolt.core == "wedge" else SPINE_BANDS
        core_mats = [lit(f"pulse_core_{index:02x}", index, glow, roughness=CORE_ROUGHNESS) for _, index, glow in bands]
        parts.append(core(f"{name}_core{i}", bolt, heat, core_mats))
    return triangulate(parts)


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_view(prefix, objects):
    """The model as the game's camera sees it (20 degrees from straight down, from the bottom of the screen), lit by the
    game's sun, with a three-quarter view (mk.preview's top and three-quarter views first)."""
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    data = bpy.data.cameras.new("game")
    data.type = "ORTHO"
    data.ortho_scale = 16.0
    cam = bpy.data.objects.new("game", data)
    tilt = math.radians(20.0)
    cam.location = (0.0, -60.0 * math.sin(tilt), 60.0 * math.cos(tilt))
    cam.rotation_euler = (tilt, 0.0, 0.0)
    scene.collection.objects.link(cam)
    sun = bpy.data.lights.new("game_sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("game_sun", sun)
    sun_obj.rotation_euler = Vector((0.6, -0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)
    scene.camera = cam
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun_obj)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, sprite, bolts, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, sprite, bolts)
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): {what}")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots.png"), [(sprite, turn(0), f"shots {sprite}")],
                         move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
