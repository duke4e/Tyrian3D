"""Claw ship (sheet D sprite 121, 2x2: 24 x 28 pixels; ASTEROID1, ASTEROID2), as the sprite draws
it (models.cfg: yaw=0).

A dark gunmetal craft: a rounded dome head at the top of the sprite (rows 0-6) with a red slit
light in a dark visor across its front (row 4), a short ribbed neck (row 7) over a yoke that
carries two long claws reaching down the screen to points that turn inwards (rows 9-25), and a
short prong hanging in the middle under the neck (rows 8-10). Each claw is a blade with a ridge
along its top, arching down to its point, under an armour plate over its broad upper part (rows
11-16) that reaches in towards the other claw and ends in a step across the blade at row 16,
its inner corner a barb (where the sprite's claw narrows). The sprite's craft is centred on
column 10.5, a pixel left of the sprite's centre: the model is built symmetric about x = 0 and
moved by X0 at the end (origin at the sprite's centre, pixel 12, 14). Like talon.py, the plan
keeps about half a pixel inside the sprite's dark outline.

Polish (2026-10-18): replaces later_episodes.py's extruded silhouette (silhouette_ship).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

X0 = -1.0  # the craft's axis: the sprite's columns 3-18 are centred on column 10.5

# The head along y (front to back): half-width, centre height, top and bottom (above and
# below the centre). Its plan follows the sprite's rows 0-6 (with their dark outline); it is
# highest behind the visor, so the visor lies on its front slope, facing the camera.
HEAD = [
    (6.85, 3.2, 3.0, 0.8, 0.9),
    (7.2, 4.8, 3.0, 1.3, 1.3),
    (7.8, 5.6, 3.0, 1.8, 1.45),
    (8.8, 5.95, 3.0, 2.3, 1.5),
    (10.0, 6.0, 3.0, 2.65, 1.5),
    (11.2, 5.7, 3.0, 2.85, 1.45),
    (12.2, 4.85, 3.0, 2.75, 1.35),
    (13.0, 3.7, 3.0, 2.4, 1.15),
    (13.6, 2.4, 3.0, 1.75, 0.9),
    (14.0, 1.2, 3.0, 1.0, 0.6),
]
HEAD_POWER = 2.3
HEAD_SLIM = 0.95  # inside the sprite's dark outline by about half a pixel
HEAD_SAMPLES = k.profile(HEAD, step=0.05)
# The visor: a groove across the head's front slope (the sprite's dark band, columns 8-13 of rows
# 3-5) holding a dark glass plate with the red slit (columns 9-12 of row 4) on it.
VISOR_Y, VISOR_HALF_DEPTH, VISOR_HALF_WIDTH, VISOR_SINK = 9.45, 0.95, 3.0, 0.5
PLATE_HALF_WIDTH, SLIT_HALF_WIDTH = 2.75, 2.0

# The neck under the head's front, along y: half-width, centre height, top, bottom.
NECK = [
    (3.6, 3.3, 2.4, 1.5, 1.3),
    (4.6, 3.15, 2.45, 1.6, 1.3),
    (5.6, 3.0, 2.5, 1.65, 1.3),
    (6.6, 3.05, 2.55, 1.65, 1.3),
    (7.8, 3.4, 2.6, 1.6, 1.3),
]

RIBS = (5.0, 6.15)  # the ribs round the neck (y)
YOKE = (0.0, 5.0, 2.75, 5.0)  # the bar across under the neck carrying the claws: x, y, z, half-length

# The right claw (the left one is its mirror) by rows across it, from its point to its root: y,
# inner edge, ridge, outer edge (x), the height of its middle, the ridge above it and the bottom
# below it. The edges follow the sprite's columns 12-18. The blade is the long point (rows
# 17-25) whose outer edge turns in to the tip, running up to the shoulder; the ridge follows the
# sprite's highlight (column 15) and the blade arches down to its point.
BLADE = [
    (-12.3, 3.75, 3.85, 4.15, 0.75, 0.12, 0.1),
    (-11.8, 3.65, 4.05, 4.4, 0.8, 0.35, 0.25),
    (-11, 3.45, 4.25, 5, 0.9, 0.55, 0.38),
    (-10, 3.4, 4.45, 5.6, 1.05, 0.75, 0.5),
    (-8.8, 3.4, 4.65, 6.25, 1.25, 0.9, 0.6),
    (-7.4, 3.4, 4.85, 7, 1.45, 1.05, 0.7),
    (-5.8, 3.4, 4.95, 7.5, 1.65, 1.2, 0.78),
    (-4.2, 3.4, 5, 7.65, 1.85, 1.3, 0.85),
    (-2, 3.3, 5, 7.65, 2.05, 1.35, 0.9),
    (0.5, 3.1, 4.95, 7.6, 2.3, 1.4, 0.95),
    (2.5, 2.7, 4.7, 7.05, 2.5, 1.45, 1),
    (3.8, 2.05, 4.4, 6.15, 2.65, 1.45, 1),
    (4.6, 2.05, 4.2, 5.35, 2.65, 1.35, 0.95),
    (5.2, 2.6, 4, 4.65, 2.6, 1.05, 0.8),
    (5.55, 3.3, 3.75, 4.05, 2.55, 0.6, 0.5),
]
BLADE_ROOT, BLADE_TIP = (3.8, 5.75, 2.5), (4.0, -12.55, 0.72)
# The armour plate over the blade's broad upper part (rows 11-16), reaching in to the gap
# between the claws; it ends in a step across the claw at row 16, its inner corner a barb.
PLATE = [
    (-3.2, 1.9, 4.65, 7.25, 2, 1.45, 0.55),
    (-3.02, 1.6, 4.65, 7.55, 2.02, 2, 0.7),
    (-2.6, 1.5, 4.7, 7.65, 2.08, 2.12, 0.75),
    (-1, 1.5, 4.7, 7.7, 2.22, 2.2, 0.8),
    (0.6, 1.52, 4.68, 7.6, 2.38, 2.15, 0.82),
    (1.8, 1.6, 4.6, 7.35, 2.5, 2, 0.82),
    (2.8, 1.75, 4.5, 6.85, 2.58, 1.8, 0.82),
    (3.5, 1.95, 4.4, 6.25, 2.62, 1.5, 0.8),
    (3.9, 2.4, 4.35, 5.65, 2.62, 1.1, 0.7),
]
PLATE_ROOT, PLATE_TIP = (4.3, 4.15, 2.6), (4.65, -3.25, 2.0)

# The short prong in the middle under the neck (the sprite's columns 10-11, rows 8-10): x, y,
# centre height, half-width, top, bottom.
PRONG = [
    (0.0, 4.6, 2.1, 1.1, 0.95, 0.75),
    (0.0, 3.4, 1.85, 0.85, 0.7, 0.55),
    (0.0, 2.5, 1.6, 0.4, 0.32, 0.25),
]
PRONG_START, PRONG_TIP = (0.0, 5.2, 2.1), (0.0, 2.0, 1.5)


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic): a function."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2 if d[i - 1] * d[i] > 0 else 0.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a * a + b * b > 9:
            t = 3 / math.sqrt(a * a + b * b)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def f(x):
        i = max(0, min(n - 2, next((j for j in range(n - 1) if x <= xs[j + 1]), n - 2)))
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        return ((2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h * m[i] +
                (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h * m[i + 1])
    return f


def claw_ring(y, inner, ridge, outer, zc, top, bottom, segments=18, p_top=1.5, p_bottom=2.6):
    """A cross-section of the claw in the XZ plane at y: from its inner edge over the ridge to its
    outer edge and back under it (a superellipse split at the ridge)."""
    points = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        c, s = math.cos(a), math.sin(a)
        p = p_top if s >= 0 else p_bottom
        half = (outer - ridge) if c >= 0 else (ridge - inner)
        points.append(Vector((ridge + math.copysign(abs(c) ** (2 / p), c) * half, y,
                              zc + math.copysign(abs(s) ** (2 / p), s) * (top if s >= 0 else bottom))))
    return points


def claw_part(name, table, mat, root, tip, fine=(), step=0.7, segments=16, p_top=1.15):
    """A loft of claw_ring cross-sections through a table of rows (smoothly between them), every
    `step` along y, or every step / 2 inside the y ranges of `fine`."""
    columns = list(zip(*table))
    curves = [monotone(columns[0], column) for column in columns[1:]]
    ys, y = [], table[0][0]
    while y < table[-1][0] - 0.05:
        ys.append(y)
        y += step / 2 if any(a < y < b for a, b in fine) else step
    ys.append(table[-1][0])
    rings = [claw_ring(y, *(f(y) for f in curves), segments=segments, p_top=p_top) for y in ys]
    return k.loft(name, rings, mat, start_point=tip, end_point=root)


def section(half_width, top, bottom, segments, p_top=2.0, p_bottom=2.0):
    """A cross-section's points (across, up), counter-clockwise: a superellipse with its own
    power above and below (below 2 the top comes to a ridge)."""
    points = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        c, s = math.cos(a), math.sin(a)
        p = p_top if s >= 0 else p_bottom
        points.append((math.copysign(abs(c) ** (2 / p), c) * half_width,
                       math.copysign(abs(s) ** (2 / p), s) * (top if s >= 0 else bottom)))
    return points


def sweep(name, points, ups, sizes, mat, segments=12, p_top=2.0, p_bottom=2.0, start=None, end=None):
    """A hull along a 3D path: at each point a cross-section (half-width, top, bottom) stands
    across the path, its up towards ups[i]."""
    rings = []
    n = len(points)
    for i in range(n):
        t = (points[min(i + 1, n - 1)] - points[max(i - 1, 0)]).normalized()
        across = t.cross(ups[i]).normalized()
        up = across.cross(t).normalized()
        hw, top, bottom = sizes[i]
        rings.append([points[i] + across * u + up * v for u, v in section(hw, top, bottom, segments, p_top, p_bottom)])
    return k.loft(name, rings, mat, start_point=start, end_point=end)


def plan_sweep(name, control, mat, segments=16, step=0.8, **options):
    """A hull along a smooth path through control points (x, y, z, half-width, top, bottom),
    its cross-sections standing upright across the path."""
    t, previous, keyed = 0.0, None, []
    for c in control:
        if previous is not None:
            t += math.dist(c[:2], previous[:2])
        keyed.append((t, *c))
        previous = c
    samples = [s[1:] for s in k.profile(keyed, step=step)]
    return sweep(name, [Vector(s[:3]) for s in samples], [Vector((0, 0, 1))] * len(samples),
                 [s[3:] for s in samples], mat, segments, **options)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def head_profile(y):
    """The head's (half-width, centre height, top, bottom) at y."""
    return min(HEAD_SAMPLES, key=lambda s: abs(s[0] - y))[1:]


def head_top(x, y):
    """The height of the head's top surface (before the visor groove) at (x, y)."""
    hw, zc, top, _ = head_profile(y)
    hw *= HEAD_SLIM
    f = min(1.0, abs(x) / hw)
    return zc + top * (1 - f ** HEAD_POWER) ** (1 / HEAD_POWER)


def head_normal(x, y):
    e = 0.05
    dx = (head_top(x + e, y) - head_top(x - e, y)) / (2 * e)
    dy = (head_top(x, y + e) - head_top(x, y - e)) / (2 * e)
    return Vector((-dx, -dy, 1.0)).normalized()


def on_head(name, half_width, sink, size, mat, segments, ends=0.3, count=9):
    """A bar lying across the head's front slope at the visor (plate, slit), following its curve
    `sink` below the surface; size: (half-depth, top, bottom) of its cross-section."""
    xs = [-half_width + 2 * half_width * i / (count - 1) for i in range(count)]
    points = [Vector((x, VISOR_Y, head_top(x, VISOR_Y))) - head_normal(x, VISOR_Y) * sink for x in xs]
    ups = [head_normal(x, VISOR_Y) for x in xs]
    tip = lambda x: Vector((x, VISOR_Y, head_top(x, VISOR_Y))) - head_normal(x, VISOR_Y) * sink
    bar = sweep(name, points, ups, [size] * count, mat, segments, p_top=3.0, p_bottom=3.0,
                start=tip(-half_width - ends), end=tip(half_width + ends))
    return k.smooth(bar, 60)


def build():
    k.reset()
    metal = k.material("claw_metal", palette=8, metallic=0.45, roughness=0.24)
    joint = k.material("claw_joint", palette=7, metallic=0.5, roughness=0.35)
    glass = k.material("claw_visor", palette=2, metallic=0.2, roughness=0.12)
    slit = k.material("claw_slit", palette=119, roughness=0.3, emission=(255, 45, 8), emission_strength=3.0)

    # The head: a helmet with the visor's groove pressed into its front slope.
    samples = k.profile(HEAD, step=0.45)
    rings = [k.ring(y, hw * HEAD_SLIM, 1.0, 26, z=zc, top=top, bottom=bottom, power=HEAD_POWER)
             for y, hw, zc, top, bottom in samples]
    head = k.loft("head", rings, metal, start_point=(0, 6.7, 3.1), end_point=(0, 14.15, 3.3))
    for v in head.data.vertices:
        p = v.co
        if p.z <= 3.0:
            continue
        w = ((1 - smoothstep(VISOR_HALF_DEPTH, VISOR_HALF_DEPTH + 0.45, abs(p.y - VISOR_Y))) *
             (1 - smoothstep(VISOR_HALF_WIDTH, VISOR_HALF_WIDTH + 0.6, abs(p.x))))
        if w > 0:
            v.co = p - head_normal(p.x, p.y) * VISOR_SINK * w
    k.smooth(head, 50)

    # The visor: a dark glass plate in the groove, the red slit on it.
    on_head("visor", PLATE_HALF_WIDTH, 0.42, (0.85, 0.22, 0.25), glass, 12)
    on_head("slit", SLIT_HALF_WIDTH, 0.24, (0.32, 0.16, 0.16), slit, 10, ends=0.2)

    # The neck under the head's front, ringed by two ribs, and the yoke across under it that
    # carries the claws (the sprite's row 8).
    samples = k.profile(NECK, step=0.6)
    neck = k.loft("neck", [k.ring(y, hw, 1.0, 16, z=zc, top=top, bottom=bottom, power=2.6)
                           for y, hw, zc, top, bottom in samples], joint)
    k.smooth(neck, 50)
    neck_samples = k.profile(NECK, step=0.05)
    for i, y in enumerate(RIBS):
        hw, zc, top, bottom = min(neck_samples, key=lambda s: abs(s[0] - y))[1:]
        rib = k.loft(f"rib{i}", [k.ring(y + dy, hw + grow, 1.0, 16, z=zc, top=top + grow, bottom=bottom + grow,
                                        power=2.6)
                                 for dy, grow in ((-0.32, -0.05), (-0.2, 0.22), (0.2, 0.22), (0.32, -0.05))],
                     metal, cap_start=False, cap_end=False)
        k.smooth(rib, 50)
    length = YOKE[3]
    yoke = k.lathe("yoke", [(-length, 0.0), (-length + 0.08, 0.6), (-length + 0.4, 0.95), (-length + 0.9, 1.05),
                            (length - 0.9, 1.05), (length - 0.4, 0.95), (length - 0.08, 0.6), (length, 0.0)],
                   joint, segments=14, squash=1.1)
    yoke.data.transform(Matrix.Translation(YOKE[:3]) @ Matrix.Rotation(math.radians(90), 4, "Z"))
    k.smooth(yoke, 50)

    # The claws: the blade and the plate over it.
    for side in (1, -1):
        parts = [claw_part("blade", BLADE, metal, BLADE_ROOT, BLADE_TIP, step=0.85),
                 claw_part("plate", PLATE, metal, PLATE_ROOT, PLATE_TIP, fine=((-3.3, -2.4),), step=0.65)]
        for part in parts:
            k.smooth(part, 32)
            if side < 0:
                part.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
                part.data.flip_normals()
            part.name += "_r" if side > 0 else "_l"

    prong = plan_sweep("prong", PRONG, joint, segments=12, step=0.5, p_top=1.7, start=PRONG_START, end=PRONG_TIP)
    k.smooth(prong, 50)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((X0, 0, 0)))

    print("triangles:", triangles())
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "claw_ship.glb"))


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
