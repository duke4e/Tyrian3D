"""The Ice Beam's and the Ice Blast's shot (shots2 sheet sprites 134-154, all 1x1: 12 x 14 cells: the frames of one
animation), modelled (2026-10-30, round 3 of the energy shots' models; until then each frame was drawn as its sprite
with volume, flat, from the 4x sheets, with the automatic glow).

Who fires it: two special weapons of stype 1 ("weapon": varz.c JE_specialComplete), each firing its weapon once on
every new press of the fire button (JE_doSpecialShot: a press, not a held button; shotrepeat 1): the Ice Beam (special
5, weapon 621: one shot straight up the screen at 8 pixels a tick) and the Ice Blast (special 42, weapon 706: five at
once, fanned out: sx 0, -1, 1, -2, 2 and sy 8, 7, 7, 5, 5). Nothing else fires these sprites. The shot's sprite is
634 (shots2 134) and it animates (weapani 20: a player's shot shows weapani + 1 = 21 frames, 134 to 154, a tick each)
but lives only 20 ticks (del 20: shotAvail, counted down each tick), so it shows 134 to 153 and is gone before 154,
which the game never draws (modelled all the same). Its damage 99 is ice: an enemy it hits is frozen (iced 40 ticks)
and the shot is gone (tyrian2.c).

As the sprites draw it: a spray of ice flying up the screen and shrinking to sparks as it goes. 134-140: a wide cap of
ice 12 pixels across (rows 2-8), white (0x8f) in its middle and blue round it (ramp 9: 0x9c, 0x9a, the darker 0x97
0x94 at its edge), its ends drooping at the cell's sides; under it a trail of blue chips down the middle (rows 8-13)
and drops falling off its left end (136-140). 141-147: the cap smaller (7-9 across), a cross of ice with a short stem
and sparks scattered below. 148-151: a small blue star (5 across) with a thin tail of light blue (0x9d 0x9f) below.
152-154: a few dim blue sparks. From 143 on every frame has a stray black pixel (0xfe) at column 3, row 6, left of the
ice: a speck in the original sheet, left out.

The models: a model per frame (every frame changes its shape: the cap shrinks, the trail's chips and sparks move; no
frame only shrinks, so scale= serves none), each built from its sprite's pixels. The cap: a crystal of ice round on top
and flat underneath (the game's camera only ever sees shots from above), its outline the head's pixels as seen from
its bright middle along 12-24 spokes (by its size), the ridges' a little further out and the valleys' a little less (a
star's edge: points of ice), cut in facets like a star-cut gem: its height falls from a peak over its middle to its
edge, every other spoke a ridge (standing higher) and the spokes between them valleys, the faces flat, so that the
facets catch the sun each its own way. Its colours in rings round the middle (the mesh's own rings, no face cut): white
(0x8f) over its middle and out to 0.78 of the way, light blue (0x9e), then the blue of its edge (0x9a), a frame's whole
ramp a shade or more darker as the sprites dim (by the brightest pixels of the frame's head: 134-147 white, 148-150
light blue, 151 blue, 152 and 153-154 darker). The trail: every other group of pixels an ice chip, in the palette
colour of its brightest pixel (the nearest of the ramp): the stem below the cap (a group of three rows or more) a
smooth tapered icicle along the straight line fitted through its rows (the pixels' zigzag read as a lightning bolt, a
chip per row as a stack of plates), a group in one column a thin faceted shard, any other each row's run of pixels a
little four-sided pyramid (the drops and sparks). Each band glows in its own colour (0.24-0.55: pale ice glows most).
2-5 materials; 150-340 triangles a frame. The first version (blue rings round a small white middle, the stem as
chips) read as a blue fan next to the sprites' white caps in a white glow: the white now reaches out to 0.78, the
relief is higher and the glow paler and stronger.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the ice stands on z = 0
(the game centres shot models in height on the player's layer).

models.cfg (the shots section): the build prints the model and shot lines (a glow= of pale blue (0x9f) round each
frame's cap, as wide as it + 6 and weaker as it dims: 0.6 to 0.3).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_ice.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each frame's top view against its sprite in
     <dir>/shots2.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views, and
     <prefix>frames_game.png: the frames in a row as the game shows them)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import grid, lit, check_frames, turn  # noqa: E402
from polish_shot_starburst import game_camera  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")

# --- The sprites (palette indices, '..' transparent): the 21 frames ---------------------------------------------------

SPRITES = {
    134: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 97 9c 9c 9c 97 .. .. ..
.. .. 9a 9c 9c 8f 8f 8f 9c 9c 97 ..
.. 97 9c 8f 8f 8f 8f 8f 8f 8f 9c ..
.. 9c 8f 9c 8f 8f 8f 8f 8f 9c 8f 97
9a 9c 9c 94 9c 8f 8f 8f 9c 94 9a 9c
9a 95 .. .. 94 9c 8f 9c 94 .. .. 9a
94 .. .. .. .. 9a 9e 9a .. .. .. 94
.. .. .. .. .. 98 9c 96 .. .. .. ..
.. .. .. .. .. .. 9a 94 .. .. .. ..
.. .. .. .. .. 9a 94 .. .. .. .. ..
.. .. .. .. .. .. 9a .. .. .. .. ..
.. .. .. .. .. .. .. 94 .. .. .. ..
""",
    135: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 97 9c 9c 9c 97 .. .. ..
.. .. 9a 9c 9c 8f 8f 8f 9c 9c 97 ..
.. 96 9c 8f 8f 8f 8f 8f 8f 8f 9c ..
94 99 8f 9f 8f 8f 8f 8f 8f 9f 8f 9a
94 9b 9b 94 9c 8f 8f 8f 9c 94 9c 9a
.. 95 .. .. 94 9c 8f 9c 94 .. .. 96
.. 99 .. .. .. 9a 9e 9a .. .. .. ..
.. .. .. .. .. 98 9c 96 .. .. .. ..
.. .. .. .. .. .. 9a 94 .. .. .. ..
.. .. .. .. .. 94 97 .. .. .. .. ..
.. .. .. .. .. .. 98 .. .. .. .. ..
.. .. .. .. .. .. 92 93 .. .. .. ..
""",
    136: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 97 9c 9c 9c 97 .. .. ..
.. .. 97 9a 9c 8f 8f 8f 9c 9c 97 ..
.. 95 9c 8f 8f 8f 8f 8f 8f 8f 9c 93
.. 98 89 8a 8f 8f 8f 8f 8f 89 89 97
.. 93 9b 94 9d 8f 8f 8f 9e 94 9c 97
.. 93 .. .. 95 9d 8f 9e 95 .. .. 93
.. 94 .. .. .. 9a 9e 9b .. .. .. ..
.. 99 .. .. .. 98 9c 96 .. .. .. ..
.. .. .. .. .. .. 96 98 .. .. .. ..
.. .. .. .. .. 92 9b .. .. .. .. ..
.. .. .. .. .. .. 94 95 .. .. .. ..
.. .. .. .. .. .. 95 .. .. .. .. ..
""",
    137: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 95 9c 9c 9c 95 .. .. ..
.. .. 95 9a 9c 8f 8f 8f 9c 9a 93 ..
.. 93 9c 9f 8f 8f 8f 8f 8f 9f 9a ..
.. 94 9c 8f 8f 8f 8f 8f 8f 8f 9c ..
.. .. 99 94 9d 8f 8f 8f 9e 94 9a ..
.. .. .. .. 95 9d 8f 9e 95 .. .. ..
.. 93 .. .. .. 9a 9e 9b .. .. .. ..
.. 95 .. .. .. 94 9c 9a .. .. .. ..
.. 99 .. .. .. .. 95 9b .. .. .. ..
.. .. .. .. .. .. 9c 94 .. .. .. ..
.. .. .. .. .. .. 92 99 .. .. .. ..
.. .. .. .. .. 92 94 .. .. .. .. ..
""",
    138: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 95 9c 9c 9c 95 .. .. ..
.. .. 95 9a 9c 8f 8f 8f 9c 9a 93 ..
.. 93 9c 9f 8f 8f 8f 8f 8f 9f 9a ..
.. 94 9c 8f 8f 8f 8f 8f 8f 8f 9c ..
.. .. 99 94 9d 8f 8f 8f 9e 94 9a ..
.. .. .. .. 95 9d 8f 9e 95 .. .. ..
.. .. .. .. .. 9a 9e 9b .. .. .. ..
.. 92 .. .. .. 98 9c 96 .. .. .. ..
.. 94 .. .. .. .. 96 98 .. .. .. ..
.. 97 .. .. .. 92 9b .. .. .. .. ..
.. .. .. .. .. .. 94 95 .. .. .. ..
.. .. .. .. .. .. 95 .. .. .. .. ..
""",
    139: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 93 99 9c 9a 93 .. .. ..
.. .. 93 9a 9a 9f 8f 9f 9c 9a .. ..
.. .. 9c 9e 8f 8f 8f 8f 8f 9e 98 ..
.. .. 9c 9f 8f 8f 8f 8f 8f 9f 9a ..
.. .. 99 94 9d 8f 8f 8f 9e 94 96 ..
.. .. .. .. 94 9d 8f 9e 94 .. .. ..
.. .. .. .. .. 9a 9e 9b .. .. .. ..
.. .. .. .. .. 94 9c 96 .. .. .. ..
.. .. .. .. .. .. 96 9b .. .. .. ..
.. 93 .. .. .. 94 9a .. .. .. .. ..
.. 95 .. .. .. .. 93 97 .. .. .. ..
.. .. .. .. .. 92 94 .. .. .. .. ..
""",
    140: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 93 99 9c 9a 93 .. .. ..
.. .. 91 9a 9a 9f 8f 9f 9c 9a .. ..
.. .. 99 9e 8f 8f 8f 8f 8f 9e 96 ..
.. .. 99 9f 8f 8f 8f 8f 8f 9f 98 ..
.. .. 96 94 9d 8f 8f 8f 9e 94 93 ..
.. .. .. .. 94 9d 8f 9e 94 .. .. ..
.. .. .. .. .. 9a 9e 9b .. .. .. ..
.. .. .. .. .. 94 9c 96 .. .. .. ..
.. .. .. .. .. .. 94 9c .. .. .. ..
.. .. .. .. .. 96 98 .. .. .. .. ..
.. 92 .. .. .. .. 92 99 .. .. .. ..
.. 93 .. .. .. 94 93 .. .. .. .. ..
""",
    141: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 97 9c 9a .. .. .. ..
.. .. .. 98 9a 9f 8f 9f 9c 96 .. ..
.. .. 95 9b 9f 8f 8f 8f 9f 9a 94 ..
.. .. 96 9d 8f 8f 8f 8f 8f 9f 96 ..
.. .. .. .. 99 8f 8f 8f 9d .. .. ..
.. .. .. .. .. 9b 8f 9c .. .. .. ..
.. .. .. .. .. 9a 9f 9b .. .. .. ..
.. .. .. .. .. 93 9a 94 .. .. .. ..
.. .. .. .. .. .. 93 9d .. .. .. ..
.. .. .. .. .. 99 94 .. .. .. .. ..
.. .. .. .. .. .. 92 9a .. .. .. ..
.. .. .. .. .. 95 92 .. .. .. .. ..
""",
    142: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 95 9a 98 .. .. .. ..
.. .. .. 95 99 9e 8f 9d 9a 93 .. ..
.. .. 93 9b 9d 8f 8f 8f 9f 98 .. ..
.. .. 93 9b 9f 8f 8f 8f 9f 9c 93 ..
.. .. .. .. 99 9f 8f 9f 9d .. .. ..
.. .. .. .. .. 9b 9f 9c .. .. .. ..
.. .. .. .. .. 98 9d 99 .. .. .. ..
.. .. .. .. .. 93 98 93 .. .. .. ..
.. .. .. .. .. .. .. 9a 95 .. .. ..
.. .. .. .. .. 9b .. .. .. .. .. ..
.. .. .. .. .. .. .. 9d .. .. .. ..
.. .. .. .. 93 97 .. .. .. .. .. ..
""",
    143: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 94 9a 96 .. .. .. ..
.. .. .. 93 99 9c 8f 9b 9a .. .. ..
.. .. .. 99 9b 9f 8f 8f 9d 97 .. ..
.. .. .. 98 9d 8f 8f 8f 9d 9a .. ..
.. .. .. fe 99 9f 8f 9f 9b .. .. ..
.. .. .. .. .. 9a 9e 9b .. .. .. ..
.. .. .. .. .. 95 9b 95 .. .. .. ..
.. .. .. .. .. 91 95 91 .. .. .. ..
.. .. .. .. .. .. .. 95 96 .. .. ..
.. .. .. .. .. 97 .. .. .. .. .. ..
.. .. .. .. .. .. .. 9b 97 .. .. ..
.. .. .. .. 97 93 .. .. .. .. .. ..
""",
    144: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 93 98 93 .. .. .. ..
.. .. .. .. 96 9c 9f 99 98 .. .. ..
.. .. .. 94 99 9f 8f 9f 99 94 .. ..
.. .. .. 94 9d 8f 8f 8f 9d 98 .. ..
.. .. .. fe 97 9f 8f 9f 98 .. .. ..
.. .. .. .. .. 97 9e 97 .. .. .. ..
.. .. .. .. .. 93 9b 93 .. .. .. ..
.. .. .. .. .. 91 93 91 .. .. .. ..
.. .. .. .. .. .. .. .. 98 .. .. ..
.. .. .. .. 95 93 .. .. .. .. .. ..
.. .. .. .. .. .. .. 93 99 .. .. ..
.. .. .. 94 97 92 .. .. .. .. .. ..
""",
    145: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 93 98 93 .. .. .. ..
.. .. .. .. 96 9c 9f 99 98 .. .. ..
.. .. .. 94 99 9f 8f 9f 99 94 .. ..
.. .. .. 94 9d 8f 8f 8f 9d 98 .. ..
.. .. .. fe 97 9f 8f 9f 98 .. .. ..
.. .. .. .. .. 97 9e 97 .. .. .. ..
.. .. .. .. .. 93 9b 93 .. .. .. ..
.. .. .. .. .. 91 93 91 .. .. .. ..
.. .. .. .. .. .. .. .. 94 95 .. ..
.. .. .. 92 95 .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. 98 93 .. ..
.. .. .. 96 93 .. .. .. .. .. .. ..
""",
    146: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 93 96 93 .. .. .. ..
.. .. .. .. 94 99 9c 99 95 .. .. ..
.. .. .. 94 99 9f 8f 9f 99 95 .. ..
.. .. .. 93 9c 8f 8f 8f 9c 93 .. ..
.. .. .. fe 97 9f 8f 9f 96 .. .. ..
.. .. .. .. .. 9a 9f 99 .. .. .. ..
.. .. .. .. .. 93 9d 93 .. .. .. ..
.. .. .. .. .. 91 9b 91 .. .. .. ..
.. .. .. .. .. .. 93 .. 92 93 .. ..
.. .. .. 94 93 .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. 93 95 .. ..
.. .. .. 94 .. .. .. .. .. .. .. ..
""",
    147: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 93 .. .. .. .. ..
.. .. .. .. .. 96 9a 97 .. .. .. ..
.. .. .. .. 97 9b 8f 9f 99 .. .. ..
.. .. .. 92 9a 8f 8f 8f 9a 91 .. ..
.. .. .. fe 96 9b 9f 9b 94 .. .. ..
.. .. .. .. .. 99 8f 97 .. .. .. ..
.. .. .. .. .. 93 9f 93 .. .. .. ..
.. .. .. .. .. 91 9b 91 .. .. .. ..
.. .. .. .. .. .. 95 .. .. 92 .. ..
.. .. .. 92 .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. 93 .. ..
.. .. 91 .. .. .. .. .. .. .. .. ..
""",
    148: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 93 98 95 .. .. .. ..
.. .. .. .. 93 99 8f 9b 96 .. .. ..
.. .. .. .. 99 8a 9d 8c 97 91 .. ..
.. .. .. fe 96 9d 9b 9d 92 .. .. ..
.. .. .. .. .. 99 9f 97 .. .. .. ..
.. .. .. .. .. 93 8f 93 .. .. .. ..
.. .. .. .. .. 91 9d 91 .. .. .. ..
.. .. .. .. .. .. 96 .. .. .. .. ..
.. .. .. .. .. .. 93 .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    149: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 96 93 .. .. .. ..
.. .. .. .. .. 97 8d 9b 93 .. .. ..
.. .. .. .. 97 9e 9b 9f 95 .. .. ..
.. .. .. fe 94 9b 99 9b .. .. .. ..
.. .. .. .. .. 97 9a 94 .. .. .. ..
.. .. .. .. .. 93 9c 93 .. .. .. ..
.. .. .. .. .. 91 9f 91 .. .. .. ..
.. .. .. .. .. .. 9d .. .. .. .. ..
.. .. .. .. .. .. 94 .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    150: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 94 .. .. .. .. ..
.. .. .. .. .. 95 9f 99 .. .. .. ..
.. .. .. .. 95 9c 99 9c 93 .. .. ..
.. .. .. fe 92 99 93 99 .. .. .. ..
.. .. .. .. .. 93 94 92 .. .. .. ..
.. .. .. .. .. .. 95 .. .. .. .. ..
.. .. .. .. .. .. 9a .. .. .. .. ..
.. .. .. .. .. .. 9f .. .. .. .. ..
.. .. .. .. .. .. 9b .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    151: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 93 .. .. .. .. ..
.. .. .. .. .. 93 9b 95 .. .. .. ..
.. .. .. .. .. 99 9d 9a .. .. .. ..
.. .. .. fe .. 95 93 96 .. .. .. ..
.. .. .. .. .. 93 91 93 .. .. .. ..
.. .. .. .. .. .. 92 .. .. .. .. ..
.. .. .. .. .. .. 94 .. .. .. .. ..
.. .. .. .. .. .. 9a .. .. .. .. ..
.. .. .. .. .. .. 9e .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    152: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 99 93 .. .. .. ..
.. .. .. .. .. 94 9a 97 .. .. .. ..
.. .. .. fe .. 93 92 93 .. .. .. ..
.. .. .. .. .. 91 .. 91 .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 92 .. .. .. .. ..
.. .. .. .. .. .. 95 .. .. .. .. ..
.. .. .. .. .. .. 9b .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    153: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 94 91 .. .. .. ..
.. .. .. .. .. 92 98 94 .. .. .. ..
.. .. .. fe .. 91 92 91 .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 93 .. .. .. .. ..
.. .. .. .. .. .. 98 .. .. .. .. ..
""",
    154: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 91 .. .. .. .. ..
.. .. .. .. .. 91 93 91 .. .. .. ..
.. .. .. fe .. .. 91 .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. 92 .. .. .. .. ..
.. .. .. .. .. .. 93 .. .. .. .. ..
""",
}

# --- The frames -------------------------------------------------------------------------------------------------------
# Each frame's head: its pixels in rows up to HEAD_LAST (the cap, down to where it narrows into its stem) in the biggest
# group of touching pixels there; every other group of pixels (the stem, drops, sparks) a chip of the trail. The stray
# black pixel is left out.
STRAY = 0xfe
HEAD_LAST = {134: 8, 135: 8, 136: 8, 137: 8, 138: 8, 139: 8, 140: 8, 141: 9, 142: 9, 143: 9, 144: 9, 145: 9, 146: 9,
             147: 9, 148: 9, 149: 9, 150: 7, 151: 7, 152: 7, 153: 6, 154: 6}
# The ice's ramp from the deep blue of an edge to the white (palette indices), each glowing in its own colour, the paler
# the more.
RAMP = (0x94, 0x97, 0x9a, 0x9c, 0x9e, 0x8f)
GLOW = {0x94: 0.24, 0x97: 0.28, 0x9a: 0.32, 0x9c: 0.36, 0x9e: 0.42, 0x8f: 0.55}
ROUGHNESS = 0.3
# A frame's level: the ramp's index its cap's middle takes, by the brightest pixels of its head (3 or more of ramp 8's
# white 0x8f: the white; any pale pixel: light blue; ...).
LEVELS = ((5, {0x8f}, 3), (4, {0x8f, 0x8e, 0x8d, 0x8c, 0x8a, 0x9e, 0x9f}, 1), (3, {0x9c, 0x9d}, 1),
          (2, {0x9a, 0x9b}, 1))
# The cap: its spokes, its rings (fractions of the way out to the outline), each ring's height (a fraction of the cap's
# height: the ridges'; the valleys' VALLEY of it), the peak over the middle, the cap's height over its mean radius,
# how many shades below the frame's level each ring's faces are (the middle's fan, then between the rings).
SPOKES = ((5, 12), (9, 16), (99, 24))  # (up to this many pixels across: spokes)
RINGS = (0.3, 0.6, 0.78, 0.92, 1.0)
RING_HEIGHT = (0.92, 0.76, 0.52, 0.26, 0.0)
VALLEY, PEAK, DEPTH = 0.74, 1.2, 0.6
SHADES = (0, 0, 0, 1, 3)
# The ridges reach a little further out than the outline, the valleys a little less (a star's edge: ice's points).
SPIKE = 0.08
# The chips: a single pixel's pyramid (half-size, height), a group's shard (its half-width per pixel of its rows'
# width, at least SHARD_HALF; its height; how far its ends reach past its first and last rows' middles).
CHIP_HALF, CHIP_LIFT = 0.5, 0.6
SHARD_HALF, SHARD_LIFT, SHARD_REACH = 0.42, 0.62, 0.45


def luminance(index):
    r, g, b = k.level_palette()[index]
    return 0.3 * r + 0.59 * g + 0.11 * b


def nearest_in_ramp(index):
    """The ramp's index whose brightness is the nearest to the palette index's."""
    lum = luminance(index)
    return min(range(len(RAMP)), key=lambda i: abs(luminance(RAMP[i]) - lum))


def groups(cells):
    """The groups of touching cells (8 neighbours) of a set of (row, col)."""
    left, out = set(cells), []
    while left:
        stack = [left.pop()]
        group = set(stack)
        while stack:
            r, c = stack.pop()
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    n = (r + dr, c + dc)
                    if n in left:
                        left.remove(n)
                        group.add(n)
                        stack.append(n)
        out.append(group)
    return out


def frame_parts(sprite):
    """The frame's head (a set of (row, col)), its trail's groups and the pixels' palette indices."""
    rows = grid(SPRITES[sprite])
    cells = {(r, c): v for r, row in enumerate(rows) for c, v in enumerate(row) if v is not None and v != STRAY}
    upper = [g for g in groups([rc for rc in cells if rc[0] <= HEAD_LAST[sprite]])]
    head = max(upper, key=len)
    trail = groups([rc for rc in cells if rc not in head])
    return head, trail, cells


def level_of(head, cells):
    values = [cells[rc] for rc in head]
    for level, indices, count in LEVELS:
        if sum(1 for v in values if v in indices) >= count:
            return level
    return 1


def centre_of(head, cells):
    """The middle of the head's light: its pixels' centres weighted by the square of their brightness."""
    w = [(luminance(cells[rc]) ** 2, rc) for rc in head]
    total = sum(a for a, _ in w)
    return (sum(a * (c + 0.5 - 6.0) for a, (r, c) in w) / total, sum(a * (6.5 - r) for a, (r, c) in w) / total)


def outline(head, centre, spokes):
    """The head's outline as a radius per spoke: the farthest point along it inside the head's pixels (each a unit
    square), smoothed a little round the spokes, the ridges' (every other spoke) SPIKE further out and the valleys'
    SPIKE less."""
    cx, cy = centre
    radii = []
    for i in range(spokes):
        phi = 2 * math.pi * i / spokes
        far = 0.3
        for step in range(1, 200):
            d = step * 0.05
            x, y = cx + d * math.cos(phi), cy + d * math.sin(phi)
            if (math.floor(7.0 - y), math.floor(x + 6.0)) in head:
                far = d
        radii.append(far)
    smooth = [0.25 * radii[i - 1] + 0.5 * radii[i] + 0.25 * radii[(i + 1) % spokes] for i in range(spokes)]
    return [r * (1.0 + SPIKE if i % 2 == 0 else 1.0 - SPIKE) for i, r in enumerate(smooth)]


def mesh(name, verts, faces, bands, materials):
    """A mesh of these faces, each taking materials[bands[i]] (a slot for each material the faces use)."""
    obj = k.mesh_object(name, verts, faces)
    slots = []
    for b in sorted(set(bands)):
        if materials[b] not in slots:
            slots.append(materials[b])
            obj.data.materials.append(materials[b])
    for poly, b in zip(obj.data.polygons, bands):
        poly.material_index = slots.index(materials[b])
    return obj


def wound(verts, face, up):
    """The face turned so that its normal points up (or down)."""
    p = [Vector(verts[v]) for v in face]
    normal = (p[1] - p[0]).cross(p[2] - p[0])
    return tuple(reversed(face)) if (normal.z < 0) == up else tuple(face)


def cap(name, head, cells, level, materials):
    """The head: a star-cut crystal over its outline, its peak over the middle of its light, ridges on every other
    spoke, its rings' faces in the ramp's shades below the frame's level; a flat underside."""
    centre = centre_of(head, cells)
    cols = [c for _, c in head]
    spokes = next(n for most, n in SPOKES if max(cols) - min(cols) + 1 <= most)
    radii = outline(head, centre, spokes)
    height = DEPTH * sum(radii) / len(radii)
    cx, cy = centre
    verts = [(cx, cy, height * PEAK)]
    for f, h in zip(RINGS, RING_HEIGHT):
        for i, r in enumerate(radii):
            phi = 2 * math.pi * i / spokes
            z = height * h * (1.0 if i % 2 == 0 else VALLEY)
            verts.append((cx + f * r * math.cos(phi), cy + f * r * math.sin(phi), z))
    bottom = len(verts)
    verts.append((cx, cy, 0.0))
    faces, bands = [], []

    def band(ring):
        return max(level - SHADES[ring], 0)
    for i in range(spokes):
        j = (i + 1) % spokes
        faces.append(wound(verts, (0, 1 + i, 1 + j), True))
        bands.append(band(0))
    for ring in range(len(RINGS) - 1):
        a, b = 1 + ring * spokes, 1 + (ring + 1) * spokes
        for i in range(spokes):
            j = (i + 1) % spokes
            faces.append(wound(verts, (a + i, b + i, b + j, a + j), True))
            bands.append(band(ring + 1))
    last = 1 + (len(RINGS) - 1) * spokes
    for i in range(spokes):
        j = (i + 1) % spokes
        faces.append(wound(verts, (bottom, last + i, last + j), False))
        bands.append(band(len(RINGS) - 1))
    return k.smooth(mesh(name, verts, faces, bands, materials), 10), centre, radii


def chip(group, cells):
    """A chip of the trail: (verts, faces, its ramp index). A single pixel a four-sided pyramid; a group a faceted
    shard along its rows' middles, tapering at its ends."""
    index = max((cells[rc] for rc in group), key=luminance)
    ramp = nearest_in_ramp(index)
    rows = sorted({r for r, _ in group})
    if len(group) == 1:
        (r, c), = group
        x, y = c + 0.5 - 6.0, 6.5 - r
        verts = [(x + CHIP_HALF, y, 0.0), (x, y + CHIP_HALF, 0.0), (x - CHIP_HALF, y, 0.0), (x, y - CHIP_HALF, 0.0),
                 (x, y, CHIP_LIFT)]
        faces = [wound(verts, f, True) for f in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4))]
        faces.append(wound(verts, (0, 1, 2, 3), False))
        return verts, faces, ramp
    # (a shard: down its rows, or across one row)
    if len(rows) == 1:
        cols = sorted(c for _, c in group)
        y = 6.5 - rows[0]
        path = [(cols[0] + 0.5 - 6.0 - SHARD_REACH, y, 0.5), (cols[0] + 0.5 - 6.0, y, 0.5),
                (cols[-1] + 0.5 - 6.0, y, 0.5), (cols[-1] + 0.5 - 6.0 + SHARD_REACH, y, 0.5)]
    else:
        # (down the straight line fitted through its rows' middles: a smooth icicle, not the pixels' zigzag; as wide
        # as its widest row at its top, narrowing down it)
        mids = []
        for r in rows:
            cols = [c for rr, c in group if rr == r]
            mids.append(((min(cols) + max(cols) + 1) / 2 - 6.0, 6.5 - r, 0.5 * (max(cols) - min(cols) + 1)))
        n = len(mids)
        my = sum(m[1] for m in mids) / n
        mx = sum(m[0] for m in mids) / n
        slope = sum((m[1] - my) * (m[0] - mx) for m in mids) / max(sum((m[1] - my) ** 2 for m in mids), 1e-9)
        widest = max(m[2] for m in mids)
        path = []
        for i, (_, y, _) in enumerate(mids):
            f = i / (n - 1)
            path.append((mx + slope * (y - my), y, widest * (1.0 - 0.55 * f)))
        (x0, y0, _), (x1, y1, _) = path[0], path[1]
        d = math.hypot(x0 - x1, y0 - y1) or 1.0
        path.insert(0, (x0 + (x0 - x1) / d * SHARD_REACH, y0 + (y0 - y1) / d * SHARD_REACH, 0.5))
        (x0, y0, _), (x1, y1, _) = path[-1], path[-2]
        d = math.hypot(x0 - x1, y0 - y1) or 1.0
        path.append((x0 + (x0 - x1) / d * SHARD_REACH, y0 + (y0 - y1) / d * SHARD_REACH, 0.5))
    verts, faces = [], []
    across = 5
    count = len(path)
    for i, (x, y, half) in enumerate(path):
        ax, ay, _ = path[max(i - 1, 0)]
        bx, by, _ = path[min(i + 1, count - 1)]
        length = math.hypot(bx - ax, by - ay) or 1.0
        nx, ny = -(by - ay) / length, (bx - ax) / length
        end = i in (0, count - 1)
        w = 0.06 if end else max(half, SHARD_HALF)
        lift = 0.05 if end else SHARD_LIFT
        for j in range(across):
            a = math.pi * j / (across - 1)
            verts.append((x + nx * w * math.cos(a), y + ny * w * math.cos(a), lift * math.sin(a)))
    for i in range(count - 1):
        for j in range(across - 1):
            a, b = i * across + j, (i + 1) * across + j
            faces.append(wound(verts, (a, b, b + 1, a + 1), True))
        under = (i * across, (i + 1) * across, (i + 1) * across + across - 1, i * across + across - 1)
        faces.append(wound(verts, under, False))
    return verts, faces, ramp


def pieces(group):
    """A trail's group as its chips: a group of three rows or more (the stem) or in one column a shard down it; any
    other each row's runs of touching pixels a chip of their own (a spray, not a wire)."""
    if len({c for _, c in group}) == 1 or len({r for r, _ in group}) >= 3:
        return [group]
    out = []
    for r in sorted({r for r, _ in group}):
        cols = sorted(c for rr, c in group if rr == r)
        run = [cols[0]]
        for c in cols[1:]:
            if c == run[-1] + 1:
                run.append(c)
            else:
                out.append({(r, cc) for cc in run})
                run = [c]
        out.append({(r, cc) for cc in run})
    return out


def trail(name, groups_, cells, materials):
    verts, faces, bands = [], [], []
    for g in [p for group in groups_ for p in pieces(group)]:
        vs, fs, ramp = chip(g, cells)
        base = len(verts)
        verts += vs
        faces += [tuple(base + v for v in f) for f in fs]
        bands += [ramp] * len(fs)
    return k.smooth(mesh(name, verts, faces, bands, materials), 10)


def material(index):
    return lit(f"ice_{index:02x}", index, GLOW[index], roughness=ROUGHNESS)


def build_model(name, sprite):
    """The frame's cap and trail; also its level, the cap's middle and its width (for the glow)."""
    head, trail_groups, cells = frame_parts(sprite)
    level = level_of(head, cells)
    materials = [material(i) for i in RAMP]
    head_obj, centre, radii = cap(name + "_cap", head, cells, level, materials)
    parts = [head_obj]
    if trail_groups:
        parts.append(trail(name + "_trail", trail_groups, cells, materials))
    cols = [c for _, c in head]
    return triangulate(parts), level, centre, max(cols) - min(cols) + 1


MODELS = [(f"shot_ice_{n}", n) for n in range(134, 155)]

# The shot lines' glow: a halo of light blue round the cap, its size the cap's width + GLOW_MARGIN, its strength by the
# frame's level.
GLOW_COLOUR, GLOW_MARGIN = 0x9f, 6
GLOW_STRENGTH = {5: 0.6, 4: 0.5, 3: 0.42, 2: 0.35, 1: 0.3}


def cfg_lines(info):
    """The models.cfg lines: the model lines, then a shot line per frame (info: name -> (sprite, level, centre,
    width))."""
    width = max(len(n) for n in info)
    lines = [f"model {n.ljust(width)} shots/{n}.glb" for n in info]
    for name, (sprite, level, centre, cap_width) in info.items():
        size = min(max(cap_width + GLOW_MARGIN, 7), 18)
        glow = f"glow={size}:{GLOW_STRENGTH[level]:g}:{GLOW_COLOUR}:{round(centre[0] * 20) / 20 + 0.0:g}:" \
               f"{round(-centre[1] * 20) / 20 + 0.0:g}"
        note = {134: "  # the spray of ice, as fired (134-140: the wide cap, an icicle stem)",
                141: "  # 141-147: the cap smaller, a cross with sparks", 148: "  # 148-151: a small star, a thin tail",
                152: "  # 152-154: sparks (154: never drawn, the shot lives 20 ticks)"}.get(sprite, "")
        lines.append(f"shot shots2 {sprite} {name.ljust(width)} {glow.ljust(28)}{note}".rstrip())
    return lines


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_view(prefix, objects):
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0, (512, 512))
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


def frames_view(prefix):
    """The 21 frames side by side in three rows of seven, each centred in height on its bounds as the game does, from
    the game's camera."""
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    for i, (name, sprite) in enumerate(MODELS):
        parts, _, _, _ = build_model(f"{name}_v", sprite)
        zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
        mk.transform(parts, Matrix.Translation(((i % 7 - 3) * 14.0, (1 - i // 7) * 16.0, -(max(zs) + min(zs)) / 2)))
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 104.0, (1400, 800))
    scene.render.filepath = prefix + "frames_game.png"
    bpy.ops.render.render(write_still=True)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    info = {}
    for name, sprite in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts, level, centre, width = build_model(name, sprite)
        info[name] = (sprite, level, centre, width)
        bpy.context.view_layer.update()
        print(f"== {name} (shots2 {sprite}): level {level}, the cap's middle ({centre[0]:.2f}, {centre[1]:.2f}), "
              f"{width} pixels across")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots2.png"), [(sprite, turn(0), f"shots2 {sprite}")],
                         move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    if "preview" in options and only is None:
        frames_view(options["preview"])
    print("models.cfg:")
    for line in cfg_lines(info):
        print("  " + line)


if __name__ == "__main__":
    build()
