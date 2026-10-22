"""The dart MINEMAZE's, GAUNTLET's and ASTEROIDS' hatch ships fire (sheet S sprite 9, 1x1; enemy 592 of episodes 1-5,
launched every 20 game frames by the grey hatch ship S 93 (enemy 590, polish_hatch_ship.py: its hatch opens on the red
eye, S 131, as it fires), in MINEMAZE (13 hatch ships in the sky, one on the ground2 layer), GAUNTLET (10, sky) and
ASTEROIDS (1, sky); never placed by a level event of its own; flying straight down the screen, (0, 4), not aimed;
armour 3). Polished (2026-10-22; nothing replaced: no generator made a model of S 9 and models.cfg had no line for it,
so the game drew it as its sprite with volume).

S 9 is the asteroid levels' white dart (D 171, polish_launched_darts.py's white_dart) repainted: its outline is D 171's
pixel for pixel (and x5e 171's) - the body three pixels wide, the two sets of diamond fins (rows 0-4 and 5-9, nine
pixels across at rows 1-2 and 6-7), the band round the body near its nose (row 10, columns 4-6) and the dark point
(row 12) - and its band steps through the same colours: S 9 0x74 0x78 0x74 (D 171's), S 10 0x76 0x7a 0x75 (D 190's
0x76 0x7a 0x76), S 28 0x79 0x7c 0x78 (between D 190 and D 209), S 29 0x7b 0x7e 0x7a (D 209's 0x7a 0x7e 0x7a); its
animation 9 9 10 10 28 28 29 29 28 28 10 10 pulses the band from dark red to yellow and back. Only the greys differ:
S 9 is shaded more (dark grooves 0x05-0x09 beside the light middle stripe, a white glint 0x0f at the top of the body,
the lower fins' tips dark grey 0x05 instead of the outline), the look the white dart's lit model already has in the
game. So S 9 shows white_dart, its frames white_dart_190 and white_dart_209, and the one band D lacks, S 28's, is a new
frame model built here: white_dart_s28, polish_launched_darts.white_dart() with the band 0x79 (emission 0.39) and its
crown 0x7c (0.5), between D 190's (0x76 0.3, 0x7a 0.42) and D 209's (0x7a 0.42, 0x7e 0.58). The same mesh as
white_dart (the same bounds: the game, which centres it in height, keeps it in place). No other enemy shows S 9, 10,
28 or 29 (launched ones included), so the frame lines are safe.

Coordinates as in polish_launched_darts.py: authored with its nose up the screen, for yaw=velocity (it points along its
path, down the screen); origin at the sprite's centre. models.cfg (new): model white_dart_s28
enemies/white_dart_s28.glb; sprite s 9 white_dart yaw=velocity glow=6:0.3:120:-0.5:3.5 (the band: the same place as
D 171's), frame s 10 white_dart_190, frame s 28 white_dart_s28, frame s 29 white_dart_209.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of white_dart
and its frame models against S 9, 10, 28 and 29, turned down the screen as the game shows them; only white_dart_s28 is
exported), --preview <prefix>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_launched_darts as darts  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import check_frames, turn  # noqa: E402

# S 28's band: its sides and its crown (palette index, emission strength), between D 190's and D 209's.
S28_BAND = ((0x79, 0.39), (0x7c, 0.5))
# The white dart's band per S frame, as polish_launched_darts.DART_FRAMES has them (171 = S 9, 190 = S 10, 209 = S 29).
S_FRAMES = [(9, 171), (10, 190), (28, 28), (29, 209)]


def build():
    options = k.args()
    darts.DART_FRAMES.setdefault(28, S28_BAND)
    if "check" in options:
        # white_dart and its frame models (built here only for the check) against S's frames.
        sheet = os.path.join(options["check"], "enemy_S.png")
        for sprite, frame in S_FRAMES:
            k.reset()
            objects = darts.white_dart(f"dart_{sprite}", frame)
            triangulate(objects)
            bpy.context.view_layer.update()
            check_frames(objects, sheet, [(sprite, turn(180), f"S {sprite} ({'white_dart' if frame != 28 else 's28'}"
                                                                   f"{'' if frame in (171, 28) else '_%d' % frame})")],
                         move_to_frame=False)
    k.reset()
    objects = darts.white_dart("white_dart_s28", 28)
    triangulate(objects)
    bpy.context.view_layer.update()
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("white_dart_s28", objects, os.path.join(mk.outdir(options), "white_dart_s28.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "white_dart_s28", objects, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
