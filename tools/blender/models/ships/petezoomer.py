"""PeteZoomer (ship 17; sprite 119 of the Tyrian 2000 ships sheet).

A flying beer mug, lying along the flight path: golden beer behind glass, foam at the open front,
a glass handle on the left, and two beer cans strapped to its lower sides with blue thrusters.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - row


def col_x(col):
    return col - 12


def build():
    k.reset()
    beer = k.material("mug_beer", palette=124, roughness=0.18)
    foam = k.material("mug_foam", palette=126, roughness=0.7)
    glass = k.material("mug_glass", palette=12, metallic=0.1, roughness=0.15)
    blue = k.material("mug_thrusters", (60, 120, 220), roughness=0.3, emission=(80, 150, 255), emission_strength=3.0)

    cx = col_x(12.7)  # the mug's axis (the handle sits to its left)
    body = [(27.2, 0.0), (26.6, 6.4), (25.5, 7.1), (2, 7.3), (0.6, 7.3), (0.3, 0.0)]
    body.sort(key=lambda q: row_y(q[0]))
    k.smooth(k.lathe("mug", [(row_y(r), w) for r, w in body], beer, 28, axis_x=cx, axis_z=0.0, squash=0.55), 40)
    # Foam spilling over the open front, and the glass rim around it.
    k.smooth(k.ellipsoid("foam", (cx, row_y(1.4), 0.6), (6.8, 1.6, 3.7), foam, 20, 8), 60)
    rim = [k.ring(row_y(r), 7.55, 7.55 * 0.55, 28, x=cx) for r in (1.6, 0.4)]
    k.smooth(k.loft("rim", rim, glass), 40)

    # Handle: a bent glass bar on the left side.
    points = []
    for i in range(9):
        a = math.pi * i / 8
        points.append(Vector((cx - 6.8 - 3.2 * math.sin(a), row_y(11.0) - 5.0 * i / 8, 1.0)))
    rings = []
    for i, p in enumerate(points):
        rings.append(k.ring(p.y, 1.1, 1.1, 10, x=p.x, z=p.z))
    k.smooth(k.loft("handle", rings, glass), 50)

    # Cans along the lower sides, with thrusters at their backs.
    for x in (col_x(2.6), col_x(21.6)):
        can = [(24.6, 0.0), (24.3, 2.0), (14.6, 2.0), (14.3, 0.0)]
        can.sort(key=lambda q: row_y(q[0]))
        k.smooth(k.lathe("can", [(row_y(r), w) for r, w in can], beer, 16, axis_x=x, axis_z=-0.5), 45)
        k.smooth(k.ellipsoid("thruster", (x, row_y(24.8), -0.5), (1.4, 0.6, 1.4), blue, 12, 6), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "petezoomer.glb"))


build()
