"""Helpers shared by the hard-surface machines polished in round 5 (2026-10-18): polish_arm_bridge.py,
polish_twin_panel.py, polish_orb_tower.py, polish_green_scarab.py, polish_redgem_panel.py and
polish_disc_turret.py. Not a model script itself.

Their bodies are built as a CAD modeller builds them: polygons extruded along an axis (prism: a plan
extruded up, a side or front profile extruded across; wedge: a plan under a sloping top),
intersected and cut by Blender's exact booleans, their edges rounded by a bevel and their shading
kept flat on flat faces (weighted normals); or, where the upscales paint the steel soft and
rounded all over, remeshed and smoothed (soften). Grooves, vents and sockets are cut into them;
small parts (balls, domes, knobs, lamps, ribs laid on a surface) are lathed or lofted with tyrkit.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a
2x2 sprite's column c and row r are x = c + 0.5 - 12, y = 13.5 - r (its origin is its pixel 12, 14).

Also here: the silhouette checks (a top view's coverage against a mask of the sprite's pixels, which
the scripts write out, the ground and shadows painted into ground sprites left out), the cut of
an object built whole into the pieces the levels draw from several sprites (polish_redjet.py's
method: the pieces keep the whole's shading across the cuts), previews and the export.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402
from glb_winding import reverse_winding  # noqa: E402

DEFAULT_OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies")


# --- Numbers -------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)






def chaikin(points, iterations=2, closed=True):
    """Rounds a polygon's corners (straight runs stay straight)."""
    pts = [tuple(p) for p in points]
    for _ in range(iterations):
        out = [] if closed else [pts[0]]
        count = len(pts) if closed else len(pts) - 1
        for i in range(count):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            out.append(tuple(0.75 * a + 0.25 * b for a, b in zip(p, q)))
            out.append(tuple(0.25 * a + 0.75 * b for a, b in zip(p, q)))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts




def rounded_rect_distance(x, y, hw, hh, r):
    """Signed distance from (x, y) to a rectangle |x| <= hw, |y| <= hh whose corners are rounded
    with radius r (negative inside)."""
    qx, qy = abs(x) - (hw - r), abs(y) - (hh - r)
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r


def ray_to(distance, theta, reach=100.0):
    """How far the ray from the origin at angle theta goes before distance(x, y) turns positive."""
    lo, hi = 0.0, reach
    c, s = math.cos(theta), math.sin(theta)
    for _ in range(40):
        mid = (lo + hi) / 2
        if distance(mid * c, mid * s) < 0:
            lo = mid
        else:
            hi = mid
    return lo


def rounded_rect_ring(centre, hw, hh, r, z, segments=96):
    """Points round a rounded rectangle (on rays from its centre at equal angles), at height z."""
    r = max(0.02, min(r, hw - 1e-3, hh - 1e-3))
    pts = []
    for j in range(segments):
        theta = 2 * math.pi * j / segments
        d = ray_to(lambda x, y: rounded_rect_distance(x, y, hw, hh, r), theta, hw + hh)
        pts.append(Vector((centre[0] + d * math.cos(theta), centre[1] + d * math.sin(theta), z)))
    return pts


def split_along(bm, values, threshold):
    """Cuts a bmesh's faces along the contour where the vertex values (a dict) cross threshold, so
    that the materials on either side meet along a smooth line rather than along the faces' edges
    (polish_sphere_nozzle.py's). The new vertices get the threshold as their value."""
    made = set()
    for e in list(bm.edges):
        a, b = e.verts
        fa, fb = values[a], values[b]
        if (fa - threshold) * (fb - threshold) < 0:
            _, v = bmesh.utils.edge_split(e, a, (threshold - fa) / (fb - fa))
            values[v] = threshold
            made.add(v)
    for f in list(bm.faces):
        ends = [v for v in f.verts if v in made]
        if len(ends) == 2 and not any(ends[1] in e.verts for e in ends[0].link_edges):
            bmesh.utils.face_split(f, ends[0], ends[1])
    return made


# --- Solids --------------------------------------------------------------------------------------

def _link(name, mesh, mat):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def prism(name, outline, a0, a1, mat=None, axis="z"):
    """A polygon extruded along an axis from a0 to a1: outline [(u, v), ...] lies in the plane of
    the two other axes, (x, y) for axis z, (y, z) for axis x, (x, z) for axis y. Outlines may be
    concave; the faces stay n-gons (for booleans and bevels)."""
    def place(u, v, w):
        return (u, v, w) if axis == "z" else (w, u, v) if axis == "x" else (u, w, v)
    bm = bmesh.new()
    lo = [bm.verts.new(place(u, v, a0)) for u, v in outline]
    hi = [bm.verts.new(place(u, v, a1)) for u, v in outline]
    bm.faces.new(lo)
    bm.faces.new(hi)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return _link(name, mesh, mat)


def box(name, x0, x1, y0, y1, z0, z1, mat=None):
    return prism(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mat)


def wedge(name, outline, z0, top, mat=None, bottom=None):
    """A plan extruded up from z0 (or bottom(x, y)) to a top given as a function top(x, y) (a plane
    keeps its faces flat): blocks with sloping tops, blades, keels."""
    obj = prism(name, outline, 0.0, 1.0, mat)
    for v in obj.data.vertices:
        if v.co.z > 0.5:
            v.co.z = top(v.co.x, v.co.y)
        else:
            v.co.z = bottom(v.co.x, v.co.y) if bottom else z0
    obj.data.update()
    return obj


def plane(p0, p1, p2):
    """The plane through three points (x, y, z), as a function z(x, y)."""
    a, b, c = Vector(p0), Vector(p1), Vector(p2)
    n = (b - a).cross(c - a)
    return lambda x, y: a.z - (n.x * (x - a.x) + n.y * (y - a.y)) / n.z


def apply(obj):
    """Applies an object's modifiers to its mesh."""
    if not obj.modifiers:
        return obj
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    old = obj.data
    obj.modifiers.clear()
    obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


def boolean(obj, other, operation="INTERSECT", keep=False):
    """obj intersected with (or joined to, or cut by: UNION, DIFFERENCE) other, applied. Faces
    coming from other keep its materials. other is removed unless keep."""
    others = other if isinstance(other, (list, tuple)) else [other]
    for o in others:
        o.hide_render = True
        mod = obj.modifiers.new("boolean", "BOOLEAN")
        mod.operation = operation
        mod.solver = "EXACT"
        mod.material_mode = "TRANSFER"
        mod.object = o
        apply(obj)
        if not keep:
            data = o.data
            bpy.data.objects.remove(o)
            if data.users == 0:
                bpy.data.meshes.remove(data)
        else:
            o.hide_render = False
    return obj


def cleanup(obj, merge=1e-4, dissolve=0.5):
    """Merges doubles and dissolves needless edges between coplanar faces (after booleans)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    if dissolve > 0:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(dissolve), use_dissolve_boundaries=False,
                                 verts=bm.verts, edges=bm.edges, delimit={"MATERIAL"})
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def bevel(obj, width, segments=3, angle=35.0, profile=0.5):
    """Rounds the edges sharper than angle (degrees), applied."""
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle)
    mod.profile = profile
    mod.use_clamp_overlap = True
    mod.miter_outer = "MITER_ARC"
    apply(obj)
    return obj


def soften(obj, voxel=0.25, iterations=8, factor=0.6, ratio=None, angle=180.0):
    """Rounds every edge of a closed hard-surface body softly, as the 4x upscales paint them: a voxel
    remesh (voxel pixels), smoothed (iterations of factor; more rounds wider), decimated to ratio of
    its triangles, shaded smooth (edges sharper than angle kept)."""
    remesh = obj.modifiers.new("remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = voxel
    smooth = obj.modifiers.new("smooth", "SMOOTH")
    smooth.factor = factor
    smooth.iterations = iterations
    apply(obj)
    if ratio is not None:
        decimate = obj.modifiers.new("decimate", "DECIMATE")
        decimate.ratio = ratio
        apply(obj)
    return k.smooth(obj, angle)


def shade(obj, angle=40.0, weighted=True):
    """Smooth shading across edges flatter than angle; with weighted, the large flat faces keep
    flat normals next to their rounded edges (weighted normals, applied)."""
    k.smooth(obj, angle)
    if weighted:
        mod = obj.modifiers.new("weighted", "WEIGHTED_NORMAL")
        mod.mode = "FACE_AREA"
        mod.weight = 50
        mod.keep_sharp = True
        apply(obj)
    return obj


def slot_of(obj, mat):
    names = [m.name for m in obj.data.materials]
    if mat.name not in names:
        obj.data.materials.append(mat)
        names.append(mat.name)
    return names.index(mat.name)


def paint(obj, pick):
    """Gives faces materials: pick(centre, normal) returns a material, or None to keep the face's."""
    slots = {}
    for poly in obj.data.polygons:
        mat = pick(poly.center, poly.normal)
        if mat is not None:
            if mat.name not in slots:
                slots[mat.name] = slot_of(obj, mat)
            poly.material_index = slots[mat.name]
    return obj


def superellipse_point(a, power):
    """The point at angle a on the unit superellipse |x|^power + |y|^power = 1 (2: a circle)."""
    c, s = math.cos(a), math.sin(a)
    return (math.copysign(abs(c) ** (2 / power), c), math.copysign(abs(s) ** (2 / power), s))


def lathe(name, profile, centre, mat=None, segments=32, squash=(1.0, 1.0), power=2.0):
    """A round part about a vertical axis at centre (x, y): profile [(radius, z), ...] from its
    bottom up; the ends close to the axis. squash scales x and y (ovals); power > 2 makes its
    plan a superellipse (squarer)."""
    cx, cy = centre
    unit = [superellipse_point(2 * math.pi * j / segments, power) for j in range(segments)]
    rings = []
    for r, z in profile:
        rings.append([Vector((cx + r * squash[0] * u, cy + r * squash[1] * v, z)) for u, v in unit])
    obj = k.loft(name, rings, mat, start_point=(cx, cy, profile[0][1]), end_point=(cx, cy, profile[-1][1]))
    return obj


def plan_radius(dx, dy, squash=(1.0, 1.0), power=2.0):
    """How far out (dx, dy) from a lathed part's axis is, in its profile's radius."""
    return (abs(dx / squash[0]) ** power + abs(dy / squash[1]) ** power) ** (1 / power)


def ball(name, centre, radii, mat=None, segments=28, rings=14, angle=70.0):
    return k.smooth(k.ellipsoid(name, centre, radii, mat, segments, rings), angle)


def dome(name, centre, radii, z0, mat=None, segments=32, steps=10, power=2.0, angle=70.0):
    """Half an ellipsoid standing on z0 (flat underneath): plan radii rx, ry at centre (x, y), height
    rz; power > 2 makes it fuller."""
    rx, ry, rz = radii
    profile = []
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((max(1e-3, rx * math.cos(t) ** (2 / power)), z0 + rz * math.sin(t) ** (2 / power)))
    return k.smooth(lathe(name, profile, centre, mat, segments, squash=(1.0, ry / rx)), angle)


def smooth_tube(name, points, mat=None, segments=16, iterations=2):
    """A round bar along points (x, y, z, radius), its path and radii rounded together (Chaikin)."""
    dense = chaikin([tuple(p) for p in points], iterations, closed=False)
    return tube(name, [p[:3] for p in dense], dense[0][3], mat, segments, radii=[p[3] for p in dense])


def tube(name, points, radius, mat=None, segments=10, radii=None, cap=True):
    """A round bar along a polyline of 3D points (radii: one per point)."""
    pts = [Vector(p) for p in points]
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        a = t.cross(ref).normalized()
        b = t.cross(a).normalized()
        r = radii[i] if radii else radius
        rings.append([p + (a * math.cos(2 * math.pi * j / segments) + b * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, cap_start=cap, cap_end=cap)
    return obj


def surface(objects):
    """hit(x, y): where a ray cast straight down onto the objects first meets them, and the
    surface's normal there (pointing up), or None (polish_eye_turret.py's)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]

    def hit(x, y):
        best = None
        for tree in trees:
            location, normal, _, _ = tree.ray_cast(Vector((x, y, 100.0)), Vector((0, 0, -1)))
            if location is not None and (best is None or location.z > best[0].z):
                best = (location, normal if normal.z > 0 else -normal)
        return best
    return hit


def bar(name, points, ups, half_width, top, bottom, mat=None, segments=12, power=3.0):
    """A bar along a path of points on a surface (ups: the surface's normals there): rounded-box
    cross-sections, half_width across, reaching top above the path and bottom below it
    (polish_eye_turret.py's)."""
    rings = []
    n = len(points)
    for i, p in enumerate(points):
        t = (points[min(i + 1, n - 1)] - points[max(i - 1, 0)]).normalized()
        across = t.cross(ups[i]).normalized()
        up = across.cross(t).normalized()
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s = math.cos(a), math.sin(a)
            ring.append(p + across * math.copysign(abs(c) ** (2 / power), c) * half_width +
                        up * math.copysign(abs(s) ** (2 / power), s) * (top if s >= 0 else bottom))
        rings.append(ring)
    return k.loft(name, rings, mat)




def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def transform(objects, matrix):
    for obj in objects:
        obj.data.transform(matrix)


# --- Checks --------------------------------------------------------------------------------------







def coverage(objects, w, h, centre=(0.0, 0.0), supersample=4):
    """Which pixels of a w x h top view round centre the objects cover (rows of bools)."""
    import numpy as np
    scene = bpy.context.scene
    hidden = {}
    for obj in scene.objects:
        if obj.type == "MESH":
            hidden[obj.name] = obj.hide_render
            obj.hide_render = obj not in objects
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new("check")
    data.type = "ORTHO"
    data.ortho_scale = max(w, h)
    data.clip_end = 1000
    cam = bpy.data.objects.new("check", data)
    cam.location = (centre[0], centre[1], 300)
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "machine_check.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    for obj in scene.objects:
        if obj.name in hidden:
            obj.hide_render = hidden[obj.name]
    covered = alpha.reshape(h, supersample, w, supersample).mean(axis=(1, 3)) > 0.5
    return covered.tolist()


def compare(label, covered, m):
    """Prints the overlap (intersection over union) of a coverage and a mask and their map ('#' both,
    '+' the model only, '-' the mask only); returns the overlap."""
    h, w = len(m), len(m[0])
    both = sum(covered[y][x] and m[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or m[y][x] for y in range(h) for x in range(w))
    score = both / max(either, 1)
    print("silhouette overlap %s: %.3f" % (label, score))
    for y in range(h):
        print("".join("#" if covered[y][x] and m[y][x] else "+" if covered[y][x] else "-" if m[y][x] else "."
                      for x in range(w)))
    return score


# --- Cutting an object built whole into pieces (polish_redjet.py's method) --------------------------

def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return (1 / 3, 1 / 3, 1 / 3)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    weights = [max(0.0, 1 - v - w), max(0.0, v), max(0.0, w)]
    total = sum(weights) or 1.0
    return [x / total for x in weights]


class NormalSource:
    """An uncut object's shading: its corner normals, looked up at any point of its surface."""

    def __init__(self, obj):
        mesh = obj.data
        mesh.calc_loop_triangles()
        self.verts = [v.co.copy() for v in mesh.vertices]
        self.tris = [(tuple(t.vertices), tuple(t.loops)) for t in mesh.loop_triangles]
        self.normals = [n.vector.copy() for n in mesh.corner_normals]
        self.bvh = BVHTree.FromPolygons(self.verts, [t[0] for t in self.tris])

    def normal(self, co, towards):
        _, _, index, _ = self.bvh.find_nearest(co + (towards - co) * 0.02)
        if index is None:
            return None
        (ia, ib, ic), (la, lb, lc) = self.tris[index]
        w = barycentric(co, self.verts[ia], self.verts[ib], self.verts[ic])
        n = self.normals[la] * w[0] + self.normals[lb] * w[1] + self.normals[lc] * w[2]
        return n.normalized() if n.length > 1e-8 else None


def cut(source, box_xy, cap_mat):
    """The part of an object (modifiers applied) inside box (x0, x1, y0, y1), its cuts closed with
    flat caps of cap_mat, its normals those of the uncut object. None if nothing is inside."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = slot_of(obj, cap_mat)
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
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    shading = NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    # Materials no face uses any more are dropped.
    used = {p.material_index for p in mesh.polygons}
    for i in reversed(range(len(mesh.materials))):
        if i not in used and len(mesh.materials) > 1:
            for p in mesh.polygons:
                if p.material_index > i:
                    p.material_index -= 1
            mesh.materials.pop(index=i)
    return obj


# --- Output --------------------------------------------------------------------------------------

def triangles(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        total += len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
    return total


def materials_of(objects):
    return sorted({m.name for obj in objects for m in obj.data.materials if m is not None})


def bounds(objects):
    corners = [obj.matrix_world @ Vector(c) for obj in objects for c in obj.bound_box]
    return (Vector([min(c[i] for c in corners) for i in range(3)]),
            Vector([max(c[i] for c in corners) for i in range(3)]))


def export(objects, path):
    """Exports the objects to a .glb (the game's winding); returns its size in bytes."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_apply=True,
                              export_materials="EXPORT", use_selection=True)
    reverse_winding(path)
    size = os.path.getsize(path)
    print("exported %s (%d bytes)" % (path, size))
    return size


def report(name, objects, path):
    low, high = bounds(objects)
    size = export(objects, path)
    print("== %s: %d triangles, %d materials (%s), %d bytes, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        name, triangles(objects), len(materials_of(objects)), ", ".join(materials_of(objects)), size,
        low.x, high.x, low.y, high.y, low.z, high.z))


def preview(prefix, objects, size=(24, 28), scale=16, distance=1.0, centre=(0.0, 0.0)):
    """tyrkit.preview of some objects only (top view framed like the sprite, three-quarter view),
    its lights and cameras removed again."""
    scene = bpy.context.scene
    hidden = []
    for obj in scene.objects:
        if obj.type == "MESH" and obj not in objects and not obj.hide_render:
            obj.hide_render = True
            hidden.append(obj)
    shift = Matrix.Translation((-centre[0], -centre[1], 0))
    transform(objects, shift)
    before = set(bpy.data.objects)
    scene.view_settings.view_transform = "Standard"
    k.preview(prefix, size, scale)
    if distance != 1.0:  # the three-quarter view again from farther away
        cam = bpy.data.objects["3q"]
        cam.location = Vector(cam.location) * distance
        scene.render.resolution_x = scene.render.resolution_y = 768
        scene.camera = cam
        scene.render.filepath = prefix + "_3q.png"
        bpy.ops.render.render(write_still=True)
    for obj in set(bpy.data.objects) - before:
        bpy.data.objects.remove(obj)
    transform(objects, shift.inverted())
    for obj in hidden:
        obj.hide_render = False


def outdir(options):
    return options.get("outdir", DEFAULT_OUTDIR)
