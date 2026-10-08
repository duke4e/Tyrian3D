"""Enemies of wave 3, batch Z, continued (sheet L): MINERS's crawler train, modelled as its sprites look (models.cfg:
yaw=0). The kit is wave3_z_kit.py, the pixels wave3_z_art.py.

MINERS sends the train down the screen three times: its head (L 275, enemy 1160) with two wagons behind it (L
277, enemy 1161, its frames 277/279), each car 24 pixels behind the one in front, so that each overlaps the next
by four rows (the head is drawn over the wagon behind it). The cars are separate enemies and the two wagons the
same model, so each car is a model of its own, drawn at its own origin: low dark blue-grey hulls on tracks,
their front ends coupled under the car in front.

- crawler_head (L 275): the head, a hull with a ribbed spine, three slanted vents with orange lights on each
  side and a big pale blue glass dome in front.
- crawler_wagon (L 277): a wagon with a brown dome turret whose twin barrels point down the screen (frame 279
  lights their muzzles red: the model keeps them dark), a hatch with a blue lamp on its deck in front.

usage: Blender -b --factory-startup -P wave3_z_train.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--assembly <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_z_kit as kit  # noqa: E402
from wave3_z_kit import k, sh, w, pal  # noqa: E402

LOCO = kit.frame("LOCO", 24, (12, 14))
WAGON = kit.frame("WAGON", 24, (12, 14))
DECK = 6.6   # the hull's deck


def hull_mats(prefix):
    paint = kit.Painter(prefix, shades={6: (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 3: (2, 4, 6, 8, 10, 12)},
                        metallic=0.4, roughness=0.38, remap={0x30: 0x63, 0x31: 0x63, 0x60: 0x62})
    return paint, pal(prefix + "_dark", 0x61, metallic=0.4, roughness=0.5), pal(prefix + "_track", 0x02, metallic=0.3,
                                                                              roughness=0.6)


def hull(prefix, f, art_name, row0, row1):
    """A car's hull: a block with rounded corners over columns 3-20 between rows row0 and row1 (its deck
    painted by the sprite), on two dark tracks along its sides."""
    paint, dark, track = hull_mats(prefix)
    x0, x1 = f.left(3) + 0.3, f.right(20) - 0.3
    y0, y1 = f.bottom(row1), f.top(row0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    body = w.block(prefix + "_hull", (cx, cy), (x1 - x0) / 2 - 0.4, (y1 - y0) / 2, DECK - 1.6, paint(0x66), taper=0.6,
                   rounding=1.8, power=3.2, segments=48, z0=1.6, dome=0.5)
    paint_f = kit.frame(art_name, 24, (12, 14)).fill({0x30, 0x31, 0x60}, edge_only=True)
    kit.pixelate(body, paint_f)
    kit.paint_sprite(body, paint_f, paint, wall_steps=2, under=dark, blur=1)
    kit.merge_flat(body)
    # The tracks: dark ribbed bands under the hull's sides.
    for side in (-1, 1):
        tx = cx + side * ((x1 - x0) / 2 - 1.7)
        w.rounded_box(f"{prefix}_track{side}", (tx, cy, 1.15), (3.2, y1 - y0 - 1.0, 2.3), track, bevel=0.9)
        for i in range(int((y1 - y0 - 3) / 2.2)):
            yy = y0 + 2.0 + i * 2.2
            w.rounded_box(f"{prefix}_cleat{side}_{i}", (tx + side * 0.25, yy, 1.2), (3.0, 0.8, 2.5), dark, bevel=0.25)
    return paint, dark


# --- L 275: the head -------------------------------------------------------------------------------

@kit.model("crawler_head", mask=lambda: LOCO.mask())
def crawler_head():
    f = LOCO
    X, Y = f.X, f.Y
    paint, dark = hull("head", f, "LOCO", 0, 24)
    spine = pal("head_spine", 0x69, metallic=0.45, roughness=0.3)
    rib = pal("head_rib", 0x6b, metallic=0.45, roughness=0.3)
    vent = pal("head_vent", 0x62, metallic=0.3, roughness=0.5)
    light = pal("head_light", 0x7b, metallic=0.0, roughness=0.3, glow=1.6)
    light_red = pal("head_light_red", 0x78, metallic=0.0, roughness=0.3, glow=1.1)
    glass = pal("head_glass", 0x3c, metallic=0.2, roughness=0.06, glow=0.35)
    glass_rim = pal("head_glass_rim", 0x36, metallic=0.4, roughness=0.3)
    glint = pal("head_glint", 0x3f, metallic=0.1, roughness=0.05, glow=0.8)
    # The spine along the deck's middle (rows 1-14) and its ribs across it.
    ridge = kit.lathe_y("spine", [(0.0, 0.6), (0.6, 1.8), (12.4, 1.8), (13.4, 0.8)], spine, X(11.5) + 0.5, DECK - 0.1,
                        segments=16, squash=0.8)
    kit.move([ridge], 0.0, f.top(1))
    for row in (2.5, 6.5, 10.5):
        w.rounded_box(f"rib{row}", (X(11.5) + 0.5, Y(row), DECK + 0.7), (7.4, 1.1, 1.0), rib, bevel=0.35)
    # The vents along the sides: slanted slots with an orange light in each (rows 3-5, 7-9, 11-13).
    for side in (-1, 1):
        for row in (4.0, 8.0, 12.0):
            cx = X(5.5) if side < 0 else X(17.5)
            pts = [(cx - side * 1.2, Y(row - 1.2), DECK + 0.1), (cx + side * 0.9, Y(row + 0.9), DECK - 0.2)]
            w.tube(f"vent{side}{row}", pts, 0.95, vent, 10)
            lp = [(cx - side * 1.0, Y(row - 1.0), DECK + 0.45), (cx + side * 0.2, Y(row + 0.1), DECK + 0.35)]
            w.tube(f"light{side}{row}", lp, 0.5, light if row < 11 else light_red, 8)
    # The glass dome in front (rows 15-23, columns 7-16) in a dark rim.
    gx, gy = X(11.5) + 0.5, Y(19.2)
    w.hoop("glass_rim", (gx, gy, DECK - 0.3), [(4.6, -0.6), (5.4, -0.6), (5.4, 0.5), (4.7, 0.7)], glass_rim, 40,
           scale_y=1.18)
    w.sphere("glass", (gx, gy, DECK - 0.6), (4.7, 5.5, 4.0), glass, 32, 16)
    w.sphere("glint", (gx - 1.6, gy + 1.6, DECK + 3.0), (1.0, 1.4, 0.4), glint, 10, 5)
    # The nose under the dome (rows 24-27).
    w.rounded_box("nose", (gx, Y(25.5), 2.2), (9.0, 3.4, 3.4), dark, bevel=1.2)
    sh.flat_bottom(w.meshes(), 0.0)


# --- L 277: the wagon ------------------------------------------------------------------------------

@kit.model("crawler_wagon", mask=lambda: WAGON.mask())
def crawler_wagon():
    f = WAGON
    X, Y = f.X, f.Y
    paint, dark = hull("wagon", f, "WAGON", 0, 26)
    brown = pal("wagon_turret", 0x15, metallic=0.4, roughness=0.35)
    brown_lit = pal("wagon_turret_lit", 0x18, metallic=0.4, roughness=0.3)
    brown_dark = pal("wagon_turret_dark", 0x12, metallic=0.35, roughness=0.45)
    barrel = pal("wagon_barrel", 0x13, metallic=0.5, roughness=0.35)
    hatch = pal("wagon_hatch", 0xd3, metallic=0.4, roughness=0.4)
    hatch_rim = pal("wagon_hatch_rim", 0xd6, metallic=0.4, roughness=0.35)
    lamp = pal("wagon_lamp", 0x3d, metallic=0.1, roughness=0.1, glow=1.4)
    # The turret: a brown dome on a ring (rows 4-8, columns 8-15), its twin barrels down the screen (rows 9-12).
    tx, ty = X(11.5) + 0.5, Y(6.3)
    w.column("turret_ring", [(DECK - 0.2, 3.6), (DECK + 0.6, 3.6), (DECK + 0.9, 3.2)], brown_dark, tx, ty, 28)
    dome = w.sphere("turret", (tx, ty, DECK + 0.8), (4.1, 3.0, 2.8), brown, 28, 12)
    kit.paint_faces(dome, lambda c, nrm: brown_lit if (nrm.z > 0.6 and nrm.x > -0.1 and nrm.y > -0.2) else
                    brown_dark if nrm.z < 0.25 else None)
    for dx in (-1.5, 1.5):
        w.lathe_axis(f"barrel{dx}", [(0.0, 0.8), (5.6, 0.7), (5.8, 0.85), (6.4, 0.85), (6.5, 0.35), (6.5, 0.01)],
                     barrel, (tx + dx, ty - 1.6, DECK + 1.8), (0, -1, -0.12), 12)
    # The hatch in front (rows 18-25): a teal frame round a plate with the blue lamp in its middle.
    hx, hy = X(11.5) + 0.5, Y(21.5)
    w.rounded_box("hatch_rim", (hx, hy, DECK + 0.15), (8.6, 8.2, 0.9), hatch_rim, bevel=0.35)
    w.rounded_box("hatch", (hx, hy, DECK + 0.45), (6.6, 6.2, 0.9), hatch, bevel=0.35)
    w.sphere("lamp", (hx, hy + 0.2, DECK + 1.0), (1.2, 1.2, 0.8), lamp, 12, 6)
    # The coupling bar at its front, low, under the car in front.
    w.rounded_box("coupler", (hx, Y(26.6), 1.8), (3.0, 3.0, 1.6), dark, bevel=0.5)
    sh.flat_bottom(w.meshes(), 0.0)


kit.assembly("crawler_train", (24, 76), [(crawler_wagon, (0.0, 24.0)), (crawler_wagon, (0.0, 0.0)),
                                         (crawler_head, (0.0, -24.0))])


if __name__ == "__main__":
    kit.run()
