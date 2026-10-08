"""Helpers for the sidekick models (the player's options; sidekicks_small.py and sidekicks_ships.py):
pixel coordinates of the sidekick sprites, materials, a few shapes (puffed outlines, turned parts
along any axis, tubes, rings, rounded boxes, boolean cuts) and the build loop.

Sidekicks fly beside the player's ship at its height and are seen from above, so each model keeps
its sprite's top view (outline, colours, lights) and gets real depth below it.

The small sidekicks are 1x1 sprites of the ships sheet (12 x 14 pixels, origin at pixel (6, 7)), the
companion ships 2x2 sprites of the power-ups sheet (24 x 28, origin at pixel (12, 14)): the game
puts the model's origin where the sprite's centre would be.
Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera).

usage: Blender -b --factory-startup -P <sidekicks_small.py|sidekicks_ships.py> -- [--only <name>,...]
           [--preview <directory>] [--check <sheets directory>] [--out <directory>]
--preview renders <directory>/<name>_top.png (framed like the sprite) and _3q.png; --check prints
each model's silhouette overlap with its sprite (sheets exported by TYR3D_EXTRACT: ships.png and
powerups.png).
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

ASSETS = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "sidekicks")


# --- Pixels --------------------------------------------------------------------------------------

def sx(col, large=False):
    """The centre of a sprite column in model units."""
    return col + 0.5 - (12 if large else 6)


def sy(row, large=False):
    """The centre of a sprite row in model units."""
    return (14 if large else 7) - (row + 0.5)


# --- Materials -----------------------------------------------------------------------------------

def pal(name, index, metallic=0.45, roughness=0.3, glow=None, strength=1.0):
    """A palette material (the game colours it from the level's palette); glow: an emitted colour."""
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=glow,
                      emission_strength=strength)


def light(name, rgb, strength=3.0, color=None, roughness=0.3):
    """An emissive material (lamps, cores, muzzles, flames): rgb the emitted colour."""
    return k.material(name, color or rgb, roughness=roughness, emission=rgb, emission_strength=strength)


def glass(name, index, alpha=0.55, roughness=0.08):
    return k.material(name, palette=index, roughness=roughness, metallic=0.1, alpha=alpha)


# --- Shapes --------------------------------------------------------------------------------------

def ccw(outline):
    """The outline [(x, y), ...] counter-clockwise seen from above."""
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    return list(outline) if area > 0 else list(reversed(outline))


def smooth_outline(points, step=0.35, closed=True):
    """A smooth closed curve (Catmull-Rom) through 2D points, sampled about every step."""
    pts = [Vector((p[0], p[1])) for p in points]
    n = len(pts)
    out = []
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        if not closed:
            p0, p3 = pts[max(i - 1, 0)], pts[min(i + 2, n - 1)]
        count = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            q = 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((q.x, q.y))
    if not closed:
        out.append((pts[-1].x, pts[-1].y))
    return out


def superellipse(cx, cy, rx, ry, power=2.0, count=48, angle=0.0):
    out = []
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    for i in range(count):
        a = 2 * math.pi * i / count
        c, s = math.cos(a), math.sin(a)
        x = math.copysign(abs(c) ** (2 / power), c) * rx
        y = math.copysign(abs(s) ** (2 / power), s) * ry
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def puff(name, outline, z0, z1, mat, side=0.35, steps=8, power=2.0, centre=None, bottom=None, smooth_angle=50,
         z_fn=None):
    """A part puffed from an outline (star-shaped about its centre): straight sides from z0 for `side`
    of its height, then a rounded top (a superellipse of the given power: 2 round, higher flatter) up
    to z1 in the middle. bottom: the bottom's depth below z0 for a rounded underside too (else flat).
    z_fn(x, y, z) -> z bends the result (e.g. to follow a surface)."""
    outline = ccw(outline)
    n = len(outline)
    c = Vector(centre) if centre is not None else sum((Vector(p) for p in outline), Vector((0.0, 0.0))) / n
    h = z1 - z0
    zs = z0 + h * side
    rings = []  # (scale, z)
    if bottom:
        for i in range(steps // 2, 0, -1):
            a = math.pi / 2 * i / (steps // 2)
            rings.append((math.cos(a) ** (2 / 2.0), z0 - bottom * math.sin(a)))
    rings.append((1.0, z0))
    if side > 0:
        rings.append((1.0, zs))
    for i in range(1, steps):
        a = math.pi / 2 * i / steps
        rings.append((math.cos(a) ** (2 / power), zs + (z1 - zs) * math.sin(a) ** (2 / power)))
    verts, faces = [], []
    for s, z in rings:
        for x, y in outline:
            verts.append(Vector((c.x + (x - c.x) * s, c.y + (y - c.y) * s, z)))
    for r in range(len(rings) - 1):
        for i in range(n):
            a, b = r * n + i, r * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    verts.append(Vector((c.x, c.y, z1)))
    top = len(verts) - 1
    last = (len(rings) - 1) * n
    faces += [(last + i, last + (i + 1) % n, top) for i in range(n)]
    verts.append(Vector((c.x, c.y, z0 - (bottom or 0.0))))
    bot = len(verts) - 1
    faces += [((i + 1) % n, i, bot) for i in range(n)]
    if z_fn is not None:
        verts = [Vector((v.x, v.y, z_fn(v.x, v.y, v.z))) for v in verts]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def lathe_y(name, profile, mat, x=0.0, z=0.0, squash=1.0, segments=24, smooth_angle=50):
    """A turned part along Y: profile (y, radius) in increasing y."""
    return k.smooth(k.lathe(name, profile, mat, segments=segments, axis_x=x, axis_z=z, squash=squash), smooth_angle)


def lathe_axis(name, profile, mat, start, direction, segments=24, squash=1.0, smooth_angle=50, up=(0, 0, 1)):
    """A turned part along any axis: profile (t, radius) in increasing t along `direction` from
    `start`; squash scales the cross-sections towards `up`."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
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
    return k.smooth(obj, smooth_angle)


def sphere(name, centre, radii, mat, segments=24, rings=12, smooth_angle=70):
    return k.smooth(k.ellipsoid(name, centre, radii, mat, segments, rings), smooth_angle)


def catmull(points, step=0.4):
    """A smooth 3D path through points, sampled about every step."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        count = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def tube(name, points, radius, mat, segments=12, smooth_angle=60, squash=1.0, closed=False):
    """A round tube through 3D points with rounded ends; radius a number or one per point."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    if isinstance(radius, (list, tuple)):
        # Radii given at evenly spaced points along the path: interpolated for every point.
        m = len(radius)
        radii = []
        for i in range(n):
            t = i / max(n - 1, 1) * (m - 1)
            j = min(int(t), m - 2) if m > 1 else 0
            radii.append(radius[j] + (radius[min(j + 1, m - 1)] - radius[j]) * (t - j))
    else:
        radii = [radius] * n
    rings = []
    for i, p in enumerate(pts):
        if closed:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) +
                           up * math.sin(2 * math.pi * j / segments) * squash) * radii[i] for j in range(segments)])
    if closed:
        verts = [v for r in rings for v in r]
        faces = []
        for i in range(n):
            for j in range(segments):
                a, b = i * segments + j, i * segments + (j + 1) % segments
                c, d = ((i + 1) % n) * segments + (j + 1) % segments, ((i + 1) % n) * segments + j
                faces.append((a, b, c, d))
        obj = k.mesh_object(name, verts, faces, mat)
        k.recalc_normals(obj)
        return k.smooth(obj, smooth_angle)
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radii[0] * 0.7, end_point=pts[-1] + t1 * radii[-1] * 0.7)
    return k.smooth(obj, smooth_angle)


def hoop(name, centre, rx, ry, minor, mat, segments=40, sides=10, squash=1.0, smooth_angle=60):
    """A ring (torus) lying flat round (cx, cy) at height cz: radii rx, ry, tube radius minor
    (squash scales its height)."""
    cx, cy, cz = centre
    verts, faces = [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        ox, oy = math.cos(a), math.sin(a)
        for j in range(sides):
            b = 2 * math.pi * j / sides
            r = minor * math.cos(b)
            verts.append((cx + (rx + r) * ox, cy + (ry + r) * oy, cz + minor * math.sin(b) * squash))
    for i in range(segments):
        for j in range(sides):
            a, b = i * sides + j, i * sides + (j + 1) % sides
            c, d = ((i + 1) % segments) * sides + (j + 1) % sides, ((i + 1) % segments) * sides + j
            faces.append((a, d, c, b))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def rbox(name, centre, size, mat, bevel=0.4, segments=2, smooth_angle=40):
    """A box with rounded edges."""
    obj = k.box(name, centre, size, mat)
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = min(bevel, min(size) / 2 - 0.01)
    mod.segments = segments
    mod.limit_method = "NONE"
    apply_modifiers(obj)
    return k.smooth(obj, smooth_angle)


def slab(name, outline, z0, z1, mat, bevel=0.3, segments=2, smooth_angle=40):
    obj = k.slab(name, ccw(outline), z0, z1, mat, bevel_width=bevel, bevel_segments=segments)
    apply_modifiers(obj)
    return k.smooth(obj, smooth_angle)


def apply_modifiers(obj):
    with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj],
                                   selected_editable_objects=[obj]):
        for mod in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def cut(obj, cutter, keep_cutter=False):
    """Subtracts the cutter from obj (exact boolean); the cutter is removed unless kept."""
    apply_modifiers(obj)
    mod = obj.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    apply_modifiers(obj)
    if not keep_cutter:
        bpy.data.objects.remove(cutter)
    return obj


def transform(objects, matrix):
    for obj in objects if isinstance(objects, (list, tuple)) else [objects]:
        obj.data.transform(matrix)
    return objects


def mirror(objects, axis_x=0.0):
    """Mirrored copies across the vertical line x = axis_x."""
    out = []
    for obj in objects if isinstance(objects, (list, tuple)) else [objects]:
        copy = k.mirror_x(obj)
        if axis_x:
            copy.data.transform(Matrix.Translation((2 * axis_x, 0, 0)))
        out.append(copy)
    return out


def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in meshes():
        mesh = obj.evaluated_get(depsgraph).to_mesh()
        mesh.calc_loop_triangles()
        total += len(mesh.loop_triangles)
        obj.evaluated_get(depsgraph).to_mesh_clear()
    return total


# --- Previews and the build loop -----------------------------------------------------------------

def preview(prefix, large):
    """Top view framed like the sprite (12 x 14 or 24 x 28 pixels) and a three-quarter view."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"  # the game clamps bright colours
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
    w, h = (24, 28) if large else (12, 14)
    scale = 16 if large else 24
    scene.render.resolution_x, scene.render.resolution_y = w * scale, h * scale
    top = k._camera("top", (0, 0, 100), (0, 0, 0), ortho_scale=max(w, h))
    scene.camera = top
    scene.render.filepath = prefix + "_top.png"
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x = scene.render.resolution_y = 512
    d = 0.75 if large else 0.42
    three_quarter = k._camera("3q", (38 * d, -48 * d, 42 * d), (math.radians(55), 0, math.radians(38)))
    scene.camera = three_quarter
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)


MODELS = []  # (name, sheet, sprite, large, builder)


def model(name, sheet, sprite, large=False):
    """Registers a model built by the decorated function, replacing sprite `sprite` of `sheet`."""
    def register(fn):
        MODELS.append((name, sheet, sprite, large, fn))
        return fn
    return register


def run():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    out = options.get("out", ASSETS)
    for name, sheet, sprite, large, build in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        print(f"{name}: {triangles()} triangles")
        if "stats" in options:  # --stats 1: the parts with the most triangles
            counts = {}
            for obj in meshes():
                mesh = obj.data
                mesh.calc_loop_triangles()
                key = obj.name.rstrip("0123456789.")
                counts[key] = counts.get(key, 0) + len(mesh.loop_triangles)
            print("  ", sorted(counts.items(), key=lambda kv: -kv[1])[:8])
        if "check" in options:
            print(f"{name} ({sheet} {sprite}):")
            k.check_silhouette(os.path.join(options["check"], sheet + ".png"), [sprite], large=large)
            for obj in list(bpy.context.scene.objects):
                if obj.type == "CAMERA":
                    bpy.data.objects.remove(obj)
        k.export(os.path.join(out, name + ".glb"))
        if "preview" in options:
            os.makedirs(options["preview"], exist_ok=True)
            preview(os.path.join(options["preview"], name), large)
