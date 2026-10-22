"""Wave 2, batch E of the enemy models, authored as their sprites look (models.cfg: yaw=0 unless noted; the faceted orbs, V 153: polish_facet_orb.py):

- face_eye (sheet 5 270): the eyeballs of NOSE DRIP's face, authored looking up the screen so that
  yaw=aim turns them after the player (the sprite looks down the screen).
- nose_bridge (sheet 5 154): the bridge of NOSE DRIP's nose; nose_tip_left / nose_tip_right (5 191 / 193)
  are the tip below it, cut from the same nose.

The pieces of larger objects are built whole (wave2_e_parts.py, from the pixel art in wave2_e_art.py)
and cut along the sprites' edges, so they meet again in the game (models.cfg: origin).

usage: blender -b --factory-startup -P wave2_e.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--assembled <prefix>]
--preview renders <prefix><name>_top.png and _3q.png for each model; --check prints each model's
silhouette overlap with its sprite; --assembled renders the whole objects (<prefix><object>_top.png).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402
import wave2_e_parts as parts  # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models")
MODELS = []  # (name, builder, sheet file, sprite, large, directory, yaw of the preview)


def model(name, sheet, sprite, large=True, directory="enemies", preview_yaw=0.0):
    def register(fn):
        MODELS.append((name, fn, sheet, sprite, large, directory, preview_yaw))
        return fn
    return register


# --- NOSE DRIP's eye (sheet 5 270) ------------------------------------------------------------------

@model("face_eye", "5", 270, preview_yaw=180.0)
def face_eye():
    """A glossy eyeball, its blue iris and black pupil looking up the screen and towards the camera
    (models.cfg turns it towards the player with yaw=aim; the sprite looks down). Its centre is the
    sprite's (0.5, 1.5), radius 10.5; a little flattened."""
    white = k.material("eye_white", palette=62, metallic=0.0, roughness=0.12)
    iris = k.material("eye_iris", palette=57, metallic=0.1, roughness=0.15, emission=(40, 110, 170),
                      emission_strength=0.3)
    ring = k.material("eye_ring", palette=52, metallic=0.1, roughness=0.2)
    inner = k.material("eye_iris_inner", palette=55, metallic=0.1, roughness=0.15)
    pupil = k.material("eye_pupil", palette=48, metallic=0.2, roughness=0.06)
    cx, cy, rad, flat = -0.5, -1.5, 10.5, 0.8  # (0.5, 1.5) when turned to look down
    k.smooth(k.ellipsoid("ball", (cx, cy, 0.0), (rad, rad, rad * flat), white, 48, 24), 80)
    # The iris: a cap on the ball, turned towards (0, sin, cos) of the look's angle.
    look = math.radians(28)  # from straight up (the camera) towards +Y
    iris_angle = math.radians(35)

    def cap(name, angle, lift, mat, segments=40):
        rings = []
        steps = 8
        for i in range(1, steps + 1):
            a = angle * i / steps
            rings.append([(math.sin(a) * math.cos(2 * math.pi * s / segments),
                           math.sin(a) * math.sin(2 * math.pi * s / segments), math.cos(a)) for s in range(segments)])
        verts = [(0.0, 0.0, 1.0)]
        for rr in rings:
            verts += rr
        faces = [(0, 1 + (s + 1) % segments, 1 + s) for s in range(segments)]
        for i in range(steps - 1):
            for s in range(segments):
                a0, a1 = 1 + i * segments + s, 1 + i * segments + (s + 1) % segments
                faces.append((a0, a1, a1 + segments, a0 + segments))
        # The cap's rim tucks under the ball.
        rim = [(x * 0.97, y * 0.97, z * 0.97) for x, y, z in rings[-1]]
        base = len(verts)
        verts += rim
        last = 1 + (steps - 1) * segments
        for s in range(segments):
            faces.append((last + s, last + (s + 1) % segments, base + (s + 1) % segments, base + s))
        scaled = []
        for x, y, z in verts:
            p = Matrix.Rotation(-look, 3, "X") @ Vector((x, y, z))  # tilt towards +Y
            scaled.append((cx + p.x * (rad + lift), cy + p.y * (rad + lift), p.z * (rad + lift) * flat))
        obj = k.mesh_object(name, scaled, faces, mat)
        k.recalc_normals(obj)
        return k.smooth(obj, 80)

    # The iris in rings, dark at its rim and round the pupil, each a little proud of the last.
    cap("iris_ring", iris_angle, 0.1, ring)
    cap("iris", iris_angle * 0.88, 0.2, iris)
    cap("iris_inner", iris_angle * 0.55, 0.28, inner)
    cap("pupil", iris_angle * 0.33, 0.36, pupil)


# --- The assembled objects (wave2_e_parts.py) -------------------------------------------------------

for _name, _sheet, _sprite, _builder in parts.PIECES:
    model(_name, _sheet, _sprite)(_builder)


# --- Main ----------------------------------------------------------------------------------------

def triangles(obj):
    return sum(len(poly.vertices) - 2 for poly in obj.data.polygons)


def budget(target=4800):
    """Keeps a model light: with its modifiers applied, its larger meshes (the inflated parts) are
    decimated until the whole has about `target` triangles."""
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    for obj in meshes:
        sh.apply_modifiers(obj)
    total = sum(triangles(obj) for obj in meshes)
    if total <= target:
        return total
    big = [obj for obj in meshes if triangles(obj) > 400]
    small = total - sum(triangles(obj) for obj in big)
    ratio = max(0.12, (target - small) / max(1, total - small))
    for obj in big:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return sum(triangles(obj) for obj in meshes)


def main():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sheet, sprite, large, directory, preview_yaw in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        print(f"{name}: {budget()} triangles")
        k.export(os.path.join(ROOT, directory, name + ".glb"))
        if preview_yaw:
            for obj in bpy.data.objects:
                if obj.type == "MESH":
                    obj.data.transform(Matrix.Rotation(math.radians(preview_yaw), 4, "Z"))
        size = (24, 28) if large else (12, 14)
        if "check" in options:
            sheet_file = "coins.png" if sheet == "coins" else f"enemy_{sheet}.png"
            print(f"--- {name} (sheet {sheet} sprite {sprite})")
            k.check_silhouette(os.path.join(options["check"], sheet_file), [sprite], large)
        if "preview" in options:
            k.preview(options["preview"] + name, size)
    if "assembled" in options:
        for name, build, size in parts.ASSEMBLED:
            if only and name not in only:
                continue
            k.reset()
            build()
            k.preview(options["assembled"] + name, size, scale=8)
            # A three-quarter view from farther away, for the whole object.
            scene = bpy.context.scene
            cam = bpy.data.objects["3q"]
            cam.location = Vector((38, -48, 42)) * (max(size) / 44.0)
            scene.camera = cam
            scene.render.resolution_x, scene.render.resolution_y = 1024, 768
            scene.render.filepath = options["assembled"] + name + "_3q.png"
            bpy.ops.render.render(write_still=True)


main()
