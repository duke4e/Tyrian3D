"""Helpers for the batch N models of wave 3 (sheet 3: SURFACE, DESERTRUN and CORE; wave3_n.py, the
machines and ships, wave3_n_rocks.py, the rock arch and the stepped pyramid, wave3_n_fire.py, CORE's
fire): the sprites' pixels (wave3_n_art.py), the parts and materials of batch J's kit
(wave3_j_kit.py, re-exported here), painting faces by the sprite's shades, relief solids inflated from
the pixels, larger objects built whole and cut into their sprites' pieces (several pieces from one
build), the silhouette check against any pixel mask, and the build loop.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre. Pixel art rows run top to bottom; pixel (column c, row r) of an
art with origin (ox, oy) covers x = c - ox .. c + 1 - ox, y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_art as art  # noqa: E402,F401
from glb_winding import reverse_winding  # noqa: E402
from wave3_j_kit import (pal, grid, regions, relabel, px, py, sampler, paint_faces, part, lathe_axis, hoop,  # noqa: E402,F401
                         column, tube, catmull, sphere, rounded_box, block, meshes, bake, triangles, simplify_bottom,
                         decimate, floor)

ENEMIES = w.ENEMIES
SHEET = "enemy_3"


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def joined(*parts):
    """Grids side by side: parts are (grid, width) pairs, padded to the tallest."""
    h = max(len(g) for g, _ in parts)
    out = []
    for r in range(h):
        row = []
        for g, width in parts:
            row += g[r] if r < len(g) else [None] * width
        out.append(row)
    return out


def band_index(value, bands):
    """The index of the band value falls in: bands [(lowest value, material)], ascending."""
    index = 0
    for i, (lowest, _) in enumerate(bands):
        if value >= lowest:
            index = i
    return index


def paint_shades(obj, shade, bands, wall=None, under=None, wall_drop=2.5, wall_z=0.35):
    """Paints the faces by the sprite's shade under their centres: shade(x, y) -> value, bands
    [(lowest value, material)]; faces steeper than wall_z take the band wall_drop lower (or `wall`),
    faces looking down take `under` (default: the darkest band)."""
    def pick(c, n):
        if n.z < -0.5:
            return under or bands[0][1]
        s = shade(c.x, c.y)
        if abs(n.z) < wall_z:
            if wall is not None:
                return wall
            s -= wall_drop
        return bands[band_index(s, bands)][1]
    return paint_faces(obj, pick)


def merge_by_material(objects=None):
    """Joins the meshes into one object (fewer draw calls)."""
    objs = objects or meshes()
    if len(objs) < 2:
        return objs[0] if objs else None
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
        bpy.ops.object.join()
    return objs[0]


def budget(target=4800, objects=None):
    """Keeps a model light: its larger meshes are decimated until the whole has about `target`
    triangles. Returns the count."""
    objs = objects or meshes()
    for obj in objs:
        sh.apply_modifiers(obj)

    def count(o):
        return sum(len(p.vertices) - 2 for p in o.data.polygons)
    total = sum(count(o) for o in objs)
    if total <= target:
        return total
    big = [o for o in objs if count(o) > 300]
    small = total - sum(count(o) for o in big)
    ratio = max(0.08, (target - small) / max(1, total - small))
    for obj in big:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return sum(count(o) for o in objs)


def soft_floor(name, g, bands, is_floor, origin=(12, 14), top=0.8, relief=0.6, edge=1.2, blur=2, step=1.0):
    """The ground a sprite draws round its object (sand, dust), as a low slab over the whole sprite
    like wave3_j_kit.floor but smooth: a heightfield whose relief and colours follow the floor
    pixels' shades blurred `blur` times (bands: [(lowest shade, material)]), its edge falling away
    over `edge` pixels. Pixels that are not floor lie flat at `top`."""
    import bmesh
    h, wd = len(g), len(g[0])
    ox, oy = origin
    shade = sampler(g, origin, value=lambda v: v & 15, blur=blur,
                    keep=lambda v: v is not None and is_floor(v, 0, 0))
    known = [g[r][c] & 15 for r in range(h) for c in range(wd) if g[r][c] is not None and is_floor(g[r][c], c, r)]
    lo, hi = (np.percentile(known, 10), np.percentile(known, 90)) if known else (2, 7)
    span = max(hi - lo, 1.0)
    nx, ny = int(round(wd / step)), int(round(h / step))

    def height(i, j):
        x, y = i * step - ox, oy - j * step
        border = min(i * step, wd - i * step, j * step, h - j * step)
        fall = min(1.0, border / edge)
        z = top + relief * (min(max((shade(x, y) - lo) / span, 0.0), 1.0) - 0.5)
        return max(0.05, z * (0.35 + 0.65 * math.sqrt(fall)))
    bm = bmesh.new()
    verts = [[bm.verts.new((i * step - ox, oy - j * step, height(i, j))) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            a, b, c, d = verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]
            tris = [(a, d, c), (a, c, b)] if abs(a.co.z - c.co.z) <= abs(b.co.z - d.co.z) else [(a, d, b), (b, d, c)]
            for t in tris:
                f = bm.faces.new(t)
                cx = sum(v.co.x for v in t) / 3
                cy = sum(v.co.y for v in t) / 3
                f.material_index = band_index(shade(cx, cy), bands)
    ring = [verts[0][i] for i in range(nx + 1)] + [verts[j][nx] for j in range(1, ny + 1)] + \
           [verts[ny][i] for i in range(nx - 1, -1, -1)] + [verts[j][0] for j in range(ny - 1, 0, -1)]
    low = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in ring]
    for i in range(len(ring)):
        f = bm.faces.new((ring[i], ring[(i + 1) % len(ring)], low[(i + 1) % len(ring)], low[i]))
        f.material_index = 0
    bottom = bm.faces.new(list(reversed(low)))
    bottom.material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for _, m in bands:
        obj.data.materials.append(m)
    return k.smooth(obj, 40)


# --- Masks and the silhouette check ----------------------------------------------------------------

def art_mask(g, box=None):
    """A grid's coverage (rows of bools); box (c0, c1, r0, r1), end exclusive, keeps only that part of
    the grid (the rest counts as empty) and crops to it."""
    h, wd = len(g), len(g[0])
    c0, c1, r0, r1 = box or (0, wd, 0, h)
    return [[0 <= r < h and 0 <= c < wd and g[r][c] is not None for c in range(c0, c1)] for r in range(r0, r1)]


def check_mask(mask, label="", supersample=4, offset=(0.0, 0.0)):
    """Compares the scene's top view with a pixel mask (rows of bools centred on the origin, moved
    by offset): prints the overlap (intersection over union) and a map ('#' both, '+' model only,
    '-' mask only)."""
    h, wd = len(mask), len(mask[0])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = wd * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = k._camera("silhouette", (offset[0], offset[1], 200), (0, 0, 0), ortho_scale=max(wd, h))
    cam.data.clip_end = 1000
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "wave3n_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    covered = alpha.reshape(h, supersample, wd, supersample).mean(axis=(1, 3)) > 0.5
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(wd))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(wd))
    score = both / max(either, 1)
    print("silhouette overlap %s: %.3f" % (label, score))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(wd)))
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    return score


# --- Output --------------------------------------------------------------------------------------

def export_objects(objects, path):
    """Exports only the given objects (glTF binary, the game's winding)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_apply=True,
                              export_materials="EXPORT", use_selection=True)
    reverse_winding(path)
    print("exported", path)


def clear_views():
    """Removes the cameras and lights previews leave behind."""
    for obj in list(bpy.context.scene.objects):
        if obj.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(obj)


def render_3q(prefix, size, scale=1.0):
    """A three-quarter view from farther away (for large objects), to <prefix>_3q.png."""
    scene = bpy.context.scene
    cam = bpy.data.objects["3q"]
    cam.location = Vector((38, -48, 42)) * scale
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = 1024, 768
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)


# --- Registry and build loop ---------------------------------------------------------------------

MODELS = []   # (name, builder, mask builder, size)
OBJECTS = []  # (object name, whole builder, size, [(piece name, box (x0, x1, y0, y1), centre (x, y), mask builder)])


def model(name, mask=None, size=(24, 28)):
    """Registers a stand-alone model; mask() -> rows of bools for --check (default: none)."""
    def register(fn):
        MODELS.append((name, fn, mask, size))
        return fn
    return register


def pieced(name, builder, size, pieces):
    """Registers an object built whole and cut into pieces: each (piece name, the box it keeps in the
    whole's coordinates, its sprite's centre there, mask() for --check or None)."""
    OBJECTS.append((name, builder, size, pieces))


def run():
    """Options after "--": --only a,b (models, objects or pieces)  --preview <prefix>
    --check 1 (silhouettes)  --stats 1  --whole <prefix> (renders the whole objects instead)."""
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    if "whole" in options:
        for name, build, size, pieces in OBJECTS:
            if only and name not in only:
                continue
            k.reset()
            build()
            bake()
            print(f"== whole {name}: {triangles()} triangles")
            # Centred for the views.
            pts = [v.co for o in meshes() for v in o.data.vertices]
            cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
            cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
            sh.move(meshes(), -cx, -cy)
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["whole"] + name, size, scale=max(4, int(640 / max(size))))
            render_3q(options["whole"] + name, size, max(size) / 40.0)
        return
    for name, build, mask, size in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        bake()
        raw = triangles()
        if "stats" in options:
            for obj in meshes():
                print(f"   {obj.name}: {sum(len(p.vertices) - 2 for p in obj.data.polygons)}")
        count = budget()
        print(f"== {name}: {count} triangles ({raw} before the budget), {len(meshes())} parts")
        if "check" in options and mask is not None:
            check_mask(mask(), name)
        k.export(os.path.join(ENEMIES, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)
    for name, build, size, pieces in OBJECTS:
        wanted = [p for p in pieces if not only or name in only or p[0] in only]
        if not wanted:
            continue
        k.reset()
        build()
        bake()
        whole_objects = meshes()
        for piece_name, (x0, x1, y0, y1), (cx, cy), mask in wanted:
            copies = []
            for obj in whole_objects:
                c = obj.copy()
                c.data = obj.data.copy()
                c.name = f"{piece_name}_{obj.name}"
                bpy.context.scene.collection.objects.link(c)
                copies.append(c)
            for obj in whole_objects:
                obj.hide_render = True
            kept = sh.cut_box(copies, x0, x1, y0, y1)
            sh.move(kept, -cx, -cy)
            for obj in kept:
                k.smooth(obj, 40)
            count = budget(4800, kept)
            print(f"== {piece_name}: {count} triangles, {len(kept)} parts")
            if "check" in options and mask is not None:
                check_mask(mask(), piece_name)
            export_objects(kept, os.path.join(ENEMIES, piece_name + ".glb"))
            if "preview" in options:
                bpy.context.scene.view_settings.view_transform = "Standard"
                k.preview(options["preview"] + piece_name, (24, 28))
                clear_views()
            for obj in kept:
                bpy.data.objects.remove(obj)
            for obj in whole_objects:
                obj.hide_render = False
