"""Enemies of wave 3, batch J (sheet D, the asteroid levels), the machines; modelled as their sprites
look (models.cfg: yaw=0). The rocks and the stone face are in wave3_j_rocks.py; the cage turret (D 275), the red furnace
(D 267) and the red medallion (D 117) are built by polish_cage_turret.py, polish_red_furnace.py and
polish_medallion_red.py; the eye tub (D 193 and its frames) by polish_eye_tub.py; the dome cannon (D 245 above 283)
by polish_dome_cannon.py; the vent dome (D 241 and its frames) by polish_vent_dome.py.

- shell_ship (D 157): the ship of two dark curved shells round a red eye (its frames close the shells;
  the model shows them open).
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
from wave3_j_kit import k, sh, pal, px, model  # noqa: E402

D = "enemy_D"


# --- D 157: the shell ship -----------------------------------------------------------------------

@model("shell_ship", [(D, 157, True)])
def shell_ship():
    """Two dark curved shells standing like wings either side of a small hub with a glowing red
    eye (the frames close the shells over it; the model shows them open)."""
    shell = pal("shell_dark", 0x05, metallic=0.75, roughness=0.25)
    inner = pal("shell_inner", 0x02, metallic=0.6, roughness=0.45)
    hub_mat = pal("shell_hub", 0x03, metallic=0.6, roughness=0.4)
    rim = pal("shell_rim", 0x07, metallic=0.7, roughness=0.3)
    eye = pal("shell_eye", 0x77, metallic=0.0, roughness=0.2, glow=1.4)
    # A shell: half of a pointed egg along y, cut flat on the inside.
    prof = k.profile([(-10.4, 0.01), (-9.4, 1.8), (-6.0, 4.4), (-1.0, 6.6), (4.0, 7.4), (8.0, 6.8), (11.0, 5.0),
                      (12.6, 2.6), (13.3, 0.01)], 0.6)
    for side in (-1, 1):
        x_in = side * 3.6
        body = w.lathe_axis(f"shell{side}", prof, shell, (x_in, 0.0, 0.0), (0, 1, 0), 32, squash=1.15)
        kept = sh.cut_planes([body], [((x_in, 0, 0), (-side, 0, 0))])
        for obj in kept:
            k.smooth(obj, 40)
            w.paint_faces(obj, lambda c, n, s=side: inner if n.x * s < -0.9 else None)
        # A rim along the shell's inner edge, over its top.
        top = [(x_in + side * 0.3, y, max(0.3, 1.15 * r - 0.2)) for y, r in prof[2:-2]]
        w.tube(f"rim{side}", top, 0.45, rim, 8)
    # The hub between them, the eye on it.
    w.rounded_box("hub", (0.0, 3.0, 0.0), (7.6, 10.0, 5.0), hub_mat, bevel=0.8)
    w.rounded_box("neck", (0.0, -2.6, -0.4), (4.0, 3.6, 3.4), inner, bevel=0.6)
    w.hoop("eye_ring", (0.0, 5.3, 2.4), [(1.4, -0.3), (2.2, -0.2), (2.3, 0.3), (1.6, 0.5)], rim, 20, scale_y=0.8)
    w.sphere("eye", (0.0, 5.3, 2.3), (1.6, 1.2, 0.9), eye, 16, 8)


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
