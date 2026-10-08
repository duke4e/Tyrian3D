"""Helpers for the batch X models of wave 3 (sheet C: DELI, New Deli and BONUS, some also in TORM, SOH JIN,
GRYPHON, BOTANY, HARVEST and SAVARA): wave3_x.py, the glass hatch with the red machine, the grey bunker with
the glowing slits and the blue helm with the red eye; wave3_x_tower.py, DELI's tall grey tower with the red
bands and the gun on its mast over a ball; wave3_x_cannon.py, DELI's long blue cannon and its mirror image.
The sprites' pixels are in wave3_x_art.py; the part builders come from the earlier batches' kits
(wave3_j_kit: palette materials, turned parts, tubes, painting faces, the build loop; wave3_o_kit: cutting a
whole object into its sprites' pieces, mirroring, the triangle budget; wave3_q_kit: heightfield parts;
wave3_t_kit: hulls lofted along x or y, round plates).

DELI's ground objects stand on the level's blue-grey floor tiles (ramp 6), which their sprites draw round
them with the object's shadow on them below and to the right. The game casts its own shadows now, so the
models lay the floor as a thin bed in the floor's shades and leave the drawn shadows out (the shadow's
pixels take the shade of a floor pixel from the same rows).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's centre for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import random
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
import wave3_o_kit as o  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_t_kit as t  # noqa: E402,F401
import wave3_x_art as art  # noqa: E402,F401
from wave3_j_kit import (bake, block, catmull, grid, hoop, lathe_axis, meshes, paint_faces, pal, part,  # noqa: E402,F401
                         regions, rounded_box, sampler, sphere, transform, triangles, tube)
from wave3_o_kit import cut, merge, mirror_x, mirror_y, move, paint_bands, smoothstep, budget, decimate  # noqa: E402,F401

C = "enemy_C"


def model(name, sprites, size=(24, 28)):
    """Registers a builder (wave3_j_kit.model); sprites: sheet C sprites [(sprite, large)]."""
    return w.model(name, [(C, s, large) for s, large in sprites], size)


whole = w.whole


def run():
    """wave3_j_kit.run, with --whole renders at a larger scale (768 pixels across the longer side)."""
    options = k.args()
    if "whole" not in options:
        return w.run()
    for name in options["whole"].split(","):
        fn, size = w.WHOLES[name]
        k.reset()
        fn()
        bake()
        print(f"--- {name}: {triangles()} triangles")
        bpy.context.scene.view_settings.view_transform = "Standard"
        prefix = options.get("preview", "/tmp/whole_") + name
        k.preview(prefix, size, scale=max(6, 768 // max(size)))
        scene = bpy.context.scene
        cam = bpy.data.objects["3q"]
        cam.location = Vector((38, -48, 42)) * (0.5 * max(size) / 24.0)
        scene.render.resolution_x = scene.render.resolution_y = 768
        scene.render.filepath = prefix + "_3q.png"
        bpy.ops.render.render(write_still=True)


# --- Pixels --------------------------------------------------------------------------------------

def at(g, c, r):
    if 0 <= r < len(g) and 0 <= c < len(g[r]):
        return g[r][c]
    return None


def px(col, ox=12):
    """A pixel column's centre as x."""
    return col + 0.5 - ox


def py(row, oy=14):
    """A pixel row's centre as y."""
    return oy - (row + 0.5)


def shades(g, origin, keep, blur=1, value=lambda v: v & 15):
    """(x, y) -> the shade of the pixels keep(index) accepts, bilinear and blurred (wave3_j_kit.sampler)."""
    return sampler(g, origin, value=value, blur=blur, keep=lambda v: v is not None and keep(v))


def pixel_polys(g, keep, origin, smooth=2, epsilon=0.4, min_area=0.5):
    """The outlines of the pixels keep(index, column, row) accepts."""
    rows = regions(g, lambda v, c, r: "#" if keep(v, c, r) else ".")
    return sh.outlines(rows, "#", origin, smooth=smooth, epsilon=epsilon, min_area=min_area)


# --- Materials -----------------------------------------------------------------------------------

def ramp_mats(prefix, ramp, shades_, metallic=0.4, roughness=0.4):
    """Palette materials of one ramp: {shade: material}."""
    return {s: pal(f"{prefix}{s:x}", ramp * 16 + s, metallic=metallic, roughness=roughness) for s in shades_}


def glass(name, index, alpha, roughness=0.05, metallic=0.2):
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha)


def nearest(mats, s):
    """The material of mats ({shade: material}) nearest shade s."""
    key = min(mats, key=lambda x: abs(x - s))
    return mats[key]


# --- The floor -------------------------------------------------------------------------------------

FLOOR_SHADES = (1, 2, 3, 4, 5, 6, 7)


def floor_grid(g, is_floor, is_shadow, seed=3):
    """A copy of the grid keeping only floor pixels (is_floor(index, column, row)); those is_shadow accepts (the
    shadow the sprite draws on the floor) take the index of a floor pixel from rows near them that is not in
    shadow (or, in the tiles' dark grout lines, stay dark)."""
    rnd = random.Random(seed)
    out = [[None] * len(row) for row in g]
    pool = [(r, v) for r, row in enumerate(g) for c, v in enumerate(row)
            if v is not None and is_floor(v, c, r) and not is_shadow(v, c, r) and v & 15 >= 4]
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v is None or not is_floor(v, c, r):
                continue
            if is_shadow(v, c, r):
                near = [pv for pr, pv in pool if abs(pr - r) <= 2] or [pv for _, pv in pool] or [0x65]
                out[r][c] = rnd.choice(near)
            else:
                out[r][c] = v
    return out


def floor_bed(name, fg, origin, top=0.35, prefix="floor", shades_=FLOOR_SHADES, ramp=6):
    """The floor as a thin bed over the pixels of fg (floor_grid) that are not None, each pixel the floor's
    shade there (snapped to `shades_`): a flat top whose like pixels merge into few faces, its outer edges
    turned down to the ground (no bottom: the camera looks down on it)."""
    ox, oy = origin
    mats, index = [], {}
    bm = bmesh.new()
    verts = {}

    def vert(c, r):
        if (c, r) not in verts:
            verts[(c, r)] = bm.verts.new((c - ox, oy - r, top))
        return verts[(c, r)]
    for r, row in enumerate(fg):
        for c, v in enumerate(row):
            if v is None:
                continue
            shade = min(shades_, key=lambda x: abs(x - (v & 15)))
            if shade not in index:
                index[shade] = len(mats)
                mats.append(pal(f"{prefix}_{shade:x}", ramp * 16 + shade, metallic=0.05, roughness=0.85))
            face = bm.faces.new((vert(c, r + 1), vert(c + 1, r + 1), vert(c + 1, r), vert(c, r)))
            face.material_index = index[shade]
    bm.normal_update()
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f_ for f_ in bm.faces if len(f_.verts) > 3], quad_method="BEAUTY",
                          ngon_method="EAR_CLIP")
    border = [e for e in bm.edges if len(e.link_faces) == 1]
    if border:
        made = bmesh.ops.extrude_edge_only(bm, edges=border)
        down = [v for v in made["geom"] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=down, vec=(0.0, 0.0, -top))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bm.faces and sum(f_.normal.z * f_.calc_area() for f_ in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m_ in mats:
        obj.data.materials.append(m_)
    return obj


# --- Parts ---------------------------------------------------------------------------------------

def loft_axis(name, sections, mat, start, direction, up=(0, 0, 1), segments=32, power=2.0, smooth_angle=50,
              cap=True):
    """A body along any axis: sections (t, half-width, half-height[, half-height below]) along `direction` from
    `start`, each a superellipse of `power` whose width lies along direction x up (sideways) and height along
    the up vector made square to the axis."""
    d = Vector(direction).normalized()
    upv = Vector(up)
    side = d.cross(upv)
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    upv = side.cross(d).normalized()
    s0 = Vector(start)
    rings = []
    for sec in sections:
        tt, hw, hh = sec[0], sec[1], sec[2]
        hb = sec[3] if len(sec) > 3 else hh
        c0 = s0 + d * tt
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / power), c) * hw
            v = math.copysign(abs(s) ** (2 / power), s) * (hh if s >= 0 else hb)
            pts.append(c0 + side * u + upv * v)
        rings.append(pts)
    first, last = sections[0][0], sections[-1][0]
    if cap:
        obj = k.loft(name, rings, mat, start_point=s0 + d * first, end_point=s0 + d * last)
    else:
        obj = k.loft(name, rings, mat, cap_start=False, cap_end=False)
    return k.smooth(obj, smooth_angle)


def subdivide_mesh(obj, cuts=1):
    """Splits the mesh's faces (finer painting)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def torus(name, centre, major, minor, mat, segments=40, sides=10, squash=1.0, scale_y=1.0):
    return q.torus(name, centre, major, minor, mat, segments, sides, squash, scale_y)


def frame_mesh(name, outer, inner, z0, z1, mat, bevel=0.3):
    """A square frame: the ring between two rectangles (x0, x1, y0, y1), from z0 up to z1, its edges bevelled."""
    ox0, ox1, oy0, oy1 = outer
    ix0, ix1, iy0, iy1 = inner
    bm = bmesh.new()

    def ring(r, z):
        x0, x1, y0, y1 = r
        return [bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)), bm.verts.new((x1, y1, z)),
                bm.verts.new((x0, y1, z))]
    ob, ot, it, ib = ring(outer, z0), ring(outer, z1), ring(inner, z1), ring(inner, z0)
    for a, b in ((ob, ot), (ot, it), (it, ib), (ib, ob)):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        k.bevel(obj, bevel, 2)
    return k.smooth(obj, 40)


def report():
    """With the environment variable X_PARTS set: prints the parts' triangle counts, largest first."""
    if not os.environ.get("X_PARTS"):
        return
    rows = sorted(((triangles([obj]), obj.name) for obj in meshes()), reverse=True)
    print("--- parts: " + ", ".join(f"{name} {count}" for count, name in rows[:14 if os.environ["X_PARTS"] != "all" else 99]))


def drop_slivers(prefix="tiles", below=40):
    """Removes what a cut leaves of the floor bed along a piece's edge (a few faces lying in the cut's plane)."""
    for obj in meshes():
        if obj.name.startswith(prefix) and triangles([obj]) < below:
            bpy.data.objects.remove(obj, do_unlink=True)
