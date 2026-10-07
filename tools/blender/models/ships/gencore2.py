"""Gencore II (ship 16; sprite 81 of the Tyrian 2000 ships sheet).

A grey fighter with a glazed nose, big wings whose tips sweep forward to the sprite's edges (blue
lights along them), and two engine pods with blue nozzles behind the wings.
"""
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - row


def col_x(col):
    return col - 12


def mirrored(obj, name):
    """A mirrored copy about the sprite's centre column."""
    return k.mirror_x(obj, name)


def build():
    k.reset()
    body = k.material("gencore2_body", (105, 109, 105), metallic=0.3, roughness=0.32)
    dark = k.material("gencore2_dark", (40, 40, 40), metallic=0.3, roughness=0.45)
    glass = k.material("gencore2_glass", (40, 70, 110), roughness=0.1)
    blue = k.material("gencore2_lights", (77, 130, 200), roughness=0.3, emission=(90, 160, 255), emission_strength=3.0)

    # Fuselage: (row at pixel centre, half-width, top, bottom).
    rows = [(27.3, 1.6, 0.8, 0.5), (26, 3.0, 1.4, 0.9), (23, 3.6, 1.8, 1.1), (19, 4.4, 2.2, 1.3),
            (15, 4.6, 2.4, 1.4), (11, 4.2, 2.3, 1.3), (8, 3.8, 2.1, 1.2), (5, 3.8, 2.0, 1.1),
            (3, 3.0, 1.7, 0.9), (1.4, 1.8, 1.1, 0.6), (0.5, 0.9, 0.5, 0.3)]
    rows.sort(key=lambda r: row_y(r[0]))
    samples = k.profile([(row_y(r), w, t, b) for r, w, t, b in rows], step=0.4)
    k.smooth(k.loft("fuselage", [k.ring(y, w, 1.0, 20, top=t, bottom=b) for y, w, t, b in samples], body,
                    start_point=(0, row_y(27.7), 0.1), end_point=(0, row_y(0.1), 0.2)), 55)
    k.smooth(k.ellipsoid("canopy_ring", (0, row_y(4.6), 1.3), (2.6, 2.6, 1.1), dark, 16, 10), 60)
    k.smooth(k.ellipsoid("canopy", (0, row_y(4.4), 1.7), (1.5, 1.8, 0.9), glass, 16, 10), 60)
    k.smooth(k.ellipsoid("spine", (0, row_y(15.5), 2.0), (1.2, 4.5, 0.6), dark, 12, 10), 55)

    # Side nacelles: from tips at the sprite's front corners back to engines behind the wings.
    # (row at pixel centre, half-width, centre column).
    nacelle = [(25.8, 0.0, 4.8), (25.2, 1.7, 4.6), (23, 2.4, 4.2), (20, 2.9, 3.4), (17, 3.0, 3.0),
               (14, 2.9, 3.0), (12, 2.3, 2.4), (10, 1.5, 1.6), (8.4, 0.5, 0.9)]
    nacelle.sort(key=lambda q: row_y(q[0]))
    samples = k.profile([(row_y(r), w, col_x(c)) for r, w, c in nacelle], step=0.4)
    left = k.loft("nacelle_left", [k.ring(y, w, w * 0.75, 16, x=x, z=0.3, power=3) for y, w, x in samples if w > 0],
                  body, start_point=(col_x(4.8), row_y(25.9), 0.3), end_point=(col_x(0.8), row_y(8.2), 0.4))
    k.smooth(left, 50)
    k.smooth(mirrored(left, "nacelle_right"), 50)
    # Wings joining them to the fuselage.
    wing = [(4.5, 20.4), (8.6, 20.4), (8.6, 14.2), (4.5, 13.4)]
    joint = k.slab("wing_left", [(col_x(c), row_y(r)) for c, r in wing], -0.3, 0.7, dark, bevel_width=0.25)
    mirrored(joint, "wing_right")

    # Blue lights: on the nacelles' outer sides, beside the neck, and the engine nozzles.
    for obj in (k.ellipsoid("light_side", (col_x(0.4), row_y(15.0), 0.6), (0.45, 1.4, 0.6), blue, 10, 6),
                k.ellipsoid("light_neck", (col_x(9.6), row_y(10.6), 1.9), (0.55, 0.9, 0.5), blue, 10, 6),
                k.ellipsoid("nozzle", (col_x(4.7), row_y(25.6), 0.3), (1.5, 0.45, 1.1), blue, 12, 6)):
        k.smooth(obj, 60)
        k.smooth(mirrored(obj, obj.name + "_right"), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "gencore2.glb"))


build()
