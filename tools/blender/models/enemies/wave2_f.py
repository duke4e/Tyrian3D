"""Batch F of the second wave of enemy models, facing the way their sprites do (models.cfg: yaw=0)
(spike_star, 3 246: polish_spike_star.py; 7 51 is the squid ship turned round, polish_squid_ship.py; the mug of
beer, coins 241: items/polish_beer_mug.py; the pebble, D 133: polish_pebbles.py; the steel jet, F 79:
polish_jet_steel.py):

- obsidian_egg (sheet M 271): MINERS' indestructible black glass egg with a smoky light inside,
  lying on the ground.


usage: blender -b --factory-startup -P wave2_f.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave2_f_kit as w  # noqa: E402
from wave2_f_kit import k, sh, model, pal  # noqa: E402


# --- The obsidian egg (sheet M 271) ------------------------------------------------------------

@model("obsidian_egg", "enemy_M", 271)
def obsidian_egg():
    """A black glass egg lying on the ground (flat underneath), a smoky light inside it along the
    streak the sprite draws from the upper left to the lower right."""
    glass = pal("egg_glass", 96, metallic=0.2, roughness=0.04, alpha=0.5)
    layers = [("smoke", 3, 0.8, (60, 64, 76), 1.0, (4.0, 8.4, 2.6)),
              ("haze", 6, 1.4, (100, 104, 118), 1.7, (3.0, 7.0, 2.1)),
              ("glow", 10, 2.4, (160, 165, 180), 2.4, (2.1, 5.6, 1.7)),
              ("core", 13, 4.0, (225, 230, 245), 3.0, (1.2, 4.0, 1.4))]
    # The sprite's outline is an ellipse 16 x 25 pixels round (0, 0.5).
    axis_z = 2.4
    k.smooth(k.ellipsoid("egg", (0.0, 0.5, axis_z), (7.75, 12.4, 6.6), glass, 48, 28), 70)
    # The smoke and its bright core, tilted along the streak (rows 9-22, leaning to the left at the top),
    # nested: each layer rises a little above the one under it, so all of them show from above.
    tilt = Matrix.Translation((0.5, -1.6, axis_z)) @ Matrix.Rotation(math.radians(-22), 4, "Z")
    for name, index, strength, colour, z, radii in layers:
        mat = pal("egg_" + name, index, roughness=0.5, glow=strength, emission=colour)
        obj = k.ellipsoid(name, (0, 0, z), radii, mat, 24, 14)
        obj.data.transform(tilt)
        k.smooth(obj, 70)
    sh.flat_bottom(w.meshes())


# --- The twin-panel ship (sheet H 284) ---------------------------------------------------------

TWIN = w.art("""
........................
......cdfff..fffdc......
.....cfddggccggddfc.....
.....fgnnggccggnngf.....
...cc#gnngg##ggnng#cc...
.cc#a#gnnggddggnng#a#cc.
c#a#gggnnggggggnnggg#a#c
cggggggnnggddggnnggggggc
#ggggggnngg##ggnngggggg#
gggggggnnggggggnnggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
#gggga#gggggggggg#agggg#
c####f#ggggggggggcf####c
.......#ggggggggc.......
........#gggggg#........
.........#gggg#.........
..........###c..........
""")


# --- Main ----------------------------------------------------------------------------------------

if __name__ == "__main__":
    w.main()
