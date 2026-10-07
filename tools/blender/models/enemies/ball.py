"""Balls (the mines and spheres of the asteroid levels: sheet A sprites 165 and 283, sheet M sprite
115, and the like): a glossy sphere 18 pixels across. Two shades, light (ball.glb) and dark
(ball_dark.glb); models.cfg colours them with the sprite's colour (color=sprite), so they are grey.

The sphere's centre is the sprite's pixel (12, 13.5).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def build(name, shade):
    k.reset()
    shell = k.material(name, palette=shade, metallic=0.3, roughness=0.25)
    k.smooth(k.ellipsoid("ball", (0.0, 0.5, 0.0), (8.8, 8.8, 8.8), shell, 32, 18), 80)
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


build("ball", 8)
build("ball_dark", 4)
