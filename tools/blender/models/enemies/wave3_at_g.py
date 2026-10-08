"""Batch AT of wave 3 (the second animation pass), sheet G: two creatures whose frames close their arms, for frame
lines. Built by batch R's own builders (wave3_r_beasts.py, imported as it is, its output unchanged) and posed as the
frames draw them (models.cfg: as their first frame's models, yaw=0).

- violet_pincer_<sprite> (G 123, 125; enemy 184 of GYGES and MISTAKES, violet_pincer): it closes its arms and opens
  them again, 121 123 123 123 125 125 125 123 123 123 121, its head brightening: both arms (the segments, joints and
  golden fangs) move in by 1 pixel (123) and 2 (125, its fangs a pixel more: turned 3 degrees in about the
  shoulder), the head's highlight glowing brighter.
- tusk_beetle_<sprite> (G 51, 53; enemy 778 of SOH JIN and MISTAKES, tusk_beetle): it closes its tusks and horns, 49
  49 49 51 51 51 53 53 53 51 51 51: the tusks move in by 1 and 2 pixels (at 53 they meet under the carapace), the
  horns turn in about their roots so that their tips are 1 and 2 pixels further in.

usage: Blender -b --factory-startup -P wave3_at_g.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

rb = kit.quiet_import("wave3_r_beasts")
kit.forget()
w = kit.w
pal = kit.pal
G = "enemy_G"
AXIS = 0.5            # the creatures' middle (both builders' axis)


def move_in(names, side, shift, degrees=0.0, pivot=(0.0, 0.0)):
    """Moves one side's parts (side -1 left, 1 right) in towards the axis by `shift` and turns them in by `degrees`
    about pivot (x, y, before the shift; for the left side, its mirror image for the right one): their lower ends
    swing in."""
    objs = [bpy.data.objects[f"{nm}{side}"] for nm in names]
    px_ = AXIS + side * abs(pivot[0] - AXIS)
    turn = kit.about((px_, pivot[1]), Matrix.Rotation(math.radians(-side * degrees), 4, "Z"))
    w.transform(objs, Matrix.Translation((-side * shift, 0.0, 0.0)) @ turn)


def violet_pincer_closed(shift, degrees, glow):
    """wave3_r_beasts' violet pincer with its arms moved in, its head's highlight glowing `glow`."""
    rb.violet_pincer()
    shoulder = (AXIS - 3.0, rb.py(9.0))
    for side in (-1, 1):
        move_in(("upper", "elbow", "lower", "wrist", "fang"), side, shift, degrees, shoulder)
    hot = bpy.data.objects["head_hot"]
    hot.data.materials[0] = pal(f"pincer_head_hot_{int(glow * 10)}", 0x5e, metallic=0.1, roughness=0.15, glow=glow)


for s, (shift, degrees, glow) in {123: (1.0, 0.0, 0.6), 125: (2.0, 3.0, 0.85)}.items():
    w.model(f"violet_pincer_{s}", [(G, s, True)])(
        lambda shift=shift, degrees=degrees, glow=glow: violet_pincer_closed(shift, degrees, glow))


def tusk_beetle_closed(shift, horn_degrees):
    """wave3_r_beasts' tusk beetle with its tusks moved in by `shift`, its horns turned in about their roots."""
    rb.tusk_beetle()
    horn_root = (AXIS - 4.0, rb.py(8.5))
    for side in (-1, 1):
        move_in(("tusk",), side, shift)
        move_in(("horn",), side, 0.0, -horn_degrees, horn_root)


for s, (shift, horn) in {51: (1.0, 6.0), 53: (2.0, 12.0)}.items():
    w.model(f"tusk_beetle_{s}", [(G, s, True)])(lambda shift=shift, horn=horn: tusk_beetle_closed(shift, horn))


if __name__ == "__main__":
    w.run()
