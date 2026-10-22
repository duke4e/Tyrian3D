"""Batch AH of wave 3 (sheet M: the asteroid levels, WINDY, SOH JIN and MINERS), modelled as the sprites look
(models.cfg: yaw=0). The armoured dome of the asteroid levels is in polish_armour_dome.py, MINERS' rock column in
wave3_ah_rock.py and MINERS' drilling rig in wave3_ah_rig.py; the kit is wave3_ah_kit.py, the pixels
wave3_ah_art.py.

- block_rubble (M 3): SOH JIN's red block broken (its damaged look: enemy 837 shows it below 20 armour), the
  block's rounded shape cracked into lumps with dark gaps between them.
- block_half_rubble (M 2): what the indestructible red blocks of ASTEROID1 and WINDY (542, 849) name as their
  wreck (dgr 2): the sprite there is the red block's right half beside the broken block's left half, so the
  model is too (the two models cut and put side by side).
- miners_roller_l, miners_roller_r (M 155, 157; enemies 1187, 1188 side by side): MINERS' grey roller on the
  red ground: a toothed grey wheel, a black ribbed roller and a grey motor block with eight plates on its top.
- miners_tank_l, miners_tank_r (M 159, 161; enemies 1189, 1190 side by side): MINERS' blue tank on the red
  ground: a long blue body with panels and a tan rail along its back, a taller end plate on its left and a
  small tab under its right end.
The red ground the roller's and the tank's sprites draw round them is the map's (the game draws it under them):
the models have none (batch AV); they stand on the ground at z 0.
(WINDY's blue question block, block_question (M 55), is built with the other blocks by polish_blocks.py.)

usage: Blender -b --factory-startup -P wave3_ah.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ah_kit as kit  # noqa: E402
from wave3_ah_kit import k, sh, w, pal  # noqa: E402

RUBBLE = kit.frame("RUBBLE", 24, (12, 14))
HALF = kit.frame("HALF", 24, (12, 14))
ROLLER = kit.frame("ROLLER", 48, (24, 14))
TANK = kit.frame("TANK", 48, (24, 14))

# The WINDY blocks' body (polish_blocks.py): 11 x 12.6 half sizes, 9 high to the top's edge, the top bulging 1.2
# more.
HALF_W, HALF_D, HEIGHT, DOME = 11.0, 12.6, 9.0, 1.2
TOP = HEIGHT + DOME


# --- M 3: the broken red block -----------------------------------------------------------------------------------

# The lumps the broken block lies in, as the sprite draws them: (centre x, y, half width, half depth, height).
CHUNKS = [(-7.4, 8.4, 3.5, 4.0, 7.6), (-1.6, 9.6, 2.7, 2.9, 6.2), (5.9, 7.6, 4.8, 4.8, 8.4), (-7.2, -0.8, 3.6, 4.6, 5.4),
          (2.4, -0.2, 4.4, 3.4, 6.8), (-6.6, -8.8, 4.1, 3.6, 6.2), (6.4, -8.4, 4.4, 3.9, 7.2), (-0.4, -8.6, 2.0, 2.6, 3.8),
          (-2.6, 3.6, 2.0, 2.2, 4.2)]


def rubble(name, f, x_shift=0.0):
    """The red block broken: angular lumps of it (convex hulls of jittered blocks, tilted a little) lying on a
    low bed of dark crumbs within the block's outline, their tops in the red of the sprite's lumps."""
    import random
    rnd = random.Random(5)
    is_red = lambda v: v >> 4 == 4 and (v & 15) >= 3
    lit = kit.field_sampler(f, kit.field(f, lambda v: (v & 15) if is_red(v) else 4.0, lambda v: True, blur=1))
    crumbs = pal("br_crumbs", 0x42, metallic=0.05, roughness=0.7)
    base = k.pillow(f"{name}_bed", HALF_W - 0.6, HALF_D - 0.6, 1.4, crumbs, rounding=1.0, dome=0.4)
    kit.jitter(base, 0.25, seed=3, scale=0.9, min_z=0.3)
    reds = None
    out = [base]
    for i, (cx, cy, hx, hy, hz) in enumerate(CHUNKS):
        # A broken piece: its top a part of the block's surface (flat, a little tilted), its sides broken.
        tilt_x, tilt_y = rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12)
        pts = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts.append((cx + sx * hx * rnd.uniform(0.85, 1.0), cy + sy * hy * rnd.uniform(0.85, 1.0), 0.2))
                for mid in (0.62, 0.9):
                    pts.append((cx + sx * hx * rnd.uniform(0.9, 1.0) * (1.0 if mid < 0.8 else 0.93),
                                cy + sy * hy * rnd.uniform(0.9, 1.0) * (1.0 if mid < 0.8 else 0.93),
                                hz * mid * rnd.uniform(0.92, 1.0)))
                tx, ty = sx * hx * rnd.uniform(0.6, 0.78), sy * hy * rnd.uniform(0.6, 0.78)
                pts.append((cx + tx, cy + ty, hz + tilt_x * tx + tilt_y * ty))
        chunk = kit.aa.convex_rock(f"{name}_chunk{i}", pts, None)
        kit.band_paint(chunk, "br_red", 4, lambda x, y: lit(x, y) + 1.0, (4, 5, 6, 7, 8, 9, 10, 11), wall=2.5,
                       under=3.0, metallic=0.05, roughness=0.32)
        k.smooth(chunk, 35)
        out.append(chunk)
    if x_shift:
        for obj in out:
            obj.data.transform(Matrix.Translation((x_shift, 0, 0)))
    return out


@kit.model("block_rubble", mask=lambda: RUBBLE.mask())
def block_rubble():
    rubble("rubble", RUBBLE)


# --- M 2: the red block's right half beside the broken block's left half --------------------------------------

@kit.model("block_half_rubble", mask=lambda: HALF.mask())
def block_half_rubble():
    shell = pal("block_red", 71, metallic=0.05, roughness=0.3)  # block_red's material (polish_blocks.py)
    blk = k.pillow("block", HALF_W, HALF_D, HEIGHT, shell, rounding=3.6, dome=DOME)
    blk.data.transform(Matrix.Translation((-12.0, 0, 0)))
    rub = rubble("rubble", RUBBLE, x_shift=12.0)
    kept = sh.cut_box([blk] + rub, -12.0, 12.0, -14.0, 14.0)
    for obj in kept:
        k.smooth(obj, 40)


# --- Painting flat parts by the sprite ---------------------------------------------------------------------------

def pixel_paint(obj, painter, f):
    """Cuts the part's faces along the pixel grid, paints them by the sprite and merges like flat faces."""
    kit.pixelate(obj, f)
    painter(obj)
    kit.merge_flat(obj)
    return obj


# --- M 155, 157: the roller --------------------------------------------------------------------------------------

def roller_whole():
    f = ROLLER
    grey = kit.RampPainter("ro", f, ramps={0, 6, 5}, fallback=6, blur=1, wall=1.0,
                           shades={0: (3, 5, 7, 9, 11, 12), 6: (6, 8, 9, 10, 11, 12, 13), 5: (13, 15)},
                           finish={0: (0.6, 0.3), 6: (0.6, 0.3), 5: (0.5, 0.3)})
    steel = pal("ro_steel", 0x69, metallic=0.6, roughness=0.3)
    steel_dark = pal("ro_steel_dark", 0x66, metallic=0.6, roughness=0.35)
    rubber = pal("ro_rubber", 0x03, metallic=0.1, roughness=0.6)
    rib = pal("ro_rib", 0x06, metallic=0.2, roughness=0.5)

    # The black roller (cols 10-32, rows 7-19), ribbed round, its ribs on the ground.
    axis_z = 6.5
    x0, x1 = f.left(10) + 0.2, f.right(32) - 0.5
    y_mid = (f.Y(7) + f.Y(19)) / 2
    w.lathe_axis("roller", [(0.0, 5.4), (0.4, 6.1), (x1 - x0 - 0.4, 6.1), (x1 - x0, 5.4)], rubber,
                 (x0, y_mid, axis_z), (1, 0, 0), 28)
    n_ribs = 9
    for i in range(n_ribs):
        x = x0 + 1.4 + (x1 - x0 - 2.8) * i / (n_ribs - 1)
        ring = kit.torus(f"rib{i}", (0, 0, 0), 6.05, 0.42, rib, 28, 8)
        sh.apply_modifiers(ring)
        kit.orient(ring, (x, y_mid, axis_z), (1, 0, 0))

    # The toothed wheel on its left end (cols 2-10, rows 2-23).
    wx0, wx1 = f.left(3), f.right(9)
    wy = (f.Y(2) + f.Y(23)) / 2
    wr = 10.4
    wheel = w.lathe_axis("wheel", [(0.0, wr - 1.0), (0.5, wr), (wx1 - wx0 - 0.5, wr), (wx1 - wx0, wr - 1.0)], steel,
                         (wx0, wy, wr), (1, 0, 0), 40)
    for i in range(14):
        a = 2 * math.pi * (i + 0.5) / 14
        cz, cy = wr + (wr + 0.6) * math.sin(a), wy + (wr + 0.6) * math.cos(a)
        if cz < 0.8:
            continue
        tooth = w.rounded_box(f"tooth{i}", (0.0, 0.0, 0.0), (wx1 - wx0 - 0.8, 2.2, 1.8), steel_dark, bevel=0.3)
        sh.apply_modifiers(tooth)
        tooth.data.transform(Matrix.Translation(((wx0 + wx1) / 2, cy, cz)) @ Matrix.Rotation(a + math.pi / 2, 4, "X"))
    hub = w.lathe_axis("hub", [(0.0, 3.6), (0.8, 3.4), (1.6, 2.2)], steel_dark, (wx1, wy, wr), (1, 0, 0), 20)
    grey(wheel)

    # The motor block (cols 32-44, rows 1-26) with eight plates on its top (2 x 4).
    bx0, bx1 = f.left(32) + 0.3, f.right(44) - 0.3
    by0, by1 = f.bottom(26) + 0.3, f.top(1) - 0.3
    block_h = 12.5
    body = w.rounded_box("motor", ((bx0 + bx1) / 2, (by0 + by1) / 2, block_h / 2), (bx1 - bx0, by1 - by0, block_h),
                         steel, bevel=1.0, segments=2)
    pixel_paint(body, grey, f)
    for i in range(2):
        for j in range(4):
            px0 = bx0 + 1.0 + i * (bx1 - bx0 - 2.0) / 2
            px1 = px0 + (bx1 - bx0 - 2.0) / 2 - 0.8
            py1 = by1 - 1.0 - j * (by1 - by0 - 2.0) / 4
            py0 = py1 - (by1 - by0 - 2.0) / 4 + 0.8
            plate = w.rounded_box(f"plate{i}{j}", ((px0 + px1) / 2, (py0 + py1) / 2, block_h + 0.3),
                                  (px1 - px0, py1 - py0, 0.9), steel, bevel=0.3, segments=1)
            pixel_paint(plate, grey, f)
    # The axle from the block into the roller.
    w.lathe_axis("axle", [(0.0, 3.0), (1.6, 3.0)], steel_dark, (bx0 - 1.2, y_mid, axis_z), (1, 0, 0), 20)


kit.pieced("miners_roller", roller_whole, (48, 28),
           [kit.quarter("miners_roller_l", ROLLER, 0, 0), kit.quarter("miners_roller_r", ROLLER, 24, 0)])


# --- M 159, 161: the tank ----------------------------------------------------------------------------------------

def tank_whole():
    f = TANK
    paint = kit.RampPainter("tk", f, ramps={3, 8, 6, 10, 5}, fallback=3, blur=1, wall=1.2,
                            shades={3: (3, 4, 5, 6, 7, 8, 9, 10), 8: (0, 2, 4), 6: (1, 2, 3, 4, 5), 10: (4, 5, 6, 7, 8),
                                    5: (1, 3)},
                            finish={3: (0.35, 0.35), 8: (0.4, 0.35), 6: (0.4, 0.4), 10: (0.5, 0.3), 5: (0.3, 0.4)})
    blue = pal("tk_blue", 0x36, metallic=0.35, roughness=0.35)

    # The body (cols 10-43, rows 6-22): a long box, its top rounded across.
    x0, x1 = f.left(10), f.right(43) - 0.2
    y0, y1 = f.bottom(22) + 0.2, f.top(6) - 0.1
    height = 10.5
    body = kit.prism_x("body", [(y0, 0.0), (y1, 0.0), (y1, height - 2.2), (y1 - 1.2, height - 0.5),
                                (y1 - 3.0, height), ((y0 + y1) / 2, height + 0.4), (y0 + 3.0, height),
                                (y0 + 1.2, height - 0.5), (y0, height - 2.2)], x0, x1, blue, bevel=0.5)
    pixel_paint(body, paint, f)
    # The tan rail along its back (rows 6-7).
    rail = pal("tk_rail", 0xa6, metallic=0.5, roughness=0.3)
    w.rounded_box("rail", ((x0 + x1) / 2 + 0.4, y1 - 0.9, height - 0.6), (x1 - x0 - 1.0, 1.6, 1.6), rail, bevel=0.4)
    # The end plate on its left (cols 4-11, rows 1-22), taller than the body.
    ex0, ex1 = f.left(4) + 0.2, f.right(10)
    ey0, ey1 = f.bottom(22) + 0.2, f.top(1) - 0.2
    end = w.rounded_box("end", ((ex0 + ex1) / 2, (ey0 + ey1) / 2, 7.0), (ex1 - ex0, ey1 - ey0, 14.0), blue,
                        bevel=1.0, segments=2)
    pixel_paint(end, paint, f)
    # The tab under its right end (cols 33-36, rows 22-24).
    tab = w.rounded_box("tab", (f.X(34.5), f.Y(23.0), 2.5), (3.2, 3.2, 5.0), blue, bevel=0.5)
    paint(tab)


kit.pieced("miners_tank", tank_whole, (48, 28),
           [kit.quarter("miners_tank_l", TANK, 0, 0), kit.quarter("miners_tank_r", TANK, 24, 0)])


if __name__ == "__main__":
    kit.run()
