"""Batch AR of wave 3, sheet N (written n in models.cfg): GYGES' maw opening and its pincers opening, for frame lines.
Built by batch AN's own builders (wave3_an_boss.py's boss, wave3_an.py's pincer claw; imported as they are, their
output unchanged), fed the frames' pixels (wave3_ar_art.py) and posed as the frames draw them, cut into the same
pieces as the first frame's models, drawn at their own origins (origin, yaw=0 as those).

- The maw (enemies 379 380 384 385: n 119 121 above 157 159, the middle of the 24-piece boss) opens when the boss
  fires: 119 229 233 237 241 237 233 229 119 (and 121 231 235 239 243 ..., 157 267 271 275 279 ..., 159 269 273 277
  281 ...). A fireball swells in its throat (a glowing lumpy ball, small and dim at 229, filling the throat at 241)
  and the two long fangs of its top lip fold back (shorter and shorter); the throat is painted by the frame's pixels
  (its floor lit by the fire). The other pieces don't change. Models gyges_maw_<sprite> for the four pieces of
  each of 229 233 237 241: the boss rebuilt whole with the frame's middle and cut as gyges_maw_119 ... are.
- The pincers (enemies 180 above 181: n 163 above 201; 182 above 183: n 11 above 49, its mirror image) open and
  close: 163 203 203 203 207 207 207 203 203 203 163 ... (and 201 205 245; 11 9 1; 49 47 39): the small finger,
  its blue knob at its root, swings out from the big one. Models gyges_pincer_<sprite> for 203 205 207 245 (left)
  and 9 47 1 39 (right): wave3_an.py's pincer built from the frame's pixels (the shell follows the frame's outline),
  its knob moved with the finger.

usage: Blender -b --factory-startup -P wave3_ar_gyges.py -- [--only names] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ar_kit as kit  # noqa: E402
import wave3_ar_art as art  # noqa: E402

ab = kit.quiet_import("wave3_an_boss")
an = kit.quiet_import("wave3_an")
kit.forget()
ak = ab.kit                       # wave3_an_kit
Frame = ak.Frame
pal = kit.pal


# --- The maw ---------------------------------------------------------------------------------------------------------

MAW_CELL = (48, 84)               # the four middle sprites' top left pixel in the boss


MARGIN = 3                        # pixels at the middle's edges kept as the first frame's (see maw_frame)


def maw_frame(name):
    """The boss's art with the four middle sprites replaced by one of the opening frames' (wave3_ar_art.MAW_<s>),
    but for a margin round them: there the frames only darken the side teeth (the models' teeth are cones, not
    pixels), and the body's relief, embossed from the pixels, stays as the pieces round the middle have it, so that
    they meet without a step."""
    block = kit.w.grid(getattr(art, name), 48)
    out = Frame.__new__(Frame)
    out.__dict__.update(ab.BOSS.__dict__)
    out._shades = {}
    out.g = [row[:] for row in ab.BOSS.g]
    c0, r0 = MAW_CELL
    for r in range(MARGIN, 56 - MARGIN):
        for c in range(MARGIN, 48 - MARGIN):
            out.g[r0 + r][c0 + c] = block[r][c] if r < len(block) else None
    return out


def folded_teeth(fold):
    """TEETH and TOOTH_AXIS with the top lip's fangs (tooth0, its mirror image, the one on the axis) folded back to
    `fold` of their length."""
    def short(spec):
        (bc, br), (tc, tr), rad = spec
        return ((bc, br), (bc + (tc - bc) * fold, br + (tr - br) * fold), rad)
    teeth = list(ab.TEETH)
    teeth[0] = short(teeth[0])
    return teeth, short(ab.TOOTH_AXIS)


def fireball(radius, heat):
    """The fire in the throat: a lumpy ball of flame low in the throat (with smaller flames bulging from it once it
    is big), red at its flanks, orange and yellow over its crown, white-hot inside; heat (0-1) brightens it."""
    c, r = 63.0, 112.5
    x, y = ab.X(c), ab.Y(r)
    z = ab.throat_floor(c, r) + radius * 0.75
    hot = int(round(2 * heat))
    shades = [0x75, 0x77, 0x79 + hot // 2, 0x7a + hot, 0x7c + hot]
    glows = [0.5, 0.8, 1.1, 1.5, 2.0]
    mats = [pal(f"maw_fire_{i:x}", i, metallic=0.0, roughness=0.35, glow=g * (0.7 + 0.6 * heat))
            for i, g in zip(shades, glows)]

    def pick(cc, nrm):
        up = nrm.z
        return mats[3] if up > 0.8 else mats[2] if up > 0.45 else mats[1] if up > 0.0 else mats[0]
    parts = [kit.w.lumpy("fireball", (x, y, z), (radius, radius * 0.9, radius * 0.8), mats[2], seed=7, amount=0.3,
                         segments=20, rings=12)]
    if radius > 3.0:
        flames = ((-0.75, 0.35, 0.45), (0.7, -0.4, 0.4), (0.15, 0.8, 0.35), (-0.3, -0.75, 0.38))
        for i, (ax, ay, s_) in enumerate(flames):
            rr = radius * s_
            parts.append(kit.w.lumpy(f"fireball_flame{i}", (x + ax * radius, y + ay * radius, z - radius * 0.15),
                                     (rr, rr, rr * 0.9), mats[1], seed=11 + i, amount=0.3, segments=12, rings=7))
    for obj in parts:
        kit.paint_faces(obj, pick)
    if heat > 0.2:
        inner = kit.w.lumpy("fireball_core", (x - radius * 0.15, y + radius * 0.2, z + radius * 0.35),
                            (radius * 0.45, radius * 0.4, radius * 0.45), mats[4], seed=3, amount=0.25, segments=14,
                            rings=8)
        kit.paint_faces(inner, lambda cc, nrm: mats[4] if nrm.z > 0.3 else mats[3])
        parts.append(inner)
    return parts


def maw_open(name, fold, radius, heat):
    """The whole boss with its maw as frame `name` draws it."""
    saved = ab.BOSS, ab.TEETH, ab.TOOTH_AXIS
    ab.BOSS = maw_frame(name)
    ab.TEETH, ab.TOOTH_AXIS = folded_teeth(fold)
    try:
        ab.boss()
    finally:
        ab.BOSS, ab.TEETH, ab.TOOTH_AXIS = saved
    for obj in fireball(radius, heat):
        kit.k.smooth(obj, 60)


# (frame: the top left sprite, its pieces' sprites in the order of 119 121 157 159; the fangs' length; the fire's
# radius and heat)
MAW = [(229, (229, 231, 267, 269), 1.0, 1.6, 0.0), (233, (233, 235, 271, 273), 0.85, 2.4, 0.3),
       (237, (237, 239, 275, 277), 0.65, 4.0, 0.65), (241, (241, 243, 279, 281), 0.45, 6.5, 1.0)]
MAW_CELLS = [(48, 84), (72, 84), (48, 112), (72, 112)]

for s, sprites, fold, radius, heat in MAW:
    f = maw_frame(f"MAW_{s}")
    kit.pieced(f"gyges_maw_open_{s}", lambda s=s, fold=fold, radius=radius, heat=heat: maw_open(f"MAW_{s}", fold,
                                                                                                radius, heat),
               (120, 168), [ak.piece(f"gyges_maw_{p}", f, c0, r0, 24, 28) for p, (c0, r0) in zip(sprites, MAW_CELLS)])


# --- The pincers -----------------------------------------------------------------------------------------------------

def pincer_open(right, left_name, right_name, knob):
    """wave3_an's pincer built from an opening frame's pixels (left_name for the shell, which the right pincer
    mirrors; right_name paints the right one), its blue knob moved by `knob` (dx, dy, as for the left pincer)."""
    saved = an.CLAW_L, an.CLAW_R
    an.CLAW_L = ak.Frame(getattr(art, left_name), 24, (12, 28))
    an.CLAW_R = ak.Frame(getattr(art, right_name), 24, (12, 28))
    try:
        an.claw(right)
    finally:
        an.CLAW_L, an.CLAW_R = saved
    dx, dy = knob
    joint = bpy.data.objects["pincer_joint"]
    joint.data.transform(Matrix.Translation((-dx if right else dx, dy, 0.0)))


# The frames: the left pincer's (top, bottom), the right one's, the knob's move (from where the frames draw its
# light).
PINCERS = [((203, 205), (9, 47), (2.0, 3.0)), ((207, 245), (1, 39), (4.0, 5.0))]
for (lt, lb), (rt, rb), knob in PINCERS:
    fl = ak.Frame(getattr(art, f"CLAW_L_{lt}"), 24, (12, 28))
    fr = ak.Frame(getattr(art, f"CLAW_R_{rt}"), 24, (12, 28))
    kit.pieced(f"gyges_pincer_left_{lt}", lambda lt=lt, rt=rt, knob=knob: pincer_open(False, f"CLAW_L_{lt}",
                                                                                     f"CLAW_R_{rt}", knob),
               (24, 56), [ak.piece(f"gyges_pincer_{lt}", fl, 0, 0), ak.piece(f"gyges_pincer_{lb}", fl, 0, 28)])
    kit.pieced(f"gyges_pincer_right_{rt}", lambda lt=lt, rt=rt, knob=knob: pincer_open(True, f"CLAW_L_{lt}",
                                                                                      f"CLAW_R_{rt}", knob),
               (24, 56), [ak.piece(f"gyges_pincer_{rt}", fr, 0, 0), ak.piece(f"gyges_pincer_{rb}", fr, 0, 28)])


if __name__ == "__main__":
    ak.run()
