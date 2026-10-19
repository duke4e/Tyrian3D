"""APPROACH's tan fighter (sheet 5 sprite 49, 2x2: 24 x 28 pixels; not animated; enemy 731, sky, about
60 of them), polished (2026-10-19; it replaces wave3_l.py's tan_fighter(), a lathed body with slab
wings). models.cfg: sprite 5 49 tan_fighter yaw=0 (the model faces the way the sprite does, nose down
the screen; the game centres sky objects in height). No other enemy uses 5 49.

As the 4x upscale draws it, nose down the screen, all in the sprite's tan ramp (ramp 1) but for two grey
rails: a round fuselage (columns 10-14) from a thin tail spike (column 12 of rows 1-3) to the wing roots,
lit along its left (column 11); two leaf-shaped tail planes swept back from its rear (their tips at
columns 6-8 and 16-18 of row 1); broad wings (rows 6-12) with a straight trailing edge along row 6
and leading edges swept back from the roots (row 12) to the squared tips (columns 1 and 23 of rows 7-9);
under each wing tip a grey rail, a gun barrel showing in front of and behind it (columns 3 and 21 of rows
5-11); in front of the wings a glossy dome (rows 13-16, its highlight at column 11 of row 14); the cockpit on
the nose in front of it, a small round canopy of dark glass in a tan frame (columns 11-13 of rows 17-19,
its glint the sprite's light middle); canards like a star's points either side of it (rows 17-19, their
tips at columns 5 and 19); and the nose cone (rows 20-26).

Built as a real aircraft with polish_jets.py's parts: a lofted round fuselage, thin wings, canards and
tail planes lofted from airfoil sections (a little thickness and dihedral), the dome and the cockpit
bubbles, the gun barrels lathed on pylons under the wing tips. The sprite's dark outline is not geometry: the plans reach about two thirds into the outline
pixels, so that the silhouette matches the sprite's.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen (sprite row r is y = 13.5 -
r), +Z towards the camera; origin at the sprite's centre (pixel 12, 14). The sprite is symmetric about
its column 12: the fighter is built about x = 0 (u below) and moved onto that column (AXIS).

Replaces wave3_l.py's tan_fighter() (and wave3_l_art.py's TAN_FIGHTER, which only it reads): remove
them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_5.png), --preview <prefix> (top and 3/4 views).
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_jets import (Plan, bubble, fuselage, hull_seam, hull_top, lifting_surface, mirrored, preview,  # noqa: E402
                         triangles)

AXIS = 0.5
SPRITE = 49

# The fuselage, from the nose's point (row 26) to the tail spike's (row 0): y, half-width, centre z, top,
# bottom (the half-widths cover the outline pixels about two thirds: columns 10-14 are 3.1 either side).
FUSELAGE = [(-12.2, 0.05, -0.3, 0.05, 0.05), (-11.75, 0.55, -0.27, 0.45, 0.38), (-11.05, 0.98, -0.22, 0.8, 0.6),
            (-10.3, 1.4, -0.17, 1.1, 0.8), (-9.4, 1.92, -0.11, 1.45, 1.0), (-8.4, 2.18, -0.06, 1.65, 1.12),
            (-7.4, 2.4, -0.02, 1.85, 1.22), (-6.4, 2.85, 0.02, 2.05, 1.32), (-5.2, 3.05, 0.05, 2.15, 1.4),
            (-3.6, 3.05, 0.1, 2.25, 1.48), (-1.5, 3.0, 0.1, 2.3, 1.5),
            (0.5, 3.05, 0.1, 2.35, 1.5), (3.0, 3.12, 0.1, 2.35, 1.5), (6.0, 3.1, 0.1, 2.25, 1.45),
            (8.3, 2.95, 0.1, 2.1, 1.38), (9.6, 2.6, 0.12, 1.85, 1.22), (10.5, 1.85, 0.15, 1.35, 0.95),
            (11.2, 1.05, 0.18, 0.85, 0.66), (11.9, 0.8, 0.2, 0.7, 0.55), (12.8, 0.66, 0.2, 0.58, 0.46),
            (13.45, 0.36, 0.2, 0.32, 0.26), (13.7, 0.05, 0.2, 0.05, 0.05)]
SEAMS = (0.65, -3.15)            # panel lines round it: before the dome (row 13), behind it (row 16)
# The dome (rows 13-16, glossy, its highlight at column 11 of row 14): y, half-width, height above the
# fuselage's top.
DOME = [(-3.05, 0.0, 0.0), (-2.7, 1.5, 0.7), (-2.0, 2.3, 1.25), (-1.1, 2.55, 1.5), (-0.2, 2.4, 1.38),
        (0.4, 1.8, 1.0), (0.8, 0.0, 0.0)]
# The cockpit on the nose (rows 17-19): dark glass, its glint the sprite's light middle, in a frame.
GLASS = [(-3.45, 0.0, 0.0), (-3.75, 0.95, 0.55), (-4.3, 1.4, 0.88), (-4.95, 1.48, 0.92), (-5.55, 1.2, 0.72),
         (-5.95, 0.7, 0.4), (-6.15, 0.0, 0.0)]
FRAME = [(-3.15, 0.0, 0.0), (-3.45, 1.4, 0.25), (-4.2, 1.95, 0.35), (-5.1, 2.0, 0.36), (-5.9, 1.6, 0.3),
         (-6.35, 1.0, 0.22), (-6.6, 0.0, 0.0)]
# The wing (left): the trailing edge along row 6, the leading edge y = 0.33 - 0.571 (u + 3) fitted to the
# sprite's staircase (rows 9-12), the tip squared off (column 1 of rows 6-9).
WING = [(-1.2, -0.45), (-3.0, 0.33), (-6.5, 2.33), (-10.0, 4.33), (-10.75, 4.7), (-11.12, 5.5), (-11.15, 6.9),
        (-10.85, 7.55), (-10.1, 7.67), (-1.2, 7.67)]
# The canard (left): its trailing edge along row 17, its point at column 5, its leading edge back to the
# nose (rows 19-20).
CANARD = [(-1.6, -3.3), (-4.6, -3.33), (-6.2, -3.55), (-7.0, -3.95), (-7.38, -4.3), (-6.95, -4.65), (-5.4, -5.55),
          (-3.9, -6.4), (-1.6, -6.95)]
# The gun barrels under the wing tips (columns 3 and 21 of rows 5-11): u, y from its muzzle to its back,
# radius, the height of its axis.
GUN = (-9.0, (1.35, 9.7), 0.92, -0.7)
# The tail planes (left): leaf-shaped, swept back from the fuselage's rear (rows 2-4) to their pointed
# tips (columns 5-8 of rows 0-2), with a little dihedral.
TAIL = [(-1.2, 9.2), (-4.0, 9.3), (-5.2, 10.4), (-6.3, 11.55), (-7.25, 13.2), (-6.9, 13.6), (-5.8, 13.68),
        (-4.3, 13.55), (-2.85, 12.5), (-1.9, 11.55), (-1.2, 11.3)]
TAIL_ROOT_Z, TAIL_DIHEDRAL = 0.75, 0.13


def materials():
    return {
        "body": k.material("tanfighter_body", palette=0x18, metallic=0.45, roughness=0.32),
        "wing": k.material("tanfighter_wing", palette=0x17, metallic=0.45, roughness=0.36),
        "dome": k.material("tanfighter_dome", palette=0x19, metallic=0.55, roughness=0.1),
        "seam": k.material("tanfighter_seam", palette=0x13, metallic=0.3, roughness=0.55),
        "frame": k.material("tanfighter_frame", palette=0x15, metallic=0.4, roughness=0.35),
        "glass": k.material("tanfighter_glass", palette=0x11, metallic=0.0, roughness=0.15),
        "gun": k.material("tanfighter_gun", palette=0x08, metallic=0.6, roughness=0.28),
        "bore": k.material("tanfighter_bore", palette=0x03, metallic=0.2, roughness=0.6),
    }


def build_fighter(m):
    _, curve = fuselage("fuselage", FUSELAGE, m["body"], step=0.38, segments=28)
    top = hull_top(curve)
    for i, y in enumerate(SEAMS):
        hull_seam(f"seam{i}", curve, y, m["seam"], radius=0.13)
    bubble("dome", DOME, lambda y: top(0.0, y), m["dome"], segments=24, sink=0.45)

    # The cockpit on the nose, in its frame.
    bubble("frame", FRAME, lambda y: top(0.0, y), m["frame"], segments=20, sink=0.4)
    bubble("glass", GLASS, lambda y: top(0.0, y) + 0.22, m["glass"], segments=20, sink=0.4)

    # The wings: thin, a little dihedral, thinner towards the tips.
    plan = Plan(WING, rounding=2)

    def wing_mid(u):
        return 0.05 + 0.05 * max(0.0, -u - 2.5)

    def wing_thick(u):
        return min(0.72, max(0.18, 0.1 * plan.chord(u)))

    us = plan.stations(22)
    mirrored(lifting_surface("wing_l", us, plan, wing_mid, wing_thick, m["wing"], under=0.55, tip=plan.tip))

    # The canards: pointed darts either side of the cockpit.
    cplan = Plan(CANARD, rounding=1)

    def canard_mid(u):
        return 0.1 + 0.03 * max(0.0, -u - 2.0)

    us = cplan.stations(14)
    mirrored(lifting_surface("canard_l", us, cplan, canard_mid, lambda u: min(0.42, max(0.1, 0.13 * cplan.chord(u))),
                             m["wing"], under=0.6, tip=cplan.tip))

    # The gun barrels under the wing tips: a rounded breech, the barrel, a collar and the muzzle.
    u, (y0, y1), r, zc = GUN
    profile = [(y0, 0.0), (y0, r * 0.62), (y0 + 0.12, r * 0.74), (y0 + 0.5, r * 0.74), (y0 + 0.62, r * 0.9),
               (y0 + 1.25, r * 0.9), (y0 + 1.4, r * 0.8), (y1 - 1.8, r), (y1 - 0.8, r * 0.96), (y1 - 0.3, r * 0.75),
               (y1, 0.0)]
    gun = k.lathe("gun_l", profile, m["gun"], 16, axis_x=u, axis_z=zc)
    k.smooth(gun, 50)
    bore = k.lathe("gun_bore_l", [(y0 - 0.02, 0.0), (y0 - 0.02, r * 0.45), (y0 + 0.4, r * 0.45), (y0 + 0.4, 0.0)],
                   m["bore"], 12, axis_x=u, axis_z=zc)
    # The pylon joining it to the wing.
    pylon = k.loft("gun_pylon_l", [k.ring(y, 0.28, 0.5, 8, z=zc + r * 0.75, x=u) for y in (y0 + 2.6, y1 - 1.6)],
                   m["gun"])
    k.smooth(pylon, 50)
    for part in (gun, bore, pylon):
        mirrored(part)

    # The tail planes on the fuselage's rear.
    tplan = Plan(TAIL, rounding=1)
    us = tplan.stations(16)
    mirrored(lifting_surface("tail_l", us, tplan, lambda u: TAIL_ROOT_Z + TAIL_DIHEDRAL * max(0.0, -u - 1.5),
                             lambda u: min(0.4, max(0.12, 0.11 * tplan.chord(u))), m["body"], under=0.6,
                             tip=tplan.tip))


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    m = materials()
    build_fighter(m)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS, 0, 0)))
    used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
    print("== tan_fighter (5 %d): %d triangles, %d materials: %s" % (SPRITE, triangles(), len(used),
                                                                     ", ".join(sorted(used))))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_5.png"), SPRITE)
    path = os.path.join(outdir, "tan_fighter.glb")
    k.export(path)
    print("   tan_fighter: %.1f KB" % (os.path.getsize(path) / 1024))
    if "preview" in options:
        preview(options["preview"] + "tan_fighter")


if __name__ == "__main__":
    build()
