"""Batch AF of wave 3 (sheet R): the glass domes over their cities in IXMUCANE and SAWBLADES, modelled as their
sprites look (models.cfg: yaw=0). The kit is wave3_af_kit.py, the pixels wave3_af_art.py.

The sprites draw each dome on a square of dark brown dirt: the levels' own ground there (IXMUCANE's and
SAWBLADES' first background is that dirt), which the 3D ground shows already, so the models leave the drawn
dirt out (and the dome's drawn shadow: the game casts its own); their silhouettes are checked against the
domes' own pixels.

- glass_city_tl, _tr, _bl, _br (R 1, 3 above 39, 41; events 291, 292, 289, 290 at (x, y - 28), (x + 24, y - 28),
  (x, y), (x + 24, y)): the small dome, 36 pixels across: a dark steel collar round a dark floor, a city of
  blue-grey tower blocks on it (their roofs in the sprite's shades, a few lit windows), and over them a clear
  dome of dark glass, about 15 pixels high, its rim dark, a bright glint up and to the left and a pale
  reflection along its lower right edge, as the sprite draws them.
- purple_dome_tl, _tc, _tr, _ml, _mc, _mr, _bl, _bc, _br (R 5, 7, 9 above 43, 45, 47 above 81, 83, 85; events
  299-301, 296-298, 293-295, 24 pixels apart): the big dome, an egg of purple glass 60 x 66 pixels and 30 high
  over a city of taller towers that rises towards the back, its highest spire under the dome's crown; the
  glass is purple where the sprite draws glass, clear where it shows the city through it, with a big glint up
  and to the left.

Both are built whole and cut into their sprites' pieces (origin); the glass is an open shell, cut without
caps so that no wall shows through it where the pieces meet.

usage: Blender -b --factory-startup -P wave3_af_domes.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>] [--stats 1]
"""
import math
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_af_kit as a  # noqa: E402
from wave3_af_kit import k, sh, pal, sphere, smoothstep  # noqa: E402


def is_dirt(v):
    """The dirt the sprites draw round the domes: the browns (ramps 1 and 10)."""
    return v is not None and v >> 4 in (1, 10)


def city(prefix, f, keep, glass_z, height_of, roof_of, rect, seed, min_size=2.6, max_size=5.6, street=0.55,
         z0=0.4, gap=1.8, fill=0.5, lights=None, min_depth=None, max_depth=None):
    """Tower blocks over the ground rect (x0, y0, x1, y1) split at random into blocks; a block becomes a tower
    when keep(x, y) covers `fill` of it: height_of(x, y, rng) high, kept `gap` under glass_z(x, y); roof_of(r)
    -> (roof, wall) materials (r: the block's rect). Tall towers step back near their top. lights: (material, chance) of a lit window
    on a roof. Returns the towers' (rect, height)."""
    rng = random.Random(seed)
    out = []
    for i, (x0, y0, x1, y1) in enumerate(a.blocks(rect, rng, min_size, max_size, min_depth, max_depth)):
        r = (x0 + street / 2, y0 + street / 2, x1 - street / 2, y1 - street / 2)
        if a.coverage(r, keep) < fill:
            continue
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        cap = min(glass_z(x, y) for x in (r[0], r[2], cx) for y in (r[1], r[3], cy)) - gap
        h = min(height_of(cx, cy, rng), cap)
        if h < z0 + 1.0:
            continue
        roof, wall = roof_of(r)
        tall = h > 7.0 and min(r[2] - r[0], r[3] - r[1]) > 3.2
        if tall and rng.random() < 0.6:
            # A setback: the tower's top storeys narrower.
            low = z0 + (h - z0) * rng.uniform(0.6, 0.75)
            a.tower(f"{prefix}{i}", r, z0, low, roof, wall)
            inset = rng.uniform(0.6, 0.9)
            r2 = (r[0] + inset, r[1] + inset, r[2] - inset, r[3] - inset)
            a.tower(f"{prefix}{i}_top", r2, low - 0.2, h, roof, wall)
        else:
            a.tower(f"{prefix}{i}", r, z0, h, roof, wall)
        if lights and rng.random() < lights[1]:
            lx = rng.uniform(r[0] + 0.8, r[2] - 0.8)
            ly = rng.uniform(r[1] + 0.8, r[3] - 0.8)
            k.box(f"{prefix}{i}_light", (lx, ly, h + 0.1), (0.55, 0.55, 0.25), lights[0])
        out.append((r, h))
    return out


# --- R 1 3 / 39 41: the small dome -----------------------------------------------------------------

SMALL = a.frame("SMALL_DOME", 48, (24, 28))
S_CENTRE = (0.6, 0.4)     # the dome's centre: the sprite's pixel (24.6, 27.6)
S_RADIUS = 17.9
S_HEIGHT = 14.0
S_Z0 = 1.0               # the glass stands on the collar


def small_mask(box):
    """The dome's own pixels (its drawn dirt and shadow left out)."""
    c0, c1, r0, r1 = box
    cx, cy = S_CENTRE
    return [[math.hypot(SMALL.X(c) - cx, SMALL.Y(r) - cy) < S_RADIUS + 0.3 for c in range(c0, c1)]
            for r in range(r0, r1)]


def roof_picker(f, roofs, blues, shift=1.0):
    """roof_of for city(): a block's roof and walls in the mean shade of the city pixels under it (ramp 6, the
    blue-greys, lifted `shift`), in the blues (ramp 3) where those make most of it."""
    def pick(rect):
        x0, y0, x1, y1 = rect
        grey, blue = [], []
        for i in range(4):
            for j in range(4):
                v = f.at(x0 + (i + 0.5) * (x1 - x0) / 4, y0 + (j + 0.5) * (y1 - y0) / 4)
                if v is None:
                    continue
                if v >> 4 == 6:
                    grey.append(v & 15)
                elif v >> 4 in (3, 8):
                    blue.append(v & 15)
        if len(blue) > len(grey):
            s_ = sum(blue) / len(blue) + shift
            return blues[min(blues, key=lambda q: abs(q - s_))]
        s_ = (sum(grey) / len(grey) if grey else 4.0) + shift
        return roofs[min(roofs, key=lambda q: abs(q - s_))]
    return pick


def small_dome():
    cx, cy = S_CENTRE
    R = S_RADIUS
    steel = pal("sd_steel", 0x02, metallic=0.6, roughness=0.35)
    steel_light = pal("sd_steel_light", 0x04, metallic=0.6, roughness=0.3)
    floor = pal("sd_floor", 0x60, metallic=0.2, roughness=0.6)
    street = pal("sd_street", 0x01, metallic=0.1, roughness=0.8)
    window = pal("sd_window", 0x89, metallic=0.0, roughness=0.3, glow=1.4)
    red = pal("sd_red", 0x76, metallic=0.0, roughness=0.3, glow=2.5)
    roofs = {s_: (pal(f"sd_roof{s_}", 0x60 + s_, metallic=0.45, roughness=0.35),
                  pal(f"sd_wall{s_}", 0x60 + max(1, s_ - 3), metallic=0.45, roughness=0.4)) for s_ in (4, 5, 6, 7, 8, 9, 10)}
    blues = {s_: (pal(f"sd_blue{s_}", 0x30 + s_, metallic=0.45, roughness=0.35),
                  pal(f"sd_bluewall{s_}", 0x30 + max(1, s_ - 3), metallic=0.45, roughness=0.4)) for s_ in (4, 6, 8, 10)}

    # The collar: a low ring of dark steel round the dome's foot, its top lit.
    collar = a.hoop("collar", (cx, cy, 0.0), [(R - 0.6, 0.0), (R + 1.0, 0.0), (R + 1.0, 0.8), (R + 0.6, 1.4),
                                               (R - 0.6, 1.4)], steel, segments=96)
    a.paint_faces(collar, lambda c, nrm: steel_light if nrm.z > 0.7 else None)
    # The floor inside it.
    k.smooth(sh.inflate("floor", [sh.ellipse(cx, cy, R - 0.4, R - 0.4, count=64)], floor,
                        lambda d, wd: 0.0 * d, bottom=0.0, base=0.0, rim=0.45, spacing=1.2), 30)

    glass_z = a.shell_height(S_CENTRE, lambda ang: R, S_HEIGHT, z0=S_Z0)

    def is_city(x, y):
        if math.hypot(x - cx, y - cy) > R - 2.6:
            return False
        v = SMALL.at(x, y)
        if v is None:
            return False
        ramp, shade_ = v >> 4, v & 15
        return ramp in (6, 3, 8) or (ramp == 0 and shade_ >= 3) or (ramp == 5 and shade_ <= 8)

    def height_of(x, y, rng):
        # Higher in the middle and towards the back (up the screen), as the sprite stacks its blocks.
        d = math.hypot(x - cx, y - cy) / R
        return 2.5 + 7.5 * (1.0 - d * d) + 2.0 * smoothstep(-10.0, 8.0, y - cy) + rng.uniform(-1.5, 2.0)
    towers = city("sd_tower", SMALL, is_city, glass_z, height_of, roof_picker(SMALL, roofs, blues),
                  (cx - R + 1.5, cy - R + 1.5, cx + R - 1.5, cy + R - 1.5), seed=7, min_size=2.4, max_size=5.2,
                  fill=0.42, lights=(window, 0.18))
    # Streets: the floor among the blocks is dark.
    a.paint_faces(bpy.data.objects["floor"], lambda c, nrm: street if is_city(c.x, c.y) else None)
    a.merge_flat(bpy.data.objects["floor"])
    # The red lamp the sprite draws in the middle of the city (its pixel (29, 27)).
    lx, ly = SMALL.X(29), SMALL.Y(27)
    top = max([h for (x0, y0, x1, y1), h in towers if x0 <= lx <= x1 and y0 <= ly <= y1] + [0.6])
    sphere("lamp", (lx, ly, top + 0.3), (0.6, 0.6, 0.5), red, 10, 5)

    # The glass: clear over the city, darkening towards its rim, which is nearly black; the pale reflection
    # along its lower right edge (the sprite's light blue-grey crescent) and a bright glint up and to the left.
    clear = a.glass("sd_glass_clear", 0x69, 0.12)
    dim = a.glass("sd_glass_dim", 0x63, 0.35)
    dark = a.glass("sd_glass_dark", 0x61, 0.6)
    rim = a.glass("sd_glass_rim", 0x60, 0.88)
    pale = a.glass("sd_glass_pale", 0x6a, 0.5, glow=0.3)
    paler = a.glass("sd_glass_paler", 0x6d, 0.68, glow=0.6)
    shell = a.dome_shell("glassshell", S_CENTRE, lambda ang: R, S_HEIGHT, clear, rings=30, segments=120, z0=S_Z0)

    def paint(c, nrm):
        d = math.hypot(c.x - cx, c.y - cy) / R
        ang = math.degrees(math.atan2(c.y - cy, c.x - cx))
        # The crescent along the lower right edge (the sprite's light blue-greys, about -75 to -15 degrees),
        # smooth so that it runs cleanly down the glass's steep foot.
        if 0.88 < d < 0.975 and -72.0 < ang < -16.0:
            return paler if -60.0 < ang < -30.0 and d > 0.91 else pale
        if d > 0.95:
            return rim
        if d > 0.86:
            return dark
        if d > 0.74:
            return dim
        return clear
    a.paint_faces(shell, paint)
    a.merge_flat(shell)
    # The glint: a white lens on the glass up and to the left (the sprite's pixels 17-19, rows 16-18).
    gx, gy = SMALL.X(18.0), SMALL.Y(17.0)
    gz = glass_z(gx, gy)
    nx, ny = (gx - cx) / R, (gy - cy) / R
    glint = a.glass("sd_glint", 0x5f, 0.9, glow=2.0)
    halo = a.glass("sd_glint_halo", 0x6d, 0.4, glow=0.8)
    aa_lens("glassshell_glint", (gx, gy, gz), (nx * 0.8, ny * 0.8, 1.0), (1.6, 1.6, 0.25), glint)
    aa_lens("glassshell_halo", (gx, gy, gz - 0.05), (nx * 0.8, ny * 0.8, 1.0), (2.5, 2.5, 0.2), halo)


def aa_lens(name, centre, normal, radii, mat):
    obj = a.aa.lens(name, centre, normal, radii, mat, sink=-0.05, segments=24)
    return obj


S_PIECES = a.grid_pieces(["glass_city_tl", "glass_city_tr", "glass_city_bl", "glass_city_br"], SMALL, 2, 2,
                         small_mask)
a.pieced("glass_city", small_dome, (48, 56), S_PIECES)


# --- R 5 7 9 / 43 45 47 / 81 83 85: the big dome -----------------------------------------------------

BIG = a.frame("BIG_DOME", 72, (36, 42))
B_HEIGHT = 28.0
B_Z0 = 1.6               # the glass stands on the collar


def big_outline():
    """The egg's outline: each row's leftmost and rightmost glass or city pixel (ramps 5 and 6), out by most of
    the black outline round them, closed by the top and bottom rows' outline pixels."""
    rows = []
    for r in range(BIG.height):
        cols = [c for c in range(BIG.width) if BIG.g[r][c] is not None and BIG.g[r][c] >> 4 in (5, 6)]
        if cols:
            rows.append((BIG.Y(r), min(cols) - 0.6 - BIG.ox, max(cols) + 1.6 - BIG.ox))
    # Smoothed over a few rows (the pixel steps left out).
    wts = (1, 2, 3, 2, 1)
    smooth = []
    for i, (yy, _, _) in enumerate(rows):
        near = [(rows[j], wts[j - i + 2]) for j in range(i - 2, i + 3) if 0 <= j < len(rows)]
        total = sum(wt for _, wt in near)
        smooth.append((yy, sum(r_[1] * wt for r_, wt in near) / total, sum(r_[2] * wt for r_, wt in near) / total))
    rows = smooth
    top = (sum(rows[0][1:]) / 2, rows[0][0] + 1.1)
    bottom = (sum(rows[-1][1:]) / 2, rows[-1][0] - 1.1)
    poly = [top] + [(xl, yy) for yy, xl, xr in rows] + [bottom] + [(xr, yy) for yy, xl, xr in reversed(rows)]
    return poly


B_POLY = big_outline()
B_CENTRE = (sum(p[0] for p in B_POLY) / len(B_POLY), BIG.Y(33.0))


def inside_egg(x, y):
    import numpy as np
    a_, b_ = sh._segments([B_POLY])
    return bool(sh._inside(np.array([(x, y)], dtype=float), a_, b_)[0])


def big_mask(box):
    """The dome's pixels: inside its egg (the drawn dirt left out)."""
    c0, c1, r0, r1 = box
    a_, b_ = sh._segments([B_POLY])
    import numpy as np
    pts = np.array([(BIG.X(c), BIG.Y(r)) for r in range(r0, r1) for c in range(c0, c1)], dtype=float)
    inside = sh._inside(pts, a_, b_)
    wd = c1 - c0
    return [[bool(inside[(r - r0) * wd + (c - c0)]) for c in range(c0, c1)] for r in range(r0, r1)]


def big_dome():
    cx, cy = B_CENTRE
    reach = a.polygon_reach(B_POLY, B_CENTRE)
    steel = pal("bd_collar", 0x53, metallic=0.55, roughness=0.35)
    steel_light = pal("bd_collar_light", 0x57, metallic=0.55, roughness=0.3)
    floor = pal("bd_floor", 0x52, metallic=0.2, roughness=0.6)
    street = pal("bd_street", 0x60, metallic=0.1, roughness=0.8)
    window = pal("bd_window", 0x89, metallic=0.0, roughness=0.3, glow=1.4)
    beacon = pal("bd_beacon", 0x5f, metallic=0.0, roughness=0.3, glow=3.0)
    roofs = {s_: (pal(f"bd_roof{s_}", 0x60 + s_, metallic=0.45, roughness=0.35),
                  pal(f"bd_wall{s_}", 0x60 + max(1, s_ - 3), metallic=0.45, roughness=0.4)) for s_ in (3, 4, 5, 6, 7, 8, 9, 10)}

    # The collar round the dome's foot and the floor inside it.
    ring = [(cx + reach(2 * math.pi * i / 128) * math.cos(2 * math.pi * i / 128),
             cy + reach(2 * math.pi * i / 128) * math.sin(2 * math.pi * i / 128)) for i in range(128)]
    outer = sh.inset(ring, -0.9)
    inner = sh.inset(ring, 0.8)
    collar = sh.inflate("collar", [outer, sh.inset(ring, 1.4)], steel, lambda d, wd: 0.0 * d, bottom=0.0, base=0.0,
                        rim=B_Z0, spacing=1.5)
    k.smooth(collar, 40)
    a.paint_faces(collar, lambda c, nrm: steel_light if nrm.z > 0.7 else None)
    k.smooth(sh.inflate("floor", [inner], floor, lambda d, wd: 0.0 * d, bottom=0.0, base=0.0, rim=B_Z0 + 0.3,
                        spacing=1.5), 30)

    glass_z = a.shell_height(B_CENTRE, reach, B_HEIGHT, z0=B_Z0)

    def is_city(x, y):
        v = BIG.at(x, y)
        if v is None or not inside_egg(x, y):
            return False
        if v >> 4 in (6, 3, 8):
            return True
        # Black outlines between towers count as city where city pixels lie on both sides.
        if v >> 4 == 0:
            left, right = BIG.at(x - 1.5, y), BIG.at(x + 1.5, y)
            up, down = BIG.at(x, y + 1.5), BIG.at(x, y - 1.5)
            return ((left is not None and left >> 4 == 6 and right is not None and right >> 4 == 6) or
                    (up is not None and up >> 4 == 6 and down is not None and down >> 4 == 6))
        return False

    blues = {s_: (pal(f"bd_blue{s_}", 0x30 + s_, metallic=0.45, roughness=0.35),
                  pal(f"bd_bluewall{s_}", 0x30 + max(1, s_ - 3), metallic=0.45, roughness=0.4)) for s_ in (4, 6, 8, 10)}
    roof_of = roof_picker(BIG, roofs, blues, shift=0.0)

    def height_of(x, y, rng):
        # The skyline rises towards the back (up the screen) and the middle, as the sprite's towers do.
        back = smoothstep(-26.0, 14.0, y)
        middle = math.exp(-((x - cx + 2.0) / 14.0) ** 2)
        return 4.0 + 13.0 * back + 7.0 * middle + rng.uniform(-3.0, 4.0)
    towers = city("bd_tower", BIG, is_city, glass_z, height_of, roof_of,
                  (cx - 30.0, cy - 36.0, cx + 30.0, cy + 34.0), seed=11, min_size=2.8, max_size=4.8, min_depth=4.0,
                  max_depth=9.0, street=0.8, z0=B_Z0 + 0.25, gap=2.2, fill=0.45, lights=(window, 0.08))
    # Streets: the floor among the towers.
    a.paint_faces(bpy.data.objects["floor"], lambda c, nrm: street if is_city(c.x, c.y) else None)
    a.merge_flat(bpy.data.objects["floor"])
    # The spire: the sprite's tallest tower (columns 31-34, its top at row 9) reaching up under the crown.
    sx, sy = BIG.X(32.5), BIG.Y(20.0)
    top = glass_z(sx, sy) - 1.5
    a.tower("bd_spire", (sx - 1.9, sy - 1.9, sx + 1.9, sy + 1.9), B_Z0 + 0.25, top - 3.0, roofs[8][0], roofs[8][1])
    a.tower("bd_spire_top", (sx - 1.1, sy - 1.1, sx + 1.1, sy + 1.1), top - 3.2, top, roofs[9][0], roofs[9][1])
    sphere("bd_beacon", (sx, sy, top + 0.35), (0.6, 0.6, 0.5), beacon, 10, 5)

    # The glass: purple where the sprite draws glass, clear over the city, its outline dark; a big glint.
    shades = (2, 4, 6, 8, 10)
    purple = {s_: a.glass(f"bd_glass{s_}", 0x50 + s_, 0.72) for s_ in shades}
    clear = a.glass("bd_glass_clear", 0x68, 0.07)
    glass_shade = BIG.shade((5,), blur=2)
    rim = a.glass("bd_glass_rim", 0x51, 0.85)
    pale = a.glass("bd_glass_pale", 0x5c, 0.8, glow=0.5)
    shell = a.dome_shell("glassshell", B_CENTRE, reach, B_HEIGHT, clear, rings=30, segments=128, z0=B_Z0)
    a.pixelate(shell, BIG)

    def paint(c, nrm):
        v = BIG.at(c.x, c.y)
        dx, dy = c.x - cx, c.y - cy
        t = math.hypot(dx, dy) / max(reach(math.atan2(dy, dx)), 1e-6)
        if nrm.z < 0.55:
            # The steep foot of the glass: smoothly purple (no pixel steps down its side), dark at the bottom.
            if c.z < B_Z0 + 1.2:
                return rim
            q = glass_shade(c.x, c.y)
            return purple[min(shades, key=lambda s_: abs(s_ - q))]
        if v is not None and v >> 4 == 5:
            if (v & 15) >= 12:
                return pale
            return purple[min(shades, key=lambda q: abs(q - (v & 15)))]
        if t > 0.95:
            return rim
        if v is not None and v >> 4 == 0 and not is_city(c.x, c.y):
            return purple[2]
        return clear
    a.paint_faces(shell, paint)
    a.merge_flat(shell)
    # The glint up and to the left (the sprite's white pixels, columns 14-24, rows 12-20).
    gx, gy = BIG.X(19.0), BIG.Y(16.0)
    gz = glass_z(gx, gy)
    dx, dy = gx - cx, gy - cy
    t = math.hypot(dx, dy) / reach(math.atan2(dy, dx))
    tilt = 0.9 * t
    nrm = (dx / math.hypot(dx, dy) * tilt, dy / math.hypot(dx, dy) * tilt, 1.0)
    glint = a.glass("bd_glint", 0x5f, 0.88, glow=2.0)
    halo = a.glass("bd_glint_halo", 0x5d, 0.45, glow=0.9)
    aa_lens("glassshell_glint", (gx, gy, gz), nrm, (2.4, 2.2, 0.3), glint)
    aa_lens("glassshell_halo", (gx, gy, gz - 0.05), nrm, (4.6, 4.2, 0.25), halo)


B_PIECES = a.grid_pieces(["purple_dome_tl", "purple_dome_tc", "purple_dome_tr", "purple_dome_ml", "purple_dome_mc",
                          "purple_dome_mr", "purple_dome_bl", "purple_dome_bc", "purple_dome_br"], BIG, 3, 3, big_mask)
a.pieced("purple_dome", big_dome, (72, 84), B_PIECES)


if __name__ == "__main__":
    a.PROTECT[:] = ["glassshell"]
    a.run()
