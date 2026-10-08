"""Enemies of wave 3, batch Z, continued (sheet L): the station of STATION and TIME WAR and TIME WAR's grey capsule,
modelled as their sprites look (models.cfg: yaw=0). The kit is wave3_z_kit.py, the pixels wave3_z_art.py.

- station_l_tl, station_l_tr, station_l_bl, station_l_br (L 7, 9 above 45, 47) and station_r_tl, station_r_tr,
  station_r_bl, station_r_br (L 11, 13 above 49, 51): the two halves of the station, which the levels put at the
  two sides of the screen (on the top layer: enemies 664-668 the left half with its axle end L 24 on its outer
  side, 659-663 the right half with L 34; the end pieces are station_end_left / station_end_right of wave 2,
  wave2_e.py). Each half: the steel axle housing going on from the end's collar (the same elliptic section,
  its middle at the end's axle, z = 0) with a blue band and a red clamp, a dark docking block at its inner end,
  bent struts above and below it out to four solar panels, one straight up and down the screen and one at 45
  degrees on each side. The halves are mirror images; the whole station (144 x 56 pixels) is built at once and
  cut into its eight pieces (origin).
- grey_capsule_tl, grey_capsule_tr, grey_capsule_ml, grey_capsule_mr, grey_capsule_bl, grey_capsule_br (L 1, 3
  above 39, 41 above 77, 79): TIME WAR's grey capsule (enemies 653-658, two of them side by side in the sky),
  48 x 84: a ship lying along the screen, nose up, its long body with two red glowing slots and side rails, a
  waist and a flange with red lights, engine rings and a red glow at its tail. Built whole, cut into its six
  pieces (origin).

usage: Blender -b --factory-startup -P wave3_z_station.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_z_kit as kit  # noqa: E402
from wave3_z_kit import k, sh, w, pal  # noqa: E402

STATION = kit.frame("STATION", 144, (72, 28))
POD = kit.frame("POD", 48, (24, 42))
SQUASH = 0.62  # the axle's section, as station_end's


def lathe_x(name, profile, mat, y, z, segments=32, squash=SQUASH):
    """A round part along +x: profile (x, radius) pairs in increasing x, its axis at (y, z)."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    obj.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
    obj.data.transform(Matrix.Translation((0.0, y, z)))
    return k.smooth(obj, 50)


def panel(prefix, centre, half, angle, m):
    """A solar panel lying flat: a light frame round four dark cells, turned by angle (degrees)."""
    cx, cy = centre
    parts = [kit.slab(prefix + "_frame", [(-half, -half), (half, -half), (half, half), (-half, half)], -0.7, 0.5,
                      m["frame"], bevel=0.3)]
    cell = half - 1.05
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x0, y0 = (0.35 if sx > 0 else -cell), (0.35 if sy > 0 else -cell)
        x1, y1 = x0 + cell - 0.35, y0 + cell - 0.35
        parts.append(kit.slab(f"{prefix}_cell{i}", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.2, 0.75, m["cell"],
                              bevel=0.15))
    rot = Matrix.Translation((cx, cy, 0.0)) @ Matrix.Rotation(math.radians(angle), 4, "Z")
    for p in parts:
        sh.apply_modifiers(p)
        p.data.transform(rot)
    return parts


def station_whole():
    f = STATION
    X, Y = f.X, f.Y
    y0 = Y(27.0)   # the axle's middle (station_end's y = 0.5)
    paint = kit.Painter("station", shades={0: (3, 4, 5, 6, 7, 8, 9, 10, 11, 12)}, metallic=0.4, roughness=0.32,
                        remap={0x01: 0x03, 0x02: 0x03, 0x72: 0x07, 0x71: 0x06, 0x73: 0x07})
    m = {"frame": pal("station_frame", 0x09, metallic=0.5, roughness=0.3),
         "cell": pal("station_cell", 0x03, metallic=0.4, roughness=0.25)}
    dark = pal("station_dark", 0x03, metallic=0.45, roughness=0.4)
    steel = pal("station_steel", 0x08, metallic=0.55, roughness=0.3)
    blue = pal("station_blue", 0x36, metallic=0.5, roughness=0.3)
    red = pal("station_red", 0x74, metallic=0.3, roughness=0.3, glow=0.4)
    paint_f = kit.frame("STATION", 144, (72, 28)).fill({0x01}, edge_only=True)
    left = []
    # The axle housing from the end's collar (cut at column 24, radius 7.45) to the docking block.
    xa, xb = f.left(24), f.right(58)
    axle = lathe_x("axle", [(xa, 7.45), (xa + 1.0, 7.45), (xa + 1.4, 5.9), (f.left(33), 5.6), (f.right(51), 5.6),
                            (xb, 5.2)], steel, y0, 0.0, 40)
    kit.pixelate(axle, paint_f)
    kit.paint_sprite(axle, paint_f, paint, wall_steps=2, under=dark, blur=1,
                     keep=lambda v: v >> 4 == 0)
    left.append(axle)
    left.append(lathe_x("blue_band", [(f.left(33), 5.7), (f.left(33) + 0.3, 6.15), (f.right(36) - 0.3, 6.15),
                                      (f.right(36), 5.7)], blue, y0, 0.0, 40))
    left.append(lathe_x("red_clamp", [(f.left(52), 5.5), (f.left(52) + 0.3, 6.2), (f.right(54) - 0.3, 6.2),
                                      (f.right(54), 5.5)], red, y0, 0.0, 40))
    left.append(w.tube("red_rod", [(f.left(54), y0, 5.4 * SQUASH + 0.3), (f.right(58) + 0.3, y0, 5.0 * SQUASH + 0.2)],
                       0.8, red, 10))
    # The docking block at the inner end (columns 59-71).
    block = w.rounded_box("dock", ((f.left(59) + f.right(71)) / 2 + 0.2, y0, 0.0), (12.6, 11.0, 8.0), dark, bevel=1.2)
    kit.paint_faces(block, lambda c, nrm: steel if (nrm.z > 0.5 and (abs(c.y - y0) > 3.5 or c.x < f.left(60) + 1.2))
                    else None)
    left.append(block)
    for dy in (-3.2, 0.0, 3.2):
        left.append(w.rounded_box(f"dock_slat{dy}", (f.left(66), y0 + dy, 4.05), (6.0, 1.3, 0.6), steel, bevel=0.25))
    # The struts above the axle (rows 14-21) and their mirror below: from the hub up and along to the straight
    # panel's stem and on to the diagonal panel.
    upper = []
    path = w.catmull([(X(25.0), Y(21.5), 0.8), (X(26.8), Y(18.0), 1.6), (X(30.0), Y(16.2), 2.0),
                      (X(46.0), Y(16.2), 2.0), (X(50.5), Y(14.6), 1.6), (X(54.0), Y(12.0), 1.0)], 0.5)
    upper.append(w.tube("strut", path, 1.35, steel, 14))
    upper.append(w.tube("stem", [(X(39.0), Y(16.0), 1.8), (X(39.0), Y(12.5), 1.0), (X(39.0), Y(10.2), 0.6)], 1.15,
                        steel, 12))
    upper.append(w.sphere("knuckle", (X(39.0), Y(16.2), 2.2), (1.9, 1.7, 1.5), dark, 14, 7))
    upper += panel("panel_up", (X(39.0), Y(5.0)), 5.5, 0.0, m)
    upper += panel("panel_diag", (X(58.7), Y(9.8)), 5.6, 45.0, m)
    # The dark web between the struts and the axle (the sprite's dark pixels there), set back under them.
    for i, poly in enumerate(kit.polys_of(f, lambda v, c, r: 14 <= r <= 21 and 24 <= c <= 58, smooth=1, epsilon=0.3)):
        upper.append(kit.slab(f"web{i}", poly, -1.4, 0.4, dark, bevel=0.3))
    lower = kit.mirror_y_copies(upper, y0, "_low")
    left += upper + lower
    # The right half: the mirror image across the middle (x = 0).
    kit.mirror_copies(left, 0.0, "_r")


STATION_PIECES = [("station_l_tl", 24, 0), ("station_l_tr", 48, 0), ("station_l_bl", 24, 28), ("station_l_br", 48, 28),
                  ("station_r_tl", 72, 0), ("station_r_tr", 96, 0), ("station_r_bl", 72, 28), ("station_r_br", 96, 28)]
kit.pieced("station", station_whole, (144, 56), [kit.quarter(nm, STATION, c, r) for nm, c, r in STATION_PIECES])


# --- L 1 3 / 39 41 / 77 79: the grey capsule --------------------------------------------------------

# Its half-width along the screen (rows of the 48 x 84 whole), from the sprite.
CAPSULE = [(4.0, 1.5), (4.6, 6.0), (5.2, 10.0), (6.0, 11.6), (7.0, 12.6), (8.0, 13.4), (12.0, 13.5), (13.0, 12.6),
           (14.0, 11.2), (15.0, 9.6), (16.5, 9.2), (17.5, 9.4), (18.4, 11.6), (19.2, 13.4), (55.0, 13.3), (56.0, 11.8),
           (57.0, 9.8), (58.5, 8.2), (60.0, 6.6), (61.5, 6.8), (62.4, 8.4), (63.2, 10.6), (64.2, 11.8), (65.2, 12.6),
           (67.6, 12.6), (68.2, 9.2), (69.2, 10.6), (71.4, 10.6), (72.2, 12.6), (73.6, 12.6), (74.4, 11.4),
           (75.4, 10.0), (76.0, 7.2), (76.9, 6.6)]
CAPSULE_SQUASH = 0.62


def capsule_whole():
    f = POD
    X, Y = f.X, f.Y
    cx = X(24.0)
    paint = kit.Painter("capsule", shades={0: (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)}, metallic=0.3, roughness=0.35,
                        remap={0x01: 0x03})
    dark = pal("capsule_dark", 0x02, metallic=0.4, roughness=0.45)
    red = pal("capsule_red", 0x73, metallic=0.1, roughness=0.35, glow=0.6)
    red_hot = pal("capsule_red_hot", 0x78, metallic=0.0, roughness=0.35, glow=1.6)
    rail = pal("capsule_rail", 0x05, metallic=0.5, roughness=0.35)
    paint_f = kit.frame("POD", 48, (24, 42)).fill({v for row in f.g for v in row if v is not None and v >> 4 == 7},
                                                  edge_only=False)
    # The hull: turned along the screen (nose up), its section squashed.
    profile = [(f.top(0) - row, hw) for row, hw in CAPSULE]
    rings = [k.ring(y, hw, hw * CAPSULE_SQUASH, 40, x=cx) for y, hw in profile]
    hull = k.loft("hull", rings, paint(0x07), start_point=(cx, profile[0][0], 0.0), end_point=(cx, profile[-1][0], 0.0))
    k.smooth(hull, 45)
    kit.pixelate(hull, paint_f)
    kit.paint_sprite(hull, paint_f, paint, wall_steps=2, under=dark, blur=1)
    kit.merge_flat(hull)
    # The red slots (columns 16-18 and 30-32, rows 23-56) along the body's top, glowing, in dark frames; the
    # rails beside them.
    for side, col in ((-1, 17.0), (1, 31.0)):
        x = X(col)
        r = 13.4
        z = CAPSULE_SQUASH * r * math.sqrt(max(0.0, 1 - ((x - cx) / r) ** 2))
        w.rounded_box(f"slot_frame{side}", (x, (Y(23.0) + Y(56.0)) / 2, z - 0.3), (3.8, Y(23.0) - Y(56.0) + 1.4, 1.4),
                      dark, bevel=0.5)
        w.rounded_box(f"slot{side}", (x, (Y(23.0) + Y(56.0)) / 2, z + 0.25), (2.4, Y(23.0) - Y(56.0), 0.8), red,
                      bevel=0.35)
        xr = X(13.5 if side < 0 else 34.5)
        zr = CAPSULE_SQUASH * r * math.sqrt(max(0.0, 1 - ((xr - cx) / r) ** 2))
        w.tube(f"rail{side}", [(xr, Y(19.5), zr - 0.2), (xr, Y(55.0), zr - 0.2)], 1.0, rail, 10)
    # The panel box on the middle (rows 34-45).
    w.rounded_box("panel_box", (cx, Y(39.5), CAPSULE_SQUASH * 13.4 - 0.2), (10.0, 12.0, 1.6), rail, bevel=0.5)
    # The red lights under the flange (rows 60-63) and the glow at the tail (rows 77-78).
    w.lathe_axis("flange_lights", [(0.0, 6.6), (0.3, 7.6), (1.9, 7.6), (2.2, 6.6)], red, (cx, f.top(60) - 0.2, 0.0),
                 (0, -1, 0), 36, squash=CAPSULE_SQUASH)
    w.lathe_axis("exhaust", [(0.0, 7.4), (0.8, 7.0), (1.6, 4.5), (2.0, 0.01)], red_hot, (cx, f.top(77) + 0.1, 0.0),
                 (0, -1, 0), 28, squash=CAPSULE_SQUASH)


CAPSULE_PIECES = [("grey_capsule_tl", 0, 0), ("grey_capsule_tr", 24, 0), ("grey_capsule_ml", 0, 28),
                  ("grey_capsule_mr", 24, 28), ("grey_capsule_bl", 0, 56), ("grey_capsule_br", 24, 56)]
kit.pieced("grey_capsule", capsule_whole, (48, 84), [kit.quarter(nm, POD, c, r) for nm, c, r in CAPSULE_PIECES])


if __name__ == "__main__":
    kit.run()
