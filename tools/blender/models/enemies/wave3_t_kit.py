"""Helpers for the batch T models of wave 3 (sheet V: GEM WAR, GRYPHON, MISTAKES, STATION, MARKERS,
UNDERDELI, DREAD-NOT), on top of the batch P and J kits (wave3_p_kit, wave3_j_kit: pixel grids, palette
materials, inflated parts, turned parts, tubes, cutting larger objects into pieces, mirroring, the
triangle budget): the sprites' pixels (wave3_t_art.py), blocks whose top follows a function (cushions),
lofts along x or y through superellipse sections, and the build loop (silhouettes checked against
sheet V).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave3_p_kit as pk  # noqa: E402
from wave3_p_kit import (k, sh, grid, regions, relabel, px, py, pal, paint_faces, part, lathe_axis, hoop,  # noqa: E402,F401
                         column, tube, catmull, sphere, rounded_box, block, lumpy, meshes, bake, transform, triangles,
                         simplify_bottom, decimate, piece, sampler, pixel_at, outlines, ramp, shade, chamfered,
                         octagon, planar, mirror_all, budget, check_mask, mask_of, fill_holes)
import wave3_t_art as art  # noqa: E402,F401

SHEET = "enemy_V"
ENEMIES = pk.ENEMIES


def smoothstep(edge0, edge1, x):
    return sh.smoothstep(edge0, edge1, x)


def ccw(poly):
    """The polygon counter-clockwise."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    return poly if area > 0 else list(reversed(poly))


def edges(points, origin=(12, 14)):
    """Pixel-edge coordinates (column, row) to model (x, y), counter-clockwise."""
    ox, oy = origin
    return ccw([(c - ox, oy - r) for c, r in points])


# --- Parts -----------------------------------------------------------------------------------------

def cushion(name, polys, mat, top, rounding=1.2, spacing=0.5, base=0.0, smooth_angle=50, sigma=1.2):
    """A part standing on `base` over the polygons (model coordinates, counter-clockwise; holes
    clockwise), its top following top(x, y), its edge rounded over `rounding` pixels into
    straight sides (as wave1_b.cushion)."""
    if polys and isinstance(polys[0][0], (int, float)):
        polys = [polys]
    profile = sh.pillow_profile(rounding, rounding)
    obj = sh.inflate(name, polys, mat, profile, bottom=0.0, base=base, rim=0.0, spacing=spacing,
                     z_fn=lambda x, y, z: max(base + 0.05, top(x, y) - rounding + (z - base)), sigma=sigma)
    simplify_bottom(obj)
    return k.smooth(obj, smooth_angle)


def lite(obj, target, smooth_angle=50):
    """The part collapsed to about `target` triangles before it is painted (so the budget need not
    decimate the painted model), its smoothing redone."""
    decimate(obj, target)
    return k.smooth(obj, smooth_angle)


def loft_x(name, sections, mat, segments=24, power=2.0, start=None, end=None, smooth_angle=50):
    """A hull along x through sections (x, y centre, z centre, half-depth in y, top, bottom): each a
    superellipse of `power` whose upper half is `top` high and lower half `bottom` deep."""
    rings = []
    for x, yc, zc, hd, top, bottom in sections:
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / power), c) * hd
            v = math.copysign(abs(s) ** (2 / power), s) * (top if s >= 0 else bottom)
            pts.append(Vector((x, yc - u, zc + v)))
        rings.append(pts)
    first, last = sections[0], sections[-1]
    obj = k.loft(name, rings, mat, start_point=start or (first[0], first[1], first[2]),
                 end_point=end or (last[0], last[1], last[2]))
    return k.smooth(obj, smooth_angle)


def loft_y(name, sections, mat, segments=24, power=2.0, start=None, end=None, smooth_angle=50):
    """A hull along y through sections (y, x centre, z centre, half-width, top, bottom) (as loft_x)."""
    rings = []
    for y, xc, zc, hw, top, bottom in sections:
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / power), c) * hw
            v = math.copysign(abs(s) ** (2 / power), s) * (top if s >= 0 else bottom)
            pts.append(Vector((xc + u, y, zc + v)))
        rings.append(pts)
    first, last = sections[0], sections[-1]
    obj = k.loft(name, rings, mat, start_point=start or (first[1], first[0], first[2]),
                 end_point=end or (last[1], last[0], last[2]))
    return k.smooth(obj, smooth_angle)


def disc(name, centre, radius, z0, z1, mat, segments=32, bevel=0.3, scale_y=1.0):
    """A round plate: a short cylinder from z0 to z1, its top edge bevelled; scale_y makes it oval."""
    cx, cy = centre
    h = z1 - z0
    obj = column(name, [(0.0, radius), (h - bevel, radius), (h, radius - bevel)], mat, cx, cy, segments=segments,
                 smooth_angle=30)
    m = Matrix.Translation((0, 0, z0))
    if scale_y != 1.0:
        m = Matrix.Translation((cx, cy, z0)) @ Matrix.Scale(scale_y, 4, (0, 1, 0)) @ Matrix.Translation((-cx, -cy, 0))
    obj.data.transform(m)
    return obj


def surface(objs, x, y, default=0.0):
    """The highest top surface of the objects over (x, y)."""
    best = None
    for obj in objs:
        z = sh.surface_z(obj, x, y, None)
        if z is not None and (best is None or z > best):
            best = z
    return default if best is None else best


# --- Registry and build loop -------------------------------------------------------------------------

MODELS = []  # (name, builder, [sheet V sprites], size)
WHOLES = {}  # name: (builder, size): objects drawn in pieces, for --whole


def model(name, sprites, size=(24, 28)):
    """Registers a builder; sprites: the sheet V sprites it stands for (the first is checked)."""
    def register(fn):
        MODELS.append((name, fn, sprites, size))
        return fn
    return register


def whole(name, size):
    def register(fn):
        WHOLES[name] = (fn, size)
        return fn
    return register


def run():
    """Options after "--": --only a,b  --preview <prefix>  --check <extracted sheets dir>  --stats 1
    --whole <name,name> --preview <prefix>: renders whole objects (no export)."""
    options = k.args()
    if "whole" in options:
        for name in options["whole"].split(","):
            fn, size = WHOLES[name]
            k.reset()
            fn()
            bake()
            print(f"== whole {name}: {triangles()} triangles")
            bpy.context.scene.view_settings.view_transform = "Standard"
            prefix = options.get("preview", "/tmp/whole_") + name
            k.preview(prefix, size, scale=max(4, 640 // max(size)))
            pk.render_3q(prefix, size, max(size) / 40.0)
        return
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sprites, size in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        bake()
        raw = triangles()
        if "stats" in options:
            for obj in meshes():
                print(f"   {obj.name}: {sum(len(p.vertices) - 2 for p in obj.data.polygons)}")
        count = budget()
        print(f"== {name}: {count} triangles ({raw} before the budget)")
        if "check" in options:
            sheet_png = os.path.join(options["check"], SHEET + ".png")
            check_mask(k.sprite_mask(sheet_png, [sprites[0]], size == (24, 28)), f"{name} (V {sprites[0]})")
        k.export(os.path.join(ENEMIES, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)
