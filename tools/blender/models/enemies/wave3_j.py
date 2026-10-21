"""Enemies of wave 3, batch J (sheet D, the asteroid levels), the machines; modelled as their sprites
look (models.cfg: yaw=0). The rocks and the stone face are in wave3_j_rocks.py; the cage turret (D 275), the red furnace
(D 267) and the red medallion (D 117) are built by polish_cage_turret.py, polish_red_furnace.py and
polish_medallion_red.py; the eye tub (D 193 and its frames) by polish_eye_tub.py.

- dome_cannon_barrel, dome_cannon_dome (D 245 above D 283): the brown dome on the tiled floor with a
  red band of lights and a heavy dark cannon reaching up the screen from its ribbed bronze collar,
  in two pieces (origin); the dome's lights flash (281): they glow.
- vent_dome (D 241): the grey armoured block on the tiled floor, reaching in from the top of its
  sprite, a red-hot crescent vent under its rounded front (the frames 239, 243 brighten it: it glows).
- shell_ship (D 157): the ship of two dark curved shells round a red eye (its frames close the shells;
  the model shows them open).
- bronze_beetle (D 16): the bronze beetle with red wing cases and green hooked legs.

The ground machines stand directly on the ground: the tiled floor the sprites draw round them is the map's (the game
draws it under them), so the models have none (batch AV); their parts that stood on it reach down to z 0.

usage: Blender -b --factory-startup -P wave3_j.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole dome_cannon --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_j_kit as w  # noqa: E402
from wave3_j_kit import art, k, sh, pal, px, py, model, whole  # noqa: E402

D = "enemy_D"


# --- D 245 above D 283: the dome cannon ----------------------------------------------------------

@whole("dome_cannon", (24, 56))
def dome_cannon_whole():
    """A brown dome on the ground: its north half ribbed bronze, a red band across it with two
    lights in a tan frame, a seam down its south side; from its top a heavy dark cannon reaches up
    the screen through a grey, a tan and a red collar, its muzzle open. Built whole and cut in two at
    y = 0; the tiled floor both sprites draw round it is the map's ground (batch AV): not modelled."""
    brown = pal("cannon_brown", 0x14, metallic=0.5, roughness=0.4)
    rib_light = pal("cannon_rib", 0x18, metallic=0.55, roughness=0.35)
    rib_dark = pal("cannon_rib_dark", 0x15, metallic=0.5, roughness=0.4)
    seam = pal("cannon_seam", 0x1a, metallic=0.6, roughness=0.3)
    red = pal("cannon_red", 0x46, metallic=0.4, roughness=0.35)
    lamp = pal("cannon_lamp", 0x4c, metallic=0.1, roughness=0.2, glow=0.9)
    tan = pal("cannon_tan", 0xa4, metallic=0.5, roughness=0.4)
    black = pal("cannon_black", 0x02, metallic=0.75, roughness=0.25)
    grey = pal("cannon_grey", 0x09, metallic=0.7, roughness=0.3)
    bore = pal("cannon_bore", 0x01, metallic=0.2, roughness=0.7)

    # The dome.
    dcx, dcy = -1.5, -4.6
    dome = k.ellipsoid("dome", (dcx, dcy, 0.0), (9.8, 12.2, 9.0), brown, 40, 20)
    sh.flat_bottom([dome])
    k.smooth(dome, 50)

    def paint(c, n):
        if n.z < -0.5:
            return None
        if -3.8 < c.y < 0.4:
            return red
        if c.y >= 0.4:
            return rib_light if int((c.x - dcx + 20.0) / 1.6) % 2 == 0 else rib_dark
        return None
    w.paint_faces(dome, paint)
    # The lights on the band, in a tan frame, and the seam down the south side.
    for y in (-1.0, -5.4):
        z = sh.surface_z(dome, -1.8, y, 8.0)
        w.rounded_box(f"lamp_frame{y}", (-1.8, y, z - 0.4), (4.6, 3.2, 1.6), tan, bevel=0.4)
        w.sphere(f"lamp{y}", (-1.8, y, z + 0.3), (1.8, 1.25, 0.8), lamp, 16, 8)
    path = [(-1.5, y, sh.surface_z(dome, -1.5, y, 4.0) + 0.05) for y in (-8.0, -10.5, -13.0, -15.0, -16.2)]
    w.tube("seam", path, 0.5, seam, 8)
    # The cannon.
    start, direction = Vector((-1.2, 4.5, 5.6)), Vector((0.0, 1.0, 0.12))
    w.lathe_axis("cannon_neck", [(0.0, 4.2), (6.0, 4.4), (6.2, 4.6)], black, start, direction, 32)
    w.lathe_axis("collar_grey", [(5.6, 4.9), (5.9, 5.5), (7.6, 5.5), (7.9, 5.0)], grey, start, direction, 32)
    w.lathe_axis("collar_tan", [(7.8, 5.0), (8.0, 5.3), (8.9, 5.3), (9.1, 5.0)], tan, start, direction, 32)
    w.lathe_axis("collar_red", [(9.0, 5.0), (9.2, 5.4), (10.1, 5.4), (10.3, 5.0)], red, start, direction, 32)
    barrel = [(10.0, 5.2), (10.4, 5.7), (19.6, 5.7), (20.6, 5.5), (21.2, 5.0), (21.3, 4.0), (20.4, 3.4), (20.3, 0.01)]
    w.lathe_axis("barrel", barrel, black, start, direction, 32, smooth_angle=40)
    w.lathe_axis("bore", [(20.0, 3.45), (20.45, 3.45), (20.5, 0.01)], bore, start, direction, 24)


def dome_cannon_piece(y0, y1):
    dome_cannon_whole()
    w.bake()
    w.piece(w.meshes(), -12, 12, y0, y1)


model("dome_cannon_barrel", [(D, 245, True)])(lambda: dome_cannon_piece(0, 28))
model("dome_cannon_dome", [(D, 283, True)])(lambda: dome_cannon_piece(-28, 0))


# --- D 241: the vent dome ------------------------------------------------------------------------

@model("vent_dome", [(D, 241, True)])
def vent_dome():
    """A grey armoured block reaching in from the top of the sprite, its south end rounded, panel
    seams across and along it, and a red-hot crescent vent under its rounded front."""
    grey = pal("vent_grey", 0x09, metallic=0.6, roughness=0.3)
    grey_light = pal("vent_grey_light", 0x0b, metallic=0.6, roughness=0.25)
    seam_mat = pal("vent_seam", 0x06, metallic=0.5, roughness=0.4)
    hot = pal("vent_hot", 0x73, metallic=0.0, roughness=0.4, glow=1.0)
    hotter = pal("vent_hotter", 0x76, metallic=0.0, roughness=0.3, glow=1.5)
    cx, cy, half, r_end = -1.0, 2.5, 8.0, 4.6

    # No floor round it: the sprite's tiles are the map's ground (batch AV); the block stands on the ground.
    outline = [(cx + half, 18.0), (cx - half, 18.0)]
    for i in range(25):
        a = math.radians(180 + 180 * i / 24)
        outline.append((cx + half * math.cos(a), cy + r_end * math.sin(a)))

    def grooves(x, y, z):
        d = 0.0
        d += math.exp(-((y - 7.5) / 0.35) ** 2)
        if y > 7.5:
            d += math.exp(-((x + 4.5) / 0.35) ** 2) + math.exp(-((x - 3.5) / 0.35) ** 2)
        else:
            d += math.exp(-((x + 2.5) / 0.3) ** 2) + math.exp(-((x + 0.5) / 0.3) ** 2)
        return z - 0.55 * min(1.0, d) * min(1.0, max(0.0, z - 1.5) / 2.0)
    block = sh.inflate("block", [outline], grey, sh.pillow_profile(7.0, 3.2, crown=0.8), bottom=0.0, spacing=0.45,
                       z_fn=grooves)
    w.simplify_bottom(block)
    sh.cut_planes([block], [((0, 14.0, 0), (0, 1, 0))])
    w.decimate(block, 2200)
    k.smooth(block, 50)
    w.paint_faces(block, lambda c, n: seam_mat if n.z > 0.2 and (abs(c.y - 7.5) < 0.45 or
                  (c.y > 7.5 and min(abs(c.x + 4.5), abs(c.x - 3.5)) < 0.45) or
                  (c.y < 7.5 and min(abs(c.x + 2.5), abs(c.x + 0.5)) < 0.4)) and c.z > 2.5 else
                  grey_light if n.z > 0.85 and c.z > 7.0 and c.y > 8.0 else None)
    # The crescent vent under the front.
    arc = []
    for i in range(17):
        a = math.radians(195 + 150 * i / 16)
        arc.append((cx + (half + 0.4) * math.cos(a), cy + (r_end + 2.2) * math.sin(a), 1.0))
    w.tube("vent", arc, 1.35, hot, 12, squash=0.8)
    inner = [(x, y + 0.4, 1.7) for x, y, _ in arc[3:-3]]
    w.tube("vent_core", inner, 0.6, hotter, 8)


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
