"""The station of STATION and TIME WAR (sheet L: its two halves, each an axle end and four 2x2 sprites, and their damaged
looks) and TIME WAR's grey capsule (sheet L 1 3 above 39 41 above 77 79). The halves rebuilt (2026-10-23, round 38, the
quality redo) as machined parts: round 36's halves (one heightfield of each half's picture on polish_gyges_wall.Plate's
grid, painted by the sprites' shades, the damaged looks the same heightfield dented where the wreck is darker) read as
a dark noisy relief, their damaged looks as noise. The capsule is round 36's, kept as it was (its code below, its
models unchanged). Round 36's models replaced wave3_z_station.py, wave3_ap_station.py and wave2_e.py's station_end.

Where they appear (as round 36 found it): TIME WAR (episode 4) t120, event 7 (the top layer): half A, 659 (L 11) and
660 (13) at x 10 and 34, y -28, 661 (49) and 662 (51) at x 10 and 34, y 0, 663 (its axle end, 34) at x 58, y -14 (link
26); half B, 664 (its axle end, 24) at x 236, y -14, 665 (7) and 666 (9) at x 260 and 284, y -28, 667 (45) and 668 (47)
at y 0 (link 25): each half 72 x 56, its end beside the middle of its side, the ends facing each other across the
screen; t6950 event 25 makes them mortal (armour 254); the ends fire (guns 151, 152). STATION (episode 5) t3420 the
same at x 20 ... 68 and 266 ... 314, swaying up and down the screen (events 19). Every piece switches to its damaged
sprite and stays so when the station is killed (dlevel -1): 11 13 49 51 34 -> 87 89 125 127 110, 24 7 9 45 47 -> 100
83 85 121 123. The capsule: TIME WAR t110, event 15 (the sky), 653-658 at x 64 and 88 (y -56, -28, 0), and again at x
136 and 160. Half A is half B's pixels mirrored (L 11 = 9, 13 = 7, 49 = 47, 51 = 45, 34 = 24 mirrored, and so are
their damaged sprites); no other enemy shows these sprites (launched ones included).

As the sprites and their 4x upscales draw half B (its picture's columns and rows): a steel axle along its middle (row
27.5) from its end (24) at the left: a rounded knob (columns 4-7), a shaft (7-12), two flanges (12-14 and 17-19, 21
pixels tall) with a disc between them carrying a red lamp above and below (column 15, rows 19 and 36), a collar
(19-29) with red pads above and below (columns 20-23), a hub (29-33), a blue band in the neck (33-37), the housing
(37-50) with a saddle over it above and below (columns 42-50), a red clamp (50-55) and a rod (to 60) into the docking
block (60-72 of rows 22-33) with a panel in its face; a strut curving from the hub out to a bar above (rows 15-18)
and below, a stem from each bar to a solar panel straight up (columns 34-46 of rows 0-12) and down, a spike from each
bar's end to a panel at 45 degrees (columns 52-67 of rows 3-17 and the mirror image). The damaged sprites shoot the
panels away (the top one to a shard hanging from its stem, the upper diagonal one to a stub, the lower one gone, the
bottom one torn at its outer side), tear the dock off to a stub on the rod and burn the axle black in patches.

Built as such a machine, in half B's picture's plane (x, y as the sprites draw them, z up from the axle's axis: the
station floats, its parts reach under it), cut along the sprites' edges and sheared along the game camera's line of
sight (polish_fleet_walker.export_pieces): the axle's parts turned about its axis (AXLE: each its own solid and
material, the steps between them chamfered; the sections ZT high above the axis, ZB deep under it: never seen), the
lamps red ellipsoids on the disc, the pads red tubes on the collar, the saddles bevelled blocks, the struts, stems and
spikes smooth tubes, each panel a dark plate with four bevelled cells on it (the dark grooves between them) and a
bevelled frame round them, hanging a little from its stem (DROOP: the upper panels face the sun, the lower ones turn
from it, as the sprites light them), the dock a bevelled body under such a panel. Half A is half B mirrored. The
damaged look is the same machine broken: the panels' fragments (TOP_SHARD, DIAG_SHARD, BOTTOM_TORN: torn plates with
what is left of their frames and cells, bent down about their stems), the lower spike broken off short, the dock torn
to a stub (DOCK_STUB), soot on the axle, the saddles and the struts where the damaged sprites draw them burnt (BURNS: a
scorched rim round a sooty middle, the metal sunk a little there). Materials by part, palette indices of the sprites'
ramps: the axle's steel 0x0a, its darker parts 0x07, the flanges 0x0b, the struts 0x08, the frames, saddles and dock
0x0a, the cells 0x09, the grooves 0x04, the reds 0x76 (glowing 0.45) and 0x73 (0.3), the blue band 0x39 (0.25), the
wreck's soot 0x02 and scorch 0x05, the torn plates 0x03. Heights: the halves z -4.7 to 7.5 (the flanges; the collar
5.4, the housing 4.0, the saddles 4.5, the panels up to 3.2), as round 36's (-4.7 to 6.5). Deterministic: no random
numbers, no booleans; every mesh triangulated before the export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. A half's origin is
its picture's middle (its pixel edge 36, 28): column c's left edge is x = c - 36, row r's top edge y = 28 - r; its
pieces' origins are their sprites' middles: half B's end (-24, 0), 7 (0, 14), 9 (24, 14), 45 (0, -14), 47 (24, -14);
half A's end (24, 0), 13 (0, 14), 11 (-24, 14), 51 (0, -14), 49 (-24, -14). The capsule's origin is its picture's middle
(24, 42): its pieces' at (-12, 28), (12, 28), (-12, 0), (12, 0), (-12, -28), (12, -28).

models.cfg: unchanged (the model and sprite lines, yaw=0, origin on all the pieces and the axle ends).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite, intact and damaged, and the capsule's), --preview <prefix> --pieces 1 (each piece's
top and 3/4 views), --only <name,...> (pieces to export), --whole <prefix> (half B's uncut wholes, unsheared).
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
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_fleet_walker as fw  # noqa: E402  (export_pieces: cut, check, shear, origin, join, export)
import polish_gyges_wall as gw  # noqa: E402  (the capsule only: Plate, the shear to the camera, the faces' light)
from polish_ring_machine import relief  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_green_shell import limit_materials  # noqa: E402  (the capsule only)

W, H = 72, 56                     # a half's picture (L 24 beside 7 9 above 45 47); its origin its middle, pixel edge (36, 28)
LEFT, TOP = -36.0, 28.0
S = 4                             # the capsule's fine grid: S cells a pixel
AXIS_R = 27.5                     # the axle's axis (a pixel-edge row)


def X(c):
    return c - 36.0


def Y(r):
    return 28.0 - r


YA = Y(AXIS_R)                    # the axle's axis: y 0.5


def MR(r):
    """A row mirrored about the axle's axis (the half's lower side is its upper side mirrored)."""
    return 2 * AXIS_R - r


def rounded(t):
    t = min(1.0, max(0.0, t))
    return math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))


def smooth01(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


# --- Materials ------------------------------------------------------------------------------------------------------
# key: (palette index, metallic, roughness, emission strength in its own colour)
MATS = {
    "axle": (0x0a, 0.5, 0.26, 0.0),       # the axle's machined steel: the collar, the housing, the knob
    "dark": (0x07, 0.5, 0.3, 0.0),        # its darker turned parts: the shaft, the spacer and its disc, the hub, the rod
    "flange": (0x0b, 0.5, 0.24, 0.0),     # the two flanges
    "strut": (0x08, 0.45, 0.3, 0.0),      # the struts and stems
    "frame": (0x0a, 0.3, 0.42, 0.0),      # the panels' frames, the saddles, the dock
    "cell": (0x09, 0.3, 0.28, 0.0),       # the panels' cells
    "groove": (0x04, 0.2, 0.5, 0.0),      # the dark grooves between the cells
    "red": (0x76, 0.1, 0.3, 0.45),        # the lamps and the clamp at the axle's end
    "red_pad": (0x73, 0.15, 0.35, 0.3),   # the collar's red pads
    "blue": (0x39, 0.3, 0.25, 0.25),      # the blue band in the neck
    "soot": (0x02, 0.0, 0.85, 0.0),       # the wreck's burns
    "scorch": (0x05, 0.2, 0.7, 0.0),      # their scorched rims
    "torn": (0x03, 0.3, 0.6, 0.0),        # torn edges of broken plates
    "cap": (0x03, 0.2, 0.6, 0.0),         # cut faces
}


def materials():
    pal = k.level_palette()
    m = {}
    for key, (index, metallic, roughness, glow) in MATS.items():
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        m[key] = k.material("station_%s" % key, palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


# --- The axle -----------------------------------------------------------------------------------------------------------
# Turned about the axle's axis (along x at y YA): each part's profile (column edge, radius); the sections are flattened
# below the axis (ZB: never seen) and a little above it (ZT).
ZT, ZB = 0.72, 0.45
AXLE = [  # (name, material, profile)
    ("knob", "axle", [(3.9, 0.02), (3.95, 1.3), (4.15, 2.2), (4.55, 2.85), (5.1, 3.3), (5.7, 3.5), (7.3, 3.5)]),
    ("shaft", "dark", [(7.1, 3.5), (7.2, 5.1), (7.45, 5.45), (12.4, 5.45)]),
    ("flange_a", "flange", [(12.2, 5.4), (12.25, 9.8), (12.6, 10.4), (13.85, 10.4), (14.2, 9.8), (14.25, 6.2)]),
    ("spacer", "dark", [(14.1, 6.2), (17.0, 6.2)]),
    ("disc", "dark", [(14.9, 6.0), (14.95, 8.9), (15.2, 9.35), (15.75, 9.35), (16.0, 8.9), (16.05, 6.0)]),
    ("flange_b", "flange", [(16.8, 6.2), (16.85, 9.8), (17.2, 10.4), (18.6, 10.4), (18.95, 9.8), (19.0, 7.4)]),
    ("collar", "axle", [(18.9, 7.3), (19.0, 7.5), (23.5, 7.5), (23.7, 7.0), (24.3, 7.0), (24.5, 7.5), (26.0, 7.5),
                        (26.2, 7.1), (26.7, 7.1), (26.9, 7.5), (28.6, 7.5), (29.0, 7.0)]),
    ("hub", "dark", [(28.9, 7.0), (29.0, 6.5), (32.6, 6.5), (33.0, 6.1), (33.1, 4.4)]),
    ("band", "blue", [(32.9, 4.2), (33.0, 4.5), (37.0, 4.5), (37.1, 4.2)]),
    ("housing", "axle", [(36.9, 4.6), (37.0, 5.2), (37.35, 5.6), (49.6, 5.6), (50.0, 5.2), (50.1, 3.2)]),
    ("clamp", "red", [(50.0, 3.1), (50.1, 3.3), (51.6, 3.3), (51.75, 2.9), (52.05, 2.9), (52.2, 3.3), (53.6, 3.3),
                      (53.75, 2.9), (54.05, 2.9), (54.2, 3.3), (55.2, 3.3), (55.3, 1.0)]),
    ("rod", "dark", [(55.2, 1.0), (60.4, 1.0)]),
]


def turned(name, profile, mat, segments=32):
    """A part turned about the axle: rings round x at each profile point, its ends closed to the axis."""
    rings = []
    for c, rad in profile:
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            ca, sa = math.cos(a), math.sin(a)
            ring.append(Vector((X(c), YA + rad * ca, (ZT if sa >= 0 else ZB) * rad * sa)))
        rings.append(ring)
    obj = k.loft(name, rings, mat, start_point=(X(profile[0][0]), YA, 0.0), end_point=(X(profile[-1][0]), YA, 0.0))
    return k.smooth(obj, 40)


def on_axle(c, rad, theta):
    """The point of a turned surface of radius rad at column c, theta from straight up round the axis (+: up the
    screen)."""
    return Vector((X(c), YA + rad * math.sin(theta), (ZT if math.cos(theta) >= 0 else ZB) * rad * math.cos(theta)))


def axle(m):
    parts = [turned(name, profile, m[key]) for name, key, profile in AXLE]
    # the red lamps round the disc between the flanges, where the sprite draws them (rows 19 and 36)
    for i, th in enumerate((1.08, -1.08)):
        p = on_axle(15.45, 9.5, th)
        lamp = k.ellipsoid("lamp_%d" % i, (p.x, p.y, p.z), (0.85, 1.1, 0.9), m["red"], 16, 8)
        k.smooth(lamp, 70)
        parts.append(lamp)
    # the collar's red pads (columns 20-23 of rows 21-22 and 33-34)
    for i, th in enumerate((0.95, -0.95)):
        pts = []
        for c in (19.8, 23.2):
            pts.append(on_axle(c, 7.75, th))
        pad = mk.tube("pad_%d" % i, [tuple(pts[0]), tuple(pts[1])], 1.0, m["red_pad"], 12)
        k.smooth(pad, 50)
        parts.append(pad)
    return parts


# --- The saddles, struts and panels --------------------------------------------------------------------------------------
# (columns, rows) of the upper side; the lower side is its mirror image about the axle's axis.
SADDLE = (42.4, 50.2, 17.6, 23.8, -0.6, 4.5)     # columns, rows, bottom, top
STRUT = [(28.8, 22.6, 2.0, 1.2), (28.7, 20.2, 2.2, 1.28), (29.6, 17.8, 2.4, 1.38), (31.8, 16.5, 2.5, 1.5),
         (40.0, 16.4, 2.5, 1.6), (48.4, 16.6, 2.5, 1.6)]           # column, row, height, radius: the hub to the bar
STEM = [(39.6, 16.0, 2.5, 1.0), (39.6, 13.6, 2.6, 0.9), (39.6, 11.5, 2.7, 0.85)]
CONE = [(48.0, 17.2, 2.4, 1.7), (50.2, 16.2, 2.5, 1.3), (52.4, 15.0, 2.6, 0.95), (54.6, 14.0, 2.7, 0.7)]
CONE_BROKEN = 0.55                # the wreck's lower cone: what is left of it (its panel shot away)
# The panels: middle (column, row), width, height, its turn in the picture (degrees), its tilt about its arm (degrees),
# its height; the dock a thick one at the axle's end.
PANEL_TOP = ((39.6, 6.0), 11.4, 11.6, 0.0, 0.0, 2.7)
PANEL_DIAG = ((59.2, 10.4), 10.6, 11.0, -45.0, 0.0, 2.7)
DOCK = ((65.6, 27.5), 12.0, 11.8, 0.0, 0.0, 1.8)
DROOP = -9.0                      # the panels' outer edges hang a little (degrees, about their stems' edge)
FRAME_W, DIVIDER, CORNER = 1.15, 0.42, 1.3       # the frames' width, the dividers' half-width, the corners' radius
FRAME_UP, GROOVE = 0.5, 0.22                     # the frames over the cells, the grooves between them under
PANEL_BASE = 0.55                                # the panels' thickness under their cells (the dock's: DOCK_BASE)
DOCK_BASE = 4.2


def strut_tube(name, pts_crzr, mat, lower=False):
    pts = [(X(c), Y(MR(r) if lower else r), z, rad) for c, r, z, rad in pts_crzr]
    obj = mk.smooth_tube(name, pts, mat, 14, 2)
    return k.smooth(obj, 50)


def rect_outline(w, h, n=6, inset=0.0):
    """A rounded rectangle's outline about the origin, counter-clockwise (its corners CORNER - inset round)."""
    pts = []
    hw, hh, r = w / 2 - inset, h / 2 - inset, max(0.2, CORNER - inset)
    for (cx, cy), a0 in (((hw - r, hh - r), 0), ((-hw + r, hh - r), 90), ((-hw + r, -hh + r), 180),
                         ((hw - r, -hh + r), 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def ring_prism(name, outer, inner, z0, z1, mat):
    """A band between two outlines of equal point counts (a frame), from z0 to z1."""
    n = len(outer)
    verts = [(x, y, z0) for x, y in outer] + [(x, y, z1) for x, y in outer] + \
            [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))                       # outer wall
        faces.append((2 * n + j, 2 * n + i, 3 * n + i, 3 * n + j))   # inner wall
        faces.append((n + i, n + j, 3 * n + j, 3 * n + i))       # top
        faces.append((j, i, 2 * n + i, 2 * n + j))               # bottom
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def bevelled(obj, width, segments=2, angle=30.0, smooth=35.0):
    mk.bevel(obj, width, segments, angle)
    mk.shade(obj, smooth)
    return obj


def tile_boxes(w, h):
    """The four cells' plans (u0, u1, v0, v1) inside a panel's frame, the grooves between them."""
    iu, iv = w / 2 - FRAME_W, h / 2 - FRAME_W
    return [(DIVIDER, iu, DIVIDER, iv), (-iu, -DIVIDER, DIVIDER, iv), (-iu, -DIVIDER, -iv, -DIVIDER),
            (DIVIDER, iu, -iv, -DIVIDER)]


def panel_parts(name, w, h, m, base, fragment=None):
    """A panel in its own plane (u across, v out along its arm; the cells' tops at 0): a dark plate, four cells on it
    with the dark grooves between them, a bevelled frame round them. fragment: (outline, frame bars kept as
    (side, from, to) fractions, cells kept): what is left of a panel shot to pieces, its plate torn and sooty."""
    parts = []
    outline = rect_outline(w, h) if fragment is None else fragment[0]
    plate = mk.prism("%s_plate" % name, outline, -base, -0.2, m["groove"] if fragment is None else m["torn"])
    parts.append(bevelled(plate, 0.12, 1))
    cells = range(4) if fragment is None else fragment[2]
    boxes = tile_boxes(w, h)
    for i in cells:
        u0, u1, v0, v1 = boxes[i]
        tile = mk.prism("%s_cell%d" % (name, i), [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], -0.35, 0.0, m["cell"])
        parts.append(bevelled(tile, 0.14, 1))
    if fragment is None:
        ring = ring_prism("%s_frame" % name, rect_outline(w, h, 6), rect_outline(w, h, 6, FRAME_W), -0.3, FRAME_UP,
                          m["frame"])
        parts.append(bevelled(ring, 0.22, 2, 30.0, 40.0))
    else:
        hw, hh, fw_ = w / 2, h / 2, FRAME_W
        sides = {"bottom": ((-hw, -hh), (hw, -hh), (0, 1)), "top": ((-hw, hh), (hw, hh), (0, -1)),
                 "left": ((-hw, -hh), (-hw, hh), (1, 0)), "right": ((hw, -hh), (hw, hh), (-1, 0))}
        for side, t0, t1 in fragment[1]:
            (ax, ay), (bx, by), (nx, ny) = sides[side]
            p0 = (ax + (bx - ax) * t0, ay + (by - ay) * t0)
            p1 = (ax + (bx - ax) * t1, ay + (by - ay) * t1)
            q0, q1 = (p0[0] + nx * fw_, p0[1] + ny * fw_), (p1[0] + nx * fw_, p1[1] + ny * fw_)
            bar = mk.prism("%s_bar_%s" % (name, side), [p0, p1, q1, q0], -0.3, FRAME_UP, m["frame"])
            parts.append(bevelled(bar, 0.2, 2, 30.0, 40.0))
    for obj in parts:
        mk.apply(obj)
    return parts


def place_panel(objs, spec, lower=False, bend=None):
    """Turns a panel built in its own plane to its place: bent about its hinge (bend: (v of the hinge, degrees)),
    tilted about its arm, turned in the picture, moved to its middle (the lower side: mirrored)."""
    (c, r), w, h, turn, tilt, z = spec
    mats = []
    if bend is not None:
        hv, ang = bend
        mats.append(Matrix.Translation((0, hv, 0)) @ Matrix.Rotation(math.radians(ang), 4, "X") @
                    Matrix.Translation((0, -hv, 0)))
    mats.append(Matrix.Rotation(math.radians(tilt), 4, "Y"))
    mats.append(Matrix.Rotation(math.radians(turn), 4, "Z"))
    mats.append(Matrix.Translation((X(c), Y(r), z)))
    total = Matrix()
    for mt in mats:
        total = mt @ total
    if lower:
        total = Matrix.Translation((0, YA, 0)) @ Matrix.Scale(-1, 4, (0, 1, 0)) @ Matrix.Translation((0, -YA, 0)) @ total
    for obj in objs:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        rot = total.to_3x3()
        mesh.transform(total)
        out = [(rot @ n).normalized() for n in normals]
        if lower:
            corner = {}
            for poly in mesh.polygons:
                for li in poly.loop_indices:
                    corner[(poly.index, mesh.loops[li].vertex_index)] = tuple(out[li])
            mesh.flip_normals()
            out = [None] * len(mesh.loops)
            for poly in mesh.polygons:
                for li in poly.loop_indices:
                    out[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()
    return objs


def saddle(m, lower=False):
    c0, c1, r0, r1, z0, z1 = SADDLE
    rows = (r0, r1) if not lower else (MR(r1), MR(r0))
    pts = [(X(c0), Y(rows[1])), (X(c1), Y(rows[1])), (X(c1), Y(rows[0])), (X(c0), Y(rows[0]))]
    obj = mk.prism("saddle_%s" % ("low" if lower else "up"), pts, z0, z1, m["frame"])
    mk.bevel(obj, 0.55, 3, 30.0)
    mk.shade(obj, 35.0)
    return obj


# --- The wreck's broken panels (their fragments' outlines in the panels' own planes: u across, v out along the arm) --
TOP_SHARD = ([(-5.7, -5.8), (5.7, -5.8), (5.7, 1.6), (4.6, 2.5), (3.7, 1.2), (2.4, 0.5), (1.6, 1.5), (0.2, 0.2),
              (-1.0, -0.9), (-2.4, -0.2), (-3.6, -2.0), (-4.6, -1.6), (-5.7, -2.8)],
             [("bottom", 0.0, 1.0), ("right", 0.0, 0.62), ("left", 0.0, 0.22)], [3])
TOP_BEND = (-5.8, -24.0)          # bent down about its stem (the hinge's v, degrees)
DIAG_SHARD = ([(-5.3, -5.5), (1.2, -5.5), (0.4, -3.8), (1.4, -2.6), (0.0, -1.6), (-0.6, -0.2), (-2.0, -0.9),
               (-3.0, 0.6), (-5.3, -0.4)], [("bottom", 0.0, 0.52), ("left", 0.0, 0.42)], [2])
DIAG_BEND = (-5.5, -32.0)
BOTTOM_TORN = ([(-5.7, -5.8), (5.7, -5.8), (5.7, -3.6), (4.3, -3.0), (3.1, -1.9), (3.7, -0.5), (2.6, 0.9),
                (3.4, 2.3), (4.5, 3.0), (5.7, 3.4), (5.7, 5.8), (-5.7, 5.8)],
               [("bottom", 0.0, 1.0), ("top", 0.0, 1.0), ("left", 0.0, 1.0), ("right", 0.0, 0.16),
                ("right", 0.82, 1.0)], [1, 2])
BOTTOM_BEND = (-5.8, -9.0)
DOCK_STUB = ([(-6.0, -4.2), (-3.0, -4.2), (-2.2, -3.0), (-0.8, -2.4), (0.6, -1.0), (-0.4, 0.2), (0.2, 1.2),
              (-1.8, 1.8), (-2.6, 2.6), (-6.0, 2.6)], [("left", 0.15, 0.62)], [])
DENT = 0.1                        # the burnt metal sunk this much
# Burns: soot patches on the wreck's axle, saddles and struts where the damaged sprites draw it burnt (column, row,
# half-width, half-height), their edges wavering a little (fixed sines).
BURNS = [(10.5, 27.0, 6.0, 3.2), (25.5, 26.6, 4.2, 3.4), (44.0, 27.4, 8.6, 4.4), (39.6, 16.0, 3.6, 2.4),
         (46.6, 20.4, 3.0, 2.4), (54.6, 13.4, 2.2, 3.0), (61.0, 28.0, 3.2, 3.2), (38.6, 37.2, 3.0, 1.8),
         (16.0, 29.0, 2.4, 3.0), (31.0, 30.5, 2.4, 2.0), (44.0, 33.5, 2.6, 1.8)]


def soot_value(x, y):
    best = -9.0
    for c, r, hw, hh in BURNS:
        u = ((x - X(c)) / hw) ** 2 + ((y - Y(r)) / hh) ** 2
        best = max(best, 1.0 - u)
    return best + 0.18 * math.sin(1.7 * x + 2.3 * y) + 0.12 * math.sin(3.1 * x - 1.3 * y)


def burn(obj, m):
    """The soot patches on a part of one material: a scorched rim round a sooty middle, the metal sunk a little there."""
    mat = obj.data.materials[0]
    values = [soot_value(v.co.x, v.co.y) for v in obj.data.vertices]
    if max(values) <= 0.0:
        return obj
    band_split(obj, values, [(-99.0, mat), (0.0, m["scorch"]), (0.42, m["soot"])])
    for v in obj.data.vertices:
        f = soot_value(v.co.x, v.co.y)
        if f > 0.0 and v.co.z > 0.0:
            v.co.z -= DENT * min(1.0, f / 0.6)
    obj.data.update()
    return k.smooth(obj, 40)


def dock_parts(m, fragment=None):
    """The docking block at the axle's end: a bevelled body under a panel (the wreck's: a torn stub)."""
    (_, w, h, _, _, _) = DOCK
    outline = rect_outline(w, h) if fragment is None else fragment[0]
    body = bevelled(mk.prism("dock_body", outline, -DOCK_BASE, -0.25, m["frame"]), 0.45, 2)
    mk.apply(body)
    return [body] + panel_parts("dock", w, h, m, 0.4, fragment)


def half(m, damaged=False):
    """Half B of the station (its axle end on its left) as built in its picture's plane."""
    parts = axle(m)
    for lower in (False, True):
        parts.append(saddle(m, lower))
        parts.append(strut_tube("strut_%d" % lower, STRUT, m["strut"], lower))
        parts.append(strut_tube("stem_%d" % lower, STEM, m["strut"], lower))
        cone = CONE if not (damaged and lower) else [CONE[0], (
            CONE[0][0] + CONE_BROKEN * (CONE[1][0] - CONE[0][0]), CONE[0][1] + CONE_BROKEN * (CONE[1][1] - CONE[0][1]),
            CONE[1][2], 1.35)]
        parts.append(strut_tube("cone_%d" % lower, cone, m["strut"], lower))
    (_, w, h, _, _, _) = PANEL_TOP
    (_, wd, hd, _, _, _) = PANEL_DIAG
    if not damaged:
        for lower in (False, True):
            parts += place_panel(panel_parts("panel_top_%d" % lower, w, h, m, PANEL_BASE), PANEL_TOP, lower,
                                 (-h / 2, DROOP))
            parts += place_panel(panel_parts("panel_diag_%d" % lower, wd, hd, m, PANEL_BASE), PANEL_DIAG, lower,
                                 (-hd / 2, DROOP))
        parts += place_panel(dock_parts(m), DOCK)
    else:
        parts += place_panel(panel_parts("panel_top_0", w, h, m, PANEL_BASE, TOP_SHARD), PANEL_TOP, False, TOP_BEND)
        parts += place_panel(panel_parts("panel_top_1", w, h, m, PANEL_BASE, BOTTOM_TORN), PANEL_TOP, True,
                             BOTTOM_BEND)
        parts += place_panel(panel_parts("panel_diag_0", wd, hd, m, PANEL_BASE, DIAG_SHARD), PANEL_DIAG, False,
                             DIAG_BEND)
        parts += place_panel(dock_parts(m, DOCK_STUB), DOCK)
        for obj in parts:
            if len(obj.data.materials) == 1 and obj.data.materials[0] not in (m["red"], m["blue"], m["red_pad"]):
                burn(obj, m)
    for obj in parts:
        mk.apply(obj)
    return parts


def mirrored(objects):
    """Half A: copies of half B's parts mirrored across x = 0 (faces turned back out, custom normals mirrored)."""
    out = []
    flip = Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        c = obj.copy()
        c.data = obj.data.copy()
        c.name = obj.name + "_a"
        bpy.context.scene.collection.objects.link(c)
        mesh = c.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        mesh.update()
        out.append(c)
    return out


# --- The pieces -----------------------------------------------------------------------------------------------------------
# (name, sprite, damaged name, damaged sprite, box in the half's plane, origin); half B's, and half A's (its mirror image).
PIECES_B = [("station_end_left", 24, "station_end_left_damaged", 100, (-36.0, -12.0, -14.0, 14.0)),
            ("station_l_tl", 7, "station_l_tl_damaged", 83, (-12.0, 12.0, 0.0, 28.0)),
            ("station_l_tr", 9, "station_l_tr_damaged", 85, (12.0, 36.0, 0.0, 28.0)),
            ("station_l_bl", 45, "station_l_bl_damaged", 121, (-12.0, 12.0, -28.0, 0.0)),
            ("station_l_br", 47, "station_l_br_damaged", 123, (12.0, 36.0, -28.0, 0.0))]
PIECES_A = [("station_end_right", 34, "station_end_right_damaged", 110, (12.0, 36.0, -14.0, 14.0)),
            ("station_r_tr", 13, "station_r_tr_damaged", 89, (-12.0, 12.0, 0.0, 28.0)),
            ("station_r_tl", 11, "station_r_tl_damaged", 87, (-36.0, -12.0, 0.0, 28.0)),
            ("station_r_br", 51, "station_r_br_damaged", 127, (-12.0, 12.0, -28.0, 0.0)),
            ("station_r_bl", 49, "station_r_bl_damaged", 125, (-36.0, -12.0, -28.0, 0.0))]


def export_list(pieces, damaged):
    """fw.export_pieces' (name, sprite, box, origin): the boxes reach out past the half's picture where it ends (the
    origin stays the sprite's middle)."""
    out = []
    for name, sprite, dname, dsprite, box in pieces:
        x0, x1, y0, y1 = box
        origin = ((x0 + x1) / 2, (y0 + y1) / 2)
        if x0 <= -36.0:
            x0 -= 10.0
        if x1 >= 36.0:
            x1 += 10.0
        if y1 >= 28.0:
            y1 += 10.0
        if y0 <= -28.0:
            y0 -= 10.0
        out.append((dname if damaged else name, dsprite if damaged else sprite, (x0, x1, y0, y1), origin))
    return out


def cap_key(m):
    def cap_of(src):
        return m["cap"]
    return cap_of


def build_halves(options, only, sheet):
    results = {}
    for damaged in (False, True):
        lists = [export_list(PIECES_B, damaged), export_list(PIECES_A, damaged)]
        if only is not None and not any(p[0] in only for lst in lists for p in lst):
            continue
        k.reset()
        m = materials()
        half_b = half(m, damaged)
        half_a = mirrored(half_b)
        for whole, lst in ((half_b, lists[0]), (half_a, lists[1])):
            triangulate(whole)
        bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        for label, whole in (("B", half_b), ("A", half_a)):
            low, high = mk.bounds(whole)
            print("== half %s%s: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
                label, " damaged" if damaged else "", mk.triangles(whole), low.x, high.x, low.y, high.y, low.z,
                high.z))
        if "whole" in options:
            mk.export(half_b, options["whole"] + ("station_b_damaged" if damaged else "station_b") + ".glb")
        for whole in (half_a,):
            for o in whole:
                o.hide_render = True
        results.update(fw.export_pieces(half_b, lists[0], cap_key(m), options, sheet, "L", only))
        for o in half_b:
            o.hide_render = True
        for o in half_a:
            o.hide_render = False
        results.update(fw.export_pieces(half_a, lists[1], cap_key(m), options, sheet, "L", only))
    return results


# --- TIME WAR's grey capsule: round 36's, kept as it was (a heightfield over its sprites' pixels, painted by their
# shades: the capsule's own models are unchanged by round 38) ---------------------------------------------------------

INKS = {   # shades, (metallic, roughness), glow strengths by shade, lift, contrast (about shade 7), comp
    "metal": ([0x03, 0x05, 0x07, 0x09, 0x0b, 0x0d, 0x0f], (0.3, 0.32), {}, 1.6, 1.1, 2.0),
    "red": ([0x72, 0x74, 0x76, 0x78], (0.1, 0.3), {0x72: 0.3, 0x74: 0.4, 0x76: 0.5, 0x78: 0.58}, 1.5, 1.0, 0.8),
    "blue": ([0x33, 0x36, 0x39, 0x3c], (0.4, 0.28), {}, 1.5, 1.0, 1.5),
    "soot": ([0x01, 0x02, 0x03], (0.0, 0.8), {}, 0.6, 1.0, 0.6),   # the damaged look's burns (black over intact steel)
}
RAMPS = {"metal": 0, "red": 7, "blue": 3}
WALL = ("metal", 0x05)            # the sides (seen off the screen's middle)
LIT_MEAN = 0.72


def pal(prefix, index, metallic, roughness, glow=0.0):
    extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow > 0 else {}
    return k.material("%s_%x" % (prefix, index), palette=index, metallic=metallic, roughness=roughness, **extra)


def mat_of(key):
    shades, (met, rough), glows, _, _, _ = INKS[key[0]]
    return pal("station_" + key[0], key[1], met, rough, glows.get(key[1], 0.0))


class Paint:
    def __init__(self, a, intact, mirror=False):
        self.mirror = mirror
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        ramp = np.where(a >= 0, a >> 4, -1)
        burnt = (a == 1) & (intact > 1)
        self.inks = []
        for name, (shades, _, _, lift, contrast, comp) in INKS.items():
            if name == "soot":
                mask = burnt
            else:
                mask = (ramp == RAMPS[name]) & (a >= 1) & ~burnt
            if not mask.any():
                continue
            soft = gw.blur(gw.fill(shade, mask), 0.5)
            self.inks.append((name, shades, gw.blur(mask.astype(float), 0.6), 7.0 + contrast * (soft - 7.0), lift,
                              comp))

    def sample(self, field, Xa, Ya):
        Xa = -np.asarray(Xa, float) if self.mirror else np.asarray(Xa, float)
        fc = np.clip(Xa - LEFT - 0.5, 0.0, W - 1.0)
        fr = np.clip(TOP - np.asarray(Ya, float) - 0.5, 0.0, H - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), W - 2)
        r0 = np.minimum(np.floor(fr).astype(int), H - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)

    def keys(self, Xa, Ya, normals):
        lit_by = gw.sun_on(normals)
        weights = np.stack([self.sample(ink[2], Xa, Ya) for ink in self.inks], 0)
        which = weights.argmax(0)
        per = [gw.nearest(self.sample(soft, Xa, Ya) + lift + comp * (LIT_MEAN - lit_by), shades)
               for name, shades, _, soft, lift, comp in self.inks]
        return [(self.inks[w][0], int(per[w][i])) for i, w in enumerate(which)]


def assign(obj, keys):
    keys = limit_materials(keys)
    order = sorted(set(keys), key=lambda key: str(key))
    slot = {key: i for i, key in enumerate(order)}
    mesh = obj.data
    mesh.materials.clear()
    for key in order:
        mesh.materials.append(mat_of(key))
    mesh.polygons.foreach_set("material_index", [slot[key] for key in keys])
    mesh.update()


# --- TIME WAR's grey capsule (L 1 3 above 39 41 above 77 79: one 48 x 84 picture) ---------------------------------------

CW, CH = 48, 84                   # its picture; its origin its middle, the pixel edge (24, 42)
CAP_AXIS = 24.5                   # its axis (a pixel-edge column: x 0.5)
CAP_SQUASH = 0.62                 # its sections: this flat (as the station's)
CAP_SLOT = 0.55                   # its red slots and lights sunk this deep into the hull
CAP_GROOVE = 0.55                 # its dark lines (black, the darkest greys) creased this deep


class Capsule:
    """The capsule lying along the screen, nose up: a body turned about its axis whose half-width row by row is the
    sprite's (smoothed), its red slots sunk into it, its dark lines creased; tops and bases (mirrored) over its middle
    plane; the sprite's holes left open."""

    def __init__(self, a):
        self.a = a
        xs = -24.0 + (np.arange(CW * S) + 0.5) / S
        ys = 42.0 - (np.arange(CH * S) + 0.5) / S
        X, Y = np.meshgrid(xs, ys)
        opaque = a >= 0
        widths = np.zeros(CH)
        for r in range(CH):
            cs = np.nonzero(opaque[r])[0]
            if len(cs):
                widths[r] = max(CAP_AXIS - cs.min(), cs.max() + 1 - CAP_AXIS)
        wf = np.repeat(widths, S)
        k_ = np.exp(-0.5 * (np.arange(-4, 5) / 2.0) ** 2)
        wf = np.convolve(np.pad(wf, 4, mode="edge"), k_ / k_.sum(), mode="valid")
        R = np.maximum(wf[:, None] + 0.4, 0.5) + np.zeros_like(X)
        dx = np.abs(X - (CAP_AXIS - 24.0))
        hull = CAP_SQUASH * np.sqrt(np.clip(R * R - dx * dx, 0.0, None))
        ramp = np.where(a >= 0, a >> 4, -1)
        shade = np.where(a >= 0, a & 15, 0)
        red = gw.blur(up_c(ramp == 7).astype(float), 0.4 * S)
        dark = gw.blur(up_c(((a == 1) | ((ramp == 0) & (shade <= 2))) & opaque).astype(float), 0.4 * S)
        top = hull - CAP_SLOT * np.clip(red * 1.5, 0.0, 1.0) - CAP_GROOVE * np.clip(dark * 1.3, 0.0, 1.0)
        soft = gw.blur(up_c(opaque).astype(float), 0.45 * S) > 0.5
        top = np.where(soft, np.maximum(top, 0.0), 0.0)
        self.cells_f = CapField(soft.astype(float))
        self.top_f = CapField(top)
        self.base_f = CapField(np.where(soft, -hull, 0.0))

    def cells(self, cx, cy):
        return self.cells_f(cx, cy) > 0.5

    def heights(self, Xa, Ya):
        return self.top_f(Xa, Ya)

    def bases(self, Xa, Ya):
        return np.minimum(self.base_f(Xa, Ya), self.top_f(Xa, Ya) - 0.05)


def up_c(m):
    return np.repeat(np.repeat(m, S, 0), S, 1)


class CapField:
    """Values on the capsule's fine grid, sampled bilinearly."""

    def __init__(self, values):
        self.v = values

    def __call__(self, Xa, Ya):
        h, w = self.v.shape
        fc = np.clip((np.asarray(Xa, float) + 24.0) * S - 0.5, 0.0, w - 1.0)
        fr = np.clip((42.0 - np.asarray(Ya, float)) * S - 0.5, 0.0, h - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), w - 2)
        r0 = np.minimum(np.floor(fr).astype(int), h - 2)
        tc, tr = fc - c0, fr - r0
        v = self.v
        return ((v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc) * (1 - tr) +
                (v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc) * tr)


class CapPaint(Paint):
    """polish_station.Paint on the capsule's picture."""

    def __init__(self, a):
        Paint.__init__(self, a, a)

    def sample(self, field, Xa, Ya):
        fc = np.clip(np.asarray(Xa, float) + 24.0 - 0.5, 0.0, CW - 1.0)
        fr = np.clip(42.0 - np.asarray(Ya, float) - 0.5, 0.0, CH - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), CW - 2)
        r0 = np.minimum(np.floor(fr).astype(int), CH - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)


def parse_capsule(text, first_row=4):
    a = -np.ones((CH, CW), int)
    for i, line in enumerate(text.split()):
        for c in range(CW):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[first_row + i, c] = int(t, 16)
    return a


CAPSULE_PIECES = [("grey_capsule_tl", 1, (-24.0, 0.0, 14.0, 42.0)), ("grey_capsule_tr", 3, (0.0, 24.0, 14.0, 42.0)),
                  ("grey_capsule_ml", 39, (-24.0, 0.0, -14.0, 14.0)), ("grey_capsule_mr", 41, (0.0, 24.0, -14.0, 14.0)),
                  ("grey_capsule_bl", 77, (-24.0, 0.0, -42.0, -14.0)),
                  ("grey_capsule_br", 79, (0.0, 24.0, -42.0, -14.0))]


def check_capsule(cap, sheet):
    covered = gw.own_coverage(lambda Xa, Ya: cap.cells(Xa, Ya), CW, CH, -24.0, 42.0)
    mask = [[False] * CW for _ in range(CH)]
    for _, sprite, box in CAPSULE_PIECES:
        c0, r0 = int(box[0] + 24.0), int(42.0 - box[3])
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    mk.compare("the grey capsule (its 48 x 84 picture)", covered, mask)
    for name, sprite, box in CAPSULE_PIECES:
        c0, r0 = int(box[0] + 24.0), int(42.0 - box[3])
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap %s (l %d): %.3f" % (name, sprite, both / max(1, either)))


def build_capsule(options, only, out, sheet):
    a = parse_capsule(CAPSULE)
    cap = Capsule(a)
    if sheet and only is None:
        check_capsule(cap, sheet)
    plate = gw.Plate((-24.0, 24.0, -42.0, 42.0), cap.heights, base=cap.bases, cells=cap.cells, bottom=False)
    paint = CapPaint(a)
    for name, sprite, box in CAPSULE_PIECES:
        if only is not None and name not in only:
            continue
        k.reset()
        obj, kinds, _ = plate.mesh(name, gw.piece_owner(box))
        centres, normals = gw.face_data(obj)
        centres, normals = np.round(centres, 4), np.round(normals, 4)
        top = paint.keys(centres[:, 0], centres[:, 1], normals)
        keys = [top[i] if kinds[i] == 0 else WALL for i in range(len(kinds))]
        assign(obj, keys)
        gw.finish_piece(name, [obj], box, out, options)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_L.png") if os.path.isdir(sheets) else sheets
    results = build_halves(options, only, sheet)
    if sheet:
        for name, score in results.items():
            if score is not None:
                print("overlap %-28s %.3f" % (name, score))
    build_capsule(options, only, out, sheet)


# --- The capsule's pixels ---------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom (the picture's empty rows left out).

CAPSULE = """
............................................010101..............................................
..............................05060606040605050204040505040101030302............................
..........................0406070708070409080803060408070601030504030201........................
........................0406070a0a0908050504040307040404030304060504030202......................
......................0406070a0c0b0908070908080407050a0908020406050403020303....................
......................040507080909080807060607050806060606040506050403020305....................
......................040507080808080808080909060807080909060706050403020306....................
......................040506080808080808070707070807070707060706050403020406....................
......................030405070808080808080808080808080707070605040302040705....................
........................03040506070707070707070707070707060605040302040705......................
..........................0303030304040505050505050505050505040404050605........................
..............................03040505050505050506040404040405050606............................
..............................04050506060606060607040404040404030404............................
..............................0202020304040404050704020203030302................................
..........................03050506070808080903060804020a0605040403020202........................
........................04040402010202020202010608040201010101......020202......................
......................01050703070a0303030304050708040402010101010504..0302......................
......................0305090306080305050506070708040403020202010604..030202....................
......................030407030608030403050607070804040302......0604..030202....................
......................030406030608037303050607070804040302..72..0504..040202....................
......................030406030202037503060607070804040303..72........040202....................
......................030406030271737703070607070804040303..727371..02050202....................
......................020305040372737603070607070804040403..727371..02040202....................
........................0204040574747403090606070804040403..727371..020202......................
........................0102020273747403090606070804040403..727371..010101......................
........................0104060771747403080606070705040403..72737106040303......................
........................0204040671737403070606070605040302..72737104020202......................
........................0304040670727403050606060605030301..72737104020202......................
........................0404040670707002020405050504030201..70707004020202......................
........................0404040571717102020202030202010101..70717004020202......................
........................04040405717372040b0807070706060607..71727004020202......................
........................0404040571737203070504030303040505..71727004020202......................
........................0404040571717103070403030303030405..70717104020202......................
........................0404040571737803070303030303030305..73757204020202......................
........................04040405727376030703030303030303040172737104020202......................
........................04040405727375030703030303030303040172737104020202......................
........................04040405727374030703030303030303040172737104020202......................
........................04040405707274030703030303030303040171737104020202......................
........................0404040570707003070403030303030404..70707004020202......................
........................0404040571727103060504030303040405..71717004020202......................
........................0404040571737203060505040404040505..71727004020202......................
........................04040405717372..0101010102010101....71727004020202......................
........................0404040571717101010304050402030101..70717104020202......................
........................0304040571737801030606050503040401..73757204020202......................
........................0204040572737602060607090804040403..72737104020202......................
........................0204040572737503080708090906040403..72737104020202......................
........................0204040572737403090708090906040403..72737103020101......................
........................0103030172737403090708080805040403..727371..010101......................
........................0204040373737403090607070804040403..72737103030303......................
........................0204040474747403090606070804040403..72737101020202......................
........................0204040574747403090606070804040403..727371..020202......................
........................0204040574747403090606070804040403..727371..020202......................
..........................0204057474040806060607080404040403..7270..0102........................
..............................01730308050506060709050404040303..72..............................
..................................090605060606070a05030404040304................................
..................................060506060606090a08060204050606................................
......................................0204060907070708050301020101..............................
....................................73760509070707070708047571..................................
..................................02050506090707070707090504030201..............................
............................040707070707090a07070707070a08060606050403..........................
..........................040707080808090a0a0707070707090a09090706040404........................
........................04060708090909090907060606070706070607070605040304......................
........................05070709090909080203030303030303040606060605040306......................
........................060708090b0d0b080304040404040404040606060605040306......................
..................................010204030606060505040301020101010101..........................
................................04050807070706060505050505060302020305..........................
............................010204050807070706060505050505060302020304..........................
..............................0101010405060606050404030302010101010202..........................
........................030607090b0d0f0f0e0d0c0b0a090808070606050403030303......................
........................03050606060606060707070707060606060505040303040603......................
..........................0304050505050505050505050505050504030303040602........................
..............................04040404040404040404040404030403040505............................
....................................010203030505040302020201....................................
..................................7173767a7977757575757778767472................................
..................................717275777877767575747475757371................................
..............................................0101..............................................
"""



if __name__ == "__main__":
    build()
