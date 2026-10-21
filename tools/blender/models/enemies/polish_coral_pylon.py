"""CORAL's segmented grey column (sheet T, three 2x2 sprites of 24 x 28 pixels; enemies 1213, 1214, 1215 of episode 5,
ground enemies, armour 20 each, one frame each: T 279, 281, 283). Polished (2026-10-21, round 29); it replaces
wave3_v_sea.py's column. CORAL sends it 15 times (t 320-5260), always as one 24 x 84 picture of three enemies moving
together, with its red sea worm inside it (polish_coral_worm.py): 1213 (279) at (x, y), 1214 (281) at (x, y + 28),
1215 (283) at (x, y + 56), all type 10 (ground 2, slots 75-99), and the worm's 1216 (' 1) at (x, y + 14) and 1217
(' 39) at (x, y + 42), type 6 (ground, slots 25-49). The game draws slots 25-49 before 75-99, so the column covers the
worm: every one of its 422 pixels lies under the column's. The column swims in from beyond the screen's left or right
edge (x -30, -40, 260, 280; exc -2 or 2, eyc -1: it holds still on the screen while the floor scrolls under it), the
worm shoots out of it down the screen 50 ticks later (eyc 3) and the column accelerates away up the screen (eycc -4).
So it is a carrier: a grey metal tube with the worm lying in its bore, its muzzle at the bottom end. No episode 6
level takes a CORAL wave. No other enemy, launched ones included, shows its sprites; twins3.py (every sheet, the
eight turns and mirrors, other ramps) finds no twin. Its enemy data has no damaged look (dgr 0) and no animation.

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 84 picture): a grey tube (ramp 0) lying up
the screen, 14 pixels wide (columns 5-18, a dark outline 0x01), lit along its middle (0x0b-0x0c, its flanks 0x06-0x08);
four dark joints arching across it (rows 15-18, 35-38, 53-55, 63-65: a pale lip over a dark groove); at its far end
(rows 0-12) the tube narrows to a rounded end with a lip, two lugs beside it (columns 2-5 and 18-21, the left one in
shadow); a wide flange (rows 19-28, the whole width, its lower corners chamfered), a sleeve with a rail along each side
(rows 39-52, columns 2-5 and 18-21), a smaller flange with a round knob on each side (rows 66-71); at the near end a
wider head (rows 72-78, 16 pixels) with a round dark port in its top, a grey ball in it lit from the upper right, a
bright lip over it, and a short rounded nose (rows 79-83).

Built as such a machine: the tube is a closed hollow shell turned about an axis along y (its cross-sections ellipses,
AXIS_Z high, SQUASH times as high as wide: the body from z 0.8 to 12.8, so it glides under a pixel over the floor;
the wider head dips to 0.1), its outer profile following the sprites' half widths (the far end rounded, a shoulder,
the head drum, a dome down to the nose), its bore (BORE, its axis BORE_Z a little lower) big enough for the worm,
which lies in it on its floor (polish_coral_worm.py: the worm's body and knot stay 0.4 pixels inside the outer
surface everywhere, so the whole column hides it from every side, as the sprites do; --check there tests it). The
joints are dark seams on planes leaning back JOINT_LEAN (their tops further up the screen than their sides: with the
camera's tilt they arch as the sprites draw them), each with a pale lip up the screen of it; the far end's rim a seam
too. The flanges are flat collars round the tube (COLLARS: turned like it, their cross-sections ellipses less than a
third as high as wide, so that they lie under the tube's top and show beside it, as the sprites run the tube's light
straight through them), their outlines the sprites' (the chamfered corners); the second carries a knob on each side.
The lugs are rounded blocks against the far end, the rails rounded bars against the sleeve. The port is a dark lens
let into the dome's upper slope (where the camera sees it where the sprite draws it) with a bright rim, the ball
sitting in it (glowing a little in its own greys, BALL_GLOW, so that it doesn't read black from the slanted camera).
Painted in ramp 0's shades in bands by how much each part faces up (shade_of(), SHADES, LIFT: the stripe along the
top 0x0b-0x0c, the flanks 0x07-0x08, below 0x04-0x06; the game shows these greys darker than Blender's previews),
satin metal (metallic 0.22, roughness 0.42); the bore 0x02, the cut faces 0x05.

The tube is built piece by piece (its profile between the cuts, the cuts closed by rings of the wall's section and
the bore left open behind them: when a neighbour is shot away the cut shows the dark bore and the worm in it); the
other parts are built whole and cut along the sprites' edges (y = 14, -14; this script's cut(): the caps keep their
material and the uncut parts' shading). Each piece is moved so that its sprite's centre is its origin, every mesh is
triangulated (polish_k_pod.triangulate: the same output with and without --check) and its parts are joined into one
mesh (polish_deli_boss.join). Deterministic: no random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor. The whole's origin
is the middle of the picture's width on the middle of 281: column c is x = c - 11.5, row r is y = 41.5 - r. The pieces'
centres: 279 (0, 28), 281 (0, 0), 283 (0, -28).

models.cfg (model lines unchanged: model coral_pylon_top / _mid / _base enemies/coral_pylon_*.glb origin): sprite t 279
coral_pylon_top yaw=0 height=-4, sprite t 281 coral_pylon_mid yaw=0 height=-4, sprite t 283 coral_pylon_base yaw=0
height=-4 (height=-4 sets it on the sea floor: drawn at their origin, ground pieces otherwise float 4 pixels over the
terrain; the worm's lines take the same). Replaces wave3_v_sea.py's column (its section "T 279 above 281 above 283: the
segmented column": COLUMN, column_whole(), column_piece(), the v.pieced("coral_pylon", ...) registration, its docstring
paragraph) and wave3_v_art.py's COLUMN (read only by that section): remove them so that they don't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_T.png), --preview <prefix> (the whole: top and 3/4 views; --pieces 1 also each
piece's), --only <model,...>, --whole <file.glb> (the uncut whole, for looking at), --stats 1 (parts' triangles).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# --- The tube ----------------------------------------------------------------------------------------------------------
AXIS_Z = 6.8                 # the tube's axis over the floor
SQUASH = 0.86                # its cross-sections' height over their width
SEGMENTS = 32                # round it (the bore half as many)
# Its half width along y (control points of a monotone cubic): the nose's tip, the nose, the dome, the head drum, its
# bevelled back edge, the body, the shoulder, the far end's section and its rounded end.
OUTER = [(-42.0, 0.0), (-41.88, 1.25), (-41.6, 2.3), (-41.1, 3.15), (-40.3, 3.85), (-39.2, 4.3), (-38.2, 4.75),
         (-37.6, 5.25), (-37.0, 6.0), (-36.3, 6.75), (-35.5, 7.3), (-34.5, 7.68), (-33.6, 7.8), (-30.7, 7.8),
         (-30.2, 7.6), (-29.75, 7.2), (-29.3, 7.0), (35.3, 7.0), (35.75, 6.6), (36.2, 6.15), (36.6, 6.0),
         (40.0, 6.0), (40.7, 5.6), (41.2, 4.85), (41.6, 3.7), (41.85, 2.3), (42.0, 0.0)]
# The bore (half width; its height BORE_SQUASH times that, about the same axis) and its rounded ends.
BORE = [(-29.3, 0.0), (-29.25, 3.6), (-29.0, 5.0), (-28.5, 5.6), (34.5, 5.6), (35.0, 5.0), (35.25, 3.6),
        (35.3, 0.0)]
BORE_SQUASH = 0.89
BORE_Z = 6.2                 # the bore's axis (a little under the tube's: the worm lies on its floor)
CUTS = (14.0, -14.0)
PIECES = [("coral_pylon_top", 279, (-12.0, 12.0, 14.0, 42.0)), ("coral_pylon_mid", 281, (-12.0, 12.0, -14.0, 14.0)),
          ("coral_pylon_base", 283, (-12.0, 12.0, -42.0, -14.0))]

# --- Painting ----------------------------------------------------------------------------------------------------------
# The shade (ramp 0, 0-15) of a part by how much it faces up (n.z): below MID it falls from FLANK to UNDER (facing
# down); above it it rises to TOP as ((n.z - MID) / (1 - MID)) ** RISE (the sprites' narrow bright stripe).
UNDER, FLANK, TOP, MID, RISE = 4.0, 7.6, 12.3, 0.5, 1.7
LIFT = 0.5                   # a lift of every shade (the game shows palette greys darker than Blender's previews)
SHADES = [(-99.0, 0x04), (5.3, 0x06), (6.9, 0x07), (7.8, 0x08), (8.7, 0x09), (9.6, 0x0a), (10.5, 0x0b),
          (11.4, 0x0c)]
METAL = dict(metallic=0.22, roughness=0.42)
BORE_INDEX, SECTION_INDEX, SEAM_INDEX, SOCKET_INDEX, LIP_INDEX = 0x02, 0x05, 0x02, 0x01, 0x0b

# --- The joints: (y of the seam's top, the tube's half width there); JOINT_LEAN: how far up the screen a seam's top
# lies from its sides, per pixel of height. The far end's rim seam too.
JOINTS = [23.6, 3.7, -13.3, -23.3]
RIM_SEAM = 38.9
JOINT_LEAN = 0.55
SEAM_RADIUS, SEAM_SINK = 0.36, 0.14
SEAM_ARC = (-35.0, 215.0)           # the seams run round the tube's upper side (degrees from +x)
LIP_RADIUS, LIP_GAP = 0.26, 0.55   # the pale lip: its radius, how far behind the seam (along y)

# --- The flanges: flat collars round the tube: (name, half widths along y following the sprites' outlines with their
# chamfered corners, their cross-sections' height over width about the tube's axis: their tops lie under the tube's
# at its middle and over it at its flanks).
COLLARS = [("collar_a", [(13.0, 6.2), (13.4, 7.6), (14.4, 9.0), (15.6, 10.6), (16.6, 11.8), (17.2, 12.0), (21.8, 12.0),
                         (22.4, 11.6), (22.8, 10.2), (23.0, 6.2)], 0.283),
           ("collar_c", [(-30.0, 6.2), (-29.8, 8.0), (-29.3, 9.2), (-28.6, 10.2), (-27.8, 10.95), (-27.3, 11.0),
                         (-25.2, 11.0), (-24.7, 10.6), (-24.3, 9.4), (-24.0, 6.2)], 0.29)]
KNOBS = [(8.7, -26.6, 1.25, 0.95)]   # on collar_c, both sides: x, y, radius, height over the collar's top
# The rails along the sleeve (rows 39-52): x, z over the axis, their half width and height, y0, y1.
RAIL = (8.4, 0.2, 1.5, 1.05, -10.35, 2.4)
# The lugs beside the far end (rows 0-12): inner x, outer x, y0, y1, z0, z1 over the axis, the rounding.
LUG = (6.2, 9.9, 29.2, 41.9, -2.3, 2.5, 0.75)
# The port: its middle's y on the dome's top line, its half sizes (across, along the slope), the lens' depth; the
# ball's radius and how far it stands out of the lens; the rim's radius.
PORT = (-35.3, 4.0, 3.5, 0.85)
BALL = (2.05, 1.25)
PORT_RIM = 0.42
BALL_SHADES = [(-99.0, 0x09), (8.6, 0x0b), (10.6, 0x0d)]
BALL_GLOW = 0.4
SUN = Vector((-0.6, 0.6, 1.0)).normalized()    # towards the game's sun (from above and the top left)


def X(c):
    return c - 11.5


def Y(r):
    return 41.5 - r


# --- Profiles ------------------------------------------------------------------------------------------------------------

class Monotone:
    """A monotone cubic (Fritsch-Carlson) through points [(y, value)], y ascending: value(y) and its slope."""

    def __init__(self, points):
        self.x = [p[0] for p in points]
        self.y = [p[1] for p in points]
        n = len(points)
        h = [self.x[i + 1] - self.x[i] for i in range(n - 1)]
        d = [(self.y[i + 1] - self.y[i]) / h[i] for i in range(n - 1)]
        m = [0.0] * n
        m[0], m[-1] = d[0], d[-1]
        for i in range(1, n - 1):
            if d[i - 1] * d[i] <= 0:
                m[i] = 0.0
            else:
                w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
        self.h, self.m = h, m

    def _seg(self, t):
        if t <= self.x[0]:
            return 0
        for i in range(len(self.x) - 1):
            if t <= self.x[i + 1]:
                return i
        return len(self.x) - 2

    def __call__(self, t):
        t = min(max(t, self.x[0]), self.x[-1])
        i = self._seg(t)
        h = self.h[i]
        s = (t - self.x[i]) / h
        h00, h10 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s
        h01, h11 = -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
        return h00 * self.y[i] + h10 * h * self.m[i] + h01 * self.y[i + 1] + h11 * h * self.m[i + 1]

    def slope(self, t):
        e = 1e-3
        return (self(t + e) - self(t - e)) / (2 * e)


R_OUT = Monotone(OUTER)
R_BORE = Monotone(BORE)


def outer_z_top(y):
    return AXIS_Z + R_OUT(y) * SQUASH


def turned_normal(profile, squash, axis_z, inward=False):
    """The normal of a turned surface (half widths profile(y), cross-sections ellipses squash times as high as
    wide about an axis along y at height axis_z) at a point p of it or near it: n(p)."""
    lo, hi = profile.x[0], profile.x[-1]
    mid = (lo + hi) / 2

    def normal(p):
        y = min(max(p.y, lo + 1e-3), hi - 1e-3)
        r = max(profile(y), 1e-4)
        c, s = p.x / r, (p.z - axis_z) / (r * squash)
        n = Vector((squash * c, -profile.slope(y) * squash * math.hypot(c, s), s))
        if n.length < 1e-9 or math.hypot(c, s) < 0.2:   # an end's flat face or fan
            n = Vector((0.0, 1.0 if p.y > mid else -1.0, 0.0))
        n.normalize()
        return -n if inward else n
    return normal


outer_normal = turned_normal(R_OUT, SQUASH, AXIS_Z)
bore_normal = turned_normal(R_BORE, BORE_SQUASH, BORE_Z, inward=True)


def samples(profile, y0, y1, step=3.0, dr=0.5):
    """The ys the tube's rings stand at between y0 and y1 (both included): every step, closer where the radius turns
    fast, and at the profile's points."""
    ys = {round(y0, 6), round(y1, 6)}
    for p in profile.x:
        if y0 < p < y1:
            ys.add(round(p, 6))
    y = y0
    while y < y1:
        r, sl = profile(y), abs(profile.slope(y))
        d = min(step, dr / max(sl, 1e-6))
        y += max(d, 0.04)
        if y < y1:
            ys.add(round(y, 6))
    return sorted(ys)


def ring(profile, squash, y, axis_z=AXIS_Z, segments=SEGMENTS):
    r = profile(y)
    return [Vector((r * math.cos(2 * math.pi * j / segments), y,
                    axis_z + r * squash * math.sin(2 * math.pi * j / segments))) for j in range(segments)]


def surface_section(name, profile, squash, y0, y1, close_low, close_high, mat, axis_z=AXIS_Z, segments=SEGMENTS,
                    step=3.0, dr=0.5):
    """A turned surface between y0 and y1 (rings), closed by a fan to the axis at an end the profile closes at."""
    ys = [y for y in samples(profile, y0, y1, step, dr) if profile(y) > 0.02]
    verts, faces = [], []
    for y in ys:
        verts += ring(profile, squash, y, axis_z, segments)
    n = segments
    for i in range(len(ys) - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, a + n, b + n, b))
    if close_low:
        verts.append(Vector((0.0, profile.x[0], axis_z)))
        c = len(verts) - 1
        faces += [(c, (j + 1) % n, j) for j in range(n)]
    if close_high:
        verts.append(Vector((0.0, profile.x[-1], axis_z)))
        c = len(verts) - 1
        base = (len(ys) - 1) * n
        faces += [(c, base + j, base + (j + 1) % n) for j in range(n)]
    return k.mesh_object(name, verts, faces, mat), ys


def annulus(name, y, facing, mat):
    """The wall's section at a cut y: a ring between the outer surface and the bore, facing +y or -y."""
    outer, inner = ring(R_OUT, SQUASH, y), ring(R_BORE, BORE_SQUASH, y, BORE_Z, SEGMENTS // 2)
    verts = outer + inner
    n, h = SEGMENTS, SEGMENTS // 2
    faces = []
    for j in range(h):  # two outer segments to each of the bore's
        a, b, c = 2 * j, 2 * j + 1, (2 * j + 2) % n
        i0, i1 = n + j, n + (j + 1) % h
        faces += [(a, b, i0), (b, c, i1, i0)]
    obj = k.mesh_object(name, verts, faces, mat)
    orient(obj, lambda c: Vector((0.0, facing, 0.0)))
    return obj


def orient(obj, outward):
    """Flips the faces whose normals don't point along outward(centre)."""
    mesh = obj.data
    flip = [p.index for p in mesh.polygons if p.normal.dot(outward(p.center)) < 0]
    if flip:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        bmesh.ops.reverse_faces(bm, faces=[bm.faces[i] for i in flip])
        bm.to_mesh(mesh)
        bm.free()
    mesh.update()


def set_normals(obj, normal_of):
    """Smooth faces with the given normals (normal_of(co)) at their corners."""
    mesh = obj.data
    mesh.shade_smooth()
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            normals.append(tuple(normal_of(mesh.vertices[mesh.loops[li].vertex_index].co)))
    mesh.normals_split_custom_set(normals)


def shade_of(n):
    """The shade (0-15) a part facing n is painted in."""
    if n.z >= MID:
        s = FLANK + (TOP - FLANK) * ((n.z - MID) / (1.0 - MID)) ** RISE
    else:
        s = UNDER + (FLANK - UNDER) * max(0.0, (n.z + 0.35) / (MID + 0.35))
    return s + LIFT


# --- Materials ---------------------------------------------------------------------------------------------------------

def materials():
    m = {}
    for _, index in SHADES:
        m[index] = k.material(f"pylon_{index:02x}", palette=index, **METAL)
    m["bore"] = k.material(f"pylon_bore_{BORE_INDEX:02x}", palette=BORE_INDEX, metallic=0.2, roughness=0.7)
    m["section"] = k.material(f"pylon_cut_{SECTION_INDEX:02x}", palette=SECTION_INDEX, metallic=0.3, roughness=0.55)
    m["seam"] = m["bore"]
    m["lip"] = m[LIP_INDEX]
    m["socket"] = k.material(f"pylon_port_{SOCKET_INDEX:02x}", palette=SOCKET_INDEX, metallic=0.2, roughness=0.25)
    pal = k.level_palette()
    for _, index in BALL_SHADES:
        m[("ball", index)] = k.material(f"pylon_ball_{index:02x}", palette=index, metallic=0.35, roughness=0.22,
                                        emission=pal[index], emission_strength=BALL_GLOW)
    return m


def paint_by_facing(obj, m, normal_of=None, bands=None):
    """band_split by the shade of each vertex's normal (normal_of(co), or the mesh's own smooth normals)."""
    bands = bands or [(lo, m[index]) for lo, index in SHADES]
    mesh = obj.data
    if normal_of is None:
        normals = [v.normal.copy() for v in mesh.vertices]
    else:
        normals = [normal_of(v.co) for v in mesh.vertices]
    band_split(obj, [shade_of(n) for n in normals], bands)
    return obj


# --- The tube, piece by piece --------------------------------------------------------------------------------------------

def tube_piece(m, box):
    """The tube's shell between the piece's cuts: its outer surface painted by facing, the bore (left open where the
    piece is cut: it ends in the cut's ring) and the rings of the wall's section at the cuts."""
    _, _, y0, y1 = box
    lo_end, hi_end = y0 <= OUTER[0][0], y1 >= OUTER[-1][0]
    ya, yb = max(y0, OUTER[0][0]), min(y1, OUTER[-1][0])
    parts = []
    outer, _ = surface_section("pylon_tube", R_OUT, SQUASH, ya, yb, lo_end, hi_end, m[0x08])
    orient(outer, outer_normal)
    paint_by_facing(outer, m, outer_normal)
    orient(outer, outer_normal)
    set_normals(outer, outer_normal)
    parts.append(outer)
    ba, bb = max(y0, BORE[0][0]), min(y1, BORE[-1][0])
    if ba < bb:
        bore, _ = surface_section("pylon_bore", R_BORE, BORE_SQUASH, ba, bb, ba <= BORE[0][0], bb >= BORE[-1][0],
                                  m["bore"], BORE_Z, SEGMENTS // 2, 30.0, 1.0)
        orient(bore, bore_normal)
        set_normals(bore, bore_normal)
        parts.append(bore)
    for y, facing in ((y0, -1.0), (y1, 1.0)):
        if OUTER[0][0] < y < OUTER[-1][0]:
            parts.append(annulus("pylon_cut", y, facing, m["section"]))
    return parts


# --- The whole's other parts ------------------------------------------------------------------------------------------

def loop_tube(name, points, radius, mat, segments=8, closed=True):
    """A tube round a closed loop of points (or along an open run of them, its ends capped)."""
    n = len(points)
    verts, faces = [], []
    for i, p in enumerate(points):
        if closed:
            t = (points[(i + 1) % n] - points[i - 1]).normalized()
        else:
            t = (points[min(i + 1, n - 1)] - points[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        a = t.cross(ref).normalized()
        b = t.cross(a).normalized()
        for j in range(segments):
            ang = 2 * math.pi * j / segments
            verts.append(p + (a * math.cos(ang) + b * math.sin(ang)) * radius)
    for i in range(n if closed else n - 1):
        i2 = (i + 1) % n
        for j in range(segments):
            j2 = (j + 1) % segments
            faces.append((i * segments + j, i2 * segments + j, i2 * segments + j2, i * segments + j2))
    if not closed:
        for end, step in ((0, 1), (n - 1, -1)):
            verts.append(points[end] - (points[end + step] - points[end]).normalized() * radius * 0.6)
            c = len(verts) - 1
            faces += [(c, end * segments + (j + 1) % segments, end * segments + j) for j in range(segments)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def seam_loop(y_top, behind=0.0, sink=SEAM_SINK, count=26):
    """Points along the tube's upper side (SEAM_ARC: the rest is never seen) on the plane leaning back JOINT_LEAN
    through the seam (its top at y_top), sunk sink into the surface; behind moves it up the screen."""
    pts = []
    a0, a1 = (math.radians(a) for a in SEAM_ARC)
    for i in range(count + 1):
        a = a0 + (a1 - a0) * i / count
        y = y_top + behind
        for _ in range(4):  # the plane: y = y_side + JOINT_LEAN * (z - axis)
            r = R_OUT(y)
            z = r * SQUASH * math.sin(a)
            y = y_top + behind - JOINT_LEAN * (R_OUT(y_top) * SQUASH - z)
        r = R_OUT(y) - sink
        pts.append(Vector((r * math.cos(a), y, AXIS_Z + r * SQUASH * math.sin(a))))
    return pts


def seams(m):
    out = []
    for i, y in enumerate(JOINTS + [RIM_SEAM]):
        out.append(loop_tube(f"pylon_seam{i}", seam_loop(y), SEAM_RADIUS, m["seam"], 5, closed=False))
        lip = loop_tube(f"pylon_lip{i}", seam_loop(y, behind=LIP_GAP, sink=0.05), LIP_RADIUS, m["lip"], 5,
                        closed=False)
        out.append(lip)
    return out


def collars(m):
    """The flat collars, turned like the tube (closed by flat ends inside it), painted by facing."""
    out = []
    for name, points, squash in COLLARS:
        prof = Monotone(points)
        obj, _ = surface_section(f"pylon_{name}", prof, squash, points[0][0], points[-1][0], True, True, m[0x08],
                                 segments=24, step=2.5, dr=1.1)
        normal = turned_normal(prof, squash, AXIS_Z)
        orient(obj, normal)
        paint_by_facing(obj, m, normal)
        orient(obj, normal)
        set_normals(obj, normal)
        out.append(obj)
    return out


def collar_top(index, x, y):
    _, points, squash = COLLARS[index]
    w = Monotone(points)(y)
    return AXIS_Z + w * squash * math.sqrt(max(0.0, 1.0 - (x / w) ** 2))


def knobs(m):
    out = []
    for x, y, r, h in KNOBS:
        for side in (1, -1):
            z = collar_top(1, x, y) - 0.3
            obj = mk.dome(f"pylon_knob{side}", (side * x, y), (r, r, h + 0.3), z, m[0x0a], segments=14, steps=4)
            paint_by_facing(obj, m)
            k.smooth(obj, 60)
            out.append(obj)
    return out


def rails(m):
    x, dz, hw, hh, y0, y1 = RAIL
    out = []
    for side in (1, -1):
        prof = [(y0, 0.0), (y0 + 0.12, 0.45), (y0 + 0.4, 0.75), (y0 + 0.9, 0.95), (y0 + 1.6, 1.0), (y1 - 1.6, 1.0),
                (y1 - 0.9, 0.95), (y1 - 0.4, 0.75), (y1 - 0.12, 0.45), (y1, 0.0)]
        obj = k.lathe(f"pylon_rail{side}", [(y, r * hw) for y, r in prof], m[0x08], segments=14, axis_x=side * x,
                      axis_z=AXIS_Z + dz, squash=hh / hw)
        k.smooth(obj, 60)
        paint_by_facing(obj, m)
        k.smooth(obj, 60)
        out.append(obj)
    return out


def lugs(m):
    x0, x1, y0, y1, z0, z1, rnd = LUG
    out = []
    for side in (1, -1):
        obj = mk.box(f"pylon_lug{side}", x0, x1, y0, y1, AXIS_Z + z0, AXIS_Z + z1, m[0x08])
        mk.bevel(obj, rnd, 3, 30)
        if side < 0:
            obj.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
            obj.data.flip_normals()
        triangulate([obj])
        k.smooth(obj, 38)
        paint_by_facing(obj, m)
        k.smooth(obj, 38)
        out.append(obj)
    return out


def port(m):
    """The dark lens in the dome's upper slope, its bright rim and the ball in it."""
    y, ha, hl, depth = PORT
    z = outer_z_top(y)
    nrm = Vector((0.0, -R_OUT.slope(y) * SQUASH, 1.0)).normalized()
    rot = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
    place = Matrix.Translation((0.0, y, z)) @ rot
    lens = mk.ball("pylon_port", (0.0, 0.0, 0.0), (ha, hl, depth), m["socket"], 24, 8)
    lens.data.transform(place @ Matrix.Translation((0.0, 0.0, -depth + 0.18)))
    rim_pts = []
    for i in range(20):
        a = 2 * math.pi * i / 20
        rim_pts.append((place @ Vector(((ha + 0.15) * math.cos(a), (hl + 0.15) * math.sin(a), 0.0))).to_3d())
    # the rim follows the surface: each point moved onto it
    fixed = []
    for p in rim_pts:
        r = R_OUT(p.y) + 0.12
        ang = math.atan2((p.z - AXIS_Z) / SQUASH, p.x)
        fixed.append(Vector((r * math.cos(ang), p.y, AXIS_Z + r * SQUASH * math.sin(ang))))
    rim = loop_tube("pylon_port_rim", fixed, PORT_RIM, m[0x0a], 5)
    paint_by_facing(rim, m)
    k.smooth(rim, 80)
    radius, stand = BALL
    ball = mk.ball("pylon_ball", (0.0, 0.0, 0.0), (radius, radius, radius), m[("ball", 0x0b)], 18, 9)
    ball.data.transform(place @ Matrix.Translation((0.0, 0.0, 0.18 + stand - radius)))
    bands = [(lo, m[("ball", index)]) for lo, index in BALL_SHADES]
    centre = (place @ Vector((0.0, 0.0, 0.18 + stand - radius))).to_3d()

    def ball_normal(co):
        return (Vector(co) - centre).normalized()
    mesh = ball.data
    values = []
    for v in mesh.vertices:
        n = ball_normal(v.co)
        values.append(6.5 + 4.0 * max(0.0, n.z) + 2.0 * max(0.0, n.dot(SUN)))
    band_split(ball, values, bands)
    set_normals(ball, ball_normal)
    return [lens, rim, ball]


def build_parts(m):
    """The whole column's parts but its tube (built per piece)."""
    parts = seams(m)
    parts += collars(m)
    parts += knobs(m)
    parts += rails(m)
    parts += lugs(m)
    parts += port(m)
    for obj in parts:
        mk.apply(obj)
    return parts


# --- Cutting, checks, export -------------------------------------------------------------------------------------------

def cut(source, box_xy, cap_mat):
    """The part of an object inside box (x0, x1, y0, y1), its cuts capped with cap_mat (facing out of the cut, flat),
    its normals the uncut object's (polish_coral_manta.cut, with the caps' own normals); None if nothing is inside."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    if (min(c.x for c in corners) >= x0 and max(c.x for c in corners) <= x1 and
            min(c.y for c in corners) >= y0 and max(c.y for c in corners) <= y1):
        obj = source.copy()
        obj.data = source.data.copy()
        bpy.context.scene.collection.objects.link(obj)
        return obj
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    caps = set()
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    f.material_index = cap_index
                    f.smooth = False
                    caps.add(f)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    caps = {f for f in caps if f.is_valid}
    bm.normal_update()
    bm.faces.index_update()
    cap_normals = {f.index: f.normal.copy() for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_normals:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else cap_normals.get(poly.index, poly.normal)))
    mesh.normals_split_custom_set(normals)
    return obj


def whole_mask(sheet):
    mask = []
    for sprite in (279, 281, 283):
        mask += k.sprite_mask(sheet, sprite)
    return mask


def build_piece(m, parts, name, box, stats=False):
    pieces = [p for p in (cut(src, box, m["section"]) for src in parts) if p is not None]
    pieces += tube_piece(m, box)
    drop_unused(pieces)
    mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    triangulate(pieces)
    if stats:
        for obj in sorted(pieces, key=lambda o: -mk.triangles([o]))[:8]:
            print("    %s: %-22s %6d" % (name, obj.name, mk.triangles([obj])))
    obj = join(pieces, name)
    obj.data.name = name
    obj.hide_render = False   # the cut copies took the hidden sources' state
    return obj


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_T.png") if os.path.isdir(sheets) else sheets
    k.reset()
    m = materials()
    parts = build_parts(m)
    triangulate(parts)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    whole = None
    if sheet or "preview" in options or "whole" in options:
        tube = tube_piece(m, (-12.0, 12.0, -42.0, 42.0))
        triangulate(tube)
        whole = parts + tube
        low, high = mk.bounds(whole)
        print("== whole: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
        if sheet:
            mk.compare("whole (T 279 above 281 above 283)", mk.coverage(whole, 24, 84), whole_mask(sheet))
        if "preview" in options:
            mk.preview(options["preview"] + "coral_pylon_whole", whole, size=(24, 84), scale=8, distance=2.2)
        if "whole" in options:
            mk.export(whole, options["whole"])
        for obj in tube:
            bpy.data.objects.remove(obj)
        whole = None
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        for src in parts:
            src.hide_render = True
        obj = build_piece(m, parts, name, box, "stats" in options)
        if sheet:
            mk.compare("%s (T %d)" % (name, sprite), mk.coverage([obj], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in parts:
            src.hide_render = False


if __name__ == "__main__":
    build()
