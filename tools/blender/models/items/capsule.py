"""Power-up capsule (the coins sheet's sprites 165 and 203: the front and rear weapon power-ups,
values -1 and -2): a grey capsule with a dark band and red lights, which the sprites blink.
models.cfg turns it slowly.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def build():
    k.reset()
    shell = k.material("capsule_shell", palette=8, metallic=0.5, roughness=0.28)
    band = k.material("capsule_band", palette=3, metallic=0.4, roughness=0.35)
    light = k.material("capsule_light", (186, 12, 0), roughness=0.3, emission=(255, 40, 10), emission_strength=3.0)

    k.smooth(k.ellipsoid("shell", (0, 0, 0), (11.0, 7.6, 5.6), shell, 32, 16), 70)
    # The band round the middle, a little proud of the shell.
    k.smooth(k.ellipsoid("band", (0, 0, 0), (11.3, 2.4, 5.9), band, 32, 8), 70)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        x, z = 9.4 * math.cos(a), 4.6 * math.sin(a)
        if z > 0:
            k.smooth(k.ellipsoid("light", (x, 0, z + 0.6), (1.1, 1.6, 1.0), light, 10, 6), 60)
    for x in (-4.0, 4.0):
        k.smooth(k.ellipsoid("light", (x, 0, 6.0), (1.0, 1.4, 0.8), light, 10, 6), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "capsule.glb"))


build()
