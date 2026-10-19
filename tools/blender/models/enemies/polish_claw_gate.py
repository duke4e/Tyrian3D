"""The armoured claw gate of APPROACH and BRAINIAC (episode 4): sheet 5 sprites 85 (the left half) and 87 (the right
half), 2x2 each: one 48 x 28 picture; ground layer (the levels' ground2 slots); enemies 522 and 523; one frame each),
polished (2026-10-19; it replaces wave1_c.py's claw_gate(), reliefs inflated from letter-drawn outlines). models.cfg:
model claw_gate_left / claw_gate_right ... origin; sprite 5 85 claw_gate_left yaw=0 height=-4, sprite 5 87
claw_gate_right yaw=0 height=-4. The levels put the halves side by side: 522 (85) at x and 523 (87) at x + 24, at the
same y (APPROACH's events 124-1270, BRAINIAC's 168-5620).

87 is 85 mirrored: its pixels are 85's flipped left to right one pixel over (column c of the picture is column 48 - c;
two pixels differ), only re-shaded for the light from the left; so the gate is symmetric about the middle of the
picture's column 24 (x = 0.5 here): the left half is built and mirrored, the parts across the middle (the red arc
below, the red pin above) are built whole.

As the sprite and its 4x upscale draw the left half (columns and rows of the picture): an armoured tower (columns
3-12 of rows 1-11), its top-left corner cut away, a raised strap across its top like a T (down column 9 from row 2,
across row 6, down its inner side, column 12), its front sloping down to a lit ledge (row 10) with two red eyes in
the slope (columns 7 and 10 of row 8); in front of it (down the screen) its leg (columns 4-12 of rows 12-19), a
groove down it (column 9), the strap running on down its inner side to a foot; under the leg a red claw hooking
down to the ground (columns 5-10 of rows 20-24). Inward of the tower a beam (columns 13-16 of rows 3-7, dark
machinery and a small blue lamp under it) to the inner pylon: a grey cap like a barrel vault (columns 17-22 of rows
1-7, its crest lit down column 19), a red fang hanging from its front (columns 18-20 of rows 8-13, salmon down its
middle) and a thin strut on down (column 20 of rows 14-19) to the red arc that joins the two halves below (rows
20-25 from column 19 to column 29), a red pin joining the caps above (column 24 of rows 3-4). Between them, under the
arch, the ground shows.

Built as a CAD modeller would (polish_machine_kit): the tower is its plan and its side profile extruded and
intersected, bevelled; the cap a vault section extruded down the screen; the straps, the beam, the legs boxes and
wedges; the fang and the claw lofted, the arc and the strut swept. The whole gate is then cut along the sprites'
edge (x = 0; polish_arch.py's cut(): the pieces keep the whole's shading across the cut), each piece moved so its
sprite's centre is its origin.

Where it stands: models drawn at their origin stand at the ground enemies' layer, about 4 pixels above the terrain;
"height=-4" on the sprite lines sets the gate on the ground (its base reaches SKIRT below z = 0).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the edge between the two sprites at their middle (column c of the picture is x = c + 0.5 - 24,
row r is y = 13.5 - r).

Replaces wave1_c.py's claw gate: remove GATE_LEFT, GATE_RIGHT, claw_gate(), claw_gate_left(), claw_gate_right(), the
"claw_gate_left" and "claw_gate_right" entries of MODELS and the gate's lines of its docstring, so that it doesn't
overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each half against enemy_5.png), --preview <prefix>.
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


def XE(c):
    """The left edge of the picture's column c (fractions allowed)."""
    return c - 24.0


def YE(r):
    """The top edge of the picture's row r."""
    return 14.0 - r


def P(c, r):
    return (XE(c), YE(r))


AXIS_X = 0.5                    # the gate is symmetric about x = AXIS_X (the middle of the picture's column 24)
SKIRT = 1.5                     # how far the base reaches below the ground (z = 0)
PIECES = [("claw_gate_left", 85, (-24.0, 0.0, -14.0, 14.0)), ("claw_gate_right", 87, (0.0, 24.0, -14.0, 14.0))]

# --- The left half's measures (the right half is their mirror image) -------------------------------------------
# The tower: its plan (the top-left corner cut away) and its side profile (y, z): the flat top, the slope down the
# screen to the lit ledge, the ledge's front edge.
TOWER_PLAN = [P(8.7, 1.45), P(12.75, 1.45), P(12.75, 11.4), P(2.45, 11.4), P(2.45, 7.3), P(3.45, 6.6), P(3.45, 3.9),
              P(5.0, 2.45)]
TOP_Z, SLOPE_FOOT, LEDGE_Z = 10.6, (YE(9.6), 8.4), 8.1
TOWER_PROFILE = [(YE(1.2), -SKIRT), (YE(1.2), TOP_Z), (YE(6.6), TOP_Z), (SLOPE_FOOT[0], SLOPE_FOOT[1]),
                 (YE(9.8), LEDGE_Z), (YE(11.4), LEDGE_Z), (YE(11.4), -SKIRT)]
STRAP_UP = 0.42                 # how far the straps stand above the surface they lie on
STRAP_SPINE = (XE(9.0), XE(10.05), YE(6.7), YE(1.75))     # down the top (column 9)
STRAP_CROSS = (XE(9.0), XE(12.75), YE(6.75), YE(5.85))    # across (row 6)
STRAP_SIDE = (XE(11.75), XE(12.85))                       # down the inner side (column 12), on over the leg
EYES = [(XE(7.5), YE(8.5)), (XE(10.5), YE(8.5))]          # the two red eyes in the slope (columns 7 and 10, row 8)
EYE_R = 0.62
# The leg: the outer block (columns 4-8) and the inner strap block (columns 10-12), the groove between them.
LEG_OUTER = (XE(4.55), XE(9.25), YE(19.3), YE(10.6), 6.4, 4.4)      # x0, x1, y0, y1, top at the back, at the front
LEG_INNER = (XE(9.75), XE(12.85), YE(20.3), YE(10.6), 6.8, 4.8)
LEG_FOOT = (XE(9.0), XE(12.9), YE(20.9), YE(17.2), 4.2)            # the inner block's foot, wider
# The claw: its path (x, y, z, radius) from under the leg's foot down to its tip.
CLAW = [(XE(7.3), YE(18.4), 4.0, 1.75), (XE(7.4), YE(20.6), 3.7, 2.05), (XE(7.9), YE(22.4), 2.6, 1.7),
        (XE(8.9), YE(23.9), 1.2, 1.05), (XE(9.8), YE(24.9), 0.1, 0.25)]
CLAW_FLAT = 0.78                # its sections squashed in height
# The beam from the tower to the cap, the machinery under it, the blue lamp.
BEAM = (XE(12.4), XE(17.0), YE(7.7), YE(3.3), 8.7)
UNDER = (XE(12.6), XE(17.6), YE(12.8), YE(7.0), 4.6)
LAMP = (XE(15.5), YE(11.0), 4.5)
# The cap: its vault section (x, z) extruded from y0 to y1; its plan's front corners rounded.
CAP_Y = (YE(7.7), YE(1.35))
CAP_SECTION = [(XE(16.55), -SKIRT), (XE(16.55), 7.9), (XE(17.4), 9.9), (XE(18.9), 10.85), (XE(20.1), 10.85),
               (XE(21.6), 9.9), (XE(22.6), 7.9), (XE(22.6), -SKIRT)]
# The fang under the cap's front: along y from its root to its tip: (y, half-width, base z, crest height).
FANG = [(YE(7.4), 1.55, 6.3, 1.5), (YE(9.0), 1.55, 5.9, 1.45), (YE(10.6), 1.35, 5.3, 1.25), (YE(12.0), 0.95, 4.7, 0.95),
        (YE(13.2), 0.45, 4.2, 0.55), (YE(13.9), 0.08, 3.9, 0.15)]
FANG_X = XE(19.55)
# The strut from under the fang down to the arc's foot; the foot.
STRUT = [(XE(20.45), YE(12.4), 4.2, 0.82), (XE(20.5), YE(15.5), 3.6, 0.78), (XE(20.3), YE(18.6), 3.0, 0.86)]
STRUT_FOOT = (XE(18.4), XE(21.7), YE(21.2), YE(17.9), 3.4)
# The red arc (whole, symmetric): its left half's path (x, y, z); and the pin joining the caps (y, z, radius).
ARC = [(XE(19.9), YE(19.4), 2.6), (XE(20.3), YE(21.4), 2.3), (XE(21.3), YE(22.9), 2.0), (XE(22.8), YE(23.7), 1.8),
       (AXIS_X, YE(23.9), 1.75)]
ARC_HALF, ARC_TOP = 1.22, 1.15
PIN = (YE(4.0), 8.7, 1.05)


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.4):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.2):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    return {
        "dark": mat("gate_dark", 0x02, 0.4, 0.55),
        "steel": mat("gate_steel", 0x04, 0.5, 0.42),
        "grey": mat("gate_grey", 0x06, 0.5, 0.38),
        "light": mat("gate_light", 0x08, 0.5, 0.34),
        "edge": mat("gate_edge", 0x0a, 0.5, 0.3),
        "red_dark": mat("gate_red_dark", 0x43, 0.35, 0.4),
        "red": mat("gate_red", 0x46, 0.35, 0.32),
        "red_light": mat("gate_red_light", 0x49, 0.3, 0.28),
        "salmon": mat("gate_salmon", 0x4b, 0.25, 0.22),
        "brown": mat("gate_brown", 0xa2, 0.3, 0.5),
        "eye": lit("gate_eye", 0x4a, 1.6),
        "eye_hot": lit("gate_eye_hot", 0x4d, 2.4),
        "lamp": lit("gate_lamp", 0x6c, 0.9),
    }


# --- Helpers -----------------------------------------------------------------------------------------------------

def clip_below(obj, z):
    """Cuts an object off below z (closing the cut)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                                    plane_no=(0, 0, -1), clear_outer=True)
    edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def tower_z(y):
    """The tower's top at y: flat, then the slope, then the ledge."""
    for (y0, z0), (y1, z1) in zip(TOWER_PROFILE[1:-2], TOWER_PROFILE[2:-1]):
        if y1 <= y <= y0:
            return z0 + (z1 - z0) * (y0 - y) / (y0 - y1) if y0 != y1 else max(z0, z1)
    return TOP_Z if y > TOWER_PROFILE[1][0] else LEDGE_Z


def lofted(name, sections, mat, start=None, end=None):
    """A hull through sections (lists of Vectors of equal length)."""
    return k.loft(name, sections, mat, start_point=start, end_point=end)


# --- The parts (left half) ----------------------------------------------------------------------------------------

def tower(m):
    """The tower: its plan and its side profile extruded and intersected, bevelled; the top grey, the slope darker,
    the ledge lit; the straps on it; the eyes in its slope."""
    body = mk.prism("tower", TOWER_PROFILE, XE(2.0), XE(13.0), m["grey"], axis="x")
    mk.boolean(body, mk.prism("tower_plan", TOWER_PLAN, -SKIRT - 1.0, TOP_Z + 2.0), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 1.1, 5, 30)
    mk.shade(body, 35)
    slope_top = TOWER_PROFILE[2][0]

    def pick(c, n):
        if n.z > 0.85 and c.z > TOP_Z - 0.3:
            return m["grey"]
        if n.z > 0.85 and abs(c.z - LEDGE_Z) < 0.3:
            return m["light"]       # the ledge (row 10)
        if n.y < -0.3 and n.z > 0.3 and SLOPE_FOOT[0] - 0.2 < c.y < slope_top + 0.2:
            return m["grey"]        # the slope (rows 7-9)
        if n.z < 0.3:
            return m["steel"]
        return None
    mk.paint(body, pick)
    # The straps: the spine down the top, the cross piece, the side strap down the inner side and over the leg.
    up = STRAP_UP
    for name, (x0, x1, y0, y1) in (("strap_spine", STRAP_SPINE), ("strap_cross", STRAP_CROSS)):
        strap = mk.box(name, x0, x1, y0, y1, TOP_Z - 0.5, TOP_Z + up, m["light"])
        mk.bevel(strap, 0.2, 2, 35)
        mk.shade(strap, 35)
        mk.paint(strap, lambda c, n: m["edge"] if n.z > 0.85 else None)
    x0, x1 = STRAP_SIDE
    start = STRAP_CROSS[3]
    profile = [(start, TOP_Z + up)] + [(y, z + up) for y, z in TOWER_PROFILE[2:-1]]
    side = mk.prism("strap_side", [(start, -SKIRT)] + profile + [(TOWER_PROFILE[-1][0], -SKIRT)], x0, x1, m["light"],
                    axis="x")
    mk.bevel(side, 0.2, 2, 30)
    mk.shade(side, 35)
    mk.paint(side, lambda c, n: m["edge"] if n.z > 0.85 else None)
    # The eyes: small glowing domes set in the slope, facing down its normal; a hot spot in each.
    slope = Vector((0.0, TOWER_PROFILE[2][0] - SLOPE_FOOT[0], TOP_Z - SLOPE_FOOT[1]))
    normal = Vector((0.0, -slope.z, slope.y)).normalized()
    turn = normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
    for i, (x, y) in enumerate(EYES):
        z = tower_z(y)
        socket = mk.lathe(f"eye_socket{i}", [(EYE_R + 0.32, -0.3), (EYE_R + 0.32, 0.12), (EYE_R + 0.12, 0.2)],
                          (0.0, 0.0), m["dark"], 20)
        eye = mk.dome(f"eye{i}", (0.0, 0.0), (EYE_R, EYE_R * 0.85, 0.42), 0.0, m["eye"], 20, 5)
        hot = mk.dome(f"eye_hot{i}", (-0.12, 0.1), (EYE_R * 0.45, EYE_R * 0.4, 0.2), 0.3, m["eye_hot"], 14, 3)
        for part in (socket, eye, hot):
            part.data.transform(Matrix.Translation((x, y, z)) @ turn)
        k.smooth(socket, 40)


def leg(m):
    """The leg in front of the tower: the outer block and the inner strap block (its crest lit) with the groove
    between them, the inner one's wider foot; the red claw hooking down from under the outer block."""
    for name, (x0, x1, y0, y1, back, front) in (("leg_outer", LEG_OUTER), ("leg_inner", LEG_INNER)):
        top = (lambda back, front, y0, y1: lambda x, y: front + (back - front) * (y - y0) / (y1 - y0))(back, front, y0,
                                                                                                    y1)
        block = mk.wedge(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], -SKIRT, top, m["grey"])
        mk.bevel(block, 1.35 if name == "leg_outer" else 0.75, 5, 30)
        mk.shade(block, 35)
        mk.paint(block, lambda c, n: m["light"] if n.z > 0.85 else m["steel"] if n.z < 0.3 else None)
    x0, x1, y0, y1, top = LEG_FOOT
    foot = mk.box("leg_foot", x0, x1, y0, y1, -SKIRT, top, m["steel"])
    mk.bevel(foot, 0.45, 3, 35)
    mk.shade(foot, 35)
    mk.paint(foot, lambda c, n: m["grey"] if n.z > 0.85 else None)
    # The claw: a talon of squashed round sections bending down to its tip, its top red, its sides dark.
    dense = mk.chaikin([tuple(p) for p in CLAW], 2, closed=False)
    segments = 18
    claw = mk.tube("claw", [p[:3] for p in dense], dense[0][3], m["red_dark"], segments, radii=[p[3] for p in dense])
    # Its sections squashed in height about the path: a broader, flatter talon.
    for i, v in enumerate(claw.data.vertices[:len(dense) * segments]):
        centre = dense[i // segments]
        v.co.z = centre[2] + (v.co.z - centre[2]) * CLAW_FLAT
    claw.data.update()
    claw.data.update()
    values = [v.normal.z for v in claw.data.vertices]
    band_split(claw, values, [(-9.0, m["brown"]), (-0.15, m["red_dark"]), (0.35, m["red"]), (0.8, m["red_light"])])
    k.smooth(claw, 60)


def beam(m):
    """The beam from the tower to the cap; the dark machinery under it and the small blue lamp."""
    x0, x1, y0, y1, top = BEAM
    b = mk.box("beam", x0, x1, y0, y1, top - 2.6, top, m["grey"])
    mk.bevel(b, 0.4, 3, 35)
    mk.shade(b, 35)
    mk.paint(b, lambda c, n: m["light"] if n.z > 0.85 else m["steel"] if n.z < 0.3 else None)
    x0, x1, y0, y1, top = UNDER
    under = mk.box("under", x0, x1, y0, y1, -SKIRT, top, m["dark"])
    mk.bevel(under, 0.4, 2, 35)
    mk.shade(under, 35)
    x, y, z = LAMP
    mk.dome("lamp", (x, y), (0.6, 0.6, 0.45), z, m["lamp"], 16, 4)


def cap(m):
    """The inner pylon's cap: a vault section extruded down the screen, its front corners rounded, bevelled; its crest
    lit."""
    y0, y1 = CAP_Y
    body = mk.prism("cap", CAP_SECTION, y0, y1, m["grey"], axis="y")
    plan = mk.chaikin([P(16.4, 1.2), P(22.8, 1.2), P(22.8, 7.0), P(21.6, 7.8), P(17.6, 7.8), P(16.4, 7.0)], 1)
    mk.boolean(body, mk.prism("cap_plan", plan, -SKIRT - 1.0, 14.0), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 0.7, 4, 28)
    mk.shade(body, 30)
    mk.paint(body, lambda c, n: m["edge"] if n.z > 0.97 else m["light"] if n.z > 0.75 else
             m["steel"] if n.z < 0.3 else None)


def fang(m):
    """The red fang hanging from the cap's front: lofted diamond sections tapering to its tip, sloping down; salmon
    along its crest."""
    sections = []
    for y, w, z, h in FANG:
        ring = []
        for j in range(12):
            a = 2 * math.pi * j / 12
            c, s = math.cos(a), math.sin(a)
            # A rounded diamond: across w, up h above its base z, a little below it.
            px = math.copysign(abs(c) ** 1.4, c) * w
            pz = (math.copysign(abs(s) ** 1.4, s) * (h if s > 0 else 0.45 * h + 0.1))
            ring.append(Vector((FANG_X + px, y, z + pz)))
        sections.append(ring)
    tip = FANG[-1]
    f = lofted("fang", sections, m["red"], start=(FANG_X, FANG[0][0] + 0.2, FANG[0][2]),
               end=(FANG_X, tip[0] - 0.15, tip[2]))
    k.smooth(f, 60)
    mk.paint(f, lambda c, n: m["salmon"] if n.z > 0.86 else m["red_light"] if n.z > 0.5 else
             m["red_dark"] if n.z < 0.0 else None)


def strut(m):
    """The thin strut from under the fang down to the arc's foot, and the foot."""
    s = mk.smooth_tube("strut", STRUT, m["grey"], 12, iterations=2)
    k.smooth(s, 60)
    mk.paint(s, lambda c, n: m["light"] if n.z > 0.8 else None)
    x0, x1, y0, y1, top = STRUT_FOOT
    foot = mk.box("strut_foot", x0, x1, y0, y1, -SKIRT, top, m["grey"])
    mk.bevel(foot, 0.6, 3, 35)
    mk.shade(foot, 35)
    mk.paint(foot, lambda c, n: m["light"] if n.z > 0.85 else m["steel"] if n.z < 0.3 else None)


def arc(m):
    """The red arc joining the two halves below (whole, symmetric): a bar swept through its path and its mirror."""
    left = [Vector(p) for p in ARC]
    right = [Vector((2 * AXIS_X - p.x, p.y, p.z)) for p in reversed(left[:-1])]
    path = mk.chaikin([tuple(p) for p in left + right], 2, closed=False)
    points = [Vector(p) for p in path]
    ups = [Vector((0, 0, 1))] * len(points)
    depth = max(p.z for p in points) + SKIRT + 0.5
    bar = mk.bar("arc", points, ups, ARC_HALF, ARC_TOP, depth, m["red"], 16, 3.2)
    clip_below(bar, -SKIRT)
    k.smooth(bar, 50)
    mk.paint(bar, lambda c, n: m["red_light"] if n.z > 0.85 else m["red_dark"] if n.z < 0.3 else None)


def pin(m):
    """The red pin joining the two caps above (whole)."""
    y, z, r = PIN
    x0, x1 = CAP_SECTION[-1][0] - 0.4, 2 * AXIS_X - (CAP_SECTION[-1][0] - 0.4)
    rings = []
    for x, rr in ((x0, r * 0.9), (x0 + 0.3, r), (x1 - 0.3, r), (x1, r * 0.9)):
        rings.append([Vector((x, y + rr * math.cos(2 * math.pi * j / 18), z + rr * math.sin(2 * math.pi * j / 18)))
                      for j in range(18)])
    p = k.loft("pin", rings, m["red"])
    k.smooth(p, 50)
    mk.paint(p, lambda c, n: m["red_light"] if n.z > 0.7 else None)
    # A ring at its middle.
    rings = []
    for x, rr in ((AXIS_X - 0.45, r + 0.18), (AXIS_X + 0.45, r + 0.18)):
        rings.append([Vector((x, y + rr * math.cos(2 * math.pi * j / 18), z + rr * math.sin(2 * math.pi * j / 18)))
                      for j in range(18)])
    k.smooth(k.loft("pin_ring", rings, m["red_dark"]), 40)


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
    tower(m)
    leg(m)
    beam(m)
    cap(m)
    fang(m)
    strut(m)
    half = mk.meshes()
    for obj in half:
        mk.apply(obj)
    mirror_half(half)
    arc(m)
    pin(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, m


def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(28)]
    for sprite, c0 in ((85, 0), (87, 24)):
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[y][c0 + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    whole, m = build_whole()
    print("whole claw gate: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_5.png") if "check" in options else None
    if sheet:
        mk.compare("whole (5 85 + 87)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "claw_gate_whole", whole, size=(48, 28), scale=8, distance=1.7)
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (5 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
