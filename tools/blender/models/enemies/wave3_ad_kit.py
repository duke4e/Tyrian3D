"""Helpers for the batch AD models of wave 3 (sheet H: GYGES, TORM and BONUS; wave3_ad.py, GYGES' bronze worm
and its small flying parts; wave3_ad_wall.py, GYGES' creatures in their pieces of tube wall; wave3_ad_fall.py,
the waterfall of TORM and BONUS; TORM's beetle is polish_torm_beetle.py's): the sprites' pixels (wave3_ad_art.py),
and the parts, painting and build loop of batch AA (wave3_aa_kit: pixel frames, reliefs, painting faces by
the sprite's pixel under them, stand-alone models and whole objects cut into their sprites' pieces), with a
few of its own: heightfield slabs over a box, lofted paths and GYGES' tube wall.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
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


def luminance(index):
    r, g, b = k.level_palette()[index]
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255.0


# --- Heightfield slabs -----------------------------------------------------------------------------

def field_slab(name, x0, x1, y0, y1, z_top, mat, step=(0.5, 0.5), base=0.0, smooth_angle=40):
    """A slab over the box x0..x1, y0..y1: its top a grid (step (x, y)) at z_top(x, y), straight sides down
    to `base` and a flat bottom; each quad split along its flatter diagonal."""
    sx, sy = step
    nx, ny = max(1, int(round((x1 - x0) / sx))), max(1, int(round((y1 - y0) / sy)))
    bm = bmesh.new()
    rows = []
    for j in range(ny + 1):
        y = y0 + (y1 - y0) * j / ny
        rows.append([bm.verts.new((x0 + (x1 - x0) * i / nx, y, z_top(x0 + (x1 - x0) * i / nx, y))) for i in range(nx + 1)])
    for j in range(ny):
        for i in range(nx):
            a, b, c, d = rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]
            if abs(a.co.z - c.co.z) <= abs(b.co.z - d.co.z):
                bm.faces.new((a, b, c))
                bm.faces.new((a, c, d))
            else:
                bm.faces.new((a, b, d))
                bm.faces.new((b, c, d))
    ring = [rows[0][i] for i in range(nx + 1)] + [rows[j][nx] for j in range(1, ny + 1)] + \
           [rows[ny][i] for i in range(nx - 1, -1, -1)] + [rows[j][0] for j in range(ny - 1, 0, -1)]
    low = [bm.verts.new((p.co.x, p.co.y, base)) for p in ring]
    count = len(ring)
    for i in range(count):
        bm.faces.new((ring[(i + 1) % count], ring[i], low[i], low[(i + 1) % count]))
    bm.faces.new(low[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return k.smooth(obj, smooth_angle)


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


# --- GYGES' tube wall --------------------------------------------------------------------------------

def tube_wall(name, f, box, height=2.6, relief=2.2, step=0.5, blur=1, prefix="wall"):
    """The wall of grey-blue tubes GYGES' sprites draw behind their creatures (palette ramp 6), as a slab over
    the box (x0, x1, y0, y1): its top raised where the tubes are light and sunk in the dark gaps between
    them, painted by the sprite's shades (where a creature hides the wall, by the nearest wall pixels)."""
    shade = sampler(f.g, (f.ox, f.oy), value=lambda v: v & 15, blur=blur,
                    keep=lambda v: v is not None and v >> 4 == 6)
    known = [v & 15 for row in f.g for v in row if v is not None and v >> 4 == 6]
    lo = sorted(known)[len(known) // 10] if known else 1
    hi = sorted(known)[len(known) * 9 // 10] if known else 8
    span = max(1.0, hi - lo)

    shadow = sampler(f.g, (f.ox, f.oy), value=lambda v: 1.0 if v in (0x00, 0x01) else 0.0, blur=1,
                     keep=lambda v: v is not None)

    def z_top(x, y):
        t = min(1.2, max(-0.2, (shade(x, y) - lo) / span))
        return height + relief * (t - 0.5) - 1.6 * shadow(x, y)
    x0, x1, y0, y1 = box
    slab = field_slab(name, x0, x1, y0, y1, z_top, None, step=(step, step), smooth_angle=50)
    paint = Painter(prefix, shades={6: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb)}, metallic=0.2, roughness=0.5)
    sharp = sampler(f.g, (f.ox, f.oy), value=lambda v: v & 15, blur=0,
                    keep=lambda v: v is not None and v >> 4 == 6)

    def pick(c, nrm):
        s = 0.5 * shade(c.x, c.y) + 0.5 * sharp(c.x, c.y) - 0.8 - 6.0 * shadow(c.x, c.y)
        if abs(nrm.z) < 0.45:
            s -= 1.5
        if nrm.z < -0.5:
            s = 0
        return paint(0x60 + max(0, min(11, int(round(s)))))
    paint_faces(slab, pick)
    return slab
