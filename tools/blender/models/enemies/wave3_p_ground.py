"""Wave 3, batch P of the enemy models, continued (the rods: polish_rod.py): sheet 2's ground sprites drawn
on rock and dirt, modelled as their sprites look (models.cfg: yaw=0), the rock and dirt as round boulders
and cobbles where the sprites draw them (wave3_p_kit.boulders). (TYRIAN's panel of purple pads: polish_purple_pads.py;
its golden machines, 2 77-121: polish_gold_machines.py.)

- red_works_tl, _tr, _bl, _br (2 15, 17 above 53, 55): TYRIAN's red works in the rocks: a steel deck
  crowded with red blocks and pipes, a column of two glowing yellow grilles, a tan box with a red
  button, a dark recess with a tan floor and tan rails. Built whole and cut (origin).

usage: Blender -b --factory-startup -P wave3_p_ground.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       [--whole red_works --preview <prefix>]
"""
import os
import sys

import numpy as np


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_p_kit as w  # noqa: E402
from wave3_p_kit import art, pal, model, whole, grid, ramp, shade  # noqa: E402


# --- Helpers for the pieces cut in four ------------

def inside_outline(outline, col, row):
    """Whether a pixel's centre lies inside an outline of pixel corners."""
    x, y, inside = col + 0.5, row + 0.5, False
    n = len(outline)
    for i in range(n):
        (x0, y0), (x1, y1) = outline[i], outline[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def quarters(name, sprites, builder):
    """Registers the four sprites of a 48 x 56 object built whole: top left, top right, bottom left,
    bottom right."""
    for (suffix, sprite), (x0, y0) in zip((("tl", sprites[0]), ("tr", sprites[1]), ("bl", sprites[2]),
                                           ("br", sprites[3])), ((-24, 0), (0, 0), (-24, -28), (0, -28))):
        def build(x0=x0, y0=y0):
            builder()
            w.bake()
            w.piece(w.meshes(), x0, x0 + 24, y0, y0 + 28)
        model(f"{name}_{suffix}", [sprite])(build)
    whole(name, (48, 56))(builder)


# --- TYRIAN's red works in the rocks (48 x 56, built whole and cut into four sprites) -----------------

WORKS_OUTLINE = [(2.5, 4), (36.5, 4), (36.5, 48.5), (6.5, 48.5), (6.5, 30), (0, 30), (0, 16), (2.5, 15.5)]


def works_whole():
    """A low steel deck in the rocks crowded with red machinery: red blocks at its top left and in the
    middle, a column of two glowing yellow grilles, red pipes along it and down its right side, a tan
    box with a red button at its left, a dark recess with a tan floor, a tan block at its lower left
    and tan rails."""
    g = grid(art.WORKS, 48)
    steel = pal("works_steel", 0x04, metallic=0.55, roughness=0.4)
    steel_light = pal("works_steel_light", 0x07, metallic=0.55, roughness=0.35)
    dark = pal("works_dark", 0x01, metallic=0.4, roughness=0.6)
    red = pal("works_red", 0x46, metallic=0.4, roughness=0.32)
    red_light = pal("works_red_light", 0x4a, metallic=0.4, roughness=0.28)
    tan = pal("works_tan", 0xa8, metallic=0.2, roughness=0.5)
    tan_light = pal("works_tan_light", 0xab, metallic=0.2, roughness=0.45)
    glow = pal("works_glow", 0x7b, metallic=0.0, roughness=0.2, glow=2.0)
    glow_hot = pal("works_glow_hot", 0x7d, metallic=0.0, roughness=0.15, glow=3.0)

    def XYc(c, r):
        return (c - 24.0, 28.0 - r)
    inside = [[inside_outline(WORKS_OUTLINE, c, r) for c in range(48)] for r in range(56)]
    w.grey_rocks("rocks", g, lambda v, c, r: v is not None and not inside[r][c] and ramp(v) in (0, 0xa), prefix="works",
                 origin=(24, 28), keep_base=lambda v, c, r: True)
    # The deck: a low steel slab over the machine, lighter where the sprite is light.
    h = np.zeros((56, 48))
    idx = np.zeros((56, 48), dtype=int)
    for r in range(56):
        for c in range(48):
            v = g[r][c]
            light = v is not None and ramp(v) == 0 and shade(v) >= 5
            h[r, c] = 2.2 + (0.4 if light else 0.0)
            idx[r, c] = 1 if light else 0
    w.bed("deck", h, idx, [steel, steel_light], (24, 28), keep=inside, dissolve=0.5)

    def box(name, c0, r0, c1, r1, z0, z1, mat, bevel=0.6, paint=None):
        (x0, y0), (x1, y1) = XYc(c0, r0), XYc(c1, r1)
        obj = w.rounded_box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y0 - y1, z1 - z0), mat,
                            bevel=bevel)
        if paint:
            w.paint_faces(obj, lambda cc, n: paint if n.z > 0.6 and n.x < 0.3 else None)
        return obj
    # Red blocks.
    box("red_tl", 3.5, 7, 16.8, 11, 1.5, 7.0, red, 0.9, red_light)
    box("red_tl_drop", 3.0, 10.5, 9.8, 15.5, 1.5, 6.2, red, 0.8, red_light)
    box("red_mid", 21.8, 7.8, 28.2, 15.4, 1.5, 6.6, red, 0.8, red_light)
    box("red_low", 12.6, 38.6, 18.6, 47.0, 1.5, 5.8, red, 0.8, red_light)
    box("red_right_low", 28.8, 32.8, 34.6, 47.6, 1.5, 4.8, red, 0.7, red_light)
    box("red_left_mid", 10.8, 21.6, 18.6, 29.4, 1.5, 5.0, red, 0.7, red_light)
    # The red pipes: along the middle, down the right side and across below the recess.
    zp = 4.6
    for name, pts in (("pipe_mid", [(11.0, 16.6), (24.0, 16.6), (34.5, 16.6)]),
                      ("pipe_right", [(34.5, 16.6), (34.5, 30.0), (34.5, 47.5)]),
                      ("pipe_low", [(21.0, 27.5), (28.0, 27.5), (34.5, 27.5)])):
        path = [(XYc(c, r)[0], XYc(c, r)[1], zp) for c, r in pts]
        pipe = w.tube(name, w.catmull(path, 1.0), 1.15, red, 10)
        w.paint_faces(pipe, lambda cc, n: red_light if n.z > 0.7 else None)
    for i, (c, r) in enumerate(((34.5, 16.6), (34.5, 27.5))):
        x, y = XYc(c, r)
        w.sphere(f"pipe_joint{i}", (x, y, zp), (1.7, 1.7, 1.6), red_light, 12, 6)
    # The column of glowing grilles.
    box("grille_column", 13.2, 10.6, 19.4, 21.6, 1.5, 7.4, dark, 0.6)
    for i, r0 in enumerate((11.6, 17.6)):
        box(f"grille{i}", 14.0, r0, 18.8, r0 + 3.4, 6.6, 7.9, glow, 0.4)
        for j in range(3):
            c = 14.8 + 1.6 * j
            box(f"grille_bar{i}{j}", c, r0 + 0.2, c + 0.5, r0 + 3.2, 7.4, 8.2, dark, 0.15)
        x, y = XYc(16.4, r0 + 1.7)
        w.sphere(f"grille_hot{i}", (x, y, 7.9), (1.4, 0.9, 0.35), glow_hot, 10, 5)
    # The tan box with its red button, the recess with its tan floor, the tan block and rails.
    box("tan_box", 0.2, 16.8, 10.0, 29.8, 1.5, 5.4, tan, 0.8, tan_light)
    x, y = XYc(5.0, 22.5)
    w.sphere("button_rim", (x, y, 5.2), (3.0, 2.6, 0.9), steel, 18, 8)
    w.sphere("button", (x, y, 5.5), (2.3, 2.0, 1.4), red, 18, 9)
    w.sphere("button_hi", (x - 0.7, y + 0.6, 6.6), (0.8, 0.6, 0.3), red_light, 8, 4)
    box("recess_frame", 21.0, 17.8, 31.0, 27.0, 1.5, 4.4, steel_light, 0.6)
    box("recess_floor", 22.6, 20.6, 29.8, 26.2, 1.5, 4.7, tan, 0.4)
    box("recess_shade", 22.6, 19.4, 29.8, 20.8, 1.5, 4.8, dark, 0.3)
    box("tan_block", 7.0, 33.0, 12.0, 47.8, 1.5, 6.0, tan, 0.8, tan_light)
    box("tan_rail", 15.0, 3.6, 28.0, 5.0, 1.5, 3.4, tan_light, 0.5)
    box("tan_rod", 31.0, 7.0, 33.0, 15.8, 1.5, 5.6, tan_light, 0.6)

quarters("red_works", (15, 17, 53, 55), works_whole)

w.run()
