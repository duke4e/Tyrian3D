"""U-arch (episode 1 enemies 10 and 12; sheet 2, sprites 191-205): an arch like an upside-down U on
two thin legs, with a small cockpit pod hung in the middle. The sprite's animation rolls it about
the screen's vertical axis, half a turn in its 8 frames (models.cfg rolls the model with them).
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - (row + 0.5)


def tube(name, path, radius, mat, segments=10):
    """A tube along a path in the XY plane (radius per point or one radius)."""
    rings = []
    for i, p in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, len(path) - 1)]
        tangent = (b - a).normalized()
        side = Vector((-tangent.y, tangent.x, 0))
        r = radius[i] if isinstance(radius, list) else radius
        rings.append([p + side * (r * math.cos(2 * math.pi * j / segments)) + Vector((0, 0, r * math.sin(2 * math.pi * j / segments)))
                      for j in range(segments)])
    obj = k.loft(name, rings, mat)
    k.smooth(obj, 60)
    return obj


def build():
    k.reset()
    arch = k.material("uarch_arch", palette=25, metallic=0.4, roughness=0.3)
    legs = k.material("uarch_legs", palette=9, metallic=0.5, roughness=0.3)
    pod = k.material("uarch_pod", palette=24, metallic=0.3, roughness=0.3)
    glass = k.material("uarch_glass", palette=163, roughness=0.15)

    # The arch: from the left leg's top over the top to the right one (centre at row 7.5).
    cy, r = row_y(7.5), 6.3
    path = [Vector((r * math.cos(a), cy + r * math.sin(a), 1.0)) for a in [math.pi - math.pi * i / 24 for i in range(25)]]
    radius = [1.0 + 0.5 * math.sin(math.pi * i / 24) for i in range(25)]  # thicker over the top
    tube("arch", path, radius, arch)
    # The legs, straight down to row 19.
    for x in (-r, r):
        tube("leg", [Vector((x, cy - d, 1.0)) for d in (0.0, 4.0, 8.0, 11.4)], 1.0, legs)
    # The cockpit pod and the strut that holds it.
    k.smooth(k.ellipsoid("pod", (0, row_y(10), 1.2), (3.2, 4.0, 2.4), pod, 16, 10), 60)
    k.smooth(k.ellipsoid("canopy", (0, row_y(8.6), 2.6), (1.6, 1.9, 1.0), glass, 12, 8), 60)
    tube("strut", [Vector((x, row_y(10.3), 1.0)) for x in (-r, -2.5, 2.5, r)], 0.55, legs)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "uarch.glb"))


build()
