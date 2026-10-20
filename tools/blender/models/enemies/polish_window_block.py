"""The grey building of TORM and BONUS (sheet J sprites 5 and 7 above 43 and 45, 2x2 each: one 48 x 56 picture; ground
layer; enemies 747 (5), 748 (7), 745 (43), 746 (45); 5 and 43 animate: 5 5 9 9 9 9 11 11 11 11 9 9 9 9 5 5 and 43 43
47 47 47 47 49 49 49 49 47 47 47 47 43 43), polished (2026-10-20; it replaces wave3_m_ground.py's block_whole() and
block_piece(), a plain grey block with three green windows). models.cfg: model window_block_tl / _tr / _bl / _br and
the frame models window_block_tl_9, _tl_11, _bl_47, _bl_49 ... origin; sprite j 5 window_block_tl yaw=0 height=-4,
sprite j 7 window_block_tr ..., sprite j 43 window_block_bl ..., sprite j 45 window_block_br ..., frame j 9
window_block_tl_9 and so on. The levels put the four together (event 12: 5 at (x, y - 28), 7 at (x + 24, y - 28), 43
at (x, y), 45 at (x + 24, y)). None of these sprites is another sprite's pixels mirrored or in other ramps (43, 47 and
49 are one picture but for the windows' light; nothing else uses 9, 11, 47 or 49).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture; greys of ramp 0): a bunker
of grey armour plate on the foliage. In its middle a tower (columns 13-24 of rows 4-30) whose top is a frame round
three square windows of green glass (columns 16-22 of rows 7-13, 15-21 and 23-29, bars between them), lit from
inside, their left and upper reveals in shadow; under it the tower's front (rows 31-35) with a narrow door. Left of
it a wing (columns 4-12 of rows 5-36), its back cut off on the diagonal, a rim round a recessed dark panel whose
lower right corner is cut off on the diagonal too. Right of it a lower block (columns 25-37 of rows 7-35): at its
back a vent housing with three fins running up the screen (rows 7-13, its back right corner cut off); its top laid
with louvres across the screen (lit edges at rows 15, 20, 25 and 31, grooves at 14, 19, 24 and 30), a duct running
down its right half (columns 31-35) over its front and on across the plinth to the plinth's front edge (row 42); its
right edge dark. Under it all a plinth (rows 36-46): its top with a vent of two slots at its left end, a dark channel
like a T (column 14, row 38), a hatch (columns 15-24 of rows 39-41) and a pipe (column 26); its front a dark battered
face (rows 44-46) under a lit lip (row 43). The foliage round it and the dark patch right of it (its shadow) are the
map's and the game's: left out.

The animation runs a light down the windows: 5/43 the top one blazing (a hot spot at its upper left), the middle
one glowing, the bottom one dark; 9/47 the middle one blazing, the top one glowing, the bottom one dim; 11/49 the
bottom one blazing, the middle one glowing, the top one dark. The windows lie in 5 and 43 (the bottom one across
both): window_block_tl and _bl are the first frame, window_block_tl_9 / _bl_47 the second, _tl_11 / _bl_49 the third
(the same geometry, the glass' materials changed; emission well under 1: the bloom adds to it).

Built as such a bunker: CAD-like solids (polish_machine_kit: polygons extruded, cut by planes and each other with
exact booleans, edges bevelled, flat faces kept flat), heights giving the slanted camera depth: the plinth 5 pixels
high, its front battered from the lip down to the foliage; the wing's top sloping down to the left from 12.5 to 8.5;
the right block 11 (its vent housing a little higher, the duct 1.6 above it, bending down its battered front onto the
plinth); the tower 15.5, its front battered down to the plinth, the windows sunk 1.2 into its top with sloping left
and upper reveals and the glass on their floor. Every wall reaches SKIRT under the foliage, so the building stands on
the terrain with height=-4 (the green tower beside it in TORM stands 4 pixels up without it; the jaw guns and the
block house use it). The whole is built about the picture's centre and cut along the sprites' edges (polish_arch.py's
cut(): the pieces keep the whole's shading across the cuts), each piece moved so its sprite's centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the foliage (z = 0); P(c, r)
turns a pixel edge of the picture (column c, row r) into the whole's coordinates (x = c - 24, y = 28 - r).

Replaces wave3_m_ground.py's window block: remove BLOCK_ORIGIN, block_whole() (its @whole("block", (48, 56))
registration), block_piece() and the four model("window_block_..") lines; greys(), wedge(), rect() and inside() stay
(the field gun, the lens pad and the eye orb use greys(); the others are the file's helpers).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against the building's own pixels, written below), --preview <prefix> (the whole's and each piece's
top and 3/4 views), --only <model,...>.
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
from polish_arch import cut, plane_box  # noqa: E402  (cut: polish_machine_kit.cut without its material indices
#                                                      shifted twice)

# The building's own pixels in the 48 x 56 picture ('#'): the foliage and the shadow right of it left out.
OWN = """
................................................
................................................
................................................
................................................
..............############......................
.............#############......................
............##############......................
...........##########################...........
..........############################..........
.........##############################.........
........################################........
.......#################################........
......##################################........
.....##################################.........
....##################################..........
....##################################..........
....##################################..........
....##################################..........
....##################################..........
.....#################################..........
.....#################################..........
.....#################################..........
....##################################..........
....##################################..........
....##################################..........
....##################################..........
....##################################..........
....##################################..........
.....#################################..........
.....#################################..........
.....#################################..........
.....#################################..........
.....#################################..........
....##################################..........
....##################################..........
....##################################..........
....###################################.........
....###################################.........
....###################################.........
....###################################.........
....###################################.........
....###################################.........
....###################################.........
....###################################.........
.....##################################.........
.....##################################.........
.....##################################.........
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

# The pieces: (name, its sprite in each frame, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("window_block_tl", (5, 9, 11), (-24.0, 0.0, 0.0, 28.0)),
          ("window_block_tr", (7, 7, 7), (0.0, 24.0, 0.0, 28.0)),
          ("window_block_bl", (43, 47, 49), (-24.0, 0.0, -28.0, 0.0)),
          ("window_block_br", (45, 45, 45), (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {"tl": (0, 0), "tr": (24, 0), "bl": (0, 28), "br": (24, 28)}  # top left corners in the picture
# The frames: each window's light (top, middle, bottom).
FRAMES = [("bright", "medium", "dark"), ("medium", "bright", "dim"), ("dark", "medium", "bright")]


def P(c, r):
    """A pixel edge of the 48 x 56 picture (column c, row r) in the whole's coordinates."""
    return (c - 24.0, 28.0 - r)


def X(c):
    return c - 24.0


def Y(r):
    return 28.0 - r


SKIRT = -4.0                 # how far the walls reach under the foliage
PL_H = 5.0                   # the plinth's top
LIP_R, FOOT_R = 43.6, 47.0   # its front: the lip (z = PL_H) and the foot of the battered face (z = 0)
GLACIS_SEAMS = (14.4, 30.6)  # the seams between the plates of the plinth's front (columns)
PLINTH = [(4.2, 14.0), (12.6, 5.6), (26.0, 5.6), (26.0, 7.4), (37.0, 7.4), (37.8, 8.2), (37.8, 35.8), (38.8, 36.6),
          (38.8, 44.0), (37.8, 47.0), (5.0, 47.0), (4.2, 44.0)]
# The tower: its plan, its top, its front battered from row TOWER_FRONT (the top's edge) down to TOWER_FOOT.
TOWER = [(13.0, 5.0), (14.0, 4.0), (25.6, 4.0), (25.6, 37.0), (13.0, 37.0)]
T_H = 15.5
TOWER_FRONT, TOWER_FOOT = 31.0, 36.0
# The windows: their openings in the top (columns c0-c1, rows r0-r1, pixel edges), sunk WIN_D; the reveals slope in
# by REVEAL (left, top, right, bottom) on the way down to the glass.
WINDOWS = [(16.0, 23.0, 7.0, 14.0), (16.0, 23.0, 15.0, 22.0), (16.0, 23.0, 23.0, 30.0)]
WIN_D = 1.2
REVEAL = (0.9, 0.7, 0.12, 0.12)
HOT = (1.9, 1.9, 1.7)        # the hot spot of a blazing window: right of its left edge, down from its top, radius
DOOR = (17.6, 20.4)          # the door in the tower's front (columns)
TOWER_RIVETS = [(14.5, 5.6), (24.3, 5.6), (14.5, 14.5), (14.5, 22.5), (24.3, 14.5), (24.3, 22.5), (14.5, 30.3),
                (24.3, 30.3)]   # rivets on its top's rim, where the bars meet it and at its corners
# The wing: its plan, its top sloping from WING_LO at its left edge up to WING_HI by the tower, its front battered
# from WING_FRONT down to the plinth at WING_FOOT; the recessed panel in it, PANEL_D deep.
WING = [(4.4, 13.6), (12.4, 5.6), (12.4, 37.0), (4.4, 37.0)]
WING_LO, WING_HI = 8.5, 12.5
WING_FRONT, WING_FOOT = 34.6, 36.4
WING_PANEL = [(7.0, 16.0), (10.0, 13.0), (11.9, 13.0), (11.9, 27.1), (7.0, 32.0)]
PANEL_D = 0.7
# The right block: its plan, its top, its front battered from RB_FRONT down to the plinth at RB_FOOT; its right edge
# chamfered from CHAMFER_C; the vent housing at its back (its top sloping from CAP_BACK to CAP_FRONT), three fins on it.
RIGHT = [(26.0, 13.6), (37.8, 13.6), (37.8, 37.0), (26.0, 37.0)]
RB_H = 11.0
RB_FRONT, RB_FOOT = 33.0, 36.4
CHAMFER_C = 36.0
CAP = [(26.0, 7.0), (37.0, 7.0), (39.6, 9.6), (39.6, 14.0), (26.0, 14.0)]
CAP_BACK, CAP_FRONT = 12.9, 12.1
FINS = [(26.8, 28.7), (29.9, 31.8), (33.7, 35.6)]
LOUVRES = [(14.4, 19.0), (19.5, 24.0), (24.5, 30.0), (30.5, 33.4)]   # rows of the louvres (left half, columns 26.3-30.3)
LOUVRE_C = (26.3, 30.3)
# The duct: columns, from its back (abutting the vent housing) to its end on the plinth; its top over the block and
# over the plinth; the joints across it.
DUCT_C = (31.0, 36.0)
DUCT_R = (13.8, 42.6)
DUCT_TOP, DUCT_LOW = RB_H + 1.6, PL_H + 1.5
DUCT_JOINTS = (19.5, 24.5, 30.5, 38.5)
# On the plinth's top: the vent (its plate and two slots), the T channel, the hatch, the pipe.
VENT = (5.3, 9.9, 37.1, 41.8)
VENT_SLOTS = [(6.0, 6.9), (8.0, 8.9)]
VENT_SLOT_R = (37.9, 41.0)
CHANNELS = [(13.7, 15.0, 36.2, 41.9), (13.7, 25.2, 37.6, 38.9)]
CHANNEL_D = 1.1
HATCH = (15.4, 24.6, 39.2, 42.2)
HATCH_INNER = (17.0, 23.0, 39.9, 41.8)
PIPE = (26.2, 36.9, 42.7, 0.62)   # column of its axis, rows from-to, radius


def materials():
    def mat(name, index, metallic=0.45, roughness=0.42):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "slot": mat("wblock_slot", 0x03, 0.3, 0.6),
        "dark": mat("wblock_dark", 0x04, 0.4, 0.5),
        "panel": mat("wblock_panel", 0x05, 0.4, 0.48),
        "wall": mat("wblock_wall", 0x06, 0.45, 0.45),
        "rim": mat("wblock_rim", 0x07, 0.45, 0.42),
        "deck": mat("wblock_deck", 0x09, 0.45, 0.4),
        "top": mat("wblock_top", 0x0a, 0.45, 0.38),
        "lit": mat("wblock_lit", 0x0b, 0.45, 0.34),
        "edge": mat("wblock_edge", 0x0c, 0.45, 0.3),
    }


def glass_materials():
    """The glass' states: (base material, hot spot material or None)."""
    glow = k.level_palette()

    def lit(name, index, strength):
        if strength <= 0:
            return k.material(name, palette=index, metallic=0.1, roughness=0.12)
        return k.material(name, palette=index, metallic=0.0, roughness=0.12, emission=glow[index],
                          emission_strength=strength)
    return {
        "bright": (lit("wblock_glass_bright", 0xc9, 0.4), lit("wblock_glass_hot", 0xcc, 0.55)),
        "medium": (lit("wblock_glass_medium", 0xc6, 0.18), None),
        "dim": (lit("wblock_glass_dim", 0xc3, 0.06), None),
        "dark": (lit("wblock_glass_dark", 0xc1, 0.0), None),
    }


# --- Helpers --------------------------------------------------------------------------------------------------------

def plan(points):
    """Pixel-edge points (c, r) to the whole's (x, y), counter-clockwise seen from above."""
    pts = [P(c, r) for c, r in points]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


def rect(c0, c1, r0, r1):
    return plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)])


def frustum(name, bottom, z0, top, z1, mat=None):
    """A box whose bottom (x0, x1, y0, y1) at z0 and top at z1 differ (sloping sides), for cutting reveals."""
    bm = bmesh.new()
    rings = []
    for (x0, x1, y0, y1), z in ((bottom, z0), (top, z1)):
        rings.append([bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)), bm.verts.new((x1, y1, z)),
                      bm.verts.new((x0, y1, z))])
    b, t = rings
    bm.faces.new(b[::-1])
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def batter(top_z, top_r, foot_z, foot_r):
    """The plane of a battered front: top_z along row top_r, falling to foot_z along row foot_r (z(x, y))."""
    slope = (top_z - foot_z) / (Y(top_r) - Y(foot_r))
    return lambda x, y: top_z + slope * (y - Y(top_r))


def inside_rect(c, box, pad=0.0):
    x0, x1, y0, y1 = box
    return x0 - pad <= c.x <= x1 + pad and y0 - pad <= c.y <= y1 + pad


def box_of(c0, c1, r0, r1):
    """A pixel-edge box as (x0, x1, y0, y1)."""
    return (X(c0), X(c1), Y(r1), Y(r0))


def finish(obj, width, segments=2, angle=35.0):
    mk.cleanup(obj)
    mk.bevel(obj, width, segments, angle)
    mk.shade(obj, 35)
    return obj


# --- The parts ------------------------------------------------------------------------------------------------------

def plinth(m):
    """The plinth under it all: its top at PL_H, its front battered from the lip down to the foliage; the vent's slots
    and the T channel cut into its top."""
    body = mk.prism("plinth", plan(PLINTH), SKIRT, PL_H, m["deck"])
    mk.boolean(body, plane_box("glacis", batter(PL_H, LIP_R, 0.0, FOOT_R)), "INTERSECT")
    for i, (c0, c1, r0, r1) in enumerate(CHANNELS):
        mk.boolean(body, mk.box(f"channel{i}", X(c0), X(c1), Y(r1), Y(r0), PL_H - CHANNEL_D, PL_H + 2.0), "DIFFERENCE")
    # The seams between the armour plates of its front.
    glacis = batter(PL_H, LIP_R, 0.0, FOOT_R)
    n = Vector((0.0, -PL_H, Y(LIP_R) - Y(FOOT_R))).normalized()   # out of the front
    pa, pb = Vector((0.0, Y(LIP_R) + 0.4, glacis(0.0, Y(LIP_R) + 0.4))), Vector((0.0, Y(FOOT_R) - 1.0, glacis(0.0, Y(FOOT_R) - 1.0)))
    for i, c in enumerate(GLACIS_SEAMS):
        profile = [tuple((pa - n * 0.4).yz), tuple((pa + n * 2.0).yz), tuple((pb + n * 2.0).yz), tuple((pb - n * 0.4).yz)]
        mk.boolean(body, mk.prism(f"glacis_seam{i}", profile, X(c) - 0.17, X(c) + 0.17, axis="x"), "DIFFERENCE")
    finish(body, 0.32)
    chans = [box_of(*ch) for ch in CHANNELS]

    def pick(c, n):
        if c.z < PL_H - 0.05 and any(inside_rect(c, b, 0.02) for b in chans):
            return m["slot"]
        if n.z > 0.95:
            return None
        if any(abs(c.x - X(sc)) < 0.2 for sc in GLACIS_SEAMS) and c.y < Y(LIP_R) and abs(n.x) > 0.5:
            return m["slot"]           # the seams' walls
        if n.y < -0.3 and n.z > 0.15:
            return m["rim"]            # the battered face (it faces away from the sun: a lighter shade)
        if n.z > 0.3:
            return m["edge"] if (n.y > 0.25 or n.x < -0.25) else m["dark"]
        return m["wall"]
    mk.paint(body, pick)
    return body


def plinth_details(m):
    """On the plinth's top: the vent plate with its two slots, the hatch, the pipe, a pipe in the T channel."""
    c0, c1, r0, r1 = VENT
    vent = mk.box("vent", X(c0), X(c1), Y(r1), Y(r0), PL_H - 0.3, PL_H + 0.45, m["top"])
    for i, (s0, s1) in enumerate(VENT_SLOTS):
        mk.boolean(vent, mk.box(f"vent_slot{i}", X(s0), X(s1), Y(VENT_SLOT_R[1]), Y(VENT_SLOT_R[0]), PL_H + 0.08,
                                PL_H + 2.0), "DIFFERENCE")
    finish(vent, 0.18)
    slots = [box_of(s0, s1, *VENT_SLOT_R) for s0, s1 in VENT_SLOTS]

    def vent_pick(c, n):
        if c.z < PL_H + 0.4 and any(inside_rect(c, b, 0.02) for b in slots):
            return m["slot"]
        if n.z > 0.95:
            return None
        if n.z > 0.3:
            return m["edge"] if (n.y > 0.25 or n.x < -0.25) else m["dark"]
        return m["wall"]
    mk.paint(vent, vent_pick)
    # The hatch: a frame plate and a raised inner plate, bolted at its corners.
    c0, c1, r0, r1 = HATCH
    frame = mk.box("hatch", X(c0), X(c1), Y(r1), Y(r0), PL_H - 0.3, PL_H + 0.22, m["deck"])
    finish(frame, 0.12, 1)
    c0, c1, r0, r1 = HATCH_INNER
    inner = mk.box("hatch_inner", X(c0), X(c1), Y(r1), Y(r0), PL_H, PL_H + 0.55, m["top"])
    finish(inner, 0.16, 2)
    for obj in (frame, inner):
        mk.paint(obj, lambda c, n: m["edge"] if (n.z > 0.3 and n.z < 0.95 and (n.y > 0.25 or n.x < -0.25)) else
                 m["dark"] if (n.z > 0.3 and n.z < 0.95) else None)
    for i, (bc, br) in enumerate(((15.95, 39.75), (24.05, 39.75), (15.95, 41.65), (24.05, 41.65))):
        mk.dome(f"hatch_bolt{i}", P(bc, br), (0.28, 0.28, 0.18), PL_H + 0.2, m["edge"], 10, 3)
    # The pipe lying on the deck, flanged at both ends.
    pc, pr0, pr1, rad = PIPE
    x = X(pc)
    rings = []
    for r in (pr0, pr1):
        rings.append([Vector((x + rad * math.cos(2 * math.pi * j / 16), Y(r), PL_H + rad * 0.9 +
                              rad * math.sin(2 * math.pi * j / 16))) for j in range(16)])
    pipe = k.loft("pipe", rings, m["deck"])
    k.smooth(pipe, 50)
    mk.paint(pipe, lambda c, n: m["dark"] if n.z < -0.2 else m["edge"] if n.x < -0.4 and n.z > -0.2 else None)
    for i, r in enumerate((pr0 + 0.35, pr1 - 0.35)):
        mk.tube(f"pipe_flange{i}", [(x, Y(r) + 0.22, PL_H + rad * 0.9), (x, Y(r) - 0.22, PL_H + rad * 0.9)],
                rad + 0.22, m["wall"], 16)
    # A conduit lying in the T channel (dark: the channel's shadow on it).
    for i, (c0, c1, r0, r1) in enumerate(CHANNELS):
        z = PL_H - CHANNEL_D + 0.42
        if c1 - c0 < r1 - r0:
            a, b = (X((c0 + c1) / 2), Y(r0 + 0.2), z), (X((c0 + c1) / 2), Y(r1 - 0.2), z)
        else:
            a, b = (X(c0 + 0.2), Y((r0 + r1) / 2), z), (X(c1 - 0.2), Y((r0 + r1) / 2), z)
        k.smooth(mk.tube(f"conduit{i}", [a, b], 0.38, m["dark"], 10), 50)


def tower(m):
    """The tower: its top a frame round the three windows (sunk, their left and upper reveals sloping), its front
    battered down to the plinth with a door in it."""
    body = mk.prism("tower", plan(TOWER), PL_H - 1.0, T_H, m["top"])
    front = batter(T_H, TOWER_FRONT, PL_H, TOWER_FOOT)
    mk.boolean(body, plane_box("tower_front", front), "INTERSECT")
    for i, (c0, c1, r0, r1) in enumerate(WINDOWS):
        top = box_of(c0, c1, r0, r1)
        rl, rt, rr, rb = REVEAL
        bottom = (top[0] + rl, top[1] - rr, top[2] + rb, top[3] - rt)
        cutter = frustum(f"window_cut{i}", bottom, T_H - WIN_D, (top[0] - rl * 0.4 / WIN_D, top[1] + rr * 0.4 / WIN_D,
                                                                 top[2] - rb * 0.4 / WIN_D, top[3] + rt * 0.4 / WIN_D),
                         T_H + 0.4)
        mk.boolean(body, cutter, "DIFFERENCE")
    # The door: a recess in the battered front.
    d0, d1 = DOOR
    ya, yb = Y(TOWER_FRONT + 1.4), Y(TOWER_FOOT - 0.15)
    depth = 0.55
    n = Vector((0.0, -(T_H - PL_H), Y(TOWER_FRONT) - Y(TOWER_FOOT))).normalized()   # out of the front, down the screen
    pa = Vector((0.0, ya, front(0.0, ya)))
    pb = Vector((0.0, yb, front(0.0, yb)))
    profile = [tuple((pa - n * depth).yz), tuple((pa + n * 2.0).yz), tuple((pb + n * 2.0).yz), tuple((pb - n * depth).yz)]
    door = mk.prism("door_cut", profile, X(d0), X(d1), axis="x")
    mk.boolean(body, door, "DIFFERENCE")
    finish(body, 0.3)
    for i, (rc, rr) in enumerate(TOWER_RIVETS):
        mk.dome(f"tower_rivet{i}", P(rc, rr), (0.3, 0.3, 0.18), T_H - 0.04, m["edge"], 10, 3)
    wins = [box_of(*w) for w in WINDOWS]
    door_box = (X(d0), X(d1), yb - 0.3, ya + 0.3)

    def pick(c, nrm):
        if c.z < T_H - 0.05 and any(inside_rect(c, b, 0.05) for b in wins):
            return m["slot"]               # the reveals and the floor under the glass
        if inside_rect(c, door_box) and c.z < front(c.x, c.y) - 0.05:
            if nrm.dot(n) > 0.9:
                return m["dark"]           # the door
            return m["slot"] if nrm.z < 0.5 else m["edge"]   # its jambs, its lintel's lit sill
        if nrm.z > 0.95:
            return None
        if nrm.y < -0.5 and nrm.z > 0.2:
            return m["rim"]
        if nrm.z > 0.3:
            return m["edge"] if (nrm.y > 0.25 or nrm.x < -0.25) else m["dark"]
        return m["wall"]
    mk.paint(body, pick)
    return body


def glass():
    """The windows' glass on the reveals' floors: grids (their hot spots split off by set_light)."""
    panes = []
    for i, (c0, c1, r0, r1) in enumerate(WINDOWS):
        x0, x1, y0, y1 = box_of(c0, c1, r0, r1)
        rl, rt, rr, rb = REVEAL
        x0, x1, y0, y1 = x0 + rl - 0.05, x1 - rr + 0.05, y0 + rb - 0.05, y1 - rt + 0.05
        z = T_H - WIN_D + 0.06
        nx, ny = 14, 14
        bm = bmesh.new()
        verts = [[bm.verts.new((x0 + (x1 - x0) * a / nx, y0 + (y1 - y0) * b / ny, z)) for a in range(nx + 1)]
                 for b in range(ny + 1)]
        for b in range(ny):
            for a in range(nx):
                bm.faces.new((verts[b][a], verts[b][a + 1], verts[b + 1][a + 1], verts[b + 1][a]))
        mesh = bpy.data.meshes.new(f"glass{i}")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f"glass{i}", mesh)
        bpy.context.scene.collection.objects.link(obj)
        panes.append(obj)
    return panes


def set_light(panes, states, mats):
    """Gives the panes a frame's light (states: each window's), the hot spot of a blazing one its own material."""
    for i, (pane, state) in enumerate(zip(panes, states)):
        base, hot = mats[state]
        pane.data.materials.clear()
        pane.data.materials.append(base)
        if hot is not None:
            pane.data.materials.append(hot)
        c0, c1, r0, r1 = WINDOWS[i]
        hx, hy, hr = X(c0) + HOT[0], Y(r0) - HOT[1], HOT[2]
        for poly in pane.data.polygons:
            near = math.hypot(poly.center.x - hx, (poly.center.y - hy) * 1.1) < hr
            poly.material_index = 1 if (hot is not None and near) else 0
        pane.data.update()


def wing(m):
    """The wing: its top sloping down to the left, a rim round a recessed panel, its front battered."""
    xs = [x for x, _ in plan(WING)]
    xa, xb = min(xs), max(xs)

    def top(x, y):
        return WING_LO + (WING_HI - WING_LO) * (x - xa) / (xb - xa)
    body = mk.wedge("wing", plan(WING), SKIRT, top, m["rim"])
    slope = (WING_HI - PL_H) / (Y(WING_FRONT) - Y(WING_FOOT))
    mk.boolean(body, plane_box("wing_front", lambda x, y: top(x, y) + slope * (y - Y(WING_FRONT))), "INTERSECT")
    panel = mk.wedge("panel_cut", plan(WING_PANEL), 0.0, lambda x, y: top(x, y) + 2.0,
                     bottom=lambda x, y: top(x, y) - PANEL_D)
    mk.boolean(body, panel, "DIFFERENCE")
    finish(body, 0.3)
    outline = plan(WING_PANEL)

    def in_panel(c):
        hit = False
        j = len(outline) - 1
        for i in range(len(outline)):
            (ax, ay), (bx, by) = outline[i], outline[j]
            if (ay > c.y) != (by > c.y) and c.x < (bx - ax) * (c.y - ay) / (by - ay) + ax:
                hit = not hit
            j = i
        return hit

    def pick(c, n):
        below = c.z < top(c.x, c.y) - 0.1
        if below and in_panel(c) and n.z > 0.9:
            return m["panel"]
        if below and n.z < 0.9 and c.z > top(c.x, c.y) - PANEL_D - 0.2 and c.y > Y(WING_FRONT) + 0.5:
            return m["slot"] if (n.x > 0.3 or n.y < -0.3) else m["edge"]   # its walls: shaded, or lit facing the sun
        if n.z > 0.9:
            return None
        if n.y < -0.3 and n.z > 0.15:
            return m["deck"]               # its front, lit where the sprite draws the rim
        if n.z > 0.3:
            return m["edge"] if (n.y > 0.25 or n.x < -0.25) else m["dark"]
        return m["wall"]
    mk.paint(body, pick)
    # Bolts in the panel's corners.
    for i, (bc, br) in enumerate(((8.0, 17.2), (11.1, 14.0), (11.1, 26.4), (8.0, 30.4))):
        x, y = P(bc, br)
        mk.dome(f"panel_bolt{i}", (x, y), (0.3, 0.3, 0.2), top(x, y) - PANEL_D, m["rim"], 10, 3)
    return body


def right_block(m):
    """The right block: its top under the louvres, its right edge chamfered, its front battered; the vent housing at
    its back with its fins."""
    body = mk.prism("right", plan(RIGHT), SKIRT, RB_H, m["deck"])
    mk.boolean(body, plane_box("right_front", batter(RB_H, RB_FRONT, PL_H, RB_FOOT)), "INTERSECT")
    xc = X(CHAMFER_C)
    mk.boolean(body, plane_box("right_chamfer", lambda x, y: RB_H - (x - xc)), "INTERSECT")
    finish(body, 0.28)

    def pick(c, n):
        if n.z > 0.95:
            return None
        if n.x > 0.4 and n.z > 0.3:
            return m["dark"]               # the chamfer, away from the sun
        if n.y < -0.3 and n.z > 0.15:
            return m["rim"]
        if n.z > 0.3:
            return m["edge"] if (n.y > 0.25 or n.x < -0.25) else m["dark"]
        return m["wall"]
    mk.paint(body, pick)
    # The vent housing: its top sloping a little down the screen, its back right corner cut off.
    cap_top = lambda x, y: CAP_FRONT + (CAP_BACK - CAP_FRONT) * (y - Y(14.0)) / (Y(7.0) - Y(14.0))  # noqa: E731
    cap = mk.wedge("cap", plan(CAP), RB_H - 1.5, cap_top, m["rim"])
    mk.boolean(cap, plane_box("cap_chamfer", lambda x, y: RB_H + 2.5 - 0.9 * (x - X(37.4))), "INTERSECT")
    finish(cap, 0.3)

    def cap_pick(c, n):
        if n.z > 0.95:
            return None
        if n.x > 0.4 and n.z > 0.3:
            return m["dark"]
        if n.z > 0.3:
            return m["edge"] if (n.y > 0.25 or n.x < -0.25) else m["dark"]
        return m["wall"]
    mk.paint(cap, cap_pick)
    for i, (c0, c1) in enumerate(FINS):
        fin = mk.wedge(f"fin{i}", rect(c0, c1, 7.5, 13.7), CAP_FRONT - 1.0, lambda x, y: cap_top(x, y) + 0.75, m["top"])
        finish(fin, 0.3, 2, 30)
        mk.paint(fin, lambda c, n: m["edge"] if (n.z > 0.2 and n.z < 0.95 and (n.y > 0.25 or n.x < -0.25)) else
                 m["wall"] if n.z < 0.2 else None)
    # The louvres across the left half: plates sloping down the screen, their back edges raised and lit.
    for i, (r0, r1) in enumerate(LOUVRES):
        ya, yb = Y(r0), Y(r1)
        hi, lo = RB_H + 0.75, RB_H + 0.2
        louvre = mk.wedge(f"louvre{i}", rect(LOUVRE_C[0], LOUVRE_C[1], r0, r1), RB_H - 0.4,
                          lambda x, y, ya=ya, yb=yb: lo + (hi - lo) * (y - yb) / (ya - yb), m["rim"])
        finish(louvre, 0.22, 2, 30)
        mk.paint(louvre, lambda c, n: m["edge"] if (n.y > 0.3 and n.z > 0.2) else
                 m["slot"] if (n.y < -0.3 and n.z < 0.6) else m["wall"] if n.z < 0.2 else None)
    return body


def duct(m):
    """The duct down the right block's right half, bending down its front onto the plinth to the plinth's lip; joints
    across it."""
    c0, c1 = DUCT_C
    r0, r1 = DUCT_R
    bend0, bend1 = RB_FRONT - 0.3, RB_FOOT - 0.4
    profile = [(Y(r0), RB_H - 0.6), (Y(r0), DUCT_TOP), (Y(bend0), DUCT_TOP), (Y(bend1), DUCT_LOW), (Y(r1), DUCT_LOW),
               (Y(r1), PL_H - 0.5), (Y(RB_FOOT + 0.4), PL_H - 0.5), (Y(RB_FRONT + 0.2), RB_H - 0.6)]
    body = mk.prism("duct", profile, X(c0), X(c1), m["lit"], axis="x")
    for i, r in enumerate(DUCT_JOINTS):
        z = (DUCT_TOP if r < RB_FRONT else DUCT_LOW) - 0.38
        mk.boolean(body, mk.box(f"duct_joint{i}", X(c0) - 1.0, X(c1) + 1.0, Y(r) - 0.2, Y(r) + 0.2, z, DUCT_TOP + 2.0),
                   "DIFFERENCE")
    finish(body, 0.4, 2, 30)

    def pick(c, n):
        if any(abs(c.y - Y(r)) < 0.21 for r in DUCT_JOINTS) and abs(n.y) > 0.8:
            return m["slot"]
        if n.z > 0.95:
            return None
        if n.y < -0.3 and n.z > 0.15:
            return m["deck"]               # its bend down the front
        if n.z > 0.3:
            return m["edge"] if (n.y > 0.25 or n.x < -0.25) else m["wall"]
        return m["wall"]
    mk.paint(body, pick)
    return body


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(m):
    plinth(m)
    plinth_details(m)
    tower(m)
    wing(m)
    right_block(m)
    duct(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def own_mask(r0=0, c0=0, rows=56, cols=48):
    lines = [line for line in OWN.strip("\n").split("\n")]
    mask = [[ch == "#" for ch in line] for line in lines]
    return [row[c0:c0 + cols] for row in mask[r0:r0 + rows]]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    gm = glass_materials()
    whole = build_whole(m)
    panes = glass()
    set_light(panes, FRAMES[0], gm)
    whole += panes
    print("whole window block: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "check" in options:
        mk.compare("whole (J 5 + 7 above 43 + 45, the building)", mk.coverage(whole, 48, 56), own_mask())
    for f, states in enumerate(FRAMES):
        set_light(panes, states, gm)
        if "preview" in options:
            mk.preview(options["preview"] + "window_block_whole_%d" % (f + 1), whole, size=(48, 56), scale=8,
                       distance=1.8)
        for name, sprites, box in PIECES:
            if f > 0 and sprites[f] == sprites[0]:
                continue                   # tr and br don't change
            model = name if f == 0 else "%s_%d" % (name, sprites[f])
            if only and model not in only and name not in only:
                continue
            pieces = [p for p in (cut(src, box, m["wall"]) for src in whole) if p is not None]
            mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if "check" in options and f == 0:
                c0, r0 = SPRITE_AT[name.rsplit("_", 1)[1]]
                mk.compare("%s (J %d)" % (model, sprites[f]), mk.coverage(pieces, 24, 28), own_mask(r0, c0, 28, 24))
            mk.report(model, pieces, os.path.join(out, model + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + model, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
