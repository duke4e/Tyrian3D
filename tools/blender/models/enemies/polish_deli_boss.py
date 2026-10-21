"""DELI's boss, the red war machine at the end of DELI and New Deli (sky enemies) that HARVEST sends over again and
again (top enemies): sheet T, twelve 2x2 sprites that the levels always place as one 144 x 56 picture and move together
(DELI's and DELIANI's events at t 4780, type 15: enemies 400-405 = T 1 3 5 7 9 11 at x = -6 + 24 i, 28 pixels above
406-411 = T 39 41 43 45 47 49 at the same x). Polished 2026-10-21; it replaces wave3_v.py's boss (reliefs inflated from
the pixels and painted pixel by pixel) and wave1_c.py's gun arms (deli_arm). models.cfg (as before): model
deli_boss_<sprite> enemies/deli_boss_<sprite>.glb origin for 1 3 5 7 9 11 41 43 45 47, model deli_arm_left / _right
enemies/deli_arm_left.glb / _right.glb origin for 39 / 49; sprite t <sprite> <model> yaw=0. The arms' frames (39 77 79
and 49 87 85) only brighten the eye: the eye stays lit, no frame models. Its damaged look (T 115 119 121 125 153 163)
is polish_deli_boss_dmg.py's, built from this one.

The picture is its own mirror image about the middle of pixel column 71 (column c is column 142 - c; only the light,
from the upper left, differs): the left half is built and mirrored, the parts across the middle are built whole. As
the sprites and their 4x upscales draw it (the picture's columns and rows):
- The hull (columns 38-105, rows 1-41): a red armoured deck (its back edge at row 8, rounded and lit; its outer
  corners chamfered; down its sides a frame strip, columns 46-50) round two big glossy black spheres (columns 51-65 of
  rows 15-34, sunk in sockets, a lit rim round them) with a dark glass canopy between them (columns 65-77 of rows
  13-24: a dome with a grey frame across its back and down its sides). On the deck's back two fire grilles (columns
  53-68 of rows 1-9, their outer ends swept down the screen), the fire glowing between dark slats; between them the
  raised top plate, a spine (columns 68-75 of rows 4-12) between two wings sloping to the grilles. On the shoulders a
  vent of three slots (columns 49-53 of rows 12-16) and a louvre (columns 57-60 of rows 9-15). Under the canopy the red
  jaw: two prongs (columns 60-67 of rows 25-35, a groove down each) whose lips nearly meet (row 25), a dark slot between
  them with a grey nub at its front (rows 31-35) pointing down the screen. Under each sphere a lobe of the deck, its
  front sloping down (rows 36-41), seams across it (columns 57 and 62); a notch between the lobes. A thin fin down the
  hull's flank (column 43 of rows 24-31).
- The beams (columns 13-42 of rows 13-24) from the hull's flanks out to the arms: a bar (rows 20-24) with a raised
  block on its inner end (columns 25-42 of rows 13-20; grooves across it, its end stepping down under the hull's
  shoulder), a black hump over the block's back and the hull's corner (columns 32-44 of rows 6-13: a curved fender
  with a groove along it), a small red claw hanging from the bar's front (columns 26-32 of rows 23-31) and a grey pin
  across a dark gap to the shoulder (row 18).
- The arms (columns 3-21 of rows 10-53): a black shoulder pad of two lobes (columns 8-20 of rows 10-20; the outer one
  ribbed across, a grey joint block under the inner one); under it the arm, a thick fluted red tube (columns 3-15)
  from a rounded shoulder (rows 19-24, the bar running into it) down the screen to a cuff across its end (rows 35-40);
  under the cuff the gun pod (columns 7-21 of rows 39-53): its top level, its face sloping towards the camera with a
  black socket and the glowing eye (red, its yellow pupil at the upper left), a grey nozzle on its outer side. A black
  hose from under the bar down the arm's inner side into the pod's top.

Built as a CAD modeller would (polish_machine_kit): plates and blocks are prisms of their plan cut by the planes of
their tops and chamfers (exact booleans), their slots, sockets and grooves cut by booleans, edges bevelled, flat faces
kept flat; round parts are lofted (the spheres, the canopy, the pads, the tube, the pod, the hose). The whole machine
is then cut along the sprites' edges (polish_arch.cut: the pieces keep the whole's shading across the cuts, their cuts
capped) into the twelve pieces, each moved so that its sprite's centre is its origin; every mesh is triangulated before
the export (polish_k_pod.triangulate), so the output is the same with and without --check, and each piece's parts are
joined into one mesh (a primitive per material rather than per part and material: the GLBs a sixth smaller).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z = 0 the layer:
the machine reaches from -6 to 10, under background 3 in the sky). The whole's origin is the corner where T 5, 7, 43
and 45 meet: column c's left edge is x = c - 72, row r's top edge y = 28 - r. Built about X = x + 0.5 = 0 (the middle
of column 71) and moved there at the end (AXIS_X).

Replaces wave3_v.py (all of it: the boss is all it builds; only wave3_ap_deli.py loads it), wave3_v_art.py's BOSS
(read only by wave3_v.py and wave3_ap_deli.py) and wave1_c.py's arms (its section "DELI's gun arms": ARM_POD,
deli_arm, deli_arm_left, deli_arm_right; their MODELS entries and docstring lines; the helpers only they use:
frame_rings, tube, catmull, bake_transforms, mirror_scene): remove them so that they don't overwrite these models
(polish_deli_boss_dmg.py says what replaces wave3_ap_deli.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_T.png), --preview <prefix> (the whole's and each piece's top and 3/4 views), --only
<model,...> (pieces to export; "none": none), --whole <file.glb> (the uncut machine as well, for looking at), --stats 1
(each piece's largest parts).
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
from polish_arch import cut, plane_box  # noqa: E402  (cut: polish_machine_kit.cut without its indices shifted twice)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AXIS_X = -0.5                    # the middle of column 71, where the built machine's X = 0 goes
# The pieces: model, sprite, the picture's column and row of its top left corner.
CELLS = [("deli_boss_1", 1, 0, 0), ("deli_boss_3", 3, 24, 0), ("deli_boss_5", 5, 48, 0), ("deli_boss_7", 7, 72, 0),
         ("deli_boss_9", 9, 96, 0), ("deli_boss_11", 11, 120, 0),
         ("deli_arm_left", 39, 0, 28), ("deli_boss_41", 41, 24, 28), ("deli_boss_43", 43, 48, 28),
         ("deli_boss_45", 45, 72, 28), ("deli_boss_47", 47, 96, 28), ("deli_arm_right", 49, 120, 28)]


def box_of(col, row):
    """A piece's box in the whole's coordinates (x0, x1, y0, y1)."""
    return (col - 72.0, col - 48.0, -row, 28.0 - row)


PIECES = [(name, sprite, box_of(col, row)) for name, sprite, col, row in CELLS]


def XE(c):
    """The left edge of the picture's column c (fractions allowed), in the built frame (X = 0 the middle of 71)."""
    return c - 71.5


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
    right = [(-x, y) for x, y in reversed(left[1:-1])]
    return ccw(left + right)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- The measures (pixel edges of the picture; the left half, mirrored) ----------------------------------------------
# The deck under the plates: its left half's outline (middle of the back edge, round the flank and the lobe, to the
# middle of the notch), its top (the frame round the spheres) and bottom, the planes chamfering it: the back edge, the
# flank, the lobe's front and its outer corner.
DECK = [(71.5, 8.0), (44.2, 8.0), (42.5, 8.6), (41.0, 9.7), (39.8, 10.9), (38.8, 12.2), (38.5, 13.2), (38.5, 16.6),
        (42.5, 16.6), (42.5, 23.9), (46.2, 24.3), (46.2, 34.6), (46.9, 35.6), (47.5, 36.8), (48.2, 38.2), (49.1, 39.5),
        (50.2, 40.6), (51.6, 41.7), (63.4, 41.7), (64.9, 41.0), (66.1, 39.8), (67.2, 38.6), (68.6, 37.4), (68.8, 36.0),
        (71.5, 36.0)]
DECK_TOP, DECK_BOTTOM = 5.6, -2.6
DECK_BACK = (9.6, 4.9, 8.0)       # the back edge's chamfer: DECK_TOP at row 9.6, z 4.9 at row 8.0
DECK_FLANK = (44.0, 4.4, 38.5)    # the flank's: DECK_TOP at column 44, z 4.4 at column 38.5
DECK_FRONT = (36.4, 2.2, 41.7)    # the lobes' fronts: DECK_TOP at row 36.4, z 2.2 at row 41.7
DECK_CORNER = ((46.2, 34.6), (51.6, 41.7), 1.6, 0.75)   # the lobe's outer corner: its edge, how far inside the
                                                        # chamfer begins, its slope
# The shoulder plate on the deck (left): its plan, top, the back edge's and the flank's chamfers; the vent cut into it
# (three slots: columns, rows) and the louvre (three slots across: columns, rows), how deep.
SHOULDER = [(44.2, 8.1), (52.9, 8.1), (52.9, 9.6), (60.6, 9.6), (60.6, 16.9), (42.4, 16.9), (38.7, 16.7), (38.7, 13.2),
            (39.0, 12.2), (40.0, 10.9), (41.1, 9.7), (42.6, 8.6)]
SHOULDER_TOP = 7.0
SHOULDER_BACK = (9.7, 6.1, 8.1)
SHOULDER_FLANK = (44.6, 5.7, 38.7)
VENT_SLOTS = [(48.7, 49.6), (50.7, 51.6), (52.7, 53.6)]
VENT_ROWS = (11.7, 16.4)
LOUVRE_COLS = (56.9, 60.0)
LOUVRE_ROWS = [(9.9, 10.6), (11.8, 12.5), (13.7, 14.4)]
SLOT_DEPTH = 1.2
# The lobe plate under each sphere: its plan, top, the front's and the outer corner's chamfers; the seams across it
# (columns, rows).
LOBE = [(46.6, 34.3), (59.6, 34.3), (60.4, 35.1), (61.0, 35.7), (67.0, 35.7), (68.8, 36.0), (68.6, 37.4), (67.2, 38.6),
        (66.1, 39.8), (64.9, 41.0), (63.4, 41.7), (51.6, 41.7), (50.2, 40.6), (49.1, 39.5), (48.2, 38.2), (47.5, 36.8),
        (46.9, 35.6)]
LOBE_TOP = 6.5
LOBE_FRONT = (36.8, 2.6, 41.7)
LOBE_CORNER = ((46.6, 34.6), (51.6, 41.7), 1.8, 0.8)
LOBE_SEAMS = [(56.7, 57.5), (61.7, 62.4)]
LOBE_SEAM_ROWS = (34.0, 42.5)
# The sphere (its centre column, row, height; radii), its socket (the sphere's radii grown by SOCKET), the rim round
# it on the deck (its section's radius).
SPHERE = (58.1, 24.7, 2.0, (7.9, 10.1, 7.8))
SOCKET = 0.6
RIM_R = 0.55
# The fin down the flank: its plan, its top at its ends (rows 24 and 31.6), its bottom.
FIN = [(42.3, 23.5), (44.3, 23.5), (44.3, 31.0), (43.3, 31.9), (42.3, 31.0)]
FIN_Z = (4.8, 3.2, -1.2)
# The top plate: the spine (whole: columns, rows, top, its back chamfer to z at row 4) and the wings (left; their top,
# the outer chamfer from column 63.2 down to z at column 60.8).
SPINE = (67.7, 75.3, 4.0, 13.0, 8.9, 8.0)
WING = [(63.6, 5.5), (67.3, 5.5), (67.3, 13.0), (65.2, 13.2), (64.4, 14.8), (61.6, 15.6), (60.8, 15.0), (60.8, 8.3)]
WING_TOP, WING_CHAMFER = 7.9, (63.2, 60.8, 6.6)
# The grille: the housing's plan (left), the opening inside it, the housing's top, the fire's floor, the slats
# (columns of their middles), their width and top; the fire hottest between rows HOT, dimmest beyond LOW.
GRILLE = [(59.8, 0.9), (68.0, 0.9), (68.0, 5.7), (63.6, 5.7), (61.4, 8.6), (60.6, 9.6), (52.8, 9.6), (52.8, 8.0),
          (54.9, 5.2), (57.4, 2.7)]
OPENING = [(60.2, 1.9), (67.1, 1.9), (67.1, 4.8), (63.1, 4.8), (60.8, 8.2), (53.8, 8.2), (56.2, 5.0), (58.4, 2.8)]
GRILLE_TOP, FIRE_Z = 7.8, 5.6
SLATS = [57.5, 59.5, 61.5, 63.5, 65.5]
SLAT_W, SLAT_TOP = 0.95, 7.45
FIRE_HOT, FIRE_LOW = (3.0, 6.4), (2.5, 7.6)
# The canopy (whole): its centre row, half-width and half-length (columns 65-78, rows 13-24.6), its foot and top; the
# frame across its back (rows) and down its sides (columns, left).
CANOPY = (18.8, 6.5, 5.8, 5.4, 8.8)
CANOPY_BAR = (16.2, 18.4)
CANOPY_RAIL = (65.5, 66.8)
# The jaw: the left prong's plan, its top, its lip's top, the groove down it (columns, rows); the slot between the
# prongs (columns, rows, its floor); the nub (rows from its back to its tip, half-width, half-height, axis height).
PRONG = [(62.8, 24.4), (69.1, 24.4), (69.1, 25.9), (67.0, 26.2), (67.0, 35.7), (61.0, 35.7), (59.8, 34.6),
         (61.6, 31.0), (62.8, 30.2)]
PRONG_TOP, LIP_TOP = 7.7, 7.95
PRONG_GROOVE = (64.6, 65.3, 26.6, 34.8)
SLOT = (66.9, 76.1, 24.6, 36.4, 1.9)
NUB = (29.4, 35.3, 3.05, 2.6, 3.0)
# The beam: the bar (plan, bottom, top), the block on its inner end (plan, top) and its low end under the shoulder
# (plan; its top slopes from z at a column down to z at another), the grooves across the block (columns), the hump
# (its path from the hull's corner down the block's back: column, row, top; its half-width along the path, its foot),
# the claw (the stem and the fork's prongs: column, row, z; their radii; its two knuckles at its foot: column, row, z,
# radius; its tip), the pin (columns, row, z, radius).
BAR = [(9.0, 19.6), (42.7, 19.6), (42.7, 24.0), (31.6, 24.0), (31.0, 23.6), (9.0, 23.6)]
BAR_Z = (1.0, 5.0)
BLOCK = [(25.2, 13.0), (38.3, 13.0), (38.3, 16.6), (25.2, 16.6)]
BLOCK_LOW = [(25.2, 16.4), (42.6, 16.4), (42.6, 19.9), (25.2, 19.9)]
BLOCK_TOP = 7.2
BLOCK_STEP = (37.6, 7.0, 42.6, 5.6)
BLOCK_GROOVES = [(28.0, 28.8), (32.1, 32.9)]
HUMP = [(44.0, 7.2, 8.6), (41.6, 8.2, 9.1), (39.0, 9.5, 9.3), (36.6, 11.0, 9.0), (34.4, 12.3, 8.4), (32.4, 13.3, 7.8)]
HUMP_W = [2.2, 3.1, 3.4, 3.2, 2.7, 2.1]
HUMP_BASE = 3.0
CLAW_STEM = [(28.6, 23.4, 2.4), (28.5, 25.6, 1.6), (28.4, 28.2, 0.6)]
CLAW_FORK = [[(26.9, 23.3, 2.6), (27.9, 25.3, 1.9)], [(30.6, 23.3, 2.6), (29.4, 25.3, 1.9)]]
CLAW_R = (1.25, 0.75)
CLAW_KNUCKLES = [(27.8, 29.9, -0.2, 1.7), (31.0, 29.9, -0.2, 1.7)]
CLAW_TIP = (29.4, 31.0, -0.7, 1.0)
PIN = (19.6, 26.0, 18.6, 5.1, 0.85)
# The core under the hull and the beams, dark, filling the seams between the parts: its left half's outline, its
# bottom and top.
CORE = [(71.5, 9.6), (44.0, 9.6), (40.0, 12.2), (39.6, 17.0), (19.6, 17.0), (17.5, 19.6), (16.6, 23.6), (17.4, 25.8),
        (21.6, 26.9), (25.9, 26.7), (26.4, 25.0), (31.8, 24.6), (42.2, 24.6), (42.4, 31.9), (46.2, 32.2), (47.6, 36.2),
        (51.5, 40.8), (63.6, 40.8), (68.0, 36.0), (71.5, 36.0)]
CORE_Z = (-2.4, 3.4)
# The arm: the shoulder pad's outer lobe (plan; its top, its foot; the grooves across it: rows) and inner lobe (plan,
# top), the grey joint under the inner lobe (plan, top).
PAD_OUTER = [(12.9, 10.1), (14.6, 10.1), (14.6, 19.9), (7.9, 19.9), (7.9, 13.4), (8.8, 12.1), (10.5, 11.0)]
PAD_TOP, PAD_BASE = 9.8, 3.0
PAD_GROOVES = [13.1, 15.3]
PAD_INNER = [(14.4, 10.0), (17.8, 10.0), (18.8, 10.9), (19.8, 12.0), (20.2, 13.0), (20.2, 16.6), (14.4, 16.6)]
PAD_INNER_TOP = 8.8
JOINT = [(14.6, 16.4), (20.4, 16.4), (20.4, 19.9), (14.6, 19.9)]
JOINT_TOP = 7.6
# The tube: its axis column, the rows of its shoulder (the rounded top's middle) and of its foot (in the cuff), its
# axis height there, its half-width and half-height, how far its rounded top reaches up, how much narrower its foot
# is; the flutes (how many round it, how deep, the rows they run between).
TUBE = (9.25, 24.6, 36.4, 2.6, 1.6, 6.0, 4.8, 5.0, 0.92)
FLUTES, FLUTE_DEPTH, FLUTE_ROWS = 18, 0.55, (26.4, 35.4)
# The cuff: from column to column, its row, axis height, half-length (y) and half-height (z); the collar on it.
CUFF = (3.3, 19.6, 37.9, 1.3, 2.45, 4.4)
COLLAR = (7.8, 10.6)
# The pod: its plan, its top, where its face begins and ends (rows), the face's bottom height, its bottom; the socket
# (centre column and row, half-width across, half-length in plan, depth); the pupil (column, row); the nozzle (row, z,
# from column to column, radius).
POD = [(7.6, 39.0), (20.4, 39.0), (21.0, 39.8), (21.0, 49.8), (20.0, 50.9), (19.0, 51.9), (17.8, 52.9), (16.0, 53.8),
       (10.2, 53.8), (9.0, 52.9), (8.0, 51.9), (7.0, 50.6), (7.0, 40.4)]
POD_TOP, POD_FACE, POD_FACE_LOW, POD_BOTTOM = 4.6, (43.2, 53.8), -2.4, -3.6
SOCKET_EYE = (14.5, 47.5, 3.6, 3.5, 1.5)
PUPIL = (13.4, 46.2)
NOZZLE = (48.0, 0.4, 9.4, 7.2, 0.9)
# The hose: its path (column, row, z, radius) from under the bar to the pod's top.
HOSE = [(21.8, 23.4, 1.8, 2.9), (20.8, 25.2, 2.4, 2.9), (19.4, 27.0, 2.8, 2.8), (18.2, 29.0, 3.0, 2.7),
        (17.4, 31.0, 3.0, 2.5), (17.0, 33.0, 2.9, 2.4), (17.1, 35.0, 2.7, 2.3), (17.7, 37.0, 2.3, 2.2),
        (18.3, 39.0, 1.8, 2.1), (18.5, 40.8, 1.3, 2.0)]


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.4, glow=0.0, glow_index=None):
        if glow > 0:
            return k.material("deli_" + name, palette=index, metallic=metallic, roughness=roughness,
                              emission=pal[index if glow_index is None else glow_index], emission_strength=glow)
        return k.material("deli_" + name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "core": mat("core", 0x01, 0.25, 0.65),
        "red_dark": mat("red_dark", 0x45, 0.35, 0.4),
        "red": mat("red", 0x47, 0.35, 0.34),
        "red_lit": mat("red_lit", 0x49, 0.3, 0.3),
        "black": mat("black", 0x02, 0.45, 0.2),
        "black_lit": mat("black_lit", 0x05, 0.45, 0.24),
        # The spheres: glossy, in bands of the sprite's light (dark at the edges, a soft glare at the upper left, a
        # rim lit underneath), each with a little light of its own so that they don't read as holes.
        "sphere": mat("sphere", 0x04, 0.45, 0.12, glow=0.16, glow_index=0x04),
        "sphere_mid": mat("sphere_mid", 0x06, 0.45, 0.1, glow=0.14, glow_index=0x06),
        "sphere_glare": mat("sphere_glare", 0x0c, 0.3, 0.08, glow=0.12, glow_index=0x0c),
        "glass": mat("glass", 0x03, 0.35, 0.08, glow=0.14, glow_index=0x04),    # also the spheres' dark band
        "steel": mat("steel", 0x07, 0.6, 0.3),
        "steel_light": mat("steel_light", 0x0a, 0.6, 0.26),
        "fire_low": mat("fire_low", 0x73, 0.0, 0.5, glow=0.3),
        "fire": mat("fire", 0x76, 0.0, 0.5, glow=0.42),
        "fire_hot": mat("fire_hot", 0x79, 0.0, 0.45, glow=0.55),
        "eye_rim": mat("eye_rim", 0x73, 0.0, 0.35, glow=0.3),
        "eye": mat("eye", 0x77, 0.0, 0.3, glow=0.45),
        "eye_hot": mat("eye_hot", 0x7c, 0.0, 0.25, glow=0.6),
    }


# --- Helpers ---------------------------------------------------------------------------------------------------------

def x_plane(c0, z0, c1, z1):
    """A plane z0 at column c0, z1 at column c1, level along y (in the built frame)."""
    a0, a1 = XE(c0), XE(c1)
    return lambda x, y: z0 + (z1 - z0) * (x - a0) / (a1 - a0)


def y_plane(r0, z0, r1, z1):
    a0, a1 = YE(r0), YE(r1)
    return lambda x, y: z0 + (z1 - z0) * (y - a0) / (a1 - a0)


def level(z):
    return lambda x, y: z + 0.0 * x


def mirrored_plane(f):
    return lambda x, y: f(-x, y)


def edge_plane(a, b, inset, slope, z0):
    """A plane z0 along the line inset pixels inside the edge a-b (pixel edges), falling by slope per pixel outwards
    (away from the line's inner side, the side of the deck)."""
    ax, ay = P(*a)
    bx, by = P(*b)
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    nx, ny = dy / length, -dx / length
    # the outward side: away from the deck's middle (x towards 0 is inward)
    if nx * (0.0 - ax) + ny * (YE(24.0) - ay) > 0:
        nx, ny = -nx, -ny
    return lambda x, y: z0 - slope * ((x - ax) * nx + (y - ay) * ny + inset)


def cut_by(body, planes):
    """A prism intersected with the half-spaces under the planes (polish_arch.py's wing)."""
    for i, top in enumerate(planes):
        mk.boolean(body, plane_box(f"{body.name}_plane{i}", top, size=120.0), "INTERSECT")
    return body


def box_cutter(name, x0, x1, y0, y1, z0, z1, mat):
    return mk.box(name, x0, x1, y0, y1, z0, z1, mat)


def plate(name, outline, planes, mat, bevel=0.45, segments=3, bottom=DECK_BOTTOM + 1.0, cutters=()):
    """A plate of a plan (x, y) cut by planes, bevelled (before the cuts, so that the bevel stays clean: bevelling a
    boolean's slots and sockets filled them in again), then the cutters taken out of it; shaded."""
    body = mk.prism(name, outline, bottom, 30.0, mat)
    cut_by(body, list(planes))
    mk.cleanup(body)
    if bevel > 0:
        mk.bevel(body, bevel, segments, 30.0)
    for c in cutters:
        mk.boolean(body, c, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    mk.shade(body, 35.0)
    return body


def paint_red(obj, m, top="red", keep_names=()):
    """Red faces by how they face: tops red, chamfers facing the sun lit, walls facing it red, the others dark; faces
    of the materials keep_names are kept (the cuts' dark)."""
    mats = obj.data.materials
    keep = {m[n].name for n in keep_names} | {m["core"].name}
    slots = {}
    for poly in obj.data.polygons:
        if mats[poly.material_index].name in keep:
            continue
        n = poly.normal
        if n.z > 0.97:
            mat = m[top]
        elif n.z > 0.45:
            mat = m["red_lit"] if (n.y > 0.2 or n.x < -0.2) else m[top]
        elif n.z > -0.2:
            mat = m["red"] if (n.y > 0.3 or n.x < -0.5) else m["red_dark"]
        else:
            mat = m["red_dark"]
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]


def paint_by_normal(obj, top=None, side=None, under=None, top_min=0.8, under_max=0.05, lit=None,
                    lit_dir=(-0.6, 0.6, 0.5), lit_min=0.55):
    """Faces facing up get top, the downward ones under, the rest side (None: kept); with lit, the sides facing
    lit_dir (the upper left, the sun's side) get lit."""
    lit_v = Vector(lit_dir).normalized()

    def pick(c, n):
        if top is not None and n.z > top_min:
            return top
        if under is not None and n.z < under_max:
            return under
        if lit is not None and n.dot(lit_v) > lit_min:
            return lit
        return side
    mk.paint(obj, pick)


def section_ring(y, cx, half_w, z0, z1, power=2.6, segments=24):
    """A ring across the y axis at y: a superellipse from z0 to z1, half_w across."""
    zc, hh = (z0 + z1) / 2, (z1 - z0) / 2
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        u, v = mk.superellipse_point(a, power)
        pts.append(Vector((cx + u * half_w, y, zc + v * hh)))
    return pts


def loft_y(name, stations, mat, power=2.6, segments=24):
    """A body lofted along y through stations (y, centre x, half-width, z0, z1), its ends closed to points."""
    rings = [section_ring(y, cx, hw, z0, z1, power, segments) for y, cx, hw, z0, z1 in stations]
    first, last = stations[0], stations[-1]
    return k.loft(name, rings, mat, start_point=(first[1], first[0], (first[3] + first[4]) / 2),
                  end_point=(last[1], last[0], (last[3] + last[4]) / 2))


def plan_width(poly, y):
    """The x range of a plan (x, y) at y (its leftmost and rightmost crossings)."""
    xs = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        if (ay - y) * (by - y) <= 0 and ay != by:
            xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def tube_path(name, points, radius, mat, segments=14, iterations=2, squash=1.0, ends=0.7):
    """A round bar along points (x, y, z) or (x, y, z, radius), its path (and radii) rounded (Chaikin), its ends
    rounded."""
    pts4 = [tuple(p) if len(p) == 4 else tuple(p) + (radius,) for p in points]
    dense = mk.chaikin(pts4, iterations, closed=False)
    pts = [Vector(p[:3]) for p in dense]
    radii = [p[3] for p in dense]
    rings = []
    for i, p in enumerate(pts):
        radius = radii[i]
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        a = t.cross(ref).normalized()
        b = t.cross(a).normalized()
        if b.z < 0:
            b = -b
        rings.append([p + a * math.cos(2 * math.pi * j / segments) * radius +
                      b * math.sin(2 * math.pi * j / segments) * radius * squash for j in range(segments)])
    t0 = (pts[0] - pts[1]).normalized()
    t1 = (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] + t0 * radii[0] * ends, end_point=pts[-1] + t1 * radii[-1] * ends)
    return k.smooth(obj, 60)


# --- The hull --------------------------------------------------------------------------------------------------------

def socket_cutters(name, grow, mat, both=True):
    c, r, z, (rx, ry, rz) = SPHERE
    x, y = P(c, r)
    out = []
    for sx in ((1, -1) if both else (1,)):
        out.append(k.ellipsoid(f"{name}_{'l' if sx > 0 else 'r'}", (sx * x, y, z), (rx + grow, ry + grow, rz + grow),
                               mat, 36, 18))
    return out


def deck(m):
    """The red deck under the plates (whole): its plan cut by its top and chamfers, bevelled; the sockets and the slot
    cut into it, dark."""
    flank = x_plane(DECK_FLANK[0], DECK_TOP, DECK_FLANK[2], DECK_FLANK[1])
    corner = edge_plane(DECK_CORNER[0], DECK_CORNER[1], DECK_CORNER[2], DECK_CORNER[3], DECK_TOP)
    planes = [level(DECK_TOP), y_plane(DECK_BACK[0], DECK_TOP, DECK_BACK[2], DECK_BACK[1]), flank,
              mirrored_plane(flank), y_plane(DECK_FRONT[0], DECK_TOP, DECK_FRONT[2], DECK_FRONT[1]), corner,
              mirrored_plane(corner)]
    cutters = socket_cutters("deck_socket", SOCKET, m["core"])
    x0, x1, r0, r1, floor = SLOT
    cutters.append(box_cutter("slot_cut", XE(x0), XE(x1), YE(r1), YE(r0), floor, 20.0, m["core"]))
    body = plate("deck", mk.chaikin(whole_plan(DECK), 1), planes, m["red"], bevel=0.5, bottom=DECK_BOTTOM,
                 cutters=cutters)
    paint_red(body, m, top="red_dark")
    return body


def shoulder(m):
    """The shoulder plate (left), its vent and louvre cut into it."""
    flank = x_plane(SHOULDER_FLANK[0], SHOULDER_TOP, SHOULDER_FLANK[2], SHOULDER_FLANK[1])
    planes = [level(SHOULDER_TOP), y_plane(SHOULDER_BACK[0], SHOULDER_TOP, SHOULDER_BACK[2], SHOULDER_BACK[1]), flank]
    cutters = socket_cutters("shoulder_socket", SOCKET, m["core"], both=False)
    for c0, c1 in VENT_SLOTS:
        cutters.append(box_cutter("vent_cut", XE(c0), XE(c1), YE(VENT_ROWS[1]), YE(VENT_ROWS[0]),
                                  SHOULDER_TOP - SLOT_DEPTH, 20.0, m["core"]))
    for r0, r1 in LOUVRE_ROWS:
        cutters.append(box_cutter("louvre_cut", XE(LOUVRE_COLS[0]), XE(LOUVRE_COLS[1]), YE(r1), YE(r0),
                                  SHOULDER_TOP - SLOT_DEPTH, 20.0, m["core"]))
    body = plate("shoulder", mk.chaikin(plan(SHOULDER), 1), planes, m["red"], bevel=0.45, bottom=DECK_TOP - 1.5,
                 cutters=cutters)
    paint_red(body, m)
    return body


def lobe(m):
    """The lobe plate under the sphere (left), its seams cut across it."""
    corner = edge_plane(LOBE_CORNER[0], LOBE_CORNER[1], LOBE_CORNER[2], LOBE_CORNER[3], LOBE_TOP)
    planes = [level(LOBE_TOP), y_plane(LOBE_FRONT[0], LOBE_TOP, LOBE_FRONT[2], LOBE_FRONT[1]), corner]
    cutters = socket_cutters("lobe_socket", SOCKET, m["core"], both=False)
    for c0, c1 in LOBE_SEAMS:
        cutters.append(box_cutter("seam_cut", XE(c0), XE(c1), YE(LOBE_SEAM_ROWS[1]), YE(LOBE_SEAM_ROWS[0]), -1.0, 20.0,
                                  m["core"]))
    body = plate("lobe", mk.chaikin(plan(LOBE), 1), planes, m["red"], bevel=0.45, bottom=DECK_BOTTOM + 0.5,
                 cutters=cutters)
    paint_red(body, m)
    return body


def rim(m):
    """A lit rim round the sphere's socket on the deck (the frame's inner edge, left)."""
    c, r, z, (rx, ry, rz) = SPHERE
    x, y = P(c, r)
    f = math.sqrt(max(0.0, 1 - ((DECK_TOP - z) / (rz + SOCKET)) ** 2))
    ax, ay = (rx + SOCKET) * f + RIM_R * 0.55, (ry + SOCKET) * f + RIM_R * 0.55
    count, seg = 48, 5
    rings = []
    for i in range(count):
        a = 2 * math.pi * i / count
        p = Vector((x + ax * math.cos(a), y + ay * math.sin(a), DECK_TOP - 0.2))
        out = Vector((math.cos(a) / ax, math.sin(a) / ay, 0)).normalized()
        rings.append([p + out * math.cos(math.pi * j / (seg - 1)) * RIM_R +
                      Vector((0, 0, math.sin(math.pi * j / (seg - 1)) * RIM_R * 0.9)) for j in range(seg)])
    verts = [v for ring in rings for v in ring]
    faces = []
    for i in range(count):
        for j in range(seg - 1):
            a_, b = i * seg + j, i * seg + j + 1
            faces.append((a_, b, ((i + 1) % count) * seg + j + 1, ((i + 1) % count) * seg + j))
    obj = k.mesh_object("rim", verts, faces, m["red_lit"])
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def sphere(m):
    """The glossy black sphere (left), in bands of the sprite's light."""
    c, r, z, (rx, ry, rz) = SPHERE
    x, y = P(c, r)
    body = k.ellipsoid("sphere", (x, y, z), (rx, ry, rz), m["sphere"], 40, 20)
    light = Vector((-0.32, 0.38, 0.87)).normalized()
    values = []
    for v in body.data.vertices:
        nrm = Vector(((v.co.x - x) / rx ** 2, (v.co.y - y) / ry ** 2, (v.co.z - z) / rz ** 2)).normalized()
        t = nrm.dot(light)
        rim_light = max(0.0, -nrm.y - 0.55) * 1.6 * max(0.0, nrm.z + 0.2)   # the rim lit underneath (the sprite's
        values.append(max(t, 0.62 + rim_light * 0.35) if rim_light > 0 else t)  # light at its bottom)
    band_split(body, values, [(-9.0, m["glass"]), (0.55, m["sphere"]), (0.86, m["sphere_mid"]),
                              (0.975, m["sphere_glare"])])
    k.smooth(body, 80)
    return body


def fin(m):
    body = plate("fin", plan(FIN), [y_plane(24.0, FIN_Z[0], 31.6, FIN_Z[1])], m["red"], bevel=0.3, segments=2,
                 bottom=FIN_Z[2])
    paint_red(body, m)
    return body


def top_plate(m):
    """The spine (whole) and the left wing."""
    c0, c1, r0, r1, top, back_z = SPINE
    spine = plate("spine", plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)]), [level(top), y_plane(5.4, top, r0, back_z)],
                  m["red"], bevel=0.45, bottom=3.0)
    paint_red(spine, m)
    wing = plate("wing", plan(WING), [level(WING_TOP), x_plane(WING_CHAMFER[0], WING_TOP, WING_CHAMFER[1],
                                                               WING_CHAMFER[2])], m["red"], bevel=0.4, bottom=3.0)
    paint_red(wing, m)
    return spine, wing


def grille(m):
    """The housing (dark, its opening cut down to the fire), the fire's floor glowing (hottest in its middle rows),
    the slats across the opening."""
    opening = mk.prism("grille_opening", plan(OPENING), FIRE_Z + 0.3, 20.0, m["core"])
    housing = plate("grille_housing", plan(GRILLE), [level(GRILLE_TOP)], m["black"], bevel=0.3, segments=2,
                    bottom=2.0, cutters=[opening])
    paint_by_normal(housing, top=m["black_lit"], top_min=0.9)
    fire_bed(m, "grille_fire")
    for c in SLATS:
        x = XE(c)
        s = mk.box(f"slat{c}", x - SLAT_W / 2, x + SLAT_W / 2, YE(8.6), YE(1.5), FIRE_Z - 0.2, SLAT_TOP, m["black"])
        mk.boolean(s, mk.prism(f"slat_clip{c}", plan(OPENING), FIRE_Z - 1.0, 20.0, None), "INTERSECT")
        mk.cleanup(s)
        mk.bevel(s, 0.14, 1, 30.0)
        mk.shade(s, 35.0)
        paint_by_normal(s, top=m["black_lit"], top_min=0.9)
    return housing


def gap_middle(x):
    """How near x is to the middle of a gap between the slats (1 in the middle, 0 at a slat's middle)."""
    xs = [XE(c) for c in SLATS]
    d = min(abs(x - s) for s in xs)
    return min(1.0, d / ((xs[1] - xs[0]) / 2))


def fire_bed(m, name, mats=("fire_low", "fire", "fire_hot")):
    """The fire under the slats: a floor in the opening, cut into a fine grid; its tongues rise in the middles of the
    gaps and in its middle rows, where they glow hottest; dimmer at its ends (the sprite's dark top and bottom rows)."""
    floor = mk.prism(name, plan(OPENING), FIRE_Z - 0.5, FIRE_Z + 0.3, m[mats[1]])
    bm = bmesh.new()
    bm.from_mesh(floor.data)
    for i in range(1, 17):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=(XE(53.6) + i * 0.83, 0, 0), plane_no=(1, 0, 0))
    for i in range(1, 8):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=(0, YE(1.9 + i * 0.8), 0), plane_no=(0, 1, 0))
    bm.to_mesh(floor.data)
    bm.free()
    for v in floor.data.vertices:
        if v.co.z > FIRE_Z:
            row = 28.0 - v.co.y
            along = math.sin(math.pi * min(1.0, max(0.0, (row - 1.9) / 6.3)))
            v.co.z += 0.25 * along + 0.45 * along * gap_middle(v.co.x) ** 2
    floor.data.update()
    low = mk.slot_of(floor, m[mats[0]])
    hot = mk.slot_of(floor, m[mats[2]])
    for poly in floor.data.polygons:
        row = 28.0 - poly.center.y
        g = gap_middle(poly.center.x)
        if poly.normal.z < 0.3 or row < FIRE_LOW[0] or row > FIRE_LOW[1]:
            poly.material_index = low
        elif FIRE_HOT[0] < row < FIRE_HOT[1] and g > 0.45:
            poly.material_index = hot
        elif g < 0.3:
            poly.material_index = low
    k.smooth(floor, 30)
    return floor


def canopy(m):
    """The dark glass dome between the spheres (whole) and its grey frame: a bar across its back, rails down its
    sides, laid on the glass."""
    r, hw, hl, z0, z1 = CANOPY
    cy = YE(r)
    rad = 1.8
    profile = []
    for i in range(8):
        a = (math.pi / 2) * i / 7
        profile.append((1.0 - (1 - math.cos(a)) * rad / hw, z0 + (z1 - 0.45 - z0) * math.sin(a) ** 0.85))
    inner = 1.0 - rad / hw
    for i in range(1, 5):
        f = inner * (1 - i / 4)
        profile.append((max(f, 0.03), z1 - 0.45 + 0.45 * (1 - (f / inner) ** 2)))
    rings = []
    for s, z in profile:
        ring = []
        for j in range(40):
            u, v = mk.superellipse_point(2 * math.pi * j / 40, 4.0)
            ring.append(Vector((u * hw * s, cy + v * hl * s, z)))
        rings.append(ring)
    glass = k.loft("canopy", rings, m["glass"], start_point=(0, cy, z0), end_point=(0, cy, z1))
    k.smooth(glass, 50)
    bpy.context.view_layer.update()
    hit = mk.surface([glass])

    def strip(name, pts2d, width, lift=0.14, top=0.42, bottom=0.4):
        path, ups = [], []
        for x, y in pts2d:
            h = hit(x, y)
            if h is None:
                continue
            p, n = h
            path.append(p + n * lift)
            ups.append(n)
        bar = mk.bar(name, path, ups, width, top, bottom, m["steel"], segments=8, power=3.0)
        k.smooth(bar, 50)
        paint_by_normal(bar, top=m["steel_light"], top_min=0.6)
        return bar
    y_bar = (YE(CANOPY_BAR[0]) + YE(CANOPY_BAR[1])) / 2
    half_bar = (YE(CANOPY_BAR[0]) - YE(CANOPY_BAR[1])) / 2
    strip("canopy_bar", [(XE(65.4) + (XE(77.6) - XE(65.4)) * i / 28, y_bar) for i in range(29)], half_bar)
    xr = (XE(CANOPY_RAIL[0]) + XE(CANOPY_RAIL[1])) / 2
    half_rail = (XE(CANOPY_RAIL[1]) - XE(CANOPY_RAIL[0])) / 2
    ys = [YE(CANOPY_BAR[1]) + 0.3 - (YE(CANOPY_BAR[1]) + 0.3 - YE(24.3)) * i / 14 for i in range(15)]
    strip("canopy_rail_l", [(xr, y) for y in ys], half_rail)
    strip("canopy_rail_r", [(-xr, y) for y in ys], half_rail)
    return glass


def jaw(m):
    """The left prong (a groove down it, its lip a little higher)."""
    c0, c1, r0, r1 = PRONG_GROOVE
    groove = box_cutter("prong_groove", XE(c0), XE(c1), YE(r1), YE(r0), PRONG_TOP - 0.55, 20.0, m["core"])
    prong = plate("prong", plan(PRONG), [lambda x, y: LIP_TOP if y > YE(26.05) else PRONG_TOP], m["red"], bevel=0.35,
                  bottom=0.5, cutters=[groove])
    paint_red(prong, m)
    return prong


def nub(m):
    """The grey nub in the slot (whole): a short bar along y, its front end domed (lit), a dark collar at its back."""
    r0, r1, hw, hh, zc = NUB
    ys = [YE(r0), YE(r0) - 0.4, YE(r1) + 2.0]
    fs = [0.86, 1.0, 1.0]
    for i in range(1, 7):
        a = (math.pi / 2) * i / 7
        ys.append(YE(r1) + 2.0 - 2.0 * math.sin(a))
        fs.append(math.cos(a) * 0.92 + 0.08)
    rings = [k.ring(yv, hw * f, hh * f, 24, z=zc) for yv, f in zip(ys, fs)][::-1]
    body = k.loft("nub", rings, m["steel"], start_point=(0, YE(r1), zc), end_point=(0, YE(r0), zc))
    k.smooth(body, 50)
    mk.paint(body, lambda c, n: m["steel_light"] if n.y < -0.5 else None)
    collar = k.lathe("nub_collar", [(YE(r0) - 0.2, 0.0), (YE(r0) - 0.2, hw + 0.35), (YE(r0) + 0.8, hw + 0.35),
                                    (YE(r0) + 0.8, 0.0)], m["core"], segments=24, axis_z=zc, squash=hh / hw)
    k.smooth(collar, 40)
    return body


# --- The beams -----------------------------------------------------------------------------------------------------

def beam(m):
    bar = plate("bar", plan(BAR), [level(BAR_Z[1])], m["red"], bevel=0.55, bottom=BAR_Z[0])
    paint_red(bar, m)
    grooves = [box_cutter("block_groove", XE(c0), XE(c1), YE(20.0), YE(12.9), BLOCK_TOP - 0.7, 20.0, m["core"])
               for c0, c1 in BLOCK_GROOVES]
    block = plate("block", plan(BLOCK), [level(BLOCK_TOP)], m["red"], bevel=0.45, bottom=BAR_Z[0], cutters=grooves)
    paint_red(block, m)
    grooves = [box_cutter("block_low_groove", XE(c0), XE(c1), YE(20.0), YE(16.0), BLOCK_TOP - 0.9, 20.0, m["core"])
               for c0, c1 in BLOCK_GROOVES]
    low = plate("block_low", plan(BLOCK_LOW), [level(BLOCK_TOP - 0.2),
                                               x_plane(BLOCK_STEP[0], BLOCK_STEP[1], BLOCK_STEP[2], BLOCK_STEP[3])],
                m["red"], bevel=0.4, bottom=BAR_Z[0], cutters=grooves)
    paint_red(low, m)
    hump(m)
    claw(m)
    c0, c1, r, z, rad = PIN
    pin = mk.tube("pin", [(XE(c0), YE(r), z), (XE(c1), YE(r), z)], rad, m["steel"], segments=14)
    k.smooth(pin, 50)
    for cc in (c0 + 0.5, c1 - 0.6):
        col = k.lathe("pin_collar", [(-0.3, 0.0), (-0.3, rad + 0.3), (0.3, rad + 0.3), (0.3, 0.0)], m["steel_light"],
                      segments=14)
        col.data.transform(Matrix(((0, 1, 0, XE(cc)), (1, 0, 0, YE(r)), (0, 0, -1, z), (0, 0, 0, 1))))
        k.recalc_normals(col)
        k.smooth(col, 50)
    return bar


def hump(m):
    """The black fender over the block's back: rings across its path, a groove along its middle, rounded ends."""
    pts = [Vector((XE(c), YE(r), z)) for c, r, z in HUMP]
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)])
        t.z = 0
        t.normalize()
        across = Vector((-t.y, t.x, 0))
        w = HUMP_W[i]
        zc, hh = (p.z + HUMP_BASE) / 2, (p.z - HUMP_BASE) / 2
        ring = []
        for j in range(24):
            u, v = mk.superellipse_point(2 * math.pi * j / 24, 2.4)
            zz = zc + v * hh
            if v > 0:
                zz -= 0.5 * math.exp(-(u / 0.16) ** 2) * v       # the groove along its middle
            ring.append(Vector((p.x, p.y, 0)) + across * u * w + Vector((0, 0, zz)))
        rings.append(ring)
    t0 = (pts[0] - pts[1])
    t0.z = 0
    t1 = (pts[-1] - pts[-2])
    t1.z = 0
    body = k.loft("hump", rings, m["black"],
                  start_point=Vector((pts[0].x, pts[0].y, (pts[0].z + HUMP_BASE) / 2)) + t0.normalized() * 1.2,
                  end_point=Vector((pts[-1].x, pts[-1].y, (pts[-1].z + HUMP_BASE) / 2)) + t1.normalized() * 1.0)
    k.smooth(body, 60)
    paint_by_normal(body, lit=m["black_lit"], lit_min=0.86, lit_dir=(-0.35, 0.45, 0.82))
    return body


def claw(m):
    """The small claw hanging from the bar's front: a stem forked at its top, two knuckles at its foot, a tip."""
    parts = [tube_path("claw_stem", [(XE(c), YE(r), z) for c, r, z in CLAW_STEM], CLAW_R[0], m["red"], segments=12)]
    for i, fork in enumerate(CLAW_FORK):
        parts.append(tube_path(f"claw_fork{i}", [(XE(c), YE(r), z) for c, r, z in fork], CLAW_R[1], m["red"],
                               segments=10, iterations=0))
    for i, (c, r, z, rad) in enumerate(CLAW_KNUCKLES):
        parts.append(mk.ball(f"claw_knuckle{i}", (XE(c), YE(r), z), (rad, rad, rad * 0.85), m["red"], 16, 8))
    c, r, z, rad = CLAW_TIP
    parts.append(mk.ball("claw_tip", (XE(c), YE(r), z), (rad, rad, rad * 0.9), m["red"], 14, 7))
    for p in parts:
        paint_by_normal(p, lit=m["red_lit"], lit_min=0.6, lit_dir=(-0.4, 0.4, 0.8))
    return parts


def core(m):
    """The dark core under the hull and the beams (whole)."""
    body = mk.prism("core", whole_plan(CORE), CORE_Z[0], CORE_Z[1], m["core"])
    mk.cleanup(body)
    mk.shade(body, 35.0)
    return body


# --- The arms --------------------------------------------------------------------------------------------------------

def pad_lobe(name, outline, top, base, mat, grooves=(), steps=18, power=2.3):
    """A rounded lobe lofted along y over a plan: each section a superellipse from base to top, the grooves across it
    pinched in; its back and front ends rounded."""
    pts = plan(outline)
    y0 = min(p[1] for p in pts) + 0.05
    y1 = max(p[1] for p in pts) - 0.05
    ys = [y0 + (y1 - y0) * i / steps for i in range(steps + 1)]
    for g in grooves:
        yg = YE(g)
        ys += [yg - 0.45, yg - 0.2, yg, yg + 0.2, yg + 0.45]
    ys = sorted(set(round(v, 4) for v in ys if y0 <= v <= y1))
    stations = []
    for y in ys:
        w = plan_width(pts, y)
        if w is None:
            continue
        xl, xr = w
        f_end = min(1.0, math.sqrt(max(0.0, (y - y0) / 1.6)), math.sqrt(max(0.0, (y1 - y) / 1.2)))
        pinch = 1.0
        for g in grooves:
            d = abs(y - YE(g))
            if d < 0.45:
                pinch = min(pinch, 1.0 - 0.1 * (1 - d / 0.45))
        z_top = base + (top - base) * (0.55 + 0.45 * f_end) * pinch
        stations.append((y, (xl + xr) / 2, (xr - xl) / 2 * (0.75 + 0.25 * f_end) * pinch, base, z_top))
    body = loft_y(name, stations, mat, power=power, segments=24)
    return k.smooth(body, 60)


def arm(m):
    outer = pad_lobe("pad_outer", PAD_OUTER, PAD_TOP, PAD_BASE, m["black"], grooves=PAD_GROOVES)
    inner = pad_lobe("pad_inner", PAD_INNER, PAD_INNER_TOP, PAD_BASE, m["black"])
    for p in (outer, inner):
        paint_by_normal(p, lit=m["black_lit"], lit_min=0.86, lit_dir=(-0.45, 0.3, 0.84))
    joint = plate("joint", plan(JOINT), [level(JOINT_TOP)], m["steel"], bevel=0.4, bottom=1.5)
    paint_by_normal(joint, lit=m["steel_light"], lit_min=0.3, lit_dir=(-0.3, -0.5, 0.6))
    arm_tube(m)
    cuff(m)
    pod(m)
    hose = tube_path("hose", [(XE(c), YE(r), z, rad) for c, r, z, rad in HOSE], 2.0, m["black"], segments=16)
    paint_by_normal(hose, lit=m["black_lit"], lit_min=0.88, lit_dir=(-0.45, 0.35, 0.82))


def arm_tube(m):
    """The fluted tube from its rounded shoulder down into the cuff."""
    c, r_top, r_bot, z_top, z_bot, hw, hh, cap_h, foot = TUBE
    x = XE(c)
    y_top, y_bot = YE(r_top), YE(r_bot)
    seg = 60
    stations = []
    for i in range(10, 0, -1):
        a = (math.pi / 2) * i / 10
        stations.append((y_top + cap_h * math.sin(a), math.cos(a)))
    n_body = 20
    stations += [(y_top - (y_top - y_bot) * i / n_body, 1.0 - (1.0 - foot) * (i / n_body) ** 2)
                 for i in range(n_body + 1)]
    stations += [(y_bot - 0.45, foot * 0.94), (y_bot - 0.8, foot * 0.8)]   # its foot tucked into the cuff
    rings = []
    for y, f in stations:
        t = min(1.0, (y_top - y) / (y_top - y_bot)) if y <= y_top else 0.0
        zc = z_top + (z_bot - z_top) * t
        row = 28.0 - y
        fl = (smoothstep(FLUTE_ROWS[0], FLUTE_ROWS[0] + 1.2, row) *
              (1 - smoothstep(FLUTE_ROWS[1] - 0.8, FLUTE_ROWS[1], row)))
        ff = max(0.1, f)
        ring = []
        for j in range(seg):
            a = 2 * math.pi * j / seg
            s = math.sin(a)
            flute = 1.0
            if s > -0.25:
                flute -= FLUTE_DEPTH / hw * fl * (0.5 - 0.5 * math.cos(FLUTES * a)) * min(1.0, (s + 0.25) * 3)
            ring.append(Vector((x + math.cos(a) * hw * ff * flute, y, zc + s * hh * ff * flute)))
        rings.append(ring)
    tube = k.loft("arm_tube", rings, m["red"], start_point=(x, stations[0][0] + 0.1, z_top),
                  end_point=(x, y_bot - 0.95, z_bot))
    k.smooth(tube, 70)
    paint_by_normal(tube, lit=m["red_lit"], lit_min=0.82, lit_dir=(-0.55, 0.25, 0.8))
    return tube


def cuff(m):
    """The cuff across the tube's foot: a drum along x, its outer end rounded, a lit collar on it."""
    c0, c1, r, zc, hl, hh = CUFF
    y = YE(r)
    xs = []
    for i in range(8, 0, -1):
        a = (math.pi / 2) * i / 8
        xs.append((XE(c0) + 2.2 * (1 - math.sin(a)), max(0.2, math.cos(a))))
    xs += [(XE(c0) + 2.2 + (XE(c1) - 0.7 - XE(c0) - 2.2) * i / 12, 1.0) for i in range(13)]
    xs.append((XE(c1), 0.86))
    rings = [[Vector((xv, y + math.cos(2 * math.pi * j / 24) * hl * f, zc + math.sin(2 * math.pi * j / 24) * hh * f))
              for j in range(24)] for xv, f in xs]
    body = k.loft("cuff", rings, m["red"], start_point=(XE(c0), y, zc), end_point=(XE(c1) + 0.1, y, zc))
    k.smooth(body, 60)
    a, b = COLLAR
    mk.paint(body, lambda cc, n: m["red_lit"] if XE(a) < cc.x < XE(b) and n.z > 0.3 else
             (m["red_dark"] if n.z < -0.2 else None))
    return body


def pod_top(y):
    """The pod's top height at y: level, then its face sloping down towards the camera."""
    f0, f1 = YE(POD_FACE[0]), YE(POD_FACE[1])
    if y >= f0:
        return POD_TOP
    return POD_TOP + (POD_FACE_LOW - POD_TOP) * (f0 - y) / (f0 - f1)


def pod(m):
    """The gun pod: lofted across y over its plan (its top level, its face sloping down towards the camera), the
    socket cut into the face, the eye in it (a lens, its pupil hot), a brow over the socket, the nozzle."""
    pts = plan(POD)
    y0 = min(p[1] for p in pts) + 0.03
    y1 = max(p[1] for p in pts) - 0.03
    stations = []
    n = 28
    for i in range(n + 1):
        y = y1 - (y1 - y0) * i / n
        w = plan_width(pts, y)
        if w is None:
            continue
        xl, xr = w
        f = min(1.0, math.sqrt(max(0.0, (y1 - y) / 1.0)), math.sqrt(max(0.0, (y - y0) / 1.2)))
        stations.append((y, (xl + xr) / 2, max(0.3, (xr - xl) / 2 * (0.8 + 0.2 * f)), POD_BOTTOM, pod_top(y)))
    body = loft_y("pod", stations, m["red"], power=3.2, segments=32)
    k.smooth(body, 45)
    sc, sr, shw, shl, depth = SOCKET_EYE
    sx, sy = P(sc, sr)
    f0, f1 = YE(POD_FACE[0]), YE(POD_FACE[1])
    slope = math.atan2(POD_TOP - POD_FACE_LOW, f0 - f1)
    nrm = Vector((0.0, -math.sin(slope), math.cos(slope)))
    along = Vector((0.0, math.cos(slope), math.sin(slope)))
    centre = Vector((sx, sy, pod_top(sy)))
    half_along = shl / math.cos(slope)
    # The socket's cutter: a cylinder along the face's normal, its section an ellipse (shw across, half_along along
    # the face).
    rings = []
    for d in (-depth, 3.0):
        rings.append([centre + nrm * d + Vector((math.cos(2 * math.pi * j / 40) * shw, 0, 0)) +
                      along * math.sin(2 * math.pi * j / 40) * half_along for j in range(40)])
    well = k.loft("socket_cut", rings, m["core"])
    mk.boolean(body, well, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    k.smooth(body, 45)
    paint_by_normal(body, lit=m["red_lit"], lit_min=0.8, lit_dir=(-0.5, 0.35, 0.8))
    brow = mk.tube("pod_brow", [(XE(8.2), YE(POD_FACE[0]) + 0.1, POD_TOP - 0.1),
                                (XE(20.0), YE(POD_FACE[0]) + 0.1, POD_TOP - 0.1)], 0.55, m["red_lit"], segments=10)
    k.smooth(brow, 50)
    r_, z_, c0, c1, rad = NOZZLE
    nozzle = mk.tube("nozzle", [(XE(c0), YE(r_), z_), (XE(c1), YE(r_), z_)], rad, m["steel"], segments=12)
    k.smooth(nozzle, 50)
    tip = k.lathe("nozzle_tip", [(-0.25, 0.0), (-0.25, rad * 0.55), (0.0, rad * 0.55), (0.0, 0.0)], m["core"],
                  segments=12)
    tip.data.transform(Matrix(((0, 1, 0, XE(c1) - 0.02), (1, 0, 0, YE(r_)), (0, 0, -1, z_), (0, 0, 0, 1))))
    k.recalc_normals(tip)
    return body


def face_frame():
    """The pod's face: its slope, normal and the direction up along it."""
    f0, f1 = YE(POD_FACE[0]), YE(POD_FACE[1])
    slope = math.atan2(POD_TOP - POD_FACE_LOW, f0 - f1)
    return slope, Vector((0.0, -math.sin(slope), math.cos(slope))), Vector((0.0, math.cos(slope), math.sin(slope)))


def eye(m, side, name="eye", mats=("eye_rim", "eye", "eye_hot")):
    """The eye in a pod's socket (side 1 the left arm, -1 the right one): a lens bulging in the socket, in bands round
    its pupil, which the sprites draw at its upper left on both arms (a glint, not mirrored): a dark red rim, red,
    the hot yellow pupil."""
    sc, sr, shw, shl, depth = SOCKET_EYE
    sx, sy = P(sc, sr)
    sx *= side
    slope, nrm, along = face_frame()
    half_along = shl / math.cos(slope)
    centre = Vector((sx, sy, pod_top(sy))) - nrm * (depth * 0.62)
    to_face = Matrix(((1, 0, 0, 0), (0, along.y, nrm.y, 0), (0, along.z, nrm.z, 0), (0, 0, 0, 1)))
    lens = k.ellipsoid(name, (0, 0, 0), (shw - 1.05, half_along - 1.05, 1.05), m[mats[1]], 28, 12)
    lens.data.transform(Matrix.Translation(centre) @ to_face)
    k.recalc_normals(lens)
    px, py = P(*PUPIL)
    hot = Vector((sx + px - P(sc, sr)[0], py, 0.0))         # the pupil's offset from the socket's middle kept
    values = []
    for v in lens.data.vertices:
        local = to_face.inverted() @ (v.co - centre)
        top = max(0.0, local.z) / 1.05
        du = (v.co.x - hot.x) / (shw - 1.05)
        dv = (v.co.y - hot.y) / (shl - 1.0)
        values.append(math.hypot(du, dv) - 0.25 * top)
    band_split(lens, values, [(-9.0, m[mats[2]]), (0.28, m[mats[1]]), (0.95, m[mats[0]])])
    k.smooth(lens, 70)
    return lens


# --- Whole -----------------------------------------------------------------------------------------------------------

def mirror_half(objects):
    """Mirrored copies of the left half's parts about X = 0."""
    flip = Matrix.Scale(-1, 4, (1, 0, 0))
    out = []
    for obj in objects:
        mk.apply(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(flip)
        copy.data.flip_normals()
        copy.data.update()
        out.append(copy)
    return out


def build_parts(m):
    """The left half's parts (mirrored) and the whole parts; returns the meshes."""
    whole_names = ("deck", "core", "canopy", "canopy_bar", "canopy_rail_l", "canopy_rail_r", "spine", "nub",
                   "nub_collar")
    shoulder(m)
    lobe(m)
    rim(m)
    sphere(m)
    fin(m)
    top_plate(m)
    grille(m)
    jaw(m)
    nub(m)
    beam(m)
    arm(m)
    half = [o for o in mk.meshes() if o.name not in whole_names]
    mirror_half(half)
    eye(m, 1)
    eye(m, -1, "eye_r")
    deck(m)
    canopy(m)
    core(m)
    return mk.meshes()


def build_whole(m=None):
    m = m or materials()
    build_parts(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
        obj.data.update()
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def whole_mask(sheet, cells=None):
    """The twelve sprites' silhouettes placed as the levels place them: 144 x 56."""
    mask = [[False] * 144 for _ in range(56)]
    for name, sprite, col, row in (cells or CELLS):
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[row + y][col + x] = True
    return mask


def drop_unused(objects):
    """Takes the material slots no face uses off the objects (polish_ball_mast.py's)."""
    for obj in objects:
        mesh = obj.data
        used = sorted({p.material_index for p in mesh.polygons})
        if len(used) == len(mesh.materials):
            continue
        keep = [mesh.materials[i] for i in used]
        remap = {old: new for new, old in enumerate(used)}
        indices = [remap[p.material_index] for p in mesh.polygons]
        mesh.materials.clear()
        for mat in keep:
            mesh.materials.append(mat)
        mesh.polygons.foreach_set("material_index", indices)
        mesh.update()


def join(parts, name):
    """The parts of a piece as one object (its custom normals kept), so that the GLB holds one mesh with a primitive
    per material instead of one per part and material (a third smaller)."""
    with bpy.context.temp_override(active_object=parts[0], selected_editable_objects=parts, object=parts[0]):
        bpy.ops.object.join()
    obj = parts[0]
    obj.name = name
    drop_unused([obj])
    return obj


def export_pieces(whole, m, pieces, options, sheet=None, label="T"):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box in pieces:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["core"]) for src in whole) if p is not None]
        drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:12]:
                print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
        parts = [join(parts, name)]
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (%s %d)" % (name, label, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole boss: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:16]:
        print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_T.png") if "check" in options else None
    if sheet:
        mk.compare("whole (T 1-11 above 39-49)", mk.coverage(whole, 144, 56), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "deli_boss_whole", whole, size=(144, 56), scale=8, distance=3.2)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        export_pieces(whole, m, PIECES, options, sheet)


if __name__ == "__main__":
    build()
