"""Helpers for the batch Y models of wave 3 (sheet 8: IXMUCANE and SAWBLADES; wave3_y.py, the small
creatures and ships; wave3_y_wall.py, the rock wall with its glowing slots; wave3_y_boss.py, the big
spider): the sprites' pixels (wave3_y_art.py), the pixel
frames, sprite painting and shapes of batch S (wave3_s_kit), the parts and materials of batch J
(wave3_j_kit), heightfield parts (wave3_q_kit), and the build loop of batch N (wave3_n_kit: stand-alone
models and whole objects cut into their sprites' pieces, silhouettes checked against pixel masks).

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
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_y_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, part, lathe_axis, hoop, column, tube, catmull,  # noqa: E402,F401
                         sphere, rounded_box, block, lumpy, meshes, bake, triangles, simplify_bottom, decimate,
                         sampler)
from wave3_s_kit import (Frame, Painter, paint_sprite, paint_pixels, pixelate, merge_flat, slab, prism_x,  # noqa: E402,F401
                         prism_y, lathe_y, lift, mirror_copies, smoothstep)

model = n.model
pieced = n.pieced
run = n.run
check_mask = n.check_mask


def frame(name, width, origin):
    """A Frame of one of wave3_y_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def heightfield(name, polys, z_of, mat=None, spacing=0.5, smooth_angle=50, edge=None):
    return q.heightfield(name, polys, z_of, mat, spacing, smooth_angle, edge)


def polys_of(fr, keep, smooth=2, epsilon=0.4, min_area=0.5, grow=0.0):
    """The outlines of the frame's pixels keep(index, column, row) accepts (model coordinates)."""
    rows = regions(fr.g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    polys = sh.outlines(rows, "#", (fr.ox, fr.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)
    if grow:
        polys = [sh.inset(p, -grow) for p in polys]
    return polys


def ellipse(cx, cy, rx, ry, count=32, angle=0.0):
    return sh.ellipse(cx, cy, rx, ry, angle, count)


def torus(name, centre, major, minor, mat, segments=40, sides=12, squash=1.0, scale_y=1.0):
    return q.torus(name, centre, major, minor, mat, segments, sides, squash, scale_y)


def cone(name, start, direction, length, base, mat, tip=0.12, segments=16):
    return q.cone(name, start, direction, length, base, mat, tip, segments)


def loft_path(name, path, sections, mat, segments=16, smooth_angle=55, up=(0, 0, 1)):
    """A tapering limb along a 3D path: sections[i] = (half-width, half-height) of an elliptical
    cross-section at path[i] (the height measured towards `up`, the width across)."""
    pts = [Vector(p) for p in path]
    upv = Vector(up)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        side = t.cross(upv)
        if side.length < 1e-6:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        u = side.cross(t).normalized()
        hw, hh = sections[i]
        rings.append([p + side * math.cos(2 * math.pi * j / segments) * hw + u * math.sin(2 * math.pi * j / segments) * hh
                      for j in range(segments)])
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * min(sections[0]) * 0.6,
                 end_point=pts[-1] + t1 * min(sections[-1]) * 0.6)
    return k.smooth(obj, smooth_angle)


def resample(points, count):
    """A smooth path (catmull) through 3D points, resampled to `count` points evenly along it."""
    dense = catmull(points, 0.1)
    lengths = [0.0]
    for a, b in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    out, j = [], 0
    for i in range(count):
        target = total * i / (count - 1)
        while j < len(lengths) - 2 and lengths[j + 1] < target:
            j += 1
        seg = max(lengths[j + 1] - lengths[j], 1e-9)
        t = (target - lengths[j]) / seg
        out.append(dense[j].lerp(dense[j + 1], min(1.0, max(0.0, t))))
    return out


def jitter(obj, amount, seed=1, scale=1.6, min_z=0.15):
    """Displaces the vertices above min_z by smooth noise (sines), for rough rock."""
    rnd = random.Random(seed)
    waves = [(Vector([rnd.uniform(-1, 1) for _ in range(3)]).normalized() * rnd.uniform(0.6, 1.4) * scale,
              rnd.uniform(0, 6.3)) for _ in range(7)]
    for v in obj.data.vertices:
        if v.co.z < min_z:
            continue
        d = sum(math.sin(wv.dot(v.co) + ph) for wv, ph in waves) / len(waves) ** 0.5
        nrm = v.normal
        v.co += nrm * d * amount
    return obj


def frame_mask(fr, box=None):
    """Coverage of a frame (rows of bools); box (c0, c1, r0, r1), end exclusive."""
    return n.art_mask(fr.g, box)


def loft_y(name, sections, mat, segments=24, power=2.0, start=None, end=None, smooth_angle=50):
    """A hull along y through sections (y, x centre, z centre, half-width, top, bottom): each a superellipse
    of `power` whose upper half is `top` high and lower half `bottom` deep (as wave3_t_kit.loft_y)."""
    rings = []
    for yy, xc, zc, hw, top, bottom in sections:
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s_ = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / power), c) * hw
            v = math.copysign(abs(s_) ** (2 / power), s_) * (top if s_ >= 0 else bottom)
            pts.append(Vector((xc + u, yy, zc + v)))
        rings.append(pts)
    first, last = sections[0], sections[-1]
    obj = k.loft(name, rings, mat, start_point=start or (first[1], first[0], first[2]),
                 end_point=end or (last[1], last[0], last[2]))
    return k.smooth(obj, smooth_angle)


def smooth_sections(points, step=0.5):
    """Sections for loft_y sampled smoothly (Catmull-Rom, k.profile) through key sections."""
    return [tuple(p) for p in k.profile(points, step)]


def ring_path(name, points, radius, mat, segments=10):
    """A closed tube through 3D points (a hoop of any shape), as wave3_u_kit.ring_path."""
    pts = [Vector(p) for p in points]
    count = len(pts)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[(i - 1) % count], pts[(i + 1) % count]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(t).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) + up * math.sin(2 * math.pi * j / segments))
                      * radius for j in range(segments)])
    verts = [v for r in rings for v in r]
    faces = []
    for i in range(count):
        i2 = (i + 1) % count
        for j in range(segments):
            j2 = (j + 1) % segments
            faces.append((i * segments + j, i * segments + j2, i2 * segments + j2, i2 * segments + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def interp(table, t):
    """Linear interpolation in a table of (t, value) pairs sorted by t (clamped)."""
    if t <= table[0][0]:
        return table[0][1]
    for (t0, v0), (t1, v1) in zip(table, table[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / max(t1 - t0, 1e-9)
    return table[-1][1]
