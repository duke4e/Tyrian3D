"""The eye in the glowing ring (sheet C sprite 165, 2x2: 24 x 28 pixels; BONUS, the ground layer;
models.cfg: sprite c 165 eye_ring yaw=0). Its animation (165, 167, 169, 167, 165) only brightens the
ring, two shades a frame: one model, the ring glowing at the middle frame's colours.

A blue eye lies between two glowing crescent lids, open: the sprite's columns 4-19 of rows 9-18
are a glossy blue almond (an iris), split down the middle by a dark groove holding a pink, faintly
glowing slit pupil (columns 10-13); each of its halves bulges like a lens. Above and below it two
crescents (rows 0-11 and 16-27) curve round to near meet at the sides, a broken ring of molten red:
fat in the middle (seven pixels at the top), tapering to blunt tips beside the eye's corners, their
crest a hot orange-yellow line nearer their outer edge, their inner flank sloping gently down to
the gap round the eye (the dark pixels along their inner edge), a little tongue in the middle of
each inner edge. The ground shows between lids and eye, as in the sprite.

Both are symmetric about the sprite's middle (pixel 12, 14), the origin: the lower lid is the upper
one mirrored. Ground objects stand on z = 0.

Polish (2026-10-18): replaces later_episodes.py's eye_ring (a torus round a disc).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

# The lids' outer edge: a superellipse (half-width, half-height, power) round the whole sprite.
OUTER = (11.95, 13.95, 2.5)
# The upper lid's inner edge, its right half from the middle to the tip, (x, y): a small tongue
# in the middle (columns 10-13 reach row 6), up to row 5 beside it, down round the eye's corner.
INNER = [(0.0, 7.05), (1.0, 7.1), (1.8, 7.45), (2.6, 7.9), (3.6, 8.05), (4.6, 8.0), (5.6, 7.75), (6.4, 7.25),
         (7.2, 6.45), (8.0, 5.45), (8.7, 4.4), (9.1, 3.5), (9.35, 2.8), (9.6, 2.2), (9.9, 1.8)]
TIP = 9.0          # the lids end here (degrees from the x axis), rounded from CAP on: blunt tips
CAP = 17.0         # three pixels wide down to row 10, as in the sprite
SECTIONS = 40      # along a lid
CREST = 0.6        # where across the lid its crest lies (0 inner edge, 1 outer)
SPREAD = (0.3, 0.17)        # how fast its glow falls off down the inner and the outer flank
LEVELS = (0.2, 0.55, 0.86)  # the glow where the body, the crest line and the hot line begin
# The faces across a lid, inner edge to outer (section_s): edge, body, crest, hot, crest, body, edge.
BANDS = [0, 0, 0, 1, 1, 2, 3, 3, 2, 1, 1, 0, 0, 0]

# The eye: a superellipse almond (half-width, half-height, power), its height, the groove.
EYE = (8.15, 5.1, 2.8)
EYE_HEIGHT = 4.0
GROOVE = (0.3, 1.05)  # depth (a fraction of the height) and half-width of the groove down its middle
GROOVE_EDGE = 1.5     # its dark walls, out to this x
BEZEL = (0.42, 0.5)   # the dark ring round the eye's foot: half-width, half-height
PUPIL = (0.78, 0.45)  # the slit pupil's half-width and half-height


def superellipse_radius(theta, a, b, p):
    """The distance from the centre to a superellipse along the direction theta."""
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    return ((c / a) ** p + (s / b) ** p) ** (-1 / p)


def inner_radius_table():
    """The inner edge as (angle, radius) pairs, smoothed and sorted by angle (0-90 degrees)."""
    pairs = sorted((math.atan2(y, x), math.hypot(x, y)) for x, y in INNER)
    return k.profile(pairs, step=math.radians(0.5))


def lerp_table(table, x):
    if x <= table[0][0]:
        return table[0][1]
    for (x0, v0), (x1, v1) in zip(table, table[1:]):
        if x <= x1:
            return v0 + (v1 - v0) * (x - x0) / (x1 - x0)
    return table[-1][1]


def lid_profile(s):
    """The lid's height across it (s: 0 inner edge, 1 outer), 0-1: its crest at CREST, rounded
    down to both edges, steeper outside."""
    gamma = math.log(0.5) / math.log(CREST)
    return math.sin(math.pi * min(1.0, max(0.0, s)) ** gamma) ** 0.62


def along(theta):
    """How hot the lid's glow is along it: hottest in the middle, a little cooler at the tips."""
    return 0.72 + 0.28 * max(0.0, math.cos(1.6 * (theta - math.pi / 2)))


def section_s(theta):
    """Where the points of the section at theta lie across the lid (0 inner edge, 1 outer): on the
    edges of the glow's bands, so that the bands run smoothly along the lid. The glow is
    exp(-((s - CREST) / spread) ** 2) * along(theta), falling off more slowly down the broad inner
    flank than down the outer one; each band begins where it reaches its level (LEVELS)."""
    a = along(theta)

    def reach(level, spread):
        return spread * math.sqrt(math.log(a / level)) if a > level + 0.004 else 0.004

    (b_in, b_out), (c_in, c_out), (h_in, h_out) = [(CREST - reach(level, SPREAD[0]), CREST + reach(level, SPREAD[1]))
                                                   for level in LEVELS]
    b_in, b_out = max(b_in, 0.12), min(b_out, 0.9)
    return [0.0, b_in * 0.35, b_in * 0.7, b_in, (b_in + c_in) / 2, c_in, h_in, CREST, h_out, c_out,
            (c_out + b_out) / 2, b_out, b_out + (1 - b_out) * 0.4, b_out + (1 - b_out) * 0.75, 1.0]


def lid(name, edge, body, crest, hot):
    """The upper lid: sections along rays from the middle, from the right tip over the top to the
    left one. Each runs over the top from the inner edge to the outer, then back underneath."""
    table = inner_radius_table()
    rings, angles = [], []
    for i in range(SECTIONS):
        t = i / (SECTIONS - 1)  # tip to tip, closer together near the tips
        angles.append(math.radians(TIP) + (math.pi - 2 * math.radians(TIP)) * (t - 0.11 * math.sin(2 * math.pi * t)))
    for theta in angles:
        side = min(theta, math.pi - theta)  # the angle from the nearer tip's side
        r_out = superellipse_radius(theta, *OUTER)
        r_in = lerp_table(table, side)
        middle, half = (r_out + r_in) / 2, (r_out - r_in) / 2
        cap = 1.0
        if side < math.radians(CAP):  # the rounded tip
            u = (math.radians(CAP) - side) / math.radians(CAP - TIP)
            cap = math.sqrt(max(0.0, 1 - u * u))
        height = (0.62 * min(r_out - r_in, 7.0) ** 0.92 + 0.3) * max(cap, 0.04) ** 0.8
        half *= max(cap, 0.04)
        d = Vector((math.cos(theta), math.sin(theta), 0))
        ring = []
        for s in section_s(theta):  # over the top
            ring.append(d * (middle + half * (2 * s - 1)) + Vector((0, 0, height * lid_profile(s))))
        for s in (0.8, 0.5, 0.2):  # back underneath
            ring.append(d * (middle + half * (2 * s - 1)) + Vector((0, 0, -0.05)))
        rings.append(ring)
    tip = lambda theta: Vector((math.cos(theta), math.sin(theta), 0)) * \
        ((superellipse_radius(theta, *OUTER) + lerp_table(table, min(theta, math.pi - theta))) / 2) + Vector((0, 0, 0.25))
    obj = k.loft(name, rings, edge, start_point=tip(math.radians(TIP) - 0.01),
                 end_point=tip(math.pi - math.radians(TIP) + 0.01))
    for mat in (body, crest, hot):
        obj.data.materials.append(mat)
    n = len(rings[0])
    for poly in obj.data.polygons[:(len(rings) - 1) * n]:
        column = poly.index % n
        if column < len(BANDS):
            poly.material_index = BANDS[column]
    return k.smooth(obj, 60)


def eye_surface(x, y):
    """The eye's height at (x, y) (0 outside): a dome on the almond, the groove down its middle."""
    a, b, p = EYE
    rho = ((abs(x) / a) ** p + (abs(y) / b) ** p) ** (1 / p)
    if rho >= 1:
        return 0.0
    dome = (1 - rho ** 2.2) ** 0.55
    return EYE_HEIGHT * dome * (1 - GROOVE[0] * math.exp(-(x / GROOVE[1]) ** 2))


def eye(name, blue, groove):
    """The eye, lofted across x: each section a curve over the top in y, back underneath."""
    a, b, p = EYE
    xs = sorted({round(a * math.sin(math.pi / 2 * (2 * i / 26 - 1)), 4) for i in range(1, 26)} |
                {-1.5, -1.1, -0.7, -0.35, 0.0, 0.35, 0.7, 1.1, 1.5})
    rings = []
    for x in xs:
        half = b * max(0.0, 1 - (abs(x) / a) ** p) ** (1 / p)
        ring = []
        for j in range(13):  # over the top, y from -half to +half
            y = half * math.sin(math.pi / 2 * (2 * j / 12 - 1))
            ring.append(Vector((x, y, max(eye_surface(x, y * 0.999), 0.0))))
        for j in (0.5, 0.0, -0.5):
            ring.append(Vector((x, half * j, -0.05)))
        rings.append(ring)
    obj = k.loft(name, rings, blue, start_point=(-a, 0, 0.1), end_point=(a, 0, 0.1))
    obj.data.materials.append(groove)
    for poly in obj.data.polygons:
        if abs(poly.center.x) < GROOVE_EDGE and poly.normal.z > 0:
            poly.material_index = 1
    return k.smooth(obj, 60)


def bezel(name, mat):
    """A dark ring round the eye's foot (the sprite's dark blue outline round the eye)."""
    a, b, p = EYE
    count = 48
    outline = []
    for i in range(count):
        t = 2 * math.pi * i / count
        c, s = math.cos(t), math.sin(t)
        outline.append(Vector((math.copysign(abs(c) ** (2 / p), c) * a, math.copysign(abs(s) ** (2 / p), s) * b, 0)))
    rings = []
    for i, point in enumerate(outline + outline[:1]):
        tangent = (outline[(i + 1) % count] - outline[i - 1]).normalized()
        out = Vector((tangent.y, -tangent.x, 0))  # the outline runs counter-clockwise
        rings.append([point + out * (BEZEL[0] * math.cos(u) - 0.12) + Vector((0, 0, BEZEL[1] * (1 + math.sin(u))))
                      for u in (2 * math.pi * j / 6 for j in range(6))])
    obj = k.loft(name, rings, mat, cap_start=False, cap_end=False)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)  # the last ring onto the first
    bm.to_mesh(obj.data)
    bm.free()
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def pupil(name, mat):
    """The slit pupil lying in the groove, following the eye's curve: brightest at its upper middle."""
    a, b, p = EYE
    rings = []
    count = 15
    for i in range(count):
        y = b * 0.97 * math.sin(math.pi / 2 * (2 * i / (count - 1) - 1))
        z = eye_surface(0.0, y)
        f = math.sqrt(max(0.0, 1 - (abs(y) / (b * 0.97)) ** 6))  # rounded ends
        rings.append(k.ring(y, PUPIL[0] * max(f, 0.2), PUPIL[1] * max(f, 0.2), 10, z=z - 0.12))
    obj = k.loft(name, rings, mat, start_point=(0, -b * 0.99, eye_surface(0, -b * 0.97) - 0.1),
                 end_point=(0, b * 0.99, eye_surface(0, b * 0.97) - 0.1))
    return k.smooth(obj, 60)


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


def build():
    k.reset()
    edge = k.material("eyering_lid_edge", palette=115, metallic=0.0, roughness=0.6, emission=(110, 6, 0),
                      emission_strength=0.55)
    body = k.material("eyering_lid", palette=118, metallic=0.0, roughness=0.55, emission=(205, 28, 0),
                      emission_strength=0.7)
    crest = k.material("eyering_lid_crest", palette=121, metallic=0.0, roughness=0.45, emission=(240, 100, 12),
                       emission_strength=0.9)
    hot = k.material("eyering_lid_hot", palette=123, metallic=0.0, roughness=0.4, emission=(255, 180, 45),
                     emission_strength=1.1)
    blue = k.material("eyering_iris", palette=59, metallic=0.25, roughness=0.16)
    rim = k.material("eyering_bezel", palette=54, metallic=0.3, roughness=0.3)
    groove = k.material("eyering_groove", palette=51, metallic=0.2, roughness=0.4)
    slit = k.material("eyering_pupil", palette=75, metallic=0.0, roughness=0.2, emission=(255, 90, 70),
                      emission_strength=0.55)

    upper = lid("lid_upper", edge, body, crest, hot)
    lower = k.mirror_x(upper, "lid_lower")  # mirrored across x, then turned half round: across y
    lower.data.transform(Matrix.Rotation(math.pi, 4, "Z"))
    lower.data.name = "lid_lower"
    eye("eye", blue, groove)
    bezel("bezel", rim)
    pupil("pupil", slit)

    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    print("triangles:", triangles())
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "eye_ring.glb"))


build()
