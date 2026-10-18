"""The blue segmented beetle craft of SOH JIN and MISTAKES (sheet M, sprite 125: 2x2, 24 x 28;
ground layer, not animated; models.cfg: sprite m 125 ship_blue yaw=0).

Polish (2026-10-18), after the 4x upscale: a helmet-like cap at the front whose back edge is cut
back in the middle, a ribbed neck behind it between two dark sockets that each hold two blue
lamps, a wide thorax with three raised ribs (the sprite's highlights in columns 8, 12 and 17),
and a long rounded abdomen with a small teardrop pod on either side. The parts are smooth lofted
shells in the sprite's blues; a dark chassis under them shows in the gaps between the segments,
where the sprite draws its dark lines.

The sprite is symmetric about the boundary of its columns 12 and 13, a pixel right of the
24-pixel box's centre: the model is built about x = 0 and moved there (AXIS_X).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import bpy  # noqa: E402
import tyrkit as k  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

AXIS_X = 1.0  # the sprite's axis of symmetry (model x)
BASE = 0.9    # the height of the shells' rims; their undersides sink into the chassis
BOTTOM = 0.45


def row_y(row):
    """Blender y of the centre of sprite pixel row `row` (the sprite's top is +y)."""
    return 14 - (row + 0.5)


def smooth01(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def end_factor(y, y0, y1, r0, r1):
    """1 inside [y0, y1], falling to 0 at its ends along quarter circles of radius r0 (at y0) and
    r1 (at y1): rounds the ends of a lofted part."""
    if y <= y0 or y >= y1:
        return 0.0
    f = 1.0
    if y - y0 < r0:
        f = min(f, math.sqrt(max(0.0, 1 - (1 - (y - y0) / r0) ** 2)))
    if y1 - y < r1:
        f = min(f, math.sqrt(max(0.0, 1 - (1 - (y1 - y) / r1) ** 2)))
    return f


def samples(y0, y1, count):
    """count values from y0 to y1, closer together near the ends (where the parts round off)."""
    return [y0 + (y1 - y0) * (1 - math.cos(math.pi * i / (count - 1))) / 2 for i in range(count)]


def dome(u, centre, half_width, height, power=2.0):
    """An upper half-superellipse over [centre - half_width, centre + half_width] (0 outside):
    power 2 is an ellipse, higher ones have flatter tops and tighter rims."""
    if half_width <= 1e-3:
        return 0.0
    t = abs(u - centre) / half_width
    return height * (1 - t ** power) ** (1 / power) if t < 1 else 0.0


def smax(a, b, k=0.45):
    """A smooth maximum: the crease where two domes meet becomes a narrow fillet."""
    if min(a, b) <= 0:
        return max(a, b)
    h = max(k - abs(a - b), 0.0) / k
    return max(a, b) + h * h * k / 4


def section(y, half_width, top, n_top=26, n_bottom=4, x=0.0):
    """A cross-section in the XZ plane at y: over the top, z = BASE + top(u) for u from
    +half_width to -half_width (closer together at the rims), then back underneath along a
    shallow curve down to BOTTOM."""
    points = []
    for i in range(n_top + 1):
        t = i / n_top
        u = half_width * (0.6 * math.cos(math.pi * t) + 0.4 * (1 - 2 * t))
        points.append(Vector((x + u, y, BASE + max(0.0, top(u)))))
    for i in range(1, n_bottom):
        t = i / n_bottom
        points.append(Vector((x - half_width * math.cos(math.pi * t), y,
                              BASE - (BASE - BOTTOM) * math.sin(math.pi * t))))
    return points


def shell(name, mat, ys, half_width_at, top_at, n_top=26, angle=50):
    """A part lofted through sections (half_width_at(y), top_at(y) -> top(u)), closed at both
    ends."""
    rings = [section(y, max(half_width_at(y), 0.05), top_at(y), n_top) for y in ys]
    body = k.loft(name, rings, mat, start_point=(0, ys[0] - 0.02, BASE), end_point=(0, ys[-1] + 0.02, BASE))
    return k.smooth(body, angle)


def loft_across(name, rings, mat):
    """A loft along X: rings built with k.ring(x position, depth / 2, height / 2, x=y centre),
    whose X and Y are swapped here."""
    obj = k.loft(name, rings, mat)
    obj.data.transform(Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    k.recalc_normals(obj)
    return obj


# --- The parts ------------------------------------------------------------------------------------

def chassis(mat):
    """The dark underbody: within the parts' rims, but filling the sprite's outline where its dark
    lines run between the segments (round the sockets, between the thorax and the pods)."""
    half = [(-11.9, 0.6), (-11.4, 1.3), (-10.5, 2.1), (-9.0, 3.0), (-7.0, 3.6), (-5.0, 4.6),
            (-3.4, 5.4), (-2.4, 4.4), (-1.5, 5.4), (-0.8, 6.3), (0.0, 6.9), (2.0, 7.1), (3.6, 7.0),
            (4.4, 5.6), (5.2, 5.0), (6.5, 4.7), (8.0, 4.6), (9.0, 4.3), (10.0, 3.6), (11.0, 2.6),
            (11.6, 1.6)]
    rings = [k.ring(y, w, 0.65, 12, z=0.65, power=3.5) for y, w in k.profile(half, step=1.2)]
    body = k.loft("chassis", rings, mat, start_point=(0, -12.05, 0.5), end_point=(0, 11.75, 0.5))
    return k.smooth(body, 50)


def cap(mat):
    """The helmet at the front (sprite rows 2-5): a dome across the craft, rounded in plan like
    a D; its back edge is cut back in the middle (the dark gap under it in row 5)."""
    a = 4.85
    rings = []
    for i in range(15):
        u = -a + 2 * a * (0.03 + 0.94 * i / 14)
        t = abs(u) / a
        front = 8.6 + 3.3 * (1 - t ** 2.6) ** (1 / 2.6)
        back = 8.05 + 0.95 * smooth01((2.7 - abs(u)) / 1.3)
        height = 3.0 * (1 - t ** 2.4) ** 0.45
        rings.append(k.ring(u, (front - back) / 2, height / 2 + 0.3, 16, z=0.65 + height / 2 + 0.3,
                            x=(front + back) / 2, power=2.4))
    return k.smooth(loft_across("cap", rings, mat), 60)


def neck(mat):
    """Behind the cap (rows 5-10): a low block with two raised ribs along it, rising from under
    the cap to the thorax."""
    def top_at(y):
        f = end_factor(y, 2.6, 9.4, 0.5, 0.8)
        rise = smooth01((8.2 - y) / 4.0)
        rib = (1.6 + 1.2 * rise) * f
        block = 0.95 * f

        def top(u):
            return smax(dome(u, 0, 2.25, block), max(dome(u, -1.45, 0.72, rib), dome(u, 1.45, 0.72, rib)), 0.35)
        return top

    return shell("neck", mat, samples(2.6, 9.4, 9), lambda y: 2.25, top_at, n_top=18, angle=60)


def sockets(dark, lamp):
    """The dark sockets either side of the neck (rows 5-9), each with two blue lamps."""
    for side in (-1, 1):
        k.smooth(k.ellipsoid(f"socket{side}", (side * 3.55, 5.9, 1.2), (1.55, 2.7, 1.25), dark, 14, 7), 60)
        # A small lamp (row 7) and a larger one at the socket's outer edge (row 9).
        k.smooth(k.ellipsoid(f"lamp_small{side}", (side * 3.5, row_y(7), 2.15), (0.55, 0.55, 0.42), lamp, 10, 5), 60)
        k.smooth(k.ellipsoid(f"lamp{side}", (side * 3.95, row_y(9) + 0.1, 1.8), (0.95, 0.62, 0.55), lamp, 12, 6), 60)


def thorax(mat):
    """The wide middle (rows 10-15): a raised centre rib and a lower shoulder either side, like
    three fingers hanging from a bar: the front edge runs straight across and the grooves between
    them start shallow behind it and deepen towards the back, where the shoulders round off (row
    14) and the centre rib reaches on to the abdomen."""
    def lobes(y):
        fc = end_factor(y, -2.45, 4.25, 1.1, 1.5)
        fs = end_factor(y, -1.55, 4.25, 2.0, 1.4)
        back = end_factor(y, -1.55, 99, 2.0, 1)  # the shoulders round off in plan at the back only
        wc = 2.45 * (0.55 + 0.45 * fc ** 0.5)
        ws = 2.75 * (0.45 + 0.55 * back ** 0.5) * (0.9 + 0.1 * fs) if fs > 0 else 0.0
        xs = min(4.8, wc + ws - 0.4)  # the plates just touch: a groove runs between them
        hs = (2.7 - 0.5 * smooth01((1.2 - y) / 2.6)) * fs
        return wc, 4.2 * fc, xs, ws, hs

    def half_width(y):
        wc, _, xs, ws, _ = lobes(y)
        return max(wc, xs + ws)

    def top_at(y):
        wc, hc, xs, ws, hs = lobes(y)
        fillet = 0.3 + 1.3 * smooth01((y - 1.6) / 2.4)  # the grooves fade out towards the front

        def top(u):
            return smax(dome(u, 0, wc, hc, 2.4), max(dome(u, -xs, ws, hs, 3.0), dome(u, xs, ws, hs, 3.0)), fillet)
        return top

    return shell("thorax", mat, samples(-2.45, 4.25, 16), half_width, top_at, n_top=30)


def abdomen(mat):
    """The long rounded tail (rows 16-25)."""
    width = k.profile([(-12.0, 0.9), (-11.3, 1.9), (-10.5, 2.6), (-9.5, 3.1), (-8.5, 3.4), (-7.0, 3.6),
                       (-5.0, 3.65), (-3.6, 3.45), (-2.6, 3.0), (-1.7, 2.3)], step=0.05)
    height = k.profile([(-12.0, 0.5), (-11.3, 1.2), (-10.5, 1.8), (-9.0, 2.6), (-7.0, 3.3), (-4.5, 3.6),
                        (-3.0, 3.4), (-2.2, 2.8), (-1.7, 2.0)], step=0.05)

    def at(table, y):
        return min(table, key=lambda p: abs(p[0] - y))[1]

    def top_at(y):
        w, h = at(width, y), at(height, y) * end_factor(y, -12.05, -1.65, 0.6, 0.5)
        return lambda u: h * max(0.0, 1 - abs(u / w) ** 2.3) ** (1 / 2.3)

    return shell("abdomen", mat, samples(-12.05, -1.65, 18), lambda y: at(width, y), top_at, n_top=20)


def pods(mat):
    """The small teardrop pods on the abdomen's sides (rows 17-21), rounded in front, tapering
    back along the body."""
    for side in (-1, 1):
        rings = []
        for y in samples(-7.9, -3.85, 8):
            f = end_factor(y, -8.0, -3.75, 2.9, 0.9)
            t = (y + 8.0) / 4.25  # 0 at the tail end, 1 at the front
            x = side * (3.7 + 0.5 * t)
            rings.append(k.ring(y, 1.1 * f ** 0.7 + 0.02, 1.0 * f + 0.02, 12, z=1.4 + 0.35 * t, x=x))
        k.smooth(k.loft(f"pod{side}", rings, mat), 60)


def tri_count():
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
    k.reset()

    hull = k.material("shipblue_hull", palette=56, metallic=0.35, roughness=0.26)
    light = k.material("shipblue_light", palette=58, metallic=0.35, roughness=0.22)
    dark = k.material("shipblue_dark", palette=49, metallic=0.4, roughness=0.3)
    socket = k.material("shipblue_socket", palette=50, metallic=0.3, roughness=0.42)
    lamp = k.material("shipblue_lamp", palette=154, roughness=0.2, emission=(40, 95, 255), emission_strength=2.4)

    chassis(dark)
    cap(light)
    neck(light)
    sockets(socket, lamp)
    thorax(hull)
    abdomen(hull)
    pods(hull)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
    print("triangles:", tri_count())

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "ship_blue.glb"))


build()
