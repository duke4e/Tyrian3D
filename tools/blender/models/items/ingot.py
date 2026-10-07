"""Armour ingot (the coins sheet's sprites 127, 129 and 131: grey, brown and blue; the ship that
comes when the player's armour runs low leaves them): a metal bar with sloping sides. models.cfg
turns it slowly and colours it with the sprite's colour (color=sprite), so the model is grey.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
from mathutils import Matrix  # noqa: E402


def build():
    k.reset()
    metal = k.material("ingot", palette=9, metallic=0.5, roughness=0.3)

    bottom = [(-7.0, -3.6, -2.2), (7.0, -3.6, -2.2), (7.0, 3.6, -2.2), (-7.0, 3.6, -2.2)]
    top = [(-5.2, -2.2, 2.2), (5.2, -2.2, 2.2), (5.2, 2.2, 2.2), (-5.2, 2.2, 2.2)]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7)] + [(i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i) for i in range(4)]
    bar = k.mesh_object("ingot", bottom + top, faces, metal)
    k.recalc_normals(bar)
    k.bevel(bar, 0.45, 2)
    k.smooth(bar, 35)
    # Tipped over a little, as in the sprite, so the turning bar shows its sides.
    bar.data.transform(Matrix.Rotation(math.radians(28), 4, "X") @ Matrix.Rotation(math.radians(12), 4, "Y"))

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "ingot.glb"))


build()
