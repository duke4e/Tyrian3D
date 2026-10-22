"""Helpers for the batch AD models of wave 3 (sheet H: GYGES, TORM and BONUS; wave3_ad.py, GYGES' green balls and
spike; GYGES' creatures in their pieces of tube wall are polish_gyges_wall.py's, the waterfall of TORM and BONUS
polish_waterfall.py's, TORM's beetle polish_torm_beetle.py's): the sprites' pixels (wave3_ad_art.py), and the parts,
painting and build loop of batch AA (wave3_aa_kit: pixel frames, reliefs, painting faces by the sprite's pixel under
them, stand-alone models and whole objects cut into their sprites' pieces), with lofted paths of its own.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_aa_kit as aa  # noqa: E402,F401
import wave3_ad_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box,  # noqa: E402,F401
                         meshes, bake, sampler, transform, lumpy, triangles)
from wave3_v_kit import (Frame, Painter, paint_sprite, merge_flat, relief, outlines_of, mirror_scene, lift,  # noqa: E402,F401
                         smoothstep)
from wave3_aa_kit import piece, grid_pieces, cone, lens, ellipsoid_point, blobs  # noqa: E402,F401

model = n.model
pieced = n.pieced
PROTECT = v.PROTECT


def frame(name, width, origin):
    """A Frame of one of wave3_ad_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def loft_path(name, path, radii, mat, segments=14, squash=1.0, up=(0, 0, 1), smooth_angle=60, caps=True):
    """A tube along a 3D path whose radius varies (one per point; a pair (across, up) flattens it), its
    cross-sections kept level (their `up` towards `up`), its ends closed to points."""
    pts = [Vector(p) for p in path]
    rings = []
    upv = Vector(up)
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        side = t.cross(upv)
        if side.length < 1e-6:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        u = side.cross(t).normalized()
        r = radii[i]
        rw, rh = (r, r * squash) if not isinstance(r, (tuple, list)) else r
        rings.append([p + side * (rw * math.cos(2 * math.pi * j / segments)) + u * (rh * math.sin(2 * math.pi * j / segments))
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, cap_start=caps, cap_end=caps, start_point=pts[0], end_point=pts[-1])
    return k.smooth(obj, smooth_angle)


def run():
    """wave3_v_kit.run: the stand-alone models and the objects cut into pieces. Options as there: --only a,b
    --preview <prefix>  --check 1  --stats 1  --whole <prefix>."""
    v.run()

