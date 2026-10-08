"""Helpers for the batch S models of wave 3 (sheet F: SAVARA, SAVARA IV, SAVARA V, SAVARA Y and TORM;
wave3_s.py, the gun silo and the two green jets; wave3_s_boss.py, SAVARA's boss): the sprites' pixels
(wave3_s_art.py), pixel frames for objects the game draws in pieces, bevelled slabs and prisms, painting
faces with the colour of the sprite's pixel under them, mirroring, and the build loop of batch N
(wave3_n_kit: stand-alone models and whole objects cut into their sprites' pieces, the silhouette
check against the pixels).

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
import wave3_s_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, part, lathe_axis, tube, catmull, sphere,  # noqa: E402,F401
                         rounded_box, block, meshes, bake, simplify_bottom, decimate, sampler)

F = "enemy_F"
model = n.model
pieced = n.pieced
run = n.run


# --- Pixel frames ----------------------------------------------------------------------------------

class Frame:
    """An art grid and its origin: pixel columns and rows to model coordinates."""

    def __init__(self, text, width, origin):
        self.g = grid(text, width)
        self.width = width
        self.ox, self.oy = origin

    def X(self, col):
        """A pixel column's centre (fractions allowed)."""
        return col + 0.5 - self.ox

    def Y(self, row):
        return self.oy - (row + 0.5)

    def left(self, col):
        return col - self.ox

    def right(self, col):
        return col + 1 - self.ox

    def top(self, row):
        return self.oy - row

    def bottom(self, row):
        return self.oy - row - 1

    def rect(self, c0, c1, r0, r1, inset=0.0):
        """The pixels c0..c1, r0..r1 (inclusive) as a polygon, counter-clockwise, moved in by inset."""
        x0, x1 = self.left(c0) + inset, self.right(c1) - inset
        y0, y1 = self.bottom(r1) + inset, self.top(r0) - inset
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def at(self, x, y):
        """The palette index under a point (None: transparent or outside)."""
        c, r = int(math.floor(x + self.ox)), int(math.floor(self.oy - y))
        if 0 <= r < len(self.g) and 0 <= c < self.width:
            return self.g[r][c]
        return None

    def mask(self, box=None):
        """Coverage for the silhouette check: box (c0, c1, r0, r1), end exclusive."""
        return n.art_mask(self.g, box)

    def shade(self, ramp, blur=1):
        """A function (x, y) -> the shade of the ramp's pixels there, smoothed (wave3_j_kit.sampler)."""
        if not hasattr(self, "_shades"):
            self._shades = {}
        key = (ramp, blur)
        if key not in self._shades:
            self._shades[key] = sampler(self.g, (self.ox, self.oy), value=lambda v: v & 15, blur=blur,
                                        keep=lambda v: v is not None and v >> 4 == ramp)
        return self._shades[key]

    def fill(self, outline, edge_only=True):
        """Replaces the outline pixels (indices in `outline`; with edge_only, only those next to the
        transparent outside) by their nearest other pixel, so that the model's surfaces take the colour
        inside the outline (its edges are shaded by the light)."""
        from collections import deque
        h = len(self.g)

        def is_outline(r, c):
            if self.g[r][c] not in outline:
                return False
            if not edge_only:
                return True
            return any(not (0 <= r + dr < h and 0 <= c + dc < self.width) or self.g[r + dr][c + dc] is None
                       for dr in (-1, 0, 1) for dc in (-1, 0, 1))
        out = [row[:] for row in self.g]
        queue = deque((r, c) for r in range(h) for c in range(self.width)
                      if self.g[r][c] is not None and not is_outline(r, c))
        seen = set(queue)
        while queue:
            r, c = queue.popleft()
            for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= rr < h and 0 <= cc < self.width and (rr, cc) not in seen and self.g[rr][cc] is not None:
                    seen.add((rr, cc))
                    out[rr][cc] = out[r][c]
                    queue.append((rr, cc))
        self.g = out
        self._shades = {}
        return self


# --- Shapes ----------------------------------------------------------------------------------------

def slab(name, poly, z0, z1, mat, bevel=0.4, segments=2, z_fn=None, angle=40):
    """The polygon [(x, y)] extruded from z0 to z1, its edges bevelled; z_fn(x, y, z) -> z reshapes it."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    obj = k.slab(name, poly if area > 0 else poly[::-1], z0, z1, mat, bevel_width=bevel, bevel_segments=segments)
    sh.apply_modifiers(obj)
    if z_fn is not None:
        for v in obj.data.vertices:
            v.co.z = z_fn(v.co.x, v.co.y, v.co.z)
    return k.smooth(obj, angle)


def prism_x(name, profile, x0, x1, mat, bevel=0.4, segments=2, angle=40):
    """A part with the cross-section profile [(y, z)] (counter-clockwise seen from +x), running from
    x0 to x1: blocks with sloped faces (glacis, ramps)."""
    area = sum(profile[i][0] * profile[(i + 1) % len(profile)][1] - profile[(i + 1) % len(profile)][0] * profile[i][1]
               for i in range(len(profile)))
    obj = k.slab(name, profile if area > 0 else profile[::-1], x0, x1, mat, bevel_width=bevel,
                 bevel_segments=segments)
    sh.apply_modifiers(obj)
    # Built with (y, z) in the XY plane and x along Z: turn (a, b, c) into (c, a, b).
    obj.data.transform(Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    k.recalc_normals(obj)
    return k.smooth(obj, angle)


def prism_y(name, profile, y0, y1, mat, bevel=0.4, segments=2, angle=40):
    """A part with the cross-section profile [(x, z)] (counter-clockwise seen from -y), running from
    y0 to y1."""
    area = sum(profile[i][0] * profile[(i + 1) % len(profile)][1] - profile[(i + 1) % len(profile)][0] * profile[i][1]
               for i in range(len(profile)))
    obj = k.slab(name, profile if area > 0 else profile[::-1], y0, y1, mat, bevel_width=bevel,
                 bevel_segments=segments)
    sh.apply_modifiers(obj)
    # (a, b, c) -> (a, c, b) mirrors; flip the normals back.
    obj.data.transform(Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    obj.data.flip_normals()
    k.recalc_normals(obj)
    return k.smooth(obj, angle)


def lathe_y(name, profile, mat, x, z, segments=24, squash=1.0, angle=50, direction=(0, -1, 0)):
    """A turned part along an axis through (x, profile start, z): profile [(y, radius)] where y is the
    distance along `direction` from y = 0 (default: down the screen)."""
    return lathe_axis(name, profile, mat, (x, 0.0, z), direction, segments, squash, angle)


def lift(obj, dz):
    obj.data.transform(Matrix.Translation((0, 0, dz)))
    return obj


def mirror_copies(objects, axis_x=0.0, suffix="_m"):
    """Mirrored copies of objects across x = axis_x (the originals kept)."""
    out = []
    m = Matrix.Translation((axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-axis_x, 0, 0))
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


# --- Painting by the sprite -------------------------------------------------------------------------

class Painter:
    """Materials for a sprite's palette indices: palette materials named <prefix>_<index>, an index's
    shade snapped to the nearest of the shades allowed for its ramp (fewer materials)."""

    def __init__(self, prefix, shades=None, metallic=0.4, roughness=0.4, glow=None, finish=None, remap=None):
        self.prefix = prefix
        self.remap = remap or {}         # index -> index (outline pixels to a body colour)
        self.shades = shades or {}
        self.metallic, self.roughness = metallic, roughness
        self.glow = glow or {}           # index -> emission strength
        self.finish = finish or {}       # ramp -> (metallic, roughness)
        self.cache = {}

    def snap(self, index):
        index = self.remap.get(index, index)
        ramp, shade = index >> 4, index & 15
        allowed = self.shades.get(ramp)
        if allowed:
            shade = min(allowed, key=lambda s: abs(s - shade))
        return ramp * 16 + shade

    def __call__(self, index):
        index = self.snap(index)
        if index not in self.cache:
            metallic, roughness = self.finish.get(index >> 4, (self.metallic, self.roughness))
            if index >> 4 == 0 and (index & 15) <= 2:  # black stays black: little reflection
                metallic, roughness = 0.15, 0.75
            self.cache[index] = pal(f"{self.prefix}_{index:02x}", index, metallic=metallic, roughness=roughness,
                                    glow=self.glow.get(index))
        return self.cache[index]

    def darker(self, index, steps=2):
        index = self.remap.get(index, index)
        ramp, shade = index >> 4, index & 15
        return self(ramp * 16 + max(1 if ramp == 0 else 0, shade - steps))


def paint_sprite(obj, frame, painter, wall_steps=2, under=None, default=None, keep=None, probe=0.0, offset=(0.0, 0.0),
                 blur=0, shade_shift=0.0):
    """Gives each face the colour of the sprite's pixel under its centre (painter: index -> material):
    walls (steep faces) take it `wall_steps` shades darker, faces looking down `under`; where the
    sprite is transparent, `default` (None: keep). keep(index) -> False leaves a face as it is.
    probe: walls sample that far out along their normal (their outline pixels). blur > 0 takes the
    shade of the pixel's ramp smoothed that many times (less pixel noise), shifted by shade_shift."""
    dx, dy = offset

    def pick(c, nrm):
        if nrm.z < -0.5:
            return under
        x, y = c.x + dx, c.y + dy
        wall = abs(nrm.z) < 0.45
        if wall and probe:
            x += nrm.x * probe
            y += nrm.y * probe
        index = frame.at(x, y)
        if index is None:
            return default
        if keep is not None and not keep(index):
            return None
        if blur:
            ramp = index >> 4
            shade = int(round(frame.shade(ramp, blur)(x, y) + shade_shift))
            index = ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade))
        return painter.darker(index, wall_steps) if wall else painter(index)
    return paint_faces(obj, pick)


def pixelate(obj, frame, step=1.0, box=None):
    """Cuts obj's faces along the pixel grid (every `step` pixels in x and y, within box (x0, x1, y0, y1)
    or the object's extent), so that painting by the sprite follows its pixels."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.verts:
        bm.free()
        return obj
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    x0, x1, y0, y1 = box or (min(xs), max(xs), min(ys), max(ys))
    fx, fy = frame.ox % 1.0, frame.oy % 1.0
    for axis, lo, hi, frac in ((0, x0, x1, fx), (1, y0, y1, fy)):
        v = math.floor((lo + frac) / step) * step - frac
        while v <= hi:
            if lo + 1e-4 < v < hi - 1e-4:
                co = (v, 0, 0) if axis == 0 else (0, v, 0)
                no = (1, 0, 0) if axis == 0 else (0, 1, 0)
                geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
                bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
            v += step
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def merge_flat(obj, angle=1.0):
    """Merges flat stretches of faces that share a material into few triangles (after painting)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    ngons = [f for f in bm.faces if len(f.verts) > 3]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def paint_pixels(obj, frame, painter, merge=True, **kw):
    """pixelate, paint_sprite and merge_flat in one."""
    pixelate(obj, frame)
    paint_sprite(obj, frame, painter, **kw)
    if merge:
        merge_flat(obj)
    return obj


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)
