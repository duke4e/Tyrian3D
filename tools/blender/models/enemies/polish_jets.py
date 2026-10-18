"""The four jets of sheet F (2x2 sprites, 24 x 28 pixels, not animated; sky enemies, which the game
centres in height; models.cfg: yaw=0, the models face the way the sprites do, nose down the screen),
polished (2026-10-18) after their 4x upscales. One script, as they share their parts:

- jet_cross (F 125; SAVARA, INVADERS, SURFACE, DESERTRUN...): a grey early jet with straight
  tapered wings, side intakes and a cruciform tail.
- jet_green (F 3; SAVARA, APPROACH, INVADERS): a green arrow-shaped delta with a tail spike, twin
  canted orange fins, orange elevons and two yellow dorsal intakes.
- jet_brown (F 49; SAVARA, SAVARA V/Y): a stubby brown jet with twin tail booms, grey tail planes,
  grey leading edges and two red lamps.
- jet_delta (F 11; SAVARA, INVADERS): a grey jet with swept delta wings, chines along the nose and
  a cruciform tail.

Each is built as a real aircraft: a round lofted fuselage, thin wings and tail planes lofted from
airfoil sections (a little thickness and dihedral), a glossy dark canopy with a bright glint, intakes
and nozzles. The sprites' dark outline is not geometry: the plans reach about two thirds into the
outline pixels (staircase edges fitted so that each outline pixel is mostly covered and each pixel
outside mostly not), so that the silhouettes match the sprites'.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen (sprite row r is
y = 13.5 - r, its pixels' edges at whole numbers), +Z towards the camera. Origin at the sprite's
centre (pixel 12, 14). Each jet is built symmetric about x = 0 (u below: x relative to the axis) and
moved onto its sprite's axis (AXIS: column 12 for jet_cross and jet_delta, column 13 for jet_green,
between columns 12 and 13 for jet_brown).

Replaces jets.py (the extruded silhouettes of all four): remove it, or its jet() calls, so that it
doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette of each against its sprite in <dir>/enemy_F.png), --preview <prefix> (top and 3/4
views), --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402


# --- Curves -----------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic)."""
    n = len(xs)
    if n == 1:
        return lambda x: ys[0]
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
    """Smooth curves through table rows (x, value, ...), one per value column: called with x, it
    returns the value (one column) or the list of values."""

    def __init__(self, rows):
        rows = sorted(rows)
        columns = list(zip(*rows))
        self.functions = [monotone(columns[0], c) for c in columns[1:]]

    def __call__(self, x):
        values = [f(x) for f in self.functions]
        return values if len(values) > 1 else values[0]


def quarter(d, r):
    """A quarter circle: 0 at d = 0 rising to 1 at d = r (rounds a corner of radius r)."""
    if r <= 0 or d >= r:
        return 1.0
    if d <= 0:
        return 0.0
    return math.sqrt(1 - (1 - d / r) ** 2)


def spaced(a, b, count, dense_a=0.0, dense_b=0.0):
    """count values from a to b, closer together towards a (dense_a 0-1) and towards b (dense_b)."""
    out = []
    for i in range(count):
        t = i / (count - 1)
        s = t + dense_a * ((1 - math.cos(math.pi * t / 2)) - t) + dense_b * (math.sin(math.pi * t / 2) - t)
        out.append(a + (b - a) * s)
    return out


def chaikin(points, iterations=2):
    """Rounds a closed polygon's corners (straight runs stay straight)."""
    pts = [tuple(p) for p in points]
    for _ in range(iterations):
        out = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        pts = out
    return pts


class Plan:
    """A lifting surface's plan on the left side: a closed outline [(u, y)] (u < 0, the root's
    edge inside the fuselage), its corners rounded. Called with u, returns where the line across it
    at u enters and leaves it (the leading and the trailing edge); .tip is its outermost point."""

    def __init__(self, outline, rounding=2):
        self.points = chaikin(outline, rounding) if rounding else [tuple(p) for p in outline]
        tip = min(self.points, key=lambda p: p[0])
        self.tip = tip
        self.root = max(p[0] for p in self.points)

    def __call__(self, u):
        ys = []
        pts = self.points
        for i in range(len(pts)):
            (u0, y0), (u1, y1) = pts[i], pts[(i + 1) % len(pts)]
            if (u0 <= u < u1) or (u1 <= u < u0):
                ys.append(y0 + (u - u0) / (u1 - u0) * (y1 - y0))
        if len(ys) < 2:
            return self.tip[1], self.tip[1]
        return min(ys), max(ys)

    def chord(self, u):
        y_le, y_te = self(u)
        return y_te - y_le

    def stations(self, count, extra=(), dense=0.75):
        """count span stations from the root to just short of the tip, closer together towards
        the tip, and the extra ones (borders between materials), from the root outwards."""
        u0 = self.root - 0.02
        u1 = self.tip[0] + 0.02
        us = spaced(u0, u1, count, dense_b=dense)
        for e in extra:
            us = [u for u in us if abs(u - e) > 0.12] + [e]
        return sorted(us, reverse=True)


def tip_planform(u, le, te, tip, r_le, r_te):
    """A straight wing's leading and trailing edges (y) at span u (negative: the left side), its
    tip at u = tip rounded: the leading edge's corner with radius r_le, the trailing edge's with
    r_te (quarter circles; where they meet, the tip comes to a point)."""
    d = u - tip  # how far in from the tip
    y_le = le(u) + r_le * (1 - quarter(d, r_le))
    y_te = te(u) - r_te * (1 - quarter(d, r_te))
    if y_le > y_te:
        y_le = y_te = (le(u) * r_te + te(u) * r_le) / (r_le + r_te)
    return y_le, y_te


# --- Lifting surfaces -------------------------------------------------------------------------------

def naca(c):
    """A rounded airfoil's half-thickness along the chord (0-1), 1 at its thickest (c 0.3)."""
    c = min(max(c, 0.0), 1.0)
    return (0.2969 * math.sqrt(c) - 0.1260 * c - 0.3516 * c ** 2 + 0.2843 * c ** 3 - 0.1036 * c ** 4) / 0.1002


CHORD = [(1 - math.cos(math.pi * i / 12)) / 2 for i in range(13)]  # along a chord, dense at the edges


def chord_samples(border=None, ref=None):
    """The chord fractions an airfoil section samples: CHORD, or CHORD stretched so that its sample
    ref falls on the fraction border (a border between materials; the same sample in every
    section, so that the border runs along the loft's edges)."""
    if border is None:
        return list(CHORD)
    r = CHORD[ref]
    return [c * border / r if c <= r else border + (c - r) * (1 - border) / (1 - r) for c in CHORD]


def airfoil_ring(u, y_le, y_te, mid, thickness, under=0.55, camber=0.1, border=None, ref=None):
    """A wing's section at span u (x = u): from the leading edge (y_le) over the top to the
    trailing edge (y_te) and back underneath (chord_samples(border, ref))."""
    cs = chord_samples(border, ref)

    def point(c, sign):
        y = y_le + c * (y_te - y_le)
        z = mid + camber * thickness * math.sin(math.pi * c)
        z += thickness * naca(c) * (1.0 if sign > 0 else -under)
        return Vector((u, y, z))
    return [point(c, 1) for c in cs] + [point(c, -1) for c in reversed(cs[1:-1])]


def lifting_surface(name, us, planform, mid, thickness, mat, under=0.55, camber=0.1, tip=None, border=None,
                    ref=None, paint=None, mats=()):
    """A wing, a tail plane or a fin on the left (u < 0), lofted through airfoil sections at the
    span stations us (from its root to its tip): planform(u) -> (y_le, y_te), mid(u) the height of
    its chord, thickness(u). Closed at the tip in the point tip (u, y) (default: the middle of the
    last station). border(u): a chord fraction every section samples (with CHORD's sample ref),
    where materials meet; paint(u, c0, c1, top) -> the index into [mat] + mats of the face at span
    u covering the chord fractions c0-c1, on the top or underneath."""
    rings, fractions = [], []
    for u in us:
        y_le, y_te = planform(u)
        b = border(u) if border is not None else None
        rings.append(airfoil_ring(u, y_le, y_te, mid(u), thickness(u), under, camber, b, ref))
        cs = chord_samples(b, ref)
        fractions.append(cs + list(reversed(cs[1:-1])))
    if tip is None:
        y_le, y_te = planform(us[-1])
        tip = (us[-1] - 0.02, (y_le + y_te) / 2)
    end = (tip[0], tip[1], mid(tip[0]))
    first = rings[0]
    obj = k.loft(name, rings, mat, start_point=sum(first, Vector()) / len(first), end_point=end)
    if paint is not None:
        for extra_mat in mats:
            obj.data.materials.append(extra_mat)
        n = len(fractions[0])
        for poly in obj.data.polygons[:(len(rings) - 1) * n]:
            i, j = divmod(poly.index, n)
            a = (fractions[i][j] + fractions[i + 1][j]) / 2
            b = (fractions[i][(j + 1) % n] + fractions[i + 1][(j + 1) % n]) / 2
            poly.material_index = paint((us[i] + us[i + 1]) / 2, min(a, b), max(a, b), j < len(CHORD) - 1)
    return k.smooth(obj, 48)


def surface_height(planform, mid, thickness, under=0.55, camber=0.1):
    """The height of a lifting surface's top at (u, y)."""
    def z(u, y):
        y_le, y_te = planform(u)
        c = (y - y_le) / max(y_te - y_le, 1e-6)
        t = thickness(u)
        return mid(u) + camber * t * math.sin(math.pi * min(max(c, 0.0), 1.0)) + t * naca(c)
    return z


def to_fin(obj, x=0.0, z=0.0, cant=0.0):
    """Stands a lifting surface built on the left (span along -x) upright (span along +z), leaning
    out by cant degrees (towards -x for positive cant), its root at (x, z)."""
    rot = Matrix.Rotation(math.radians(90 - cant), 4, "Y")
    obj.data.transform(Matrix.Translation((x, 0, z)) @ rot)
    return obj


def mirrored(obj, name=None):
    """A mirror of obj across x = 0 (the right side of a left part)."""
    copy = k.mirror_x(obj, name or (obj.name[:-2] + "_r" if obj.name.endswith("_l") else obj.name + "_r"))
    copy.data.name = copy.name
    return k.smooth(copy, 48)


# --- Fuselage parts ---------------------------------------------------------------------------------

def fuselage(name, table, mat, segments=24, power=2.0, step=0.45, nose=None, tail=None):
    """A round hull along y through table rows (y, half-width, centre z, top, bottom), lofted
    smoothly between them and closed at both ends (in nose and tail, default the end rows'
    centres). Returns the object and the curve through the table."""
    curve = Curve(table)
    y0, y1 = table[0][0], table[-1][0]
    count = max(2, int(round((y1 - y0) / step)))
    # Closer together at the ends, where the hull rounds off.
    stations = spaced(y0, y1, count + 1, dense_a=0.35, dense_b=0.35)
    rings = []
    for y in stations:
        hw, zc, top, bottom = curve(y)
        rings.append(k.ring(y, max(hw, 0.02), 1.0, segments, z=zc, top=max(top, 0.02), bottom=max(bottom, 0.02),
                            power=power))
    obj = k.loft(name, rings, mat, start_point=nose or (0, y0, curve(y0)[1]),
                 end_point=tail or (0, y1, curve(y1)[1]))
    return k.smooth(obj, 50), curve


def hull_top(curve, power=2.0):
    """The height of a fuselage's top at (u, y) (curve from fuselage())."""
    def z(u, y):
        hw, zc, top, _ = curve(y)
        if hw <= 0.02 or abs(u) >= hw:
            return zc
        return zc + top * (1 - (abs(u) / hw) ** power) ** (1 / power)
    return z


def bubble(name, table, base, mat, segments=20, sink=0.5, under=1.2, step=0.32):
    """A bubble along y through table rows (y, half-width, height above base(y)), sunk `sink`
    into what it sits on (base(y): the height of the fuselage's top there): canopies and their
    sills."""
    curve = Curve(table)
    y0, y1 = table[0][0], table[-1][0]
    count = max(8, int(round((y1 - y0) / step)))
    rings = []
    for y in spaced(y0, y1, count + 1, dense_a=0.4, dense_b=0.4)[1:-1]:
        hw, h = curve(y)
        rings.append(k.ring(y, max(hw, 0.03), 1.0, segments, z=base(y) - sink, top=max(h + sink, 0.05),
                            bottom=under))
    obj = k.loft(name, rings, mat, start_point=(0, y0, base(y0) - sink), end_point=(0, y1, base(y1) - sink))
    return k.smooth(obj, 60)


def tube(name, points, radius, mat, segments=6, radii=None, squash=1.0):
    """A round tube through points (Vectors), radius thick (or radii[i] at each point; squash
    scales its height), closed with rounded ends."""
    rings = []
    for i, p in enumerate(points):
        r = radii[i] if radii else radius
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(tangent).normalized()
        angles = [2 * math.pi * j / segments for j in range(segments)]
        rings.append([p + (side * math.cos(a) + up * squash * math.sin(a)) * r for a in angles])
    t0 = (points[1] - points[0]).normalized()
    t1 = (points[-1] - points[-2]).normalized()
    r0, r1 = (radii[0], radii[-1]) if radii else (radius, radius)
    obj = k.loft(name, rings, mat, start_point=points[0] - t0 * r0 * 0.8, end_point=points[-1] + t1 * r1 * 0.8)
    return k.smooth(obj, 60)


def intake(name, mouth_y, back_y, centre, half_w, half_h, mat, dark, lip=0.2, depth=0.9, power=2.4,
           segments=16, taper=None):
    """An intake: a duct fairing whose open mouth faces down the screen (-y) at mouth_y and which
    runs back into the hull at back_y, narrowing (taper(t), t 0 at the mouth and 1 at the back).
    centre(y) -> (x, z) of its middle; half_w, half_h its mouth's half sizes. Its inside is dark."""
    if taper is None:
        def taper(t):
            return max(0.0, 1 - t ** 2.2)
    cx, cz = centre(mouth_y)
    edge = max(half_w, half_h)
    rings = []
    # From inside the duct out over the lip, then back along the outside.
    for dy, s in ((depth, 1 - lip / edge * 1.7), (0.22, 1 - lip / edge), (-0.03, 1 - lip / edge * 0.45),
                  (0.08, 1.0)):
        rings.append(k.ring(mouth_y + dy, half_w * s, half_h * s, segments, z=cz, x=cx, power=power))
    count = 9
    for i in range(1, count + 1):
        t = i / count
        y = mouth_y + 0.08 + (back_y - mouth_y - 0.08) * t
        x, z = centre(y)
        f = taper(t)
        rings.append(k.ring(y, max(half_w * f, 0.04), max(half_h * (0.4 + 0.6 * f), 0.04), segments, z=z, x=x,
                            power=power))
    bx, bz = centre(back_y)
    obj = k.loft(name, rings, mat, start_point=(cx, mouth_y + depth + 0.1, cz), end_point=(bx, back_y, bz))
    obj.data.materials.append(dark)
    n = segments
    sides = (len(rings) - 1) * n
    for poly in obj.data.polygons:
        if poly.index < 2 * n or sides <= poly.index < sides + n:  # the duct and its far end
            poly.material_index = 1
    return k.smooth(obj, 50)


def nozzle(name, y0, y1, radius, mat, dark, axis_x=0.0, axis_z=0.0, segments=20, lip=0.14):
    """A jet nozzle along +y from y0 (inside the hull) to its mouth at y1: a short metal can with a
    rolled lip and a dark core."""
    r_in = radius - lip
    profile = [(y0, 0.0), (y0, radius), (y1 - 0.25, radius * 1.02), (y1 - 0.05, radius * 0.98),
               (y1, radius - lip * 0.5), (y1 - 0.08, r_in), (y1 - 0.5, r_in * 0.97), (y1 - 0.5, 0.0)]
    can = k.lathe(name, profile, mat, segments, axis_x=axis_x, axis_z=axis_z)
    k.smooth(can, 50)
    core = k.lathe(name + "_core", [(y1 - 0.48, 0.0), (y1 - 0.48, r_in * 0.95), (y1 - 0.44, r_in * 0.95),
                                    (y1 - 0.44, 0.0)], dark, segments, axis_x=axis_x, axis_z=axis_z)
    return can, core


def lamp(name, centre, radii, mat, segments=14, rings_count=7):
    """A small lens: an ellipsoid, sunk into what it sits on."""
    return k.smooth(k.ellipsoid(name, centre, radii, mat, segments, rings_count), 60)


def hull_seam(name, curve, y, mat, radius=0.12, sink=0.06, power=2.0, count=17):
    """A panel line round the top of a fuselage (curve from fuselage()) at y: a thin dark tube
    over it from side to side, sunk so that a narrow line shows."""
    hw, zc, top, bottom = curve(y)
    points = []
    for i in range(count):
        a = math.radians(-12 + 204 * i / (count - 1))
        c, s = math.cos(a), math.sin(a)
        px = math.copysign(abs(c) ** (2 / power), c) * (hw - sink)
        pz = math.copysign(abs(s) ** (2 / power), s) * ((top if s >= 0 else bottom) - sink)
        points.append(Vector((px, y, zc + pz)))
    return tube(name, points, radius, mat, segments=6)


# --- jet_cross (F 125) ------------------------------------------------------------------------------
# A grey early jet, nose down: a long pointed nose (rows 20-27), side intakes in front of the wing
# roots (rows 18-19, their dark mouths), a bubble canopy over the wing roots (rows 13-17, dark with
# a bright glint), straight tapered wings (rows 11-17: the trailing edge straight along row 11, the
# leading edge sweeping back a little to the rounded tips in columns 2 and 22) with lighter ailerons
# near the tips (row 12), a slim tail boom (rows 6-10, its top lit: column 12) ending in a nozzle, a
# panel line round it in front of the tail (the upscale's dark ring, rows 5-6), and a cruciform
# tail: tail planes (rows 2-5) crossed by a swept fin whose top reaches row 0.

def build_cross():
    m = {
        "body": k.material("jetcross_body", palette=8, metallic=0.45, roughness=0.32),
        "wing": k.material("jetcross_wing", palette=7, metallic=0.45, roughness=0.36),
        "aileron": k.material("jetcross_aileron", palette=9, metallic=0.4, roughness=0.32),
        "seam": k.material("jetcross_seam", palette=3, metallic=0.3, roughness=0.55),
        "glass": k.material("jetcross_glass", palette=3, metallic=0.0, roughness=0.22),
        "frame": k.material("jetcross_frame", palette=5, metallic=0.45, roughness=0.3),
        "dark": k.material("jetcross_dark", palette=1, metallic=0.2, roughness=0.7),
        "nozzle": k.material("jetcross_nozzle", palette=4, metallic=0.55, roughness=0.3),
    }
    # The fuselage: y, half-width, centre z, top, bottom.
    table = [(-13.75, 0.05, -0.3, 0.05, 0.05), (-13.3, 0.5, -0.27, 0.5, 0.45), (-12.6, 0.9, -0.22, 0.88, 0.8),
             (-11.8, 1.2, -0.17, 1.17, 1.05), (-11.0, 1.45, -0.12, 1.42, 1.25), (-10.0, 1.75, -0.07, 1.72, 1.5),
             (-9.0, 2.0, -0.03, 1.98, 1.7), (-8.0, 2.15, 0.0, 2.15, 1.82), (-7.0, 2.27, 0.0, 2.28, 1.92),
             (-6.0, 2.42, 0.0, 2.42, 2.0), (-5.0, 2.55, 0.0, 2.52, 2.08), (-4.0, 2.62, 0.0, 2.56, 2.12),
             (-3.0, 2.62, 0.0, 2.56, 2.12), (-2.0, 2.58, 0.0, 2.52, 2.08), (-1.0, 2.5, 0.0, 2.46, 2.03),
             (0.0, 2.42, 0.0, 2.4, 1.98), (1.5, 2.32, 0.0, 2.3, 1.9), (3.0, 2.22, 0.0, 2.2, 1.8),
             (5.0, 2.14, 0.02, 2.05, 1.68), (7.0, 2.06, 0.05, 1.9, 1.52), (8.5, 1.85, 0.08, 1.7, 1.38),
             (9.5, 1.6, 0.1, 1.5, 1.22), (10.5, 1.34, 0.12, 1.26, 1.04), (11.3, 1.15, 0.13, 1.07, 0.9),
             (11.6, 1.1, 0.13, 1.02, 0.86)]
    _, curve = fuselage("fuselage", table, m["body"], step=0.42)
    top = hull_top(curve)
    nozzle("nozzle", 11.0, 11.95, 1.1, m["nozzle"], m["dark"], axis_z=curve(11.6)[1])
    hull_seam("tail_seam", curve, 8.0, m["seam"])

    # The canopy: a bubble over the wing roots (rows 13-18), in a frame.
    bubble("frame", [(-5.15, 0.0, 0.0), (-4.85, 1.05, 0.26), (-4.2, 1.5, 0.36), (-3.0, 1.72, 0.4), (-1.8, 1.7, 0.4),
                     (-0.6, 1.5, 0.36), (0.4, 1.12, 0.3), (1.05, 0.0, 0.0)], lambda y: top(0.0, y), m["frame"],
           sink=0.4)
    bubble("canopy", [(-4.8, 0.0, 0.0), (-4.5, 0.78, 0.6), (-4.0, 1.15, 0.98), (-3.3, 1.36, 1.22),
                      (-2.4, 1.43, 1.36), (-1.4, 1.39, 1.33), (-0.4, 1.22, 1.16), (0.3, 0.88, 0.82), (0.8, 0.0, 0.0)],
           lambda y: top(0.0, y) + 0.24, m["glass"], sink=0.45)

    # The intakes either side, in front of the wing roots (rows 18-19).
    def intake_centre(y):
        t = smoothstep(-6.4, -1.6, y)
        return (-(2.25 - 0.55 * t), -0.25 - 0.2 * t)
    mirrored(intake("intake_l", -6.35, -1.6, intake_centre, 0.92, 1.12, m["body"], m["dark"]))

    # The wings: straight, tapered (the leading edge sweeping back a little), rounded tips; the
    # ailerons near the tips (row 12) lighter, a seam along their hinge.
    le = Curve([(-10.2, -2.62), (-9.0, -2.75), (-7.5, -3.18), (-6.0, -3.55), (-4.5, -3.78), (-3.0, -3.85),
                (-1.5, -3.85)])

    def wing_plan(u):
        return tip_planform(u, le, lambda u: 2.62, -10.18, 1.6, 0.7)

    def wing_mid(u):
        return -0.95 + 0.075 * max(0.0, -u - 2.0)

    def wing_thick(u):
        return (0.34 + 0.32 * smoothstep(-10.2, -2.5, u)) * (0.3 + 0.7 * quarter(u + 10.18, 0.6))

    a0, a1, hinge = -8.4, -4.6, 0.7

    def paint(u, c0, c1, top_side):
        return 1 if a0 < u < a1 and c0 >= hinge - 1e-6 else 0

    us = [-1.6, -2.4, -3.2, -4.0, a1, -5.4, -6.2, -7.0, -7.8, a0, -9.0] + spaced(-9.4, -10.16, 6, dense_b=0.6)
    wing = lifting_surface("wing_l", us, wing_plan, wing_mid, wing_thick, m["wing"], under=0.5,
                           border=lambda u: hinge, ref=8, paint=paint, mats=(m["aileron"],))
    height = surface_height(wing_plan, wing_mid, wing_thick, under=0.5)
    line = []
    for i in range(13):
        u = a1 - (a1 - a0) * i / 12
        y_le, y_te = wing_plan(u)
        y = y_le + hinge * (y_te - y_le)
        line.append(Vector((u, y, height(u, y) - 0.06)))
    seam = tube("aileron_seam_l", line, 0.12, m["seam"])
    for part in (wing, seam):
        mirrored(part)

    # The tail planes (rows 2-5): the trailing edge straight along row 2, the leading edge swept.
    tle = Curve([(-6.2, 9.65), (-5.2, 9.25), (-4.2, 8.6), (-3.2, 8.38), (-1.0, 8.35)])

    def tail_plan(u):
        return tip_planform(u, tle, lambda u: 11.62, -6.18, 0.9, 0.35)

    us = [-0.6, -1.4, -2.2, -3.0, -3.8, -4.5, -5.1, -5.55, -5.85, -6.05, -6.16]
    mirrored(lifting_surface("stab_l", us, tail_plan, lambda u: 0.35 + 0.04 * max(0.0, -u - 1.0),
                             lambda u: (0.2 + 0.16 * smoothstep(-6.2, -1.5, u)) * (0.3 + 0.7 * quarter(u + 6.18, 0.4)),
                             m["wing"], under=0.6))

    # The fin: swept, its top reaching row 0, standing on the boom behind the lit spine (rows 6-10).
    fle = Curve([(0.0, 7.0), (-1.5, 8.55), (-3.0, 10.0), (-4.0, 10.95), (-4.75, 11.6)])
    fte = Curve([(0.0, 11.95), (-2.0, 12.45), (-4.0, 13.1), (-4.75, 13.45)])

    def fin_plan(u):
        return tip_planform(u, fle, fte, -4.75, 0.9, 0.3)

    us = [0.0, -0.6, -1.2, -1.8, -2.4, -3.0, -3.5, -3.9, -4.2, -4.45, -4.62, -4.73]
    fin = lifting_surface("fin", us, fin_plan, lambda u: 0.0, lambda u: 0.32 - 0.035 * (-u), m["body"],
                          under=1.0, camber=0.0)
    to_fin(fin, z=top(0.0, 9.5) - 0.4)


# --- jet_green (F 3) --------------------------------------------------------------------------------
# A green arrow, nose down: a delta wing whose leading edges run straight from the nose (row 25) to
# the tips (rows 6-11, columns 5 and 21) and whose trailing edges come back in from the tips to the
# fuselage at row 10, orange elevons along them (rows 8-12); a raised body down the middle with the
# canopy (rows 15-21: dark, a bright glint) in a light green sill, a light green hump behind it
# (rows 13-15), a panel line and two yellow dorsal intakes behind that (rows 11-12); twin orange fins
# canted out from the fuselage's rear (their tips at rows 3-4) and a slim tail spike (rows 1-5). The
# sprite draws the fins and elevons khaki (index 26) with orange highlights (122); the upscale, and
# these, orange.

GREEN_AXIS = 1.5


def build_green():
    m = {
        "body": k.material("jetgreen_body", palette=42, metallic=0.35, roughness=0.3),
        "wing": k.material("jetgreen_wing", palette=41, metallic=0.35, roughness=0.34),
        "light": k.material("jetgreen_light", palette=44, metallic=0.3, roughness=0.3),
        "orange": k.material("jetgreen_orange", palette=122, metallic=0.35, roughness=0.3),
        "yellow": k.material("jetgreen_yellow", palette=125, metallic=0.2, roughness=0.3),
        "glass": k.material("jetgreen_glass", palette=34, metallic=0.0, roughness=0.22),
        "dark": k.material("jetgreen_dark", palette=32, metallic=0.2, roughness=0.7),
        "seam": k.material("jetgreen_seam", palette=36, metallic=0.3, roughness=0.5),
    }
    # The fuselage, from the nose to the tip of the spike: y, half-width, centre z, top, bottom.
    table = [(-11.65, 0.05, -0.35, 0.05, 0.05), (-11.25, 0.5, -0.3, 0.45, 0.35), (-10.6, 1.0, -0.22, 0.85, 0.6),
             (-9.8, 1.38, -0.15, 1.2, 0.8), (-8.8, 1.7, -0.08, 1.5, 0.95), (-7.5, 2.0, 0.0, 1.75, 1.05),
             (-6.0, 2.2, 0.0, 1.9, 1.1), (-4.5, 2.32, 0.0, 2.0, 1.15), (-3.0, 2.4, 0.0, 2.12, 1.15),
             (-1.5, 2.45, 0.0, 2.3, 1.15), (0.0, 2.42, 0.0, 2.25, 1.12), (1.5, 2.35, 0.0, 2.02, 1.1),
             (3.0, 2.25, 0.0, 1.8, 1.05), (4.5, 2.12, 0.05, 1.6, 1.0), (6.0, 1.95, 0.1, 1.42, 0.95),
             (7.3, 1.7, 0.15, 1.26, 0.85), (8.5, 1.42, 0.2, 1.1, 0.75), (9.6, 1.15, 0.25, 0.98, 0.68),
             (10.6, 1.02, 0.28, 0.9, 0.62), (11.5, 0.88, 0.3, 0.78, 0.55), (12.2, 0.58, 0.3, 0.52, 0.38),
             (12.65, 0.05, 0.3, 0.05, 0.05)]
    _, curve = fuselage("fuselage", table, m["body"], step=0.4)
    top = hull_top(curve)

    # The canopy in its light green sill (rows 15-21).
    glass = [(-7.5, 0.0, 0.0), (-7.2, 0.8, 0.5), (-6.6, 1.25, 0.95), (-5.6, 1.48, 1.2), (-4.4, 1.55, 1.3),
             (-3.2, 1.45, 1.2), (-2.3, 1.15, 0.95), (-1.8, 0.75, 0.6), (-1.5, 0.0, 0.0)]
    sill = [(-7.95, 0.0, 0.0), (-7.6, 1.2, 0.3), (-6.8, 1.75, 0.42), (-5.4, 1.98, 0.48), (-4.2, 2.02, 0.5),
            (-2.8, 1.9, 0.5), (-1.7, 1.55, 0.45), (-1.1, 1.0, 0.35), (-0.8, 0.0, 0.0)]
    bubble("sill", sill, lambda y: top(0.0, y), m["light"], sink=0.4)
    bubble("canopy", glass, lambda y: top(0.0, y) + 0.3, m["glass"], sink=0.4)
    hull_seam("seam", curve, 0.55, m["seam"])

    # The yellow dorsal intakes (rows 11-12), their mouths facing forward.
    def scoop_centre(y):
        return (-1.12, top(-1.12, y) - 0.12)
    mirrored(intake("scoop_l", 1.1, 3.8, scoop_centre, 0.66, 0.58, m["yellow"], m["dark"], lip=0.15, depth=0.6,
                    taper=lambda t: (1 - t ** 3) ** 0.5))

    # The wing: the leading edge y = -14 - 2u fitted to the sprite's staircase, the trailing edge
    # y = 0.8 - u, the tip's outer edge nearly upright (column 5).
    plan = Plan([(-0.5, -10.0), (-0.9, -10.4), (-2.0, -10.0), (-4.5, -5.0), (-7.0, 0.0), (-7.75, 1.5),
                 (-8.15, 2.7), (-8.3, 4.2), (-8.3, 5.6), (-8.15, 6.9), (-7.75, 7.65), (-7.2, 7.9), (-6.75, 7.65),
                 (-5.0, 5.8), (-3.3, 4.1), (-2.6, 3.5), (-1.6, 3.1), (-0.5, 3.0)], rounding=2)
    e0, e1, width = -6.4, -2.95, 1.15  # the elevons: span and width (y) along the trailing edge

    def elevon_border(u):
        return max(0.5, 1 - width / max(plan.chord(u), 1e-3))

    def paint(u, c0, c1, top_side):
        return 1 if e0 < u < e1 and c0 >= elevon_border(u) - 0.02 else 0

    def wing_mid(u):
        return -0.42 + 0.035 * max(0.0, -u - 1.0)

    def wing_thick(u):
        return min(0.75, max(0.04, 0.052 * plan.chord(u)))

    us = plan.stations(22, extra=(e0, e1))
    wing = lifting_surface("wing_l", us, plan, wing_mid, wing_thick, m["wing"], under=0.5, border=elevon_border,
                           ref=9, paint=paint, mats=(m["orange"],), tip=plan.tip)
    height = surface_height(plan, wing_mid, wing_thick, under=0.5)
    line = []
    for i in range(12):
        u = e1 - (e1 - e0) * i / 11
        y_le, y_te = plan(u)
        y = y_te - width
        line.append(Vector((u, y, height(u, y) - 0.06)))
    seam = tube("elevon_seam_l", line, 0.11, m["seam"])
    for part in (wing, seam):
        mirrored(part)

    # The twin fins, canted out from the fuselage's rear flanks (their tips at rows 3-4).
    fle = Curve([(0.0, 4.2), (-1.5, 6.4), (-3.3, 9.3)])
    fte = Curve([(0.0, 8.6), (-1.5, 9.6), (-3.3, 10.95)])

    def fin_plan(u):
        return tip_planform(u, fle, fte, -3.35, 0.7, 0.25)

    us = [0.0, -0.5, -1.0, -1.5, -2.0, -2.4, -2.75, -3.0, -3.18, -3.3]
    fin = lifting_surface("fin_l", us, fin_plan, lambda u: 0.0, lambda u: 0.24 - 0.02 * (-u), m["orange"],
                          under=1.0, camber=0.0, tip=(-3.35, 10.3))
    to_fin(fin, x=-1.15, z=0.75, cant=38)
    mirrored(fin)


# --- jet_brown (F 49) -------------------------------------------------------------------------------
# A stubby brown jet, nose down: a broad fuselage widening from the blunt nose (row 25) to the wing
# roots (rows 18-20), a round canopy (rows 15-19: dark in a dark frame, a bright glint), wings with a
# straight trailing edge along row 10 and leading edges swept at 45 degrees to the tips in columns 3
# and 22, grey along their outer leading edges (rows 12-16); two red lamps on the flanks where the
# booms start (row 12); twin booms running back to row 0 (columns 10 and 15), each with a small fin
# at its end, grey tail planes on their outer sides (rows 4-8), and the grey nozzle between them
# (rows 4-6) behind the fuselage's tapering rear (rows 7-9).

BROWN_AXIS = 1.0
BROWN_LAMP = (2.6, 1.55)  # the red lamps (u, y)


def build_brown():
    palette = k.level_palette()
    m = {
        "body": k.material("jetbrown_body", palette=24, metallic=0.35, roughness=0.32),
        "wing": k.material("jetbrown_wing", palette=23, metallic=0.35, roughness=0.34),
        "grey": k.material("jetbrown_grey", palette=7, metallic=0.5, roughness=0.3),
        "edge": k.material("jetbrown_edge", palette=5, metallic=0.5, roughness=0.3),
        "nozzle": k.material("jetbrown_nozzle", palette=5, metallic=0.55, roughness=0.3),
        "glass": k.material("jetbrown_glass", palette=17, metallic=0.0, roughness=0.22),
        "frame": k.material("jetbrown_frame", palette=18, metallic=0.4, roughness=0.35),
        "dark": k.material("jetbrown_dark", palette=16, metallic=0.2, roughness=0.7),
        "red": k.material("jetbrown_red", palette=116, roughness=0.25, emission=palette[119],
                          emission_strength=2.5),
    }
    # The fuselage, from the blunt nose to its rear between the booms: y, half-width, centre z, top,
    # bottom.
    table = [(-11.62, 0.5, -0.45, 0.3, 0.24), (-11.4, 0.95, -0.42, 0.56, 0.42), (-10.9, 1.42, -0.36, 0.86, 0.62),
             (-10.2, 1.75, -0.28, 1.1, 0.76), (-9.3, 2.12, -0.18, 1.34, 0.88), (-8.3, 2.6, -0.1, 1.58, 1.0),
             (-7.3, 3.0, -0.04, 1.78, 1.1), (-6.3, 3.45, 0.0, 1.94, 1.18), (-5.3, 3.62, 0.0, 2.04, 1.24),
             (-4.3, 3.58, 0.0, 2.08, 1.26), (-3.0, 3.5, 0.0, 2.1, 1.26), (-1.5, 3.32, 0.0, 2.06, 1.24),
             (0.0, 3.15, 0.0, 2.0, 1.2), (1.5, 3.0, 0.0, 1.92, 1.16), (3.0, 2.82, 0.0, 1.82, 1.1),
             (4.2, 2.3, 0.04, 1.6, 1.0), (5.3, 1.72, 0.08, 1.38, 0.92), (6.3, 1.45, 0.1, 1.2, 0.84),
             (7.1, 1.36, 0.12, 1.12, 0.8), (7.5, 1.32, 0.12, 1.08, 0.78)]
    _, curve = fuselage("fuselage", table, m["body"], step=0.4, segments=28)
    top = hull_top(curve)
    nozzle("nozzle", 6.9, 10.25, 1.24, m["nozzle"], m["dark"], axis_z=0.14)

    # The round canopy (rows 15-19) in a dark frame.
    glass = [(-5.9, 0.0, 0.0), (-5.6, 1.05, 0.62), (-5.0, 1.6, 1.12), (-4.1, 1.85, 1.42), (-3.2, 1.85, 1.45),
             (-2.3, 1.6, 1.25), (-1.6, 1.05, 0.8), (-1.25, 0.0, 0.0)]
    frame = [(-6.25, 0.0, 0.0), (-5.9, 1.35, 0.3), (-5.2, 2.0, 0.42), (-4.1, 2.22, 0.48), (-3.0, 2.2, 0.48),
             (-2.0, 1.85, 0.42), (-1.2, 1.25, 0.32), (-0.85, 0.0, 0.0)]
    bubble("frame", frame, lambda y: top(0.0, y), m["frame"], sink=0.4)
    bubble("canopy", glass, lambda y: top(0.0, y) + 0.28, m["glass"], sink=0.4)
    bubble("spine", [(-1.6, 0.0, 0.0), (-1.0, 0.55, 0.32), (1.0, 0.7, 0.36), (3.5, 0.66, 0.34), (5.5, 0.52, 0.26),
                     (6.9, 0.3, 0.12), (7.4, 0.0, 0.0)], lambda y: top(0.0, y), m["body"], segments=12, sink=0.3,
           under=0.5)

    # The wings: the trailing edge along row 10, the leading edge y = -u - 8.35 (fitted to the
    # sprite's 45-degree staircase); grey along the outer leading edge.
    plan = Plan([(-1.0, -7.4), (-3.5, -4.85), (-6.0, -2.35), (-8.6, 0.25), (-9.35, 1.0), (-9.7, 1.6),
                 (-9.8, 2.7), (-9.82, 3.45), (-9.75, 3.63), (-9.6, 3.64), (-6.0, 3.63), (-3.0, 3.63), (-1.0, 3.63)],
                rounding=2)
    g0, band = -4.3, 1.75  # the grey leading edge: from u g0 out to the tip, band wide (y)

    def edge_border(u):
        return min(0.6, band / max(plan.chord(u), 1e-3))

    def paint(u, c0, c1, top_side):
        return 1 if u < g0 and c1 <= edge_border(u) + 0.02 else 0

    def wing_mid(u):
        return -0.7 + 0.06 * max(0.0, -u - 2.0)

    def wing_thick(u):
        return min(0.72, max(0.12, 0.1 * plan.chord(u)))

    us = plan.stations(20, extra=(g0,))
    wing = lifting_surface("wing_l", us, plan, wing_mid, wing_thick, m["wing"], under=0.5, border=edge_border,
                           ref=4, paint=paint, mats=(m["edge"],), tip=plan.tip)
    mirrored(wing)

    # The booms (columns 10 and 15): out of the fuselage's tapering rear (rows 7-9), bending out to
    # run back to row 0, each with a small fin at its end.
    path = Curve([(3.4, -1.65, 0.45, 0.85), (4.5, -1.85, 0.36, 0.92), (5.8, -2.2, 0.24, 0.95), (7.0, -2.45, 0.18, 0.95),
                  (8.0, -2.5, 0.15, 0.95), (12.2, -2.5, 0.15, 0.94), (13.0, -2.5, 0.15, 0.86), (13.4, -2.5, 0.15, 0.64),
                  (13.62, -2.5, 0.15, 0.3)])
    ys = spaced(3.4, 13.62, 28, dense_b=0.45)
    left = tube("boom_l", [Vector((path(y)[0], y, path(y)[1])) for y in ys], 1.0, m["body"], segments=16,
                radii=[path(y)[2] for y in ys])
    k.smooth(left, 50)
    fle = Curve([(0.0, 8.7), (-1.4, 10.6), (-2.7, 12.3)])
    fte = Curve([(0.0, 13.2), (-1.4, 13.4), (-2.7, 13.62)])
    us = [0.0, -0.5, -1.0, -1.5, -1.9, -2.25, -2.5, -2.66]
    fin = lifting_surface("bfin_l", us, lambda u: tip_planform(u, fle, fte, -2.7, 0.7, 0.2), lambda u: 0.0,
                          lambda u: 0.24 - 0.025 * (-u), m["body"], under=1.0, camber=0.0, tip=(-2.7, 13.2))
    to_fin(fin, x=-2.5, z=0.15 + 0.45, cant=0)

    # The grey tail planes on the booms' outer sides (rows 4-8): their leading edge y = 0.7 - u, the
    # trailing edge along row 4, the tip at column 6.
    tplan = Plan([(-2.2, 3.4), (-6.25, 7.0), (-6.62, 7.7), (-6.62, 9.1), (-6.3, 9.6), (-2.2, 9.6)], rounding=2)
    us = tplan.stations(12)
    stab = lifting_surface("tail_l", us, tplan, lambda u: 0.2 + 0.03 * max(0.0, -u - 2.5),
                           lambda u: min(0.32, max(0.06, 0.07 * tplan.chord(u))), m["grey"], under=0.7,
                           tip=tplan.tip)
    for part in (left, fin, stab):
        mirrored(part)

    # The red lamps on the flanks where the booms start (row 12).
    u, y = BROWN_LAMP
    z = top(-u, y)
    left_lamp = lamp("lamp_l", (-u, y, z - 0.2), (0.3, 0.85, 0.34), m["red"])
    mirrored(left_lamp)


# --- jet_delta (F 11) -------------------------------------------------------------------------------
# A grey delta, nose down: swept wings whose leading edges run straight from the tips (rows 5-8,
# columns 2 and 22) down to the nose (row 26) as chines beside it, their trailing edges coming back
# in from the tips to the fuselage at row 9, a panel line along each leading edge; intakes at the
# wing roots (rows 18-19, the dark slots beside the fuselage); a framed canopy (rows 16-20, dark
# with a bright glint) and a hump behind it (rows 13-15); the slim rear (rows 6-8) ending in a
# nozzle, and a cruciform tail: swept tail planes (rows 2-5) and a fin reaching row 0.

def build_delta():
    m = {
        "body": k.material("jetdelta_body", palette=8, metallic=0.45, roughness=0.32),
        "wing": k.material("jetdelta_wing", palette=8, metallic=0.45, roughness=0.36),
        "slat": k.material("jetdelta_slat", palette=10, metallic=0.45, roughness=0.32),
        "seam": k.material("jetdelta_seam", palette=4, metallic=0.3, roughness=0.5),
        "glass": k.material("jetdelta_glass", palette=4, metallic=0.0, roughness=0.22),
        "frame": k.material("jetdelta_frame", palette=5, metallic=0.45, roughness=0.3),
        "dark": k.material("jetdelta_dark", palette=1, metallic=0.2, roughness=0.7),
        "nozzle": k.material("jetdelta_nozzle", palette=4, metallic=0.55, roughness=0.3),
    }
    table = [(-12.65, 0.05, -0.35, 0.05, 0.05), (-12.2, 0.6, -0.3, 0.55, 0.45), (-11.6, 1.08, -0.25, 0.98, 0.8),
             (-11.0, 1.5, -0.2, 1.32, 1.05), (-10.3, 1.95, -0.14, 1.62, 1.25), (-9.5, 2.12, -0.08, 1.78, 1.38),
             (-8.5, 2.3, -0.03, 1.92, 1.48), (-7.0, 2.5, 0.0, 2.05, 1.55), (-5.5, 2.62, 0.0, 2.12, 1.6),
             (-4.0, 2.7, 0.0, 2.18, 1.62), (-2.5, 2.72, 0.0, 2.3, 1.62), (-1.0, 2.7, 0.0, 2.38, 1.6),
             (0.5, 2.62, 0.0, 2.3, 1.56), (2.0, 2.5, 0.0, 2.15, 1.5), (3.5, 2.35, 0.0, 2.0, 1.42),
             (5.0, 2.18, 0.02, 1.88, 1.35), (6.5, 2.1, 0.05, 1.78, 1.28), (7.5, 2.02, 0.07, 1.68, 1.22),
             (8.5, 1.82, 0.09, 1.52, 1.12), (9.5, 1.56, 0.1, 1.32, 1.0), (10.5, 1.3, 0.12, 1.12, 0.88),
             (11.2, 1.12, 0.13, 0.98, 0.78), (11.45, 1.08, 0.13, 0.95, 0.76)]
    _, curve = fuselage("fuselage", table, m["body"], step=0.42)
    top = hull_top(curve)
    nozzle("nozzle", 10.9, 11.85, 1.06, m["nozzle"], m["dark"], axis_z=curve(11.45)[1])

    # The canopy (rows 16-20) in its frame.
    glass = [(-7.2, 0.0, 0.0), (-6.9, 0.75, 0.55), (-6.3, 1.15, 0.95), (-5.3, 1.4, 1.25), (-4.2, 1.48, 1.35),
             (-3.1, 1.4, 1.28), (-2.2, 1.12, 1.0), (-1.7, 0.72, 0.6), (-1.4, 0.0, 0.0)]
    frame = [(-7.55, 0.0, 0.0), (-7.2, 1.1, 0.28), (-6.4, 1.6, 0.4), (-5.0, 1.8, 0.45), (-3.6, 1.8, 0.45),
             (-2.3, 1.55, 0.4), (-1.4, 1.1, 0.32), (-1.0, 0.0, 0.0)]
    bubble("frame", frame, lambda y: top(0.0, y), m["frame"], sink=0.4)
    bubble("canopy", glass, lambda y: top(0.0, y) + 0.26, m["glass"], sink=0.4)
    bubble("fairing", [(-2.2, 0.0, 0.0), (-1.6, 1.2, 0.42), (-0.6, 1.25, 0.46), (0.6, 1.0, 0.36), (1.8, 0.6, 0.2),
                       (2.6, 0.0, 0.0)], lambda y: top(0.0, y), m["body"], segments=16, sink=0.3, under=0.6)

    # The intakes in the wing roots (rows 18-19).
    def intake_centre(y):
        t = smoothstep(-6.0, -1.4, y)
        return (-(2.85 - 0.5 * t), 0.85 - 0.2 * t)
    mirrored(intake("intake_l", -6.0, -1.4, intake_centre, 0.66, 0.72, m["body"], m["dark"], lip=0.15))

    # The wings: the leading edge y = -15 - 2u (fitted to the sprite's staircase) from the tip down to
    # the nose, the trailing edge y = 0.8 - u, the tip's outer edge nearly upright (column 2).
    plan = Plan([(-0.5, -11.3), (-0.75, -11.95), (-1.75, -11.5), (-2.0, -10.95), (-3.0, -8.75), (-4.0, -6.4),
                 (-5.0, -4.55), (-6.0, -2.75), (-8.0, 1.0), (-9.2, 3.4),
                 (-9.75, 4.6), (-10.05, 6.0), (-10.1, 7.4), (-9.9, 8.3), (-9.4, 8.65), (-8.6, 8.72), (-7.95, 8.6),
                 (-5.0, 5.8), (-3.6, 4.4), (-2.6, 3.6), (-1.6, 3.2), (-0.6, 3.0)], rounding=2)

    def wing_mid(u):
        return -0.38 + 0.04 * max(0.0, -u - 1.0)

    def wing_thick(u):
        return min(0.8, max(0.04, 0.062 * plan.chord(u)))

    # The leading edge's slats lighter (the sprite's bright strip along it), a panel line behind
    # them, from near the tip to the intakes.
    s0, s1, slat = -9.0, -3.3, 1.7

    def slat_border(u):
        return min(0.6, slat / max(plan.chord(u), 1e-3))

    def paint(u, c0, c1, top_side):
        return 1 if s0 - 0.6 < u < s1 and c1 <= slat_border(u) + 0.02 else 0

    us = plan.stations(24, extra=(s1,))
    wing = lifting_surface("wing_l", us, plan, wing_mid, wing_thick, m["wing"], under=0.5, border=slat_border, ref=3,
                           paint=paint, mats=(m["slat"],), tip=plan.tip)
    height = surface_height(plan, wing_mid, wing_thick, under=0.5)
    line = []
    for i in range(16):
        u = s0 + (s1 - s0) * i / 15
        y_le, _ = plan(u)
        y = y_le + slat
        line.append(Vector((u, y, height(u, y) - 0.06)))
    seam = tube("slat_seam_l", line, 0.12, m["seam"])
    for part in (wing, seam):
        mirrored(part)

    # The tail planes (rows 2-5): their leading edge y = 4.2 - u, the trailing edge along row 2.
    tplan = Plan([(-0.8, 6.1), (-2.0, 6.2), (-4.75, 8.95), (-5.12, 9.6), (-5.18, 10.7), (-5.0, 11.4),
                  (-4.6, 11.62), (-0.8, 11.62)], rounding=2)
    us = tplan.stations(13)
    mirrored(lifting_surface("stab_l", us, tplan, lambda u: 0.3 + 0.03 * max(0.0, -u - 1.0),
                             lambda u: min(0.38, max(0.05, 0.075 * tplan.chord(u))), m["wing"], under=0.6,
                             tip=tplan.tip))

    # The fin: swept, its top reaching row 0.
    fle = Curve([(0.0, 6.6), (-1.5, 8.2), (-3.0, 9.8), (-4.3, 11.2)])
    fte = Curve([(0.0, 11.9), (-2.0, 12.45), (-4.3, 13.3)])
    us = [0.0, -0.6, -1.2, -1.8, -2.4, -2.95, -3.4, -3.75, -4.0, -4.17, -4.27]
    fin = lifting_surface("fin", us, lambda u: tip_planform(u, fle, fte, -4.3, 0.85, 0.3), lambda u: 0.0,
                          lambda u: 0.3 - 0.035 * (-u), m["body"], under=1.0, camber=0.0)
    to_fin(fin, z=top(0.0, 9.5) - 0.4)


# --- Build ------------------------------------------------------------------------------------------

JETS = {
    # name: (sprite, builder, the sprite's axis of symmetry (model x))
    "jet_cross": (125, build_cross, 0.5),
    "jet_green": (3, build_green, GREEN_AXIS),
    "jet_brown": (49, build_brown, BROWN_AXIS),
    "jet_delta": (11, build_delta, 0.5),
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


def preview(prefix, distance=0.6):
    """tyrkit.preview (the top view framed like the sprite, a three-quarter view), the
    three-quarter view rendered again from closer by."""
    bpy.context.scene.view_settings.view_transform = "Standard"  # the game's colours
    k.preview(prefix)
    cam = bpy.data.objects["3q"]
    cam.location = Vector(cam.location) * distance
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = options["only"].split(",") if "only" in options else list(JETS)
    for name in only:
        k.reset()
        sprite, builder, axis = JETS[name]
        builder()
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                obj.data.transform(Matrix.Translation((axis, 0, 0)))
        materials = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
        print("== %s (F %d): %d triangles, %d materials: %s" % (name, sprite, triangles(), len(materials),
                                                                ", ".join(sorted(materials))))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_F.png"), sprite)
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("   %s: %.1f KB" % (name, os.path.getsize(path) / 1024))
        if "preview" in options:
            preview(options["preview"] + name)


if __name__ == "__main__":
    build()
