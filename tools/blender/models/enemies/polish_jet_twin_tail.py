"""SAVARA's green jet with twin tails (sheet F sprite 55, 2x2: 24 x 28 pixels; not animated; enemy 168:
sky in episode 1's and episode 5's SAVARA, and on the ground2 layer in episode 5's, where formations sit on
the ground before they take off), polished (2026-10-19; it replaces wave3_s.py's jet_twin_tail(), a
painted plate with a lathed body). models.cfg: sprite f 55 jet_twin_tail yaw=0 (the model faces the way
the sprite does, nose down the screen; the game centres it in height, lifting it clear of the ground).
No other enemy uses F 55.

As the 4x upscale draws it, nose down the screen: a round green fuselage (the sprite's ramp 2) from the
pointed nose (row 24) to the tail, lit along its left (column 10), a big round cockpit of dark glass
over the wing roots' front (columns 11-14 of rows 16-19, a light glint at its top left); delta wings
whose trailing edge runs straight along row 10 and whose leading edges run at 45 degrees from the
cropped tips (columns 3-4 and 21-22 of rows 11-12) down to the cockpit, banded in brown along them (the
sprite's ramp 1, two pixels wide); two blue lights on the wing roots (columns 10 and 15 of row 12); brown
tail planes swept back behind the wings (rows 4-8); a brown nozzle at the tail (columns 11-14 of rows
4-6); and twin fins standing over it, seen nearly edge on (columns 10 and 15 of rows 1-6), reaching past it.

Built as a real aircraft with polish_jets.py's parts: a lofted round fuselage, thin wings and tail
planes lofted from airfoil sections (a little thickness and dihedral), the wings' leading edges painted
brown along the sections, upright fins, a bubble cockpit in its frame, a nozzle, lamps. The sprite's
dark outline is not geometry: the plans reach about two thirds into the outline pixels, so that the
silhouette matches the sprite's.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen (sprite row r is y = 13.5 -
r), +Z towards the camera; origin at the sprite's centre (pixel 12, 14). The sprite is symmetric about
the edge between its columns 12 and 13: the jet is built about x = 0 (u below) and moved there (AXIS).

Replaces wave3_s.py's jet_twin_tail() (with J55 and J55_PAINT; wave3_s_art.py's JET55, which only they
read): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_F.png), --preview <prefix> (top and 3/4 views).
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_jets import (Curve, Plan, bubble, fuselage, hull_top, lamp, lifting_surface, mirrored, nozzle,  # noqa: E402
                         preview, tip_planform, to_fin, triangles)

AXIS = 1.0
SPRITE = 55

# The fuselage, from the nose's point (row 25) to the nozzle (row 6): y, half-width, centre z, top, bottom.
FUSELAGE = [(-11.75, 0.05, -0.3, 0.05, 0.05), (-11.35, 0.72, -0.27, 0.55, 0.42), (-10.7, 1.3, -0.22, 0.95, 0.68),
            (-9.8, 1.72, -0.16, 1.28, 0.88), (-8.9, 2.2, -0.1, 1.58, 1.04), (-7.8, 2.62, -0.05, 1.85, 1.18),
            (-6.8, 3.1, 0.0, 2.05, 1.3), (-5.6, 3.42, 0.0, 2.2, 1.38), (-4.4, 3.48, 0.0, 2.28, 1.4),
            (-3.0, 3.38, 0.0, 2.28, 1.4), (-1.5, 3.2, 0.0, 2.25, 1.38), (0.5, 3.02, 0.0, 2.15, 1.32),
            (2.5, 2.85, 0.0, 2.0, 1.25), (4.5, 2.6, 0.0, 1.85, 1.18), (6.0, 2.35, 0.02, 1.7, 1.1),
            (7.3, 2.1, 0.05, 1.55, 1.02), (8.2, 1.95, 0.06, 1.45, 0.96)]
NOZZLE = (7.9, 10.6, 1.78)      # from inside the fuselage to its mouth (row 3), radius
# The cockpit (rows 16-19): dark glass in a dark green frame; y, half-width, height over the fuselage.
GLASS = [(-6.05, 0.0, 0.0), (-5.75, 1.15, 0.7), (-5.2, 1.72, 1.15), (-4.4, 1.95, 1.4), (-3.5, 1.9, 1.38),
         (-2.7, 1.55, 1.08), (-2.15, 0.95, 0.62), (-1.95, 0.0, 0.0)]
FRAME = [(-6.45, 0.0, 0.0), (-6.1, 1.5, 0.3), (-5.3, 2.25, 0.42), (-4.2, 2.45, 0.46), (-3.1, 2.35, 0.45),
         (-2.1, 1.85, 0.38), (-1.55, 1.1, 0.28), (-1.3, 0.0, 0.0)]
# The wing (left): the trailing edge along row 10, the leading edge u + y = -8.25 (the sprite's 45-degree
# staircase, rows 12-18), the tip cropped (column 3 of rows 10-12).
WING = [(0.0, -8.25), (-2.6, -5.65), (-9.0, 0.75), (-9.55, 1.45), (-9.72, 2.3), (-9.7, 3.3), (-9.45, 3.67),
        (0.0, 3.67)]
BAND = 2.2                       # the brown band along the leading edge: its width (y)
# The tail planes (left, brown): the trailing edge along row 4, the leading edge u + y = 0.75 (rows 7-9),
# the tip at column 6.
TAIL = [(-0.6, 1.35), (-2.4, 3.15), (-6.45, 7.2), (-6.67, 7.8), (-6.67, 9.0), (-6.35, 9.6), (-5.6, 9.67),
        (-0.6, 9.67)]
# The fins (columns 10 and 15 of rows 1-6): on the tail planes' roots, swept, leaning out a little
# (FIN_CANT degrees); along their span (0 at the root, FIN_SPAN at the top) their leading and trailing
# edges.
FIN_X, FIN_Z, FIN_SPAN, FIN_CANT = -2.3, 0.85, 3.9, 12.0
FIN_LE = Curve([(0.0, 5.6), (-2.0, 8.6), (-3.9, 11.4)])
FIN_TE = Curve([(0.0, 10.4), (-2.0, 12.4), (-3.9, 13.65)])
LIGHT = (-2.5, 1.5)              # the blue lights on the wing roots (columns 10 and 15 of row 12)


def materials():
    glow = k.level_palette()
    return {
        "body": k.material("jettwin_body", palette=0x29, metallic=0.35, roughness=0.3),
        "wing": k.material("jettwin_wing", palette=0x28, metallic=0.35, roughness=0.34),
        "fin": k.material("jettwin_fin", palette=0x2a, metallic=0.35, roughness=0.3),
        "band": k.material("jettwin_band", palette=0x16, metallic=0.4, roughness=0.32),
        "tail": k.material("jettwin_tail", palette=0x17, metallic=0.4, roughness=0.32),
        "nozzle": k.material("jettwin_nozzle", palette=0x14, metallic=0.55, roughness=0.3),
        "dark": k.material("jettwin_dark", palette=0x20, metallic=0.2, roughness=0.7),
        "glass": k.material("jettwin_glass", palette=0x21, metallic=0.0, roughness=0.12),
        "frame": k.material("jettwin_frame", palette=0x23, metallic=0.35, roughness=0.35),
        "light": k.material("jettwin_light", palette=0x86, roughness=0.2, emission=glow[0x88],
                            emission_strength=2.0),
    }


def build_jet(m):
    _, curve = fuselage("fuselage", FUSELAGE, m["body"], step=0.38, segments=28)
    top = hull_top(curve)
    y0, y1, r = NOZZLE
    nozzle("nozzle", y0, y1, r, m["nozzle"], m["dark"], axis_z=curve(8.2)[1])

    # The cockpit in its frame.
    bubble("frame", FRAME, lambda y: top(0.0, y), m["frame"], segments=24, sink=0.4)
    bubble("glass", GLASS, lambda y: top(0.0, y) + 0.24, m["glass"], segments=24, sink=0.4)

    # The wings: brown along the leading edge.
    plan = Plan(WING, rounding=2)

    def band_border(u):
        return min(0.6, BAND / max(plan.chord(u), 1e-3))

    def paint(u, c0, c1, top_side):
        return 1 if c1 <= band_border(u) + 0.02 else 0

    def wing_mid(u):
        return -0.35 + 0.06 * max(0.0, -u - 2.5)

    def wing_thick(u):
        return min(0.7, max(0.14, 0.08 * plan.chord(u)))

    us = plan.stations(22)
    wing = lifting_surface("wing_l", us, plan, wing_mid, wing_thick, m["wing"], under=0.5, border=band_border,
                           ref=4, paint=paint, mats=(m["band"],), tip=plan.tip)
    mirrored(wing)

    # The brown tail planes.
    tplan = Plan(TAIL, rounding=2)
    us = tplan.stations(14)
    mirrored(lifting_surface("tail_l", us, tplan, lambda u: 0.35 + 0.05 * max(0.0, -u - 1.5),
                             lambda u: min(0.36, max(0.08, 0.08 * tplan.chord(u))), m["tail"], under=0.6,
                             tip=tplan.tip))

    # The twin fins on the tail planes' roots.
    def fin_plan(u):
        return tip_planform(u, FIN_LE, FIN_TE, -FIN_SPAN, 0.9, 0.3)

    us = [0.0, -0.5, -1.0, -1.5, -2.0, -2.5, -2.9, -3.25, -3.5, -3.7, -3.82, -3.88]
    fin = lifting_surface("fin_l", us, fin_plan, lambda u: 0.0, lambda u: 0.5 - 0.03 * (-u), m["fin"], under=1.0,
                          camber=0.0, tip=(-FIN_SPAN, 12.9))
    to_fin(fin, x=FIN_X, z=FIN_Z, cant=FIN_CANT)
    mirrored(fin)

    # The blue lights on the wing roots.
    u, y = LIGHT
    left = lamp("light_l", (u, y, top(u, y) - 0.25), (0.62, 0.72, 0.42), m["light"])
    mirrored(left)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    m = materials()
    build_jet(m)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS, 0, 0)))
    used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
    print("== jet_twin_tail (F %d): %d triangles, %d materials: %s" % (SPRITE, triangles(), len(used),
                                                                       ", ".join(sorted(used))))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_F.png"), SPRITE)
    path = os.path.join(outdir, "jet_twin_tail.glb")
    k.export(path)
    print("   jet_twin_tail: %.1f KB" % (os.path.getsize(path) / 1024))
    if "preview" in options:
        preview(options["preview"] + "jet_twin_tail")


if __name__ == "__main__":
    build()
