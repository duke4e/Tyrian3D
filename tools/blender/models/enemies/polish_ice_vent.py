"""The vent in the ice of CAMANIS, ICESECRET and DEEP ICE (sheet 7 sprite 55, 2x2: 24 x 28 pixels; enemy 84 of episodes
3, 4 and 6, ground layer; its animation 55, 55, 93, 131, 93, 55... flares the orb when it fires), polished (2026-10-19;
it replaces wave3_ac.py's ice_vent(), a pixel heightfield of the whole crater with three stacked balls). models.cfg:
model ice_vent / ice_vent_93 / ice_vent_131 ... origin; sprite 7 55 ice_vent yaw=0 ...; frame 7 93 ice_vent_93;
frame 7 131 ice_vent_131.

As the sprite and its upscales draw it: a red-hot orb (columns 8-15 of rows 7-14) in a pit, its yellow-white core at
its upper left, a dark, heat-tinted rim round it (the sprite's greys, browns and dull pinks of columns 7-16), a lip of
white ice round the pit (rows 15-16 below it), and light ridges of ice running out from the lip, down and to the
sides, with dark cracks between them. The rest of the 24 x 28 sprite is CAMANIS' ice plateau, the map's ground: the
model leaves it out (the 3D ground shows it), so its silhouette covers only the vent, not the sprite's whole cell.

Built as a low cone of ice round the orb: one polar mesh (rings round the orb) whose height is the cone, the lip
and the ridges (angular bumps of a few pixels' width tapering out to the cone's edge), falling inside the lip to the
pit's floor; its edge meets the ground (z = 0) and a skirt goes on down to z = -SKIRT, so no gap shows if the model
stands above the terrain (models drawn at their origin stand at the ground enemies' layer height, about 4 pixels up;
height=-4 on the sprite line sets it on the terrain and buries the skirt). The orb sits half sunk in the pit, its
colours cut in along smooth lines (a hot core at its upper left, an orange band round it, red beyond), glowing in
them. The frames 93 and 131 only make the orb hotter (the rim stays): the frame models are the same mesh, the orb's
materials orange with a pale glare (93) and white-hot (131); no other enemy uses those sprites.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14): its column c, row r is (c + 0.5 - 12, 13.5 - r).

Replaces wave3_ac.py's ice vent: remove its section (VENT, ORB, ORB_R, pixel_relief(), which only the vent used, and
ice_vent() with its @a.model("ice_vent", ...) registration), the vent's lines in its docstring and the imports only
it used (math, bmesh, bpy, and k from wave3_ac_kit); and wave3_ac_art.py's CRATER and CRATER_HOT (nothing else reads
them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_7.png), --preview <prefix> (top and 3/4 views of each frame's model).
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

CENTRE = (0.0, 3.0)             # the orb's middle (the sprite's columns 8-15, rows 7-14)
ORB_R, ORB_Z = 4.25, 1.75       # its radius and the height of its middle
PIT_R, PIT_FLOOR = 4.45, 0.35   # the pit's wall foot (radius) and floor
LIP_R, LIP_H, LIP_W = 5.35, 1.45, 0.9    # the lip round the pit: radius, height above the cone, width
EDGE_R, EDGE_DOWN = 9.2, 2.6    # the cone's edge: its radius, reaching this much farther down the screen
CONE_H = 1.0                    # the cone's height at the lip
SKIRT = 4.2
# The ridges of white ice running out from the lip (as the sprite's light pixels lie round the orb), two branching
# off them farther out, as segments from (direction in degrees, 0 right and 90 up the screen; distance from the orb's
# middle) to (direction; distance), with their height and half-width at the start; the branches (start = True)
# grow out of their ridge at full height.
RIDGES = [(-118.0, 4.8, -124.0, 12.2, 1.6, 1.4, False), (-70.0, 4.8, -61.0, 11.8, 1.5, 1.35, False),
          (10.0, 4.8, 2.0, 9.4, 1.1, 1.1, False), (172.0, 4.8, 182.0, 9.6, 1.15, 1.15, False),
          (125.0, 4.8, 118.0, 7.8, 0.7, 0.9, False), (55.0, 4.8, 62.0, 7.4, 0.6, 0.85, False),
          (-121.0, 8.0, -142.0, 11.6, 0.95, 0.9, True), (-66.0, 8.2, -45.0, 11.0, 0.9, 0.85, True)]
# The dark cracks between them (the sprite's darkest ice), likewise: from, to, depth, half-width.
CRACKS = [(-82.0, 6.8, -92.0, 11.2, 0.42, 1.15, False), (-27.0, 6.4, -37.0, 11.0, 0.5, 1.25, False),
          (38.0, 6.4, 45.0, 8.8, 0.3, 0.9, False), (148.0, 6.4, 152.0, 8.6, 0.25, 0.85, False)]
RIDGE_PAINT, CRACK_PAINT = 0.45, 0.5   # the fields' borders between colours
SEGMENTS = 128
# The orb's colours by frame: its body, the band round its core, the core, and their emission strengths; the core's
# direction (from the middle, towards the upper left) and the band's and core's reach (cosine of the angle).
CORE_DIR = Vector((-0.55, 0.45, 0.7)).normalized()
FRAMES = {
    55: dict(body=0x75, band=0x79, core=0x7c, strengths=(1.0, 1.5, 2.2), reach=(0.55, 0.86)),
    93: dict(body=0x79, band=0x7b, core=0x4d, strengths=(1.4, 1.8, 1.6), reach=(0.35, 0.8)),
    131: dict(body=0x7c, band=0x7e, core=0x7f, strengths=(1.8, 2.2, 2.6), reach=(0.1, 0.55)),
}


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def edge_r(theta):
    """The cone's edge radius in the direction theta (longer down the screen, where the ridges run)."""
    return EDGE_R + EDGE_DOWN * max(0.0, -math.sin(theta)) ** 1.5


def polar(angle, r):
    a = math.radians(angle)
    return Vector((r * math.cos(a), r * math.sin(a), 0.0))


def streak(p, seg):
    """How much the point p (from the orb's middle) lies on a streak (a ridge or a crack: (from angle, from
    distance, to angle, to distance, size, half-width, branch)): 1 on its line, falling off across it, narrowing
    towards its end; and how far along it the point is (0-1)."""
    a0, r0, a1, r1, _, w, branch = seg
    p0, p1 = polar(a0, r0), polar(a1, r1)
    d = p1 - p0
    t = max(0.0, min(1.0, (p - p0).dot(d) / d.length_squared))
    dist = (p - (p0 + d * t)).length
    width = w * (1.0 - 0.6 * t)
    ends = (1.0 if branch else smoothstep(0.0, 0.1, t)) * smoothstep(1.0, 0.72, t)
    if not branch and t <= 0.0:
        ends = smoothstep(-0.9, 0.0, (p - p0).dot(d.normalized()))
    return math.exp(-(dist / width) ** 2) * ends, t


def fields(r, theta):
    """The ice at (r, theta) from the orb's middle: its height (the cone, the lip, the ridges, the cracks; inside the
    lip the pit), how much ridge and how much crack it is (0-1)."""
    s = r / edge_r(theta)
    cone = CONE_H * max(0.0, 1.0 - s * s) ** 1.6 / max(1e-3, (1.0 - (LIP_R / edge_r(theta)) ** 2) ** 1.6)
    cone = min(cone, CONE_H * 1.25)
    wobble = 1.0 + 0.16 * math.sin(3 * theta + 0.7) + 0.1 * math.sin(7 * theta + 2.1)
    lip = LIP_H * wobble * math.exp(-((r - LIP_R - 0.12 * math.sin(5 * theta + 1.3)) / LIP_W) ** 2)
    p = Vector((r * math.cos(theta), r * math.sin(theta), 0.0))
    ridge = height = 0.0
    for seg in RIDGES:
        f, t = streak(p, seg)
        h = seg[4] * (1.0 - 0.5 * t) * (1.0 + 0.1 * math.sin(9.0 * t + seg[0]))
        if f * h > height:
            height, ridge = f * h, f
    crack = depth = 0.0
    for seg in CRACKS:
        f, _ = streak(p, seg)
        if f * seg[4] > depth:
            depth, crack = f * seg[4], f
    z = cone + lip + height * smoothstep(PIT_R, LIP_R, r) - depth
    if r < LIP_R:  # the fall into the pit inside the lip
        f = smoothstep(PIT_R - 0.6, LIP_R - 0.15, r)
        z = PIT_FLOOR + (z - PIT_FLOOR) * f
    z *= smoothstep(1.0, 0.85, s)  # down to the ground at the edge
    return max(z, 0.0), ridge, crack


def ring_radii():
    """The rings' radii: dense over the pit's wall and the lip, then out to the edge (for those outside the lip,
    radii of the round EDGE_R, stretched to the edge in each direction)."""
    inner = [2.6, 3.4, 3.9, 4.2, 4.45, 4.7, 4.95, 5.2, 5.45, 5.7, 6.0, 6.35]
    outer = [6.35 + (EDGE_R - 6.35) * (i / 15) ** 0.92 for i in range(1, 16)]
    return inner, outer


def ice(m):
    """The ice cone as one polar mesh, its skirt; its colours cut in along the fields' contours."""
    cx, cy = CENTRE
    inner, outer = ring_radii()
    bm = bmesh.new()
    rows = []
    polar = {}
    for j, r in enumerate(inner + outer):
        row = []
        for i in range(SEGMENTS):
            theta = 2 * math.pi * i / SEGMENTS
            rr = r if j < len(inner) else 6.35 + (r - 6.35) * (edge_r(theta) - 6.35) / (EDGE_R - 6.35)
            z, _, _ = fields(rr, theta)
            v = bm.verts.new((cx + rr * math.cos(theta), cy + rr * math.sin(theta), z))
            row.append(v)
        rows.append(row)
    centre = bm.verts.new((cx, cy, PIT_FLOOR - 0.05))
    for i in range(SEGMENTS):
        bm.faces.new((centre, rows[0][i], rows[0][(i + 1) % SEGMENTS]))
    for j in range(len(rows) - 1):
        for i in range(SEGMENTS):
            a, b = rows[j][i], rows[j][(i + 1) % SEGMENTS]
            c, d = rows[j + 1][(i + 1) % SEGMENTS], rows[j + 1][i]
            bm.faces.new((a, b, c, d))
    # The skirt round the edge, down below the ground.
    last = rows[-1]
    low = [bm.verts.new((v.co.x, v.co.y, -SKIRT)) for v in last]
    for i in range(SEGMENTS):
        bm.faces.new((last[i], low[i], low[(i + 1) % SEGMENTS], last[(i + 1) % SEGMENTS]))
    bm.faces.new(list(reversed(low)))

    def at(co):
        r = math.hypot(co.x - cx, co.y - cy)
        return r, math.atan2(co.y - cy, co.x - cx)
    top = [v for v in bm.verts if v.co.z > -0.01]

    def field(index):
        values = {}
        for v in bm.verts:
            if v.co.z < -0.01:
                values[v] = -1.0
            else:
                values[v] = fields(*at(v.co))[index]
        return values
    # The colours' borders: the pit's wall, the lip's outer foot, the ridges' and cracks' contours.
    for threshold in (PIT_R - 0.3, LIP_R - 0.2, LIP_R + 0.85):
        mk.split_along(bm, {v: (at(v.co)[0] if v.co.z > -0.01 else 99.0) for v in bm.verts}, threshold)
    mk.split_along(bm, field(1), RIDGE_PAINT)
    mk.split_along(bm, field(2), CRACK_PAINT)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        if c.z < -0.02:
            keys.append("ice_dark")
            continue
        r, theta = at(c)
        _, ridge, crack = fields(r, theta)
        if r < PIT_R - 0.3:
            keys.append("scorch_hot")
        elif r < LIP_R - 0.2:
            keys.append("scorch")
        elif r < LIP_R + 0.85:
            keys.append("ice_light")
        elif crack > CRACK_PAINT:
            keys.append("crack")
        elif ridge > RIDGE_PAINT:
            keys.append("ice_white")
        else:
            keys.append("ice")
    mesh = bpy.data.meshes.new("ice")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("ice", mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for poly, key in zip(obj.data.polygons, keys):
        if key not in names:
            names.append(key)
            obj.data.materials.append(m[key])
        poly.material_index = names.index(key)
    return k.smooth(obj, 50)


def orb(m, frame):
    """The orb, half sunk in the pit: a red-hot ball, its colours cut in along smooth lines round its core."""
    cx, cy = CENTRE
    f = FRAMES[frame]
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=18, radius=1.0)
    for v in bm.verts:
        v.co = Vector((cx + v.co.x * ORB_R, cy + v.co.y * ORB_R * 0.96, ORB_Z + v.co.z * ORB_R * 0.92))
    lo, hi = f["reach"]

    def heat(v):
        d = (v.co - Vector((cx, cy, ORB_Z))).normalized()
        return d.dot(CORE_DIR)
    values = {v: heat(v) for v in bm.verts}
    mk.split_along(bm, values, lo)
    values = {v: heat(v) for v in bm.verts}
    mk.split_along(bm, values, hi)
    bmesh.ops.triangulate(bm, faces=[x for x in bm.faces if len(x.verts) > 4])
    mesh = bpy.data.meshes.new("orb")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("orb", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in ("orb_body", "orb_band", "orb_core"):
        obj.data.materials.append(m[key])
    for poly in obj.data.polygons:
        h = (Vector(poly.center) - Vector((cx, cy, ORB_Z))).normalized().dot(CORE_DIR)
        poly.material_index = 2 if h > hi else 1 if h > lo else 0
    k.smooth(obj, 70)
    return obj


def materials(frame):
    glow = k.level_palette()
    f = FRAMES[frame]
    sb, sn, sc = f["strengths"]
    ice_ = dict(metallic=0.1, roughness=0.28)
    return {
        "ice": k.material("vent_ice", palette=0x3b, **ice_),
        "ice_light": k.material("vent_ice_light", palette=0x3d, **ice_),
        "ice_white": k.material("vent_ice_white", palette=0x3e, metallic=0.1, roughness=0.22),
        "ice_dark": k.material("vent_ice_dark", palette=0x39, **ice_),
        "crack": k.material("vent_crack", palette=0x36, metallic=0.1, roughness=0.4),
        "scorch": k.material("vent_scorch", palette=0xa6, metallic=0.2, roughness=0.5),
        "scorch_hot": k.material("vent_scorch_hot", palette=0x46, metallic=0.1, roughness=0.45, emission=glow[0x46],
                                 emission_strength=0.5),
        "orb_body": k.material("vent_orb_%d" % frame, palette=f["body"], metallic=0.0, roughness=0.3,
                               emission=glow[f["body"]], emission_strength=sb),
        "orb_band": k.material("vent_orb_band_%d" % frame, palette=f["band"], metallic=0.0, roughness=0.25,
                               emission=glow[f["band"]], emission_strength=sn),
        "orb_core": k.material("vent_orb_core_%d" % frame, palette=f["core"], metallic=0.0, roughness=0.2,
                               emission=glow[f["core"]], emission_strength=sc),
    }


def build():
    options = k.args()
    out = mk.outdir(options)
    for frame, name in ((55, "ice_vent"), (93, "ice_vent_93"), (131, "ice_vent_131")):
        k.reset()
        m = materials(frame)
        ice(m)
        orb(m, frame)
        objects = mk.meshes()
        bpy.context.scene.view_settings.view_transform = "Standard"
        if "check" in options and frame == 55:
            sheet = os.path.join(options["check"], "enemy_7.png")
            mk.compare("ice_vent (7 55; the sprite's whole cell is ice)", mk.coverage(objects, 24, 28),
                       k.sprite_mask(sheet, 55))
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects)


if __name__ == "__main__":
    build()
