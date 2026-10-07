"""Crystal (the coins sheet's sprites 39, 77 and 115: orange, green and purple crystals of 1000,
2500 and 5000 credits): a six-sided prism with pointed ends, lying along the screen's vertical
axis. The sprites turn it about that axis, a sixth of a turn per animation; models.cfg rolls the
model with them and colours it with the frame's colour (color=sprite), so the model is grey.

The crystal spans the sprite's rows 2-24 (straight sides on rows 8-18) and columns 5-18.
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
    side_mat = k.material("crystal_side", palette=8, roughness=0.12, metallic=0.1)
    tip_mat = k.material("crystal_tip", palette=10, roughness=0.1, metallic=0.1)

    radius = 7.0
    body_top, body_bottom = row_y(8) + 0.5, row_y(18) - 0.5
    tip_top, tip_bottom = row_y(2) + 0.5, row_y(24) - 0.5

    def hexagon(y):
        return [(radius * math.cos(math.radians(90 + 60 * i)), y, radius * math.sin(math.radians(90 + 60 * i)))
                for i in range(6)]

    top, bottom = hexagon(body_top), hexagon(body_bottom)
    sides = [(i, (i + 1) % 6, 6 + (i + 1) % 6, 6 + i) for i in range(6)]
    k.recalc_normals(k.mesh_object("sides", bottom + top, sides, side_mat))
    cap = [(i, (i + 1) % 6, 6) for i in range(6)]
    k.recalc_normals(k.mesh_object("tip_top", top + [(0.0, tip_top, 0.0)], cap, tip_mat))
    k.recalc_normals(k.mesh_object("tip_bottom", bottom + [(0.0, tip_bottom, 0.0)], cap, tip_mat))

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "crystal.glb"))


build()
