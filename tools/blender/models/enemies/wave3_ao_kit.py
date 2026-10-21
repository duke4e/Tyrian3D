"""Helpers for batch AO of wave 3: the damaged looks (and wrecks) of objects earlier batches modelled, built by the
earlier scripts' own builders and damaged as the damaged sprites show (burnt, dented, broken), cut into the same
pieces so that each swaps in place when the game switches an enemy to its damaged sprite (the enemy data's dgr).
The script: wave3_ao_works.py (sheet P: the cargo pod, the drilling rig's crane, the tan launcher, the small block;
and the stone face's right half). The damaged sprites' pixels are in wave3_ao_art.py. (SAVARA's airship damaged,
the tusked boss's, the bronze pump's dome's and DELI's tower's, the gun on its mast's and the long cannons' damaged
looks: polish_*.py.)

The earlier scripts are imported as they are (quiet_import: their build loops, run on import by some of them,
build nothing), so that their output stays unchanged; their registered models are then forgotten (forget) and
the damaged ones registered in their place.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera); the origin
is the whole object's centre. Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 -
ox, y = oy - r - 1 .. oy - r.
"""
import importlib
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_ao_art as art  # noqa: E402,F401
from wave3_j_kit import pal, paint_faces, sphere, rounded_box, tube, meshes, bake, sampler, triangles  # noqa: E402,F401
from wave3_s_kit import Frame, Painter, paint_sprite, pixelate, merge_flat  # noqa: E402,F401


# --- The earlier scripts ------------------------------------------------------------------------------------

def quiet_import(name):
    """Imports an earlier model script without letting its build loop build anything (some run it on import):
    the command line is replaced by one that asks for no model while it loads."""
    saved = sys.argv
    sys.argv = [saved[0], "--", "--only", "__none__"]
    try:
        return importlib.import_module(name)
    finally:
        sys.argv = saved


def forget():
    """Drops what the imported scripts registered with the build loops (their intact models)."""
    del n.MODELS[:]
    del n.OBJECTS[:]
    del w.MODELS[:]
    w.WHOLES.clear()


def run():
    """Builds what this batch registered: wave3_n_kit's loop (models, whole objects cut into pieces), then
    wave3_j_kit's (models registered there)."""
    if n.MODELS or n.OBJECTS:
        n.run()
    if w.MODELS or w.WHOLES:
        w.run()


# --- Pixels ----------------------------------------------------------------------------------------------------

def frame(name, width, origin):
    """A wave3_s_kit Frame of one of wave3_ao_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def diff_grid(fi, fd, test=lambda dv, iv: dv != iv):
    """A grid of 1.0 where test(damaged pixel, intact pixel) holds, 0.0 elsewhere in the damaged frame's
    extent (None where both are transparent)."""
    h = max(len(fi.g), len(fd.g))
    out = []
    for r in range(h):
        row = []
        for c in range(fi.width):
            iv = fi.g[r][c] if r < len(fi.g) else None
            dv = fd.g[r][c] if r < len(fd.g) else None
            if iv is None and dv is None:
                row.append(None)
            else:
                row.append(1.0 if test(dv, iv) else 0.0)
        out.append(row)
    return out


def field(fi, fd, test, blur=1):
    """(x, y) -> 0..1: where test(damaged pixel, intact pixel) holds, smoothed `blur` times."""
    g = diff_grid(fi, fd, test)
    return sampler(g, (fi.ox, fi.oy), value=lambda v: v, blur=blur, keep=lambda v: v is not None)


def is_dark(v):
    """Black and the darkest greys (holes, soot)."""
    return v is not None and v >> 4 == 0 and (v & 15) <= 2


def is_hot(v):
    """The reds of embers."""
    return v is not None and v >> 4 == 7


def patched(base, top, keep=lambda c, r: True):
    """A copy of frame `base` whose pixels are those of frame `top` where they differ and keep(c, r) (the
    damaged look painted over the intact paint frame); transparent pixels of `top` keep base's."""
    out = Frame.__new__(Frame)
    out.__dict__.update(base.__dict__)
    out._shades = {}
    out.g = [row[:] for row in base.g]
    for r in range(min(len(base.g), len(top.g))):
        for c in range(base.width):
            t = top.g[r][c]
            if t is not None and t != base.g[r][c] and keep(c, r):
                out.g[r][c] = t
    return out


def damage_box(fi, fd, test=lambda dv, iv: dv != iv, grow=1.0):
    """The box (x0, x1, y0, y1) round the pixels where the damaged frame differs."""
    cells = [(c, r) for r in range(min(len(fi.g), len(fd.g))) for c in range(fi.width)
             if test(fd.g[r][c], fi.g[r][c])]
    if not cells:
        return None
    c0, c1 = min(c for c, _ in cells), max(c for c, _ in cells)
    r0, r1 = min(r for _, r in cells), max(r for _, r in cells)
    return (fi.left(c0) - grow, fi.right(c1) + grow, fi.bottom(r1) - grow, fi.top(r0) + grow)


# --- Damage -------------------------------------------------------------------------------------------------

def hot_painter(prefix, shades, metallic=0.4, roughness=0.45, finish=None, remap=None, ember=1.0):
    """A Painter whose reds (ramp 7) glow, brighter the lighter they are: embers."""
    glow = {0x70 + i: ember * (0.25 + 0.2 * i) for i in range(16)}
    sh_ = dict(shades)
    sh_.setdefault(7, (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc))
    fin = dict(finish or {})
    fin.setdefault(7, (0.0, 0.5))
    return Painter(prefix, shades=sh_, metallic=metallic, roughness=roughness, glow=glow, finish=fin, remap=remap)


def sink(obj, fld, depth, mode="z", min_z=None, seed=0.0, roughness=0.35, scale=1.4, box=None):
    """Pushes the part's vertices in where fld(x, y) (0..1) says, by up to `depth`, unevenly (noise): dents and
    craters in plating. mode "z": straight down; "normal": in along the vertex normal (round parts)."""
    sh.apply_modifiers(obj)
    off = Vector((seed * 3.7, seed * 1.3, seed * 2.1))
    obj.data.update()
    normals = [vt.normal.copy() for vt in obj.data.vertices]  # before any vertex moves
    for vt, nv in zip(obj.data.vertices, normals):
        if min_z is not None and vt.co.z < min_z:
            continue
        if box is not None and not (box[0] <= vt.co.x <= box[1] and box[2] <= vt.co.y <= box[3]):
            continue
        f = fld(vt.co.x, vt.co.y)
        if f <= 0.02:
            continue
        nz = 1.0 + roughness * max(-1.0, min(1.0, noise.noise(vt.co / scale + off)))
        d = depth * f * nz
        if mode == "normal":
            vt.co -= nv * d
        else:
            vt.co.z -= d
    obj.data.update()
    return obj


def repaint(obj, fi, fd, painter, walls=2, under=None, test=lambda dv, iv: dv != iv, probe=0.0, pixel=True,
            box=None, min_nz=-0.5, merge=True, blur=0, default=None):
    """Paints the faces of a part lying over the pixels where the damaged frame differs from the intact one
    (test) with the damaged pixel's colour (walls `walls` shades darker), cutting its faces along the pixel grid
    there first (pixel), so that the soot, holes and embers sit where the damaged sprite draws them. blur > 0
    takes the shade of the pixel's ramp smoothed that many times (less speckle); default: the material of the
    part's other faces (None: they keep theirs)."""
    sh.apply_modifiers(obj)
    if pixel:
        b = box or damage_box(fi, fd, test)
        if b is None:
            return obj
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        if not xs or max(xs) < b[0] or min(xs) > b[1] or max(ys) < b[2] or min(ys) > b[3]:
            return obj
        pixelate(obj, fi, 1.0, (max(b[0], min(xs)), min(b[1], max(xs)), max(b[2], min(ys)), min(b[3], max(ys))))

    def pick(c, nrm):
        if nrm.z < min_nz:
            return under
        x, y = c.x, c.y
        wall = abs(nrm.z) < 0.45
        if wall and probe:
            x += nrm.x * probe
            y += nrm.y * probe
        col, row = int(math.floor(x + fi.ox)), int(math.floor(fi.oy - y))
        if not (0 <= row < min(len(fi.g), len(fd.g)) and 0 <= col < fi.width):
            return default
        dv, iv = fd.g[row][col], fi.g[row][col]
        if dv is None or not test(dv, iv):
            return default
        if blur and not is_hot(dv) and not is_dark(dv):
            ramp = dv >> 4
            shade = int(round(fd.shade(ramp, blur)(x, y)))
            dv = ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade))
        return painter.darker(dv, walls) if wall else painter(dv)
    paint_faces(obj, pick)
    if merge:
        merge_flat(obj)
    return obj


def delete_over(obj, fn, min_nz=None):
    """Deletes the faces whose centre (x, y, z) fn accepts (fn(centre, normal))."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    doomed = [f for f in bm.faces if fn(f.calc_center_median(), f.normal) and (min_nz is None or f.normal.z >= min_nz)]
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def jag(obj, axis_point, direction, depth, scale=0.9, seed=0.0):
    """Breaks a part's end: the vertices within `depth` of its end along `direction` (the end at axis_point)
    pulled back by noise, so that the end looks snapped off rather than cut (as wave3_ag_kit.jag)."""
    sh.apply_modifiers(obj)
    d = Vector(direction).normalized()
    p0 = Vector(axis_point)
    off = Vector((seed * 5.3, seed * 2.9, seed * 7.1))
    for vt in obj.data.vertices:
        t = (vt.co - p0).dot(d)
        if t > -depth:
            pull = (0.5 + 0.5 * noise.noise(vt.co / scale + off)) * depth
            a = min(1.0, max(0.0, (t + depth) / depth))
            vt.co -= d * pull * a * a * (3 - 2 * a)
    obj.data.update()
    return obj


def cut_plane(obj, point, normal, keep_side=-1, cap=True):
    """Cuts a part at a plane, keeping the side the normal points away from (keep_side -1) or towards (+1), the
    cut closed (cap)."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    no = Vector(normal).normalized()
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=Vector(point),
                                 plane_no=no, clear_inner=keep_side > 0, clear_outer=keep_side < 0)
    if cap:
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if edges:
            try:
                bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            except Exception:  # noqa: BLE001 (left open)
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def debris(name, points, mat, size=(1.2, 2.4), seed=3, flat=0.4):
    """Small twisted plates and chunks at points [(x, y, z)]: wreckage."""
    rnd = random.Random(seed)
    parts = []
    for i, (x, y, z) in enumerate(points):
        sz = rnd.uniform(*size)
        obj = rounded_box(f"{name}{i}", (0.0, 0.0, 0.0),
                          (sz, sz * rnd.uniform(0.4, 0.9), sz * rnd.uniform(0.6 * flat, flat)), mat, bevel=0.15,
                          segments=1)
        sh.apply_modifiers(obj)
        rot = (Matrix.Rotation(rnd.uniform(0, 6.3), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.8, 0.8), 4, "X") @
               Matrix.Rotation(rnd.uniform(-0.8, 0.8), 4, "Y"))
        obj.data.transform(Matrix.Translation((x, y, z)) @ rot)
        parts.append(obj)
    return parts


def scatter(fld, box, count, spacing, threshold=0.5, seed=5, tries=4000):
    """Points (x, y) in box where fld(x, y) > threshold, at least `spacing` apart."""
    rnd = random.Random(seed)
    pts = []
    for _ in range(tries):
        if len(pts) >= count:
            break
        x, y = rnd.uniform(box[0], box[1]), rnd.uniform(box[2], box[3])
        if fld(x, y) <= threshold or any(math.hypot(x - a, y - b) < spacing for a, b in pts):
            continue
        pts.append((x, y))
    return pts


def surface_z(objects, x, y, default=0.0, above=200.0):
    """The highest point of the objects' surfaces over (x, y) (a ray cast down)."""
    best = None
    for obj in objects:
        ok, loc, _, _ = obj.ray_cast(Vector((x, y, above)), Vector((0.0, 0.0, -1.0)))
        if ok and (best is None or loc.z > best):
            best = loc.z
    return default if best is None else best


def find(prefix):
    """The scene's meshes whose names start with prefix."""
    return [o for o in meshes() if o.name.startswith(prefix)]


def removed(fi, fd):
    """(x, y) -> whether the damaged frame leaves out a pixel the intact one draws there."""
    def at(x, y):
        c, r = int(math.floor(x + fi.ox)), int(math.floor(fi.oy - y))
        if 0 <= r < min(len(fi.g), len(fd.g)) and 0 <= c < fi.width:
            return fi.g[r][c] is not None and fd.g[r][c] is None
        return False
    return at


def wreck(objects, fi, fd, painter, box, walls=2, blur=0, keep_floor="floor", delete=True,
          test=lambda dv, iv: dv != iv):
    """Damages the parts within box (x0, x1, y0, y1) as the damaged frame draws them: their faces cut along the
    pixel grid there, the faces over pixels it leaves out deleted (broken off; delete), those over pixels it
    draws differently painted its colours (soot, burns, embers). Parts whose names contain keep_floor are left."""
    gone = removed(fi, fd)
    for obj in objects:
        if keep_floor and keep_floor in obj.name:
            continue
        sh.apply_modifiers(obj)
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        if not xs or max(xs) < box[0] or min(xs) > box[1] or max(ys) < box[2] or min(ys) > box[3]:
            continue
        pixelate(obj, fi, 1.0, (max(box[0], min(xs)), min(box[1], max(xs)), max(box[2], min(ys)), min(box[3], max(ys))))
        if delete:
            delete_over(obj, lambda c, nrm: box[0] <= c.x <= box[1] and box[2] <= c.y <= box[3] and gone(c.x, c.y))
        repaint(obj, fi, fd, painter, walls=walls, pixel=False, blur=blur, test=test)
        if not obj.data.polygons:
            bpy.data.objects.remove(obj)
