"""TYRIAN's and HOLES's two golden machines on the dirt (sheet 2, 2x2 sprites: each machine one 48 x 56 picture of four;
ground layer in TYRIAN and TYRIAN X, top layer in HOLES; not animated), polished (2026-10-21; they replace
wave3_p_ground.py's domes_whole() and pyramid_whole(): a slab with four plain spheres and a slab with a tetrahedron).
- gold_domes_tl, _tr, _bl, _br (2 77, 79 above 115, 117; enemies 123, 124, 121, 122 of episodes 1 and 3): a dark steel
  housing with four golden domes;
- gold_pyramid_tl, _tr, _bl, _br (2 81, 83 above 119, 121; enemies 127, 128, 125, 126): a dark steel capsule with a
  golden pyramid lying on it and golden horns.
TYRIAN's and TYRIAN X's event 12 (t 132-916) makes the bottom-left enemy (121 or 125) at (x, y) and the next three at
(x + 24, y), (x, y - 28) and (x + 24, y - 28): the sprites as the sheet arranges them, 77 and 79 (81, 83) above 115 and
117 (119, 121); HOLES's events 7 (t 725-1052) put them the same way (y -29 above -1). Each event group is one layer and
the four move together. None of the eight sprites is another sprite's pixels mirrored, turned or in other ramps, and
no other enemy shows them (catalog.json; GAUNTLET's, FLEET's and MACES's events 49-52 with these numbers are other
shapes: there they name graphics, not enemies).

As the sprites and their 4x upscales draw them (columns and rows of each 48 x 56 picture; the gold is ramp 1's light
shades, 0x15-0x1f with cream highlights, the steel ramp 0's 0x02-0x08; the dirt round them is ramp 1's dark shades and
is the map's ground, not modelled; the black patches right of and below them are their shadows, left out too):
- the domes: the housing (columns 2-37 of rows 12-39, columns 7-32 below that, its lower corners cut off on the
  diagonal (lit on the left) to a bottom edge at row 51) is plates of dark steel: a shoulder plate up each side of the
  big dome (columns 2-9, a seam across at row 20), a raised keel in the middle (the Y between the side domes, rows
  22-37, a seam down its stem), two small blocks either side of the bottom dome (columns 8-11 and 27-30 of rows
  39-41). The big dome (columns 6-31 of rows 1-22) wears an arch-shaped plate on its face (columns 13-24 of rows 6-12,
  its legs down to row 20 either side of a shadowed recess, lit at its upper left) between two dark slots (columns 11
  and 26 of rows 9-14); golden pipes run from its lower sides into the tops of the two side domes (columns 2-14 and
  24-36 of rows 26-35), each held by a steel clamp of two bars over its front (columns 6-10 of rows 30-35, its edge
  lit blue-grey); the bottom dome (columns 13-25 of rows 35-45) has a dark port in its lower middle (columns 17-20 of
  rows 40-42). The machine is symmetric about the middle of column 19 (x -4.5); the big dome is drawn half a pixel
  left of it (x -5).
- the pyramid: the capsule (columns 10-30 of rows 3-46, its top rounded, three panels between seams at columns 17 and
  24) splits below row 35 into two legs (columns 10-17 and 23-29) with the ground between them, their outer corners
  cut off on the diagonal; a golden pyramid lies across it (its point at row 12, column 20; its base corners at
  columns 5 and 35 of row 27, past the capsule's sides; its front point at row 29): its left face lit, its right face
  dark, a ridge between, narrow faces along its lower edges; a golden rod runs down from its front point into the gap
  between the legs (columns 19-21 of rows 29-34); golden horns curl out from the capsule's sides, two a side (from
  rows 9-10 and 14-15 down to the dirt at columns 3-4 and 36-37). Symmetric about the middle of column 20 (x -3.5).

Built as such machines: CAD-like solids (polish_machine_kit: plans extruded, cut by planes with exact booleans,
grooves cut in, edges bevelled, flat faces kept flat) for the steel, smooth domes (half ellipsoids) and bars for the
gold, the plates and clamps laid on the domes' surfaces (polish_redjet.facet), the slots and the port cut in. Heights
give the slanted camera depth: the housing 3 pixels high (its shoulders 4, its keel 4.3), its front and its cut-off
lower corners battered down to the dirt; the big dome rising to 10, the side domes to 7.1, the bottom dome to 6.5; the
capsule 5 high with rounded edges, three panels standing proud on its top; the pyramid's ridge rising from its point
(4.7) to 12 over its front point. Every wall reaches SKIRT under the dirt, so the machines stand on the terrain with
height=-4. The gold and the steel are shaded by their faces' turn to the light as the sprites shade them (lit to the
upper left, darker to the lower right), on top of the game's own light: the gold in five shades of ramp 1 (0x15,
0x17, 0x1a, 0x1c, 0x1e; the domes', pipes', rod's and horns' bands with smooth borders, polish_orb_red.band_split),
a little metallic (0.25-0.3: more reads olive in the game's light), the steel in six of ramp 0 (0x01-0x06), the
clamps 0x08 with blue-grey lit faces (0x6b), the slots and the port 0x10. Nothing glows.
The whole is built about the picture's centre and cut along the sprites' edges (polish_savara_boss.cut: the pieces
keep the whole's shading across the cuts, the faces' winding kept), each piece moved so that its sprite's centre is
its origin, its parts joined, every mesh triangulated before export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the dirt (z = 0); P(c, r)
turns a pixel edge of the picture (column c, row r) into the whole's coordinates (x = c - 24, y = 28 - r).

models.cfg (the model lines stay): sprite 2 77 gold_domes_tl yaw=0 height=-4, sprite 2 79 gold_domes_tr yaw=0
height=-4, sprite 2 115 gold_domes_bl yaw=0 height=-4, sprite 2 117 gold_domes_br yaw=0 height=-4, sprite 2 81
gold_pyramid_tl yaw=0 height=-4, sprite 2 83 gold_pyramid_tr yaw=0 height=-4, sprite 2 119 gold_pyramid_bl yaw=0
height=-4, sprite 2 121 gold_pyramid_br yaw=0 height=-4 (height=-4: on the terrain where TYRIAN and TYRIAN X put them
on the ground layer; in HOLES, on the top layer, they stand 2 pixels over background 3's plane).

Replaces wave3_p_ground.py's golden machines: remove XY(), dirtish(), machine_mask(), gold_mats(), housing(),
DOMES_HOUSING, PYRAMID_HOUSING, domes_whole(), pyramid_whole() and the two quarters("gold_domes" ...) and
quarters("gold_pyramid" ...) lines (and their docstring entries); inside_outline(), quarters() and works_whole() stay
(the red works use them; nothing else imports the file).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of each whole
and each piece against the machines' own pixels, OWN_DOMES and OWN_PYRAMID below), --preview <prefix> (the wholes'
and each piece's top and 3/4 views), --only <model,...> (or gold_domes / gold_pyramid for a machine's four).
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
from polish_arch import plane_box  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_redjet import facet, resample  # noqa: E402
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping the faces' winding)
from polish_squid_ship import rounded_rect  # noqa: E402

# The machines' own pixels in their 48 x 56 pictures ('#'): the dirt and the shadows round them left out.
OWN_DOMES = """
................#######.........................
.............#############......................
...........#################....................
..........###################...................
.........#####################..................
........#########################...............
.......##########################...............
......###########################...............
......###########################...............
.....############################...............
.....############################...............
.....############################...............
....#############################...............
...#################################............
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
.#####################################..........
.#####################################..........
.#####################################..........
.#####################################..........
.#####################################..........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
..###################################...........
.......#########################................
.......#########################................
.......#########################................
.......#########################................
.......#########################................
.......#########################................
..........###################...................
..........###################...................
...........#################....................
............###############.....................
.............#############......................
..............###########.......................
................................................
................................................
................................................
................................................
................................................
"""
OWN_PYRAMID = """
................................................
................................................
................................................
...............###########......................
.............###############....................
............#################...................
...........###################..................
..........#####################.................
..........#####################.................
.........######################.................
.......#########################................
......###.########################..............
.....###..#####################.###.............
.....##...#####################..###............
....##..#######################....#............
...##..#########################....#...........
......###.########################..#...........
......##..#####################.###.............
.....##.#######################..###............
....##...######################....#............
....#....######################.....#...........
....#....######################.....#...........
.........######################.................
.........#######################................
........#########################...............
.......###########################..............
......#############################.............
.....###############################............
.....###############################............
.......########################.................
.........######################.................
.........######################.................
.........######################.................
.........######################.................
.........######################.................
.........#########.....#########................
.........#########.....#########................
.........#########.....#########................
.........#########.....#########................
.........#########.....#########................
.........#########.....#########................
.........#########.....#########................
...........#######.....#######..................
............######.....######...................
.............#####.....#####....................
..............####.....####.....................
................##.....##.......................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
"""

# The pieces of each machine: (suffix, sprite, the box it covers in the whole's coordinates, its top left corner in
# the picture).
MACHINES = {"gold_domes": (77, 79, 115, 117), "gold_pyramid": (81, 83, 119, 121)}
QUARTERS = [("tl", (-24.0, 0.0, 0.0, 28.0), (0, 0)), ("tr", (0.0, 24.0, 0.0, 28.0), (24, 0)),
            ("bl", (-24.0, 0.0, -28.0, 0.0), (0, 28)), ("br", (0.0, 24.0, -28.0, 0.0), (24, 28))]

SKIRT = -3.0                 # how far the walls reach under the dirt
LIGHT = Vector((-0.45, 0.45, 0.77)).normalized()   # towards the sprites' light (and the game's sun): the upper left
# The gold's bands of the turn to the light (the lowest of shade, gold, lit, highlight; dark below).
GOLD_BANDS = (0.12, 0.38, 0.74, 0.93)


def P(c, r):
    """A pixel edge of the 48 x 56 picture (column c, row r) in the whole's coordinates."""
    return (c - 24.0, 28.0 - r)


def X(c):
    return c - 24.0


def Y(r):
    return 28.0 - r


def plan(points):
    """Pixel-edge points (c, r) to the whole's (x, y), counter-clockwise seen from above."""
    pts = [P(c, r) for c, r in points]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


def mirror_cols(points, axis_c):
    """A half outline (pixel edges, from the axis round one side) completed by its mirror image about column axis_c."""
    right = [(2 * axis_c - c, r) for c, r in reversed(points)]
    return points + right


# --- The domes: dimensions ------------------------------------------------------------------------------------------

AXIS_D = 19.5                # the housing's and the side and bottom domes' axis (pixel edge; x -4.5)
H0 = 3.0                     # the housing's top
# The housing's plan (pixel edges): the upper part, columns 2-37 of rows 12-39, the lower part columns 7-32, its lower
# corners cut off on the diagonal down to the bottom edge (row 50.8).
HOUSING = mirror_cols([(4.0, 12.0), (2.0, 14.0), (2.0, 39.0), (7.0, 39.0), (7.0, 43.6), (9.8, 45.0), (13.6, 50.8)],
                      AXIS_D)
FRONT = (47.4, 50.8)         # the battered front: its top edge (row; z = H0) and its foot (z = 0)
CHAMFER_INSET = 2.6          # the cut-off lower corners: their batter's top edge is this far in from the plan
# The shoulder plates up each side (left; the right is its mirror image), their top, the seam across them (row).
SHOULDER = [(2.5, 14.3), (4.3, 12.5), (10.8, 12.5), (10.8, 27.6), (2.5, 27.6)]
SHOULDER_TOP, SHOULDER_SEAM = H0 + 1.0, 20.3
# The keel: the Y between the side domes, its stem down to the bottom dome; its top; the seam down its stem.
KEEL = mirror_cols([(19.5, 21.6), (10.4, 21.6), (10.4, 24.2), (15.6, 29.6), (15.6, 36.8), (19.5, 36.8)][1:-1], AXIS_D)
KEEL_TOP = H0 + 1.3
# The small blocks either side of the bottom dome (left: columns, rows), their top.
BLOCK = (7.8, 12.0, 38.8, 42.2)
BLOCK_TOP = H0 + 1.1
# The domes: centre (pixel edges), plan radii, height, base.
BIG_DOME = ((19.0, 11.75), (13.2, 11.3), 10.5, -0.5)
SIDE_DOMES = [((8.5, 31.0), (6.9, 5.3), 5.6, 1.5), ((30.5, 31.0), (6.9, 5.3), 5.6, 1.5)]
BOTTOM_DOME = ((19.5, 40.5), (6.6, 5.6), 5.0, 1.5)
# The big dome's face: the arch plate (its bar: columns, rows; its legs: their columns, down to row) raised PLATE_H;
# the slots (column of their middle, rows), cut SLOT_D deep.
ARCH_BAR = (13.0, 25.0, 6.0, 13.2)
ARCH_LEGS = [(13.0, 15.0), (23.0, 25.0)]
ARCH_LEG_END = 21.0
PLATE_H = 0.75
SLOTS = [(11.5, 8.8, 15.2), (26.5, 8.8, 15.2)]
SLOT_W, SLOT_D = 1.3, 1.0
RECESS_DARK = 0.3            # how much darker the recess between the arch's legs is painted (its shadow)
# The pipes from the big dome into the side domes (the left one, pixel edges and height; the right one its mirror).
PIPE = [(10.3, 19.4, 2.6), (9.3, 21.4, 4.1), (8.4, 23.6, 5.0), (8.1, 25.6, 4.9), (8.2, 27.2, 4.3)]
PIPE_R = 0.9
# The clamps over the side domes' fronts: two bars (columns, relative to the dome's middle), from row CLAMP_ROWS[0] down
# over the dome's front edge to CLAMP_ROWS[1] on the housing.
CLAMP_BARS = [(-2.45, -0.2), (0.15, 2.4)]
CLAMP_ROWS = (29.6, 37.0)
CLAMP_LIFT, CLAMP_T = 0.25, 0.7
# The bottom dome's port: its middle (pixel edges), radii, depth.
PORT = ((19.0, 41.5), (1.6, 1.3), 1.4)

# --- The pyramid: dimensions ----------------------------------------------------------------------------------------

AXIS_P = 20.5                # its axis (pixel edge; x -3.5)
HC = 5.0                     # the capsule's top
CORNER_R = 6.5               # the capsule's top corners
# The capsule: its sides (columns), its top (row); the legs below SLOT_TOP: the gap between them (columns), their
# outer corners cut off from row LEG_CUT down to their tips at row LEG_END (columns from the gap).
CAP_SIDES, CAP_TOP = (10.0, 31.0), 3.0
LEG_SIDES, STEP_ROW = (9.2, 31.8), 27.5   # below the pyramid the capsule is a little wider (the legs)
SLOT_TOP, SLOT_COLS = 35.0, (18.0, 23.0)
LEG_CUT, LEG_END, LEG_TIP = 41.6, 47.0, 16.6
CAP_BEVEL = 1.1
# The three panels on its upper part (columns; the seams between them at 17 and 24), from its top down under the
# pyramid (rows), standing PANEL_H proud, PANEL_INSET in from its rounded outline, their edges rounded PANEL_BEVEL.
PANELS = [(10.7, 17.1), (17.7, 23.3), (23.9, 30.3)]
PANEL_ROWS, PANEL_H, PANEL_INSET, PANEL_BEVEL = (3.0, 24.0), 0.6, 0.65, 0.4
# The pyramid: its point, base corners and front point (pixel edges) at the capsule's top, the ridge's top over the
# front point (a little behind it), its height.
PYR_POINT, PYR_LEFT, PYR_FRONT = (20.5, 12.3), (4.8, 28.3), (20.5, 29.8)
PYR_TOP = (20.5, 28.6, HC + 7.0)
PYR_BASE = HC - 0.35
# The rod down from the front point (pixel edges and height), its radius.
ROD = [(20.5, 28.4, HC + 1.6), (20.5, 30.6, HC - 0.2), (20.5, 33.0, 3.6), (20.5, 35.2, 2.9)]
ROD_R = 0.95
# The horns (the left ones; the right ones their mirror images): paths (pixel edges, height, radius).
HORNS = [[(11.0, 9.2, 3.0, 1.35), (9.3, 9.9, 3.6, 1.3), (7.5, 11.1, 3.7, 1.2), (5.9, 12.7, 3.2, 1.05),
          (4.7, 14.5, 2.3, 0.9), (4.1, 16.0, 1.3, 0.78), (4.4, 17.2, 0.6, 0.66), (5.2, 17.7, 0.45, 0.55)],
         [(11.0, 14.2, 3.0, 1.35), (9.3, 14.9, 3.6, 1.3), (7.5, 16.1, 3.7, 1.2), (5.9, 17.7, 3.2, 1.05),
          (4.7, 19.5, 2.3, 0.9), (4.1, 21.0, 1.3, 0.78), (4.4, 22.2, 0.6, 0.66), (5.2, 22.7, 0.45, 0.55)]]
HORN_SHIFT = (0.0, 0.8)      # how far down the screen (rows) the left and the right horns sit (the right a row lower)


def materials():
    def mat(name, index, metallic, roughness):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "gold_dark": mat("goldm_gold_dark", 0x15, 0.3, 0.3),
        "gold_shade": mat("goldm_gold_shade", 0x17, 0.3, 0.28),
        "gold": mat("goldm_gold", 0x1a, 0.3, 0.25),
        "gold_lit": mat("goldm_gold_lit", 0x1c, 0.3, 0.23),
        "gold_hi": mat("goldm_gold_hi", 0x1e, 0.25, 0.2),
        "hole": mat("goldm_hole", 0x10, 0.2, 0.7),
        "steel_dark": mat("goldm_steel_dark", 0x01, 0.45, 0.5),
        "steel_shade": mat("goldm_steel_shade", 0x02, 0.5, 0.45),
        "steel": mat("goldm_steel", 0x03, 0.5, 0.42),
        "steel_top": mat("goldm_steel_top", 0x04, 0.5, 0.4),
        "steel_lit": mat("goldm_steel_lit", 0x05, 0.5, 0.38),
        "steel_edge": mat("goldm_steel_edge", 0x06, 0.5, 0.34),
        "clamp": mat("goldm_clamp", 0x08, 0.55, 0.32),
        "clamp_lit": mat("goldm_clamp_lit", 0x6b, 0.55, 0.28),
    }


# --- Helpers --------------------------------------------------------------------------------------------------------

def finish(obj, width, segments=2, angle=35.0):
    mk.cleanup(obj)
    mk.bevel(obj, width, segments, angle)
    mk.shade(obj, 35)
    return obj


def batter(p, q, inset, top):
    """The plane of a battered face along the plan edge p-q (whole coordinates; the solid on its left, seen from
    above): z 0 along the edge, top at inset pixels in from it (z(x, y))."""
    (px, py), (qx, qy) = p, q
    ex, ey = qx - px, qy - py
    length = math.hypot(ex, ey)
    nx, ny = -ey / length, ex / length            # inward (left of p -> q)
    return lambda x, y: top * ((x - px) * nx + (y - py) * ny) / inset


def dome_z(dome, x, y):
    """The top of a dome (centre, plan radii, height, base; pixel edges) at the whole's (x, y), or None outside."""
    (c, r), (a, b), h, z0 = dome
    cx, cy = P(c, r)
    t = ((x - cx) / a) ** 2 + ((y - cy) / b) ** 2
    if t >= 1.0:
        return None
    return z0 + h * math.sqrt(1.0 - t)


def gold_pick(m, hi=0.93, lit=0.76, mid=0.45, low=0.12):
    """Gold shaded by its faces' turn to the light."""
    def pick(c, n):
        d = n.dot(LIGHT)
        return (m["gold_hi"] if d > hi else m["gold_lit"] if d > lit else m["gold"] if d > mid else
                m["gold_shade"] if d > low else m["gold_dark"])
    return pick


def steel_pick(m):
    """Steel shaded by its faces' turn: lit edges facing the light, flat tops as they are, walls dark."""
    def pick(c, n):
        if n.z > 0.95:
            return None
        d = n.dot(LIGHT)
        if n.z > 0.3:
            return m["steel_edge"] if d > 0.8 else m["steel_lit"] if d > 0.62 else m["steel_shade"]
        return m["steel_lit"] if d > 0.35 else m["steel_dark"]
    return pick


def dome(name, spec, m, segments=48, steps=14):
    (c, r), (a, b), h, z0 = spec
    obj = mk.dome(name, P(c, r), (a, b, h), z0, m["gold"], segments, steps)
    return obj


def plate_on(name, outline, surface, height, mat, rim=0.28):
    """A plate lying on a surface (polish_redjet.facet over surface(x, y)), its outline resampled."""
    return k.smooth(facet(name, resample(outline, 0.4), surface, height, mat, rim=rim, steps=2, dome=0.0,
                          dome_rings=1, sink=0.6), 40)


def ring_obj(name, centre, radii, z, tube_r, mat, segments=24):
    """A ring (torus) lying flat round centre (x, y) at height z."""
    pts = []
    for j in range(segments + 1):
        a = 2 * math.pi * j / segments
        pts.append((centre[0] + radii[0] * math.cos(a), centre[1] + radii[1] * math.sin(a), z))
    return mk.tube(name, pts, tube_r, mat, 10, cap=False)


# --- The domes ------------------------------------------------------------------------------------------------------

def domes_housing(m):
    """The housing: its plan from under the dirt to H0, its front and its cut-off lower corners battered down to the
    dirt; the shoulder plates (a seam across each), the keel (a seam down its stem), the small blocks."""
    outline = plan(HOUSING)
    body = mk.prism("housing", outline, SKIRT, H0, m["steel"])
    front = batter(P(13.5, FRONT[1]), P(25.5, FRONT[1]), FRONT[1] - FRONT[0], H0)
    mk.boolean(body, plane_box("housing_front", front), "INTERSECT")
    for i, (p, q) in enumerate(((P(7.0, 44.0), P(13.5, FRONT[1])), (P(25.5, FRONT[1]), P(32.0, 44.0)))):
        mk.boolean(body, plane_box(f"housing_chamfer{i}", batter(p, q, CHAMFER_INSET, H0)), "INTERSECT")
    finish(body, 0.35)
    mk.paint(body, steel_pick(m))
    parts = [body]
    for side in (-1, 1):
        pts = SHOULDER if side < 0 else [(2 * AXIS_D - c, r) for c, r in reversed(SHOULDER)]
        sh = mk.prism(f"shoulder{side}", plan(pts), H0 - 0.5, SHOULDER_TOP, m["steel_top"])
        c0, c1 = (2.0, 11.5) if side < 0 else (27.5, 37.0)
        mk.boolean(sh, mk.box(f"shoulder_seam{side}", X(c0), X(c1), Y(SHOULDER_SEAM + 0.3), Y(SHOULDER_SEAM - 0.3),
                              SHOULDER_TOP - 0.45, SHOULDER_TOP + 2.0), "DIFFERENCE")
        finish(sh, 0.3)
        mk.paint(sh, steel_pick(m))
        parts.append(sh)
    keel = mk.prism("keel", plan(KEEL), H0 - 0.5, KEEL_TOP, m["steel_top"])
    mk.boolean(keel, mk.box("keel_seam", X(AXIS_D - 0.22), X(AXIS_D + 0.22), Y(37.5), Y(28.6), KEEL_TOP - 0.4,
                            KEEL_TOP + 2.0), "DIFFERENCE")
    finish(keel, 0.4, 2, 30)
    mk.paint(keel, steel_pick(m))
    parts.append(keel)
    c0, c1, r0, r1 = BLOCK
    for side, (a, b) in ((-1, (c0, c1)), (1, (2 * AXIS_D - c1, 2 * AXIS_D - c0))):
        blk = mk.box(f"block{side}", X(a), X(b), Y(r1), Y(r0), H0 - 0.5, BLOCK_TOP, m["steel_top"])
        finish(blk, 0.3)
        mk.paint(blk, steel_pick(m))
        parts.append(blk)
    return parts


def gold_bands(obj, m, darken=None):
    """Paints a smooth gold part in bands of its turn to the light (each vertex's normal; darken(co) lowers it where
    the sprite draws shadow), their borders smooth contours (polish_orb_red.band_split), shaded smooth again."""
    obj.data.update()
    values = []
    for v in obj.data.vertices:
        d = v.normal.dot(LIGHT)
        if darken is not None:
            d -= darken(v.co)
        values.append(d)
    band_split(obj, values, [(-99.0, m["gold_dark"]), (GOLD_BANDS[0], m["gold_shade"]), (GOLD_BANDS[1], m["gold"]),
                             (GOLD_BANDS[2], m["gold_lit"]), (GOLD_BANDS[3], m["gold_hi"])])
    return k.smooth(obj, 50)


def cut_in(obj, name, outline, spec, depth, mat):
    """Cuts a hole of the plan outline into a dome (spec) depth deep under its surface; its walls and floor mat."""
    cutter = mk.prism(name, outline, 0.0, 30.0, mat)
    for v in cutter.data.vertices:
        if v.co.z < 1.0:
            v.co.z = (dome_z(spec, v.co.x, v.co.y) or 0.0) - depth
    cutter.data.update()
    mk.boolean(obj, cutter, "DIFFERENCE")
    return k.smooth(obj, 50)


def big_dome(m):
    """The big dome with its arch plate and its two slots; the recess between the arch's legs in shadow."""
    body = dome("big_dome", BIG_DOME, m, 56, 16)
    c0, c1, r0, r1 = ARCH_BAR
    rx0, rx1, ry0, ry1 = X(ARCH_LEGS[0][1]), X(ARCH_LEGS[1][0]), Y(ARCH_LEG_END), Y(r1)

    def recess(co):
        inside = min(co.x - rx0, rx1 - co.x, co.y - ry0, ry1 - co.y)
        return RECESS_DARK * mk.smoothstep(-0.3, 0.5, inside)
    gold_bands(body, m, recess)
    for i, (c, s0, s1) in enumerate(SLOTS):
        x = X(c)
        cut_in(body, f"slot_cut{i}", rounded_rect(x - SLOT_W / 2, x + SLOT_W / 2, Y(s1), Y(s0), SLOT_W / 2 - 0.05, 3),
               BIG_DOME, SLOT_D, m["hole"])
    surface = lambda x, y: dome_z(BIG_DOME, x, y) or 0.0   # noqa: E731
    bar = plate_on("arch_bar", rounded_rect(X(c0), X(c1), Y(r1), Y(r0), 0.9, 4), surface, PLATE_H, m["gold_lit"])
    legs = []
    for i, (a, b) in enumerate(ARCH_LEGS):
        legs.append(plate_on(f"arch_leg{i}", rounded_rect(X(a), X(b), Y(ARCH_LEG_END), Y(r1) + 0.6, 0.45, 3), surface,
                             PLATE_H, m["gold_lit"]))
    for obj in [bar] + legs:
        mk.paint(obj, gold_pick(m, hi=0.93, lit=0.72, mid=0.4, low=0.1))
    return [body, bar] + legs


def side_domes(m):
    """The side domes, each held by a clamp of two bars over its front; the pipes from the big dome into them."""
    parts = []
    for i, spec in enumerate(SIDE_DOMES):
        obj = gold_bands(dome(f"side_dome{i}", spec, m, 40, 12), m)
        parts.append(obj)
        (c, r), _, _, _ = spec
        cx = X(c)

        def surface(x, y, spec=spec):
            z = dome_z(spec, x, y)
            return H0 if z is None else max(z, H0)
        for j, (a, b) in enumerate(CLAMP_BARS):
            bar = plate_on(f"clamp{i}_{j}", rounded_rect(cx + a, cx + b, Y(CLAMP_ROWS[1]), Y(CLAMP_ROWS[0]), 0.35, 3),
                           lambda x, y, s=surface: s(x, y) + CLAMP_LIFT, CLAMP_T, m["clamp"], rim=0.25)
            mk.paint(bar, lambda cc, n: m["clamp_lit"] if n.dot(LIGHT) > 0.72 else m["steel_shade"] if n.z < 0.2
                     else None)
            parts.append(bar)
    for side in (-1, 1):
        pts = []
        for c, r, z in PIPE:
            cc = c if side < 0 else 2 * 19.25 - c
            pts.append((X(cc), Y(r), z, PIPE_R))
        pipe = mk.smooth_tube(f"pipe{side}", pts, m["gold"], 14)
        parts.append(gold_bands(pipe, m))
    return parts


def bottom_dome(m):
    """The bottom dome with its dark port (cut in, a lit rim round it)."""
    obj = gold_bands(dome("bottom_dome", BOTTOM_DOME, m, 40, 12), m)
    (c, r), (a, b), depth = PORT
    x, y = P(c, r)
    pts = [(x + a * math.cos(2 * math.pi * j / 20), y + b * math.sin(2 * math.pi * j / 20)) for j in range(20)]
    cut_in(obj, "port_cut", pts, BOTTOM_DOME, depth, m["hole"])
    rim = ring_obj("port_rim", (x, y), (a + 0.25, b + 0.25), (dome_z(BOTTOM_DOME, x, y) or 0.0) - 0.1, 0.32,
                   m["gold_lit"], 24)
    k.smooth(rim, 60)
    mk.paint(rim, gold_pick(m))
    return [obj, rim]


def domes_whole(m):
    parts = domes_housing(m) + big_dome(m) + side_domes(m) + bottom_dome(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


# --- The pyramid ----------------------------------------------------------------------------------------------------

def capsule(m):
    """The capsule: its top rounded, splitting into two legs (the ground between them), their outer corners cut off,
    its edges rounded; on its upper part three panels (between the seams), each standing PANEL_H proud, its edges
    rounded so that its left edge catches the light."""
    c0, c1 = CAP_SIDES
    s0, s1 = SLOT_COLS
    top = []
    for cx, a0 in ((c1 - CORNER_R, 0.0), (c0 + CORNER_R, 90.0)):
        for i in range(7):
            a = math.radians(a0 + 90.0 * i / 6)
            top.append((cx + CORNER_R * math.cos(a), CAP_TOP + CORNER_R - CORNER_R * math.sin(a)))
    l0, l1 = LEG_SIDES
    pts = top + [(c0, STEP_ROW), (l0, STEP_ROW), (l0, LEG_CUT), (LEG_TIP, LEG_END), (s0, LEG_END), (s0, SLOT_TOP),
                 (s1, SLOT_TOP), (s1, LEG_END), (2 * AXIS_P - LEG_TIP, LEG_END), (l1, LEG_CUT), (l1, STEP_ROW),
                 (c1, STEP_ROW)]
    body = mk.prism("capsule", plan(pts), SKIRT, HC - PANEL_H, m["steel"])
    finish(body, CAP_BEVEL, 3, 30)
    mk.paint(body, steel_pick(m))
    parts = [body]
    # The panels: bands between the seams, cut to the capsule's rounded top (its plan shrunk by PANEL_INSET).
    inner = [(c, r) for c, r in top]
    for i, (a, b) in enumerate(PANELS):
        panel = mk.box(f"panel{i}", X(a), X(b), Y(PANEL_ROWS[1]), Y(PANEL_ROWS[0]), HC - PANEL_H - 0.6, HC,
                       m["steel_top"])
        clip = mk.prism(f"panel_clip{i}", plan(inner + [(c0, STEP_ROW + 2.0), (c1, STEP_ROW + 2.0)]), -5.0, 20.0)
        for v in clip.data.vertices:          # shrunk towards the capsule's middle by PANEL_INSET
            d = Vector((v.co.x - X(AXIS_P), v.co.y - Y(15.0)))
            if d.length > 1e-6:
                v.co.x -= PANEL_INSET * d.x / d.length
                v.co.y -= PANEL_INSET * d.y / d.length
        clip.data.update()
        mk.boolean(panel, clip, "INTERSECT")
        finish(panel, PANEL_BEVEL, 2, 30)
        mk.paint(panel, steel_pick(m))
        parts.append(panel)
    return parts


def pyramid(m):
    """The pyramid: its base (the point, the base corners, the front point) on the capsule, its ridge rising from the
    point to the top over the front point; its edges rounded a little."""
    a, l_, f = (P(*PYR_POINT), P(*PYR_LEFT), P(*PYR_FRONT))
    r_ = P(2 * AXIS_P - PYR_LEFT[0], PYR_LEFT[1])
    t = Vector((*P(PYR_TOP[0], PYR_TOP[1]), PYR_TOP[2]))
    bm = bmesh.new()
    va, vl, vf, vr = (bm.verts.new((p[0], p[1], PYR_BASE)) for p in (a, l_, f, r_))
    vt = bm.verts.new(t)
    for face in ((va, vl, vt), (vl, vf, vt), (vf, vr, vt), (vr, va, vt), (va, vr, vf, vl)):
        bm.faces.new(face)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("pyramid")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("pyramid", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(m["gold"])
    mk.bevel(obj, 0.28, 2, 20)
    mk.shade(obj, 30)

    axis = X(AXIS_P)

    def pick(c, n):
        if n.z < -0.5:
            return m["gold_dark"]
        left = c.x < axis
        if n.y < -0.5 and n.z < 0.6:                      # the narrow faces along its lower edges
            return m["gold_hi"] if left else m["gold_shade"]
        if n.z > 0.8:                                     # its two big faces: lit at the left, dark at the right
            return m["gold_lit"] if left else m["gold_dark"]
        return gold_pick(m)(c, n)                         # the rounded edges
    mk.paint(obj, pick)
    rod = gold_bands(mk.smooth_tube("rod", [(X(c), Y(r), z, ROD_R) for c, r, z in ROD], m["gold"], 14), m)
    collar = ring_obj("rod_collar", P(AXIS_P, 28.9), (1.05, 0.55), HC + 1.0, 0.45, m["gold_shade"], 16)
    k.smooth(collar, 60)
    return [obj, rod, collar]


def horns(m):
    parts = []
    for i, path in enumerate(HORNS):
        for side in (-1, 1):
            shift = HORN_SHIFT[0 if side < 0 else 1]
            pts = [(X(c if side < 0 else 2 * AXIS_P - c), Y(r + shift), z, rad) for c, r, z, rad in path]
            horn = mk.smooth_tube(f"horn{i}{side}", pts, m["gold"], 12)
            parts.append(gold_bands(horn, m))
    return parts


def pyramid_whole(m):
    parts = capsule(m) + pyramid(m) + horns(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


# --- Build ----------------------------------------------------------------------------------------------------------

def own_mask(text, r0=0, c0=0, rows=56, cols=48):
    lines = text.strip("\n").split("\n")
    return [[ch == "#" for ch in line[c0:c0 + cols]] for line in lines[r0:r0 + rows]]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprites in MACHINES.items():
        wanted = [f"{name}_{s}" for s, _, _ in QUARTERS]
        if only and name not in only and not any(w in only for w in wanted):
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        whole = domes_whole(m) if name == "gold_domes" else pyramid_whole(m)
        triangulate(whole)
        own = OWN_DOMES if name == "gold_domes" else OWN_PYRAMID
        print("whole %s: %d triangles, %d objects" % (name, mk.triangles(whole), len(whole)))
        if "check" in options:
            mk.compare("whole %s (2 %d %d above %d %d)" % ((name,) + sprites), mk.coverage(whole, 48, 56),
                       own_mask(own))
        if "preview" in options:
            mk.preview(options["preview"] + name + "_whole", whole, size=(48, 56), scale=8, distance=1.8)
        for (suffix, box, (c0, r0)), sprite in zip(QUARTERS, sprites):
            model = f"{name}_{suffix}"
            if only and model not in only and name not in only:
                continue
            parts = [p for p in (cut(src, box, m["steel_dark"]) for src in whole) if p is not None]
            mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0.0)))
            triangulate(parts)
            piece = join(parts, model)
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if "check" in options:
                mk.compare("%s (2 %d)" % (model, sprite), mk.coverage([piece], 24, 28), own_mask(own, r0, c0, 28, 24))
            mk.report(model, [piece], os.path.join(out, model + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + model, [piece])
            bpy.data.objects.remove(piece)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
