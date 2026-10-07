"""U-Ship (ship 10; sprite 271 of the ships sheet).

A U-shaped frame open to the front: two dark arms with a light stripe, joined at the back by a
tan arc, around a tan bullet-shaped pod in the middle.
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
    frame = k.material("uship_frame", palette=3, metallic=0.3, roughness=0.45)
    stripe = k.material("uship_stripe", palette=10, metallic=0.3, roughness=0.3)
    tan = k.material("uship_tan", palette=25, metallic=0.25, roughness=0.35)

    cx = col_x(11.5)
    # Arms: rounded bars down the sides (sprite columns 4-6 and 16-18, rows 7-22).
    for c0 in (4, 16):
        x = col_x(c0 + 1.5)
        rows = [(22.5, 1.5), (8.5, 1.5), (7.2, 1.1)]
        rings = [k.ring(row_y(r), w, 1.4, 12, x=x, z=0.3, power=3) for r, w in sorted(rows, key=lambda q: row_y(q[0]))]
        k.smooth(k.loft("arm", rings, frame, end_point=(x, row_y(7.0), 0.4)), 45)
        bar = [(c0 + 1.1, 7.6), (c0 + 1.1, 21.5), (c0 + 1.9, 21.5), (c0 + 1.9, 7.6)]
        k.slab("arm_stripe", [(col_x(c), row_y(r)) for c, r in bar], 1.5, 1.85, stripe, bevel_width=0.12)

    # The back: an arc joining the arms, tan, around the pod's rear.
    outer, inner = [], []
    for i in range(13):
        a = math.pi * i / 12
        outer.append((cx - 7.0 * math.cos(a), row_y(21.0) - 4.9 * math.sin(a)))
        inner.append((cx - 5.4 * math.cos(a), row_y(21.0) - 3.4 * math.sin(a)))
    arc = outer + inner[::-1]
    k.slab("arc", arc[::-1], -0.5, 1.0, tan, bevel_width=0.3)

    # Struts from the arms to the pod.
    for c0, c1 in ((6.5, 9.0), (14.0, 16.5)):
        strut = [(c0, 15.2), (c0, 17.8), (c1, 17.8), (c1, 15.2)]
        k.slab("strut", [(col_x(c), row_y(r)) for c, r in strut], -0.2, 0.9, stripe, bevel_width=0.2)

    # The pod: a bullet pointing forward.
    pod = [(20.6, 0.0), (20.3, 2.6), (19, 3.4), (16, 3.5), (14, 3.1), (12.8, 2.1), (12.1, 0.0)]
    pod.sort(key=lambda q: row_y(q[0]))
    rings = [k.ring(row_y(r), w, w * 0.85, 20, x=cx, z=0.2, power=3) for r, w in pod if w > 0]
    k.smooth(k.loft("pod", rings, tan, start_point=(cx, row_y(20.6), 0.2), end_point=(cx, row_y(12.1), 0.2)), 50)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "uship.glb"))


build()
