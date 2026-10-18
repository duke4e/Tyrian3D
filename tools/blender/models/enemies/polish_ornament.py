"""The golden ornament (sheet D sprite 79, 2x2: 24x28 game pixels; models.cfg: sprite d 79 ornament yaw=0).

A cast-gold heraldic brooch lying face up: a dark backing plate in the sprite's outline carries
carved, bevelled facets; raised bright ridges form an X across it, the upper arms from the tips of
the upper lobes down to a round bezel holding a blue cabochon gem in the lower centre, the lower
arms from the bezel's flanks out to the sides. A hanging ring (loop) rises at the top centre,
between the lobes, over a dark socket (the sprite's dark hole). Engraved scrolls curl on the upper
wings, as in the upscale. The animation (frames 79, 81, 83) only makes the gem glint.

Facets, from the sprite's light and dark lines: the two upper wings, the recessed top centre
between the upper arms (under the loop), two lower side facets below the lower arms and the lower
centre lobe down to the point, with grooves at the sprite's dark lines. Origin at the sprite's
centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


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


def smooth_outline(points, spacing=1.1, keep=()):
    return resample(chaikin(points, 2, keep), spacing)


def mirrored(left_half):
    """A symmetric CCW polygon from its left half, listed from the top centre down to the bottom
    centre (x <= 0); points on the axis are not repeated."""
    right = [(-x, y) for x, y in reversed(left_half) if abs(x) > 1e-6]
    return left_half + right


def mirror_points(points):
    """The mirror image of a CCW polygon across X, still CCW."""
    return [(-x, y) for x, y in reversed(points)]


def facet(name, outline, z0, z1, mat, rim=0.7, steps=3, dome=0.2, dome_rings=2, lift=None, bottom=False):
    """A carved facet: the polygon `outline` (CCW, seen from above) standing from z0 to z1, its
    top edge rounded with radius `rim` (inset rings) and its top bulging by `dome` in the middle
    (rings closing in on the centroid: outlines must be star-shaped from it). lift(x, y) raises
    everything above the bottom ring (z0 stays as given; heights above it are relative to the
    lift) for tilted or curved facets. The bottom stays open (sunk into a plate) unless `bottom`."""
    n = len(outline)
    # Inset directions: the corner bisectors, scaled so that straight edges move by the inset
    # (miter), limited at sharp corners so that they don't shoot out.
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


def revolve(name, profile, centre, mat, segments=24, closed=False, sx=1.0, sy=1.0):
    """A round part about a vertical axis at centre (x, y): profile [(radius, z)]. closed joins the
    profile's ends (a ring); otherwise the ends are closed by fans to the axis."""
    cx, cy = centre
    vertices, faces = [], []
    m = len(profile)
    for r, z in profile:
        for s in range(segments):
            a = 2 * math.pi * s / segments
            vertices.append((cx + r * math.cos(a) * sx, cy + r * math.sin(a) * sy, z))
    for i in range(m if closed else m - 1):
        j = (i + 1) % m
        for s in range(segments):
            t = (s + 1) % segments
            faces.append((i * segments + s, i * segments + t, j * segments + t, j * segments + s))
    if not closed:
        vertices.append((cx, cy, profile[0][1]))
        c = len(vertices) - 1
        faces += [((s + 1) % segments, s, c) for s in range(segments)]
        vertices.append((cx, cy, profile[-1][1]))
        c = len(vertices) - 1
        base = (m - 1) * segments
        faces += [(base + s, base + (s + 1) % segments, c) for s in range(segments)]
    obj = k.mesh_object(name, vertices, faces, mat)
    k.recalc_normals(obj)
    return obj


def ridge_section(width, height, base, power=1.4, points=7):
    """A raised rib's cross-section: a pointed half-superellipse on a flat foot sunk to `base`."""
    out = []
    for i in range(points):
        a = math.pi * i / (points - 1)
        c, s = math.cos(a), math.sin(a)
        out.append((math.copysign(abs(c) ** (2 / power), c) * width, base + 0.45 + s ** (2 / power) * height))
    out += [(-width * 0.85, base), (width * 0.85, base)]
    return out


# --- The ornament ------------------------------------------------------------------------------

# The backing plate: the sprite's outline (its dark outline pixels included), left half from the
# top centre (under the loop) down to the bottom point.
PLATE = [
    (0.0, 9.6), (-1.8, 9.6), (-2.7, 9.0), (-3.5, 8.75), (-4.6, 8.8), (-5.7, 9.45), (-6.7, 10.2),
    (-7.6, 10.8), (-8.5, 10.9), (-9.3, 10.6), (-10.3, 9.8), (-11.3, 8.75), (-11.95, 7.6), (-11.95, -3.3),
    (-11.6, -4.3), (-10.9, -5.0), (-10.2, -5.8), (-9.95, -6.8), (-9.35, -7.75), (-8.5, -8.65),
    (-7.55, -9.55), (-6.5, -10.0), (-4.5, -10.25), (-3.7, -11.05), (-2.8, -11.85), (0.0, -11.95),
]

TIP = (-8.1, 10.2)          # the upper left lobe's tip, where the X's upper arm starts
CENTRE = (0.0, -0.1)        # where the upper arms meet, on top of the bezel
GEM = (0.0, -4.0)           # the gem's and bezel's centre
BEZEL_R = 3.9
LOWER_ARM = ((-3.3, -1.75), (-11.3, -2.65))   # the X's lower left arm: from the bezel's flank to the edge


def arm_offset(t, offset):
    """A point on the left upper arm (t 0 at the lobe tip, 1 at the centre), `offset` to its
    lower left (the wing's side; negative: towards the top centre)."""
    dx, dy = CENTRE[0] - TIP[0], CENTRE[1] - TIP[1]
    length = math.hypot(dx, dy)
    nx, ny = dy / length, -dx / length
    return (TIP[0] + dx * t + nx * offset, TIP[1] + dy * t + ny * offset)


def lower_arm(x, offset=0.0):
    """y of the left lower arm at x, `offset` above it (negative: below)."""
    (x0, y0), (x1, y1) = LOWER_ARM
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0) + offset


def bezel_arc(a0, a1, radius, count):
    return [(GEM[0] + radius * math.cos(math.radians(a0 + (a1 - a0) * i / (count - 1))),
             GEM[1] + radius * math.sin(math.radians(a0 + (a1 - a0) * i / (count - 1)))) for i in range(count)]


def wing_outline():
    """The upper left wing, CCW: down the outer edge, along the lower arm to the bezel, round the
    bezel and up the upper arm back to the lobe tip."""
    gap = BEZEL_R + 0.4
    pts = [arm_offset(0.0, 0.3), (-9.15, 10.15), (-10.1, 9.4), (-10.95, 8.45), (-11.3, 7.4),
           (-11.35, lower_arm(-11.35, 0.35)), (-7.5, lower_arm(-7.5, 0.35)), (-4.6, lower_arm(-4.6, 0.35))]
    pts += bezel_arc(146, 104, gap, 5)
    pts += [arm_offset(0.75, 0.35), arm_offset(0.4, 0.35)]
    return smooth_outline(pts)


def top_centre_outline():
    """Between the upper arms, under the loop, CCW: down the left arm, up the right one, back
    along the top through the notches."""
    left = [arm_offset(0.0, -0.3), arm_offset(0.5, -0.35)]
    bottom = (0.0, CENTRE[1] + 0.5)
    right = [(-x, y) for x, y in reversed(left)]
    top = [(7.0, 10.15), (6.0, 9.45), (4.9, 8.65), (3.6, 8.45), (2.4, 8.8), (1.2, 9.2),
           (-1.2, 9.2), (-2.4, 8.8), (-3.6, 8.45), (-4.9, 8.65), (-6.0, 9.45), (-7.0, 10.15)]
    return smooth_outline(left + [bottom] + right + top, keep=[bottom])


def lower_side_outline():
    """The lower left facet, CCW: from below the lower arm down the outer edge to the bottom, up
    the groove beside the lower centre lobe, round the bezel and back along the lower arm."""
    gap = BEZEL_R + 0.4
    pts = [(-11.35, lower_arm(-11.35, -0.35)), (-11.0, -4.45), (-10.3, -5.25), (-9.6, -6.15), (-9.35, -7.15),
           (-8.6, -8.15), (-7.6, -9.0), (-6.55, -9.45), (-5.05, -9.6), (-5.05, -5.6)]
    pts += bezel_arc(196, 166, gap, 4)
    pts += [(-5.2, lower_arm(-5.2, -0.35)), (-8.0, lower_arm(-8.0, -0.35))]
    return smooth_outline(pts)


def lower_centre_outline():
    """The lower centre lobe under the bezel down to the point, CCW."""
    pts = [(-3.0, -3.2), (-4.35, -4.6), (-4.35, -9.7), (-3.65, -10.55), (-2.6, -11.3), (-1.0, -11.45),
           (1.0, -11.45), (2.6, -11.3), (3.65, -10.55), (4.35, -9.7), (4.35, -4.6), (3.0, -3.2)]
    return smooth_outline(pts)


def scroll_path():
    """The left wing's engraving: a tail rising along the wing's inner side into a spiral curl."""
    centre = (-7.4, 4.0)
    pts = [(-5.6, -0.3), (-5.25, 1.0)]
    turns, count = 1.15, 16
    for i in range(count):
        s = i / (count - 1)
        a = math.radians(-10) + 2 * math.pi * turns * s        # counter-clockwise from the right
        r = 2.1 * (1 - 0.72 * s)
        pts.append((centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)))
    return pts


def convex(x, y):
    """The brooch is slightly convex: facets rise towards the middle."""
    return 0.55 * max(0.0, 1.0 - (x / 12.5) ** 2 - ((y + 1.0) / 13.0) ** 2)


def build():
    k.reset()
    backing = k.material("ornament_backing", palette=18, metallic=0.2, roughness=0.55)
    gold = k.material("ornament_gold", palette=25, metallic=0.45, roughness=0.28)
    gold_mid = k.material("ornament_gold_mid", palette=24, metallic=0.45, roughness=0.3)
    gold_low = k.material("ornament_gold_low", palette=22, metallic=0.45, roughness=0.32)
    ridge = k.material("ornament_ridge", palette=29, metallic=0.25, roughness=0.22)
    bezel = k.material("ornament_bezel", palette=27, metallic=0.45, roughness=0.22)
    loop_gold = k.material("ornament_loop", palette=26, metallic=0.45, roughness=0.24)
    bead = k.material("ornament_bead", palette=27, metallic=0.4, roughness=0.25)
    socket = k.material("ornament_socket", palette=17, metallic=0.1, roughness=0.65)
    gem = k.material("ornament_gem", palette=56, metallic=0.1, roughness=0.06, emission=(40, 105, 180),
                     emission_strength=0.38)

    # The backing plate, darker gold with a rounded edge: it shows in the grooves and round the
    # rim, as the sprite's dark lines and outline.
    facet("plate", resample(chaikin(mirrored(PLATE), 2), 1.2), 0.0, 1.3, backing, rim=0.5, dome=0.0,
          dome_rings=0, bottom=True)

    # The facets.
    wing = wing_outline()
    wing_l = facet("wing_l", wing, 0.8, 2.55, gold, rim=0.7, dome=0.2, lift=convex)
    wing_r = facet("wing_r", mirror_points(wing), 0.8, 2.55, gold, rim=0.7, dome=0.2, lift=convex)
    facet("top_centre", top_centre_outline(), 0.8, 1.9, gold_low, rim=0.55, dome=0.15, lift=convex)
    side = lower_side_outline()
    facet("lower_l", side, 0.8, 2.3, gold_mid, rim=0.65, dome=0.2, lift=convex)
    facet("lower_r", mirror_points(side), 0.8, 2.3, gold_mid, rim=0.65, dome=0.2, lift=convex)
    facet("lower_centre", lower_centre_outline(), 0.8, 2.45, gold, rim=0.7, dome=0.3, lift=convex)

    # The X's upper arms: bright ridges from the lobe tips to the bezel, rising towards the centre.
    for name, sign in (("arm_l", 1), ("arm_r", -1)):
        count = 12
        path = []
        for i in range(count):
            t = i / (count - 1)
            path.append((sign * (TIP[0] + (CENTRE[0] - TIP[0]) * t), TIP[1] + (CENTRE[1] - TIP[1]) * t, 0.0))

        def section(i, t, path=path):
            narrow = min(1.0, t / 0.08 + 0.35)                      # the tip end narrows and sinks
            sink = 0.25 + 0.75 * min(1.0, t / 0.18) ** 0.7          # into the lobe's point
            base = 1.6 + convex(path[i][0], path[i][1])
            return ridge_section(0.62 * narrow, (0.7 + 0.4 * t) * sink, base)
        k.smooth(sweep(name, path, section, ridge), 50)

    # The X's lower arms: lower ridges from the bezel's flanks out to the edges.
    for name, sign in (("lower_arm_l", 1), ("lower_arm_r", -1)):
        (x0, _), (x1, _) = LOWER_ARM
        count = 8
        path = [(sign * (x0 + (x1 - x0) * i / (count - 1)), lower_arm(x0 + (x1 - x0) * i / (count - 1)), 0.0)
                for i in range(count)]

        def section(i, t, path=path):
            end = min(1.0, (1 - t) / 0.15 + 0.3)                   # the outer end sinks into the rim
            base = 1.5 + convex(path[i][0], path[i][1])
            return ridge_section(0.5 * min(1.0, (1 - t) / 0.1 + 0.4), (0.6 - 0.15 * t) * end, base)
        k.smooth(sweep(name, path, section, ridge), 50)

    # The bezel: a rounded ring round the gem, standing proud of the facets.
    lift = convex(*GEM)
    ring_profile = [(BEZEL_R, 1.6), (BEZEL_R + 0.05, 2.55), (BEZEL_R - 0.35, 3.2), (BEZEL_R - 0.9, 3.45),
                    (2.6, 3.3), (2.25, 2.9), (2.15, 2.3), (2.6, 1.6)]
    k.smooth(revolve("bezel", [(r, z + lift) for r, z in ring_profile], GEM, bezel, segments=24, closed=True), 50)

    # The gem: a glossy blue cabochon set in the bezel.
    gem_profile = [(2.35, 2.2), (2.35, 2.75), (2.15, 3.35), (1.7, 3.88), (1.0, 4.25), (0.4, 4.38)]
    k.smooth(revolve("gem", [(r, z + lift) for r, z in gem_profile], GEM, gem, segments=20, sy=1.05), 70)

    # The loop at the top: a ring over a dark socket, tilted back a little as a hanging ring
    # rising from the brooch.
    loop_centre = (0.0, 8.0)
    tube = [(2.1 + 0.95 * math.cos(2 * math.pi * i / 10), 2.35 + 0.8 * math.sin(2 * math.pi * i / 10))
            for i in range(10)]
    loop = revolve("loop", tube, loop_centre, loop_gold, segments=24, closed=True)
    hole = revolve("socket", [(1.45, 1.2), (1.45, 2.4), (0.0, 2.4)], loop_centre, socket, segments=16)
    pivot = Vector((loop_centre[0], loop_centre[1] - 2.0, 2.0))
    tilt = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(16), 4, "X") @ Matrix.Translation(-pivot)
    for part in (loop, hole):
        part.data.transform(tilt)
    k.smooth(loop, 60)
    k.smooth(hole, 30)

    # Engraved scrolls on the wings: a raised bead curling into a spiral, following the surface.
    for wing_obj, sign in ((wing_l, 1), (wing_r, -1)):
        path = []
        for x, y in scroll_path():
            hit, location, _, _ = wing_obj.ray_cast(Vector((sign * x, y, 30.0)), Vector((0, 0, -1)))
            path.append((sign * x, y, (location.z if hit else 2.8) - 0.06))

        def bead_section(i, t):
            r = 0.3 * min(1.0, 0.45 + 2.5 * min(t, 1 - t))
            return [(r * math.cos(2 * math.pi * j / 6), r * math.sin(2 * math.pi * j / 6)) for j in range(6)]
        k.smooth(sweep("scroll", path, bead_section, bead), 60)

    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    depsgraph = bpy.context.evaluated_depsgraph_get()
    print("triangles:", sum(sum(len(p.vertices) - 2 for p in o.evaluated_get(depsgraph).data.polygons)
                            for o in bpy.context.scene.objects if o.type == "MESH"))
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "ornament.glb"))


build()
