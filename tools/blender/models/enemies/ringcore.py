"""Ring core (episode 1 enemies 5 and 11; sheet 2, sprites 229-243): a small armoured core with two
red eyes inside two arcs that turn around it (the sprite's animation turns them a 16th of a full
turn per frame; models.cfg turns the model with the frames).

The ring's centre is the sprite's pixel (12, 12), two above the sprite's centre.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - (row + 0.5)


def build():
    k.reset()
    arc_mat = k.material("ringcore_arc", palette=11, metallic=0.5, roughness=0.22)
    core_mat = k.material("ringcore_core", palette=8, metallic=0.4, roughness=0.3)
    eye_mat = k.material("ringcore_eye", (186, 12, 0), roughness=0.3, emission=(255, 40, 10), emission_strength=4.0)

    cy = row_y(12)
    # Two arcs of a torus (major radius 8.5, tube 1.4), left and right, with gaps at the top and
    # bottom, as in the sprite's first frame.
    major, minor, gap = 8.4, 1.75, math.radians(24)
    for side in (0, 1):
        start, end = (math.pi / 2 + gap, 3 * math.pi / 2 - gap) if side == 0 else (-math.pi / 2 + gap, math.pi / 2 - gap)
        steps = 24
        rings = []
        for i in range(steps + 1):
            a = start + (end - start) * i / steps
            cx, cyy = major * math.cos(a), cy + major * math.sin(a)
            # A cross-section of the tube: a circle in the plane through the ring's axis (z) and
            # the radius at this angle.
            pts = []
            for j in range(10):
                b = 2 * math.pi * j / 10
                r = minor * math.cos(b)
                pts.append(k.Vector((cx + r * math.cos(a), cyy + r * math.sin(a), minor * math.sin(b) + 0.4)))
            rings.append(pts)
        arc = k.loft(f"arc{side}", rings, arc_mat)
        k.smooth(arc, 60)

    # The core: a rounded shield, nose down (the eyes look down the screen).
    core = k.ellipsoid("core", (0, cy, 1.0), (4.3, 4.4, 2.3), core_mat, 18, 12)
    k.smooth(core, 60)
    for x in (-1.3, 1.3):
        k.smooth(k.ellipsoid("eye", (x * 1.2, cy - 1.0, 2.8), (0.9, 0.7, 0.5), eye_mat, 10, 6), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "ringcore.glb"))


build()
