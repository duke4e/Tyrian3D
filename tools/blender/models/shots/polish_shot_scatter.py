"""The Scatter Wave's shots (shots sheet sprites 285 and 170, both 1x1: 12 x 14 cells), modelled (2026-10-30, the third
round of the energy shots' models; until then each was drawn as its sprite with volume and the automatic glow). Built
with polish_shot_fireball.py's kit (the pulse's method: half-bodies on the bands' borders, a raised core).

Who fires them: the Scatter Wave rear (port 30, shop 2:1, 900), a volley every 4-5 frames, the balls flying out
sideways and up and down the screen at 10 pixels a frame:
  power  1: 285 285 (left, right)               power  6: 170 170 (left, right), 285 285 (up, down)
  power  2: 285 x 3 (left, right, down)         power  7: 170 x 4 (left and right, 8 above and below), 285 (down)
  power  3: 285 x 4 (left and right, 3 above and 4 below)   power  8: 170 x 4, 285 x 3
  power  4: 285 x 4 (the four ways)             power  9: 170 x 4, 285 x 4
  power  5: 285 x 6                             power 10: 170 x 6 (16 apart)   power 11: 170 x 6, 285 285
Enemies: weapon 117 (285 aimed at the player, by fire override events in episodes 4 and 5: UNDERDELI, LAVA RUN,
DREAD-NOT's turrets 312-314, 339, 435, 439 and 638). (The second player's turret of rear port 30 fires the Wild Ball's
steel ball, 126, weapon 448: not these.)

As the sprites draw them (ramp 7, the fire: 0x7a orange-yellow .. 0x7f white): 285 a ball 6 pixels across (columns
3-8, rows 4-9), yellow (0x7c, 0x7d) with a white-hot spot up and right of its middle (0x7f at columns 6-7 of rows 5-6,
0x7e round it) and an orange-yellow rim (0x7a, 0x7b) darkest down and left; 170 two of them one above the other
(rows 0-5 and 8-13).

The models: a ball of plasma (polish_shot_fireball.Dome, as the fireballs' balls: rings round the hot spot out to the
rim, the heat falling from white-hot there to the rim's orange-yellow, the rim's heat round the ball brighter up and
right (fourier_rim), the bands' borders swirling a little), round on top and flat underneath, a raised white core on
the hot spot (dome_core); shot_scatter one ball, shot_scatter_2 two (4 above and below the middle). 6 materials.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); built on z = 0.

models.cfg: see the block's comment.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_scatter.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (the silhouettes against <dir>/shots.png)
     [--preview <prefix>]
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402

# The ball: its middle (the cell's), radius, height over its radius, the hot spot, the heat there and round the rim
# (fourier_rim: brighter up and right), the fall, the swirl, the bands (orange-yellow at the rim to the pale yellow
# round the core), the core (half-axes across and along, lift, bands from its middle out).
BALL = dict(
    radius=3.05, depth=0.86, hot=(0.85, 0.9),
    heat=15.0, rim=kit.fourier_rim(10.6, 0.7, 45.0), fall=1.2, swirl=(0.2, 2, 2.2, 0.6), tongues=(5, 0.03, 1.3),
    segments=20,
    bands=[(-99.0, 0x7a, 0.5), (11.0, 0x7b, 0.52), (12.0, 0x7c, 0.56), (13.0, 0x7d, 0.58)],
    core=(1.15, 2.1, 0.34, ((0.0, 0x7f, 0.62), (0.45, 0x7e, 0.6))),
)
# name: (sprite, the balls' middles, what it is)
MODELS = {
    "shot_scatter": (285, [(0.0, 0.0)], "a ball of plasma"),
    "shot_scatter_2": (170, [(0.0, 4.0), (0.0, -4.0)], "two balls one above the other"),
}


def build_ball(name, centre):
    """One ball round centre: [dome, core]."""
    cx, cy = centre
    r = BALL["radius"]
    top, radius_from = kit.ellipse_dome(cx, cy, r, r, r * BALL["depth"])
    hot = (cx + BALL["hot"][0], cy + BALL["hot"][1])
    heat = kit.ball_heat(BALL["heat"], BALL["rim"], BALL["fall"], BALL["swirl"])
    dome = kit.Dome(hot, radius_from(*hot), top, heat, BALL["bands"], segments=BALL["segments"],
                    tongues=BALL["tongues"])
    fire = kit.materials("scatter_fire", BALL["bands"])
    parts = [dome.build(name + "_ball", fire)]
    w, length, lift, cbands = BALL["core"]
    cmats = kit.materials("scatter_core", cbands, kit.CORE_ROUGHNESS)
    parts.append(kit.dome_core(name + "_core", hot, w, length / 2, lift, top, cbands, cmats))
    return parts


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", kit.OUTDIR)
    for name, (sprite, centres, what) in MODELS.items():
        if only is not None and name not in only:
            continue
        k.reset()
        parts = []
        for i, c in enumerate(centres):
            parts += build_ball("%s_%d" % (name, i), c)
        parts = triangulate(parts)
        bpy.context.view_layer.update()
        print("== %s (shots %d): %s" % (name, sprite, what))
        if "check" in options:
            hot = (BALL["hot"][0], BALL["hot"][1] + centres[0][1])
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(sprite, 0, 0, 0)], hot)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
