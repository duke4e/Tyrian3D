"""The two big grey asteroids of the asteroid levels, polished (2026-10-19; they replace wave2_f_more.py's and
wave3_j_rocks.py's clusters of smooth boulders on a flat base). Each is drawn as four 2x2 sprites of sheet D
that the levels place as one 48 x 56 picture (event 12, "4-part enemy": the first part at x, y, the second 24
pixels right of it, the third 28 pixels up the screen, the fourth both):

- asteroid (ASTEROID1, ASTEROID?, enemies 440-443; ASTEROIDS, 1107-1110): D 45 bottom left, D 47 bottom right,
  D 7 top left, D 9 top right; models asteroid_bl, asteroid_br, asteroid_tl, asteroid_tr.
- asteroid2 (ASTEROID1, ASTEROID?, ASTEROIDS, enemies 138-141): D 39, D 41, D 1, D 3; models asteroid2_bl,
  asteroid2_br, asteroid2_tl, asteroid2_tr.

The levels put them on the ground, the top and the sky layers, drifting down the screen; each part is an enemy
of its own (it can be shot away alone). models.cfg draws the parts at their own origin (model ... origin): each
piece's origin is its sprite's centre, its base on the layer.

As the sprites and their 4x upscales draw them: real rock, broken into blocks by thin dark cracks, light where
it faces the light from the upper left, dark on the lower right and along the bottom, and carved with swirl
markings. The first asteroid is a few large angular blocks, each a few flat planes with bevelled edges: a
pointed block at the top right with a swirl round a knob, a broad light block at the upper left, a bright one
in the middle with a curl, a ring round a shallow bowl at the lower left. The second is a compact cluster of
rounded knobs between deep crevices, a carved glyph (an ammonite's spiral) on its light knob at the upper left.

The rock is built as such blocks, each a convex polyhedron (the intersection of half-spaces: its footprint's
walls rising steeply from the ground and bevelled near the top, one or more roof planes, a few chips off its
corners; for a rounded knob, the faces of a faceted hull of points on an ellipsoid). Where two blocks meet,
both reach a little across the crack line between them, their walls there steep, so that they meet along it.
The blocks are joined (boolean union, Blender's Manifold solver: the exact one leaves the shared ground plane
and outline walls non-manifold), the cracks cut in as narrow V-shaped grooves of dark rock along those lines
(their course and width wandering a little), the bowls cut out, the curls, rings and knobs laid on the
surface and joined to it. The faces the game's camera sees are then retriangulated evenly (about 0.9 pixels
apart, constrained Delaunay inside each flat face) and every point moved a little along its normal by smooth
noise: weathered stone, its facets' edges kept sharp. The whole rock is cut along the sprites' edges into the
four pieces, each moved so that its sprite's centre is its origin, the cuts closed with dark rock (seen when a
piece is shot away), the pieces' shading that of the whole (polish_machine_kit.cut's method). Greys are the
sprites' own palette indices (ramp 0): the blocks 06-0b, the curls a shade lighter, the cracks 04.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole
rock's origin is the corner where its four sprites meet (pixel 24, 28 of the 48 x 56 picture); px(c, r) turns
a pixel corner of the picture (column c, row r) into these coordinates.

Options after "--": --outdir <dir> (default assets/models/enemies), --only asteroid,asteroid2, --check
<sheets dir> (the silhouettes of the whole and of each piece against enemy_D.png), --preview <prefix> (each
piece's top and 3/4 view), --whole <prefix> (the whole rock's top and 3/4 views).

Replaces wave2_f_more.py's asteroid (asteroid_whole and its pieces) and wave3_j_rocks.py's asteroid2.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402

# The quarters: model suffix, the box they cover in the whole's coordinates (x0, x1, y0, y1).
QUARTERS = [("tl", (-24.0, 0.0, 0.0, 28.0)), ("tr", (0.0, 24.0, 0.0, 28.0)),
            ("bl", (-24.0, 0.0, -28.0, 0.0)), ("br", (0.0, 24.0, -28.0, 0.0))]

REACH = 0.7  # how far a block reaches across a crack line into its neighbour


def px(c, r):
    """A pixel corner of the 48 x 56 picture (column c, row r) in the whole rock's coordinates."""
    return Vector((c - 24.0, 28.0 - r))


def convex_hull(points):
    """The convex hull of 2D points (x, y, tag), counter-clockwise (x right, y up)."""
    pts = sorted({(round(p[0], 6), round(p[1], 6)): p for p in points}.values(), key=lambda p: (p[0], p[1]))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-9:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-9:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def open_edges(obj):
    """How many of a mesh's edges are not between exactly two faces (0 for a closed, manifold mesh)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    count = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return count


def tidy(obj, dissolve=0.2):
    """Dissolves the edges between coplanar faces of the same material (left by the booleans), unless that
    would leave the mesh open (then it is left as it was)."""
    before = obj.data.copy()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(dissolve), use_dissolve_boundaries=False,
                             verts=bm.verts, edges=bm.edges, delimit={"MATERIAL"})
    bm.to_mesh(obj.data)
    bm.free()
    if open_edges(obj):
        broken = obj.data
        obj.data = before
        bpy.data.meshes.remove(broken)
    else:
        bpy.data.meshes.remove(before)
    return obj


def boolean(obj, others, operation="UNION"):
    """obj joined to (or cut by) the others, applied, with Blender's Manifold solver (the blocks share the
    ground plane and some outline walls, which the exact solver leaves non-manifold); the others are
    removed. Faces keep their materials. The solver needs closed meshes: an open one is an error."""
    others = others if isinstance(others, (list, tuple)) else [others]
    for other in others:
        for o in (obj, other):
            if open_edges(o):
                raise RuntimeError("%s is not closed (%d open edges): the boolean would fail" % (o.name, open_edges(o)))
        other.hide_render = True
        mod = obj.modifiers.new("boolean", "BOOLEAN")
        mod.operation = operation
        mod.solver = "MANIFOLD"
        mod.material_mode = "TRANSFER"
        mod.object = other
        mk.apply(obj)
        data = other.data
        bpy.data.objects.remove(other)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    return obj


# --- Blocks: convex polyhedra from half-spaces (n . p <= d) ----------------------------------------

def edge_planes(a, b, profile):
    """For an edge a-b of a counter-clockwise footprint: the half-space inside it and the planes of a wall
    profile [(inset, height), ...] (concave: steep from the ground, flatter towards the top) rising
    inward from it."""
    e = (b - a).normalized()
    m = Vector((-e.y, e.x))  # inward
    planes = [(Vector((-m.x, -m.y, 0.0)), -m.dot(a))]
    for (i0, z0), (i1, z1) in zip(profile, profile[1:]):
        s = (z1 - z0) / (i1 - i0)
        planes.append((Vector((-s * m.x, -s * m.y, 1.0)), z0 - s * m.dot(a) - s * i0))
    return planes


def roof(point, nx, ny):
    """The half-space under a plane through point (x, y, z) whose normal leans as (nx, ny, 1)."""
    x, y, z = point
    return (Vector((nx, ny, 1.0)), z + nx * x + ny * y)


def solid(name, planes, mat=None):
    """The convex polyhedron of the half-spaces, standing on z = 0."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(160.0, 160.0, 80.0), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 30.0), verts=bm.verts)
    for n, d in [(Vector((0.0, 0.0, -1.0)), 0.0)] + planes:
        length = n.length
        n, d = n / length, d / length
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=n * d,
                               plane_no=n, clear_outer=True)
        open_edges = [e for e in bm.edges if e.is_boundary]
        if open_edges:
            bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.2), verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        mesh.materials.append(mat)
    return obj


class Crack:
    """A crack between blocks: a polyline of pixel corners, cut in as a V-shaped groove width wide at the
    surface and depth deep; an end on the rock's rim ("out") runs on through its wall, an end inside a
    block ("in") tapers away."""

    def __init__(self, corners, width=1.3, depth=2.2, ends=("in", "in"), cut=True):
        self.points = [px(c, r) for c, r in corners]
        self.width, self.depth, self.ends = width, depth, ends
        self.cut = cut  # False: only a border between blocks (a crease where their caps meet)

    def offset(self, towards, distance):
        """The polyline moved sideways by distance, to the side of the point towards."""
        out = []
        n = len(self.points)
        for i, p in enumerate(self.points):
            t = (self.points[min(i + 1, n - 1)] - self.points[max(i - 1, 0)]).normalized()
            side = Vector((-t.y, t.x))
            if side.dot(towards - p) < 0:
                side = -side
            out.append(p + side * distance)
        return out


class Block:
    """A block of the rock: the rim points it reaches (pixel corners on the rock's outline), the cracks it
    borders (it reaches REACH across them), its roof planes ((column, row, height, nx, ny): through that
    point, leaning as (nx, ny, 1); the first one's point must lie on the block's own side of its cracks),
    its grey, chips off its top ((column, row, height, nx, ny), as roofs), how many chips more at random
    (off its top corners and across its roof) and, for a rounded knob, a cap (column, row, rx, ry, rz, z,
    points): the faceted hull of points on an ellipsoid centred z under that pixel corner."""

    def __init__(self, name, rim, cracks, roofs, shade, chips=(), random_chips=4, seed=0, cap=None):
        self.name = name
        self.cap = cap
        self.rim = [px(c, r) for c, r in rim]
        self.cracks = cracks
        self.roofs = [(px(c, r).to_3d() + Vector((0, 0, z)), nx, ny) for c, r, z, nx, ny in roofs]
        self.shade = shade
        self.chips = [(px(c, r).to_3d() + Vector((0, 0, z)), nx, ny) for c, r, z, nx, ny in chips]
        self.random_chips = random_chips
        self.seed = seed

    def footprint(self, cracks):
        """The convex footprint, its points tagged "rim" or "crack"."""
        pts = [(p.x, p.y, "rim") for p in self.rim]
        own = self.roofs[0][0].to_2d()  # a point on the block's own side of its cracks
        for c in self.cracks:
            pts += [(p.x, p.y, "crack") for p in cracks[c].offset(own, -REACH)]
        return convex_hull(pts)

    def planes(self, cracks, outer, inner):
        poly = self.footprint(cracks)
        planes = []
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            profile = inner if a[2] == "crack" and b[2] == "crack" else outer
            planes += edge_planes(Vector(a[:2]), Vector(b[:2]), profile)
        planes += [roof(p, nx, ny) for p, nx, ny in self.roofs + self.chips]
        if self.cap is not None:
            planes += self.capped()
        planes += self.chipped(poly, planes)
        return planes

    def capped(self):
        """The planes of the faces of the convex hull of points spread over an ellipsoid (most of them on
        its upper half, a little jittered): a rounded cap of large facets."""
        c, r, rx, ry, rz, z0, count = self.cap
        rng = random.Random(self.seed * 53 + 11)
        centre = px(c, r).to_3d() + Vector((0, 0, z0))
        golden = math.pi * (3 - math.sqrt(5))
        bm = bmesh.new()
        for i in range(count):
            t = 1 - 1.3 * (i + 0.5) / count  # from the top down to below the equator
            ring = math.sqrt(max(0.0, 1 - t * t))
            a = golden * i + rng.uniform(-0.3, 0.3)
            d = Vector((ring * math.cos(a), ring * math.sin(a), t))
            d = (d + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.12).normalized()
            f = rng.uniform(0.93, 1.05)
            bm.verts.new(centre + Vector((d.x * rx * f, d.y * ry * f, d.z * rz * f)))
        bmesh.ops.convex_hull(bm, input=bm.verts[:])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        planes = []
        for face in bm.faces:
            n = face.normal.copy()
            if n.z < -0.2:
                continue  # the underside: the ground cuts there
            planes.append((n, n.dot(face.verts[0].co)))
        bm.free()
        return planes

    def chipped(self, poly, planes):
        """Random chips: off the top of the footprint's corners (planes leaning outward) and across the
        roof (planes a little below it, leaning a little), so that no two blocks look cut alike."""
        rng = random.Random(self.seed * 7919 + len(self.name))
        tops = [(n, d) for n, d in planes if n.z > 1e-6]

        def height(p):
            return min((d - n.x * p.x - n.y * p.y) / n.z for n, d in tops)
        centre = sum((Vector(p[:2]) for p in poly), Vector((0, 0))) / len(poly)
        out = []
        corners = sorted(range(len(poly)), key=lambda i: rng.random())
        for i in range(self.random_chips):
            if i % 3 == 2:  # across the roof
                q = centre + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1))) * 2.5
                lean = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1))).normalized() * rng.uniform(0.18, 0.32)
                point = Vector((q.x, q.y, height(q) - rng.uniform(0.15, 0.35)))
                normal = Vector((lean.x, lean.y, 1.0))
            else:  # off a corner
                corner = Vector(poly[corners[i % len(corners)]][:2])
                inward = (centre - corner).normalized()
                q = corner + inward * rng.uniform(1.6, 3.0)
                outward = -inward
                ang = rng.uniform(-0.5, 0.5)
                outward = Vector((outward.x * math.cos(ang) - outward.y * math.sin(ang),
                                  outward.x * math.sin(ang) + outward.y * math.cos(ang)))
                tilt = rng.uniform(0.55, 1.0)
                point = Vector((q.x, q.y, height(q) - rng.uniform(0.1, 0.4)))
                normal = Vector((outward.x * tilt, outward.y * tilt, 1.0))
            out.append((normal, normal.dot(point)))
        return out


# --- The surface and what is laid on it or cut into it -----------------------------------------------

class Surface:
    """The rock's top: where a ray straight down meets it, and its normal there."""

    def __init__(self, obj):
        mesh = obj.data
        self.bvh = BVHTree.FromPolygons([obj.matrix_world @ v.co for v in mesh.vertices],
                                        [list(p.vertices) for p in mesh.polygons])

    def hit(self, x, y):
        location, normal, _, _ = self.bvh.ray_cast(Vector((x, y, 100.0)), Vector((0, 0, -1)))
        if location is None:
            return Vector((x, y, 0.0)), Vector((0, 0, 1))
        return location, (normal if normal.z > 0 else -normal)


def resample(points, step):
    path = [Vector(points[0])]
    for p in points[1:]:
        p = Vector(p)
        while (p - path[-1]).length > step:
            path.append(path[-1] + (p - path[-1]).normalized() * step)
    if (Vector(points[-1]) - path[-1]).length > 1e-3:
        path.append(Vector(points[-1]))
    return path


def outward(obj):
    """Turns a closed mesh's faces outward (a positive volume)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def crack_cutter(name, surface, crack, mat, seed):
    """The solid a crack's groove is cut with: along the crack, a V under the surface, open above it; its
    course and width wander a little (smooth noise), as broken rock does."""
    rng = random.Random(seed)
    pts = list(crack.points)
    for end, (i, j) in zip(crack.ends, ((0, 1), (-1, -2))):
        if end == "out":  # run on through the rim
            pts.insert(0 if i == 0 else len(pts), pts[i] + (pts[i] - pts[j]).normalized() * 2.0)
    path = resample(pts, 0.4)
    shift = Vector((rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50)))
    wander = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        q = p.to_3d() * 0.55 + shift
        wander.append(p + Vector((-t.y, t.x)) * (0.22 * noise.noise(q) + 0.08 * noise.noise(q * 3.1)))
    path = wander
    total = sum((b - a).length for a, b in zip(path, path[1:]))
    rings = []
    walked = 0.0
    for i, p in enumerate(path):
        if i:
            walked += (p - path[i - 1]).length
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        side = Vector((-t.y, t.x))
        f = 1.0
        if crack.ends[0] == "in":
            f = min(f, walked / 2.0)
        if crack.ends[1] == "in":
            f = min(f, (total - walked) / 2.0)
        f = max(0.0, min(1.0, f))
        q = p.to_3d() * 0.8 + shift * 1.7
        w = 0.5 * crack.width * (0.3 + 0.7 * f) * (1.0 + 0.3 * noise.noise(q))
        hl = surface.hit(*(p - side * w))[0].z
        hr = surface.hit(*(p + side * w))[0].z
        hc = surface.hit(*p)[0].z
        low = min(hl, hr, hc)
        bottom = max(0.4, low - crack.depth * f * (1.0 + 0.2 * noise.noise(q * 1.3)))
        if f < 0.02:
            bottom = low + 0.02
        top = 40.0
        rings.append([(p - side * w).to_3d() + Vector((0, 0, top)), (p - side * w).to_3d() + Vector((0, 0, hl + 0.03)),
                      p.to_3d() + Vector((0, 0, bottom)),
                      (p + side * w).to_3d() + Vector((0, 0, hr + 0.03)), (p + side * w).to_3d() + Vector((0, 0, top))])
    return outward(k.loft(name, rings, mat))


def ridge(name, surface, corners, half_width, height, mat, step=0.45, taper=0.2, seed=0):
    """A raised curl lying on the surface along a polyline of pixel corners (rounded): a low welt about
    half_width wide either side of it, its top rounded, standing height above the surface, its ends
    tapering, its width wandering a little (weathered)."""
    pts = mk.chaikin([tuple(px(c, r)) for c, r in corners], 3, closed=False)
    path = resample(pts, step)
    shift = Vector((seed * 3.7, seed * 1.3, seed * 5.1))
    across = [-1.0, -0.8, -0.55, -0.28, 0.0, 0.28, 0.55, 0.8, 1.0]
    rings = []
    count = len(path)
    for i, p in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, count - 1)]
        t = (b - a).normalized()
        hit, normal = surface.hit(p.x, p.y)
        side = Vector((t.x, t.y, 0.0)).cross(normal).normalized()
        f = min(1.0, (i + 0.5) / (count * taper), (count - i - 0.5) / (count * taper))
        f = math.sqrt(max(f, 0.06))
        wob = 1.0 + 0.18 * noise.noise(p.to_3d() * 0.9 + shift)
        w, h = half_width * (0.55 + 0.45 * f) * wob, height * f
        ring = []
        for u in across:  # over the top, from one side to the other
            ring.append(hit + side * (w * u) + normal * (h * (1 - abs(u) ** 3.0) ** 0.45 - 0.25))
        ring.append(hit + side * (w * 0.7) - normal * 0.9)  # buried underneath
        ring.append(hit - side * (w * 0.7) - normal * 0.9)
        rings.append(ring)
    t0 = (path[1] - path[0]).normalized().to_3d()
    t1 = (path[-1] - path[-2]).normalized().to_3d()
    obj = k.loft(name, rings, mat, start_point=sum(rings[0], Vector()) / len(rings[0]) - t0 * 0.3,
                 end_point=sum(rings[-1], Vector()) / len(rings[-1]) + t1 * 0.3)
    return outward(obj)


def knob(name, surface, c, r, radius, height, mat, segments=14, rings=5):
    """A round boss standing out of the surface at pixel corner (c, r)."""
    p = px(c, r)
    hit, up = surface.hit(p.x, p.y)
    side = (Vector((1, 0, 0)) - up * up.x).normalized()
    other = up.cross(side)
    verts, faces = [], []
    for i in range(rings + 1):
        phi = (math.pi / 2) * i / rings
        for j in range(segments):
            a = 2 * math.pi * j / segments
            rr = radius * math.cos(phi) ** 0.8
            verts.append(hit + side * (rr * math.cos(a)) + other * (rr * math.sin(a)) +
                         up * (-0.8 + (0.8 + height) * math.sin(phi)))
    for i in range(rings):
        for j in range(segments):
            a, b = i * segments + j, i * segments + (j + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    verts.append(hit + up * height)
    top = len(verts) - 1
    faces += [(rings * segments + j, rings * segments + (j + 1) % segments, top) for j in range(segments)]
    verts.append(hit - up * 1.0)
    bottom = len(verts) - 1
    faces += [((j + 1) % segments, j, bottom) for j in range(segments)]
    return outward(k.mesh_object(name, verts, faces, mat))


def bowl_cutter(name, surface, c, r, radius, depth, mat):
    """The solid a shallow round bowl is cut with at pixel corner (c, r): a flat ellipsoid whose surface
    meets the rock's on a circle of the radius, depth under it in the middle."""
    p = px(c, r)
    hit, normal = surface.hit(p.x, p.y)
    rz = 0.6 * radius
    lift = rz - depth
    wide = radius / math.sqrt(1 - (lift / rz) ** 2)
    sphere = mk.ball(name, (0.0, 0.0, 0.0), (wide, wide, rz), mat, segments=28, rings=14)
    q = normal.to_track_quat("Z", "Y")
    sphere.data.transform(Matrix.Translation(hit + normal * lift) @ q.to_matrix().to_4x4())
    return sphere


def split_edges(bm, edges, spacing):
    """Splits each edge into pieces about spacing long (its faces gain the new points)."""
    for e in edges:
        if not e.is_valid:
            continue
        count = int(e.calc_length() / spacing)
        a, b = e.verts
        current = e
        for i in range(count, 0, -1):
            _, v = bmesh.utils.edge_split(current, a, 1.0 / (i + 1))
            a = v
            current = bm.edges.get((v, b))
            if current is None:
                break


def refine(bm, spacing, seen):
    """Retriangulates the large flat faces the camera sees evenly: points on a jittered grid spacing apart
    inside each, joined to its outline's points by a constrained Delaunay triangulation."""
    from mathutils.geometry import delaunay_2d_cdt
    rng = random.Random(5)
    bm.normal_update()
    split_edges(bm, [e for e in bm.edges if e.calc_length() > spacing * 1.2 and
                     any(seen(f) for f in e.link_faces) and max(v.co.z for v in e.verts) > 0.02], spacing)
    for face in [f for f in bm.faces if seen(f) and f.calc_area() > spacing * spacing * 1.5]:
        n = face.normal.copy()
        u = (Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))).cross(n).normalized()
        w = n.cross(u)
        origin = face.verts[0].co.copy()
        ring = list(face.verts)
        flat = [Vector(((v.co - origin).dot(u), (v.co - origin).dot(w))) for v in ring]
        xs, ys = [p.x for p in flat], [p.y for p in flat]
        inner = []
        y = min(ys) + spacing * 0.5
        row = 0
        while y < max(ys):
            x = min(xs) + spacing * (0.5 + 0.5 * (row % 2))
            while x < max(xs):
                q = Vector((x + rng.uniform(-0.2, 0.2) * spacing, y + rng.uniform(-0.2, 0.2) * spacing))
                if inside(q, flat) and edge_distance(q, flat) > 0.45 * spacing:
                    inner.append(q)
                x += spacing
            y += spacing * 0.866
            row += 1
        if not inner:
            continue
        coords = flat + inner
        out_coords, _, out_faces, orig_verts, _, _ = delaunay_2d_cdt(
            coords, [], [list(range(len(flat)))], 1, 1e-6)
        verts = []
        for i, co in enumerate(out_coords):
            source = orig_verts[i]
            if source and source[0] < len(flat):
                verts.append(ring[source[0]])
            else:
                verts.append(bm.verts.new(origin + u * co[0] + w * co[1]))
        material, smooth = face.material_index, face.smooth
        bm.faces.remove(face)
        for tri in out_faces:
            vs = [verts[i] for i in tri]
            if len(set(vs)) < 3 or bm.faces.get(vs) is not None:
                continue
            f = bm.faces.new(vs)
            f.material_index = material
            f.smooth = smooth
            f.normal_update()
            if f.normal.dot(n) < 0:
                f.normal_flip()
    bm.normal_update()


def inside(p, poly):
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        a, b = poly[i], poly[j]
        if (a.y > p.y) != (b.y > p.y) and p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x:
            hit = not hit
        j = i
    return hit


def edge_distance(p, poly):
    best = 1e9
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.dot(ab), 1e-12)))
        best = min(best, (a + ab * t - p).length)
    return best


CAMERA = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))  # towards the game's camera


def roughen(obj, spacing=0.9, amount=0.2, seed=0):
    """Weathers the rock's surface: the flat faces the game's camera sees retriangulated evenly (about
    spacing pixels apart), every point moved along its normal by smooth noise (up to about amount pixels),
    the ground kept flat."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges,
                             delimit={"MATERIAL"})
    bm.normal_update()
    refine(bm, spacing, lambda f: f.normal.dot(CAMERA) > 0.1)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    bm.normal_update()
    shift = Vector((seed * 2.1 + 11.0, seed * 4.7 + 3.0, seed * 0.9 + 7.0))
    moves = []
    for v in bm.verts:
        if v.co.z < 0.02:
            moves.append(Vector())
            continue
        q = v.co * 0.7 + shift
        d = amount * (0.65 * noise.noise(q) + 0.35 * noise.noise(q * 2.6))
        moves.append(v.normal * d * min(1.0, v.co.z / 1.5))
    for v, m in zip(bm.verts, moves):
        v.co += m
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def cut(source, box_xy, cap_mat):
    """polish_machine_kit.cut (the part of an object inside a box, its cuts capped, its shading the uncut
    object's), without its last step: dropping the materials no face uses any more shifted the faces'
    material indices twice (Blender's materials.pop shifts them itself), which gave some faces another
    material. Unused material slots export nothing; they are left."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                caps |= set(bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"])
    caps = {f for f in caps if f.is_valid}
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    for f in caps:
        f.material_index = cap_index
        f.smooth = False
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.faces.index_update()
    cap_ids = {f.index for f in caps if f.is_valid}
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.validate()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def used_materials(objects):
    return sorted({obj.data.materials[p.material_index].name for obj in objects for p in obj.data.polygons})


# --- The rock ---------------------------------------------------------------------------------------

def greys(prefix):
    """The rock's materials: palette greys (ramp 0) by index."""
    cache = {}

    def grey(index):
        if index not in cache:
            cache[index] = k.material(f"{prefix}_rock", palette=index, metallic=0.0, roughness=0.62)
        return cache[index]
    return grey


def build_rock(spec):
    grey = greys(spec["prefix"])
    cracks = spec["cracks"]
    blocks = []
    for i, b in enumerate(spec["blocks"]):
        b.seed = b.seed or i + 1
        blocks.append(solid(b.name, b.planes(cracks, spec["outer"], spec["inner"]), grey(b.shade)))
    rock = blocks[0]
    boolean(rock, blocks[1:], "UNION")
    tidy(rock)
    rock.name = spec["prefix"]
    # The cracks.
    surface = Surface(rock)
    lines = [(crack, spec["crack_shade"]) for _, crack in sorted(cracks.items()) if crack.cut]
    lines += [(crack, spec["hairline_shade"]) for crack in spec.get("hairlines", ())]
    cutters = [crack_cutter("crack%d" % i, surface, crack, grey(shade), seed=i)
               for i, (crack, shade) in enumerate(lines)]
    boolean(rock, cutters, "DIFFERENCE")
    # The bowls.
    surface = Surface(rock)
    bowls = [bowl_cutter("bowl%d" % i, surface, c, r, radius, depth, grey(shade))
             for i, (c, r, radius, depth, shade) in enumerate(spec.get("bowls", ()))]
    if bowls:
        boolean(rock, bowls, "DIFFERENCE")
    # The curls, rings and knobs.
    surface = Surface(rock)
    raised = []
    for i, (corners, half_width, height, shade) in enumerate(spec.get("ridges", ())):
        raised.append(ridge("ridge%d" % i, surface, corners, half_width, height, grey(shade), seed=i))
    for i, (c, r, radius, height, shade) in enumerate(spec.get("knobs", ())):
        raised.append(knob("knob%d" % i, surface, c, r, radius, height, grey(shade)))
    if raised:
        boolean(rock, raised, "UNION")
    tidy(rock)
    roughen(rock, seed=len(spec["prefix"]))
    # The facets' edges sharp, the weathered faces, curls and knobs smooth.
    k.smooth(rock, 34)
    return rock, grey


def whole_mask(sheet, sprites):
    """The four sprites' silhouettes placed as the levels place them: 48 x 56 (tl, tr, bl, br)."""
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (ox, oy) in zip(sprites, ((0, 0), (24, 0), (0, 28), (24, 28))):
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[oy + y][ox + x] = True
    return mask


def build(spec, options):
    k.reset()
    rock, grey = build_rock(spec)
    whole = [rock]
    print("%s whole: %d triangles, %d materials" % (spec["prefix"], mk.triangles(whole), len(rock.data.materials)))
    sheets = options.get("check")
    sheet = os.path.join(sheets, "enemy_D.png") if sheets else None
    if sheet:
        mk.compare(spec["prefix"] + " whole", mk.coverage(whole, 48, 56), whole_mask(sheet, spec["sprites"]))
    if "whole" in options:
        mk.preview(options["whole"] + spec["prefix"], whole, size=(48, 56), scale=8, distance=2.0)
    out = mk.outdir(options)
    cap = grey(spec["cap"])
    for (suffix, box), sprite in zip(QUARTERS, spec["sprites"]):
        name = "%s_%s" % (spec["prefix"], suffix)
        pieces = [p for p in (cut(src, box, cap) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        if sheet:
            mk.compare("%s (D %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        size = mk.export(pieces, os.path.join(out, name + ".glb"))
        low, high = mk.bounds(pieces)
        print("== %s: %d triangles, %d bytes, materials %s, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            name, mk.triangles(pieces), size, ", ".join(used_materials(pieces)), low.x, high.x, low.y, high.y,
            low.z, high.z))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)


# --- D 7, 9, 45, 47: the first asteroid ---------------------------------------------------------------
# Blocks as the sprites draw them (pixel corners of the 48 x 56 picture): the pointed block at the top right
# with the swirl round a knob (tr), the broad light block at the upper left (ul), the bright block in the
# middle with a curl (mid), the dark right rim (rim), the lower left block with the ring round a bowl (ll),
# the lower right block (lr) and the slab along the bottom (bot).

AST1_CRACKS = {
    "a": Crack([(24.7, 11.5), (26.6, 14.4), (28.4, 17.2), (29.6, 20.0)], 1.3, 2.6, ("out", "in")),
    "d": Crack([(29.6, 20.0), (33.0, 21.6), (37.4, 23.8)], 1.1, 2.2),
    "trrim": Crack([(37.4, 23.8), (41.6, 21.0), (47.0, 18.4)], 1.0, 2.0, ("in", "out")),
    "c": Crack([(37.4, 23.8), (38.6, 27.4), (39.2, 31.6)], 1.2, 2.4),
    "rimlr": Crack([(39.2, 31.6), (42.0, 30.4), (44.3, 29.7)], 1.0, 2.0, ("in", "out")),
    "ulmid": Crack([(29.6, 20.0), (28.4, 24.6), (27.4, 28.4), (26.8, 30.8)], 1.0, 1.8),
    "b": Crack([(13.0, 31.0), (17.0, 31.0), (21.0, 30.8), (26.8, 30.8)], 1.3, 2.6, ("out", "in")),
    "midlr": Crack([(26.8, 30.8), (30.4, 32.4), (34.4, 33.0), (39.2, 31.6)], 1.0, 2.0),
    "lllr": Crack([(26.8, 30.8), (29.4, 34.8), (31.6, 38.6), (33.6, 41.6)], 1.2, 2.4),
    "llbot": Crack([(7.0, 41.6), (13.0, 42.2), (20.0, 42.6), (27.0, 42.2), (33.6, 41.6)], 1.0, 2.0, ("out", "in")),
    "lrbot": Crack([(33.6, 41.6), (38.6, 41.0), (44.0, 40.5)], 0.9, 1.8, ("in", "out")),
}
# Hairline cracks inside blocks (not between them).
AST1_HAIRLINES = [
    Crack([(14.0, 18.0), (16.6, 21.4), (17.4, 24.6)], 0.45, 0.6),
    Crack([(36.0, 44.6), (31.0, 47.0), (26.0, 47.6), (22.0, 50.6)], 0.5, 0.7),
    Crack([(41.0, 34.0), (39.6, 37.0), (40.4, 39.6)], 0.45, 0.6),
    Crack([(10.0, 44.0), (13.6, 45.0), (16.0, 47.4)], 0.45, 0.6),
]

AST1_BLOCKS = [
    Block("tr", [(24.7, 11.5), (25.5, 10.6), (31.0, 4.6), (32.4, 4.0), (35.0, 4.0), (43.0, 8.3), (47.0, 15.2),
                 (47.0, 18.4)], ["a", "d", "trrim"],
          [(31.0, 12.0, 10.6, -0.55, 0.35), (40.0, 10.0, 10.6, 0.65, 0.25), (38.0, 16.0, 11.4, 0.1, -0.12)], 0x09),
    Block("ul", [(13.0, 31.0), (13.0, 30.0), (12.0, 28.8), (11.0, 26.6), (10.0, 25.8), (10.0, 20.0), (11.0, 18.4),
                 (13.0, 16.2), (15.0, 13.6), (16.4, 11.8), (17.2, 11.0), (24.0, 11.0), (24.7, 11.5)], ["a", "ulmid", "b"],
          [(19.0, 21.0, 11.6, -0.36, 0.26), (24.0, 26.0, 11.8, 0.1, -0.35)], 0x0a),
    Block("mid", [], ["d", "c", "midlr", "ulmid"], [(32.6, 25.6, 12.8, -0.22, 0.18), (35.0, 29.0, 12.6, 0.3, -0.25)],
          0x0a),
    Block("rim", [(47.0, 18.4), (47.0, 19.8), (46.0, 20.6), (46.0, 24.6), (45.0, 25.5), (44.2, 28.0), (44.3, 29.7)],
          ["trrim", "c", "rimlr"], [(42.0, 25.0, 10.0, 0.7, -0.1)], 0x07),
    Block("ll", [(13.0, 31.0), (13.0, 32.6), (12.0, 33.2), (11.0, 34.0), (11.0, 37.6), (10.0, 38.4), (8.4, 39.8),
                 (7.0, 41.2), (7.0, 41.6)], ["b", "lllr", "llbot"],
          [(19.0, 36.0, 11.2, -0.36, 0.14), (24.0, 39.0, 11.2, 0.15, -0.3)], 0x0a),
    Block("lr", [(44.3, 29.7), (45.2, 30.5), (46.0, 32.2), (46.0, 38.8), (44.0, 40.5)], ["rimlr", "midlr", "lllr", "lrbot"],
          [(36.0, 35.0, 10.8, 0.05, 0.12), (41.0, 37.0, 10.4, 0.55, -0.15)], 0x09),
    Block("bot", [(7.0, 41.6), (7.0, 46.5), (7.6, 47.0), (10.0, 48.5), (13.5, 50.5), (17.5, 52.5), (20.0, 54.0),
                  (24.0, 54.0), (29.0, 52.5), (32.5, 51.5), (36.3, 50.5), (38.4, 49.2), (39.6, 46.6), (41.5, 44.0),
                  (44.0, 40.5)], ["llbot", "lrbot"],
          [(16.0, 45.0, 9.4, -0.35, 0.25), (32.0, 45.0, 9.2, 0.3, 0.1), (24.0, 49.0, 8.4, 0.0, -0.55)], 0x07),
]

# --- D 1, 3, 39, 41: the second asteroid --------------------------------------------------------------
# A compact cluster of rounded knobs (like a clenched fist's knuckles) between deep dark crevices: the top
# knob (top) and the dark shoulder at its right with a hollow (tr), the small knob at the upper left (ul), the
# light knob with the carved glyph, which the upscale draws as a ring round a face and the model as a spiral
# round a hollow, an ammonite (glyph), the light lobe at the left (left), the dark recess in the middle
# (midr), the knob at the right (right), the light lobe below the middle with a curl (bc), the lower left
# lobe (ll), the dark lower right (lr) and the bottom block, pitted (bottom). Each block's top is a rounded
# cap of large facets; only the deep crevices are cut as cracks, the other borders are where knobs meet.

AST2_CRACKS = {
    "c1": Crack([(14.0, 11.0), (15.0, 15.0), (16.5, 17.5)], 1.2, 2.6, ("out", "in")),
    "c2": Crack([(16.5, 17.5), (21.0, 17.0), (25.5, 15.5)], 1.1, 2.4),
    "c3": Crack([(25.5, 15.5), (27.4, 12.0), (29.0, 9.0)], 1.3, 2.8, ("in", "out")),
    "c4": Crack([(16.5, 17.5), (12.0, 21.0)], cut=False),
    "c5": Crack([(12.0, 21.0), (8.0, 20.4), (5.0, 20.2)], 1.0, 2.2, ("in", "out")),
    "trlow1": Crack([(25.5, 15.5), (29.4, 16.8), (33.0, 17.5)], 1.3, 2.8),
    "trlow2": Crack([(33.0, 17.5), (37.0, 17.0), (40.4, 16.6)], 1.1, 2.4, ("in", "out")),
    "c6": Crack([(25.5, 15.5), (27.0, 22.0), (27.0, 28.0)], 1.4, 3.0),
    "glleft": Crack([(12.0, 21.0), (11.0, 25.0), (12.0, 29.0)], cut=False),
    "glbc": Crack([(12.0, 29.0), (19.0, 29.6), (27.0, 28.0)], 1.0, 2.2),
    "leftll": Crack([(12.0, 29.0), (8.0, 30.0), (4.5, 30.5)], cut=False),
    "midright": Crack([(33.0, 17.5), (31.4, 24.0), (34.0, 30.5)], 1.4, 3.0),
    "midlr": Crack([(27.0, 28.0), (31.0, 30.0), (34.0, 30.5)], 1.2, 2.6),
    "rightlr": Crack([(34.0, 30.5), (38.0, 31.4), (42.0, 32.0)], cut=False),
    "bcll": Crack([(12.0, 29.0), (13.0, 34.0), (15.0, 39.0)], cut=False),
    "bcbot": Crack([(15.0, 39.0), (21.0, 38.6), (28.0, 37.5)], cut=False),
    "bclr": Crack([(27.0, 28.0), (27.6, 32.0), (28.0, 37.5)], 1.3, 2.8),
    "lrbot": Crack([(28.0, 37.5), (33.0, 39.6), (38.0, 39.0)], 1.0, 2.2, ("in", "out")),
    "llbot": Crack([(15.0, 39.0), (13.4, 40.4), (12.0, 41.5)], cut=False),
}
AST2_HAIRLINES = [
    Crack([(36.4, 20.0), (38.6, 23.0), (41.6, 24.6)], 0.45, 0.6),
    Crack([(20.0, 42.0), (24.0, 44.6), (26.0, 47.4)], 0.5, 0.7),
]


def spiral(c, r, outer, inner, turns, start, steps=40, squash=1.0):
    """Pixel corners along a spiral round (c, r) from radius outer to inner, turning counter-clockwise on
    the screen from the angle start (degrees, 0 to the right, 90 up the screen)."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = math.radians(start) + 2 * math.pi * turns * t
        rad = outer + (inner - outer) * t
        pts.append((c + rad * math.cos(a), r - rad * math.sin(a) * squash))
    return pts


AST2_BLOCKS = [
    Block("top", [(14.0, 11.0), (14.0, 6.0), (16.0, 5.0), (18.0, 4.0), (24.0, 4.0), (26.0, 5.0), (27.0, 6.0), (28.0, 7.0),
                  (29.0, 8.0), (29.0, 9.0)], ["c1", "c2", "c3"], [(21.0, 10.5, 11.2, -0.15, 0.35)], 0x09,
          cap=(21.2, 10.8, 10.5, 9.4, 15.0, -3.6, 24)),
    Block("tr", [(29.0, 9.0), (35.0, 9.0), (36.0, 10.0), (37.0, 11.0), (37.0, 13.6), (38.0, 14.0), (39.0, 15.0),
                 (40.0, 16.0)], ["c3", "trlow1", "trlow2"], [(32.5, 13.0, 9.8, 0.4, 0.3)], 0x06,
          cap=(32.6, 13.0, 10.5, 7.2, 13.5, -3.5, 20)),
    Block("ul", [(5.0, 20.2), (5.0, 14.0), (6.0, 13.0), (7.0, 12.0), (8.0, 11.0), (14.0, 11.0)], ["c1", "c4", "c5"],
          [(9.6, 15.4, 9.9, -0.45, 0.3)], 0x0b, cap=(9.6, 15.4, 8.2, 7.7, 13.0, -2.8, 18)),
    Block("glyph", [], ["c2", "c4", "c6", "glleft", "glbc"], [(18.6, 22.4, 12.8, -0.2, 0.12)], 0x0b,
          cap=(18.6, 22.4, 11.6, 11.0, 16.5, -3.5, 26)),
    Block("left", [(5.0, 20.2), (4.0, 21.0), (3.0, 22.0), (2.0, 23.0), (2.0, 27.5), (4.0, 28.0), (4.0, 29.5), (4.5, 30.5)],
          ["c5", "glleft", "leftll"], [(7.2, 25.4, 10.3, -0.5, 0.05)], 0x0b, cap=(7.2, 25.4, 8.2, 8.8, 13.0, -2.4, 18)),
    Block("midr", [], ["trlow1", "c6", "midright", "midlr"], [(29.8, 23.2, 8.2, 0.05, 0.05)], 0x06,
          cap=(29.8, 23.2, 7.2, 11.0, 11.5, -3.0, 18)),
    Block("right", [(40.0, 16.0), (40.0, 17.0), (44.0, 17.0), (44.0, 30.0), (43.0, 31.0), (42.0, 32.0)],
          ["trlow2", "midright", "rightlr"], [(37.6, 23.6, 10.8, 0.35, 0.05)], 0x08,
          cap=(37.6, 23.6, 9.4, 11.0, 14.0, -3.0, 21)),
    Block("bc", [], ["glbc", "bcll", "bcbot", "bclr"], [(19.6, 33.4, 11.8, -0.25, -0.1)], 0x0b,
          cap=(19.6, 33.4, 11.6, 9.4, 15.5, -3.4, 24)),
    Block("ll", [(4.5, 30.5), (5.0, 31.0), (6.0, 32.0), (7.0, 33.5), (8.0, 35.0), (9.0, 36.5), (10.0, 38.5),
                 (11.0, 40.5), (12.0, 41.5)], ["leftll", "bcll", "llbot"], [(9.4, 34.8, 9.7, -0.45, -0.25)], 0x08,
          cap=(9.4, 34.8, 8.2, 9.4, 12.5, -2.6, 18)),
    Block("lr", [(42.0, 32.0), (41.0, 33.0), (40.0, 34.0), (39.6, 36.0), (38.5, 37.0), (38.0, 38.0), (38.0, 39.0)],
          ["rightlr", "midlr", "bclr", "lrbot"], [(33.6, 34.4, 9.9, 0.35, -0.25)], 0x07,
          cap=(33.6, 34.4, 10.5, 8.2, 13.0, -2.8, 20)),
    Block("bottom", [(12.0, 41.5), (12.0, 42.5), (13.0, 44.0), (13.0, 45.0), (14.0, 46.0), (15.0, 47.0), (18.0, 48.0),
                     (19.0, 49.5), (24.0, 49.5), (26.0, 48.3), (29.0, 47.5), (32.0, 46.5), (35.0, 45.5), (38.0, 45.0),
                     (38.0, 39.0)], ["llbot", "bcbot", "lrbot"], [(25.0, 43.4, 9.2, 0.05, -0.45)], 0x06,
          cap=(25.0, 43.4, 16.5, 9.4, 13.0, -3.6, 26)),
]

SPECS = {
    "asteroid": {
        "prefix": "asteroid", "sprites": (7, 9, 45, 47), "blocks": AST1_BLOCKS, "cracks": AST1_CRACKS,
        "hairlines": AST1_HAIRLINES,
        "outer": [(0.0, 0.0), (0.5, 3.2), (1.5, 6.4), (3.0, 8.4), (4.6, 9.4)],
        "inner": [(0.0, 0.0), (0.15, 4.0), (0.5, 9.0), (1.1, 11.5), (2.0, 12.6)],
        "crack_shade": 0x04, "hairline_shade": 0x06, "cap": 0x05,
        # (column, row, radius, depth, grey)
        "bowls": [(19.6, 36.4, 3.0, 0.8, 0x08)],
        # (pixel corners, half width, height, grey)
        "ridges": [
            ([(34.0, 19.6), (34.2, 16.0), (35.4, 13.0), (38.0, 11.2), (41.0, 11.6), (43.0, 14.0), (43.0, 17.4),
              (41.4, 19.4), (39.0, 19.6), (37.0, 18.4)], 1.15, 0.75, 0x0a),
            ([(30.0, 22.0), (29.0, 25.0), (29.2, 28.2), (30.8, 30.4), (33.4, 30.6), (35.2, 29.0), (35.2, 26.6),
              (33.6, 25.4), (32.0, 26.2), (31.8, 27.8)], 1.0, 0.65, 0x0b),
            ([(22.6, 31.8), (19.0, 32.2), (16.4, 34.0), (15.4, 37.0), (16.2, 40.0), (18.6, 41.6), (21.6, 41.6),
              (23.6, 40.0)], 1.2, 0.75, 0x0b),
        ],
        # (column, row, radius, height, grey)
        "knobs": [(38.8, 15.6, 2.1, 1.3, 0x0a)],
    },
    "asteroid2": {
        "prefix": "asteroid2", "sprites": (1, 3, 39, 41), "blocks": AST2_BLOCKS, "cracks": AST2_CRACKS,
        "hairlines": AST2_HAIRLINES,
        "outer": [(0.0, 0.0), (0.5, 3.2), (1.5, 6.4), (3.0, 8.4), (4.6, 9.4)],
        "inner": [(0.0, 0.0), (0.15, 4.0), (0.5, 9.0), (1.1, 11.5), (2.0, 12.6)],
        "crack_shade": 0x04, "hairline_shade": 0x06, "cap": 0x05,
        # The hollow in the middle of the glyph's spiral, the hollow in the dark shoulder, pits in the dark
        # lower right.
        "bowls": [(18.2, 22.0, 1.3, 0.6, 0x06), (31.6, 12.8, 2.2, 0.8, 0x06),
                  (30.0, 42.4, 0.9, 0.4, 0x06), (33.8, 43.4, 0.7, 0.35, 0x06), (31.6, 40.4, 0.6, 0.3, 0x06)],
        "ridges": [
            # The glyph: a spiral, an ammonite carved in relief.
            (spiral(18.0, 22.4, 4.5, 2.0, 1.2, -95, squash=1.1), 0.85, 0.7, 0x0b),
            # The curl on the light lobe below the middle.
            ([(15.0, 32.4), (14.8, 35.6), (16.8, 37.8), (19.8, 37.8), (21.8, 35.8), (21.4, 33.4), (19.4, 32.6),
              (18.2, 34.2)], 1.0, 0.6, 0x0b),
        ],
        "knobs": [],
    },
}


def main():
    options = k.args()
    only = options["only"].split(",") if "only" in options else list(SPECS)
    for name in only:
        build(SPECS[name], options)


if __name__ == "__main__":
    main()
