"""Nort Ship (ship 12; the game draws it in two halves, sprites 220 and 222 of the ships sheet,
side by side: 48x28 pixels, centred like the other ships).

A grey delta: a long fuselage with a dark canopy, red gun barrels at the shoulders, wide swept
wings with blue leading edges, and two engine booms under the trailing edge.

Coordinates are pixel boundaries of the 48x28 pair: the origin is its centre, column 24, row 14.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
from mathutils import Matrix  # noqa: E402


def bx(col):
    return col - 24


def by(row):
    return 14 - row


def build():
    k.reset()
    body = k.material("nort_body", palette=9, metallic=0.35, roughness=0.3)
    wing_mat = k.material("nort_wing", palette=8, metallic=0.3, roughness=0.35)
    dark = k.material("nort_dark", palette=4, metallic=0.3, roughness=0.4)
    blue = k.material("nort_blue", palette=57, metallic=0.2, roughness=0.3)
    red = k.material("nort_gun", palette=116, metallic=0.3, roughness=0.35)
    glass = k.material("nort_canopy", palette=48, roughness=0.1)

    cx = -0.5  # the pair's silhouette spans columns 5-41
    # Fuselage: (row, half-width, top, bottom), nose to tail.
    rows = [(0.2, 1.0, 0.8, 0.5), (1.0, 1.8, 1.2, 0.7), (2.5, 3.3, 1.8, 0.9), (4.5, 4.4, 2.4, 1.1),
            (7.0, 4.9, 2.8, 1.3), (10.0, 5.1, 3.0, 1.4), (14.0, 5.3, 3.0, 1.4), (18.0, 5.2, 2.8, 1.3),
            (21.0, 4.6, 2.3, 1.2), (22.8, 3.0, 1.6, 0.9)]
    rows.sort(key=lambda r: by(r[0]))
    samples = k.profile([(by(r), w, t, b) for r, w, t, b in rows], step=0.4)
    k.smooth(k.loft("fuselage", [k.ring(y, w, 1.0, 24, x=cx, top=t, bottom=b, crest=0.5) for y, w, t, b in samples],
                    body, start_point=(cx, by(23.2), 0.2), end_point=(cx, by(0.0), 0.3)), 50)
    k.smooth(k.ellipsoid("canopy", (cx, by(6.0), 2.6), (2.0, 3.0, 1.0), glass, 16, 10), 60)

    # Wings (left, then mirrored about the fuselage's axis), with blue leading edges.
    wing = [(-4.0, 4.6), (-11.4, 4.0), (-18.8, -3.0), (-18.8, -6.6), (-15.6, -10.0), (-3.0, -10.0), (-3.0, 2.0)]
    left = k.slab("wing_left", [(x + cx + 0.5, y) for x, y in wing], -0.6, 0.8, wing_mat, bevel_width=0.3)
    stripe = [(-4.6, 4.75), (-11.5, 4.2), (-19.0, -2.8), (-19.0, -4.3), (-11.8, 2.9), (-4.6, 3.4)]
    # A darker panel on each wing, inboard of the tip.
    panel = [(-5.0, 1.5), (-11.0, 1.5), (-16.0, -4.0), (-16.0, -7.5), (-5.0, -7.5)]
    left_panel = k.slab("panel_left", [(x + cx + 0.5, y) for x, y in panel], 0.6, 0.95, dark, bevel_width=0.2)
    left_stripe = k.slab("stripe_left", [(x + cx + 0.5, y) for x, y in stripe], 0.55, 1.0, blue, bevel_width=0.15)
    mirror = Matrix.Translation((2 * cx, 0, 0))
    for part in (left, left_stripe, left_panel):
        k.mirror_x(part, part.name.replace("left", "right")).data.transform(mirror)

    # Gun barrels at the shoulders (columns 15 and 31, rows 5-10), in grey housings.
    for col in (15.5, 31.5):
        x = bx(col)
        k.smooth(k.lathe("gun", [(by(r), w) for r, w in sorted([(10.5, 0.0), (10.2, 1.3), (7.5, 1.3), (7.2, 0.0)],
                                                                 key=lambda q: by(q[0]))], dark, 12, axis_x=x, axis_z=0.9), 50)
        k.smooth(k.lathe("barrel", [(by(r), w) for r, w in sorted([(7.6, 0.0), (7.4, 0.7), (4.6, 0.7), (4.4, 0.0)],
                                                                   key=lambda q: by(q[0]))], red, 10, axis_x=x, axis_z=0.9), 50)

    # Engine booms under the trailing edge (columns 14-20 and 26-32, rows 21-27).
    for col in (17.5, 29.5):
        boom = [(27.6, 0.0), (27.3, 1.6), (25.5, 2.8), (23.0, 3.2), (21.0, 2.6), (20.0, 0.0)]
        boom.sort(key=lambda q: by(q[0]))
        k.smooth(k.lathe("boom", [(by(r), w) for r, w in boom], body, 18, axis_x=bx(col), axis_z=0.2), 50)
        nozzle = [(27.9, 0.0), (27.7, 1.2), (27.0, 1.4), (26.6, 0.0)]
        nozzle.sort(key=lambda q: by(q[0]))
        k.smooth(k.lathe("nozzle", [(by(r), w) for r, w in nozzle], dark, 14, axis_x=bx(col), axis_z=0.2), 50)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "nortship.glb"), size=(48, 28))


build()
