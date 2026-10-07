"""Tyrian3D model kit for Blender.

Model scripts import this module and build their model with it; tools/blender/build.sh runs them
headless and exports the result as glTF binary (.glb) for assets/models.

Conventions (see TYRIAN3D.md): 1 unit = 1 game pixel. In Blender, X is right, +Y is the nose (up
the screen) and Z is up; the glTF exporter turns that into the game's Y up, nose towards -Z.
The origin is the centre of the sprite the model replaces (for a 2x2 sprite, pixel (12, 14)).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glb_winding import reverse_winding  # noqa: E402


# --- Scene -------------------------------------------------------------------------------------

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def args():
    """Options after "--": --out <file.glb>, --preview <file prefix>."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    options = {}
    i = 0
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            options[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            i += 1
    return options


# --- Colours and materials ---------------------------------------------------------------------

def srgb(rgb):
    """0-255 sRGB (as in the game's palette) to linear 0-1, as Blender and glTF expect."""
    def channel(value):
        c = value / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(channel(v) for v in rgb[:3])


# In the game, a surface facing straight up shows about this much of its albedo (sun and sky,
# measured with test plates). Materials take the colour a surface should show, as in the sprites.
UP_FACING_LIGHT = 1.16


def material(name, color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0):
    """A Principled BSDF material. color is 0-255 sRGB, the colour an up-facing surface shows in
    the game (a sprite's colour): the albedo is that divided by the game's light."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    albedo = tuple(min(1.0, c / UP_FACING_LIGHT) for c in srgb(color))
    bsdf.inputs["Base Color"].default_value = (*albedo, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*srgb(emission), 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m


# --- Mesh building -----------------------------------------------------------------------------

def mesh_object(name, vertices, faces, mat=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in vertices], [], faces)
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def ring(y, half_width, half_height, segments=16, z=0.0, x=0.0, top=1.0, bottom=1.0, power=2.0, crest=0.0):
    """A cross-section in the XZ plane at y: a superellipse (power 2 = ellipse, higher = boxier).
    top/bottom scale the upper and lower halves; crest raises a ridge along the top's middle.
    Points run counter-clockwise seen from +Y."""
    points = []
    for k in range(segments):
        a = 2 * math.pi * k / segments
        c, s = math.cos(a), math.sin(a)
        px = math.copysign(abs(c) ** (2 / power), c) * half_width
        pz = math.copysign(abs(s) ** (2 / power), s) * half_height * (top if s >= 0 else bottom)
        if s > 0:
            pz += crest * s ** 12
        points.append(Vector((x + px, y, z + pz)))
    return points


def loft(name, rings, mat=None, cap_start=True, cap_end=True, start_point=None, end_point=None):
    """Hull through rings of equal point counts (from ring(), ordered along +Y). The ends are
    closed by a fan to start_point/end_point (default: the ring's centre), which keeps them
    rounded or pointed when smoothed."""
    vertices = [p for r in rings for p in r]
    n = len(rings[0])
    faces = []
    for i in range(len(rings) - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            faces.append((a, b, b + n, a + n))
    if cap_start:
        vertices.append(Vector(start_point) if start_point is not None else sum(rings[0], Vector()) / n)
        c = len(vertices) - 1
        faces += [((k + 1) % n, k, c) for k in range(n)]
    if cap_end:
        vertices.append(Vector(end_point) if end_point is not None else sum(rings[-1], Vector()) / n)
        c = len(vertices) - 1
        base = (len(rings) - 1) * n
        faces += [(base + k, base + (k + 1) % n, c) for k in range(n)]
    obj = mesh_object(name, vertices, faces, mat)
    recalc_normals(obj)
    return obj


def ellipsoid(name, centre, radii, mat=None, segments=16, rings_count=10):
    rings = []
    for i in range(1, rings_count):
        t = math.pi * i / rings_count
        y = centre[1] - radii[1] * math.cos(t)
        r = math.sin(t)
        rings.append(ring(y, radii[0] * r, radii[2] * r, segments, z=centre[2], x=centre[0]))
    cx, cy, cz = centre
    return loft(name, rings, mat, start_point=(cx, cy - radii[1], cz), end_point=(cx, cy + radii[1], cz))


def profile(points, step=0.5):
    """Samples a smooth curve through (y, value...) points (Catmull-Rom), every `step` along y.
    Points must be ordered by increasing y. Returns [(y, value...)]."""
    out = []
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        count = max(1, int(round((p2[0] - p1[0]) / step)))
        for k in range(count):
            t = k / count
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                       (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                for j in range(len(p1))))
    out.append(tuple(points[-1]))
    return out


def box(name, centre, size, mat=None):
    hx, hy, hz = (s / 2 for s in size)
    cx, cy, cz = centre
    v = [(cx + x * hx, cy + y * hy, cz + z * hz) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    obj = mesh_object(name, v, faces, mat)
    recalc_normals(obj)
    return obj


def recalc_normals(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def mirror_x(obj, name=None):
    """A mirrored copy across X (for symmetric parts built on one side)."""
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name or obj.name + "_mirror"
    bpy.context.scene.collection.objects.link(copy)
    copy.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    copy.data.flip_normals()
    return copy


def smooth(obj, angle=40.0):
    with bpy.context.temp_override(selected_editable_objects=[obj], active_object=obj, object=obj):
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    return obj


def bevel(obj, width, segments=2):
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    return obj


def subdivide(obj, levels=1):
    mod = obj.modifiers.new("subdivision", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels
    return obj


# --- Output ------------------------------------------------------------------------------------

def export(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_apply=True,
                              export_materials="EXPORT")
    reverse_winding(path)
    print("exported", path)


def _camera(name, location, rotation, ortho_scale=None):
    data = bpy.data.cameras.new(name)
    if ortho_scale is not None:
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new(name, data)
    cam.location = location
    cam.rotation_euler = rotation
    bpy.context.scene.collection.objects.link(cam)
    return cam


def preview(prefix, size=(24, 28), scale=16):
    """Renders a top view (orthographic, framed like the sprite: size in game pixels) and a
    three-quarter view, to <prefix>_top.png and <prefix>_3q.png."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    world = bpy.data.worlds.new("preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.37, 0.42, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("sun", sun)
    # The game's sun: from the upper left of the screen, slightly from the bottom.
    sun_obj.rotation_euler = Vector((0.45, 0.35, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)

    w, h = size
    scene.render.resolution_x = w * scale
    scene.render.resolution_y = h * scale
    top = _camera("top", (0, 0, 100), (0, 0, 0), ortho_scale=max(w, h))
    scene.camera = top
    scene.render.filepath = prefix + "_top.png"
    bpy.ops.render.render(write_still=True)

    scene.render.resolution_x = scene.render.resolution_y = 512
    three_quarter = _camera("3q", (38, -48, 42), (math.radians(55), 0, math.radians(38)))
    scene.camera = three_quarter
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)


def finish(default_out):
    """Exports to --out (or default_out) and renders previews if --preview is given."""
    options = args()
    export(options.get("out", default_out))
    if "preview" in options:
        preview(options["preview"])
