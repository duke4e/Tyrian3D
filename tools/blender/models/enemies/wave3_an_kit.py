"""Helpers for the batch AN models of wave 3 (sheet n, written n in models.cfg: GYGES' maw boss, its damaged look,
its pincers and the blue bubbles; wave3_an_boss.py, the boss; wave3_an.py, the rest): the sprites' pixels
(wave3_an_art.py), and the kits of batches AG and AK (wave3_ag_kit, wave3_ak_kit: pixel frames, painting faces by the
sprite's pixel under them, heightfield parts, relief by the sprite's brightness, broken ends, soot, dents, debris;
whole objects cut into their sprites' pieces, the silhouette check and the build loop), with a few helpers of their
own: soft unions of blobs (organic masses), parts inflated from the pixels of one region, cones (teeth, horns).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

import bpy
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
import wave3_aj_kit as aj  # noqa: E402,F401
import wave3_ak_kit as akk  # noqa: E402,F401
import wave3_an_art as art  # noqa: E402,F401
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
patched = akk.patched
dent = akk.dent
debris = akk.debris
pipe = akk.pipe
smin = aj.smin
smax = aj.smax


def frame(name, width, origin):
    """A Frame of one of wave3_an_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def blob(x, y, cx, cy, rx, ry, top, power=2.0):
    """The height of an ellipsoidal blob centred (cx, cy) with radii rx, ry and height `top` at (x, y) (0 outside):
    power > 2 flattens its crown."""
    d = (abs(x - cx) / rx) ** power + (abs(y - cy) / ry) ** power
    if d >= 1.0:
        return 0.0
    return top * (1.0 - d) ** (1.0 / power)


def soft_union(values, r=3.0):
    """The smooth maximum of several heights (blobs melting into each other)."""
    out = 0.0
    for val in values:
        out = smax(out, val, r) if out > 0.0 else val
    return out


def inflated(name, polys, mat, height, aspect=0.9, spacing=0.5, base=0.0, z_fn=None, min_height=0.4):
    """A rounded part filling the polygons (a flat bottom at `base`): thin stretches round like tubes, wide ones
    capped at `height`; z_fn(x, y, z) -> z reshapes its top."""
    obj = sh.inflate(name, polys, mat, sh.round_profile(aspect, height, min_height), bottom=0.0, base=base, rim=0.0,
                     spacing=spacing, z_fn=z_fn, sigma=1.0)
    return k.smooth(obj, 55)


def draped(name, polys, mat, height, surf, sink=0.8, aspect=0.9, spacing=0.5, under=0.6, min_height=0.4):
    """A rounded part lying on a surface (surf(x, y) -> its height): a lens filling the polygons, its top raised by
    a round profile capped at `height`, its underside `under` times as deep, the whole moved onto the surface and
    sunk `sink` into it, so that it hugs slopes without walls."""
    obj = sh.inflate(name, polys, mat, sh.round_profile(aspect, height, min_height), bottom=under, base=0.0, rim=0.0,
                     spacing=spacing, sigma=1.0)
    displace_z(obj, lambda x, y, z: surf(x, y) - sink)
    return k.smooth(obj, 55)


def cone(name, base, tip, radius, mat, segments=12, squash=1.0, bulge=0.25, tip_radius=0.12):
    """A curved horn from `base` to `tip` (3D points), `radius` at its foot: its section swelling a little near the
    foot (bulge), tapering to a rounded point."""
    b, t = Vector(base), Vector(tip)
    length = (t - b).length
    prof = []
    steps = 10
    for i in range(steps + 1):
        s = i / steps
        r = radius * (1.0 - s) ** 0.85 * (1.0 + bulge * math.sin(math.pi * min(1.0, s * 1.6)))
        prof.append((s * length, max(tip_radius, r)))
    return lathe_axis(name, prof, mat, tuple(b), tuple(t - b), segments, squash=squash, smooth_angle=60)


def paint(obj, f, p, walls=-2, probe=-0.5, grid=False, default=None, under=None, merge=True):
    """Paints a part by the pixels under it (its underside one dark colour); grid: its faces cut along the pixel
    grid first (exact pixels on its top); merge: flat stretches of one colour merged into few triangles."""
    if grid:
        pixelate(obj, f, step=1.0)
    paint_sprite(obj, f, p, wall_steps=walls, probe=probe, under=under if under is not None else p(0x01),
                 default=default if default is not None else p(0x02))
    delete_faces(obj, lambda c, nrm: nrm.z < -0.95)
    if merge:
        merge_flat(obj, angle=1.0)
    return obj


def region(f, keep, smooth=2, min_area=1.0, grow=0.0):
    """The outlines of the pixels keep(index, column, row) accepts."""
    return polys_of(f, lambda val, c, r: val is not None and keep(val, c, r), smooth=smooth,
                    epsilon=0.3 if smooth < 2 else 0.4, min_area=min_area, grow=grow)


def filled(f, inside):
    """A copy of frame f whose transparent pixels inside(c, r) accepts take their nearest opaque neighbour's
    index (holes and slits in a sprite closed)."""
    out = Frame.__new__(Frame)
    out.__dict__.update(f.__dict__)
    out._shades = {}
    g = [row[:] for row in f.g]
    changed = True
    while changed:
        changed = False
        new = [row[:] for row in g]
        for r in range(f.height):
            for c in range(f.width):
                if g[r][c] is not None or not inside(c, r):
                    continue
                near = [g[rr][cc] for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                        if 0 <= rr < f.height and 0 <= cc < f.width and g[rr][cc] is not None]
                if near:
                    new[r][c] = min(near, key=lambda val: val & 15)
                    changed = True
        g = new
    out.g = g
    return out


def emboss_z(obj, field, amount, min_nz=0.3):
    """Relief following the sprite (bright raised, dark sunk), straight up and down: the vertices of faces looking
    up (normal z over min_nz) moved by amount * field(x, y), faded towards steep flanks. Unlike emboss, the
    vertices keep their x and y (parts sampled on the pixel grid stay on it)."""
    sh.apply_modifiers(obj)
    obj.data.update()
    moves = []
    for vt in obj.data.vertices:
        nz = vt.normal.z
        moves.append(0.0 if nz <= min_nz else amount * field(vt.co.x, vt.co.y) * smoothstep(min_nz, min_nz + 0.35, nz))
    for vt, dz in zip(obj.data.vertices, moves):
        vt.co.z += dz
    obj.data.update()
    return obj


def wobble(obj, amount, scale=1.4, seed=0.0, min_z=0.3):
    """Organic unevenness: the vertices above min_z pushed up or down by noise."""
    sh.apply_modifiers(obj)
    off = Vector((seed * 3.3, seed * 1.9, seed * 2.7))
    for vt in obj.data.vertices:
        if vt.co.z > min_z:
            vt.co.z += amount * noise.noise(Vector((vt.co.x, vt.co.y, 0.0)) / scale + off)
    obj.data.update()
    return obj
