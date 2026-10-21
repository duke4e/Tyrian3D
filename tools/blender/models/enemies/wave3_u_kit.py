"""Helpers for the batch U models of wave 3 (sheet S: MINEMAZE, GAUNTLET and the asteroid levels): wave3_u.py,
the bunker with the green lamp and the blue pipe across the mine maze; wave3_u_carrier.py, the tracked carrier with the launcher and the robot it carries;
wave3_u_hangar.py, the hangar with the numbers on its roof. The sprites' pixels are in wave3_u_art.py; the
part builders come from the earlier batches' kits (wave3_j_kit: palette materials, turned parts, tubes, the
tiled floor, painting faces, the build loop; wave3_o_kit: cutting a whole object into its sprites' pieces,
mirroring, the triangle budget; wave3_p_kit: heightfield beds and the grey rubble as boulders; wave3_q_kit:
heightfield parts, ribs and grooves on a surface).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
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
import wave3_o_kit as o  # noqa: E402,F401
import wave3_p_kit as p  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_u_art as art  # noqa: E402,F401
from wave3_j_kit import (bake, block, catmull, grid, hoop, lathe_axis, meshes, paint_faces, pal, part,  # noqa: E402,F401
                         regions, rounded_box, sampler, sphere, transform, triangles, tube)
from wave3_o_kit import cut, merge, mirror_x, mirror_y, move, paint_bands, smoothstep, budget, decimate  # noqa: E402,F401

S = "enemy_S"


def model(name, sprites, size=(24, 28)):
    """Registers a builder (wave3_j_kit.model); sprites: sheet S sprites [(sprite, large)]."""
    return w.model(name, [(S, s, large) for s, large in sprites], size)


whole = w.whole


def run():
    """wave3_j_kit.run, with --whole renders at a larger scale (768 pixels across the longer side)."""
    options = k.args()
    if "whole" not in options:
        return w.run()
    for name in options["whole"].split(","):
        fn, size = w.WHOLES[name]
        k.reset()
        fn()
        bake()
        print(f"--- {name}: {triangles()} triangles")
        bpy.context.scene.view_settings.view_transform = "Standard"
        prefix = options.get("preview", "/tmp/whole_") + name
        k.preview(prefix, size, scale=max(8, 768 // max(size)))
        scene = bpy.context.scene
        cam = bpy.data.objects["3q"]
        cam.location = Vector((38, -48, 42)) * (0.5 * max(size) / 24.0)
        scene.render.resolution_x = scene.render.resolution_y = 768
        scene.render.filepath = prefix + "_3q.png"
        bpy.ops.render.render(write_still=True)


# --- Pixels --------------------------------------------------------------------------------------

def at(g, c, r):
    if 0 <= r < len(g) and 0 <= c < len(g[r]):
        return g[r][c]
    return None


def px(col, ox=12):
    """A pixel column's centre as x."""
    return col + 0.5 - ox


def py(row, oy=14):
    """A pixel row's centre as y."""
    return oy - (row + 0.5)


def shades(g, origin, keep, blur=1, value=lambda v: v & 15):
    """(x, y) -> the shade of the pixels keep(index) accepts, bilinear and blurred (wave3_j_kit.sampler)."""
    return sampler(g, origin, value=value, blur=blur, keep=lambda v: v is not None and keep(v))


def pixel_polys(g, keep, origin, smooth=2, epsilon=0.4, min_area=0.5):
    """The outlines of the pixels keep(index, column, row) accepts."""
    rows = regions(g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    return sh.outlines(rows, "#", origin, smooth=smooth, epsilon=epsilon, min_area=min_area)


def refill(g, replace, sources, seed=1, darker=0):
    """A copy of the grid whose pixels replace(index, column, row) accepts (shadows the sprite draws, which the
    game's own shadows now cast) take the index of a random pixel sources(index, column, row) accepts, from the
    same rows if possible, `darker` shades darker (ramp 0 only)."""
    rnd = random.Random(seed)
    out = [list(row) for row in g]
    pool = [(r, v) for r, row in enumerate(g) for c, v in enumerate(row) if v is not None and sources(v, c, r)]
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v is None or not replace(v, c, r):
                continue
            near = [pv for pr, pv in pool if abs(pr - r) <= 2] or [pv for _, pv in pool]
            nv = rnd.choice(near)
            if darker and nv >> 4 == 0:
                nv = max(1, nv - darker)
            out[r][c] = nv
    return out


# --- Parts ---------------------------------------------------------------------------------------

def rubble(name, g, keep, prefix, origin=(12, 14), **options):
    """The grey rubble a ground sprite is drawn on, as round boulders on a dark base (wave3_p_kit.grey_rocks);
    keep(index, column, row) picks the rubble's pixels."""
    options.setdefault("rmax", 2.8)
    options.setdefault("height", 0.6)
    options.setdefault("base_h", 0.45)
    return p.grey_rocks(name, g, keep, prefix=prefix, origin=origin, **options)


def torus(name, centre, major, minor, mat, segments=40, sides=10, squash=1.0, scale_y=1.0):
    return q.torus(name, centre, major, minor, mat, segments, sides, squash, scale_y)


def ring_path(name, points, radius, mat, segments=10, closed=True):
    """A closed tube through 3D points (a hoop of any shape): a loft of circles round the path."""
    pts = [Vector(pt) for pt in points]
    n = len(pts)
    rings = []
    for i, pt in enumerate(pts):
        a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = tangent.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([pt + (side * math.cos(2 * math.pi * j / segments) + up * math.sin(2 * math.pi * j / segments))
                      * radius for j in range(segments)])
    verts = [v for r in rings for v in r]
    faces = []
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(segments):
            j2 = (j + 1) % segments
            faces.append((i * segments + j, i * segments + j2, i2 * segments + j2, i2 * segments + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def paint_by_pixels(obj, g, origin, mats, pick=None, side=None):
    """Paints the faces facing up with the material of the pixel under their centre: mats maps palette
    indices to materials, pick(index) -> a key of mats for indices it lacks (None keeps the face); faces
    facing sideways (normal z < 0.35) take `side` if given."""
    def choose(c, n):
        if side is not None and n.z < 0.35:
            return side
        v = w.pixel_at(g, c.x, c.y, origin)
        if v is None:
            return None
        if v in mats:
            return mats[v]
        if pick is not None:
            key = pick(v)
            return mats.get(key) if key is not None else None
        return None
    return paint_faces(obj, choose)


def subdivide_mesh(obj, cuts=1):
    """Splits the mesh's faces (finer painting)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    bm.to_mesh(obj.data)
    bm.free()
    return obj
