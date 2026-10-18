"""Round episode 1 enemies, facing the way their sprites do (models.cfg: yaw=0):

- spike_mine (sheet A 169): a grey ball with spikes.

(dome_green and dome_red, sheet A 17 and A 93, are built by polish_domes.py; band_sphere, bubbles,
missile and disc_turret by polish_<name>.py.)
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


spike_mine()
