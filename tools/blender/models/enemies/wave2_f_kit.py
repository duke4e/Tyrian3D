"""Helpers for the batch F models of wave 2 (wave2_f.py, wave2_f_more.py): parts traced from pixel
art and given volume (wave1_d_shapes), turned parts along any axis, tubes, palette materials,
painting by position, and a registry that builds, checks, exports and previews the models.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera).
Pixel art is rows of letters, row 0 at the top; (ox, oy) is the art's origin in pixels (a 2x2
sprite's centre is (12, 14), a 1x1 sprite's (6, 7)).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "..")
ENEMIES = os.path.join(ROOT, "assets", "models", "enemies")
ITEMS = os.path.join(ROOT, "assets", "models", "items")


# --- Art ---------------------------------------------------------------------------------------

def art(text):
    return [line for line in text.strip("\n").split("\n")]


def relabel(rows, boxes):
    """The art with pixels relabelled: boxes are (from chars, to char, c0, c1, r0, r1), inclusive."""
    grid = [list(r) for r in rows]
    for src, dst, c0, c1, r0, r1 in boxes:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if 0 <= r < len(grid) and 0 <= c < len(grid[r]) and grid[r][c] in src:
                    grid[r][c] = dst
    return ["".join(line) for line in grid]


def keep(rows, chars, into="#"):
    """The art with the pixels of chars as `into`, everything else empty."""
    return ["".join(into if ch in chars else "." for ch in row) for row in rows]


def px(col, ox=12):
    """A pixel column's centre as x."""
    return col + 0.5 - ox


def py(row, oy=14):
    """A pixel row's centre as y."""
    return oy - (row + 0.5)


def outlines(rows, chars, origin=(12, 14), smooth=1, epsilon=0.4, min_area=0.5):
    return sh.outlines(rows, chars, origin, smooth=smooth, epsilon=epsilon, min_area=min_area)


# --- Materials ---------------------------------------------------------------------------------

def pal(name, index, metallic=0.3, roughness=0.4, glow=None, emission=None, alpha=None):
    """A palette material; glow: emission strength (in the palette colour, or `emission`)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=emission or k.level_palette()[index], emission_strength=glow, alpha=alpha)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha)


def paint(obj, mat_of, mats):
    """Gives each face of obj the material mat_of(centre: Vector, normal: Vector) -> index into mats."""
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)
    for poly in obj.data.polygons:
        poly.material_index = mat_of(poly.center, poly.normal)
    return obj


# --- Parts -------------------------------------------------------------------------------------

def inflate(name, polys, mat, profile=None, bottom=0.6, base=0.0, rim=0.15, spacing=0.4, z_fn=None, sigma=1.2,
            smooth_angle=50):
    obj = sh.inflate(name, polys, mat, profile, bottom=bottom, base=base, rim=rim, spacing=spacing, z_fn=z_fn,
                     sigma=sigma)
    return k.smooth(obj, smooth_angle)


def lathe_axis(name, profile, mat, start, direction, segments=24, squash=1.0, smooth_angle=50, up=(0, 0, 1)):
    """A turned part along any axis: profile is (t, radius) pairs in increasing t along `direction`
    from `start`; squash scales the cross-sections towards `up`."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    d = Vector(direction).normalized()
    # Built along +Y with Z up: turn +Y onto d, keeping Z as close to `up` as possible.
    upv = Vector(up)
    side = d.cross(upv)
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    upv = side.cross(d).normalized()
    # Columns: where X, Y and Z go.
    rot = Matrix(((side.x, d.x, upv.x, 0), (side.y, d.y, upv.y, 0), (side.z, d.z, upv.z, 0), (0, 0, 0, 1)))
    obj.data.transform(Matrix.Translation(Vector(start)) @ rot)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def tube(name, points, radius, mat, segments=12, smooth_angle=60, radii=None):
    """A round tube through 3D points, closed with rounded ends; radii: one per point (or radius)."""
    pts = [Vector(p) for p in points]
    rs = radii or [radius] * len(pts)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) + up * math.sin(2 * math.pi * j / segments))
                      * rs[i] for j in range(segments)])
    t0 = (pts[1] - pts[0]).normalized()
    t1 = (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * rs[0] * 0.7, end_point=pts[-1] + t1 * rs[-1] * 0.7)
    return k.smooth(obj, smooth_angle)


def catmull(points, step=0.5):
    """A smooth path through 3D points, sampled about every step."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        count = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def sphere(name, centre, radii, mat, segments=24, rings=12, smooth_angle=60):
    return k.smooth(k.ellipsoid(name, centre, radii, mat, segments, rings), smooth_angle)


def cone(name, base, tip, radius, mat, segments=12, tip_radius=0.0, smooth_angle=40):
    """A cone (or a frustum) from base to tip."""
    base, tip = Vector(base), Vector(tip)
    length = (tip - base).length
    return lathe_axis(name, [(0.0, radius), (length, max(tip_radius, 0.01))], mat, base, tip - base, segments,
                      smooth_angle=smooth_angle)


def blade(name, base, tip, sections, mat, smooth_angle=30, sides=4):
    """A faceted spike from base to tip: sections are (t 0-1 along it, half width, height above the
    axis, depth below it); the cross-section is a diamond (sides=4) or a flattened octagon (8)."""
    base, tip = Vector(base), Vector(tip)
    d = (tip - base).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d).normalized()
    rings = []
    for t, hw, top, bot in sections:
        c = base + (tip - base) * t
        ring = []
        for j in range(sides):
            a = 2 * math.pi * j / sides
            ca, sa = math.cos(a), math.sin(a)
            if sides > 4:
                ca = math.copysign(abs(ca) ** 0.8, ca)
                sa = math.copysign(abs(sa) ** 0.8, sa)
            ring.append(c + side * ca * hw + up * sa * (top if sa >= 0 else bot))
        rings.append(ring)
    obj = k.loft(name, rings, mat, end_point=tip)
    return k.smooth(obj, smooth_angle)


def lumpy(name, centre, radii, mat, seed=1, amount=0.18, segments=28, rings=16):
    """An ellipsoid with a few soft bumps (rocks)."""
    obj = k.ellipsoid(name, centre, radii, mat, segments, rings)
    c = Vector(centre)
    rnd = random.Random(seed)
    bumps = [(Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.6, 1))).normalized(),
              rnd.uniform(-1, 1) * amount, rnd.uniform(0.5, 0.9)) for _ in range(9)]
    for v in obj.data.vertices:
        d = v.co - c
        n = Vector((d.x / radii[0], d.y / radii[1], d.z / radii[2]))
        if n.length < 1e-6:
            continue
        n.normalize()
        f = 1.0 + sum(h * math.exp(-((1 - n.dot(b)) / (1 - math.cos(width))) ** 2) for b, h, width in bumps)
        v.co = c + d * f
    return k.smooth(obj, 70)


def rounded_box(name, centre, size, mat, bevel=0.4, segments=2):
    obj = k.box(name, centre, size, mat)
    k.bevel(obj, bevel, segments)
    return k.smooth(obj, 40)


def transform(objects, matrix):
    for obj in objects:
        obj.data.transform(matrix)
        if matrix.determinant() < 0:
            obj.data.flip_normals()
    return objects


def mirror(objects, axis_x=0.0):
    """Mirrored copies of objects across x = axis_x (the originals stay)."""
    out = []
    flip = Matrix.Translation((2 * axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        sh.apply_modifiers(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_m"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(flip)
        copy.data.flip_normals()
        out.append(copy)
    return out


def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def bake():
    """Applies modifiers and transforms of every mesh."""
    for obj in meshes():
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)


def triangles():
    total = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in meshes():
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        total += sum(len(p.vertices) - 2 for p in mesh.polygons)
    return total


def piece(objects, x0, x1, y0, y1):
    """The part of objects in x0..x1, y0..y1 (closed at the cuts), moved so that the box's centre is
    the origin: one sprite of a larger object."""
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -(x0 + x1) / 2, -(y0 + y1) / 2)
    for obj in kept:
        k.smooth(obj, 50)
    return kept


# --- Registry ----------------------------------------------------------------------------------

MODELS = []  # (name, builder, sheet file, sprite(s), large, size, out dir)


def model(name, sheet, sprite, large=True, out=ENEMIES, size=None):
    """Registers a builder for a model; sheet: the extracted sheet's file name (enemy_X, coins)."""
    def register(fn):
        MODELS.append((name, fn, sheet, sprite, large, size or ((24, 28) if large else (12, 14)), out))
        return fn
    return register


def main():
    """Options: --only a,b  --preview <prefix>  --check <extracted sheets dir>  --stats 1"""
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sheet, sprite, large, size, out in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        bake()
        if "stats" in options:
            print(f"--- {name}: {triangles()} triangles")
        if "check" in options:
            print(f"--- {name} ({sheet} {sprite})")
            k.check_silhouette(os.path.join(options["check"], sheet + ".png"),
                               sprite if isinstance(sprite, list) else [sprite], large)
        k.export(os.path.join(out, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)
