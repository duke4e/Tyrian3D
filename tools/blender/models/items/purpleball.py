"""Purple ball (the power-ups sheet's sprite 41; enemy type 628 and others with value 30000): the
glossy ball enemies leave most often, a power-up for the weapons (experience in a rogue run), in
Tyrian purple.

The ball's centre is the sprite's pixel (12.5, 13.5) of 24x28, half a pixel right of and up from
the sprite's centre.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def build():
    k.reset()
    # Tyrian purple (#66023c), glowing a little so the dark colour reads over dark ground.
    shell = k.material("ball", color=(0x66, 0x02, 0x3c), roughness=0.22, emission=(0x66, 0x02, 0x3c),
                       emission_strength=0.15)
    k.smooth(k.ellipsoid("ball", (0.5, 0.5, 0.0), (10.2, 10.2, 10.2), shell, 40, 22), 80)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "purpleball.glb"))


build()
