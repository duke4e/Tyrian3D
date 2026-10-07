"""Gem (the coins sheet's sprites 14, 32 and 51: red, green and blue gems of 250, 100 and 500
credits): a cut stone whose girdle is the sprite's diamond. models.cfg turns it about the vertical
axis with the sprites' sparkle (a quarter turn per animation) and colours it with the frame's
colour (color=sprite), so the model is grey (ramp 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def build():
    k.reset()
    crown_mat = k.material("gem_crown", palette=9, roughness=0.1, metallic=0.1)
    star_mat = k.material("gem_star", palette=11, roughness=0.08, metallic=0.1)
    table_mat = k.material("gem_table", palette=13, roughness=0.06, metallic=0.1)
    pavilion_mat = k.material("gem_pavilion", palette=5, roughness=0.12, metallic=0.1)

    # The girdle: points on the axes reach the sprite's corners, the ones between bulge a little.
    # Above it a ring of star facets turned half a step, then the table; below, the pavilion.
    def octagon(scale, z, turn=0.0):
        points = []
        for i in range(8):
            a = math.radians(45 * i + turn)
            r = (5.4 if i % 2 == 0 else 4.2) if turn == 0 else 4.6
            points.append((scale * r * math.cos(a), scale * r * math.sin(a), z))
        return points

    girdle = octagon(1.0, 0.3)
    star = octagon(0.72, 1.25, 22.5)
    table = octagon(0.42, 1.9)
    # Girdle to star ring: a triangle under each star point and one over each girdle point.
    lower = []
    for i in range(8):
        lower.append((i, (i + 1) % 8, 8 + i))
        lower.append(((i + 1) % 8, 8 + (i + 1) % 8, 8 + i))
    # Star ring to table: a triangle over each table edge and one under each star point.
    upper = []
    for i in range(8):
        upper.append((i, 8 + (i + 1) % 8, 8 + i))
        upper.append((i, (i + 1) % 8, 8 + (i + 1) % 8))
    k.recalc_normals(k.mesh_object("crown", girdle + star, lower, crown_mat))
    k.recalc_normals(k.mesh_object("star", star + table, upper, star_mat))
    k.recalc_normals(k.mesh_object("table", table, [tuple(range(8))], table_mat))
    pavilion = [((i + 1) % 8, i, 8) for i in range(8)]
    k.recalc_normals(k.mesh_object("pavilion", girdle + [(0.0, 0.0, -3.4)], pavilion, pavilion_mat))

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "items", "gem.glb"))


build()
