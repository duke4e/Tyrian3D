"""Coin (the coins sheet's sprites 1-31: green, gold, silver and copper coins of 10 to 75 credits):
a disc with a raised rim and a boss in the middle. The sprites flip the coin about the screen's
vertical axis, half a turn in six frames; models.cfg rolls the model with them and colours it
with the frame's colour (color=sprite), so the model is grey (ramp 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
from mathutils import Matrix  # noqa: E402


def build():
    k.reset()
    metal = k.material("coin", palette=8, metallic=0.45, roughness=0.3)

    # The profile from the middle of the bottom face to the middle of the top one: (along the
    # coin's axis, radius). Faces 0.55 from the middle plane, the rim and the boss stand out.
    half = [(0.55, 5.3), (0.85, 4.95), (0.85, 4.3), (0.55, 3.9), (0.55, 2.0), (0.75, 1.7), (0.75, 0.0)]
    profile = [(-t, r) for t, r in reversed(half)] + half
    coin = k.lathe("coin", profile, metal, segments=36)
    # Turned so that its axis is Z (the face looks up at the camera).
    coin.data.transform(Matrix.Rotation(math.radians(90), 4, "X"))
    k.smooth(coin, 50)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "coin.glb"))


build()
