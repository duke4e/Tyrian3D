"""The grey and red jet of APPROACH and SAVARA IV, drawn from three sprites of sheet 5: the wings,
229 (left) and 231 (right), above the nose, 268 (models.cfg: model redjet_left / redjet_right /
redjet_nose ... origin; sprite 5 229 redjet_left yaw=0 and so on). The levels place them as one
48 x 56 picture: 742 (229) at x 0 and 743 (231) at x 24, both 28 pixels above 744 (268) at x 12
(SAVARA IV's events at 1400-1440), and they move together.

The jet is built whole, nose down the screen, and cut along the sprites' edges into the three
pieces, each moved so that its sprite's centre is its origin (base on the layer): drawn at their
own places, they meet again. The normals of the cut pieces are taken from the whole jet, so the
shading runs on across the cuts as if nothing was cut.

As the sprites draw it (polish, 2026-10-18, after the 4x upscale): a round grey fuselage from the
pointed nose (row 51 of the 48 x 56 picture) to the tail (row 3), drooping a little at the nose,
whose underside is dark red (the sprite's dark red outline round it); a framed canopy, four dark
panes either side of a broad middle frame and the windscreen in front (rows 33-42); a low spine
from the canopy back to the fin (the dark line down the fuselage, rows 17-27); red strakes along
the fuselage's flanks from the wing roots (rows 16-28), rising behind into two grey humps either
side of the fin (rows 9-16) with a red heart-shaped shield between them; swept wings with a dark
red leading edge, a panel line along it and a red flap at the root's trailing edge, the roots'
leading edges running forward beside the fuselage as prongs (rows 28-32); upright fins at the
wing tips, red at the front; tail planes at the top, their roots running forward into red fangs
(rows 5-8); and a tall swept fin with a red top edge (column 24).

The sprite is symmetric about its column 24 (x 0.5 here): the jet is built about x = 0 and moved
there (AXIS_X). Coordinates as in tyrkit: 1 unit = 1 game pixel, +Y up the screen, +Z towards
the camera; the jet's origin is the corner where the three sprites meet (the wings' bottom edge,
the nose's top edge, between 229 and 231).

Replaces wave3_l_parts.py's jet (build_jet, jet_piece): remove those pieces from its registry so
that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_5.png> (the
silhouettes of the pieces and of the whole), --preview <prefix> (each piece's top and 3/4 view,
and the whole jet's).
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
import tyrkit as k  # noqa: E402
from glb_winding import reverse_winding  # noqa: E402

AXIS_X = 0.5
# name, sprite, the box it covers in the jet's coordinates (x0, x1, y0, y1)
PIECES = [("redjet_left", 229, (-24.0, 0.0, 0.0, 28.0)),
          ("redjet_right", 231, (0.0, 24.0, 0.0, 28.0)),
          ("redjet_nose", 268, (-12.0, 12.0, -28.0, 0.0))]
SPRITE_CELLS = {229: (0, 0), 231: (24, 0), 268: (12, 28)}  # top left corners in the 48 x 56 picture


# --- Helpers ----------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic)."""
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
        x = min(max(x, xs[0]), xs[-1])
        i = max(0, min(n - 2, next((j for j in range(n - 1) if x <= xs[j + 1]), n - 2)))
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        return ((2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h * m[i] +
                (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h * m[i + 1])
    return f


class Curve:
    """Smooth curves through table rows (x, value, ...): one per value column."""

    def __init__(self, rows):
        columns = list(zip(*rows))
        self.functions = [monotone(columns[0], c) for c in columns[1:]]

    def __call__(self, x):
        values = [f(x) for f in self.functions]
        return values if len(values) > 1 else values[0]


def end_round(y, y0, y1, r0, r1):
    """1 inside [y0, y1], falling on a quarter circle to 0 within r0 of y0 and r1 of y1."""
    f = 1.0
    for d, r in ((y - y0, r0), (y1 - y, r1)):
        if r > 0 and d < r:
            f = min(f, math.sqrt(max(0.0, 1 - (1 - max(d, 0.0) / r) ** 2)))
    return f


def chaikin(points, iterations=2):
    """Rounds a closed polygon's corners."""
    pts = [tuple(p) for p in points]
    for _ in range(iterations):
        out = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
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


def facet(name, outline, base, height, mat, rim=0.3, steps=3, dome=0.1, dome_rings=2, sink=0.5):
    """A raised plate lying on a surface: the polygon `outline` (counter-clockwise seen from above)
    standing from base(x, y) - sink to base(x, y) + height, its top edge rounded with radius rim
    and its top bulging by dome towards the middle (the outline must be star-shaped from its
    centroid); closed underneath."""
    n = len(outline)
    dirs = []
    for i in range(n):
        p0, p1, p2 = Vector(outline[i - 1]), Vector(outline[i]), Vector(outline[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))  # inward for a counter-clockwise outline
        m = n1 + n2
        m = m.normalized() if m.length > 1e-6 else n1
        dirs.append(m / max(m.dot(n1), 0.7))
    profile = [(0.0, -sink), (0.0, height - rim)]
    for i in range(1, steps + 1):
        a = 0.5 * math.pi * i / steps
        profile.append((rim * (1 - math.cos(a)), height - rim + rim * math.sin(a)))
    rings = [[(p[0] + d.x * inset, p[1] + d.y * inset, dz) for p, d in zip(outline, dirs)] for inset, dz in profile]
    inner = rings[-1]
    cx, cy = sum(v[0] for v in inner) / n, sum(v[1] for v in inner) / n
    for r in range(1, dome_rings + 1):
        f = 1 - r / (dome_rings + 1)
        rings.append([(cx + (x - cx) * f, cy + (y - cy) * f, height + dome * (1 - f * f)) for x, y, _ in inner])
    vertices = [(x, y, base(x, y) + dz) for ring in rings for x, y, dz in ring]
    faces = []
    for r in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((r * n + i, r * n + j, (r + 1) * n + j, (r + 1) * n + i))
    vertices.append((cx, cy, base(cx, cy) + height + dome))
    top = (len(rings) - 1) * n
    faces += [(top + i, top + (i + 1) % n, len(vertices) - 1) for i in range(n)]
    bx, by = sum(p[0] for p in outline) / n, sum(p[1] for p in outline) / n
    vertices.append((bx, by, base(bx, by) - sink))
    faces += [((i + 1) % n, i, len(vertices) - 1) for i in range(n)]
    obj = k.mesh_object(name, vertices, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def tube(name, points, radius, mat, segments=6, radii=None):
    """A thin round tube through points (Vectors), closed with rounded ends."""
    rings = []
    for i, p in enumerate(points):
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(tangent).normalized()
        r = radii[i] if radii else radius
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) + up * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    t0 = (points[1] - points[0]).normalized()
    t1 = (points[-1] - points[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=points[0] - t0 * radius * 0.8, end_point=points[-1] + t1 * radius * 0.8)
    return k.smooth(obj, 60)


def blade_section(cz, w_bottom, w_top, h, count=12, power=2.4):
    """An upright blade's cross-section [(across, up)]: a rounded rectangle 2h tall, narrowing from
    w_bottom to w_top (halves) towards its top edge."""
    out = []
    for j in range(count):
        a = 2 * math.pi * j / count
        c, s = math.cos(a), math.sin(a)
        w = w_bottom + (w_top - w_bottom) * (s + 1) / 2
        out.append((math.copysign(abs(c) ** (2 / power), c) * w, cz + math.copysign(abs(s) ** (2 / power), s) * h))
    return out


def naca(c):
    """A rounded airfoil's half-thickness along the chord (0-1), 1 at its thickest (c 0.3)."""
    c = min(max(c, 0.0), 1.0)
    return (0.2969 * math.sqrt(c) - 0.1260 * c - 0.3516 * c ** 2 + 0.2843 * c ** 3 - 0.1036 * c ** 4) / 0.1002


CHORD = [(1 - math.cos(math.pi * i / 12)) / 2 for i in range(13)]  # samples along a chord, dense at the edges


def airfoil_ring(u, y_le, y_te, mid, thickness, extra=(), camber=0.12, under=0.45, droop=None):
    """A wing's section at span u: from the leading edge over the top to the trailing edge and back
    underneath (points in the YZ plane at x = u). extra: chord fractions to sample as well (for
    material borders); droop(y) lowers the section's points."""
    cs = list(CHORD)
    for e in extra:
        e = min(max(e, 0.06), 0.94)
        while min(abs(e - c) for c in cs) < 0.012:
            e += 0.013
        cs.append(e)
    cs.sort()

    def point(c, sign):
        y = y_le + c * (y_te - y_le)
        z = mid + camber * thickness * math.sin(math.pi * c)
        z += thickness * naca(c) * (1.0 if sign > 0 else -under)
        if droop is not None:
            z -= droop(y)
        return Vector((u, y, z))
    return [point(c, 1) for c in cs] + [point(c, -1) for c in reversed(cs[1:-1])]


# --- The hull ---------------------------------------------------------------------------------------
# A lofted surface whose cross-sections are the outline of a union of lobes (tyrkit.lobed_ring): the
# fuselage, the two humps either side of the fin and the two strakes along the flanks, so that the
# creases where they meet show as in the sprite. Lobes: (x, z, half-width, top, bottom).

# The fuselage's half-width along y: inside the sprite's dark outline by about half a pixel (rows
# 29-39: 5.5 with the outline; the nose cone rows 40-51).
FUSELAGE = Curve([(-23.25, 0.3), (-22.6, 0.95), (-21.5, 1.5), (-20.0, 2.2), (-18.5, 2.85), (-17.0, 3.4),
                  (-15.5, 3.9), (-14.0, 4.35), (-12.5, 4.7), (-11.0, 4.95), (-9.0, 5.05), (-6.0, 5.05), (-3.0, 5.0),
                  (0.0, 4.95), (3.0, 4.85), (6.0, 4.75), (9.0, 4.6), (12.0, 4.45), (15.0, 4.3), (18.0, 4.1),
                  (20.0, 4.0), (22.0, 3.85), (23.5, 3.55), (24.4, 3.0), (25.0, 2.2)])
NOSE_TIP, TAIL_END = -23.45, 25.25


def fuselage_z(y):
    """The fuselage's axis: level, the nose drooping a little."""
    return 3.0 - 0.85 * smoothstep(-9.0, -23.4, y)


def fuselage_top(y):
    """The fuselage's top above its axis, as a fraction of its half-width: lower between the humps,
    so that the shield lies in a hollow there."""
    return 0.84 - 0.08 * smoothstep(9.0, 11.0, y) * (1 - smoothstep(19.5, 21.5, y))


# The left hump (rows 9-16): y, distance of its middle from the axis, half-width, top, bottom
# (about z 3.6). It starts with a rounded front over the strake at y 10.2 and ends beside the fin.
HUMP_Z, HUMP_Y = 3.6, (10.2, 20.4)
HUMP = Curve([(10.2, 6.6, 2.3, 2.6, 1.9), (11.0, 6.6, 2.3, 2.6, 1.9), (12.0, 6.5, 2.75, 3.15, 2.2),
              (13.5, 6.3, 2.85, 3.3, 2.3), (15.0, 6.2, 2.85, 3.3, 2.3), (16.5, 5.8, 2.8, 3.2, 2.2),
              (17.5, 5.2, 2.65, 3.0, 2.1), (18.5, 4.5, 2.3, 2.75, 1.9), (19.5, 3.7, 1.7, 2.4, 1.5),
              (20.4, 3.4, 1.2, 2.0, 1.2)])
# The left strake (rows 16-28): y, middle, half-width, centre height, top, bottom. Pointed at the
# front (y -0.9), widest under the wing root's trailing edge, its end tucked under the hump.
STRAKE_Y = (-0.9, 12.8)
STRAKE = Curve([(-0.9, 5.0, 0.0, 3.3, 0.0, 0.0), (-0.4, 5.1, 0.6, 3.3, 0.35, 0.45), (0.5, 5.15, 1.25, 3.35, 0.65, 0.7),
                (2.0, 5.1, 1.55, 3.4, 0.95, 0.85), (4.0, 5.05, 1.7, 3.45, 1.25, 0.95),
                (5.5, 5.1, 1.75, 3.5, 1.45, 1.05), (6.5, 5.5, 2.05, 3.5, 1.6, 1.15), (7.5, 6.0, 2.5, 3.5, 1.75, 1.25),
                (8.5, 6.55, 2.9, 3.5, 1.85, 1.35), (9.5, 6.9, 2.6, 3.5, 1.9, 1.35), (10.5, 7.0, 2.5, 3.5, 1.85, 1.3),
                (11.5, 7.1, 2.2, 3.5, 1.6, 1.2), (12.3, 7.2, 1.6, 3.5, 1.1, 0.9), (12.8, 7.3, 1.2, 3.5, 0.8, 0.7)])
STRAKE_LOBES = (3, 4)
CREASE_PAIRS = {(0, 3), (0, 4), (1, 3), (2, 4)}  # seams: the strakes' inner edges, the humps' fronts

# Ray angles of the hull's sections (degrees): fine over the top and the sides, coarse underneath.
ANGLES = [math.radians(a % 360) for a in sorted(list(range(-12, 194, 5)) + list(range(205, 341, 15)))]
ANGLES.sort()


def hull_lobes(y):
    hw = FUSELAGE(y)
    zc = fuselage_z(y)
    lobes = [(0.0, zc, hw, hw * fuselage_top(y), hw * 0.62)]
    for side in (-1, 1):
        if HUMP_Y[0] < y < HUMP_Y[1]:
            d, w, top, bottom = HUMP(y)
            f = end_round(y, HUMP_Y[0], HUMP_Y[1], 1.6, 1.0)
            lobes.append((side * d, HUMP_Z, w * f, top * f, bottom * f))
        else:
            lobes.append((side * 5.0, HUMP_Z, 0.0, 0.0, 0.0))
    for side in (-1, 1):
        if STRAKE_Y[0] < y < STRAKE_Y[1]:
            d, w, z, top, bottom = STRAKE(y)
            f = end_round(y, STRAKE_Y[0], STRAKE_Y[1], 0.0, 0.9)
            lobes.append((side * d, z, w * f, top * f, bottom * f))
        else:
            lobes.append((side * 5.0, 3.3, 0.0, 0.0, 0.0))
    return lobes


def hull_top(u, y):
    """The hull's top surface at (u, y) (the highest lobe there), for parts lying on it."""
    best = None
    for x, z, w, top, _ in hull_lobes(y):
        if w > 0.05 and abs(u - x) < w:
            h = z + top * math.sqrt(1 - ((u - x) / w) ** 2)
            best = h if best is None else max(best, h)
    return best if best is not None else fuselage_z(y)


def lobed_ring(y, lobes, origin_z, owners, creases):
    """tyrkit.lobed_ring with the hull's own ray angles (ANGLES)."""
    points, hits = [], []
    for a in ANGLES:
        t, owner = k._lobed_hit(a, lobes, origin_z)
        hits.append((a, owner))
        points.append(Vector((t * math.cos(a), y, origin_z + t * math.sin(a))))
        owners.append(owner)
    n = len(ANGLES)
    for i in range(n):
        (a0, o0), (a1, o1) = hits[i], hits[(i + 1) % n]
        if o0 == o1:
            continue
        if a1 < a0:
            a1 += 2 * math.pi
        for _ in range(16):
            mid = (a0 + a1) / 2
            if k._lobed_hit(mid, lobes, origin_z)[1] == o0:
                a0 = mid
            else:
                a1 = mid
        a = (a0 + a1) / 2
        t, _ = k._lobed_hit(a, lobes, origin_z)
        creases.append(((min(o0, o1), max(o0, o1)), Vector((t * math.cos(a), y, origin_z + t * math.sin(a)))))
    return points


def hull_stations():
    ys = []
    for y0, y1, step in ((-23.25, -19.0, 0.55), (-19.0, -9.0, 0.9), (-9.0, -1.5, 0.95), (-1.5, 2.5, 0.6),
                         (2.5, 9.0, 0.85), (9.0, 21.0, 0.5), (21.0, 25.0, 0.57)):
        count = max(1, int(round((y1 - y0) / step)))
        ys += [y0 + (y1 - y0) * i / count for i in range(count)]
    ys.append(25.0)
    return ys


def hull(m):
    rings, owners, creases = [], [], []
    for y in hull_stations():
        o, c = [], []
        rings.append(lobed_ring(y, hull_lobes(y), fuselage_z(y), o, c))
        owners.append(o)
        creases.append([(pair, p) for pair, p in c if pair in CREASE_PAIRS])
    body = k.loft("hull", rings, m["hull"], start_point=(0, NOSE_TIP, fuselage_z(NOSE_TIP)),
                  end_point=(0, TAIL_END, fuselage_z(TAIL_END)))
    for mat in (m["red"], m["dark_red"]):
        body.data.materials.append(mat)
    n = len(ANGLES)
    for poly in body.data.polygons[:(len(rings) - 1) * n]:
        i, j = divmod(poly.index, n)
        votes = [owners[i][j], owners[i][(j + 1) % n], owners[i + 1][j], owners[i + 1][(j + 1) % n]]
        if sum(o in STRAKE_LOBES for o in votes) >= 2:
            poly.material_index = 1
        elif poly.center.y < -12.5 and poly.normal.z < 0.0:
            poly.material_index = 2  # the nose's dark red underside
    k.smooth(body, 40)
    k.crease_seams("seam", creases, m["seam"], radius=0.2, sink=0.06)
    return body


def spine(m):
    """The low ridge along the fuselage's top from behind the canopy to the fin (rows 17-27)."""
    y0, y1 = -1.4, 12.9
    rings = []
    for i in range(24):
        y = y0 + (y1 - y0) * i / 23
        f = end_round(y, y0, y1, 1.4, 0.8)
        rings.append(k.ring(y, 0.78 * max(f, 0.08), 1.0, 10, z=hull_top(0.0, y) - 0.25, top=0.25 + 0.5 * f,
                            bottom=0.45, power=2.2))
    return k.smooth(k.loft("spine", rings, m["hull"]), 55)


# --- The wings --------------------------------------------------------------------------------------
# The left wing by span (u, from its tip to its root inside the fuselage): the leading edge (the
# sprite's dark red outline, rows 21-32, inside it by half a pixel) sweeping from the tip fin to the
# prong beside the fuselage (its point at row 32), and back up the prong's inner edge into the
# strake; the trailing edge from the tip fin's top (row 13) down to row 17, stepping back up behind
# the red flap (rows 15-16) and into the hump.
WING_LE = Curve([(-20.3, 6.9), (-19.4, 6.45), (-18.5, 5.75), (-17.5, 4.85), (-16.5, 3.85), (-15.5, 2.6),
                 (-14.5, 1.45), (-13.5, 0.85), (-12.5, 0.2), (-11.5, -0.8), (-10.5, -1.95), (-9.5, -2.95),
                 (-8.5, -3.85), (-7.9, -4.3), (-7.5, -4.45), (-7.15, -3.5), (-6.95, -2.1), (-6.6, -0.6),
                 (-6.0, 0.6), (-5.0, 1.6), (-4.2, 2.6)])
WING_TE = Curve([(-20.3, 13.75), (-19.6, 14.1), (-19.0, 13.5), (-18.0, 12.5), (-17.0, 11.5), (-16.0, 10.65),
                 (-15.2, 10.4), (-14.8, 10.9), (-14.4, 11.8), (-13.8, 12.3), (-12.0, 12.45), (-10.0, 12.45),
                 (-8.5, 12.3), (-7.0, 11.8), (-5.5, 10.8), (-4.2, 9.6)])
WING_SPAN = [-4.2, -4.8, -5.4, -5.9, -6.3, -6.6, -6.85, -7.05, -7.25, -7.45, -7.7, -8.1, -8.6, -9.2] + \
            [-9.9 - 0.75 * i for i in range(13)] + [-19.4, -19.85, -20.3]
WING_TIP_U = -21.0  # the tip fin (column 3)


def wing_mid(u):
    return 2.85 + 0.055 * max(0.0, -u - 4.5)  # a little dihedral


def wing_thickness(u):
    return 0.42 + 0.53 * smoothstep(-20.3, -7.0, u)


def wing_top(u, y):
    """The left wing's top surface at (u, y)."""
    y_le, y_te = WING_LE(u), WING_TE(u)
    c = (y - y_le) / max(y_te - y_le, 1e-6)
    t = wing_thickness(u)
    return wing_mid(u) + 0.12 * t * math.sin(math.pi * min(max(c, 0), 1)) + t * naca(c)


def wings(m):
    rings = [airfoil_ring(u, WING_LE(u), WING_TE(u), wing_mid(u), wing_thickness(u)) for u in WING_SPAN]
    left = k.loft("wing_l", rings, m["wing"])
    left.data.materials.append(m["dark_red"])
    n = len(rings[0])
    for poly in left.data.polygons[:(len(rings) - 1) * n]:
        if poly.index % n in (0, 1, n - 2, n - 1):  # the leading edge's strips, above and below
            poly.material_index = 1
    k.smooth(left, 45)
    # A panel line along the leading edge (the sprite's darker diagonal, about 5.6 px behind it).
    us = [-15.6 + (15.6 - 7.9) * i / 13 for i in range(14)]
    line = [Vector((u, WING_LE(u) + 5.6, wing_top(u, WING_LE(u) + 5.6) - 0.08)) for u in us]
    parts = [left, tube("panel_l", line, 0.17, m["seam"])]
    # The red flap on the root's trailing edge (rows 16-18, columns 10-13).
    flap = resample(chaikin([(-12.2, 9.45), (-10.5, 9.65), (-10.55, 12.35), (-13.6, 12.3), (-14.65, 11.2)], 2), 0.4)
    parts.append(facet("flap_l", flap, lambda x, y: wing_top(x, y) - 0.05, 0.6, m["red"], rim=0.28, steps=2,
                       dome=0.08, dome_rings=1, sink=0.4))
    # The tip fin: upright, red at its front (rows 20-26), grey behind (rows 13-19).
    stations = [0.6, 0.85, 1.2, 1.7, 2.2, 3.0, 4.0, 5.2, 6.4, 7.6, 8.8, 10.0, 11.2, 12.4, 13.4, 14.0, 14.4, 14.7]
    profile = Curve([(0.6, 3.1, 3.9), (1.2, 2.6, 5.2), (2.2, 2.35, 6.1), (4.0, 2.3, 6.6), (7.6, 2.35, 6.9),
                     (11.0, 2.45, 7.0), (13.4, 2.6, 7.0), (14.3, 2.9, 6.7), (14.7, 3.4, 6.1)])
    fin_rings = []
    for y in stations:
        z0, z1 = profile(y)
        f = min(1.0, 0.35 + (y - 0.6) / 0.9, 0.35 + (14.7 - y) / 0.9)
        fin_rings.append([Vector((WING_TIP_U + s, y, z)) for s, z in
                          blade_section((z0 + z1) / 2, 0.95 * f, 0.4 * f, (z1 - z0) / 2)])
    fin = k.loft("tip_fin_l", fin_rings, m["hull"], start_point=(WING_TIP_U, 0.45, 3.5),
                 end_point=(WING_TIP_U, 14.85, 4.9))
    fin.data.materials.append(m["red"])
    for poly in fin.data.polygons:
        if poly.center.y < 7.6:
            poly.material_index = 1
    parts.append(k.smooth(fin, 50))
    for part in parts:
        mirror = k.mirror_x(part, part.name[:-2] + "_r")
        mirror.data.name = mirror.name


# --- The tail ---------------------------------------------------------------------------------------
# The left tail plane by span: its front edge from the rounded tip (column 9) along row 5, then
# running forward at the root into the red fang (rows 5-8, its point at row 8, column 17-18) and back
# along the boom; its rear edge along row 1, curving down to the boom at rows 3-4.
TAIL_LE = Curve([(-15.1, 24.0), (-14.8, 23.3), (-14.3, 22.9), (-13.5, 22.7), (-12.5, 22.5), (-11.5, 22.0),
                 (-10.5, 21.55), (-9.5, 21.0), (-8.5, 20.3), (-7.6, 19.75), (-6.9, 19.4), (-6.3, 19.25),
                 (-5.6, 19.5), (-4.6, 20.3), (-3.6, 20.8), (-2.8, 21.1)])
TAIL_TE = Curve([(-15.1, 24.6), (-14.8, 25.6), (-14.4, 26.1), (-13.5, 26.45), (-12.0, 26.55), (-9.0, 26.5),
                 (-7.5, 26.2), (-6.5, 25.4), (-5.5, 24.6), (-4.6, 24.3), (-2.8, 24.4)])
TAIL_SPAN = [-2.8, -3.6, -4.6, -5.1, -5.6, -6.0, -6.3, -6.6, -7.0, -7.6, -8.3, -9.1, -10.0, -11.0, -12.0, -12.7,
             -13.4, -14.0, -14.5, -14.85, -15.1]
TAIL_RED_Y, TAIL_RED_U = 22.85, -12.7  # the fang is red in front of row 5's top, inside column 12


def tail_mid(u):
    return 5.25 + 0.085 * max(0.0, -u - 4.6)


def tail_droop(u):
    """The fang curving down towards its point."""
    s = smoothstep(-10.5, -7.0, u)
    return lambda y: 0.85 * s * smoothstep(21.8, 19.3, y)


def tail(m):
    rings = []
    for u in TAIL_SPAN:
        y_le, y_te = TAIL_LE(u), TAIL_TE(u)
        t = 0.3 + 0.45 * smoothstep(-15.1, -6.0, u)
        rings.append(airfoil_ring(u, y_le, y_te, tail_mid(u), t, extra=((TAIL_RED_Y - y_le) / (y_te - y_le),),
                                  droop=tail_droop(u)))
    plane = k.loft("tail_l", rings, m["hull"])
    plane.data.materials.append(m["red"])
    for poly in plane.data.polygons:
        if poly.center.y < TAIL_RED_Y and poly.center.x > TAIL_RED_U:
            poly.material_index = 1
    k.smooth(plane, 45)
    mirror = k.mirror_x(plane, "tail_r")
    mirror.data.name = "tail_r"

    # The tall fin on the boom (column 24 from row 0 to row 15), its top edge red: y, bottom, top.
    rows = Curve([(12.5, 4.5, 6.3), (13.2, 4.3, 7.0), (14.5, 4.2, 7.9), (16.0, 4.2, 8.8), (18.0, 4.2, 10.0),
                  (20.0, 4.2, 11.1), (22.0, 4.2, 12.1), (23.5, 4.2, 12.75), (24.8, 4.2, 13.15), (25.6, 5.6, 13.3),
                  (26.4, 7.8, 13.4), (27.0, 9.6, 13.35), (27.4, 11.2, 13.15), (27.7, 12.3, 12.9)])
    y0, y1 = 12.5, 27.7
    fin_rings = []
    count = 28
    for i in range(count):
        y = y0 + (y1 - y0) * (i / (count - 1)) ** 0.95
        z0, z1 = rows(y)
        f = min(1.0, 0.4 + (y - y0) / 1.2, 0.35 + (y1 - y) / 0.6)
        fin_rings.append([Vector((s, y, z)) for s, z in blade_section((z0 + z1) / 2, 1.15 * f, 0.42 * f,
                                                                       (z1 - z0) / 2, count=14)])
    fin = k.loft("fin", fin_rings, m["hull"], start_point=(0, 12.3, 5.3), end_point=(0, 27.85, 12.7))
    fin.data.materials.append(m["red_light"])
    for poly in fin.data.polygons:
        if poly.normal.z > 0.42:
            poly.material_index = 1
    k.smooth(fin, 50)

    # The dark nozzle at the tail's end.
    k.smooth(k.lathe("nozzle", [(24.2, 0.0), (24.2, 2.75), (24.9, 2.85), (25.35, 2.6), (25.4, 2.1), (25.0, 1.5),
                                (24.8, 0.0)], m["seam"], segments=16, axis_z=fuselage_z(25.0)), 50)


# --- The shield and the canopy ----------------------------------------------------------------------

def shield(m):
    """The red heart between the humps (rows 10-15), the fin standing in its notch."""
    right = [(0.0, 12.15), (1.4, 12.25), (2.6, 12.6), (3.65, 13.3), (4.35, 14.3), (4.3, 15.5), (3.6, 16.6),
             (2.6, 17.55), (1.7, 17.4), (1.0, 16.5)]
    outline = right + [(-x, y) for x, y in reversed(right[1:])]
    outline = resample(chaikin(outline, 2), 0.4)
    return facet("shield", outline, lambda x, y: hull_top(x, y) - 0.08, 0.42, m["red"], rim=0.26, steps=2, dome=0.1,
                 dome_rings=2, sink=0.6)


# The canopy along y: half-width, height above its base (the fuselage's top less CANOPY_SINK).
CANOPY = Curve([(-15.0, 0.0, 0.0), (-14.7, 0.9, 0.35), (-14.0, 1.6, 0.75), (-12.8, 2.3, 1.15), (-11.4, 2.8, 1.5),
                (-10.0, 3.05, 1.7), (-8.6, 3.1, 1.75), (-7.2, 3.0, 1.7), (-6.2, 2.7, 1.45), (-5.5, 2.1, 1.0),
                (-5.15, 1.2, 0.45), (-5.0, 0.0, 0.0)])
CANOPY_SINK = 0.45
FRAME_BOWS = (-5.65, -8.5, -11.55)  # the frames across it (rows 33, 36 and 39)


def canopy_surface(u, y):
    w, h = CANOPY(y)
    base = hull_top(0.0, y) - CANOPY_SINK
    if w <= 0.05 or abs(u) >= w:
        return base
    return base + h * math.sqrt(1 - (u / w) ** 2)


def canopy(m):
    rings = []
    ys = [-15.0 + 10.0 * i / 30 for i in range(31)]
    for y in ys[1:-1]:
        w, h = CANOPY(y)
        rings.append(k.ring(y, max(w, 0.05), 1.0, 24, z=hull_top(0.0, y) - CANOPY_SINK, top=max(h, 0.05),
                            bottom=1.4))
    glass = k.loft("canopy", rings, m["glass"], start_point=(0, -15.05, hull_top(0.0, -15.0) - CANOPY_SINK),
                   end_point=(0, -4.95, hull_top(0.0, -5.0) - CANOPY_SINK))
    k.smooth(glass, 60)
    # The broad middle frame over the canopy's top (columns 23-25), from its back to the windscreen.
    rings = []
    for i in range(16):
        y = -5.2 - (11.8 - 5.2) * i / 15
        f = end_round(y, -11.8, -5.2, 0.5, 0.3)
        rings.append(k.ring(y, 1.3 * max(f, 0.1), 1.0, 12, z=canopy_surface(0.0, y) - 0.25, top=0.42 * max(f, 0.3),
                            bottom=0.4, power=2.6))
    k.smooth(k.loft("canopy_spine", rings[::-1], m["frame"]), 55)
    # The bows across it.
    for i, y in enumerate(FRAME_BOWS):
        w, _ = CANOPY(y)
        us = [-w * 1.02 + 2.04 * w * j / 12 for j in range(13)]
        points = [Vector((u, y, canopy_surface(u, y) - 0.05)) for u in us]
        bow = tube(f"canopy_bow{i}", points, 0.36, m["frame"], segments=8)
        bow.data.transform(Matrix.Translation((0, y, 0)) @ Matrix.Scale(1.25, 4, (0, 1, 0)) @
                           Matrix.Translation((0, -y, 0)))


# --- Cutting into the pieces ------------------------------------------------------------------------

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
        """The shading normal at co on the face that lies towards `towards` (a point inside the
        face the corner belongs to)."""
        _, _, index, _ = self.bvh.find_nearest(co + (towards - co) * 0.02)
        if index is None:
            return None
        (ia, ib, ic), (la, lb, lc) = self.tris[index]
        w = barycentric(co, self.verts[ia], self.verts[ib], self.verts[ic])
        n = self.normals[la] * w[0] + self.normals[lb] * w[1] + self.normals[lc] * w[2]
        return n.normalized() if n.length > 1e-8 else None


def cut(source, box, cap_mat):
    """The part of an object inside box (x0, x1, y0, y1), its cuts closed with flat caps of
    cap_mat, its normals those of the uncut object. None if nothing is inside."""
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
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))):
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
        for e in f.edges:
            if any(g not in caps for g in e.link_faces):
                e.smooth = False
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cap_ids = set()
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    # The normals of the uncut surface, the caps flat.
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


# --- Checks, previews and export --------------------------------------------------------------------

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
    path = os.path.join(bpy.app.tempdir or "/tmp", "redjet_silhouette.png")
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
    print("exported", path)


def whole_mask(sheet):
    """The three sprites' silhouettes placed as the levels place them: 48 x 56."""
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (cx, cy) in SPRITE_CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[cy + y][cx + x] = True
    return mask


# --- Build ------------------------------------------------------------------------------------------

def materials():
    return {
        "hull": k.material("redjet_hull", palette=6, metallic=0.4, roughness=0.34),
        "wing": k.material("redjet_wing", palette=7, metallic=0.4, roughness=0.38),
        "red": k.material("redjet_red", palette=70, metallic=0.3, roughness=0.34),
        "red_light": k.material("redjet_red_light", palette=72, metallic=0.3, roughness=0.3),
        "dark_red": k.material("redjet_dark_red", palette=114, metallic=0.25, roughness=0.4),
        "seam": k.material("redjet_seam", palette=3, metallic=0.3, roughness=0.55),
        "glass": k.material("redjet_glass", palette=2, metallic=0.3, roughness=0.06),
        "frame": k.material("redjet_frame", palette=9, metallic=0.4, roughness=0.3),
    }


def build():
    k.reset()
    options = k.args()
    m = materials()
    hull(m)
    spine(m)
    wings(m)
    tail(m)
    shield(m)
    canopy(m)
    whole = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for obj in whole:
        obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
    print("whole jet: %d triangles, %d objects" % (triangles(whole), len(whole)))

    sheet = options.get("check")
    if sheet:
        check_mask(whole_mask(sheet), "whole (229 + 231 above 268)", whole)
    if "preview" in options:
        preview(options["preview"] + "whole", whole, size=(48, 56), scale=8, distance=2.0)

    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        move(pieces, -(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2)
        print("== %s (5 %d): %d triangles, %d objects" % (name, sprite, triangles(pieces), len(pieces)))
        if sheet:
            check_mask(k.sprite_mask(sheet, sprite), "%s (5 %d)" % (name, sprite), pieces)
        export(pieces, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
