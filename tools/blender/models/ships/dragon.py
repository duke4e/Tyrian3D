"""Red Dragon (ship 15; sprite 43 of the Tyrian 2000 ships sheet).

A red dragon flying head first: horned head, spread bat wings with ribs and scalloped trailing
edges, a scaled body and a long tail.
"""
import math
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
    scales = k.material("dragon_scales", palette=117, roughness=0.4)
    dark = k.material("dragon_dark", palette=114, roughness=0.5)
    membrane = k.material("dragon_membrane", palette=115, roughness=0.6)
    eyes = k.material("dragon_eyes", (255, 200, 40), emission=(255, 170, 30), emission_strength=4.0)

    # Body from tail to snout: (row at pixel centre, half-width, top, bottom).
    rows = [(27.6, 0.3, 0.3, 0.2), (26, 0.9, 0.7, 0.5), (24, 1.2, 0.9, 0.6), (22, 2.6, 1.5, 1.0),
            (20, 4.0, 2.0, 1.3), (18, 3.8, 2.0, 1.3), (16.5, 2.6, 1.6, 1.0), (14, 2.0, 1.5, 0.9),
            (11, 2.2, 1.6, 1.0), (8, 2.4, 1.6, 1.0), (6, 4.4, 1.8, 1.0), (4, 3.6, 1.6, 0.9),
            (2, 2.4, 1.2, 0.7), (0.6, 1.0, 0.6, 0.4)]
    rows.sort(key=lambda r: row_y(r[0]))
    samples = k.profile([(row_y(r), w, t, b) for r, w, t, b in rows], step=0.4)
    k.smooth(k.loft("body", [k.ring(y, w, 1.0, 18, top=t, bottom=b, crest=0.25) for y, w, t, b in samples], scales,
                    start_point=(0, row_y(28.0), 0.0), end_point=(0, row_y(0.1), 0.2)), 55)
    for x in (-1.3, 1.3):
        k.smooth(k.ellipsoid("eye", (x, row_y(2.6), 1.0), (0.45, 0.5, 0.35), eyes, 8, 6), 60)
    # Horns beside the head.
    for side in (-1, 1):
        horn = k.slab("horn", [(side * 3.0, row_y(5.6)), (side * 5.2, row_y(6.4)), (side * 3.4, row_y(7.4))][::side],
                      0.3, 0.9, dark, bevel_width=0.15)

    # Wings: a membrane from the shoulders to the tips with a scalloped trailing edge, and ribs.
    for side in (-1, 1):
        outline = [(1.8, 8.2), (9.0, 7.6), (12.0, 9.8), (12.0, 13.6), (9.6, 14.6), (7.8, 13.6), (5.6, 15.2),
                   (3.8, 14.0), (2.0, 15.6)]
        points = [(side * x, row_y(r)) for x, r in outline]
        if side < 0:
            points = points[::-1]
        k.slab("wing", points, -0.2, 0.25, membrane, bevel_width=0.1)
        for tip_x, tip_r in ((12.0, 13.6), (7.8, 13.6), (3.8, 14.0)):
            rib = [(1.8, 8.6), (2.4, 8.2), (tip_x + 0.3, tip_r), (tip_x - 0.3, tip_r)]
            rib_points = [(side * x, row_y(r)) for x, r in rib]
            if side < 0:
                rib_points = rib_points[::-1]
            k.slab("rib", rib_points, 0.2, 0.6, scales, bevel_width=0.1)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "dragon.glb"))


build()
