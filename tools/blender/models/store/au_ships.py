"""The store's illustration in 3D (batch AU, part "ships"): the five big ship pictures of the store
as models, their decks at z = 12 where the store puts the guns and the generator.

    store_ship_31  USP Talon, SuperCarrot, USP Fang, U-Ship, Silver Ship, Nort Ship (option shape 31)
    store_ship_32  the Stalkers, Red Dragon, PeteZoomer, Rum Bottle (option shape 32)
    store_ship_27  Gencore Phoenix, Gencore Maelstrom (option shape 27)
    store_ship_44  Storm (option shape 44)
    store_ship_45  Gencore II (option shape 45)

Units are the store screen's pixels; X right, +Y up the screen, Z up; each model's origin is the
centre of its picture (the store draws each piece at its picture's centre). The pictures
(au_ships_art.py) give the outlines and the colours' regions; the forms are modelled here: each
hull is one surface over the picture's outline whose height is a function of the position (a
ship's `height`), sampled finely where it bends and along the outline (so rims shade smoothly),
with real parts (rails, frames, engines, nozzles, domes, glass, lamps) set on it. The guns and
the generator are separate models (au_front_guns.py, au_rear_guns.py, au_generators.py) standing
on the deck; the hulls keep the deck clear along the centre line where they go.

usage: Blender -b --factory-startup -P au_ships.py -- [--only 31,44] [--preview <prefix>] [--check 1]
       [--stats 1] [--mounts 1] [--sprites <folder with the store's weapon_<n>.png>]
  --preview renders <prefix><n>_top.png (framed like the picture), _3q.png and _store.png (tilted as
  the store turns it); --mounts shows where the store puts the guns and the generator in those
  previews, --sprites lays the store's pictures of a generator and two guns there; --check prints
  the top view's overlap with the picture; --stats triangles per part.
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
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402
import au_ships_art as art  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "store")
DECK = 12.0  # where the guns and the generator stand (SHOWCASE_DECK in video.c)
RES = 0.5    # the finest sampling of the hulls, in pixels

# Where the store draws each ship's picture, and the guns' and generators' pictures (store.json:
# top-left corners and sizes, screen pixels), for --mounts.
SHIP_AT = {31: (35, 33), 27: (31, 36), 32: (31, 35), 44: (36, 33), 45: (30, 30)}
MOUNTS = [  # (x, y, w, h)
    (62, 84, 31, 35),   # generator 16 (standard)
    (61, 48, 33, 34),   # front gun 0 (pulse cannon)
    (54, 36, 46, 44),   # front gun 2 (mega cannon)
    (41, 92, 73, 50),   # rear gun 8 (starburst)
    (39, 96, 76, 49),   # rear gun 13 (vulcan)
]


# --- Small maths ---------------------------------------------------------------------------------

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def round_up(t):
    """0 at t = 0 rising as a quarter circle to 1 at t = 1 (a rounded edge's profile)."""
    t = np.clip(t, 0.0, 1.0)
    return np.sqrt(np.maximum(0.0, 1.0 - (1.0 - t) ** 2))


def smax(a, b, r=1.0):
    """Smooth maximum (a fillet of about r where the two meet)."""
    h = np.clip(0.5 + 0.5 * (a - b) / r, 0.0, 1.0)
    return b + (a - b) * h + r * h * (1 - h)


def smin(a, b, r=1.0):
    return -smax(-a, -b, r)


def groove(dist, width=0.9, depth=0.6):
    """A groove's profile across it (dist from its middle line): flat-bottomed, crisp edges."""
    return depth * (1 - smoothstep(width * 0.4, width, dist))


def interp(points, x):
    """A smooth curve through (x, value) points (Catmull-Rom), at x (any array)."""
    pts = k.profile(points, step=0.25)
    xs = np.array([p[0] for p in pts])
    vs = np.array([p[1] for p in pts])
    return np.interp(x, xs, vs)


def gauss_kernel(sigma):
    radius = max(1, int(math.ceil(3 * sigma)))
    xs = np.arange(-radius, radius + 1)
    kern = np.exp(-xs ** 2 / (2 * sigma ** 2))
    return kern / kern.sum()


def lowpass(poly, sigma=1.0, spacing=0.4):
    """A closed outline resampled every `spacing` and smoothed along itself with a Gaussian of
    `sigma` pixels: the pixels' staircases ironed out (they would shade as ripples)."""
    pts = np.array(list(poly) + [poly[0]], dtype=float)
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    count = max(8, int(cum[-1] / spacing))
    t = np.linspace(0, cum[-1], count, endpoint=False)
    xy = np.stack([np.interp(t, cum, pts[:, 0]), np.interp(t, cum, pts[:, 1])], 1)
    kern = gauss_kernel(sigma / (cum[-1] / count))
    r = len(kern) // 2
    padded = np.concatenate([xy[-r:], xy, xy[:r]]) if r else xy
    out = np.stack([np.convolve(padded[:, i], kern, mode="valid") for i in (0, 1)], 1)
    return [tuple(p) for p in out]


# --- The picture -----------------------------------------------------------------------------------

class Picture:
    """A ship picture: its coverage and outline (smoothed along itself by sigma pixels). Picture
    coordinates: px right, py down, pixel (c, r) covering c..c+1, r..r+1; model x = px - w / 2,
    y = h / 2 - py."""

    def __init__(self, number, sigma=2.0):
        p = art.PICTURES[number]
        self.number = number
        self.w, self.h = p["size"]
        self.alpha = np.array([[ch != "." for ch in row] for row in p["rows"]])
        rows = ["".join("#" if a else "." for a in row) for row in self.alpha]
        self.polys = [lowpass(q, sigma) for q in
                      sh.outlines(rows, "#", (self.w / 2, self.h / 2), smooth=0, epsilon=0.3, min_area=4.0)]
        self.seg_a, self.seg_b = sh._segments(self.polys)

    def inward_normals(self, poly):
        p = np.array(poly)
        t = np.roll(p, -1, 0) - np.roll(p, 1, 0)
        n = np.stack([-t[:, 1], t[:, 0]], 1)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        inward = sh._inside(p + 0.3 * n, self.seg_a, self.seg_b)
        n[~inward] *= -1
        return p, n

    def offset_paths(self, d, keep, step=0.8, min_length=3.0):
        """Curves parallel to the outline d pixels inside it, where keep(px, py) holds (picture
        coordinates), as polylines [(px, py), ...]: for panel lines along rims."""
        paths = []
        for poly in self.polys:
            p, n = self.inward_normals(poly)
            q = p + d * n
            real = sh._distance(q, self.seg_a, self.seg_b)
            px, py = q[:, 0] + self.w / 2, self.h / 2 - q[:, 1]
            ok = (np.abs(real - d) < 0.15) & sh._inside(q, self.seg_a, self.seg_b) & keep(px, py)
            if ok.all():
                runs = [list(range(len(q))) + [0]]
            else:
                start = int(np.argmin(ok))  # begin the walk at a gap
                order = [(start + i) % len(q) for i in range(len(q))]
                runs, run = [], []
                for i in order:
                    if ok[i]:
                        run.append(i)
                    elif run:
                        runs.append(run)
                        run = []
                if run:
                    runs.append(run)
            for run in runs:
                pts = [(px[i], py[i]) for i in run]
                out = [pts[0]]
                for pt in pts[1:]:
                    if math.hypot(pt[0] - out[-1][0], pt[1] - out[-1][1]) >= step:
                        out.append(pt)
                length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(out, out[1:]))
                if len(out) >= 3 and length >= min_length:
                    paths.append(out)
        return paths

    def X(self, px):
        return px - self.w / 2

    def Y(self, py):
        return self.h / 2 - py

    def signed_distance(self, px, py):
        """Distance into the outline (negative outside), at picture points (arrays)."""
        shape = np.shape(px)
        pts = np.stack([np.ravel(px) - self.w / 2, self.h / 2 - np.ravel(py)], 1)
        d = sh._distance(pts, self.seg_a, self.seg_b)
        inside = sh._inside(pts, self.seg_a, self.seg_b)
        return np.where(inside, d, -d).reshape(shape)

    def field(self, px, py):
        return Field(self, px, py)

    def grid(self, step=RES):
        gx = np.arange(0.0, self.w + step / 2, step)
        gy = np.arange(0.0, self.h + step / 2, step)
        PX, PY = np.meshgrid(gx, gy)
        return Field(self, PX, PY)


class Field:
    """Points (picture coordinates, arrays of any shape) where a ship's height and materials are
    evaluated: P, Q (px, py), D (distance into the outline), dx (from the picture's middle), and
    shapes' signed distances there (negative inside)."""

    def __init__(self, pic, px, py, distance=True):
        self.pic = pic
        self.P = np.asarray(px, dtype=float)
        self.Q = np.asarray(py, dtype=float)
        self.D = pic.signed_distance(self.P, self.Q) if distance else None
        self.dx = self.P - pic.w / 2
        self.adx = np.abs(self.dx)

    def rect(self, x0, y0, x1, y1, r=0.0):
        """A rounded rectangle."""
        cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
        qx, qy = np.abs(self.P - cx) - hx, np.abs(self.Q - cy) - hy
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

    def ellipse(self, cx, cy, rx, ry):
        """An ellipse (the distance is approximate away from round ones)."""
        return (np.hypot((self.P - cx) / rx, (self.Q - cy) / ry) - 1) * min(rx, ry)

    def polyline(self, points):
        """Distance to an open polyline [(px, py), ...]."""
        a = np.array(points[:-1], dtype=float)
        b = np.array(points[1:], dtype=float)
        pts = np.stack([self.P.ravel(), self.Q.ravel()], 1)
        return sh._distance(pts, a, b).reshape(self.P.shape)

    def poly(self, points):
        """A polygon [(px, py), ...]."""
        a, b = sh._segments([list(points)])
        pts = np.stack([self.P.ravel(), self.Q.ravel()], 1)
        d = sh._distance(pts, a, b)
        inside = sh._inside(pts, a, b)
        return np.where(inside, -d, d).reshape(self.P.shape)



# --- The hull: a surface over the outline ----------------------------------------------------------

class Hull:
    """A closed hull over the picture's outline: its top at height(field) and, face by face, the
    material material(field, z) picks (an index into mats); its underside at bottom(d) (d: the
    distance into the outline; the faces take `under`); walls between them along the outline.
    The top is sampled every RES pixels where it bends sharply or its material changes, every
    2 RES where it bends gently, every coarse * RES elsewhere, along curves parallel to the
    outline at the distances `rims` (so that rounded rims shade smoothly), along contour lines
    where it is steep, and along the zero lines of the fields borders(field) gives (where
    materials meet), so that edges run straight rather than in the grid's steps. Its normals come
    from the height function, so it shades smoothly whatever the triangles."""

    def __init__(self, pic, height, material, mats, under, bottom, name="hull", coarse=4,
                 rims=(0.25, 0.7, 1.3, 2.0, 2.9, 4.0), borders=None):
        self.pic, self.height, self.material, self.borders = pic, height, material, borders
        self.mats, self.under = mats, under
        self.obj = self._build(name, bottom, coarse, rims)

    def z_at(self, x, y):
        """The top's height at model (x, y)."""
        f = self.pic.field(np.array([x + self.pic.w / 2]), np.array([self.pic.h / 2 - y]))
        return float(self.height(f)[0])

    def seam(self, name, path, m, radius=0.34, sink=0.1, squash=0.7):
        """A thin line laid into the surface along a path [(px, py), ...] (picture coordinates):
        a panel line (or a lit strip) drawn crisply rather than cut into the sampled surface."""
        p = np.array(path, dtype=float)
        # Every half pixel, following the surface; only where it is well inside the outline.
        seg = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1))
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        t = np.linspace(0, cum[-1], max(3, int(cum[-1] / 0.7) + 1))
        p = np.stack([np.interp(t, cum, p[:, 0]), np.interp(t, cum, p[:, 1])], 1)
        f = self.pic.field(p[:, 0], p[:, 1])
        z = self.height(f)
        inside = f.D > 1.2
        out, run = [], []
        for ok, (a, b), c in zip(inside, p, z):
            if ok:
                run.append((self.pic.X(a), self.pic.Y(b), c - sink))
            elif run:
                out.append(run)
                run = []
        if run:
            out.append(run)
        objs = []
        for pts in out:
            if len(pts) >= 3:
                radii = [radius * 0.4] + [radius] * (len(pts) - 2) + [radius * 0.4]
                objs.append(tube(name, pts, radii, m, segments=5, squash=squash))
        return objs

    def _contours(self, g, zg, steep, levels=None):
        """Points and segments of the height's contour lines every `levels` units across the
        steep cells of the grid (marching squares), in model coordinates; or of the field zg
        at the given levels."""
        pic = self.pic
        lv = self.levels
        z0 = math.floor(zg.min() / lv) * lv
        if levels is not None:
            lv, z0 = 1.0, levels[0]
        points, index, segs = [], {}, []

        def crossing(i0, j0, i1, j1, n, level):
            key = (i0, j0, i1, j1, n)
            if key not in index:
                za, zb = zg[i0, j0], zg[i1, j1]
                t = (level - za) / (zb - za)
                px = g.P[i0, j0] + (g.P[i1, j1] - g.P[i0, j0]) * t
                py = g.Q[i0, j0] + (g.Q[i1, j1] - g.Q[i0, j0]) * t
                index[key] = len(points)
                points.append((pic.X(px), pic.Y(py)))
            return index[key]
        cells = np.argwhere(steep[:-1, :-1] & steep[1:, :-1] & steep[:-1, 1:] & steep[1:, 1:])
        for i, j in cells:
            corners = [(i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)]
            zs = [zg[c] for c in corners]
            lo, hi = min(zs), max(zs)
            n0 = int(math.ceil((lo - z0) / lv))
            n1 = int(math.floor((hi - z0) / lv))
            if levels is not None:
                n0, n1 = (0, 0) if lo < z0 < hi else (1, 0)
            for n in range(n0, n1 + 1):
                level = z0 + n * lv + 1e-6
                hits = []
                for e in range(4):
                    (ia, ja), (ib, jb) = corners[e], corners[(e + 1) % 4]
                    if (zg[ia, ja] - level) * (zg[ib, jb] - level) < 0:
                        a_, b_ = sorted([(ia, ja), (ib, jb)])
                        hits.append(crossing(a_[0], a_[1], b_[0], b_[1], n, level))
                if len(hits) == 2:
                    segs.append((hits[0], hits[1]))
                elif len(hits) == 4:
                    segs += [(hits[0], hits[1]), (hits[2], hits[3])]
        return points, segs

    flatten = 2.0  # neighbouring faces closer than this (degrees) to coplanar are merged
    steep = 0.9    # slopes steeper than this (height per pixel) are sampled along contour lines
    levels = 0.6   # every this much height

    def _rim_points(self, rims):
        pts = []
        for poly in self.pic.polys:
            p, n = self.pic.inward_normals(poly)
            for d in rims:
                step = max(1, int(round((0.45 + 0.12 * d) / 0.4)))  # sparser further in
                q = (p + d * n)[::step]
                real = sh._distance(q, self.pic.seg_a, self.pic.seg_b)
                ok = (np.abs(real - d) < 0.12) & sh._inside(q, self.pic.seg_a, self.pic.seg_b)
                pts.append(q[ok])
        return np.concatenate(pts) if pts else np.zeros((0, 2))

    def _build(self, name, bottom, coarse, rims):
        pic = self.pic
        polys = pic.polys
        a, b = pic.seg_a, pic.seg_b
        boundary = [q for poly in polys for q in sh._resample(poly, RES)]
        constraint, start = [], 0
        for poly in polys:
            count = len(sh._resample(poly, RES))
            constraint += [(start + i, start + (i + 1) % count) for i in range(count)]
            start += count
        n_boundary = len(boundary)

        # The grid: heights and materials to find where the surface needs fine sampling.
        g = pic.grid()
        zg = self.height(g)
        mg = self.material(g, zg)
        lap = np.zeros_like(zg)
        lap[1:-1, 1:-1] = np.abs(zg[2:, 1:-1] + zg[:-2, 1:-1] + zg[1:-1, 2:] + zg[1:-1, :-2] -
                                 4 * zg[1:-1, 1:-1])
        change = np.zeros_like(zg, dtype=bool)
        for axis in (0, 1):
            diff = np.diff(mg, axis=axis) != 0
            if axis == 0:
                change[1:, :] |= diff
                change[:-1, :] |= diff
            else:
                change[:, 1:] |= diff
                change[:, :-1] |= diff
        ii, jj = np.indices(zg.shape)
        rim_max = max(rims) if rims else 0.0
        # Steep walls are sampled along their contour lines (so that their edges run straight
        # rather than in steps of the grid), the rest on the grid.
        gy_, gx_ = np.gradient(zg, RES)
        steep = (np.hypot(gx_, gy_) > self.steep) & (g.D > rim_max + 0.6)
        steep |= (np.roll(steep, 1, 0) & np.roll(steep, -1, 0)) | (np.roll(steep, 1, 1) & np.roll(steep, -1, 1))
        fine = (lap > 0.2) | change
        medium = (lap > 0.05)
        keep = (g.D > rim_max + 0.35) & (fine | (medium & (ii % 2 == 0) & (jj % 2 == 0)) |
                                         ((ii % coarse == 0) & (jj % coarse == 0)))
        keep |= (g.D > 0.3) & fine & change  # material borders out to the rims too
        near_steep = steep.copy()
        for axis in (0, 1):
            near_steep |= np.roll(steep, 1, axis) | np.roll(steep, -1, axis)
        keep &= ~near_steep
        nodes = np.stack([pic.X(g.P[keep]), pic.Y(g.Q[keep])], 1)
        cpts, csegs = self._contours(g, zg, steep)
        # Material borders (zero lines of the fields `borders` gives) become edges too, so that
        # the colours meet along clean lines.
        if self.borders is not None:
            for sdf in self.borders(g):
                bpts, bsegs = self._contours(g, sdf, g.D > 0.4, levels=[0.0])
                bsegs = [(s + len(cpts), t + len(cpts)) for s, t in bsegs]
                cpts, csegs = cpts + bpts, csegs + bsegs
        rim = self._rim_points(rims)
        pts2 = ([Vector(q) for q in boundary] + [Vector(tuple(q)) for q in rim] +
                [Vector(tuple(q)) for q in nodes] + [Vector(tuple(q)) for q in cpts])
        base = len(boundary) + len(rim) + len(nodes)
        constraint = constraint + [(base + s, base + t) for s, t in csegs]
        verts, _e, faces, orig, *_ = geometry.delaunay_2d_cdt(pts2, constraint, [], 0, 1e-4)
        pts = np.array([(v.x, v.y) for v in verts], dtype=float)
        tris = [f for f in faces if len(f) == 3]
        cen = np.array([pts[list(f)].mean(0) for f in tris])
        tris = [f for f, kf in zip(tris, sh._inside(cen, a, b)) if kf]
        fv = pic.field(pts[:, 0] + pic.w / 2, pic.h / 2 - pts[:, 1])
        ztop = self.height(fv)
        cen = np.array([pts[list(f)].mean(0) for f in tris])
        fc = pic.field(cen[:, 0] + pic.w / 2, pic.h / 2 - cen[:, 1])
        mtop = self.material(fc, np.array([ztop[list(f)].mean() for f in tris]))

        # The underside: the outline and a coarse grid.
        keep_b = (g.D > 1.0) & (ii % 6 == 0) & (jj % 6 == 0)
        bnodes = np.stack([pic.X(g.P[keep_b]), pic.Y(g.Q[keep_b])], 1)
        bpts2 = [Vector(q) for q in boundary] + [Vector(tuple(q)) for q in bnodes]
        bverts, _e2, bfaces, borig, *_ = geometry.delaunay_2d_cdt(bpts2, constraint, [], 0, 1e-4)
        bp = np.array([(v.x, v.y) for v in bverts], dtype=float)
        btris = [f for f in bfaces if len(f) == 3]
        bcen = np.array([bp[list(f)].mean(0) for f in btris])
        btris = [f for f, kf in zip(btris, sh._inside(bcen, a, b)) if kf]
        bd = sh._distance(bp, a, b)
        on_outline = [i for i, o in enumerate(borig) if any(j < n_boundary for j in o)]
        bd[on_outline] = 0.0
        zb = np.array([bottom(float(dd), x, y) for dd, (x, y) in zip(bd, bp)])

        # The top's normals from the height function's slope (smooth whatever the triangles).
        e = 0.12
        hx = (self.height(pic.field(fv.P + e, fv.Q)) - self.height(pic.field(fv.P - e, fv.Q))) / (2 * e)
        hy = (self.height(pic.field(fv.P, fv.Q - e)) - self.height(pic.field(fv.P, fv.Q + e))) / (2 * e)
        nrm = np.stack([-hx, -hy, np.ones_like(hx)], 1)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)

        bm = bmesh.new()
        layer = bm.verts.layers.float_vector.new("analytic_normal")
        tv = [bm.verts.new((x, y, z)) for (x, y), z in zip(pts, ztop)]
        for v, n in zip(tv, nrm):
            v[layer] = n
        bv = [bm.verts.new((x, y, z)) for (x, y), z in zip(bp, zb)]
        for v in bv:
            v[layer] = (0.0, 0.0, 0.0)
        input_to_bottom = {}
        for i, o in enumerate(borig):
            for j in o:
                if j < n_boundary:
                    input_to_bottom[j] = bv[i]
        top_to_bottom = {}
        for i, o in enumerate(orig):
            for j in o:
                if j < n_boundary and j in input_to_bottom:
                    top_to_bottom[i] = input_to_bottom[j]
        under_index = len(self.mats)
        edge_use = {}
        for f, m in zip(tris, mtop):
            try:
                face = bm.faces.new([tv[i] for i in f])
            except ValueError:
                continue
            face.material_index = int(m)
            for i in range(3):
                e = (f[i], f[(i + 1) % 3])
                edge_use.setdefault((min(e), max(e)), []).append((e, int(m)))
        for f in btris:
            try:
                face = bm.faces.new([bv[i] for i in reversed(f)])
                face.material_index = under_index
            except ValueError:
                pass
        for uses in edge_use.values():
            if len(uses) != 1:
                continue
            (i, j), m = uses[0]
            if i in top_to_bottom and j in top_to_bottom:
                try:
                    wall = bm.faces.new([tv[j], tv[i], top_to_bottom[i], top_to_bottom[j]])
                    wall.material_index = m
                except ValueError:
                    pass
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        # Nearly flat stretches need few triangles (their shading comes from the normals).
        if self.flatten > 0:
            bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(self.flatten), verts=bm.verts[:],
                                     edges=bm.edges[:], use_dissolve_boundaries=False, delimit={"MATERIAL"})
            bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.normal_update()
        for v in bm.verts:  # the underside's and the walls' normals from their faces
            if Vector(v[layer]).length < 0.5:
                v[layer] = v.normal
        normals = [Vector(v[layer]).normalized() for v in bm.verts]
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for m in self.mats:
            obj.data.materials.append(m)
        obj.data.materials.append(self.under)
        mesh.shade_smooth()
        mesh.normals_split_custom_set_from_vertices(normals)
        if "analytic_normal" in mesh.attributes:
            mesh.attributes.remove(mesh.attributes["analytic_normal"])
        return obj


# --- Parts -----------------------------------------------------------------------------------------

def mat(name, rgb, metallic=0.4, roughness=0.4, glow=None, glow_rgb=None, alpha=None):
    """An explicit-colour material (the store's palette is fixed); glow: emission strength."""
    if glow:
        return k.material(name, rgb, metallic=metallic, roughness=roughness, emission=glow_rgb or rgb,
                          emission_strength=glow, alpha=alpha)
    return k.material(name, rgb, metallic=metallic, roughness=roughness, alpha=alpha)


def lathe(name, profile, m, axis="y", at=(0.0, 0.0), segments=24, squash=1.0, angle=50):
    """A round part about an axis through `at` ((x, z) for axis y, (y, z) for axis x, (x, y) for
    axis z): profile [(t, radius)] in increasing t along the axis."""
    rings = []
    for t, r in profile:
        r = max(r, 0.02)
        ring = []
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            u, v = math.cos(ang) * r, math.sin(ang) * r * squash
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
    obj = k.loft(name, rings, m, start_point=s, end_point=e)
    return k.smooth(obj, angle)


def frame_rings(path, radii, segments=12, squash=1.0, up=(0, 0, 1)):
    path = [Vector(q) for q in path]
    radii = radii if isinstance(radii, (list, tuple)) else [radii] * len(path)
    up = Vector(up)
    out = []
    for i, q in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        u = up if abs(t.dot(up)) < 0.95 else Vector((1, 0, 0))
        side = t.cross(u).normalized()
        upv = side.cross(t).normalized()
        r = radii[i]
        rr = r if isinstance(r, (tuple, list)) else (r, r * squash)
        out.append([q + side * math.cos(2 * math.pi * j / segments) * rr[0] +
                    upv * math.sin(2 * math.pi * j / segments) * rr[1] for j in range(segments)])
    return out


def tube(name, path, radii, m, segments=12, squash=1.0, angle=60, up=(0, 0, 1)):
    return k.smooth(k.loft(name, frame_rings(path, radii, segments, squash, up), m), angle)


def rbox(name, centre, size, m, bevel=0.4, segments=2):
    obj = k.box(name, centre, size, m)
    if bevel > 0:
        k.bevel(obj, min(bevel, min(size) / 2 - 0.01), segments)
        mod = obj.modifiers[-1]
        mod.limit_method = "NONE"
    return k.smooth(obj, 40)


def ellipsoid(name, centre, radii, m, segments=24, rings=12, angle=60):
    return k.smooth(k.ellipsoid(name, centre, radii, m, segments, rings), angle)


def slab(name, outline, z0, z1, m, bevel=0.0):
    obj = k.slab(name, outline, z0, z1, m, bevel_width=bevel, bevel_segments=2)
    return k.smooth(obj, 35)


def torus(name, centre, major, minor, m, segments=32, sides=12, squash=1.0):
    """A ring lying flat (axis z)."""
    cx, cy, cz = centre
    verts, faces = [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        for j in range(sides):
            b = 2 * math.pi * j / sides
            r = major + minor * math.cos(b)
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz + minor * squash * math.sin(b)))
    for i in range(segments):
        for j in range(sides):
            a0, a1 = i * sides + j, i * sides + (j + 1) % sides
            b0, b1 = ((i + 1) % segments) * sides + j, ((i + 1) % segments) * sides + (j + 1) % sides
            faces.append((a0, b0, b1, a1))
    obj = k.mesh_object(name, verts, faces, m)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def capsule(name, p0, p1, radius, m, squash=1.0, segments=16, angle=50):
    """A rod with rounded ends from p0 to p1 (3D points), its section squashed towards z."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = p1 - p0
    length = axis.length
    steps = 5
    profile = []
    for i in range(steps + 1):  # the rounded ends
        a = math.pi / 2 * (1 - i / steps)
        profile.append((-radius * math.sin(a) + radius, radius * math.cos(a)))
    for i in range(steps + 1):
        a = math.pi / 2 * i / steps
        profile.append((length - radius + radius * math.sin(a), radius * math.cos(a)))
    obj = lathe(name, profile, m, axis="y", segments=segments, squash=squash, angle=angle)
    # Built along +y from the origin: turned onto the axis.
    direction = axis.normalized()
    rot = Vector((0, 1, 0)).rotation_difference(direction).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(p0) @ rot)
    return obj


def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def triangles():
    total = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in meshes():
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        total += sum(len(q.vertices) - 2 for q in mesh.polygons)
    return total


def bounds():
    bpy.context.view_layer.update()
    corners = [o.matrix_world @ Vector(c) for o in meshes() for c in o.bound_box]
    low = Vector([min(c[i] for c in corners) for i in range(3)])
    high = Vector([max(c[i] for c in corners) for i in range(3)])
    return low, high


# --- Previews and the silhouette check ------------------------------------------------------------

def _lights():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.58, 0.68, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.5
    sun_obj = bpy.data.objects.new("sun", sun)
    # The game's sun (render_gpu.c: 0.6, -1, 0.6 in its axes): from the upper left, 50 degrees up.
    sun_obj.rotation_euler = Vector((0.6, -0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)


def preview(prefix, pic):
    _lights()
    scene = bpy.context.scene
    w, h = pic.w, pic.h
    scale = int(os.environ.get("AU_TOP", "5"))
    scene.render.resolution_x, scene.render.resolution_y = w * scale, h * scale
    top = k._camera("top", (0, 0, 200), (0, 0, 0), ortho_scale=max(w, h))
    scene.camera = top
    scene.render.filepath = prefix + "_top.png"
    bpy.ops.render.render(write_still=True)
    # Three-quarter view from the front right.
    scene.render.resolution_x = scene.render.resolution_y = int(os.environ.get("AU_3Q", "640"))
    eye = Vector((80, -140, 115))
    cam = k._camera("3q", eye, (-eye).to_track_quat("-Z", "Y").to_euler())
    cam.data.lens = 58
    scene.camera = cam
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)
    # As the store shows it: from above, the ship turned and banked a little.
    scene.render.resolution_x, scene.render.resolution_y = w * scale, h * scale
    cam = k._camera("store", (0, 0, 260), (0, 0, 0))
    cam.data.lens = 50
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_width = cam.data.sensor_height = (h * 1.3) / 260 * 50
    pivot = bpy.data.objects.new("pivot", None)
    scene.collection.objects.link(pivot)
    for o in meshes():
        o.parent = pivot
    pivot.rotation_euler = (math.radians(-8), math.radians(14), math.radians(12))
    scene.camera = cam
    scene.render.filepath = prefix + "_store.png"
    bpy.ops.render.render(write_still=True)
    pivot.rotation_euler = (0, 0, 0)


def check(pic, supersample=4):
    """The top view's coverage against the picture's (intersection over union)."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    w, h = pic.w, pic.h
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = k._camera("silhouette", (0, 0, 200), (0, 0, 0), ortho_scale=max(w, h))
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "au_ships_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    px = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    covered = px.reshape(h, supersample, w, supersample).mean(axis=(1, 3)) > 0.5
    mask = pic.alpha
    both = (covered & mask).sum()
    either = (covered | mask).sum()
    print("silhouette overlap: %.3f (model only %d, picture only %d)" %
          (both / max(either, 1), (covered & ~mask).sum(), (mask & ~covered).sum()))
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    return both / max(either, 1)


# --- Shared ----------------------------------------------------------------------------------------

def under_material():
    return mat("store_under", (44, 44, 48), metallic=0.3, roughness=0.6)


def mount_markers(number, pic):
    """Translucent plates on the deck where the store draws the guns and the generator (previews)."""
    sx, sy = SHIP_AT[number]
    cx, cy = sx + pic.w / 2, sy + pic.h / 2
    marker = mat("mount_marker", (60, 230, 90), metallic=0.0, roughness=0.8, alpha=0.3)
    for x, y, w, h in MOUNTS:
        k.box("mount", ((x + w / 2) - cx, cy - (y + h / 2), DECK + 0.05), (w, h, 0.1), marker)


def mount_sprites(number, pic, folder):
    """The store's pictures of a generator and two guns (weapon_<n>.png in folder) laid flat on
    the deck where the store draws them (previews)."""
    sx, sy = SHIP_AT[number]
    cx, cy = sx + pic.w / 2, sy + pic.h / 2
    for sprite, (x, y, w, h) in ((16, MOUNTS[0]), (0, MOUNTS[1]), (8, MOUNTS[3])):
        path = os.path.join(folder, f"weapon_{sprite}.png")
        if not os.path.exists(path):
            continue
        image = bpy.data.images.load(path)
        image.alpha_mode = "STRAIGHT"
        m = bpy.data.materials.new(f"sprite_{sprite}")
        m.use_nodes = True
        nodes = m.node_tree.nodes
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.interpolation = "Closest"
        bsdf = nodes["Principled BSDF"]
        m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        m.node_tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        bsdf.inputs["Roughness"].default_value = 0.6
        m.surface_render_method = "DITHERED"
        x0, y0 = x - cx, cy - y
        obj = k.mesh_object(f"sprite_{sprite}", [(x0, y0 - h, DECK + 0.05), (x0 + w, y0 - h, DECK + 0.05),
                                                 (x0 + w, y0, DECK + 0.05), (x0, y0, DECK + 0.05)], [(0, 1, 2, 3)], m)
        uv = obj.data.uv_layers.new()
        for loop, coord in zip(obj.data.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[loop.index].uv = coord


# ===================================================================================================
# store_ship_31: USP Talon (and SuperCarrot, USP Fang, U-Ship, Silver Ship, Nort Ship)
# ===================================================================================================

def dish(name, centre, rx, ry, depth, m, segments=32):
    """A shallow open bowl (its rim at centre's z, `depth` deep), elliptical: a dark hollow."""
    cx, cy, cz = centre
    rings = []
    for i in range(1, 7):
        t = i / 6
        r = math.sin(t * math.pi / 2)
        z = cz - depth * math.cos(t * math.pi / 2)
        rings.append([Vector((cx + rx * r * math.cos(2 * math.pi * j / segments),
                              cy + ry * r * math.sin(2 * math.pi * j / segments), z)) for j in range(segments)])
    obj = k.loft(name, rings, m, cap_start=True, cap_end=False, start_point=(cx, cy, cz - depth))
    return k.smooth(obj, 60)


def talon():
    """A gold arrowhead: a cone of a nose with a spine, the gun mount's two rails on the deck, the
    generator's bay (a grey frame, red cushions, the gem's column), wide wings with a thick rolled
    rim, panel lines and cooling ribs, two engine housings, two gold lobes and a tail ring."""
    pic = Picture(31)
    fw_points = [(0, 4), (12, 9), (26, 15), (40, 21), (50, 21.5), (60, 19.0), (80, 19.0), (94, 15.5), (104, 11),
                 (113, 7)]

    def shape(f):
        P, Q, D, dx, adx = f.P, f.Q, f.D, f.dx, f.adx
        # A cone of a nose running into a central body (the deck, from the gun mount to the
        # tail); to the sides wide wings, their edges a thick rolled rim falling round to a
        # thin edge.
        c = interp([(-2, 3.0), (0, 3.5), (6, 7.6), (14, 10.4), (22, 11.8), (30, 12.0), (100, 12.0),
                    (106, 10.6), (113, 6.0)], Q)
        fw = interp(fw_points, Q)
        nose = interp([(0, 3), (10, 5), (20, 9), (40, 13), (60, 12)], Q)
        body = 1.5 + (c - 1.5) * round_up((fw - adx) / 5.5) * round_up(D / nose)
        rim_h = interp([(30, 3.0), (50, 5.6), (70, 6.6), (95, 6.6), (113, 5.8)], Q)
        rim = 1.5 + (rim_h - 1.5) * round_up(D / 4.6)
        inner = rim_h - 1.1 + 2.0 * smoothstep(7.0, 26.0, D)
        wing = np.where(D < 4.6, rim, smax(rim_h - 0.2 * smoothstep(4.6, 6.0, D), inner, 1.2))
        Z = smax(body, wing, 2.0)
        wing_zone = smoothstep(fw + 0.5, fw + 2.5, adx)
        # Soft hollows under the panel lines (the lines themselves are seams), and the wings'
        # panels between them standing a little proud by turns.
        rear = smoothstep(42, 50, Q)
        Z = Z - rear * np.maximum(groove(np.abs(D - 6.0), 1.8, 0.3),
                                  wing_zone * groove(np.abs(D - 14.5), 1.6, 0.25))
        panel = wing_zone * smoothstep(6.4, 7.8, D) * (1 - smoothstep(13.2, 14.6, D)) * rear
        Z = Z + 0.4 * panel * (1 - smoothstep(69.0, 72.0, Q)) + 0.3 * panel * smoothstep(97.0, 100.0, Q)

        # The gun mount: a grey plate at the deck, a light strip between its rails.
        mount = f.rect(31.0, 28.4, 54.0, 50.2, 1.6)
        Z = smin(Z, DECK + 0.1 + 4 * smoothstep(0.0, 1.5, mount), 0.3)
        strip = f.rect(38.8, 28.5, 46.2, 50, 0.8)
        Z = Z + 0.25 * smoothstep(0.4, -0.4, strip) - 0.2 * smoothstep(0.4, -0.4, mount)

        # The generator's bay, just below the deck, its red cushions low either side.
        bay = f.rect(26, 51, 59, 92, 3)
        inbay = smoothstep(0.6, -0.6, bay)
        Z = Z * (1 - inbay) + (DECK - 0.3) * inbay
        cushion_shape = [(26.0, 61.0), (37.0, 61.0), (38.6, 66.0), (38.2, 79.0), (27.0, 79.0), (25.6, 70.0)]
        cushion = mirrored(f, cushion_shape)
        in_c = smoothstep(0.25, -0.25, cushion)
        Z = Z * (1 - in_c) + (DECK - 1.3 + 1.2 * round_up(-cushion / 3.0)) * in_c
        # A recess round the two lobes behind the bay.
        lobes = np.minimum(f.ellipse(35.5, 91.5, 7.4, 7.4), f.ellipse(50.5, 91.5, 7.4, 7.4))
        Z = smin(Z, DECK - 3.2 + 6 * smoothstep(-0.5, 2.0, lobes), 0.8)

        # The tail: a gentle hollow where the dark dish sits.
        hollow = f.ellipse(42.5, 103.5, 7.0, 6.0)
        Z = smin(Z, 8.6 + 2.6 * smoothstep(-1.5, 2.0, hollow) + 8 * smoothstep(2.0, 4.0, hollow), 1.0)
        return dict(Z=Z, mount=mount, strip=strip, bay=bay, cushion=cushion, lobes=lobes)

    gold = mat("talon_gold", (156, 124, 70), metallic=0.4, roughness=0.36)
    steel_mid = mat("talon_steel_mid", (112, 114, 114), metallic=0.45, roughness=0.36)
    gold_light = mat("talon_gold_light", (204, 180, 132), metallic=0.4, roughness=0.32)
    seam = mat("talon_seam", (58, 38, 16), metallic=0.2, roughness=0.6)
    steel = mat("talon_steel", (150, 152, 150), metallic=0.5, roughness=0.3)
    steel_dark = mat("talon_steel_dark", (82, 82, 86), metallic=0.45, roughness=0.4)
    crimson = mat("talon_red", (146, 52, 40), metallic=0.25, roughness=0.42)
    blue = mat("talon_blue", (40, 90, 240), metallic=0.1, roughness=0.2, glow=3.0, glow_rgb=(60, 120, 255))
    hollow_m = mat("talon_hollow", (30, 22, 12), metallic=0.2, roughness=0.6)

    def material(f, z):
        s = shape(f)
        m = np.zeros(np.shape(f.P), dtype=int)
        m[s["mount"] < 0] = 5
        m[s["strip"] < 0] = 1
        m[s["bay"] < 0] = 2
        m[s["cushion"] < 0] = 3
        m[s["lobes"] < 0.5] = 4
        return m

    def borders(f):
        s = shape(f)
        q = np.maximum(46.0 - f.Q, 0.0)  # the panels' edges, on the wings
        return [s["mount"], s["strip"], s["bay"], s["cushion"], s["lobes"] - 0.5, f.D - 7.1 + q, f.D - 13.9 + q]

    hull = Hull(pic, lambda f: shape(f)["Z"], material, [gold, gold_light, steel_dark, crimson, hollow_m, steel_mid],
                under_material(), bottom=lambda d, x, y: 1.2 - 3.0 * float(round_up(d / 6.0)), borders=borders)
    X, Y, zat = pic.X, pic.Y, hull.z_at

    # Panel lines: inside the rim, a second line further in, joints across the wings, the collar
    # at the gun mount and the bay's front edge.
    def fw_at(py):
        return interp(fw_points, py)
    for path in pic.offset_paths(6.0, lambda px, py: (py > 46) & (np.hypot((px - 42.5) / 9.0, (py - 103.5) / 8.0) > 1)):
        hull.seam("seam_rim", path, seam)
    for path in pic.offset_paths(14.5, lambda px, py: (py > 58) & (py < 104) & (np.abs(px - 42.5) > fw_at(py) + 1.5)):
        hull.seam("seam_inner", path, seam)
    for (ax, ay), (bx, by) in (((11.5, 72.5), (21.0, 69.2)), ((21.0, 99.5), (26.5, 93.8))):
        for mirror_ in (False, True):
            px0, px1 = (pic.w - ax, pic.w - bx) if mirror_ else (ax, bx)
            hull.seam("seam_joint", [(px0 + (px1 - px0) * t, ay + (by - ay) * t) for t in np.linspace(0, 1, 9)], seam)
    hull.seam("seam_collar", [(x, 27.6) for x in np.linspace(31.5, 53.5, 23)], seam)
    hull.seam("seam_bay", [(x, 50.5) for x in np.linspace(27.0, 58.0, 32)], seam)

    # The nose's spine.
    path = [(X(42.5), Y(py), zat(X(42.5), Y(py)) - 0.35) for py in np.arange(4.0, 26.6, 0.75)]
    tube("spine", path, [0.3] + [1.15] * (len(path) - 2) + [0.5], gold_light, segments=12, squash=0.75)
    # Gun mount rails (under the front gun).
    for xc in (35.0, 50.0):
        capsule("rail", (X(xc), Y(49.5), DECK - 1.0), (X(xc), Y(29.0), DECK - 1.0), 3.3, steel, squash=0.42)
        capsule("rail_band", (X(xc), Y(41.5), DECK - 0.95), (X(xc), Y(38.5), DECK - 0.95), 3.55, steel_dark,
                squash=0.42)
    # The bay's grey frame across its top, its column and the gem, the engine housings.
    frame = [(29.0, 52.5), (56.0, 52.5), (57.5, 56.0), (56.0, 63.0), (49.0, 63.0), (47.5, 60.5), (37.5, 60.5),
             (36.0, 63.0), (29.0, 63.0), (27.5, 56.0)]
    slab("bay_frame", [(X(px), Y(py)) for px, py in frame], DECK - 2.0, DECK + 0.4, steel, bevel=0.6)
    rbox("bay_column", (X(42.5), Y(76.0), DECK - 1.0), (8.6, 29.0, 2.2), steel, bevel=0.7)
    rbox("bay_column_slot", (X(42.5), Y(83.5), DECK + 0.1), (4.0, 7.0, 0.3), steel_dark, bevel=0.12)
    ellipsoid("gem", (X(42.5), Y(73.0), DECK - 0.5), (3.6, 2.8, 1.0), blue)
    for x0 in (24.5, 49.5):
        rbox("housing", (X(x0 + 5.5), Y(84.5), DECK - 1.5), (11.0, 12.0, 3.4), steel_dark, bevel=1.0)
        rbox("housing_vent", (X(x0 + 5.5), Y(86.0), DECK + 0.2), (7.0, 1.0, 0.4), steel, bevel=0.15)
        rbox("housing_vent", (X(x0 + 5.5), Y(83.0), DECK + 0.2), (7.0, 1.0, 0.4), steel, bevel=0.15)
    # Gold lobes behind the housings.
    for lx in (35.5, 50.5):
        ellipsoid("lobe", (X(lx), Y(91.5), DECK - 3.0), (6.3, 6.5, 3.4), gold, segments=28, rings=14)
    # Cooling ribs on the wings.
    for xr in (14.6, 16.9, 19.2, 21.5):
        for px_ in (xr, pic.w - xr):
            path = [(X(px_), Y(py), zat(X(px_), Y(py)) - 0.1) for py in np.arange(82.0, 96.5, 1.0)]
            tube("rib", path, [0.3] + [0.8] * (len(path) - 2) + [0.3], gold_light, segments=8, squash=0.8)
    # The tail: a stem down from the column into a dark dish with a ring in it.
    dish("tail_dish", (X(42.5), Y(103.5), 10.4), 6.6, 5.6, 2.0, hollow_m)
    capsule("stem", (X(42.5), Y(99.5), 9.0), (X(42.5), Y(89.0), DECK - 0.8), 1.7, gold, squash=0.8)
    torus("tail_ring", (X(42.5), Y(103.8), 8.9), 3.3, 1.25, gold, squash=0.9)
    ellipsoid("tail_core", (X(42.5), Y(103.8), 8.6), (1.4, 1.4, 0.8), steel_dark, segments=12, rings=6)
    return pic


# ===================================================================================================
# store_ship_32: the Stalkers (and Red Dragon, PeteZoomer, Rum Bottle)
# ===================================================================================================

def mirrored(f, points, axis=None):
    """A polygon and its mirror image across the ship's centre line (default the picture's): the
    nearer one's distance."""
    axis = f.pic.w / 2 if axis is None else axis
    return np.minimum(f.poly(points), Field(f.pic, 2 * axis - f.P, f.Q, distance=False).poly(points))


def stalker():
    """A grey helmet of a nose (the gun mount's rails either side of a tan strip, two brown eyes),
    a torso with the generator's bay, gold engine lobes, round shoulders and grilles, two long
    blades of wings swept forward, two grey pods and a glowing exhaust at the tail."""
    pic = Picture(32, sigma=1.4)
    cx = pic.w / 2
    body_shape = [(46.5, -0.5), (42.0, 5.5), (38.2, 12.5), (34.6, 19.5), (31.5, 27.0), (29.4, 34.0), (29.4, 66.0),
                  (28.2, 72.0), (28.0, 100.0), (33.0, 108.5), (60.0, 108.5), (65.0, 100.0), (64.8, 72.0),
                  (63.6, 66.0), (63.6, 34.0), (61.5, 27.0), (58.4, 19.5), (54.8, 12.5), (51.0, 5.5)]
    cushion_shape = [(30.6, 58.5), (40.0, 59.0), (41.6, 64.0), (40.6, 75.0), (35.0, 76.0), (31.0, 68.0)]
    eye_shape = [(37.6, 26.4), (42.2, 26.4), (42.4, 30.4), (37.4, 30.4)]

    def shape(f):
        P, Q, D, adx = f.P, f.Q, f.D, f.adx
        body = f.poly(body_shape)
        # The body: a pointed helmet and a torso, the deck along their middle; the wings low
        # plates with rounded edges.
        c = interp([(-2, 3.0), (0, 4.0), (8, 9.0), (16, 11.4), (24, 12.0), (94, 12.0), (100, 9.5), (106, 7.5),
                    (110, 6.0)], Q)
        reach = interp([(0, 4.0), (12, 7.0), (30, 9.0), (60, 8.0), (80, 6.0), (110, 4.0)], Q)
        hb = 2.0 + (c - 2.0) * round_up(-body / reach)
        wing = 1.5 + 3.4 * round_up(D / 2.6) + 0.6 * smoothstep(60, 100, Q - 0.6 * adx + 0.0)
        wing = wing + 0.7 * smoothstep(5.2, 6.4, D) * smoothstep(1.0, 2.5, body)  # a raised middle panel
        Z = smax(np.where(body < 0, hb, 2.0), wing, 1.0)
        # The nose: a light strip between the rails, two eyes recessed above them, two slots.
        strip = f.rect(43.2, 27.5, 49.8, 46.5, 0.8)
        Z = smin(Z, DECK + 0.1 + 4 * smoothstep(0.0, 1.5, strip), 0.3)
        Z = Z + 0.25 * smoothstep(0.4, -0.4, strip)
        eyes = mirrored(f, eye_shape)
        Z = Z - 0.9 * smoothstep(0.3, -0.5, eyes)
        slots = mirrored(f, [(38.0, 20.5), (41.5, 20.5), (41.5, 24.5), (38.0, 24.5)])
        Z = Z - 0.6 * smoothstep(0.3, -0.4, slots)
        # The generator's bay: a platform just below the deck, two red cushions.
        bay = f.rect(30.0, 51.0, 63.0, 96.0, 3)
        inbay = smoothstep(0.6, -0.6, bay)
        Z = Z * (1 - inbay) + (DECK - 0.3) * inbay
        cushion = mirrored(f, cushion_shape)
        in_c = smoothstep(0.25, -0.25, cushion)
        Z = Z * (1 - in_c) + (DECK - 1.3 + 1.2 * round_up(-cushion / 3.0)) * in_c
        # Recesses round the engine lobes and the pods.
        lobes = np.minimum(f.ellipse(38.5, 91.0, 7.6, 8.0), f.ellipse(54.5, 91.0, 7.6, 8.0))
        Z = smin(Z, DECK - 3.2 + 6 * smoothstep(-0.5, 2.0, lobes), 0.8)
        return dict(Z=Z, body=body, strip=strip, eyes=eyes, slots=slots, bay=bay, cushion=cushion, lobes=lobes)

    steel = mat("stalker_steel", (132, 134, 132), metallic=0.5, roughness=0.32)
    steel_light = mat("stalker_steel_light", (176, 178, 176), metallic=0.5, roughness=0.3)
    steel_dark = mat("stalker_steel_dark", (70, 70, 74), metallic=0.45, roughness=0.42)
    seam = mat("stalker_seam", (30, 30, 34), metallic=0.2, roughness=0.6)
    tan = mat("stalker_tan", (196, 168, 128), metallic=0.3, roughness=0.36)
    brown = mat("stalker_brown", (92, 60, 24), metallic=0.3, roughness=0.4)
    crimson = mat("stalker_red", (146, 52, 40), metallic=0.25, roughness=0.42)
    gold = mat("stalker_gold", (156, 122, 66), metallic=0.4, roughness=0.36)
    hollow_m = mat("stalker_hollow", (30, 28, 26), metallic=0.2, roughness=0.6)
    blue = mat("stalker_blue", (40, 90, 240), metallic=0.1, roughness=0.2, glow=3.0, glow_rgb=(60, 120, 255))
    exhaust = mat("stalker_exhaust", (230, 70, 30), metallic=0.0, roughness=0.4, glow=3.0, glow_rgb=(255, 80, 24))

    def material(f, z):
        s = shape(f)
        m = np.zeros(np.shape(f.P), dtype=int)
        m[s["strip"] < 0] = 1
        m[(s["eyes"] < 0) | (s["slots"] < 0)] = 2
        m[s["bay"] < 0] = 3
        m[s["cushion"] < 0] = 4
        m[s["lobes"] < 0.5] = 5
        return m

    def borders(f):
        s = shape(f)
        return [s["body"], s["strip"], s["eyes"], s["slots"], s["bay"], s["cushion"], s["lobes"] - 0.5, f.D - 5.8]

    hull = Hull(pic, lambda f: shape(f)["Z"], material, [steel, tan, brown, steel_dark, crimson, hollow_m],
                under_material(), bottom=lambda d, x, y: 1.0 - 2.6 * float(round_up(d / 5.0)), borders=borders)
    X, Y, zat = pic.X, pic.Y, hull.z_at

    # Panel lines: the helmet's, the wings' along their length and across them.
    body_line = lambda px, py: Field(pic, px, py, distance=False).poly(body_shape)
    for path in pic.offset_paths(3.6, lambda px, py: body_line(px, py) > 1.5):
        hull.seam("seam_wing", path, seam)
    for (ax, ay), (bx, by) in (((4.2, 56.5), (10.5, 50.5)), ((13.0, 79.5), (20.5, 72.0)), ((19.5, 94.0), (27.0, 86.0))):
        for mirror_ in (False, True):
            px0, px1 = (pic.w - ax, pic.w - bx) if mirror_ else (ax, bx)
            hull.seam("seam_joint", [(px0, ay), (px1, by)], seam)
    for path in pic.offset_paths(4.5, lambda px, py: (py > 8) & (py < 50) & (body_line(px, py) < 0)):
        hull.seam("seam_helmet", path, seam)
    hull.seam("seam_brow", [(x, 25.2) for x in np.linspace(36.0, 57.0, 22)], seam)
    hull.seam("seam_chin", [(x, 49.0) for x in np.linspace(31.0, 62.0, 32)], seam)

    # The nose's spine and the gun mount's rails (under the front gun).
    path = [(X(cx), Y(py), zat(X(cx), Y(py)) - 0.35) for py in np.arange(3.0, 20.0, 0.75)]
    tube("spine", path, [0.3] + [1.0] * (len(path) - 2) + [0.4], steel_light, segments=12, squash=0.75)
    for xc in (39.6, 53.4):
        capsule("rail", (X(xc), Y(47.0), DECK - 0.75), (X(xc), Y(31.0), DECK - 0.75), 2.3, steel_light, squash=0.5)
        capsule("rail_band", (X(xc), Y(41.0), DECK - 0.7), (X(xc), Y(38.5), DECK - 0.7), 2.5, steel_dark, squash=0.5)
    # The chin plate, the bay's column with the gem.
    rbox("chin", (X(cx), Y(52.5), DECK - 0.6), (17.0, 6.0, 2.0), steel_light, bevel=0.6)
    rbox("bay_column", (X(cx), Y(78.0), DECK - 1.0), (8.6, 34.0, 2.2), steel, bevel=0.7)
    rbox("bay_column_slot", (X(cx), Y(86.0), DECK + 0.1), (4.0, 7.0, 0.3), steel_dark, bevel=0.12)
    ellipsoid("gem", (X(cx), Y(71.0), DECK - 0.5), (3.6, 2.8, 1.0), blue)
    # Gold lobes: two small above two big ones.
    for lx in (39.5, 53.5):
        ellipsoid("lobe_small", (X(lx), Y(79.0), DECK - 1.8), (4.2, 4.4, 2.2), gold, segments=20, rings=10)
    for lx in (38.5, 54.5):
        ellipsoid("lobe", (X(lx), Y(91.0), DECK - 3.0), (6.6, 7.0, 3.4), gold, segments=28, rings=14)
    # Shoulders where the wings join: round joints with a ring; grilles below them.
    for sx in (24.8, pic.w - 24.8):
        z0 = zat(X(sx), Y(74.5))
        lathe("shoulder", [(z0 - 3.0, 6.4), (z0 + 1.6, 6.4), (z0 + 2.6, 5.4), (z0 + 2.9, 2.0), (z0 + 2.9, 0.01)], steel,
              axis="z", at=(X(sx), Y(74.5)), segments=28, angle=40)
        torus("shoulder_ring", (X(sx), Y(74.5), z0 + 2.7), 3.6, 0.55, steel_dark, segments=24, sides=8)
    for gx in (31.5, pic.w - 31.5):
        z0 = zat(X(gx), Y(87.0))
        rbox("grille", (X(gx), Y(87.0), z0 - 0.4), (9.0, 10.0, 1.6), steel_dark, bevel=0.5)
        for gy in np.arange(83.5, 91.0, 1.75):
            rbox("grille_bar", (X(gx), Y(gy), z0 + 0.45), (8.0, 0.7, 0.5), steel, bevel=0.2)
    # Two grey pods at the tail and the exhaust between them.
    for px_ in (35.0, pic.w - 35.0):
        ellipsoid("pod", (X(px_), Y(102.0), 8.0), (5.0, 5.2, 4.2), steel, segments=24, rings=12)
    capsule("exhaust", (X(37.5), Y(107.4), 5.6), (X(55.5), Y(107.4), 5.6), 1.9, exhaust, squash=0.9)
    return pic


# ===================================================================================================
# store_ship_27: Gencore Phoenix (and Gencore Maelstrom)
# ===================================================================================================

def phoenix():
    """A grey bullet of a nose (the gun mount's rails, a tan strip, two tall brown vents), a neck
    with the generator's bay, a torso of gold engine lobes, and on arms either side two long pods,
    their fronts tan blades, red spheres on their inner sides."""
    pic = Picture(27, sigma=1.4)
    cx = pic.w / 2
    body_shape = [(46.5, -0.5), (42.0, 4.5), (37.6, 11.0), (34.6, 17.5), (32.6, 24.0), (31.0, 31.0), (30.6, 38.0),
                  (30.6, 58.0), (32.0, 62.0), (33.2, 68.0), (36.5, 72.0), (39.6, 74.0), (39.6, 75.5),
                  (33.0, 77.5), (28.5, 80.5), (28.5, 93.0), (32.5, 97.0), (33.5, 103.5), (59.5, 103.5),
                  (60.5, 97.0), (64.5, 93.0), (64.5, 80.5), (60.0, 77.5), (53.4, 75.5), (53.4, 74.0), (56.5, 72.0),
                  (59.8, 68.0), (61.0, 62.0), (62.4, 58.0), (62.4, 38.0), (62.0, 31.0), (60.4, 24.0), (58.4, 17.5),
                  (55.4, 11.0), (51.0, 4.5)]
    cushion_shape = [(32.6, 61.0), (40.6, 61.0), (41.4, 64.0), (40.8, 72.0), (37.2, 71.6), (33.6, 67.6)]
    vent_shape = [(36.2, 20.8), (41.2, 20.8), (41.4, 31.2), (36.6, 31.2)]

    def shape(f):
        P, Q, D, adx = f.P, f.Q, f.D, f.adx
        body = f.poly(body_shape)
        # The body: a bullet nose and a torso, the deck along their middle.
        c = interp([(-2, 3.0), (0, 4.0), (8, 9.0), (16, 11.5), (24, 12.0), (96, 12.0), (101, 10.0), (104, 8.0)], Q)
        reach = interp([(0, 4.0), (12, 8.0), (30, 11.0), (58, 10.0), (70, 6.0), (80, 7.0), (104, 5.0)], Q)
        hb = 2.0 + (c - 2.0) * round_up(-body / reach)
        # The pods: round, their fronts thin blades; the arms between, lower.
        pod_zone = smoothstep(22.0, 24.5, adx)
        pod_top = interp([(28, 2.5), (40, 4.2), (56, 5.6), (64, 9.0), (98, 9.5), (106, 8.0)], Q)
        arm_top = 7.2
        side_top = arm_top + (pod_top - arm_top) * pod_zone
        side = 1.5 + (side_top - 1.5) * round_up(D / np.where(pod_zone > 0.5, 6.0, 3.5))
        Z = smax(np.where(body < 0, hb, 2.0), side, 1.2)
        # The nose: a light strip between the rails, two tall vents either side.
        strip = f.rect(43.4, 31.0, 49.6, 50.5, 0.8)
        Z = smin(Z, DECK + 0.1 + 4 * smoothstep(0.0, 1.5, strip), 0.3)
        Z = Z + 0.25 * smoothstep(0.4, -0.4, strip)
        vents = mirrored(f, vent_shape)
        Z = Z - 1.0 * smoothstep(0.3, -0.6, vents)
        # The generator's bay in the neck: a platform just below the deck, two red cushions.
        bay = f.rect(30.0, 52.0, 63.0, 80.0, 3)
        inbay = smoothstep(0.6, -0.6, bay) * smoothstep(-0.5, 1.5, body * -1)
        Z = Z * (1 - inbay) + (DECK - 0.3) * inbay
        cushion = mirrored(f, cushion_shape)
        in_c = smoothstep(0.25, -0.25, cushion)
        Z = Z * (1 - in_c) + (DECK - 1.3 + 1.2 * round_up(-cushion / 2.6)) * in_c
        # Recesses round the engine lobes.
        lobes = np.minimum(f.ellipse(39.5, 92.5, 7.6, 8.0), f.ellipse(53.5, 92.5, 7.6, 8.0))
        Z = smin(Z, DECK - 3.2 + 6 * smoothstep(-0.5, 2.0, lobes), 0.8)
        # The pods' tan patches.
        patch = mirrored(f, [(7.2, 77.0), (11.8, 77.0), (12.4, 82.0), (11.8, 87.0), (7.2, 87.0), (6.6, 82.0)])
        Z = Z + 0.5 * smoothstep(0.4, -0.6, patch)
        blade = np.maximum(Q - interp([(0, 57.0), (10, 59.0), (24, 60.0)], adx - 23.0) - 0.0 * adx, 23.0 - adx)
        return dict(Z=Z, body=body, strip=strip, vents=vents, bay=np.maximum(bay, body), cushion=cushion,
                    lobes=lobes, patch=patch, blade=blade)

    steel = mat("phoenix_steel", (132, 134, 132), metallic=0.5, roughness=0.32)
    steel_light = mat("phoenix_steel_light", (176, 178, 176), metallic=0.5, roughness=0.3)
    steel_dark = mat("phoenix_steel_dark", (70, 70, 74), metallic=0.45, roughness=0.42)
    seam = mat("phoenix_seam", (30, 30, 34), metallic=0.2, roughness=0.6)
    tan = mat("phoenix_tan", (186, 156, 108), metallic=0.35, roughness=0.36)
    brown = mat("phoenix_brown", (100, 70, 32), metallic=0.3, roughness=0.4)
    crimson = mat("phoenix_red", (150, 54, 42), metallic=0.3, roughness=0.36)
    gold = mat("phoenix_gold", (156, 122, 66), metallic=0.4, roughness=0.36)
    hollow_m = mat("phoenix_hollow", (30, 28, 26), metallic=0.2, roughness=0.6)
    blue = mat("phoenix_blue", (40, 90, 240), metallic=0.1, roughness=0.2, glow=3.0, glow_rgb=(60, 120, 255))

    def material(f, z):
        s = shape(f)
        m = np.zeros(np.shape(f.P), dtype=int)
        m[(s["strip"] < 0) | (s["patch"] < 0) | (s["blade"] < 0)] = 1
        m[s["vents"] < 0] = 2
        m[s["bay"] < 0] = 3
        m[s["cushion"] < 0] = 4
        m[s["lobes"] < 0.5] = 5
        return m

    def borders(f):
        s = shape(f)
        return [s["body"], s["strip"], s["vents"], s["bay"], s["cushion"], s["lobes"] - 0.5, s["patch"], s["blade"]]

    hull = Hull(pic, lambda f: shape(f)["Z"], material, [steel, tan, brown, steel_dark, crimson, hollow_m],
                under_material(), bottom=lambda d, x, y: 1.0 - 2.6 * float(round_up(d / 5.0)), borders=borders)
    X, Y, zat = pic.X, pic.Y, hull.z_at

    # Panel lines: the nose's, along the pods and across them.
    body_line = lambda px, py: Field(pic, px, py, distance=False).poly(body_shape)
    for path in pic.offset_paths(4.5, lambda px, py: (py > 8) & (py < 52) & (body_line(px, py) < 0)):
        hull.seam("seam_nose", path, seam)
    for path in pic.offset_paths(3.0, lambda px, py: (np.abs(px - cx) > 24.5) & (py > 60) & (py < 102)):
        hull.seam("seam_pod", path, seam)
    for py_ in (60.0, 72.0, 90.0):
        for x0, x1 in ((2.0, 22.0), (pic.w - 22.0, pic.w - 2.0)):
            hull.seam("seam_pod_ring", [(x, py_) for x in np.linspace(x0, x1, 21)], seam)
    hull.seam("seam_brow", [(x, 18.8) for x in np.linspace(35.5, 57.5, 23)], seam)
    hull.seam("seam_chin", [(x, 50.8) for x in np.linspace(31.0, 62.0, 32)], seam)

    # The nose's spine and the gun mount's rails (under the front gun).
    path = [(X(cx), Y(py), zat(X(cx), Y(py)) - 0.35) for py in np.arange(3.0, 18.0, 0.75)]
    tube("spine", path, [0.3] + [1.0] * (len(path) - 2) + [0.4], steel_light, segments=12, squash=0.75)
    for xc in (39.4, 53.6):
        capsule("rail", (X(xc), Y(49.0), DECK - 0.75), (X(xc), Y(33.0), DECK - 0.75), 2.3, steel_light, squash=0.5)
        capsule("rail_band", (X(xc), Y(42.5), DECK - 0.7), (X(xc), Y(40.0), DECK - 0.7), 2.5, steel_dark, squash=0.5)
    # The chin plate, the bay's column with the gem.
    rbox("chin", (X(cx), Y(54.5), DECK - 0.6), (19.0, 6.5, 2.0), steel_light, bevel=0.6)
    rbox("bay_column", (X(cx), Y(76.0), DECK - 1.0), (8.6, 30.0, 2.2), steel, bevel=0.7)
    ellipsoid("gem", (X(cx), Y(73.5), DECK - 0.5), (3.6, 2.8, 1.0), blue)
    # Gold lobes: two small above two big ones.
    for lx in (39.5, 53.5):
        ellipsoid("lobe_small", (X(lx), Y(80.5), DECK - 1.8), (4.6, 4.4, 2.2), gold, segments=20, rings=10)
        ellipsoid("lobe", (X(lx), Y(92.5), DECK - 3.0), (6.6, 7.0, 3.4), gold, segments=28, rings=14)
    # The arms' struts and joints, the pods' red spheres.
    for side in (1, -1):
        def sx(px):
            return px if side == 1 else pic.w - px
        capsule("arm", (X(sx(17.0)), Y(87.0), 6.6), (X(sx(33.0)), Y(87.0), 7.4), 2.2, steel_light, squash=0.8)
        lathe("arm_joint", [(4.0, 3.4), (8.2, 3.4), (8.8, 2.6), (9.0, 0.01)], steel, axis="z",
              at=(X(sx(25.0)), Y(87.0)), segments=20, angle=35)
        torus("arm_joint_ring", (X(sx(25.0)), Y(87.0), 8.5), 2.0, 0.4, steel_dark, segments=16, sides=6)
        ellipsoid("pod_ball", (X(sx(18.5)), Y(80.0), 8.0), (4.4, 4.6, 3.6), crimson, segments=20, rings=10)
        ellipsoid("pod_ball", (X(sx(18.5)), Y(99.5), 8.0), (4.0, 4.2, 3.4), crimson, segments=20, rings=10)
    return pic


# ===================================================================================================
# store_ship_44: Storm
# ===================================================================================================

def storm():
    """A dark stealth flying wing: a narrow neck with a glassy sensor dome at its tip and a blue band,
    a long bay down the middle for the generator and the guns, dark blue panels inset in the
    wings with blue lamps on struts, a blue-glowing exhaust and tail fins."""
    pic = Picture(44, sigma=1.4)
    cx = pic.w / 2
    panel_shape = [(31.0, 58.0), (31.0, 94.0), (20.0, 94.5), (10.0, 88.0), (7.0, 81.0), (12.5, 71.0), (22.0, 62.5)]

    def shape(f):
        P, Q, D, adx = f.P, f.Q, f.D, f.adx
        c = interp([(-2, 3.0), (0, 4.0), (6, 8.8), (14, 11.4), (20, 12.0), (97, 12.0), (101, 10.5), (106, 7.5),
                    (110, 5.0)], Q)
        fw = interp([(0, 4.0), (20, 9.0), (38, 9.5), (52, 11.5), (96, 11.5), (104, 8.0), (110, 4.0)], Q)
        reach = interp([(0, 4.0), (16, 7.5), (38, 8.5), (60, 9.0), (110, 4.0)], Q)
        body = 1.5 + (c - 1.5) * round_up((fw - adx) / 6.0) * round_up(D / reach)
        wing = 1.4 + 4.2 * round_up(D / 11.0) + 0.8 * smoothstep(30.0, 12.0, adx)
        Z = smax(body, wing, 2.5)
        # The bay down the middle: two long doors on its floor.
        bay = f.rect(33.6, 57.0, 50.4, 97.0, 1.2)
        inbay = smoothstep(0.4, -0.4, bay)
        doors = np.minimum(f.rect(34.8, 58.4, 41.4, 95.6, 0.6), f.rect(42.6, 58.4, 49.2, 95.6, 0.6))
        floor = DECK - 0.6 + 0.35 * smoothstep(0.3, -0.3, doors)
        Z = Z * (1 - inbay) + floor * inbay
        # The wings' inset panels.
        panels = mirrored(f, panel_shape)
        Z = Z - 0.4 * smoothstep(0.3, -0.3, panels)
        # The exhaust's recess.
        nozzle = f.rect(33.0, 96.4, 51.0, 101.0, 1.2)
        Z = Z - 1.2 * smoothstep(0.4, -0.6, nozzle)
        return dict(Z=Z, bay=bay, doors=doors, panels=panels, nozzle=nozzle)

    hull_m = mat("storm_hull", (44, 46, 50), metallic=0.55, roughness=0.3)
    panel_m = mat("storm_panel", (24, 38, 54), metallic=0.45, roughness=0.34)
    bay_m = mat("storm_bay", (70, 72, 74), metallic=0.5, roughness=0.34)
    door_m = mat("storm_door", (96, 98, 100), metallic=0.5, roughness=0.32)
    dark = mat("storm_dark", (16, 16, 18), metallic=0.3, roughness=0.5)
    line_m = mat("storm_line", (110, 114, 120), metallic=0.5, roughness=0.3)
    seam = mat("storm_seam", (84, 92, 104), metallic=0.5, roughness=0.35)
    glass = mat("storm_glass", (70, 76, 86), metallic=0.7, roughness=0.12)
    glow = mat("storm_glow", (40, 100, 255), metallic=0.0, roughness=0.3, glow=3.5, glow_rgb=(50, 110, 255))

    def material(f, z):
        s = shape(f)
        m = np.zeros(np.shape(f.P), dtype=int)
        m[s["panels"] < 0] = 1
        m[s["bay"] < 0] = 2
        m[s["doors"] < 0] = 3
        m[s["nozzle"] < 0] = 4
        return m

    def borders(f):
        s = shape(f)
        return [s["bay"], s["doors"], s["panels"], s["nozzle"]]

    hull = Hull(pic, lambda f: shape(f)["Z"], material, [hull_m, panel_m, bay_m, door_m, dark],
                under_material(), bottom=lambda d, x, y: 1.0 - 2.4 * float(round_up(d / 6.0)), borders=borders)
    X, Y, zat = pic.X, pic.Y, hull.z_at

    # Panel lines along the wings' edges, down the body's sides and round the inset panels.
    for path in pic.offset_paths(4.0, lambda px, py: (py > 44) & (np.abs(px - cx) > 13)):
        hull.seam("seam_edge", path, seam)
    for side in (1, -1):
        def sx(px):
            return px if side == 1 else pic.w - px
        hull.seam("seam_root", [(sx(31.6), py) for py in np.linspace(46.0, 96.0, 51)], seam)
        ring = panel_shape[1:] + panel_shape[:1]  # from the panel's bottom corner round to its top
        hull.seam("seam_panel", [(sx(px), py) for px, py in ring], seam, radius=0.3)
    # The light spine down the neck, the blue bands across it and over the bay.
    path = [(X(cx), Y(py), zat(X(cx), Y(py)) - 0.3) for py in np.arange(18.0, 57.0, 0.75)]
    tube("spine", path, [0.3] + [0.9] * (len(path) - 2) + [0.3], line_m, segments=10, squash=0.6)
    hull.seam("band", [(x, 33.6) for x in np.linspace(34.0, 50.0, 33)], glow, radius=0.5, sink=0.15)
    hull.seam("band", [(x, 57.6) for x in np.linspace(34.5, 49.5, 31)], glow, radius=0.4, sink=0.1)
    # The sensor dome at the tip.
    ellipsoid("dome", (X(cx), Y(11.0), DECK - 2.0), (4.0, 7.0, 2.3), glass, segments=24, rings=12)
    # Lamps on struts in the wings.
    for side in (1, -1):
        def sx(px):
            return px if side == 1 else pic.w - px
        z0 = zat(X(sx(16.6)), Y(81.0))
        capsule("lamp", (X(sx(16.6)), Y(85.5), z0 + 0.1), (X(sx(16.6)), Y(76.5), z0 + 0.1), 1.6, glow, squash=0.8)
        rbox("lamp_frame", (X(sx(16.6)), Y(81.0), z0 - 0.2), (4.4, 12.0, 1.2), line_m, bevel=0.4)
        path = [(X(sx(px)), Y(82.0), zat(X(sx(px)), Y(82.0)) + 0.1) for px in np.arange(18.5, 33.6, 1.0)]
        tube("strut", path, 0.55, line_m, segments=8)
    # The exhaust's glow and the tail fins.
    rbox("exhaust", (X(cx), Y(98.8), zat(X(cx), Y(98.8)) - 0.6), (16.0, 3.4, 1.4), glow, bevel=0.6)
    for fx in (36.0, 39.6, 44.4, 48.0):
        z0 = zat(X(fx), Y(104.0))
        fin = [(X(fx) - 0.5, Y(108.0)), (X(fx) + 0.5, Y(108.0)), (X(fx) + 0.5, Y(100.6)), (X(fx) - 0.5, Y(100.6))]
        slab("fin", fin, z0 - 1.0, z0 + 1.6, dark, bevel=0.2)
    return pic


# ===================================================================================================
# store_ship_45: Gencore II
# ===================================================================================================

def gencore2():
    """A round cockpit head (a grey frame round a big dark canopy), two blue lamps on the neck, a
    round fuselage, two engine nacelles with blue exhausts, wings swept back with inset panels
    outlined in blue and blue lamps."""
    pic = Picture(45, sigma=1.4)
    cx = 48.0  # the ship is drawn on pixels 2..93: its middle is half a pixel right of the picture's
    body_shape = [(48.0, -0.5), (44.0, 3.0), (40.0, 8.0), (37.1, 14.0), (35.9, 21.0), (36.1, 28.0), (38.1, 34.0),
                  (37.9, 50.0), (35.9, 55.0), (35.9, 98.0), (37.5, 104.0), (41.5, 107.5), (54.5, 107.5),
                  (58.5, 104.0), (60.1, 98.0), (60.1, 55.0), (58.1, 50.0), (57.9, 34.0), (59.9, 28.0), (60.1, 21.0),
                  (58.9, 14.0), (56.0, 8.0), (52.0, 3.0)]
    panel_shape = [(12.9, 52.0), (22.5, 52.0), (22.5, 69.0), (14.5, 69.0), (12.9, 66.0)]

    def shape(f):
        P, Q, D, adx = f.P, f.Q, f.D, f.adx
        body = f.poly(body_shape)
        c = interp([(-2, 3.0), (0, 4.0), (6, 9.0), (14, 11.0), (34, 11.0), (38, 12.0), (98, 12.0), (103, 10.0),
                    (108, 6.0)], Q)
        reach = interp([(0, 4.0), (12, 9.0), (34, 10.0), (50, 8.0), (60, 10.0), (98, 10.0), (108, 5.0)], Q)
        hb = 2.0 + (c - 2.0) * round_up(-body / reach)
        wing = 1.4 + 2.8 * round_up(D / 2.4) + 0.5 * smoothstep(40.0, 70.0, Q)
        Z = smax(np.where(body < 0, hb, 2.0), wing, 1.0)
        # The cockpit: a hollow in the head's frame for the canopy.
        canopy = f.ellipse(cx, 20.0, 8.6, 11.6)
        Z = smin(Z, 8.6 + 6 * smoothstep(-0.6, 1.4, canopy), 0.6)
        # The wings' inset panels.
        panels = mirrored(f, panel_shape, cx)
        Z = Z - 0.4 * smoothstep(0.3, -0.3, panels)
        # Rings round the fuselage.
        rings = np.minimum(np.abs(Q - 60.5), np.abs(Q - 82.5)) + 99 * (body > 0) + 99 * (Q < 40)
        Z = Z - groove(rings, 0.9, 0.35)
        return dict(Z=Z, body=body, canopy=canopy, panels=panels)

    steel = mat("gencore2_steel", (128, 130, 132), metallic=0.55, roughness=0.3)
    steel_light = mat("gencore2_steel_light", (172, 176, 178), metallic=0.55, roughness=0.28)
    steel_dark = mat("gencore2_steel_dark", (62, 64, 68), metallic=0.45, roughness=0.4)
    wing_m = mat("gencore2_wing", (78, 80, 84), metallic=0.5, roughness=0.34)
    panel_m = mat("gencore2_panel", (28, 40, 56), metallic=0.45, roughness=0.34)
    seam = mat("gencore2_seam", (22, 22, 26), metallic=0.2, roughness=0.6)
    glass = mat("gencore2_glass", (14, 18, 30), metallic=0.6, roughness=0.08)
    glow = mat("gencore2_glow", (40, 100, 255), metallic=0.0, roughness=0.3, glow=3.5, glow_rgb=(50, 110, 255))

    def material(f, z):
        s = shape(f)
        m = np.zeros(np.shape(f.P), dtype=int)
        m[s["body"] > 0] = 1
        m[s["panels"] < 0] = 2
        m[s["canopy"] < 0] = 3
        return m

    def borders(f):
        s = shape(f)
        return [s["body"], s["canopy"], s["panels"]]

    hull = Hull(pic, lambda f: shape(f)["Z"], material, [steel, wing_m, panel_m, steel_dark],
                under_material(), bottom=lambda d, x, y: 1.0 - 2.4 * float(round_up(d / 5.0)), borders=borders)
    X, Y, zat = pic.X, pic.Y, hull.z_at

    # The canopy: dark glass in the head's frame, the frame's light rim round it.
    ellipsoid("canopy", (X(cx), Y(20.0), 9.4), (8.0, 11.0, 2.6), glass, segments=32, rings=16)
    path = []
    for i in range(41):
        a = 2 * math.pi * i / 40
        px, py = cx + 9.2 * math.cos(a), 20.0 + 12.2 * math.sin(a)
        path.append((X(px), Y(py), zat(X(px), Y(py)) - 0.15))
    tube("canopy_rim", path, 0.55, steel_light, segments=8, squash=0.7)
    # The fuselage's light ridge and the rings' seams; panel lines on the wings.
    rpath = [(X(cx), Y(py), zat(X(cx), Y(py)) - 0.3) for py in np.arange(36.0, 101.0, 0.8)]
    tube("ridge", rpath, [0.3] + [0.85] * (len(rpath) - 2) + [0.3], steel_light, segments=10, squash=0.6)
    for path in pic.offset_paths(3.4, lambda px, py: (np.abs(px - cx) > 13.5) & (py > 28) & (py < 82)):
        hull.seam("seam_wing", path, seam)
    # The panels' blue outlines, the wing lamps, the neck lamps.
    for side in (1, -1):
        def sx(px):
            return px if side == 1 else 2 * cx - px
        outline = [(sx(px), py) for px, py in panel_shape] + [(sx(panel_shape[0][0]), panel_shape[0][1])]
        dense = []
        for (ax, ay), (bx, by) in zip(outline, outline[1:]):
            n = max(2, int(math.hypot(bx - ax, by - ay) / 0.5))
            dense += [(ax + (bx - ax) * t, ay + (by - ay) * t) for t in np.linspace(0, 1, n, endpoint=False)]
        dense.append(outline[-1])
        hull.seam("panel_glow", dense, glow, radius=0.42, sink=0.12)
        z0 = zat(X(sx(9.0)), Y(52.0))
        capsule("wing_lamp", (X(sx(9.0)), Y(57.5), z0 + 0.1), (X(sx(9.0)), Y(46.5), z0 + 0.1), 1.6, glow, squash=0.7)
        z0 = zat(X(sx(39.6)), Y(42.0))
        capsule("neck_lamp", (X(sx(39.6)), Y(48.0), z0 - 0.3), (X(sx(39.6)), Y(36.5), z0 - 0.3), 1.5, glow, squash=0.8)
        ellipsoid("side_lamp", (X(sx(18.6)), Y(86.0), 4.6), (2.0, 3.6, 1.6), glow, segments=16, rings=8)
    # The engine nacelles: intakes at the front, blue exhausts at the back.
    for nx in (28.0, 2 * cx - 28.0):
        lathe("nacelle", [(Y(100.5), 3.8), (Y(99.0), 5.0), (Y(95.0), 5.6), (Y(62.0), 5.8), (Y(57.0), 5.6),
                          (Y(55.0), 4.8), (Y(54.6), 0.01)][::-1], steel, axis="y", at=(X(nx), 6.0), segments=28,
              squash=0.95, angle=40)
        lathe("intake", [(Y(56.2), 0.01), (Y(56.0), 3.8), (Y(54.4), 3.8)], steel_dark, axis="y", at=(X(nx), 6.3),
              segments=24)
        lathe("exhaust", [(Y(101.6), 0.01), (Y(101.4), 3.4), (Y(99.6), 3.6)], glow, axis="y", at=(X(nx), 6.0),
              segments=24)
        for ry in (64.0, 78.0, 92.0):
            lathe("nacelle_ring", [(Y(ry + 0.7), 5.85), (Y(ry - 0.7), 5.85)], steel_dark, axis="y",
                  at=(X(nx), 6.0), segments=28, squash=0.95)
    return pic


SHIPS = {
    31: talon,
    32: stalker,
    27: phoenix,
    44: storm,
    45: gencore2,
}


def main():
    options = k.args()
    only = {int(v) for v in options["only"].split(",")} if "only" in options else None
    for number, build in SHIPS.items():
        if only and number not in only:
            continue
        k.reset()
        pic = build()
        low, high = bounds()
        print(f"== store_ship_{number}: {triangles()} triangles, bounds {tuple(round(v, 2) for v in low)} .. "
              f"{tuple(round(v, 2) for v in high)}")
        if "stats" in options:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            counts = {}
            for obj in meshes():
                mesh = obj.evaluated_get(depsgraph).to_mesh()
                key = obj.name.split(".")[0]
                counts[key] = counts.get(key, 0) + sum(len(q.vertices) - 2 for q in mesh.polygons)
            print("   ", sorted(counts.items(), key=lambda kv: -kv[1]))
        if "check" in options:
            check(pic)
        k.export(os.path.join(OUT, f"store_ship_{number}.glb"))
        if "preview" in options:
            if "mounts" in options:
                mount_markers(number, pic)
            if "sprites" in options:
                mount_sprites(number, pic, options["sprites"])
            preview(options["preview"] + str(number), pic)


main()
