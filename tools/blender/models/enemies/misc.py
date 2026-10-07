"""More episode 1 enemies, facing the way their sprites do (models.cfg: yaw=0):

- diamond (sheet 2 sprite 171, 1x1): a small bronze gem pointing down, which turns.
- container (sheet 2 sprite 89): a purple ribbed container.
- claws (sheet F 169): SAVARA's twin red claws standing on the ground.
- ornament (sheet D 79): a golden winged medallion with a blue gem and a loop.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
import silhouette as s  # noqa: E402

ORNAMENT = """
........................
........................
........................
...00.....0000.....00...
..01100..047530..00110..
.0253210038545300123220.
012353212251152212342210
023325432350263234522210
023323753335753345223220
023222385221123463222310
024324349531135742322310
025453434852258433232310
025333335683384323223310
026334355674563332322410
023653568458852532234210
012376895693385353342110
012237845832238545421110
011213558326313865211110
.0357972531111372776530.
..03568246311383253350..
..02345244633653244720..
...022424335643425610...
....0231433333371210....
.....00023333473000.....
........01235510........
.........000000.........
........................
........................
"""


def export(name):
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


def diamond():
    """A 1x1 sprite (12 x 14): the gem's wide top at the sprite's row 2, its point at row 13."""
    k.reset()
    bronze = k.material("diamond_bronze", palette=22, metallic=0.75, roughness=0.25)
    sides = 8
    top_y, girdle_y, tip_y = 4.5, 3.0, -6.5   # the table, the widest ring, the point (y)
    verts = [(0.0, top_y, 2.2)]
    for i in range(sides):  # the table's ring
        a = 2 * math.pi * i / sides
        verts.append((2.6 * math.cos(a), top_y - 0.3 + 1.0 * math.sin(a) * 0.3, 2.2 + 1.6 * math.sin(a)))
    for i in range(sides):  # the girdle
        a = 2 * math.pi * (i + 0.5) / sides
        verts.append((5.0 * math.cos(a), girdle_y, 2.2 + 3.0 * math.sin(a)))
    verts.append((0.0, tip_y, 2.2))
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((0, 1 + i, 1 + j))                              # the table
        faces.append((1 + i, 1 + sides + i, 1 + j))                  # crown, down
        faces.append((1 + j, 1 + sides + i, 1 + sides + j))           # crown, up
        faces.append((1 + sides + i, 1 + 2 * sides, 1 + sides + j))  # the pavilion to the point
    obj = k.mesh_object("diamond", verts, faces, bronze)
    k.recalc_normals(obj)
    export("diamond")


def container():
    k.reset()
    shell = k.material("container_shell", palette=85, metallic=0.35, roughness=0.35)
    ribs = k.material("container_ribs", palette=88, metallic=0.45, roughness=0.3)
    body = k.pillow("body", 11.0, 12.0, 8.0, shell, rounding=3.0, dome=0.8)
    body.location = (0.0, 0.5, 0.0)
    # Ribs across the top, as the sprite's bright lines.
    for x in (-6.5, -2.0, 2.5, 7.0):
        rib = k.box("rib", (x, 0.5, 8.6), (1.4, 17.0, 1.2), ribs)
        k.bevel(rib, 0.4, 2)
    export("container")


def claws():
    k.reset()
    shell = k.material("claws_shell", palette=71, metallic=0.3, roughness=0.35)
    dark = k.material("claws_dark", palette=67, metallic=0.3, roughness=0.45)
    for side, x in (("left", -6.0), ("right", 6.0)):
        # The body from the bottom (row 26) to the top (row 4): wide shoulders, a thin waist.
        profile = [(-12.5, 1.0), (-11.0, 3.4), (-9.5, 4.0), (-8.0, 2.4), (-5.0, 2.0), (0.0, 2.2), (1.0, 3.6),
                   (3.5, 4.6), (5.5, 4.4), (7.0, 3.0), (8.5, 1.6), (9.5, 0.6)]
        body = k.lathe("body_" + side, profile, shell, segments=20, axis_x=x, axis_z=3.5, squash=0.8)
        k.smooth(body, 60)
        # The prongs at the top.
        for dx in (-2.4, 2.4):
            prong = k.lathe("prong", [(8.0, 0.8), (10.5, 0.5), (12.0, 0.1)], dark, segments=8,
                            axis_x=x + dx, axis_z=4.5)
            k.smooth(prong, 60)
    export("claws")


def ornament():
    k.reset()
    gold = k.material("ornament_gold", palette=25, metallic=0.85, roughness=0.25)
    gem = k.material("ornament_gem", palette=153, metallic=0.2, roughness=0.1, emission=(40, 110, 255),
                     emission_strength=0.8)
    rows = [line for line in ORNAMENT.strip("\n").split("\n")]
    plate = s.plate("plate", rows, 0.0, 3.0, gold, bevel=1.0)
    k.smooth(plate, 35)
    k.smooth(k.ellipsoid("boss", (0.0, -1.0, 2.8), (5.2, 6.0, 1.8), gold, 24, 10), 60)
    k.smooth(k.ellipsoid("gem", (0.0, -1.5, 4.2), (2.4, 2.6, 1.6), gem, 20, 10), 60)
    # The loop at the top.
    bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.6, major_segments=24, minor_segments=8,
                                     location=(0.0, 9.0, 1.6), rotation=(math.radians(90), 0, 0))
    loop = bpy.context.active_object
    loop.data.materials.append(gold)
    k.smooth(loop, 60)
    export("ornament")


diamond()
container()
claws()
ornament()
