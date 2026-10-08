"""Batch AT of wave 3 (the second animation pass), sheet ' (written x27 in models.cfg): FRUIT's bladed orange turning
its blades, for frame lines. Built by batch AE's own builder (wave3_ae.py, imported as it is, its output unchanged),
posed as the frames draw it and cut into the same four pieces as the first frame's models (origin, yaw=0 as those).

- orange_saw_<sprite> (' 82, 84 above 120, 122; enemies 1229-1232, whose frames are 78 82, 80 84, 116 120, 118 122):
  the saw plate's eight curved blades turned a sixteenth of a turn (22.5 degrees, counter-clockwise on the screen as
  the frames draw them) about the orange, which stays as it is. With the first frame's pieces (orange_saw_tl ...)
  the two frames make the blades turn on and on.

usage: Blender -b --factory-startup -P wave3_at_orange.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ar_kit as kit  # noqa: E402

ae = kit.quiet_import("wave3_ae")
kit.forget()

TURN = 22.5           # degrees, counter-clockwise seen from above (on the screen)


def orange_saw_turned():
    """wave3_ae's bladed orange with its saw plate turned by TURN about the orange's centre."""
    ae.orange_saw_whole()
    kit.turn_z([bpy.data.objects["saw_plate"]], TURN, (ae.ORANGE_C.x, ae.ORANGE_C.y))


# The same boxes as orange_saw_tl, _tr, _bl, _br (the whole's centre is the four sprites' shared corner).
kit.n.pieced("orange_saw_turned", orange_saw_turned, (48, 56), kit.quad_pieces("orange_saw_", "enemy_x27", 82))


if __name__ == "__main__":
    ae.kit.run()
