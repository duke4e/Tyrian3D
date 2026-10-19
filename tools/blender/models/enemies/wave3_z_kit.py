"""Helpers for the batch Z models of wave 3 (sheet L: MINERS, SQUADRON, TIME WAR, STATION; wave3_z_small.py, the small creatures and ships of SQUADRON,
TIME WAR and MINERS; wave3_z_rock.py, MINERS's red rock: the spire, the mounds and the tan dome creature in its
pool; wave3_z_train.py, MINERS's crawler train; wave3_z_station.py, the station of STATION and TIME WAR and TIME
WAR's grey capsule). The sprites' pixels are in wave3_z_art.py; the parts come from the earlier batches' kits
(wave3_s_kit: pixel frames, painting by the sprite, slabs and prisms; wave3_q_kit: heightfield parts, rings;
wave3_j_kit: palette materials, turned parts, tubes, spheres; wave3_n_kit: stand-alone models and whole objects
cut into their sprites' pieces, the silhouette check, the triangle budget, the build loop).

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
import wave3_z_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, lathe_axis, hoop, column, tube, catmull, sphere,  # noqa: E402,F401
                         rounded_box, block, lumpy, meshes, bake, triangles, decimate, sampler)
from wave3_s_kit import (Frame, Painter, paint_sprite, paint_pixels, pixelate, merge_flat, slab, prism_x,  # noqa: E402,F401
                         prism_y, lathe_y, lift, mirror_copies, smoothstep)

L = "enemy_L"
model = n.model
pieced = n.pieced
check_mask = n.check_mask
torus = q.torus
cone = q.cone


def frame(name, width, origin):
    """A Frame of one of wave3_z_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def polys_of(fr, keep, smooth=2, epsilon=0.4, min_area=0.5, grow=0.0):
    """The outlines of the frame's pixels keep(index, column, row) accepts (model coordinates)."""
    rows = regions(fr.g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    polys = sh.outlines(rows, "#", (fr.ox, fr.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)
    if grow:
        polys = [sh.inset(p, -grow) for p in polys]
    return polys


def heightfield(name, polys, z_of, mat=None, spacing=0.5, smooth_angle=50, edge=None):
    """A closed part over the polygons, its top at z_of(x, y) (with edge: z_of(x, y, e), e rising from 0 on
    the outline to 1 `edge` pixels inside), its bottom flat at z = 0 (wave3_q_kit.heightfield)."""
    return q.heightfield(name, polys, z_of, mat, spacing, smooth_angle, edge)


def quarter(name, f, c0, r0, width=24, height=28, check=True):
    """A piece of a whole object at pixel (c0, r0) of frame f, one sprite (24 x 28, or 12 x 14 for a small
    one): (piece name, its box in the whole's coordinates, its sprite's centre there, its mask for --check)."""
    x0, y1 = f.left(c0), f.top(r0)
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    return (name, (x0 + e, x0 + width - e, y1 - height + e, y1 - e), (x0 + width / 2, y1 - height / 2),
            (lambda: f.mask((c0, c0 + width, r0, r0 + height))) if check else None)


def move(objects, dx=0.0, dy=0.0, dz=0.0):
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(Matrix.Translation((dx, dy, dz)))
    return objects


def rotate_about(objects, axis, angle, pivot):
    """Turns objects by angle (radians) about an axis ('X', 'Y', 'Z') through pivot."""
    m = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-Vector(pivot))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
    return objects


def field(fr, value, keep, blur=1):
    """A numpy field over the frame's pixels: value(index) where keep(index) holds, NaN elsewhere, blurred
    `blur` times among the kept pixels."""
    h, wd = len(fr.g), fr.width
    f = np.full((h, wd), np.nan)
    for r in range(h):
        for c in range(wd):
            v = fr.g[r][c]
            if v is not None and keep(v):
                f[r, c] = value(v)
    for _ in range(blur):
        out = f.copy()
        for r in range(h):
            for c in range(wd):
                if np.isnan(f[r, c]):
                    continue
                vals, wts = [], []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < wd and not np.isnan(f[rr, cc]):
                            vals.append(f[rr, cc])
                            wts.append(2.0 if dr == dc == 0 else 1.0 if dr == 0 or dc == 0 else 0.5)
                out[r, c] = np.average(vals, weights=wts)
        f = out
    return f


def field_sampler(fr, f):
    """(x, y) -> the field bilinear between pixel centres (the nearest known value outside)."""
    h, wd = f.shape
    known = np.argwhere(~np.isnan(f))

    def at(x, y):
        c, r = x + fr.ox - 0.5, fr.oy - y - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        total = weight = 0.0
        for rr, cc, wt in ((r0, c0, (1 - (r - r0)) * (1 - (c - c0))), (r0, c0 + 1, (1 - (r - r0)) * (c - c0)),
                           (r0 + 1, c0, (r - r0) * (1 - (c - c0))), (r0 + 1, c0 + 1, (r - r0) * (c - c0))):
            if 0 <= rr < h and 0 <= cc < wd and not np.isnan(f[rr, cc]):
                total += f[rr, cc] * wt
                weight += wt
        if weight > 0.05:
            return total / weight
        i = int(np.argmin((known[:, 0] - r) ** 2 + (known[:, 1] - c) ** 2))
        return f[known[i, 0], known[i, 1]]
    return at


def bands(prefix, ramp, shades, metallic=0.1, roughness=0.7, glow=None):
    """Materials of one ramp's shades, dark to light: [(shade, material)]."""
    return [(sh_, pal(f"{prefix}_{ramp * 16 + sh_:02x}", ramp * 16 + sh_, metallic=metallic, roughness=roughness,
                      glow=glow(sh_) if callable(glow) else glow)) for sh_ in shades]


def nearest_band(bands_, value):
    return min(bands_, key=lambda b: abs(b[0] - value))[1]


def paint_by(obj, value_at, bands_, wall_drop=1.5, under=None, wall_z=0.4):
    """Paints faces by value_at(x, y) (a shade), the nearest band's material; steep faces wall_drop darker,
    faces looking down `under` (default: the darkest band)."""
    def pick(c, nrm):
        if nrm.z < -0.5:
            return under or bands_[0][1]
        v = value_at(c.x, c.y)
        if abs(nrm.z) < wall_z:
            v -= wall_drop
        return nearest_band(bands_, v)
    return paint_faces(obj, pick)


def jitter(obj, amount, seed=1, scale=1.6, min_z=0.15):
    """Moves the vertices above min_z by smooth noise (rocks, crusts)."""
    rng = random.Random(seed)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() / scale, rng.uniform(0, 6.3))
             for _ in range(8)]
    for v in obj.data.vertices:
        if v.co.z <= min_z:
            continue
        d = sum(math.sin(wv.dot(v.co) + ph) for wv, ph in waves) / math.sqrt(len(waves))
        v.co += Vector((d * amount * 0.5, d * amount * 0.5, d * amount))
    return obj


# --- Previews of objects drawn from several separate models ----------------------------------------

ASSEMBLIES = {}  # name: (size, [(builder, (dx, dy))])


def assembly(name, size, parts):
    """Registers an assembly for --assembly previews: builders (each building one object in its own
    coordinates) and where its origin lies in the assembly."""
    ASSEMBLIES[name] = (size, parts)


def run():
    """wave3_n_kit.run; --assembly <prefix> [--only names] renders the registered assemblies instead."""
    options = k.args()
    if "assembly" not in options:
        return n.run()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, (size, parts) in ASSEMBLIES.items():
        if only and name not in only:
            continue
        k.reset()
        for build, (dx, dy) in parts:
            before = set(meshes())
            build()
            bake()
            move([o for o in meshes() if o not in before], dx, dy)
        print(f"== assembly {name}: {triangles()} triangles")
        bpy.context.scene.view_settings.view_transform = "Standard"
        prefix = options["assembly"] + name
        k.preview(prefix, size, scale=max(6, 640 // max(size)))
        n.render_3q(prefix, size, max(size) / 34.0)


# --- MINERS's hex rock -------------------------------------------------------------------------------

SQRT3 = math.sqrt(3.0)


def hex_cell(x, y, size=3.6):
    """The hexagonal cell of a lattice of `size` pixels round a point (MINERS's dark red rock is laid with
    such cells): (its bump, 1 in the cell's middle falling to 0 at its rim, and the cell's id)."""
    row_h = size * SQRT3 / 2
    j0 = int(math.floor(y / row_h))
    best = None
    for j in (j0 - 1, j0, j0 + 1, j0 + 2):
        off = (size / 2) if j % 2 else 0.0
        i0 = int(math.floor((x - off) / size))
        for i in (i0 - 1, i0, i0 + 1, i0 + 2):
            cx, cy = i * size + off, j * row_h
            d = math.hypot(x - cx, y - cy)
            if best is None or d < best[0]:
                best = (d, (i, j))
    d, cell = best
    bump = max(0.0, 1.0 - (d / (size * 0.62)) ** 2)
    return bump, cell


def cell_jitter(cell, seed=7):
    """A steady pseudo-random number in -1..1 for a cell."""
    h = (cell[0] * 73856093) ^ (cell[1] * 19349663) ^ (seed * 83492791)
    return ((h & 0xffff) / 0xffff) * 2.0 - 1.0


def hex_rock_paint(obj, shade_at, mats, size=3.6, seed=7, groove_drop=1.6, wall_drop=1.0):
    """Paints a hex rock part: each face the band of shade_at(x, y), moved by its cell's jitter, darker in the
    grooves between the cells and on steep faces; mats [(shade, material)] dark to light."""
    def pick(c, nrm):
        if nrm.z < -0.5:
            return mats[0][1]
        bump, cell = hex_cell(c.x, c.y, size)
        v = shade_at(c.x, c.y) + 0.8 * cell_jitter(cell, seed)
        if bump < 0.25:
            v -= groove_drop
        if abs(nrm.z) < 0.4:
            v -= wall_drop
        return nearest_band(mats, v)
    return paint_faces(obj, pick)


def lava_rock_mats(prefix):
    """The dark red rock's shades (ramp 7, dull: it does not glow)."""
    return bands(prefix, 7, (1, 2, 3, 4, 5, 6, 7), metallic=0.05, roughness=0.75)


def mirror_y_copies(objects, axis_y=0.0, suffix="_y"):
    """Mirrored copies of objects across y = axis_y (the originals kept)."""
    out = []
    m = Matrix.Translation((0, axis_y, 0)) @ Matrix.Scale(-1, 4, (0, 1, 0)) @ Matrix.Translation((0, -axis_y, 0))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)
        c = obj.copy()
        c.data = obj.data.copy()
        c.name = obj.name + suffix
        bpy.context.scene.collection.objects.link(c)
        c.data.transform(m)
        c.data.flip_normals()
        out.append(c)
    return out
