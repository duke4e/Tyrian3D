"""Enemies of wave 3, batch N (sheet 3, SURFACE and DESERTRUN): the rock arch, built
whole and cut into its sprites' pieces (models.cfg: origin; authored as the sprites look,
yaw=0). The machines and ships are in wave3_n.py.

- rock_arch_<sprite> (3 198, 162, 200, 164, 202, 166, 204, 168, 206, 170, 208, 241, 262, 279, 281, 282):
  the tan rock arch of SURFACE and DESERTRUN. The levels put it together from 2x2 sprites (events 6,
  7, 10): its left leg and the start of its span (198, 162/200, 164/202), optionally three more
  columns of span (166/204, 168/206, 170/208), and its right leg (241, 262, 279, 281, 282), which
  joins whichever column comes last. Built whole (the long version, 204 x 56 pixels) as a sinewy
  ridge of tan rock, its shades the sprites', its cross-section where the right leg may join (after
  164/202 and after 170/208) the same, so either version meets. The right leg's sprites overlap; each
  piece keeps a part of it (262 the top, 281 the left, 282 the right of the bottom row). The 1x1 nub
  in the notch of the left leg (3 180) is desert_rock_tip (wave2_h.py).

usage: Blender -b --factory-startup -P wave3_n_rocks.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_n_kit as n  # noqa: E402
from wave3_n_kit import art, k, sh, w, pal  # noqa: E402


# --- The rock arch -------------------------------------------------------------------------------

ARCH_ORIGIN = (0, 28)  # the whole's x runs along the columns, y = 0 between the two rows of sprites
JOINTS = (72.0, 144.0)  # where the right leg may join (the right ends of 164/202 and of 170/208)
BASE = -5.0  # the underside: the arch hangs a little below its layer


def arch_grid():
    return n.joined((w.grid(art.ROCK_A, 144), 144), (w.grid(art.ROCK_B, 60), 60))


def arch_whole():
    """A ridge of tan rock through the arch's pixels: a rounded cross-section higher where the
    sprites are lighter (the top of the ridge, along the north side of the span), the sprites' light
    lobes standing out a little and their dark creases sunk in; painted in the sprites' shades. Near
    the joints its cross-section is a fixed one, so that the right leg meets either version."""
    g = arch_grid()
    ox, oy = ARCH_ORIGIN
    tan = lambda v: v is not None and v >> 4 == 1  # noqa: E731
    sharp = w.sampler(g, ARCH_ORIGIN, value=lambda v: v & 15, blur=0, keep=tan)
    fine = w.sampler(g, ARCH_ORIGIN, value=lambda v: v & 15, blur=1, keep=tan)
    coarse = w.sampler(g, ARCH_ORIGIN, value=lambda v: v & 15, blur=4, keep=tan)
    # The joints' cross-section: the mean of the sprites' columns there (they are nearly the same).
    joint_cols = [71, 72, 143, 144]

    def joint_shade(y, column):
        r = int(math.floor(oy - y))
        vals = []
        for c in joint_cols:
            for rr in (r - 1, r, r + 1):
                if 0 <= rr < len(g) and g[rr][c] is not None and tan(g[rr][c]):
                    vals.append(g[rr][c] & 15)
        return sum(vals) / len(vals) if vals else 4.0

    top_row, bottom_row = 2.0, 41.0  # the joints' edges (rows)

    def lift(d, wd):
        """The rounded cross-section: up to 11 pixels over the underside, edges rounded over 6."""
        h = min(0.7 * wd, 13.5)
        t = min(1.0, max(0.0, d / min(max(wd, 0.5), 6.0)))
        return h * math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))

    def shaped(base_lift, s1, s4):
        detail = s1 - s4  # light lobes stand out, dark creases (s1 the unblurred shade there) sink in
        return BASE + 0.4 + base_lift * (0.48 + 0.05 * s4) + (0.3 * detail if detail > 0 else 0.45 * detail)

    def z_fn(x, y, z):
        s0, s4 = sharp(x, y), coarse(x, y)
        s1 = fine(x, y)
        s1 = s0 if s0 < s1 - 1.0 else s1
        z_nat = shaped(z - BASE - 0.4, s1, s4)
        for xj in JOINTS:
            wj = n.smoothstep(9.0, 2.0, abs(x - xj))
            if wj > 0:
                row = oy - y
                d = max(0.0, min(row - top_row, bottom_row - row))
                sj = joint_shade(y, xj)
                z_nat = z_nat * (1 - wj) + shaped(lift(d, (bottom_row - top_row) / 2), sj, sj) * wj
        return z_nat

    def profile(d, wd):
        import numpy as np
        return np.array([lift(a, b) for a, b in zip(d, wd)])

    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", ARCH_ORIGIN, smooth=2, epsilon=0.35, min_area=2.0)
    stone = pal("arch_tan6", 0x16, metallic=0.0, roughness=0.8)
    rock = sh.inflate("arch", polys, stone, profile, bottom=0.0, base=BASE, rim=0.4, spacing=0.6, z_fn=z_fn,
                      sigma=1.5)
    w.simplify_bottom(rock)
    bands = [(s - 0.5 if s > 1 else 0, pal(f"arch_tan{s:x}", 0x10 + s, metallic=0.0, roughness=0.8)) for s in range(1, 14)]

    def paint(x, y):
        s0, s1 = sharp(x, y), fine(x, y)
        return 0.5 * (s0 + s1) if s0 < s1 - 1.6 else s1
    n.paint_shades(rock, paint, bands, wall_drop=2.5)
    k.smooth(rock, 38)


def arch_piece(sprite, col, row, keep=None):
    """A piece of the arch: the sprite whose top left pixel is at (col, row) of the whole; keep (c0,
    c1, r0, r1) narrows the part it keeps (overlapping sprites)."""
    ox, oy = ARCH_ORIGIN
    c0, c1, r0, r1 = keep or (col, col + 24, row, row + 28)
    box = (c0 - ox, c1 - ox, oy - r1, oy - r0)
    centre = (col + 12 - ox, oy - row - 14)

    def mask():
        g = arch_grid()
        part = [[g[r][c] is not None and c0 <= c < c1 and r0 <= r < r1 if 0 <= c < len(g[0]) else False
                 for c in range(col, col + 24)] for r in range(row, row + 28)]
        return part
    return (f"rock_arch_{sprite}", box, centre, mask)


n.pieced("arch", arch_whole, (204, 56), [
    arch_piece(198, 0, 28),
    arch_piece(162, 24, 0), arch_piece(200, 24, 28),
    arch_piece(164, 48, 0), arch_piece(202, 48, 28),
    arch_piece(166, 72, 0), arch_piece(204, 72, 28),
    arch_piece(168, 96, 0), arch_piece(206, 96, 28),
    arch_piece(170, 120, 0), arch_piece(208, 120, 28),
    arch_piece(241, 144, 0), arch_piece(279, 144, 28),
    arch_piece(262, 168, 14, keep=(168, 192, 14, 28)),
    arch_piece(281, 168, 28, keep=(168, 180, 28, 56)),
    arch_piece(282, 180, 28, keep=(180, 204, 28, 56)),
])


n.run()
