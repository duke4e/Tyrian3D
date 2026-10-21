"""Eye turret (sheet S sprite 269, 2x2: 24 x 28 pixels; the asteroid levels, MINEMAZE, BONUS, ALE),
as the sprite draws it (models.cfg: yaw=0).

A round ground turret: a glossy red glass dome (the eye, the sprite's columns 4-20 of rows 2-19)
set in a dark metal housing whose oval fills the sprite (columns 1-23, rows 0-26). The dome sits
towards the top of the housing; below it the housing's broad front carries a bracket of two ribs
with dark slots beside them (rows 20-25), and two small lugs stand on its rim above the dome
(row 1). A grey metal lens with a dark vertical slit, the pupil, bulges out of the dome's front
(columns 8-16, rows 9-15), looking down the screen. Origin at the sprite's centre (pixel 12, 14).

The damaged look (eye_turret_damaged) is polish_eye_turret_dmg.py's, built from this turret's own
parts with the same bounds, so the turret doesn't change size when it is hit.

Polish (2026-10-18): replaces misc.py's eye_turret (three ellipsoids).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

CENTRE = (0.5, 0.5)                 # the housing's middle (columns 1-23, rows 0-26)
OUTER = (11.2, 13.05, 2.4)          # its outline: half-width, half-depth, superellipse power
DOME_CENTRE = (0.5, 3.0)            # the eye (columns 4-20, rows 2-19)
DOME_RADII = (8.35, 8.85)           # where it meets the housing
LIP = (8.75, 9.25)                  # the inner edge of the housing's lip round it
DOME_BASE, DOME_HEIGHT = 2.7, 5.4   # the dome rises from its socket to 8.1
# The housing from its outline in (t = 0) to the lip (t = 1): (t, inward offset, height). A seam
# runs round its foot; its rim crests near the outline (the sprite's bright column 2) and it
# slopes down into the dome's socket (the dark column 3), ending in a small lip round the dome.
HOUSING = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.55), (0.0, 0.22, 0.65), (0.0, 0.22, 0.85), (0.0, 0.0, 0.95),
           (0.0, 0.0, 1.25), (0.04, 0.0, 2.0), (0.1, 0.0, 2.75), (0.2, 0.0, 3.25), (0.3, 0.0, 3.45),
           (0.45, 0.0, 3.35), (0.65, 0.0, 3.0), (0.85, 0.0, 2.7), (0.92, 0.0, 2.65), (0.96, 0.0, 2.9),
           (0.99, 0.0, 3.0), (1.0, 0.0, 2.8), (1.0, 0.0, 2.0)]
SEGMENTS = 56

PUPIL = (0.5, 1.4, 7.0)             # the lens' centre (columns 8-16, rows 9-15) and radii
PUPIL_RADII = (4.25, 3.5, 3.1)
SLIT_DEPTH, SLIT_WIDTH = 0.16, 0.22  # the groove along the lens
GASKET_SEGMENTS = 26
RIB_MIDDLE = 0.25                   # the bracket on the housing's front (columns 8-15)
RIBS = (RIB_MIDDLE - 2.5, RIB_MIDDLE + 2.5)  # its ribs (columns 9 and 14), a dark slot outside each, x
RIB_TOP, RIB_BOTTOM = -6.35, -10.6  # from the dome's socket up to the rim's crest (rows 20-25), y
LUGS = ((-2.0, 12.55), (3.0, 12.55))  # on the rim above the dome (row 1)


def outline_point(theta, t, inset=0.0):
    """The point at angle theta on the ring t of the housing (0 its outline, 1 the lip), moved
    `inset` further in."""
    c, s = math.cos(theta), math.sin(theta)
    a, b, p = OUTER
    outer = Vector((CENTRE[0] + math.copysign(abs(c) ** (2 / p), c) * a,
                    CENTRE[1] + math.copysign(abs(s) ** (2 / p), s) * b))
    inner = Vector((DOME_CENTRE[0] + c * LIP[0], DOME_CENTRE[1] + s * LIP[1]))
    return outer.lerp(inner, t) + (inner - outer).normalized() * inset


def housing(mat):
    rings = []
    for t, inset, z in HOUSING:
        rings.append([Vector((*outline_point(2 * math.pi * i / SEGMENTS, t, inset), z)) for i in range(SEGMENTS)])
    body = k.loft("housing", rings, mat, start_point=(*CENTRE, 0.0), end_point=(*DOME_CENTRE, 2.0))
    return k.smooth(body, 40)


def dome(mat):
    rings = []
    steps = 9
    for i in range(steps):
        phi = (math.pi / 2) * i / steps
        r = math.cos(phi) ** 0.9  # a little fuller than an ellipse
        z = DOME_BASE + DOME_HEIGHT * math.sin(phi)
        rings.append([Vector((DOME_CENTRE[0] + DOME_RADII[0] * r * math.cos(a), DOME_CENTRE[1] + DOME_RADII[1] * r *
                              math.sin(a), z))
                      for a in (2 * math.pi * j / 44 for j in range(44))])
    # Start below the lip so no gap shows round it.
    base = [Vector((p.x, p.y, DOME_BASE - 0.8)) for p in rings[0]]
    eye = k.loft("eye", [base] + rings, mat, start_point=(*DOME_CENTRE, DOME_BASE - 0.8),
                 end_point=(*DOME_CENTRE, DOME_BASE + DOME_HEIGHT))
    return k.smooth(eye, 50)


def lens(mat, slit_mat):
    """The pupil: an ellipsoid lofted across x whose cross-sections dip in the middle, so a groove
    runs along it (down the screen) between two rounded halves; the groove is dark."""
    cx, cy, cz = PUPIL
    rx, ry, rz = PUPIL_RADII
    xs = sorted({round(cx + rx * math.sin(math.pi * (i / 14 - 0.5)), 3) for i in range(1, 14) if i != 7} |
                {round(cx + d, 3) for d in (-0.45, -0.22, 0.0, 0.22, 0.45)})
    rings = []
    for x in xs:
        u = (x - cx) / rx
        f = math.sqrt(max(0.0, 1 - u * u)) * (1 - SLIT_DEPTH * math.exp(-((x - cx) / SLIT_WIDTH) ** 2))
        rings.append([Vector((x, cy + ry * f * math.cos(a), cz + rz * f * math.sin(a)))
                      for a in (2 * math.pi * j / 22 for j in range(22))])
    obj = k.loft("lens", rings, mat, start_point=(cx - rx, cy, cz), end_point=(cx + rx, cy, cz))
    obj.data.materials.append(slit_mat)
    for face in obj.data.polygons:
        if abs(face.center.x - cx) < 0.25:
            face.material_index = 1
    return k.smooth(obj, 60)


def dome_height(x, y):
    """The dome's surface height at (x, y) (None outside it)."""
    u = math.hypot((x - DOME_CENTRE[0]) / DOME_RADII[0], (y - DOME_CENTRE[1]) / DOME_RADII[1])
    if u >= 1:
        return None
    # r = cos(phi) ** 0.9 at z = base + height * sin(phi)
    phi = math.acos(min(1.0, u ** (1 / 0.9)))
    return DOME_BASE + DOME_HEIGHT * math.sin(phi)


def gasket(mat):
    """A dark ring round the lens where it meets the dome: a tube along the line where the two
    surfaces cross."""
    cx, cy, cz = PUPIL
    rx, ry, rz = PUPIL_RADII
    points = []
    for i in range(GASKET_SEGMENTS):
        a = 2 * math.pi * i / GASKET_SEGMENTS
        # Along the ray from the lens' middle (in plan), the point where the lens' surface sinks
        # under the dome's.
        lo, hi = 0.0, 1.0
        for _ in range(30):
            f = (lo + hi) / 2
            x, y = cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)
            lens_z = cz + rz * math.sqrt(max(0.0, 1 - f * f))
            if lens_z > dome_height(x, y):
                lo = f
            else:
                hi = f
        x, y = cx + rx * lo * math.cos(a), cy + ry * lo * math.sin(a)
        points.append(Vector((x, y, dome_height(x, y))))
    rings = []
    for i, p in enumerate(points):
        t = (points[(i + 1) % GASKET_SEGMENTS] - points[i - 1]).normalized()
        out = Vector((p.x - cx, p.y - cy, 0)).normalized()
        up = t.cross(out).normalized()
        if up.z < 0:
            up = -up
        side = up.cross(t).normalized()
        rings.append([p + side * 0.32 * math.cos(b) + up * 0.22 * math.sin(b)
                      for b in (2 * math.pi * j / 6 for j in range(6))])
    rings.append(rings[0])  # round to the start, welded below
    obj = k.loft("gasket", rings, mat, cap_start=False, cap_end=False)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(obj.data)
    bm.free()
    return k.smooth(obj, 60)


def surface(objects):
    """A function giving the top surface of objects at (x, y), by casting a ray down: the point
    hit and the surface's normal there, or None."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]

    def hit(x, y):
        best = None
        for tree in trees:
            location, normal, _, _ = tree.ray_cast(Vector((x, y, 50.0)), Vector((0, 0, -1)))
            if location is not None and (best is None or location.z > best[0].z):
                best = (location, normal if normal.z > 0 else -normal)
        return best
    return hit


def bar(name, points, ups, half_width, top, bottom, mat, segments=8, power=3.0):
    """A bar along a path on a surface: rounded-box cross-sections across it, their up the
    surface's normal (ups)."""
    rings = []
    n = len(points)
    for i, p in enumerate(points):
        t = (points[min(i + 1, n - 1)] - points[max(i - 1, 0)]).normalized()
        across = t.cross(ups[i]).normalized()
        up = across.cross(t).normalized()
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s = math.cos(a), math.sin(a)
            ring.append(p + across * math.copysign(abs(c) ** (2 / power), c) * half_width +
                        up * math.copysign(abs(s) ** (2 / power), s) * (top if s >= 0 else bottom))
        rings.append(ring)
    ends = [p + up_end * (top - bottom) / 2 for p, up_end in ((points[0], ups[0]), (points[-1], ups[-1]))]
    obj = k.loft(name, rings, mat, start_point=ends[0], end_point=ends[1])
    return k.smooth(obj, 40)


def build():
    k.reset()
    metal = k.material("eyeturret_metal", palette=5, metallic=0.5, roughness=0.4)
    trim = k.material("eyeturret_trim", palette=7, metallic=0.4, roughness=0.45)
    dark = k.material("eyeturret_dark", palette=1, metallic=0.3, roughness=0.7)
    red = k.material("eyeturret_red", palette=116, metallic=0.0, roughness=0.26, emission=(150, 8, 0),
                     emission_strength=0.2)
    steel = k.material("eyeturret_lens", palette=9, metallic=0.6, roughness=0.25)
    slit = k.material("eyeturret_slit", palette=1, metallic=0.2, roughness=0.5)

    body = housing(metal)
    dome(red)

    # The pupil: a grey lens bulging out of the dome's front, split by a dark slit along it, in a
    # dark gasket where it leaves the glass.
    lens(steel, slit)
    gasket(dark)

    # The bracket on the housing's front: two ribs running down it, a dark slot beside each.
    on_body = surface([body])
    for x in RIBS:
        side = 1 if x > RIB_MIDDLE else -1
        for name, dx, hw, top, mat in (("slot", 0.95 * side, 0.42, 0.05, dark), ("rib", 0.0, 0.55, 0.5, trim)):
            hits = [on_body(x + dx, RIB_TOP - (RIB_TOP - RIB_BOTTOM) * i / 8) for i in range(9)]
            hits = [h for h in hits if h is not None]
            bar(f"{name}{x}", [h[0] for h in hits], [h[1] for h in hits], hw, top, 0.3, mat, power=5.0)

    # The lugs on the rim above the dome.
    for i, (x, y) in enumerate(LUGS):
        z = on_body(x, y)[0].z
        k.smooth(k.ellipsoid(f"lug{i}", (x, y, z + 0.1), (0.95, 0.75, 0.6), trim, 12, 6), 50)

    print("triangles:", triangles())
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "eye_turret.glb"))


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


build()
