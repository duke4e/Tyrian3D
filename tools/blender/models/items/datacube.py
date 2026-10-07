"""Data cube (the coins sheet's sprites 159 and 191, value 1: the cubes that carry the game's
messages): a glass cube in a bright frame with a core, standing on a corner. models.cfg spins it
about the vertical axis and colours it with the frame's colour (color=sprite: the sprites'
animation cycles through several colours), so the model is grey.

A cube of edge 12 on its corner is about as wide as the sprite's cube (20 pixels).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
from mathutils import Vector  # noqa: E402


def build():
    k.reset()
    frame_mat = k.material("cube_frame", palette=12, roughness=0.3, metallic=0.3)
    glass_mat = k.material("cube_glass", palette=9, roughness=0.08, alpha=0.4)
    core_mat = k.material("cube_core", palette=15, roughness=0.2)

    edge, bar = 12.0, 1.3
    h = edge / 2
    parts = []
    # The frame: a bar along each of the twelve edges.
    for axis in range(3):
        for a in (-1, 1):
            for b in (-1, 1):
                centre = [0.0, 0.0, 0.0]
                size = [bar, bar, bar]
                centre[(axis + 1) % 3] = a * (h - bar / 2)
                centre[(axis + 2) % 3] = b * (h - bar / 2)
                size[axis] = edge
                parts.append(k.box("bar", centre, size, frame_mat))
    parts.append(k.box("glass", (0, 0, 0), (edge - 0.4, edge - 0.4, edge - 0.4), glass_mat))
    core = k.ellipsoid("core", (0, 0, 0), (2.2, 2.2, 2.2), core_mat, 16, 10)
    k.smooth(core, 80)

    # On a corner: the cube's diagonal (1, 1, 1) turned up.
    turn = Vector((1, 1, 1)).rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
    for obj in parts:
        obj.data.transform(turn)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "datacube.glb"))


build()
