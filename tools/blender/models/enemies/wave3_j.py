"""Enemies of wave 3, batch J (sheet D, the asteroid levels), the machines; modelled as their sprites
look (models.cfg: yaw=0). The cage turret (D 275), the red furnace (D 267) and the red medallion (D 117) are built by
polish_cage_turret.py, polish_red_furnace.py and polish_medallion_red.py; the eye tub (D 193 and its frames) by
polish_eye_tub.py; the dome cannon (D 245 above 283) by polish_dome_cannon.py; the vent dome (D 241 and its frames) by
polish_vent_dome.py; the shell ship (D 157 and its frames) by polish_shell_ship.py; the rocks by polish_asteroids.py,
polish_pebbles.py, polish_sky_rocks.py, polish_crag.py and polish_beacon_rocks.py.

- bronze_beetle (D 16): the bronze beetle with red wing cases and green hooked legs.

The ground machines stand directly on the ground: the tiled floor the sprites draw round them is the map's (the game
draws it under them), so the models have none (batch AV); their parts that stood on it reach down to z 0.

usage: Blender -b --factory-startup -P wave3_j.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_j_kit as w  # noqa: E402
from wave3_j_kit import k, pal, px, model  # noqa: E402

D = "enemy_D"


# --- D 16: the bronze beetle ---------------------------------------------------------------------

@model("bronze_beetle", [(D, 16, True)])
def bronze_beetle():
    """A bronze beetle: a ribbed body between two raised wing cases (bronze frames round red
    panels, two on each), red eyes at its head, and green hooked legs reaching down the screen with
    red claws between them."""
    bronze = pal("beetle_bronze", 0x18, metallic=0.7, roughness=0.3)
    bronze_light = pal("beetle_bronze_light", 0x1b, metallic=0.7, roughness=0.25)
    bronze_dark = pal("beetle_bronze_dark", 0x14, metallic=0.6, roughness=0.4)
    red = pal("beetle_red", 0x46, metallic=0.45, roughness=0.3)
    green = pal("beetle_green", 0x24, metallic=0.4, roughness=0.35)
    eye = pal("beetle_eye", 0x75, metallic=0.0, roughness=0.2, glow=1.0)
    # The body: a long ribbed hull down the middle.
    hull = [(-4.0, 0.01), (-3.6, 1.6), (-2.0, 2.9), (2.0, 3.5), (6.0, 3.5), (8.5, 3.0), (10.2, 2.0), (11.0, 0.01)]
    w.lathe_axis("body", k.profile(hull, 0.6), bronze, (px(11.5), 0.0, 1.0), (0, 1, 0), 24, squash=1.1)
    for x in (-1.6, 0.0, 1.6):
        w.tube(f"rib{x}", [(px(11.5) + x, y, 3.9 - 0.04 * (y - 5) ** 2 * 0.3) for y in (-2.0, 2.0, 6.0, 10.0)], 0.4,
               bronze_light, 8)
    # The wing cases: a bronze frame round two red panels each, leaning out.
    for side in (-1, 1):
        cx = px(11.5) + side * 6.1
        frame = w.block(f"case{side}", (cx, 5.6), 2.5, 7.8, 3.2, bronze_dark, rounding=1.0, power=3.0, segments=24,
                        z0=0.8)
        for y0, y1 in ((12.0, 6.2), (4.2, -0.8)):
            w.block(f"panel{side}{y0}", (cx, (y0 + y1) / 2), 2.0, (y0 - y1) / 2 - 0.3, 0.8, red, rounding=0.4,
                    power=3.0, segments=20, z0=3.6)
        w.tube(f"case_edge{side}", [(cx + side * 2.4, y, 3.4) for y in (12.6, 8.0, 3.0, -1.6)], 0.5, bronze_light, 8)
        frame.data.transform(Matrix.Translation((cx, 0, 0)) @ Matrix.Rotation(math.radians(-8 * side), 4, "Y") @
                             Matrix.Translation((-cx, 0, 0)))
    # The eyes at the head.
    for side in (-1, 1):
        w.sphere(f"eye{side}", (px(11.5) + side * 2.2, 10.0, 3.6), (1.0, 1.2, 0.9), eye, 12, 6)
    # The legs: green hooks from the body's lower corners down the screen, the claws between them.
    for side in (-1, 1):
        x0 = px(11.5)
        leg = [(x0 + side * 5.4, -2.6, 2.2), (x0 + side * 7.9, -5.6, 2.0), (x0 + side * 7.8, -9.4, 1.6),
               (x0 + side * 6.0, -11.9, 1.2), (x0 + side * 3.8, -13.0, 1.0)]
        w.tube(f"leg{side}", w.catmull(leg, 0.7), 0.62, green, 10)
        claw = [(x0 + side * 1.4, -3.5, 1.8), (x0 + side * 1.6, -6.0, 1.5), (x0 + side * 1.1, -7.6, 1.2)]
        w.tube(f"claw{side}", claw, 0.5, bronze_light, 8)
        w.sphere(f"claw_tip{side}", (x0 + side * 1.1, -7.8, 1.2), (0.6, 0.7, 0.5), eye, 10, 5)


w.run()
