"""USP Talon, the starting ship (ship 1; sprite 233 of the ships sheet, 24x28 pixels).

A teardrop hull with a pointed nose, a dark canopy in its front third, a spine along the top and
two engine pods that make the rear the widest part. The hull is one surface: its cross-sections
follow the sprite's silhouette row by row (origin at the sprite's centre, pixel 12, 14), with the
pods and the spine as bulges on top.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    """Blender y of the centre of sprite pixel row `row` (nose up)."""
    return 14 - (row + 0.5)


def section(y, w, top, bottom, spine, pods, segments=40):
    """Cross-section: an ellipse of half-width w (top/bottom half-heights) with a spine crest along
    the middle and two pod bulges at 62% of the half-width."""
    points = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        c, s = math.cos(a), math.sin(a)
        x = w * c
        if s >= 0:
            z = top * s
            z += spine * math.exp(-(x / 0.9) ** 2)
            z += pods * math.exp(-((abs(x) - 0.62 * w) / (0.22 * w + 0.01)) ** 2) * s
        else:
            z = bottom * s
        points.append(Vector((x, y, z)))
    return points


def build():
    k.reset()

    # The sprite's colours. The scene's sky reflections are dim, so metals stay low.
    hull = k.material("talon_hull", (154, 130, 85), metallic=0.2, roughness=0.32)
    trim = k.material("talon_trim", (85, 60, 24), metallic=0.2, roughness=0.45)
    canopy = k.material("talon_canopy", (28, 16, 0), roughness=0.2)

    # (sprite row, half-width, top, bottom, spine, pods): the half-width is the silhouette's.
    rows = [
        (26.75, 2.2, 1.0, 0.6, 0.1, 0.0),
        (26.0, 3.4, 1.6, 0.9, 0.2, 0.25),
        (25.0, 4.9, 2.0, 1.1, 0.3, 0.6),
        (24.0, 6.0, 2.2, 1.2, 0.4, 0.85),
        (23, 6.6, 2.4, 1.3, 0.45, 1.0),
        (21, 8.4, 2.6, 1.4, 0.7, 1.5),
        (19.5, 8.9, 2.7, 1.5, 0.8, 1.6),
        (18, 8.4, 2.8, 1.5, 0.8, 1.4),
        (16.5, 7.4, 2.9, 1.5, 0.7, 0.9),
        (15, 6.6, 2.9, 1.5, 0.45, 0.35),
        (13.5, 5.8, 2.8, 1.5, 0.4, 0.1),
        (12, 4.9, 2.7, 1.4, 0.3, 0.0),
        (10, 4.1, 2.4, 1.3, 0.1, 0.0),
        (7.5, 3.3, 2.0, 1.1, 0.25, 0.0),
        (5.5, 2.8, 1.7, 0.9, 0.3, 0.0),
        (3.5, 1.9, 1.2, 0.7, 0.2, 0.0),
        (2.3, 0.9, 0.6, 0.4, 0.0, 0.0),
    ]
    rows.sort(key=lambda r: row_y(r[0]))
    samples = k.profile([(row_y(r), *rest) for r, *rest in rows], step=0.4)
    rings = [section(*sample) for sample in samples]
    body = k.loft("hull", rings, hull, start_point=(0, row_y(27.0), 0.15), end_point=(0, row_y(1.7), 0.15))
    k.smooth(body, 55)

    # Canopy: a dark glass dome in the front third.
    k.smooth(k.ellipsoid("canopy", (0, row_y(9.7), 1.95), (1.25, 1.7, 0.85), canopy, segments=16, rings_count=10), 60)

    # Panel seams across the rear: the sprite's dark bands at rows 19 and 22.
    for r in (19.2, 22.2):
        y = row_y(r)
        _, w, top, bottom, spine, pods = min(samples, key=lambda sample: abs(sample[0] - y))
        seam = [section(y + d, w + 0.06, top + 0.06, bottom + 0.06, spine + 0.02, pods) for d in (-0.2, 0.2)]
        k.smooth(k.loft("seam", seam, trim), 55)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "talon.glb"))


build()
