"""Batch AT of wave 3 (the second animation pass): two more objects whose frames change shape, for frame lines, each
built by its own script's builder (imported as it is, its output unchanged) and posed as the frames draw it
(models.cfg: as the first frame's models, yaw=0).

- ice_drill_arm_<sprite> (sheet 7: 205, 203; enemy 86 of CAMANIS, ice_drill_arm; wave3_ac_ice.py): the arm pulls in
  when it launches, 207 205 203 205 207: the knuckle, the grey head with its band, point and bracket slide up the
  screen 2 and 3 pixels, the thin rod behind them sliding into the flange.
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
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

wa = kit.quiet_import("wave3_ac_ice")
wz = kit.quiet_import("wave3_z_rock")
kit.forget()
w = kit.w


# --- Sheet 7: the drill's arm pulling in --------------------------------------------------------------------------

def drill_in(shift):
    """wave3_ac_ice's red hood with its arm's head (the knuckle down to the point and the bracket, and the thin rod
    behind them) slid `shift` up the screen."""
    wa.build_drill()
    parts = kit.objects(("rod2", "knuckle", "head", "head_band", "tip", "bracket"))
    w.transform(parts, Matrix.Translation((0.0, shift, 0.0)))


for s, shift in ((205, 2.0), (203, 3.0)):
    kit.n.pieced(f"ice_drill_in_{s}", lambda shift=shift: drill_in(shift), (24, 56),
                 [(f"ice_drill_arm_{s}", (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0),
                   lambda s=s: kit.sheet_mask("enemy_7", s))])


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
