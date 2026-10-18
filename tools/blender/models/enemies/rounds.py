"""Round episode 1 enemies, facing the way their sprites do (models.cfg: yaw=0):

- spike_mine (sheet A 169): a grey ball with spikes.
- band_sphere (sheet E 13): a blue sphere with a glowing orange band (HOLES).
- bubbles (sheet E 153): a cluster of red bubbles (BUBBLES).
- disc_turret (sheet F 39): a bronze disc with a red eye on the ground.
- missile (sheet D 77): a grey missile with red fins, nose up the screen.

(dome_green and dome_red, sheet A 17 and A 93, are built by polish_domes.py.)
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def pos(col, row, z=0.0):
    """A sprite pixel's centre as model coordinates (2x2 sprite: 24 x 28)."""
    return (col + 0.5 - 12, 14 - (row + 0.5), z)


def torus(name, centre, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=48, minor_segments=12,
                                     location=centre)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return k.smooth(obj, 60)


def cone(name, base, tip, radius, mat):
    """A cone from a base centre to a tip."""
    base, tip = Vector(base), Vector(tip)
    axis = tip - base
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=radius, radius2=0.0, depth=axis.length,
                                    location=(base + tip) / 2)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    return obj


def ccw(outline):
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    return outline if area > 0 else outline[::-1]


def export(name):
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


def spike_mine():
    k.reset()
    steel = k.material("mine_steel", palette=8, metallic=0.7, roughness=0.35)
    tips = k.material("mine_tips", palette=11, metallic=0.7, roughness=0.3)
    c = Vector(pos(11, 13, 0.0))
    k.smooth(k.ellipsoid("ball", tuple(c), (6.4, 6.4, 6.4), steel, 24, 14), 70)
    # Spikes all round (a Fibonacci sphere), a little more of them seen from above.
    count = 14
    for i in range(count):
        z = 1 - 2 * (i + 0.5) / count
        r = math.sqrt(1 - z * z)
        a = i * math.pi * (3 - math.sqrt(5))
        d = Vector((r * math.cos(a), r * math.sin(a), z))
        cone(f"spike{i}", c + d * 5.6, c + d * 10.2, 1.4, tips)
    export("spike_mine")


def band_sphere():
    k.reset()
    shell = k.material("sphere_shell", palette=57, metallic=0.2, roughness=0.15)
    band = k.material("sphere_band", palette=123, roughness=0.3, emission=(255, 140, 20), emission_strength=1.2)
    c = pos(11.5, 13)
    k.smooth(k.ellipsoid("sphere", c, (8.6, 8.6, 8.6), shell, 32, 18), 70)
    # The band round its middle, as the sprite shows it: across the screen.
    band_obj = torus("band", c, 8.5, 0.9, band)
    band_obj.rotation_euler = (math.radians(90), 0, 0)
    export("band_sphere")


def bubbles():
    k.reset()
    skin = k.material("bubbles_skin", palette=70, metallic=0.1, roughness=0.25)
    for i, (col, row, r) in enumerate([(5.5, 7, 6.0), (18.5, 5, 4.8), (12.5, 11.5, 5.2), (20.5, 12, 3.6),
                                       (5.5, 18.5, 5.6), (13, 21, 4.6), (9.5, 14.5, 3.4)]):
        k.smooth(k.ellipsoid(f"bubble{i}", pos(col, row, r * 0.55), (r, r, r * 0.85), skin, 24, 12), 70)
    export("bubbles")


def disc_turret():
    k.reset()
    bronze = k.material("disc_bronze", palette=24, metallic=0.6, roughness=0.35)
    dark = k.material("disc_dark", palette=19, metallic=0.5, roughness=0.5)
    eye = k.material("disc_eye", palette=120, roughness=0.2, emission=(255, 60, 10), emission_strength=1.5)
    c = pos(8.5, 9.5)
    k.smooth(k.ellipsoid("disc", (c[0], c[1], 0.8), (7.4, 7.4, 2.6), dark, 32, 10), 60)
    k.smooth(k.ellipsoid("dome", (c[0], c[1], 1.8), (6.0, 6.0, 4.4), bronze, 32, 14), 70)
    k.smooth(k.ellipsoid("eye", (c[0] + 0.6, c[1] - 0.4, 5.6), (1.7, 1.7, 1.0), eye, 16, 8), 60)
    # The pipe to the right and down, as the sprite shows it.
    pipe = k.lathe("pipe", [(0, 1.1), (7, 1.1)], bronze, segments=12)
    pipe.rotation_euler = (0, 0, math.radians(-120))
    pipe.location = (c[0] + 4.5, c[1] - 1.0, 1.4)
    k.smooth(pipe, 60)
    export("disc_turret")


def missile():
    k.reset()
    steel = k.material("missile_steel", palette=8, metallic=0.6, roughness=0.3)
    red = k.material("missile_red", palette=71, metallic=0.3, roughness=0.4)
    x = 0.5
    # Nose (top of the sprite) to tail: y decreasing; the lathe takes increasing y.
    profile = [(-13.0, 0.4), (-11.0, 1.6), (-8.0, 3.2), (-6.0, 4.4), (-4.0, 5.8), (1.0, 6.0), (2.5, 5.2),
               (4.0, 6.0), (6.5, 6.4), (8.5, 5.8), (9.8, 4.2), (10.6, 1.8), (11.0, 0.3)]
    body = k.lathe("body", profile[4:], steel, segments=24, axis_x=x, axis_z=6.0)
    k.smooth(body, 50)
    tail = k.lathe("tail", profile[:5], red, segments=24, axis_x=x, axis_z=6.0)
    k.smooth(tail, 50)
    for side in (-1, 1):
        k.slab(f"fin{side}", ccw([(x, -3.0), (x + side * 6.0, -10.5), (x + side * 6.0, -12.5), (x, -9.0)]),
               5.5, 6.5, red)
    export("missile")


spike_mine()
band_sphere()
bubbles()
disc_turret()
missile()
