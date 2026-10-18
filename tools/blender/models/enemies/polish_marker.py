"""The marker of MARKERS (episode 2 enemy 810, sheet V sprite 8, 2x2: 24 x 28 cell; ground layer, not
animated; about 670 of them line the level; models.cfg: sprite v 8 marker yaw=0).

As the 4x upscale draws it: a symmetric grey metal post on a low base. A raised central housing
(columns 8-15, rows 5-13) carries a bright white light in a channel between two light rails (columns
9 and 14, rows 6-11), closed at the back by a cap (row 6); dark chamfers run down its sides
(columns 8 and 15) and its front slopes down to the base (rows 11-13). Either side of it sits a red
lamp, a rounded block of red glass glowing orange-yellow in its middle, in a dark frame (columns 1-7
and 16-22, rows 7-13). Under them the base (rows 14-20) is a hipped plate: its faces rise from the
edges to the housing's foot and meet along two light diagonal hips that run from there down to the
outer corners of the two feet (row 19); between the feet a notch (columns 8-15, rows 18-20). Just
below the housing a dark slot is cut into the base's front, two small red lights and a grey sensor in
it (row 15).

Origin at the sprite's centre (pixel 12, 14): sprite column c is x = c + 0.5 - 12, row r is
y = 14 - (r + 0.5); +Y up the screen, +Z towards the camera, standing on z = 0.

Polish (2026-10-18): replaces marker.py (a slab, a box and two ellipsoids).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against enemy_V.png sprite 8), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

# --- The base -------------------------------------------------------------------------------------
# A plate over the rectangle SIDE x [FRONT, BACK] (the sprite's outline pixels included; behind y = 0
# it hides under the lamps and the housing) less the notch between the feet (columns 8-15 of rows
# 18-20; its top is the dark row 18).
SIDE = 11.0             # x of its sides (columns 1 and 22)
FRONT, BACK = -7.0, 0.9  # y of its front (the feet's bottom, row 20) and back
NOTCH_X, NOTCH_Y = 3.4, -4.6
BASE_EDGE = 1.0         # the base's height at its edges
BASE_SLOPE = 0.33       # its faces rise this much per pixel towards the housing's foot
HIP_ROUND = 1.1         # the hips' rounding (in pixels across, measured along the faces' rise)
HIP_BAND = 0.5          # the light band along each hip: its half-width
EDGE_ROUND = 0.45       # the rounding of the plate's outer edges
SLOT = (-3.0, 3.0, -2.05, -0.95)  # the dark slot below the housing (row 15, columns 9-14): x0, x1, y0, y1
SLOT_CORNER = 0.35
SLOT_DEPTH = 0.45
SLOT_WALL = 0.12        # its walls' width in plan
SLOT_LIP = 0.3          # the light lip round it
LEDS = (-1.5, 1.5)      # its red lights (columns 10 and 13)


def hip_distance(x, y):
    """The distance (in plan) to the nearer hip: where the side faces (rising towards the middle) meet
    the front face (rising towards the back), the lines y = 4 - |x|."""
    return abs(abs(x) - (SIDE + FRONT - y)) / math.sqrt(2.0)


def edge_distance(x, y):
    """The distance (in plan) to the plate's outer edge: its sides, its front and the notch."""
    u = abs(x)
    d = min(SIDE - u, y - FRONT)
    if y < NOTCH_Y and u < NOTCH_X:
        return 0.0
    if y < NOTCH_Y:
        d = min(d, u - NOTCH_X)
    elif u < NOTCH_X:
        d = min(d, y - NOTCH_Y)
    else:
        d = min(d, math.hypot(u - NOTCH_X, y - NOTCH_Y))
    return d


def slot_distance(x, y):
    """The signed distance to the slot's outline (a rounded rectangle; negative inside)."""
    x0, x1, y0, y1 = SLOT
    hx, hy = (x1 - x0) / 2 - SLOT_CORNER, (y1 - y0) / 2 - SLOT_CORNER
    qx, qy = abs(x - (x0 + x1) / 2) - hx, abs(y - (y0 + y1) / 2) - hy
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - SLOT_CORNER


def base_plane(x, y):
    """The hipped top without its details: the side faces and the front face, the hips between them
    rounded."""
    return BASE_EDGE + BASE_SLOPE * smin(SIDE - abs(x), y - FRONT, HIP_ROUND)


def base_height(x, y):
    z = base_plane(x, y)
    d = edge_distance(x, y)
    if d < EDGE_ROUND:  # the outer edges rounded down to the walls
        t = 1 - d / EDGE_ROUND
        z -= EDGE_ROUND * (1 - math.sqrt(max(0.0, 1 - t * t)))
    s = slot_distance(x, y)
    if s < 0:
        z -= SLOT_DEPTH * min(1.0, -s / SLOT_WALL)
    return z


# --- The housing ----------------------------------------------------------------------------------
HOUSING_X = 4.0         # its half-width (columns 8-15)
HOUSING_Y = (0.0, 9.0)  # from inside the base to its back (row 5)
CHANNEL_Z, RAIL_Z, CAP_Z = 7.2, 7.9, 8.1
# Across the housing (|x|, z): the channel's floor, a rounded rail (columns 9 and 14), the chamfer
# down its side (columns 8 and 15).
U_PROFILE = [(0.0, CHANNEL_Z), (1.9, CHANNEL_Z), (2.08, CHANNEL_Z + 0.1), (2.22, CHANNEL_Z + 0.38),
             (2.38, RAIL_Z - 0.1), (2.65, RAIL_Z), (2.9, RAIL_Z - 0.1), (3.1, RAIL_Z - 0.36), (4.0, RAIL_Z - 1.45)]
CAP_PROFILE = [(0.0, CAP_Z), (2.65, CAP_Z), (2.9, CAP_Z - 0.1), (3.1, CAP_Z - 0.36), (4.0, CAP_Z - 1.45)]
CAP_Y = (7.55, 7.95)    # the channel's back wall up to the cap (row 6)
BACK_ROUND = 0.6
FRONT_Z0 = 3.0          # the front slope (rows 11-13): its height at y = 0, rising
FRONT_RISE = 1.45       # per pixel up the screen
RAIL_X = (2.12, 3.1)    # the rails' light tops, |x|
RAIL_FRONT = 3.15       # where the rails' light ends (the slope cuts them off)
CHANNEL_FRONT = 2.75    # where the channel's floor meets the slope
LENS = (0.0, 5.4)       # the white light (columns 10-13, rows 7-10)
LENS_R = 1.95
LENS_STRETCH = 1.15     # an oval, longer up the screen
LENS_CORE = 1.25        # its white-hot middle

# --- The lamps ------------------------------------------------------------------------------------
LAMP_FRAME = (-11.0, -4.0, -0.2, 7.0)  # the dark frame round the left lamp: x0, x1, y0, y1
LAMP_FRAME_Z = 4.0
LAMP_CORNER = 2.0       # its outer top corner, rounded (rows 7-8)
LAMP = (-7.0, 3.0)      # the red glass (columns 2-7, rows 8-13): its middle
LAMP_HALF = 3.0
LAMP_Z, LAMP_DOME = 4.55, 1.3
HOT = (-7.0, 3.7)       # the glowing middle (rows 9-10, columns 4-5)
LAMP_BANDS = (0.7, 1.45, 2.6)  # the glass's rings round it: radii where its colour changes


def lerp_profile(points, u):
    for (u0, z0), (u1, z1) in zip(points, points[1:]):
        if u <= u1:
            return z0 + (z1 - z0) * (u - u0) / (u1 - u0)
    return points[-1][1]


def smin(a, b, r):
    """A smooth minimum: the crease where two surfaces meet rounded over about r."""
    h = max(r - abs(a - b), 0.0) / r
    return min(a, b) - h * h * r / 4


# --- Building -------------------------------------------------------------------------------------

def mesh_from_bmesh(name, bm):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def paint(obj, mats, key_of):
    """Gives every face the material key_of(polygon) names."""
    mesh = obj.data
    mesh.materials.clear()
    names = []
    slots = []
    for poly in mesh.polygons:
        mat = mats[key_of(poly)]
        if mat.name not in names:
            names.append(mat.name)
            mesh.materials.append(mat)
        slots.append(names.index(mat.name))
    for poly, slot in zip(mesh.polygons, slots):
        poly.material_index = slot


def base(mats):
    """The hipped base plate: a heightfield over a grid whose material borders (the light bands along
    the hips, the slot and its lip) are cut exactly, walls down to the ground round it."""
    near = [0.0, 0.08, 0.2, 0.33]  # grid lines close to the edges, for their rounding
    xs = grid_lines(-SIDE, SIDE, 0.25, [s * (SIDE - e) for s in (-1, 1) for e in near] +
                    [s * (NOTCH_X + e) for s in (-1, 1) for e in near] + [SLOT[0], SLOT[1]])
    ys = grid_lines(FRONT, BACK, 0.25, [FRONT + e for e in near] + [NOTCH_Y + e for e in near] + [SLOT[2], SLOT[3]])
    bm = bmesh.new()
    grid = [[bm.verts.new((x, y, 0.0)) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if abs(cx) < NOTCH_X and cy < NOTCH_Y:
                continue  # the notch
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    # The borders between the materials first, on the flat grid.
    split_along(bm, {v: hip_distance(v.co.x, v.co.y) for v in bm.verts}, HIP_BAND)
    for t in (-SLOT_WALL, 0.0, SLOT_LIP):
        split_along(bm, {v: slot_distance(v.co.x, v.co.y) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co.z = base_height(v.co.x, v.co.y)
    # The walls down to the ground.
    result = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary])
    for v in (e for e in result["geom"] if isinstance(e, bmesh.types.BMVert)):
        v.co.z = 0.0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = mesh_from_bmesh("base", bm)

    def key(poly):
        c = poly.center
        if poly.normal.z < 0.05 and edge_distance(c.x, c.y) < 0.02:
            return "base"  # the walls
        s = slot_distance(c.x, c.y)
        if s < 0:
            return "slot"
        if s < SLOT_LIP:
            return "edge"
        if hip_distance(c.x, c.y) < HIP_BAND and c.y < BACK - 0.3:
            return "edge"
        return "base"
    paint(obj, mats, key)
    mod = obj.modifiers.new("dissolve", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(1.0)
    mod.delimit = {"MATERIAL"}
    return k.smooth(obj, 35)


def housing_height(x, y):
    u = abs(x)
    z = lerp_profile(U_PROFILE, u)
    cap = lerp_profile(CAP_PROFILE, u)
    z += (cap - z) * smoothstep(CAP_Y[0], CAP_Y[1], y)
    back = HOUSING_Y[1] - BACK_ROUND
    if y > back:
        t = min(1.0, (y - back) / BACK_ROUND)
        z -= BACK_ROUND * 1.6 * (1 - math.sqrt(max(0.0, 1 - t * t)))
    return smin(z, FRONT_Z0 + FRONT_RISE * (y - HOUSING_Y[0]), 0.5)


def grid_lines(lo, hi, step, extra=()):
    count = max(1, int(round((hi - lo) / step)))
    values = {round(lo + (hi - lo) * i / count, 4) for i in range(count + 1)}
    values |= {round(v, 4) for v in extra if lo < v < hi}
    out = []
    for v in sorted(values):
        if not out or v - out[-1] > 0.03:
            out.append(v)
    return out


def relief(name, xs, ys, height_of):
    """A part over the rectangle spanned by the grid lines xs and ys: its top height_of(x, y), walls
    down to the ground round it."""
    bm = bmesh.new()
    grid = [[bm.verts.new((x, y, height_of(x, y))) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    ring = ([grid[0][i] for i in range(len(xs))] + [grid[j][-1] for j in range(1, len(ys))] +
            [grid[-1][i] for i in range(len(xs) - 2, -1, -1)] + [grid[j][0] for j in range(len(ys) - 2, 0, -1)])
    low = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in ring]
    n = len(ring)
    for i in range(n):
        bm.faces.new((ring[(i + 1) % n], ring[i], low[i], low[(i + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from_bmesh(name, bm)


def housing(mats):
    """The central housing: a heightfield over its rectangle (the rails, the channel, the cap, the
    chamfers and the front slope), its colours' borders on grid lines."""
    u_lines = [u for u, _ in U_PROFILE] + [u for u, _ in CAP_PROFILE] + [RAIL_X[0], RAIL_X[1], 3.5]
    xs = grid_lines(-HOUSING_X, HOUSING_X, 0.4, [s * u for u in u_lines for s in (-1, 1)])
    ys = grid_lines(HOUSING_Y[0], HOUSING_Y[1], 0.2,
                    [CHANNEL_FRONT, RAIL_FRONT, CAP_Y[0], CAP_Y[1], 7.75, HOUSING_Y[1] - BACK_ROUND])
    obj = relief("housing", xs, ys, housing_height)

    def key(poly):
        c = poly.center
        u = abs(c.x)
        if poly.normal.z < 0.2:
            return "dark" if u > HOUSING_X - 0.05 else "tower"
        if u > RAIL_X[1]:
            return "dark"  # the chamfers down its sides
        if c.y > CAP_Y[0]:
            return "light"  # the cap
        if u > RAIL_X[0]:
            return "light" if c.y > RAIL_FRONT else "channel"
        return "channel"  # the channel's floor and the front slope below it
    paint(obj, mats, key)
    mod = obj.modifiers.new("dissolve", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(2.0)
    mod.delimit = {"MATERIAL"}
    return k.smooth(obj, 38)


def revolve(name, profile, centre, segments=32, sy=1.0):
    """A round part about a vertical axis at centre (x, y): profile [(radius, z)], from its rim in to
    the axis (closed there by a fan); sy stretches it along y."""
    cx, cy = centre
    bm = bmesh.new()
    rings = [[bm.verts.new((cx + r * math.cos(2 * math.pi * s / segments),
                            cy + r * sy * math.sin(2 * math.pi * s / segments), z)) for s in range(segments)]
             for r, z in profile[:-1]]
    for a, b in zip(rings, rings[1:]):
        for s in range(segments):
            bm.faces.new((a[s], a[(s + 1) % segments], b[(s + 1) % segments], b[s]))
    apex = bm.verts.new((cx, cy, profile[-1][1]))
    for s in range(segments):
        bm.faces.new((rings[-1][s], rings[-1][(s + 1) % segments], apex))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from_bmesh(name, bm)


def lens(mats):
    """The white light in the channel: a domed oval lens, white-hot in its middle, in a grey gasket."""
    z = CHANNEL_Z
    profile = [(LENS_R + 0.3, z - 0.1), (LENS_R + 0.3, z + 0.12), (LENS_R + 0.15, z + 0.32), (LENS_R, z + 0.34),
               (LENS_R - 0.12, z + 0.3)]
    profile += [(LENS_R * math.cos(a), z + 0.3 + 0.75 * math.sin(a))
                for a in (math.radians(d) for d in (12, 25, 38, 50, 62, 74, 86))]
    profile += [(0.0, z + 1.05)]
    obj = revolve("lens", profile, LENS, sy=LENS_STRETCH)

    def key(poly):
        r = math.hypot(poly.center.x - LENS[0], (poly.center.y - LENS[1]) / LENS_STRETCH)
        return "tower" if r > LENS_R - 0.05 else "lens_core" if r < LENS_CORE else "lens"
    paint(obj, mats, key)
    return k.smooth(obj, 50)


def rounded_rect(x0, x1, y0, y1, corner, steps=6):
    """The lamp frame's outline, counter-clockwise: a rectangle whose top left corner is rounded."""
    pts = [(x0, y0), (x1, y0), (x1, y1)]
    for i in range(steps + 1):
        a = math.pi / 2 + (math.pi / 2) * i / steps
        pts.append((x0 + corner + corner * math.cos(a), y1 - corner + corner * math.sin(a)))
    return pts


def cushion(centre, half, z0, z1, dome, rounding=1.1, power=4.0, segments=40):
    """The lamp's glass (a bmesh): a block with rounded corners in plan (a superellipse) from z0 up,
    its top edge rounded and its top bulging by `dome` to z1 + dome."""
    cx, cy = centre
    rings = []

    def outline(scale, z):
        return [Vector((cx + math.copysign(abs(math.cos(a)) ** (2 / power), math.cos(a)) * half * scale,
                        cy + math.copysign(abs(math.sin(a)) ** (2 / power), math.sin(a)) * half * scale, z))
                for a in (2 * math.pi * s / segments for s in range(segments))]
    rings.append(outline(1.0, z0))
    rings.append(outline(1.0, z1 - rounding))
    for i in range(1, 5):  # the rounded edge
        a = math.radians(90 * i / 4)
        rings.append(outline(1 - rounding * (1 - math.cos(a)) / half, z1 - rounding + rounding * math.sin(a) +
                             dome * 0.15 * (i / 4) ** 2))
    inner = 1 - rounding / half
    for j in range(1, 7):  # the bulge
        f = 1 - j / 7
        rings.append(outline(inner * f, z1 + dome * 0.15 + dome * 0.85 * (1 - f ** 2)))
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in r] for r in rings]
    n = segments
    for a, b in zip(vs, vs[1:]):
        for s in range(n):
            bm.faces.new((a[s], a[(s + 1) % n], b[(s + 1) % n], b[s]))
    top = bm.verts.new((cx, cy, z1 + dome))
    for s in range(n):
        bm.faces.new((vs[-1][s], vs[-1][(s + 1) % n], top))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def lamp(mats):
    """The left lamp: red glass in a dark frame, glowing orange-yellow in its middle."""
    x0, x1, y0, y1 = LAMP_FRAME
    frame = k.slab("lamp_frame", rounded_rect(x0, x1, y0, y1, LAMP_CORNER), 0.0, LAMP_FRAME_Z, mats["dark"])
    k.bevel(frame, 0.3, 2)
    k.smooth(frame, 40)
    bm = cushion(LAMP, LAMP_HALF, LAMP_FRAME_Z - 0.6, LAMP_Z, LAMP_DOME)
    # The glass's rings of colour round its glowing middle, cut exactly.
    for t in LAMP_BANDS:
        split_along(bm, {v: math.hypot(v.co.x - HOT[0], v.co.y - HOT[1]) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    glass = mesh_from_bmesh("lamp_glass", bm)

    def key(poly):
        r = math.hypot(poly.center.x - HOT[0], poly.center.y - HOT[1])
        if poly.normal.z < 0.25:
            return "lamp_rim"
        return ("lamp_core", "lamp_mid", "lamp", "lamp_rim")[sum(r > b for b in LAMP_BANDS)]
    paint(glass, mats, key)
    mod = glass.modifiers.new("dissolve", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(1.5)
    mod.delimit = {"MATERIAL"}
    k.smooth(glass, 50)
    return frame, glass


def slot_details(mats):
    """In the slot: two small red lights either side of a grey sensor."""
    x0, x1, y0, y1 = SLOT
    cy = (y0 + y1) / 2
    floor = base_height(0.0, cy)  # the slot's floor
    for i, x in enumerate(LEDS):
        k.smooth(k.ellipsoid(f"led{i}", (x, cy, floor), (0.5, 0.42, 0.36), mats["led"], 12, 6), 60)
    k.smooth(k.ellipsoid("sensor", (0.0, cy, floor), (0.85, 0.4, 0.3), mats["edge"], 14, 6), 60)


def materials():
    lp = k.level_palette()
    return {
        "base": k.material("marker_base", palette=0x67, metallic=0.4, roughness=0.4),
        "edge": k.material("marker_edge", palette=0x6b, metallic=0.4, roughness=0.3),
        "tower": k.material("marker_tower", palette=0x68, metallic=0.4, roughness=0.36),
        "channel": k.material("marker_channel", palette=0x6a, metallic=0.4, roughness=0.32),
        "light": k.material("marker_rail", palette=0x6d, metallic=0.4, roughness=0.26),
        "dark": k.material("marker_dark", palette=0x64, metallic=0.35, roughness=0.5),
        "slot": k.material("marker_slot", palette=0x61, metallic=0.2, roughness=0.6),
        "lens": k.material("marker_lens", palette=0x6d, roughness=0.2, emission=lp[0x6d], emission_strength=0.8),
        "lens_core": k.material("marker_lens_core", palette=0x6f, roughness=0.15, emission=lp[0x6f],
                                emission_strength=2.0),
        "lamp_core": k.material("marker_lamp_core", palette=0x7b, roughness=0.2, emission=lp[0x7b],
                                emission_strength=2.4),
        "lamp_mid": k.material("marker_lamp_mid", palette=0x77, roughness=0.2, emission=lp[0x77],
                               emission_strength=1.4),
        "lamp": k.material("marker_lamp", palette=0x74, roughness=0.22, emission=lp[0x74], emission_strength=0.75),
        "lamp_rim": k.material("marker_lamp_rim", palette=0x71, roughness=0.3, emission=lp[0x71],
                               emission_strength=0.3),
        "led": k.material("marker_led", palette=0x75, roughness=0.3, emission=lp[0x75], emission_strength=1.6),
    }


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            obj.evaluated_get(depsgraph).to_mesh_clear()
    return total


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    mats = materials()
    base(mats)
    housing(mats)
    lens(mats)
    for part in lamp(mats):
        k.mirror_x(part, part.name + "_right")
    slot_details(mats)
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== marker (V 8): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_V.png"), 8)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    k.export(os.path.join(outdir, "marker.glb"))
    if "preview" in options:
        k.preview(options["preview"] + "marker")


if __name__ == "__main__":
    build()
