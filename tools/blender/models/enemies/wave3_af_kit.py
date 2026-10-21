"""Helpers for the batch AF models of wave 3 (sheet R: IXMUCANE, SAWBLADES and ASSASSIN; wave3_af.py, the small
flying stones; wave3_af_heap.py, IXMUCANE's boss: a
machine in a rock heap and the heap that covers it): the sprites' pixels (wave3_af_art.py), the pixel frames,
painting and budget of batch V (wave3_v_kit), the parts of batches J and AA (wave3_j_kit, wave3_aa_kit: convex
rocks, faceted painting) and the build loop of batch N (wave3_n_kit: stand-alone models and whole objects cut
into their sprites' pieces, silhouettes checked against pixel masks). (The glass domes, which had their open glass
shells and cities of towers here, are polish_glass_city.py and polish_purple_dome.py.)

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_aa_kit as aa  # noqa: E402,F401
import wave3_af_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box,  # noqa: E402,F401
                         block, meshes, bake, sampler, lumpy)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, outlines_of, lift, slab,  # noqa: E402,F401
                         smoothstep)
from wave3_aa_kit import convex_rock, paint_facets, subdivide_faces  # noqa: E402,F401

model = n.model
pieced = n.pieced
PROTECT = v.PROTECT


def frame(name, width, origin):
    """A Frame of one of wave3_af_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def piece(name, f, c0, r0, mask_fn=None, width=24, height=28):
    """A width x height piece of a whole object at pixel (c0, r0) of frame f: (piece name, its box in the
    whole's coordinates, its sprite's centre there, its mask for --check: mask_fn(box) or the frame's pixels)."""
    x0, y1 = c0 - f.ox, f.oy - r0
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    box = (c0, c0 + width, r0, r0 + height)
    return (name, (x0 + e, x0 + width - e, y1 - height + e, y1 - e), (x0 + width / 2, y1 - height / 2),
            (lambda: mask_fn(box)) if mask_fn else (lambda: f.mask(box)))


def grid_pieces(names, f, columns, rows, mask_fn=None, c0=0, r0=0):
    """The pieces of a whole object laid out as columns x rows 2x2 sprites from pixel (c0, r0): names row by
    row."""
    return [piece(names[j * columns + i], f, c0 + 24 * i, r0 + 28 * j, mask_fn) for j in range(rows)
            for i in range(columns)]


run = v.run
