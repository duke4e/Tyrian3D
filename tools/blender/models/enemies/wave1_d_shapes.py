"""Shapes first made for the batch D models (wave1_d.py, whose models are all polish_*.py's now), kept for the kits
and scripts built on them: outlines traced from a sprite's pixels, parts inflated from them (rounded like tubes or
pillows, so curved outlines get real volume), and cutting a large model into the pieces the game draws as separate
sprites.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up. Pixel art is
given as rows of characters (row 0 at the top); pixel (column c, row r) covers x = c - ox .. c + 1 - ox
and y = oy - r - 1 .. oy - r, where (ox, oy) is the art's origin (the sprite's centre: 12, 14 for
a 2x2 sprite).
"""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, geometry

import tyrkit as k


def art(text):
    """Pixel art as rows (blank lines around it dropped)."""
    return [line for line in text.strip("\n").split("\n")]


# --- Outlines ----------------------------------------------------------------------------------

def _pixel_loops(covered, width, height):
    """Boundary loops of the covered pixels, as lists of pixel corners (image coordinates, rows
    down), clockwise round the covered pixels; outer outlines and holes alike."""
    edges = {}
    for r in range(height):
        for c in range(width):
            if not covered(c, r):
                continue
            if not covered(c, r - 1):
                edges.setdefault((c, r), []).append((c + 1, r))
            if not covered(c + 1, r):
                edges.setdefault((c + 1, r), []).append((c + 1, r + 1))
            if not covered(c, r + 1):
                edges.setdefault((c + 1, r + 1), []).append((c, r + 1))
            if not covered(c - 1, r):
                edges.setdefault((c, r + 1), []).append((c, r))
    loops = []
    while edges:
        start = next(iter(edges))
        loop, point = [start], start
        while True:
            nexts = edges.get(point)
            if not nexts:
                break
            nxt = nexts.pop()
            if not nexts:
                del edges[point]
            if nxt == start:
                break
            loop.append(nxt)
            point = nxt
        if len(loop) >= 4:
            loops.append(loop)
    return loops


def _simplify_closed(points, epsilon):
    """Douglas-Peucker on a closed polygon (split at the two points farthest apart)."""
    if len(points) < 5 or epsilon <= 0:
        return points

    def dp(pts):
        if len(pts) < 3:
            return pts
        (ax, ay), (bx, by) = pts[0], pts[-1]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        worst, at = -1.0, 0
        for i in range(1, len(pts) - 1):
            px, py = pts[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / length if length > 1e-9 else math.hypot(px - ax, py - ay)
            if d > worst:
                worst, at = d, i
        if worst <= epsilon:
            return [pts[0], pts[-1]]
        return dp(pts[:at + 1])[:-1] + dp(pts[at:])

    far = max(range(len(points)), key=lambda i: (points[i][0] - points[0][0]) ** 2 + (points[i][1] - points[0][1]) ** 2)
    first, second = points[:far + 1], points[far:] + [points[0]]
    return dp(first)[:-1] + dp(second)[:-1]


def _chaikin(points, iterations):
    for _ in range(iterations):
        out = []
        n = len(points)
        for i in range(n):
            (ax, ay), (bx, by) = points[i], points[(i + 1) % n]
            out.append((0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by))
            out.append((0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by))
        points = out
    return points


def outlines(rows, chars, origin, smooth=1, epsilon=0.2, min_area=0.0):
    """The outlines of the pixels whose character is in `chars` (outer outlines and holes), as
    polygons [(x, y), ...] in model coordinates. They run through the midpoints of the pixels'
    edges (so 45-degree staircases come out straight and square corners lose half a pixel),
    simplified, then rounded with `smooth` rounds of corner cutting (0 keeps corners)."""
    height = len(rows)
    width = max(len(r) for r in rows)
    grid = [r.ljust(width, ".") for r in rows]
    covered = lambda c, r: 0 <= c < width and 0 <= r < height and grid[r][c] in chars
    ox, oy = origin
    polys = []
    for loop in _pixel_loops(covered, width, height):
        n = len(loop)
        mids = [((loop[i][0] + loop[(i + 1) % n][0]) / 2, (loop[i][1] + loop[(i + 1) % n][1]) / 2) for i in range(n)]
        pts = _simplify_closed(mids, epsilon)
        pts = _chaikin(pts, smooth)
        poly = [(x - ox, oy - y) for x, y in pts]
        area = 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly)))
        if abs(area) >= min_area:
            polys.append(poly)
    return polys


def grow(rows, chars, into, steps=1):
    """The art with the pixels of `into` next to pixels of `chars` turned into chars[0] (parts
    that should tuck under their neighbours)."""
    grid = [list(r) for r in rows]
    for _ in range(steps):
        add = []
        for r, line in enumerate(grid):
            for c, ch in enumerate(line):
                if ch in into and any(0 <= r + dr < len(grid) and 0 <= c + dc < len(grid[r + dr]) and
                                      grid[r + dr][c + dc] in chars for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((r, c))
        for r, c in add:
            grid[r][c] = chars[0]
    return ["".join(line) for line in grid]


def smoothstep(edge0, edge1, x):
    t = min(1.0, max(0.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


def inset(poly, amount):
    """A polygon moved inwards by amount (simple: along the corners' bisectors; counter-clockwise
    or clockwise alike)."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sign = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
        n1 = Vector((-(by - ay), bx - ax)).normalized() * sign
        n2 = Vector((-(cy - by), cx - bx)).normalized() * sign
        bis = n1 + n2
        if bis.length < 1e-6:
            bis = n1
        bis.normalize()
        scale = amount / max(0.3, bis.dot(n1))
        out.append((bx + bis.x * scale, by + bis.y * scale))
    return out


def mirror_polys(polys, axis_x=0.0):
    return [[(2 * axis_x - x, y) for x, y in reversed(poly)] for poly in polys]


# --- Inflation ---------------------------------------------------------------------------------

def _segments(polys):
    a, b = [], []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            a.append(poly[i])
            b.append(poly[(i + 1) % n])
    return np.array(a, dtype=float), np.array(b, dtype=float)


def _distance(points, a, b, chunk=2048):
    """Distance from each point to the nearest segment."""
    out = np.empty(len(points))
    ab = b - a
    ab2 = np.maximum((ab ** 2).sum(1), 1e-12)
    for s in range(0, len(points), chunk):
        p = points[s:s + chunk, None, :]
        t = np.clip(((p - a[None]) * ab[None]).sum(2) / ab2[None], 0.0, 1.0)
        q = a[None] + t[..., None] * ab[None]
        out[s:s + chunk] = np.sqrt(((p - q) ** 2).sum(2)).min(1)
    return out


def _inside(points, a, b):
    """Even-odd test of points against the polygons' segments."""
    px, py = points[:, 0:1], points[:, 1:2]
    ax, ay, bx, by = a[None, :, 0], a[None, :, 1], b[None, :, 0], b[None, :, 1]
    crosses = (ay > py) != (by > py)
    with np.errstate(divide="ignore", invalid="ignore"):
        xi = ax + (py - ay) * (bx - ax) / (by - ay)
    hits = crosses & (px < xi)
    return (hits.sum(1) % 2) == 1


def _resample(poly, spacing):
    out = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        steps = max(1, int(math.ceil(math.hypot(bx - ax, by - ay) / spacing)))
        for s in range(steps):
            t = s / steps
            out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def thickness(points, d, spacing, sigma=1.2, chunk=1024):
    """Local thickness: for each point, the radius of the largest disk inside the shape (centred
    on one of the points) that covers it, then smoothed a little."""
    n = len(points)
    w = np.empty(n)
    reach = d + 0.6 * spacing
    for s in range(0, n, chunk):
        dist = np.sqrt(((points[s:s + chunk, None, :] - points[None, :, :]) ** 2).sum(2))
        w[s:s + chunk] = np.where(dist <= reach[None, :], d[None, :], 0.0).max(1)
    w = np.maximum(w, d)
    smoothed = np.empty(n)
    for s in range(0, n, chunk):
        dist2 = ((points[s:s + chunk, None, :] - points[None, :, :]) ** 2).sum(2)
        weight = np.exp(-dist2 / (2 * sigma ** 2)) * (dist2 < (3 * sigma) ** 2)
        smoothed[s:s + chunk] = (weight * w[None, :]).sum(1) / weight.sum(1)
    return np.maximum(smoothed, 1e-3)


def round_profile(aspect=1.0, max_height=None, min_height=0.0):
    """Tubes: a round cross-section as high as `aspect` times the local half-width."""
    def profile(d, w):
        h = aspect * w
        if max_height is not None:
            h = np.minimum(h, max_height)
        h = np.maximum(h, min_height)
        t = np.clip(d / w, 0.0, 1.0)
        return h * np.sqrt(np.maximum(0.0, 1.0 - (1.0 - t) ** 2))
    return profile


def pillow_profile(height, radius, crown=0.0):
    """Plates: a flat top `height` high with edges rounded over `radius`, bulging `crown` more in
    the middle of wide parts."""
    def profile(d, w):
        t = np.clip(d / radius, 0.0, 1.0)
        edge = np.sqrt(np.maximum(0.0, 1.0 - (1.0 - t) ** 2))
        bulge = crown * np.clip((d - radius) / np.maximum(w - radius, 1e-3), 0.0, 1.0) ** 0.7
        return height * edge + bulge
    return profile


def inflate(name, polys, mat, profile=None, bottom=1.0, base=0.0, rim=0.15, spacing=0.5, z_fn=None, sigma=1.2):
    """A closed part filling the polygons (even-odd: holes stay open), its top raised by
    profile(distance to the outline, local half-width) and its underside lowered by `bottom` times
    that (0: a flat bottom at `base`, for things standing on the ground). rim: the height of the
    straight edge all round. z_fn(x, y, z) -> z may reshape the top (grooves, slopes)."""
    profile = profile or round_profile()
    a, b = _segments(polys)
    xs = np.concatenate([a[:, 0], b[:, 0]])
    ys = np.concatenate([a[:, 1], b[:, 1]])
    # Samples: the outlines, and a grid inside.
    boundary = [p for poly in polys for p in _resample(poly, spacing)]
    gx = np.arange(math.floor(xs.min() / spacing) * spacing, xs.max() + spacing, spacing)
    gy = np.arange(math.floor(ys.min() / spacing) * spacing, ys.max() + spacing, spacing)
    grid = np.array([(x, y) for y in gy for x in gx], dtype=float)
    grid = grid[_inside(grid, a, b)]
    grid = grid[_distance(grid, a, b) > 0.35 * spacing]
    points2d = [Vector(p) for p in boundary] + [Vector(tuple(p)) for p in grid]
    constraint, start = [], 0
    for poly in polys:
        count = len(_resample(poly, spacing))
        constraint += [(start + i, start + (i + 1) % count) for i in range(count)]
        start += count
    verts, _edges, faces, *_ = geometry.delaunay_2d_cdt(points2d, constraint, [], 0, 1e-6)
    pts = np.array([(v.x, v.y) for v in verts], dtype=float)
    tris = [f for f in faces if len(f) == 3]
    centroids = np.array([pts[list(f)].mean(0) for f in tris])
    keep = _inside(centroids, a, b)
    tris = [f for f, kf in zip(tris, keep) if kf]
    d = _distance(pts, a, b)
    d[d < 1e-4] = 0.0
    w = thickness(pts, d, spacing, sigma)
    lift = profile(d, w)
    z_top = base + rim + lift
    if z_fn is not None:
        z_top = np.array([z_fn(x, y, z) for (x, y), z in zip(pts, z_top)])
    z_bot = base - bottom * (rim + lift)

    bm = bmesh.new()
    top = [bm.verts.new((x, y, z)) for (x, y), z in zip(pts, z_top)]
    bot = [bm.verts.new((x, y, z)) for (x, y), z in zip(pts, z_bot)]
    edge_use = {}
    for f in tris:
        try:
            bm.faces.new([top[i] for i in f])
            bm.faces.new([bot[i] for i in reversed(f)])
        except ValueError:
            continue
        for i in range(3):
            e = (f[i], f[(i + 1) % 3])
            key = (min(e), max(e))
            edge_use[key] = edge_use.get(key, []) + [e]
    for key, uses in edge_use.items():
        if len(uses) == 1:  # an outline edge: a wall from the top down to the underside
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
    return obj


# --- Cutting into pieces -----------------------------------------------------------------------

def apply_modifiers(obj):
    if not obj.modifiers:
        return obj
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()
    obj.data = mesh
    return obj


def cut_box(objects, x0, x1, y0, y1):
    """Keeps what lies in x0..x1, y0..y1 of each object, closing the cuts with flat caps (the
    pieces of a large model, which the game draws as separate sprites). Objects left empty are
    removed; returns the rest."""
    planes = [((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))]
    return cut_planes(objects, planes)


def flat_bottom(objects, z=0.0):
    """Cuts everything below z away, closing the cuts (things standing on the ground)."""
    return cut_planes(objects, [((0, 0, z), (0, 0, -1))])


def cut_planes(objects, planes):
    """Keeps what lies behind every plane (point, outward normal), closing the cuts."""
    kept = []
    for obj in objects:
        apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for co, no in planes:
            if not bm.verts:
                break
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            result = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=no, clear_outer=True)
            cut = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
            open_edges = [e for e in cut if len(e.link_faces) == 1]
            if open_edges:
                filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
                if filled["faces"]:
                    bmesh.ops.triangulate(bm, faces=filled["faces"], quad_method="BEAUTY", ngon_method="BEAUTY")
        if not bm.faces:
            bm.free()
            bpy.data.objects.remove(obj)
            continue
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(obj.data)
        bm.free()
        kept.append(obj)
    return kept


def paint_x(obj, ranges):
    """Paints an object by x: cuts its faces along the ranges' ends, then gives the faces whose
    centre lies in a range (x0, x1, material) that material (appended to the object)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for x0, x1, _ in ranges:
        for x in (x0, x1):
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(x, 0, 0), plane_no=(1, 0, 0))
    bm.to_mesh(obj.data)
    bm.free()
    for x0, x1, mat in ranges:
        if mat.name not in obj.data.materials:
            obj.data.materials.append(mat)
        index = list(obj.data.materials).index(mat)
        for poly in obj.data.polygons:
            if x0 <= poly.center.x <= x1:
                poly.material_index = index
    return obj


def move(objects, dx, dy, dz=0.0):
    for obj in objects:
        obj.data.transform(Matrix.Translation((dx, dy, dz)))


# --- Placing details ---------------------------------------------------------------------------

def surface_z(obj, x, y, default=0.0):
    """The height of an object's top surface at (x, y) (a ray from above)."""
    hit, location, _normal, _index = obj.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
    return location.z if hit else default


def ellipse(cx, cy, rx, ry, angle=0.0, count=32):
    """An ellipse as a polygon, turned by angle (degrees, counter-clockwise)."""
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    out = []
    for i in range(count):
        a = 2 * math.pi * i / count
        px, py = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + c * px - s * py, cy + s * px + c * py))
    return out


def tube_along(name, path, radius, mat, segments=12, z_of=None):
    """A thin round tube through points (x, y, z) (z_of(x, y) gives z where z is None), closed
    with rounded ends."""
    pts = [Vector((x, y, z if z is not None else z_of(x, y))) for x, y, z in path]
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(tangent).normalized()
        ring = [p + (side * math.cos(2 * math.pi * j / segments) + up * math.sin(2 * math.pi * j / segments)) * radius
                for j in range(segments)]
        rings.append(ring)
    t0 = (pts[1] - pts[0]).normalized()
    t1 = (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radius * 0.8, end_point=pts[-1] + t1 * radius * 0.8)
    return k.smooth(obj, 60)
