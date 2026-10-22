"""The hangar of ASTEROID2, ASTCITY and AST. CITY (sheet S sprites 13 15 above 51 53 above 89 91, 2x2 each: one 48 x 84
picture; ground layer; enemies 326-331, armour 30 each) and its broken far end (S 17 and 55), polished (2026-10-22, round
37; it replaces wave3_u_hangar.py's hangar, a heightfield over the pixels painted pixel by pixel, the numbers in blocks,
and wave3_ap_ast.py's damaged look made from it). models.cfg: model roof_hangar_tl / _tr / _ml / _mr / _bl / _br and
roof_hangar_tl_damaged / _tr_damaged enemies/*.glb origin (unchanged); the eight sprite lines get height=-4.

Where the levels put it (the level events, tools/content/tyrevents.py): ASTEROID2 t6264 (x 162), ASTCITY t2233 (x 138),
AST. CITY t3940 (x 186): event 6 puts 326 (S 13) at (x, y - 84) and 327 (S 15) at (x + 24, y - 84), event 12 puts 330
331 (51 53) at y - 56 and 328 329 (89 91) at y - 28: the sheet's picture whole, one link. The maps paint the hangar's
ruin under its lower four sprites (tiles 421 422 above 431 432: its floor burnt, red streaks, a pale rim on its left and
a kerb and ribbed apron before it); the top row is plain floor (372) or rubble (380 388). The sprites' own kerb (rows
66-70), apron (71-83), left rim (columns 4-5) and rubble round the building are the map's floor: left out. When it is
shot, the top pieces turn to their damaged look (dgr 17 and 55, dlevel -1: they stay), the other four die (one link) and
the map's ruin shows. Not animated; no other enemy shows these sprites; none is another's pixels mirrored or recoloured;
no episode 6 level makes it (VAULT takes only ASTEROID2's boss). Terrain under it: flat (ASTEROID2, AST. CITY) or -5..1
(ASTCITY): height=-4 sets it on the terrain, its walls reach SKIRT below it.

As the sprites and their 4x upscales draw it (ramp 0's greys; columns and rows of the picture): a long hangar with a
pitched roof, its ridge up the screen in the middle (between columns 23 and 24), outlined in black (columns 6 and 41,
the far edge); the left slope lit (0x09, its ridge edge 0x0a-0x0b), the right one darker (0x07); its far end drawn as a
low chevron (row 11 at the ridge to row 17 at the eaves), its near edge as one too (row 52 to 57) with a pale fascia;
both slopes clad in panels: four a slope at the far end (rows 12-19) and at the near end (rows 45-52) between seams
running up the roof, a seam across each band; between them "92" on the left slope and "26" on the right, painted large
and turned on their sides (0x0d, 0x0a-0x0b). Under the near edge the gable front (columns 7-40, rows 52-65) in shadow:
black under the eaves, then a barred gate (columns 19-27: four bars, a top rail, a jamb), a dark doorway beside it
(28-33) under a lintel, raised wall panels left and right. The damaged top (17 55): the far end broken open, a black
gash beside the ridge on the right slope (columns 28-33) with a red-hot crack in it (column 31), the left slope caved in
by the ridge (columns 15-20), soot and an ember at its foot.

Built for the game's camera in the picture's plane (polish_asteroid_kit: x, y as the picture draws them, z up; sheared
y - z tan 20 afterwards, so the camera sees every point where the sprites draw it): the body one solid grid (its columns
at the seams and the ridge, its rows at the foot, the gable's band, the roof's near edge, the panel bands and the far
edge) whose top is the gable front rising from the ground (row 66) to the roof's near edge and then the two roof planes,
eaves EAVES and ridge RIDGE high (after the shear the front leans back about 20 degrees and the roof's edges are nearly
straight: a pitched-roof hangar about 46 px long); walls down to SKIRT. On it, laid on the roof's planes: the ridge cap,
the fascia along the near edge, dark eave and barge trims (the outline), the seams of the panel bands, the numbers as
thin decals (their outlines traced from the upscale, NUMBERS); on the gable front the gate (a black backing, bars, a
rail, a jamb), the doorway (black, a lintel, jambs) and the wall panels. Painted in the sprites' greys, a little lighter
where the game's light reads darker (the front faces away from the sun). The damaged whole is the same with a fine roof
grid in its far half, sunk where the damaged sprites draw the gash and the hole (DAMAGE, ragged by a fixed NOISE) and
broken off along its lower edge, sagging into the ruin (BREAK: the lower pieces are gone when it shows), its parts there
split finer so they bend with it; the faces there sooted and charred, a smudge of soot round them, the crack's faces
and three embers on the broken edge glowing a dull red (0x72 0.35, 0x75 0.5), the numbers burnt off where it is broken.
The side and far walls (never seen from the game's camera but at the screen's edges) are painted as walls in shade.

Cut along the sprites' edges in the picture's plane (x = 0; y = 14 and -14) into the six pieces (the cuts capped in the
body's inside grey, the damaged ones' charred), sheared, each moved so its sprite's middle is its origin: tl (-12, 28),
tr (12, 28), ml (-12, 0), mr (12, 0), bl (-12, -28), br (12, -28) in the picture's coordinates (column c's left edge
x = c - 24, row r's top edge y = 42 - r).

Replaces wave3_u_hangar.py (all of it: the hangar was all it built; its kit wave3_u_kit.py and pixels wave3_u_art.py go
with it: nothing else imports them) and wave3_ap_ast.py (all of it: the damaged look was all it built), with
wave3_ap_art.py's HANGAR_DMG (only it read that).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline from above
in the picture's plane against its sprite's own pixels), --preview <prefix>, --only <model,...>, --whole <prefix> (the
uncut hangar and its damaged far end as GLBs, sheared).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroid_kit as ak  # noqa: E402

# --- The picture's outline (pixel edges in the plane) --------------------------------------------------------------------
WALL_X = 17.0                   # the gable front's and the side walls' half width (columns 7-40)
EAVE_X = 17.5                   # the eave trims' middle (the outline columns 6 and 41 reach 18)
RIDGE, EAVES = 20.0, 10.5       # the roof's heights over the ground in the plane
SKIRT = -4.0                    # the walls reach this far under the ground
FOOT = -24.0                    # the gable front's foot (row 66's top edge)
GATE_TOP = -16.0                # the front's band of doors and panels: from the foot up to here (row 58)
NEAR_BAND, FAR_BAND = 7.0, 7.5  # the panel bands' depth from the near and the far edge
SEAMS = (4.5, 9.0, 13.5)        # the seams of the bands (|x|)
LIFT = 0.035                    # the decals over the roof


def y_far(x):
    """The roof's far edge (the outline's top: row 11 over columns 22-24, a row lower every three columns, row 17 at the
    eaves; its apex half a pixel left of the ridge, as the sprites draw it)."""
    return 31.0 - abs(x + 0.5) / 3.0


def y_near(x):
    """The roof's near edge (below the fascia: row 52 at the ridge, row 57 at the eaves)."""
    return -10.0 - 5.0 * abs(x) / 17.0


def roof_z(x):
    return RIDGE - (RIDGE - EAVES) * min(1.0, abs(x) / 18.0)


def front_z(x, y):
    """The gable front: from the ground at the foot up to the roof's near edge."""
    return roof_z(x) * max(0.0, (y - FOOT) / (y_near(x) - FOOT))


def surface(x, y):
    return roof_z(x) if y >= y_near(x) else front_z(x, y)


def roof_normal(side):
    """The roof plane's normal on the left (side -1) or the right (1) of the ridge."""
    s = (RIDGE - EAVES) / 18.0
    return Vector((side * s, 0.0, 1.0)).normalized()


# The numbers, traced from the 4x upscale (iso-lines of its brightness halfway between the slope's grey and the paint's):
# "92" on the left slope, "26" on the right, each glyph an outline, the 9's and the 6's holes inside them.
NUMBERS = [
    [(-16.62, -1.62), (-16.40, 4.62), (-16.33, 5.12), (-16.12, 5.49), (-15.38, 5.60), (-13.12, 5.61), (-12.62, 5.54),
     (-12.12, 5.21), (-10.88, 4.10), (-8.38, 2.47), (-7.62, 2.21), (-6.88, 2.27), (-5.88, 2.61), (-5.47, 3.12),
     (-5.06, 6.38), (-5.15, 6.88), (-5.31, 7.12), (-6.88, 7.73), (-7.13, 8.12), (-7.10, 8.38), (-6.88, 8.68),
     (-6.12, 8.94), (-4.38, 8.65), (-3.62, 8.62), (-3.54, 8.38), (-3.70, 7.62), (-3.72, 4.12), (-4.19, 2.12),
     (-4.47, 1.62), (-4.88, 1.19), (-6.38, 0.43), (-7.12, 0.38), (-8.12, 0.53), (-8.88, 0.81), (-10.62, 1.74),
     (-12.38, 2.98), (-13.60, 3.62), (-14.12, 3.83), (-14.62, 3.82), (-14.86, 3.62), (-14.92, 3.38), (-14.99, 0.62),
     (-15.12, -0.62), (-15.38, -1.88), (-16.12, -2.59), (-16.38, -2.58), (-16.57, -2.12)],
    [(-16.43, 10.88), (-16.38, 12.96), (-16.07, 14.38), (-16.25, 15.38), (-16.12, 15.83), (-15.88, 16.03),
     (-15.38, 16.07), (-15.12, 15.99), (-14.88, 15.77), (-14.71, 15.38), (-14.70, 14.38), (-14.99, 13.38),
     (-15.04, 12.62), (-14.94, 11.88), (-14.65, 10.88), (-14.38, 10.42), (-14.12, 10.26), (-13.38, 10.20),
     (-12.53, 10.62), (-12.09, 11.12), (-11.87, 11.88), (-11.68, 13.62), (-11.46, 14.38), (-11.34, 15.38),
     (-10.95, 16.12), (-10.38, 16.76), (-9.62, 17.28), (-8.38, 17.85), (-6.12, 18.69), (-5.38, 18.78), (-4.88, 18.72),
     (-4.38, 18.52), (-3.93, 18.12), (-3.67, 17.38), (-3.67, 15.62), (-4.15, 12.12), (-4.45, 11.38), (-5.12, 10.82),
     (-5.62, 10.66), (-6.38, 10.73), (-7.75, 10.62), (-8.66, 10.38), (-11.12, 9.45), (-15.12, 8.59), (-16.12, 8.84),
     (-16.38, 9.04)],
    [(-10.05, 13.12), (-9.97, 13.88), (-10.01, 15.12), (-9.78, 15.62), (-9.38, 16.06), (-8.53, 16.38), (-6.38, 16.81),
     (-5.88, 16.68), (-5.38, 16.20), (-5.12, 15.50), (-5.08, 14.88), (-5.38, 13.38), (-5.62, 12.86), (-6.12, 12.56),
     (-7.12, 12.24), (-9.12, 12.02), (-9.62, 12.12), (-9.88, 12.36)],
    [(2.11, 14.38), (2.12, 16.69), (2.23, 17.62), (2.45, 18.38), (3.12, 19.28), (3.38, 19.42), (4.12, 19.56),
     (4.38, 19.50), (4.88, 19.11), (5.88, 18.72), (7.12, 17.98), (7.62, 17.58), (8.64, 16.38), (9.72, 14.38),
     (10.57, 13.62), (10.87, 12.88), (11.88, 11.30), (12.88, 10.25), (13.62, 9.72), (13.88, 9.67), (13.94, 9.88),
     (14.01, 11.88), (13.90, 14.12), (14.00, 14.62), (14.25, 14.88), (14.62, 14.94), (15.43, 14.88), (15.88, 14.73),
     (16.05, 14.38), (16.15, 11.88), (16.12, 9.55), (15.90, 7.88), (15.62, 7.65), (15.38, 7.60), (14.62, 7.60),
     (14.12, 7.70), (13.12, 8.02), (12.09, 8.88), (11.08, 10.12), (9.26, 12.88), (8.62, 14.04), (8.12, 14.19),
     (7.66, 15.38), (6.62, 16.91), (6.38, 17.15), (5.12, 17.35), (4.62, 17.30), (4.33, 17.12), (4.00, 16.38),
     (3.91, 14.62), (3.96, 14.38), (4.52, 13.88), (5.03, 13.12), (5.80, 12.38), (5.86, 11.88), (5.62, 11.59),
     (5.12, 11.43), (4.62, 11.50), (3.62, 12.06), (2.38, 13.28), (2.12, 13.83)],
    [(2.16, 6.38), (2.21, 7.38), (2.49, 8.12), (3.62, 8.95), (4.12, 8.97), (6.62, 8.39), (10.77, 6.38), (13.88, 5.07),
     (15.12, 4.18), (15.78, 3.88), (15.93, 3.62), (16.15, 1.38), (16.06, -0.38), (15.88, -0.98), (15.61, -1.38),
     (15.28, -1.62), (14.62, -1.94), (13.88, -2.02), (13.62, -1.90), (13.41, -1.62), (13.14, -0.62), (13.20, -0.38),
     (13.56, 0.12), (13.77, 0.62), (13.96, 1.88), (13.95, 2.88), (13.89, 3.12), (13.62, 3.46), (12.62, 3.88),
     (12.12, 3.97), (11.62, 3.90), (11.03, 3.38), (10.74, 2.62), (10.62, 0.90), (10.38, 0.53), (10.12, 0.44),
     (9.12, 0.42), (7.12, 0.58), (4.38, 1.63), (3.50, 2.38), (2.81, 3.12), (2.50, 3.62), (2.19, 4.88)],
    [(3.89, 5.62), (3.92, 6.12), (4.12, 6.62), (4.62, 6.92), (5.12, 7.02), (6.62, 6.85), (8.60, 5.88), (9.05, 5.38),
     (9.15, 4.88), (8.96, 3.62), (8.60, 2.62), (8.42, 2.38), (8.12, 2.18), (7.62, 2.12), (5.38, 2.77), (4.88, 3.02),
     (4.54, 3.38), (4.12, 4.15)],
]

# The gable front's parts (plan boxes x0, x1, y0, y1 in the plane, how far they stand out, their material).
FRONT = [
    ("gate_back", (-5.0, 3.3, -23.9, -16.7), (-0.25, 0.12), "dark"),
    ("gate_rail", (-5.2, 3.6, -17.7, -16.3), (0.0, 0.55), "bar"),
    ("gate_jamb", (3.2, 4.0, -23.9, -16.5), (0.0, 0.5), "panel"),
    ("door_back", (4.2, 9.9, -23.5, -18.0), (-0.25, 0.1), "dark"),
    ("door_lintel", (3.9, 10.4, -18.0, -16.3), (0.0, 0.5), "panel"),
    ("door_jamb", (9.8, 10.4, -23.6, -18.0), (0.0, 0.45), "panel"),
    ("panel_l1", (-16.7, -13.9, -23.6, -18.6), (0.0, 0.45), "panel"),
    ("panel_l2", (-13.5, -10.3, -23.6, -18.6), (0.0, 0.45), "panel"),
    ("panel_l3", (-9.9, -5.8, -23.6, -18.6), (0.0, 0.45), "panel"),
    ("band_l", (-16.7, -5.8, -18.2, -16.4), (0.0, 0.35), "panel"),
    ("panel_r1", (10.8, 13.8, -23.6, -19.4), (0.0, 0.45), "panel"),
    ("panel_r2", (14.2, 16.7, -23.6, -19.4), (0.0, 0.45), "panel"),
    ("band_r", (10.8, 16.7, -19.0, -16.4), (0.0, 0.35), "panel"),
]
BARS = (-4.5, -2.5, -0.5, 1.5)           # the gate's bars (x)

PIECES = [("roof_hangar_tl", 13, (-24.0, 0.0, 14.0, 42.0)), ("roof_hangar_tr", 15, (0.0, 24.0, 14.0, 42.0)),
          ("roof_hangar_ml", 51, (-24.0, 0.0, -14.0, 14.0)), ("roof_hangar_mr", 53, (0.0, 24.0, -14.0, 14.0)),
          ("roof_hangar_bl", 89, (-24.0, 0.0, -42.0, -14.0)), ("roof_hangar_br", 91, (0.0, 24.0, -42.0, -14.0))]
DAMAGED = [("roof_hangar_tl_damaged", 17, (-24.0, 0.0, 14.0, 42.0)),
           ("roof_hangar_tr_damaged", 55, (0.0, 24.0, 14.0, 42.0))]

# The damaged far end (S 17 55, rows 11-27): where its sprites draw the roof broken (the gash and the crack beside the
# ridge, the hole in the left slope, the ember at its foot): ellipses of the plane (centre x, y; radii; turn in degrees;
# how deep the roof sinks there), ragged by NOISE; along its lower edge (where the lower pieces were) the roof is broken
# off and sags into the ruin (BREAK: from y0 down to the edge, how deep); the crack's glowing line (x, y from, y to).
DAMAGE = [((6.6, 21.0), (2.6, 7.6), -4.0, 4.8),      # the gash (columns 28-33, rows 14-27)
          ((7.4, 26.5), (1.6, 3.0), 0.0, 3.6),       # its top, under the far edge
          ((-5.6, 21.5), (2.3, 6.6), 6.0, 1.6),      # the left slope caved in by the ridge (columns 15-20)
          ((-7.0, 15.4), (3.2, 1.8), 0.0, 1.3)]      # the burnt hole at its foot (rows 25-27)
BREAK = (17.0, 14.0, 4.2)
CRACK = (7.5, 15.0, 28.0)                            # the red-hot crack (column 31, rows 14-27)
EMBERS = [(-3.5, 15.6, 0.8), (9.4, 15.2, 0.7), (-12.5, 14.8, 0.6)]   # embers glowing on the broken edge (x, y, r)


def materials(damaged=False):
    def m(name, index, metallic=0.3, roughness=0.55, glow=0.0, glow_index=None):
        return ak.pal("hangar_" + name, index, metallic, roughness, glow, glow_index)
    out = {"roof": m("roof", 0x09, 0.3, 0.5), "roof_r": m("roof_r", 0x08, 0.3, 0.5), "seam": m("seam", 0x07),
           "ridge": m("ridge", 0x0b, 0.35, 0.45), "trim": m("trim", 0x02, 0.25, 0.6),
           "number": m("number", 0x0d, 0.25, 0.5), "number_r": m("number_r", 0x0c, 0.25, 0.5),
           "wall": m("wall", 0x07), "gable": m("gable", 0x04), "panel": m("panel", 0x0b),
           "bar": m("bar", 0x0a, 0.4, 0.45), "dark": m("dark", 0x01, 0.1, 0.8), "inside": m("inside", 0x03, 0.2, 0.7),
           "side": m("side", 0x05)}
    if damaged:
        out.update({"soot": m("soot", 0x03, 0.1, 0.8), "char": m("char", 0x01, 0.05, 0.9),
                    "smudge": m("smudge", 0x05, 0.15, 0.75),
                    "ember": m("ember", 0x72, 0.0, 0.6, 0.35, 0x74), "hot": m("hot", 0x75, 0.0, 0.5, 0.5, 0x76)})
    return out


# --- The damage ----------------------------------------------------------------------------------------------------------

def noise(x, y):
    """A smooth ragged value (0.1 to 1), the same every run."""
    return 0.55 + 0.25 * math.sin(1.9 * x + 0.7 * y) + 0.2 * math.sin(1.1 * x - 1.7 * y + 0.8)


def damage_at(x, y):
    """How deep the damaged roof sinks at a point of the plane (0 where it is whole)."""
    d = 0.0
    n = noise(x, y)
    for (cx, cy), (rx, ry), turn, depth in DAMAGE:
        a = math.radians(turn)
        grow = 0.85 + 0.3 * n
        u = ((x - cx) * math.cos(a) + (y - cy) * math.sin(a)) / (rx * grow)
        v = (-(x - cx) * math.sin(a) + (y - cy) * math.cos(a)) / (ry * grow)
        r = u * u + v * v
        if r < 1.0:
            d = max(d, depth * (0.75 + 0.5 * n) * (1.0 - r) ** 0.6)
    y0, y1, depth = BREAK
    if y < y0:
        t = min(1.0, (y0 - y) / (y0 - y1))
        d = max(d, depth * (0.5 + 0.5 * noise(1.7 * x, 3.1)) * t * t)
    return d


def soot_at(x, y):
    """Whether a point lies in the soot round the broken parts."""
    for (cx, cy), (rx, ry), turn, depth in DAMAGE:
        a = math.radians(turn)
        u = ((x - cx) * math.cos(a) + (y - cy) * math.sin(a)) / (rx * 1.45)
        v = (-(x - cx) * math.sin(a) + (y - cy) * math.cos(a)) / (ry * 1.25)
        if u * u + v * v < 1.0:
            return True
    return y < BREAK[0] + 1.5 * noise(x, 0.0)


def crack_at(x, y):
    cx, y0, y1 = CRACK
    if not (y0 <= y <= y1):
        return 0.0
    return max(0.0, 1.0 - abs(x - cx - 0.25 * math.sin(y * 0.9)) / 0.7)


# --- The body ----------------------------------------------------------------------------------------------------------

def body(m, damaged):
    """The hangar's body: one grid solid, its top the gable front and the two roof planes (finer in its far half when
    damaged: sunk there)."""
    if damaged:
        xs = [round(-WALL_X + 0.5 * i, 3) for i in range(int(2 * WALL_X / 0.5) + 1)]
    else:
        xs = [-WALL_X] + [-s for s in SEAMS[::-1]] + [0.0] + list(SEAMS) + [WALL_X]
    # rows: (y(x), z(x)) along each column
    rows = [lambda x: (FOOT, 0.0),
            lambda x: (GATE_TOP, front_z(x, GATE_TOP)),
            lambda x: (y_near(x), roof_z(x)),
            lambda x: (y_near(x) + NEAR_BAND, roof_z(x))]
    if damaged:
        n = 64
        for i in range(1, n + 1):
            rows.append(lambda x, t=i / n: (y_near(x) + NEAR_BAND + t * (y_far(x) - 0.8 - FAR_BAND - y_near(x) -
                                                                         NEAR_BAND), roof_z(x)))
        top_band = 12
        for i in range(1, top_band + 1):
            rows.append(lambda x, t=i / top_band: (y_far(x) - 0.8 - FAR_BAND * (1 - t), roof_z(x)))
    else:
        rows += [lambda x: (y_far(x) - 0.8 - FAR_BAND, roof_z(x)), lambda x: (y_far(x) - 0.8, roof_z(x))]
    top = []
    for row in rows:
        line = []
        for x in xs:
            y, z = row(x)
            if damaged and y > y_near(x) + 0.01:
                z -= damage_at(x, y)
            line.append((x, y, z))
        top.append(line)
    obj = ak.grid_solid("hangar_body", top, SKIRT, m["roof"])

    def pick(c, n):
        if n.z < -0.5:
            return m["inside"]
        if abs(n.z) < 0.2 and (abs(c.x) > WALL_X - 0.01 or c.y > y_far(c.x) - 1.0):
            return m["side"]
        if c.y < y_near(c.x) - 0.02:
            return m["wall"] if c.y < GATE_TOP else m["gable"]
        slope = m["roof"] if c.x < 0.0 else m["roof_r"]
        if damaged:
            return paint_damage(m, c) or slope
        return slope
    mk.paint(obj, pick)
    return obj


def paint_damage(m, c):
    """A damaged roof face's paint by how deep it sank, the crack and the embers (None: whole)."""
    if c.y < 10.0:
        return None
    d = damage_at(c.x, c.y)
    if crack_at(c.x, c.y) > 0.35 and d > 1.0:
        return m["hot"] if crack_at(c.x, c.y) > 0.75 else m["ember"]
    for x, y, r in EMBERS:
        if (c.x - x) ** 2 + (c.y - y) ** 2 < r * r and d > 0.3:
            return m["hot"] if (c.x - x) ** 2 + (c.y - y) ** 2 < 0.3 * r * r else m["ember"]
    if d > 1.8:
        return m["char"]
    if d > 0.15:
        return m["soot"]
    if soot_at(c.x, c.y):
        return m["smudge"]
    return None


# --- The trim ----------------------------------------------------------------------------------------------------------

def on_roof(x, y, lift=0.0):
    return Vector((x, y, roof_z(x) + lift))


def trims(m):
    parts = []
    # The ridge cap, the fascia along the near edge, the eave and barge trims (the sprites' outline).
    parts.append(ak.beam("ridge_cap", (0.0, y_near(0.0), RIDGE + 0.05), (0.0, y_far(0.0) - 0.45, RIDGE + 0.05),
                         ak.round_profile(0.75, 10, 0.55, below=0.5), (0, 0, 1), m["ridge"]))
    for side in (-1, 1):
        nrm = roof_normal(side)
        x1 = side * EAVE_X
        parts.append(ak.beam("fascia%d" % side, on_roof(0.0, y_near(0.0) + 0.42, 0.0),
                             on_roof(x1, y_near(x1) + 0.42, 0.0), ak.rect_profile(0.95, 0.32, 0.14, below=0.9),
                             nrm, m["ridge"]))
        parts.append(ak.beam("eave%d" % side, on_roof(x1, y_near(x1) + 0.05, 0.0), on_roof(x1, y_far(x1) - 0.4, 0.0),
                             ak.rect_profile(1.0, 0.3, 0.12, below=1.4), nrm, m["trim"]))
        parts.append(ak.beam("barge%d" % side, on_roof(0.0, y_far(0.0) - 0.42, 0.0),
                             on_roof(x1, y_far(x1) - 0.42, 0.0), ak.rect_profile(0.85, 0.3, 0.12, below=1.0),
                             nrm, m["trim"]))
        # The panel bands: seams up the roof and one across each band.
        for s in SEAMS:
            x = side * s
            parts.append(ak.beam("seam_far%d_%g" % (side, s), on_roof(x, y_far(x) - 0.85), on_roof(x, y_far(x) - 0.8 -
                                                                                               FAR_BAND),
                                 ak.rect_profile(0.5, 0.22, 0.1, below=0.2), nrm, m["seam"]))
            parts.append(ak.beam("seam_near%d_%g" % (side, s), on_roof(x, y_near(x) + 0.9),
                                 on_roof(x, y_near(x) + NEAR_BAND), ak.rect_profile(0.5, 0.22, 0.1, below=0.2), nrm,
                                 m["seam"]))
        xe = side * (WALL_X - 0.2)
        parts.append(ak.beam("band_far%d" % side, on_roof(0.0, y_far(0.0) - 0.8 - FAR_BAND),
                             on_roof(xe, y_far(xe) - 0.8 - FAR_BAND), ak.rect_profile(0.5, 0.22, 0.1, below=0.2), nrm,
                             m["seam"]))
        parts.append(ak.beam("band_near%d" % side, on_roof(0.0, y_near(0.0) + NEAR_BAND),
                             on_roof(xe, y_near(xe) + NEAR_BAND), ak.rect_profile(0.5, 0.22, 0.1, below=0.2), nrm,
                             m["seam"]))
    return parts


def front(m):
    """The gable front's gate, doorway and panels, standing out of its surface."""
    parts = []
    for name, (x0, x1, y0, y1), (z0, z1), mat in FRONT:
        outline = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        parts.append(ak.prism_on(name, outline, front_z, z0, z1, m[mat]))
    for i, x in enumerate(BARS):
        outline = [(x - 0.36, -23.9), (x + 0.36, -23.9), (x + 0.36, -17.4), (x - 0.36, -17.4)]
        parts.append(ak.prism_on("gate_bar%d" % i, outline, front_z, 0.0, 0.5, m["bar"]))
    return parts


def numbers(m, damaged):
    """The numbers as decals on the roof (the right slope's a shade darker, as the sprites paint its light)."""
    obj = ak.decal("numbers", NUMBERS, lambda x, y: roof_z(x), LIFT, m["number"])
    mk.paint(obj, lambda c, n: m["number_r"] if c.x > 0.0 else None)
    return obj


def deform(objects, damaged):
    """The damaged roof: every part's points over the roof sunk with it."""
    if not damaged:
        return
    for obj in objects:
        mesh = obj.data
        for v in mesh.vertices:
            if v.co.y > y_near(v.co.x) + 0.5:
                v.co.z -= damage_at(v.co.x, v.co.y)
        mesh.update()


def burn(objects, m):
    """The damaged parts' faces painted where the roof is broken; the decals' faces there burnt off."""
    for obj in objects:
        if obj.name.startswith("numbers"):
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            gone = [f for f in bm.faces if damage_at(*f.calc_center_median()[:2]) > 0.05 or
                    soot_at(*f.calc_center_median()[:2])]
            bmesh.ops.delete(bm, geom=gone, context="FACES")
            bm.to_mesh(obj.data)
            bm.free()
            continue
        mk.paint(obj, lambda c, n: paint_damage(m, c))


def dense(objects, size):
    """Splits the faces of the objects reaching into the damage until no edge is much longer than size (they bend with
    the damaged roof)."""
    for obj in objects:
        if not any(soot_at(v.co.x, v.co.y) or damage_at(v.co.x, v.co.y) > 0 for v in obj.data.vertices) and \
                not any(soot_at(*p) for p in sample_along(obj)):
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for _ in range(6):
            long = [e for e in bm.edges if e.calc_length() > size]
            if not long:
                break
            bmesh.ops.subdivide_edges(bm, edges=long, cuts=1, use_grid_fill=False)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bm.to_mesh(obj.data)
        bm.free()


def sample_along(obj, step=0.5):
    """Points along an object's edges (whether a long part crosses the damage between its ends)."""
    out = []
    mesh = obj.data
    for e in mesh.edges:
        a, b = mesh.vertices[e.vertices[0]].co, mesh.vertices[e.vertices[1]].co
        n = max(1, int((b - a).length / step))
        out += [(a.x + (b.x - a.x) * i / n, a.y + (b.y - a.y) * i / n) for i in range(n + 1)]
    return out


def build_whole(damaged):
    m = materials(damaged)
    solids = [body(m, damaged)] + trims(m) + front(m)
    decals = [numbers(m, damaged)]
    if damaged:
        dense(solids[1:] + decals, 0.7)
    deform(solids[1:] + decals, damaged)
    if damaged:
        burn(solids[1:] + decals, m)
    for o in solids:
        k.smooth(o, 30)
    bpy.context.view_layer.update()
    return m, solids, decals


# --- The sprites' own pixels -----------------------------------------------------------------------------------------------

def piece_mask(box, sheets, sprite):
    """A piece's own pixels: its sprite's pixels on the building (the roof, columns 6-41 down to its near edge, and the
    gable front, columns 7-40 down to row 65), the map's floor round it left out."""
    pix = k.sprite_mask(os.path.join(sheets, "enemy_S.png"), sprite)
    x0, y1 = box[0], box[3]
    rows = []
    for r in range(28):
        row = []
        for c in range(24):
            x, y = x0 + c + 0.5, y1 - r - 0.5
            roof = abs(x) < 18.0 and y >= y_near(x) - 0.01
            gable = abs(x) < WALL_X and y >= FOOT
            row.append(pix[r][c] and (roof or gable))
        rows.append(row)
    return rows


# --- Build -------------------------------------------------------------------------------------------------------------

def export_pieces(specs, damaged, options, out, results):
    m, solids, decals = build_whole(damaged)
    if "whole" in options:
        view = ak.copy_all(solids + decals, "_w")
        ak.shear_to_camera(view)
        ak.triangulate(view)
        mk.export(view, options["whole"] + ("hangar_damaged.glb" if damaged else "hangar.glb"))
        ak.remove(view)
    cap = m["char"] if damaged else m["inside"]
    for name, sprite, box in specs:
        parts = ak.piece(solids, box, cap, decals)
        ak.hide(solids + decals)
        centre = ((box[0] + box[1]) / 2, (box[2] + box[3]) / 2)
        mask = piece_mask(box, options["check"], sprite) if "check" in options else None
        obj, score = ak.finish(name, parts, centre, out, options, mask, label="%s (S %d)" % (name, sprite))
        results.append((name, score))
        ak.remove([obj])
        ak.hide(solids + decals, False)
    ak.remove(solids + decals)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    results = []
    for damaged, specs in ((False, PIECES), (True, DAMAGED)):
        chosen = [s for s in specs if not only or s[0] in only]
        if not chosen and not ("whole" in options and not only):
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        export_pieces(chosen, damaged, options, out, results)
    for name, score in results:
        if score is not None:
            print("overlap %-26s %.3f" % (name, score))


if __name__ == "__main__":
    build()
