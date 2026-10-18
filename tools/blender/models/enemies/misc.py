"""More episode 1 enemies, facing the way their sprites do (models.cfg: yaw=0):

- container (sheet 2 sprite 89): a purple ribbed container.
- claws (sheet F 169): SAVARA's twin red claws standing on the ground.

(diamond, ornament, shield_ship and eye_turret are built by polish_<name>.py.)
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


def container():
    k.reset()
    shell = k.material("container_shell", palette=85, metallic=0.35, roughness=0.35)
    ribs = k.material("container_ribs", palette=88, metallic=0.45, roughness=0.3)
    body = k.pillow("body", 11.0, 12.0, 8.0, shell, rounding=3.0, dome=0.8)
    body.location = (0.0, 0.5, 0.0)
    # Ribs across the top, as the sprite's bright lines.
    for x in (-6.5, -2.0, 2.5, 7.0):
        rib = k.box("rib", (x, 0.5, 8.6), (1.4, 17.0, 1.2), ribs)
        k.bevel(rib, 0.4, 2)
    export("container")


def claws():
    k.reset()
    shell = k.material("claws_shell", palette=71, metallic=0.3, roughness=0.35)
    dark = k.material("claws_dark", palette=67, metallic=0.3, roughness=0.45)
    for side, x in (("left", -6.0), ("right", 6.0)):
        # The body from the bottom (row 26) to the top (row 4): wide shoulders, a thin waist.
        profile = [(-12.5, 1.0), (-11.0, 3.4), (-9.5, 4.0), (-8.0, 2.4), (-5.0, 2.0), (0.0, 2.2), (1.0, 3.6),
                   (3.5, 4.6), (5.5, 4.4), (7.0, 3.0), (8.5, 1.6), (9.5, 0.6)]
        body = k.lathe("body_" + side, profile, shell, segments=20, axis_x=x, axis_z=3.5, squash=0.8)
        k.smooth(body, 60)
        # The prongs at the top.
        for dx in (-2.4, 2.4):
            prong = k.lathe("prong", [(8.0, 0.8), (10.5, 0.5), (12.0, 0.1)], dark, segments=8,
                            axis_x=x + dx, axis_z=4.5)
            k.smooth(prong, 60)
    export("claws")


container()
claws()
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

PURPLE_FIGHTER = """
........................
........................
........................
........................
.........#....#.........
.......##########.......
.......##########.......
.......####..####.......
.......####..####.......
.......##########.......
.......##########.......
....################....
....################....
....#######oo#######....
..####################..
.#########o##o#########.
.######################.
.########o####o########.
.######################.
.######################.
.######################.
..####################..
...##################...
....################....
......############......
.......##########.......
.........######.........
...........##...........
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


def purple_fighter():
    def cockpit():
        red = k.material("purple_red", palette=118, roughness=0.3, emission=(255, 40, 0), emission_strength=0.8)
        k.smooth(k.ellipsoid("cockpit", (0.0, 4.5, 3.4), (2.6, 3.4, 1.6), red, 16, 8), 60)
    plate_model("purple_fighter", PURPLE_FIGHTER, 86, 3.2, 1.2, cockpit)


def red_gem_panel():
    """The red gem (sheet S 229, columns 4-18, rows 4-23) in its dark bezel, held by four dark clips (above,
    below, beside it). The grey stone round it in the sprite is the map's floor: no plate under it."""
    k.reset()
    plate = k.material("redgem_plate", palette=2, metallic=0.5, roughness=0.45)
    red = k.material("redgem_gem", palette=116, metallic=0.25, roughness=0.15, emission=(200, 20, 0),
                     emission_strength=0.3)
    gx = -0.5
    k.pillow("bezel", 8.3, 10.7, 1.4, plate, rounding=0.7, dome=0.1).location = (gx, 0.0, 0.0)
    k.pillow("gem", 7.3, 9.7, 3.2, red, rounding=2.4, dome=1.2).location = (gx, 0.0, 0.6)
    for name, centre, size in (("clip_left", (-9.0, 0.5, 1.5), (3.6, 11.0, 3.0)),
                               ("clip_right", (8.2, 0.5, 1.5), (3.6, 11.0, 3.0)),
                               ("clip_top", (0.0, 10.7, 1.3), (8.0, 3.0, 2.6)),
                               ("clip_bottom", (-0.5, -10.8, 1.3), (7.0, 3.0, 2.6))):
        k.bevel(k.box(name, centre, size, plate), 0.5)
    export("redgem_panel")


arch_ship()
purple_fighter()
red_gem_panel()
