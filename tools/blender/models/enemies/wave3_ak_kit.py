"""Helpers for the batch AK models of wave 3 (sheet b: CAMANIS' boss, wave3_ak_boss.py): the sprites' pixels
(wave3_ak_art.py), and the kit of batch AG (wave3_ag_kit: pixel frames, painting faces by the sprite's pixel under
them, heightfield parts, relief by the sprite's brightness, broken (jagged) ends, soot; whole objects cut into
their sprites' pieces, the silhouette check and the build loop), with a few helpers of their own: frames made
symmetric or patched (the damaged look painted over the intact one), dents and debris for wrecked plating.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the whole object's centre. Pixel (column c, row r) of an art with origin (ox, oy) covers
x = c - ox .. c + 1 - ox, y = oy - r - 1 .. oy - r.
"""
import math
import os
import random
import sys

from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_ae_kit as ae  # noqa: E402,F401
import wave3_ag_kit as ag  # noqa: E402,F401
import wave3_ak_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, lathe_axis, tube, sphere, rounded_box, meshes, bake, sampler,  # noqa: E402,F401
                         transform, triangles)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, lift, smoothstep,  # noqa: E402,F401
                         mirror_copies)
from wave3_ae_kit import disc, delete_faces, join, displace_z  # noqa: E402,F401
from wave3_ag_kit import emboss, jag, scorch, ico_ellipsoid, brightness, luminance  # noqa: E402,F401

model = n.model
pieced = n.pieced
run = v.run
PROTECT = v.PROTECT
piece = ag.piece
lens = ag.lens
heightfield = ag.heightfield
polys_of = ag.polys_of


def frame(name, width, origin):
    """A Frame of one of wave3_ak_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def patched(base, top, keep=lambda c, r: True, shift=None):
    """A copy of frame `base` whose pixels are replaced by those of frame `top` where they differ from base's
    pixels as drawn (base.raw, kept before fill() or symmetric(); default its pixels) and keep(c, r): the
    damaged look painted over the intact one, so that what the damage leaves alone keeps the intact frame's
    colours. shift(c, r) -> (dc, dr) reads `top` displaced there."""
    raw_base = base.raw if hasattr(base, "raw") else base.g
    out = Frame.__new__(Frame)
    out.__dict__.update(base.__dict__)
    out._shades = {}
    out.g = [row[:] for row in base.g]
    for r in range(base.height):
        for c in range(base.width):
            if not keep(c, r):
                continue
            dc, dr = shift(c, r) if shift else (0, 0)
            t = top.get(c + dc, r + dr)
            if t != raw_base[r][c] and t is not None:
                out.g[r][c] = t
    return out


def dent(obj, centre, radius, depth, seed=0.0):
    """Pushes the vertices round (x, y) within `radius` down by up to `depth` (noisy): a crater in plating."""
    sh.apply_modifiers(obj)
    cx, cy = centre
    off = Vector((seed * 3.7, seed * 1.3, 0.0))
    for vt in obj.data.vertices:
        d = math.hypot(vt.co.x - cx, vt.co.y - cy) / radius
        if d < 1.0 and vt.co.z > 0.2:
            nz = 0.75 + 0.5 * noise.noise(Vector((vt.co.x, vt.co.y, 0.0)) / 1.3 + off)
            vt.co.z = max(0.4, vt.co.z - depth * (1.0 - d * d) * nz)
    obj.data.update()
    return obj


def debris(name, points, mat, size=(1.4, 2.6), seed=3):
    """Small twisted plates and chunks at points [(x, y, z)]: wreckage strewn over a torn hull."""
    rnd = random.Random(seed)
    parts = []
    for i, (x, y, z) in enumerate(points):
        s = rnd.uniform(*size)
        obj = rounded_box(f"{name}{i}", (0.0, 0.0, 0.0), (s, s * rnd.uniform(0.4, 0.9), s * rnd.uniform(0.25, 0.5)),
                          mat, bevel=0.15, segments=1)
        rot = (Matrix.Rotation(rnd.uniform(0, 6.3), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.7, 0.7), 4, "X") @
               Matrix.Rotation(rnd.uniform(-0.7, 0.7), 4, "Y"))
        obj.data.transform(Matrix.Translation((x, y, z)) @ rot)
        parts.append(obj)
    return parts


def pipe(name, points, radius, mat, bend=3.5, segments=16, step=1.0, cap=0.45):
    """wave3_ae_kit.pipe with its rings `step` apart (fewer triangles along long straight runs): a round pipe
    along straight runs between 3D points, its bends rounded, its ends closed by low rounded caps."""
    path = ae.fillet_path(points, bend, step)
    t0 = (path[1] - path[0]).normalized()
    t1 = (path[-1] - path[-2]).normalized()
    head, tail, sections_head, sections_tail = [], [], [], []
    for f_, d in ((0.93, 0.35), (0.72, 0.75), (0.42, 0.95)):
        head.insert(0, path[0] - t0 * radius * cap * d)
        sections_head.insert(0, f_)
        tail.append(path[-1] + t1 * radius * cap * d)
        sections_tail.append(f_)
    full = head + path + tail
    scales = sections_head + [1.0] * len(path) + sections_tail
    rings = []
    upv = Vector((0, 0, 1))
    for i, pt in enumerate(full):
        a, b = full[max(i - 1, 0)], full[min(i + 1, len(full) - 1)]
        t = (b - a).normalized()
        side = t.cross(upv)
        if side.length < 1e-6:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        u = side.cross(t).normalized()
        r = radius * scales[i]
        rings.append([pt + side * math.cos(2 * math.pi * j / segments) * r + u * math.sin(2 * math.pi * j / segments) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=path[0] - t0 * radius * cap, end_point=path[-1] + t1 * radius * cap)
    return k.smooth(obj, 50)
