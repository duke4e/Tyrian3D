"""Helpers for the batch AM models of wave 3 (sheet o, written o in models.cfg: the walker of FLEET and STATION and
the hatches on it; wave3_am.py): the sprites' pixels (wave3_am_art.py) and the kit of batch AJ (wave3_aj_kit: pixel
frames, painting faces by the sprite's pixel under them, heightfield parts, reliefs inflated from pixel regions,
limbs and pipes along curves, discs, rings, glossy bulbs, smooth blends of heights; whole objects cut into their
sprites' pieces, the silhouette check and the build loop), with the heights the walker and its hatches share and a
few helpers for large painted parts: heightfields without the local thickness (field), outlines that close the art's
holes (enclosed, cells_polys), walls and undersides painted one colour (paint_walls, paint_under), flat stretches
merged within each piece (split_at, merge_seamed) and kept flat-shaded (sharpen_flats), heights stretched (stretch_z).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
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
import wave3_aj_kit as aj  # noqa: E402,F401
from wave3_aj_kit import (k, sh, w, n, q, ae, pal, paint_faces, lathe_axis, hoop, catmull, sphere,  # noqa: E402,F401
                          rounded_box, meshes, bake, transform, Frame, Painter, paint_sprite, pixelate, merge_flat,
                          relief, outlines_of, mirror_copies, lift, smoothstep, displace_z, bumps, plate, limb,
                          band_y, pipe, disc, ellipse_ring, superellipse, surface_z, delete_faces, join,
                          flatten_under, bisect_mesh, rotate_z, model, pieced, run, lens, ellipsoid_point, loft_path,
                          torus, heightfield, groove, cone, piece, smin, smax, dome, seg_dist, path_dist, bulb,
                          ring_on, inside, merge_bottom)
import wave3_am_art as art  # noqa: E402,F401

PROTECT = aj.PROTECT

# The hatches (o 191 193, enemies 737 738) lie in three bays of the walker: their bodies' foot at HATCH_FOOT, the
# bays' floors a little below it, so that a hatch sits in its bay wherever the level puts it.
HATCH_FOOT = 16.9
BAY_FLOOR = 16.5

# The walker and its hatches are built with the heights above, then stretched up by Z_SCALE (more depth; the hatches
# keep sitting in their bays).
Z_SCALE = 1.2


def frame(name, width, origin):
    """A Frame of one of wave3_am_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def field(name, polys, z_of, mat=None, spacing=0.5, edge=2.0, smooth_angle=35):
    """A closed part filling the polygons (even-odd), its top at z_of(x, y, e) and its bottom flat at z = 0, its
    sides straight down from the top's outline: as wave3_q_kit.heightfield, without the local thickness (which
    costs the square of the samples: this one serves large parts). e is 0 on the outline, rising as a quarter
    circle to 1 `edge` pixels inside it. The grid's samples lie on multiples of `spacing`, so with an origin on
    whole pixels every inner triangle lies in one pixel (painting by the pixel under it needs no cutting)."""
    a, b = sh._segments(polys)
    xs = np.concatenate([a[:, 0], b[:, 0]])
    ys = np.concatenate([a[:, 1], b[:, 1]])
    boundary = [p for poly in polys for p in sh._resample(poly, spacing)]
    gx = np.arange(math.floor(xs.min() / spacing) * spacing, xs.max() + spacing, spacing)
    gy = np.arange(math.floor(ys.min() / spacing) * spacing, ys.max() + spacing, spacing)
    grid = np.array([(x, y) for y in gy for x in gx], dtype=float)
    grid = grid[sh._inside(grid, a, b)]
    grid = grid[sh._distance(grid, a, b) > 0.3 * spacing]
    points2d = [Vector(p) for p in boundary] + [Vector(tuple(p)) for p in grid]
    constraint, start = [], 0
    for poly in polys:
        count = len(sh._resample(poly, spacing))
        constraint += [(start + i, start + (i + 1) % count) for i in range(count)]
        start += count
    verts, _edges, faces, *_ = geometry.delaunay_2d_cdt(points2d, constraint, [], 0, 1e-6)
    pts = np.array([(v.x, v.y) for v in verts], dtype=float)
    tris = [f for f in faces if len(f) == 3]
    centroids = np.array([pts[list(f)].mean(0) for f in tris])
    keep = sh._inside(centroids, a, b)
    tris = [f for f, kf in zip(tris, keep) if kf]
    d = sh._distance(pts, a, b)
    t = np.clip(d / max(edge, 1e-3), 0.0, 1.0)
    e = np.sqrt(t * (2.0 - t))
    z_top = np.array([max(0.05, z_of(x, y, ee)) for (x, y), ee in zip(pts, e)])

    bm = bmesh.new()
    top = [bm.verts.new((x, y, z)) for (x, y), z in zip(pts, z_top)]
    bot = [bm.verts.new((x, y, 0.0)) for (x, y) in pts]
    edge_use = {}
    for f in tris:
        try:
            bm.faces.new([top[i] for i in f])
            bm.faces.new([bot[i] for i in reversed(f)])
        except ValueError:
            continue
        for i in range(3):
            ed = (f[i], f[(i + 1) % 3])
            key = (min(ed), max(ed))
            edge_use[key] = edge_use.get(key, []) + [ed]
    for key, uses in edge_use.items():
        if len(uses) == 1:
            i, j = uses[0]
            try:
                bm.faces.new([top[j], top[i], bot[i], bot[j]])
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return k.smooth(obj, smooth_angle)


def pixel_polys(f, keep, smooth=2, epsilon=0.35, min_area=0.4):
    """The outlines of the pixels keep(index, column, row) accepts (smoothed pixel staircases)."""
    return outlines_of(f, keep, smooth=smooth, epsilon=epsilon, min_area=min_area)


def box_poly(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def paint_walls(obj, f, paint, probe=1.5, max_nz=0.5, grey=0x04, blue=0x37, dark_blue=0x63):
    """Paints the steep faces (walls) one colour by the ramp of the pixel `probe` pixels inside them: grey,
    blue or dark blue (the pixels along a wall vary too much to paint them one by one)."""
    def pick(c, nrm):
        if abs(nrm.z) >= max_nz:
            return None
        hx, hy = nrm.x, nrm.y
        length = math.hypot(hx, hy)
        if length < 1e-6:
            return None
        hx, hy = hx / length, hy / length
        v = None
        for p in (probe, probe * 2.0, 0.5):
            v = f.at(c.x - hx * p, c.y - hy * p)
            if v is not None:
                break
        if v is None:
            return paint(grey)
        ramp = v >> 4
        if ramp in (3, 8, 9):
            return paint(blue)
        if ramp == 6:
            return paint(dark_blue)
        return paint(grey)
    return paint_faces(obj, pick)


def sharpen_flats(obj, min_area=0.6):
    """Marks the edges of large faces sharp: after merging flat stretches into large triangles, their corners
    would otherwise share normals with the bevels round them and shade the whole triangle in a gradient."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for f in bm.faces:
        if f.calc_area() >= min_area:
            for e in f.edges:
                e.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def split_at(obj, xs=(), ys=()):
    """Cuts obj's faces along the lines x = v and y = v (the pieces' borders) and marks the cuts as seams, so that
    merging flat stretches (merge_seamed) keeps each piece's triangles within the piece: cutting the pieces out
    later splits nothing, and no long slivers run across a border."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for axis, values in ((0, xs), (1, ys)):
        for v in values:
            co = (v, 0, 0) if axis == 0 else (0, v, 0)
            no = (1, 0, 0) if axis == 0 else (0, 1, 0)
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
            for e in res["geom_cut"]:
                if isinstance(e, bmesh.types.BMEdge):
                    e.seam = True
    # Edges already lying on a line (the grid's own) are seams too.
    for e in bm.edges:
        a, b = e.verts[0].co, e.verts[1].co
        if any(abs(a.x - v) < 1e-4 and abs(b.x - v) < 1e-4 for v in xs) or \
                any(abs(a.y - v) < 1e-4 and abs(b.y - v) < 1e-4 for v in ys):
            e.seam = True
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def merge_seamed(obj, angle=0.5):
    """merge_flat, keeping seams (split_at's lines) and material borders."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL", "SEAM"})
    ngons = [f for f in bm.faces if len(f.verts) > 3]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def enclosed(f, keep):
    """The pixels keep(index, column, row) accepts plus the transparent ones they enclose (holes in the art that
    would let the ground show through): a set of (column, row)."""
    inside = {(c, r) for r in range(f.height) for c in range(f.width)
              if f.g[r][c] is not None and keep(f.g[r][c], c, r)}
    outside = set()
    stack = [(c, r) for c in range(-1, f.width + 1) for r in (-1, f.height)] + \
            [(c, r) for r in range(f.height) for c in (-1, f.width)]
    while stack:
        c, r = stack.pop()
        if (c, r) in outside or (c, r) in inside:
            continue
        if not (-1 <= c <= f.width and -1 <= r <= f.height):
            continue
        outside.add((c, r))
        stack += [(c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)]
    holes = {(c, r) for r in range(f.height) for c in range(f.width)
             if (c, r) not in inside and (c, r) not in outside}
    return inside | holes


def paint_under(obj, mat):
    """One material for every face looking down (the never-seen underside: it then merges into few triangles)."""
    return paint_faces(obj, lambda c, nrm: mat if nrm.z < -0.9 else None)


def cells_polys(f, cells, smooth=2, epsilon=0.35, min_area=0.4):
    """The outlines of a set of pixels (column, row) of frame f (smoothed pixel staircases)."""
    rows = ["".join("x" if (c, r) in cells else "." for c in range(f.width)) for r in range(f.height)]
    return sh.outlines(rows, "x", (f.ox, f.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)


def stretch_z(objects, factor=None):
    """Scales the objects' heights by Z_SCALE (or factor) from z = 0."""
    m = Matrix.Scale(Z_SCALE if factor is None else factor, 4, (0.0, 0.0, 1.0))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
        obj.data.update()
    return objects
