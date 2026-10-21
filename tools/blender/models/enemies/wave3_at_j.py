"""Batch AT of wave 3 (the second animation pass), sheet J: the green shell of TORM and the botany levels, whose frames
open its eye, for frame lines. Built by batch M's own builders (wave3_m_shell.py, imported as it is, its output
unchanged) and posed as the frames draw it (models.cfg: as its first frame's models, yaw=0). (TORM's eye orb's frames:
polish_eye_orb.py.)

- green_shell_<sprite> (J 241, 243, 231, 233; enemies 774, 775, the green shell's eye housing, green_shell_241 and
  _243): the eye opens when the shell fires, 241 231 231 231 241 (and 243 233 ... 243): the sprites draw it dark in
  its ring (241, 243) and then glowing green, all of it (231, 233). wave3_m_shell's shell has the eye half hidden
  under two lids; here 241 and 243 have the lids shut over it (the shell as it is most of the time, frame lines on
  241 and 243 themselves) and 231 and 233 have them drawn back into the ring, the whole eye glowing brighter. The
  whole shell is built and cut as green_shell_241 and _243 are (the eye lies across both).
usage: Blender -b --factory-startup -P wave3_at_j.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

ms = kit.quiet_import("wave3_m_shell")
kit.forget()
w = kit.w
sh = kit.sh
pal = kit.pal
J = "enemy_J"


# --- The green shell's eye -----------------------------------------------------------------------------------------

def shell_eye(open_):
    """wave3_m_shell's whole shell with its lids shut over a dark eye (open_ False) or drawn back into the ring, the
    eye glowing (True)."""
    ms.shell_whole()
    eye = bpy.data.objects["eye"]
    zs = [v.co.z for v in eye.data.vertices]
    xs = [v.co.x for v in eye.data.vertices]
    ys = [v.co.y for v in eye.data.vertices]
    ex, ey = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    ez = (min(zs) + max(zs)) / 2 + 0.4             # as wave3_m_shell places the eye
    kit.remove(["lid-1", "lid1"])
    lid = pal("shell_grey7", 0x07, metallic=0.65, roughness=0.3)
    if open_:
        eye.data.materials[0] = pal("shell_eye_open", 0xc9, metallic=0.1, roughness=0.1, glow=1.6)
        bpy.data.objects["eye_core"].data.materials[0] = pal("shell_eye_core_open", 0xce, metallic=0.0,
                                                             roughness=0.05, glow=2.2)
        # The lids drawn back: thin crescents sunk into the ring at the eye's top and bottom.
        for s in (-1, 1):
            obj = w.sphere(f"lid{s}", (ex, ey + s * 3.4, ez - 0.9), (4.9, 3.0, 2.2), lid, 24, 10)
            sh.cut_planes([obj], [((ex, ey + s * 4.0, 0), (0, -s, 0))])
    else:
        eye.data.materials[0] = pal("shell_eye_dark", 0xc1, metallic=0.2, roughness=0.15)
        kit.remove(["eye_core"])
        # The lids shut: meeting over the eye's middle, a little higher than they are when half open.
        for s in (-1, 1):
            obj = w.sphere(f"lid{s}", (ex, ey + s * 0.2, ez + 0.2), (4.9, 4.7, 2.7), lid, 24, 10)
            sh.cut_planes([obj], [((ex, ey + s * 0.08, 0), (0, -s, 0))])


def shell_piece(i, j, open_):
    """The piece (i, j) of the shell (as wave3_m_shell.shell_piece cuts it) with its eye as shell_eye makes it."""
    shell_eye(open_)
    w.bake()
    x0 = -48 + 24 * i if j < 3 else -36 + 24 * i
    y1 = 56 - 28 * j
    w.piece(w.meshes(), x0, x0 + 24, y1 - 28, y1)


for s, i, open_ in ((241, 1, False), (243, 2, False), (231, 1, True), (233, 2, True)):
    w.model(f"green_shell_eye_{s}", [(J, s, True)])(
        lambda i=i, open_=open_: shell_piece(i, 2, open_))


if __name__ == "__main__":
    w.run()
