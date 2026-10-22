"""Helpers for the batch L models of wave 3 (wave3_l.py, wave3_l_parts.py: sheet 5): pixel art with its
origin, palette materials, the shared part builders of the earlier batches (wave2_f_kit, wave2_h_kit,
wave1_d_shapes), cutting a whole object into the sprites the game draws, a silhouette check against
any pixel mask, a triangle budget and the build loop.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402
from wave2_f_kit import (blade, bake, catmull, cone, lathe_axis, lumpy, meshes, paint, pal,  # noqa: E402,F401
                         rounded_box, sphere, transform, triangles, tube)
from wave2_h_kit import (band_split, distance_to, frame_rings, round_edge, section_loft, smoothstep,  # noqa: E402,F401
                        solid)

ROOT = os.path.join(HERE, "..", "..", "..", "..")
ENEMIES = os.path.join(ROOT, "assets", "models", "enemies")


# --- Pixel art ---------------------------------------------------------------------------------

class Art:
    """Pixel art (rows of characters, '.' empty) whose pixel (ox, oy) corner is the model's origin:
    x(c), y(r) give a pixel's centre (fractions allowed), polys() the outlines of some characters."""

    def __init__(self, text, origin):
        self.rows = [line for line in text.strip("\n").split("\n")]
        width = max(len(r) for r in self.rows)
        self.rows = [r.ljust(width, ".") for r in self.rows]
        self.w, self.h = width, len(self.rows)
        self.ox, self.oy = origin

    def x(self, c):
        return c + 0.5 - self.ox

    def y(self, r):
        return self.oy - (r + 0.5)

    def p(self, c, r, z=None):
        return (self.x(c), self.y(r)) if z is None else (self.x(c), self.y(r), z)

    def at(self, c, r):
        if 0 <= r < self.h and 0 <= c < self.w:
            return self.rows[r][c]
        return "."

    def select(self, keep):
        """The rows with only the pixels where keep(column, row, char) holds."""
        return ["".join(ch if ch != "." and keep(c, r, ch) else "." for c, ch in enumerate(line))
                for r, line in enumerate(self.rows)]

    def polys(self, chars=None, rows=None, smooth=2, epsilon=0.45, min_area=0.5):
        """Outlines of the pixels whose character is in chars (None: every pixel)."""
        rows = rows or self.rows
        if chars is None:
            rows = ["".join("#" if ch != "." else "." for ch in line) for line in rows]
            chars = "#"
        return sh.outlines(rows, chars, (self.ox, self.oy), smooth=smooth, epsilon=epsilon, min_area=min_area)

    def mask(self, keep=None):
        return [[ch != "." and (keep is None or keep(c, r)) for c, ch in enumerate(line)]
                for r, line in enumerate(self.rows)]

    def char(self, x, y):
        """The character of the pixel under the point (x, y)."""
        return self.at(int(math.floor(x + self.ox)), int(math.floor(self.oy - y)))

    def near(self, x, y, chars, radius=1):
        """Whether a pixel within `radius` pixels of (x, y) has one of chars."""
        c0, r0 = int(math.floor(x + self.ox)), int(math.floor(self.oy - y))
        return any(self.at(c0 + dc, r0 + dr) in chars for dr in range(-radius, radius + 1)
                   for dc in range(-radius, radius + 1))

    def shade(self, c, r, default=None):
        """The pixel's shade (its hex digit), or default for letters and empty pixels."""
        ch = self.at(c, r)
        return int(ch, 16) if ch in "0123456789abcdef" else default


def shade_field(art, blur=1, letters=None, skip=""):
    """A function (x, y) -> the art's shade at a point: bilinear between pixel centres, blurred `blur`
    times; letters count as letters.get(char) (default: not known), characters in skip are not known
    either (outlines); outside the known pixels, the nearest one's."""
    letters = letters or {}
    h, w = art.h, art.w
    field = np.full((h, w), np.nan)
    for r in range(h):
        for c in range(w):
            ch = art.rows[r][c]
            if ch in skip:
                continue
            if ch in "0123456789abcdef":
                field[r, c] = int(ch, 16)
            elif ch in letters:
                field[r, c] = letters[ch]
    for _ in range(blur):
        out = field.copy()
        for r in range(h):
            for c in range(w):
                if np.isnan(field[r, c]):
                    continue
                vals, wts = [], []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < w and not np.isnan(field[rr, cc]):
                            vals.append(field[rr, cc])
                            wts.append(2.0 if dr == dc == 0 else 1.0 if dr == 0 or dc == 0 else 0.5)
                out[r, c] = np.average(vals, weights=wts)
        field = out
    known = np.array([(r, c) for r in range(h) for c in range(w) if not np.isnan(field[r, c])])
    # The unknown pixels take the mean of their known neighbours, ring by ring (a smooth extension).
    for _ in range(6):
        out = field.copy()
        for r in range(h):
            for c in range(w):
                if not np.isnan(field[r, c]):
                    continue
                vals = [field[r + dr, c + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                        if 0 <= r + dr < h and 0 <= c + dc < w and not np.isnan(field[r + dr, c + dc])]
                if vals:
                    out[r, c] = sum(vals) / len(vals)
        field = out

    def at(x, y):
        c, r = x + art.ox - 0.5, art.oy - y - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        total = weight = 0.0
        for rr, cc, wt in ((r0, c0, (1 - (r - r0)) * (1 - (c - c0))), (r0, c0 + 1, (1 - (r - r0)) * (c - c0)),
                           (r0 + 1, c0, (r - r0) * (1 - (c - c0))), (r0 + 1, c0 + 1, (r - r0) * (c - c0))):
            if 0 <= rr < h and 0 <= cc < w and not np.isnan(field[rr, cc]):
                total += field[rr, cc] * wt
                weight += wt
        if weight > 0.05:
            return total / weight
        i = int(np.argmin((known[:, 0] - r) ** 2 + (known[:, 1] - c) ** 2))
        return field[known[i][0], known[i][1]]
    return at


# --- Parts -------------------------------------------------------------------------------------

def rounded(name, polys, mat, aspect=1.0, max_height=None, base=0.0, bottom=0.0, spacing=0.4, z_fn=None, angle=55,
            sigma=1.2):
    """A part filling the polygons, round in section (as high as aspect times its local half-width)."""
    obj = sh.inflate(name, polys, mat, sh.round_profile(aspect, max_height=max_height), bottom=bottom, base=base,
                     rim=0.1, spacing=spacing, z_fn=z_fn, sigma=sigma)
    return k.smooth(obj, angle)


def decimate(obj, target):
    """Collapses a part's mesh to about `target` triangles (if it has more)."""
    sh.apply_modifiers(obj)
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tris > target:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.ratio = target / tris
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return obj


def simplify_flat(obj, normal_z=-0.999):
    """Dissolves the flat faces facing straight down (or up: normal_z=0.999) into few faces."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    if normal_z < 0:
        faces = [f for f in bm.faces if f.normal.z < normal_z]
    else:
        faces = [f for f in bm.faces if f.normal.z > normal_z]
    if faces:
        try:
            bmesh.ops.dissolve_faces(bm, faces=faces, use_verts=True)
        except Exception:  # noqa: BLE001 (keep it as it is)
            pass
        ngons = [f for f in bm.faces if len(f.verts) > 3]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def budget(target=4800):
    """Keeps a model light: with its modifiers applied, its larger meshes are decimated until the
    whole has about `target` triangles. Returns the count."""
    objs = meshes()
    for obj in objs:
        sh.apply_modifiers(obj)
    count = lambda o: sum(len(p.vertices) - 2 for p in o.data.polygons)  # noqa: E731
    total = sum(count(o) for o in objs)
    if total <= target:
        return total
    big = [o for o in objs if count(o) > 300]
    small = total - sum(count(o) for o in big)
    ratio = max(0.1, (target - small) / max(1, total - small))
    for obj in big:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return sum(count(o) for o in objs)


# --- Pieces ------------------------------------------------------------------------------------

def cut_piece(x0, x1, y0, y1):
    """Keeps the part of the scene's meshes in x0..x1, y0..y1 (closing the cuts) and moves it so that
    the box's centre is the origin: one sprite of a larger object (models.cfg: origin)."""
    bake()
    kept = sh.cut_box(meshes(), x0, x1, y0, y1)
    sh.move(kept, -(x0 + x1) / 2, -(y0 + y1) / 2)
    for obj in kept:
        k.smooth(obj, 50)
    return kept


# --- Silhouette check --------------------------------------------------------------------------

def check_mask(mask, label="", supersample=4, offset=(0.0, 0.0)):
    """Compares the scene's top view with a pixel mask (rows of bools, its centre on the origin
    moved by offset): prints the overlap (intersection over union) and a map ('#' both, '+' model
    only, '-' mask only)."""
    h, w = len(mask), len(mask[0])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = k._camera("silhouette", (offset[0], offset[1], 200), (0, 0, 0), ortho_scale=max(w, h))
    cam.data.clip_end = 1000
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "wave3l_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    covered = alpha.reshape(h, supersample, w, supersample).mean(axis=(1, 3)) > 0.5
    both = sum(covered[y][x] and mask[y][x] for y in range(h) for x in range(w))
    either = sum(covered[y][x] or mask[y][x] for y in range(h) for x in range(w))
    score = both / max(either, 1)
    print("silhouette overlap %s: %.3f" % (label, score))
    for y in range(h):
        print("".join("#" if covered[y][x] and mask[y][x] else "+" if covered[y][x] else "-" if mask[y][x] else "."
                      for x in range(w)))
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    return score


# --- Registry and build loop -------------------------------------------------------------------

MODELS = []  # (name, builder, sheet, sprite, large)
WHOLES = []  # (name, builder, size, mask or None): whole objects drawn in pieces, for --whole previews


def model(name, sprite, large=True, sheet="5"):
    def register(fn):
        MODELS.append((name, fn, sheet, sprite, large))
        return fn
    return register


def whole(name, builder, size, mask=None):
    WHOLES.append((name, builder, size, mask))


def render_3q(prefix, size, scale=1.0):
    """A three-quarter view from farther away (for large objects), to <prefix>_3q.png."""
    scene = bpy.context.scene
    cam = bpy.data.objects["3q"]
    cam.location = Vector((38, -48, 42)) * scale
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = 1024, 768
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)


def main():
    """Options after "--": --only a,b  --preview <prefix>  --check <extracted sheets dir>  --stats 1
    --whole <prefix> (renders the whole objects instead of building the models; --check with it
    compares them with their art)."""
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    if "whole" in options:
        for name, build, size, mask in WHOLES:
            if only and name not in only:
                continue
            k.reset()
            build()
            bake()
            print(f"== whole {name}: {triangles()} triangles")
            if "check" in options and mask is not None:
                check_mask(mask, name)
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["whole"] + name, size, scale=max(4, int(640 / max(size))))
            render_3q(options["whole"] + name, size, max(size) / 40.0)
        return
    for name, build, sheet, sprite, large in MODELS:
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
            sheet_png = os.path.join(options["check"], f"enemy_{sheet}.png")
            check_mask(k.sprite_mask(sheet_png, [sprite], large), f"{name} ({sheet} {sprite})")
        k.export(os.path.join(ENEMIES, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, (24, 28) if large else (12, 14))
