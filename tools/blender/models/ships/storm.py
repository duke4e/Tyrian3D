"""Storm (ship 14; sprite 5 of the Tyrian 2000 ships sheet).

A black stealth delta: a long narrow nose with a blue canopy, widening into flat wings, with
two flat pods on the rear wings and a bar of blue lights at the tail.
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
    hull = k.material("storm_hull", (24, 16, 36), metallic=0.4, roughness=0.28)
    trim = k.material("storm_trim", (48, 60, 69), metallic=0.4, roughness=0.3)
    glass = k.material("storm_glass", (77, 130, 146), roughness=0.1, emission=(77, 130, 146), emission_strength=0.6)
    lights = k.material("storm_lights", (77, 130, 146), roughness=0.3, emission=(110, 190, 230), emission_strength=3.0)

    # Hull: (row at pixel centre, half-width, top, bottom, crest).
    rows = [(27.3, 1.2, 0.5, 0.3, 0.0), (26.5, 4.6, 0.9, 0.5, 0.2), (25.5, 6.8, 1.1, 0.6, 0.3), (24.5, 8.8, 1.2, 0.7, 0.4),
            (23, 10.3, 1.2, 0.7, 0.5), (21, 10.9, 1.2, 0.7, 0.7), (19, 10.8, 1.2, 0.7, 0.9), (17, 9.6, 1.2, 0.7, 1.0),
            (15, 7.9, 1.3, 0.7, 1.1), (13, 5.9, 1.4, 0.8, 1.1), (11, 3.9, 1.5, 0.8, 0.9), (8, 3.0, 1.5, 0.8, 0.5),
            (5, 2.9, 1.4, 0.8, 0.3), (3, 2.6, 1.2, 0.7, 0.2), (1.5, 1.6, 0.8, 0.4, 0.0), (0.6, 0.8, 0.4, 0.3, 0.0)]
    rows.sort(key=lambda r: row_y(r[0]))
    samples = k.profile([(row_y(r), w, t, b, c) for r, w, t, b, c in rows], step=0.4)
    rings = [k.ring(y, w, 1.0, 24, top=t, bottom=b, crest=c) for y, w, t, b, c in samples]
    k.smooth(k.loft("hull", rings, hull, start_point=(0, row_y(27.7), 0.0), end_point=(0, row_y(0.2), 0.1)), 40)

    k.smooth(k.ellipsoid("canopy", (0, row_y(3.9), 1.05), (1.1, 1.6, 0.55), glass, 14, 8), 60)

    # Rear pods with lights on their sides.
    for side in (-1, 1):
        pod = [(22.4, 0.0), (21.8, 1.4), (19, 1.9), (16.5, 1.5), (15.6, 0.0)]
        pod.sort(key=lambda q: row_y(q[0]))
        k.smooth(k.lathe("pod", [(row_y(r), w) for r, w in pod], trim, 14, axis_x=side * 7.2, axis_z=0.9, squash=0.6), 55)
        k.smooth(k.ellipsoid("pod_light", (side * 8.6, row_y(19.4), 0.95), (0.5, 1.6, 0.4), lights, 10, 6), 60)

    # The tail's light bar.
    bar = [(-3.2, row_y(24.7)), (3.2, row_y(24.7)), (3.2, row_y(24.1)), (-3.2, row_y(24.1))]
    k.slab("light_bar", bar[::-1], 1.0, 1.55, lights, bevel_width=0.12)
    # Lights along the middle (the sprite's blue windows).
    for r, w in ((16.6, 1.0), (20.6, 1.2)):
        k.smooth(k.ellipsoid("window", (0, row_y(r), 1.9), (w, 0.7, 0.35), lights, 10, 6), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "storm.glb"))


build()
