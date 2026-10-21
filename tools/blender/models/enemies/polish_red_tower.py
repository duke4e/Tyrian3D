"""DELI's and New Deli's tall red tower (sheet C sprites 77 above 115 above 17 above 55, 2x2 each: one 24 x 112 picture;
enemies 240 (the head), 239 (the vents), 238 (the shaft) and 237 (the base) of episodes 1 and 3, ground layer; episode
6's VAULT puts the base, 237, on its own), polished (2026-10-21; it replaces wave3_x_tower.py, a turned body leaning 16
degrees over the floor, painted by the sprite's shading, on a carpet of the map's floor tiles, its vents glowing at
emission 1.3-1.8). models.cfg: model red_tower_head / red_tower_vents / red_tower_shaft / red_tower_base ... origin
(unchanged) and the new model red_tower_head_79, _81, _83, _85, _87, _89 ... origin; sprite c 77 red_tower_head yaw=0
height=-4 and the same for 115, 17 and 55 (height=-4: the base stands on the floor; without it the tower floats 4
pixels over it); frame c 79 red_tower_head_79, ..., frame c 89 red_tower_head_89. Its damaged look (C 91 above 129
above 93 above 131) is polish_red_tower_dmg.py's, built from this script's parts and cut the same way.

Where the levels put it: DELI (1:19) and New Deli (3:23) place every tower with four ground events (6) at one time and
one link: 237 at (x, y), 238 at d5 -28, 239 at -56, 240 at -84, all at one x (x 114 to 210, t2456 to t4108), so the
sprites stack as the sheet's picture; the game lifts the four pieces together (render_gpu.c compute_object_lifts: the
terrain under their middle). VAULT (episode 6, the episode-1 enemy 237, link 0) shows the base alone. When any piece
of a linked tower is destroyed, all four switch to their damaged sprites at once (dlevel -1). No sprite of any sheet is
these mirrored, turned or in other ramps; no other enemy (launched ones included) shows C 17, 55, 77-89 or 115-127.

The frames: the head (240) fires weapon 143 every 4 ticks and plays its 13 frames each time it fires (animate 2: 77 79
81 83 85 87 89 87 85 83 81 79 77, one a tick), so in the game it pumps nearly all the time: 79, 81 and 83 lower the
dome and the skirt 3, 5 and 6 rows (the cup under them hidden), the gun port glowing up red (79 a dim spark, 81 a red
disc, 83 bright, 85 brightest, 87 dimmer, 89 dark again); 85, 87 and 89 part the skirt's two halves 1, 2 and 3
pixels each way, its front seam opening onto the dark inside. Frame models: the head's assembly lowered and opened,
the port's lens glowing (0x70 0.3, 0x72 0.4, 0x73 0.45, 0x76 0.55). The vents (239) have frames of the same kind
(117-127 would slide the crown and the cup down over the shoulders, light the vents in ramp 7 and stretch the upper
lamp) but it neither fires nor launches and no event animates its links (event 24 only targets others): the game
never shows them, so they get no frame models; the vents keep 115's dark red, with a faint ember (0x45, 0.16).

C 55's ramp-6 pixels and the black lines among them (its rows 14-27, the whole's 98-111) are DELI's floor tiles: the
map's, left out (the silhouettes are checked against the tower's own pixels, the whole's rows 0-97).

As the sprites draw it (columns and rows of the 24 x 112 picture, symmetric about its middle): the head (rows 0-21): a
grey dome (a ball of radius 9 about row 9) with a dark gun port near its top (columns 9-14 of rows 3-6), a small red
lamp over it (row 1) and a red strip under it (columns 11-12 of rows 7-10), sitting in a red skirt (rows 12-21, its
bottom rounding in) with a dark seam down its front (column 11), the dome showing down to row 14 over the skirt's
front; a dark neck (row 22) and a grey finned cup (rows 23-27) on the crown (rows 28-38): a ring, its rounded top lit
(rows 28-29), two dark red vents in its front (columns 6-8 and 14-17 of rows 29-34) with a grey bar between them
(columns 10-12), a lit rim under them (row 36), its foot curving in to a dark neck (row 39); the upper bulb (rows
40-54): a domed top with two red shoulder pads (columns 4-8 and 15-19 of rows 41-44) and a grey bar down its front
between them (columns 10-12), a crisp ledge (row 47), a barrel and a taper with a red lamp on its front (columns 10-13
of rows 51-53), a dark joint (row 54); the shaft (rows 55-64, radius 7), three rivets down its right (column 17); the
lower bulb (rows 65-77): the upper one's lower half (its ledge at row 70, its lamp rows 74-76, its joint row 77) under
a plain top; the base (rows 78-97): a domed top, a lit ledge, a red door wrapping round its left (columns 4-10 of rows
86-91, its top edge falling to the right), a grey hatch (columns 11-15 of rows 88-93), a lit rib down its right
(column 19), a foot rim (rows 92-93) and its bottom rounding into the floor.

The layout (round 24's lesson): the sprites draw the tower standing up the screen from its foot. It is built upright
about its axis (x right, y back: its front, which the game's camera sees, towards -y; z up the axis) and leaned back
up the screen 70 degrees from upright about its foot (FOOT: where the axis meets the floor under the picture's row
97.5), so that the camera (20 degrees from straight down, from the bottom of the screen) sees it face on from the
side, as the sprites draw it, and every part where its sprite draws it, where the game hits it: a point h up the axis
shows h / cos 20 rows up the picture from the foot, whatever its depth, so the picture's row r is the height H(r) =
(97.5 - r) cos 20 (the parts 6 percent shorter along the axis than the sprite's rows, as wide as its columns). Its top
is 38 pixels over the floor (the old tower's 35 with the 4 it floated), under background 2 and the sky layer even on
DELI's raised floor. Its back half near the foot, under the floor, is cut away (FLOOR_CUT, closed). The camera's planes
of sight through the sprites' edges are square to the leaned axis, so the pieces are cut there across the bodies (rows
56 and 84, where the shaft and the base's body are round: the cut faces closed in the inside's dark, the base's top in
a lid's grey, as VAULT shows it alone) and part by part at row 28 (the head's assembly above, the crown below). Each
piece is moved so that its sprite's centre is its origin; each holds what its sprite draws, below its origin (the
head's parts lie from 3 pixels above its origin to 25 below it, 16 to 38 pixels up).

The head (dome, port, lamp, strip, skirt, neck and cup) is one assembly, which the frame models lower along the axis
and open: the skirt is two halves (split at the front seam and the back, three panels each, a lit rim along their
tops) parting sideways; their top edge dips in a V at the front (and the back) to row 15, so the camera sees the
dome's foot over it, as the sprite draws it; their lip (6.55 inside) goes down over the cup (6.4 with its fins), and
the cup slides into the crown's opening (6.65) as the head comes down 6 rows (5.6 pixels along the axis): lowered, the
skirt's lip sits on the crown's rim, the dark neck in the gap between the parted halves.

Parts: bodies turned through profiles of the sprites' half-widths (DOME_*, SKIRT, CUP, CROWN, UPPER, LOWER, BASE, in
the picture's rows), a ring vertex on the front, painted in bands of rows (the ledges and the crown's top lit, the
tapers a shade darker, the joints dark); plates lying on them (patch(): the skirt's panels and rims, the pads, the bars,
the lamps' bezels and lenses, the door, the hatch and its frame, the rib, the cup's fins, the louvres: a grid on the
surface, its outer face proud of it, side walls round it); the gun port bored into the dome (an exact boolean) with a
bezel ring and a lens deep in it; the vents cut into the crown (exact booleans with superellipse sector cutters, their
back plates the ember), three louvres in each; beads round the crown's foot and the shaft; rivets. Greys (metallic 0.5,
roughness 0.3): the bodies 0x09, the dome 0x0a, lit bands and bars 0x0a, the tapers 0x08, the hatch 0x08, the bezel
0x05, the necks and the inside 0x03, rivets 0x0c, seams and the bore 0x01; reds (0.3 / 0.38): the skirt and the pads
0x47, their rims and the strip 0x49, the door 0x46 (lit 0x47, its foot 0x43), the louvres 0x47 / 0x46 / 0x43, insides
0x42; glowing: the lamps 0x4b 0.3, the vents' ember 0x45 0.16, the port in the frames (above).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); the whole's
origin is the middle of the picture (between 115 and 17): column c is x = c - 12 at its left edge, row r is y = 56 - r
at its top edge; the pieces' centres: 77 (0, 42), 115 (0, 14), 17 (0, -14), 55 (0, -42).

Replaces wave3_x_tower.py: delete it (only the tower is left in it since round 18: TOWER_ORIGIN, LEAN, FOOT, AXIS,
ty(), t_of_row(), on_axis(), tower_mats(), TOWER_PROFILE, HEAD_PROFILE, DOME_ROW/DOME_R/DOME_L, tower_whole(),
_frame_matrix(), x.whole("tower", ...), TOWER_PIECES, tower_piece() and its model loop); only wave3_ao_deli.py imports
it (kit.quiet_import("wave3_x_tower")), and it goes too (polish_red_tower_dmg.py replaces it). And wave3_x_art.py's
TOWER and TOWER_UP (only those two scripts read TOWER, nothing reads TOWER_UP); its BUNKER stays (wave3_x.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's, each piece's and
each head frame's silhouette as the game's camera sees it against enemy_C.png, the floor left out), --preview
<prefix> (the whole's and each model's top and three-quarter views), --only <name,...>, --whole <file.glb> (the leaned
uncut tower), --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (drop_unused, join)

# --- The layout ---------------------------------------------------------------------------------------------------
# The game's camera: CAMERA from straight down, from the bottom of the screen. A point at height z shows where the
# floor point T20 * z further up the screen is (the sprites' place for it).
CAMERA = math.radians(20.0)
C20, S20, T20 = math.cos(CAMERA), math.sin(CAMERA), math.tan(CAMERA)
VIEW = Vector((0.0, S20, -C20))               # the camera's line of sight (world)
# The tower is built upright (x right, y back: its front, which the camera sees, towards -y; z up its axis) and leaned
# back up the screen LEAN from upright about its foot, the point where its axis meets the floor (z = 0) under the
# picture's FOOT_ROW. Leaned 70 degrees, the camera sees it face on from the side, and a point h up the axis shows h /
# cos(20) rows up the picture from FOOT_ROW, whatever its depth: the picture's row r is the height H(r).
LEAN = math.radians(70.0)
FOOT_ROW = 97.5
FOOT = Vector((0.0, 56.0 - FOOT_ROW, 0.0))
TO_WORLD = Matrix.Translation(FOOT) @ Matrix.Rotation(-LEAN, 4, "X")
LIGHT = (TO_WORLD.to_3x3().inverted() @ Vector((-0.6, 0.6, 1.0))).normalized()   # towards the sun, upright
FLOOR_CUT = -0.8                              # nothing lower than this (the floor hides it)


def H(row):
    """The height up the upright axis that the camera shows at the picture's row (a pixel edge)."""
    return (FOOT_ROW - row) * C20


def ROW(h):
    return FOOT_ROW - h / C20


# The pieces: model, sprite, the picture's rows they cover, their sprite's centre (y in the whole's coordinates).
PIECES = [("red_tower_head", 77, 0.0, 28.0, 42.0), ("red_tower_vents", 115, 28.0, 56.0, 14.0),
          ("red_tower_shaft", 17, 56.0, 84.0, -14.0), ("red_tower_base", 55, 84.0, 112.0, -42.0)]
# The head's frames (it plays them each time it fires): model, sprite, rows the head is lowered, pixels each half of
# the skirt is parted, the port's glow (0 dark .. 4 brightest).
HEAD_FRAMES = [("red_tower_head", 77, 0, 0, 0), ("red_tower_head_79", 79, 3, 0, 1), ("red_tower_head_81", 81, 5, 0, 2),
               ("red_tower_head_83", 83, 6, 0, 3), ("red_tower_head_85", 85, 6, 1, 4),
               ("red_tower_head_87", 87, 6, 2, 2), ("red_tower_head_89", 89, 6, 3, 0)]


# --- Materials ------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.32, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = {"seam": mat("rtow_seam", 0x01, 0.3, 0.6)}
    for s in (3, 5, 7, 8, 9, 10, 12):
        m["g%x" % s] = mat("rtow_grey%x" % s, s, 0.5, 0.3)
    for s in (2, 3, 6, 7, 9):
        m["r%x" % s] = mat("rtow_red%x" % s, 0x40 | s, 0.3, 0.38)
    m["lamp"] = mat("rtow_lamp", 0x4b, roughness=0.25, glow=0.3)
    m["vent"] = mat("rtow_vent", 0x45, roughness=0.45, glow=0.16)
    m["p70"] = mat("rtow_port70", 0x70, roughness=0.3, glow=0.3)
    m["p72"] = mat("rtow_port72", 0x72, roughness=0.3, glow=0.4)
    m["p73"] = mat("rtow_port73", 0x73, roughness=0.25, glow=0.45)
    m["p76"] = mat("rtow_port76", 0x76, roughness=0.2, glow=0.55)
    return m


def paint_by(obj, pick):
    """Gives faces materials: pick(centre, normal, material name) returns a material or None (keep)."""
    for poly in obj.data.polygons:
        mat = pick(poly.center, poly.normal, obj.data.materials[poly.material_index].name)
        if mat is not None:
            poly.material_index = mk.slot_of(obj, mat)
    return obj


def bands(obj, spec):
    """Paints a turned body in bands of the picture's rows: spec [(from row, to row, material)] (the first that holds
    a face's centre wins)."""
    def pick(c, n, _):
        row = ROW(c.z)
        for r0, r1, mat in spec:
            if r0 <= row < r1:
                return mat
        return None
    return paint_by(obj, pick)


# --- Profiles (the picture's row, radius) ---------------------------------------------------------------------------

def sphere_rows(row_c, radius, a0, a1, step=6.0):
    """A sphere of the picture's radius about row row_c, from a0 to a1 degrees from its top (rows, radii)."""
    out, a = [], a0
    while a < a1 - 1e-6:
        out.append((row_c - radius * math.cos(math.radians(a)), radius * math.sin(math.radians(a))))
        a = min(a + step, a1)
    out.append((row_c - radius * math.cos(math.radians(a1)), radius * math.sin(math.radians(a1))))
    return out


DOME_ROW, DOME_R = 9.0, 9.0                   # the dome: a ball of the picture's radius 9 about row 9
DOME_FOOT = 15.0                              # its underside (inside the skirt)
SKIRT = [(10.8, 8.62), (11.5, 8.9), (12.1, 9.0), (18.2, 9.0), (18.9, 8.75), (19.6, 8.3), (20.3, 7.75), (20.9, 7.35),
         (21.4, 7.12), (21.8, 7.0)]
SKIRT_T = 0.45                                # its thickness
SKIRT_SPLIT = math.asin(-0.45 / 9.0)          # the front seam (column 11), the halves split there and at the back
SKIRT_GAP = 0.22                              # half the seams' width
SKIRT_PANELS = (52.0, 128.0)                  # the panel lines on each half (degrees from the front)
NECK = (14.8, 23.4, 4.0)                      # the head's neck: rows, radius
CUP = [(23.0, 4.1), (23.4, 4.9), (24.0, 5.5), (24.8, 5.9), (25.6, 6.08), (26.4, 6.12), (29.2, 6.12)]
CUP_FINS = (14, 23.5, 26.3, 0.28, 0.5)        # count, rows, how far out, width
CROWN = [(35.6, 6.65), (28.15, 6.65), (27.98, 6.85), (27.95, 7.25), (28.05, 7.7), (28.4, 8.25), (28.9, 8.7),
         (29.5, 8.95), (30.0, 9.02), (35.0, 9.02), (35.6, 8.95), (36.2, 8.65), (36.8, 8.05), (37.3, 7.4), (37.8, 6.75),
         (38.3, 6.15), (38.7, 5.3), (38.95, 4.3)]
CROWN_OPEN = 6.65                             # the crown's top opening (the head's cup slides into it)
CROWN_BEAD = (35.55, 36.15, 0.22)             # the lit bead round the crown's foot: rows, how proud
VENTS = [(-45.0, -19.0), (13.0, 45.0)]        # the vents' sides (degrees from the front)
VENT_ROWS = (29.5, 34.5)
VENT_DEPTH = 1.3
LOUVRES = (30.75, 32.0, 33.25)
PILLAR = (-2.1, 1.0, 29.35, 34.9)             # the bar between them: x, rows
NECK2 = (38.7, 40.3, 4.0)
UPPER = [(39.9, 4.15), (40.3, 4.9), (40.8, 5.9), (41.5, 7.0), (42.3, 7.95), (43.2, 8.6), (44.2, 8.95), (45.2, 9.1),
         (46.4, 9.22), (46.95, 9.32), (47.15, 9.32), (47.22, 9.0), (50.0, 9.0), (50.6, 8.75), (51.2, 8.2), (51.8, 7.6),
         (52.6, 7.2), (53.6, 7.05), (54.05, 6.95), (54.25, 6.65), (54.6, 6.65)]
UPPER_BANDS = ((46.35, 47.18, "ga"), (50.65, 54.1, "g8"), (54.1, 55.0, "seam"))
PADS = (22.0, 158.0, 40.55, 45.0)             # the red shoulder pads: degrees from the front, rows
SPINE = (-2.1, 1.1, 39.85, 45.35)             # the bar down the upper bulb's front: x, rows
SHAFT_R = 7.0
SHAFT_RINGS = [(56.6, 57.0), (63.7, 64.1)]    # thin raised rings round the shaft: rows
RIVETS = [(5.5, 58.0), (5.5, 60.0), (5.5, 62.0)]
LOWER = [(64.6, 7.0), (65.1, 7.4), (65.6, 7.88), (66.5, 8.35), (67.4, 8.75), (68.4, 9.05), (69.4, 9.22),
         (69.95, 9.32), (70.15, 9.32), (70.22, 9.0), (73.0, 9.0), (73.6, 8.75), (74.2, 8.2), (74.8, 7.6), (75.6, 7.2),
         (76.6, 7.05), (77.0, 6.95), (77.15, 6.65), (77.75, 6.65)]
LOWER_BANDS = ((69.35, 70.18, "ga"), (73.65, 77.1, "g8"), (77.1, 78.0, "seam"))
BASE = [(77.6, 6.95), (78.3, 7.35), (78.9, 7.78), (79.6, 8.15), (80.4, 8.52), (81.2, 8.85), (81.9, 9.1), (82.45, 9.22),
        (82.6, 9.22), (82.67, 9.02), (92.1, 9.02), (92.3, 9.22), (93.4, 9.22), (93.8, 8.97), (94.5, 8.55), (95.3, 8.0),
        (96.1, 7.35), (96.8, 6.6), (97.4, 5.6), (97.9, 4.2), (98.2, 2.6), (98.35, 1.0)]
BASE_BANDS = ((81.85, 82.63, "ga"), (92.05, 93.45, "ga"), (93.45, 99.0, "g8"))
LAMPS = [(-2.05, 2.05, 50.95, 53.95), (-2.05, 2.05, 73.95, 76.95)]   # x, rows
DOOR = [(-80.0, 85.2), (-12.0, 88.4), (-17.0, 92.0), (-80.0, 90.6)]  # the red door's corners (degrees, rows)
HATCH = (-1.8, 24.5, 88.0, 91.85)             # the grey hatch: degrees, rows
RIB = (47.0, 55.0, 84.3, 91.9)                # the lit rib down the base's right: degrees, rows


def radius_on(prof, row):
    """A profile's radius at a row (linear between its points)."""
    pts = sorted(prof)
    if row <= pts[0][0]:
        return pts[0][1]
    for (r0, a), (r1, b) in zip(pts, pts[1:]):
        if r0 <= row <= r1:
            return a + (b - a) * (row - r0) / max(r1 - r0, 1e-9)
    return pts[-1][1]


def dome_radius(row):
    dz = DOME_ROW - row
    return math.sqrt(max(0.0, DOME_R * DOME_R - dz * dz))


# --- Builders -------------------------------------------------------------------------------------------------------

def turn(name, prof, mat, segments=40, caps=(True, True), smooth=30.0):
    """A body turned about the upright axis through prof [(row, radius)] in order along its outline (radius 0 at an
    end: a pole); a vertex of every ring on the front."""
    pts = list(prof)
    start = end = None
    if pts[0][1] <= 1e-6:
        start = Vector((0.0, 0.0, H(pts[0][0])))
        pts = pts[1:]
    if pts[-1][1] <= 1e-6:
        end = Vector((0.0, 0.0, H(pts[-1][0])))
        pts = pts[:-1]
    rings = []
    for row, r in pts:
        h = H(row)
        rings.append([Vector((r * math.sin(2 * math.pi * j / segments), -r * math.cos(2 * math.pi * j / segments), h))
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, cap_start=caps[0], cap_end=caps[1],
                 start_point=start if start is not None else (0.0, 0.0, H(pts[0][0])),
                 end_point=end if end is not None else (0.0, 0.0, H(pts[-1][0])))
    if smooth:
        k.smooth(obj, smooth)
    return obj


def on_turned(prof_radius, az, row, out=0.0):
    """The point of a turned surface (its radius a function of the row) at an angle from the front and a row."""
    r = prof_radius(row) + out
    return Vector((r * math.sin(az), -r * math.cos(az), H(row)))


def on_front(prof_radius, x, row, out=0.0):
    """The point of a turned surface's front at the picture's x and row."""
    r = prof_radius(row) + out
    return Vector((x, -math.sqrt(max(0.0, r * r - x * x)), H(row)))


def patch(name, surf, nu, nv, lift, depth, mats, paint_outer=None):
    """A plate lying on a surface: surf(u, v) gives the surface's point for u, v in 0..1 (nu x nv cells); its outer
    face lift above the surface, its inner face depth below it, side walls round its border. mats: (outer, inner,
    side); paint_outer(centre, normal) may repaint the outer faces. Normals point away from the tower's axis."""
    eps = 1e-3
    grid_o, grid_i = [], []
    for i in range(nu + 1):
        for j in range(nv + 1):
            u, v = i / nu, j / nv
            p = surf(u, v)
            du = surf(min(u + eps, 1.0), v) - surf(max(u - eps, 0.0), v)
            dv = surf(u, min(v + eps, 1.0)) - surf(u, max(v - eps, 0.0))
            n = du.cross(dv)
            if n.length < 1e-9:
                n = Vector((p.x, p.y, 0.0))
            n.normalize()
            if n.dot(Vector((p.x, p.y, 0.0))) < 0:
                n = -n
            grid_o.append(p + n * lift)
            grid_i.append(p - n * depth)
    verts = grid_o + grid_i
    off = len(grid_o)

    def idx(i, j):
        return i * (nv + 1) + j
    faces, roles = [], []
    for i in range(nu):
        for j in range(nv):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            faces.append((a, b, c, d))
            roles.append(0)
            faces.append((d + off, c + off, b + off, a + off))
            roles.append(1)
    border = []
    for i in range(nu):
        border.append((idx(i, 0), idx(i + 1, 0)))
    for j in range(nv):
        border.append((idx(nu, j), idx(nu, j + 1)))
    for i in range(nu, 0, -1):
        border.append((idx(i, nv), idx(i - 1, nv)))
    for j in range(nv, 0, -1):
        border.append((idx(0, j), idx(0, j - 1)))
    for a, b in border:
        faces.append((b, a, a + off, b + off))
        roles.append(2)
    obj = k.mesh_object(name, verts, faces)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, role in zip(obj.data.polygons, roles):
        poly.material_index = role
    k.recalc_normals(obj)
    if paint_outer is not None:
        for poly, role in zip(obj.data.polygons, roles):
            if role == 0:
                mat = paint_outer(poly.center, poly.normal)
                if mat is not None:
                    poly.material_index = mk.slot_of(obj, mat)
    return obj


def sector_cutter(name, az0, az1, row0, row1, r_in, r_out, mat, power=4.0, rings=4, segments=28):
    """A closed solid for cutting a rounded window into a turned wall: its outline a superellipse in (angle, row),
    reaching from r_in out past r_out."""
    ac, ah = (az0 + az1) / 2, (az1 - az0) / 2
    rc, rh = (row0 + row1) / 2, (row1 - row0) / 2
    outline = [mk.superellipse_point(2 * math.pi * j / segments, power) for j in range(segments)]

    def pt(u, v, r):
        az, row = ac + u * ah, rc - v * rh
        return Vector((r * math.sin(az), -r * math.cos(az), H(row)))
    verts, faces = [], []
    for r in (r_in, r_out):
        base = len(verts)
        verts.append(pt(0.0, 0.0, r))
        for s in range(1, rings + 1):
            f = s / rings
            for (u, v) in outline:
                verts.append(pt(u * f, v * f, r))
        for j in range(segments):
            faces.append((base, base + 1 + j, base + 1 + (j + 1) % segments))
        for s in range(rings - 1):
            a0, a1 = base + 1 + s * segments, base + 1 + (s + 1) * segments
            for j in range(segments):
                jn = (j + 1) % segments
                faces.append((a0 + j, a1 + j, a1 + jn, a0 + jn))
    inner_edge = 1 + (rings - 1) * segments
    outer_base = 1 + rings * segments
    outer_edge = outer_base + 1 + (rings - 1) * segments
    for j in range(segments):
        jn = (j + 1) % segments
        faces.append((inner_edge + j, inner_edge + jn, outer_edge + jn, outer_edge + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def bead(name, prof_radius, row0, row1, out, mat, segments=40):
    """A rounded bead round a turned body between two rows, proud of it by out at its middle."""
    prof = []
    for i in range(7):
        t = i / 6
        row = row0 + (row1 - row0) * t
        prof.append((row, prof_radius(row) - 0.05 + (out + 0.05) * math.sin(math.pi * t)))
    return turn(name, [(row0, prof[0][1] - 0.3)] + prof + [(row1, prof[-1][1] - 0.3)], mat, segments, smooth=50.0)


def place(obj, matrix):
    obj.data.transform(matrix)
    obj.data.update()
    return obj


def frame_on(axis):
    """Two unit vectors square to an axis."""
    ref = Vector((1.0, 0.0, 0.0)) if abs(axis.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    u = axis.cross(ref).normalized()
    return u, axis.cross(u).normalized()


def lathe_on_axis(name, prof, centre, axis, mat, segments=24, smooth=40.0):
    """A part turned about an arbitrary axis: prof [(t along the axis, radius)] (radius 0 at an end: flat to the
    axis there)."""
    u, w = frame_on(axis)
    rings = []
    pts = [p for p in prof if p[1] > 1e-6]
    for t, r in pts:
        c = centre + axis * t
        rings.append([c + (u * math.cos(2 * math.pi * j / segments) + w * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=centre + axis * prof[0][0], end_point=centre + axis * prof[-1][0])
    if smooth:
        k.smooth(obj, smooth)
    return obj


def ring_on_axis(name, loop, centre, axis, mat, segments=24, smooth=45.0):
    """A ring turned about an arbitrary axis from a closed outline loop [(t along the axis, radius)] (a bezel)."""
    u, w = frame_on(axis)
    verts, faces = [], []
    n = len(loop)
    for t, r in loop:
        c = centre + axis * t
        verts += [c + (u * math.cos(2 * math.pi * j / segments) + w * math.sin(2 * math.pi * j / segments)) * r
                  for j in range(segments)]
    for i in range(n):
        a, b = i * segments, ((i + 1) % n) * segments
        for j in range(segments):
            jn = (j + 1) % segments
            faces.append((a + j, a + jn, b + jn, b + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    if smooth:
        k.smooth(obj, smooth)
    return obj


# --- The head (dome, skirt, neck, cup): one assembly, lowered and opened by its frames --------------------------------

def port_frame():
    """The gun port: its centre on the dome, its axis (outwards), from the picture (row 4.6, x 0)."""
    e = math.asin((DOME_ROW - 4.6) / DOME_R)
    centre = Vector((0.0, -DOME_R * math.cos(e), H(DOME_ROW) + DOME_R * math.sin(e) * C20))
    a = math.radians(40.0)
    axis = Vector((0.0, -math.cos(a), math.sin(a)))
    return centre, axis


def dome(m):
    """The dome: a ball (the picture's radius 9 about row 9, squashed along the axis by cos 20 as the camera's rows)
    from its top down into the skirt (row 15), closed underneath; the gun port bored into its front, a bezel round it,
    the lens deep in it."""
    foot = math.degrees(math.acos((DOME_ROW - DOME_FOOT) / DOME_R))
    prof = [(DOME_ROW - DOME_R, 0.0)] + sphere_rows(DOME_ROW, DOME_R, 4.0, foot, 4.0)
    prof += [(DOME_FOOT + 0.05, 4.2), (DOME_FOOT + 0.05, 0.0)]
    body = turn("dome", prof, m["ga"], segments=48, smooth=0)
    centre, axis = port_frame()
    cutter = mk.tube("port_cut", [centre + axis * 3.0, centre - axis * 1.7], 2.55, m["seam"], segments=28)
    mk.boolean(body, cutter, "DIFFERENCE")
    mk.cleanup(body)
    k.smooth(body, 40)
    bezel = ring_on_axis("port_bezel", [(-0.9, 3.2), (0.0, 3.2), (0.2, 3.05), (0.3, 2.8), (0.24, 2.6), (-0.9, 2.56)],
                         centre, axis, m["g5"], 32)
    mk.paint(bezel, lambda c, n: m["ga"] if n.dot(LIGHT) > 0.8 else m["seam"] if n.dot(axis) < -0.2 else None)
    lens = lathe_on_axis("port_lens", [(-1.5, 2.5), (-1.3, 2.5), (-1.3, 0.0)], centre, axis, m["seam"], 28, smooth=30)
    core = lathe_on_axis("port_core", [(-1.32, 1.3), (-1.18, 1.3), (-1.12, 1.0), (-1.12, 0.0)], centre, axis,
                         m["seam"], 24, smooth=30)
    return [body, bezel, lens, core]


def dome_point(x, row):
    """A point on the dome's front at the picture's x and row."""
    r = dome_radius(row)
    return Vector((x, -math.sqrt(max(0.0, r * r - x * x)), H(row)))


def stripe_and_lamp(m):
    """The red strip down the dome's front under the port (rows 7-10, columns 11-12) and the small red lamp in a dark
    collar near the dome's top (row 1)."""
    strip = patch("dome_stripe", lambda u, v: dome_point(-0.95 + 1.9 * u, 6.85 + 3.6 * v), 3, 6, 0.22, 0.5,
                  (m["r9"], m["r3"], m["r6"]))
    mk.bevel(strip, 0.12, 2, 30)
    k.smooth(strip, 40)
    e = math.radians(56.0)
    c = Vector((0.0, -DOME_R * math.cos(e), H(DOME_ROW) + DOME_R * math.sin(e) * C20))
    axis = Vector((0.0, -math.cos(e) * C20, math.sin(e))).normalized()
    collar = lathe_on_axis("apex_collar", [(-0.6, 1.45), (0.12, 1.45), (0.2, 1.2), (0.2, 0.0)], c, axis, m["g5"], 20)
    lamp = lathe_on_axis("apex_lamp", [(0.0, 1.05), (0.25, 1.0), (0.45, 0.7), (0.53, 0.0)], c, axis, m["lamp"], 20,
                         smooth=60)
    return [strip, collar, lamp]


def skirt_top(az):
    """The row of the skirt's top edge at an angle from the front: tucked under the dome's middle at the sides, dipping
    to row 15 at the front (and the back), where the dome shows down to its foot."""
    a = abs(math.atan2(math.sin(az), math.cos(az)))
    t = min(a, math.pi - a) / math.radians(75.0)
    f = (1.0 - t * t) ** 1.5 if t < 1.0 else 0.0
    return 11.0 + 4.0 * f


def skirt_radius(row):
    return radius_on(SKIRT, row)


def skirt_panels(m):
    """The skirt: two halves split at the front seam and the back, each of three panels (dark lines between) with a lit
    rim along their top, a shell SKIRT_T thick, red outside, dark red inside; returns (left parts, right parts)."""
    halves = ([], [])
    bottom = SKIRT[-1][0]
    for side in (0, 1):
        a_from = SKIRT_SPLIT + (math.pi if side == 0 else 0.0)
        cuts = [0.0] + [math.radians(p) for p in SKIRT_PANELS] + [math.pi]
        for i in range(3):
            g0 = SKIRT_GAP / 9.0 if i == 0 else 0.16 / 9.0
            g1 = SKIRT_GAP / 9.0 if i == 2 else 0.16 / 9.0
            a0, a1 = a_from + cuts[i] + g0, a_from + cuts[i + 1] - g1

            def surf(u, v, a0=a0, a1=a1):
                az = a0 + (a1 - a0) * u
                top = skirt_top(az)
                row = top + (bottom - top) * (v ** 0.85)
                return on_turned(skirt_radius, az, row)
            nu = max(4, int(round((a1 - a0) / math.radians(7.5))))
            obj = patch("skirt%d_%d" % (side, i), surf, nu, 10, 0.0, SKIRT_T, (m["r7"], m["r2"], m["seam"]))
            k.smooth(obj, 35)
            halves[side].append(obj)

            def rim_surf(u, v, a0=a0, a1=a1):
                az = a0 + (a1 - a0) * u
                return on_turned(skirt_radius, az, skirt_top(az) + 0.05 + 0.5 * v)
            rim = patch("skirt_rim%d_%d" % (side, i), rim_surf, nu, 1, 0.16, 0.1, (m["r9"], m["r3"], m["r3"]))
            k.smooth(rim, 35)
            halves[side].append(rim)
    return halves


def neck_and_cup(m):
    """The neck under the skirt (dark) and the cup it stands in: a flared collar with fins round it, sitting in the
    crown's top opening."""
    r0, r1, rad = NECK
    neck = turn("neck", [(r1, rad), (r0, rad)], m["g3"], 24, smooth=40)
    cup = turn("cup", list(reversed(CUP)), m["g9"], 40)
    parts = [neck, cup]
    count, f0, f1, out, width = CUP_FINS
    cup_r = lambda row: radius_on(CUP, row)  # noqa: E731
    for i in range(count):
        az = 2 * math.pi * (i + 0.5) / count
        half = width / 2 / 6.0

        def surf(u, v, az=az, half=half):
            return on_turned(cup_r, az - half + 2 * half * u, f0 + (f1 - f0) * v)
        fin = patch("cup_fin%d" % i, surf, 1, 4, out, 0.3, (m["ga"], m["g5"], m["g5"]))
        k.smooth(fin, 30)
        parts.append(fin)
    return parts


GLOWS = {0: ("seam", "seam"), 1: ("seam", "p70"), 2: ("p70", "p72"), 3: ("p72", "p76"), 4: ("p73", "p76")}


def head_assembly(m, lowered=0.0, parted=0.0, glow=0):
    """The head: dome, port, strip, lamp, skirt, neck and cup; lowered rows down the axis and the skirt's halves
    parted sideways (pixels each) as the frames draw them, the port's lens glowing (0..4)."""
    parts = dome(m)
    lens, core = parts[2], parts[3]
    rim_mat, core_mat = GLOWS[glow]
    mk.paint(lens, lambda c, n: m[rim_mat])
    mk.paint(core, lambda c, n: m[core_mat])
    parts += stripe_and_lamp(m)
    left, right = skirt_panels(m)
    parts += neck_and_cup(m)
    for obj in left:
        place(obj, Matrix.Translation((-parted, 0.0, 0.0)))
    for obj in right:
        place(obj, Matrix.Translation((parted, 0.0, 0.0)))
    parts += left + right
    if lowered:
        for obj in parts:
            place(obj, Matrix.Translation((0.0, 0.0, -lowered * C20)))
    return parts


# --- The crown with its vents -----------------------------------------------------------------------------------------

def crown(m):
    """The crown: a ring round the head's cup (its top a rounded lit rim, open in the middle), two vents cut into its
    front (louvres in them over a faint ember), the bar between them, a lit bead round its foot, which curves in to
    the neck."""
    body = turn("crown", CROWN, m["g9"], 44, smooth=0)
    for i, (a0, a1) in enumerate(VENTS):
        cutter = sector_cutter("vent_cut%d" % i, math.radians(a0), math.radians(a1), VENT_ROWS[0], VENT_ROWS[1],
                               9.02 - VENT_DEPTH, 10.5, m["vent"])
        mk.boolean(body, cutter, "DIFFERENCE")
    mk.cleanup(body)
    k.smooth(body, 32)
    vent_name = m["vent"].name

    def pick(c, n, name):
        radial = Vector((c.x, c.y, 0.0))
        if name == vent_name:
            if radial.length > 1e-6 and n.dot(radial.normalized()) > 0.75:
                return m["vent"]
            return m["r3"]
        if radial.length < CROWN_OPEN + 0.05:
            return m["g3"]                     # the opening's inside and floor
        if ROW(c.z) < 29.6:
            return m["ga"]                     # the rounded top rim
        return None
    paint_by(body, pick)
    parts = [body]
    crown_r = lambda row: 9.02  # noqa: E731
    for i, (a0, a1) in enumerate(VENTS):
        for j, row in enumerate(LOUVRES):
            def surf(u, v, a0=a0, a1=a1, row=row):
                az = math.radians(a0 + 1.4 + (a1 - a0 - 2.8) * u)
                return on_turned(crown_r, az, row - 0.3 + 0.6 * v, out=-VENT_DEPTH + 0.12)
            slat = patch("louvre%d_%d" % (i, j), surf, 8, 1, 0.6, 0.0, (m["r7"], m["r3"], m["r3"]),
                         paint_outer=lambda c, n: m["r7"] if n.z > 0.25 else m["r3"] if n.z < -0.25 else m["r6"])
            k.smooth(slat, 40)
            parts.append(slat)
    x0, x1, r0, r1 = PILLAR
    bar = patch("crown_bar", lambda u, v: on_front(crown_r, x0 + (x1 - x0) * u, r0 + (r1 - r0) * v), 4, 5, 0.32,
                0.4, (m["ga"], m["g5"], m["g8"]))
    mk.bevel(bar, 0.14, 2, 30)
    k.smooth(bar, 40)
    parts.append(bar)
    parts.append(bead("crown_bead", lambda row: radius_on(CROWN[9:], row), CROWN_BEAD[0], CROWN_BEAD[1],
                      CROWN_BEAD[2], m["ga"]))
    r0, r1, rad = NECK2
    parts.append(turn("neck2", [(r1, rad), (r0, rad)], m["g3"], 24, smooth=40))
    return parts


# --- The bulbs, the shaft and the base --------------------------------------------------------------------------------

def bulb(name, prof, spec, m):
    obj = turn(name, list(reversed(prof)), m["g9"], 40, smooth=28)
    bands(obj, [(a, b, m[key]) for a, b, key in spec])
    return obj


def lamp(name, box, prof, m):
    """A red lamp on a bulb's lower front: a dark bezel and the raised lens in it."""
    x0, x1, r0, r1 = box
    rad = lambda row: radius_on(prof, row)  # noqa: E731

    def surf_of(x0, x1, r0, r1):
        return lambda u, v: on_front(rad, x0 + (x1 - x0) * u, r0 + (r1 - r0) * v)
    bezel = patch(name + "_bezel", surf_of(x0 - 0.45, x1 + 0.45, r0 - 0.4, r1 + 0.3), 6, 4, 0.12, 0.4,
                  (m["seam"], m["seam"], m["seam"]))
    k.smooth(bezel, 30)
    lens = patch(name, surf_of(x0, x1, r0, r1), 6, 4, 0.55, 0.5, (m["lamp"], m["r3"], m["r6"]),
                 paint_outer=lambda c, n: m["lamp"] if n.y < -0.45 or n.dot(LIGHT) > 0.62 else m["r6"])
    mk.bevel(lens, 0.22, 2, 30)
    k.smooth(lens, 40)
    return [bezel, lens]


def upper_bulb(m):
    """The upper bulb: a domed top under the neck, a crisp ledge, a barrel, a taper to the shaft with a red lamp on it;
    two red pads on its shoulders and a grey bar down its front between them."""
    parts = [bulb("upper_bulb", UPPER, UPPER_BANDS, m)]
    rad = lambda row: radius_on(UPPER, row)  # noqa: E731
    a0, a1, r0, r1 = PADS
    for side in (-1, 1):
        def surf(u, v, side=side):
            az = side * math.radians(a0 + (a1 - a0) * u)
            return on_turned(rad, az, r0 + (r1 - r0) * v)
        pad = patch("pad%d" % side, surf, 12, 5, 0.38, 0.5, (m["r7"], m["r3"], m["r3"]),
                    paint_outer=lambda c, n: m["r9"] if n.dot(LIGHT) > 0.86 else None)
        mk.bevel(pad, 0.18, 2, 30)
        k.smooth(pad, 35)
        parts.append(pad)
    x0, x1, s0, s1 = SPINE
    spine = patch("spine", lambda u, v: on_front(rad, x0 + (x1 - x0) * u, s0 + (s1 - s0) * v), 4, 8, 0.42, 0.6,
                  (m["ga"], m["g5"], m["g8"]))
    mk.bevel(spine, 0.15, 2, 30)
    k.smooth(spine, 40)
    parts.append(spine)
    parts += lamp("lamp_upper", LAMPS[0], UPPER, m)
    return parts


def shaft(m, row0, row1, name):
    obj = turn(name, [(row1, SHAFT_R), (row0, SHAFT_R)], m["g9"], 40, smooth=40)
    paint_by(obj, lambda c, n, _: m["g3"] if abs(n.z) > 0.99 else None)     # its cut ends: the inside's dark
    return obj


def shaft_details(m):
    out = []
    for i, (r0, r1) in enumerate(SHAFT_RINGS):
        out.append(bead("shaft_ring%d" % i, lambda row: SHAFT_R, r0, r1, 0.2, m["ga"], 40))
    for i, (x, row) in enumerate(RIVETS):
        c = on_front(lambda r: SHAFT_R, x, row)
        n = Vector((c.x, c.y, 0.0)).normalized()
        r = lathe_on_axis("rivet%d" % i, [(-0.3, 0.48), (0.0, 0.48), (0.16, 0.36), (0.25, 0.0)], c, n, m["gc"], 12,
                          smooth=60)
        out.append(r)
    return out


def lower_bulb(m):
    return [bulb("lower_bulb", LOWER, LOWER_BANDS, m)] + lamp("lamp_lower", LAMPS[1], LOWER, m)


def base_body(m, row0, row1, name):
    prof = [p for p in BASE if row0 - 1e-6 <= p[0] <= row1 + 1e-6]
    if prof[0][0] > row0 + 1e-6:
        prof.insert(0, (row0, radius_on(BASE, row0)))
    if prof[-1][0] < row1 - 1e-6 and row1 < BASE[-1][0]:
        prof.append((row1, radius_on(BASE, row1)))
    if prof[-1][0] >= BASE[-1][0] - 1e-6:
        prof.append((BASE[-1][0] + 0.02, 0.0))
    obj = turn(name, list(reversed(prof)), m["g9"], 40, smooth=28)
    bands(obj, [(a, b, m[key]) for a, b, key in BASE_BANDS])
    # The cut at row 84: the inside's dark below the shaft's piece; a lid's grey on the base's (VAULT shows it alone).
    lid = m["g3"] if row0 < 84.0 - 1e-6 else m["g5"]
    paint_by(obj, lambda c, n, _: lid if abs(n.z) > 0.995 and abs(c.z - H(84.0)) < 0.05 else None)
    return obj


def base_details(m):
    rad = lambda row: radius_on(BASE, row)  # noqa: E731
    (a_tl, r_tl), (a_tr, r_tr), (a_br, r_br), (a_bl, r_bl) = DOOR

    def door_surf(u, v):
        top_a, top_r = a_tl + (a_tr - a_tl) * u, r_tl + (r_tr - r_tl) * u
        bot_a, bot_r = a_bl + (a_br - a_bl) * u, r_bl + (r_br - r_bl) * u
        return on_turned(rad, math.radians(top_a + (bot_a - top_a) * v), top_r + (bot_r - top_r) * v)
    door = patch("door", door_surf, 12, 6, 0.32, 0.5, (m["r6"], m["r2"], m["seam"]),
                 paint_outer=lambda c, n: m["r7"] if n.dot(LIGHT) > 0.7 else m["r3"] if n.z < -0.3 else None)
    mk.bevel(door, 0.14, 2, 30)
    k.smooth(door, 35)
    a0, a1, r0, r1 = HATCH

    def frame_surf(u, v):
        return on_turned(rad, math.radians(a0 - 2.4 + (a1 - a0 + 4.8) * u), r0 - 0.38 + (r1 - r0 + 0.66) * v)
    frame = patch("hatch_frame", frame_surf, 6, 4, 0.05, 0.4, (m["seam"], m["seam"], m["seam"]))

    def hatch_surf(u, v):
        return on_turned(rad, math.radians(a0 + (a1 - a0) * u), r0 + (r1 - r0) * v)
    hatch = patch("hatch", hatch_surf, 6, 4, 0.22, 0.4, (m["g8"], m["g3"], m["ga"]))
    mk.bevel(hatch, 0.1, 2, 30)
    k.smooth(hatch, 35)
    b0, b1, s0, s1 = RIB
    rib = patch("base_rib", lambda u, v: on_turned(rad, math.radians(b0 + (b1 - b0) * u), s0 + (s1 - s0) * v), 3, 5,
                0.3, 0.4, (m["ga"], m["g5"], m["g8"]))
    mk.bevel(rib, 0.12, 2, 30)
    k.smooth(rib, 35)
    return [door, frame, hatch, rib]


# --- The whole --------------------------------------------------------------------------------------------------------

def lean(objects):
    for obj in objects:
        mk.apply(obj)
        place(obj, TO_WORLD)
    return objects


def floor_cut(objects, z=FLOOR_CUT, cap=None):
    """Everything below z cut away, the cut closed (cap material) in case the floor sinks under it."""
    for obj in objects:
        if min(v.co.z for v in obj.data.vertices) >= z:
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                                     plane_no=(0, 0, -1), clear_outer=True)
        if cap is not None:
            edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and
                     len(e.link_faces) == 1]
            if edges:
                filled = bmesh.ops.holes_fill(bm, edges=edges, sides=0)
                tris = bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]
                slot = mk.slot_of(obj, cap)
                for f in tris:
                    f.material_index = slot
                    f.smooth = False
                    if f.normal.z > 0:
                        f.normal_flip()
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
    return [o for o in objects if len(o.data.polygons) > 0]


def build_tower(m, lowered=0.0, parted=0.0, glow=0, head_only=False):
    """The tower's parts, upright, by piece: {piece name: [objects]}."""
    pieces = {"red_tower_head": head_assembly(m, lowered, parted, glow)}
    if head_only:
        return pieces
    vents = crown(m) + upper_bulb(m) + [shaft(m, 54.3, 56.0, "shaft_top")]
    lower = [shaft(m, 56.0, 65.3, "shaft")] + shaft_details(m) + lower_bulb(m) + [base_body(m, 77.6, 84.0, "base_top")]
    base = [base_body(m, 84.0, 98.35, "base")] + base_details(m)
    pieces.update({"red_tower_vents": vents, "red_tower_shaft": lower, "red_tower_base": base})
    return pieces


def finish(pieces, m):
    """Leans every part, cuts away what is under the floor."""
    out = {}
    for name, objs in pieces.items():
        out[name] = floor_cut(lean(objs), cap=m["seam"])
    bpy.context.view_layer.update()
    return out


# --- Checks -----------------------------------------------------------------------------------------------------------

def sprite_indices(sheet, sprite):
    mask = k.sprite_mask(sheet, sprite)
    raw = open(sheet[:-4] + ".idx", "rb").read()
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[raw[(y0 + r) * 228 + x0 + c] if mask[r][c] else None for c in range(24)] for r in range(28)]


def own_mask(sheet, sprite, base=False):
    """A sprite's own pixels: all of them, but the base's: its rows 0-13 without the floor's ramp-6 tiles."""
    idx = sprite_indices(sheet, sprite)
    return [[v is not None and (not base or (r <= 13 and v >> 4 != 6 and 3 <= c <= 20)) for c, v in enumerate(row)]
            for r, row in enumerate(idx)]


def view_coverage(objects, rows, centre_y, sub=3):
    """Which pixels of a 24-wide picture the camera sees the objects at (rows of bools): rays along the camera's line
    of sight through each pixel's samples onto the floor; the picture's top edge at y = centre_y + rows / 2."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    out = []
    top = centre_y + rows / 2.0
    for r in range(rows):
        line = []
        for c in range(24):
            hits = 0
            for i in range(sub):
                for j in range(sub):
                    x = c - 12.0 + (i + 0.5) / sub
                    y = top - r - (j + 0.5) / sub
                    origin = Vector((x, y, 0.0)) - VIEW * 200.0
                    if any(t.ray_cast(origin, VIEW, 400.0)[0] is not None for t in trees):
                        hits += 1
            line.append(hits * 2 > sub * sub)
        out.append(line)
    return out


# --- Output -----------------------------------------------------------------------------------------------------------

def remove(objects):
    for obj in objects:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)


def export_piece(parts, name, y_centre, options, mask=None, label=""):
    out = mk.outdir(options)
    objs = [o for o in parts if len(o.data.polygons) > 0]
    db.drop_unused(objs)
    mk.transform(objs, Matrix.Translation((0.0, -y_centre, 0.0)))
    bpy.context.view_layer.update()
    triangulate(objs)
    if "stats" in options:
        for obj in sorted(objs, key=lambda o: -mk.triangles([o]))[:12]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    obj = db.join(objs, name)
    obj.data.name = name
    if mask is not None:
        mk.compare("%s (%s), as the game's camera sees it" % (name, label), view_coverage([obj], 28, 0.0), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj], size=(24, 40), scale=10, distance=1.8, centre=(0.0, -8.0))
    remove([obj])


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    want = lambda name: not only or name in only  # noqa: E731
    sheet = os.path.join(options["check"], "enemy_C.png") if "check" in options else None
    k.reset()
    m = materials()
    pieces = finish(build_tower(m), m)
    masks = {s: own_mask(sheet, s, base=(s == 55)) for s in (77, 115, 17, 55)} if sheet else {}
    if sheet:
        everything = [o for objs in pieces.values() for o in objs]
        mk.compare("whole tower (C 77 above 115 above 17 above 55), as the game's camera sees it",
                   view_coverage(everything, 112, 0.0), masks[77] + masks[115] + masks[17] + masks[55])
    if "preview" in options:
        everything = [o for objs in pieces.values() for o in objs]
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.preview(options["preview"] + "red_tower_whole", everything, size=(28, 112), scale=6, distance=2.8)
    if "whole" in options:
        everything = [o for objs in pieces.values() for o in objs]
        triangulate(everything)
        mk.export(everything, options["whole"])
    for name, sprite, r0, r1, yc in PIECES:
        objs = pieces.pop(name)
        if name == "red_tower_head" or not want(name):
            remove(objs)
            continue
        for rest in pieces.values():
            for o in rest:
                o.hide_render = True
        export_piece(objs, name, yc, options, masks.get(sprite), "C %d" % sprite)
        for rest in pieces.values():
            for o in rest:
                o.hide_render = False
    # The head in each of its frames (frame models: the same piece, lowered and opened).
    for name, sprite, lowered, parted, glow in HEAD_FRAMES:
        if not want(name):
            continue
        head = finish(build_tower(m, lowered, parted, glow, head_only=True), m)["red_tower_head"]
        mask = own_mask(sheet, sprite) if sheet else None
        export_piece(head, name, 42.0, options, mask, "C %d" % sprite)


if __name__ == "__main__":
    build()
