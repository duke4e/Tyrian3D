"""Helpers for the batch AC models of wave 3 (sheet 7: CAMANIS and ICESECRET; wave3_ac.py, the stand-alone
models; wave3_ac_ice.py, the objects the game draws in pieces): the sprites' pixels (wave3_ac_art.py), the
pixel frames, sprite painting and shapes of batch S (wave3_s_kit), the parts and materials of batch J
(wave3_j_kit), heightfields (wave3_q_kit), the lofts and paths of batch Y (wave3_y_kit) and the build loop
of batch N (wave3_n_kit: stand-alone models and whole objects cut into their sprites' pieces, silhouettes
checked against pixel masks).

The ground objects of sheet 7 stand on CAMANIS' ice plateaus, which their sprites draw round them (and the
objects' shadows on it, below and to the right). The 3D ground shows that ice already, and the game casts its
own shadows, so the models leave the drawn ice and shadows out (their silhouettes are checked against the
object's own pixels); only the crater, which is a shape in the ice, is modelled as ice.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

import bmesh  # noqa: F401
import bpy  # noqa: F401
from mathutils import Matrix, Vector  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_y_kit as yk  # noqa: E402,F401
import wave3_ac_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, lathe_axis, hoop, column, tube, catmull,  # noqa: E402,F401
                         sphere, rounded_box, block, meshes, bake, triangles, sampler)
from wave3_s_kit import (Frame, Painter, paint_sprite, paint_pixels, pixelate, merge_flat, slab, prism_x,  # noqa: E402,F401
                         prism_y, lathe_y, lift, mirror_copies, smoothstep)
from wave3_y_kit import loft_y, loft_path, smooth_sections, ring_path, torus, cone, ellipse, interp  # noqa: E402,F401

model = n.model
pieced = n.pieced
run = n.run


def frame(name, width, origin):
    """A Frame of one of wave3_ac_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def is_ice(v):
    """The ice the sprites draw round the objects (and the shadows on it): ramp 3, the dark blues."""
    return v is not None and v >> 4 == 3


def object_mask(fr, box=None, keep=lambda v, c, r: not is_ice(v)):
    """Coverage of a frame's object pixels (the drawn ice and shadows left out); box (c0, c1, r0, r1), end
    exclusive."""
    h, wd = len(fr.g), fr.width
    c0, c1, r0, r1 = box or (0, wd, 0, h)
    return [[0 <= r < h and 0 <= c < wd and fr.g[r][c] is not None and keep(fr.g[r][c], c, r)
             for c in range(c0, c1)] for r in range(r0, r1)]


def heightfield(name, polys, z_of, mat=None, spacing=0.5, smooth_angle=50, edge=None):
    return q.heightfield(name, polys, z_of, mat, spacing, smooth_angle, edge)


def superellipse(cx, cy, rx, ry, power=2.0, count=48, angle=0.0):
    """A superellipse outline (counter-clockwise), turned by `angle` radians."""
    ca, sa = math.cos(angle), math.sin(angle)
    out = []
    for i in range(count):
        a = 2 * math.pi * i / count
        c, s_ = math.cos(a), math.sin(a)
        u = math.copysign(abs(c) ** (2 / power), c) * rx
        v = math.copysign(abs(s_) ** (2 / power), s_) * ry
        out.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return out


def carve(obj, centre, size):
    """Cuts a box (centre, size) out of obj (a boolean difference, applied)."""
    mat = obj.data.materials[0] if obj.data.materials else None
    cutter = k.box(obj.name + "_cutter", centre, size, mat)
    mod = obj.modifiers.new("carve", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    mod.material_mode = "TRANSFER"
    sh.apply_modifiers(obj)
    bpy.data.objects.remove(cutter)
    # Keep only the object's own material slots (the cutter's face the cut takes its first material).
    while len(obj.data.materials) > 1 and obj.data.materials[-1] is None:
        obj.data.materials.pop()
    for poly in obj.data.polygons:
        if poly.material_index >= len(obj.data.materials) or obj.data.materials[poly.material_index] is None:
            poly.material_index = 0
    return obj
