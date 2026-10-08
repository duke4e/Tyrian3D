"""Helpers for the batch R models of wave 3 (sheet G: TORM, BOTANY A and B, BONUS, GYGES, MISTAKES, SOH JIN,
GRYPHON, GEM WAR, MARKERS; wave3_r.py, the machines on the foliage; wave3_r_beasts.py, the creatures and
ships): the sprites' pixels (wave3_r_art.py), the part builders of batch J (wave3_j_kit: palette materials,
inflated parts, turned parts, tubes, painting faces, cutting a whole object into the pieces the game draws,
the build loop), the foliage of batch M (wave3_m_kit: sheet G draws its ground machines on the same leaves
as sheet J), relief heightfields over a sprite's pixels, and a triangle budget.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
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
import wave3_m_kit as mk  # noqa: E402,F401
import wave3_r_art as art  # noqa: E402,F401
from wave3_j_kit import (bake, catmull, grid, hoop, lathe_axis, meshes, paint_faces, pal, part, regions,  # noqa: E402,F401
                         relabel, rounded_box, sampler, sphere, transform, triangles, tube, column, block)

G = "enemy_G"


def model(name, sprites, size=(24, 28)):
    """Registers a builder (wave3_j_kit.model); sprites: sheet G sprites [(sprite, large)]."""
    return w.model(name, [(G, s, large) for s, large in sprites], size)


whole = w.whole
run = w.run
is_leaf = mk.is_leaf


def foliage(name, g, is_floor, prefix, origin=(12, 14), top=1.2, relief=1.1, edge=1.6):
    """The leafy ground of TORM and BOTANY under a machine (wave3_m_kit.foliage)."""
    return mk.foliage(name, g, is_floor, prefix, origin=origin, top=top, relief=relief, edge=edge)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def at(g, c, r):
    if 0 <= r < len(g) and 0 <= c < len(g[r]):
        return g[r][c]
    return None


def greys(prefix, metallic=0.55):
    """The grey ramp (ramp 0) as materials by shade."""
    return {s: pal(f"{prefix}_grey{s:x}", s, metallic=metallic, roughness=0.62 - 0.03 * s) for s in range(1, 14)}


def band(value, bands):
    """The material of the band value falls in: bands [(lowest, material)], ascending."""
    chosen = bands[0][1]
    for lowest, mat in bands:
        if value >= lowest:
            chosen = mat
    return chosen


# --- Parts ---------------------------------------------------------------------------------------

def _inside(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[i - 1]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def grown(rows, chars, grow, origin=(12, 14), smooth=2, epsilon=0.4, min_area=0.3):
    """The outlines of the pixels whose char is in chars, the outer ones moved out by `grow` and the
    holes in them shrunk by as much (so a part grown over the sprite's dark outline keeps its holes'
    outline too)."""
    polys = sh.outlines(rows, chars, origin, smooth=smooth, epsilon=epsilon, min_area=min_area)
    out = []
    for i, p in enumerate(polys):
        hole = any(j != i and _inside(q, *p[0]) for j, q in enumerate(polys))
        out.append(sh.inset(p, grow if hole else -grow))
    return out


def inflated(name, rows, chars, mat, profile, grow=0.0, origin=(12, 14), bottom=0.0, base=0.0, z_fn=None,
             spacing=0.5, rim=0.15, smooth_angle=50, smooth=2):
    """A part inflated from the pixels of rows whose char is in chars (wave1_d_shapes.inflate), grown by
    `grow` over the sprite's outline (its holes shrunk as much)."""
    polys = grown(rows, chars, grow, origin, smooth=smooth)
    obj = sh.inflate(name, polys, mat, profile, bottom=bottom, base=base, rim=rim, spacing=spacing, z_fn=z_fn)
    return k.smooth(obj, smooth_angle)


# --- Relief --------------------------------------------------------------------------------------

def heightfield(name, cells, z_of, mat_of, origin=(12, 14), sub=2, base=0.0, smooth_angle=40, mats=(), target=None):
    """A solid over a set of pixels (cells: {(column, row)}): its top a heightfield z_of(x, y) sampled
    `sub` times per pixel, its sides straight down to `base` and a flat bottom; each top face takes
    the material mat_of(centre, normal) (the sides and bottom the first of `mats`). target: collapse
    it to about that many triangles (before painting)."""
    ox, oy = origin
    step = 1.0 / sub
    verts = {}
    bm = bmesh.new()

    def vert(i, j, top=True):
        key = (i, j, top)
        if key not in verts:
            x, y = i * step - ox, oy - j * step
            verts[key] = bm.verts.new((x, y, z_of(x, y) if top else base))
        return verts[key]
    quads = set()
    for c, r in cells:
        for a in range(sub):
            for b in range(sub):
                quads.add((c * sub + a, r * sub + b))
    for i, j in quads:
        a, b, cc, d = vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)
        # Rows run down the screen (j up = y down): counter-clockwise seen from above is a, d, cc, b.
        if abs(a.co.z - cc.co.z) <= abs(b.co.z - d.co.z):
            bm.faces.new((a, d, cc))
            bm.faces.new((a, cc, b))
        else:
            bm.faces.new((a, d, b))
            bm.faces.new((b, d, cc))
    # The sides: along every quad edge with no neighbour.
    for i, j in quads:
        for (di, dj), (p, q) in (((0, -1), ((i, j), (i + 1, j))), ((1, 0), ((i + 1, j), (i + 1, j + 1))),
                                 ((0, 1), ((i + 1, j + 1), (i, j + 1))), ((-1, 0), ((i, j + 1), (i, j)))):
            if (i + di, j + dj) in quads:
                continue
            t0, t1 = vert(*p), vert(*q)
            b0, b1 = vert(*p, top=False), vert(*q, top=False)
            bm.faces.new((t1, t0, b0, b1))
    bottoms = [f for f in bm.faces if all(abs(v.co.z - base) < 1e-6 for v in f.verts)]
    for f in bottoms:
        bm.faces.remove(f)
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    if target:
        w.decimate(obj, target)
    paint_faces(obj, lambda c, n: mat_of(c, n) if n.z > 0.05 else None)
    return k.smooth(obj, smooth_angle)


def stats_print(*objects):
    """Prints the triangle counts of parts (while tuning)."""
    if "stats" in k.args():
        for obj in objects:
            print(f"--- part {obj.name}: {triangles([obj])} triangles")


# --- Cutting and the budget ----------------------------------------------------------------------

def cut(objects, box, centre):
    """The part of objects inside box (x0, x1, y0, y1), closed at the cuts, moved so that `centre` (the
    sprite's centre in the whole object's coordinates) is the origin."""
    x0, x1, y0, y1 = box
    kept = sh.cut_box(objects, x0, x1, y0, y1)
    sh.move(kept, -centre[0], -centre[1])
    for obj in kept:
        k.smooth(obj, 50)
    return kept


def mirror_x(objects, axis_x=0.0):
    return transform(objects, Matrix.Translation((2 * axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)))


def move(objects, dx=0.0, dy=0.0, dz=0.0):
    return transform(objects, Matrix.Translation((dx, dy, dz)))


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
        w.decimate(obj, max(floor, int(triangles([obj]) * ratio)))
    return triangles(meshes())
