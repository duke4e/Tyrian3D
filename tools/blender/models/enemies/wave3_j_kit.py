"""Helpers for the batch J models of wave 3 (sheet D: wave3_j.py, the machines; wave3_j_rocks.py, the
rocks and the stone face): the sprites' pixels (wave3_j_art.py), palette materials, parts inflated
from pixel regions (wave1_d_shapes), turned parts and tubes, painting faces by the sprite's shades,
the tiled floor some ground sprites stand on, faceted and lumpy rocks, cutting larger objects into
their sprites' pieces, and the build loop.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre. Pixel art rows run top to bottom; pixel (column c, row r) of an
art with origin (ox, oy) covers x = c - ox .. c + 1 - ox, y = oy - r - 1 .. oy - r.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_art as art  # noqa: E402,F401

ROOT = os.path.join(HERE, "..", "..", "..", "..")
ENEMIES = os.path.join(ROOT, "assets", "models", "enemies")


# --- Pixels --------------------------------------------------------------------------------------

def grid(text, width):
    """The art's rows as lists of palette indices (None: transparent), `width` pixels each."""
    out = []
    for line in text.strip("\n").split("\n"):
        line = line.ljust(2 * width, ".")
        out.append([None if line[2 * i:2 * i + 2] == ".." else int(line[2 * i:2 * i + 2], 16) for i in range(width)])
    return out


def regions(g, fn):
    """Char rows of a grid: fn(index, column, row) -> a char ('.' for nothing)."""
    return ["".join("." if v is None else fn(v, c, r) for c, v in enumerate(row)) for r, row in enumerate(g)]


def relabel(rows, boxes):
    """The rows with chars relabelled: boxes are (from chars, to char, c0, c1, r0, r1), inclusive."""
    grid_ = [list(r) for r in rows]
    for src, dst, c0, c1, r0, r1 in boxes:
        for r in range(max(0, r0), min(len(grid_), r1 + 1)):
            for c in range(max(0, c0), min(len(grid_[r]), c1 + 1)):
                if grid_[r][c] in src:
                    grid_[r][c] = dst
    return ["".join(line) for line in grid_]


def px(col, ox=12):
    """A pixel column's centre as x."""
    return col + 0.5 - ox


def py(row, oy=14):
    """A pixel row's centre as y."""
    return oy - (row + 0.5)


def outlines(rows, chars, origin=(12, 14), smooth=2, epsilon=0.4, min_area=0.5):
    return sh.outlines(rows, chars, origin, smooth=smooth, epsilon=epsilon, min_area=min_area)


def sampler(g, origin=(12, 14), value=lambda v: v & 15, blur=1, keep=lambda v: v is not None):
    """A function (x, y) -> the grid's value at a point (value(index) of the pixels `keep` accepts),
    bilinear between pixel centres and blurred `blur` times; elsewhere the nearest kept pixel's."""
    h, w = len(g), len(g[0])
    field = np.full((h, w), np.nan)
    for r in range(h):
        for c in range(w):
            if keep(g[r][c]):
                field[r, c] = value(g[r][c])
    for _ in range(blur):
        out = field.copy()
        for r in range(h):
            for c in range(w):
                if np.isnan(field[r, c]):
                    continue
                vals, wts = [], []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < w and not np.isnan(field[rr, cc]):
                            vals.append(field[rr, cc])
                            wts.append(2.0 if dr == dc == 0 else 1.0 if dr == 0 or dc == 0 else 0.5)
                out[r, c] = np.average(vals, weights=wts)
        field = out
    known = np.array([(r, c) for r in range(h) for c in range(w) if not np.isnan(field[r, c])], dtype=float)
    ox, oy = origin

    def at(x, y):
        c, r = x + ox - 0.5, oy - y - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        total = weight = 0.0
        for rr, cc, wt in ((r0, c0, (1 - (r - r0)) * (1 - (c - c0))), (r0, c0 + 1, (1 - (r - r0)) * (c - c0)),
                           (r0 + 1, c0, (r - r0) * (1 - (c - c0))), (r0 + 1, c0 + 1, (r - r0) * (c - c0))):
            if 0 <= rr < h and 0 <= cc < w and not np.isnan(field[rr, cc]):
                total += field[rr, cc] * wt
                weight += wt
        if weight > 0.05:
            return total / weight
        i = int(np.argmin((known[:, 0] - r) ** 2 + (known[:, 1] - c) ** 2))
        return field[int(known[i, 0]), int(known[i, 1])]
    return at


def pixel_at(g, x, y, origin=(12, 14)):
    """The grid's index under a point (None outside or transparent)."""
    c, r = int(math.floor(x + origin[0])), int(math.floor(origin[1] - y))
    if 0 <= r < len(g) and 0 <= c < len(g[r]):
        return g[r][c]
    return None


# --- Materials -----------------------------------------------------------------------------------

def pal(name, index, metallic=0.3, roughness=0.4, glow=None, emission=None):
    """A palette material; glow: emission strength, in the palette colour (or `emission`, 0-255 sRGB)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=emission or k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def paint_faces(obj, fn):
    """Gives each face the material fn(face centre, normal) returns (None: keep), appending the
    materials to the object."""
    names = [m.name for m in obj.data.materials]
    for poly in obj.data.polygons:
        mat = fn(poly.center, poly.normal)
        if mat is None:
            continue
        if mat.name not in names:
            obj.data.materials.append(mat)
            names.append(mat.name)
        poly.material_index = names.index(mat.name)
    return obj


# --- Parts ---------------------------------------------------------------------------------------

def part(name, rows, chars, mat, profile, origin=(12, 14), bottom=0.0, base=0.0, z_fn=None, smooth=2, epsilon=0.4,
         spacing=0.5, grow=0.0, sigma=1.2, min_area=0.3, rim=0.15, extra=None, smooth_angle=50):
    """A part inflated from the pixels of rows whose char is in chars (wave1_d_shapes.inflate); grow
    moves its outline outwards (tucks it under its neighbours)."""
    polys = sh.outlines(rows, chars, origin, smooth=smooth, epsilon=epsilon, min_area=min_area)
    if grow:
        polys = [sh.inset(p, -grow) for p in polys]
    if extra:
        polys += extra
    obj = sh.inflate(name, polys, mat, profile, bottom=bottom, base=base, rim=rim, spacing=spacing, z_fn=z_fn,
                     sigma=sigma)
    return k.smooth(obj, smooth_angle)


def lathe_axis(name, profile, mat, start, direction, segments=24, squash=1.0, smooth_angle=50, up=(0, 0, 1)):
    """A turned part along any axis: profile is (t, radius) pairs in increasing t along `direction`
    from `start`; squash scales the cross-sections towards `up`."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    d = Vector(direction).normalized()
    upv = Vector(up)
    side = d.cross(upv)
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    upv = side.cross(d).normalized()
    rot = Matrix(((side.x, d.x, upv.x, 0), (side.y, d.y, upv.y, 0), (side.z, d.z, upv.z, 0), (0, 0, 0, 1)))
    obj.data.transform(Matrix.Translation(Vector(start)) @ rot)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def hoop(name, centre, section, mat, segments=40, smooth_angle=50, scale_y=1.0):
    """A ring round a vertical axis at centre (x, y, z): section is its cross-section, a closed loop
    of (radius, z offset) points; scale_y stretches it along y (oval rings)."""
    cx, cy, cz = centre
    verts, faces = [], []
    n = len(section)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        for r, dz in section:
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a) * scale_y, cz + dz))
    for i in range(segments):
        j = (i + 1) % segments
        for s in range(n):
            t = (s + 1) % n
            faces.append((i * n + s, j * n + s, j * n + t, i * n + t))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def column(name, profile, mat, x, y, segments=28, smooth_angle=50, squash=1.0):
    """A turned part standing upright at (x, y): profile is (z, radius) pairs in increasing z."""
    return lathe_axis(name, profile, mat, (x, y, 0.0), (0, 0, 1), segments, squash, smooth_angle, up=(0, 1, 0))


def tube(name, points, radius, mat, segments=12, smooth_angle=60, squash=1.0):
    """A round tube through 3D points with rounded ends; radius a number or one per point."""
    pts = [Vector(p) for p in points]
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) +
                           up * math.sin(2 * math.pi * j / segments) * squash) * radii[i] for j in range(segments)])
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radii[0] * 0.7, end_point=pts[-1] + t1 * radii[-1] * 0.7)
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


def rounded_box(name, centre, size, mat, bevel=0.4, segments=2, smooth_angle=40):
    obj = k.box(name, centre, size, mat)
    k.bevel(obj, bevel, segments)
    return k.smooth(obj, smooth_angle)


def block(name, centre, half_w, half_d, height, mat, taper=0.0, rounding=1.0, power=4.0, segments=48, z0=0.0,
          dome=0.0, smooth_angle=45):
    """A block standing on z0 at centre (x, y): rounded corners (a superellipse of `power` in plan),
    its sides leaning in by `taper` pixels from bottom to top, its top edge rounded over `rounding`
    and its top bulging by `dome`."""
    cx, cy = centre

    def rect(z, hw, hd):
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s = math.cos(a), math.sin(a)
            pts.append(Vector((cx + math.copysign(abs(c) ** (2 / power), c) * hw,
                               cy + math.copysign(abs(s) ** (2 / power), s) * hd, z)))
        return pts
    rings = [rect(z0, half_w, half_d)]
    side_top = height - rounding
    rings.append(rect(z0 + side_top * 0.5, half_w - taper * 0.5 * side_top / height, half_d - taper * 0.5 * side_top / height))
    for i in range(0, 6):
        a = math.radians(90 * i / 5)
        shrink = taper * (side_top / height) + rounding * (1 - math.cos(a))
        rings.append(rect(z0 + side_top + rounding * math.sin(a) + dome * 0.2 * (i / 5) ** 2,
                          half_w - shrink, half_d - shrink))
    inner = (half_w - taper - rounding, half_d - taper - rounding)
    for j in (0.66, 0.33):
        rings.append(rect(z0 + height + dome * (1 - j * j), inner[0] * j, inner[1] * j))
    obj = k.loft(name, rings, mat, start_point=(cx, cy, z0), end_point=(cx, cy, z0 + height + dome))
    return k.smooth(obj, smooth_angle)


def lumpy(name, centre, radii, mat, seed=1, amount=0.18, segments=28, rings=16, smooth_angle=70):
    """An ellipsoid with a few soft bumps (rocks), as wave2_f_kit.lumpy."""
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
    return k.smooth(obj, smooth_angle)


# --- Mesh helpers --------------------------------------------------------------------------------

def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def bake():
    """Applies modifiers and transforms of every mesh."""
    for obj in meshes():
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)


def transform(objects, matrix):
    for obj in objects:
        obj.data.transform(matrix)
        if matrix.determinant() < 0:
            obj.data.flip_normals()
    return objects


def triangles(objects=None):
    total = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects or meshes():
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        total += sum(len(p.vertices) - 2 for p in mesh.polygons)
    return total


def simplify_bottom(obj, angle=0.999):
    """Dissolves the flat, downward faces at the part's lowest level into few faces."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    zmin = min(v.co.z for v in bm.verts)
    faces = [f for f in bm.faces if f.normal.z < -angle and all(abs(v.co.z - zmin) < 1e-3 for v in f.verts)]
    if faces:
        try:
            bmesh.ops.dissolve_faces(bm, faces=faces, use_verts=True)
        except Exception:  # noqa: BLE001 (leave it as it is)
            pass
        ngons = [f for f in bm.faces if len(f.verts) > 3]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def decimate(obj, target):
    """Collapses the part's mesh to about `target` triangles (if it has more)."""
    sh.apply_modifiers(obj)
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tris > target:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.ratio = target / tris
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return obj


def piece(objects, x0, x1, y0, y1):
    """The part of objects in x0..x1, y0..y1 (closed at the cuts), moved so that the box's centre is
    the origin: one sprite of a larger object."""
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -(x0 + x1) / 2, -(y0 + y1) / 2)
    for obj in kept:
        k.smooth(obj, 50)
    return kept


# --- The tiled floor -----------------------------------------------------------------------------

def floor(name, g, bands, is_floor, origin=(12, 14), top=0.9, relief=0.45, edge=0.7, under=None):
    """The tiled floor a ground sprite stands on, as a low slab over the whole sprite: a heightfield
    on the pixel grid whose stones stand higher than the mortar (the floor pixels' shades), each
    pixel painted in the band of its shade (bands: [(lowest shade, material)], ascending); its edge
    falls away over `edge` pixels. Pixels that are not floor (is_floor(index, column, row) false:
    the machine on it) lie flat at `top` in the darkest band."""
    h, w = len(g), len(g[0])
    ox, oy = origin
    shade = np.zeros((h, w))
    known = np.zeros((h, w), dtype=bool)
    for r in range(h):
        for c in range(w):
            v = g[r][c]
            if v is not None and is_floor(v, c, r):
                shade[r, c] = v & 15
                known[r, c] = True
    mean = shade[known].mean() if known.any() else 4.0
    shade[~known] = mean if under is None else under
    # Heights at the pixel corners: the mean of the pixels round them.
    corner = np.zeros((h + 1, w + 1))
    for r in range(h + 1):
        for c in range(w + 1):
            vals = [shade[rr, cc] for rr in (r - 1, r) for cc in (c - 1, c) if 0 <= rr < h and 0 <= cc < w]
            corner[r, c] = sum(vals) / len(vals)
    lo, hi = np.percentile(shade[known], 10) if known.any() else 2, np.percentile(shade[known], 90) if known.any() else 7
    span = max(hi - lo, 1.0)

    def hidden(r, c):
        """A corner inside the machine (all its pixels covered): flat, so that it merges."""
        return all(not known[rr, cc] for rr in (r - 1, r) for cc in (c - 1, c) if 0 <= rr < h and 0 <= cc < w)

    def height(r, c):
        border = min(c, w - c, r, h - r)
        if hidden(r, c) and border > 0:
            return top
        fall = min(1.0, border / edge)
        z = top + relief * (min(max((corner[r, c] - lo) / span, 0.0), 1.0) - 0.5)
        return max(0.05, z * (0.35 + 0.65 * math.sqrt(fall)))

    bm = bmesh.new()
    verts = [[bm.verts.new((c - ox, oy - r, height(r, c))) for c in range(w + 1)] for r in range(h + 1)]
    mats = [m for _, m in bands]
    faces = []
    for r in range(h):
        for c in range(w):
            a, b, cc, d = verts[r][c], verts[r][c + 1], verts[r + 1][c + 1], verts[r + 1][c]
            # Split along the diagonal that keeps the surface smoothest.
            if abs(a.co.z - cc.co.z) <= abs(b.co.z - d.co.z):
                tris = [(a, d, cc), (a, cc, b)]
            else:
                tris = [(a, d, b), (b, d, cc)]
            s = shade[r, c] if known[r, c] else bands[0][0]
            index = 0
            for i, (lowest, _) in enumerate(bands):
                if s >= lowest:
                    index = i
            for t in tris:
                f = bm.faces.new(t)
                f.material_index = index
                faces.append(f)
    # The skirt down to z = 0 and the bottom.
    ring = [verts[0][c] for c in range(w + 1)] + [verts[r][w] for r in range(1, h + 1)] + \
           [verts[h][c] for c in range(w - 1, -1, -1)] + [verts[r][0] for r in range(h - 1, 0, -1)]
    low = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in ring]
    n = len(ring)
    for i in range(n):
        f = bm.faces.new((ring[i], ring[(i + 1) % n], low[(i + 1) % n], low[i]))
        f.material_index = 0
    bottom = bm.faces.new(list(reversed(low)))
    bottom.material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # The flat stretches (under the machine, the bottom) become few faces.
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    return k.smooth(obj, 35)


def floor_bands(prefix):
    """The floor tiles' shades (the grey ramp) in four bands: mortar, dark stone, stone, light stone."""
    return [(0, pal(f"{prefix}_floor1", 0x02, metallic=0.05, roughness=0.85)),
            (3.5, pal(f"{prefix}_floor4", 0x04, metallic=0.05, roughness=0.8)),
            (5.5, pal(f"{prefix}_floor6", 0x06, metallic=0.05, roughness=0.8)),
            (7.5, pal(f"{prefix}_floor8", 0x08, metallic=0.05, roughness=0.75))]


# --- Rocks ---------------------------------------------------------------------------------------

def _ray_polygon(poly, origin, direction):
    """The nearest distance along a ray from inside a polygon to its outline."""
    best = 1e9
    ox, oy = origin
    dx, dy = direction
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - ox) * ey - (ay - oy) * ex) / den
        u = ((ax - ox) * dy - (ay - oy) * dx) / den
        if t > 1e-6 and -1e-9 <= u <= 1 + 1e-9:
            best = min(best, t)
    return best if best < 1e8 else 0.0


def faceted_rock(name, poly, height, shades, seed=5, depth=None, shade_of=None, lumps=0.12, dissolve=11.0,
                 subdivisions=4, centre=None, flat_bottom=False):
    """A rock over an outline (the polygon, model coordinates), as the asteroids of batch H
    (asteroid_lumpy): a lumpy blob through the outline, `height` above its middle and `depth` below
    it (default: as high), its surface broken into flat facets in the materials `shades` (dark to
    light): shade_of(centre) -> 0..len-1 (default: patches of lighter and darker facets)."""
    cx = sum(p[0] for p in poly) / len(poly) if centre is None else centre[0]
    cy = sum(p[1] for p in poly) / len(poly) if centre is None else centre[1]
    depth = height if depth is None else depth
    rng = random.Random(seed)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(2.5, 5.5),
              rng.uniform(0, 6.3)) for _ in range(10)]
    middle = Vector((cx, cy, 0.0))

    def blob(n):
        theta = math.atan2(n.y, n.x)
        r = _ray_polygon(poly, (cx, cy), (math.cos(theta), math.sin(theta))) - 0.1
        bump = 1 + lumps * sum(math.sin(w.dot(n) + phase) for w, phase in waves) / len(waves) ** 0.5
        bump = 1 + (bump - 1) * min(1.0, abs(n.z) * 2.0)  # the outline stays the sprite's
        hz = height if n.z >= 0 else depth
        return middle + Vector((n.x * r * bump, n.y * r * bump, n.z * hz * bump))

    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        jitter = 1 + rng.uniform(-0.04, 0.04) * min(1.0, abs(n.z) * 2.0)
        v.co = middle + (blob(n) - middle) * jitter
        if flat_bottom and v.co.z < 0:
            v.co.z = 0.0
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(dissolve), verts=bm.verts[:], edges=bm.edges[:])
    patches = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(0.35, 0.7),
                rng.uniform(0, 6.3)) for _ in range(6)]
    for f in bm.faces:
        c = f.calc_center_median()
        if shade_of is not None:
            s = shade_of(c, f.normal)
        else:
            field = sum(math.sin(w.dot(c) + phase) for w, phase in patches) / len(patches) ** 0.5
            s = (len(shades) - 1) * 0.5 + 0.33 * (len(shades) - 1) * field
        s += rng.choice((-1, 0, 0, 1))
        f.material_index = max(0, min(len(shades) - 1, int(round(s))))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in shades:
        obj.data.materials.append(m)
    return obj


# --- Building ------------------------------------------------------------------------------------

MODELS = []  # (name, builder, [(sheet file, sprite, large)], size, out dir)
WHOLES = {}  # name: (builder, size in pixels): objects the game draws in pieces, for --whole previews


def model(name, sprites, size=(24, 28), out=ENEMIES):
    """Registers a builder; sprites: [(sheet file, sprite, large)] for the silhouette check."""
    def register(fn):
        MODELS.append((name, fn, sprites, size, out))
        return fn
    return register


def whole(name, size):
    def register(fn):
        WHOLES[name] = (fn, size)
        return fn
    return register


def run():
    """Options: --only a,b  --preview <prefix>  --check <extracted sheets dir>  --stats 1
    --whole <name> --preview <prefix>: renders a whole object (no export)."""
    options = k.args()
    if "whole" in options:
        fn, size = WHOLES[options["whole"]]
        k.reset()
        fn()
        bake()
        print(f"--- {options['whole']}: {triangles()} triangles")
        bpy.context.scene.view_settings.view_transform = "Standard"
        k.preview(options.get("preview", "/tmp/whole_") + options["whole"], size, scale=max(4, 384 // max(size)))
        scene = bpy.context.scene
        cam = bpy.data.objects["3q"]
        cam.location = Vector((38, -48, 42)) * (0.5 * max(size) / 24.0)
        scene.render.filepath = options.get("preview", "/tmp/whole_") + options["whole"] + "_3q.png"
        bpy.ops.render.render(write_still=True)
        return
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sprites, size, out in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        bake()
        if "stats" in options:
            print(f"--- {name}: {triangles()} triangles, {len(meshes())} parts")
        if "check" in options:
            for sheet, sprite, large in sprites:
                print(f"--- {name} ({sheet} {sprite})")
                k.check_silhouette(os.path.join(options["check"], sheet + ".png"), [sprite], large)
        k.export(os.path.join(out, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)
