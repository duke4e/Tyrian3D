"""Batch AK of wave 3 (sheet b, written b in models.cfg): CAMANIS' boss and its damaged look, modelled as the sprites
look (models.cfg: yaw=0), built whole and cut into its sprites' pieces, drawn at their own origins (origin) so they
meet. The kit is wave3_ak_kit.py, the pixels wave3_ak_art.py (BOSS, BOSS_DMG).

The level events (CAMANIS, six times) put the boss together from 23 sprites, all sky enemies (201-223), in rows
spawned 14 ticks apart (28 pixels): 2 4 6 8 at (x + 12, y) ... ; 39 41 43 45 47 at (x, y + 28) ...;
77 79 81 83 85; 115 117 119 121 123; 154 156 158 160 under them, as the sheet lays them out: 120 x 140 pixels,
symmetric about pixel column 59 (x = -0.5 here), origin (60, 70).

What it is: a flying fortress seen from above, its nose (a turret) down the screen. Two dark blue tanks run
down the screen from two engine hoods at its top and bend into one U at its bottom, their bend swelling into a
heart-shaped basin; grey grid plates wrap the tanks, a ribbed panel on each tank's inner side, a machinery block
with a vent and a grid plate sits in the U. The hoods: dark grey wedges with three red vents and a grille on
top, sloping down the screen into wide purple skirts. Beside the tanks two glowing blue lamps. Under it all a
wide grey bowl of a hull (purple wings at its sides, grey ribs, panel lines, a gun port either side), its two
gun barrels with red lamps pointing down the screen either side of a raised chin. On the hull's rim either side
two beaded antenna masts reach up the screen, a valve on each.

- camanis_boss_<sprite> for the 23 sprites. 39 and 47 (the masts' pieces) replace wave1_d's mast_left and
  mast_right, which modelled those two sprites on their own.
- The damaged looks (dgr: each piece switches to its own when hit hard, in place): camanis_boss_12 14 16 18
  (of 2 4 6 8; the hoods' flanks burst, embers glowing in the breaches), 49 51 53 55 208 (of 39-47: the right
  outer mast's casing blown off its core), 87 89 91 93 246, 125 127 129 131 284, 164 166 168 170: the hull's
  plating smashed in, craters and debris on its left and along its bottom, embers in cracks on its right. Same
  shapes as the intact pieces (so that they swap in place), painted by the damaged sprites (the top row's
  damaged sprites are drawn a pixel higher than the intact ones: read a row lower).

usage: Blender -b --factory-startup -P wave3_ak_boss.py -- [--only names] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ak_kit as kit  # noqa: E402
from wave3_ak_kit import k, w, pal, Painter, smoothstep  # noqa: E402

ORIGIN = (60, 70)
AX = -0.5          # the boss is symmetric about x = -0.5 (pixel column 59): column c mirrors 118 - c
OUTLINE = {0x01, 0x02}

BOSS = kit.frame("BOSS", 120, ORIGIN)            # the pixels as drawn (regions, masks)
DMG = kit.frame("BOSS_DMG", 120, ORIGIN)         # the damaged look as drawn (its masks)


def X(col):
    return col + 0.5 - ORIGIN[0]


def Y(row):
    return ORIGIN[1] - (row + 0.5)


def row_of(y):
    return ORIGIN[1] - y - 0.5


def mirror_col(c):
    return 118 - c


def paint_frame():
    """The intact boss for painting: the outline at the edge taking the colour inside it, the left half (lit by
    the sprite's light from the left) mirrored over the right, so that the model's own light shades both."""
    f = kit.frame("BOSS", 120, ORIGIN).fill(OUTLINE).symmetric(59)
    f.raw = [row[:] for row in BOSS.g]
    return f


def damaged_frame():
    """The damaged look painted over the intact paint frame: pixels that differ from the intact sprite's take the
    damaged sprite's (the top row's damaged sprites read a row lower); pixels the damage took away go dark; the
    dark red of cracks becomes glowing embers."""
    base = paint_frame()
    out = kit.patched(base, DMG, shift=lambda c, r: (0, -1) if r < 28 else (0, 0))
    for r in range(out.height):
        for c in range(out.width):
            dr = -1 if r < 28 else 0
            d, i = DMG.get(c, r + dr), BOSS.get(c, r)
            if i is not None and d is None:
                out.g[r][c] = 0x01                    # torn away: a dark hole
            elif d is not None and d >> 4 == 7 and d != i and not (r <= 6 and (33 <= c <= 49 or 69 <= c <= 85)):
                out.g[r][c] = 0x75 + min(2, d & 15)   # embers in cracks (not the hoods' own red vents)
    return out


def painter(prefix):
    return Painter(prefix, shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc),
                                   5: (0, 2, 4, 5, 6, 7, 9, 0xa, 0xb, 0xc),
                                   7: (1, 2, 5, 6, 7, 0xa, 0xc), 3: (2, 3, 4, 5, 6, 7, 8, 0xa),
                                   9: (2, 4, 6, 8, 0xa, 0xc, 0xe), 8: (5, 8, 0xb)},
                   metallic=0.55, roughness=0.34,
                   glow={0x75: 0.7, 0x76: 0.9, 0x77: 1.1, 0x7a: 1.6, 0x7c: 2.0,
                         0x92: 0.5, 0x94: 0.8, 0x96: 1.1, 0x98: 1.4, 0x9a: 1.7, 0x9c: 2.0, 0x9e: 2.4},
                   finish={5: (0.35, 0.36), 7: (0.1, 0.45), 9: (0.1, 0.15), 3: (0.6, 0.2), 8: (0.6, 0.2)},
                   remap={0x00: 0x01})


def paint(obj, f, p, walls=-2, probe=-0.5, grid=False, blur=0, default=None, shift=0.0):
    """Paints a part by the pixels under it (its underside one dark colour), then merges flat stretches of one
    colour into few triangles; grid: its faces cut along the pixel grid first (exact pixels on flat tops)."""
    if grid:
        kit.pixelate(obj, f, step=1.0)
    kit.paint_sprite(obj, f, p, wall_steps=walls, blur=blur, probe=probe, under=p(0x01),
                     default=default if default is not None else p(0x03), shade_shift=shift)
    kit.delete_faces(obj, lambda c, nrm: nrm.z < -0.95)
    return kit.merge_flat(obj, angle=1.0)


def region(f, keep, smooth=2):
    return kit.polys_of(f, lambda val, c, r: val is not None and keep(val, c, r), smooth=smooth,
                        epsilon=0.3 if smooth < 2 else 0.4, min_area=1.0)


# --- The hull -------------------------------------------------------------------------------------------------

# The hull's top edge (rows) along the left half's columns: under the masts it runs diagonally down to the
# left; under the tanks it is hidden.
EDGE = [(0, 82.0), (4, 81.5), (5, 81.0), (7, 79.5), (10, 78.0), (13, 76.0), (16, 74.0), (18, 72.5), (20, 71.0),
        (23, 69.5), (28, 67.0), (31, 66.0), (32, 64.0), (53, 64.0), (54, 73.0), (59, 73.0)]


def edge_row(c):
    c = min(c, mirror_col(c))
    for (c0, r0), (c1, r1) in zip(EDGE, EDGE[1:]):
        if c0 <= c <= c1:
            return r0 + (r1 - r0) * (c - c0) / max(c1 - c0, 1e-6)
    return EDGE[-1][1]


def is_hull(c, r):
    return r >= edge_row(c)


def hull_z(x, y):
    """The bowl's top over (x, y): highest in its middle, falling round its rim."""
    dx = (x - AX) / 58.5
    dy = min(0.0, y + 14.0) / 55.0
    rho = min(1.0, math.hypot(dx, dy))
    return 2.0 + 12.0 * (1.0 - rho ** 2.4) ** 0.55


def hull(f, p, damage=None):
    polys = region(BOSS, lambda val, c, r: is_hull(c, r), smooth=3)
    # Sampled every pixel on the pixel grid (pixel corners fall on whole numbers): two triangles a pixel, each
    # painted exactly by its pixel.
    body = kit.heightfield("hull", polys, lambda x, y, e: hull_z(x, y) * (0.3 + 0.7 * e), p(0x06), spacing=1.0,
                           edge=3.0)
    # The sprite's shading as relief: ribs and plates raised, panel lines and grooves sunk.
    def relief(val):
        ramp, shade = val >> 4, val & 15
        if ramp in (0, 5) and shade <= 3:
            return -0.8
        if (ramp == 0 and shade >= 9) or (ramp == 5 and shade >= 0xb):
            return 0.5
        return 0.0
    field = w.sampler(f.g, ORIGIN, value=relief, blur=1, keep=lambda val: val is not None)
    kit.emboss(body, field, 1.0, min_nz=0.55)
    parts = [body]
    if damage is not None:  # the smashed plating pushed in, unevenly
        field = damage
        kit.displace_z(body, lambda x, y, z: -3.6 * field(x, y) * (0.7 + 0.3 * noise.noise(Vector((x / 2.3, y / 2.3,
                                                                                                    0.5))))
                       if z > 1.0 else 0.0)
    # A shade darker than the sprite: the sprite's light from the left is painted on both sides, and the model's
    # own light brightens the bowl's left slope again.
    paint(body, f, p, walls=-2, probe=-0.6, shift=-1.0)
    return parts


# --- The tanks ---------------------------------------------------------------------------------------------------

ZT, RT = 13.0, 11.0     # the tanks' axis height and radius
TANK_L, TANK_R = -17.0, 16.0
BEND_Y = -20.0


def tank_top(x, lift_=0.0):
    """The height of the left tank's top over x (its straight run), `lift_` out from its surface."""
    return ZT + math.sqrt(max(0.0, (RT + lift_) ** 2 - (x - TANK_L) ** 2))


def paint_tank(obj, f, p, blues, grey=True):
    """The tanks: blue by their shape (lighter on top, a glint on the upper left, dark beneath), glossy; where
    the sprite has grey (bands, grilles) on their straight runs, its grey."""
    def pick(c, nrm):
        val = f.at(c.x, c.y)
        if grey and c.y > Y(71.0) and val is not None and val >> 4 == 0 and (val & 15) >= 3 and nrm.z > 0.3:
            return p(val)
        if nrm.z < -0.4:
            return blues[0]
        if nrm.x < -0.35 and nrm.z > 0.45:
            return blues[4]
        if nrm.z > 0.8:
            return blues[3]
        if nrm.z > 0.45:
            return blues[2]
        return blues[1]
    kit.paint_faces(obj, pick)


def tanks(f, p):
    blues = [pal("tank_32", 0x32, metallic=0.6, roughness=0.25), pal("tank_34", 0x34, metallic=0.6, roughness=0.2),
             pal("tank_35", 0x35, metallic=0.6, roughness=0.18), pal("tank_36", 0x36, metallic=0.6, roughness=0.16),
             pal("tank_38", 0x38, metallic=0.55, roughness=0.14)]
    u = kit.pipe("tank", [(TANK_L, 46.0, ZT), (TANK_L, BEND_Y, ZT), (TANK_R, BEND_Y, ZT), (TANK_R, 46.0, ZT)], RT,
                 blues[2], bend=13.0, segments=28, step=1.0)
    # The bend swells into a heart-shaped basin (as the sprite draws it): a fat lobe round each tank's turn,
    # and the middle between them filled.
    lobe = kit.ico_ellipsoid("tank_lobe", (TANK_L + 2.6, -17.2, ZT), (13.4, 14.0, 11.4), blues[2], 4)
    lobes = [lobe] + kit.mirror_copies([lobe], AX)
    core = kit.ico_ellipsoid("tank_core", (AX, -12.5, ZT + 0.5), (9.0, 8.8, 10.4), blues[2], 3)
    for obj in [u, core] + lobes:
        kit.delete_faces(obj, lambda c, nrm: nrm.z < -0.9 and c.z < ZT - RT + 1.0)
        paint_tank(obj, f, p, blues, grey=obj is u)
    parts = [u, core] + lobes
    # Grey grid plates wrapping the tanks (rows 28-44), the ribbed panels on their inner sides (rows 57-71),
    # the rails along their inner edges (rows 43-58).
    left = []
    for name, c0, c1, r0, r1, lift_ in (("tank_plate", 34.6, 48.6, 27.6, 44.5, 0.75),
                                        ("tank_ribs", 35.6, 41.4, 56.6, 71.4, 0.6)):
        poly = [(X(c0) - 0.5, Y(r1) - 0.5), (X(c1) + 0.5, Y(r1) - 0.5), (X(c1) + 0.5, Y(r0) + 0.5),
                (X(c0) - 0.5, Y(r0) + 0.5)]
        # Curved with the tank, its edges tucked into it.
        obj = kit.heightfield(name, [poly], lambda x, y, e, l_=lift_: tank_top(x, l_) * (0.92 + 0.08 * e),
                              p(0x06), spacing=0.5, edge=0.6)
        paint(obj, f, p, walls=-2, probe=-0.3, grid=True)
        left.append(obj)
    rail = w.tube("tank_rail", [(X(54) + 0.3, Y(43), ZT + 1.5), (X(54) + 0.3, Y(58.5), ZT + 1.5)], 0.85, p(0x05), 10)
    paint(rail, f, p, walls=-1, probe=0.0)
    left.append(rail)
    parts += left + kit.mirror_copies(left, AX)
    return parts


# --- The machinery in the U -----------------------------------------------------------------------------------

def machinery(f, p):
    parts = []
    # The lower block (rows 91-103), its top over the bend.
    block = w.rounded_box("block", (AX, (Y(90.6) + Y(103.4)) / 2, 16.0), (16.6, 13.0, 18.6), p(0x05), bevel=1.0)
    # The grid plate over the basin (rows 86-89) and the small vent above it (rows 82-85).
    plate = w.rounded_box("block_plate", (AX, (Y(85.6) + Y(89.4)) / 2, 22.6), (12.4, 4.4, 6.0), p(0x05), bevel=0.6)
    vent = w.rounded_box("block_vent", (AX, (Y(81.6) + Y(85.4)) / 2, 22.8), (8.4, 4.4, 6.4), p(0x05), bevel=0.6)
    for obj in (block, plate, vent):
        paint(obj, f, p, walls=-2, probe=-0.4, grid=True)
        parts.append(obj)
    return parts


# --- The hoods ------------------------------------------------------------------------------------------------------

def is_hood(val, c, r):
    if c > 58 or c < 18 or r > 34:
        return False
    if r >= 19 and val >> 4 in (3, 8):
        return False
    return not (r >= 28 and 31 <= c <= 53)


def hood_left_col(r):
    """The hood's left outline (pixel column) at a row: diagonal down to the left, then straight."""
    return 33.0 - (min(r, 25.0) - 1.0) * 0.5


def hood_z(x, y, e):
    """A wedge: flat on top (rows 1-13), sloping down the screen into its skirt; a narrow bevel down its left
    edge, its right flank falling away."""
    r = row_of(y)
    c = x + ORIGIN[0] - 0.5
    t = min(1.0, max(0.0, (r - 13.0) / 21.0))
    z = 28.0 - 19.0 * t
    z -= max(0.0, x - X(49.0)) * 2.2
    z *= 0.58 + 0.42 * smoothstep(0.3, 4.2, c - hood_left_col(r))
    return max(4.0, z) * (0.7 + 0.3 * e)


def hoods(f, p, broken=False):
    polys = region(BOSS, is_hood, smooth=2)
    hood = kit.heightfield("hood", polys, hood_z, p(0x04), spacing=0.6, edge=1.2)
    # The red vents sunk into the top.
    red = lambda x, y: BOSS.at(x, y) is not None and BOSS.at(x, y) >> 4 == 7  # noqa: E731
    kit.displace_z(hood, lambda x, y, z: -0.9 if z > 26.0 and all(red(x + dx, y + dy) for dx in (-0.4, 0.4)
                                                                    for dy in (-0.4, 0.4)) else 0.0)
    parts = [hood] + kit.mirror_copies([hood], AX)
    if broken:
        # The left hood's right flank burst; the right hood cracked on top and its outer flank torn off.
        kit.dent(parts[0], (X(52.0), Y(14.0)), 6.0, 5.0, seed=1.0)
        kit.dent(parts[1], (X(77.5), Y(9.5)), 3.4, 2.4, seed=2.0)
        kit.dent(parts[1], (X(88.5), Y(16.0)), 7.5, 7.0, seed=3.0)
    for obj in parts:
        paint(obj, f, p, walls=-2, probe=-0.4, grid=True)
    return parts


# --- The lamps, the gun ports ----------------------------------------------------------------------------------------

def lamps(f, p):
    # Half tucked under the tank's side, as the sprite shows its outer half.
    lamp = kit.ico_ellipsoid("lamp", (X(30.6), Y(59.0), 7.0), (7.9, 13.6, 7.6), p(0x96), 4)
    kit.delete_faces(lamp, lambda c, nrm: nrm.z < -0.2)
    shades = [pal(f"lamp_{i:02x}", i, metallic=0.1, roughness=0.12, glow=g)
              for i, g in ((0x93, 0.6), (0x95, 0.9), (0x98, 1.3), (0x9b, 1.7), (0x9e, 2.3))]

    def glass(c, nrm):
        """Glowing blue glass, its glint on the upper left (as the sprite draws it)."""
        if nrm.z > 0.45 and nrm.x < -0.2 and nrm.y > -0.1 and -0.75 * nrm.x + 0.5 * nrm.y > 0.42:
            return shades[4] if -0.75 * nrm.x + 0.5 * nrm.y > 0.55 else shades[3]
        if nrm.z > 0.75:
            return shades[2]
        return shades[1] if nrm.z > 0.25 else shades[0]
    kit.paint_faces(lamp, glass)
    parts = [lamp]
    # The gun port beside the tank's bend: a light grey hatch with a dim red muzzle in it.
    x, y = X(28.0), Y(91.5)
    z = hull_z(x, y)
    hatch = w.rounded_box("port", (x, y, z + 0.2), (6.6, 7.6, 2.0), p(0x0a), bevel=0.5)
    paint(hatch, f, p, walls=-2, probe=-0.3, grid=True)
    muzzle = kit.lens("port_muzzle", (x, y, z + 1.25), (0.0, 0.0, 1.0), (1.7, 1.9, 0.5),
                      pal("muzzle", 0x72, metallic=0.1, roughness=0.3, glow=0.6), sink=0.1, segments=16)
    parts += [hatch, muzzle]
    return parts + kit.mirror_copies(parts, AX)


# --- The turret ----------------------------------------------------------------------------------------------------

def turret(f, p):
    parts = []
    # The raised chin between the barrels (columns 55-63, rows 113-128).
    cx, cy = AX, (Y(112.6) + Y(128.4)) / 2
    chin = w.rounded_box("chin", (cx, cy, hull_z(cx, cy) + 0.2), (9.0, 15.6, 4.6), p(0x06), bevel=1.2)
    paint(chin, f, p, walls=-2, probe=-0.4, grid=True)
    parts.append(chin)
    # The left barrel (columns 50-52) from the slot (row 113) to its lamp (rows 122-127).
    bx = X(51.0)
    y0, y1 = Y(112.5), Y(121.5)
    z = hull_z(bx, (y0 + y1) / 2) + 1.4
    barrel = w.lathe_axis("barrel", [(0.0, 1.9), (0.6, 1.6), (9.0, 1.6), (9.4, 1.9), (10.0, 1.9)], p(0x07),
                          (bx, y0 + 0.6, z), (0.0, -1.0, 0.0), 14, smooth_angle=50)
    paint(barrel, f, p, walls=-1, probe=0.0)
    socket = w.lathe_axis("barrel_socket", [(0.0, 2.0), (1.0, 2.25), (4.6, 2.25), (5.4, 1.8), (5.8, 0.6)], p(0x07),
                          (bx, Y(121.6), z), (0.0, -1.0, 0.0), 16, smooth_angle=50)
    paint(socket, f, p, walls=-1, probe=0.0)
    lamp = kit.lens("barrel_lamp", (bx, Y(124.6), z + 1.8), (0.0, -0.25, 1.0), (1.45, 2.1, 0.8),
                    pal("barrel_lamp", 0x76, metallic=0.1, roughness=0.2, glow=1.8), sink=0.2, segments=16)
    parts += [barrel, socket, lamp]
    return parts[:1] + parts[1:] + kit.mirror_copies(parts[1:], AX)


# --- The masts -----------------------------------------------------------------------------------------------------

def mast(name, col, rows, mat, tilt=0.06, z0=5.6, segments=16):
    """A turned mast lying along the screen at pixel column `col`, rising `tilt` per pixel up the screen; rows:
    (row, radius) from its foot to its tip."""
    x = X(col)
    y_base = ORIGIN[1] - rows[0][0]
    prof = []
    for r, rad in rows:
        prof.append((ORIGIN[1] - r - y_base, rad))
    dense = [prof[0]]
    for (ya, ra), (yb, rb) in zip(prof, prof[1:]):  # a ring every pixel, for painting
        steps = max(1, int(round(yb - ya)))
        dense += [(ya + (yb - ya) * i / steps, ra + (rb - ra) * i / steps) for i in range(1, steps + 1)]
    length = dense[-1][0]
    direction = Vector((0.0, 1.0, tilt)).normalized()
    scale = math.sqrt(1.0 + tilt * tilt)
    return w.lathe_axis(name, [(t * scale, rad) for t, rad in dense], mat, (x, y_base, z0), tuple(direction),
                        segments, smooth_angle=55)


TIP = [(42.5, 3.5), (42.0, 2.6), (41.6, 1.45), (39.0, 1.45), (38.7, 2.45), (36.3, 2.45), (36.0, 1.2),
       (33.0, 1.25), (32.4, 1.45), (31.8, 1.15), (30.4, 1.45), (29.6, 1.1), (29.1, 0.3)]


def mast_rows(base, shift, broken=False):
    """The profile of a mast whose tip is `shift` rows below mast A's (row 29): its foot (base), its body
    (rows 42.5-54 of mast A, a valve at its side) and the beaded tip; broken: its body's casing blown off,
    leaving a thin core up to the collar."""
    body = [(54.0, 2.5), (53.6, 3.1), (53.0, 3.5), (45.0, 3.55), (42.5, 3.5)] + TIP[1:]
    if broken:
        body = [(54.0, 2.45), (53.2, 1.7), (40.8, 1.7), (40.2, 2.3), (39.6, 1.45)] + TIP[3:]
    out = list(base)
    for r, rad in body:
        if r + shift < out[-1][0] - 0.05:
            out.append((r + shift, rad))
    return out


def masts(f, p, broken_right=False):
    grey = p(0x06)
    # Mast A (columns 12-18): a wide foot block (rows 65-80), a neck (rows 54-64), the body with a valve, the tip.
    a_rows = mast_rows([(80.5, 3.45), (65.2, 3.45), (64.6, 3.0), (64.0, 2.45), (54.2, 2.45)], 0.0)
    # Mast B (columns 1-9): a neck from the hull (rows 70-80), then the same body and tip, 16 rows lower.
    b_rows = mast_rows([(81.0, 2.45), (70.2, 2.45)], 16.0)
    b_broken = mast_rows([(81.0, 2.45), (70.2, 2.45)], 16.0, broken=True)

    def one_side(suffix, mirror, broken):
        parts = [mast("mast_a" + suffix, 15.0, a_rows, grey),
                 mast("mast_b" + suffix, 6.0, b_broken if broken else b_rows, grey, z0=5.2)]
        # The valves on the bodies' outer sides, the pole between the masts' feet.
        parts.append(w.sphere("mast_a_valve" + suffix, (X(10.6), Y(47.6), 5.6 + 0.06 * (80.5 - 47.6) + 0.2),
                              (1.35, 2.2, 1.35), grey, 14, 8))
        if not broken:
            parts.append(w.sphere("mast_b_valve" + suffix, (X(1.6), Y(62.6), 5.2 + 0.06 * (81.0 - 62.6) + 0.2),
                                  (1.35, 2.2, 1.35), grey, 14, 8))
        else:
            # The casing's torn stump at the body's foot, a shard of purple plating behind it, a bent rod.
            zb = 5.2 + 0.06 * (81.0 - 70.4)
            ring = mast("mast_b_ring" + suffix, 6.0, [(70.6, 3.2), (69.6, 3.4), (68.4, 3.2)], grey, z0=zb)
            kit.jag(ring, (X(6.0), Y(68.4), zb + 0.12), (0, 1, 0.06), 1.4, scale=0.7, seed=4.0)
            parts.append(ring)
            shard = w.rounded_box("mast_b_shard" + suffix, (0.0, 0.0, 0.0), (4.6, 6.4, 0.9), grey, bevel=0.3)
            shard.data.transform(Matrix.Translation((X(9.6), Y(66.2), 4.6)) @ Matrix.Rotation(0.5, 4, "Y") @
                                 Matrix.Rotation(0.25, 4, "Z"))
            parts.append(shard)
            parts.append(w.tube("mast_b_rod" + suffix, [(X(9.2), Y(64.5), 6.0), (X(9.4), Y(60.0), 7.6),
                                                        (X(10.4), Y(56.0), 8.6)], 0.6, grey, 8))
        parts.append(w.tube("mast_pole" + suffix, [(X(9.0), Y(80.5), 4.4), (X(9.0), Y(69.6), 5.4)], 0.95, grey, 10))
        if mirror:
            for obj in parts:
                k.recalc_normals(obj)
            mirrored = kit.mirror_copies(parts, AX)
            for obj in parts:
                bpy.data.objects.remove(obj)
            parts = mirrored
        return parts
    parts = one_side("", False, False) + one_side("_r", True, broken_right)
    for obj in parts:
        paint(obj, f, p, walls=-2, probe=-0.35)
    return parts


# --- Damage -----------------------------------------------------------------------------------------------------------

def damage_field():
    """Where the damaged sprite smashed the hull's plating (pixels that differ from the intact sprite and are
    dark, torn away or embers), smoothed: 0-1."""
    g = []
    for r in range(BOSS.height):
        row = []
        for c in range(BOSS.width):
            i, d = BOSS.get(c, r), DMG.get(c, r)
            if i is None or r < 64 or not is_hull(c, r):
                row.append(None if i is None else 0)
                continue
            smashed = d != i and (d is None or (d >> 4 == 0 and (d & 15) <= 2) or d >> 4 == 7)
            row.append(1 if smashed else 0)
        g.append(row)
    return w.sampler(g, ORIGIN, value=lambda val: float(val), blur=2, keep=lambda val: val is not None)


def wreckage(field, f, p):
    """Debris over the smashed plating: bent plates and chunks resting in the craters."""
    rnd = random.Random(7)
    pts = []
    tries = 0
    while len(pts) < 34 and tries < 4000:
        tries += 1
        x, y = rnd.uniform(-57, 57), rnd.uniform(-68, -2)
        c, r = int(math.floor(x + ORIGIN[0])), int(math.floor(ORIGIN[1] - y))
        if BOSS.get(c, r) is None or not is_hull(c, r) or field(x, y) < 0.55:
            continue
        if any(math.hypot(x - a, y - b) < 3.2 for a, b, _ in pts):
            continue
        pts.append((x, y, hull_z(x, y) - 3.6 * field(x, y) * 0.8 + 0.4))
    parts = kit.debris("debris", pts, p(0x08), size=(1.4, 3.0), seed=11)
    for obj in parts:
        kit.paint_faces(obj, lambda c, nrm: p(0x09) if nrm.z > 0.6 else p(0x05) if nrm.z > -0.3 else p(0x02))
    return parts


# --- The whole boss ----------------------------------------------------------------------------------------------------

def boss():
    p = painter("boss")
    f = paint_frame()
    hull(f, p)
    tanks(f, p)
    machinery(f, p)
    hoods(f, p)
    lamps(f, p)
    turret(f, p)
    masts(f, p)
    for obj in kit.meshes():
        k.smooth(obj, 40)


def boss_damaged():
    p = painter("boss")
    f = damaged_frame()
    field = damage_field()
    hull(f, p, damage=field)
    tanks(f, p)
    machinery(f, p)
    hoods(f, p, broken=True)
    lamps(f, p)
    turret(f, p)
    masts(f, p, broken_right=True)
    wreckage(field, f, p)
    for obj in kit.meshes():
        k.smooth(obj, 40)


# The pieces: sprite -> its top left pixel in the whole; each intact sprite's damaged look (dgr).
CELLS = {2: (12, 0), 4: (36, 0), 6: (60, 0), 8: (84, 0),
         39: (0, 28), 41: (24, 28), 43: (48, 28), 45: (72, 28), 47: (96, 28),
         77: (0, 56), 79: (24, 56), 81: (48, 56), 83: (72, 56), 85: (96, 56),
         115: (0, 84), 117: (24, 84), 119: (48, 84), 121: (72, 84), 123: (96, 84),
         154: (12, 112), 156: (36, 112), 158: (60, 112), 160: (84, 112)}
DAMAGED = {2: 12, 4: 14, 6: 16, 8: 18, 39: 49, 41: 51, 43: 53, 45: 55, 47: 208,
           77: 87, 79: 89, 81: 91, 83: 93, 85: 246, 115: 125, 117: 127, 119: 129, 121: 131, 123: 284,
           154: 164, 156: 166, 158: 168, 160: 170}

kit.PROTECT += ["hull", "hood", "mast", "chin", "block", "tank_plate", "tank_ribs", "port", "lamp"]
kit.pieced("camanis_boss", boss, (120, 140),
           [kit.piece(f"camanis_boss_{s}", BOSS, c0, r0, 24, 28) for s, (c0, r0) in CELLS.items()])
kit.pieced("camanis_boss_damaged", boss_damaged, (120, 140),
           [kit.piece(f"camanis_boss_{DAMAGED[s]}", DMG, c0, r0, 24, 28) for s, (c0, r0) in CELLS.items()])


if __name__ == "__main__":
    kit.run()
