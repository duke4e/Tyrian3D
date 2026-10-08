"""Helpers for the batch H models of wave 2 (wave2_h.py): palette materials, solids over a sprite's
outline with free top and bottom heights, bands of colour cut along smooth borders, tubes, cutting
and mirroring, a silhouette check for 1x1 and 2x2 sprites and the build loop.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up; the origin is the
sprite's centre. Pixel art is given as rows of characters (row 0 at the top), '.' empty.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402

ENEMIES = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies")


# --- Materials -----------------------------------------------------------------------------------

def pal(name, index, metallic=0.3, roughness=0.45, glow=None, color=None):
    """A palette material; glow: emission strength, in the palette colour (or color, 0-255 sRGB)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=color or k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


# --- Sprite coordinates --------------------------------------------------------------------------

class Grid:
    """A sprite's pixel grid: w x h pixels (24 x 28 for 2x2, 12 x 14 for 1x1), centred."""

    def __init__(self, w=24, h=28):
        self.w, self.h = w, h

    def x(self, col):
        """The x of a pixel column's left edge (col may be fractional: col + 0.5 is its centre)."""
        return col - self.w / 2

    def y(self, row):
        """The y of a pixel row's top edge (row + 0.5 is its centre)."""
        return self.h / 2 - row

    def art(self, text):
        rows = [line.ljust(self.w, ".") for line in text.strip("\n").split("\n")]
        return rows + ["." * self.w] * (self.h - len(rows))

    def polys(self, rows, chars, smooth=1, epsilon=0.2, min_area=0.5):
        """Outlines of the pixels whose character is in chars (holes included), model coordinates."""
        return sh.outlines(rows, chars, (self.w / 2, self.h / 2), smooth, epsilon, min_area)


G2 = Grid(24, 28)
G1 = Grid(12, 14)


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def round_edge(d, r):
    """0 at the outline rising as a quarter circle to 1 at distance r inside."""
    t = min(1.0, max(0.0, d / r))
    return math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))


# --- Solids --------------------------------------------------------------------------------------

def solid(name, polys, top, bottom=0.0, mats=None, mat_fn=None, side_mat=0, spacing=0.5, smooth_angle=50,
          cut=None, band=None, coarse=2):
    """A closed part filling the polygons (even-odd: holes stay open): its top at top(x, y, d), d the
    distance to the outline, its underside at bottom (a height, or bottom(x, y, d)), walls between
    them along the outline. mats: a material or a list; mat_fn(x, y, z, d) picks a top face's
    material index (side_mat: the walls' and the underside's). cut(a, b): outline edges left out
    of d (where the part goes on into another sprite). band: inside points farther than this from
    the outline are kept only every `coarse` grid steps (flat middles need fewer triangles)."""
    mats = mats if isinstance(mats, (list, tuple)) else [mats]
    a, b = sh._segments(polys)
    if cut is not None:
        keep = np.array([not cut(tuple(p), tuple(q)) for p, q in zip(a, b)])
        da, db = (a[keep], b[keep]) if keep.any() else (a, b)
    else:
        da, db = a, b
    xs = np.concatenate([a[:, 0], b[:, 0]])
    ys = np.concatenate([a[:, 1], b[:, 1]])
    boundary = [p for poly in polys for p in sh._resample(poly, spacing)]
    gx = np.arange(math.floor(xs.min() / spacing) * spacing, xs.max() + spacing, spacing)
    gy = np.arange(math.floor(ys.min() / spacing) * spacing, ys.max() + spacing, spacing)
    grid = np.array([(x, y) for y in gy for x in gx], dtype=float)
    index = np.array([(i, j) for j in range(len(gy)) for i in range(len(gx))])
    keep = sh._inside(grid, a, b)
    grid, index = grid[keep], index[keep]
    edge = sh._distance(grid, a, b)
    keep = edge > 0.35 * spacing
    if band is not None:
        keep &= (edge <= band) | ((index[:, 0] % coarse == 0) & (index[:, 1] % coarse == 0))
    grid = grid[keep]
    points2d = [Vector(p) for p in boundary] + [Vector(tuple(p)) for p in grid]
    constraint, start = [], 0
    for poly in polys:
        count = len(sh._resample(poly, spacing))
        constraint += [(start + i, start + (i + 1) % count) for i in range(count)]
        start += count
    n_boundary = len(boundary)
    verts, _e, faces, orig, *_ = geometry.delaunay_2d_cdt(points2d, constraint, [], 0, 1e-6)
    pts = np.array([(v.x, v.y) for v in verts], dtype=float)
    tris = [f for f in faces if len(f) == 3]
    centroids = np.array([pts[list(f)].mean(0) for f in tris])
    inside = sh._inside(centroids, a, b)
    tris = [f for f, kf in zip(tris, inside) if kf]
    d = sh._distance(pts, da, db)
    d[sh._distance(pts, a, b) < 1e-4] = 0.0
    z_top = [top(x, y, dd) for (x, y), dd in zip(pts, d)]
    flat = not callable(bottom)

    bm = bmesh.new()
    tv = [bm.verts.new((x, y, z)) for (x, y), z in zip(pts, z_top)]
    if flat:
        # A flat underside: the outline alone, triangulated; bv maps the top's outline vertices.
        bverts, _e2, bfaces, borig, *_ = geometry.delaunay_2d_cdt([Vector(p) for p in boundary], constraint, [],
                                                                    0, 1e-6)
        bpts = np.array([(v.x, v.y) for v in bverts], dtype=float)
        bnew = [bm.verts.new((x, y, bottom)) for x, y in bpts]
        btris = [f for f in bfaces if len(f) == 3]
        bcent = np.array([bpts[list(f)].mean(0) for f in btris])
        btris = [f for f, kf in zip(btris, sh._inside(bcent, a, b)) if kf]
        for f in btris:
            try:
                fb = bm.faces.new([bnew[i] for i in reversed(f)])
                fb.material_index = side_mat
            except ValueError:
                pass
        input_to_bottom = {}
        for i, o in enumerate(borig):
            for j in o:
                input_to_bottom[j] = bnew[i]
        bv = {}
        for i, o in enumerate(orig):
            for j in o:
                if j < n_boundary and j in input_to_bottom:
                    bv[i] = input_to_bottom[j]
    else:
        bv = [bm.verts.new((x, y, bottom(x, y, dd))) for (x, y), dd in zip(pts, d)]
    edge_use = {}
    for f in tris:
        try:
            ft = bm.faces.new([tv[i] for i in f])
            if not flat:
                fb = bm.faces.new([bv[i] for i in reversed(f)])
                fb.material_index = side_mat
        except ValueError:
            continue
        if mat_fn is not None:
            cx = sum(pts[i][0] for i in f) / 3
            cy = sum(pts[i][1] for i in f) / 3
            cz = sum(z_top[i] for i in f) / 3
            ft.material_index = mat_fn(cx, cy, cz, sum(d[i] for i in f) / 3)
        for i in range(3):
            e = (f[i], f[(i + 1) % 3])
            key = (min(e), max(e))
            edge_use.setdefault(key, []).append(e)
    for key, uses in edge_use.items():
        if len(uses) == 1:
            i, j = uses[0]
            try:
                wall = bm.faces.new([tv[j], tv[i], bv[i], bv[j]])
                wall.material_index = side_mat
            except (ValueError, KeyError):
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    return k.smooth(obj, smooth_angle)


def distance_to(polys):
    """A function (x, y) -> the distance to the polygons' outlines."""
    a, b = sh._segments(polys)

    def d(x, y):
        return float(sh._distance(np.array([(x, y)], dtype=float), a, b)[0])
    return d


def section_loft(name, sections, mat, segments=24, power=2.0, start=None, end=None, angle=55):
    """A hull along x through cross-sections [(x, y centre, z centre, half width in y, half height)],
    superellipses of the given power; start/end close the ends (points, or None for flat caps)."""
    rings = []
    for x, yc, zc, hw, hz in sections:
        ring = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s_ = math.cos(a), math.sin(a)
            ring.append(Vector((x, yc + math.copysign(abs(c) ** (2 / power), c) * max(hw, 0.02),
                                zc + math.copysign(abs(s_) ** (2 / power), s_) * max(hz, 0.02))))
        rings.append(ring)
    obj = k.loft(name, rings, mat, start_point=start, end_point=end)
    return k.smooth(obj, angle)


def paint(obj, mats, fn):
    """Gives each face the material fn(centre, normal) returns (an index into mats, which are
    appended to the object if missing), None keeping its own."""
    for m in mats:
        if m.name not in [mm.name for mm in obj.data.materials if mm]:
            obj.data.materials.append(m)
    names = [mm.name for mm in obj.data.materials]
    for poly in obj.data.polygons:
        i = fn(poly.center, poly.normal)
        if i is not None:
            poly.material_index = names.index(mats[i].name)
    return obj


def band_split(obj, values, bands, face_band=None, smooth_angle=60):
    """Colours a mesh in bands of a value per vertex, cutting its faces along the bands' borders so
    the borders are smooth lines. bands: [(lowest value, material)], ascending. face_band(polygon)
    may force a band for a whole face (or None); vertices whose value is None go to the first band.
    (As in wave1_b.py.)"""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = [bands[0][0] - 1 if v is None else v for v in values]
    thresholds = [b[0] for b in bands]
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina = (vals[a] >= t) == above
            inb = (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    faces, materials = [], []
    for poly in mesh.polygons:
        indices = list(poly.vertices)
        forced = face_band(poly) if face_band else None
        if forced is not None:
            faces.append(indices)
            materials.append(forced)
            continue
        low, high = min(vals[i] for i in indices), max(vals[i] for i in indices)
        for b in range(len(bands)):
            lo = thresholds[b] if b > 0 else -1e9
            hi = thresholds[b + 1] if b + 1 < len(bands) else 1e9
            if high < lo or low >= hi:
                continue
            piece = indices
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(bands) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                materials.append(b)
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for _, mat in bands:
        new.materials.append(mat)
    for poly, m in zip(new.polygons, materials):
        poly.material_index = m
    new.validate()
    obj.data = new
    bm = bmesh.new()
    bm.from_mesh(new)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.to_mesh(new)
    bm.free()
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


# --- Round parts ---------------------------------------------------------------------------------

def ellipsoid(name, centre, radii, mat, segments=24, rings=12, angle=60):
    return k.smooth(k.ellipsoid(name, centre, radii, mat, segments, rings), angle)


def frame_rings(path, radii, segments=12, squash=1.0, up=(0, 0, 1)):
    """Rings perpendicular to a path of points: circles of the given radii (a number or one per
    point), squashed towards the up direction."""
    path = [Vector(p) for p in path]
    radii = radii if isinstance(radii, (list, tuple)) else [radii] * len(path)
    up = Vector(up)
    out = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        u = up if abs(t.dot(up)) < 0.95 else Vector((1, 0, 0))
        side = t.cross(u).normalized()
        upv = side.cross(t).normalized()
        r = radii[i]
        rr = r if isinstance(r, (tuple, list)) else (r, r * squash)
        out.append([p + side * math.cos(2 * math.pi * j / segments) * rr[0] +
                    upv * math.sin(2 * math.pi * j / segments) * rr[1] for j in range(segments)])
    return out


def tube(name, path, radii, mat, segments=12, squash=1.0, angle=60, up=(0, 0, 1)):
    """A tube along a path, its ends closed (rounded when the end radii are small)."""
    obj = k.loft(name, frame_rings(path, radii, segments, squash, up), mat)
    return k.smooth(obj, angle)


def catmull(points, step=0.5):
    """A smooth path through points (3D), sampled about every step."""
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


def lathe(name, profile, mat, axis="y", at=(0.0, 0.0), segments=24, squash=1.0, angle=50):
    """A round part about an axis through `at` ((x, z) for axis y, (y, z) for axis x, (x, y) for
    axis z): profile [(t, radius)] in increasing t along the axis."""
    rings = []
    for t, r in profile:
        r = max(r, 0.02)
        ring = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            u, v = math.cos(a) * r, math.sin(a) * r * squash
            if axis == "y":
                ring.append(Vector((at[0] + u, t, at[1] + v)))
            elif axis == "x":
                ring.append(Vector((t, at[0] - u, at[1] + v)))
            else:
                ring.append(Vector((at[0] + u, at[1] + v, t)))
        rings.append(ring)
    t0, t1 = profile[0][0], profile[-1][0]
    if axis == "y":
        s, e = (at[0], t0, at[1]), (at[0], t1, at[1])
    elif axis == "x":
        s, e = (t0, at[0], at[1]), (t1, at[0], at[1])
    else:
        s, e = (at[0], at[1], t0), (at[0], at[1], t1)
    obj = k.loft(name, rings, mat, start_point=s, end_point=e)
    return k.smooth(obj, angle)


# --- Whole scene ---------------------------------------------------------------------------------

def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def bake():
    """Applies modifiers and transforms of every mesh."""
    for obj in meshes():
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)


def transform_all(matrix):
    bake()
    flip = matrix.determinant() < 0
    for obj in meshes():
        obj.data.transform(matrix)
        if flip:
            obj.data.flip_normals()


def mirror_all():
    """Mirrors the whole model left for right (the twin of a part drawn mirrored)."""
    transform_all(Matrix.Scale(-1, 4, (1, 0, 0)))


def bounds():
    bpy.context.view_layer.update()
    corners = [o.matrix_world @ Vector(c) for o in meshes() for c in o.bound_box]
    low = Vector([min(c[i] for c in corners) for i in range(3)])
    high = Vector([max(c[i] for c in corners) for i in range(3)])
    return low, high


def triangles():
    total = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in meshes():
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        total += sum(len(p.vertices) - 2 for p in mesh.polygons)
    return total


# --- Silhouette check ----------------------------------------------------------------------------

def check(sheet, index, large=True, supersample=4):
    """Compares the model's top view with the sprite's silhouette (1x1 or 2x2): prints the overlap
    (intersection over union) and a map ('#' both, '+' model only, '-' sprite only)."""
    mask = k.sprite_mask(sheet, index, large)
    h, w = len(mask), len(mask[0])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = k._camera("silhouette", (0, 0, 100), (0, 0, 0), ortho_scale=max(w, h))
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "wave2h_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    pixels = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    covered = pixels.reshape(h, supersample, w, supersample).mean(axis=(1, 3)) > 0.5
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    print("silhouette overlap: %.3f" % (both / max(either, 1)))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    return both / max(either, 1)


# --- Build loop ----------------------------------------------------------------------------------

def run(models):
    """models: [(name, builder, [(sheet letter, sprite, large[, (dx, dy)])], out directory)], (dx, dy) moving
    the model onto the sprite for the check only. Options after "--":
    --only a,b  --preview <prefix> (renders <prefix><name>_top.png, _3q.png)  --check <sheets dir>."""
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sprites, out in models:
        if only and name not in only:
            continue
        k.reset()
        build()
        low, high = bounds()
        print(f"== {name}: {triangles()} triangles, bounds {tuple(round(v, 2) for v in low)} .. "
              f"{tuple(round(v, 2) for v in high)}")
        large = sprites[0][2]
        if "stats" in options:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            for obj in meshes():
                mesh = obj.evaluated_get(depsgraph).to_mesh()
                print(f"   {obj.name}: {sum(len(p.vertices) - 2 for p in mesh.polygons)} triangles")
        if "check" in options:
            for sheet, index, big, *offset in sprites:
                # offset: where the model sits relative to the sprite (models built round a pivot)
                dx, dy = offset[0] if offset else (0.0, 0.0)
                print(f"-- {name} vs {sheet} {index}")
                transform_all(Matrix.Translation((dx, dy, 0)))
                check(os.path.join(options["check"], f"enemy_{sheet.upper()}.png"), index, big)
                transform_all(Matrix.Translation((-dx, -dy, 0)))
        k.export(os.path.join(out, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, (24, 28) if large else (12, 14))
