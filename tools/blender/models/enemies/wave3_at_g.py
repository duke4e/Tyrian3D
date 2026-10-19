"""Batch AT of wave 3 (the second animation pass), sheet G: a creature whose frames close its tusks, for frame
lines (the violet pincer's frames: polish_violet_pincer.py). Built by batch R's own builder (wave3_r_beasts.py,
imported as it is, its output unchanged) and posed as the frames draw it (models.cfg: as its first frame's model,
yaw=0).

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
