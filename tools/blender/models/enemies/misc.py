"""More episode 1 enemies, facing the way their sprites do (models.cfg: yaw=0): arch_ship (2 49).

(diamond, ornament, shield_ship, eye_turret, container, purple_fighter, claws and
redgem_panel are built by polish_<name>.py.)
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
import silhouette as s  # noqa: E402

ORNAMENT = """
........................
........................
........................
...00.....0000.....00...
..01100..047530..00110..
.0253210038545300123220.
012353212251152212342210
023325432350263234522210
023323753335753345223220
023222385221123463222310
024324349531135742322310
025453434852258433232310
025333335683384323223310
026334355674563332322410
023653568458852532234210
012376895693385353342110
012237845832238545421110
011213558326313865211110
.0357972531111372776530.
..03568246311383253350..
..02345244633653244720..
...022424335643425610...
....0231433333371210....
.....00023333473000.....
........01235510........
.........000000.........
........................
........................
"""


def export(name):
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


# --- More of episode 1 ---------------------------------------------------------------------------

ARCH = """
............ooooo#ooo...
..........oo#########o..
........oo############o.
......oo##############o.
.....o#######oooooo#oooo
.....o######o#####ooo##o
.....o############o#####
.....o############ooo###
.....o#########oooo.o##o
...oo#########o.....o##o
..o##########o......o#oo
..o#########o.......o#o.
..o########o......ooo##o
..o#######o.......o####o
..o#######........oo#o#o
..o#######........o####o
..o#######........o#o##o
..o######o........ooo#oo
..o######o.........o##o.
..o######o.........o##o.
..o######o.........o##o.
..o#####o..........o##o.
..o####o...........o##o.
..o###o............o#o..
..o##o.............oo...
..o#o...................
..oo....................
........................
"""

SHIELD_SHIP = """
........................
........................
....##...#####...##.....
...###..#######..###....
..###################...
..###################...
..###################...
.####..#########..####..
####..###########..####.
###..#############..###.
###.###############.###.
###.###############.###.
###.###############.###.
###.###############.###.
###.###############.###.
###.###############.###.
###.###############.###.
###.##############..###.
###.##############..###.
.....#############......
......###########.......
......###########.......
.......#########........
.......#########........
........#######.........
.........#####..........
..........###...........
...........#............
"""

def plate_model(name, art, index, thickness, bevel_width, accent=None):
    """A thick plate in the sprite's outline, rounded at the edges."""
    k.reset()
    shell = k.material(name + "_shell", palette=index, metallic=0.45, roughness=0.35)
    plate = s.plate("plate", [line for line in art.strip("\n").split("\n")], 0.0, thickness, shell, bevel=bevel_width)
    k.smooth(plate, 35)
    if accent is not None:
        accent()
    export(name)


def arch_ship():
    def lights():
        red = k.material("arch_red", palette=118, roughness=0.3, emission=(255, 40, 0), emission_strength=1.0)
        purple = k.material("arch_purple", palette=91, metallic=0.4, roughness=0.3)
        k.smooth(k.ellipsoid("panel", (-4.5, 3.0, 3.6), (3.6, 5.5, 1.0), purple, 16, 8), 60)
        for x, y in ((8.5, -7.0), (8.5, -2.0)):
            k.smooth(k.ellipsoid("light", (x, y, 3.4), (0.9, 1.4, 0.8), red, 10, 6), 60)
    plate_model("arch_ship", ARCH, 6, 3.4, 1.2, lights)


arch_ship()
