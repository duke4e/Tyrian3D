"""What is left of CAMANIS' ice drill once it is destroyed (sheet 7 sprite 169, the red hood, and 207, its arm: their
stand-ins, what the ice maps paint where the drill stands, before it comes, once it is shot and where none comes; the
hood 13 times in CAMANIS 89e6d1810ded7622 and DEEP ICE a15166868146cdd3, the arm 11 times in CAMANIS), stage 4 of the
clean ground (2026-10-25), built on polish_ice_drill.py. models.cfg: model ice_drill_dome_wreck / ice_drill_arm_wreck
enemies/ice_drill_dome_wreck.glb / ice_drill_arm_wreck.glb origin; wreck 7 169 ice_drill_dome_wreck, wreck 7 207
ice_drill_arm_wreck (drawn with the live sprite lines' options, yaw=0 height=-4).

As the maps paint it at 4x (CAMANIS at 516, 4873; columns and rows of the 24 x 56 picture): the red hood (columns 1-20
of rows 0-26) still standing, hot: its red brighter than the live one's (0x73-0x7b, glints 0x7c-0x7e at its upper left
and a hot spot on its right, columns 16-18 of rows 6-8), dark cracks across its back (row 5, columns 9-16; column 7,
rows 2-4); its front blown open wider, black (0x02) from row 9 down, the fork gone: light grey splinters lying in the
black (columns 8, 11-13 of rows 13-16; column 12, rows 20-22; column 10, row 25); the inner fingers gone, the outer ones
standing (columns 2-4 of rows 6-17), a broken red finger lying at the lower left (columns 5-8 of rows 21-25); the collar
under it charred black. Under the hood (the arm's sprite, rows 28-55) only the plateau's ice: the arm is gone.

The model: polish_ice_drill.py's hood (its opening cut wider and lower, OPENING), its outer fingers, its piston block
and its collar, the arm's other parts left out; the hood's and the fingers' reds a shade hotter, glowing a little more
(0x73-0x7c, emission 0.08-0.2, the hot spot 0x7a at 0.35), the cracks cut into the shell as dark grooves (0x70: exact
booleans with thin tubes along the shell); the collar, the piston block and the cavity charred dull (0x02, 0x01); the
fork's prongs bent and snapped (light grey bars, 0x0c and 0x0a) and splinters (thin plates) in the opening; the broken
inner finger lying at the lower left (a red tube, its ends torn); the rod snapped a pixel under the collar, which is all
the arm's piece holds (the painting shows the ice there: the arm wreck is that stub only). Cut along the sprites' edge
as the live drill (polish_coral_manta.cut, the caps dark), its parts joined.

Coordinates as polish_ice_drill.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ice; the whole's
origin is the edge between the two sprites; XE(c), YE(r) the picture's column and row edges.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_ice_drill as live  # noqa: E402
from polish_jaw_gun_wreck import bent_bar, shard  # noqa: E402
from polish_pyramid_wreck import canonical  # noqa: E402

XE, YE, AX = live.XE, live.YE, live.AX
PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES]
OPENING = (8.4, 8.2, 27.0)     # the blown front: half-width, from row, down to row
# The hotter reds: (live key, palette, emission).
HOT = {"red_under": (0x73, 0.08), "red_side": (0x76, 0.12), "red": (0x78, 0.15), "red_lit": (0x7a, 0.17),
       "glint": (0x7c, 0.2)}
# The cracks across the hood's back: picture points (column, row), the groove's radius.
CRACKS = [([(9.0, 5.4), (11.0, 5.8), (13.2, 5.6), (15.6, 5.9)], 0.42), ([(7.4, 1.4), (7.6, 3.0), (7.3, 4.8)], 0.36),
          ([(9.6, 2.2), (10.8, 3.4)], 0.3), ([(3.4, 6.2), (5.4, 7.8), (8.0, 9.0)], 0.34)]
HOTSPOT = ((17.0, 7.0), (1.4, 1.2))     # the glowing patch on the hood's right: picture point, radii
# The fork's broken prongs (bars: picture points with heights) and splinters (picture points, tilt).
PRONGS = [[(8.6, 13.0, 5.0), (8.8, 15.0, 3.8), (7.6, 16.6, 2.0)], [(13.4, 13.4, 4.6), (12.4, 15.2, 3.4)],
          [(12.2, 19.6, 1.6), (12.4, 21.8, 1.0)]]
SPLINTERS = [([(10.4, 15.0), (12.6, 15.4), (11.6, 16.6)], (14.0, -8.0)), ([(9.4, 24.4), (10.8, 24.6), (10.2, 25.6)],
                                                                         (-6.0, 10.0)),
             ([(13.0, 12.6), (14.0, 13.2), (13.2, 14.4)], (8.0, 18.0))]
FINGER = [(5.4, 21.0, 1.4, 1.1), (6.4, 22.6, 1.0, 1.0), (7.4, 24.2, 0.8, 0.8), (7.8, 25.2, 0.7, 0.55)]
ROD_STUB = 29.2                 # the rod snapped at this row (a pixel into the arm's sprite)


def P(c, r, z=0.0):
    """The picture's point (column c, row r: pixel corners) at height z."""
    return Vector((XE(c), YE(r), z))


def materials():
    m = live.materials()
    pal = k.level_palette()
    for key, (index, glow) in HOT.items():
        m["hot_" + key] = k.material("idrillwreck_" + key, palette=index, metallic=0.3, roughness=0.3,
                                     emission=pal[index], emission_strength=glow)
    m["crack"] = k.material("idrillwreck_crack", palette=0x70, metallic=0.2, roughness=0.6)
    m["char"] = k.material("idrillwreck_char", palette=0x01, metallic=0.1, roughness=0.88)
    m["soot"] = k.material("idrillwreck_soot", palette=0x02, metallic=0.1, roughness=0.85)
    m["ember"] = k.material("idrillwreck_ember", palette=0x7a, metallic=0.0, roughness=0.4, emission=pal[0x7a],
                            emission_strength=0.35)
    return m


def heat(obj, m):
    """The reds a shade hotter (the materials swapped)."""
    swap = {m[key].name: m["hot_" + key] for key in HOT}
    for i, mat in enumerate(obj.data.materials):
        if mat is not None and mat.name in swap:
            obj.data.materials[i] = swap[mat.name]


def surface_points(hit, pts):
    out = []
    for c, r in pts:
        p = P(c, r)
        h = hit(p.x, p.y)
        if h is not None:
            out.append(h[0])
    return out


def build_whole():
    m = materials()
    live.OPENING = OPENING
    shell, cavity, lamp = live.hood(m)
    left = live.fingers(m)
    outer = [left[0]] + live.mirror([left[0]])
    for obj in left[1:]:
        bpy.data.objects.remove(obj)
    fork = live.fork(m)
    for obj in fork[1:]:                     # (the prongs and the pin: broken, below)
        bpy.data.objects.remove(obj)
    piston = fork[0]
    arm = live.arm(m)
    collar, rod = arm[0], arm[1]
    for obj in arm[2:]:
        bpy.data.objects.remove(obj)
    for obj in [shell, cavity, lamp, piston, collar, rod] + outer:
        mk.apply(obj)
    # The rod snapped under the collar.
    stub = mk.box("rod_cut", AX - 4.0, AX + 4.0, -40.0, YE(ROD_STUB), -2.0, 12.0, m["dark"])
    mk.boolean(rod, stub, "DIFFERENCE")
    mk.paint(rod, lambda c, n: m["soot"] if c.y < YE(ROD_STUB) + 0.6 else None)
    # The collar and the piston charred (dull: the live dark steel reads grey from the camera), the reds hotter.
    mk.paint(collar, lambda c, n: m["char"] if n.z < 0.5 else m["soot"])
    mk.paint(piston, lambda c, n: m["char"])
    mk.paint(cavity, lambda c, n: m["char"])
    mk.paint(lamp, lambda c, n: m["hot_red_side"])
    for obj in [shell] + outer:
        heat(obj, m)
    # The cracks: thin tubes along the shell cut out of it (dark grooves).
    hit = mk.surface([shell])
    for i, (line, radius) in enumerate(CRACKS):
        pts = surface_points(hit, line)
        if len(pts) >= 2:
            tube = mk.tube(f"crack{i}", pts, radius, m["crack"], 8)
            mk.boolean(shell, tube, "DIFFERENCE")
    mk.cleanup(shell, dissolve=0.0)
    canonical(shell)
    k.smooth(shell, 60)
    # The hot spot on its right.
    (c, r), (rx, ry) = HOTSPOT
    p = P(c, r)
    h = hit(p.x, p.y)
    if h is not None:
        spot = mk.ball("hotspot", tuple(h[0] + Vector((0.0, 0.0, -0.35))), (rx, ry, 0.55), m["ember"], 16, 8)
        k.smooth(spot, 70)
    # The fork's bent prongs, splinters in the opening, the broken inner finger at the lower left.
    for i, pts in enumerate(PRONGS):
        bent_bar(f"prong{i}", [tuple(P(c, r, z)) for c, r, z in pts], 0.6, m["hi"] if i != 2 else m["lit"])
    for i, (outline, tilt) in enumerate(SPLINTERS):
        shard(f"splinter{i}", [tuple(P(c, r))[:2] for c, r in outline], 0.6, 0.25, m["hi"], tilt)
    finger = mk.smooth_tube("finger_broken", [(XE(c), YE(r), z, rad) for c, r, z, rad in FINGER], m["hot_red"], 10, 2)
    k.smooth(finger, 60)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    swap = {m["black"].name: m["char"], m["dark"].name: m["soot"]}   # (the live darks read grey: dull ones)
    for obj in whole:
        mk.apply(obj)
        for i, mat in enumerate(obj.data.materials):
            if mat is not None and mat.name in swap:
                obj.data.materials[i] = swap[mat.name]
    m["dark"] = m["soot"]                                             # (the cuts' caps)
    live.triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    whole, m = build_whole()
    print("whole drill wreck: %d triangles" % mk.triangles(whole))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "ice_drill_wreck_whole", whole, size=(24, 56), scale=12, distance=1.6)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        live.export_piece(whole, m, name, sprite, box, options, None)


if __name__ == "__main__":
    build()
