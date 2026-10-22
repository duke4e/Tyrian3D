"""Batch AT of wave 3 (the second animation pass): one more object whose frames change shape, for frame lines, built
by its own script's builder (imported as it is, its output unchanged) and posed as the frames draw it (models.cfg: as
the first frame's models, yaw=0). (CAMANIS' drill pulling its arm in, sheet 7 205 and 203, is polish_ice_drill.py's.)

- tan_dome_<sprite> (sheet L: 165, 167 and 203, 205; enemies 1151, 1152 of MINERS, tan_dome_tl and _tr;
  wave3_z_rock.py): the red nub on the creature's head swells into a fire ball and bursts, 161 165 165 203 203 (and
  163 167 167 205 205): a glowing ball of fire 6 and 7 pixels across where the nub was. The whole creature is built
  and cut as tan_dome_tl and _tr are (the nub lies across both).

Left as they are (their frames only change light, not shape): the eye shell of the asteroid levels (S 93, 131: its
socket only lights up red) and FRUIT's eye cup (% 233, 235, 237: its orb only brightens).

usage: Blender -b --factory-startup -P wave3_at_misc.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

wz = kit.quiet_import("wave3_z_rock")
kit.forget()
w = kit.w


# --- Sheet L: the nub swelling into a fire ball --------------------------------------------------------------------

def tan_dome_fire(centre_dy, centre_dz, radii, heat):
    """wave3_z_rock's creature with the nub on its head swollen into a ball of fire (its centre moved from the nub's
    by dy, dz; its radii, heat)."""
    wz.dome_whole()
    nub = bpy.data.objects["nub"]
    xs = [v.co.x for v in nub.data.vertices]
    ys = [v.co.y for v in nub.data.vertices]
    zs = [v.co.z for v in nub.data.vertices]
    cx, cy, cz = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2
    kit.remove(["nub", "nub_hot"])
    kit.fireball("nub", (cx, cy + centre_dy, cz + centre_dz), radii, heat, seed=3)


# (top left frame, top right frame: the ball's offset from the nub's centre, radii, heat) -- 165/167 draw it 6 or 7
# pixels across and 4 tall at rows 17-20, 203/205 7 across and 7 tall at rows 14-20, white-hot in its middle.
NUB = [(165, 167, (0.4, 0.8), (3.0, 2.3, 2.1), 0.4), (203, 205, (1.6, 1.8), (3.6, 3.4, 3.1), 0.95)]
for tl, tr, (dy, dz), radii, heat in NUB:
    _, box_l, centre_l, _ = wz.kit.quarter("x", wz.DOME, 0, 0)
    _, box_r, centre_r, _ = wz.kit.quarter("x", wz.DOME, 24, 0)
    kit.n.pieced(f"tan_dome_fire_{tl}", lambda dy=dy, dz=dz, radii=radii, heat=heat: tan_dome_fire(dy, dz, radii, heat),
                 (48, 56), [(f"tan_dome_{tl}", box_l, centre_l, lambda s=tl: kit.sheet_mask("enemy_L", s)),
                            (f"tan_dome_{tr}", box_r, centre_r, lambda s=tr: kit.sheet_mask("enemy_L", s))])


def main():
    if w.MODELS:
        w.run()
    if kit.n.OBJECTS or kit.n.MODELS:
        kit.n.run()


if __name__ == "__main__":
    main()
