"""Helpers for the batch O models of wave 3 (sheet K: wave3_o.py, the sparks; wave3_o_machines.py, the grey
machines; also used by other batches' kits): the sprites' pixels (wave3_o_art.py), the part builders of batch J
(wave3_j_kit: palette materials, inflated parts, turned parts, tubes, painting faces), cutting a whole object into
the pieces the game draws, and the build loop (wave3_j_kit.run).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre. Pixel (column c, row r) of an art with origin (ox, oy) covers
x = c - ox .. c + 1 - ox, y = oy - r - 1 .. oy - r.
"""
import os
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
