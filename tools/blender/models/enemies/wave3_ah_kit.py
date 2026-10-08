"""Helpers for the batch AH models of wave 3 (sheet M: the asteroid levels, WINDY, SOH JIN and MINERS; wave3_ah.py,
the blocks and MINERS' roller and tank; wave3_ah_dome.py, the armoured dome of the asteroid levels and its wreck;
wave3_ah_rock.py, MINERS' banded rock column and its wreck; wave3_ah_rig.py, MINERS' drilling rig and its guns,
hatches, torches and drill). The sprites' pixels are in wave3_ah_art.py; the parts come from the earlier batches'
kits (wave3_s_kit: pixel frames, painting by the sprite, slabs and prisms; wave3_q_kit: heightfield parts, rings,
grooves; wave3_j_kit: palette materials, turned parts, tubes, spheres, the tiled floor; wave3_aa_kit: lenses set
into shells; wave3_x_kit: thin floor beds; wave3_z_kit: pieces, noise, assemblies and the build loop of
wave3_n_kit: stand-alone models and whole objects cut into their sprites' pieces, the silhouette check, the
triangle budget).

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
import wave3_q_kit as q  # noqa: E402,F401
import wave3_s_kit as s  # noqa: E402,F401
import wave3_aa_kit as aa  # noqa: E402,F401
import wave3_x_kit as xk  # noqa: E402,F401
import wave3_z_kit as z  # noqa: E402,F401
import wave3_ah_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, lathe_axis, hoop, column, tube, catmull, sphere,  # noqa: E402,F401
                         rounded_box, block, lumpy, meshes, bake, triangles, decimate, sampler)
from wave3_s_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, slab, prism_x, prism_y, lift,  # noqa: E402,F401
                         mirror_copies, smoothstep)
from wave3_z_kit import quarter, move, rotate_about, jitter, field, field_sampler, polys_of  # noqa: E402,F401

M = "enemy_M"
model = n.model
pieced = n.pieced
assembly = z.assembly
run = z.run
check_mask = n.check_mask
torus = q.torus
groove = q.groove
heightfield = q.heightfield
lens = aa.lens


def frame(name, width, origin):
    """A Frame of one of wave3_ah_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


# --- Painting --------------------------------------------------------------------------------------------

class RampPainter:
    """Paints faces by a sprite: each face takes the ramp of the sprite's pixel under its centre (if `ramps`
    accepts it, else `fallback`) and that ramp's shade there, smoothed `blur` times, snapped to `shades` (per
    ramp, or one tuple for all). Walls (steep faces) take `wall` shades less, faces looking down `under` less.
    finish: ramp -> (metallic, roughness); glow: ramp -> emission strength."""

    def __init__(self, prefix, f, ramps=None, fallback=None, shades=None, blur=1, wall=1.5, under=3.0,
                 finish=None, glow=None, metallic=0.4, roughness=0.4, shift=0.0, probe=0.0, where=None):
        self.prefix, self.f = prefix, f
        self.where = where  # where(x, y) -> False: the fallback ramp there, whatever the pixel
        self.ramps = set(ramps) if ramps is not None else None
        self.fallback = fallback
        self.shades = shades or {}
        self.blur, self.wall, self.under, self.shift, self.probe = blur, wall, under, shift, probe
        self.finish = finish or {}
        self.glow = glow or {}
        self.metallic, self.roughness = metallic, roughness
        self.cache = {}

    def material(self, ramp, shade):
        allowed = self.shades.get(ramp) if isinstance(self.shades, dict) else self.shades
        shade = int(round(max(0, min(15, shade))))
        if allowed:
            shade = min(allowed, key=lambda v: abs(v - shade))
        index = ramp * 16 + shade
        if index not in self.cache:
            metallic, roughness = self.finish.get(ramp, (self.metallic, self.roughness))
            self.cache[index] = pal(f"{self.prefix}_{index:02x}", index, metallic=metallic, roughness=roughness,
                                    glow=self.glow.get(ramp))
        return self.cache[index]

    def ramp_at(self, x, y):
        if self.where is not None and not self.where(x, y):
            return self.fallback
        v = self.f.at(x, y)
        if v is not None and (self.ramps is None or v >> 4 in self.ramps):
            return v >> 4
        return self.fallback

    def shade_at(self, ramp, x, y):
        if self.blur:
            return self.f.shade(ramp, self.blur)(x, y)
        v = self.f.at(x, y)
        return (v & 15) if v is not None and v >> 4 == ramp else self.f.shade(ramp, 1)(x, y)

    def __call__(self, obj, shift=None, wall=None):
        extra = self.shift if shift is None else shift
        wall_drop = self.wall if wall is None else wall

        def pick(c, nrm):
            x, y = c.x, c.y
            steep = abs(nrm.z) < 0.45
            if steep and self.probe:
                x += nrm.x * self.probe
                y += nrm.y * self.probe
            ramp = self.ramp_at(x, y)
            if ramp is None:
                return None
            s_ = self.shade_at(ramp, x, y) + extra
            if nrm.z < -0.5:
                s_ -= self.under
            elif steep:
                s_ -= wall_drop
            return self.material(ramp, s_)
        return paint_faces(obj, pick)


def band_paint(obj, prefix, ramp, value, shades, wall=1.5, under=3.0, metallic=0.4, roughness=0.4, glow=None):
    """Paints faces in one ramp, the shade value(x, y) snapped to `shades`."""
    cache = {}

    def mat(sv):
        sv = min(shades, key=lambda v: abs(v - sv))
        if sv not in cache:
            cache[sv] = pal(f"{prefix}_{ramp * 16 + sv:02x}", ramp * 16 + sv, metallic=metallic, roughness=roughness,
                            glow=glow)
        return cache[sv]

    def pick(c, nrm):
        v = value(c.x, c.y)
        if nrm.z < -0.5:
            v -= under
        elif abs(nrm.z) < 0.45:
            v -= wall
        return mat(v)
    return paint_faces(obj, pick)


# --- Shapes ----------------------------------------------------------------------------------------------

def ellipse(cx, cy, rx, ry, count=96, power=2.0):
    """A superellipse as a counter-clockwise polygon."""
    pts = []
    for i in range(count):
        a = 2 * math.pi * i / count
        c, s_ = math.cos(a), math.sin(a)
        pts.append((cx + math.copysign(abs(c) ** (2 / power), c) * rx, cy + math.copysign(abs(s_) ** (2 / power), s_) * ry))
    return pts


def clip_below(obj, z0=0.0):
    """Cuts away what lies below z0 (closing the cut)."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-4, plane_co=(0, 0, z0), plane_no=(0, 0, 1), clear_inner=True)
    cut = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if cut:
        try:
            bmesh.ops.holes_fill(bm, edges=cut, sides=0)
        except Exception:  # noqa: BLE001
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    tri = [f for f in bm.faces if len(f.verts) > 3]
    if tri:
        bmesh.ops.triangulate(bm, faces=tri, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def displace(obj, fn, min_z=None):
    """Moves each vertex (above min_z) by fn(co) -> a Vector offset."""
    sh.apply_modifiers(obj)
    for v in obj.data.vertices:
        if min_z is not None and v.co.z <= min_z:
            continue
        v.co += fn(v.co)
    return obj


def surface_point(surface, x, y, d=0.3):
    """The point of a height function's surface over (x, y) and its normal."""
    zc = surface(x, y)
    dzdx = (surface(x + d, y) - surface(x - d, y)) / (2 * d)
    dzdy = (surface(x, y + d) - surface(x, y - d)) / (2 * d)
    return Vector((x, y, zc)), Vector((-dzdx, -dzdy, 1.0)).normalized()


def on_surface(obj, surface, base=0.0):
    """Lifts a part built on z = 0 onto a height function: each vertex rises by surface(x, y) - base."""
    sh.apply_modifiers(obj)
    for v in obj.data.vertices:
        v.co.z += surface(v.co.x, v.co.y) - base
    return obj


def orient(obj, centre, normal):
    """Turns a part built round the origin with its axis along z so that the axis lies along `normal`, and
    moves it to `centre`."""
    nrm = Vector(normal).normalized()
    rot = nrm.to_track_quat("Z", "Y").to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(centre)) @ rot)
    k.recalc_normals(obj)
    return obj


def ring_on(name, centre, normal, major, minor, mat, scale_y=1.0, squash=1.0, segments=24, sides=8):
    """A ring (torus) lying on a surface at `centre`, its axis along the surface's `normal`."""
    obj = torus(name, (0.0, 0.0, 0.0), major, minor, mat, segments, sides, squash, scale_y)
    sh.apply_modifiers(obj)
    return orient(obj, centre, normal)


def cut_plane(obj, point, normal):
    """Cuts away what lies on the side of a plane its normal points to, closing the cut."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    nrm = Vector(normal).normalized()
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-4, plane_co=point, plane_no=nrm, clear_outer=True)
    cut = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if cut:
        try:
            bmesh.ops.holes_fill(bm, edges=cut, sides=0)
        except Exception:  # noqa: BLE001
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ngons = [f for f in bm.faces if len(f.verts) > 3]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj
