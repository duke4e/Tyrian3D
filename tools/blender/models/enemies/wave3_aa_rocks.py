"""Enemies of wave 3, batch AA (sheet E), continued (wave3_aa.py has the round ones, wave3_aa_grub.py the
lava grubs): the grey boulders in a pit in the dirt of TYRIAN, HOLES and TYRIAN X, modelled as the sprites
look (models.cfg: yaw=0).

- holes_rocks_tl, holes_rocks_tm, holes_rocks_tr, holes_rocks_bl, holes_rocks_bm, holes_rocks_br (E 1, 3, 5
  above 39, 41, 43; events 516-521 and 522-527 at (x, y), (x + 24, y), (x + 48, y), (x, y + 28), (x + 24,
  y + 28), (x + 48, y + 28), all on one layer per event group): a heap of angular grey boulders sunk in a
  dark pit in the brown dirt, a big block with a broad lit top behind smaller ones. The boulders are convex
  hulls with flat facets painted with the sprite's greys; the dirt round the pit is laid as brown cobbles
  where the sprites draw it (wave3_p_kit.brown_dirt, as batch P laid the dirt of TYRIAN and HOLES), the pit
  as a dark floor. Built whole and cut into its six sprites (origin).

usage: Blender -b --factory-startup -P wave3_aa_rocks.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aa_kit as kit  # noqa: E402
from wave3_aa_kit import art, w, p, pal, Frame  # noqa: E402

ROCKS = Frame(art.ROCKS, 72, (36, 28))

# The boulders: (name, their foot round the outline at z = 0, the points of their top (column, row, z)), in
# the art's pixels (columns 0-71, rows 0-55).
BOULDERS = [
    # The big block: a broad top tilted towards the viewer, its front corner (44, 15.5) where the top, the
    # dark left face and the right face meet.
    ("big", [(27.5, 5), (30, 3.4), (35, 2.2), (40, 1.2), (44, 0.4), (48, 1.2), (53, 2.8), (58, 4.4), (62, 6),
             (65.6, 8), (66.6, 12), (66.6, 17), (65, 21), (62.5, 25), (58, 28), (52, 30), (45, 31), (38, 31.5),
             (31, 31), (27.6, 28), (26.6, 22), (26.6, 13)],
     [(29.5, 5.6, 9.0), (35, 3.0, 11.5), (44, 1.4, 12.0), (53, 3.8, 12.5), (61.6, 6.8, 11.5), (65, 9.6, 9.0),
      (44, 15.5, 14.0), (38, 8.0, 13.5), (50, 7.5, 14.0), (57, 10.5, 12.8), (45, 25, 7.0), (59, 19, 8.0),
      (31, 19, 6.0), (36.5, 23, 7.5), (53, 22, 8.5)]),
    # Below its left face, in its shadow.
    ("low", [(28, 30), (33, 28), (40, 28.5), (45, 30), (46.2, 35), (44, 40), (40, 42.6), (36, 43), (32, 41),
             (29, 37)],
     [(35, 31, 6.0), (40, 32, 6.2), (38, 37, 5.0), (33, 35, 4.5)]),
    # The two on the left: a ridged one in the middle, a lower one at the edge.
    ("mid", [(14, 13), (18, 11.4), (23, 12), (27, 14), (28.6, 20), (28, 27), (25, 31), (19, 32), (15, 30),
             (13, 24), (12.4, 18)],
     [(17, 14.5, 6.5), (22, 15, 8.0), (25, 20, 9.0), (21, 25, 8.5), (17, 22, 7.5)]),
    ("left", [(1, 19), (4, 17), (9, 16), (13, 17), (15, 22), (14.6, 28), (11, 32), (6, 33), (2, 31), (0.6, 25)],
     [(3, 21, 5.0), (8, 19.5, 6.5), (12, 22, 6.0), (9, 27, 6.0), (4, 27, 4.5)]),
    # A small one in the right corner of the pit.
    ("right", [(47, 29), (52, 27.5), (57, 28), (59.6, 31), (58, 36), (52, 38), (47, 36), (46, 32)],
     [(51, 30.5, 4.5), (55, 31, 4.5), (53, 34, 4.0)]),
]
# Small stones in the pit (column, row, radius).
PEBBLES = [(22.5, 42.5, 1.6), (25.5, 44.0, 1.2), (46.5, 43.0, 1.7), (48.5, 45.0, 1.2), (57.0, 21.5, 1.1),
           (8.0, 35.5, 1.2), (12.5, 36.5, 1.0)]


def rocks_whole():
    f = ROCKS
    g = f.g
    greys = {s: pal(f"hrocks_grey{s:x}", s, metallic=0.08, roughness=0.75) for s in (2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb)}
    shade = f.shade(0, blur=1)

    def grey(s):
        return greys[min(greys, key=lambda v: abs(v - s))]

    # The boulders: convex hulls, their facets split a little and painted with the sprite's greys there (the
    # steep sides a shade darker, what faces down darker still).
    for name, foot, top in BOULDERS:
        pts = [(f.X(c - 0.5), f.Y(r - 0.5), 0.0) for c, r in foot] + [(f.X(c - 0.5), f.Y(r - 0.5), z) for c, r, z in top]
        # The foot a little below the floor, so that the boulders sit in it.
        pts += [(x, y, -0.6) for x, y, _ in pts[:len(foot)]]
        rock = kit.convex_rock("rock_" + name, pts, grey(5))
        kit.paint_facets(rock, lambda x, y: shade(x, y) + 1.4, grey, wall_drop=1.4, under=grey(2))
    rnd = random.Random(7)
    for i, (c, r, rad) in enumerate(PEBBLES):
        w.lumpy(f"pebble{i}", (f.X(c), f.Y(r), 0.2), (rad, rad * rnd.uniform(0.8, 1.1), rad * 0.7), grey(2 + i % 2),
                seed=20 + i, amount=0.2, segments=12, rings=6)

    # The dirt round the pit: brown cobbles over the sprite's dirt.
    def is_dirt(v, c, r):
        return v is not None and v >> 4 == 1
    p.brown_dirt("dirt", g, is_dirt, prefix="hrocks", origin=(f.ox, f.oy))

    # The pit: a dark floor over everything else.
    h, wd = len(g), f.width
    keep = np.array([[g[r][c] is not None and g[r][c] >> 4 != 1 for c in range(wd)] for r in range(h)])
    heights = np.full((h, wd), 0.25)
    index = np.array([[0 if (g[r][c] is None or g[r][c] >> 4 == 2 or (g[r][c] & 15) < 3) else 1 for c in range(wd)]
                      for r in range(h)])
    p.bed("pit", heights, index, [pal("hrocks_pit", 0x20, metallic=0.0, roughness=0.95),
                                  pal("hrocks_pit_grey", 0x03, metallic=0.0, roughness=0.9)],
          (f.ox, f.oy), z0=0.0, keep=keep)


kit.pieced("holes_rocks", rocks_whole, (72, 56),
           kit.grid_pieces("holes_rocks_", ROCKS, ["tl", "tm", "tr", "bl", "bm", "br"], 3, 2))


if __name__ == "__main__":
    kit.run()
