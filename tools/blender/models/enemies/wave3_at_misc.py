"""Batch AT of wave 3 (the second animation pass): four more objects whose frames change shape, for frame lines, each
built by its own script's builder (imported as it is, its output unchanged) and posed as the frames draw it
(models.cfg: as the first frame's models, yaw=0).

- eye_hatch_<sprite> (sheet 5: 162, 160; enemy 525 of BRAINIAC, eye_hatch; wave3_l.py): the floor hatch's lids
  slide apart on its red eye and shut again, 164 162 160 160 160 162 162 162 162 164. wave3_l's hatch has them nearly
  shut on a slit, as 164 draws them; 162 has them half open (the eye 6 pixels tall between them), 160 drawn back to
  thin rims at the socket's edge, the whole eye glowing brighter.
- maze_pipe_cage_<sprite> (sheet S: 115, 117, 119, 121, 123; enemies 589 of MINEMAZE and GAUNTLET, maze_pipe_cage;
  wave3_u.py): the red core in the pipe's cage swells and shrinks, 115 115 117 117 119 119 121 121 123 123 121 ...
  117: wave3_u's pipe (built whole and cut as maze_pipe_cage is) with its core as each frame draws it: 115 none (a
  dark plug sunk in its rim; a frame line on 115 itself, since wave3_u's core is half grown), then a dull red
  blister growing and brightening to a glowing dome over the rim (123).
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

wl = kit.quiet_import("wave3_l")
wu = kit.quiet_import("wave3_u")
wa = kit.quiet_import("wave3_ac_ice")
wz = kit.quiet_import("wave3_z_rock")
kit.forget()
lk = wl.w                         # wave3_l_kit, which keeps its own registry
del lk.MODELS[:]
del lk.WHOLES[:]
w = kit.w
pal = kit.pal


# --- Sheet 5: the eye hatch's lids -------------------------------------------------------------------------------

EYE = (0.5, 1.2)      # the eye's centre (wave3_l's ex, ey)
SOCKET_RY = 4.8       # the socket rim's half height across the screen


def eye_hatch(edge, lid_z, lid_rz, eye, hot):
    """wave3_l's hatch with its lids drawn back so that their inner edges are `edge` from the eye's middle (they shrink
    into the socket's rim as they go: centred between their edge and the rim, lower), the eye's and its hot middle's
    materials ((index, glow)) and the hot middle's radii."""
    wl.eye_hatch()
    ex, ey = EYE
    lid = bpy.data.objects["lid-1"].data.materials[0]
    kit.remove(["lid-1", "lid1"])
    ry = (SOCKET_RY - edge) / 2 + 0.25
    for side in (-1, 1):
        w.sphere(f"lid{side}", (ex, ey + side * (edge + ry - 0.05), lid_z), (5.0 - 0.15 * edge, ry, lid_rz), lid, 24,
                 10)
    ei, eg = eye
    bpy.data.objects["eye"].data.materials[0] = pal(f"hatch_eye_{ei:x}_{int(eg * 10)}", ei, metallic=0.0,
                                                    roughness=0.15, glow=eg)
    # The hot middle, larger as the eye opens (at wave3_l's height).
    (hi, hg), radii = hot
    zs = [v.co.z for v in bpy.data.objects["eye_hot"].data.vertices]
    kit.remove(["eye_hot"])
    w.sphere("eye_hot", (ex - 0.2, ey + 0.1, (min(zs) + max(zs)) / 2), radii,
             pal(f"hatch_eye_hot_{hi:x}_{int(hg * 10)}", hi, metallic=0.0, roughness=0.1, glow=hg), 16, 6)


# (sprite: the lids' inner edges, their height and thickness, the eye, its hot middle): 162 shows the eye from 3 pixels
# over its middle to 3 under it, 160 from 4 to 4.
HATCH = {162: (2.6, 1.6, 1.5, (0x77, 1.7), ((0x7b, 2.2), (2.8, 1.4, 0.9))),
         160: (3.9, 1.3, 1.0, (0x78, 2.0), ((0x7c, 2.6), (3.2, 1.9, 1.0)))}
for s, args in HATCH.items():
    lk.model(f"eye_hatch_{s}", s)(lambda args=args: eye_hatch(*args))


# --- Sheet S: the core in the pipe's cage ------------------------------------------------------------------------

CAGE_X = 12.0         # the caged segment's middle in the whole pipe (wave3_u's cage_segment(m, 12.0))


def pipe_cage(radii, mat, hot):
    """wave3_u's whole pipe with its core as a frame draws it (radii; its material's (index, glow); a hotter heart's
    (index, glow) or None), cut as maze_pipe_cage is."""
    objects = wu.pipe_whole()
    core = bpy.data.objects["core"]
    zs = [v.co.z for v in core.data.vertices]
    centre_z = (min(zs) + max(zs)) / 2            # wave3_u's core centre (the crest's top less 1.2)
    objects = [o for o in objects if o.name != "core"]
    kit.remove(["core"])
    ci, cg = mat
    m = pal(f"mp_core_{ci:x}_{int((cg or 0) * 10)}", ci, metallic=0.1 if cg else 0.3, roughness=0.25 if cg else 0.5,
            glow=cg)
    # Under 300 triangles, so that the triangle budget leaves it smooth.
    objects.append(w.sphere("core", (CAGE_X, wu.PIPE_Y, centre_z), radii, m, 18, 8))
    if hot:
        hi, hg = hot
        hm = pal(f"mp_core_hot_{hi:x}_{int(hg * 10)}", hi, metallic=0.0, roughness=0.2, glow=hg)
        objects.append(w.sphere("core_hot", (CAGE_X - 0.6, wu.PIPE_Y + 1.0, centre_z + radii[2] - 0.35),
                                (radii[0] * 0.45, radii[1] * 0.4, 0.5), hm, 16, 6))
    wu.u.cut(objects, (CAGE_X - 12.0, CAGE_X + 12.0, -14.0, 14.0), (CAGE_X, 0.0))
    wu.u.budget(4800)


# (sprite: the core's radii, its material, its hot heart) -- the frames' red grows from nothing (115) to a lump about
# 4, 6, 8 and 9 pixels across, its reds from 40-42 (dull) to 49-4f (bright).
CAGE = {115: ((3.2, 4.2, 0.5), (0x40, None), None),
        117: ((2.6, 3.5, 1.5), (0x42, 0.45), None),
        119: ((3.1, 4.1, 2.3), (0x45, 0.8), None),
        121: ((3.5, 4.6, 3.0), (0x47, 1.3), (0x4a, 1.6)),
        123: ((3.9, 5.2, 3.8), (0x49, 1.8), (0x4d, 2.3))}
for s, args in CAGE.items():
    wu.u.model(f"maze_pipe_cage_{s}", [(s, True)])(lambda args=args: pipe_cage(*args))


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
    if lk.MODELS:
        lk.main()
    if w.MODELS:
        w.run()
    if kit.n.OBJECTS or kit.n.MODELS:
        kit.n.run()


if __name__ == "__main__":
    main()
