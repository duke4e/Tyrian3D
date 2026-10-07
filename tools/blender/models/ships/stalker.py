"""MicroCorp Stalker (ships 5-8 and 13; sprite 195 of the ships sheet).

A pointed fuselage with a ring-framed canopy, forward-swept wings whose tips reach up beside the
cockpit, red fittings at the wing roots and a red engine glowing at the tail. Grey metal.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    """Blender y of a sprite row coordinate (row 0 is the top edge of the sprite)."""
    return 14 - row


def col_x(col):
    """Blender x of a sprite column coordinate (column 0 is the left edge of the sprite)."""
    return col - 12


def build():
    k.reset()
    body = k.material("stalker_body", palette=8, metallic=0.3, roughness=0.35)
    light = k.material("stalker_light", palette=11, metallic=0.3, roughness=0.3)
    dark = k.material("stalker_dark", palette=3, metallic=0.3, roughness=0.45)
    red = k.material("stalker_red", palette=116, roughness=0.4)
    engine = k.material("stalker_engine", (90, 20, 0), roughness=0.5, emission=(255, 70, 20), emission_strength=3.0)
    canopy = k.material("stalker_canopy", palette=2, roughness=0.15)

    # Fuselage, centred on the sprite's column 11.5: (row at pixel centre, half-width, top, bottom).
    cx = col_x(11.5)
    rows = [(26.2, 0.8, 0.6, 0.4), (25.3, 1.9, 1.2, 0.8), (23.5, 3.0, 1.7, 1.1), (21, 3.6, 2.0, 1.3),
            (18, 3.9, 2.2, 1.4), (15, 3.3, 2.1, 1.3), (12, 4.0, 2.3, 1.4), (9.5, 4.6, 2.5, 1.5),
            (7, 4.2, 2.3, 1.4), (5, 3.3, 1.9, 1.1), (3, 2.4, 1.5, 0.8), (1.2, 1.2, 0.8, 0.5)]
    rows.sort(key=lambda r: row_y(r[0] + 0.5))
    samples = k.profile([(row_y(r + 0.5), w, t, b) for r, w, t, b in rows], step=0.4)
    fuselage = k.loft("fuselage", [k.ring(y, w, 1.0, 20, x=cx, top=t, bottom=b) for y, w, t, b in samples], body,
                      start_point=(cx, row_y(26.9), 0.1), end_point=(cx, row_y(0.2), 0.2))
    k.smooth(fuselage, 55)
    # Canopy in a dark ring.
    k.smooth(k.ellipsoid("canopy_ring", (cx, row_y(9.0), 1.6), (2.4, 2.3, 1.1), dark, 16, 10), 60)
    k.smooth(k.ellipsoid("canopy", (cx, row_y(9.0), 2.0), (1.4, 1.5, 0.9), canopy, 16, 10), 60)

    # Forward-swept wings, in sprite pixel-edge coordinates, counter-clockwise.
    wing = [(1, 10.7), (1, 18.6), (3.6, 20.6), (8.2, 20.6), (8.2, 15.4), (3.2, 10.7)]
    left = k.slab("wing_left", [(col_x(c), row_y(r)) for c, r in wing], -0.3, 0.7, body, bevel_width=0.3)
    right = k.mirror_x(left, "wing_right")
    right.data.transform(__import__("mathutils").Matrix.Translation((2 * cx, 0, 0)))
    # Light leading edges on the wing tips.
    tip = [(1, 10.7), (1, 15.5), (2.2, 15.5), (2.2, 10.7)]
    tip_left = k.slab("tip_left", [(col_x(c), row_y(r)) for c, r in tip], 0.0, 1.0, light, bevel_width=0.25)
    tip_right = k.mirror_x(tip_left, "tip_right")
    tip_right.data.transform(__import__("mathutils").Matrix.Translation((2 * cx, 0, 0)))

    # Red fittings at the wing roots.
    for x in (col_x(6.5), 2 * cx - col_x(6.5)):
        k.smooth(k.ellipsoid("fitting", (x, row_y(14.5), 0.9), (0.9, 1.6, 0.8), red, 12, 8), 60)

    # Tail fins and the engine.
    fin = [(5, 21), (5, 24.6), (7.6, 25.6), (8.4, 21.5)]
    fin_left = k.slab("fin_left", [(col_x(c), row_y(r)) for c, r in fin], -0.2, 0.9, body, bevel_width=0.25)
    fin_right = k.mirror_x(fin_left, "fin_right")
    fin_right.data.transform(__import__("mathutils").Matrix.Translation((2 * cx, 0, 0)))
    k.smooth(k.ellipsoid("engine", (cx, row_y(25.9), 0.3), (1.3, 0.9, 0.9), engine, 12, 8), 60)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "stalker.glb"))


build()
