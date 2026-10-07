"""Gencore Phoenix (ships 3 and 4; sprite 157 of the ships sheet).

A slim fuselage with a canopy behind its pointed nose, flanked by two long engine nacelles that
widen towards the rear, joined to it by a short wing near the back. Dark grey metal.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402


def row_y(row):
    return 14 - (row + 0.5)


def col_x(col):
    return col + 0.5 - 12


def build():
    k.reset()
    body = k.material("phoenix_body", (93, 93, 93), metallic=0.3, roughness=0.35)
    dark = k.material("phoenix_dark", (40, 40, 40), metallic=0.3, roughness=0.45)
    canopy = k.material("phoenix_canopy", (24, 24, 30), roughness=0.15)

    # Fuselage: (row, half-width, top, bottom).
    rows = [(25.3, 1.2, 0.7, 0.5), (24.5, 2.6, 1.3, 0.9), (23, 4.2, 1.9, 1.2), (21, 4.8, 2.1, 1.3),
            (18, 4.3, 2.1, 1.3), (16, 4.6, 2.2, 1.4), (11, 4.9, 2.2, 1.4), (9, 4.5, 2.1, 1.3), (7, 3.9, 1.9, 1.1),
            (5, 3.0, 1.6, 0.9), (3, 2.0, 1.2, 0.6), (1.6, 1.0, 0.6, 0.4)]
    rows.sort(key=lambda r: row_y(r[0]))
    samples = k.profile([(row_y(r), w, t, b) for r, w, t, b in rows], step=0.4)
    fuselage = k.loft("fuselage", [k.ring(y, w, 1.0, 20, top=t, bottom=b) for y, w, t, b in samples], body,
                      start_point=(0, row_y(25.7), 0.1), end_point=(0, row_y(1.0), 0.2))
    k.smooth(fuselage, 55)
    k.smooth(k.ellipsoid("canopy", (0, row_y(7.4), 1.65), (1.3, 1.5, 0.75), canopy, 16, 10), 60)
    # Dark bands across the fuselage (the sprite's rows 9 and 13) and a darker engine block behind.
    for r, w, t, b in ((9.2, 4.6, 2.18, 1.38), (13.2, 5.0, 2.28, 1.48)):
        band = [k.ring(row_y(r) + d, w, 1.0, 20, top=t, bottom=b) for d in (-0.3, 0.3)]
        k.smooth(k.loft("band", band, dark), 55)
    engine = [(25.4, 0.0), (24.6, 1.6), (23.5, 2.6), (21.5, 2.9), (20.5, 2.6)]
    engine.sort(key=lambda r: row_y(r[0]))
    k.smooth(k.lathe("engine", [(row_y(r), w) for r, w in engine], dark, 16, axis_z=0.0, squash=0.75), 55)

    # Right nacelle: (row, half-width, centre x); its outer edge follows the silhouette.
    nacelle = [(24.6, 0.8, 7.6), (23.5, 1.6, 8.0), (21, 2.3, 8.6), (17, 2.4, 8.8), (14, 2.3, 8.6),
               (11.5, 1.6, 8.0), (9.4, 0.7, 7.6)]
    nacelle.sort(key=lambda r: row_y(r[0]))
    n_samples = k.profile([(row_y(r), w, c) for r, w, c in nacelle], step=0.4)
    right = k.loft("nacelle_right", [k.ring(y, w, w * 0.8, 16, x=c, z=0.2, power=3) for y, w, c in n_samples], body,
                   start_point=(7.6, row_y(25.0), 0.2), end_point=(7.5, row_y(9.0), 0.3))
    k.smooth(right, 55)
    k.smooth(k.mirror_x(right, "nacelle_left"), 55)

    # Wing joining nacelles and fuselage at the back.
    wing = [(4.0, row_y(22.2)), (7.4, row_y(22.2)), (7.4, row_y(18.6)), (4.0, row_y(19.4))]
    k.slab("wing_right", wing, -0.3, 0.6, body, bevel_width=0.25)
    k.mirror_x(bpy_obj := k.slab("wing_left_src", wing, -0.3, 0.6, body, bevel_width=0.25), "wing_left")
    import bpy
    bpy.data.objects.remove(bpy_obj)

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "ships", "phoenix.glb"))


build()
