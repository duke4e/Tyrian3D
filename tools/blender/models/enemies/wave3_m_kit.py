"""Helpers for the batch M models of wave 3 (sheet J: TORM, BOTANY A and B, BONUS and ?TUNNEL?), on top
of the batch J kit (wave3_j_kit: pixel grids, palette materials, inflated parts, turned parts, tubes,
the floor heightfield, cutting larger objects into pieces, the build loop): the sprites' pixels
(wave3_m_art.py), the foliage the ground sprites of sheet J are drawn on, fluted columns, the red
claws of the green machines and a few shape helpers.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave3_j_kit as base  # noqa: E402
from wave3_j_kit import (k, sh, grid, regions, relabel, px, py, pal, paint_faces, part, lathe_axis, hoop,  # noqa: E402,F401
                         column, tube, catmull, sphere, rounded_box, block, meshes, bake, transform, triangles,
                         simplify_bottom, decimate, piece, floor, model, whole, run)
import wave3_m_art as art  # noqa: E402,F401

J = "enemy_J"


# --- The foliage -----------------------------------------------------------------------------------

def foliage_bands(prefix):
    """The foliage's greens (ramp C) in five bands, dark to light."""
    return [(0, pal(f"{prefix}_leaf0", 0xc0, metallic=0.0, roughness=0.75)),
            (1.5, pal(f"{prefix}_leaf1", 0xc1, metallic=0.0, roughness=0.7)),
            (2.5, pal(f"{prefix}_leaf2", 0xc2, metallic=0.0, roughness=0.65)),
            (3.5, pal(f"{prefix}_leaf3", 0xc3, metallic=0.0, roughness=0.6)),
            (4.5, pal(f"{prefix}_leaf5", 0xc5, metallic=0.0, roughness=0.55))]


def is_leaf(v):
    """Foliage pixels: ramp C and the near-black greens of its shadows."""
    return v >> 4 == 0xc or 0x20 <= v <= 0x24


def foliage(name, g, is_floor, prefix, origin=(12, 14), top=1.2, relief=1.1, edge=1.6):
    """The leafy ground a sprite is drawn on, as a low heightfield slab (wave3_j_kit.floor): the
    lighter leaves stand higher than the shadows between them; its edge falls away over `edge`."""
    return floor(name, g, foliage_bands(prefix), is_floor, origin=origin, top=top, relief=relief, edge=edge)


# --- Shapes ----------------------------------------------------------------------------------------

def fluted(name, profile, mat, start, direction, flutes=8, depth=0.18, segments=48, light=None, up=(0, 0, 1),
           smooth_angle=60, squash=1.0):
    """A turned part along an axis whose surface is fluted: profile is (t, radius) pairs along
    `direction` from `start`; the radius dips by `depth` (a fraction) between `flutes` ridges.
    light: a material for the ridges' crests (painted on the outward faces)."""
    obj = lathe_axis(name, profile, mat, start, direction, segments, squash, smooth_angle, up)
    d = Vector(direction).normalized()
    s = Vector(start)
    for v in obj.data.vertices:
        rel = v.co - s
        along = rel.dot(d)
        radial = rel - d * along
        if radial.length < 1e-4:
            continue
        upv = Vector(up)
        side = d.cross(upv)
        if side.length < 1e-6:
            side = d.cross(Vector((1, 0, 0)))
        side.normalize()
        upv = side.cross(d).normalized()
        a = math.atan2(radial.dot(upv), radial.dot(side))
        f = 1.0 - depth * (0.5 - 0.5 * math.cos(flutes * a))
        v.co = s + d * along + radial * f
    if light is not None:
        def crest(c, n):
            rel = Vector(c) - s
            along = rel.dot(d)
            radial = rel - d * along
            upv = Vector(up)
            side = d.cross(upv)
            if side.length < 1e-6:
                side = d.cross(Vector((1, 0, 0)))
            side.normalize()
            upv = side.cross(d).normalized()
            a = math.atan2(radial.dot(upv), radial.dot(side))
            return light if math.cos(flutes * a) > 0.55 else None
        paint_faces(obj, crest)
    return obj


def ribbon(name, points, width, thickness, mat, smooth_angle=50):
    """A flat strip along 3D points (a band, a rib): `width` across (in the XY plane, sideways to
    the path), `thickness` up; rounded by a bevel."""
    pts = [Vector(p) for p in points]
    verts, faces = [], []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(t).normalized()
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append(p + side * sx * width / 2 + up * sz * thickness / 2)
    n = len(pts)
    for i in range(n - 1):
        for j in range(4):
            a, b = i * 4 + j, i * 4 + (j + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    faces.append((3, 2, 1, 0))
    last = (n - 1) * 4
    faces.append((last, last + 1, last + 2, last + 3))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    k.bevel(obj, min(width, thickness) * 0.3, 2)
    return k.smooth(obj, smooth_angle)


def claw(name, top, bottom, tip, radius, mat, core=None, core_rows=(0.3, 0.75), segments=14):
    """A red claw of the green machines: a pod running from `top` down to `bottom` and hooking in
    to `tip` (3D points), thinning to the tip; core: a glowing slit along its upper side between
    the fractions core_rows of the straight run."""
    path = catmull([top, bottom, tip], 0.6)
    n = len(path)
    radii = []
    for i in range(n):
        f = i / (n - 1)
        radii.append(radius * (1.0 if f < 0.55 else max(0.45, 1.0 - (f - 0.55) * 1.2)))
    obj = tube(name, path, radii, mat, segments)
    if core is not None:
        t0, t1 = core_rows
        a, b = Vector(top), Vector(bottom)
        p0, p1 = a + (b - a) * t0, a + (b - a) * t1
        lift = Vector((0, 0, radius * 0.86))
        tube(name + "_core", [p0 + lift, (p0 + p1) / 2 + lift * 1.04, p1 + lift], radius * 0.4, core, 8, squash=0.55)
    return obj


def lamp(name, centre, radius, mat, housing=None, squash=0.7):
    """A small lamp: a glowing dome in a ring."""
    x, y, z = centre
    if housing is not None:
        hoop(name + "_ring", (x, y, z - radius * 0.2), [(radius * 0.85, -0.25), (radius * 1.35, -0.2),
                                                        (radius * 1.4, 0.2), (radius * 0.95, 0.3)], housing, 16)
    return sphere(name, (x, y, z), (radius, radius, radius * squash), mat, 14, 7)


def drop_below(objects, z=0.0):
    """Cuts away what lies below z (things standing on the ground or a layer)."""
    return sh.flat_bottom(objects, z)


def rng(seed):
    return random.Random(seed)
