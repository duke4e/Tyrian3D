"""Round episode 1 enemies, facing the way their sprites do (models.cfg: yaw=0):

- spike_mine (sheet A 169): a grey ball with spikes.
- disc_turret (sheet F 39): a bronze disc with a red eye on the ground.

(dome_green and dome_red, sheet A 17 and A 93, are built by polish_domes.py; band_sphere, bubbles and
missile by polish_<name>.py.)
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


spike_mine()
disc_turret()
