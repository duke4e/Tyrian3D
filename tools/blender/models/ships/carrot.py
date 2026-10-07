"""SuperCarrot (ship 2; sprite 119 of the ships sheet).

A flying carrot: a round orange body tapering to a point at the front, ridged across, with a dark
glass canopy and green leaves fanning out behind.
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
    orange = k.material("carrot_orange", palette=121, roughness=0.45)
    ridge = k.material("carrot_ridge", palette=118, roughness=0.5)
    glass = k.material("carrot_canopy", palette=179, roughness=0.12)
    green = k.material("carrot_leaf", palette=196, roughness=0.55)

    cx = col_x(11.5)
    radius = [(18.9, 0.0), (18.4, 3.0), (17.5, 5.2), (15.5, 6.6), (13.5, 6.6), (11, 5.8), (8.5, 4.9),
              (6, 3.9), (4, 2.8), (2, 1.6), (0.6, 0.6), (0.1, 0.0)]
    radius.sort(key=lambda q: row_y(q[0]))
    samples = k.profile([(row_y(r), w) for r, w in radius], step=0.35)
    k.smooth(k.lathe("body", [(y, max(w, 0)) for y, w in samples], orange, 24, axis_x=cx, axis_z=0.0, squash=0.75), 60)
    for r in (5.5, 9.5, 13.0, 16.5):
        y = row_y(r)
        _, w = min(samples, key=lambda q: abs(q[0] - y))
        band = [k.ring(y + d, w + 0.08, (w + 0.08) * 0.75, 24, x=cx) for d in (-0.18, 0.18)]
        k.smooth(k.loft("ridge", band, ridge), 60)
    k.smooth(k.ellipsoid("canopy", (cx, row_y(10.4), 3.9), (1.8, 1.9, 1.0), glass, 16, 10), 60)

    # Leaves fanning out from the carrot's top, behind it: (angle from straight back, length).
    for angle, length in ((-62, 6.5), (-28, 7.5), (0, 8.5), (35, 6.0)):
        a = math.radians(angle)
        leaf = k.ellipsoid("leaf", (0, 0, 0), (1.5, length / 2, 0.35), green, 12, 8)
        leaf.rotation_euler = (0.25, 0, a)
        leaf.location = (cx + math.sin(a) * (length / 2), row_y(18.6) - math.cos(a) * (length / 2), 0.2)
        k.smooth(leaf, 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "carrot.glb"))


build()
