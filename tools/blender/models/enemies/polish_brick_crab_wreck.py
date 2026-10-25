"""The wreck of UNDERDELI's red-clawed machine in the brick wall (sheet ^, x5e in models.cfg, sprites 157, 159 and 161
side by side: one 72 x 28 picture), stage 4 of the clean ground (2026-10-25): what UNDERDELI's map paints where the
crabs stand, which tools/terrain/make_cleanground.py erases and the game shows as stand-ins (models.cfg
"wreck x5e 159 brick_crab_mid_wreck" and so on, drawn with the live sprite lines' options: yaw=0 height=-4).

As the map paints it (UNDERDELI's tiles at 4x; whole coordinates as below): the same crab, broken. Its left end (the
hook and the grey ball) is painted as it is (make_cleanground shows the live left piece there: "own"), the dome and
its trident stand; the chin under the dome's front is gone, a dark pit in its place (x -5..5, y 3..-3) and the dome's
front lip broken into it; both red balls are cracked open, the left one on its lower right (its dark inside showing at
x -8..-5 y 2..5), the right one on its left and lower side; the right grey ball is cracked and dented, sunk lower; the
joints under the red balls are bent; the two small pincers have fallen flat, lying as a red U under the pit (from
(-10, -3) down to (-2, -7) and from (2, -7) up to (9, -3)); the right hook still hangs at its end. No glow in the
painting, so no embers either.

Built on polish_brick_crab.py: its whole crab (left half, mirrored, the dome with the trident), then broken: the chin
taken away and a dark pit of charred lumps laid where it was, bites taken out of the dome's front and the red balls
with exact booleans (their insides dark), the right grey ball cracked (two wedges cut out of it), dented and sunk, the
pincers flattened onto the wall, the right joint bent down; scorched round the pit and the right grey ball (faces cut
along the field's contours: polish_jaw_gun_wreck.scorch). Cut along x = -12 and 12 as the live crab (polish_arch.py's
cut()); the left piece is the live left piece but lightly scorched, so that the mid wreck meets the live left piece
(the stand-in the map's "own" places show) along x = -12 as well as its own.

Coordinates as in polish_brick_crab.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the wall (z = 0);
the whole's origin is the middle of the picture (the middle of 159).

models.cfg: model brick_crab_left_wreck enemies/brick_crab_left_wreck.glb origin (and _mid_, _right_);
wreck x5e 157 brick_crab_left_wreck, wreck x5e 159 brick_crab_mid_wreck, wreck x5e 161 brick_crab_right_wreck.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <file.glb>.
"""
import math
import os
import sys

import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402
import polish_brick_crab as bc  # noqa: E402
import polish_jaw_gun_wreck as wk  # noqa: E402  (the shared wreck helpers)

XE, YE = bc.XE, bc.YE
# The bites taken out of the parts: (part, centre (x, y, z), radius).
BITES = [("red_ball", (-5.9, 3.0, 5.0), 3.1), ("red_ball_r", (7.0, 2.6, 4.8), 3.4), ("dome", (0.5, -1.6, 0.9), 3.2)]
# The cracks in the right grey ball: wedges (x, y of the crack's line through it, its direction in degrees, width).
CRACKS = [(18.4, 2.6, 62.0, 0.75), (19.6, 3.0, -28.0, 0.6)]
GREY_R_DENT = ((16.0, 4.4, 4.9), 2.9)       # a bite in its top left (the dent)
GREY_R_SINK = (0.9, 10.0)                   # how far it sinks, how far it rolls (degrees, about y)
# The pincers fallen flat: bars lying on the wall as a U under the pit (the left one; the right one mirrored):
# path (x, y, z, radius), the heights then scaled by PINCER_FLAT.
PINCER_U = [(-9.9, -2.0, 1.5, 1.35), (-9.6, -4.4, 1.3, 1.45), (-8.2, -6.3, 1.2, 1.45), (-5.6, -7.1, 1.1, 1.4),
            (-2.8, -7.2, 1.0, 1.2)]
PINCER_FLAT = 0.55
JOINT_R_DROP = (-0.8, -16.0)                # the right joint and its arm: sink, turn about x (degrees)
# The pit where the chin was: its plan (the chin's, a little wider), the charred lumps in it.
PIT = [(-4.6, 2.6), (4.8, 2.6), (5.2, -0.4), (2.6, -3.0), (-1.6, -3.0), (-4.2, -0.6)]
PIT_LUMPS = [((-2.6, 0.6, 0.6), (1.6, 1.3, 0.8)), ((2.2, 0.4, 0.5), (1.8, 1.4, 0.8)),
             ((0.2, -1.6, 0.4), (1.5, 1.0, 0.6)), ((-0.4, 1.6, 1.0), (1.2, 1.0, 0.8))]
BURN = [((0.5, 0.2, 2.0), (7.0, 5.0, 6.0), 1.0), ((18.6, 2.4, 2.0), (5.0, 5.0, 5.0), 0.9),
        ((-7.0, 2.8, 3.0), (3.5, 3.5, 4.0), 0.55), ((8.0, 2.8, 3.0), (4.0, 3.5, 4.0), 0.7)]


def burn(co):
    value = 0.0
    for centre, radii, strength in BURN:
        d = Vector(((co.x - centre[0]) / radii[0], (co.y - centre[1]) / radii[1], (co.z - centre[2]) / radii[2]))
        value += strength * math.exp(-1.4 * d.length_squared)
    return value + 0.16 * noise.noise(co * 0.5 + Vector((1.7, -3.3, 2.9)))


def materials():
    m = bc.materials()
    m["pit"] = k.material("crab_pit", palette=0x01, metallic=0.2, roughness=0.75)
    m["soot"] = k.material("soot", palette=0x10, metallic=0.2, roughness=0.8)
    return m


def turn_about(obj, pivot, axis, degrees, shift=(0.0, 0.0, 0.0)):
    obj.data.transform(Matrix.Translation(Vector(pivot) + Vector(shift)) @
                       Matrix.Rotation(math.radians(degrees), 4, axis) @ Matrix.Translation(-Vector(pivot)))


def build_whole():
    m = materials()
    # The live crab, whole (polish_brick_crab.build_whole without its last clip, which follows here).
    bc.left_half(m)
    half = mk.meshes()
    for obj in half:
        mk.apply(obj)
    bc.mirror_half(half)
    bc.middle(m)
    for obj in mk.meshes():
        mk.apply(obj)
    by = {o.name: o for o in mk.meshes()}
    # The chin is gone; the dome's front lip and the red balls bitten open (their insides dark).
    wk.delete([by.pop("chin")])
    for name, centre, radius in BITES:
        bite = mk.ball("bite_" + name, centre, (radius, radius * 0.9, radius * 0.8), m["pit"], 20, 10)
        mk.boolean(by[name], bite, "DIFFERENCE")
        mk.cleanup(by[name], dissolve=0.0)
        k.smooth(by[name], 60)
    # The right grey ball: dented, cracked through by two wedges, sunk and rolled.
    grey = by["grey_ball_r"]
    centre, radius = GREY_R_DENT
    mk.boolean(grey, mk.ball("dent", centre, (radius, radius, radius * 0.8), m["pit"], 16, 8), "DIFFERENCE")
    for i, (x, y, angle, width) in enumerate(CRACKS):
        d = Vector((math.cos(math.radians(angle)), math.sin(math.radians(angle))))
        side = Vector((-d.y, d.x)) * width / 2
        p0, p1 = Vector((x, y)) - d * 6, Vector((x, y)) + d * 6
        wedge = mk.prism(f"crack{i}", wk.ccw([tuple(p0 - side * 0.2), tuple(p1 - side), tuple(p1 + side),
                                              tuple(p0 + side * 0.2)]), 1.2, 9.0, m["pit"])
        mk.boolean(grey, wedge, "DIFFERENCE")
    mk.cleanup(grey, dissolve=0.0)
    k.smooth(grey, 60)
    sink, roll = GREY_R_SINK
    turn_about(grey, (18.8, 2.2, 0.0), "Y", roll, (0.0, 0.0, -sink))
    # The pincers fallen flat onto the wall, bent into a U under the pit; the right joint bent down.
    wk.delete([by.pop("pincer"), by.pop("pincer_r")])
    for side in (1, -1):
        path = [(x if side > 0 else 2 * bc.AXIS_X - x, y, z, r) for x, y, z, r in PINCER_U]
        bar = mk.smooth_tube("pincer_flat" + ("" if side > 0 else "_r"), path, m["red"], 14, iterations=2)
        bar.data.transform(Matrix.Scale(PINCER_FLAT, 4, (0, 0, 1)))
        if side < 0:
            bar.data.flip_normals()
        k.recalc_normals(bar)
        bc.red_bands(bar, m)
    sink, turn = JOINT_R_DROP
    for name in ("joint_r", "joint_arm_r"):
        turn_about(by[name], (11.6, -0.8, 1.5), "X", turn, (0.0, 0.0, sink))
    # The pit where the chin was: a dark floor, charred lumps.
    floor = mk.prism("pit_floor", wk.ccw(wk.jagged(PIT, 4.1, 0.35, 0.8)), 0.0, 0.45, m["pit"])
    mk.bevel(floor, 0.15, 1, 35)
    mk.shade(floor, 35)
    for i, (c, radii) in enumerate(PIT_LUMPS):
        wk.rock(f"pit_lump{i}", c, radii, m["soot"] if i % 2 else m["dark"], 21.0 + 1.7 * i, flat=0.0)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
        bc.clip_below(obj)
    # Scorched round the pit, the red balls' bites and the right grey ball.
    for obj in parts:
        if obj.name.startswith(("pit_", "trident")):
            continue
        wk.scorch(obj, burn, levels=(0.3, 0.75), step=1.2 if obj.name == "grey_ball_r" else None)
        wk.reshade(obj, 60, True)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0], m


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    whole, m = build_whole()
    print("whole brick crab wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "brick_crab_wreck_whole", whole, size=(72, 28), scale=10, distance=2.0)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in bc.PIECES:
        pieces = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(name + "_wreck", pieces, os.path.join(out, name + "_wreck.glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name + "_wreck", pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
