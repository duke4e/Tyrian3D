"""Dragonwing (the second player's ship in two-player arcade games; the game draws it in two
halves, sprites 13 and 51 of the ships sheet side by side, with banking frames 9-17 and 47-55).

A wide bronze craft: a central body with a dark canopy and a glowing exhaust, two big engine
pods at the wing ends with fins outside them.

Coordinates are pixel boundaries of the 48x28 pair: the origin is its centre, column 24, row 14.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def bx(col):
    return col - 24


def by(row):
    return 14 - row


def build():
    k.reset()
    hull = k.material("dragonwing_hull", palette=24, metallic=0.3, roughness=0.35)
    pod_mat = k.material("dragonwing_pod", palette=26, metallic=0.3, roughness=0.3)
    dark = k.material("dragonwing_dark", palette=19, metallic=0.2, roughness=0.45)
    glass = k.material("dragonwing_canopy", palette=17, roughness=0.12)
    flame = k.material("dragonwing_exhaust", (235, 138, 24), roughness=0.4, emission=(255, 120, 20), emission_strength=3.0)

    # The central body, columns 16-32, rows 7-23: (row, half-width, top, bottom).
    cx = bx(24.5)
    rows = [(7.2, 2.5, 1.2, 0.6), (8.5, 6.0, 2.4, 1.0), (10.5, 7.6, 3.2, 1.4), (14.0, 8.2, 3.4, 1.5),
            (18.0, 8.2, 3.2, 1.5), (20.5, 7.6, 2.8, 1.4), (22.2, 6.0, 2.0, 1.1), (23.2, 3.5, 1.2, 0.8)]
    rows.sort(key=lambda r: by(r[0]))
    samples = k.profile([(by(r), w, t, b) for r, w, t, b in rows], step=0.4)
    k.smooth(k.loft("body", [k.ring(y, w, 1.0, 24, x=cx, top=t, bottom=b, crest=0.4, power=2.8) for y, w, t, b in samples],
                    hull, start_point=(cx, by(23.6), 0.2), end_point=(cx, by(6.9), 0.3)), 50)
    k.smooth(k.ellipsoid("canopy", (cx, by(11.5), 3.1), (2.8, 2.0, 1.0), glass, 16, 10), 60)
    # Two ridges at the front of the body.
    for col in (20.0, 29.0):
        k.smooth(k.ellipsoid("ridge", (bx(col), by(9.5), 2.4), (1.4, 2.6, 1.2), pod_mat, 12, 8), 60)
    k.smooth(k.ellipsoid("exhaust", (cx, by(24.0), 0.6), (5.8, 2.2, 1.1), flame, 18, 8), 60)

    # The wings between body and pods, and the pods: (row, half-width, top, bottom).
    pod = [(6.4, 1.2, 0.8, 0.5), (7.5, 3.0, 2.0, 1.0), (10.0, 4.4, 3.0, 1.4), (14.0, 4.8, 3.2, 1.5),
           (18.0, 4.7, 3.0, 1.4), (20.6, 4.4, 2.6, 1.2), (21.8, 3.0, 1.4, 0.7)]
    pod.sort(key=lambda r: by(r[0]))
    pod_samples = k.profile([(by(r), w, t, b) for r, w, t, b in pod], step=0.4)
    for side in (-1, 1):
        px = cx + side * 15.0
        k.smooth(k.loft("pod", [k.ring(y, w, 1.0, 20, x=px, top=t, bottom=b, crest=0.3, power=2.6)
                                for y, w, t, b in pod_samples],
                        pod_mat, start_point=(px, by(22.1), 0.2), end_point=(px, by(6.1), 0.3)), 50)
        inner, outer = cx + side * 7.0, cx + side * 11.5
        wing = [(inner, by(9.0)), (outer, by(9.3)), (outer, by(19.0)), (inner, by(19.4))]
        if side > 0:
            wing.reverse()
        k.slab("wing", wing, -0.4, 1.4, hull, bevel_width=0.3)
        # Fins outside the pods (columns 1-4 and 44-47, rows 13-18).
        root, tip = cx + side * 19.2, cx + side * 23.0
        fin = [(root, by(12.5)), (tip, by(14.8)), (tip, by(17.6)), (root, by(18.8))]
        if side > 0:
            fin.reverse()
        k.slab("fin", fin, -0.2, 0.9, dark, bevel_width=0.2)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "dragonwing.glb"), size=(48, 28))


build()
