"""The enemies' twin fire bolts, the "flame jets" (shots sheet sprites 61 and 80, 1x1: 12 x 14 cells), modelled
(2026-10-29, round 2 of the energy shots' models; until then they were drawn as their sprites with volume, flat, from
the 4x sheets, with the automatic glow).

Who fires them: enemy weapon 131 (61, falling down the screen at 6: GRYPHON's, GEM WAR's and MISTAKES' turrets in
episode 2, STATION's in episode 5), and in episodes 4 and 5 weapons 105 (61, falling at 4) and 106 (80, moving right
at 3) of SURFACE's turret (enemy 205); all only once a fire override event (31) gives the turrets a frequency. Not
animated (weapani 0), not picked by heading.

As the sprites draw them (the catalogue called them a flame column, but the pixels are two bolts): two bolts of fire 8
pixels apart, side by side (columns 0-3 and 8-11), each the Pulse-Cannon's 4-pixel bolt (polish_shot_pulse.py) as
the outer pair of its shot 60 draws it: 80 is that pair exactly (rows 2-12), heads up the screen (0x7c, 0x7b at rows
3-4, on the bolts' outer columns), dark red tails down to row 12; 61 is 80 upside down (rows 1-11, heads down at rows
9-10: 80 turned half round about the cell's centre, the sprite being its own mirror image across its middle column).

The model: two of the pulse's bolts, built by polish_shot_pulse.py's own pieces (sheath(): the fire lofted round on
top and flat underneath, its bands of ramp 7 on the mesh's rings; core(): the pale yellow plasma standing out of each
head), from 80's pixels (their hottest columns, where the cores lie). One model, shot_ejet, for both sprites: 80 as
drawn, 61 turned half round (yaw=180): turned, the bolts land on 61's pixels exactly (80's rows 2-12 turn onto rows
1-11). 664 triangles, 10 materials (the pulse's 8 fire bands and 2 core bands).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the bolts stand on z = 0
(the game centres shot models in height on the player's layer).

models.cfg (the shots section):
    model shot_ejet shots/shot_ejet.glb
    shot shots 80 shot_ejet         glow=15:0.55:120:0:-3     # two bolts, heads up
    shot shots 61 shot_ejet yaw=180 glow=15:0.55:120:0:3      # heads down (the same turned half round)
(the halo the enemies' red-orange, 0x78, not the player's pulses' yellow)

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_ejet.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_pulse as pulse  # noqa: E402
from polish_shot_pellet import run  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import Heat  # noqa: E402
from polish_launched_flames import grid, shades, lit  # noqa: E402

SPRITE_80 = """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. 75 76 .. .. .. .. .. .. 76 75 ..
75 7c 7b 76 .. .. .. .. 76 7b 7c 75
76 7b 7a 77 .. .. .. .. 77 7a 7b 76
78 7a 79 78 .. .. .. .. 78 79 7a 78
78 77 78 77 .. .. .. .. 77 78 77 78
75 76 77 75 .. .. .. .. 75 77 76 75
74 77 77 74 .. .. .. .. 74 77 77 74
73 75 75 73 .. .. .. .. 73 75 75 73
72 73 72 72 .. .. .. .. 72 72 73 72
.. 72 71 .. .. .. .. .. .. 71 72 ..
.. 71 .. .. .. .. .. .. .. .. 71 ..
.. .. .. .. .. .. .. .. .. .. .. ..
"""

BOLTS = [pulse.wide(-4.0, 2, 12), pulse.wide(4.0, 2, 12)]  # (shot 60's outer pair)

MODELS = [
    ("shot_ejet", 80, "two fire bolts side by side, heads up (61: the same turned half round)"),
]


def build_model(name, sprite):
    heat = Heat(shades(grid(SPRITE_80), 7), pulse.TOP, sigma=(0.55, 0.7))
    fire = [lit(f"ejet_fire_{index:02x}", index, glow, roughness=pulse.FIRE_ROUGHNESS)
            for _, index, glow in pulse.FIRE_BANDS]
    parts = []
    for i, bolt in enumerate(BOLTS):
        parts.append(pulse.sheath(f"{name}_bolt{i}", bolt, heat, fire))
        cores = [lit(f"ejet_core_{index:02x}", index, glow, roughness=pulse.CORE_ROUGHNESS)
                 for _, index, glow in pulse.WEDGE_BANDS]
        parts.append(pulse.core(f"{name}_core{i}", bolt, heat, cores))
    return triangulate(parts)


if __name__ == "__main__":
    run(MODELS, build_model)
