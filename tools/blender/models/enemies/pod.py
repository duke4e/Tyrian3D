"""Pod (episode 1 enemy 4; sheet 2, sprites 159-167): a round bronze pod with a dark core, a grey bar
across its top half and red lights at the bar's ends (which the sprite's animation lights up).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - (row + 0.5)


def build():
    k.reset()
    shell = k.material("pod_shell", palette=21, metallic=0.35, roughness=0.3)
    core = k.material("pod_core", palette=3, metallic=0.4, roughness=0.25)
    bar = k.material("pod_bar", palette=6, metallic=0.5, roughness=0.3)
    light = k.material("pod_light", (134, 4, 0), roughness=0.3, emission=(255, 30, 10), emission_strength=0.8)

    cy = row_y(14)
    k.smooth(k.ellipsoid("shell", (0, cy, 0.6), (7.8, 7.9, 3.6), shell, 24, 14), 60)
    # The dark core, sunk into the shell's top.
    k.smooth(k.ellipsoid("core", (0, cy - 0.6, 2.3), (4.6, 4.8, 2.2), core, 18, 10), 60)
    # The bar across, a little up the screen from the middle.
    by = row_y(12)
    k.smooth(k.ellipsoid("bar", (0, by, 3.2), (9.0, 1.9, 1.5), bar, 20, 8), 50)
    for x in (-8.3, 8.3):
        k.smooth(k.ellipsoid("light", (x, by, 3.3), (0.9, 1.3, 0.9), light, 10, 6), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "pod.glb"))


build()
