"""Helpers for the batch T models of wave 3 (sheet V: GEM WAR, GRYPHON, MISTAKES, STATION, MARKERS,
UNDERDELI, DREAD-NOT), on top of the batch P and J kits (wave3_p_kit, wave3_j_kit: pixel grids, palette
materials, inflated parts, turned parts, tubes, cutting larger objects into pieces, mirroring, the
triangle budget), round discs and the build loop (silhouettes checked against sheet V). (The stand-alone
enemies' cushions and lofts went with them into polish_*.py.)

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave3_p_kit as pk  # noqa: E402
from wave3_p_kit import (k, sh, grid, regions, relabel, px, py, pal, paint_faces, part, lathe_axis, hoop,  # noqa: E402,F401
                         column, tube, catmull, sphere, rounded_box, block, lumpy, meshes, bake, transform, triangles,
                         simplify_bottom, decimate, piece, sampler, pixel_at, outlines, ramp, shade, chamfered,
                         octagon, planar, mirror_all, budget, check_mask, mask_of, fill_holes)

SHEET = "enemy_V"
ENEMIES = pk.ENEMIES


def ccw(poly):
    """The polygon counter-clockwise."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    return poly if area > 0 else list(reversed(poly))


# --- Parts -----------------------------------------------------------------------------------------

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
