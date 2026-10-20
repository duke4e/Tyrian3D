"""The grey and red machine of CORE, BRAINIAC, the ICE, LAVA and SIDE exits, LAVA RUN, ICESECRET and UNDERDELI (and
COLLECTOR in episode 6): sheet ^ (x5e in models.cfg) sprites 83 85 87 89 above 121 123 125 127, 2x2 each: one 96 x 56
picture; enemies 174-181 (one frame each). Polished 2026-10-20; it replaces wave3_i.py's machine_whole() (regions of the
sprite's pixels raised into blobs). models.cfg: model core_machine_tl / _tcl / _tcr / _tr / _bl / _bcl / _bcr / _br
... origin; sprite x5e 83 core_machine_tl yaw=0 height=-4 and so on (the same for all eight; see below).

The levels always place the eight pieces as one picture and move them together: 174-177 (83-89) at x, x + 24, x + 48,
x + 72, 28 pixels above 178-181 (121-127) at the same x (CORE's events 100-4900, BRAINIAC 3500, LAVA EXIT 1300 and
2100, ICESECRET 900 and 1100, SIDE EXIT 150 and 200: sky enemies, most of them coming down the screen with vy 1; LAVA
RUN 250 and 450, ICE EXIT 3400 and CORE 2300-4900 also as top enemies (vy 2); UNDERDELI 350 and 1550 on the ground
(ground2 slots, no speed of their own)). So it is mostly a flying machine: models drawn at their origin stand with
their base (z = 0) on their layer (the sky enemies' 22 pixels, the top enemies' 38), on the ground in UNDERDELI (the
ground enemies' 4, lifted onto the terrain together, compute_object_lifts). It is built with its base on z = 0 and
kept low (its stacks reach 11.9 pixels); height=-4 sets it on the floor in UNDERDELI and, in the sky, keeps it under
background 3 (32: 18 + 11.9).

As the sprites draw it (the 96 x 56 picture's columns and rows; the right half is the left half mirrored about the
middle of column 48 and darkened, in the shadow of the light from the upper left): down the middle a red core column
(columns 45-51): a head (rows 12-17), a glossy body lit down its left (rows 17-21), a neck with two dark sockets
either side (row 22), a collar (rows 23-25) and a narrow rod (rows 26-30) down to an axle across the middle (row 32);
either side of it a big red chest plate (columns 32-44 of rows 17-27) and below that a red plate bending down to the
left (columns 24-39 of rows 26-34); above them the grey shoulder (columns 14-40 of rows 10-18), a dark oval red vent in
it (columns 23-28 of rows 13-16), a dark outer step (columns 14-21) and a tall stack (columns 29-38 of rows 4-17, its
lit face down columns 33-35, a cap at its top and a pipe to the left, row 8); under the shoulder the arm (columns
11-32 of rows 19-30) with a dark red strip along its top edge (rows 19-21) and two red studs, ending in a post
(columns 6-10 of rows 19-31); under the arm the leg (columns 14-31 of rows 31-48) with a knee ball (columns 16-19 of
rows 36-40), a lit thigh and a shin down to its foot; across the middle a grey pelvis (columns 35-61 of rows 29-34,
lit at its ends) with the axle on it; under it a red claw hanging from a knuckle either side (columns 38-41 of rows
36-47) beside a grey ball (columns 34-37 of rows 39-43) and in the middle a dark ribbed belly (columns 42-54 of rows
34-46). Black outlines between the parts: a dark chassis under them all.

Built as a CAD modeller would (polish_machine_kit): plates and blocks are prisms of their plan with sloping tops
(wedges), bevelled, flat faces kept flat; the vent's well and the stack's mouth are cut by booleans; tubes, balls, the
claw and the core are lofted or lathed. The upright parts the sprite draws in its oblique view (the stacks, the posts)
lean back up the screen, so that from above they cover what the sprite draws and the game's slanted camera sees their
fronts. The left half is built and mirrored; the chassis, the core, the pelvis, the axle and the belly are built
whole. The whole machine is then cut along the sprites' edges (x = -24, 0, 24 and y = 0; polish_arch.py's cut(): the
pieces keep the whole's shading across the cuts), each piece moved so its sprite's centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the base (z = 0); the whole's
origin is the middle of the picture (the corner where 85, 87, 123 and 125 meet): column c's left edge is x = c - 48,
row r's top edge y = 28 - r.

Replaces wave3_i.py's machine: remove MACH, machine_label(), machine_whole(), machine_piece(), the
w.WHOLES["core_machine"] entry and the loop registering core_machine_tl ... _br, the core_machine lines of its
docstring (and "core_machine," in its --whole usage line), and wave3_i_art.py's MACHINE (only machine_whole() reads
it), so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_x5e.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <name,...> (pieces to export; "none": none), --whole <file.glb> (the uncut machine as well, for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_orb_red import band_split  # noqa: E402

AXIS_X = 0.5                    # the machine is symmetric about the middle of the picture's column 48
MID_C = 48.5                    # that middle as a column
# name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)
PIECES = [("core_machine_tl", 83, (-48.0, -24.0, 0.0, 28.0)), ("core_machine_tcl", 85, (-24.0, 0.0, 0.0, 28.0)),
          ("core_machine_tcr", 87, (0.0, 24.0, 0.0, 28.0)), ("core_machine_tr", 89, (24.0, 48.0, 0.0, 28.0)),
          ("core_machine_bl", 121, (-48.0, -24.0, -28.0, 0.0)), ("core_machine_bcl", 123, (-24.0, 0.0, -28.0, 0.0)),
          ("core_machine_bcr", 125, (0.0, 24.0, -28.0, 0.0)), ("core_machine_br", 127, (24.0, 48.0, -28.0, 0.0))]
SPRITE_CELLS = {83: (0, 0), 85: (24, 0), 87: (48, 0), 89: (72, 0), 121: (0, 28), 123: (24, 28), 125: (48, 28),
                127: (72, 28)}  # top left corners in the 96 x 56 picture


def XE(c):
    """The left edge of the picture's column c (fractions allowed)."""
    return c - 48.0


def YE(r):
    """The top edge of the picture's row r."""
    return 28.0 - r


def P(c, r):
    return (XE(c), YE(r))


def ccw(pts):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]


def plan(points):
    """A plan given in pixel edges (c, r), counter-clockwise seen from above."""
    return ccw([P(c, r) for c, r in points])


def whole_plan(left_path):
    """A plan symmetric about the middle from the path of its left half (pixel edges, from the middle at one end to
    the middle at the other)."""
    left = [P(c, r) for c, r in left_path]
    right = [(2 * AXIS_X - x, y) for x, y in reversed(left[1:-1])]
    return ccw(left + right)


# --- The measures (the left half; the right half is their mirror image) ------------------------------------------
# The chassis under everything (its left half's outline, from the middle at the top to the middle at the bottom).
CHASSIS = [(MID_C, 17.6), (44.2, 17.6), (41.4, 17.2), (41.4, 11.4), (38.0, 9.8), (31.2, 9.8), (30.6, 10.6),
           (17.8, 10.6), (17.8, 12.4), (14.8, 12.8), (14.6, 17.6), (15.6, 18.6), (13.2, 19.4), (11.6, 21.0),
           (11.4, 28.4), (13.6, 30.8), (15.2, 32.0), (16.6, 34.8), (15.8, 36.2), (15.6, 40.2), (18.6, 41.4),
           (18.8, 45.0), (21.6, 47.6), (24.6, 48.4), (27.6, 47.6), (29.4, 45.4), (30.2, 41.6), (32.0, 41.2),
           (33.6, 43.2), (37.4, 46.8), (41.8, 46.6), (44.4, 46.2), (MID_C, 46.8)]
CHASSIS_Z = 2.4
# The shoulder: the dark outer step (vent slots across it), the housing (its brow running out over the step) and the
# vent in it.
STEP = [(14.4, 12.6), (22.6, 12.6), (22.6, 18.4), (15.4, 18.4), (14.4, 17.4)]
STEP_Z = 4.0
STEP_SLOTS = [13.9, 15.3, 16.7]
HOUSING = [(17.4, 10.3), (31.0, 10.3), (31.4, 9.5), (37.8, 9.5), (40.9, 11.0), (40.9, 17.4), (40.0, 18.4), (22.4, 18.4),
           (22.4, 12.6), (17.4, 12.6)]
HOUSING_Z = (7.4, 6.2)          # its top at the back (row 10) and at the front (row 18.4)
BROW = [(17.4, 10.3), (31.0, 10.3), (31.4, 9.5), (32.2, 9.5), (32.2, 12.4), (17.4, 12.4)]
BROW_UP = 0.6                   # how far the brow stands over the housing
VENT = (25.9, 14.6, 3.3, 2.15)  # the vent's centre (column, row) and half-width, half-height
VENT_FLOOR = 3.8                # its well's floor
# The stack on the housing: its foot (column, row, z) and top, its half-width across and half-depth; the cap on top
# with its mouth; the pipe out of the cap to the left.
STACK_FOOT = (34.6, 16.2, 5.2)
STACK_TOP = (34.5, 8.4, 10.0)
STACK_HALF = (2.7, 2.0)
CAP = [(28.6, 8.4), (30.8, 4.4), (38.8, 4.4), (39.0, 8.6), (36.4, 9.4), (30.2, 9.4)]
CAP_Z = (8.6, 10.6, 11.2)       # its underside, its top at the front (row 9.4) and at the back (row 4.4)
MOUTH = (31.2, 37.8, 5.0, 7.8, 0.9)  # columns, rows, depth
PIPE = [(29.6, 8.3, 9.9), (26.6, 8.35, 9.0), (24.0, 8.4, 8.2)]
PIPE_R = 0.85
# The arm: the beam, the red strip along its top edge, the studs; the post at its end.
DECK = [(11.0, 20.8), (29.6, 20.8), (33.4, 22.2), (33.4, 26.4), (29.2, 26.2), (27.0, 25.4), (11.0, 25.4)]
DECK_Z = (5.8, 5.3)             # its top at the back (row 21) and the front (row 25.4)
LOWER_STEP = [(11.0, 24.6), (27.8, 24.6), (25.0, 29.0), (12.8, 29.4), (11.0, 28.0)]
LOWER_STEP_Z = 4.4
DECK_SEAM = 22.8                # a seam across the deck (column)
DECK_PANEL = [(23.8, 21.6), (29.2, 21.6), (32.4, 22.8), (32.4, 25.4), (23.8, 25.0)]
STRIP = [(13.6, 18.6), (28.2, 18.6), (29.8, 20.2), (29.0, 22.4), (14.6, 22.4), (13.6, 21.4)]
STRIP_Z = 6.4
STUDS = [(15.9, 23.0, 1.0), (21.9, 23.4, 0.9)]
POST_FOOT = (8.6, 30.4, 0.8)
POST_TOP = (8.6, 23.0, 10.2)
POST_R = 2.25
# The plates: the chest plate (the outer and the inner part, a crease between) and the lower plate.
CHEST = [(36.6, 16.8), (39.0, 16.8), (40.8, 18.0), (44.9, 18.6), (44.9, 24.6), (43.8, 25.4), (43.8, 28.0), (39.8, 28.0),
         (39.4, 25.8), (34.6, 25.8), (33.0, 23.6), (31.6, 22.4), (31.6, 19.4), (33.0, 17.8), (35.6, 17.8)]
CHEST_Z = (8.0, 5.2)            # its top at its inner edge (column 44.9) and its outer edge (31.6)
# Its two armour panels standing on it, the crease between them (column 40.4).
CHEST_PANELS = [[(36.6, 16.8), (39.0, 16.8), (40.2, 17.6), (40.2, 25.8), (34.6, 25.8), (33.0, 23.6), (31.6, 22.4),
                 (31.6, 19.4), (33.0, 17.8), (35.6, 17.8)],
                [(40.6, 17.9), (44.9, 18.6), (44.9, 24.6), (43.8, 25.4), (43.8, 28.0), (40.6, 28.0)]]
PANEL_UP = 0.4                  # how far panels stand on what they lie on
LOWER = [(29.0, 25.9), (39.2, 25.9), (39.2, 27.9), (36.4, 28.2), (34.2, 30.2), (30.8, 31.4), (28.8, 32.8), (27.6, 34.6),
         (25.4, 34.4), (24.0, 32.8), (24.0, 30.0), (28.6, 29.6)]
LOWER_Z = (5.9, 4.8)            # its top at the chest (column 39) and at its lower left end (row 34)
# The leg: the dark hip housing, the thigh, the knee ball, the shin with its ridge, the piston.
HIP = [(13.4, 28.4), (25.8, 28.4), (34.8, 31.6), (34.8, 40.6), (27.8, 40.8), (24.0, 35.0), (16.2, 35.0), (13.4, 31.2)]
HIP_Z = 3.6
THIGH = [(16.0, 31.2), (25.8, 31.2), (26.8, 36.6), (22.4, 39.6), (16.8, 38.6)]
THIGH_TOP = [(25.8, 31.2, 5.8), (16.0, 31.2, 4.8), (22.4, 39.6, 4.2)]  # three points of its top (column, row, z)
KNEE = (17.6, 38.6, 3.6, 2.2)   # column, row, z, radius
SHIN = [(18.6, 40.0), (24.8, 37.4), (30.8, 38.8), (30.6, 44.0), (28.6, 47.8), (24.6, 49.0), (21.2, 47.6), (18.4, 43.4)]
SHIN_TOP = [(30.6, 38.8, 5.6), (18.4, 42.0, 3.7), (24.6, 49.0, 2.5)]  # three points of its top (column, row, z)
SHIN_RIDGE = [(24.0, 39.6), (26.0, 39.6), (26.2, 47.2), (23.8, 47.4)]
PISTON = [(23.4, 32.0, 5.4), (27.4, 40.6, 4.6)]
# The claw: its talon (column, row, z, radius from its root to its tip), the knuckle it hangs from, its ball.
CLAW = [(38.6, 36.2, 4.4, 1.5), (39.4, 38.8, 4.1, 1.95), (39.9, 41.8, 3.3, 1.8), (40.0, 44.6, 2.2, 1.3),
        (39.6, 47.5, 1.0, 0.3)]
KNUCKLE = [(35.2, 35.4), (41.4, 35.4), (41.6, 38.4), (35.2, 38.4)]
KNUCKLE_Z = 5.0
BALL = (35.8, 41.0, 2.8, 2.15)
# Across the middle (whole): the pelvis with the rod's slot, the axle on it, the belly with its ribs.
PELVIS = [(MID_C, 28.6), (35.0, 28.6), (35.0, 34.8), (MID_C, 34.8)]
PELVIS_Z = 6.0
PELVIS_LIT = 41.6               # its ends are lit out from this column (and its mirror)
ROD_SLOT = (46.4, 28.0, 31.4)   # the slot's left edge (and its mirror), its rows
AXLE = (40.8, 32.6, 6.0, 0.9)   # from column 40.8 to its mirror, row, axis height, radius
BELLY = [(MID_C, 33.8), (41.6, 33.8), (41.6, 43.6), (43.2, 45.6), (46.0, 46.8), (MID_C, 47.2)]
BELLY_Z = 5.2
RIBS = [-4.0, -2.0, 0.0, 2.0, 4.0]  # the belly's ribs, from the middle
# The core column: its hull along it (row, half-width, top above its axis, superellipse power): the head (rows
# 12.5-17), a groove, the round body (rows 17.5-21.5), the neck (row 22), the collar (rows 23-25.6); below its axis it
# reaches CORE_BOTTOM. The dark sockets round the neck (rows, radius) and the rod (rows, radius, axis height).
CORE_AXIS = 5.6
CORE_BOTTOM = 3.0
CORE_PROFILE = [(12.45, 2.4, 2.8, 3.4), (12.85, 3.2, 3.7, 3.6), (13.5, 3.5, 4.0, 3.8), (16.5, 3.5, 4.0, 3.8),
                (17.2, 3.1, 3.4, 3.0), (17.8, 3.35, 3.4, 2.7), (21.1, 3.35, 3.4, 2.7), (21.7, 2.5, 3.25, 2.4),
                (22.1, 1.9, 3.3, 2.4), (22.6, 1.9, 3.3, 2.4), (23.1, 3.6, 2.95, 3.0), (23.6, 4.3, 3.05, 3.4),
                (25.0, 4.3, 3.05, 3.4), (25.6, 3.2, 2.4, 2.8), (25.9, 1.8, 1.8, 2.2)]
CORE_SOCKET = (21.4, 23.3, 2.95)
CORE_ROD = (25.4, 31.0, 1.6, 5.0)


def materials():
    def mat(name, index, metallic=0.5, roughness=0.4):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "black": mat("cm_black", 0x01, 0.2, 0.6),
        "chassis": mat("cm_chassis", 0x02, 0.4, 0.55),
        "dark": mat("cm_dark", 0x03, 0.45, 0.5),
        "steel_dark": mat("cm_steel_dark", 0x05, 0.5, 0.42),
        "steel": mat("cm_steel", 0x07, 0.55, 0.38),
        "steel_lit": mat("cm_steel_lit", 0x09, 0.55, 0.34),
        "steel_light": mat("cm_steel_light", 0x0b, 0.55, 0.3),
        "red_dark": mat("cm_red_dark", 0x43, 0.35, 0.36),
        "red_mid": mat("cm_red_mid", 0x45, 0.35, 0.34),
        "red": mat("cm_red", 0x46, 0.35, 0.32),
        "plate": mat("cm_plate", 0x48, 0.35, 0.3),
        "red_light": mat("cm_red_light", 0x4a, 0.3, 0.26),
        "red_hi": mat("cm_red_hi", 0x4c, 0.25, 0.2),
    }


# --- Helpers -----------------------------------------------------------------------------------------------------

def slope(c0, z0, c1, z1, axis="x"):
    """A plane: z0 at column (axis x) or row (axis y) c0, z1 at c1, level the other way."""
    if axis == "x":
        a0, a1 = XE(c0), XE(c1)
        return lambda x, y: z0 + (z1 - z0) * (x - a0) / (a1 - a0)
    a0, a1 = YE(c0), YE(c1)
    return lambda x, y: z0 + (z1 - z0) * (y - a0) / (a1 - a0)


def block(name, outline, top, mat, bevel=0.4, segments=3, angle=35.0, bottom=0.0, chaikin=0, is_plan=False):
    """A wedge of a plan (pixel edges, or a plan in x, y with is_plan) under top(x, y) (a number or a plane),
    bevelled and shaded."""
    pts = outline if is_plan else plan(outline)
    if chaikin:
        pts = mk.chaikin(pts, chaikin)
    top_fn = top if callable(top) else (lambda x, y, t=top: t)
    body = mk.wedge(name, pts, bottom, top_fn, mat)
    if bevel > 0:
        mk.bevel(body, bevel, segments, angle)
    mk.shade(body, angle)
    return body


def paint_by_normal(obj, top=None, side=None, under=None, top_min=0.8, under_max=0.05, lit=None, lit_dir=None):
    """Faces facing up (normal z over top_min) get top, the downward ones under, the rest side (None: kept); with
    lit, the sides facing lit_dir (the upper left, the sun's side) get lit."""
    def pick(c, n):
        if top is not None and n.z > top_min:
            return top
        if under is not None and n.z < under_max:
            return under
        if lit is not None and n.dot(lit_dir or Vector((-0.6, 0.6, 0.5)).normalized()) > 0.55:
            return lit
        return side
    mk.paint(obj, pick)


def frame_ring(centre, u, v, hw, hh, power=3.0, segments=16):
    """A rounded-rectangle ring round centre in the plane of u and v (unit vectors)."""
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        px, pz = mk.superellipse_point(a, power)
        pts.append(centre + u * px * hw + v * pz * hh)
    return pts


def leaning(name, foot, top, half_across, half_depth, mat, power=3.2, segments=20, steps=10, taper=1.0,
            top_round=0.6):
    """A post or stack from foot to top (Vectors), its section a rounded rectangle across x (half_across) and
    along its lean (half_depth), tapering to taper at the top, its top end rounded over top_round."""
    axis = (top - foot)
    d = axis.normalized()
    u = Vector((1, 0, 0))
    v = d.cross(u).normalized()
    if v.z < 0:
        v = -v
    rings = []
    for i in range(steps + 1):
        t = i / steps
        f = 1 + (taper - 1) * t
        rings.append(frame_ring(foot + axis * t, u, v, half_across * f, half_depth * f, power, segments))
    for i in range(1, 4):
        a = (math.pi / 2) * i / 4
        s = math.cos(a)
        rings.append(frame_ring(top + d * top_round * math.sin(a), u, v, half_across * taper * (0.35 + 0.65 * s),
                                half_depth * taper * (0.35 + 0.65 * s), power, segments))
    obj = k.loft(name, rings, mat, start_point=foot, end_point=top + d * top_round)
    return k.smooth(obj, 50)


def sunk_strip(name, x0, x1, y0, y1, top, mat, depth=0.5, proud=0.06):
    """A thin dark strip on a surface (a seam or a slot): a box from top - depth to top + proud."""
    s = mk.box(name, x0, x1, y0, y1, top - depth, top + proud, mat)
    return s


def inset_plan(pts, d):
    """A counter-clockwise plan (x, y) moved in by d along its corners' bisectors."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        mv = n1 + n2
        mv = mv.normalized() if mv.length > 1e-6 else n1
        f = d / max(mv.dot(n1), 0.35)
        out.append((p1.x + mv.x * f, p1.y + mv.y * f))
    return out


def panel(name, outline, d, top, mat, up=None, bevel=0.3, side=None, lit=None):
    """An armour panel lying on a surface of height top(x, y): the plan (pixel edges) moved in by d, standing up
    above it (a thin plate sunk into it), bevelled; its sides side, lit sides lit."""
    pts = inset_plan(plan(outline), d)
    up = PANEL_UP if up is None else up
    body = mk.wedge(name, pts, 0.0, lambda x, y: top(x, y) + up, mat, bottom=lambda x, y: top(x, y) - 0.6)
    mk.bevel(body, bevel, 2, 35)
    mk.shade(body, 35)
    paint_by_normal(body, top=mat, side=side, lit=lit)
    return body


def plane_of(points):
    """The plane through three points (column, row, z), as a function z(x, y)."""
    return mk.plane(*[(XE(c), YE(r), z) for c, r, z in points])


def rivets(m, points, top, radius=0.36, mat=None):
    """Small domed rivets at (column, row) on a surface of height top(x, y)."""
    for c, r in points:
        x, y = P(c, r)
        mk.dome(f"rivet_{c}_{r}", (x, y), (radius, radius, radius * 0.7), top(x, y) - 0.03, mat or m["steel_light"], 10,
                3)


def tube_along_x(name, x0, x1, y, z, rad, mat, segments=18):
    xs = [x0, x0 + 0.3, x1 - 0.3, x1]
    fs = [0.8, 1.0, 1.0, 0.8]
    rings = []
    for x, f in zip(xs, fs):
        rings.append([Vector((x, y + rad * f * math.cos(2 * math.pi * j / segments),
                              z + rad * f * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    obj = k.loft(name, rings, mat)
    return k.smooth(obj, 50)


def tube_along_y(name, r0, r1, rad_x, rad_z, axis_z, mat, segments=28, steps=6, power=2.0):
    rings = [k.ring(YE(r0 + (r1 - r0) * i / steps), rad_x, rad_z, segments, z=axis_z, x=AXIS_X, power=power)
             for i in range(steps + 1)]
    return k.loft(name, rings, mat)


def glossy_bands(obj, m, low=0.2, high=0.85, hot=1.15):
    """The core's red, lit down its left: bands of the normal's lean towards the light."""
    values = [v.normal.z - 0.6 * v.normal.x for v in obj.data.vertices]
    band_split(obj, values, [(-9.0, m["red"]), (low, m["plate"]), (high, m["red_light"]), (hot, m["red_hi"])])
    k.smooth(obj, 50)


# --- The parts (left half) -----------------------------------------------------------------------------------------

def shoulder(m):
    """The dark outer step with slots across it; the housing, its top sloping down to the front, the vent's oval
    well cut into it, a dark red lens in the well on a black gasket."""
    step = block("step", STEP, STEP_Z, m["steel_dark"], bevel=0.45)
    paint_by_normal(step, side=m["dark"], top=m["steel_dark"])
    for i, r in enumerate(STEP_SLOTS):
        sunk_strip(f"step_slot{i}", XE(15.4), XE(21.6), YE(r + 0.35), YE(r - 0.35), STEP_Z, m["black"])
    body = mk.wedge("housing", plan(HOUSING), 0.0, slope(10.3, HOUSING_Z[0], 18.4, HOUSING_Z[1], "y"), m["steel"])
    cx, cy = P(VENT[0], VENT[1])
    hw, hh = VENT[2], VENT[3]
    well = mk.lathe("well_cut", [(1.0, VENT_FLOOR), (1.0, 12.0)], (cx, cy), None, 28, squash=(hw, hh))
    mk.boolean(body, well, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.65, 3, 35)
    mk.shade(body, 35)

    def pick(c, n):
        inside = ((c.x - cx) / (hw + 0.15)) ** 2 + ((c.y - cy) / (hh + 0.15)) ** 2 < 1.0
        if inside and c.z < HOUSING_Z[1] - 0.25:
            return m["dark"]
        if n.z > 0.8:
            return m["steel"]
        if n.z < 0.05:
            return m["dark"]
        if n.dot(Vector((-0.6, 0.6, 0.5)).normalized()) > 0.5:
            return m["steel_lit"]
        return m["steel_dark"]
    mk.paint(body, pick)
    housing_top = slope(10.3, HOUSING_Z[0], 18.4, HOUSING_Z[1], "y")
    brow = block("brow", BROW, lambda x, y: housing_top(x, y) + BROW_UP, m["steel_lit"], bevel=0.4, bottom=2.0)
    paint_by_normal(brow, top=m["steel_lit"], side=m["steel"], lit=m["steel_light"])
    rivets(m, [(19.0, 11.4), (30.4, 11.4)], lambda x, y: housing_top(x, y) + BROW_UP)
    rivets(m, [(23.6, 17.4), (39.8, 12.0), (39.8, 17.2)], housing_top)
    gasket = mk.lathe("vent_gasket", [(1.0, VENT_FLOOR - 0.1), (1.0, VENT_FLOOR + 0.45), (0.86, VENT_FLOOR + 0.6)],
                      (cx, cy), m["black"], 28, squash=(hw - 0.05, hh - 0.05))
    k.smooth(gasket, 40)
    mk.dome("vent_lens", (cx, cy), (hw - 0.45, hh - 0.45, 1.55), VENT_FLOOR + 0.1, m["red_dark"], 28, 6, power=2.4)


def stack(m):
    """The stack leaning back up the screen from the housing, its front lit; the cap on top with a dark mouth and
    grille bars; the pipe out of the cap's left side."""
    foot = Vector((*P(STACK_FOOT[0], STACK_FOOT[1]), STACK_FOOT[2]))
    top = Vector((*P(STACK_TOP[0], STACK_TOP[1]), STACK_TOP[2]))
    body = leaning("stack", foot, top, STACK_HALF[0], STACK_HALF[1], m["steel"], power=4.0, taper=0.9, top_round=0.3)
    mk.paint(body, lambda c, n: m["steel_lit"] if n.y < -0.35 and n.x > -0.6 else
             m["steel_dark"] if n.x > 0.6 else None)
    # Two ribs down its front face.
    d = (top - foot).normalized()
    v = d.cross(Vector((1, 0, 0))).normalized()
    if v.z < 0:
        v = -v
    for i, dx in enumerate((-1.1, 1.1)):
        a = foot + Vector((dx, 0, 0)) + v * (STACK_HALF[1] - 0.05) + d * 0.6
        b = top + Vector((dx * 0.9, 0, 0)) + v * (STACK_HALF[1] * 0.9 - 0.05) - d * 0.4
        rib = mk.tube(f"stack_rib{i}", [a, b], 0.32, m["steel_lit"], 8)
        k.smooth(rib, 50)
    z0, z_front, z_back = CAP_Z
    cap = mk.wedge("cap", plan(CAP), z0, slope(9.4, z_front, 4.4, z_back, "y"), m["steel"])
    c0, c1, r0, r1, depth = MOUTH
    mouth = mk.box("mouth_cut", XE(c0), XE(c1), YE(r1), YE(r0), z_back - depth, z_back + 3.0)
    mk.boolean(cap, mouth, "DIFFERENCE")
    mk.cleanup(cap)
    mk.bevel(cap, 0.45, 2, 35)
    mk.shade(cap, 35)

    def pick(c, n):
        if XE(c0) - 0.05 < c.x < XE(c1) + 0.05 and YE(r1) - 0.05 < c.y < YE(r0) + 0.05 and c.z < z_back - 0.12:
            return m["black"]
        if n.z > 0.8 or n.y < -0.5:
            return m["steel_lit"]
        if n.z < 0.05:
            return m["dark"]
        return None
    mk.paint(cap, pick)
    for i, r in enumerate((5.95, 6.85)):
        bar = mk.box(f"grille{i}", XE(c0) - 0.1, XE(c1) + 0.1, YE(r + 0.22), YE(r - 0.22), z_back - depth,
                     z_back - 0.25, m["steel_dark"])
        mk.bevel(bar, 0.08, 1, 35)
    pts = [Vector((XE(c), YE(r), z)) for c, r, z in PIPE]
    pipe = mk.tube("pipe", pts, PIPE_R, m["steel_lit"], 14)
    k.smooth(pipe, 50)
    end = pts[-1]
    d = (pts[-1] - pts[-2]).normalized()
    flange = leaning("pipe_flange", end - d * 0.2, end + d * 0.5, PIPE_R + 0.35, PIPE_R + 0.35, m["steel_dark"],
                     power=2.0, steps=1, top_round=0.15)
    k.smooth(flange, 40)


def arm(m):
    """The deck out to the post (a seam across it, rivets) above a lower step, the dark red strip along its top
    edge, the studs; the post at its end with two bands."""
    deck_top = slope(21.0, DECK_Z[0], 25.4, DECK_Z[1], "y")
    deck = block("deck", DECK, deck_top, m["steel_lit"], bevel=0.6)
    paint_by_normal(deck, top=m["steel_lit"], side=m["steel"], under=m["dark"], lit=m["steel_light"])
    step = block("arm_step", LOWER_STEP, LOWER_STEP_Z, m["steel"], bevel=0.55)
    paint_by_normal(step, top=m["steel"], side=m["steel_dark"], under=m["dark"], lit=m["steel_lit"])
    panel("deck_panel", DECK_PANEL, 0.0, deck_top, m["steel_lit"], up=0.3, side=m["steel"], lit=m["steel_light"])
    x = XE(DECK_SEAM)
    sunk_strip("deck_seam", x - 0.2, x + 0.2, YE(25.0), YE(21.6), deck_top(x, YE(21.6)) + 0.02, m["dark"], depth=0.8)
    rivets(m, [(12.2, 22.0), (12.2, 24.4), (31.4, 23.2), (31.4, 25.4)], deck_top)
    rivets(m, [(13.4, 27.6), (22.4, 27.8)], lambda x, y: LOWER_STEP_Z)
    strip = block("strip", STRIP, STRIP_Z, m["red_dark"], bevel=0.45)
    paint_by_normal(strip, top=m["red_dark"], side=m["red_dark"], top_min=0.85)
    panel("strip_panel", STRIP, 0.5, lambda x, y: STRIP_Z, m["red_mid"], up=0.3, side=m["red_dark"], lit=m["red"])
    for i, (c, r, rad) in enumerate(STUDS):
        x, y = P(c, r)
        z = deck_top(x, y)
        base = mk.lathe(f"stud_base{i}", [(rad + 0.3, z - 0.4), (rad + 0.3, z + 0.15), (rad + 0.1, z + 0.3)], (x, y),
                        m["dark"], 20)
        k.smooth(base, 40)
        mk.dome(f"stud{i}", (x, y), (rad, rad * 1.1, 0.8), z + 0.1, m["red"], 20, 5)
    foot = Vector((*P(POST_FOOT[0], POST_FOOT[1]), POST_FOOT[2]))
    top = Vector((*P(POST_TOP[0], POST_TOP[1]), POST_TOP[2]))
    post = leaning("post", foot, top, POST_R, POST_R * 0.95, m["steel"], power=2.2, taper=0.9, top_round=0.9)
    mk.paint(post, lambda c, n: m["steel_lit"] if n.x > 0.45 or n.z > 0.85 else None)
    d = (top - foot).normalized()
    cap = leaning("post_cap", top - d * 0.5, top + d * 0.35, POST_R * 0.9 + 0.25, POST_R * 0.86 + 0.25, m["steel_dark"],
                  power=2.2, steps=1, top_round=0.3)
    k.smooth(cap, 40)
    for i, t in enumerate((0.36, 0.62)):
        p = foot + (top - foot) * t
        band = leaning(f"post_band{i}", p - d * 0.45, p + d * 0.45, POST_R + 0.3, POST_R * 0.95 + 0.3,
                       m["steel_dark"], power=2.2, steps=1, top_round=0.05)
        k.smooth(band, 40)


def plates(m):
    """The chest plate (sloping down outwards), two armour panels on it with a crease between; the lower plate with
    its panel."""
    top = slope(44.9, CHEST_Z[0], 31.6, CHEST_Z[1])
    chest = block("chest", CHEST, top, m["red"], bevel=0.6)
    paint_by_normal(chest, top=m["red"], side=m["red_dark"], under=m["red_dark"], top_min=0.75, lit=m["plate"])
    for i, outline in enumerate(CHEST_PANELS):
        panel(f"chest_panel{i}", outline, 0.55, top, m["plate"], side=m["red"], lit=m["red_light"])
    x0, y0 = P(25.0, 34.0)
    x1, y1 = P(39.0, 26.0)

    def lower_top(x, y):
        t = max(0.0, min(1.0, ((x - x0) + (y - y0)) / ((x1 - x0) + (y1 - y0))))
        return LOWER_Z[1] + (LOWER_Z[0] - LOWER_Z[1]) * t
    lower = block("lower_plate", LOWER, lower_top, m["red_dark"], bevel=0.5)
    paint_by_normal(lower, top=m["red_mid"], side=m["red_dark"], under=m["red_dark"], top_min=0.8, lit=m["red"])
    panel("lower_panel", LOWER, 0.6, lower_top, m["red"], side=m["red_mid"], lit=m["plate"])


def legs(m):
    """The dark hip housing, the thigh, the knee ball, the shin with its ridge and the piston; the claw on its knuckle
    beside its ball."""
    block("hip", HIP, HIP_Z, m["dark"], bevel=0.5, chaikin=1)
    thigh = block("thigh", THIGH, plane_of(THIGH_TOP), m["steel_lit"], bevel=0.65, chaikin=1)
    paint_by_normal(thigh, top=m["steel_lit"], side=m["steel_dark"], under=m["dark"], lit=m["steel_light"])
    c, r, z, rad = KNEE
    mk.ball("knee", (XE(c), YE(r), z), (rad, rad, rad), m["steel"], 20, 10)
    shin_top = plane_of(SHIN_TOP)
    shin = block("shin", SHIN, shin_top, m["steel_dark"], bevel=0.6)
    paint_by_normal(shin, top=m["steel_dark"], side=m["steel_dark"], under=m["dark"], lit=m["steel"])
    panel("shin_panel", SHIN, 0.7, shin_top, m["steel"], side=m["steel_dark"], lit=m["steel_lit"])
    rivets(m, [(20.8, 43.0), (28.0, 42.0)], lambda x, y: shin_top(x, y) + PANEL_UP)
    ridge = block("shin_ridge", SHIN_RIDGE, lambda x, y: shin_top(x, y) + 0.9, m["steel_lit"], bevel=0.35, segments=2,
                  bottom=1.0)
    paint_by_normal(ridge, top=m["steel_lit"], side=m["steel"])
    (c0, r0, z0), (c1, r1, z1) = PISTON
    a, b = Vector((XE(c0), YE(r0), z0)), Vector((XE(c1), YE(r1), z1))
    rod = mk.tube("piston", [a, b], 0.7, m["steel_light"], 12)
    k.smooth(rod, 50)
    sleeve = mk.tube("piston_sleeve", [a - (b - a) * 0.05, a + (b - a) * 0.5], 1.05, m["steel_dark"], 14)
    k.smooth(sleeve, 50)
    # The claw: a talon of round sections hanging down the screen, its top lit, two dark joints round it.
    path = [(XE(c), YE(r), z, rad) for c, r, z, rad in CLAW]
    talon = mk.smooth_tube("claw", path, m["red"], 14, iterations=2)
    values = [v.normal.z for v in talon.data.vertices]
    band_split(talon, values, [(-9.0, m["red_dark"]), (0.25, m["red"]), (0.75, m["red_light"])])
    k.smooth(talon, 60)
    for i in (1, 2):
        (xa, ya, za, ra), (xb, yb, zb, _) = path[i], path[i + 1]
        p, q = Vector((xa, ya, za)), Vector((xb, yb, zb))
        dd = (q - p).normalized()
        joint = mk.tube(f"claw_joint{i}", [p - dd * 0.25, p + dd * 0.25], ra * 1.07, m["red_dark"], 16)
        k.smooth(joint, 40)
    knuckle = block("knuckle", KNUCKLE, KNUCKLE_Z, m["red"], bevel=0.6, chaikin=1)
    paint_by_normal(knuckle, top=m["red"], side=m["red_dark"], lit=m["plate"])
    c, r, z, rad = BALL
    mk.ball("claw_ball", (XE(c), YE(r), z), (rad, rad, rad), m["steel"], 20, 10)


# --- The parts across the middle (whole) ---------------------------------------------------------------------------

def chassis(m):
    """The dark chassis under everything: the black between the sprite's parts."""
    body = mk.prism("chassis", whole_plan(CHASSIS), 0.0, CHASSIS_Z, m["chassis"])
    mk.bevel(body, 0.4, 2, 35)
    mk.shade(body, 35)


def core(m):
    """The red core column: one hull lofted down it (the head, a groove, the glossy body, the neck, the collar), lit
    down its left in bands; black sockets either side of the neck; the rod below."""
    axis = CORE_AXIS
    rows = k.profile(CORE_PROFILE, 0.4)
    rings = []
    for r, hw, top, power in rows:
        rings.append(k.ring(YE(r), max(hw, 0.1), 1.0, 24, z=axis, x=AXIS_X, top=max(top, 0.1),
                            bottom=CORE_BOTTOM, power=power))
    first, last = CORE_PROFILE[0], CORE_PROFILE[-1]
    hull = k.loft("core", rings, m["plate"], start_point=(AXIS_X, YE(first[0]) + 0.15, axis + 0.4 * first[2]),
                  end_point=(AXIS_X, YE(last[0]) - 0.1, axis))
    k.smooth(hull, 45)
    glossy_bands(hull, m)
    r0s, r1s, rads = CORE_SOCKET
    socket = tube_along_y("core_socket", r0s, r1s, rads, rads, axis, m["black"], steps=1)
    k.smooth(socket, 40)
    r0d, r1d, radd, axisd = CORE_ROD
    rod = tube_along_y("core_rod", r0d, r1d, radd, radd, axisd, m["plate"], segments=20, steps=1)
    k.smooth(rod, 40)
    glossy_bands(rod, m, low=0.3, high=0.9, hot=9.0)


def middle(m):
    """The pelvis across the middle (the rod's slot cut into it, its ends lit), the axle on it and the dark ribbed
    belly."""
    body = mk.prism("pelvis", whole_plan(PELVIS), 0.0, PELVIS_Z, m["steel"])
    slot_c, r0, r1 = ROD_SLOT
    sx0, sx1 = XE(slot_c), 2 * AXIS_X - XE(slot_c)
    slot = mk.box("slot_cut", sx0, sx1, YE(r1), YE(r0) + 1.0, CORE_ROD[3] - 3.0, PELVIS_Z + 2.0)
    mk.boolean(body, slot, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.55, 3, 35)
    mk.shade(body, 35)
    lit_x0, lit_x1 = XE(PELVIS_LIT), 2 * AXIS_X - XE(PELVIS_LIT)

    def pick(c, n):
        if n.z > 0.8:
            return m["steel_lit"] if (c.x < lit_x0 or c.x > lit_x1) else m["steel"]
        if n.z < 0.05:
            return m["dark"]
        if sx0 - 0.05 < c.x < sx1 + 0.05 and c.y > YE(r1) - 0.05:
            return m["dark"]  # the slot's walls
        return m["steel_dark"]
    mk.paint(body, pick)
    for i, cols in enumerate(((35.0, 41.4), (2 * MID_C - 41.4, 2 * MID_C - 35.0))):
        outline = [(cols[0], 28.6), (cols[1], 28.6), (cols[1], 34.8), (cols[0], 34.8)]
        panel(f"pelvis_panel{i}", outline, 0.6, lambda x, y: PELVIS_Z, m["steel_lit"], up=0.3, side=m["steel"],
              lit=m["steel_light"])
    rivets(m, [(36.2, 29.8), (36.2, 33.8), (2 * MID_C - 36.2, 29.8), (2 * MID_C - 36.2, 33.8)],
           lambda x, y: PELVIS_Z + 0.3)
    c0, r, z, rad = AXLE
    tube_along_x("axle", XE(c0), 2 * AXIS_X - XE(c0), YE(r), z, rad, m["steel_light"])
    for i, cc in enumerate((c0 + 1.2, 2 * MID_C - c0 - 1.2)):
        x = XE(cc)
        tube_along_x(f"axle_hub{i}", x - 0.7, x + 0.7, YE(r), z, rad + 0.35, m["steel_dark"])
    outline = mk.chaikin(whole_plan(BELLY), 2)
    belly = mk.prism("belly", outline, 0.0, BELLY_Z, m["dark"])
    mk.bevel(belly, 2.0, 4, 30)
    mk.shade(belly, 30)
    for i, off in enumerate(RIBS):
        x = AXIS_X + off
        y0, y1 = YE(35.2), YE(44.6 - 0.45 * abs(off))
        rib = mk.box(f"rib{i}", x - 0.42, x + 0.42, y1, y0, BELLY_Z - 1.8, BELLY_Z + 0.4, m["steel_dark"])
        mk.bevel(rib, 0.3, 2, 35)
        mk.shade(rib, 35)
        paint_by_normal(rib, top=m["steel_lit"] if off <= 0 else m["steel"])


# --- Whole ---------------------------------------------------------------------------------------------------------

def mirror_half(objects):
    """A mirrored copy of the left half's parts about x = AXIS_X."""
    flip = Matrix.Translation((2 * AXIS_X, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(flip)
        copy.data.flip_normals()
        copy.data.update()


def build_whole():
    m = materials()
    shoulder(m)
    stack(m)
    arm(m)
    plates(m)
    legs(m)
    half = mk.meshes()
    for obj in half:
        mk.apply(obj)
    mirror_half(half)
    chassis(m)
    core(m)
    middle(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        if min(v.co.z for v in obj.data.vertices) < -1e-4:  # nothing below the base
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                         plane_co=(0, 0, 0), plane_no=(0, 0, -1), clear_outer=True)
            edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
            if edges:
                bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            bm.to_mesh(obj.data)
            bm.free()
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def whole_mask(sheet):
    mask = [[False] * 96 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    print("whole core machine: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_x5e.png") if "check" in options else None
    if sheet:
        mk.compare("whole (x5e 83 85 87 89 above 121 123 125 127)", mk.coverage(whole, 96, 56), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "core_machine_whole", whole, size=(96, 56), scale=8, distance=2.6)
    if "whole" in options:  # the uncut machine, for looking at
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (x5e %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
