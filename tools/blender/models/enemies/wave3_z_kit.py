"""Helpers for the batch Z models of wave 3 (sheet L: STATION and TIME WAR; wave3_z_station.py, the station of
STATION and TIME WAR and TIME WAR's grey capsule; MINERS's lander, tan creature and crawler train are now
polish_lander.py's, polish_tan_dome.py's and polish_crawler.py's). The sprites' pixels are in wave3_z_art.py; the
parts come from the earlier batches' kits
(wave3_s_kit: pixel frames, painting by the sprite, slabs and prisms; wave3_q_kit: heightfield parts, rings;
wave3_j_kit: palette materials, turned parts, tubes, spheres; wave3_n_kit: stand-alone models and whole objects
cut into their sprites' pieces, the silhouette check, the triangle budget, the build loop).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_z_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, lathe_axis, hoop, column, tube, catmull, sphere,  # noqa: E402,F401
                         rounded_box, block, lumpy, meshes, bake, triangles, decimate, sampler)
from wave3_s_kit import (Frame, Painter, paint_sprite, paint_pixels, pixelate, merge_flat, slab, prism_x,  # noqa: E402,F401
                         prism_y, lathe_y, lift, mirror_copies, smoothstep)

L = "enemy_L"
pieced = n.pieced
check_mask = n.check_mask
torus = q.torus
cone = q.cone
run = n.run


def frame(name, width, origin):
    """A Frame of one of wave3_z_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def polys_of(fr, keep, smooth=2, epsilon=0.4, min_area=0.5, grow=0.0):
    """The outlines of the frame's pixels keep(index, column, row) accepts (model coordinates)."""
    rows = regions(fr.g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    polys = sh.outlines(rows, "#", (fr.ox, fr.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)
    if grow:
        polys = [sh.inset(p, -grow) for p in polys]
    return polys


def heightfield(name, polys, z_of, mat=None, spacing=0.5, smooth_angle=50, edge=None):
    """A closed part over the polygons, its top at z_of(x, y) (with edge: z_of(x, y, e), e rising from 0 on
    the outline to 1 `edge` pixels inside), its bottom flat at z = 0 (wave3_q_kit.heightfield)."""
    return q.heightfield(name, polys, z_of, mat, spacing, smooth_angle, edge)


def quarter(name, f, c0, r0, width=24, height=28, check=True):
    """A piece of a whole object at pixel (c0, r0) of frame f, one sprite (24 x 28, or 12 x 14 for a small
    one): (piece name, its box in the whole's coordinates, its sprite's centre there, its mask for --check)."""
    x0, y1 = f.left(c0), f.top(r0)
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    return (name, (x0 + e, x0 + width - e, y1 - height + e, y1 - e), (x0 + width / 2, y1 - height / 2),
            (lambda: f.mask((c0, c0 + width, r0, r0 + height))) if check else None)


def mirror_y_copies(objects, axis_y=0.0, suffix="_y"):
    """Mirrored copies of objects across y = axis_y (the originals kept)."""
    out = []
    m = Matrix.Translation((0, axis_y, 0)) @ Matrix.Scale(-1, 4, (0, 1, 0)) @ Matrix.Translation((0, -axis_y, 0))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)
        c = obj.copy()
        c.data = obj.data.copy()
        c.name = obj.name + suffix
        bpy.context.scene.collection.objects.link(c)
        c.data.transform(m)
        c.data.flip_normals()
        out.append(c)
    return out
