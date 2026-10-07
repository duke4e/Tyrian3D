"""Silver Ship (ship 11; sprite 81 of the ships sheet).

A silver fighter: a pointed nose with a dark canopy, short swept wings at the shoulders, a broad
body behind them with red-striped side panels, and two engine prongs at the tail.
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
    silver = k.material("silver_body", (162, 166, 162), metallic=0.35, roughness=0.28)
    grey = k.material("silver_grey", (93, 93, 93), metallic=0.3, roughness=0.35)
    red = k.material("silver_red", (130, 0, 0), roughness=0.35)
    glass = k.material("silver_canopy", (24, 24, 30), roughness=0.12)

    cx = col_x(11.5)
    # Fuselage: (row at pixel centre, half-width, top, bottom), with a bright spine along the top.
    rows = [(26.4, 1.4, 0.9, 0.5), (25, 2.6, 1.6, 0.9), (22, 3.2, 2.2, 1.2), (16, 3.6, 2.6, 1.4),
            (11, 3.8, 2.6, 1.4), (8.5, 4.2, 2.5, 1.3), (6.5, 4.3, 2.4, 1.2), (4.5, 3.6, 2.1, 1.0),
            (2.5, 2.8, 1.6, 0.8), (0.8, 1.5, 0.9, 0.5)]
    rows.sort(key=lambda r: row_y(r[0]))
    samples = k.profile([(row_y(r), w, t, b) for r, w, t, b in rows], step=0.4)
    k.smooth(k.loft("fuselage", [k.ring(y, w, 1.0, 22, x=cx, top=t, bottom=b, crest=0.5) for y, w, t, b in samples],
                    silver, start_point=(cx, row_y(26.8), 0.1), end_point=(cx, row_y(0.1), 0.2)), 50)
    k.smooth(k.ellipsoid("canopy", (cx, row_y(7.2), 2.55), (1.4, 1.6, 0.8), glass, 16, 10), 60)

    # Shoulder wings.
    wing = [(4.0, 9.6), (6.2, 7.4), (8.2, 7.6), (8.2, 10.2), (4.0, 10.2)]
    left = k.slab("wing_left", [(col_x(c), row_y(r)) for c, r in wing], -0.2, 0.8, grey, bevel_width=0.25)
    shift = __import__("mathutils").Matrix.Translation((2 * cx, 0, 0))
    k.mirror_x(left, "wing_right").data.transform(shift)

    # Side nacelles with red stripes at the back: (row, half-width, centre offset from cx).
    nacelle = [(25.6, 0.0, 4.6), (25.0, 1.2, 4.8), (23, 2.2, 5.6), (20, 3.1, 6.6), (16, 3.2, 6.8),
               (13.5, 2.3, 6.2), (12.0, 1.2, 5.4), (11.3, 0.0, 5.2)]
    nacelle.sort(key=lambda q: row_y(q[0]))
    samples = k.profile([(row_y(r), w, o) for r, w, o in nacelle], step=0.4)
    left_nacelle = k.loft("nacelle_left", [k.ring(y, w, w * 0.7, 16, x=cx - o, z=0.3) for y, w, o in samples if w > 0],
                          grey, start_point=(cx - 4.6, row_y(25.7), 0.3), end_point=(cx - 5.2, row_y(11.2), 0.4))
    k.smooth(left_nacelle, 50)
    k.smooth(k.mirror_x(left_nacelle, "nacelle_right"), 50).data.transform(shift)
    for r in (17.6, 21.4):
        y = row_y(r)
        _, w, o = min(samples, key=lambda q: abs(q[0] - y))
        band = k.loft("stripe_left", [k.ring(y + d, w + 0.08, (w + 0.08) * 0.7, 16, x=cx - o, z=0.3) for d in (-0.45, 0.45)], red)
        k.smooth(band, 50)
        k.smooth(k.mirror_x(band, "stripe_right"), 50).data.transform(shift)

    # Engine prongs at the tail.
    for side in (-1, 1):
        prong = [(26.6, 0.0), (26.2, 0.9), (23, 1.1), (21.5, 0.0)]
        prong.sort(key=lambda q: row_y(q[0]))
        k.smooth(k.lathe("prong", [(row_y(r), w) for r, w in prong], grey, 12, axis_x=cx + side * 1.8, axis_z=-0.2), 55)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "silver.glb"))


build()
