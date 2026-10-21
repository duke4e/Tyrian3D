"""MINERS's dark red rock spire (sheet L sprites 231 beside 233, 2x2 each: one 48 x 28 picture; enemies 1148 and 1149 of
episode 5, ground layer, armour 0: they stay; not animated), polished (2026-10-21; it replaces wave3_z_rock.py's spire,
a cone of hex cells standing upright under the drawn point, a heightfield painted by the sprite's shades). models.cfg:
model red_spire_l / red_spire_r enemies/red_spire_*.glb origin (unchanged); sprite l 231 red_spire_l yaw=0 height=-4,
sprite l 233 red_spire_r yaw=0 height=-4.

The two sprites are NOT mirror images of each other (231 is the spike's left part, its foot 12 pixels wide and dark;
233 its right part, 10 pixels, lit, with lumps on its edge), nor any other sprite's pixels mirrored, turned or in other
ramps. MINERS always puts them together as one object: its ground events (28 pairs, t1028 to t3212) create 1148 (231)
at x and 1149 (233) at x + 24 at the same time and height (y -29), so the rock is built whole and cut at their edge.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 28 picture; ramp 7's dark reds, 0x70-0x77,
speckled with 0xf6): a pinnacle of rock rising from a broad foot along the picture's bottom edge (columns 12-33 of row
27) to a blunt point at the top (columns 21-23 of row 0), seen from the front and above; its left flank smooth, sloping
straight, in shade (0x70-0x73); its right flank lit (0x74-0x77), lumpy: a rounded lump bulging out at rows 9-16 (to column
31), a second at rows 17-22 (to column 32), the foot's lit shoulder below a darker ledge (rows 21-22); dark creases
between the lumps, a darker hollow low on the left (columns 15-21 of rows 18-21).

Built as the rock the sprites lay out for the game's slanted camera: seen from straight above it covers their pixels;
its height rises from its foot's front edge (row 27) to its point at the top of the picture (row 0, ZT pixels up), a
rounded ridge down its middle and its flanks falling to the ground at the outline; the lumps bulge from its right flank
where the sprites draw them, the creases and the hollow are cut in, the sprite's fine shading becomes relief (lumps
where it is light, creases where it is dark), and smooth noise weathers it. It is a signed distance field on a grid H
pixels apart (polish_rock_arch.py's method and its surface nets): the side (the distance to the plan's outline), the top
(the height field), the underside SKIRT under the ground, met with rounded edges. Its colours are the sprite's own
shades under each face: the broad shading the sprite paints (its light from the right) kept only in part (KEEP: the
game's sun, from the upper left, shades it itself), its fine shading kept, grained a little; the speckles 0xf6; the
undersides dark. The whole is cut along the sprites' edge (x = 0) into the two pieces, the cuts capped with the rock's
dark inside (they show only through a gap: the pieces always stand together), each piece's triangles reduced with its
cut's vertices kept where they are and its normals those of the dense whole, so the halves meet exactly and shade as one
rock; each piece is moved so that its sprite's centre is its origin.

Where it stands: drawn at their origin (models.cfg origin), height=-4 sets the pieces on the terrain (as the other
polished ground models do: the rock arch, the window block; the game keeps two pieces side by side moving alike at one
height, the terrain's under their middle). The foot reaches SKIRT under the ground.

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the middle of the picture (the point where the two sprites meet, half way down): column c is x = c + 0.5 - 24, row r is
y = 13.5 - r. The pieces' centres: 231 (-12, 0), 233 (12, 0).

Replaces wave3_z_rock.py's spire: remove SPIRE = kit.frame("SPIRE", 48, (24, 14)), its section ("# --- L 231 233: the
spire": SPIRE_AXIS, SPIRE_FOOT, SPIRE_HEIGHT, spire_lobes(), spire_whole() and the kit.pieced("red_spire", ...) line)
and the red_spire paragraph of its docstring; and wave3_z_art.py's SPIRE (only that section reads it). rock_shade(),
hex_rock() and halves() stay (the mounds use them); wave3_ap_miners.py (kit.load) and wave3_at_misc.py (quiet_import)
load wave3_z_rock for the tan dome creature only.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouettes against enemy_L.png), --preview <prefix> (each piece's views), --whole <prefix> (the whole's), --only
<name,...>.
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_rock_arch import (surface_nets, finish_whole, mesh_object, noise3, smax, smoothstep, nearest,  # noqa: E402
                              fill_outside, face_data, assign, decimate, shade_like)

# The picture (231's columns 0-23, 233's 24-47): each pixel its shade of ramp 7 (palette index 0x70 + digit), b the
# brown speckles (0xf6), d the darkest browns (0x42), '.' none (the lone pixel of 233 at its far right corner, 47 of row
# 27, is the ground's and left out).
ART = """
.....................011........................
....................01440.......................
....................0345b0......................
....................03545b0.....................
...................033b6750.....................
...................035456740....................
...................024545540....................
..................0145554b30....................
..................1346656740....................
.................012b56556730...................
.................0123b655b630...................
.................0122b454b4430..................
.................01122343457540.................
.................122334642b66540................
................0122346543457540................
................0122b555643b5530................
................0122245664235b0.................
................112233545442b320................
...............0110233b4545655420...............
...............111dd23b4466776540...............
..............01221d12b3466777650...............
..............0122222132446655430...............
..............122333332234444430................
.............01233443b3b346655440...............
.............12223454443466775540...............
.............1122b446b4b3465775530..............
............0112234445453465576540..............
............1d11233455453345566543..............
"""

PIECES = [("red_spire_l", 231, (-24.0, 0.0, -14.0, 14.0), (-12.0, 0.0)),
          ("red_spire_r", 233, (0.0, 24.0, -14.0, 14.0), (12.0, 0.0))]

# The form: the point's height, the ground's edge (how high the rock's outline stands), how far it reaches under the
# ground; the ridge's rise along the picture (a share of it rising fast at the foot, the rest steadily to the point);
# the cross-section's shape (how full: the flanks' power and exponent); the edges' rounding.
ZT = 16.0
FOOT = 0.5
SKIRT = 1.0
FOOT_RISE = (0.18, 0.14)
ACROSS = (2.0, 0.55)
K_SIDE, K_BOT = 1.0, 0.6
# The lumps of the right flank and the creases and hollow (x, y, radius across, radius up the screen, height: negative
# cuts in): the upper lump (rows 9-16), the lower one (rows 17-22), the foot's shoulder, a knob under the point; the
# hollow low on the left, the ledge across below the lower lump, the crease between the lumps.
LUMPS = [(4.6, 0.6, 2.8, 3.3, 2.1), (5.7, -5.5, 3.0, 2.8, 1.9), (6.3, -11.2, 3.4, 2.4, 1.1), (1.9, 7.2, 2.0, 2.6, 0.9),
         (-4.2, -6.1, 3.0, 1.7, -1.1), (2.0, -8.4, 6.5, 0.85, -0.8), (5.2, -2.7, 2.6, 0.75, -0.6)]
# The sprite's fine shading as relief (pixels of height per shade between the fine and the middle blur), the noise
# ((amplitude, scale) of two octaves), the grid.
RELIEF = 0.28
NOISE = ((0.22, 2.6), (0.08, 1.05))
H = 0.35
X0, NX = -14.0, 78
Y0, NY = -16.0, 93
Z0, NZ = -2.0, 63
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)

# The colours: the share of the sprite's broad shading kept (round MID), the fine shading's weight, the grain.
MID, KEEP, DETAIL, DITHER = 4.0, 0.45, 1.0, 0.3
CAP = 0x72
TARGET = 3600               # triangles per piece


# --- The picture ------------------------------------------------------------------------------------------------------

def art():
    rows = ART.strip("\n").split("\n")
    shade = np.full((len(rows), 48), np.nan)
    speckle = np.zeros((len(rows), 48), bool)
    darkest = np.zeros((len(rows), 48), bool)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "b":
                shade[r, c], speckle[r, c] = 3.0, True
            elif ch == "d":
                shade[r, c], darkest[r, c] = 1.0, True
            else:
                shade[r, c] = int(ch)
    return shade, speckle, darkest


def sample(a, x, y, pad=0.0):
    """Bilinear sample of a pixel array a[row, column] (values at the pixels' centres) at whole coordinates."""
    rows, cols = a.shape
    u, v = x + 24.0 - 0.5, 13.5 - y
    c0, r0 = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - c0, v - r0

    def at(r, c):
        ok = (r >= 0) & (r < rows) & (c >= 0) & (c < cols)
        return np.where(ok, a[np.clip(r, 0, rows - 1), np.clip(c, 0, cols - 1)], pad)
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def blur(a, sigma):
    """A Gaussian blur (sigma in pixels) of a field on the grid's x, y."""
    s = sigma / H
    r = int(math.ceil(3 * s))
    kernel = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    kernel /= kernel.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(kernel):
            acc += w * (p[i:i + out.shape[0], :] if axis == 0 else p[:, i:i + out.shape[1]])
        out = acc
    return out


def contour(f, level=0.5):
    """Where a field on the grid's x, y crosses level: points (x, y)."""
    pts = []
    a, b = f[:-1, :], f[1:, :]
    i, j = np.nonzero((a - level) * (b - level) < 0)
    t = (level - a[i, j]) / (b[i, j] - a[i, j])
    pts.append(np.stack([XS[i] + t * H, YS[j]], 1))
    a, b = f[:, :-1], f[:, 1:]
    i, j = np.nonzero((a - level) * (b - level) < 0)
    t = (level - a[i, j]) / (b[i, j] - a[i, j])
    pts.append(np.stack([XS[i], YS[j] + t * H], 1))
    return np.concatenate(pts)


def sample_grid(a, x, y):
    u = np.clip((x - X0) / H, 0.0, NX - 1.001)
    v = np.clip((y - Y0) / H, 0.0, NY - 1.001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - i, v - j
    return (a[i, j] * (1 - fu) * (1 - fv) + a[i + 1, j] * fu * (1 - fv) + a[i, j + 1] * (1 - fu) * fv +
            a[i + 1, j + 1] * fu * fv)


def extents(mask):
    """The outline's left and right edges at each row's middle (x), a little smoothed: (ys ascending, lefts, rights)."""
    ys, lefts, rights = [], [], []
    for r in range(mask.shape[0]):
        cols = np.nonzero(mask[r])[0]
        ys.append(13.5 - r)
        lefts.append(cols[0] - 24.0)
        rights.append(cols[-1] + 1.0 - 24.0)
    ys, lefts, rights = (np.array(v[::-1]) for v in (ys, lefts, rights))
    kernel = np.array([0.25, 0.5, 0.25])
    lefts = np.convolve(np.pad(lefts, 1, mode="edge"), kernel, "valid")
    rights = np.convolve(np.pad(rights, 1, mode="edge"), kernel, "valid")
    return ys, lefts, rights


# --- The solid --------------------------------------------------------------------------------------------------------

def fields():
    t0 = time.time()
    shade, speckle, darkest = art()
    mask = ~np.isnan(shade)
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    mf = blur(sample(mask.astype(np.float64), gx, gy), 0.45)
    pts = contour(mf)
    (d,) = nearest(gx.ravel(), gy.ravel(), pts)
    d = d.reshape(gx.shape).astype(np.float64)
    side = np.where(mf >= 0.5, -d, d)
    # The top: the ridge's height along the picture, the flanks falling to the outline across it.
    ys, lefts, rights = extents(mask)
    xl, xr = np.interp(gy, ys, lefts), np.interp(gy, ys, rights)
    c, w = (xl + xr) / 2.0, np.maximum((xr - xl) / 2.0, 0.5)
    u = np.clip(np.abs(gx - c) / w, 0.0, 1.0)
    power, exponent = ACROSS
    g = (1.0 - u ** power) ** exponent
    t = np.clip((gy + 14.0) / 28.0, 0.0, 1.0)
    fast, span = FOOT_RISE
    crest = ZT * (fast * smoothstep(0.0, span, t) + (1.0 - fast) * t)
    top = FOOT + crest * g
    for x0, y0, rx, ry, amp in LUMPS:
        top += amp * np.exp(-((gx - x0) / rx) ** 2 - ((gy - y0) / ry) ** 2) * g ** 0.35
    filled = fill_outside(shade)
    s_px = sample(filled, gx, gy)
    fine, mid, broad = blur(s_px, 0.5), blur(s_px, 1.6), blur(s_px, 4.5)
    top += RELIEF * (fine - mid) * np.clip(3.0 * g, 0.0, 1.0)
    top = np.maximum(top, FOOT)
    # The colours: the broad shading kept in part round MID, the fine kept (softened a little, so that the patches
    # are round, not the pixels' squares); the speckles' and the darkest browns' spots, softened the same way.
    paint = MID + (broad - MID) * KEEP + DETAIL * (blur(s_px, 0.6) - broad)
    spots = blur(sample(speckle.astype(np.float64), gx, gy), 0.4)
    brown = blur(sample(darkest.astype(np.float64), gx, gy), 0.4)
    print("fields: %.1f s" % (time.time() - t0))
    return {"side": side, "top": top, "paint": paint, "mask": mask, "spots": spots, "brown": brown}


def solid(fl):
    t0 = time.time()
    z = ZS.astype(np.float32)[None, None, :]
    d = smax(fl["side"].astype(np.float32)[:, :, None], z - fl["top"].astype(np.float32)[:, :, None], K_SIDE)
    d = smax(d, np.float32(-SKIRT) - z, K_BOT).astype(np.float32)
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = XS[i], YS[j], ZS[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * noise3(x / scale, y / scale, zz / scale, 31 + n)
    detail *= np.clip((zz - 0.1) / 0.8, 0.0, 1.0)          # (none under the ground)
    d[i, j, kz] += detail.astype(np.float32)
    for axis in range(3):                                    # smoothed a little: nothing finer than the grid
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


# --- Colours ------------------------------------------------------------------------------------------------------------

def materials():
    m = {i: k.material("spire_rock", palette=i, metallic=0.0, roughness=0.85) for i in range(0x70, 0x78)}
    m[0xf6] = k.material("spire_speckle", palette=0xf6, metallic=0.0, roughness=0.8)
    m[0x42] = k.material("spire_brown", palette=0x42, metallic=0.0, roughness=0.9)
    return m


def shades(centres, normals, fl):
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    s = sample_grid(fl["paint"], x, y)
    s = s + DITHER * noise3(x / 1.2, y / 1.2, z / 1.2, 47)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 1.6), s)       # the undersides in shade
    idx = 0x70 + np.clip(np.round(s), 1, 7).astype(int)
    up = normals[:, 2] > 0.25
    idx = np.where(up & (sample_grid(fl["spots"], x, y) > 0.42), 0xf6, idx)
    idx = np.where(up & (sample_grid(fl["brown"], x, y) > 0.42), 0x42, idx)
    return idx


# --- Pieces -----------------------------------------------------------------------------------------------------------

def cut_piece(whole, box, name, cap_mat):
    """polish_rock_arch.py's cut_piece with this rock's materials: the part of the whole inside box (x0, x1, y0, y1),
    its cuts closed (caps: material slot 1, facing out of the piece). Returns the object and its vertices on the
    cuts."""
    x0, x1, y0, y1 = box
    obj = whole.copy()
    obj.data = whole.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))):
        if not bm.faces:
            break
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                     plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()

    def on_plane(co):
        return min(abs(co.x - x0), abs(co.x - x1), abs(co.y - y0), abs(co.y - y1)) < 1e-4
    bm.normal_update()
    bm.verts.index_update()
    rim = {v.index for v in bm.verts if on_plane(v.co)}
    for f in bm.faces:
        cap = all(v.index in rim for v in f.verts) and (abs(f.normal.x) > 0.999 or abs(f.normal.y) > 0.999)
        f.material_index = 1 if cap else 0
        if cap:
            f.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    obj.data.materials.append(cap_mat)
    obj.data.materials.append(cap_mat)
    return obj, rim


def piece_mask(sheet, sprite):
    full = k.sprite_mask(sheet, sprite)
    if sprite == 233:   # the ground's lone pixel at the far right corner left out
        full[27][23] = False
    return full


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_L.png") if "check" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = materials()
    fl = fields()
    d = solid(fl)
    verts, quads = surface_nets(d, (X0, Y0, Z0), H)
    whole = finish_whole(mesh_object("spire_whole", verts, quads))
    print("whole: %d vertices, %d triangles" % (len(whole.data.vertices), len(whole.data.polygons)))
    shading = mk.NormalSource(whole)
    if "whole" in options or sheet:
        preview = whole.copy()
        preview.data = whole.data.copy()
        bpy.context.scene.collection.objects.link(preview)
        centres, normals = face_data(preview)
        assign(preview, shades(centres, normals, fl), mats)
        whole.hide_render = True
        if sheet:
            mk.compare("whole (L 231 + 233)", mk.coverage([preview], 48, 28), fl["mask"].tolist())
        if "whole" in options:
            mk.preview(options["whole"] + "red_spire_whole", [preview], size=(48, 28), scale=12, distance=1.2)
        bpy.data.objects.remove(preview)
        whole.hide_render = False
    for name, sprite, box, (ox, oy) in PIECES:
        if only and name not in only:
            continue
        obj, rim = cut_piece(whole, box, name, mats[CAP])
        whole.hide_render = True
        decimate(obj, rim, TARGET)
        shade_like(obj, shading)
        centres, normals = face_data(obj)
        indices = shades(centres, normals, fl)
        flags = np.empty(len(obj.data.polygons), np.int64)
        obj.data.polygons.foreach_get("material_index", flags)
        indices[flags == 1] = CAP
        assign(obj, indices, mats)
        obj.data.transform(Matrix.Translation((-ox, -oy, 0.0)))
        obj.data.validate()
        mk.apply(obj)
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s (L %d)" % (name, sprite), mk.coverage([obj], 24, 28), piece_mask(sheet, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        whole.hide_render = False


if __name__ == "__main__":
    build()
