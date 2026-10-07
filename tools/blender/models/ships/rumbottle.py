"""Rum Bottle (ship 18; sprite 157 of the Tyrian 2000 ships sheet).

A brown glass bottle flying neck first, with a cork, fins along its lower half and a pale base.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - row


def col_x(col):
    return col - 12


def build():
    k.reset()
    bottle = k.material("bottle_glass", palette=22, roughness=0.12)
    fins = k.material("bottle_fins", palette=20, roughness=0.4)
    cork = k.material("bottle_cork", palette=26, roughness=0.7)
    base = k.material("bottle_base", palette=237, roughness=0.4)

    profile = [(26.8, 0.0), (26.4, 3.0), (25.5, 4.8), (24, 5.6), (19, 5.8), (16, 5.6), (13, 4.6),
               (10, 3.4), (8.5, 2.5), (4, 2.4), (1.6, 2.6), (1.0, 0.0)]
    profile.sort(key=lambda q: row_y(q[0]))
    samples = k.profile([(row_y(r), w) for r, w in profile], step=0.35)
    k.smooth(k.lathe("bottle", [(y, max(w, 0)) for y, w in samples], bottle, 24, axis_z=0.0, squash=0.8), 60)
    k.smooth(k.lathe("cork", [(row_y(r), w) for r, w in sorted([(2.2, 0.0), (2.0, 2.2), (0.5, 2.2), (0.2, 0.0)],
                                                                key=lambda q: row_y(q[0]))], cork, 16, squash=0.8), 50)
    k.smooth(k.lathe("base", [(row_y(r), w) for r, w in sorted([(27.4, 0.0), (27.0, 3.8), (25.6, 4.6), (25.2, 0.0)],
                                                                key=lambda q: row_y(q[0]))], base, 24, squash=0.8), 50)

    # Fins: swept plates from the bottle's lower half out to the sprite's edges.
    for side in (-1, 1):
        outline = [(5.0, 16.2), (12.0, 19.0), (12.0, 23.6), (5.0, 24.2)]
        points = [(side * x, row_y(r)) for x, r in outline]
        if side > 0:
            points = points[::-1]
        k.slab("fin", points, -0.4, 0.5, fins, bevel_width=0.3)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "rumbottle.glb"))


build()
