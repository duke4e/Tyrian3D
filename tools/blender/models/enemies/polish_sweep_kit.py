"""Helpers for the round-38 organic models built from smooth solids (polish_gryphon.py, polish_violet_shell.py): solids
lofted along paths through superellipse sections (sweep), ellipsoids from explicit rings, feathers, Catmull-Rom curves
resampled by length, tables of sections interpolated smoothly, mirrored copies, the shear along the game camera's line
of sight. Not a model script itself. Every mesh is lofted from explicit rings (no bmesh primitives, no booleans, no
random numbers: jitter() is a fixed hash), so the output is the same every run.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera.
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

TAN_T = math.tan(math.radians(20.0))   # the game's camera: 20 degrees off straight down, from the bottom of the screen


# --- Curves -----------------------------------------------------------------------------------------------------------

def catmull(points, per=8):
    """A Catmull-Rom curve through points (tuples of any length), per samples a span."""
    pts = [tuple(p) for p in points]
    n = len(pts)
    out = []
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[q] + (-p0[q] + p2[q]) * t +
                                    (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * t2 +
                                    (-p0[q] + 3 * p1[q] - 3 * p2[q] + p3[q]) * t3) for q in range(len(p1))))
    out.append(pts[-1])
    return out


def resample(points, count):
    """count points evenly spaced along a polyline of tuples (by the length of their first three values)."""
    lengths = [0.0]
    for a, b in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.dist(a[:3], b[:3]))
    total = lengths[-1]
    out = []
    j = 0
    for i in range(count):
        target = total * i / (count - 1)
        while j < len(points) - 2 and lengths[j + 1] < target:
            j += 1
        span = lengths[j + 1] - lengths[j]
        f = 0.0 if span <= 0 else (target - lengths[j]) / span
        f = min(1.0, max(0.0, f))
        out.append(tuple(a + (b - a) * f for a, b in zip(points[j], points[j + 1])))
    return out


# --- Solids -----------------------------------------------------------------------------------------------------------

def section(j, n, hw, top, bottom, power=2.0, ridge=0.0):
    """Point j of n round a section: half-width hw, its upper half top high, its lower half bottom deep (a
    superellipse of power), a crest of ridge along its top's middle."""
    a = 2 * math.pi * j / n
    c, s = math.cos(a), math.sin(a)
    x = math.copysign(abs(c) ** (2 / power), c) * hw
    if s >= 0:
        z = abs(s) ** (2 / power) * top + ridge * max(0.0, 1 - (3 * c) ** 2) ** 2
    else:
        z = -abs(s) ** (2 / power) * bottom
    return x, z


def set_smooth(obj):
    """Every face shaded smooth (no sharp edges: the same shading every run)."""
    mesh = obj.data
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.update()
    return obj


def sweep(name, path, sections, mat, segments=12, up=(0.0, 0.0, 1.0), power=2.0, ridge=0.0, bank=None,
          start=None, end=None):
    """A solid along a path of 3D points: at each point a section (half-width, top, bottom) lying across the path,
    its "up" as near the given up as the path allows; bank (a horizontal direction and a slope) tilts every section
    so that its side towards that direction rises. The ends close in fans to start and end (default: just past the
    end sections along the path)."""
    pts = [Vector(p) for p in path]
    n = len(pts)
    upv = Vector(up).normalized()
    top_max = max(max(sec[1] for sec in sections), 1e-6)
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        a = upv.cross(t)
        if a.length < 1e-6:
            a = Vector((1.0, 0.0, 0.0)).cross(t)
        a.normalize()
        b = t.cross(a).normalized()
        hw, top, bottom = sections[i]
        ring = []
        for j in range(segments):
            x, z = section(j, segments, hw, top, bottom, power, ridge * top / top_max)
            q = p + a * x + b * z
            if bank is not None:
                direction, slope = bank
                q.z += slope * (a * x).dot(direction)
            ring.append(q)
        rings.append(ring)
    t0 = (pts[1] - pts[0]).normalized()
    t1 = (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=start if start is not None else pts[0] - t0 * 0.3,
                 end_point=end if end is not None else pts[-1] + t1 * 0.3)
    return set_smooth(obj)


def ellipsoid(name, centre, radii, mat, count=10, around=20, axes=None):
    """An ellipsoid lofted from explicit rings (the same every run); axes: its own x, y, z directions."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    ax, ay, az = axes or (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
    c = Vector(centre)
    rings = []
    for i in range(1, count):
        p = math.pi * i / count
        r, y = math.sin(p), -math.cos(p)
        rings.append([c + ax * (rx * r * math.cos(2 * math.pi * j / around)) + ay * (ry * y) +
                      az * (rz * r * math.sin(2 * math.pi * j / around)) for j in range(around)])
    obj = k.loft(name, rings, mat, start_point=c - ay * ry, end_point=c + ay * ry)
    return set_smooth(obj)


def jitter(*keys):
    """A number in [0, 1) fixed by the keys (no random numbers: the same every run)."""
    h = 0.0
    for i, key in enumerate(keys):
        h += (i + 1) * 12.9898 * key + 78.233 * (i + 0.5)
    return (math.sin(h) * 43758.5453) % 1.0


# A feather's half-width and thickness along it (from its quill to its tip): fractions of the given ones.
FEATHER_W = [(0.0, 0.3), (0.1, 0.6), (0.28, 0.88), (0.48, 1.0), (0.66, 0.95), (0.8, 0.78), (0.91, 0.5),
             (0.98, 0.18)]
FEATHER_H = [1.0, 1.0, 0.95, 0.9, 0.82, 0.72, 0.58, 0.4]


def feather(name, root, tip, hw, hh, mat, bank=(None, 0.0), arch=0.2, bend=(None, 0.0), segments=8):
    """One feather from root to tip (3D points): a long vane, narrow at its quill, widest past its middle, pointed
    at its tip; arched a little along its length, bent sideways (bend: a direction and how far its tip goes), a
    rachis along its top, banked (bank: a direction and slope: that side rises)."""
    root, tip = Vector(root), Vector(tip)
    path, secs = [], []
    for (f, w), h in zip(FEATHER_W, FEATHER_H):
        p = root.lerp(tip, f)
        p.z += arch * math.sin(math.pi * f)
        if bend[0] is not None:
            p += bend[0] * (bend[1] * f * f)
        path.append(p)
        secs.append((hw * w, hh * h, hh * h * 0.4))
    end = path[-1] + (path[-1] - path[-2]).normalized() * 0.35
    return sweep(name, path, secs, mat, segments=segments, power=2.0, ridge=0.12,
                 bank=bank if bank[0] is not None else None, start=root, end=end)


def loft_sections(name, table, place, mat, seg=26, power=2.2, bottom=1.4, start=None, end=None, steps=24):
    """A body lofted down the screen through a table of sections (row, half-width, height of its top; interp between
    them): each a superellipse of power, its upper half rising from height bottom to the top, its lower half reaching
    from bottom down to 0; place(x, row, z) puts a section's point where it belongs."""
    vs = [table[0][0] + (table[-1][0] - table[0][0]) * i / steps for i in range(steps + 1)]
    rings = []
    for v in vs:
        hw, top = interp(table, v)
        ring = []
        for j in range(seg):
            x, z = section(j, seg, hw, top - bottom, bottom, power=power)
            ring.append(place(x, v, z + bottom))
        rings.append(ring)
    obj = k.loft(name, rings, mat, start_point=start, end_point=end)
    return set_smooth(obj)


def interp(table, v):
    """A table of (row, a, b) rows interpolated smoothly (smoothstep between its rows) at row v: (a, b)."""
    vs = [row[0] for row in table]
    v = min(max(v, vs[0]), vs[-1])
    for (v0, w0, h0), (v1, w1, h1) in zip(table, table[1:]):
        if v0 <= v <= v1:
            f = (v - v0) / (v1 - v0)
            f = f * f * (3 - 2 * f)
            return w0 + (w1 - w0) * f, h0 + (h1 - h0) * f
    return table[-1][1], table[-1][2]


def mirrored(objs, axis_x=0.0):
    """Mirrored copies of the objects (about x = axis_x), named <name>_r."""
    out = []
    for o in objs:
        c = k.mirror_x(o, o.name + "_r")
        if axis_x:
            c.data.transform(Matrix.Translation((2 * axis_x, 0.0, 0.0)))
        out.append(c)
    return out


def flatten_below(objects, z0=0.0):
    """Nothing reaches below z0 (the ground or the layer): the round parts' undersides are flattened there (never
    seen from the game's camera)."""
    for obj in objects:
        for v in obj.data.vertices:
            if v.co.z < z0:
                v.co.z = z0
        obj.data.update()


def shear_to_camera(objects):
    """Every point moved along the game camera's line of sight to its height (y - z tan 20), so that the camera sees
    each where the sprites draw it; the normals follow (the shear's inverse transpose)."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN_T
        mesh.normals_split_custom_set([tuple(Vector((n.x, n.y, n.z + TAN_T * n.y)).normalized()) for n in normals])
        mesh.update()
