"""Helpers for round 38's hard-surface rebuild of the armoured head (polish_dome_heads.py) and DREAD-NOT's machine round
it (polish_dread_parts.py). Not a model script itself.

Every object is built whole in the picture's plane (x, y as its sprites draw it, z up towards the camera) from separate
solids: armour plates (polish_ring_machine.relief: a constrained Delaunay top over a smooth outline, a narrow rounded
edge, straight walls), domes and bulbs lofted from explicit rings, turned parts (lathes along an axis), tubes along
paths; each part its own palette material (painted steel, dark steel, black pipe, red glass, the white lamp), the
shading left to the geometry and the game's light (no face takes its colour from the sprite's pixels). Then it is cut
along its sprites' boxes into the pieces the levels draw (polish_coral_manta.cut: each cut capped in the part's dark
inside colour), each piece sheared along the game camera's line of sight (y - z tan 20, the normals with it:
polish_fleet_walker.shear_to_camera, so that the camera sees every point where the sprite draws it and whatever stands
higher in the plane covers what lies under it, as the game's draw order does), moved so that its sprite's middle is its
origin, triangulated, joined and exported.

Outlines of the sprites' pixel masks are traced through the midpoints of their boundary edges and smoothed
(polish_fleet_walker.mask_loops: no pixel steps); a part's outline can be the sprite's pixels inside a hand-drawn region
(region_outlines: traced on a grid four times finer, so that the hand-drawn edges are smooth too, shrunk to leave a
seam); hand-drawn outlines are rounded by Chaikin.

A part laid over others (DREAD-NOT's over the head) stands on a smooth floor over their tops: Surface casts straight
down onto the built solids, Envelope spreads and blurs what it finds and adds a gap.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_fleet_walker as fw  # noqa: E402  (mask_loops, area, poly_sd, shear_to_camera, merge_materials)
from polish_ring_machine import relief  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_gyges_wall import blur  # noqa: E402

TAN_T = fw.TAN_T
LIGHT = fw.LIGHT
MAX_MATERIALS = 15


# --- Numbers ---------------------------------------------------------------------------------------------------------

def sstep(e0, e1, x):
    """smoothstep of a single number."""
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def rounded(d, r):
    """0 at an outline, rising as a quarter circle to 1 at distance r inside it."""
    t = min(1.0, max(0.0, d / r))
    return math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))


# --- Outlines --------------------------------------------------------------------------------------------------------

def to_model(points, left, top):
    """Picture points (column, row; continuous: pixel c spans c .. c + 1) as model points."""
    return [(left + c, top - r) for c, r in points]


def rounded_poly(points, left, top, iterations=2):
    """A hand-drawn outline of picture points, its corners rounded (Chaikin), in model coordinates, counter-clockwise."""
    pts = mk.chaikin(to_model(points, left, top), iterations, closed=True)
    return pts if fw.area(pts) > 0 else list(reversed(pts))


def mask_outline(mask, left, top, sigma=1.3, chaikin=1, min_area=2.0):
    """The smoothed outlines (and holes) of a pixel mask (rows, columns) in model coordinates."""
    return [p for p in fw.mask_loops(np.asarray(mask, bool), left, top, chaikin, sigma) if abs(fw.area(p)) > min_area]


def ellipse_poly(cx, cy, rx, ry, angle=0.0, segments=40):
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for j in range(segments):
        t = 2 * math.pi * j / segments
        u, v = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return out


# --- Solids ----------------------------------------------------------------------------------------------------------

def plate(name, polys, top, mat, side=None, paint=None, mats=None, bottom=-1.0, spacing=0.5, band=None,
          smooth_angle=40.0, borders=()):
    """An armour plate over polygons (even-odd: holes stay open): its top at top(x, y, d) (d: the distance in from the
    outline), straight walls down to `bottom`, a flat underside (polish_ring_machine.relief). paint(x, y, d) names a
    top face's material in mats (default: "top")."""
    m = {"top": mat, "side": side or mat}
    if mats:
        m.update(mats)
    return relief(name, polys, top, m, paint=paint, side="side", bottom=bottom, spacing=spacing, borders=borders,
                  smooth_angle=smooth_angle, band=band)


def turned(name, profile, origin, axis, mat, segments=28, squash=1.0, up=(0.0, 0.0, 1.0), close=(True, True)):
    """A turned part: profile [(t, radius), ...] along axis from origin (t increasing), its sections squashed towards
    `up`; its ends closed to the axis."""
    o, a = Vector(origin), Vector(axis).normalized()
    u0 = Vector(up)
    side = a.cross(u0)
    if side.length < 1e-6:
        side = a.cross(Vector((1.0, 0.0, 0.0)))
    side.normalize()
    u = side.cross(a).normalized()
    rings = []
    for t, r in profile:
        rings.append([o + a * t + side * (r * math.cos(2 * math.pi * j / segments)) +
                      u * (r * squash * math.sin(2 * math.pi * j / segments)) for j in range(segments)])
    t0, t1 = profile[0][0], profile[-1][0]
    obj = k.loft(name, rings, mat, cap_start=close[0], cap_end=close[1], start_point=o + a * t0, end_point=o + a * t1)
    k.recalc_normals(obj)
    return obj


def ball(name, centre, radii, mat, segments=32, rings=16, angle=0.0, smooth=80.0):
    """An ellipsoid lofted from explicit rings (the same every run), turned `angle` degrees about z."""
    obj = k.ellipsoid(name, (0.0, 0.0, 0.0), radii, mat, segments, rings)
    obj.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(math.radians(angle), 4, "Z"))
    k.recalc_normals(obj)
    return k.smooth(obj, smooth)


def tube_path(name, points, radius, mat, segments=16, radii=None, squash=1.0, up=(0.0, 0.0, 1.0), caps=True):
    """A round bar along a polyline of 3D points (its sections squashed towards `up`), its ends closed by fans."""
    pts = [Vector(p) for p in points]
    upv = Vector(up)
    rings = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = d.cross(upv)
        if side.length < 1e-6:
            side = d.cross(Vector((1.0, 0.0, 0.0)))
        side.normalize()
        u = side.cross(d).normalized()
        r = radii[i] if radii else radius
        rings.append([p + side * (r * math.cos(2 * math.pi * j / segments)) + u * (r * squash * math.sin(2 * math.pi * j / segments))
                      for j in range(segments)])
    d0 = (pts[1] - pts[0]).normalized()
    d1 = (pts[-1] - pts[-2]).normalized()
    r0 = radii[0] if radii else radius
    r1 = radii[-1] if radii else radius
    obj = k.loft(name, rings, mat, cap_start=caps, cap_end=caps, start_point=pts[0] - d0 * r0 * 0.5,
                 end_point=pts[-1] + d1 * r1 * 0.5)
    k.recalc_normals(obj)
    return obj


def mirror(objects, axis, suffix="_m"):
    """Copies of objects mirrored about x = axis (faces turned back out; custom normals mirrored with them)."""
    out = []
    flip = Matrix.Translation((2.0 * axis, 0.0, 0.0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        mk.apply(obj)
        c = obj.copy()
        c.data = obj.data.copy()
        c.name = obj.name + suffix
        bpy.context.scene.collection.objects.link(c)
        mesh = c.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        mesh.update()
        out.append(c)
    return out


def remove(objects):
    for o in objects:
        mesh = o.data
        bpy.data.objects.remove(o)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


# --- Materials -------------------------------------------------------------------------------------------------------

def materials(prefix, spec):
    """{key: (palette index, metallic, roughness, emission strength in its own colour)} -> palette materials."""
    pal = k.level_palette()
    out = {}
    for key, (index, metallic, roughness, glow) in spec.items():
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        out[key] = k.material("%s_%s" % (prefix, key), palette=index, metallic=metallic, roughness=roughness, **extra)
    return out


# --- What a part lies over -------------------------------------------------------------------------------------------

class Surface:
    """The top (largest z) of some objects over the plane: one BVH of their triangles, cast straight down."""

    def __init__(self, objects):
        bpy.context.view_layer.update()
        deps = bpy.context.evaluated_depsgraph_get()
        verts, polys = [], []
        for o in objects:
            ev = o.evaluated_get(deps)
            mesh = ev.to_mesh()
            mw = o.matrix_world
            base = len(verts)
            verts += [tuple(mw @ v.co) for v in mesh.vertices]
            mesh.calc_loop_triangles()
            polys += [tuple(base + i for i in t.vertices) for t in mesh.loop_triangles]
            ev.to_mesh_clear()
        self.tree = BVHTree.FromPolygons(verts, polys) if polys else None

    def top(self, X, Y, start=200.0):
        X = np.asarray(X, float)
        Y = np.asarray(Y, float)
        out = np.zeros(X.shape)
        if self.tree is None:
            return out
        flat_x, flat_y, res = X.ravel(), Y.ravel(), out.ravel()
        down = Vector((0.0, 0.0, -1.0))
        for i in range(len(flat_x)):
            loc, _n, _i, _d = self.tree.ray_cast(Vector((flat_x[i], flat_y[i], start)), down)
            res[i] = loc.z if loc is not None else 0.0
        return res.reshape(X.shape)


class Envelope:
    """A smooth surface over what a part lies over: the tops of `under` (a function of x, y arrays) sampled on a grid
    over box (x0, x1, y0, y1), spread `reach` pixels and blurred `sigma` pixels, never under the tops themselves plus
    `gap`; sampled bilinearly (0 off the grid)."""

    def __init__(self, under, box, gap=1.0, reach=2.0, sigma=1.5, step=0.5):
        x0, x1, y0, y1 = box
        self.x0, self.y0, self.step = x0, y0, step
        self.nx = int(round((x1 - x0) / step)) + 1
        self.ny = int(round((y1 - y0) / step)) + 1
        gx = x0 + step * np.arange(self.nx)
        gy = y0 + step * np.arange(self.ny)
        X, Y = np.meshgrid(gx, gy)
        raw = under(X, Y)
        self.raw = raw
        spread = raw.copy()
        r = int(math.ceil(reach / step))
        h, w = raw.shape
        p = np.pad(raw, r, mode="edge")
        for dr in range(-r, r + 1):
            for dc in range(-r, r + 1):
                if dr * dr + dc * dc <= r * r:
                    spread = np.maximum(spread, p[r + dr:r + dr + h, r + dc:r + dc + w])
        smooth = blur(spread, sigma / step)
        self.f = np.maximum(smooth, raw) + gap
        self.f = np.where(np.maximum(spread, raw) > 0.0, self.f, 0.0)

    def __call__(self, x, y):
        u, v = (x - self.x0) / self.step, (y - self.y0) / self.step
        i, j = int(math.floor(u)), int(math.floor(v))
        if not (0 <= i < self.nx - 1 and 0 <= j < self.ny - 1):
            return 0.0
        fu, fv = u - i, v - j
        f = self.f
        return float((f[j, i] * (1 - fu) + f[j, i + 1] * fu) * (1 - fv) + (f[j + 1, i] * (1 - fu) + f[j + 1, i + 1] * fu) * fv)


# --- Pieces ----------------------------------------------------------------------------------------------------------

def own_rects(boxes, order, reach=8.0):
    """Each piece's own part of overlapping sprite boxes {name: (x0, x1, y0, y1)}: what no piece later in `order`
    (drawn over it) covers, as rectangles on the grid of the boxes' edges; the rectangles on the outside of all the
    boxes reach `reach` further out (what pokes out past the sprites stays on)."""
    xs = sorted({b[0] for b in boxes.values()} | {b[1] for b in boxes.values()})
    ys = sorted({b[2] for b in boxes.values()} | {b[3] for b in boxes.values()})

    def owner(cx, cy):
        found = None
        for name in order:
            x0, x1, y0, y1 = boxes[name]
            if x0 <= cx < x1 and y0 <= cy < y1:
                found = name
        return found
    cells = {}
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            who = owner(cx, cy)
            if who is not None:
                cells[(i, j)] = who
    out = {name: [] for name in order}
    for (i, j), who in sorted(cells.items()):
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
        if (i - 1, j) not in cells:
            x0 -= reach
        if (i + 1, j) not in cells:
            x1 += reach
        if (i, j - 1) not in cells:
            y0 -= reach
        if (i, j + 1) not in cells:
            y1 += reach
        out[who].append((x0, x1, y0, y1))
    return out


def export_pieces(whole, pieces, cap_of, options, out, only=None, check=None):
    """Cuts the whole (in the picture's plane) into its pieces [(name, rects, origin, mask)], checks each against its
    sprite's own pixels as the camera sees it (mask: 28 rows of 24 bools, or None), shears it for the camera, moves it to
    its origin and exports it (one joined mesh); returns {name: overlap}."""
    results = {}
    for name, rects, origin, mask in pieces:
        if only and name not in only:
            continue
        parts = []
        for rect in rects:
            for src in whole:
                p = cut(src, rect, cap_of(src))
                if p is not None:
                    parts.append(p)
        if not parts:
            print("== %s: empty" % name)
            continue
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        score = None
        bpy.context.view_layer.update()
        if check and mask is not None:
            covered = mk.coverage(parts, 24, 28, centre=origin)
            score = mk.compare("%s, as the camera sees it" % name, covered, mask)
        fw.shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        obj = join(parts, name)
        obj.data.name = name
        drop_unused([obj])
        fw.merge_materials(obj, MAX_MATERIALS)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        results[name] = score
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        remove([obj])
        for src in whole:
            src.hide_render = False
    return results


def sprite_mask_of(art, c0, r0, keep=None):
    """A sprite's own pixels in a picture (an index array, -1 empty): its 24 x 28 box from (c0, r0), only the part
    `keep` (columns c0 c1, rows r0 r1 of the picture) if given; rows of bools."""
    h, w = art.shape
    m = np.zeros((28, 24), bool)
    for r in range(28):
        for c in range(24):
            pr, pc = r0 + r, c0 + c
            if 0 <= pr < h and 0 <= pc < w and art[pr, pc] >= 0:
                if keep is None or (keep[0] <= pc < keep[1] and keep[2] <= pr < keep[3]):
                    m[r, c] = True
    return m.tolist()


def parse_art(text, w, h, row0=0):
    """Rows of two hex digits a pixel ('..' empty) as an index array (h rows, w columns; -1 empty), from row0."""
    rows = [line.strip() for line in text.splitlines() if line.strip()]
    a = np.full((h, w), -1, int)
    for i, line in enumerate(rows):
        for c in range(min(w, len(line) // 2)):
            s = line[2 * c:2 * c + 2]
            if s != "..":
                a[row0 + i, c] = int(s, 16)
    return a


def export_whole(whole, path):
    """The whole object sheared for the camera as one GLB (for looking at; not a game model)."""
    copies = []
    for src in whole:
        c = src.copy()
        c.data = src.data.copy()
        bpy.context.scene.collection.objects.link(c)
        copies.append(c)
    fw.shear_to_camera(copies)
    bpy.context.view_layer.update()
    triangulate(copies)
    obj = join(copies, "whole")
    mk.report("whole", [obj], path)
    remove([obj])


def inside_polygon(C, R, poly):
    """Which points (arrays C, R) lie inside a polygon of (column, row) points (even-odd)."""
    inside = np.zeros(C.shape, bool)
    n = len(poly)
    for i in range(n):
        (c0, r0), (c1, r1) = poly[i], poly[(i + 1) % n]
        cond = (r0 > R) != (r1 > R)
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = c0 + (R - r0) * (c1 - c0) / np.where(r1 == r0, 1e-9, r1 - r0)
        inside ^= cond & (C < xi)
    return inside


def _erode(mask, steps):
    m = mask.copy()
    for _ in range(steps):
        p = np.pad(m, 1)
        h, w = m.shape
        m = m & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return m


def region_outlines(own, regions, left, top, ss=4, sigma=1.0, chaikin=1, min_area=1.5, shrink=0.0):
    """Each region's outlines (and holes): the own pixels (rows, columns) inside its picture polygon (column, row
    points; None: all of them) and not in an earlier region's, traced on a grid ss times finer (so that the hand-drawn
    edges are not stair-stepped), shrunk `shrink` pixels (a groove between neighbouring parts), smoothed over sigma
    pixels; in model coordinates (picture column c at x = left + c, row r at y = top - r). Returns a list (one entry a
    region) of lists of loops."""
    h, w = own.shape
    fine = np.kron(np.asarray(own, bool), np.ones((ss, ss), bool))
    cs = (np.arange(w * ss) + 0.5) / ss
    rs = (np.arange(h * ss) + 0.5) / ss
    C, R = np.meshgrid(cs, rs)
    taken = np.zeros(fine.shape, bool)
    out = []
    for poly in regions:
        m = fine & ~taken
        if poly is not None:
            m &= inside_polygon(C, R, poly)
        taken |= m
        if shrink > 0:
            m = _erode(m, int(round(shrink * ss)))
        if not m.any():
            out.append([])
            continue
        rows_, cols_ = np.nonzero(m)
        r0, r1 = max(rows_.min() - 2, 0), min(rows_.max() + 3, m.shape[0])
        c0, c1 = max(cols_.min() - 2, 0), min(cols_.max() + 3, m.shape[1])
        sub = m[r0:r1, c0:c1]
        loops = fw.mask_loops(sub, float(c0), float(-r0), chaikin, sigma * ss)
        res = []
        for loop in loops:
            pts = [(left + x / ss, top + y / ss) for x, y in loop]
            if abs(fw.area(pts)) > min_area:
                res.append(pts)
        out.append(res)
    return out
