"""Enemies of wave 3, batch N (sheet 3): CORE's fire, built whole and cut into its sprites' pieces
(models.cfg: origin; authored as the sprites look, yaw=0).

- core_fire_<sprite> (3 22, 23, 39, 44, 60, 61, 77, 82, 96, 98, 99, 101, 117, 118): the great fire that
  rises at the end of CORE (one event puts the fourteen 2x2 sprites together, overlapping, into a
  mass of fire 84 x 98 pixels: three columns of sprites in the middle, two at the sides). Modelled as
  a molten mass whose tongues of flame reach up the screen, rising towards their tips, its surface
  glowing in the sprites' shades of fire (the brighter, the hotter and the higher). The overlapping
  sprites share their pixels: each piece keeps a part (the overlaps are split in the middle).

usage: Blender -b --factory-startup -P wave3_n_fire.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_n_kit as n  # noqa: E402
from wave3_n_kit import art, k, sh, w, pal  # noqa: E402

FIRE_ORIGIN = (42, 49)  # the middle of the 84 x 98 pixels
BASE = -5.0


def fire_grid():
    return w.grid(art.FIRE, 84)


def fire_whole():
    """The molten mass: inflated from the sprites' pixels (the holes of the loops at its feet stay
    open), higher where the fire is brighter, the tongues rising towards their northern tips; painted
    in bands of the fire's shades, each glowing the more the hotter it is."""
    g = fire_grid()
    ox, oy = FIRE_ORIGIN
    fire = lambda v: v is not None  # noqa: E731
    fine = w.sampler(g, FIRE_ORIGIN, value=lambda v: v & 15, blur=1, keep=fire)
    coarse = w.sampler(g, FIRE_ORIGIN, value=lambda v: v & 15, blur=4, keep=fire)
    # The fire's north edge above each column (where its tongues end).
    tops = []
    for c in range(84):
        rows = [r for r in range(len(g)) if g[r][c] is not None]
        tops.append(min(rows) if rows else len(g))

    def z_fn(x, y, z):
        s1, s4 = fine(x, y), coarse(x, y)
        c = min(83, max(0, int(math.floor(x + ox))))
        tip = oy - tops[c]  # y of the tongue's tip above this column
        rise = max(0.0, 1.0 - (tip - y) / 30.0)  # the last 30 pixels below the tip rise
        lift = z - BASE - 0.3
        return BASE + 0.3 + lift * (0.55 + 0.045 * s4) + 0.35 * (s1 - s4) + 3.0 * rise * min(1.0, lift / 3.0)

    def profile(d, wd):
        import numpy as np
        h = np.minimum(0.9 * wd, 12.0)
        t = np.clip(d / np.maximum(np.minimum(wd, 5.0), 0.3), 0.0, 1.0)
        return h * np.sqrt(np.maximum(0.0, 1.0 - (1.0 - t) ** 2))

    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", FIRE_ORIGIN, smooth=2, epsilon=0.35, min_area=1.5)
    mass = sh.inflate("fire", polys, pal("fire_mid", 0x76, metallic=0.0, roughness=0.4, glow=0.8), profile,
                      bottom=0.0, base=BASE, rim=0.3, spacing=0.6, z_fn=z_fn, sigma=1.3)
    w.simplify_bottom(mass)
    bands = []
    for s in range(1, 16):
        glow = 0.25 + 0.14 * s if s < 12 else 2.2
        bands.append((s - 0.5 if s > 1 else 0, pal(f"fire_{s:x}", 0x70 + s, metallic=0.0, roughness=0.45, glow=glow)))
    n.paint_shades(mass, lambda x, y: fine(x, y), bands, wall_drop=2.0)
    k.smooth(mass, 45)


# The sprites (sprite, column, row of its top left pixel in the whole) and the part each keeps.
FIRE_PIECES = [(39, 0, 14, (0, 24, 14, 42)), (77, 0, 42, (0, 24, 42, 63)), (96, 0, 56, (0, 24, 63, 84)),
               (22, 24, 0, (24, 42, 0, 28)), (23, 36, 0, (42, 60, 0, 28)),
               (60, 24, 28, (24, 42, 28, 56)), (61, 36, 28, (42, 60, 28, 56)),
               (98, 24, 56, (24, 42, 56, 77)), (99, 36, 56, (42, 60, 56, 77)),
               (117, 24, 70, (24, 42, 77, 98)), (118, 36, 70, (42, 60, 77, 98)),
               (44, 60, 14, (60, 84, 14, 42)), (82, 60, 42, (60, 84, 42, 63)), (101, 60, 56, (60, 84, 63, 84))]


def fire_piece(sprite, col, row, keep):
    ox, oy = FIRE_ORIGIN
    c0, c1, r0, r1 = keep
    box = (c0 - ox, c1 - ox, oy - r1, oy - r0)
    centre = (col + 12 - ox, oy - row - 14)

    def mask():
        g = fire_grid()
        return [[c0 <= c < c1 and r0 <= r < r1 and g[r][c] is not None for c in range(col, col + 24)]
                for r in range(row, row + 28)]
    return (f"core_fire_{sprite}", box, centre, mask)


n.pieced("core_fire", fire_whole, (84, 98), [fire_piece(*p) for p in FIRE_PIECES])


n.run()
