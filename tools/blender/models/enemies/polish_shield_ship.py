"""The shield ship (sheet 2 sprite 267, 2x2: 24x28 game pixels; models.cfg: sprite 2 267 shield_ship yaw=0).

A grey armoured craft shaped like a heater shield pointing down the screen. Its convex hull runs
from a glossy domed head at the top to the point; down its middle a channel between two raised
rails holds the red twin-bar window, the dark slot below it and a small gold pin, and bronze
collar plates (gold on top of brown) armour its upper corners. A crossbar through the head joins
two tall blade fins standing off the hull's sides: bronze horns curving in at the top, grey along
the sides. Below a seam (the sprite's dark band, row 19) the hull narrows to a keeled point.

The sprite is drawn one pixel left of centre (its axis is pixel column 11): the model is built
about its own axis and moved to x = -0.5. Origin at the sprite's centre (pixel 12, 14); +Y up the
sprite, +Z towards the camera.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

AXIS_X = -0.5   # the sprite's axis (pixel column 11)


# --- Helpers -------------------------------------------------------------------------------------

def chaikin(points, iterations=2, keep=()):
    """Rounds a closed polygon's corners (corner cutting); points listed in `keep` stay sharp."""
    pts = [tuple(p) for p in points]
    sharp = set(tuple(p) for p in keep)
    for _ in range(iterations):
        out = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            if p in sharp:
                out.append(p)
            else:
                out.append((0.75 * p[0] + 0.25 * pts[i - 1][0], 0.75 * p[1] + 0.25 * pts[i - 1][1]))
                out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
        pts = out
    return pts


def resample(points, spacing):
    """A closed polygon resampled to points about `spacing` apart along its outline."""
    n = len(points)
    lengths = [math.dist(points[i], points[(i + 1) % n]) for i in range(n)]
    total = sum(lengths)
    count = max(8, int(round(total / spacing)))
    out, i, walked = [], 0, 0.0
    for c in range(count):
        target = total * c / count
        while walked + lengths[i] < target:
            walked += lengths[i]
            i += 1
        t = (target - walked) / lengths[i] if lengths[i] > 0 else 0.0
        p, q = points[i], points[(i + 1) % n]
        out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def rounded_rect(x0, y0, x1, y1, spacing=0.5):
    """A rectangle with rounded corners, CCW."""
    return resample(chaikin([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 3), spacing)


def facet(name, outline, z0, z1, mat, rim=0.7, steps=3, dome=0.2, dome_rings=2, lift=None, bottom=False):
    """A raised part: the polygon `outline` (CCW, seen from above) standing from z0 to z1, its
    top edge rounded with radius `rim` and its top bulging by `dome` in the middle (rings closing
    in on the centroid: outlines must be star-shaped from it). lift(x, y) raises the top (not the
    bottom), to follow a curved surface. The bottom stays open unless `bottom`."""
    n = len(outline)
    dirs = []
    for i in range(n):
        p0, p1, p2 = Vector(outline[i - 1]), Vector(outline[i]), Vector(outline[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))  # inward for a CCW outline
        m = n1 + n2
        m = m.normalized() if m.length > 1e-6 else n1
        dirs.append(m / max(m.dot(n1), 0.7))
    profile = [(0.0, z0), (0.0, z1 - rim)]
    for i in range(1, steps + 1):
        a = 0.5 * math.pi * i / steps
        profile.append((rim * (1 - math.cos(a)), z1 - rim + rim * math.sin(a)))
    vertices = []
    for inset, z in profile:
        vertices += [(p[0] + d.x * inset, p[1] + d.y * inset, z) for p, d in zip(outline, dirs)]
    inner = vertices[-n:]
    cx, cy = sum(v[0] for v in inner) / n, sum(v[1] for v in inner) / n
    for r in range(1, dome_rings + 1):
        f = 1 - r / (dome_rings + 1)
        vertices += [(cx + (x - cx) * f, cy + (y - cy) * f, z1 + dome * (1 - f * f)) for x, y, _ in inner]
    rings = len(vertices) // n
    faces = []
    for r in range(rings - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((r * n + i, r * n + j, (r + 1) * n + j, (r + 1) * n + i))
    vertices.append((cx, cy, z1 + dome))
    top = (rings - 1) * n
    faces += [(top + i, top + (i + 1) % n, len(vertices) - 1) for i in range(n)]
    if bottom:
        vertices.append((sum(p[0] for p in outline) / n, sum(p[1] for p in outline) / n, z0))
        faces += [((i + 1) % n, i, len(vertices) - 1) for i in range(n)]
    if lift is not None:  # everything but the bottom ring (and the bottom's centre)
        vertices = [(x, y, z + lift(x, y) if n <= i < rings * n + 1 else z) for i, (x, y, z) in enumerate(vertices)]
    obj = k.mesh_object(name, vertices, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def sweep(name, path, section, mat, start_point=None, end_point=None):
    """A part swept along `path` [(x, y, z)]: at each point the cross-section section(i, t)
    gives [(side, up)] offsets (side: to the right of the path's direction in plan, up: +Z)."""
    rings = []
    n = len(path)
    for i, p in enumerate(path):
        a, b = Vector(path[max(i - 1, 0)]), Vector(path[min(i + 1, n - 1)])
        t = Vector((b.x - a.x, b.y - a.y, 0)).normalized()
        side = Vector((t.y, -t.x, 0))
        rings.append([Vector(p) + side * s + Vector((0, 0, u)) for s, u in section(i, i / (n - 1))])
    return k.loft(name, rings, mat, start_point=start_point, end_point=end_point)


def ellipse(cx, cz, w, h, count=12):
    """An elliptical cross-section [(side, up)]."""
    return [(cx + w * math.cos(2 * math.pi * j / count), cz + h * math.sin(2 * math.pi * j / count))
            for j in range(count)]


# --- The ship ----------------------------------------------------------------------------------

# The upper hull, by y (sprite rows 7-19): half-width (the sprite's outline included, less a
# little for the rounded edge) and height of the top above the base (z 0.5).
UPPER = [
    (6.8, 3.4, 1.4),
    (6.4, 4.45, 1.9),
    (5.6, 5.35, 2.2),
    (4.6, 6.3, 2.45),
    (3.5, 6.95, 2.58),
    (2.4, 7.3, 2.62),
    (0.0, 7.35, 2.58),
    (-2.5, 7.35, 2.48),
    (-4.0, 7.2, 2.32),
    (-4.9, 6.95, 2.12),
    (-5.5, 6.55, 1.85),
    (-5.95, 5.7, 1.35),
]

# The keel below the seam, down to the point (rows 19-27): half-width, top height, crest.
LOWER = [
    (-5.25, 6.3, 1.95, 0.3),
    (-6.0, 6.2, 1.9, 0.32),
    (-7.0, 5.7, 1.78, 0.34),
    (-8.0, 5.05, 1.62, 0.34),
    (-9.0, 4.4, 1.45, 0.33),
    (-10.0, 3.7, 1.27, 0.31),
    (-11.0, 2.95, 1.07, 0.28),
    (-12.0, 2.1, 0.85, 0.23),
    (-13.0, 1.15, 0.6, 0.15),
    (-13.8, 0.25, 0.32, 0.04),
]

RAIL_X = 2.1        # the rails either side of the channel with the window and the slot
BASE_Z = 0.5


def lower_at(y):
    """The keel's profile values at y (linear between the LOWER rows)."""
    rows = sorted(LOWER)
    for (y0, *a), (y1, *b) in zip(rows, rows[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return [u + (v - u) * t for u, v in zip(a, b)]
    return rows[0][1:] if y < rows[0][0] else rows[-1][1:]


HULL_POWER = 2.2   # the hull's cross-section: a superellipse, a little boxier than an ellipse


def upper_section(y, half, top):
    """The upper hull's cross-section (the rails are separate ribs on it)."""
    return k.ring(y, half, 1.0, 30, z=BASE_Z, top=top, bottom=BASE_Z, power=HULL_POWER)


def lower_section(y, half, top, crest):
    """The keel's cross-section: an ellipse with a smooth crest along its top."""
    return k.ring(y, half, 1.0, 24, z=BASE_Z, top=top, bottom=BASE_Z, crest=crest)


# The fins' centre line (left fin): the tip leaning in towards the head, the horn curving out
# and down to the vertical blade along the hull's side (pixel column 1).
FIN_PATH = [(-6.2, 11.65), (-6.7, 10.9), (-7.2, 9.85), (-7.5, 8.7), (-7.65, 7.7), (-8.1, 6.85), (-8.85, 6.15),
            (-9.6, 5.35), (-9.95, 4.4), (-10.0, 3.0), (-10.0, 1.0), (-10.0, -1.0), (-10.0, -2.8), (-10.0, -4.2),
            (-10.0, -5.0)]
FIN_BRONZE_Y = 4.0  # above this the fin is bronze (the horn), below it grey


def fin_centre_line():
    """The fin's centre line, resampled smoothly (Catmull-Rom), from the tip down: closely along
    the horn and the ends, sparsely along the straight blade."""
    samples = k.profile(sorted((y, x) for x, y in FIN_PATH), step=0.5)
    line = [(x, y) for y, x in reversed(samples)]
    bottom = line[-1][1]
    keep = [p for i, p in enumerate(line) if p[1] > 3.2 or p[1] < bottom + 1.0 or i % 4 == 0]
    return keep


def blade(cz, w_bottom, w_top, h, count=10, power=2.4):
    """A fin's cross-section: a rounded rectangle (superellipse) h tall (half), narrowing from
    w_bottom to w_top (halves) towards its top edge."""
    out = []
    for j in range(count):
        a = 2 * math.pi * j / count
        c, s = math.cos(a), math.sin(a)
        w = w_bottom + (w_top - w_bottom) * (s + 1) / 2
        out.append((math.copysign(abs(c) ** (2 / power), c) * w, cz + math.copysign(abs(s) ** (2 / power), s) * h))
    return out


def fin_section(y, from_tip, from_bottom):
    """The fin at height y of the sprite: a tall blade, a wedge in section (wide foot, narrow
    rounded top edge), thickest and highest in the horn; both ends round off (arc lengths from
    the tip and the bottom end)."""
    horn = max(0.0, min(1.0, (y - 3.0) / 3.5))
    f = min(1.0, 0.42 + from_tip / 1.4, 0.5 + from_bottom / 0.9)
    cz = 1.8 + 0.5 * horn + 0.35 * (1 - f)
    return blade(cz, (1.45 + 0.12 * horn) * f, (0.42 + 0.1 * horn) * f, (1.75 + 0.3 * horn) * f)


def body_height(x, y):
    """The upper hull's top at (x, y), for parts lying on it."""
    rows = sorted(UPPER)
    for (y0, *a), (y1, *b) in zip(rows, rows[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            half, top = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            return BASE_Z + top * max(0.0, 1 - abs(x / half) ** HULL_POWER) ** (1 / HULL_POWER)
    return BASE_Z


def build():
    k.reset()
    hull_m = k.material("shield_hull", palette=7, metallic=0.3, roughness=0.38)
    keel_m = k.material("shield_keel", palette=6, metallic=0.3, roughness=0.42)
    head_m = k.material("shield_head", palette=10, metallic=0.35, roughness=0.22)
    bar_m = k.material("shield_bar", palette=6, metallic=0.3, roughness=0.36)
    fin_grey = k.material("shield_fin", palette=7, metallic=0.3, roughness=0.34)
    bronze = k.material("shield_bronze", palette=24, metallic=0.45, roughness=0.26)
    gold = k.material("shield_gold", palette=28, metallic=0.45, roughness=0.18)
    brown = k.material("shield_brown", palette=166, metallic=0.35, roughness=0.36)
    seam_m = k.material("shield_seam", palette=3, metallic=0.2, roughness=0.6)
    frame_m = k.material("shield_frame", palette=2, metallic=0.2, roughness=0.4)
    slot_m = k.material("shield_slot", palette=3, metallic=0.25, roughness=0.5)
    red = k.material("shield_red", palette=119, roughness=0.25, emission=(255, 70, 10), emission_strength=1.6)
    pin_m = k.material("shield_pin", palette=27, metallic=0.45, roughness=0.22)
    pin_light = k.material("shield_pin_light", palette=31, roughness=0.3, emission=(255, 235, 170),
                           emission_strength=0.8)

    # The upper hull: a convex shield.
    samples = k.profile(sorted(UPPER), step=0.6)
    hull = k.loft("hull", [upper_section(*s) for s in samples], hull_m,
                  start_point=(0, -6.1, 0.9), end_point=(0, 6.9, 1.2))
    k.smooth(hull, 60)

    # Two rails down its middle, framing the channel with the window, the slot and the pin:
    # rounded ribs lying on the hull, their ends sloping into it.
    rail_path_y = [5.6, 5.25, 4.6, 2.6, 0.4, -1.8, -3.6, -4.3, -4.7]
    for sign, tag in ((1, "l"), (-1, "r")):
        path = [(sign * RAIL_X, y, 0.0) for y in rail_path_y]

        def rib(i, t, path=path):
            x, y, _ = path[i]
            end = min(1.0, 0.35 + min(5.6 - y, y + 4.7) / 1.0)   # 1 along the rib, less towards its ends
            base = body_height(x, y) - 0.25
            width, height = 0.72 * (0.7 + 0.3 * end), 0.25 + 0.55 * end
            out = []
            for j in range(10):
                a = 2 * math.pi * j / 10
                c, s_ = math.cos(a), math.sin(a)
                side = width * math.copysign(abs(c) ** 0.8, c)
                out.append((side, base + height * s_ ** 0.8 if s_ >= 0 else base - 0.2))
            return out
        k.smooth(sweep("rail_" + tag, path, rib, hull_m), 60)

    # The keel: below the seam, narrowing to the point, a crest down its middle.
    samples = k.profile(sorted(LOWER), step=0.6)
    keel = k.loft("keel", [lower_section(*s) for s in samples], keel_m,
                  start_point=(0, -13.95, 0.45), end_point=(0, -5.1, 1.2))
    k.smooth(keel, 45)
    # The seam between them: a dark band hugging the keel where the upper hull ends.
    band = []
    for y, grow in ((-5.4, 0.04), (-5.62, 0.14), (-5.84, 0.14), (-6.06, 0.04)):
        centre = Vector((0.0, y, 0.6))
        band.append([centre + (p - centre) * (1 + grow / max((p - centre).length, 0.1))
                     for p in lower_section(y, *lower_at(y))])
    k.smooth(k.loft("seam", band, seam_m, cap_start=False, cap_end=False), 60)

    # Collar plates on the upper corners: brown armour, a gold plate on it towards the window.
    brown_plate = [(-2.95, 5.4), (-3.0, 2.6), (-3.7, 1.3), (-5.2, 0.9), (-6.6, 1.4), (-7.05, 2.7), (-6.7, 3.9),
                   (-5.6, 4.9), (-4.3, 5.6)]
    gold_plate = [(-2.75, 6.1), (-2.8, 3.1), (-3.4, 2.6), (-4.6, 2.75), (-5.35, 3.6), (-5.2, 4.8), (-4.2, 5.75)]
    for sign, tag in ((1, "l"), (-1, "r")):
        pts = [(sign * x, y) for x, y in brown_plate]
        pts = pts if sign > 0 else pts[::-1]
        facet("collar_" + tag, resample(chaikin(pts, 3), 0.75), 0.75, 0.38, brown, rim=0.3, steps=2, dome=0.06,
              dome_rings=1,
              lift=lambda x, y: body_height(x, y) - 0.1)
        pts = [(sign * x, y) for x, y in gold_plate]
        pts = pts if sign > 0 else pts[::-1]
        facet("collar_gold_" + tag, resample(chaikin(pts, 3), 0.7), 0.75, 0.85, gold, rim=0.32, steps=2, dome=0.1,
              dome_rings=1,
              lift=lambda x, y: body_height(x, y) - 0.1)

    # The window: a dark frame in the channel with two glowing red bars; the dark slot below it.
    floor = lambda x, y: body_height(0.0, y)
    facet("frame", rounded_rect(-1.75, 1.55, 1.75, 5.45, 0.6), 1.0, 0.35, frame_m, rim=0.25, steps=2, dome=0.0,
          dome_rings=0, lift=floor)
    for name, y0 in (("light_top", 4.0), ("light_bottom", 2.05)):
        facet(name, rounded_rect(-1.3, y0, 1.3, y0 + 0.95, 0.45), 1.0, 0.52, red, rim=0.22, steps=2, dome=0.06,
              dome_rings=0, lift=floor)
    facet("slot", rounded_rect(-1.45, -1.15, 1.45, 1.35, 0.6), 1.0, 0.22, slot_m, rim=0.2, steps=2, dome=0.0, dome_rings=0,
          lift=floor)

    # The gold pin below the slot, its top end a small light.
    pin_z = body_height(0.0, -2.6)
    k.smooth(k.ellipsoid("pin", (0.0, -2.65, pin_z + 0.05), (0.42, 1.45, 0.38), pin_m, 10, 8), 60)
    k.smooth(k.ellipsoid("pin_light", (0.0, -1.3, body_height(0.0, -1.3) + 0.12), (0.5, 0.5, 0.4), pin_light, 10, 6),
             60)

    # The head: a glossy dome at the top, on the crossbar.
    k.smooth(k.ellipsoid("head", (0.0, 8.75, 2.2), (3.6, 3.1, 2.35), head_m, 22, 11), 60)

    # The crossbar from fin to fin, through the head, arching a little.
    bar_path = [(x, 8.55, 2.45 + 0.35 * (1 - (x / 7.8) ** 2)) for x in [-7.8 + 15.6 * i / 8 for i in range(9)]]
    bar = sweep("crossbar", bar_path, lambda i, t: [(s * 1.2, z * 0.8) for s, z in ellipse(0, 0, 1, 1, 10)], bar_m)
    k.smooth(bar, 60)

    # The fins: bronze horns curving in at the top, grey blades along the sides.
    line = fin_centre_line()
    lengths = [0.0]
    for p, q in zip(line, line[1:]):
        lengths.append(lengths[-1] + math.dist(p, q))
    split = next(i for i, (_, y) in enumerate(line) if y < FIN_BRONZE_Y)
    for sign, tag in ((1, "l"), (-1, "r")):
        for name, first, last, mat in (("horn", 0, split, bronze), ("blade", split, len(line) - 1, fin_grey)):
            part = line[first:last + 1]
            section = (lambda i, t, first=first: fin_section(line[first + i][1], lengths[first + i],
                                                             lengths[-1] - lengths[first + i]))
            k.smooth(sweep(f"{name}_{tag}", [(sign * x, y, 0.0) for x, y in part], section, mat), 55)

    # Built about the sprite's axis; moved onto it.
    shift = Matrix.Translation((AXIS_X, 0, 0))
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(shift)

    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    depsgraph = bpy.context.evaluated_depsgraph_get()
    print("triangles:", sum(sum(len(p.vertices) - 2 for p in o.evaluated_get(depsgraph).data.polygons)
                            for o in bpy.context.scene.objects if o.type == "MESH"))
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "shield_ship.glb"))


build()
