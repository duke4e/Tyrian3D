"""Renders .glb models to small PNGs in one Blender run, for contact sheets (tools/model_sheet.py).

usage: Blender -b --python tools/blender/render_models.py -- --out <dir> [--size 160] [--view 3q|top] <model.glb>...
       (or --list <file with one .glb path per line>)

Each model is framed by its bounds and lit like tyrkit.preview(); the PNG is <dir>/<model name>.png
(transparent background).
"""
import os
import shutil
import sys
import tempfile

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glb_winding import reverse_winding  # noqa: E402


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    options = {"size": "160", "view": "3q"}
    paths = []
    i = 0
    while i < len(argv):
        if argv[i].startswith("--"):
            options[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            paths.append(argv[i])
            i += 1
    if "list" in options:
        paths += [line.strip() for line in open(options["list"]) if line.strip()]
    return options, paths


def setup(size):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.view_settings.view_transform = "Standard"  # the colours as the game shows them
    world = bpy.data.worlds.new("preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.37, 0.42, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("sun", sun)
    # The game's sun (render_gpu.c sun_direction 0.6, -1, 0.6): from above and the top left of the screen.
    sun_obj.rotation_euler = Vector((0.6, -0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def frame(cam, objects, view):
    corners = []
    for obj in objects:
        if obj.type == "MESH":
            corners += [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    if not corners:
        return False
    lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    centre = (lo + hi) / 2
    extent = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z, 1.0)
    cam.data.ortho_scale = extent * (1.15 if view == "top" else 1.45)
    if view == "top":
        cam.location = centre + Vector((0, 0, 100))
        cam.rotation_euler = (0, 0, 0)
    else:
        # From in front and above, like the game's camera but steeper sideways for volume.
        direction = Vector((0.55, -0.75, 0.62)).normalized()
        cam.location = centre + direction * 100
        cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    return True


def main():
    options, paths = parse()
    out = options["out"]
    os.makedirs(out, exist_ok=True)
    size = int(options["size"])
    for path in paths:
        cam = setup(size)
        # The game's models are wound the other way round (glb_winding.py); back to glTF's for Blender.
        work = os.path.join(tempfile.gettempdir(), f"render_models_work_{os.getpid()}.glb")  # (one per run: runs in parallel)
        shutil.copyfile(path, work)
        reverse_winding(work)
        try:
            bpy.ops.import_scene.gltf(filepath=work)
        except Exception as error:  # noqa: BLE001 (a broken file shouldn't stop the run)
            print("failed", path, error)
            continue
        objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        if not frame(cam, objects, options["view"]):
            print("empty", path)
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        bpy.context.scene.render.filepath = os.path.join(out, name + ".png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name)


main()
