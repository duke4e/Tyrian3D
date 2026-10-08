"""Helpers for the batch O models of wave 3 (sheet K: wave3_o.py, the fire column, the WARNING sign and
the sparks; wave3_o_machines.py, the grey machines): the sprites' pixels (wave3_o_art.py), the part
builders of batch J (wave3_j_kit: palette materials, inflated parts, turned parts, tubes, painting faces),
cutting a whole object into the pieces the game draws, periodic noise for tiling pieces, and the build
loop (wave3_j_kit.run).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre. Pixel (column c, row r) of an art with origin (ox, oy) covers
x = c - ox .. c + 1 - ox, y = oy - r - 1 .. oy - r.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_o_art as art  # noqa: E402,F401
from wave3_j_kit import (bake, block, catmull, grid, hoop, lathe_axis, meshes, outlines, paint_faces, pal,  # noqa: E402,F401
                         part, regions, relabel, rounded_box, sampler, sphere, transform, triangles, tube)

K = "enemy_K"


def model(name, sprites, size=(24, 28)):
    """Registers a builder (wave3_j_kit.model); sprites: sheet K sprites [(sprite, large)]."""
    return w.model(name, [(K, s, large) for s, large in sprites], size)


whole = w.whole
run = w.run


# --- Pixels --------------------------------------------------------------------------------------

def shades(g, origin, keep, value=lambda v: v & 15, blur=1):
    """A function (x, y) -> the shade of the pixels keep(index) accepts, as wave3_j_kit.sampler."""
    return sampler(g, origin, value=value, blur=blur, keep=lambda v: v is not None and keep(v))


def char_rows(g, fn):
    """Char rows of a grid: fn(index, column, row) -> a char ('.' nothing)."""
    return regions(g, fn)


def at(g, c, r):
    if 0 <= r < len(g) and 0 <= c < len(g[r]):
        return g[r][c]
    return None


# --- Painting ------------------------------------------------------------------------------------

def paint_bands(obj, value, bands):
    """Gives each face the material of the band value(centre, normal) falls in: bands [(lowest, material)],
    ascending (None from value keeps the face's material)."""
    def pick(c, n):
        v = value(c, n)
        if v is None:
            return None
        chosen = bands[0][1]
        for lowest, mat in bands:
            if v >= lowest:
                chosen = mat
        return chosen
    return paint_faces(obj, pick)


# --- Cutting -------------------------------------------------------------------------------------

def cut(objects, box, centre):
    """The part of objects inside box (x0, x1, y0, y1), closed at the cuts, moved so that `centre` (the
    sprite's centre in the whole object's coordinates) is the origin."""
    x0, x1, y0, y1 = box
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -centre[0], -centre[1])
    for obj in kept:
        k.smooth(obj, 50)
    return kept


def mirror_y(objects, axis_y=0.0):
    """Mirrors objects across y = axis_y (normals kept facing out)."""
    return transform(objects, Matrix.Translation((0, 2 * axis_y, 0)) @ Matrix.Scale(-1, 4, (0, 1, 0)))


def mirror_x(objects, axis_x=0.0):
    return transform(objects, Matrix.Translation((2 * axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)))


def move(objects, dx=0.0, dy=0.0, dz=0.0):
    return transform(objects, Matrix.Translation((dx, dy, dz)))


def merge(name, objects):
    """Joins objects into one (their materials kept)."""
    objects = [o for o in objects if o is not None]
    if len(objects) == 1:
        objects[0].name = name
        return objects[0]
    for o in objects:
        sh.apply_modifiers(o)
    with bpy.context.temp_override(selected_editable_objects=objects, active_object=objects[0],
                                   selected_objects=objects):
        bpy.ops.object.join()
    objects[0].name = name
    return objects[0]


def decimate(obj, target):
    return w.decimate(obj, target)


# --- Noise ---------------------------------------------------------------------------------------

class PeriodicPuffs:
    """Soft bumps scattered over a band x0..x1 that repeats every `period` along y: value(x, y) is the
    sum of Gaussian bumps (amplitude, radius across, `stretch` times that along y) and the same for
    every copy of the pattern."""

    def __init__(self, count, x0, x1, period, radius=(3.0, 6.0), amplitude=(1.0, 3.0), stretch=(1.0, 1.0), seed=1):
        rnd = random.Random(seed)
        self.period = period
        self.puffs = []
        for _ in range(count):
            r = rnd.uniform(*radius)
            self.puffs.append((rnd.uniform(x0, x1), rnd.uniform(0, period), r, r * rnd.uniform(*stretch),
                               rnd.uniform(*amplitude)))

    def __call__(self, x, y):
        total = 0.0
        for px_, py_, rx, ry, a in self.puffs:
            dy = (y - py_) % self.period
            for d in (dy, dy - self.period):
                q = ((x - px_) / rx) ** 2 + (d / ry) ** 2
                if q < 9.0:
                    total += a * math.exp(-q)
        return total


class PeriodicWaves:
    """A sum of sine waves periodic along y with `period` (whole multiples) and free along x."""

    def __init__(self, count, period, kx=(0.15, 0.6), harmonics=(1, 4), seed=2):
        rnd = random.Random(seed)
        self.waves = [(rnd.uniform(*kx) * rnd.choice((-1, 1)), 2 * math.pi * rnd.randint(*harmonics) / period,
                       rnd.uniform(0, 2 * math.pi)) for _ in range(count)]
        self.norm = 1.0 / math.sqrt(count / 2.0)

    def __call__(self, x, y):
        return self.norm * sum(math.sin(a * x + b * y + p) for a, b, p in self.waves)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def budget(target=4800, floor=250):
    """Decimates the scene's larger meshes in proportion until it has about `target` triangles."""
    objects = meshes()
    for obj in objects:
        sh.apply_modifiers(obj)
    total = triangles(objects)
    if total <= target:
        return total
    big = [obj for obj in objects if triangles([obj]) > floor]
    fixed = total - sum(triangles([obj]) for obj in big)
    ratio = max(0.1, (target - fixed) / max(1, total - fixed))
    for obj in big:
        decimate(obj, max(floor, int(triangles([obj]) * ratio)))
    return triangles(meshes())
