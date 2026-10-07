"""USP Talon, the starting ship (ship 1; sprite 233 of the ships sheet, 24x28 pixels).

A pear-shaped hull: a pointed nose with a dark canopy in its front third, then a fuselage
flanked by two rounded pods that make the rear the widest part. The hull is one surface whose
cross-sections are the union of the fuselage and the pods, so the creases between them show as
in the sprite (origin at the sprite's centre, pixel 12, 14).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    """Blender y of the centre of sprite pixel row `row` (nose up)."""
    return 14 - (row + 0.5)


POD_Z = 0.3

# Sprite row: fuselage half-width, top, bottom; pod centre x, half-width, top, bottom. The
# silhouette follows the sprite's (less its dark outline); the pods rise above the fuselage, so
# the grooves between them run where the sprite has its dark lines.
ROWS = [
    (2.0, 0.7, 0.5, 0.35, 1.5, 0.0, 0.0, 0.0),
    (3.0, 1.3, 0.9, 0.6, 1.5, 0.0, 0.0, 0.0),
    (5.0, 2.2, 1.4, 0.9, 1.5, 0.0, 0.0, 0.0),
    (8.0, 3.1, 1.9, 1.1, 1.8, 0.0, 0.0, 0.0),
    (10.0, 3.5, 2.1, 1.3, 2.0, 0.0, 0.0, 0.0),
    (11.5, 3.6, 2.2, 1.4, 2.3, 0.6, 0.6, 0.4),
    (13.0, 3.4, 2.2, 1.4, 3.0, 2.0, 1.3, 0.8),
    (15.0, 3.2, 2.1, 1.4, 3.9, 2.9, 1.9, 1.1),
    (17.0, 3.1, 2.1, 1.4, 4.5, 3.4, 2.3, 1.3),
    (19.0, 3.0, 2.1, 1.4, 4.9, 3.7, 2.5, 1.4),
    (20.5, 3.0, 2.1, 1.4, 5.0, 3.7, 2.5, 1.4),
    (22.0, 3.0, 2.0, 1.3, 5.0, 3.2, 2.3, 1.3),
    (23.0, 2.8, 1.9, 1.3, 4.7, 2.6, 2.0, 1.2),
    (24.0, 2.4, 1.6, 1.1, 4.2, 2.0, 1.6, 0.9),
    (25.0, 1.8, 1.2, 0.8, 3.5, 1.3, 1.0, 0.6),
    (25.6, 1.2, 0.8, 0.6, 3.0, 0.7, 0.5, 0.3),
    (26.2, 0.5, 0.4, 0.3, 2.6, 0.0, 0.0, 0.0),
]


def section(y, bw, bt, bb, px, pw, pt, pb):
    lobes = [
        (0, 0, bw, bt, bb),        # fuselage
        (-px, POD_Z, pw, pt, pb),  # pods
        (px, POD_Z, pw, pt, pb),
    ]
    return k.lobed_ring(y, lobes, segments=64, origin_z=0.1)


def build():
    k.reset()

    hull = k.material("talon_hull", palette=25, metallic=0.3, roughness=0.3)
    canopy = k.material("talon_canopy", palette=16, roughness=0.12)

    samples = k.profile(sorted([(row_y(r[0]), *r[1:]) for r in ROWS]), step=0.3)
    rings = [section(*s) for s in samples]
    body = k.loft("hull", rings, hull, start_point=(0, row_y(26.5), 0.1), end_point=(0, row_y(1.5), 0.15))
    k.smooth(body, 45)

    # Canopy: a dark glass dome in the front third.
    k.smooth(k.ellipsoid("canopy", (0, row_y(10.3), 1.7), (1.6, 1.8, 0.85), canopy, segments=16, rings_count=10), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "talon.glb"))


build()
