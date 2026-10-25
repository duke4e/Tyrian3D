"""Destruct's units and walls (destruct3d.h): every unit for each side, the parts that aim apart.

blender -b -P tools/blender/models/destruct/destruct.py [-- --only <name> --preview <dir>]

Seen from the side, unlike the game's other models: X towards the other side (the left side's units
face +X; the right side's are drawn mirrored), Z up, Y away from the camera; 1 unit = 1 game pixel.
The origin is the middle of the unit's foot (the bottom of its 12 x 14 sprite). A part that aims (a
barrel, a rail, a tube, an emitter) has its origin at its pivot and points along +X; destruct.c's
units turn it by their angle (render_gpu.c present_destruct places it at the pivot below).
Out: assets/models/destruct/<name>.glb (models.cfg's destruct_* lines).
"""
import math
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "destruct")

TEAMS = {
    "l": {"body": (184, 144, 88), "dark": (96, 72, 44), "trim": (226, 190, 128), "lamp": (255, 168, 64)},
    "r": {"body": (82, 156, 74), "dark": (40, 82, 44), "trim": (150, 210, 130), "lamp": (96, 220, 255)},
}


def mats(team):
    t = TEAMS[team]
    return {
        "body": k.material(f"body_{team}", t["body"], metallic=0.35, roughness=0.42),
        "dark": k.material(f"dark_{team}", t["dark"], metallic=0.25, roughness=0.55),
        "trim": k.material(f"trim_{team}", t["trim"], metallic=0.7, roughness=0.3),
        "lamp": k.material(f"lamp_{team}", t["lamp"], emission=t["lamp"], emission_strength=6.0),
        "steel": k.material("steel", (156, 162, 172), metallic=0.85, roughness=0.32),
        "gun": k.material("gunmetal", (78, 80, 88), metallic=0.8, roughness=0.38),
        "track": k.material("track", (44, 42, 40), metallic=0.3, roughness=0.75),
        "red": k.material("red", (200, 42, 30), metallic=0.25, roughness=0.4),
        "white": k.material("white", (226, 226, 220), metallic=0.1, roughness=0.45),
        "glass": k.material("glass", (120, 190, 230), metallic=0.2, roughness=0.08),
        "panel": k.material("panel", (52, 86, 168), metallic=0.6, roughness=0.22),
        "dirt": k.material("dirt", (150, 108, 64), roughness=0.95),
        "crystal": k.material("crystal", (110, 180, 255), emission=(110, 190, 255), emission_strength=4.0, roughness=0.1),
    }


# --- Shapes ------------------------------------------------------------------------------------

def side(name, outline, d0, d1, mat, bevel=0.0):
    """A part cut in profile: the outline [(x, z), ...] (counter-clockwise as seen from the camera),
    from depth d0 to d1 (y)."""
    obj = k.slab(name, outline, -d1, -d0, mat, bevel_width=bevel, bevel_segments=2)
    obj.rotation_euler = (math.radians(90), 0, 0)
    with bpy.context.temp_override(selected_editable_objects=[obj], active_object=obj, object=obj):
        bpy.ops.object.transform_apply(rotation=True)
    return obj


def cylinder(name, a, b, radius, mat, segments=20, smooth=True):
    """A cylinder from point a to point b."""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=1.0, vertices=segments)
    obj = bpy.context.object
    obj.name = name
    ax, ay, az = a
    bx, by, bz = b
    d = (bx - ax, by - ay, bz - az)
    length = math.sqrt(sum(c * c for c in d))
    obj.scale = (1, 1, length)
    obj.location = ((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2)
    from mathutils import Vector
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    with bpy.context.temp_override(selected_editable_objects=[obj], active_object=obj, object=obj):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.materials.append(mat)
    if smooth:
        k.smooth(obj, 50)
    return obj


def cone(name, a, b, r0, r1, mat, segments=20):
    bpy.ops.mesh.primitive_cone_add(radius1=r0, radius2=r1, depth=1.0, vertices=segments)
    obj = bpy.context.object
    obj.name = name
    from mathutils import Vector
    d = Vector(b) - Vector(a)
    obj.scale = (1, 1, d.length)
    obj.location = (Vector(a) + Vector(b)) / 2
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    with bpy.context.temp_override(selected_editable_objects=[obj], active_object=obj, object=obj):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.materials.append(mat)
    k.smooth(obj, 50)
    return obj


def ball(name, centre, radii, mat, segments=20, rings=12):
    return k.smooth(k.ellipsoid(name, centre, radii, mat, segments, rings), 60)


def block(name, centre, size, mat, bevel=0.3):
    obj = k.box(name, centre, size, mat)
    if bevel > 0:
        k.bevel(obj, bevel, 2)
    return obj


def torus(name, centre, major, minor, mat, axis="y", arc=360.0, start=0.0, segments=32):
    """A torus (or an arc of one, degrees from start) round an axis through centre."""
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=segments, minor_segments=12)
    obj = bpy.context.object
    obj.name = name
    if arc < 360:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        lo, hi = math.radians(start), math.radians(start + arc)
        for v in list(bm.verts):
            a = math.atan2(v.co.y, v.co.x) % (2 * math.pi)
            a0, a1 = lo % (2 * math.pi), hi % (2 * math.pi)
            inside = (a0 <= a <= a1) if a0 <= a1 else (a >= a0 or a <= a1)
            if not inside:
                bm.verts.remove(v)
        bm.to_mesh(obj.data)
        bm.free()
    if axis == "y":
        obj.rotation_euler = (math.radians(90), 0, 0)
    elif axis == "x":
        obj.rotation_euler = (0, math.radians(90), 0)
    obj.location = centre
    with bpy.context.temp_override(selected_editable_objects=[obj], active_object=obj, object=obj):
        bpy.ops.object.transform_apply(location=True, rotation=True)
    obj.data.materials.append(mat)
    k.smooth(obj, 60)
    return obj


def tracks(m, length=12.0, height=3.2, depth=2.3, z=0.0, y=3.6, wheels=4):
    """A tracked running gear: a track each side with its road wheels showing."""
    for yy in (-y, y):
        half = length / 2
        r = height / 2
        outline = [(-half + r, z), (half - r, z), (half, z + r), (half - r, z + height), (-half + r, z + height), (-half, z + r)]
        side("track", outline, yy - depth / 2, yy + depth / 2, m["track"], bevel=0.35)
        for i in range(wheels):
            wx = -half + r + (length - 2 * r) * i / max(wheels - 1, 1)
            front = yy - depth / 2 - 0.05 if yy < 0 else yy + depth / 2 + 0.05
            cylinder("wheel", (wx, front - 0.4 * (1 if yy > 0 else -1), z + r), (wx, front, z + r), r * 0.62, m["steel"], 16)


def lamp(m, x, z, y=-4.6, r=0.5):
    ball("lamp", (x, y, z), (r, r, r), m["lamp"], 12, 8)


# --- Units -------------------------------------------------------------------------------------

def tank(m):
    tracks(m)
    side("hull", [(-6.2, 2.6), (5.0, 2.6), (6.4, 4.0), (5.4, 5.6), (-5.6, 5.6), (-6.6, 4.2)], -3.0, 3.0, m["body"], 0.3)
    side("skirt", [(-6.0, 2.4), (5.6, 2.4), (6.0, 3.0), (-6.2, 3.0)], -4.9, 4.9, m["dark"], 0.15)
    ball("turret", (-0.6, 0, 6.2), (3.4, 3.0, 2.3), m["body"])
    ball("hatch", (-1.4, 0, 8.2), (1.2, 1.1, 0.5), m["dark"])
    cylinder("mantlet", (0.6, -1.4, 7.0), (0.6, 1.4, 7.0), 1.0, m["trim"], 16)
    lamp(m, 4.6, 4.4)


def tank_barrel(m):
    cylinder("barrel", (0, 0, 0), (8.6, 0, 0), 0.55, m["gun"], 16)
    cylinder("muzzle", (7.4, 0, 0), (8.9, 0, 0), 0.85, m["gun"], 16)
    cylinder("collar", (0.4, 0, 0), (1.6, 0, 0), 0.8, m["steel"], 16)


def launcher_base(m, width=11.0):
    """A low truck: wheels, a deck, a cab at the back."""
    for x in (-3.8, 0.0, 3.8):
        for y in (-3.8, 3.8):
            cylinder("wheel", (x, y - 0.9, 1.4), (x, y + 0.9, 1.4), 1.4, m["track"], 18)
            cylinder("hub", (x, y - 1.0 if y < 0 else y + 0.7, 1.4), (x, y - 0.7 if y < 0 else y + 1.0, 1.4), 0.7, m["steel"], 12)
    side("deck", [(-width / 2, 2.2), (width / 2, 2.2), (width / 2 + 0.4, 3.0), (width / 2, 3.8), (-width / 2, 3.8)], -3.4, 3.4,
         m["body"], 0.25)
    side("cab", [(-5.8, 3.6), (-2.6, 3.6), (-2.6, 6.4), (-3.6, 7.2), (-5.8, 7.2)], -2.8, 2.8, m["body"], 0.3)
    side("window", [(-3.5, 5.3), (-2.75, 5.3), (-2.75, 6.3), (-3.4, 6.9)], -2.9, 2.9, m["glass"], 0.05)
    lamp(m, 5.4, 3.2)


def nuke(m):
    launcher_base(m)
    side("bracket", [(-1.6, 3.6), (0.8, 3.6), (0.2, 5.6), (-1.0, 5.6)], -1.2, 1.2, m["dark"], 0.15)


def nuke_rail(m):
    block("rail", (4.6, 0, -0.2), (10.4, 1.6, 0.6), m["gun"], 0.12)
    cylinder("missile", (1.0, 0, 1.2), (8.6, 0, 1.2), 1.15, m["red"], 20)
    cone("warhead", (8.6, 0, 1.2), (11.2, 0, 1.2), 1.15, 0.0, m["white"])
    cylinder("band", (5.6, 0, 1.2), (6.2, 0, 1.2), 1.22, m["white"], 20)
    for a in (45, 135, 225, 315):
        fin = side("fin", [(0.6, 0), (2.6, 0), (2.4, 1.0), (0.6, 1.9)], -0.12, 0.12, m["white"], 0.0)
        fin.rotation_euler = (math.radians(a), 0, 0)
        fin.location = (0, 0, 1.2)


def dirt_launcher(m):
    launcher_base(m)
    ball("hopper", (2.6, 0, 4.6), (2.2, 2.4, 1.3), m["dark"])
    ball("dirt", (2.6, 0, 5.4), (1.9, 2.0, 0.9), m["dirt"])
    side("mount", [(-2.2, 3.6), (0.6, 3.6), (0.6, 4.8), (-1.6, 6.0), (-2.2, 6.0)], -1.8, 1.8, m["dark"], 0.2)


def dirt_tube(m):
    cylinder("tube", (-0.6, 0, 0), (6.4, 0, 0), 1.75, m["body"], 24)
    cylinder("rim", (5.6, 0, 0), (6.9, 0, 0), 2.1, m["trim"], 24)
    cylinder("bore", (6.8, 0, 0), (6.95, 0, 0), 1.3, m["track"], 24)
    cylinder("trunnion", (0.4, -2.3, 0), (0.4, 2.3, 0), 0.7, m["steel"], 12)


def pedestal(m, height=3.0, width=10.0):
    side("plinth", [(-width / 2, 0), (width / 2, 0), (width / 2 - 1.0, height), (-width / 2 + 1.0, height)], -3.6, 3.6, m["dark"], 0.3)
    side("plate", [(-width / 2 + 1.2, height), (width / 2 - 1.2, height), (width / 2 - 1.6, height + 0.6),
                   (-width / 2 + 1.6, height + 0.6)], -3.0, 3.0, m["trim"], 0.1)


def magnet(m):
    """A horseshoe magnet on a post, its poles towards the other side."""
    pedestal(m)
    cylinder("post", (-1.6, 0, 3.4), (-1.6, 0, 7.6), 1.1, m["steel"], 16)
    torus("horseshoe", (0.2, 0, 10.0), 2.9, 1.15, m["red"], axis="y", arc=180, start=90)
    for z in (7.1, 12.9):
        cylinder("arm", (0.2, 0, z), (2.6, 0, z), 1.15, m["red"], 16)
        cylinder("pole", (2.6, 0, z), (4.4, 0, z), 1.2, m["steel"], 16)
    lamp(m, -3.4, 2.0)


def laser(m):
    pedestal(m)
    cylinder("column", (0, 0, 3.4), (0, 0, 8.4), 1.4, m["body"], 18)
    torus("collar", (0, 0, 8.4), 1.4, 0.4, m["trim"], axis="z")
    lamp(m, -3.2, 2.0)


def laser_head(m):
    ball("housing", (0, 0, 0), (1.9, 1.7, 1.7), m["dark"])
    cylinder("lens", (0.5, 0, 0), (4.6, 0, 0), 0.9, m["steel"], 16)
    for i in range(3):
        a = math.radians(i * 120)
        cylinder("prong", (3.6, math.cos(a) * 0.9, math.sin(a) * 0.9), (6.0, math.cos(a) * 1.3, math.sin(a) * 1.3), 0.22, m["trim"], 8)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=1, location=(5.6, 0, 0))
    gem = bpy.context.object
    gem.scale = (1.3, 0.75, 0.75)
    gem.data.materials.append(m["crystal"])


def satellite(m):
    ball("body", (0, 0, 7.0), (3.0, 3.0, 2.8), m["body"], 24, 16)
    torus("ring", (0, 0, 7.0), 3.1, 0.35, m["trim"], axis="z")
    for sx in (-1, 1):
        cylinder("arm", (sx * 2.6, 0, 7.0), (sx * 4.2, 0, 7.0), 0.3, m["steel"], 8)
        block("panel", (sx * 7.4, 0, 7.0), (6.2, 0.35, 3.6), m["panel"], 0.08)
        for i in range(1, 4):
            block("strut", (sx * (4.3 + i * 1.55), -0.25, 7.0), (0.12, 0.2, 3.6), m["steel"], 0.0)
    cylinder("antenna", (0, 0, 9.6), (0, 0, 12.6), 0.18, m["steel"], 8)
    lamp(m, 0, 12.8, y=0, r=0.45)
    ball("dish", (0, 0, 4.0), (1.8, 1.8, 0.6), m["steel"])


def jumper(m):
    for x in (-3.4, 3.4):
        for y in (-2.4, 2.4):
            cylinder("foot", (x - 1.0, y, 0.3), (x + 1.0, y, 0.3), 0.5, m["track"], 12)
            for i in range(4):
                torus("coil", (x, y, 1.0 + i * 0.8), 0.8, 0.22, m["steel"], axis="z", segments=20)
    side("frame", [(-5.4, 4.0), (5.4, 4.0), (5.0, 5.0), (-5.0, 5.0)], -3.2, 3.2, m["dark"], 0.2)
    ball("dome", (0, 0, 6.8), (5.0, 3.8, 3.4), m["body"], 24, 16)
    ball("visor", (2.8, -1.4, 7.6), (1.6, 1.6, 1.0), m["glass"])
    lamp(m, -2.6, 9.4, y=-2.6)


def heli(m):
    ball("body", (0.6, 0, 6.0), (4.2, 2.6, 2.7), m["body"], 24, 16)
    ball("canopy", (2.9, 0, 6.9), (2.0, 2.0, 1.6), m["glass"], 20, 12)
    cylinder("boom", (-3.0, 0, 6.6), (-10.5, 0, 7.4), 0.75, m["body"], 14)
    side("fin", [(-11.6, 6.6), (-9.6, 6.6), (-10.2, 10.0), (-11.6, 10.4)], -0.2, 0.2, m["dark"], 0.05)
    cylinder("tail rotor", (-10.8, -1.0, 8.6), (-10.8, -0.4, 8.6), 1.3, m["gun"], 16)
    for y in (-2.2, 2.2):
        cylinder("skid", (-3.2, y, 1.2), (4.2, y, 1.2), 0.4, m["steel"], 10)
        for x in (-1.6, 2.6):
            cylinder("strut", (x, y, 1.2), (x * 0.8, y * 0.6, 3.8), 0.25, m["steel"], 8)
    cylinder("mast", (0.4, 0, 8.4), (0.4, 0, 9.8), 0.45, m["gun"], 12)
    lamp(m, -11.0, 10.6, y=0, r=0.4)


def heli_rotor(m):
    cylinder("hub", (0, 0, -0.3), (0, 0, 0.3), 0.7, m["gun"], 12)
    for a in (0, 180):
        r = math.radians(a)
        block("blade", (math.cos(r) * 5.5, math.sin(r) * 5.5, 0), (10.2 if a == 0 else 10.2, 0.9, 0.15), m["gun"], 0.05).rotation_euler = (0, 0, r)


def wall(m):
    """A block of stone the size of the game's wall sprite (12 x 14), two courses, mortar between."""
    stone = k.material("stone", (92, 118, 152), metallic=0.05, roughness=0.7)
    mortar = k.material("mortar", (40, 48, 64), roughness=0.95)
    block("core", (0, 0, 7.0), (11.6, 11.0, 13.8), mortar, 0.0)
    for course, z0 in enumerate((0.15, 7.05)):
        if course == 0:
            spans = [(-5.7, 5.7)]
        else:
            spans = [(-5.7, -0.15), (0.15, 5.7)]
        for x0, x1 in spans:
            block("stone", ((x0 + x1) / 2, 0, z0 + 3.35), (x1 - x0, 11.2, 6.7), stone, 0.6)


# The models: (name, builder, by side).
MODELS = [
    ("tank", tank, True), ("tank_barrel", tank_barrel, False),
    ("nuke", nuke, True), ("nuke_rail", nuke_rail, False),
    ("dirt", dirt_launcher, True), ("dirt_tube", dirt_tube, True),
    ("magnet", magnet, True), ("laser", laser, True), ("laser_head", laser_head, False),
    ("satellite", satellite, True), ("jumper", jumper, True),
    ("heli", heli, True), ("heli_rotor", heli_rotor, False),
    ("wall", wall, False),
]


def preview(path, size=24.0):
    """The model as the game sees it: from the front, a little from above, lit from the top left."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    world = bpy.data.worlds.new("preview")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.32, 0.4, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.5
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(50), math.radians(-35), math.radians(-25))
    scene.collection.objects.link(so)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = size
    co = bpy.data.objects.new("cam", cam)
    co.location = (0, -60, 6 + 60 * math.tan(math.radians(13)))
    co.rotation_euler = (math.radians(90 - 13), 0, 0)
    scene.collection.objects.link(co)
    scene.camera = co
    scene.render.resolution_x = scene.render.resolution_y = 320
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    options = k.args()
    only = options.get("only")
    for name, build, by_side in MODELS:
        for team in (("l", "r") if by_side else ("l",)):
            out_name = f"{name}_{team}" if by_side else name
            if only and only not in (name, out_name):
                continue
            k.reset()
            build(mats(team))
            k.export(os.path.join(OUT, out_name + ".glb"))
            if "preview" in options:
                preview(os.path.join(options["preview"], out_name + ".png"))


main()
