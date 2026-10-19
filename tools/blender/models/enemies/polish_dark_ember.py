"""The dark ember of TIME WAR and SQUADRON (sheet L sprite 118, 1x1: an 11 x 11 pod in the 12 x 14 cell; enemies 672 on
top and 722 on the ground; not animated), polished (2026-10-19; it replaces wave2_h.py's dark_ember()). models.cfg:
sprite l 118 dark_ember yaw=0 glow=6:0.3:123:-1:-1.5 (the lamp's glow added). No enemy shows the same pixels
elsewhere (sheet 5's sprite 19 is the same picture, but no enemy uses it).

As the sprite and its 4x upscale draw it: a pod of dark red glass (ramp 7, 0x70-0x76), a rounded block lying across
the sprite's diagonal, its long axis rising to the upper right (47 degrees; 11 x 8 pixels round column 6, row 7),
lit along its upper left edge; near that edge a small lamp glowing yellow-orange (0x79, 0x7b: columns 4-5 of row 5)
in a dark socket (0x70-0x71 below it, row 7).

The pod: a superellipsoid (a rounded block, its top crowned), a little uneven, dark red glowing faintly in its own
colour (the slanted camera sees much of it in shade), its upper rim a lighter red; the lamp a glowing dome in a dark
ring. Origin at the sprite's centre (pixel 6, 7); +Y up the sprite, +Z towards the camera; the game centres it in
height on its layer (it stands on z = 0).

Replaces wave2_h.py's dark_ember() (the function and its ("dark_ember", dark_ember, [("L", 118, False)], E) entry in
MODELS, and the dark_ember line of the docstring): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_L.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_balls import preview, triangles  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

CENTRE = Vector((0.25, -0.45))
ANGLE = 47.0                 # the long axis, degrees from +X
HALF = Vector((5.45, 4.05, 2.4))  # half-length, half-width, half-height (its middle at z = HALF.z)
POWER = (3.0, 2.6)           # the plan's squareness, the section's
CROWN = 0.45                 # its top bulges this much more in the middle
LAMP = Vector((-1.05, 1.45))  # the lamp's middle in the top view
LAMP_RADIUS = 0.95

# The shading bands of the pod: (lowest value, palette index, emission strength in the palette colour).
BANDS = [(-9.0, 0x70, 0.0), (0.2, 0x71, 0.06), (0.36, 0x72, 0.12), (0.6, 0x73, 0.16), (0.8, 0x74, 0.2),
         (0.92, 0x75, 0.25)]


def local(p):
    """A point in the pod's frame: along its long axis, across it."""
    a = math.radians(ANGLE)
    d = Vector((p.x - CENTRE.x, p.y - CENTRE.y))
    return Vector((d.x * math.cos(a) + d.y * math.sin(a), -d.x * math.sin(a) + d.y * math.cos(a)))


def pod_point(d):
    """The pod's surface in the unit direction d (its own frame: x along, y across, z up), as a superquadric."""
    px, py = POWER
    # Plan: |x/a|^px + |y/b|^px; section: combined with z by py.
    a, b, c = HALF
    plan = (abs(d.x) / a) ** px + (abs(d.y) / b) ** px
    r = 1.0 / ((plan ** (py / px)) + (abs(d.z) / c) ** py) ** (1.0 / py)
    p = d * r
    if p.z > 0:
        u = (p.x / a) ** 2 + (p.y / b) ** 2
        p.z += CROWN * max(0.0, 1 - u)
    return p


def build_pod(m):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    rot = Matrix.Rotation(math.radians(ANGLE), 3, "Z")
    values = []
    light = Vector((-0.55, 0.55, 0.63)).normalized()   # the sprite's light, from the upper left
    for v in bm.verts:
        d = v.co.normalized()
        p = pod_point(d)
        p += d * 0.03 * noise.noise(d * 2.3 + Vector((4.0, 1.0, 7.0)))
        world = rot @ p + Vector((CENTRE.x, CENTRE.y, HALF.z))
        v.co = world
    bm.normal_update()
    for v in bm.verts:
        n = v.normal
        # Shade: lighter where it faces the sprite's light, the upper rim lightest.
        values.append(0.45 + 0.5 * n.dot(light) - 0.25 * smoothstep(0.2, -0.4, n.z))
    mesh = bpy.data.meshes.new("pod")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("pod", mesh)
    bpy.context.scene.collection.objects.link(obj)
    band_split(obj, values, [(lowest, m[index]) for lowest, index, _ in BANDS])
    return k.smooth(obj, 70)


def surface_z(obj, x, y):
    from mathutils.bvhtree import BVHTree
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(obj, depsgraph)
    hit, normal, _, _ = tree.ray_cast(Vector((x, y, 50.0)), Vector((0, 0, -1)))
    return (hit.z, normal) if hit is not None else (HALF.z * 2, Vector((0, 0, 1)))


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    pal = k.level_palette()
    m = {index: k.material(f"ember_{index:x}", palette=index, metallic=0.1, roughness=0.22,
                           emission=pal[index] if glow > 0 else None, emission_strength=glow)
         for _, index, glow in BANDS}
    m["dome"] = k.material("ember_dome", palette=0x74, metallic=0.1, roughness=0.25, emission=pal[0x74],
                           emission_strength=0.35)
    m["lamp"] = k.material("ember_lamp", palette=0x7b, metallic=0.0, roughness=0.25, emission=pal[0x7b],
                           emission_strength=1.8)
    pod = build_pod(m)
    # The lamp: a small glowing bead on a dark red dome set into the pod's upper left.
    z, n = surface_z(pod, LAMP.x, LAMP.y)
    base = Vector((LAMP.x, LAMP.y, z))
    tilt = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
    place = Matrix.Translation(base) @ tilt
    dome = k.ellipsoid("lamp_dome", (0, 0, -0.25), (LAMP_RADIUS * 1.55, LAMP_RADIUS * 1.55, 1.05), m["dome"], 20, 10)
    dome.data.transform(place)
    k.smooth(dome, 60)
    bead = k.ellipsoid("lamp", (0, 0, 0.62), (LAMP_RADIUS * 0.7, LAMP_RADIUS * 0.7, 0.42), m["lamp"], 16, 8)
    bead.data.transform(place)
    k.smooth(bead, 60)
    used = {mat.name for obj in bpy.context.scene.objects if obj.type == "MESH" for mat in obj.data.materials}
    print("== dark_ember (L 118): %d triangles, %d materials: %s" % (triangles(), len(used), ", ".join(sorted(used))))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_L.png"), 118, large=False)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "dark_ember.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        preview(options["preview"] + "dark_ember", size=(12, 14), distance=0.5)


if __name__ == "__main__":
    build()
