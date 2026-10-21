"""Batch AT of wave 3 (the second animation pass), sheet D: a machine of the asteroid levels whose frames change shape,
for frame lines. Built by batch J's own builder (wave3_j.py, imported as it is, its output unchanged) and posed as the
frames draw it (models.cfg: as its first frame's model, yaw=0). (The eye tub's frames: polish_eye_tub.py.)

- shell_ship_<sprite> (D 159, 161; enemy 285 of the asteroid levels, shell_ship): its two dark shells close over the
  eye and open again, 157 159 159 161 161 159 159 157: 159 the shells 2 pixels apart round the hub, 161 meeting in one
  egg (each a little narrower); in both the frames draw the ship a pixel to the left of 157, as the models are.

usage: Blender -b --factory-startup -P wave3_at_d.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

wj = kit.quiet_import("wave3_j")
kit.forget()
w = kit.w
pal = kit.pal
D = "enemy_D"


# --- The shell ship ----------------------------------------------------------------------------------------------

def shell_ship(left, right, narrow, dx):
    """wave3_j's shell ship with its shells' inner faces moved to x = left and right (from 157's -3.6 and 3.6), each
    shell `narrow` of its width, the hub and eye moved by dx."""
    wj.shell_ship()
    for side, x_in in ((-1, left), (1, right)):
        objs = kit.objects((f"shell{side}", f"rim{side}"))
        old = side * 3.6
        m = Matrix.Translation((x_in, 0.0, 0.0)) @ Matrix.Diagonal((narrow, 1.0, 1.0, 1.0)) @ \
            Matrix.Translation((-old, 0.0, 0.0))
        w.transform(objs, m)
    w.transform(kit.objects(("hub", "neck", "eye_ring", "eye")), Matrix.Translation((dx, 0.0, 0.0)))


# 159: the shells' inner faces at x -2 and 0 (columns 2-9 and 12-19); 161: both at -1, each 7 pixels wide (columns 4-10
# and 11-17).
SHELL_FRAMES = {159: (-2.0, 0.0, 1.0, -1.0), 161: (-1.0, -1.0, 0.95, -1.0)}
for s, args in SHELL_FRAMES.items():
    w.model(f"shell_ship_{s}", [(D, s, True)])(lambda args=args: shell_ship(*args))


if __name__ == "__main__":
    w.run()
