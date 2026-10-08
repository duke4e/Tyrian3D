"""Helpers for the batch P models of wave 3 (sheet 2: episode 1's TYRIAN, HOLES and TYRIAN X), on top of
the batch J kit (wave3_j_kit: pixel grids, palette materials, inflated parts, turned parts, tubes,
cutting larger objects into pieces): the sprites' pixels (wave3_p_art.py), heightfield slabs over a
sprite's pixels (floors), the rock and dirt many of sheet 2's ground sprites are drawn on as round
boulders where the sprites draw them, chamfered plates, mirroring, a triangle budget and the build
loop.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
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
sys.path.insert(0, HERE)
import wave3_j_kit as base  # noqa: E402
from wave3_j_kit import (k, sh, grid, regions, relabel, px, py, pal, paint_faces, part, lathe_axis, hoop,  # noqa: E402,F401
                         column, tube, catmull, sphere, rounded_box, block, lumpy, meshes, bake, transform, triangles,
                         simplify_bottom, decimate, piece, sampler, pixel_at, outlines)
import wave3_p_art as art  # noqa: E402,F401

SHEET = "enemy_2"
ENEMIES = base.ENEMIES


# --- Pixels --------------------------------------------------------------------------------------

def ramp(v):
    return None if v is None else v >> 4


def shade(v):
    return None if v is None else v & 15


def mask_of(g, keep=lambda v, c, r: v is not None):
    """Rows of bools: the pixels keep(index, column, row) accepts."""
    return [[keep(v, c, r) for c, v in enumerate(row)] for r, row in enumerate(g)]


def flood(g, passable, seeds=None):
    """The pixels reachable through pixels passable(index, column, row) accepts from `seeds` (default:
    the passable pixels on the border), 4-connected: rows of bools."""
    h, w = len(g), len(g[0])
    out = [[False] * w for _ in range(h)]
    if seeds is None:
        seeds = [(r, c) for r in range(h) for c in range(w) if (r in (0, h - 1) or c in (0, w - 1))]
    stack = [(r, c) for r, c in seeds if passable(g[r][c], c, r)]
    for r, c in stack:
        out[r][c] = True
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and not out[rr][cc] and passable(g[rr][cc], cc, rr):
                out[rr][cc] = True
                stack.append((rr, cc))
    return out


def largest_component(mask):
    """The largest 4-connected region of a mask (rows of bools), as rows of bools."""
    h, w = len(mask), len(mask[0])
    seen = [[False] * w for _ in range(h)]
    best = []
    for r in range(h):
        for c in range(w):
            if not mask[r][c] or seen[r][c]:
                continue
            region, stack = [], [(r, c)]
            seen[r][c] = True
            while stack:
                rr, cc = stack.pop()
                region.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    r2, c2 = rr + dr, cc + dc
                    if 0 <= r2 < h and 0 <= c2 < w and mask[r2][c2] and not seen[r2][c2]:
                        seen[r2][c2] = True
                        stack.append((r2, c2))
            if len(region) > len(best):
                best = region
    out = [[False] * w for _ in range(h)]
    for r, c in best:
        out[r][c] = True
    return out


def fill_holes(mask):
    """The mask with its enclosed holes filled (pixels not reachable from the border outside it)."""
    h, w = len(mask), len(mask[0])
    rows = [[None if mask[r][c] else 0 for c in range(w)] for r in range(h)]
    outside = flood(rows, lambda v, c, r: v is not None)
    return [[mask[r][c] or not outside[r][c] for c in range(w)] for r in range(h)]


def blurred(field, times=1):
    """A 2D numpy field blurred with a 3x3 kernel `times` times (edges clamped)."""
    f = np.array(field, dtype=float)
    kernel = np.array([[0.5, 1, 0.5], [1, 2, 1], [0.5, 1, 0.5]])
    kernel /= kernel.sum()
    for _ in range(times):
        p = np.pad(f, 1, mode="edge")
        f = sum(kernel[i, j] * p[i:i + f.shape[0], j:j + f.shape[1]] for i in range(3) for j in range(3))
    return f


# --- Beds of rock and dirt -------------------------------------------------------------------------

def bed(name, heights, mat_index, mats, origin, z0=0.0, keep=None, smooth_angle=35, dissolve=0.6):
    """A heightfield slab over a pixel grid: heights[r][c] is the top of pixel (c, r) (the surface
    passes through the mean of the four pixels round each pixel corner), mat_index[r][c] its material
    (an index into mats); keep[r][c] false leaves a pixel out. Walls run down to z0 round the kept
    pixels and a flat bottom closes it. Flat stretches are merged into few faces."""
    h, w = len(heights), len(heights[0])
    hts = np.array(heights, dtype=float)
    kept = np.ones((h, w), dtype=bool) if keep is None else np.array(keep, dtype=bool)
    ox, oy = origin

    def corner(r, c):
        vals = [hts[rr, cc] for rr in (r - 1, r) for cc in (c - 1, c) if 0 <= rr < h and 0 <= cc < w and kept[rr, cc]]
        return sum(vals) / len(vals) if vals else z0

    bm = bmesh.new()
    top = {}

    def tv(r, c):
        if (r, c) not in top:
            top[(r, c)] = bm.verts.new((c - ox, oy - r, corner(r, c)))
        return top[(r, c)]
    for r in range(h):
        for c in range(w):
            if not kept[r, c]:
                continue
            a, b, cc, d = tv(r, c), tv(r, c + 1), tv(r + 1, c + 1), tv(r + 1, c)
            if abs(a.co.z - cc.co.z) <= abs(b.co.z - d.co.z):
                tris = [(a, d, cc), (a, cc, b)]
            else:
                tris = [(a, d, b), (b, d, cc)]
            for t in tris:
                f = bm.faces.new(t)
                f.material_index = int(mat_index[r][c])
    # Walls along the kept region's border, down to z0, and the bottom.
    low = {}

    def lv(r, c):
        if (r, c) not in low:
            low[(r, c)] = bm.verts.new((c - ox, oy - r, z0))
        return low[(r, c)]

    def inside(r, c):
        return 0 <= r < h and 0 <= c < w and kept[r, c]
    for r in range(h):
        for c in range(w):
            if not kept[r, c]:
                continue
            # Each side of the pixel whose neighbour is not kept: (corner a, corner b) counter-clockwise
            # seen from above.
            for (dr, dc), (p, q) in (((-1, 0), ((r, c + 1), (r, c))), ((1, 0), ((r + 1, c), (r + 1, c + 1))),
                                     ((0, -1), ((r, c), (r + 1, c))), ((0, 1), ((r + 1, c + 1), (r, c + 1)))):
                if inside(r + dr, c + dc):
                    continue
                f = bm.faces.new((tv(*p), lv(*p), lv(*q), tv(*q)))
                f.material_index = int(mat_index[r][c])
            f = bm.faces.new((lv(r, c), lv(r, c + 1), lv(r + 1, c + 1), lv(r + 1, c)))
            f.material_index = int(mat_index[r][c])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(dissolve), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    return k.smooth(obj, smooth_angle)


def boulders(name, g, origin, keep, shades, tans=None, is_tan=lambda v: False, value=None, dark=2.0, base_z=0.0,
             base_h=0.7, base_mat=None, rmin=1.4, rmax=3.6, height=0.7, lift=0.0, seed=3, clip=True, segments=8,
             rings=5, keep_base=None):
    """Rocks as round boulders where the sprite draws them: lighter blobs of the pixels keep(index,
    column, row) accepts become lumpy boulders (radius from the distance to the darker gaps, rmin..rmax;
    `height` times that high), their material picked from `shades` (dark to light) by their brightness,
    or from `tans` if is_tan(index) holds for most of their pixels; a low slab of base_mat (base_h high)
    fills the gaps between them over the kept pixels (keep_base: other pixels for it). value(index) ->
    brightness (default: the shade). clip: cut everything to the sprite's rectangle. Returns the parts."""
    value = value or shade
    h, w = len(g), len(g[0])
    ox, oy = origin
    rock = np.zeros((h, w), dtype=bool)
    field = np.zeros((h, w))
    tan = np.zeros((h, w), dtype=bool)
    for r in range(h):
        for c in range(w):
            v = g[r][c]
            if keep(v, c, r):
                rock[r, c] = True
                field[r, c] = value(v)
                tan[r, c] = is_tan(v)
    mean = field[rock].mean() if rock.any() else 4.0
    full = np.where(rock, field, mean)
    soft = blurred(full, 1)
    # The distance from each pixel to the nearest gap (a dark or non-rock pixel, or the edge).
    gaps = [(r, c) for r in range(h) for c in range(w) if not rock[r, c] or field[r, c] <= dark]
    gaps += [(r, -1) for r in range(h)] + [(r, w) for r in range(h)] if not clip else []
    gap_arr = np.array(gaps, dtype=float) if gaps else np.zeros((0, 2))
    rng = random.Random(seed)
    parts = []
    covered = np.zeros((h, w), dtype=bool)
    order = sorted(((soft[r, c], r, c) for r in range(h) for c in range(w) if rock[r, c] and field[r, c] > dark),
                   reverse=True)
    count = 0
    for b, r, c in order:
        if covered[r, c]:
            continue
        if len(gap_arr):
            dist = float(np.min(np.hypot(gap_arr[:, 0] - r, gap_arr[:, 1] - c)))
        else:
            dist = rmax
        rad = max(rmin, min(rmax, dist + 0.4))
        cx, cy = c + 0.5 - ox, oy - r - 0.5
        rr0, rr1 = int(max(0, r - rad)), int(min(h - 1, r + rad))
        cc0, cc1 = int(max(0, c - rad)), int(min(w - 1, c + rad))
        cells = [(rr, cc) for rr in range(rr0, rr1 + 1) for cc in range(cc0, cc1 + 1)
                 if (rr - r) ** 2 + (cc - c) ** 2 <= (rad * 0.9) ** 2]
        for rr, cc in cells:
            covered[rr, cc] = True
        rock_cells = [(rr, cc) for rr, cc in cells if rock[rr, cc]]
        bright = np.mean([field[rr, cc] for rr, cc in rock_cells]) if rock_cells else b
        tan_share = np.mean([tan[rr, cc] for rr, cc in rock_cells]) if rock_cells else 0.0
        if tans and tan_share > 0.5:
            mats = tans
        else:
            mats = shades
        lo, hi = 2.0, 9.0
        index = int(round((len(mats) - 1) * min(1.0, max(0.0, (bright - lo) / (hi - lo)))))
        hz = rad * height * (0.75 + 0.25 * min(1.0, bright / 8.0))
        stretch = rng.uniform(0.85, 1.15)
        obj = lumpy(f"{name}_{count}", (cx + rng.uniform(-0.2, 0.2), cy + rng.uniform(-0.2, 0.2), base_z + lift),
                    (rad * stretch, rad / stretch, hz), mats[index], seed=seed + count, amount=0.16,
                    segments=segments, rings=rings)
        parts.append(obj)
        count += 1
    # The gaps between them.
    base_cells = rock if keep_base is None else rock | np.array(mask_of(g, keep_base), dtype=bool)
    if base_mat is not None and base_cells.any():
        heights = np.full((h, w), base_z + base_h)
        idx = np.zeros((h, w), dtype=int)
        parts.append(bed(name + "_base", heights, idx, [base_mat], origin, z0=base_z, keep=base_cells))
    if clip:
        x0, x1 = -ox, w - ox
        y0, y1 = oy - h, oy
        parts = sh.cut_box(parts, x0, x1, y0, y1)
        parts = sh.cut_planes(parts, [((0, 0, base_z), (0, 0, -1))])
    return parts


def grey_rocks(name, g, keep, prefix="rock", origin=(12, 14), **options):
    """Grey boulders (ramp 0) with tan stones (ramp A) among them, on a dark base (boulders)."""
    greys = [pal(f"{prefix}_rock{s}", s, metallic=0.05, roughness=0.8) for s in (3, 5, 7, 9)]
    tans = [pal(f"{prefix}_tan{s}", 0xa0 + s, metallic=0.05, roughness=0.75) for s in (8, 10, 12)]
    base = pal(f"{prefix}_gap", 0x03, metallic=0.0, roughness=0.9)
    options.setdefault("dark", 1.0)
    options.setdefault("height", 0.85)
    options.setdefault("base_h", 0.5)
    return boulders(name, g, origin, keep, greys, tans, is_tan=lambda v: ramp(v) == 0xa,
                    value=lambda v: shade(v) if ramp(v) == 0 else shade(v) - 3, base_mat=base, **options)


def brown_dirt(name, g, keep, prefix="dirt", origin=(12, 14), **options):
    """Brown cobbles (ramp 1, the dirt of TYRIAN's and HOLES's ground), on a dark base (boulders)."""
    browns = [pal(f"{prefix}_dirt{s}", 0x10 + s, metallic=0.0, roughness=0.8) for s in (2, 3, 4, 6)]
    base = pal(f"{prefix}_dirt_gap", 0x11, metallic=0.0, roughness=0.9)
    options.setdefault("dark", 1.0)
    options.setdefault("height", 0.8)
    options.setdefault("base_h", 0.45)
    options.setdefault("rmax", 3.0)
    return boulders(name, g, origin, keep, browns, value=lambda v: min(9, shade(v) * 2 - 1), base_mat=base,
                    **options)


def on_ellipsoid(centre, radii, x, y, lift=0.0):
    """The height of an ellipsoid's top surface over (x, y) (its centre's height off it), plus lift."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    q = 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2
    return cz + rz * math.sqrt(max(0.0, q)) + lift


# --- Plates ---------------------------------------------------------------------------------------

def chamfered(name, outline, z0, z1, mat, chamfer=0.8, inset_bottom=0.0, smooth_angle=30):
    """A plate over an outline (counter-clockwise, convex or mildly concave) from z0 to z1 whose top
    edge is chamfered by `chamfer` (inwards and down) and whose sides lean out by inset_bottom."""
    outer = sh.inset(outline, -inset_bottom) if inset_bottom else outline
    top_out = outline
    top_in = sh.inset(outline, chamfer)
    bm = bmesh.new()
    n = len(outline)
    lo = [bm.verts.new((x, y, z0)) for x, y in outer]
    mid = [bm.verts.new((x, y, z1 - chamfer)) for x, y in top_out]
    hi = [bm.verts.new((x, y, z1)) for x, y in top_in]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], mid[j], mid[i]))
        bm.faces.new((mid[i], mid[j], hi[j], hi[i]))
    bm.faces.new(hi)
    bm.faces.new(list(reversed(lo)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return k.smooth(obj, smooth_angle)


def octagon(cx, cy, hw, hh, cut, cut_bottom=None):
    """An octagon (counter-clockwise): half-width hw, half-height hh, its corners cut by `cut`
    (cut_bottom: the lower corners' cut, default the same)."""
    cb = cut if cut_bottom is None else cut_bottom
    return [(cx - hw + cb, cy - hh), (cx + hw - cb, cy - hh), (cx + hw, cy - hh + cb), (cx + hw, cy + hh - cut),
            (cx + hw - cut, cy + hh), (cx - hw + cut, cy + hh), (cx - hw, cy + hh - cut), (cx - hw, cy - hh + cb)]


def planar(obj, degrees=2.0):
    """Merges the nearly flat stretches of a part's surface into larger faces (keeping the borders
    between materials), then triangulates: flat tops cost few triangles."""
    mod = obj.modifiers.new("planar", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(degrees)
    mod.delimit = {"MATERIAL"}
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def mirror_all(axis_x=0.0):
    """Mirrors every mesh in place across x = axis_x (a sprite's mirror image)."""
    bake()
    m = Matrix.Translation((axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-axis_x, 0, 0))
    for obj in meshes():
        obj.data.transform(m)
        obj.data.flip_normals()


def budget(target=4800):
    """Keeps a model light: its larger meshes are decimated until the whole has about `target`
    triangles. Returns the count."""
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


# --- Silhouette check ----------------------------------------------------------------------------

def check_mask(mask, label="", supersample=4, offset=(0.0, 0.0)):
    """Compares the scene's top view with a pixel mask (rows of bools centred on the origin moved by
    offset): prints the overlap (intersection over union) and a map ('#' both, '+' model only, '-'
    mask only)."""
    h, w = len(mask), len(mask[0])
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = w * supersample, h * supersample
    scene.render.resolution_percentage = 100
    cam = k._camera("silhouette", (offset[0], offset[1], 200), (0, 0, 0), ortho_scale=max(w, h))
    cam.data.clip_end = 1000
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "wave3p_silhouette.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3]
    # The camera frames max(w, h) across the longer side; crop the rendered square to the mask.
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


# --- Registry and build loop -----------------------------------------------------------------------

MODELS = []  # (name, builder, [sprites of sheet 2], size)
WHOLES = {}  # name: (builder, size, offset of the sprite grid): objects drawn in pieces, for --whole


def model(name, sprites, size=(24, 28)):
    """Registers a builder; sprites: the sheet-2 sprites it stands for (the first is checked)."""
    def register(fn):
        MODELS.append((name, fn, sprites, size))
        return fn
    return register


def whole(name, size):
    def register(fn):
        WHOLES[name] = (fn, size)
        return fn
    return register


def render_3q(prefix, size, scale=1.0):
    scene = bpy.context.scene
    cam = bpy.data.objects["3q"]
    cam.location = Vector((38, -48, 42)) * scale
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = 1024, 768
    scene.render.filepath = prefix + "_3q.png"
    bpy.ops.render.render(write_still=True)


def run():
    """Options after "--": --only a,b  --preview <prefix>  --check <extracted sheets dir>  --stats 1
    --whole <name> --preview <prefix>: renders a whole object (no export)."""
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
            render_3q(prefix, size, max(size) / 40.0)
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
            large = size == (24, 28)
            check_mask(k.sprite_mask(sheet_png, [sprites[0]], large), f"{name} (2 {sprites[0]})")
        k.export(os.path.join(ENEMIES, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(options["preview"] + name, size)
