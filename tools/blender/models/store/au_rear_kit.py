"""Shared parts for the store illustration's rear guns and generators (au_rear_guns.py,
au_generators.py).

The store draws the player's ship big (about 90 x 115 pixels) with the generator, the front gun and
the rear gun as separate pictures on it; in 3D each picture is a model placed on the ship's deck.
Units are the store screen's pixels; the origin is the centre of the picture the model replaces,
X right, +Y up the screen, Z up. A gun or generator stands on z = 0 (the game puts it on the deck,
which is at z = 12 along the ship's centre line); parts out over the hull's sloping sides reach
down below z = 0 so that they meet the hull rather than float over it.

Pictures are described by their coverage (run-length rows: "a-b c" covers columns a to b and c),
from SCRATCH/extract/sheets/store/weapon_<n>.png; Grid turns columns and rows into model units.

usage (both scripts): Blender -b --factory-startup -P <script> -- [--only <name>,...]
    [--preview <directory>] [--check] [--out <directory>] [--refs <SCRATCH/extract/sheets/store>]
--preview renders <directory>/<name>_top.png (framed like the picture), _3q.png and _low.png;
--check prints each model's silhouette overlap with its picture; with --refs, --preview also
renders <name>_ship.png: the model on a stand-in of the USP Talon's picture, as the store shows it.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402
import silhouette as sil  # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "store")


# --- Pictures ----------------------------------------------------------------------------------

class Picture:
    """A store picture's coverage and its pixel grid in model units (origin at its centre)."""

    def __init__(self, spec):
        w, h, text = spec
        self.w, self.h = w, h
        lines = [line.strip() for line in text.strip("\n").split("\n")]
        assert len(lines) == h, (len(lines), h)
        self.rows = []
        for line in lines:
            row = ["."] * w
            for run in line.split():
                a, _, b = run.partition("-")
                for c in range(int(a), int(b or a) + 1):
                    row[c] = "#"
            self.rows.append("".join(row))

    def x(self, c):
        """The centre of column c."""
        return c + 0.5 - self.w / 2

    def y(self, r):
        """The centre of row r."""
        return self.h / 2 - (r + 0.5)

    def xe(self, c):
        """The left edge of column c."""
        return c - self.w / 2

    def ye(self, r):
        """The top edge of row r."""
        return self.h / 2 - r

    def covered(self, c, r):
        return 0 <= c < self.w and 0 <= r < self.h and self.rows[r][c] == "#"

    def outline(self, cols=None, rows=None, epsilon=0.75, keep=None):
        """The outline (counter-clockwise polygon) of the covered pixels in a column and row range
        (inclusive), or those keep(c, r) accepts."""
        c0, c1 = cols or (0, self.w - 1)
        r0, r1 = rows or (0, self.h - 1)
        masked = []
        for r in range(self.h):
            masked.append("".join(
                "#" if self.covered(c, r) and c0 <= c <= c1 and r0 <= r <= r1 and (keep is None or keep(c, r))
                else "." for c in range(self.w)))
        return sil.outline(masked, self.w, epsilon)

    def view(self, oc=0, orow=0):
        """This picture seen through another's columns and rows (column c there is c + oc here):
        for parts that two pictures share, drawn at different places."""
        return View(self, oc, orow)

    def run(self, r, c0, c1):
        """The first and last covered column of row r within c0..c1, or None."""
        cs = [c for c in range(c0, c1 + 1) if self.covered(c, r)]
        return (cs[0], cs[-1]) if cs else None


class View:
    """A picture's grid offset by oc columns and orow rows (see Picture.view)."""

    def __init__(self, picture, oc, orow):
        self.p, self.oc, self.orow = picture, oc, orow
        self.w, self.h = picture.w, picture.h

    def x(self, c):
        return self.p.x(c + self.oc)

    def y(self, r):
        return self.p.y(r + self.orow)

    def xe(self, c):
        return self.p.xe(c + self.oc)

    def ye(self, r):
        return self.p.ye(r + self.orow)

    def at(self, c, r, z=0.0):
        """The point at column c, row r (pixel centres; fractions allowed) and height z."""
        return (self.x(c), self.y(r), z)

    def outline(self, cols=None, rows=None, epsilon=0.75, keep=None):
        cols = (cols[0] + self.oc, cols[1] + self.oc) if cols else None
        rows = (rows[0] + self.orow, rows[1] + self.orow) if rows else None
        kept = None if keep is None else (lambda c, r: keep(c - self.oc, r - self.orow))
        return self.p.outline(cols, rows, epsilon, kept)

    def poly(self, points):
        """Pixel-edge points [(column, row)] to model units (an outline drawn on the grid)."""
        return [(self.xe(c), self.ye(r)) for c, r in points]


# --- Materials ---------------------------------------------------------------------------------

def mat(name, rgb, metallic=0.5, roughness=0.35, emission=None, strength=1.0, alpha=None):
    """A material with the colour an up-facing surface shows (the picture's colour)."""
    return k.material(name, rgb, metallic=metallic, roughness=roughness, emission=emission,
                      emission_strength=strength, alpha=alpha)


def materials():
    """The store pictures' shared colours (the store's palette is fixed)."""
    return {
        "steel": mat("steel", (150, 152, 150), 0.6, 0.3),
        "steel_light": mat("steel_light", (190, 192, 190), 0.6, 0.25),
        "steel_mid": mat("steel_mid", (112, 114, 112), 0.6, 0.32),
        "steel_dark": mat("steel_dark", (66, 66, 68), 0.55, 0.4),
        "black": mat("black", (26, 26, 28), 0.4, 0.5),
        "gold": mat("gold", (150, 121, 76), 0.75, 0.28),
        "gold_dark": mat("gold_dark", (92, 66, 30), 0.7, 0.35),
        "red": mat("red_paint", (160, 10, 0), 0.35, 0.22),
        "red_dark": mat("red_dark", (70, 2, 0), 0.3, 0.4),
        "glass": mat("glass_blue", (62, 104, 134), 0.3, 0.06, emission=(30, 70, 100), strength=0.5),
        "lamp": mat("lamp_red", (230, 40, 0), 0.0, 0.3, emission=(255, 40, 0), strength=2.5),
        "lamp_core": mat("lamp_core", (255, 220, 80), 0.0, 0.3, emission=(255, 200, 60), strength=3.0),
        "fire": mat("fire", (168, 12, 0), 0.0, 0.18, emission=(235, 22, 0), strength=0.6),
        "fire_dim": mat("fire_dim", (110, 6, 0), 0.0, 0.3, emission=(200, 16, 0), strength=0.4),
        "fire_warm": mat("fire_warm", (225, 70, 6), 0.0, 0.2, emission=(255, 72, 6), strength=1.0),
        "fire_hot": mat("fire_hot", (245, 160, 30), 0.0, 0.2, emission=(255, 160, 30), strength=1.6),
        "fire_core": mat("fire_core", (255, 240, 150), 0.0, 0.2, emission=(255, 235, 140), strength=2.4),
        "energy": mat("energy_blue", (12, 28, 210), 0.0, 0.15, emission=(20, 45, 255), strength=1.3),
        "energy_hot": mat("energy_hot", (90, 150, 245), 0.0, 0.12, emission=(100, 165, 255), strength=2.0),
    }


# --- Parts -------------------------------------------------------------------------------------

def slab(name, poly, z0, z1, m, bevel=0.0, segments=2):
    """A plate in the outline poly (counter-clockwise), from z0 to z1, its edges bevelled."""
    obj = k.slab(name, poly, z0, z1, m)
    if bevel > 0:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(35)
        mod.harden_normals = False
    return k.smooth(obj, 35)


def block(name, x0, x1, y0, y1, z0, z1, m, bevel=0.5, segments=2):
    """A box with bevelled edges."""
    obj = k.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), m)
    if bevel > 0:
        k.bevel(obj, bevel, segments)
    return k.smooth(obj, 35)


def section(y, cx, half_w, z0, z1, power=2.0, segments=20, top=1.0):
    """A cross-section in the XZ plane at y: a superellipse from x = cx - half_w to cx + half_w and
    z0 to z1 (top < 1 flattens the upper half)."""
    cz, hh = (z0 + z1) / 2, (z1 - z0) / 2
    return k.ring(y, max(half_w, 0.02), max(hh, 0.02), segments, z=cz, x=cx, power=power, top=top)


def loft_y(name, sections, m, smooth_angle=50):
    """A body through sections (from section(), in increasing y), closed at both ends."""
    obj = k.loft(name, sections, m)
    return k.smooth(obj, smooth_angle)


def cylinder(name, p0, p1, r0, m, r1=None, segments=18, cap=True, squash=1.0):
    """A cylinder (a cone if r1 differs) from p0 to p1; squash scales it across, in the plane of
    its axis and Z (flattened pods)."""
    p0, p1 = Vector(p0), Vector(p1)
    r1 = r0 if r1 is None else r1
    axis = p1 - p0
    length = axis.length
    verts, faces = [], []
    for i, (z, r) in enumerate(((0.0, r0), (length, r1))):
        for s in range(segments):
            a = 2 * math.pi * s / segments
            verts.append((r * math.cos(a), r * math.sin(a) * squash, z))
    for s in range(segments):
        faces.append((s, (s + 1) % segments, segments + (s + 1) % segments, segments + s))
    if cap:
        faces.append(tuple(reversed(range(segments))))
        faces.append(tuple(range(segments, 2 * segments)))
    obj = k.mesh_object(name, verts, faces, m)
    _orient(obj, p0, axis)
    k.recalc_normals(obj)
    return k.smooth(obj, 40)


def _orient(obj, origin, axis):
    """Turns a part built along +Z (local Y towards world +Z where possible) onto axis at origin."""
    axis = axis.normalized()
    up = Vector((0, 0, 1)) if abs(axis.z) < 0.95 else Vector((0, 1, 0))
    x = up.cross(axis).normalized()
    y = axis.cross(x).normalized()
    rot = Matrix((x, y, axis)).transposed().to_4x4()
    obj.data.transform(Matrix.Translation(origin) @ rot)


def lathe_axis(name, p0, p1, profile, m, segments=20, squash=1.0):
    """A turned part along the axis p0 -> p1: profile is [(t, radius)], t from 0 (p0) to 1 (p1);
    radius 0 at the ends closes them to a point. squash flattens it towards the axis' up side."""
    p0, p1 = Vector(p0), Vector(p1)
    length = (p1 - p0).length
    rings = []
    for t, r in profile:
        rings.append([Vector((max(r, 0.01) * math.cos(2 * math.pi * s / segments),
                              max(r, 0.01) * math.sin(2 * math.pi * s / segments) * squash, t * length))
                      for s in range(segments)])
    verts = [v for ring in rings for v in ring]
    faces = []
    n = segments
    for i in range(len(rings) - 1):
        for s in range(n):
            faces.append((i * n + s, i * n + (s + 1) % n, (i + 1) * n + (s + 1) % n, (i + 1) * n + s))
    verts.append(Vector((0, 0, profile[0][0] * length)))
    c = len(verts) - 1
    faces += [((s + 1) % n, s, c) for s in range(n)]
    verts.append(Vector((0, 0, profile[-1][0] * length)))
    c = len(verts) - 1
    base = (len(rings) - 1) * n
    faces += [(base + s, base + (s + 1) % n, c) for s in range(n)]
    obj = k.mesh_object(name, verts, faces, m)
    _orient(obj, p0, p1 - p0)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def dome(name, cx, cy, z0, rx, ry, rz, m, segments=24, rings=8, skirt=0.0):
    """The upper half of an ellipsoid standing on z0 (a skirt reaches it down by that much)."""
    verts, faces = [], []
    levels = []
    if skirt > 0:
        levels.append((1.0, z0 - skirt))
    for i in range(rings):
        t = (math.pi / 2) * i / rings
        levels.append((math.cos(t), z0 + rz * math.sin(t)))
    for f, z in levels:
        for s in range(segments):
            a = 2 * math.pi * s / segments
            verts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a), z))
    n = segments
    for i in range(len(levels) - 1):
        for s in range(n):
            faces.append((i * n + s, i * n + (s + 1) % n, (i + 1) * n + (s + 1) % n, (i + 1) * n + s))
    verts.append((cx, cy, z0 + rz))
    c = len(verts) - 1
    base = (len(levels) - 1) * n
    faces += [(base + s, base + (s + 1) % n, c) for s in range(n)]
    faces.append(tuple(reversed(range(n))))
    obj = k.mesh_object(name, verts, faces, m)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def glow_spot(name, centre, radii, spot, layers, segments=56, rings=28):
    """Lighter patches on an ellipsoid (centre, radii) round the point above spot = (x, y), for a
    hot spot that fades out. Each layer (radius, lift, material) is a smaller copy of the
    ellipsoid touching it at that point, raised by lift so that a patch of about that radius
    shows through: smooth outlines, each layer over the one before (give them rising lifts and
    falling radii). Hidden parts are left out."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    sx, sy = spot
    u = ((sx - cx) / rx) ** 2 + ((sy - cy) / ry) ** 2
    point = Vector((sx, sy, cz + rz * math.sqrt(max(0.0, 1 - u))))
    normal = Vector(((sx - cx) / rx ** 2, (sy - cy) / ry ** 2, (point.z - cz) / rz ** 2)).normalized()
    curvature = (rx + ry + rz) / 3
    out = []
    for i, (radius, lift, m) in enumerate(layers):
        scale = 1 / (1 + 2 * curvature * lift / radius ** 2)
        c = point + (Vector(centre) - point) * scale + normal * lift
        obj = k.ellipsoid(f"{name}_{i}", tuple(c), (rx * scale, ry * scale, rz * scale), m, segments, rings)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        inside = lambda v: ((v.co.x - cx) / rx) ** 2 + ((v.co.y - cy) / ry) ** 2 + ((v.co.z - cz) / rz) ** 2 < 0.985  # noqa: E731
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(inside(v) for v in f.verts)], context="FACES")
        bm.to_mesh(obj.data)
        bm.free()
        out.append(k.smooth(obj, 70))
    return out


def ellipsoid(name, centre, radii, m, segments=20, rings=12):
    return k.smooth(k.ellipsoid(name, centre, radii, m, segments, rings), 70)


def tube(name, points, radius, m, segments=10, closed=False, radii=None, squash=1.0, caps=True):
    """A tube along a path of points; radii: one per point (taper); squash flattens it in Z."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    rings = []
    for i, p in enumerate(pts):
        if closed:
            t = pts[(i + 1) % n] - pts[i - 1]
        else:
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        t.normalize()
        ref = Vector((0, 0, 1))
        if abs(ref.dot(t)) > 0.95:
            ref = Vector((1, 0, 0))
        side = t.cross(ref).normalized()
        up = side.cross(t).normalized()
        r = radii[i] if radii else radius
        rings.append([p + r * (math.cos(2 * math.pi * s / segments) * side +
                               squash * math.sin(2 * math.pi * s / segments) * up) for s in range(segments)])
    verts = [v for ring in rings for v in ring]
    faces = []
    count = n if closed else n - 1
    for i in range(count):
        a, b = i * segments, ((i + 1) % n) * segments
        for s in range(segments):
            faces.append((a + s, a + (s + 1) % segments, b + (s + 1) % segments, b + s))
    if not closed and caps:
        verts.append(pts[0])
        c = len(verts) - 1
        faces += [((s + 1) % segments, s, c) for s in range(segments)]
        verts.append(pts[-1])
        c = len(verts) - 1
        base = (n - 1) * segments
        faces += [(base + s, base + (s + 1) % segments, c) for s in range(segments)]
    obj = k.mesh_object(name, verts, faces, m)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def mirror(obj, name=None):
    return k.mirror_x(obj, name)


def apply_modifiers(obj):
    with bpy.context.temp_override(active_object=obj, object=obj, selected_editable_objects=[obj]):
        for mod in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)


def merge_by_material():
    """Joins the parts that share a material (fewer draw calls), after applying their modifiers."""
    groups = {}
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH" or len(obj.data.materials) != 1:
            continue
        apply_modifiers(obj)
        groups.setdefault(obj.data.materials[0].name, []).append(obj)
    for name, objs in groups.items():
        if len(objs) < 2:
            continue
        with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
            bpy.ops.object.join()
        objs[0].name = name


def triangles(verbose=False):
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            n = sum(len(p.vertices) - 2 for p in obj.data.polygons)
            if verbose:
                print(f"  {obj.name}: {n}")
            total += n
    return total


# --- Checks and previews -----------------------------------------------------------------------

def check(picture, supersample=4):
    """The model's top view against the picture's coverage: prints the overlap (intersection over
    union) and a map ('#' both, '+' the model only, '-' the picture only)."""
    w, h = picture.w, picture.h
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = k._camera("silhouette", (0, 0, 200), (0, 0, 0), ortho_scale=max(w, h))
    cam.data.clip_end = 1000
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "au_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    pixels = list(image.pixels)
    both_, either = 0, 0
    lines = []
    for r in range(h):
        line = ""
        for c in range(w):
            alpha = 0.0
            for sy in range(supersample):
                for sx in range(supersample):
                    px, py = c * supersample + sx, rh - 1 - (r * supersample + sy)
                    alpha += pixels[(py * rw + px) * 4 + 3]
            model = alpha / supersample ** 2 > 0.5
            pic = picture.covered(c, r)
            both_ += model and pic
            either += model or pic
            line += "#" if model and pic else "+" if model else "-" if pic else "."
        lines.append(line)
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    overlap = both_ / max(either, 1)
    print("silhouette overlap: %.3f" % overlap)
    print("\n".join(lines))
    return overlap


def _lights():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.37, 0.42, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("sun", sun)
    sun_obj.rotation_euler = Vector((0.45, 0.35, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)


def _look(name, location, target=(0, 0, 0), lens=50):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.clip_end = 2000
    cam = bpy.data.objects.new(name, data)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(cam)
    return cam


def preview(prefix, picture, scale=8):
    """Renders the top view framed like the picture, a three-quarter view and a low view."""
    scene = bpy.context.scene
    _lights()
    w, h = picture.w, picture.h
    scene.render.resolution_x, scene.render.resolution_y = w * scale, h * scale
    top = k._camera("top", (0, 0, 200), (0, 0, 0), ortho_scale=max(w, h))
    top.data.clip_end = 1000
    scene.camera = top
    scene.render.filepath = prefix + "_top.png"
    bpy.ops.render.render(write_still=True)
    size = max(w, h)
    scene.render.resolution_x, scene.render.resolution_y = 640, 512
    for suffix, direction in (("_3q", (0.55, -0.75, 0.75)), ("_low", (-0.25, -1.0, 0.32))):
        d = Vector(direction).normalized() * size * 1.6
        scene.camera = _look("cam" + suffix, d, (0, 0, 2))
        scene.render.filepath = prefix + suffix + ".png"
        bpy.ops.render.render(write_still=True)


def ship_preview(prefix, refs, placement, other=None):
    """The model on a stand-in of the USP Talon's picture (option 31, drawn at store position
    (35, 33)): a plate in the picture's outline, its top at z = 12 and textured with the picture,
    and the model at its store position (placement: the picture's top-left x, y and size w, h).
    other: (glb path, x, y, w, h) of another piece to show with it (the generator with a gun, a
    gun with a generator)."""
    path = os.path.join(refs, "option_31.png")
    if not os.path.exists(path):
        print("no", path)
        return
    image = bpy.data.images.load(path)
    sw, sh = image.size
    alpha = list(image.pixels)[3::4]
    rows = []
    for r in range(sh):
        rows.append("".join("#" if alpha[(sh - 1 - r) * sw + c] > 0.5 else "." for c in range(sw)))
    poly = sil.outline(rows, sw, 0.75)
    # Store screen coordinates: X = x - 80, Y = 75 - y (the illustration's middle at the origin).
    ox, oy = 35 + sw / 2 - 80, 75 - (33 + sh / 2)
    hull_mat = bpy.data.materials.new("stand_in")
    hull_mat.use_nodes = True
    nodes = hull_mat.node_tree.nodes
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    coords = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    # Object coordinates (store pixels, origin at the picture's centre) to 0-1 texture space.
    mapping.inputs["Location"].default_value = (0.5, 0.5, 0)
    mapping.inputs["Scale"].default_value = (1 / sw, 1 / sh, 1)
    links = hull_mat.node_tree.links
    links.new(coords.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    bsdf = nodes["Principled BSDF"]
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    x, y, w, h = placement
    model = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    for obj in model:
        obj.location = (x + w / 2 - 80, 75 - (y + h / 2), 12)
    ship = os.path.join(OUT_DIR, "store_ship_31.glb")
    if os.path.exists(ship):  # the ship's model (au_ships.py), if it is there yet
        bpy.ops.import_scene.gltf(filepath=ship)
        for obj in bpy.context.selected_objects:
            if obj.parent is None:
                obj.location = (ox, oy, 0)
    else:
        hull = k.slab("stand_in", poly, 0, 12, hull_mat)
        hull.location = (ox, oy, 0)
    if other and os.path.exists(other[0]):
        gpath, gx, gy, gw, gh = other
        bpy.ops.import_scene.gltf(filepath=gpath)
        for obj in bpy.context.selected_objects:
            if obj.parent is None:
                obj.location = (gx + gw / 2 - 80, 75 - (gy + gh / 2), 12)
                obj.rotation_mode = "XYZ"
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 640, 600
    top = k._camera("ship_top", (0, 0, 300), (0, 0, 0), ortho_scale=160)
    top.data.clip_end = 1000
    scene.camera = top
    scene.render.filepath = prefix + "_ship.png"
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x, scene.render.resolution_y = 640, 600
    for suffix, direction in (("_ship3q", (0.5, -0.9, 0.9)), ("_shipside", (-1.0, -0.35, 0.18))):
        scene.camera = _look("cam" + suffix, Vector(direction).normalized() * 215, (0, -16, 8))
        scene.render.filepath = prefix + suffix + ".png"
        bpy.ops.render.render(write_still=True)


def arguments():
    """Options after "--": "--name value", or "--name" alone for a flag."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    options = {}
    for i, token in enumerate(argv):
        if token.startswith("--"):
            value = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else True
            options[token[2:]] = value
    return options


def run(models, pictures, placements=None, other_for_ship=None):
    """Builds each model (name -> build function), exports it, and checks and previews it."""
    options = arguments()
    only = set(options["only"].split(",")) if "only" in options else None
    out = options.get("out", OUT_DIR)
    for name, build in models.items():
        if only and name not in only:
            continue
        k.reset()
        build()
        merge_by_material()
        print(f"{name}: {triangles('tris' in options)} triangles")
        picture = pictures[name]
        if "check" in options:
            print(f"{name}:")
            check(picture)
        path = os.path.join(out, name + ".glb")
        k.export(path)
        if "preview" in options:
            os.makedirs(options["preview"], exist_ok=True)
            prefix = os.path.join(options["preview"], name)
            preview(prefix, picture)
            if "refs" in options and placements and name in placements:
                ship_preview(prefix, options["refs"], placements[name],
                             other_for_ship(name) if other_for_ship else None)
