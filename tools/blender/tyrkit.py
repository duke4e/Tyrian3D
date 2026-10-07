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


_level_palette = None


def level_palette():
    """The palette levels are played in (palette_levels.txt, from TYR3D_EXTRACT's palette.txt):
    256 (r, g, b), in ramps of 16 shades, dark to light: index 16 * ramp + shade."""
    global _level_palette
    if _level_palette is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "palette_levels.txt")
        _level_palette = [tuple(int(v) for v in line.split()) for line in open(path) if line.strip()]
    return _level_palette


def material(name, color=None, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0, palette=None,
             alpha=None):
    """A Principled BSDF material. color is 0-255 sRGB, the colour an up-facing surface shows in
    the game (a sprite's colour): the albedo is that divided by the game's light.

    alpha (0-1) makes it see-through (glass): exported with alphaMode BLEND, drawn blended.

    palette=<index> colours the material with that palette index instead, as the game colours
    sprites: the game takes the colour from the current palette (so it follows the level's
    palette, its fades and filters), Blender shows the levels' palette. Such materials are named
    "<name>@<index>"; tools/blender/sprite_profile.py lists a sprite's indices."""
    if palette is not None:
        color = level_palette()[palette]
        name = f"{name}@{palette}"
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
    if alpha is not None:
        bsdf.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
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


def _lobed_hit(angle, lobes, origin_z):
    """The farthest point of a union of lobes along the ray from (0, origin_z) at angle: its
    distance and the lobe it lies on."""
    dx, dz = math.cos(angle), math.sin(angle)
    best, owner = 0.0, 0
    for lobe, (cx, cz, w, top, bottom) in enumerate(lobes):
        if w < 0.05:
            continue
        for h, upper in ((top, True), (bottom, False)):
            if h < 0.05:
                continue
            # Points origin + t * direction on the ellipse ((x - cx) / w)^2 + ((z - cz) / h)^2 = 1.
            ox, oz = -cx, origin_z - cz
            qa = (dx / w) ** 2 + (dz / h) ** 2
            qb = 2 * (ox * dx / w ** 2 + oz * dz / h ** 2)
            qc = (ox / w) ** 2 + (oz / h) ** 2 - 1
            disc = qb * qb - 4 * qa * qc
            if disc < 0:
                continue
            for t in ((-qb + math.sqrt(disc)) / (2 * qa), (-qb - math.sqrt(disc)) / (2 * qa)):
                if t > best and (origin_z + t * dz >= cz) == upper:
                    best, owner = t, lobe
    return best, owner


def lobed_ring(y, lobes, segments=64, origin_z=0.0, owners=None, creases=None):
    """A cross-section in the XZ plane at y: the outline of a union of lobes, for hulls with pods
    or ridges whose creases should show. Each lobe (x, z, half_width, top, bottom) is an ellipse
    centred at (x, z) whose upper and lower halves have the given heights; lobes with a
    half-width or height near 0 are left out. The outline is traced along rays from
    (0, origin_z), which must be inside the union. Points run counter-clockwise seen from +Y.
    If owners is a list, the index of the lobe each point lies on is appended to it; if creases
    is a list, ((lobe, lobe), point) is appended for every point where one lobe meets another
    (found exactly, between the samples), for seams (crease_seams)."""
    points, hits = [], []
    for k in range(segments):
        a = 2 * math.pi * k / segments
        t, owner = _lobed_hit(a, lobes, origin_z)
        hits.append((a, owner))
        points.append(Vector((t * math.cos(a), y, origin_z + t * math.sin(a))))
        if owners is not None:
            owners.append(owner)
    if creases is not None:
        for k in range(segments):
            (a0, o0), (a1, o1) = hits[k], hits[(k + 1) % segments]
            if o0 == o1:
                continue
            if a1 < a0:
                a1 += 2 * math.pi
            for _ in range(16):  # bisect to where the owner changes
                mid = (a0 + a1) / 2
                if _lobed_hit(mid, lobes, origin_z)[1] == o0:
                    a0 = mid
                else:
                    a1 = mid
            a = (a0 + a1) / 2
            t, _ = _lobed_hit(a, lobes, origin_z)
            creases.append(((min(o0, o1), max(o0, o1)), Vector((t * math.cos(a), y, origin_z + t * math.sin(a)))))
    return points


def crease_seams(name, ring_creases, mat, radius=0.25, sink=0.05, min_z=0.3, max_jump=0.5):
    """Dark seams along the upper creases of a hull lofted from lobed rings: a thin tube follows
    each line where one lobe meets another on top (above min_z; ring_creases: the creases lists
    of lobed_ring, ring by ring), sunk a little into the hull so a narrow line shows, as the
    sprites draw such grooves. Returns the tube objects."""
    curves = {}
    for creases in ring_creases:
        top = {}  # the upper crease of each pair and side in this ring (the camera sees the top)
        for pair, point in creases:
            key = (pair, point.x > 0)
            if point.z > min_z and (key not in top or point.z > top[key].z):
                top[key] = point
        for key, point in top.items():
            curves.setdefault(key, []).append(point)
    # Each line, cut where the crease jumps (where lobes stop meeting cleanly), into runs.
    runs = []
    for key, line in sorted(curves.items(), key=lambda kv: str(kv[0])):
        line.sort(key=lambda p: p.y)
        run = [line[0]]
        for p in line[1:]:
            if abs(p.x - run[-1].x) < max_jump and abs(p.z - run[-1].z) < max_jump:
                run.append(p)
            else:
                runs.append(run)
                run = [p]
        runs.append(run)
    tubes = []
    for i, run in enumerate(r for r in runs if len(r) >= 4):
        tube_rings = []
        for p in run:
            inward = Vector((-p.x, 0, -p.z))
            if inward.length > 1e-6:
                inward.normalize()
            c = p + inward * sink
            tube_rings.append(ring(c.y, radius, radius, 8, z=c.z, x=c.x))
        tube = loft(f"{name}_{i}", tube_rings, mat)
        smooth(tube, 60)
        tubes.append(tube)
    return tubes


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


def slab(name, outline, z0, z1, mat=None, bevel_width=0.0, bevel_segments=2):
    """A flat part (wing, fin, plate): the polygon `outline` [(x, y), ...] in the XY plane,
    counter-clockwise seen from above, extruded from z0 to z1. Outlines may be concave."""
    bm = bmesh.new()
    bottom = [bm.verts.new((x, y, z0)) for x, y in outline]
    face = bm.faces.new(bottom)
    bmesh.ops.reverse_faces(bm, faces=[face])  # the bottom faces down
    result = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [e for e in result["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, z1 - z0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel_width > 0:
        bevel(obj, bevel_width, bevel_segments)
    return obj


def lathe(name, profile_points, mat=None, segments=24, axis_x=0.0, axis_z=0.0, squash=1.0):
    """A round part (pod, bottle, nozzle) turned around an axis along Y: profile_points are
    (y, radius) pairs in increasing y; squash scales the height (z) of the cross-sections."""
    rings = [ring(y, r, r * squash, segments, z=axis_z, x=axis_x) for y, r in profile_points if r > 0]
    first, last = profile_points[0], profile_points[-1]
    return loft(name, rings, mat,
                start_point=(axis_x, first[0], axis_z) if first[1] > 0 else (axis_x, first[0], axis_z),
                end_point=(axis_x, last[0], axis_z))


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


def sprite_mask(sheet, index, large=True):
    """Coverage of a sprite in a sheet exported by TYR3D_EXTRACT: rows of bools."""
    from sprite_profile import sprite_pixels
    return [[p is not None for p in row] for row in sprite_pixels(sheet, index, large)]


def check_silhouette(sheet, index, large=True, supersample=4):
    """Renders the model's top view at the sprite's resolution and compares it with the sprite's
    silhouette: prints the overlap (intersection over union) and a map where '#' is covered by
    both, '+' by the model only and '-' by the sprite only."""
    mask = sprite_mask(sheet, index, large)
    h, w = len(mask), len(mask[0])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = _camera("silhouette", (0, 0, 100), (0, 0, 0), ortho_scale=max(w, h))
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "tyrkit_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    pixels = list(image.pixels)
    covered = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            alpha = 0.0
            for sy in range(supersample):
                for sx in range(supersample):
                    px, py = x * supersample + sx, rh - 1 - (y * supersample + sy)  # images are bottom-up
                    alpha += pixels[(py * rw + px) * 4 + 3]
            covered[y][x] = alpha / supersample ** 2 > 0.5
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    print("silhouette overlap: %.3f" % (both / max(either, 1)))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    bpy.data.objects.remove(cam)
    return both / max(either, 1)


def finish(default_out):
    """Exports to --out (or default_out) and renders previews if --preview is given."""
    options = args()
    if "check" in options:  # --check <sheet.png>:<sprite index>
        sheet, index = options["check"].rsplit(":", 1)
        check_silhouette(sheet, int(index))
    export(options.get("out", default_out))
    if "preview" in options:
        preview(options["preview"])
