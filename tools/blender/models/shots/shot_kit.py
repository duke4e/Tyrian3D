"""Helpers for the shot models (the player's and enemies' projectiles that are objects: missiles,
bombs, slugs, a throwing star, balls and the fun weapons' food), built by shots_missiles.py,
shots_objects.py and shots_food.py.

Shots are 1x1 sprites of the shots sheets (12 x 14 pixels, origin at pixel (6, 7)): the game puts the
model's origin where the sprite's centre is and centres it in height. Models are authored as their
reference sprite is drawn (yaw 0); a sprite that shows the same object at another angle gets its own
`shot` line with the yaw (degrees clockwise from up) that turns the model onto it. Those yaws are
found here by turning the model's top view and matching it with each sprite's outline.
Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera).
The shape helpers come from the sidekicks' kit (sidekick_kit.py).

usage: Blender -b --factory-startup -P <shots_*.py> -- [--only <name>,...] [--sheets <dir>]
           [--preview <dir>] [--cfg <dir>] [--out <dir>]
--sheets: the sheets exported by TYR3D_EXTRACT (shots.png, shots2.png): prints each model's silhouette
overlap with its reference sprite and fits the yaw of the other sprites it serves. --preview renders
<dir>/<name>_top.png (framed like the sprite), _3q.png and, per sprite, <name>_at_<sheet>_<sprite>.png
(the top view at that sprite's yaw). --cfg writes the model's models.cfg lines to <dir>/<name>.cfg.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sidekicks"))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import sidekick_kit as s  # noqa: E402
from sidekick_kit import k  # noqa: E402
from sprite_profile import sprite_pixels  # noqa: E402

ASSETS = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")


# --- Pixels and materials ------------------------------------------------------------------------

def px(col):
    """The centre of sprite column col in model units."""
    return col - 5.5


def py(row):
    """The centre of sprite row row in model units."""
    return 6.5 - row


def pal(name, index, metallic=0.45, roughness=0.3, glow=None, strength=1.0):
    return s.pal(name, index, metallic=metallic, roughness=roughness, glow=glow, strength=strength)


def light(name, rgb, strength=3.0, color=None):
    return s.light(name, rgb, strength, color=color)


# --- Shapes ----------------------------------------------------------------------------------------

def flame(name, x, y_root, y_tip, radius, core, outer, z=0.0):
    """A rocket's exhaust along -Y: a glowing outer cone from y_root down to y_tip round a brighter core."""
    length = y_root - y_tip
    s.lathe_axis(name, [(0, radius), (length * 0.25, radius * 1.05), (length * 0.6, radius * 0.6),
                        (length, 0.0)], outer, (x, y_root, z), (0, -1, 0), segments=12, smooth_angle=80)
    s.lathe_axis(name + "_core", [(0, radius * 0.6), (length * 0.3, radius * 0.55), (length * 0.55, 0.0)], core,
                 (x, y_root - 0.05, z + radius * 0.25), (0, -1, 0), segments=10, smooth_angle=80)


def fin(name, root, tip, angle, mat, thickness=0.4, x=0.0, z=0.0):
    """A fin standing out from a body along Y: root = (radius, y_front, y_back) where it leaves the
    body, tip = (radius, y_front, y_back) at its outer edge; angle: its direction round the body
    (0 = +X, 90 = up towards the camera)."""
    r0, f0, b0 = root
    r1, f1, b1 = tip
    outline = [(r0, f0), (r1, f1), (r1, b1), (r0, b0)]
    obj = s.slab(name, outline, -thickness / 2, thickness / 2, mat, bevel=min(0.15, thickness * 0.4), segments=1)
    # Built in the XY plane (span along X); turned round Y to its angle, then moved to the axis.
    a = math.radians(angle)
    obj.data.transform(Matrix.Translation((x, 0, z)) @ Matrix.Rotation(-a, 4, "Y"))
    return obj


def bevel_ring(name, x, y, radius, width, depth, mat, z=0.0, squash=1.0, segments=14):
    """A raised ring round a body along Y (a band, a groove's lips): radius at y, `width` along Y."""
    return s.lathe_y(name, [(y - width / 2, radius - depth), (y - width / 2 + 0.08, radius),
                            (y + width / 2 - 0.08, radius), (y + width / 2, radius - depth)], mat, x=x, z=z,
                     squash=squash, segments=segments)


def interp(profile, y):
    for (y0, r0), (y1, r1) in zip(profile, profile[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / max(y1 - y0, 1e-6)
    return profile[0][1] if y < profile[0][0] else profile[-1][1]


def body(prefix, profile, parts, x=0.0, z=0.0, squash=1.0, segments=14, step=0.45, grow=0.0):
    """A turned body along Y from a smooth profile [(y, radius)] (tail to nose), cut into parts
    [(y_from, y_to, material)], each closed at its ends (the caps hide inside the neighbours);
    grow widens it (sprites drawn with a dark outline)."""
    samples = [(p[0], p[1] + (grow if p[1] > 0 else 0.0)) for p in k.profile(profile, step=step)]
    for i, (y0, y1, mat) in enumerate(parts):
        pts = [(y0, interp(samples, y0))] + [(y, r) for y, r in samples if y0 < y < y1] + [(y1, interp(samples, y1))]
        s.lathe_y(f"{prefix}{i}", pts, mat, x=x, z=z, squash=squash, segments=segments, smooth_angle=60)


def nozzle(prefix, x, y, radius, dark, z=0.0, length=0.6):
    s.lathe_axis(prefix + "nozzle", [(0, radius * 0.8), (0.15, radius), (length, radius * 1.05),
                                     (length + 0.02, radius * 0.7)], dark, (x, y, z), (0, -1, 0), segments=12)


def rotate_z(objects, degrees):
    """Turns the objects round the origin, counter-clockwise seen from above (as Blender does)."""
    m = Matrix.Rotation(math.radians(degrees), 4, "Z")
    for obj in objects:
        obj.data.transform(m)


# --- Silhouettes: overlap with the sprite and the yaw that fits a sprite ---------------------------

def _material_rgb(mat):
    """The 0-255 sRGB colour a material shows from above (its emission if it glows)."""
    if mat is None or not mat.use_nodes:
        return (128, 128, 128)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    emission = bsdf.inputs["Emission Strength"].default_value
    colour = bsdf.inputs["Emission Color"].default_value if emission > 1.5 else bsdf.inputs["Base Color"].default_value

    def to_srgb(c):
        c = max(0.0, min(1.0, c * (k.UP_FACING_LIGHT if emission <= 1.5 else 1.0)))
        return 255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)
    return tuple(to_srgb(colour[i]) for i in range(3))


def top_triangles():
    """Every triangle of the scene's meshes: positions (n, 3, 3) and the colour each shows from
    above (n, 3)."""
    deps = bpy.context.evaluated_depsgraph_get()
    out, colours = [], []
    for obj in s.meshes():
        ev = obj.evaluated_get(deps)
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        mw = obj.matrix_world
        co = np.array([(mw @ v.co)[:] for v in mesh.vertices], dtype=np.float64)
        idx = np.array([t.vertices[:] for t in mesh.loop_triangles], dtype=np.int64)
        mats = [_material_rgb(slot.material) for slot in obj.material_slots] or [(128, 128, 128)]
        if len(idx):
            out.append(co[idx])
            colours.append(np.array([mats[min(t.material_index, len(mats) - 1)] for t in mesh.loop_triangles]))
        ev.to_mesh_clear()
    return np.concatenate(out), np.concatenate(colours)


SS = 4  # samples per pixel along each axis
_points = None


def _sample_points():
    global _points
    if _points is None:
        xs = -6 + (np.arange(12 * SS) + 0.5) / SS
        ys = 7 - (np.arange(14 * SS) + 0.5) / SS
        gx, gy = np.meshgrid(xs, ys)
        _points = (gx.ravel(), gy.ravel())
    return _points


def raster(model, yaw):
    """The model's top view turned by yaw (clockwise, as the game turns shots) at the sprite's
    resolution: covered fractions (14, 12) and the colour seen at each pixel (14, 12, 3)."""
    tris, colours = model
    t = math.radians(yaw)
    c, sn = math.cos(t), math.sin(t)
    x = tris[..., 0] * c + tris[..., 1] * sn
    y = -tris[..., 0] * sn + tris[..., 1] * c
    z = tris[..., 2]
    pxs, pys = _sample_points()
    best_z = np.full(pxs.shape, -np.inf)
    best_c = np.zeros(pxs.shape + (3,))
    for i in range(0, len(x), 160):
        ax, bx, cx = (x[i:i + 160, j][:, None] for j in range(3))
        ay, by, cy = (y[i:i + 160, j][:, None] for j in range(3))
        az, bz, cz = (z[i:i + 160, j][:, None] for j in range(3))
        e0 = (bx - ax) * (pys - ay) - (by - ay) * (pxs - ax)
        e1 = (cx - bx) * (pys - by) - (cy - by) * (pxs - bx)
        e2 = (ax - cx) * (pys - cy) - (ay - cy) * (pxs - cx)
        inside = ((e0 >= 0) & (e1 >= 0) & (e2 >= 0)) | ((e0 <= 0) & (e1 <= 0) & (e2 <= 0))
        area = e0 + e1 + e2
        safe = np.where(np.abs(area) < 1e-9, 1.0, area)
        zz = np.where(inside & (np.abs(area) >= 1e-9), (e1 * az + e2 * bz + e0 * cz) / safe, -np.inf)
        top = zz.argmax(axis=0)
        top_z = zz[top, np.arange(zz.shape[1])]
        better = top_z > best_z
        best_z = np.where(better, top_z, best_z)
        best_c[better] = colours[i:i + 160][top[better]]
    covered = np.isfinite(best_z)
    cov = covered.reshape(14, SS, 12, SS).mean(axis=(1, 3))
    rgb = (best_c * covered[:, None]).reshape(14, SS, 12, SS, 3).sum(axis=(1, 3))
    rgb = rgb / np.maximum(covered.reshape(14, SS, 12, SS).sum(axis=(1, 3)), 1)[..., None]
    return cov, rgb


def coverage(model, yaw):
    return raster(model, yaw)[0]


def sprite_image(sheets, sheet, sprite):
    """The sprite's coverage (14, 12) and colours (14, 12, 3)."""
    pixels = sprite_pixels(os.path.join(sheets, sheet + ".png"), sprite, large=False)
    mask = np.array([[p is not None for p in row] for row in pixels])
    rgb = np.array([[p if p is not None else (0, 0, 0) for p in row] for row in pixels], dtype=np.float64)
    return mask, rgb


def sprite_mask(sheets, sheet, sprite):
    return sprite_image(sheets, sheet, sprite)[0]


def overlap(cov, mask):
    model = cov > 0.5
    return (model & mask).sum() / max((model | mask).sum(), 1)


def colour_distance(cov, rgb, sprite):
    """The mean colour difference (0-1) where the model and the sprite both cover a pixel."""
    mask, srgb = sprite
    both = (cov > 0.5) & mask
    if not both.any():
        return 1.0
    return float(np.linalg.norm(rgb[both] - srgb[both], axis=1).mean() / 441.7)


def score(model, yaw, sprite, colour_weight=0.6):
    cov, rgb = raster(model, yaw)
    return overlap(cov, sprite[0]) - colour_weight * colour_distance(cov, rgb, sprite)


def fit_yaw(model, sprite, near=None, spread=60, colour_weight=0.6):
    """The yaw (whole degrees) whose top view matches the sprite best (outline and colours), within
    spread degrees of near if given; returns (yaw, score, overlap)."""
    coarse = range(0, 360, 6) if near is None else range(near - spread, near + spread + 1, 6)
    best = max((score(model, yaw, sprite, colour_weight), yaw) for yaw in coarse)
    best = max(((score(model, yaw, sprite, colour_weight), yaw) for yaw in range(best[1] - 5, best[1] + 6)),
               key=lambda b: b[0])
    yaw = best[1] % 360
    return yaw, best[0], overlap(coverage(model, yaw), sprite[0])


def print_map(cov, mask):
    model = cov > 0.5
    for r in range(14):
        print("    " + "".join("#" if model[r, c] and mask[r, c] else "+" if model[r, c] else "-" if mask[r, c] else "."
                               for c in range(12)))


# --- Previews ---------------------------------------------------------------------------------------

def _scene_setup():
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
    return scene


def preview(prefix, turns=()):
    """Top view framed like the sprite, a three-quarter view, and top views turned by each yaw in
    turns ((suffix, yaw), ...)."""
    scene = _scene_setup()
    top = k._camera("top", (0, 0, 100), (0, 0, 0), ortho_scale=14)
    scene.camera = top
    scene.render.resolution_x, scene.render.resolution_y = 12 * 24, 14 * 24
    scene.render.filepath = prefix + "_top.png"
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x = scene.render.resolution_y = 512
    d = 0.3
    three_quarter = k._camera("3q", (38 * d, -48 * d, 42 * d), (math.radians(55), 0, math.radians(38)))
    scene.camera = three_quarter
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)
    if turns:
        scene.camera = top
        scene.render.resolution_x, scene.render.resolution_y = 12 * 16, 14 * 16
        objects = s.meshes()
        for suffix, yaw in turns:
            m = Matrix.Rotation(math.radians(-yaw), 4, "Z")
            saved = [o.matrix_world.copy() for o in objects]
            for o in objects:
                o.matrix_world = m @ o.matrix_world
            scene.render.filepath = f"{prefix}_at_{suffix}.png"
            bpy.ops.render.render(write_still=True)
            for o, w in zip(objects, saved):
                o.matrix_world = w


# --- Registry and build loop --------------------------------------------------------------------------

MODELS = []  # (name, (sheet, sprite) authored as drawn, shots, note, builder)


def model(name, reference, shots, note=""):
    """Registers a model built by the decorated function. reference: (sheet, sprite) the model is
    authored as (yaw 0), or None; shots: [(sheet, sprite, yaw or None to fit it, options, comment)]."""
    def register(fn):
        MODELS.append((name, reference, shots, note, fn))
        return fn
    return register


def run():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    out = options.get("out", ASSETS)
    sheets = options.get("sheets")
    for name, reference, shots, note, build in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        tris_count = s.triangles()
        print(f"== {name}: {tris_count} triangles")
        lines = []
        turns = []
        if sheets:
            tris = top_triangles()
            if reference:
                sprite = sprite_image(sheets, *reference)
                cov, rgb = raster(tris, 0)
                print(f"  {reference[0]} {reference[1]} as drawn: overlap {overlap(cov, sprite[0]):.3f}, "
                      f"colour difference {colour_distance(cov, rgb, sprite):.3f}")
                print_map(cov, sprite[0])
        for sheet, sprite, yaw, opts, comment in shots:
            near = None
            if isinstance(yaw, tuple):  # ("~", near): fit within 60 degrees of near
                near, yaw = yaw[1], None
            if sheets:
                sprite_data = sprite_image(sheets, sheet, sprite)
                if yaw is None:
                    yaw, fit, ov = fit_yaw(tris, sprite_data, near)
                    print(f"  {sheet} {sprite}: fitted yaw {yaw}, score {fit:.3f}, overlap {ov:.3f}")
                else:
                    cov, rgb = raster(tris, yaw)
                    print(f"  {sheet} {sprite}: yaw {yaw}, overlap {overlap(cov, sprite_data[0]):.3f}, "
                          f"colour difference {colour_distance(cov, rgb, sprite_data):.3f}")
            if yaw is None:
                yaw = near or 0
            turns.append((f"{sheet}_{sprite}", yaw))
            line = f"shot {sheet} {sprite} {name}" + (f" yaw={yaw}" if yaw else "") + (f" {opts}" if opts else "")
            lines.append((line, comment))
        k.export(os.path.join(out, name + ".glb"))
        if "cfg" in options:
            os.makedirs(options["cfg"], exist_ok=True)
            with open(os.path.join(options["cfg"], name + ".cfg"), "w") as f:
                f.write(f"model {name} shots/{name}.glb\n")
                width = max(len(line) for line, _ in lines)
                for line, comment in lines:
                    f.write(f"{line.ljust(width)}  # {comment}\n" if comment else line + "\n")
                f.write(f"#! {tris_count} triangles; {note}\n")
        if "preview" in options:
            os.makedirs(options["preview"], exist_ok=True)
            preview(os.path.join(options["preview"], name), turns)
