"""BRAINIAC's eye hatch in the floor (sheet 5 sprite 164, 2x2: the whole 24 x 28 cell, its floor's pattern included;
ground layer; enemy 525 of episode 4, 16 of them in BRAINIAC; its animation 164 162 160 160 160 162 162 162 162 164,
played when it fires (animate 2): the shutters slide apart on the red eye and shut again), polished (2026-10-22; it
replaces wave3_l.py's eye_hatch() and wave3_at_misc.py's eye_hatch_162 / eye_hatch_160, a sunk housing round a red
ball between two lids). models.cfg: model eye_hatch / eye_hatch_162 / eye_hatch_160 enemies/....glb origin; sprite 5
164 eye_hatch yaw=0 height=-4; frame 5 162 eye_hatch_162, frame 5 160 eye_hatch_160 (models drawn at their origin
stand at the ground enemies' layer, 4 pixels over the terrain: height=-4 sets the hatch on the floor, which
BRAINIAC's terrain keeps flat at 0).

Where it stands: every hatch is put exactly on a map tile (BRAINIAC's events 160-2008 and on: event 6 at the tile
columns 2, 3, 10, 11, 12, rows .04 down), and that tile is always tile 154 of the level's tileset ')', the hatch
blown open (its wreck: the shutters torn, black holes); the plain floor round it is tile 142 (a purple cross of arms
with grooves, a round pit in its middle where the arms meet, teal-grey corners). The sprite draws that floor too: its
corners, arms and grooves are tile 142's pixels; only the round pit (the circle of the floor's pit, columns 3-19 of
rows 5-21, centred at x -0.5, y 0.5, radius 8.5) and the shutter's slot above it (columns 10-13 of rows 2-4) are the
hatch's own: the model is the hatch alone, standing in the floor's pit (OWN below; the game's erasure for these
tiles, assets/terrain/33fc79a5b8f29c38.era, puts tile 142's floor back where the sprite and the wreck agree). No
other enemy, launched ones included, shows 164, 162 or 160; they are no other sprite's pixels mirrored, turned or in
other ramps (only each other: the same hatch, its shutters moved and its eye lit).

As the sprite and its 4x upscales draw it (columns and rows of the 24 x 28 cell; purples of ramp 5, reds of ramp 7):
the pit opened into a dark socket (0x50-0x52); down its sides curved slats, two each side (columns 5 and 7, 16 and 18,
lit 0x55-0x5c), as the ribs of a cage seen from above; in its middle a red eye (columns 7-16 of rows 10-16) under two
shutters that slide on a track down the middle: a narrow bar from the top (columns 10-13: lit rails 0x56 either side
of a dark channel 0x53, its tip lit 0x5a), coming out of a slot in the floor's groove (columns 10-13 of rows 2-4),
and a wider block from the bottom (columns 9-15 down to row 21: a dark face 0x52 under a lit top edge 0x57-0x59). In
164 the bar's tip is at row 11 and the block's top at row 14: one row of the eye between them, its dark reds
(0x70-0x72) showing either side; in 162 they are drawn back two rows each (the bar to row 9, the block to row 16), the
eye a lit red lens (0x72-0x78, its glint 0x78 at row 12); in 160 four rows each (rows 7 and 18), the eye whole
(0x71-0x7e: a white-hot glint along row 12, a hot band at row 14, its lower rim in shadow).

Built as such a hatch: a raised purple rim round the pit, rings lofted across it (its foot low where it meets the
floor, a rounded top 1.8 pixels up, a steep chamfer down into the socket; notched where the floor's grooves run into
the pit at its left, right and bottom; painted in bands of how it faces the game's sun, cut along smooth contours,
polish_orb_red.band_split: the outer slope at least the floor's purple, the chamfer dark at the upper left and lit at
the lower right, as the sprite's pit), the socket's dark floor inside it, the four slats lofted fins on that floor
(their tops lit), the eye a glossy dome on the socket's floor, painted in bands (rim, body, core, glint) of its frame's
reds glowing in their own colour (0.2-0.65: the game's bloom adds on top; BRAINIAC is dark, its models lit only by the
ship's lamp, so the eye's glow is what shows most); over the eye the shutters, bevelled boxes (polish_machine_kit): the
bar two rails with a lower plate between them and a crossbar at its tip, its far end in a small housing over the slot
(its mouth dark), the block a wedge whose face slopes down towards the bottom of the screen (dark, a lit strip along
its top edge as the sprite draws it), its foot tucked under the rim. The three frames are the same hatch with the
shutters at their places and the eye in their reds (FRAMES); their bounds are equal. Every mesh is triangulated before
the export (polish_k_pod.triangulate) and joined into one.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); origin at
the sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_l.py's eye_hatch() (its section "# --- 5 164: BRAINIAC's hatch with a red eye": the @model("eye_hatch",
164) function, and the eye_hatch line of its docstring) and wave3_at_misc.py's eye hatch (its section "# --- Sheet 5:
the eye hatch's lids": EYE, SOCKET_RY, eye_hatch(), HATCH and its lk.model loop, its docstring bullet, and with them
its wl = kit.quiet_import("wave3_l"), lk = wl.w, the del lk.MODELS[:] / del lk.WHOLES[:] lines and main()'s "if
lk.MODELS: lk.main()"): remove them so that they don't overwrite these models. wave3_l_art.py's HATCH and HATCH_OPEN
are read by nothing.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png, or the sheet
itself> (each frame's silhouette against the hatch's own pixels, OWN), --preview <prefix> (top and 3/4 views of each
frame), --only <name,...>, --stats 1 (each part's triangles).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import ccw  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

NAME, SPRITE = "eye_hatch", 164
SUN = Vector((-0.6, 0.6, 1.0)).normalized()      # towards the game's sun (from above and the top left)

# The hatch's own pixels ('#'): the floor's pit (the circle of radius 8.5 round x -0.5, y 0.5) and the shutter's slot
# above it; the floor round them (tile 142's arms, grooves and corners) is the map's: left out.
OWN = """
........................
........................
..........####..........
..........####..........
..........####..........
........#######.........
.......#########........
.....#############......
.....#############......
....###############.....
...#################....
...#################....
...#################....
...#################....
...#################....
...#################....
...#################....
....###############.....
.....#############......
.....#############......
.......#########........
........#######.........
........................
........................
........................
........................
........................
........................
"""

# --- The rim and the socket: ellipses round the pit's middle (semi-axes across, up the screen) ---------------------
PIT = (-0.4, 0.6)           # the socket's middle (the floor's circle: -0.5, 0.5; the upscale's oval a little higher)
OUTER = (8.7, 8.85)         # the rim's foot, where it meets the floor
INNER = (7.05, 7.2)         # the foot of its chamfer, on the socket's floor
RIM_TOP, FLOOR = 1.8, 0.3   # its top, the socket's floor
SKIRT = -0.6                # every solid reaches this far under the floor (the terrain's relief shows no gap)
# The rim's profile across it (u: 0 at its foot, 1 at the chamfer's foot; height), rings of RIM_SEGMENTS points.
RIM_PROFILE = [(0.0, 0.12), (0.11, 0.85), (0.24, 1.42), (0.37, 1.72), (0.5, RIM_TOP), (0.61, 1.72), (0.69, 1.5),
               (0.85, 0.9), (1.0, FLOOR)]
RIM_SEGMENTS = 120
# Where the floor's grooves (the arms' middles) run into the pit, notches across the rim: (angle, half width (degrees),
# depth): left, right, bottom (the top one is under the housing).
NOTCHES = [(180.0, 3.2, 0.75), (0.0, 3.2, 0.75), (270.0, 3.0, 0.75)]

# --- The slats down the socket's sides: (x at their middle, how far they bow out, from y, to y, height) -------------
SLATS = [(-4.6, 0.35, -4.4, 6.6, 1.0), (-6.55, 0.25, -2.4, 4.0, 0.75), (4.45, 0.35, -4.3, 6.4, 1.0),
         (6.4, 0.25, -1.6, 3.4, 0.75)]
SLAT_W = 0.72

# --- The eye: its middle (seen from above), radii, the dome's foot ---------------------------------------------------
EYE = (0.4, 0.5)
EYE_R = (4.75, 3.55, 1.45)
EYE_Z = FLOOR
CORE = ((0.5, 0.65), (3.3, 2.1))            # its core (middle, radii), a little above the middle
GLINT = ((0.5, 1.35), (2.5, 1.0))           # the glint across its upper middle (row 12)

# --- The shutters: the bar (x from, to; its far end, under the housing), the block (x from, to; its foot) -----------
BAR_X, BAR_END = (-2.0, 2.0), 10.8
BAR_Z = (1.85, 2.6)                          # its underside and top
BAR_RAIL = 0.95                              # the channel between the rails: |x| < this
HOUSING = (-2.35, 2.35, 9.25, 12.15, 3.0)   # the slot's housing: x, y from, to, top
MOUTH = (-1.55, 1.55, 1.6, 2.75)            # its mouth on its south face: x, z from, to
BLOCK_X, BLOCK_FOOT = (-3.0, 3.85), -7.4
BLOCK_TOP, BLOCK_FALL, BLOCK_UNDER = 2.55, 0.12, 1.45   # its top edge's height, its fall per pixel, its underside

# The frames: (bar's tip (y), block's top edge (y), the eye's materials: rim, body, core, glint as (palette index,
# emission strength)). 164: the bar's tip at row 11, the block's top at row 14; 162: rows 9 and 16; 160: rows 7 and 18.
FRAMES = {
    164: ("eye_hatch", 1.7, 0.0, ((0x71, 0.2), (0x72, 0.3), (0x73, 0.38), (0x74, 0.42))),
    162: ("eye_hatch_162", 3.7, -2.0, ((0x71, 0.2), (0x73, 0.3), (0x75, 0.42), (0x78, 0.55))),
    160: ("eye_hatch_160", 5.7, -4.0, ((0x72, 0.25), (0x75, 0.38), (0x77, 0.5), (0x7c, 0.65))),
}

PURPLES = {  # name: (palette index, metallic, roughness)
    "socket": (0x50, 0.15, 0.6), "dark": (0x52, 0.18, 0.5), "shadow": (0x53, 0.18, 0.48), "mid": (0x54, 0.18, 0.46),
    "plate": (0x56, 0.18, 0.44), "light": (0x58, 0.18, 0.42), "edge": (0x5a, 0.18, 0.4),
}


def materials(eye):
    pal = k.level_palette()
    m = {name: k.material(f"hatch_{name}", palette=index, metallic=metallic, roughness=roughness)
         for name, (index, metallic, roughness) in PURPLES.items()}
    for key, (index, glow) in zip(("eye_rim", "eye", "eye_core", "eye_glint"), eye):
        m[key] = k.material(f"hatch_{key}_{int(round(glow * 100))}", palette=index, metallic=0.0,
                            roughness=0.12 if key != "eye_rim" else 0.2, emission=pal[index], emission_strength=glow)
    return m


# --- Helpers ---------------------------------------------------------------------------------------------------------

def q(x, y, centre, radii):
    """The elliptical radius of (x, y): 1 on the ellipse."""
    return math.hypot((x - centre[0]) / radii[0], (y - centre[1]) / radii[1])


def vertex_normals(obj):
    mesh = obj.data
    normals = [Vector((0, 0, 0)) for _ in mesh.vertices]
    for poly in mesh.polygons:
        for v in poly.vertices:
            normals[v] += poly.normal * poly.area
    return [n.normalized() if n.length > 0 else Vector((0, 0, 1)) for n in normals]


# --- The rim, the socket, the slats ----------------------------------------------------------------------------------

def notch(angle):
    """How deep the notches cut the rim at an angle (degrees): 0 outside them."""
    depth = 0.0
    for a, half, d in NOTCHES:
        off = abs((angle - a + 180.0) % 360.0 - 180.0)
        depth = max(depth, d * smoothstep(half + 1.2, half, off))
    return depth


def rim_ring(u, z):
    """A ring across the rim (u: 0 at its foot, 1 at the chamfer's foot) at height z, lowered in the notches."""
    ax = OUTER[0] + (INNER[0] - OUTER[0]) * u
    ay = OUTER[1] + (INNER[1] - OUTER[1]) * u
    out = []
    for i in range(RIM_SEGMENTS):
        t = 2 * math.pi * i / RIM_SEGMENTS
        zz = z if z <= FLOOR + 0.05 else max(FLOOR + 0.05, z - notch(math.degrees(t)) * min(1.0, (z - FLOOR) / 0.6))
        out.append(Vector((PIT[0] + ax * math.cos(t), PIT[1] + ay * math.sin(t), zz)))
    return out


def faces_up(obj):
    """Turns an open surface's faces up (towards the camera)."""
    mesh = obj.data
    if sum(p.normal.z * p.area for p in mesh.polygons) < 0:
        mesh.flip_normals()
    return obj


def rim(m):
    """The raised rim round the pit: rings lofted across it from under the floor up to a rounded top and down a steep
    chamfer to the socket's floor (and on under it); purple in bands by how it faces the sun."""
    rings = [rim_ring(0.0, SKIRT)] + [rim_ring(u, z) for u, z in RIM_PROFILE] + [rim_ring(1.0, SKIRT)]
    obj = faces_up(k.loft("rim", rings, m["plate"], cap_start=False, cap_end=False))
    # The outer slope keeps at least the floor's purple (it reads as the floor's plate rising to the rim; only the
    # side towards the sun lighter), the chamfer down into the socket by how it faces the sun: dark at the upper
    # left, lit at the lower right, as the sprite's pit.
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        value = n.dot(SUN)
        values.append(max(value, 0.64) if across_rim(v.co) < 0.48 and v.co.z > FLOOR else value)
    band_split(obj, values, [(-9.0, m["dark"]), (0.3, m["mid"]), (0.62, m["plate"]), (0.86, m["light"])])
    faces_up(obj)

    def in_notch(c, n):  # the notches' floors and walls dark, as the floor's grooves
        angle = math.degrees(math.atan2((c.y - PIT[1]) / OUTER[1], (c.x - PIT[0]) / OUTER[0]))
        return m["shadow"] if notch(angle) > 0.3 and c.z > FLOOR + 0.1 and across_rim(c) < 0.75 else None
    mk.paint(obj, in_notch)
    return k.smooth(obj, 60)


def across_rim(c):
    """Where a point lies across the rim: 0 at its foot, 1 at the chamfer's foot."""
    qo, qi = q(c.x, c.y, PIT, OUTER), q(c.x, c.y, PIT, INNER)
    a, b = max(0.0, 1.0 - qo), max(0.0, qi - 1.0)
    return a / max(a + b, 1e-9)


def socket(m):
    """The socket's dark floor, a disc under the rim's chamfer at its edge, a little lower towards the middle."""
    def ring(scale, z):
        ax, ay = (INNER[0] + 0.5) * scale, (INNER[1] + 0.5) * scale
        return [Vector((PIT[0] + ax * math.cos(2 * math.pi * i / 64), PIT[1] + ay * math.sin(2 * math.pi * i / 64),
                        z)) for i in range(64)]
    obj = k.loft("socket", [ring(1.0, FLOOR), ring(0.62, FLOOR - 0.06)], m["socket"], cap_start=False,
                 end_point=(PIT[0], PIT[1], FLOOR - 0.12))
    return faces_up(k.smooth(obj, 80))


def slat(name, m, x_mid, bow, y0, y1, height):
    """A slat down the socket's side: a fin standing on its floor, bowing out towards the rim, its top rounded (lit
    where it faces the sun), lower towards its ends."""
    steps = 16
    rings = []
    for i in range(steps + 1):
        t = i / steps
        s = 2 * t - 1
        y = y0 + (y1 - y0) * t
        x = x_mid + math.copysign(bow, x_mid) * (1 - s * s)
        dx = math.copysign(bow, x_mid) * -4 * s / (y1 - y0) * 2   # the path's slope (dx/dy)
        side = Vector((1.0, -dx, 0.0)).normalized()
        taper = smoothstep(0.0, 0.2, t) * smoothstep(1.0, 0.8, t)
        top = FLOOR + 0.2 + (height - 0.2) * taper
        r = SLAT_W / 2
        ring = [Vector((x, y, FLOOR - 0.3)) - side * r]
        for j in range(7):
            a = math.pi * (1 - j / 6)
            ring.append(Vector((x, y, top - r * 0.8 + r * 0.8 * math.sin(a))) + side * (r * math.cos(a)))
        ring.append(Vector((x, y, FLOOR - 0.3)) + side * r)
        rings.append(ring)
    obj = k.loft(name, rings, m["mid"])
    k.smooth(obj, 70)
    mk.paint(obj, lambda c, n: m["light"] if n.dot(SUN) > 0.74 else m["plate"] if n.dot(SUN) > 0.45 else
             m["shadow"])
    return obj


# --- The eye ---------------------------------------------------------------------------------------------------------

def eye(m):
    """The red eye: a glossy dome on the socket's floor, its rim darkest, a hot core a little above its middle and a
    glint across its upper middle; its underside (under the socket's floor) removed."""
    cx, cy = EYE
    shape = Ellipsoid((cx, cy, EYE_Z - 0.35), (EYE_R[0], EYE_R[1], EYE_R[2] + 0.35))

    def radial(p, n):
        return q(p.x, p.y, EYE, EYE_R[:2])

    def core(p, n):
        return q(p.x, p.y, *CORE)

    def glint(p, n):
        return q(p.x, p.y, *GLINT)
    paint = [(radial, (0.8,), ("eye", "eye_rim")), (core, (1.0,), ("eye_core", None)),
             (glint, (1.0,), ("eye_glint", None))]
    obj = painted_ball("eye", shape, paint, m, subdivisions=4)
    mk.apply(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if max(v.co.z for v in f.verts) < FLOOR - 0.15], context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    return k.smooth(obj, 80)


# --- The shutters ----------------------------------------------------------------------------------------------------

def sun_pick(m, bands):
    """A paint picker by how a face faces the sun: bands [(lowest n.sun, material name)], ascending."""
    def pick(c, n):
        value = n.dot(SUN)
        name = bands[0][1]
        for low, key in bands:
            if value >= low:
                name = key
        return m[name]
    return pick


def bar(m, tip):
    """The bar from the top: two rails either side of a dark channel (a plate lower between them) and a crossbar at
    its tip, its edges lit, from the tip up into the housing over the slot; bevelled boxes."""
    x0, x1 = BAR_X
    z0, z1 = BAR_Z
    parts = [mk.box("bar_plate", x0 + 0.2, x1 - 0.2, tip + 0.3, BAR_END, z0, z1 - 0.26, m["shadow"]),
             mk.box("bar_rail_l", x0, -BAR_RAIL, tip, BAR_END, z0, z1, m["plate"]),
             mk.box("bar_rail_r", BAR_RAIL, x1, tip, BAR_END, z0, z1, m["plate"]),
             mk.box("bar_tip", x0, x1, tip, tip + 0.62, z0, z1, m["edge"])]
    for obj in parts:
        mk.bevel(obj, 0.16, 2, 30)
        mk.shade(obj, 35)
    mk.paint(parts[1], sun_pick(m, [(-9, "shadow"), (0.5, "plate"), (0.84, "light")]))
    mk.paint(parts[2], sun_pick(m, [(-9, "shadow"), (0.5, "plate"), (0.84, "light")]))
    mk.paint(parts[3], sun_pick(m, [(-9, "shadow"), (0.45, "edge")]))
    return parts


def housing(m):
    """The slot's housing over the floor's groove above the pit: a small bevelled block (in bands by how it faces the
    sun), its mouth on its south face dark (the bar slides in there)."""
    x0, x1, y0, y1, top = HOUSING
    obj = mk.box("housing", x0, x1, y0, y1, SKIRT, top, m["plate"])
    mk.bevel(obj, 0.5, 3, 30)
    mk.shade(obj, 35)
    mk.paint(obj, sun_pick(m, [(-9, "shadow"), (0.3, "mid"), (0.62, "plate"), (0.86, "light")]))
    mx0, mx1, mz0, mz1 = MOUTH
    mouth = mk.box("mouth", mx0, mx1, y0 - 0.06, y0 + 0.5, mz0, mz1, m["socket"])
    return [obj, mouth]


def block(m, top):
    """The block from the bottom: a wedge whose face slopes down towards the bottom of the screen (dark), bevelled,
    its top edge lit, its left edge lighter; its foot tucked under the rim (its outline cut by an ellipse just
    outside the chamfer's foot)."""
    x0, x1 = BLOCK_X
    foot = []
    for i in range(17):  # its foot along the ellipse
        x = x0 + (x1 - x0) * i / 16
        dx = (x - PIT[0]) / (INNER[0] + 0.45)
        foot.append((x, max(PIT[1] - (INNER[1] + 0.45) * math.sqrt(max(0.0, 1 - dx * dx)), BLOCK_FOOT)))
    outline = ccw(foot + [(x1, top), (x0, top)])
    z_top = BLOCK_TOP + BLOCK_FALL * top  # the track slopes: drawn back, the block lies lower
    obj = mk.wedge("block", outline, BLOCK_UNDER - 0.35, mk.plane((0.0, top, z_top), (1.0, top, z_top),
                                                                   (0.0, top - 1.0, z_top - BLOCK_FALL * 1.6)),
                   m["dark"])
    mk.bevel(obj, 0.34, 2, 30)
    bm = bmesh.new()  # its face split along the lit strip at its top edge
    bm.from_mesh(obj.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                           plane_co=(0.0, top - 0.5, 0.0), plane_no=(0.0, 1.0, 0.0))
    bm.to_mesh(obj.data)
    bm.free()
    mk.shade(obj, 35)

    def pick(c, n):
        if c.y > top - 0.5 and n.z > -0.2:   # its top edge (the strip the camera sees and the bevel beyond it)
            return m["edge"]
        if n.x < -0.3:
            return m["mid"]
        return m["dark"] if n.z > 0.5 else m["shadow"]
    mk.paint(obj, pick)
    return obj


# --- Build, checks, export -------------------------------------------------------------------------------------------

def build_hatch(frame, stats=False):
    name, tip, top, eye_mats = FRAMES[frame]
    m = materials(eye_mats)
    parts = [rim(m), socket(m)]
    for i, spec in enumerate(SLATS):
        parts.append(slat(f"slat{i}", m, *spec))
    parts.append(eye(m))
    parts += bar(m, tip)
    parts += housing(m)
    parts.append(block(m, top))
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    triangulate(parts)
    if stats:
        for part in parts:
            print("    %-10s %6d triangles" % (part.name, mk.triangles([part])))
    obj = join(parts, name)
    obj.data.name = name
    return obj


def own_mask():
    rows = [line for line in OWN.strip("\n").split("\n")]
    return [[ch == "#" for ch in line] for line in rows]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for frame, (name, *_rest) in FRAMES.items():
        if only and name not in only:
            continue
        k.reset()
        obj = build_hatch(frame, "stats" in options)
        if "check" in options:
            mk.compare("%s (5 %d)" % (name, frame), mk.coverage([obj], 24, 28), own_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])


if __name__ == "__main__":
    build()
