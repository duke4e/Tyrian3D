"""What is left of SURFACE's stepped pyramid once it is destroyed (stage 4 of the clean ground: the wreck models that
stand in for the map's painting of it; sheet 3 sprites 153 and 155 above 191 and 193, and its capstone, sheet 3
sprite 3), built on polish_pyramid.py. models.cfg: model pyramid_153_wreck / pyramid_155_wreck / pyramid_191_wreck /
pyramid_193_wreck / pyramid_cap_wreck ... origin; wreck 3 153 pyramid_153_wreck (and 155, 191, 193), wreck 3 3
pyramid_cap_wreck. The game draws them where the maps paint the wreck (SURFACE and TIME WAR), with the live sprite
lines' options (yaw=0 height=-4), at the live pieces' places.

The painting (SURFACE's and TIME WAR's maps paint the same one, in the HD tiles and at 1x): the pyramid with its top
fallen in. Its flanks still stand, stepped as before (the left side's levels lit, the right side's in a mid shade),
and the base's dark front runs on below; but the top level and the capstone are gone, the middle is a crater of dark,
scorched rubble (columns 14-31 of rows 13-29 of the 48 x 56 picture, darkest in rows 18-25), its back is broken down
to the sand between columns 18 and 31 (the back edge there at rows 12-13 instead of 10), a heap of tumbled lighter
blocks lies along the crater's back (rows 12-17, columns 8-26), rubble spills over the front tread at columns 24-30
and down the base's front, and the base's front is sooted in its middle (columns 13-28). The painting lies one pixel
higher up the screen than the live sprites at every place the levels put the pyramid (the sprites are drawn one row
below their painting): the wreck is built on the live geometry moved up by PAINT_DY so that it lies where the
painting does (the pieces are still cut along the sprites' edges).

Built as the live pyramid (polish_pyramid.py's levels, masonry and joints, its materials) without its top level, then
broken: a crater cut into the levels by a cutter whose underside is a rough height field (a bowl with a jagged rim,
the back breached down to the sand behind a jagged line, steep broken walls; its faces the broken stone's material),
the masonry gone with the stone it lay on, the crater's floor sooted and the rim round it scorched, the base's front
sooted where the painting darkens it; tumbled blocks along the crater's back, rubble in it and spilling over the front,
a few embers in its floor glowing faintly in the stone's own gold (emission 0.3). The capstone's wreck (its own model,
at its own place, origin as the live capstone's) is the pyramidion broken in two and a few gold shards lying in the
rubble at the crater's back (the painting's light blocks there, columns 17-24 of rows 11-16): low in the crater, so
that inside a standing pyramid (the capstone shot away first) it is hidden.

Also here: the helpers the other wreck scripts of these buildings use (polish_block_house_wreck.py,
polish_glass_city_wreck.py, polish_window_block_wreck.py): value noise, a height-field cutter, rubble chunks and
blocks, faces dropped or refined, a canonical mesh order after booleans, triangulation before export.

Coordinates as polish_pyramid.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the sand; the
whole's origin is the corner where the four sprites meet; P(c, r) is a pixel edge of the 48 x 56 picture (column c,
row r), here of the painting (the live geometry moved up PAINT_DY).

Options after "--": --outdir <dir> (default assets/models/enemies), --check (the whole's silhouette against the
painting's own pixels, PAINTED below), --preview <prefix>, --only <model,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_pyramid as live  # noqa: E402


# --- Wreck helpers ------------------------------------------------------------------------------------------------

class Noise:
    """Value noise: smooth random values in -1..1 on a lattice `cell` units apart (deterministic for a seed)."""

    def __init__(self, seed, cell=1.0):
        rng = random.Random(seed)
        self.table = [rng.uniform(-1.0, 1.0) for _ in range(512)]
        self.perm = list(range(512))
        rng.shuffle(self.perm)
        self.cell = cell

    def lattice(self, i, j):
        return self.table[self.perm[(self.perm[i % 512] + j) % 512]]

    def __call__(self, x, y):
        x, y = x / self.cell, y / self.cell
        i, j = math.floor(x), math.floor(y)
        fx, fy = x - i, y - j
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a = self.lattice(i, j) + (self.lattice(i + 1, j) - self.lattice(i, j)) * sx
        b = self.lattice(i, j + 1) + (self.lattice(i + 1, j + 1) - self.lattice(i, j + 1)) * sx
        return a + (b - a) * sy

    def fbm(self, x, y, octaves=2):
        total, amp, norm = 0.0, 1.0, 0.0
        for o in range(octaves):
            total += amp * self(x * 2 ** o + 31.7 * o, y * 2 ** o - 17.3 * o)
            norm += amp
            amp *= 0.5
        return total / norm


def canonical(obj):
    """polish_powerups_specials.py's canonical(): the mesh rebuilt in a fixed order (vertices by position, faces by
    their corners), so that what an exact boolean returns in a changing order gives the same mesh every run."""
    me = obj.data

    def key(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    faces = []
    for poly in me.polygons:
        corners = [key(me.vertices[i].co) for i in poly.vertices]
        # (corners that the rounding merged are dropped; faces left with fewer than three go)
        corners = [c for i, c in enumerate(corners) if c != corners[i - 1]]
        if len(set(corners)) < 3 or len(set(corners)) != len(corners):
            continue
        start = corners.index(min(corners))
        faces.append((corners[start:] + corners[:start], poly.material_index))
    faces.sort()
    verts = sorted({c for corners, _ in faces for c in corners})
    index = {c: i for i, c in enumerate(verts)}
    mesh = bpy.data.meshes.new(me.name)
    mesh.from_pydata(verts, [], [[index[c] for c in corners] for corners, _ in faces])
    for mat in me.materials:
        mesh.materials.append(mat)
    for poly, (_, material) in zip(mesh.polygons, faces):
        poly.material_index = material
    mesh.validate()
    obj.data = mesh
    bpy.data.meshes.remove(me)
    return obj


def triangulate(objects):
    """Every face split into triangles the same way every run (bmesh's beauty split), each corner keeping the
    normal it had (as polish_k_pod.py's triangulate(); the triangulate modifier's keep_custom_normals crashed on
    broken pieces)."""
    for obj in objects:
        me = obj.data
        corner = {}
        for poly in me.polygons:
            for li in poly.loop_indices:
                corner[(poly.index, me.loops[li].vertex_index)] = tuple(me.corner_normals[li].vector)
        bm = bmesh.new()
        bm.from_mesh(me)
        layer = bm.faces.layers.int.new("source_face")
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            f[layer] = f.index
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
        bm.to_mesh(me)
        bm.free()
        me.validate()
        source = me.attributes["source_face"].data
        normals = []
        for poly in me.polygons:
            src = source[poly.index].value
            for li in poly.loop_indices:
                n = corner.get((src, me.loops[li].vertex_index))
                if n is None or not all(math.isfinite(v) for v in n) or Vector(n).length < 0.5:
                    n = tuple(poly.normal) if Vector(poly.normal).length > 0.5 else (0.0, 0.0, 1.0)
                normals.append(n)
        me.normals_split_custom_set(normals)
        me.attributes.remove(me.attributes["source_face"])
    return objects


def outline_radius(a, radii, power):
    """The radius of a superellipse (|x / rx|^p + |y / ry|^p = 1) in the direction a (radians)."""
    c, s = abs(math.cos(a)), abs(math.sin(a))
    return ((c / radii[0]) ** power + (s / radii[1]) ** power + 1e-12) ** (-1.0 / power)


class Hole:
    """A broken hole's outline: a superellipse round centre (x, y) with radii and power, its edge made jagged by
    noise along it (amp units in or out, `cell` units between bumps); one jag pattern for every height, so that the
    break's walls run straight down its jags."""

    def __init__(self, centre, radii, power, seed, amp=0.45, cell=1.1):
        self.centre, self.radii, self.power, self.amp = Vector(centre), radii, power, amp
        self.noise = Noise(seed, cell)

    def radius(self, a):
        r = outline_radius(a, self.radii, self.power)
        mean = (self.radii[0] + self.radii[1]) / 2
        return r + self.amp * self.noise.fbm(math.cos(a) * mean, math.sin(a) * mean, 3)

    def d(self, x, y):
        """How far (x, y) is from the middle, in the outline's radius there (1 on the edge)."""
        dx, dy = x - self.centre.x, y - self.centre.y
        return math.hypot(dx, dy) / max(self.radius(math.atan2(dy, dx)), 1e-6)

    def ring(self, z, scale, segments=160):
        out = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            r = self.radius(a) * scale
            out.append(Vector((self.centre.x + r * math.cos(a), self.centre.y + r * math.sin(a), z)))
        return out

    def cutter(self, name, levels, mat, step=None):
        """A cutter lofted through rings at levels [(z, scale), ...] from the bottom up (closed at both ends); its
        rings' points about `step` apart round the outline if given (160 points otherwise)."""
        segments = 160
        if step:
            segments = max(40, int(math.pi * (self.radii[0] + self.radii[1]) / step))
        rings = [self.ring(z, sc, segments) for z, sc in levels]
        return k.loft(name, rings, mat, start_point=(self.centre.x, self.centre.y, levels[0][0]),
                      end_point=(self.centre.x, self.centre.y, levels[-1][0]))


def line_cutter(name, points, side, z0, z1, mat, seed, amp=0.35, step=0.4):
    """A prism standing on a jagged broken edge: points [(x, y), ...] along it (the edge made jagged by noise, a
    point every `step`), closed by the points of `side` (beyond the edge, in order back to the first); from z0 to
    z1."""
    noise = Noise(seed, 1.0)
    edge = []
    for (xa, ya), (xb, yb) in zip(points, points[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) / step))
        for i in range(n):
            t = i / n
            x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
            nx, ny = -(yb - ya), xb - xa
            ln = math.hypot(nx, ny) or 1.0
            j = noise.fbm(x, y, 2) * amp
            edge.append((x + nx / ln * j, y + ny / ln * j))
    edge.append(points[-1])
    outline = edge + list(side)
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1]))
    if area < 0:
        outline = outline[::-1]
    return mk.prism(name, outline, z0, z1, mat)


def crack_cutter(name, start, heading, length, rng, mat, width=0.26, z0=-1.0, z1=30.0, step=0.45):
    """A crack: a thin prism along a wandering line from start (x, y) in the direction heading (radians), narrowing
    to its end, for cutting into a surface (from z0 up)."""
    pts, x, y, a = [], start[0], start[1], heading
    n = max(2, int(length / step))
    for i in range(n + 1):
        pts.append((x, y, width * (1 - 0.8 * i / n)))
        a += rng.uniform(-0.45, 0.45)
        x, y = x + math.cos(a) * step, y + math.sin(a) * step
    left, right = [], []
    for i, (x, y, w) in enumerate(pts):
        xa, ya, _ = pts[max(i - 1, 0)]
        xb, yb, _ = pts[min(i + 1, n)]
        dx, dy = xb - xa, yb - ya
        ln = math.hypot(dx, dy) or 1.0
        left.append((x - dy / ln * w / 2, y + dx / ln * w / 2))
        right.append((x + dy / ln * w / 2, y - dx / ln * w / 2))
    outline = left + right[::-1]
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(outline, outline[1:] + outline[:1]))
    return mk.prism(name, outline if area > 0 else outline[::-1], z0, z1, mat)


def heightfield_cutter(name, xs, ys, zmax, top, mat):
    """A solid over the grid xs x ys (sorted coordinates): from the height field z = zmax(x, y) up to z = top, for
    cutting away what lies above the field (exact boolean DIFFERENCE); its underside's triangles split the same way
    every time."""
    nx, ny = len(xs), len(ys)
    verts = [(x, y, zmax(x, y)) for y in ys for x in xs] + [(x, y, top) for y in ys for x in xs]
    off = nx * ny

    def at(i, j, upper=False):
        return j * nx + i + (off if upper else 0)
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, d = at(i, j), at(i + 1, j), at(i + 1, j + 1), at(i, j + 1)
            faces += [(a, c, b), (a, d, c)]
            faces.append((at(i, j, True), at(i + 1, j, True), at(i + 1, j + 1, True), at(i, j + 1, True)))
    border = [(i, 0) for i in range(nx - 1)] + [(nx - 1, j) for j in range(ny - 1)] + \
        [(i, ny - 1) for i in range(nx - 1, 0, -1)] + [(0, j) for j in range(ny - 1, 0, -1)]
    for q in range(len(border)):
        (i0, j0), (i1, j1) = border[q], border[(q + 1) % len(border)]
        faces.append((at(i0, j0), at(i1, j1), at(i1, j1, True), at(i0, j0, True)))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def grid(lo, hi, fine_lo, fine_hi, fine, coarse):
    """Grid coordinates from lo to hi: `fine` apart within fine_lo..fine_hi, `coarse` apart outside."""
    out = []
    v = lo
    while v < fine_lo - 1e-6:
        out.append(v)
        v += coarse
    v = fine_lo
    while v < fine_hi - 1e-6:
        out.append(v)
        v += fine
    v = fine_hi
    while v < hi - 1e-6:
        out.append(v)
        v += coarse
    out.append(hi)
    return sorted(set(round(x, 4) for x in out))


class FaceNormals:
    """An uncut object's shading, looked up at a point of its surface for a face of a given direction: among its
    triangles within reach of the point, the one facing most nearly that way (so that the slivers a break leaves
    along its edges take the shading of their own face, not of the break's)."""

    def __init__(self, obj):
        from mathutils.bvhtree import BVHTree
        mesh = obj.data
        mesh.calc_loop_triangles()
        self.verts = [v.co.copy() for v in mesh.vertices]
        self.tris = [(tuple(t.vertices), tuple(t.loops), t.normal.copy()) for t in mesh.loop_triangles]
        self.normals = [n.vector.copy() for n in mesh.corner_normals]
        self.bvh = BVHTree.FromPolygons(self.verts, [t[0] for t in self.tris])

    def normal(self, co, facing):
        best, score = None, -2.0
        for _, _, index, _ in self.bvh.find_nearest_range(co, 0.02):
            if index is not None and self.tris[index][2].dot(facing) > score:
                best, score = index, self.tris[index][2].dot(facing)
        if best is None or score < 0.5:
            return None
        (ia, ib, ic), (la, lb, lc), _ = self.tris[best]
        w = mk.barycentric(co, self.verts[ia], self.verts[ib], self.verts[ic])
        n = self.normals[la] * w[0] + self.normals[lb] * w[1] + self.normals[lc] * w[2]
        return n.normalized() if n.length > 1e-8 else None


def cut_piece(source, box_xy, cap_mat):
    """polish_arch.py's cut() (the part of an object inside box (x0, x1, y0, y1), its cuts closed with flat caps of
    cap_mat, its normals the uncut object's), its normals looked up with FaceNormals. None if nothing is inside."""
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
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    shading = FaceNormals(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.normal)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def sharp_between_materials(obj):
    """Marks the edges between faces of different materials sharp, so that a break's faces don't smooth the faces
    they cut (their shading kept apart)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.link_faces[0].material_index != e.link_faces[1].material_index:
            e.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def break_with(objects, cutter):
    """Cuts the cutter's volume out of each object (exact booleans; the broken faces take the cutter's material),
    the results in canonical order, the edges between materials sharp; the cutter is removed afterwards. Objects left
    empty are removed; returns the rest."""
    kept = []
    for obj in objects:
        mk.boolean(obj, cutter, "DIFFERENCE", keep=True)
        if len(obj.data.polygons) == 0:
            bpy.data.objects.remove(obj)
            continue
        canonical(obj)
        sharp_between_materials(obj)
        kept.append(obj)
    data = cutter.data
    bpy.data.objects.remove(cutter)
    bpy.data.meshes.remove(data)
    return kept


def drop_faces(obj, gone):
    """Deletes the faces whose centre is gone(centre) (thin strips lying on broken stone); removes the object if
    nothing is left. Returns the object or None."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    dead = [f for f in bm.faces if gone(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    if len(obj.data.polygons) == 0:
        bpy.data.objects.remove(obj)
        return None
    return obj


def refine(obj, box, step, which=None):
    """Splits the faces lying in box (x0, x1, y0, y1) (those which(face) accepts, a BMFace, if given) along a grid
    `step` apart, so that they can be painted in smaller patches (scorch)."""
    x0, x1, y0, y1 = box
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for axis in (0, 1):
        lo, hi = (x0, x1) if axis == 0 else (y0, y1)
        v = math.ceil(lo / step) * step
        while v < hi:
            faces = [f for f in bm.faces if x0 <= f.calc_center_median().x <= x1 and
                     y0 <= f.calc_center_median().y <= y1 and (which is None or which(f))]
            if faces:
                edges = list({e for f in faces for e in f.edges})
                verts = list({vv for f in faces for vv in f.verts})
                co = (v, 0, 0) if axis == 0 else (0, v, 0)
                no = (1, 0, 0) if axis == 0 else (0, 1, 0)
                bmesh.ops.bisect_plane(bm, geom=verts + edges + faces, dist=1e-5, plane_co=co, plane_no=no)
            v += step
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def hull(name, points, mat):
    """The convex hull of some points: a rubble chunk."""
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mk._link(name, mesh, mat)


def chunk(name, centre, size, rng, mat, flat=0.7, points=11):
    """A broken chunk of stone or metal about size across, flatter than wide (flat), its bottom on centre's z: the
    hull of random points in a squashed ball, turned at random about the vertical."""
    cx, cy, cz = centre
    a0 = rng.uniform(0, 2 * math.pi)
    pts = []
    for i in range(points):
        u = rng.uniform(-1, 1)
        a = a0 + 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / points
        r = math.sqrt(1 - u * u) * rng.uniform(0.75, 1.0)
        pts.append(Vector((r * math.cos(a) * size / 2, r * math.sin(a) * size / 2 * rng.uniform(0.7, 1.0),
                           (u + 1) / 2 * size * flat)))
    obj = hull(name, [p + Vector((cx, cy, cz)) for p in pts], mat)
    return obj


def block(name, centre, size, rot, mat, bevel=0.15, sink=0.25):
    """A tumbled block (a bevelled box of size (w, d, h), turned by rot (degrees about x, y, z)), its lowest corner
    sunk `sink` into whatever it rests on at centre's z."""
    w, d, h = size
    obj = mk.box(name, -w / 2, w / 2, -d / 2, d / 2, -h / 2, h / 2, mat)
    if bevel > 0:
        mk.bevel(obj, bevel, 1, 35)
    obj.data.transform(Euler([math.radians(a) for a in rot]).to_matrix().to_4x4())
    low = min(v.co.z for v in obj.data.vertices)
    obj.data.transform(Matrix.Translation(Vector(centre) + Vector((0, 0, -low - sink))))
    return obj


def emissive(name, index, strength, metallic=0.0, roughness=0.4):
    """An ember's material: the palette index, glowing in its own colour."""
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=k.level_palette()[index],
                      emission_strength=strength)


# --- The pyramid's wreck ------------------------------------------------------------------------------------------

P = live.P
PAINT_DY = 1.0                         # the painting lies this much higher up the screen than the live sprites
SEED = 153
# The crater: its middle and radii (columns, rows of the painting), its floor's height in the middle and at its rim,
# how steeply its walls rise beyond the rim.
BOWL = (22.6, 21.2, 8.3, 8.6)
BOWL_POWER = 3.0                       # (squarish: the flanks stand straight either side of it)
FLOOR = 4.0                            # its floor (under the rubble)
# Its walls: (height, the outline's scale) from the floor up (battered: they catch the light).
WALLS = [(FLOOR, 0.78), (FLOOR + 1.6, 0.88), (8.0, 0.97), (11.5, 1.02), (16.0, 1.05)]
# The back's broken edge: (column, row) of the painting; behind it (smaller rows) everything is gone down to BACK_Z.
BACK_LINE = [(7.5, -6.0), (8.0, 5.8), (11.5, 5.8), (12.4, 6.9), (12.9, 7.9), (15.6, 8.1), (16.4, 9.1), (17.0, 9.9),
             (17.6, 10.3), (18.2, 11.9), (25.6, 12.1), (26.3, 13.0), (31.6, 13.0), (32.2, 12.0), (32.8, 9.6),
             (33.4, 8.6), (34.0, 7.9), (37.8, 7.9), (38.3, 9.9), (41.0, 9.9), (41.5, -6.0)]
# Cracks from the rim: (column, row) where they start, heading (degrees, 0 to the right, 90 up the screen), length,
# the height they are cut down to.
CRACKS = [(14.6, 24.5, 200, 4.5, 6.3), (16.0, 28.6, 235, 4.0, 3.2), (24.0, 30.0, 262, 5.5, 3.0),
          (30.4, 26.8, 320, 3.5, 6.4), (30.8, 17.0, 10, 3.0, 9.6), (13.8, 15.5, 165, 3.2, 9.6),
          (20.5, 30.2, 250, 3.0, 6.6)]
BACK_Z = -0.5                          # (under the terrain: the sand shows)
# The base's sooted front (columns) and the soot's lowest height on it.
SOOT_FRONT = (12.5, 28.5, 1.6)
# The tumbled blocks along the crater's back: (column, row, (w, d, h), (rx, ry, rz), shade).
BLOCKS = [(17.6, 13.2, (3.0, 2.2, 1.9), (14, -18, 25), "lit"), (20.4, 12.6, (3.2, 2.4, 2.0), (-10, 12, -8), "tread"),
          (23.2, 13.1, (2.8, 2.0, 1.8), (20, 8, 34), "lit"), (26.0, 13.8, (2.6, 2.2, 1.7), (-16, -22, -20), "tread"),
          (15.8, 15.6, (2.4, 1.8, 1.6), (8, 26, 52), "mid"), (21.7, 15.6, (2.2, 1.8, 1.5), (-24, 6, 12), "lit"),
          (28.6, 14.6, (2.2, 1.7, 1.4), (12, -14, -40), "mid"), (18.8, 17.4, (1.9, 1.5, 1.3), (30, -10, 70), "tread")]
HEAP, HEAP_STEP, HEAP_TOP = 0.98, 2.1, 0.72   # the heap of stones in the crater: how far out (its radii)
SPILL = [(24.6, 28.0), (26.2, 27.4), (27.8, 28.6), (25.2, 30.4), (27.0, 31.2), (28.6, 30.2), (25.8, 33.2),
         (27.6, 34.0), (26.4, 36.3), (27.4, 37.6), (24.2, 34.6), (29.4, 33.0)]   # rubble spilling over the front
EMBERS = [(20.5, 21.8), (24.6, 20.4), (22.8, 24.3), (18.6, 23.6), (26.2, 23.0)]
# The capstone's wreck: where its pieces lie (columns, rows of the painting).
# Two quarters of its foot: (the side of the axis kept, their turn, where, how deep they are sunk); its tip; its plinth.
CAP_QUARTERS = [((-1, -1), (8.0, -14.0, 40.0), (18.4, 15.0), 1.5), ((1, 1), (-10.0, 12.0, 205.0), (22.8, 17.0), 1.7)]
CAP_TIP_AT = (25.0, 14.0)
CAP_SLAB_AT = (16.4, 13.6)
CAP_SHARDS = [(17.4, 11.9), (24.6, 14.9), (21.2, 16.2), (16.6, 14.2)]

# The painting's own pixels (its 48 x 56 picture; the sand left out): the wreck's silhouette is checked against it.
PAINTED = """
............#...................................
................................................
........####....................................
........#####...............#...................
......##########..................####..........
.....############................#####..........
..################...............########.......
..################...............########.......
..########################......#########.......
"""  # rows 4-12; rows 13-41 are columns 2-40 whole (row 27 but column 28)


def painted_mask():
    rows = [[False] * 48 for _ in range(56)]
    lines = PAINTED.strip("\n").split("\n")
    for i, line in enumerate(lines):
        rows[4 + i] = [ch == "#" for ch in line]
    for r in range(13, 42):
        rows[r] = [2 <= c <= 40 and not (r == 27 and c == 28) for c in range(48)]
    return rows


def col_row(x, y):
    """The painting's column and row (pixel edges) of a point."""
    return x + 24.0, 28.0 - y


def interp(points, c):
    for (c0, r0), (c1, r1) in zip(points, points[1:]):
        if c0 <= c <= c1:
            return r0 + (r1 - r0) * (c - c0) / max(c1 - c0, 1e-6)
    return -6.0


HOLE = Hole(P(BOWL[0], BOWL[1]), (BOWL[2], BOWL[3]), BOWL_POWER, SEED, 0.5, 1.0)
NOISE_C = Noise(SEED + 2, 2.4)


def bowl_d(c, r):
    """How far a point is from the crater's middle, in its outline's radius (1 on its jagged rim)."""
    return HOLE.d(*P(c, r))


def gone(co):
    """Whether a point of the live pyramid is in what the crater and the breach take away."""
    c, r = col_row(co.x, co.y)
    if r < interp(BACK_LINE, c) + 0.3:
        return True
    return co.z > FLOOR + 0.05 and bowl_d(c, r) < 1.04


def materials():
    m = live.materials()
    m["break"] = k.material("pyr_break", palette=0x16, metallic=0.25, roughness=0.7)
    m["soot"] = k.material("pyr_soot", palette=0x13, metallic=0.1, roughness=0.85)
    m["scorch"] = k.material("pyr_scorch", palette=0x17, metallic=0.3, roughness=0.55)
    m["ember"] = emissive("pyr_ember", 0x1c, 0.3, 0.2, 0.4)
    return m


def build_whole(m):
    """The live pyramid without its top level, moved up PAINT_DY, broken; its rubble and embers."""
    z0 = 0.0
    stone, strips = [], []
    for i, spec in enumerate(live.LEVELS[:3]):
        stone.append(live.level(i, spec, z0, m))
        strips.append(live.courses(i, spec, z0, m))
        strips += live.joints(i, spec, live.LEVELS[i + 1], m)
        z0 = spec[7]
    for obj in stone + strips:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((0.0, PAINT_DY, 0.0)))
    # One body of stone (the levels overlap below their treads: cut apart, their crater floors would lie on each
    # other).
    body = stone[0]
    mk.boolean(body, stone[1:], "UNION")
    stone = [canonical(body)]
    crater = HOLE.cutter("crater", WALLS, m["break"])
    stone = break_with(stone, crater)
    back = [P(c, r) for c, r in BACK_LINE]
    side = [P(BACK_LINE[-1][0], -8.0), P(BACK_LINE[0][0], -8.0)]
    breach = line_cutter("breach", back, side, BACK_Z, 30.0, m["break"], SEED + 4)
    stone = break_with(stone, breach)
    # Cracks running out from the rim over the treads (cut a little into them: their walls soot-dark).
    rng = random.Random(SEED + 9)
    for i, (c, r, heading, length, depth) in enumerate(CRACKS):
        x, y = P(c, r)
        crack = crack_cutter(f"crack{i}", (x, y), math.radians(heading), length, rng, m["soot"],
                             z0=depth, z1=30.0)
        stone = break_with(stone, crack)
    for obj in stone:
        k.smooth(obj, 35)
    # The masonry on what is gone goes with it.
    strips = [s for s in (drop_faces(s, gone) for s in strips) if s is not None]
    scorch(stone, m)
    bpy.context.view_layer.update()
    rubble(stone, m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, stone


def scorch(stone, m):
    """The crater's floor sooted, the stone round its rim scorched, the base's front sooted in its middle."""
    bx0, by1 = P(BOWL[0] - BOWL[2] * 1.45, BOWL[1] - BOWL[3] * 1.45)
    bx1, by0 = P(BOWL[0] + BOWL[2] * 1.45, BOWL[1] + BOWL[3] * 1.45)
    fx0, fy1 = P(SOOT_FRONT[0] - 1, 34.5)
    fx1, fy0 = P(SOOT_FRONT[1] + 1, 43.0)
    soot_noise = Noise(SEED + 5, 1.3)
    for obj in stone:
        broken = mk.slot_of(obj, m["break"])

        def big(f, top):
            return f.material_index != broken and f.calc_area() > 1.2 and (f.normal.z > 0.5 if top else f.normal.y < -0.3)
        refine(obj, (bx0, bx1, by0, by1), 1.0, lambda f: big(f, True))
        refine(obj, (fx0, fx1, fy0, fy1), 1.0, lambda f: big(f, False))
        k.smooth(obj, 35)

        def pick(co, n):
            c, r = col_row(co.x, co.y)
            d = bowl_d(c, r)
            if d < 0.95 and co.z < FLOOR + 0.1:
                return m["soot"]
            if d < 1.32 + soot_noise(c, r) * 0.12 and n.z > 0.5:
                return m["scorch"]
            if (SOOT_FRONT[0] + soot_noise(c, 0) < c < SOOT_FRONT[1] + soot_noise(c, 9) and r > 34.5 and
                    n.y < -0.4 and co.z > SOOT_FRONT[2] + soot_noise(c, 3) * 0.6):
                return m["scorch"]
            return None
        mk.paint(obj, pick)


def rubble(stone, m):
    """The tumbled blocks along the crater's back, a heap of rubble filling it (darker towards its middle, dark gaps
    between the stones) and spilling over the front, embers among the stones."""
    rng = random.Random(SEED)
    hit = mk.surface(stone)

    def ground(c, r):
        x, y = P(c, r)
        h = hit(x, y)
        return Vector((x, y, h[0].z if h else 0.0))
    shades = {"lit": m["west"], "tread": m["tread"], "mid": m["north"]}
    for i, (c, r, size, rot, shade) in enumerate(BLOCKS):
        mk.shade(block(f"tumbled{i}", ground(c, r), size, rot, shades[shade], 0.18, 0.35), 35)
    # The heap: dressed stones and broken ones on a jittered grid over the crater, a second layer on the first
    # towards its middle; darker in its depths, lit on top.
    layers = [(HEAP, HEAP_STEP, (m["break"], m["south"], m["north"], m["soot"], m["break"], m["tread"])),
              (HEAP_TOP, HEAP_STEP * 1.15, (m["tread"], m["north"], m["west"], m["tread"], m["east"], m["south"]))]
    n = 0
    for layer, (reach, step, mats) in enumerate(layers):
        if layer:
            hit = mk.surface(stone + [o for o in mk.meshes() if o.name.startswith(("heap", "tumbled"))])
        c = BOWL[0] - BOWL[2] + step * 0.5 * layer
        while c <= BOWL[0] + BOWL[2]:
            r = BOWL[1] - BOWL[3] + step * 0.5 * layer
            while r <= BOWL[1] + BOWL[3]:
                cc, rr = c + rng.uniform(-0.8, 0.8), r + rng.uniform(-0.8, 0.8)
                d = bowl_d(cc, rr)
                dressed, keep = rng.random() < 0.5, rng.random() > 0.1
                w, dd, h = rng.uniform(1.8, 3.0), rng.uniform(1.3, 2.1), rng.uniform(0.9, 1.5)
                rot = (rng.uniform(-35, 35), rng.uniform(-35, 35), rng.uniform(0, 180))
                if d < reach and keep:
                    mat = mats[n % 6]
                    at = ground(cc, rr)
                    if dressed:
                        mk.shade(block(f"heap{n}", at, (w, dd, h), rot, mat, 0.14, rng.uniform(0.4, 0.75)), 35)
                    else:
                        chunk(f"heap{n}", at - Vector((0, 0, rng.uniform(0.35, 0.6))), w * 1.05, rng, mat,
                              rng.uniform(0.45, 0.7))
                    n += 1
                r += step
            c += step
    for i, (c, r) in enumerate(SPILL):
        mat = (m["south"], m["tread"], m["break"], m["east"])[i % 4]
        chunk(f"spill{i}", ground(c, r) - Vector((0, 0, 0.2)), rng.uniform(0.9, 1.7), rng, mat, rng.uniform(0.55, 0.8))
    for i, (c, r) in enumerate(EMBERS):
        chunk(f"ember{i}", ground(c, r) - Vector((0, 0, 0.1)), rng.uniform(0.5, 0.75), rng, m["ember"], 0.6, 8)


# --- The capstone's wreck -----------------------------------------------------------------------------------------

def cap_wreck(stone):
    """The pyramidion broken in two and some shards, in the cap's own frame (its sprite's centre at the origin),
    lying in the rubble at the crater's back."""
    gold = k.material("cap_gold", palette=0x1a, metallic=0.3, roughness=0.35)
    tip = k.material("cap_tip_dull", palette=0x1c, metallic=0.35, roughness=0.3)
    plinth = k.material("cap_plinth", palette=0x15, metallic=0.4, roughness=0.4)
    broken = k.material("cap_break", palette=0x14, metallic=0.2, roughness=0.7)
    sooted = k.material("cap_soot", palette=0x16, metallic=0.3, roughness=0.55)
    hit = mk.surface(stone)
    rng = random.Random(SEED + 3)
    cx, cy = live.CAP_CENTRE   # the capstone's origin in the whole (where the levels put it; the painting's frame)
    bw, bh = live.CAP_BODY
    made = []

    def rest(obj, c, r, rot, sink):
        """Turns a part by rot and sets it down at the painting's (c, r), in the cap's frame."""
        obj.data.transform(Euler([math.radians(a) for a in rot]).to_matrix().to_4x4())
        x, y = P(c, r)
        h = hit(x, y)
        low = min(v.co.z for v in obj.data.vertices)
        obj.data.transform(Matrix.Translation((x - cx, y - cy, (h[0].z if h else 0.0) - low - sink)))
        made.append(obj)

    def pyramidion(name, z_lo, z_hi, slant, quarter=None):
        """The part of the pyramidion between two heights (its base at z 0), the upper cut slanted (a break); a
        quarter of it (quarter (sx, sy): the side of its axis kept) if given."""
        bm = bmesh.new()
        base = [bm.verts.new((sx * bw, sy * bw, 0.0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        apex = bm.verts.new((0.0, 0.0, bh))
        for i in range(4):
            bm.faces.new((base[i], base[(i + 1) % 4], apex))
        bm.faces.new(list(reversed(base)))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = mk._link(name, mesh, gold)
        mk.bevel(obj, 0.2, 2, 30)
        planes = []
        cuts = [((0.0, 0.0, z_hi), (slant, 0.25, 1.0)), ((0.0, 0.0, z_lo), (0.0, 0.0, -1.0))]
        if quarter:
            cuts += [((0.1 * quarter[0], 0.0, 0.0), (-quarter[0], 0.12, 0.0)),
                     ((0.0, -0.1 * quarter[1], 0.0), (-0.1, -quarter[1], 0.0))]
        for co, no in cuts:
            if co[2] is None:
                continue
            co, no = Vector(co), Vector(no).normalized()
            planes.append((co, no))
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                         plane_no=no, clear_outer=True)
            edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and len(e.link_faces) == 1]
            if edges:
                bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(obj.data)
            bm.free()
        k.smooth(obj, 30)
        noise = Noise(SEED + 7, 1.2)
        for poly in obj.data.polygons:
            c = Vector(poly.center)
            if any(abs((c - co).dot(no)) < 0.02 and Vector(poly.normal).dot(no) > 0.95 for co, no in planes):
                poly.material_index = mk.slot_of(obj, broken)   # the break
                poly.use_smooth = False
            elif poly.normal.z < -0.97 and c.z < 0.05:
                poly.material_index = mk.slot_of(obj, plinth)   # its foot, torn off the plinth
            elif c.z > bh * live.CAP_TIP:
                poly.material_index = mk.slot_of(obj, tip)
            elif noise(c.x, c.y + c.z) > 0.35:
                poly.material_index = mk.slot_of(obj, sooted)
        return obj

    # Two quarters of its foot, its tip, a piece of its plinth.
    for i, (quarter, rot, (c, r), sink) in enumerate(CAP_QUARTERS):
        part = pyramidion(f"cap_quarter{i}", None, bh * 0.42, 0.3, quarter)
        rest(part, c, r, rot, sink)
    upper = pyramidion("cap_upper", bh * 0.5, None, 0.0)
    upper.data.transform(Matrix.Translation((0, 0, -bh * 0.5)))
    rest(upper, CAP_TIP_AT[0], CAP_TIP_AT[1], (72.0, 8.0, -38.0), 0.5)
    slab = block("cap_plinth_slab", (0, 0, 0), (3.6, 2.4, 0.55), (0, 0, 0), plinth, 0.15, 0.0)
    rest(slab, CAP_SLAB_AT[0], CAP_SLAB_AT[1], (-14.0, 10.0, 18.0), 0.3)
    for i, (c, r) in enumerate(CAP_SHARDS):
        shard = chunk(f"cap_shard{i}", (0, 0, 0), rng.uniform(0.9, 1.5), rng, (gold, sooted, gold, broken)[i], 0.45, 8)
        shard.data.polygons.foreach_set("use_smooth", [False] * len(shard.data.polygons))
        rest(shard, c, r, (rng.uniform(-30, 30), rng.uniform(-30, 30), 0.0), 0.15)
    return made


# --- Build --------------------------------------------------------------------------------------------------------

PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole, stone = build_whole(m)
    print("whole pyramid wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        mk.compare("whole wreck (the painting's own pixels)", mk.coverage(whole, 48, 56), painted_mask())
    if "preview" in options:
        mk.preview(options["preview"] + "pyramid_wreck_whole", whole, size=(48, 56), scale=8, distance=1.8)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut_piece(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        triangulate(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False
    if not only or "pyramid_cap_wreck" in only:
        for src in whole:
            src.hide_render = True
        parts = cap_wreck(stone)
        for obj in parts:
            mk.apply(obj)
        triangulate(parts)
        bpy.context.view_layer.update()
        mk.report("pyramid_cap_wreck", parts, os.path.join(out, "pyramid_cap_wreck.glb"))
        if "preview" in options:
            mk.preview(options["preview"] + "pyramid_cap_wreck", parts, size=(12, 14), scale=24)


if __name__ == "__main__":
    build()
