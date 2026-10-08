"""Helpers for the batch I models of wave 3 (wave3_i.py, sheet ^): the sprites' pixels with their
palette indices (wave3_i_art.py), parts raised from regions of those pixels and coloured in bands of
the pixels' shades (cut along smooth borders), turned and tubular details, cutting a whole object
into the pieces the game draws as separate sprites, and the build loop.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera).
An Art's origin (ox, oy) is the pixel corner that becomes (0, 0): the centre of the sprite or of the
whole object the sprites make up.
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
import wave2_h_kit as hk  # noqa: E402

ENEMIES = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies")
SHEET = "enemy_x5e"


# --- Pixels --------------------------------------------------------------------------------------

def grid(text, width):
    """The art's rows as lists of palette indices (None: transparent), `width` pixels each."""
    out = []
    for line in text.strip("\n").split("\n"):
        line = line.ljust(2 * width, ".")
        out.append([None if line[2 * i:2 * i + 2] == ".." else int(line[2 * i:2 * i + 2], 16) for i in range(width)])
    return out


class Art:
    """A sprite's (or a whole object's) pixels: palette indices, None where transparent."""

    def __init__(self, text, width, origin):
        self.g = grid(text, width)
        self.w, self.h = width, len(self.g)
        self.ox, self.oy = origin

    def X(self, col):
        """The x of a pixel column's centre (col may be fractional; col - 0.5 is its left edge)."""
        return col + 0.5 - self.ox

    def Y(self, row):
        return self.oy - (row + 0.5)

    def at(self, c, r):
        if 0 <= r < self.h and 0 <= c < self.w:
            return self.g[r][c]
        return None

    def rows(self, fn):
        """Char rows: fn(index, column, row) -> a char ('.' nothing) for every opaque pixel."""
        return ["".join("." if v is None else fn(v, c, r) for c, v in enumerate(row)) for r, row in enumerate(self.g)]

    def polys(self, rows, chars, smooth=1, epsilon=0.4, min_area=0.5, grow=0.0):
        polys = sh.outlines(rows, chars, (self.ox, self.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)
        if grow:
            polys = [sh.inset(p, -grow) for p in polys]
        return polys

    def field(self, select=None, value=lambda v: v & 15, blur=1):
        """A function (x, y) -> value(index) of the pixels that select(index, column, row) keeps,
        bilinear between pixel centres and blurred `blur` times; elsewhere the nearest kept pixel's."""
        h, w = self.h, self.w
        f = np.full((h, w), np.nan)
        for r in range(h):
            for c in range(w):
                v = self.g[r][c]
                if v is not None and (select is None or select(v, c, r)):
                    f[r, c] = value(v)
        for _ in range(blur):
            out = f.copy()
            for r in range(h):
                for c in range(w):
                    if np.isnan(f[r, c]):
                        continue
                    vals, wts = [], []
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            rr, cc = r + dr, c + dc
                            if 0 <= rr < h and 0 <= cc < w and not np.isnan(f[rr, cc]):
                                vals.append(f[rr, cc])
                                wts.append(2.0 if dr == dc == 0 else 1.0 if dr == 0 or dc == 0 else 0.5)
                    out[r, c] = np.average(vals, weights=wts)
            f = out
        known = np.array([(r, c) for r in range(h) for c in range(w) if not np.isnan(f[r, c])])
        ox, oy = self.ox, self.oy

        def sample(x, y):
            c, r = x + ox - 0.5, oy - y - 0.5
            c0, r0 = math.floor(c), math.floor(r)
            total = weight = 0.0
            for rr, cc, wt in ((r0, c0, (1 - (r - r0)) * (1 - (c - c0))), (r0, c0 + 1, (1 - (r - r0)) * (c - c0)),
                               (r0 + 1, c0, (r - r0) * (1 - (c - c0))), (r0 + 1, c0 + 1, (r - r0) * (c - c0))):
                if 0 <= rr < h and 0 <= cc < w and not np.isnan(f[rr, cc]):
                    total += f[rr, cc] * wt
                    weight += wt
            if weight > 0.05:
                return total / weight
            if len(known) == 0:
                return 0.0
            i = int(np.argmin((known[:, 0] - r) ** 2 + (known[:, 1] - c) ** 2))
            return f[known[i][0], known[i][1]]
        return sample


def box_rows(rows, boxes, into="."):
    """The rows with the pixels inside any box (c0, c1, r0, r1, inclusive) set to `into`."""
    grid_ = [list(r) for r in rows]
    for c0, c1, r0, r1 in boxes:
        for r in range(max(r0, 0), min(r1, len(grid_) - 1) + 1):
            for c in range(max(c0, 0), min(c1, len(grid_[r]) - 1) + 1):
                grid_[r][c] = into
    return ["".join(line) for line in grid_]


# --- Materials -----------------------------------------------------------------------------------

def pal(name, index, metallic=0.3, roughness=0.45, glow=None, color=None):
    return hk.pal(name, index, metallic=metallic, roughness=roughness, glow=glow, color=color)


def ramp_bands(prefix, ramp, shades, metallic=0.5, roughness=0.35, glow=None):
    """Bands for paint(): [(lowest shade, material)] from [(lowest shade, palette shade)] of one ramp."""
    out = []
    for lowest, shade in shades:
        index = ramp * 16 + shade
        g = glow(shade) if callable(glow) else glow
        out.append((lowest, pal(f"{prefix}_{index:02x}", index, metallic=metallic, roughness=roughness, glow=g)))
    return out


# --- Parts ---------------------------------------------------------------------------------------

def paint_bands(obj, value, bands, side=None, side_below=0.5, smooth_angle=55):
    """Colours obj in bands of value(x, y) (the sprite's shade under each point), cut along smooth
    borders; if `side` is given, faces steeper than side_below (walls, the underside) take that band
    (otherwise walls take the band of the top's edge above them)."""
    values = [value(v.co.x, v.co.y) for v in obj.data.vertices]

    def face_band(poly):
        return side if side is not None and poly.normal.z < side_below else None
    return hk.band_split(obj, values, bands, face_band=face_band, smooth_angle=smooth_angle)


def edge_rings(polys, distances, spacing):
    """Points on lines at the given distances inside the polygons' outlines (resampled every
    `spacing`), only where that distance holds (thin parts have no inner lines): regular rows of
    vertices along the edges, so rounded edges come out smooth."""
    a, b = sh._segments(polys)
    out = []
    for dist in distances:
        for poly in polys:
            pts = np.array(sh._resample(sh.inset(poly, dist), spacing), dtype=float)
            if len(pts) == 0:
                continue
            inside = sh._inside(pts, a, b)
            d = sh._distance(pts, a, b)
            keep = inside & (np.abs(d - dist) < 0.2 * dist + 0.05)
            out += [tuple(p) for p in pts[keep]]
    return out


def solid(name, polys, top, bottom=0.0, mats=None, spacing=0.5, smooth_angle=50, band=None, coarse=2,
          rings=(0.25, 0.6, 1.0, 1.5)):
    """As wave2_h_kit.solid (a closed part over the polygons, its top at top(x, y, d), d the distance
    to the outline, a flat underside at `bottom`), with rows of vertices along the edges (at the
    distances `rings`) so that rounded edges are smooth."""
    mats = mats if isinstance(mats, (list, tuple)) else [mats]
    a, b = sh._segments(polys)
    xs = np.concatenate([a[:, 0], b[:, 0]])
    ys = np.concatenate([a[:, 1], b[:, 1]])
    boundary = [p for poly in polys for p in sh._resample(poly, spacing)]
    ring_pts = edge_rings(polys, rings, spacing * 0.9) if rings else []
    gx = np.arange(math.floor(xs.min() / spacing) * spacing, xs.max() + spacing, spacing)
    gy = np.arange(math.floor(ys.min() / spacing) * spacing, ys.max() + spacing, spacing)
    grid_ = np.array([(x, y) for y in gy for x in gx], dtype=float)
    index = np.array([(i, j) for j in range(len(gy)) for i in range(len(gx))])
    keep = sh._inside(grid_, a, b)
    grid_, index = grid_[keep], index[keep]
    edge = sh._distance(grid_, a, b)
    # Grid points clear of the edge rows (where those exist).
    if ring_pts:
        rp = np.array(ring_pts)
        near = np.zeros(len(grid_), dtype=bool)
        for s0 in range(0, len(grid_), 1024):
            dd = np.sqrt(((grid_[s0:s0 + 1024, None, :] - rp[None, :, :]) ** 2).sum(2)).min(1)
            near[s0:s0 + 1024] = dd < 0.45 * spacing
        keep = (edge > 0.35 * spacing) & ~near
    else:
        keep = edge > 0.35 * spacing
    if band is not None:
        keep &= (edge <= band) | ((index[:, 0] % coarse == 0) & (index[:, 1] % coarse == 0))
    grid_ = grid_[keep]
    points2d = [Vector(p) for p in boundary] + [Vector(p) for p in ring_pts] + [Vector(tuple(p)) for p in grid_]
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
    tris = [f for f, kf in zip(tris, sh._inside(centroids, a, b)) if kf]
    d = sh._distance(pts, a, b)
    d[d < 1e-4] = 0.0
    if top.__code__.co_argcount >= 4:  # top(x, y, d, local half-width)
        wl = sh.thickness(pts, d, spacing, sigma=1.0)
        z_top = [top(x, y, dd, ww) for (x, y), dd, ww in zip(pts, d, wl)]
    else:
        z_top = [top(x, y, dd) for (x, y), dd in zip(pts, d)]
    bm = bmesh.new()
    tv = [bm.verts.new((x, y, z)) for (x, y), z in zip(pts, z_top)]
    # A flat underside: the outline alone, triangulated.
    bverts, _e2, bfaces, borig, *_ = geometry.delaunay_2d_cdt([Vector(p) for p in boundary], constraint, [], 0, 1e-6)
    bpts = np.array([(v.x, v.y) for v in bverts], dtype=float)
    bnew = [bm.verts.new((x, y, bottom)) for x, y in bpts]
    btris = [f for f in bfaces if len(f) == 3]
    bcent = np.array([bpts[list(f)].mean(0) for f in btris])
    for f in [f for f, kf in zip(btris, sh._inside(bcent, a, b)) if kf]:
        try:
            bm.faces.new([bnew[i] for i in reversed(f)])
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
    edge_use = {}
    for f in tris:
        try:
            bm.faces.new([tv[i] for i in f])
        except ValueError:
            continue
        for i in range(3):
            e = (f[i], f[(i + 1) % 3])
            edge_use.setdefault((min(e), max(e)), []).append(e)
    for key, uses in edge_use.items():
        if len(uses) == 1:
            i, j = uses[0]
            try:
                bm.faces.new([tv[j], tv[i], bv[i], bv[j]])
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


def raise_part(name, polys, height, radius=1.0, base=0.0, crown=0.0, z_fn=None, mat=None, spacing=0.5,
               smooth_angle=50, band=None, rim=0.0, aspect=None):
    """A part over the polygons standing on z = base: a straight wall `rim` high all round, then its
    top rising to `height` above the base, the edges rounded over `radius`, bulging `crown` more
    far from the edges; z_fn(x, y, z) -> z may reshape the top. aspect: narrow stretches are at most
    aspect times their half-width high (and rounded over their half-width), so they don't stand up
    as thin fins."""
    rim = min(rim, height)
    rings = tuple(r for r in (0.2, 0.5, 0.9, 1.4, 2.0, 2.8) if r < max(radius, 0.3) * 1.05) or (0.2,)

    def top(x, y, d, wl=None):
        h, r = height, radius
        if aspect is not None and wl is not None:
            h = min(height, max(aspect * wl, 0.6))
            r = min(radius, max(wl, 0.3))
        e = hk.round_edge(d, r) if r > 0 else 1.0
        z = base + min(rim, h) + (h - min(rim, h)) * e + crown * min(1.0, max(0.0, (d - r) / 3.0)) ** 0.8
        return z_fn(x, y, z) if z_fn else z
    if aspect is None:
        top3 = top

        def top(x, y, d):  # noqa: F811 (no half-widths needed)
            return top3(x, y, d)
    return solid(name, polys, top, bottom=base, mats=mat, spacing=spacing, smooth_angle=smooth_angle, band=band,
                 rings=rings)


def lighten(obj, keep=0.999):
    """Merges the flat underside of a part into few faces (as wave2_g.simplify_bottom)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    zmin = min(v.co.z for v in bm.verts)
    faces = [f for f in bm.faces if f.normal.z < -keep and all(abs(v.co.z - zmin) < 1e-3 for v in f.verts)]
    if faces:
        try:
            bmesh.ops.dissolve_faces(bm, faces=faces, use_verts=True)
        except Exception:  # noqa: BLE001
            pass
        ngons = [f for f in bm.faces if len(f.verts) > 3]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def planar(obj, degrees=1.0):
    """Merges nearly flat stretches into larger faces (keeping material borders), then triangulates."""
    mod = obj.modifiers.new("planar", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(degrees)
    mod.delimit = {"MATERIAL"}
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def decimate(obj, target):
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tris > target:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.ratio = target / tris
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return obj


def surface(objs, x, y, default=0.0):
    """The highest top of objs at (x, y)."""
    best = None
    for obj in objs if isinstance(objs, (list, tuple)) else [objs]:
        hit, loc, _n, _i = obj.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
        if hit and (best is None or loc.z > best):
            best = loc.z
    return default if best is None else best


# --- Round parts ---------------------------------------------------------------------------------

def tube(name, path, radii, mat, segments=12, squash=1.0, angle=60, up=(0, 0, 1)):
    return hk.tube(name, path, radii, mat, segments, squash, angle, up)


def catmull(points, step=0.5):
    return hk.catmull(points, step)


def lathe(name, profile, mat, axis="y", at=(0.0, 0.0), segments=24, squash=1.0, angle=50):
    return hk.lathe(name, profile, mat, axis, at, segments, squash, angle)


def lathe_dir(name, profile, mat, start, direction, segments=24, squash=1.0, angle=50, up=(0, 0, 1)):
    """A turned part along any direction: profile [(t, radius)] from `start` along `direction`."""
    obj = k.lathe(name, [(t, max(r, 0.02)) for t, r in profile], mat, segments=segments, squash=squash)
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
    return k.smooth(obj, angle)


def ellipsoid(name, centre, radii, mat, segments=20, rings=10, angle=60):
    return hk.ellipsoid(name, centre, radii, mat, segments, rings, angle)


def rounded_box(name, centre, size, mat, bevel=0.4, segments=2, angle=40):
    obj = k.box(name, centre, size, mat)
    k.bevel(obj, bevel, segments)
    sh.apply_modifiers(obj)
    return k.smooth(obj, angle)


# --- Whole objects and pieces --------------------------------------------------------------------

def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def bake():
    for obj in meshes():
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)


def mirror_copy(objects, axis_x=0.0):
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


def mirror_all():
    hk.mirror_all()


def piece(x0, x1, y0, y1):
    """Keeps the part of the scene in x0..x1, y0..y1 (closing the cuts) and moves the box's centre to
    the origin: one sprite of a larger object."""
    bake()
    kept = sh.cut_box(meshes(), x0, x1, y0, y1)
    sh.move(kept, -(x0 + x1) / 2, -(y0 + y1) / 2)
    for obj in kept:
        k.recalc_normals(obj)
        k.smooth(obj, 50)
    return kept


def triangles(obj=None):
    objs = [obj] if obj is not None else meshes()
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)


# --- Registry and build loop ---------------------------------------------------------------------

MODELS = []   # (name, builder, [(sprite, large)], size of the preview)
WHOLES = {}   # name: (builder, size): objects drawn in pieces, for --whole previews


def model(name, sprites, size=(24, 28)):
    """Registers a builder; sprites: [(sprite index, large)] the model is checked against."""
    def register(fn):
        MODELS.append((name, fn, sprites, size))
        return fn
    return register


def run():
    """Options after "--": --only a,b  --preview <prefix>  --check <extracted sheets dir>  --stats 1
    --whole <name>[,<name>] (with --preview: renders whole objects instead of exporting)."""
    options = k.args()
    if "whole" in options:
        for name in options["whole"].split(","):
            build, size = WHOLES[name]
            k.reset()
            build()
            bake()
            print(f"== whole {name}: {triangles()} triangles")
            bpy.context.scene.view_settings.view_transform = "Standard"
            prefix = options.get("preview", "/tmp/whole_") + name
            k.preview(prefix, size, scale=10)
            scene = bpy.context.scene
            cam = bpy.data.objects["3q"]
            cam.location = Vector((38, -48, 42)) * (max(size) / 62)
            scene.render.resolution_x, scene.render.resolution_y = 900, 900
            scene.render.filepath = prefix + "_3q.png"
            bpy.ops.render.render(write_still=True)
        return
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sprites, size in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        bake()
        low, high = hk.bounds()
        print(f"== {name}: {triangles()} triangles, bounds {tuple(round(v, 2) for v in low)} .. "
              f"{tuple(round(v, 2) for v in high)}")
        if "stats" in options:
            for obj in sorted(meshes(), key=triangles, reverse=True)[:10]:
                print(f"   {obj.name}: {triangles(obj)}")
        if "check" in options:
            for index, large in sprites:
                print(f"-- {name} vs ^ {index}")
                hk.check(os.path.join(options["check"], SHEET + ".png"), index, large)
        k.export(os.path.join(ENEMIES, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)
