"""Helpers for the batch AF models of wave 3 (sheet R: IXMUCANE, SAWBLADES and ASSASSIN; wave3_af_domes.py, the
glass domes over their cities; wave3_af.py, the small flying stones; wave3_af_heap.py, IXMUCANE's boss: a
machine in a rock heap and the heap that covers it): the sprites' pixels (wave3_af_art.py), the pixel frames,
painting and budget of batch V (wave3_v_kit), the parts of batches J and AA (wave3_j_kit, wave3_aa_kit: convex
rocks, faceted painting) and the build loop of batch N (wave3_n_kit: stand-alone models and whole objects cut
into their sprites' pieces, silhouettes checked against pixel masks), with a few parts of their own: open glass
shells (cut into pieces without caps, so that no wall shows through the glass where the pieces meet), cities of
towers laid out by splitting their ground into blocks.

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
from mathutils import Matrix, Vector  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_aa_kit as aa  # noqa: E402,F401
import wave3_af_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box,  # noqa: E402,F401
                         block, meshes, bake, sampler, lumpy)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, outlines_of, lift, slab,  # noqa: E402,F401
                         smoothstep)
from wave3_aa_kit import convex_rock, paint_facets, subdivide_faces  # noqa: E402,F401

model = n.model
pieced = n.pieced
PROTECT = v.PROTECT
GLASS = "glassshell"   # parts whose names contain this are open glass shells: cut without caps


def frame(name, width, origin):
    """A Frame of one of wave3_af_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def glass(name, index, alpha, roughness=0.22, metallic=0.0, glow=None, emission=None):
    """A see-through palette material (drawn blended); glow: emission strength in its colour (or `emission`)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha,
                          emission=emission or k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha)


def piece(name, f, c0, r0, mask_fn=None, width=24, height=28):
    """A width x height piece of a whole object at pixel (c0, r0) of frame f: (piece name, its box in the
    whole's coordinates, its sprite's centre there, its mask for --check: mask_fn(box) or the frame's pixels)."""
    x0, y1 = c0 - f.ox, f.oy - r0
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    box = (c0, c0 + width, r0, r0 + height)
    return (name, (x0 + e, x0 + width - e, y1 - height + e, y1 - e), (x0 + width / 2, y1 - height / 2),
            (lambda: mask_fn(box)) if mask_fn else (lambda: f.mask(box)))


def grid_pieces(names, f, columns, rows, mask_fn=None, c0=0, r0=0):
    """The pieces of a whole object laid out as columns x rows 2x2 sprites from pixel (c0, r0): names row by
    row."""
    return [piece(names[j * columns + i], f, c0 + 24 * i, r0 + 28 * j, mask_fn) for j in range(rows)
            for i in range(columns)]


def mask_where(f, keep):
    """mask_fn for piece(): the frame's pixels keep(index, column, row) accepts, in a box."""
    def fn(box):
        c0, c1, r0, r1 = box
        return [[f.get(c, r) is not None and keep(f.get(c, r), c, r) for c in range(c0, c1)] for r in range(r0, r1)]
    return fn


# --- Cutting with open glass ------------------------------------------------------------------------

def cut_open(objects, x0, x1, y0, y1):
    """Keeps what lies in x0..x1, y0..y1 of open shells, leaving the cuts open."""
    kept = []
    planes = [((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))]
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for co, no in planes:
            if not bm.verts:
                break
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=no, clear_outer=True)
        if not bm.faces:
            bm.free()
            bpy.data.objects.remove(obj)
            continue
        bm.to_mesh(obj.data)
        bm.free()
        kept.append(obj)
    return kept


_cut_box = sh.cut_box


def cut_box(objects, x0, x1, y0, y1):
    """sh.cut_box, but the glass shells (names containing GLASS) stay open."""
    def is_glass(o):
        return GLASS in o.name
    shells = [o for o in objects if is_glass(o)]
    rest = [o for o in objects if not is_glass(o)]
    return _cut_box(rest, x0, x1, y0, y1) + cut_open(shells, x0, x1, y0, y1)


def run():
    """wave3_v_kit.run (wave3_n_kit's build loop, the budget sparing PROTECT) with glass shells cut open."""
    sh.cut_box = cut_box
    try:
        v.run()
    finally:
        sh.cut_box = _cut_box


# --- Glass shells ------------------------------------------------------------------------------------

def dome_shell(name, centre, reach, height, mat, rings=22, segments=96, power=2.2, ease=0.5, z0=0.0):
    """An open dome (no bottom): over the outline reach(angle) -> the distance from centre (x, y) to the outline
    along that angle; at the normalized radius t its height is z0 + height * (1 - t ** power) ** ease (ease 0.5:
    a round shoulder falling straight to the ground at the outline). Rings closer towards the edge."""
    cx, cy = centre
    reaches = [reach(2 * math.pi * j / segments) for j in range(segments)]
    verts = [(cx, cy, z0 + height)]
    for i in range(1, rings + 1):
        t = math.sin(0.5 * math.pi * i / rings)
        z = z0 + height * max(0.0, 1.0 - t ** power) ** ease
        for j in range(segments):
            a = 2 * math.pi * j / segments
            r = reaches[j] * t
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    faces = [(0, 1 + j, 1 + (j + 1) % segments) for j in range(segments)]
    for i in range(rings - 1):
        base, nxt = 1 + i * segments, 1 + (i + 1) * segments
        for j in range(segments):
            jj = (j + 1) % segments
            faces.append((base + j, nxt + j, nxt + jj, base + jj))
    obj = k.mesh_object(name, verts, faces, mat)
    return k.smooth(obj, 60)


def polygon_reach(poly, centre):
    """reach(angle) for dome_shell: the distance from centre to the polygon along a ray."""
    def reach(a):
        return w._ray_polygon(poly, centre, (math.cos(a), math.sin(a)))
    return reach


def shell_height(centre, reach, height, power=2.2, ease=0.5, z0=0.0):
    """The height of dome_shell's surface over (x, y) (z0 outside it)."""
    cx, cy = centre

    def z(x, y):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy)
        if d < 1e-6:
            return z0 + height
        t = d / max(reach(math.atan2(dy, dx)), 1e-6)
        if t >= 1.0:
            return z0
        return z0 + height * (1.0 - t ** power) ** ease
    return z


# --- Cities --------------------------------------------------------------------------------------------

def blocks(rect, rng, min_size=2.6, max_size=6.0, min_depth=None, max_depth=None):
    """Splits rect (x0, y0, x1, y1) into blocks between min_size and max_size across (x) and between min_depth
    and max_depth deep (y; default: as across), at random."""
    min_depth = min_size if min_depth is None else min_depth
    max_depth = max_size if max_depth is None else max_depth
    x0, y0, x1, y1 = rect
    wd, ht = x1 - x0, y1 - y0
    split_x = wd > max_size and wd >= 2 * min_size
    split_y = ht > max_depth and ht >= 2 * min_depth
    if split_x and split_y:
        split_x = wd / max_size >= ht / max_depth
        split_y = not split_x
    args = (rng, min_size, max_size, min_depth, max_depth)
    if split_x:
        cut = x0 + rng.uniform(max(min_size, 0.35 * wd), min(wd - min_size, 0.65 * wd))
        return blocks((x0, y0, cut, y1), *args) + blocks((cut, y0, x1, y1), *args)
    if split_y:
        cut = y0 + rng.uniform(max(min_depth, 0.35 * ht), min(ht - min_depth, 0.65 * ht))
        return blocks((x0, y0, x1, cut), *args) + blocks((x0, cut, x1, y1), *args)
    return [rect]


def coverage(rect, inside, step=0.5):
    """The share of rect's sample points inside(x, y) accepts."""
    x0, y0, x1, y1 = rect
    nx, ny = max(1, int((x1 - x0) / step)), max(1, int((y1 - y0) / step))
    hits = sum(inside(x0 + (i + 0.5) * (x1 - x0) / nx, y0 + (j + 0.5) * (y1 - y0) / ny)
               for i in range(nx) for j in range(ny))
    return hits / (nx * ny)


def tower(name, rect, z0, z1, roof, wall, bevel=0.22):
    """A tower block: a bevelled box over rect from z0 to z1, its roof `roof`, its sides `wall`."""
    x0, y0, x1, y1 = rect
    obj = k.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), wall)
    k.bevel(obj, bevel, 1)
    sh.apply_modifiers(obj)
    paint_faces(obj, lambda c, nrm: roof if nrm.z > 0.6 else None)
    return k.smooth(obj, 35)
