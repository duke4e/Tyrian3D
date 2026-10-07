"""Marker (episode 2 enemy 810, sheet V sprite 8; hundreds of them line the level MARKERS): a grey
block on two feet with a tower in the middle and a red lamp on each side.

Coordinates are pixel boundaries of the 24x28 sprite: x = column - 12, y = 14 - row.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def build():
    k.reset()
    base_mat = k.material("marker_base", palette=103, metallic=0.4, roughness=0.35)
    tower_mat = k.material("marker_tower", palette=107, metallic=0.4, roughness=0.3)
    lamp_mat = k.material("marker_lamp", palette=118, roughness=0.3)
    glow_mat = k.material("marker_glow", (235, 138, 24), roughness=0.3, emission=(255, 90, 20), emission_strength=2.5)

    # The block, rows 13.5-20.5, on two feet with a gap between them.
    outline = [(-11.0, 0.5), (-11.0, -6.5), (-4.0, -6.5), (-4.0, -4.0), (4.0, -4.0), (4.0, -6.5),
               (11.0, -6.5), (11.0, 0.5)]
    k.slab("base", outline, 0.0, 3.0, base_mat, bevel_width=0.5)
    # The tower, columns 8-15, rows 5-13.
    k.slab("tower", [(-4.0, 9.0), (-4.0, 0.0), (4.0, 0.0), (4.0, 9.0)], 0.0, 6.0, tower_mat, bevel_width=0.6)
    # The lamps either side, columns 2-7 and 16-21, rows 8-13.
    for x in (-7.0, 7.0):
        k.smooth(k.ellipsoid("lamp", (x, 3.2, 2.6), (3.0, 3.0, 2.2), lamp_mat, 16, 10), 60)
        k.smooth(k.ellipsoid("glow", (x, 3.4, 4.3), (1.4, 1.4, 0.9), glow_mat, 12, 8), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "marker.glb"))


build()
