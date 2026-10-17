"""USP Talon, the starting ship (ship 1; sprite 233 of the ships sheet, 24x28 pixels).

A pear-shaped hull: a pointed nose with a dark canopy in its front third, then a fuselage
flanked by two rounded pods that make the rear the widest part. The hull is one surface whose
cross-sections are the union of the fuselage, the pods and a spine, so the creases between them
show as in the sprite (origin at the sprite's centre, pixel 12, 14).

Polish (2026-10-18): the upscale shows a raised spine from the canopy to the tail with three
light bands across it near the tail, a glossy black canopy and a shinier hull; the rear of the
pods carries engine nozzles with a faint glow.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    """Blender y of the centre of sprite pixel row `row` (nose up)."""
    return 14 - (row + 0.5)


POD_Z = 0.3
SPINE_Z = 0.35

# Sprite row: fuselage half-width, top, bottom; pod centre x, half-width, top, bottom; spine
# half-width, top (above SPINE_Z). The silhouette follows the sprite's (less its dark outline);
# the pods rise above the fuselage, so the grooves between them run where the sprite has its dark
# lines. The spine stays inside the fuselage ahead of the canopy.
ROWS = [
    (2.0, 0.7, 0.5, 0.35, 1.5, 0.0, 0.0, 0.0, 0.2, 0.1),
    (3.0, 1.3, 0.9, 0.6, 1.5, 0.0, 0.0, 0.0, 0.2, 0.1),
    (5.0, 2.2, 1.4, 0.9, 1.5, 0.0, 0.0, 0.0, 0.3, 0.3),
    (8.0, 3.1, 1.9, 1.1, 1.8, 0.0, 0.0, 0.0, 0.4, 0.6),
    (10.0, 3.5, 2.1, 1.3, 2.0, 0.0, 0.0, 0.0, 0.6, 1.1),
    (11.5, 3.6, 2.2, 1.4, 2.3, 0.6, 0.6, 0.4, 0.95, 1.75),
    (13.0, 3.4, 2.2, 1.4, 3.0, 2.0, 1.3, 0.8, 1.15, 2.3),
    (15.0, 3.2, 2.1, 1.4, 3.9, 2.9, 1.9, 1.1, 1.15, 2.3),
    (17.0, 3.1, 2.1, 1.4, 4.5, 3.4, 2.3, 1.3, 1.15, 2.3),
    (19.0, 3.0, 2.1, 1.4, 4.9, 3.7, 2.5, 1.4, 1.15, 2.3),
    (20.5, 3.0, 2.1, 1.4, 5.0, 3.7, 2.5, 1.4, 1.15, 2.3),
    (22.0, 3.0, 2.0, 1.3, 5.0, 3.2, 2.3, 1.3, 1.15, 2.25),
    (23.0, 2.8, 1.9, 1.3, 4.7, 2.6, 2.0, 1.2, 1.1, 2.1),
    (24.0, 2.4, 1.6, 1.1, 4.2, 2.0, 1.6, 0.9, 1.0, 1.8),
    (25.0, 1.8, 1.2, 0.8, 3.5, 1.3, 1.0, 0.6, 0.8, 1.3),
    (25.6, 1.2, 0.8, 0.6, 3.0, 0.7, 0.5, 0.3, 0.6, 0.9),
    (26.2, 0.5, 0.4, 0.3, 2.6, 0.0, 0.0, 0.0, 0.3, 0.4),
]

RIB_ROWS = (19.4, 20.5, 21.6)  # the light bands across the spine near the tail


def section(y, bw, bt, bb, px, pw, pt, pb, sw, st, creases=None):
    lobes = [
        (0, 0, bw, bt, bb),           # fuselage
        (-px, POD_Z, pw, pt, pb),     # pods
        (px, POD_Z, pw, pt, pb),
        (0, SPINE_Z, sw, st, 0.3),    # spine
    ]
    return k.lobed_ring(y, lobes, segments=72, origin_z=0.1, creases=creases)


def spine_at(row):
    """Spine half-width and top height (z) at a sprite row, as the profile has it."""
    for (r0, *a), (r1, *b) in zip(ROWS, ROWS[1:]):
        if r0 <= row <= r1:
            t = (row - r0) / (r1 - r0)
            sw = a[7] + (b[7] - a[7]) * t
            st = a[8] + (b[8] - a[8]) * t
            return sw, SPINE_Z + st
    return 0.0, 0.0


def build():
    k.reset()

    hull = k.material("talon_hull", palette=25, metallic=0.35, roughness=0.24)
    seam = k.material("talon_seam", palette=19, metallic=0.2, roughness=0.6)
    band = k.material("talon_band", palette=28, metallic=0.35, roughness=0.2)
    canopy = k.material("talon_canopy", palette=16, roughness=0.05)
    nozzle = k.material("talon_nozzle", palette=20, metallic=0.4, roughness=0.35)
    flame = k.material("talon_exhaust", (255, 170, 70), roughness=0.4, emission=(255, 140, 40), emission_strength=2.5)

    samples = k.profile(sorted([(row_y(r[0]), *r[1:]) for r in ROWS]), step=0.3)
    creases = [[] for _ in samples]
    rings = [section(*s, creases=c) for s, c in zip(samples, creases)]
    body = k.loft("hull", rings, hull, start_point=(0, row_y(26.5), 0.1), end_point=(0, row_y(1.5), 0.15))
    k.smooth(body, 45)
    k.crease_seams("seam", creases, seam)  # the grooves between the fuselage, the pods and the spine

    # The light bands across the spine near the tail: slightly raised strips with rounded tops.
    for i, row in enumerate(RIB_ROWS):
        sw, top = spine_at(row)
        rib = k.lathe(f"band{i}", [(-sw - 0.3, 0.0), (-sw - 0.25, 0.3), (sw + 0.25, 0.3), (sw + 0.3, 0.0)],
                      band, segments=12, axis_z=top - 0.1, squash=0.6)
        # (lathe turns around Y; the band runs across the ship, along X)
        rib.data.transform(k.Matrix.Translation((0, row_y(row), 0)) @ k.Matrix.Rotation(k.math.radians(90), 4, "Z"))
        k.smooth(rib, 60)

    # Canopy: a glossy dark glass dome in the front third.
    k.smooth(k.ellipsoid("canopy", (0, row_y(10.3), 1.75), (1.55, 1.8, 0.9), canopy, segments=20, rings_count=12), 60)

    # Engine nozzles at the rear of the pods, with a faint glow inside.
    for side in (-1, 1):
        x = side * 3.0
        noz = k.lathe(f"nozzle{side}", [(row_y(26.5), 0.8), (row_y(26.0), 0.72), (row_y(25.0), 0.55)],
                      nozzle, segments=16, axis_x=x, axis_z=0.45)
        k.smooth(noz, 60)
        glow = k.ellipsoid(f"exhaust{side}", (x, row_y(26.45), 0.45), (0.55, 0.15, 0.55), flame, segments=12,
                           rings_count=6)
        k.smooth(glow, 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "talon.glb"))


build()
