"""The slot of IXMUCANE's and SAWBLADES' upright rock wall: a red machine set into the wall between rock (sheet 8
sprites 277 above 203 above 241, 2x2 each: one 24 x 84 column, its pixels in rows 0-70; enemies 109 (277, animated:
277 279 281 165 281 279, the window brightening and dimming), 110 (203) and 111 (241, armour 0: it can't be shot); on
the sky, ground or top layer as the events put the wall), polished (2026-10-21; it replaces wave3_y_wall.py's slot
column and slot_machine(): a red block with a glowing box for a window on wave3_y_wall's bumpy heightfield rock).

The levels build the wall from columns of three sprites, 24 pixels apart (IXMUCANE's events 1820 (type 6) and 2120
(type 7), SAWBLADES' the same): a left end (169 / 207 / 245), a slot, one or three rock columns (167 / 205 / 243,
polish_ixm_wall_rock.py), a slot and a right end (161 / 199 / 237), the top sprites 56 pixels above the low ones. The
slot meets the left end on its left and the rock on its right, or the rock on its left and the right end on its right:
its edges have the section every column shares (wave3_y_wall.py's upright wall: its top level at HEIGHT 20 from the
cliff at y -16.5 back to its rounded back edge (y 22 at the top, 25.5 at the ground), the relief fading out within
polish_ixm_wall_rock.EDGE of the edges). None of these sprites is another sprite's pixels mirrored, turned or in other
ramps; no other enemy shows 277, 279, 281 or 165 (catalog.json).

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 84 column): sandstone either side (columns
0-4 and 17-23, tans of ramp 1: boulders on top (rows 0-44), ribs down the cliff (rows 45-70)), black seams at columns 5
and 16, and between them the machine (reds of ramp 7): on top (the top's row r stands at y 28 - r on the upright wall,
as polish_ixm_wall_rock maps it) a lip lit along the back (rows 5-8), the housing's top (rows 9-13), a window in a dark
frame (columns 8-14 of rows 14-24; the pane columns 9-13, glowing orange round its middle, brightening through the
frames to white-hot in 165), a plate (rows 25-28), a lit bar across (columns 9-14 of rows 29-31) with a lit stem down
from its left end (column 10, rows 32-44), a dark well left of the stem (columns 6-9) and a plate right of it, the
housing's right edge lit (column 16 of rows 24-35); down the cliff (the cliff's row r at height 20 (70.5 - r) / 26) four
bars of a grille over a dark well (rows 45, 47, 49 and 51), then a foot flaring to the left (rows 53-60), its lower edge
lit; under the foot (rows 62-70) nothing: the slot is open there, dark.

Built as the rock column is built (polish_ixm_wall_rock's fields() and solid() with this column's own rock pixels, ART:
weathered layered sandstone, a bed of cobbles on top, ribs down the cliff, the bedding's grooves; its surface by
surface nets, its colours the sprite's own shades under each face, reduced to ROCK_SHADES; pieces decimated with
their cut edges kept, shaded as the dense whole), the slot cut out of it (CHANNEL, its edges rounded), and the machine
standing in it with a gap either side (the black seams, dark fillers in them): CAD-like solids (polish_machine_kit) in
reds: the housing level with the rock's top, grooves across it behind and under the window, its back lip a lit bar,
the window's frame raised round a sunk pane with a hot core, the bar (glowing a little, as the lip) and the stem
raised, the well sunk; on the cliff the grille's bars over their dark well and the foot; under the foot the housing
stands back (a dark hollow). The window's light is its frame models': ixm_wall_slot_top (277), _279, _281 and _165
(the same geometry, the pane's and the core's materials changed; emission 0.25-0.65, under 1: the bloom and the glow
halo add to it).

The pieces are cut as the sprites own the wall, not along their boxes: what the top sprite draws (the top from its back
edge down to row 28: y above Y_CUT) is the top piece, the rest of the top and the cliff down to row 56 (z above Z_CUT)
the middle piece, the cliff below that the low piece (with the column's foot behind the cliff); so the window (drawn
in 277) lies in the top piece and its frames light it, and when the shot pieces die the unshootable low piece stays as
the 2D game leaves the cliff's foot: a low stump of the wall, not a thin slab of cliff. (Box cuts at y 14 and -14 put
the window into the middle piece: wave3_y_wall.py's.) The damaged pieces (polish_ixm_wall_slot_dmg.py) are cut the same
way. Each piece is drawn at its sprite's centre (origin): the top piece's parts lie 3 to 28 pixels below its origin,
the low piece's reach 54 pixels above its own (all of it behind or under the other pieces). The cuts keep the faces'
winding and the whole's shading (polish_savara_boss.cut's way, planes instead of a box); every mesh is triangulated
before export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the column's whole
as polish_ixm_wall_rock's: x -12..12 (column c's left edge at x c - 12), the middle piece's centre at y 0, the top
piece's at y 28, the low piece's at y -28.

models.cfg (the model lines and the sprite lines stay): add model ixm_wall_slot_top_279
enemies/ixm_wall_slot_top_279.glb origin (likewise _281 and _165) and frame 8 279 ixm_wall_slot_top_279, frame 8 281
ixm_wall_slot_top_281, frame 8 165 ixm_wall_slot_top_165; sprite 8 277 ixm_wall_slot_top yaw=0
glow=16:0.3:122:-1:18.6, sprite 8 203 ixm_wall_slot_mid yaw=0 and sprite 8 241 ixm_wall_slot_low yaw=0 unchanged.

Replaces wave3_y_wall.py's slot pieces: in its PIECES loop skip the slot column too (if _name in ("rock", "slot"):
continue), so that it no longer exports ixm_wall_slot_top / _mid / _low; drop slot_machine() and its call in
build_wall() (it lies inside the slot column: the end columns' pieces don't change), SLOT_HOT (unused; and
wave3_y_art.py's SLOT_HOT, which only it reads) and the slot lines of its docstring. Keep the slot column in COLUMNS,
build_wall() and is_slot(), as the rock column is kept: the end columns' pieces keep their overlap with its rock.
wave3_ap_ixm.py (the old damaged slot, built from wave3_y_wall's build_wall(stand=False), its slot parts and PIECES)
goes too: polish_ixm_wall_slot_dmg.py replaces it.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole column's top view
against the sprites' top rows as the upright wall lays them out), --preview <prefix> (each model's top and 3/4 view,
the whole's), --only <model,...>.
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_ixm_wall_rock as rw  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_rock_arch import face_data, finish_whole, mesh_object, smax, surface_nets  # noqa: E402

# The rock's pixels of the slot column (8 277 above 203 above 241, rows 0-69): each its shade in ramp 1 (palette
# index 0x10 + digit; 0 also for the near-black seams and clefts of ramp 0), '.' none (and the machine, columns 5-16).
ART = """
..00..............000...
.0780............07640..
08a96............6bb840.
88d85............8bba740
8dc65............8bb7624
8a638............8b97645
6642c............6777568
7315b............2366488
85038............4345579
95425............9438967
66853............2589997
89882............3899aaa
99885............689aaa8
88876............4787777
88776............4677777
77776............3367777
77766............4345677
77568............3653356
54479............4666325
6558a............6787736
66599............8888757
77345............7887667
87644............4766668
98874............5455379
aa986............843358b
99998............87657ab
98899............8877599
88888............8886568
88888............8886568
88888............8876548
88887............8866547
88766............8766545
87666............7666535
66665............6666535
56654............6666445
35647............6663356
54648............6642477
64446............6416988
76633............3169a88
87721............6259bc9
98516............9649bb7
7613b............b846765
6408c............a942455
6319c............7741255
6327a............4652155
63279............1453055
54145............2010013
54124............6300355
55323............6642465
65442............6643595
a5420............64424a5
b5410............44413a5
95400............4430285
95400............4520185
95301............4510165
85302............5601265
75302............5601365
76302............6502265
66302............7202255
65302............6002245
55302............4023245
55302............0023235
55102............0124115
54202............0234103
54102............1334112
50001............2335212
000..............2335200
0................335510.
.................045300.
..................0500..
"""

# The pieces: (name, sprite in each frame of the top's animation, the half-spaces it keeps: (point, outward normal)),
# and its sprite's centre (y). The top piece is what 277 draws (the top above row 28), the middle piece the rest of the
# top and the cliff down to row 56, the low piece the cliff below.
Y_CUT = 28.0 - 28.0          # the top's row 28 on the upright wall
Z_CUT = 20.0 * (70.5 - 56.0) / 26.0   # the cliff's row 56
PIECES = [("ixm_wall_slot_top", (277, 279, 281, 165), [((0, Y_CUT, 0), (0, -1, 0)), ((0, 0, Z_CUT), (0, 0, -1))], 28.0),
          ("ixm_wall_slot_mid", (203,), [((0, Y_CUT, 0), (0, 1, 0)), ((0, 0, Z_CUT), (0, 0, -1))], 0.0),
          ("ixm_wall_slot_low", (241,), [((0, 0, Z_CUT), (0, 0, 1))], -28.0)]
SIDES = [((-12.0, 0, 0), (-1, 0, 0)), ((12.0, 0, 0), (1, 0, 0))]   # every piece: the column's edges

# The slot cut out of the rock (x), its edges rounded; the machine in it (x), a gap either side (the black seams).
CHANNEL, CHANNEL_ROUND = (-7.0, 5.0), 0.35
MX = (-6.35, 4.35)
HEIGHT, CLIFF = rw.HEIGHT, rw.CLIFF
SKIRT = -2.0
TOP = HEIGHT + 0.55          # the machine's top (the rock's top plane is HEIGHT, its cobbles stand up to 2 over it)
BACK_Y = 23.6                # the housing's back (the top's row 4.4)
FOOT_Z = 20.0 * (70.5 - 61.0) / 26.0   # the foot's lower edge (the cliff's row 61); under it the housing stands back
HOLLOW = 3.0                 # how far the housing stands back under the foot (a dark hollow)
SEAM_DEPTH = 2.6             # how far under the rock's top the seams' dark fillers stand


def TR(r):
    """The top's row r (pixel edge) on the upright wall: y."""
    return 28.0 - r


def CR(r):
    """The cliff's row r (pixel edge): z."""
    return HEIGHT * (70.5 - r) / 26.0


def XC(c):
    """Column c's left edge: x."""
    return c - 12.0


# The machine's parts (columns and rows are pixel edges of the 24 x 84 column).
LIP = (5.4, 8.0, 0.95)                        # the lit lip along the back: rows, radius
WINDOW = (8.0, 15.0, 13.6, 24.6)               # the frame (columns, rows)
PANE = (9.0, 14.0, 14.4, 23.8)                 # the pane in it
FRAME_H, PANE_D = 0.55, 0.5                    # the frame stands up, the pane sits down
CORE = (11.5, 18.6, 1.5, 2.5)                  # the pane's hot core: middle (column, row), radii (across, along)
GROOVES = [(8.4, 9.0), (24.6, 25.4)]           # grooves across the housing's top (rows): behind the window, under it
GROOVE_D = 0.4
BAR = (9.0, 15.0, 29.0, 31.6, 0.5)            # the lit bar across (columns, rows, height)
STEM = (10.0, 11.0, 31.4, 44.4, 0.42)          # the lit stem down from its left end
WELL = (6.0, 9.6, 32.4, 44.6, 2.2)             # the dark well left of the stem (columns, rows, depth)
EDGE_LIT = (24.0, 36.0)                         # the housing's right edge lit (rows)
GRILLE = [(45.0, 46.0, 6.0, 16.0), (47.0, 48.0, 6.0, 16.0), (49.0, 50.0, 6.0, 16.0), (51.0, 52.0, 7.0, 15.0)]
GRILLE_WELL = (5.6, 16.4, 44.8, 52.6, 1.1)     # the dark well behind the bars (columns, cliff rows, depth)
BAR_OUT = 0.65                                  # how far the grille's bars stand out of the cliff
FOOT = [(9.0, 53.0), (16.0, 53.0), (16.0, 60.6), (6.0, 60.6), (6.0, 57.0)]   # the foot (columns, cliff rows)
FOOT_OUT = 0.85

# The window's light in each frame: (pane: palette index, emission), (core: palette index, emission).
WINDOW_LIGHT = {277: ((0x78, 0.25), (0x7b, 0.4)), 279: ((0x7a, 0.35), (0x7e, 0.5)),
                281: ((0x7c, 0.45), (0x7f, 0.6)), 165: ((0x7e, 0.55), (0x7f, 0.65))}

# The rock's shades in these pieces (the rock column's, polish_ixm_wall_rock.shades, each moved to the nearest of these:
# the pieces hold the machine's materials too, fifteen at most); the seams' walls (the gap either side) darkest.
ROCK_SHADES = [0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1b]
SEAM_SHADE = 0x13
TARGET = 4200                # the rock's triangles per piece (fewer where the piece holds less rock)
WHOLE_TARGET = 26000


def materials():
    pal = k.level_palette()

    def red(name, index, rough=0.36, metallic=0.35, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=rough, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=rough)
    m = {
        "dark": red("slot_dark", 0x70, 0.8, 0.0),
        "red": red("slot_red", 0x74),
        "lit": red("slot_lit", 0x76, 0.32),
        "lip": red("slot_lip", 0x79, 0.3, 0.2, 0.15),
        "rock": rw.materials(),
    }
    for f, ((pi, ps), (ci, cs)) in WINDOW_LIGHT.items():
        m[f"pane{f}"] = red(f"slot_pane{f}", pi, 0.2, 0.0, ps)
        m[f"core{f}"] = red(f"slot_core{f}", ci, 0.2, 0.0, cs)
    return m


# --- The rock -------------------------------------------------------------------------------------------------------

def art(text=None):
    rows = (text or ART).strip("\n").split("\n")
    out = np.full((len(rows), 24), np.nan)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                out[r, c] = int(ch, 16)
    return out


def rock_whole(text=None):
    """The column's rock (polish_ixm_wall_rock's solid from this column's pixels, ART or text), the slot cut out."""
    shade = art(text)
    boulders, ribs, s_top, s_face = rw.fields(shade)
    d = rw.solid(boulders, ribs)
    x = rw.XS[:, None, None].astype(np.float32)
    channel = np.maximum(CHANNEL[0] - x, x - CHANNEL[1]) + np.zeros_like(d)    # negative inside the slot
    d = smax(d, -channel, CHANNEL_ROUND).astype(np.float32)
    verts, quads = surface_nets(d, (rw.X0, rw.Y0, rw.Z0), rw.STEP)
    whole = finish_whole(mesh_object("rock_whole", verts, quads))
    print("rock: %d vertices, %d triangles" % (len(whole.data.vertices), len(whole.data.polygons)))
    return whole, s_top, s_face


def rock_indices(obj, s_top, s_face):
    """Each face's palette index: the rock column's shades, moved to the nearest of ROCK_SHADES; the slot's walls
    dark."""
    centres, normals = face_data(obj)
    idx = rw.shades(centres, normals, s_top, s_face)
    choices = np.array(ROCK_SHADES)
    idx = choices[np.argmin(np.abs(idx[:, None] - choices[None, :]), axis=1)]
    x = centres[:, 0]
    seam = (np.abs(normals[:, 0]) > 0.6) & (((x > CHANNEL[0] - 0.8) & (x < CHANNEL[0] + 0.4)) |
                                           ((x > CHANNEL[1] - 0.4) & (x < CHANNEL[1] + 0.8)))
    return np.where(seam, SEAM_SHADE, idx)


# --- The machine ----------------------------------------------------------------------------------------------------

def red_pick(m, top_mat=None):
    """Reds by the faces' turn: tops as they are (or top_mat), edges facing the light lit, walls dark."""
    light = Vector((-0.45, 0.45, 0.77)).normalized()

    def pick(c, n):
        if n.z > 0.95:
            return top_mat
        if n.z > 0.3:
            return m["lit"] if n.dot(light) > 0.75 else m["red"]
        if n.y < -0.9:
            return None                       # the front on the cliff keeps its own
        return m["dark"]
    return pick


def finish(obj, width, segments=2, angle=35.0):
    mk.cleanup(obj)
    mk.bevel(obj, width, segments, angle)
    mk.shade(obj, 35)
    return obj


def housing(m):
    """The housing: level with the rock's top, flush with the cliff down to the foot, standing back under it; the well
    cut into its top left of the stem, the dark well behind the grille cut into its front."""
    x0, x1 = MX
    body = mk.box("housing", x0, x1, CLIFF, BACK_Y, SKIRT, TOP, m["red"])
    mk.boolean(body, mk.box("hollow", x0 - 1, x1 + 1, CLIFF - 2, CLIFF + HOLLOW, SKIRT - 1, FOOT_Z), "DIFFERENCE")
    c0, c1, r0, r1, depth = WELL
    mk.boolean(body, mk.box("well", XC(c0), XC(c1), TR(r1), TR(r0), TOP - depth, TOP + 2), "DIFFERENCE")
    for i, (r0, r1) in enumerate(GROOVES):
        mk.boolean(body, mk.box(f"groove{i}", x0 - 1, x1 + 1, TR(r1), TR(r0), TOP - GROOVE_D, TOP + 2), "DIFFERENCE")
    c0, c1, r0, r1, depth = GRILLE_WELL
    mk.boolean(body, mk.box("grille_well", XC(c0), XC(c1), CLIFF - 1, CLIFF + depth, CR(r1), CR(r0)), "DIFFERENCE")
    finish(body, 0.3)
    e0, e1 = TR(EDGE_LIT[1]), TR(EDGE_LIT[0])
    wells = [(XC(WELL[0]) - 0.05, XC(WELL[1]) + 0.05, TR(WELL[3]) - 0.05, TR(WELL[2]) + 0.05)]

    def pick(c, n):
        for a, b, ya, yb in wells:
            if a < c.x < b and ya < c.y < yb and c.z < TOP - 0.2:
                return m["dark"]
        if c.y < CLIFF + GRILLE_WELL[4] + 0.05 and CR(GRILLE_WELL[3]) - 0.05 < c.z < CR(GRILLE_WELL[2]) + 0.05 and \
                XC(GRILLE_WELL[0]) - 0.05 < c.x < XC(GRILLE_WELL[1]) + 0.05:
            return m["dark"]                  # the well behind the grille
        if c.z < FOOT_Z + 0.05 and c.y < CLIFF + HOLLOW + 0.1:
            return m["dark"]                  # the hollow under the foot
        if n.x > 0.5 and n.z > 0.2 and e0 < c.y < e1:
            return m["lit"]                   # the right edge lit as the sprite draws it
        if n.y < -0.9:
            return m["dark"]                  # its front on the cliff, in shade
        return red_pick(m)(c, n)
    mk.paint(body, pick)
    return body


def lip(m):
    x0, x1 = MX
    r0, r1, rad = LIP
    y = (TR(r0) + TR(r1)) / 2
    pts = [(x0 + 0.3, y, TOP + 0.15), (x1 - 0.3, y, TOP + 0.15)]
    bar = mk.tube("lip", pts, rad, m["lip"], 14)
    k.smooth(bar, 60)
    mk.paint(bar, lambda c, n: m["red"] if n.z < -0.1 or n.y < -0.6 else None)
    return bar


def window(m):
    """The window: its frame standing up, the pane sunk in it, the hot core (both repainted in each frame's light)."""
    c0, c1, r0, r1 = WINDOW
    frame = mk.box("window_frame", XC(c0), XC(c1), TR(r1), TR(r0), TOP - 0.5, TOP + FRAME_H, m["dark"])
    p0, p1, q0, q1 = PANE
    mk.boolean(frame, mk.box("pane_cut", XC(p0), XC(p1), TR(q1), TR(q0), TOP + FRAME_H - PANE_D - 0.3, TOP + 3),
               "DIFFERENCE")
    finish(frame, 0.18, 2)
    mk.paint(frame, lambda c, n: m["lit"] if (n.z > 0.3 and n.z < 0.95 and n.x < -0.3) else None)
    zp = TOP + FRAME_H - PANE_D
    pane = mk.box("pane", XC(p0) + 0.02, XC(p1) - 0.02, TR(q1) + 0.02, TR(q0) - 0.02, zp - 0.4, zp, m["pane277"])
    (cc, cr), ra, rb = CORE[:2], CORE[2], CORE[3]
    cx, cy = XC(cc), TR(cr)
    pts = [(cx + ra * math.cos(2 * math.pi * j / 24), cy + rb * math.sin(2 * math.pi * j / 24)) for j in range(24)]
    core = mk.prism("core", pts, zp - 0.3, zp + 0.06, m["core277"])
    k.smooth(core, 30)
    return [frame, pane, core]


def bar_and_stem(m):
    parts = []
    for name, (c0, c1, r0, r1, h), mat in (("bar", BAR, m["lip"]), ("stem", STEM, m["lit"])):
        obj = mk.box(name, XC(c0), XC(c1), TR(r1), TR(r0), TOP - 0.5, TOP + h, mat)
        finish(obj, 0.16, 2)
        mk.paint(obj, lambda c, n: m["red"] if (n.z < 0.3 and n.dot(Vector((-1, 1, 0))) < 0) else None)
        parts.append(obj)
    return parts


def grille_and_foot(m):
    """The grille's bars across the dark well on the cliff, the foot under them (its lower edge lit)."""
    parts = []
    for i, (r0, r1, c0, c1) in enumerate(GRILLE):
        z0, z1 = CR(r1), CR(r0)
        bar = mk.box(f"grille{i}", XC(c0), XC(c1), CLIFF - BAR_OUT, CLIFF + GRILLE_WELL[4] + 0.2, z0 + 0.05, z1 - 0.05,
                     m["red"])
        finish(bar, 0.2, 2)
        mk.paint(bar, lambda c, n: m["lit"] if n.z > 0.5 else m["red"] if n.y < -0.5 else m["dark"])
        parts.append(bar)
    outline = [(XC(c), CR(r)) for c, r in FOOT]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))
    if area < 0:
        outline = outline[::-1]
    foot = mk.prism("foot", outline, CLIFF - FOOT_OUT, CLIFF + 0.6, m["red"], axis="y")
    finish(foot, 0.25, 2)
    mk.paint(foot, lambda c, n: m["lit"] if (n.z > 0.5 or (n.z > 0.2 and c.z < CR(57.5))) else
             m["dark"] if n.z < -0.3 else None)
    parts.append(foot)
    return parts


def seams(m):
    """The black seams either side of the machine: dark fillers in the gaps between it and the rock, SEAM_DEPTH under
    the rock's top, standing back a little from the cliff."""
    parts = []
    for i, (a, b) in enumerate(((CHANNEL[0] - 0.3, MX[0] + 0.05), (MX[1] - 0.05, CHANNEL[1] + 0.3))):
        parts.append(mk.box(f"seam{i}", a, b, CLIFF + 0.5, BACK_Y - 0.3, SKIRT, HEIGHT - SEAM_DEPTH, m["dark"]))
    return parts


def machine(m):
    parts = [housing(m), lip(m)] + window(m) + bar_and_stem(m) + grille_and_foot(m) + seams(m)
    for obj in parts:
        mk.apply(obj)
    return parts


# --- Cutting --------------------------------------------------------------------------------------------------------

def cut_planes(source, planes, cap_mat, name):
    """The part of an object on the inner side of every plane (point, outward normal), its cuts capped with cap_mat
    (flat, facing out of their cut), the faces' winding kept, its normals the uncut object's. Returns the object and
    the indices of its vertices on the cuts, or (None, set())."""
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    for co, no in planes:
        if not bm.faces:
            break
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                     plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    caps.add(f)
    caps = {f for f in caps if f.is_valid}
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None, set()

    def on_plane(v):
        return any(abs((v - Vector(co)).dot(Vector(no))) < 1e-4 for co, no in planes)
    for f in caps:
        f.material_index = cap_index
        f.smooth = False
    bm.normal_update()
    bm.verts.index_update()
    bm.faces.index_update()
    rim = {v.index for v in bm.verts if on_plane(v.co)}
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj, rim


def rock_piece(coarse, shading, planes, name, mats, s_top, s_face, share, target=TARGET):
    """The rock of one piece: cut from the reduced whole, decimated (its cut edges kept), shaded as the dense whole,
    painted."""
    obj, rim = cut_planes(coarse, planes, mats[rw.CAP], name)
    if obj is None:
        return None
    # The caps: slot 1 (the whole's faces slot 0; polish_ixm_wall_rock.shade_like keeps the caps flat).
    cap_slot = mk.slot_of(obj, mats[rw.CAP])
    flags = [1 if p.material_index == cap_slot else 0 for p in obj.data.polygons]
    obj.data.polygons.foreach_set("material_index", flags)
    rw.decimate(obj, rim, int(target * min(1.0, max(0.3, share))))
    rw.shade_like(obj, shading)
    indices = rock_indices(obj, s_top, s_face)
    caps = np.empty(len(obj.data.polygons), np.int64)
    obj.data.polygons.foreach_get("material_index", caps)
    indices[caps == 1] = rw.CAP
    rw.assign(obj, indices, mats)
    return obj


# --- Build ----------------------------------------------------------------------------------------------------------

def top_mask(sheet):
    """The column's top view as the upright wall lays out its sprites' pixels: the top's rows 0-44 at y 28 - r (rows
    14-58 of a 24 x 84 frame round y 0), the cliff's ribs standing out two rows below that."""
    full = k.sprite_mask(sheet, 277) + k.sprite_mask(sheet, 203) + k.sprite_mask(sheet, 241)
    rows = [[False] * 24 for _ in range(84)]
    for r in range(45):
        rows[14 + r] = list(full[r])
    for extra in (59, 60):
        rows[extra] = [full[44][c] and (c < 5 or c > 16) for c in range(24)]
    # Only the wall's footprint (polish_ixm_wall_rock.piece_mask's: the cliff's ribs to its back's foot).
    for row in range(84):
        yc = 42.0 - (row + 0.5)
        if not CLIFF - 2.5 <= yc <= rw.BACK[0] + rw.BACK[1]:
            rows[row] = [False] * 24
    return rows


def prepare(m, text=None):
    """The rock: the dense whole (its shading), a reduced copy to cut the pieces from, the sprite's fields."""
    whole, s_top, s_face = rock_whole(text)
    shading = mk.NormalSource(whole)
    coarse = whole.copy()
    coarse.data = whole.data.copy()
    bpy.context.scene.collection.objects.link(coarse)
    rw.decimate(coarse, set(), WHOLE_TARGET)
    coarse.data.materials.append(m["rock"][0x18])     # slot 0: the rock (the cuts' caps get slot 1)
    whole.hide_render = True
    return coarse, shading, s_top, s_face


def export_pieces(options, m, rock, parts, pieces, suffix="", light=None, target=TARGET):
    """Cuts the rock and the machine's parts into the pieces (PIECES' half-spaces and the column's sides), each model
    the rock and the parts of a piece joined, moved so its sprite's centre is its origin; light(objects, frame) gives
    the parts a frame's light (the top piece's frames), None: the first sprite only."""
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    coarse, shading, s_top, s_face = rock
    for name, sprites, keep, centre in pieces:
        planes = SIDES + keep
        base = name + suffix
        cut_rock = rock_piece(coarse, shading, planes, base + "_rock", m["rock"], s_top, s_face,
                              1.0 if name.endswith("mid") else 0.6, target)
        cut_parts = [p for p in (cut_planes(src, planes, m["dark"], src.name + "_cut")[0] for src in parts) if p]
        for frame in (sprites if light else sprites[:1]):
            model = base if frame == sprites[0] else "%s_%d" % (base, frame)
            if only and model not in only and base not in only:
                continue
            if light:
                light(cut_parts, frame)
            copies = []
            for obj in ([cut_rock] if cut_rock else []) + cut_parts:
                c = obj.copy()
                c.data = obj.data.copy()
                bpy.context.scene.collection.objects.link(c)
                copies.append(c)
            mk.transform(copies, Matrix.Translation((0.0, -centre, 0.0)))
            triangulate(copies)
            piece = join(copies, model)
            bpy.context.view_layer.update()
            hidden = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj is not piece]
            states = [obj.hide_render for obj in hidden]
            for obj in hidden:
                obj.hide_render = True
            mk.report(model, [piece], os.path.join(out, model + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + model, [piece])
            bpy.data.objects.remove(piece)
            for obj, state in zip(hidden, states):
                obj.hide_render = state
        for obj in cut_parts + ([cut_rock] if cut_rock else []):
            bpy.data.objects.remove(obj)


def window_light(m):
    """light() for export_pieces: the pane's and the core's materials of a frame."""
    def light(objects, frame):
        for obj in objects:
            for i, mat in enumerate(obj.data.materials):
                if mat is not None and mat.name.startswith(("slot_pane", "slot_core")):
                    kind = "pane" if mat.name.startswith("slot_pane") else "core"
                    obj.data.materials[i] = m[f"{kind}{frame}"]
    return light


def build():
    options = k.args()
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    t0 = time.time()
    rock = prepare(m)
    coarse = rock[0]
    parts = machine(m)
    print("whole: rock %d triangles, machine %d (%.1f s)" % (len(coarse.data.polygons), mk.triangles(parts),
                                                            time.time() - t0))
    if "check" in options:
        mk.compare("whole slot column (8 277 above 203 above 241, the top's pixels as the upright wall lays them out)",
                   mk.coverage([coarse] + parts, 24, 84), top_mask(os.path.join(options["check"], "enemy_8.png")))
    if "preview" in options:
        mk.preview(options["preview"] + "ixm_wall_slot_whole", [coarse] + parts, size=(24, 84), scale=8, distance=2.0)
    export_pieces(options, m, rock, parts, PIECES, light=window_light(m))


if __name__ == "__main__":
    build()
