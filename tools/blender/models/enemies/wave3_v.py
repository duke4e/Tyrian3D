"""Enemies of wave 3, batch V (sheet T): DELI's boss, modelled as its sprites look (models.cfg: yaw=0). CORAL's
sea creatures and machines are in wave3_v_sea.py; the kit is wave3_v_kit.py, the pixels wave3_v_art.py.

- deli_boss_1, deli_boss_3, deli_boss_5, deli_boss_7, deli_boss_9, deli_boss_11 (the top row) and
  deli_boss_41, deli_boss_43, deli_boss_45, deli_boss_47 (the bottom row between the arms): the red war
  machine at the end of DELI and New Deli (in the sky) that HARVEST sends over again and again (on the top
  layer), 144 x 56 pixels, which one level event puts together from twelve 2x2 sprites (enemies 400-405 at
  (x + 24 i, y - 28), 406-411 at (x + 24 i, y)). Its gun arms (T 39 and 49, deli_arm_left and
  deli_arm_right of wave 1, wave1_c.py) hang from black shoulder pads at its ends; the arms' ribbed tubes go
  on up under the pads and bend into red beams out to the hull; a black hump on each beam's inner end, a
  small claw hanging under it. The hull: a red frame round two big glossy black spheres, between them a
  dark glass canopy; across its top two grilles with fire glowing behind them; below, a red jaw with ribs
  round a dark slot and a grey nub. Built whole (symmetric about the middle of pixel column 71, as the
  sprites and the arms are) and cut into its ten pieces (origin), the arms' tubes and hoses meeting the
  arm models at the pieces' lower edge.

usage: Blender -b --factory-startup -P wave3_v.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix> [--arms 1]]   (--arms: the whole with the arm models of wave 1)
"""
import math
import os
import sys

import bpy

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_v_kit as v  # noqa: E402
from wave3_v_kit import art, k, sh, w, n, pal  # noqa: E402

BOSS = v.Frame(art.BOSS, 144, (72, 28))          # the sprites as drawn (masks)
SYM = v.Frame(art.BOSS, 144, (72, 28)).symmetric(71)  # the left half mirrored over the right (painting, parts)
BLUR = int(k.args().get("blur", 0))
AXIS = -0.5  # x of the middle of pixel column 71: column c mirrors 142 - c
X, Y = SYM.X, SYM.Y


def L(c):
    """A column's twin on the left half."""
    return c if c <= 71 else 142 - c


def kind(index):
    """K: black outline and seams, G: the grey and black parts' lighter shades, R: red, F: fire."""
    ramp, shade = index >> 4, index & 15
    if ramp == 0:
        return "K" if shade <= 2 else "G"
    return {4: "R", 7: "F"}.get(ramp, "?")


def region(kinds, c0, c1, r0, r1):
    """keep(index, column, row) for the pixels of the given kinds whose left twin lies in c0..c1, r0..r1."""
    return lambda i, c, r: kind(i) in kinds and c0 <= L(c) <= c1 and r0 <= r <= r1


def boss_whole():
    paint = v.Painter("boss", shades={4: (2, 3, 5, 7, 8, 9, 11, 13), 0: (1, 3, 5, 8, 12), 7: (6, 9, 12, 14)},
                      metallic=0.45, roughness=0.38, finish={0: (0.5, 0.25)},
                      glow={0x70 + s: 0.6 + 0.12 * s for s in range(16)})
    core_mat = pal("boss_core", 0x01, metallic=0.3, roughness=0.6)
    shell = pal("boss_shell", 0x48, metallic=0.35, roughness=0.35)
    black = pal("boss_black", 0x02, metallic=0.4, roughness=0.18)
    glass = pal("boss_glass", 0x02, metallic=0.2, roughness=0.08)
    grey = pal("boss_grey", 0x06, metallic=0.6, roughness=0.3)
    grey_light = pal("boss_grey_light", 0x09, metallic=0.6, roughness=0.25)
    sym_parts = []   # built over the whole width (symmetric already)
    side_parts = []  # built on the left, mirrored to the right

    # The dark core under everything: what shows in the seams between the plates. Not under the arms.
    core = v.relief("core", v.outlines_of(SYM, lambda i, c, r: not (L(c) <= 20 and r >= 22), grow=0.0, smooth=1),
                    core_mat, sh.pillow_profile(5.2, 1.6), base=-3.5, spacing=1.0, flat=True)
    sym_parts.append(core)

    # The hull's red frame round the spheres and the canopy (its seams open on the core), the top plate a
    # step higher. Flat tops, painted pixel by pixel.
    frame = v.relief("frame", v.outlines_of(SYM, region("R", 39, 71, 3, 42), grow=0.35, smooth=1), shell,
                     sh.pillow_profile(8.8, 1.3), base=-3.0, spacing=0.75, flat=True)
    plate = v.relief("plate", v.outlines_of(SYM, region("R", 44, 71, 3, 12), grow=0.0, smooth=1), shell,
                     sh.pillow_profile(1.3, 0.7), base=5.7, spacing=0.65, flat=True)
    sym_parts += [frame, plate]

    # The beam from the shoulder to the hull, the arm's bend into it and the small claw under it.
    beam = v.relief("beam", v.outlines_of(SYM, region("R", 22, 41, 13, 23), grow=0.35, smooth=1), shell,
                    sh.pillow_profile(6.2, 1.4), base=-1.6, spacing=0.7, flat=True)
    bend = v.relief("bend", v.outlines_of(SYM, region("R", 5, 25, 19, 23), grow=0.4, smooth=1), shell,
                    sh.pillow_profile(5.6, 2.0), base=-1.0, spacing=0.6, flat=True)
    claw = v.relief("claw", v.outlines_of(SYM, region("R", 25, 33, 24, 32), grow=0.3, smooth=1), shell,
                    sh.round_profile(0.9, max_height=3.0), base=0.6, bottom=0.6, spacing=0.65)
    sym_parts += [beam, bend, claw]

    # The black shoulder pad over the arm's top.
    pad = v.relief("pad", v.outlines_of(SYM, region("KG", 7, 21, 9, 20), grow=0.0, smooth=2), black,
                   sh.pillow_profile(8.6, 2.6), base=-1.0, spacing=0.6, flat=True)
    sym_parts.append(pad)
    # The grey pin between the pad and the beam.
    side_parts.append(w.lathe_axis("pin", [(0.0, 0.8), (0.3, 1.3), (4.4, 1.3), (4.7, 0.8)], grey_light,
                                   (X(20.0), Y(18.5), 3.6), (1, 0, 0), 14))

    # The arm's ribbed tube, on up from the arm model (deli_arm_left: axis at column 9, z 1.6) under the pad,
    # and the black hose beside it up into the beam.
    axis_x, axis_z, radius = X(9.0), 1.6, 6.4
    rings = []
    for i in range(12):
        y = -0.9 + i * 0.85
        ring = []
        for j in range(48):
            a = 2 * math.pi * j / 48
            pleat = 1 + 0.045 * math.cos(18 * a) if math.sin(a) > -0.2 else 1
            ring.append(Vector((axis_x + math.cos(a) * radius * pleat, y,
                                axis_z + math.sin(a) * radius * 0.72 * pleat)))
        rings.append(ring)
    tube = k.loft("upper_arm", rings, shell, end_point=(axis_x, rings[-1][0].y + 1.2, axis_z))
    k.smooth(tube, 70)
    side_parts.append(tube)
    side_parts.append(w.tube("hose", w.catmull([(X(19.5) - 0.5, -1.2, 2.2), (X(19.5) - 0.3, 1.5, 2.5),
                                                (X(19.6), Y(22.5), 3.0)], 0.5), 1.75, black, 14, squash=0.8))

    # The black hump on the beam's inner end.
    side_parts.append(w.sphere("hump", (X(38.6), Y(9.6), 5.0), (6.0, 4.0, 3.8), black, 22, 11))
    # The big glossy black sphere in the hull's frame.
    side_parts.append(w.sphere("sphere", (X(57.0), Y(25.0), 2.4), (7.2, 10.2, 7.6), black, 30, 15))
    side_parts.append(w.sphere("sphere_glint", (X(53.6), Y(21.0), 8.4), (1.6, 2.2, 0.9), grey_light, 14, 7))

    # The vents across the top: a dark frame, the fire glowing low in it, dark slats across.
    vent_keep = lambda i, c, r: kind(i) == "K" and 52 <= L(c) <= 68 and r <= 9 and not (L(c) <= 53 and r >= 8)
    housing = v.relief("vent_housing", v.outlines_of(SYM, vent_keep, smooth=1), core_mat,
                       sh.pillow_profile(8.0, 0.6), base=-1.0, spacing=0.8, flat=True)
    fire = v.relief("vent_fire", v.outlines_of(SYM, lambda i, c, r: kind(i) == "F" and r <= 9, grow=0.3, smooth=1),
                    paint(0x78), sh.pillow_profile(6.0, 0.6), base=-1.0, spacing=0.55, flat=True)
    sym_parts += [housing, fire]
    for c in (56.0, 58.6, 61.2, 63.8):
        side_parts.append(k.box(f"slat{c}", (X(c), Y(4.6), 6.4), (0.7, 7.2, 1.2), core_mat))

    # The canopy between the spheres: dark glass in a frame, its upper edge catching the light.
    canopy = w.block("canopy", (AXIS, Y(18.8)), 7.6, 5.4, 8.8, glass, rounding=1.6, power=4, dome=0.8, segments=32)
    sym_parts.append(canopy)
    sym_parts.append(w.hoop("canopy_rim", (AXIS, Y(18.8), 8.2), [(6.6, -0.5), (7.6, -0.5), (7.6, 0.4), (6.8, 0.6)],
                            grey, 40, scale_y=0.72))
    # The grey nub in the dark slot under the canopy.
    sym_parts.append(w.sphere("nub", (AXIS, Y(32.5), 2.6), (3.0, 2.4, 2.0), grey, 20, 10))

    side_parts += v.mirror_copies(side_parts, AXIS)

    # Paint the red and the black reliefs by the sprite (the left half's light on both sides).
    red = lambda i: kind(i) == "R"
    for obj in (frame, plate, beam, bend):
        v.pixelate(obj, SYM)
        v.paint_sprite(obj, SYM, paint, wall_steps=-2, keep=red, probe=0.4, blur=BLUR, under=core_mat)
        v.merge_flat(obj)
    v.paint_sprite(claw, SYM, paint, wall_steps=-2, keep=red, probe=0.4, blur=1)
    v.pixelate(pad, SYM)
    v.paint_sprite(pad, SYM, paint, wall_steps=-1, keep=lambda i: kind(i) in "KG", under=core_mat)
    v.merge_flat(pad)
    v.pixelate(fire, SYM)
    v.paint_sprite(fire, SYM, paint, wall_steps=-3, keep=lambda i: kind(i) == "F", under=core_mat)
    v.merge_flat(fire)
    v.merge_flat(core)
    v.paint_sprite(canopy, SYM, paint, wall_steps=0, keep=lambda i: kind(i) == "G" and i & 15 >= 7)
    v.stats(*w.meshes())
    if "arms" in k.args():  # the arm models of wave 1 beside the whole (previews only)
        for name, centre in (("deli_arm_left", (-60.0, -14.0)), ("deli_arm_right", (60.0, -14.0))):
            bpy.ops.import_scene.gltf(filepath=os.path.join(w.ENEMIES, name + ".glb"))
            for obj in bpy.context.selected_objects:
                obj.location.x += centre[0]
                obj.location.y += centre[1]
                if obj.type == "MESH":
                    obj.data.flip_normals()  # the game's winding back to Blender's
        bpy.context.view_layer.update()


PIECES = [(1, 0, 0), (3, 24, 0), (5, 48, 0), (7, 72, 0), (9, 96, 0), (11, 120, 0),
          (41, 24, 28), (43, 48, 28), (45, 72, 28), (47, 96, 28)]


def boss_piece(sprite, col, row):
    x0, y1 = col - 72, 28 - row
    box = (x0, x0 + 24, y1 - 28, y1)
    return (f"deli_boss_{sprite}", box, (x0 + 12, y1 - 14), lambda: BOSS.mask((col, col + 24, row, row + 28)))


v.PROTECT[:] = ["frame", "plate", "beam", "bend", "pad", "vent_fire"]
v.pieced("deli_boss", boss_whole, (144, 56), [boss_piece(*p) for p in PIECES])


if __name__ == "__main__":
    v.run()
