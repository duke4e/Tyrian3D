"""The green twin-tank ship of DELI, BONUS, New Deli, STATION, VAULT and DEEP ICE (sky layer), drawn from
two sprites of sheet C, 2x2 each: 197, the left half, and 199, the right half (models.cfg: model
tank_pod_left / tank_pod_right / tank_pod_left_201 ... origin; sprite c 197 tank_pod_left yaw=0, sprite c
199 tank_pod_right yaw=0; frame c 201 tank_pod_left_201, frame c 205 tank_pod_left_205, frame c 203
tank_pod_right_203, frame c 207 tank_pod_right_207). The levels place them as one 48 x 28 picture: 197 at
x and 199 at x + 24, at the same y, linked
so that they move together (DELI's events at 140-180 and 320-360, BONUS's at 100-160, New Deli's at
140-180, STATION's at 30-70), polished (2026-10-18; it replaces wave1_b.py's tank_pod(), a plain green
cylinder, a box and a black coil, one half mirrored).

The ship is built whole and cut along the sprites' edge (x = 0 here) into the two halves, each moved so
that its sprite's centre is its origin (base on the layer, models.cfg origin): drawn at their own places,
they meet again. The normals of the cut halves are taken from the whole ship, so the shading runs on
across the cut as if nothing was cut (as polish_redjet.py does).

As the 4x upscales draw it (the halves are mirror images): in the middle a purple block (columns 21-26 of
the 48 x 28 picture, rows 1-11), its top lit, its front falling towards the bottom of the screen; from it
a green armoured tank either side along the ship (rows 2-9, columns 0-20 on the left), its outer end a
squarish rounded cap, two raised bands next to the block (columns 17 and 19) and a dark collar where it
meets the block; under the tanks a purple rail along the ship (rows 10-12), swelling at either end into a
rounded bumper under the tank's cap (columns 0-7, rows 10-14); under the rail, either side, a ribbed coil
(columns 7-20, rows 13-19): a rounded outer cap, four grooves between three ribs and a neck at its inner
end; and between the two necks a glowing core (columns 21-26, rows 14-17). Dark webs, hidden from above,
join the tank, the rail and the coil, so that the game's slanted view doesn't see through between them.

The animation (197 201 205 201 197, and 199 203 207 203 199 on the right) only pulses the core: dark red
with brighter edges (197), red-orange (201), orange-yellow (205); the purple round it brightens with it in
the sprite, which the game's glow does here. One model per frame and half: tank_pod_left (197),
tank_pod_left_201, tank_pod_left_205, tank_pod_right (199), tank_pod_right_203 and tank_pod_right_207,
the same shapes with the core's own colours and glow.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The
whole ship's x = 0 is the edge between the two sprites (column C of the picture is x = C + 0.5 - 24), its
y = 0 the sprites' centre row (row r is y = 13.5 - r); the left half is moved 12 to the right, the right
half 12 to the left. The parts are built for the left half and mirrored.

Replaces wave1_b.py's tank_pod(), tank_pod_left() and tank_pod_right(): remove them and their MODELS
entries so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes
of the whole ship and of each half against enemy_C.png), --preview <prefix> (the whole ship's and each
half's top and 3/4 views).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from glb_winding import reverse_winding  # noqa: E402
from polish_jets import Curve  # noqa: E402

# The halves: (name, sprite, the box it covers in the ship's coordinates (x0, x1, y0, y1), its centre).
HALVES = [("tank_pod_left", 197, (-30.0, 0.0, -20.0, 20.0), -12.0),
          ("tank_pod_right", 199, (0.0, 30.0, -20.0, 20.0), 12.0)]
# The frames: (the sprites of the left and the right half, the core's colours: its rim (the sides facing
# up and down the screen) and its middle (the top), palette index and emission strength). A half's model
# is named after its first frame's sprite (tank_pod_left), the others <name>_<sprite>.
FRAMES = [
    ((197, 199), {"rim": (0x73, 0.7), "hot": (0x71, 0.45)}),
    ((201, 203), {"rim": (0x74, 0.9), "hot": (0x77, 1.3)}),
    ((205, 207), {"rim": (0x76, 1.1), "hot": (0x7b, 1.9)}),
]
SEGMENTS = {"tank": 30, "coil": 24, "rail": 22, "core": 20}

# The tank (rows 2-9, the outline about two thirds covered): its axis, radius (deeper towards the
# camera: TANK_RZ), its outer end and the length of its squarish cap (a superellipse of power
# CAP_POWER), the bands next to the block (columns 17 and 19) and the grooves beside them (16 and 18),
# where it ends and the dark collar begins (column 20), which runs on into the block.
TANK_Y, TANK_Z, TANK_R, TANK_RZ = 8.0, 5.1, 3.7, 3.9
TANK_END, TANK_CAP, CAP_POWER = -23.65, 3.6, 3.2
BANDS, BAND_HALF, BAND_RISE = (-6.5, -4.6), 0.46, 0.22
GROOVES, GROOVE_HALF, GROOVE_DEPTH = (-7.5, -5.55), 0.3, 0.3
TANK_INNER, COLLAR_R, COLLAR_END = -4.0, 3.05, -2.4

# The block in the middle (columns 21-26, rows 1-11): half its width, its bottom, the rounding of its
# edges, and its top's height along y, from its front (down the screen) to its back: the top lit and
# level, the front falling.
BLOCK_HALF, BLOCK_BOTTOM, BLOCK_ROUND = 3.0, 0.9, 0.75
BLOCK_TOP = Curve([(1.7, 4.7), (2.3, 6.0), (3.2, 7.2), (4.5, 8.45), (6.0, 9.55), (7.3, 10.05), (8.5, 10.2),
                   (11.2, 10.2), (11.9, 9.95), (12.35, 9.3), (12.65, 8.2)])
BLOCK_Y = (1.7, 12.65)

# The rail under the tank (rows 10-12), running on under the block to the middle, and its bumper
# (columns 0-7, rows 10-14): x, its middle's y and z, its half-width and half-height; its ends, the
# bumper's rounding off over RAIL_ROUND.
RAIL = Curve([(-23.55, 1.3, 3.75, 2.6, 2.5), (-22.0, 1.25, 3.8, 2.75, 2.6), (-18.2, 1.25, 3.8, 2.75, 2.6),
              (-16.7, 1.75, 3.95, 2.25, 2.2), (-15.4, 2.4, 4.05, 1.6, 1.8), (0.0, 2.5, 4.05, 1.55, 1.8)])
RAIL_X, RAIL_ROUND = (-23.55, -0.001), 1.9

# The coil (columns 7-20, rows 13-19) and the core between the coils (columns 21-26, rows 14-17): their
# axis, the coil's radius, its outer end and the length of its cap, the grooves between the ribs
# (columns 12, 14, 16 and 18), the neck at its inner end (columns 19-20: from, to, radius), the core's
# radius and how much fuller it is in the middle.
COIL_Y, COIL_Z, COIL_R = -2.15, 3.85, 3.2
COIL_END, COIL_CAP = -16.6, 1.9
COIL_GROOVES, COIL_GROOVE_HALF, COIL_GROOVE_DEPTH = (-11.5, -9.5, -7.5, -5.55), 0.42, 0.55
NECK = (-5.05, -3.35, 2.35)
CORE_R, CORE_BULGE = 2.05, 0.1

# Dark webs joining the parts (hidden from above, they close the gaps the game's slanted view would see
# through): the tank to the rail and the rail to the coil; boxes (x0, x1, y0, y1, z0, z1).
WEBS = [("web_tank", (-16.0, -2.5, 3.5, 4.85, 2.7, 5.2), "collar"),
        ("web_coil", (-14.6, -3.6, 0.2, 1.75, 2.3, 4.35), "coil_groove")]


# --- Helpers ----------------------------------------------------------------------------------------

def ring_x(x, cy, cz, ry, rz, segments, power=2.0):
    """A cross-section in the YZ plane at x (a superellipse)."""
    out = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        c, s = math.cos(a), math.sin(a)
        out.append(Vector((x, cy + math.copysign(abs(c) ** (2 / power), c) * ry,
                           cz + math.copysign(abs(s) ** (2 / power), s) * rz)))
    return out


def lathe_x(name, profile, mat, cy, cz, segments, squash=1.0):
    """A round part along +x through (x, radius) pairs (increasing x), closed at both ends."""
    rings = [ring_x(x, cy, cz, r, r * squash, segments) for x, r in profile if r > 1e-4]
    return k.loft(name, rings, mat, start_point=(profile[0][0], cy, cz), end_point=(profile[-1][0], cy, cz))


def cap_profile(x_end, length, radius, power, count=10):
    """A squarish rounded end along +x: (x, r) from its tip (r 0) to the full radius."""
    out = []
    for i in range(count + 1):
        a = (math.pi / 2) * i / count
        out.append((x_end + length * (1 - math.cos(a) ** (2 / power)), radius * math.sin(a) ** (2 / power)))
    return out


def dips(x, centres, half, depth):
    """How far below its radius a ribbed surface lies at x: rounded grooves at the centres."""
    d = 0.0
    for c in centres:
        t = abs(x - c) / half
        if t < 1:
            d = max(d, depth * (0.5 + 0.5 * math.cos(math.pi * t)))
    return d


def rises(x, centres, half, rise):
    """How far above its radius a banded surface lies at x: rounded bands at the centres."""
    r = 0.0
    for c in centres:
        t = abs(x - c) / half
        if t < 1:
            r = max(r, rise * (1 - t ** 4) ** 0.5)
    return r


def samples(a, b, step, features=(), per=3):
    """Positions from a to b about step apart, and per either side of each feature (centre, half
    width), so that grooves and bands keep their shape."""
    xs = set(fine(a, b, step))
    for c, half in features:
        for i in range(-per, per + 1):
            x = c + half * i / per
            if a <= x <= b:
                xs.add(x)
    out = []
    for x in sorted(xs):
        if not out or x - out[-1] > 0.05:
            out.append(x)
    return out


def paint(obj, mats, key):
    """Gives each face the material key(face) names (keys of mats)."""
    names = []
    for poly in obj.data.polygons:
        name = key(poly)
        if name not in names:
            names.append(name)
    obj.data.materials.clear()
    for name in names:
        obj.data.materials.append(mats[name])
    for poly in obj.data.polygons:
        poly.material_index = names.index(key(poly))
    return obj


def fine(a, b, step):
    count = max(1, int(math.ceil((b - a) / step)))
    return [a + (b - a) * i / count for i in range(count + 1)]


# --- The parts (left half) ---------------------------------------------------------------------------

def tank(mats):
    """The green tank along x: its squarish outer cap, the long body, two bands and two grooves next
    to the block, the dark collar into the block."""
    profile = cap_profile(TANK_END, TANK_CAP, TANK_R, CAP_POWER)
    body_end = TANK_INNER - 0.25
    features = [(c, BAND_HALF) for c in BANDS] + [(c, GROOVE_HALF) for c in GROOVES]
    for x in samples(TANK_END + TANK_CAP, body_end, 1.6, features)[1:]:
        r = TANK_R + rises(x, BANDS, BAND_HALF, BAND_RISE) - dips(x, GROOVES, GROOVE_HALF, GROOVE_DEPTH)
        profile.append((x, r))
    # The inner end: a rounded edge down to the collar, which runs into the block.
    last = profile[-1][1]
    for i in range(1, 4):
        a = (math.pi / 2) * i / 3
        profile.append((body_end + 0.25 * math.sin(a), COLLAR_R + (last - COLLAR_R) * math.cos(a)))
    profile += [(TANK_INNER + 0.02, COLLAR_R), (COLLAR_END, COLLAR_R)]
    obj = lathe_x("tank", profile, None, TANK_Y, TANK_Z, SEGMENTS["tank"], squash=TANK_RZ / TANK_R)

    def key(poly):
        x = poly.center.x
        if x > TANK_INNER - 0.05:
            return "collar"
        if any(abs(x - c) < BAND_HALF * 0.8 for c in BANDS):
            return "band"
        if any(abs(x - c) < GROOVE_HALF * 0.7 for c in GROOVES):
            return "groove"
        return "tank"
    paint(obj, mats, key)
    return k.smooth(obj, 50)


def rounded_rect(y, hw, z0, z1, r, per_corner=4):
    """A rectangle's outline in the XZ plane at y (x within hw, z from z0 to z1), its corners rounded
    with radius r."""
    out = []
    corners = [(hw - r, z1 - r, 0), (-hw + r, z1 - r, 90), (-hw + r, z0 + r, 180), (hw - r, z0 + r, 270)]
    for cx, cz, a0 in corners:
        for i in range(per_corner + 1):
            a = math.radians(a0 + 90 * i / per_corner)
            out.append(Vector((cx + r * math.cos(a), y, cz + r * math.sin(a))))
    return out


def block(mats):
    """The purple block in the middle: rounded box sections along y, its top level at the back and
    falling towards the front; its edges rounded (BLOCK_ROUND), its ends too."""
    y0, y1 = BLOCK_Y
    ys = fine(y0, y0 + BLOCK_ROUND, 0.19) + fine(y0 + BLOCK_ROUND, y1 - BLOCK_ROUND, 0.6)[1:] + \
        fine(y1 - BLOCK_ROUND, y1, 0.19)[1:]
    rings = []
    for y in ys:
        top = BLOCK_TOP(y)
        # The ends rounded: the section shrinks within BLOCK_ROUND of them (a quarter circle).
        d = min(y - y0, y1 - y)
        f = 1.0 if d >= BLOCK_ROUND else math.sqrt(max(0.0, 1 - (1 - d / BLOCK_ROUND) ** 2))
        shrink = BLOCK_ROUND * (1 - f)
        hw = max(BLOCK_HALF - shrink, 0.05)
        z0, z1 = BLOCK_BOTTOM + shrink, top - shrink
        rings.append(rounded_rect(y, hw, z0, z1, min(BLOCK_ROUND, hw * 0.9, (z1 - z0) * 0.45)))
    obj = k.loft("block", rings, mats["block"], start_point=(0, y0, (BLOCK_BOTTOM + BLOCK_TOP(y0)) / 2),
                 end_point=(0, y1, (BLOCK_BOTTOM + BLOCK_TOP(y1)) / 2))
    return k.smooth(obj, 45)


def rail(mats):
    """The purple rail under the tank, to the middle, and its rounded bumper at the outer end."""
    x0, x1 = RAIL_X
    rings = []
    for x in fine(x0, x0 + RAIL_ROUND, 0.25)[1:] + fine(x0 + RAIL_ROUND, -15.0, 0.6)[1:] + fine(-15.0, x1, 2.5)[1:]:
        cy, cz, ry, rz = RAIL(x)
        d = x - x0
        f = 1.0 if d >= RAIL_ROUND else math.sqrt(max(0.0, 1 - (1 - d / RAIL_ROUND) ** 2))
        rings.append(ring_x(x, cy, cz, ry * f, rz * f, SEGMENTS["rail"]))
    cy0, cz0, _, _ = RAIL(x0)
    cy1, cz1, _, _ = RAIL(x1)
    obj = k.loft("rail", rings, None, start_point=(x0, cy0, cz0), end_point=(x1, cy1, cz1))
    paint(obj, mats, lambda p: "bumper" if p.center.x < -16.0 else "rail")
    return k.smooth(obj, 50)


def coil(mats):
    """The ribbed coil: a rounded outer cap, ribs and grooves, the neck at its inner end."""
    profile = cap_profile(COIL_END, COIL_CAP, COIL_R, 2.4, count=8)
    start = COIL_END + COIL_CAP
    n0, n1, nr = NECK
    features = [(c, COIL_GROOVE_HALF) for c in COIL_GROOVES]
    for x in samples(start, n0 - 0.1, 1.2, features)[1:]:
        profile.append((x, COIL_R - dips(x, COIL_GROOVES, COIL_GROOVE_HALF, COIL_GROOVE_DEPTH)))
    profile += [(n0 - 0.02, COIL_R - 0.45), (n0 + 0.04, nr + 0.12), (n0 + 0.2, nr + 0.18), (n1 - 0.25, nr + 0.18),
                (n1 - 0.05, nr), (n1, nr - 0.4)]
    obj = lathe_x("coil", profile, None, COIL_Y, COIL_Z, SEGMENTS["coil"])

    def key(poly):
        x = poly.center.x
        if x > n0 - 0.03:
            return "neck"
        if x < start - 0.6:
            return "coil_cap"
        if dips(x, COIL_GROOVES, COIL_GROOVE_HALF, 1.0) > 0.45:
            return "coil_groove"
        return "coil"
    paint(obj, mats, key)
    return k.smooth(obj, 55)


def core(mats):
    """The glowing core between the two necks (one piece across the middle), a little fuller in its
    middle; its sides (facing up and down the screen) its rim colour, its top and bottom its middle's."""
    x1 = -NECK[1] + 0.05
    profile = [(-x1, 0.0)] + [(x, CORE_R + CORE_BULGE * math.cos(math.pi * x / (2 * x1)) ** 2)
                              for x in fine(-x1, x1, 0.45)] + [(x1, 0.0)]
    obj = lathe_x("core", profile, None, COIL_Y, COIL_Z, SEGMENTS["core"])
    paint(obj, mats, lambda p: "rim" if abs(p.normal.y) > 0.62 else "hot")
    return k.smooth(obj, 60)


def webs(mats):
    out = []
    for name, (x0, x1, y0, y1, z0, z1), mat in WEBS:
        out.append(k.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mats[mat]))
    return out


def materials(colours):
    pal = k.level_palette()
    m = {
        "tank": k.material("tank_green", palette=0x29, metallic=0.35, roughness=0.32),
        "band": k.material("tank_band", palette=0x2b, metallic=0.35, roughness=0.3),
        "groove": k.material("tank_groove", palette=0x24, metallic=0.3, roughness=0.45),
        "collar": k.material("tank_collar", palette=0x22, metallic=0.3, roughness=0.5),
        "block": k.material("tank_block", palette=0x5b, metallic=0.4, roughness=0.3),
        "rail": k.material("tank_rail", palette=0x5a, metallic=0.4, roughness=0.3),
        "bumper": k.material("tank_bumper", palette=0x5b, metallic=0.4, roughness=0.28),
        "coil": k.material("tank_coil", palette=0x56, metallic=0.45, roughness=0.32),
        "coil_groove": k.material("tank_coil_groove", palette=0x52, metallic=0.35, roughness=0.5),
        "coil_cap": k.material("tank_coil_cap", palette=0x58, metallic=0.45, roughness=0.3),
        "neck": k.material("tank_neck", palette=0x5a, metallic=0.5, roughness=0.26),
        "cut": k.material("tank_cut", palette=0x52, metallic=0.3, roughness=0.5),
    }
    for key, (index, strength) in colours.items():
        m[key] = k.material(f"tank_core_{key}_{index:x}", palette=index, roughness=0.35, emission=pal[index],
                            emission_strength=strength)
    return m


# --- Cutting into the halves (as polish_redjet.py) ----------------------------------------------------

def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return (1 / 3, 1 / 3, 1 / 3)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    weights = [max(0.0, 1 - v - w), max(0.0, v), max(0.0, w)]
    total = sum(weights) or 1.0
    return [x / total for x in weights]


class NormalSource:
    """An uncut object's shading: its corner normals, looked up at any point of its surface."""

    def __init__(self, obj):
        mesh = obj.data
        mesh.calc_loop_triangles()
        self.verts = [v.co.copy() for v in mesh.vertices]
        self.tris = [(tuple(t.vertices), tuple(t.loops)) for t in mesh.loop_triangles]
        self.normals = [n.vector.copy() for n in mesh.corner_normals]
        self.bvh = BVHTree.FromPolygons(self.verts, [t[0] for t in self.tris])

    def normal(self, co, towards):
        _, _, index, _ = self.bvh.find_nearest(co + (towards - co) * 0.02)
        if index is None:
            return None
        (ia, ib, ic), (la, lb, lc) = self.tris[index]
        w = barycentric(co, self.verts[ia], self.verts[ib], self.verts[ic])
        n = self.normals[la] * w[0] + self.normals[lb] * w[1] + self.normals[lc] * w[2]
        return n.normalized() if n.length > 1e-8 else None


def cut(source, box, cap_mat):
    """The part of an object inside box (x0, x1, y0, y1), its cuts closed with flat caps of cap_mat,
    its normals those of the uncut object. None if nothing is inside."""
    x0, x1, y0, y1 = box
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    if cap_mat.name not in obj.data.materials:
        obj.data.materials.append(cap_mat)
    cap_index = list(obj.data.materials).index(cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
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
                caps |= set(bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"])
    caps = {f for f in caps if f.is_valid}
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    for f in caps:
        f.material_index = cap_index
        f.smooth = False
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    if not any(p.material_index == cap_index for p in obj.data.polygons):
        obj.data.materials.pop(index=cap_index)
    shading = NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def move(objects, dx, dy):
    for obj in objects:
        obj.data.transform(Matrix.Translation((dx, dy, 0)))


def triangles(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        mesh.calc_loop_triangles()
        total += len(mesh.loop_triangles)
        obj.evaluated_get(depsgraph).to_mesh_clear()
    return total


# --- Checks, previews and export ---------------------------------------------------------------------

def shown(objects):
    """Hides every other mesh from renders; returns the ones hidden."""
    hidden = []
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj not in objects and not obj.hide_render:
            obj.hide_render = True
            hidden.append(obj)
    return hidden


def check_mask(mask, label, objects, offset=(0.0, 0.0), supersample=4):
    """Compares the top view of objects with a pixel mask centred on offset: prints the overlap
    (intersection over union) and a map ('#' both, '+' model only, '-' mask only)."""
    import numpy as np
    hidden = shown(objects)
    h, w = len(mask), len(mask[0])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new("silhouette")
    data.type = "ORTHO"
    data.ortho_scale = max(w, h)
    data.clip_end = 1000
    cam = bpy.data.objects.new("silhouette", data)
    cam.location = (offset[0], offset[1], 300)
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "tank_pod_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    covered = alpha.reshape(h, supersample, w, supersample).mean(axis=(1, 3)) > 0.5
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    score = both / max(either, 1)
    print("silhouette overlap %s: %.3f" % (label, score))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    for obj in hidden:
        obj.hide_render = False
    return score


def preview(prefix, objects, size=(24, 28), scale=16, distance=1.0):
    """tyrkit.preview of some objects (top view framed like the sprite, three-quarter view), its
    lights and cameras removed again afterwards."""
    hidden = shown(objects)
    before = set(bpy.data.objects)
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.preview(prefix, size, scale)
    if distance != 1.0:  # the three-quarter view again from farther away
        cam = bpy.data.objects["3q"]
        cam.location = Vector(cam.location) * distance
        bpy.context.scene.render.resolution_x = bpy.context.scene.render.resolution_y = 768
        bpy.context.scene.camera = cam
        bpy.context.scene.render.filepath = prefix + "_3q.png"
        bpy.ops.render.render(write_still=True)
    for obj in set(bpy.data.objects) - before:
        bpy.data.objects.remove(obj)
    for obj in hidden:
        obj.hide_render = False


def export(objects, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_apply=True,
                              export_materials="EXPORT", use_selection=True)
    reverse_winding(path)
    print("exported %s: %.1f KB" % (path, os.path.getsize(path) / 1024))


def whole_mask(sheet):
    """The two sprites' silhouettes side by side: 48 x 28."""
    left, right = k.sprite_mask(sheet, 197), k.sprite_mask(sheet, 199)
    return [left[y] + right[y] for y in range(28)]


# --- Build ------------------------------------------------------------------------------------------

def build_whole(mats):
    for part in (tank(mats), rail(mats), coil(mats)) + tuple(webs(mats)):
        mirror = k.mirror_x(part, part.name + "_r")
        mirror.data.name = mirror.name
        k.smooth(mirror, 55)
    block(mats)  # across the middle
    core(mats)
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    sheets = options.get("check")
    sheet = None
    if sheets:
        sheet = os.path.join(sheets, "enemy_C.png") if os.path.isdir(sheets) else sheets
    for f, (sprites, colours) in enumerate(FRAMES):
        k.reset()
        mats = materials(colours)
        whole = build_whole(mats)
        used = {m.name for o in whole for m in o.data.materials}
        print("== whole ship (C %d + %d): %d triangles, %d objects, %d materials" % (*sprites, triangles(whole),
                                                                                  len(whole), len(used)))
        if sheet and f == 0:
            check_mask(whole_mask(sheet), "whole (197 + 199)", whole)
        if "preview" in options:
            preview(options["preview"] + "tank_pod_whole" + ("" if f == 0 else "_%d" % sprites[0]), whole,
                    size=(48, 28), scale=10, distance=1.15)
        for (name, first, box, centre), sprite in zip(HALVES, sprites):
            model = name if sprite == first else "%s_%d" % (name, sprite)
            pieces = [p for p in (cut(src, box, mats["cut"]) for src in whole) if p is not None]
            move(pieces, -centre, 0.0)
            used = {m.name for o in pieces for m in o.data.materials}
            print("== %s (C %d): %d triangles, %d materials: %s" % (model, sprite, triangles(pieces), len(used),
                                                                   ", ".join(sorted(used))))
            if sheet and f == 0:
                check_mask(k.sprite_mask(sheet, sprite), "%s (C %d)" % (model, sprite), pieces)
            export(pieces, os.path.join(outdir, model + ".glb"))
            if "preview" in options and f == 0:
                preview(options["preview"] + model, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
