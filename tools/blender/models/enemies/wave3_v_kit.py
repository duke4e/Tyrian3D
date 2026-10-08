"""Helpers for the batch V models of wave 3 (sheet T: DELI's boss in DELI, New Deli and HARVEST, wave3_v.py;
CORAL's sea creatures and machines, wave3_v_sea.py): the sprites' pixels (wave3_v_art.py), pixel frames
for objects the game draws in pieces, reliefs inflated from pixel regions, painting faces with the colour
of the sprite's pixel under them, mirroring, and the build loop of batch N (wave3_n_kit: stand-alone
models and whole objects cut into their sprites' pieces, the silhouette check against the pixels).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys
from collections import deque

import bmesh
import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, regions, paint_faces, lathe_axis, hoop, tube, catmull, sphere,  # noqa: E402,F401
                         rounded_box, block, meshes, bake, decimate, sampler, transform)

model = n.model
pieced = n.pieced


_n_budget = n.budget
PROTECT = []  # name prefixes of parts painted pixel by pixel: the budget decimates the others first


def budget(target=4800, objects=None):
    """wave3_n_kit.budget, but parts whose names (after the piece's prefix) start with one of PROTECT are
    decimated only if the rest cannot make room (decimation smears painted pixels)."""
    objs = objects or meshes()
    for obj in objs:
        sh.apply_modifiers(obj)

    def count(o):
        return sum(len(p.vertices) - 2 for p in o.data.polygons)

    def protected(o):
        name = o.name.split("_", 2)[-1] if o.name.startswith("deli_boss_") else o.name
        return any(name.startswith(p) or p in o.name for p in PROTECT)
    total = sum(count(o) for o in objs)
    if total <= target:
        return total
    keep = [o for o in objs if protected(o)]
    rest = [o for o in objs if not protected(o)]
    fixed = sum(count(o) for o in keep)
    if fixed < target * 0.85 and rest:
        _n_budget(target - fixed, rest)
        total = sum(count(o) for o in objs)
        if total <= target:
            return total
    return _n_budget(target, objs)


def run():
    """wave3_n_kit.run with the budget above; with --stats 1 the parts' triangles before the budget are
    printed too."""
    stats_on = "stats" in k.args()

    def counting(target=4800, objects=None):
        if stats_on:
            for obj in objects or meshes():
                sh.apply_modifiers(obj)
                print(f"   {obj.name}: {sum(len(p.vertices) - 2 for p in obj.data.polygons)}")
        return budget(target, objects)
    original = n.budget
    n.budget = counting
    try:
        n.run()
    finally:
        n.budget = original


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# --- Pixel frames ----------------------------------------------------------------------------------

class Frame:
    """An art grid and its origin: pixel columns and rows to model coordinates, the pixels under points,
    smoothed shade fields, masks for the silhouette check."""

    def __init__(self, text, width, origin):
        self.g = grid(text, width)
        self.width = width
        self.height = len(self.g)
        self.ox, self.oy = origin
        self._shades = {}

    def X(self, col):
        """A pixel column's centre (fractions allowed)."""
        return col + 0.5 - self.ox

    def Y(self, row):
        return self.oy - (row + 0.5)

    def P(self, col, row, z=0.0):
        return (self.X(col), self.Y(row), z)

    def at(self, x, y):
        """The palette index under a point (None: transparent or outside)."""
        c, r = int(math.floor(x + self.ox)), int(math.floor(self.oy - y))
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.g[r][c]
        return None

    def get(self, c, r):
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.g[r][c]
        return None

    def rows(self, fn):
        """Char rows: fn(index, column, row) -> a char ('.' for nothing); transparent pixels are '.'."""
        return regions(self.g, fn)

    def mask(self, box=None):
        """Coverage for the silhouette check: box (c0, c1, r0, r1), end exclusive; keep(index) filters."""
        return n.art_mask(self.g, box)

    def mask_where(self, keep, box=None):
        g = [[v if v is not None and keep(v) else None for v in row] for row in self.g]
        return n.art_mask(g, box)

    def shade(self, ramps, blur=1):
        """A function (x, y) -> the shade of the pixels of the given ramps there, smoothed."""
        ramps = tuple(ramps) if isinstance(ramps, (tuple, list, set)) else (ramps,)
        key = (ramps, blur)
        if key not in self._shades:
            self._shades[key] = sampler(self.g, (self.ox, self.oy), value=lambda v: v & 15, blur=blur,
                                        keep=lambda v: v is not None and v >> 4 in ramps)
        return self._shades[key]

    def fill(self, outline):
        """Replaces the outline pixels (indices in `outline`) next to the transparent outside by their
        nearest inner pixel, so that the edges of the model take the colour inside the outline."""
        h = self.height

        def is_edge(r, c):
            if self.g[r][c] not in outline:
                return False
            return any(not (0 <= r + dr < h and 0 <= c + dc < self.width) or self.g[r + dr][c + dc] is None
                       for dr in (-1, 0, 1) for dc in (-1, 0, 1))
        out = [row[:] for row in self.g]
        queue = deque((r, c) for r in range(h) for c in range(self.width)
                      if self.g[r][c] is not None and not is_edge(r, c))
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

    def symmetric(self, axis_col):
        """The grid made symmetric about a pixel column (fractional for an axis between columns): the
        left half mirrored over the right (the sprite's light from the left kept on both sides)."""
        out = [row[:] for row in self.g]
        for r in range(self.height):
            for c in range(self.width):
                m = int(round(2 * axis_col - c))
                if c > axis_col and 0 <= m < self.width:
                    out[r][c] = self.g[r][m]
        self.g = out
        self._shades = {}
        return self


# --- Reliefs ---------------------------------------------------------------------------------------

def outlines_of(frame, keep, grow=0.0, smooth=2, epsilon=0.35, min_area=0.4):
    """The outlines of the pixels keep(index, column, row) accepts, moved out by `grow` (holes shrunk)."""
    rows = frame.rows(lambda v, c, r: "x" if keep(v, c, r) else ".")
    polys = sh.outlines(rows, "x", (frame.ox, frame.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)
    if not grow:
        return polys
    out = []
    for i, p in enumerate(polys):
        hole = any(j != i and _inside(q, *p[0]) for j, q in enumerate(polys))
        out.append(sh.inset(p, grow if hole else -grow))
    return out


def _inside(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[i - 1]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def relief(name, polys, mat, profile, bottom=0.0, base=0.0, z_fn=None, spacing=0.5, rim=0.15, angle=50, sigma=1.2,
           flat=False):
    """A part inflated from polygons (wave1_d_shapes.inflate), smoothed. flat: the top's highest points
    (within 0.06) levelled exactly, so painted flat tops merge into few faces."""
    obj = sh.inflate(name, polys, mat, profile, bottom=bottom, base=base, rim=rim, spacing=spacing, z_fn=z_fn,
                     sigma=sigma)
    if flat:
        top = max(vt.co.z for vt in obj.data.vertices)
        for vt in obj.data.vertices:
            if vt.co.z > top - 0.06:
                vt.co.z = top
    return k.smooth(obj, angle)


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


def mirror_scene(axis_x=0.0):
    """Mirrors every mesh of the scene across x = axis_x (mirror images of a whole model)."""
    m = Matrix.Translation((axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-axis_x, 0, 0))
    for obj in meshes():
        sh.apply_modifiers(obj)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)
        obj.data.transform(m)
        obj.data.flip_normals()


def lift(obj, dz):
    obj.data.transform(Matrix.Translation((0, 0, dz)))
    return obj


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
            self.cache[index] = pal(f"{self.prefix}_{index:02x}", index, metallic=metallic, roughness=roughness,
                                    glow=self.glow.get(index))
        return self.cache[index]

    def shifted(self, index, steps):
        index = self.remap.get(index, index)
        ramp, shade = index >> 4, index & 15
        return self(ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade + steps)))


def paint_sprite(obj, frame, painter, wall_steps=-2, under=None, default=None, keep=None, probe=0.0, blur=0,
                 shade_shift=0.0, ramp_of=None):
    """Gives each face the colour of the sprite's pixel under its centre (painter: index -> material):
    walls (steep faces) take it `wall_steps` shades lighter (negative: darker), faces looking down
    `under` (None: the pixel's colour three shades darker); where the sprite is transparent, `default`
    (None: keep). keep(index) -> False leaves the face as it is. probe: walls sample that far out along
    their normal. blur > 0 takes the shade of the pixel's ramp smoothed that many times (less pixel
    noise), shifted by shade_shift. ramp_of(index) -> ramp overrides the ramp painted."""
    def pick(c, nrm):
        x, y = c.x, c.y
        wall = abs(nrm.z) < 0.45
        if wall and probe:
            x += nrm.x * probe
            y += nrm.y * probe
        index = frame.at(x, y)
        if index is None:
            return default
        if keep is not None and not keep(index):
            return None
        ramp = index >> 4 if ramp_of is None else ramp_of(index)
        shade = index & 15
        if blur:
            shade = frame.shade(index >> 4, blur)(x, y)
        shade = int(round(shade + shade_shift))
        index = ramp * 16 + max(1 if ramp == 0 else 0, min(15, shade))
        if nrm.z < -0.5:
            return under if under is not None else painter.shifted(index, -3)
        return painter.shifted(index, wall_steps) if wall else painter(index)
    return paint_faces(obj, pick)


def pixelate(obj, frame, step=1.0, box=None):
    """Cuts obj's faces along the pixel grid (every `step` pixels), so painting follows the pixels."""
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


def bands_of(prefix, ramp, shades, metallic=0.4, roughness=0.4, glow=None):
    """Materials of one palette ramp by shade: bands [(lowest shade, material)] for n.paint_shades."""
    out = []
    for i, s in enumerate(shades):
        lowest = -99 if i == 0 else (shades[i - 1] + s) / 2
        out.append((lowest, pal(f"{prefix}_{ramp * 16 + s:02x}", ramp * 16 + s, metallic=metallic,
                                roughness=roughness, glow=glow)))
    return out


def stats(*objects):
    if "stats" in k.args():
        for obj in objects:
            print(f"--- part {obj.name}: {w.triangles([obj])} triangles")
