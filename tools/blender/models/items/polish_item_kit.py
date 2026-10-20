"""Helpers shared by the polished items (2026-10-20): polish_gem.py, polish_crystal.py, polish_coin.py,
polish_capsule.py, polish_datacube.py and polish_ingot.py. Not a model script itself.

The items enemies leave are the things the player sees most (gems about 1170 times in the levels, coins 570,
crystals 170), drawn small (gems and coins are 1x1 sprites, 12 x 14 pixels), so they are built as crisp,
glossy, jewel-like solids: gems and crystals cut from planes (a convex solid of flat facets, as a gem cutter
grinds one: convex()), the rest lathed, lofted or extruded with tyrkit.

Most of them are one grey model each that the game colours with the sprite's frame (models.cfg color=sprite:
every palette material takes the ramp of the frame and keeps its own shade), so their materials are palette
shades of ramp 0 (shade()) without coloured emission (emission would keep its own colour). --ramp <0-15> builds
them in another ramp instead, as color=sprite shows them, written as <name>_r<ramp>.glb (for checks and
previews; the game uses the grey ones).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin
is the sprite's centre: for a 1x1 sprite its pixel (6, 7) (column c is x = c + 0.5 - 6, row r is y = 6.5 - r),
for a 2x2 sprite its pixel (12, 14) (x = c + 0.5 - 12, y = 13.5 - r). The game centres such models in height
on their layer and turns them about their origin (yaw about Z, roll about Y).

Options the scripts take after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the
silhouette against the sprite in coins.png), --preview <prefix>, --only <name,...>, --ramp <0-15>.
"""
import itertools
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402
from glb_winding import reverse_winding  # noqa: E402

DEFAULT_OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "items")


# --- Options -----------------------------------------------------------------------------------------------------

def options():
    return k.args()


def outdir(opts):
    return opts.get("outdir", DEFAULT_OUTDIR)


def wanted(opts, name):
    return "only" not in opts or name in opts["only"].split(",")


def ramp_of(opts, default=0):
    """The ramp the grey models are built in (--ramp, for checks), and the suffix of their files."""
    if "ramp" in opts:
        return int(opts["ramp"]), "_r%d" % int(opts["ramp"])
    return default, ""


# --- Materials ---------------------------------------------------------------------------------------------------

def shade(name, value, ramp=0, **finish):
    """A palette material of the given shade (0-15, clamped) in a ramp: with color=sprite the game gives it
    the ramp of the sprite's frame and keeps the shade."""
    s = max(0, min(15, int(round(value))))
    return k.material(name, palette=16 * ramp + s, **finish)


def slot_of(obj, mat):
    names = [m.name for m in obj.data.materials]
    if mat.name not in names:
        obj.data.materials.append(mat)
        names.append(mat.name)
    return names.index(mat.name)


def materials_of(objects):
    return sorted({m.name for obj in objects for m in obj.data.materials if m is not None})


# --- Numbers -----------------------------------------------------------------------------------------------------

def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


# --- A convex solid cut from planes --------------------------------------------------------------------------------
# A plane is (unit normal n, d): the solid keeps the points with n . p <= d. polish_stargate.convex()'s method,
# with each plane carrying a key (what it is, for painting).

def facet(azimuth, slope, point, below=False):
    """The half-space under (or, below=True, over) a facet that rises towards the middle: seen from above its
    steepest line points along azimuth (degrees from +X) outwards, it falls slope units per unit outwards, and
    it passes through point (x, y, z)."""
    a = math.radians(azimuth)
    c, s = math.cos(a), math.sin(a)
    if below:  # under the girdle (a pavilion): the solid keeps what is over the facet, which falls inwards
        n = unit((slope * c, slope * s, -1.0))
    else:
        n = unit((slope * c, slope * s, 1.0))
    return n, float(np.dot(n, point))


def wall(azimuth, distance):
    """The vertical half-space reaching distance from the axis along azimuth (degrees from +X)."""
    a = math.radians(azimuth)
    n = np.array((math.cos(a), math.sin(a), 0.0))
    return n, distance


def flat(z, below=False):
    """The half-space under the level z (or over it, below=True)."""
    return (np.array((0.0, 0.0, -1.0)), -z) if below else (np.array((0.0, 0.0, 1.0)), z)


def general(normal, point):
    n = unit(normal)
    return n, float(np.dot(n, point))


def chamfer(a, b, width):
    """A narrow facet ground along the edge where the half-spaces a and b meet, about width wide: its normal
    halves the angle between theirs (polish_crystal_blue.chamfer)."""
    (na, da), (nb, db) = a, b
    angle = math.acos(max(-1.0, min(1.0, float(np.dot(na, nb)))))
    s = na + nb
    length = np.linalg.norm(s)
    depth = 0.5 * width * math.tan(angle / 2)
    return s / length, (da + db) / length - depth


def convex(planes, eps=1e-7):
    """The convex solid where every half-space holds: its points and its faces (point indices, counter-clockwise
    seen from outside) with the index of the plane each lies on."""
    N = np.array([p[0] for p in planes], float)
    D = np.array([p[1] for p in planes], float)
    triples = np.array(list(itertools.combinations(range(len(planes)), 3)))
    A = N[triples]
    keep = np.abs(np.linalg.det(A)) > 1e-9
    A, b = A[keep], D[triples[keep]]
    P = np.linalg.solve(A, b[..., None])[..., 0]
    P = P[(P @ N.T <= D + eps).all(axis=1)]
    points = []
    for p in P:
        if not any(np.linalg.norm(p - q) < 1e-6 for q in points):
            points.append(p)
    points = np.array(points)
    faces, owners = [], []
    for m in range(len(planes)):
        on = np.nonzero(np.abs(points @ N[m] - D[m]) < 1e-6)[0]
        if len(on) < 3:
            continue
        centre = points[on].mean(axis=0)
        u = points[on[0]] - centre
        u /= np.linalg.norm(u)
        w = np.cross(N[m], u)
        rel = points[on] - centre
        order = on[np.argsort(np.arctan2(rel @ w, rel @ u))]
        loop = []
        for i, idx in enumerate(order):
            a, c = points[order[i - 1]], points[order[(i + 1) % len(order)]]
            if np.linalg.norm(np.cross(points[idx] - a, c - points[idx])) > 1e-9:
                loop.append(int(idx))
        if len(loop) >= 3:
            faces.append(loop)
            owners.append(m)
    return points, faces, owners


def meets(planes, a, b, points=None, min_length=0.05):
    """Whether the half-spaces a and b (indices into planes) meet in an edge of their solid at least min_length
    long (points: the solid's points, if already known)."""
    if points is None:
        points = convex(planes)[0]
    on = []
    for i in (a, b):
        n, d = planes[i]
        on.append({j for j, p in enumerate(points) if abs(float(np.dot(n, p)) - d) < 1e-6})
    common = [points[j] for j in on[0] & on[1]]
    return len(common) >= 2 and max(float(np.linalg.norm(p - q)) for p in common for q in common) >= min_length


def solid(name, planes, keys, mats):
    """A flat-faceted object from planes: keys[i] names plane i's part, mats[key] its material (a key missing
    from mats takes mats["*"]). Returns the object; each face's part is in its "part" attribute (an index into
    the sorted keys, for painting after cuts) and in obj["parts"]."""
    points, faces, owners = convex(planes)
    obj = k.mesh_object(name, [tuple(p) for p in points], faces)
    parts = sorted(set(keys))
    attr = obj.data.attributes.new("part", "INT", "FACE")
    for poly, owner in zip(obj.data.polygons, owners):
        key = keys[owner]
        mat = mats.get(key, mats.get("*"))
        poly.material_index = slot_of(obj, mat)
        poly.use_smooth = False
        attr.data[poly.index].value = parts.index(key)
    obj["parts"] = parts
    return obj


def drop_parts(obj):
    """Removes the painting attribute (not exported)."""
    if "part" in obj.data.attributes:
        obj.data.attributes.remove(obj.data.attributes["part"])
    if "parts" in obj:
        del obj["parts"]


def split_along(bm, values, threshold):
    """Cuts a bmesh's faces along the contour where the vertex values (a dict) cross threshold, so that the
    materials on either side meet along that line rather than along the faces' edges (polish_machine_kit's).
    The new vertices get the threshold as their value."""
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


def bands(obj, field, borders, pick):
    """Cuts a solid() object's faces along the contours field(point) = border (a top-view field of the point
    (x, y, z)), then paints each face: pick(part key, band) returns its material or None to keep it (band:
    how many borders the face's middle is past)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for t in borders:
        split_along(bm, {v: field(v.co) for v in bm.verts}, t)
    layer = bm.faces.layers.int.get("part")
    parts = list(obj["parts"])
    for f in bm.faces:
        value = field(f.calc_center_median())
        band = sum(value > t for t in borders)
        mat = pick(parts[f[layer]], band)
        if mat is not None:
            f.material_index = slot_of(obj, mat)
        f.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# --- Mesh helpers --------------------------------------------------------------------------------------------------

def link(name, mesh, mat=None):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def from_bmesh(name, bm, mat=None):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return link(name, mesh, mat)


def prism(name, outline, z0, z1, mat=None):
    """A polygon [(x, y), ...] extruded from z0 to z1 (quads and n-gons, for booleans and bevels)."""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in outline]
    hi = [bm.verts.new((x, y, z1)) for x, y in outline]
    bm.faces.new(lo)
    bm.faces.new(hi)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return from_bmesh(name, bm, mat)


def prism_box(name, x0, x1, y0, y1, z0, z1, mat=None):
    return prism(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mat)


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


def boolean(obj, others, operation="DIFFERENCE"):
    """obj cut by (or joined to, or intersected with) the others, applied; faces from the others keep their
    materials; the others are removed."""
    for o in others if isinstance(others, (list, tuple)) else [others]:
        o.hide_render = True
        mod = obj.modifiers.new("boolean", "BOOLEAN")
        mod.operation = operation
        mod.solver = "EXACT"
        mod.material_mode = "TRANSFER"
        mod.object = o
        apply(obj)
        data = o.data
        bpy.data.objects.remove(o)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    return obj


def bevel(obj, width, segments=2, angle=30.0, profile=0.5, harden=True, mat=None):
    """Rounds the edges sharper than angle (degrees), applied; with harden, the flat faces keep flat normals; mat:
    the rounded faces' material (else their neighbours')."""
    mod = obj.modifiers.new("bevel", "BEVEL")
    if mat is not None:
        mod.material = slot_of(obj, mat)
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle)
    mod.profile = profile
    mod.use_clamp_overlap = True
    mod.harden_normals = harden
    mod.miter_outer = "MITER_ARC"
    apply(obj)
    return obj


def weighted(obj, angle=40.0):
    """Smooth shading across edges flatter than angle, the large flat faces keeping flat normals."""
    k.smooth(obj, angle)
    mod = obj.modifiers.new("weighted", "WEIGHTED_NORMAL")
    mod.mode = "FACE_AREA"
    mod.weight = 50
    mod.keep_sharp = True
    apply(obj)
    return obj


def flat_shade(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return obj


def transform(objects, matrix):
    for obj in objects:
        obj.data.transform(matrix)
    bpy.context.view_layer.update()


def drop_unused_materials(obj):
    mesh = obj.data
    used = {p.material_index for p in mesh.polygons}
    for i in reversed(range(len(mesh.materials))):
        if i not in used and len(mesh.materials) > 1:
            mesh.materials.pop(index=i)


# --- Checks ------------------------------------------------------------------------------------------------------

def sprite_mask(sheets, sprite, large, skip=()):
    """The sprite's pixels in coins.png (rows of bools), leaving out the palette indices in skip (shadows
    drawn on the ground)."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    sheet = os.path.join(sheets, "coins.png") if os.path.isdir(sheets) else sheets
    return [[p is not None and p not in skip for p in row] for row in sprite_indices(sheet, sprite, large)]


def coverage(objects, w, h, supersample=4, shift=(0.0, 0.0), turn=0.0):
    """Which pixels of a w x h top view round the origin the objects cover (rows of bools), as if the objects
    were turned turn degrees about Z and then moved by shift (the camera moves instead: nothing is changed)."""
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
    back = Matrix.Rotation(math.radians(-turn), 3, "Z")
    where = back @ Vector((-shift[0], -shift[1], 0.0))
    cam.location = (where.x, where.y, 300.0)
    cam.rotation_euler = (0.0, 0.0, math.radians(-turn))
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "item_check.png")
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


def compare(label, covered, mask):
    """Prints the overlap (intersection over union) of a coverage and a mask and their map ('#' both, '+' the
    model only, '-' the mask only); returns the overlap."""
    h, w = len(mask), len(mask[0])
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    score = both / max(either, 1)
    print("silhouette overlap %s: %.3f" % (label, score))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    return score


def check(opts, label, objects, sprite, large, skip=(), shift=None, turn=0.0):
    """The silhouette check (--check): the overlap of the model's top view (turned turn degrees, as the sprite
    draws it) with the sprite's pixels; with shift (x, y), also with the model moved by it (models centred on the
    origin to turn in place, where the sprite draws the item off its centre)."""
    if "check" not in opts:
        return None
    w, h = (24, 28) if large else (12, 14)
    mask = sprite_mask(opts["check"], sprite, large, skip)
    score = compare(label, coverage(objects, w, h, turn=turn), mask)
    if shift is not None:
        compare("%s moved by (%g, %g)" % (label, shift[0], shift[1]),
                coverage(objects, w, h, shift=shift, turn=turn), mask)
    return score


# --- Output ------------------------------------------------------------------------------------------------------

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
    return os.path.getsize(path)


def report(name, objects, path):
    low, high = bounds(objects)
    size = export(objects, path)
    mats = materials_of(objects)
    print("== %s: %d triangles, %d materials (%s), %d bytes, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f -> %s" % (
        name, triangles(objects), len(mats), ", ".join(mats), size, low.x, high.x, low.y, high.y, low.z, high.z,
        path))
    return size


def preview(prefix, objects, size=(24, 28), scale=16, distance=1.0):
    """tyrkit.preview of some objects only (the top view framed like the sprite: size in game pixels; the
    three-quarter view from distance times tyrkit's distance), its lights and cameras removed again."""
    scene = bpy.context.scene
    hidden = []
    for obj in scene.objects:
        if obj.type == "MESH" and obj not in objects and not obj.hide_render:
            obj.hide_render = True
            hidden.append(obj)
    before = set(bpy.data.objects)
    scene.view_settings.view_transform = "Standard"
    k.preview(prefix, size, scale)
    if distance != 1.0:
        cam = bpy.data.objects["3q"]
        cam.location = Vector(cam.location) * distance
        scene.render.resolution_x = scene.render.resolution_y = 512
        scene.camera = cam
        scene.render.filepath = prefix + "_3q.png"
        bpy.ops.render.render(write_still=True)
    for obj in set(bpy.data.objects) - before:
        bpy.data.objects.remove(obj)
    for obj in hidden:
        obj.hide_render = False


def finish(opts, name, objects, sprite, large, label=None, skip=(), size=None, distance=1.0, shift=None, turn=0.0):
    """The usual end of a model: its silhouette check (--check; shift and turn: see check), export to
    <outdir>/<name>[_r<ramp>].glb and previews (--preview)."""
    _, suffix = ramp_of(opts)
    check(opts, label or "%s (coins %d)" % (name, sprite), objects, sprite, large, skip, shift, turn)
    bpy.context.scene.view_settings.view_transform = "Standard"
    path = os.path.join(outdir(opts), name + suffix + ".glb")
    report(name + suffix, objects, path)
    if "preview" in opts:
        preview(opts["preview"] + name + suffix, objects, size or ((24, 28) if large else (12, 14)),
                scale=16 if large else 32, distance=distance)
    return path
