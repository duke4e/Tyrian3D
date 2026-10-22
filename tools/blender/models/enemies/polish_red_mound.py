"""MINERS's two horns of dark red rock (sheet L sprites 234 beside 236 and 271 beside 273, 2x2 each; enemies 1144-1147
of episode 5, ground layer, armour 0: they stay; not animated), polished (2026-10-22, round 31; it replaces
wave3_z_rock.py's mounds, ridges of hex cells along the sprites' bottom edge, a heightfield painted by the sprite's
shades). models.cfg:
model red_mound_a_l / red_mound_a_r / red_mound_b_l / red_mound_b_r enemies/red_mound_*.glb origin (unchanged);
sprite l 234 red_mound_a_l yaw=0 height=-4, the same for 236 (red_mound_a_r), 271 (red_mound_b_l), 273 (red_mound_b_r).

What they are (the level events and the map): MINERS's ground events put 1144 (234) at x and 1145 (236) at x + 24 at the
same time and height (y -29), 9 times (t 300 to 972), and 1146 (271) at x, 1147 (273) at x + 24, 9 times (t 272 to 944),
always on the map's row above a pair of tiles of its own: under 234/236 the tiles 466 467, under 271/273 the tiles 456
457; the map has each pair exactly 9 times, every one under its sprites (the same as the spire: 231/233 over the tiles
468 469, 19 times). The tiles draw a curved horn of the hex rock lying out of the sand, its shadow on the sand beside
it, and the sprites draw the horn's top (the crest, rows 22-27 of their 28), which reaches up out of the tiles' row: the
level draws one object, half sprites, half map. In 3D the map's tiles lie flat on the plateau (tools/terrain/levels.json
keeps them at height 0), so the crest alone, raised over a flat picture of the horn, would show a lump on a painting
(the old mounds did): the model is the WHOLE horn, the crest from the sprites and its body from the tiles under them,
standing on the painted horn and covering it in the camera's view (the painted shadow stays on the sand beside it).
CORAL lists 1144 among its random enemies but turns them off at its start (event 13): only MINERS shows them. No episode
6 level takes MINERS's ground objects (CRUSTGATE takes its mid-boss only). The second horn is the first's pixels
mirrored exactly (sprites and tiles: 271/273 are 236/234 mirrored, 456/457 are 467/466): it is the first model
mirrored about x 0 (red_mound_b_l = red_mound_a_r mirrored, red_mound_b_r = red_mound_a_l). No other enemy, launched
ones included, shows these sprites.

As the sprites, the tiles and their 4x upscales draw the first horn (columns and rows of the 48 x 56 picture: the
sprites' row over the tiles' row; ramp 7's dark reds 0x70-0x77, speckled with 0xf6, its darkest bits 0x42): a thick
horn rising out of the sand at the lower left (its root, columns 2-17 of rows 36-52, breaking up into dark claws dug
into the sand, rows 46-52), arching up to the right into a long crest (rows 22-30, columns 11-42: lit along its top,
0x75-0x77, its underside in deep shade, 0x70-0x71), and hooking down at the right into a thin tip (columns 40-46 of
rows 27-33), which hangs over the sand: the shadow lies on the sand a gap below the arch and the tip; the body's plates
(the hex rock's cells) bulge, lit, between dark creases.

Built as that horn, a curved tusk of the rock: along a spine from the root to the tip, its cross-section a rounded tube
(half its plan's width high over the spine's height and as deep under it), the spine rising from under the sand at the
root to the crest and sinking a little to the tip, so that the arch's underside lifts off the sand from the crest on and
the tip hangs ZC(1) - its radius over it; every pixel of the horn at least a low rounded rim (the root's claws). On it:
the hex rock's plates (Voronoi cells round the points of a jittered hexagonal grid CELL apart, seeded: the same every
run), their middles bulging, their seams sunk; the picture's fine shading as relief (lumps where it is light, creases
where it is dark); smooth noise. The rock reaches SKIRT under the sand. It is a signed distance field on a grid H pixels
apart (polish_rock_arch.py's surface nets, as polish_red_spire.py's rock), designed in the picture's plane (x, y as the
picture draws them, z up) and then sheared along the game camera's line of sight (y - z tan 20, VIEW_TILT:
polish_lava_grub.py's way), so that the camera sees every point where the picture draws it (the crest where the sprites
draw it, the body over the painted horn), however high it stands. Its colours are the picture's own shades under each
face (the faces' points taken back into the picture's plane): the broad shading kept in part round MID (KEEP: the game's
sun, from the upper left, shades it itself), the fine shading kept, grained a little, the plates' seams a shade darker
and their middles lighter, no face more than DARK_KEEP shades lighter than the picture under it (the root's claws stay
dark); the speckles 0xf6 and the darkest 0x42 where the picture has them; the undersides dark. The whole is cut along
the sprites' edge (x = 0) into the two pieces, the cuts capped with the rock's dark inside (CAP: they show only through
a gap, the pieces always stand together), each piece's triangles reduced with its cut's vertices kept and its normals
those of the dense whole, so that the halves meet exactly and shade as one rock; each piece is moved so that its
sprite's centre is its origin, and holds its half of the whole horn: the crest its sprite draws and, under it, the body
the map's tile draws there. Every mesh is triangulated before the export (polish_k_pod.triangulate) and the checks work
on copies: the output is the same with and without --check.

Where it stands: drawn at their origin (models.cfg origin), height=-4 sets the pieces on the terrain (the game keeps two
pieces side by side moving alike at one height, the terrain's under their middle; MINERS's terrain is level there, 0).

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the middle of the sprites' row (the point where the two sprites meet, half way down): column c of the picture is
x = c + 0.5 - 24, row r is y = 13.5 - r (rows 28-55, the tiles' row, are y -14.5 .. -41.5). The pieces' centres: the
left sprite's (-12, 0), the right one's (12, 0).

Replaces wave3_z_rock.py's mounds: remove MOUND_A, MOUND_B, the section "# --- L 234 236 and L 271 273: the mounds"
(mound() and the two kit.pieced("red_mound_a"/"red_mound_b", ...) lines), the red_mound_a/_b paragraph of its
docstring, and wave3_z_art.py's MOUND_A and MOUND_B (only those lines read them); rock_shade(), hex_rock() and halves()
go with them (only the mounds used them), and so can wave3_z_kit.py's section "# --- MINERS's hex rock" (SQRT3,
hex_cell(), cell_jitter(), hex_rock_paint(), lava_rock_mats(): only hex_rock() called them). The rest stays: the tan
dome creature (wave3_ap_miners.py loads wave3_z_rock with kit.load, wave3_at_misc.py with quiet_import, both for
dome_whole() and DOME only) and the kit (wave3_z_small, wave3_z_train, wave3_z_station, wave3_ah_kit use it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's silhouette as the
camera sees it against the horn's pixels, each piece's against its sprite's own pixels and against its half of the
horn), --preview <prefix> (each piece's views), --whole <prefix> (the whole's views and its GLB, for looking at),
--only <name,...>.
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
from polish_k_pod import triangulate  # noqa: E402

# The first horn's picture, rows 22-52 of its 48 x 56 (rows 0-27: sprites 234 and 236; rows 28-55: the map's tiles 466
# and 467 under them, as MINERS draws them): each pixel its shade of ramp 7 (palette index 0x70 + digit), b the brown
# speckles (0xf6), d the darkest browns (0x42), g the tile's one dark tan pixel (0x11, taken as the darkest), '.' none
# (the sand and the horn's shadow on it, ramp 4: the map's, left out).
ART = """
......................000111111d................
...................21211d2333332221.............
................d12b33322b46644434b2234.........
..............01123453b33b667766476524455.......
.............0d223455645446667653564224665......
...........2001233b666553345544322bb1134665.....
.........112d112b445775522323321111200d24565....
........011221113445544b1d011ddd0d00000013454...
.......01133321123344332d000ddd0000.....0d1344..
.......1123443311232322d00d00000...........d33b.
......1222334543111111d0000.................d12.
......233233b544222d0d0d0....................12.
.....1233223b44223221d10........................
.....1233222b422222111..........................
....123322b33211211211..........................
....12332bbbb2d011ddd...........................
....02322bb553100000............................
...1dd121bbb432d0000............................
...1233bb3b33311dg0.............................
..012445b1122211000.............................
..012365b21111d0d0..............................
..0d23b5b112221000..............................
..0023bb212121d00...............................
..002233122222d00...............................
..01.3b222221dd0................................
..0..43.12221d00................................
..0..b3..112.dd0................................
....dd1...0d..d0................................
.....000..00...1................................
.....dd....00...................................
...........00...................................
"""
ART_TOP = 22                # the picture's row of ART's first line
SPRITE_ROWS = 28            # the picture's rows 0-27 are the sprites'

# The pieces: model, sprite, the first or the second horn, the piece's box in the whole (x0, x1), its sprite's centre.
PIECES = [("red_mound_a_l", 234, "a", (-24.0, 0.0), (-12.0, 0.0)),
          ("red_mound_a_r", 236, "a", (0.0, 24.0), (12.0, 0.0)),
          ("red_mound_b_l", 271, "b", (-24.0, 0.0), (-12.0, 0.0)),
          ("red_mound_b_r", 273, "b", (0.0, 24.0), (12.0, 0.0))]

VIEW_TILT = math.radians(20.0)          # the game camera's angle off straight down (from the bottom of the screen)
SHEAR = math.tan(VIEW_TILT)

# The spine (x, y in the picture's plane) from the root to the tip, and the spine's height along it (at fractions of
# its length): under the sand at the root, rising to the crest, sinking a little to the tip.
SPINE = [(-15.0, -34.0), (-14.6, -29.5), (-13.2, -25.5), (-11.1, -21.6), (-8.6, -18.6), (-5.2, -16.1), (-0.6, -14.2),
         (4.5, -13.1), (9.5, -13.1), (14.0, -14.0), (17.4, -15.1), (19.9, -16.6), (21.4, -18.2), (22.2, -19.7)]
ZC = [(0.0, -1.6), (0.14, 0.6), (0.32, 2.9), (0.5, 4.3), (0.7, 4.7), (0.86, 4.5), (1.0, 4.1)]
KZ, KB = 0.8, 0.75          # the tube's height over the spine and depth under it, as shares of its half-width
FOOT_H, FOOT_W = 0.75, 1.1  # every pixel of the horn at least a rim this high, rounded over this far from its edge
# The plates (the hex rock's cells): Voronoi cells round seeds on a jittered hexagonal grid CELL apart, their seams
# sunk SEAM_DEPTH over SEAM_W pixels, their middles bulging BULGE; the seams' and the middles' colours (shades).
CELL, JITTER, SEAM_DEPTH, SEAM_W, BULGE = 4.3, 0.32, 0.55, 0.9, 0.35
SEAM_SHADE, BULGE_SHADE = 1.1, 0.35
SKIRT = 1.0                 # how far the rock reaches under the sand
K_SIDE, K_TOP, K_BOT = 0.9, 0.7, 0.6
# The picture's fine shading as relief (pixels of height per shade between the fine and the middle blur), the noise
# ((amplitude, scale) of two octaves), the grid.
RELIEF = 0.3
NOISE = ((0.22, 2.6), (0.08, 1.05))
H = 0.35
X0, NX = -25.2, 145
Y0, NY = -42.0, 106
Z0, NZ = -2.1, 40
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)

# The colours: the share of the picture's broad shading kept (round MID), the fine shading's weight, the grain.
MID, KEEP, DETAIL, DITHER = 3.6, 0.5, 1.0, 0.3
DARK_KEEP = 1.2             # no face more than this many shades lighter than the picture's own shade under it
CAP = 0x71
TARGET = 5000               # triangles per piece


# --- The picture ------------------------------------------------------------------------------------------------------

def art():
    """The horn's shades, speckles and darkest pixels as 56 x 48 arrays (rows of the whole picture)."""
    shade = np.full((56, 48), np.nan)
    speckle = np.zeros((56, 48), bool)
    darkest = np.zeros((56, 48), bool)
    for i, line in enumerate(ART.strip("\n").split("\n")):
        r = ART_TOP + i
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "b":
                shade[r, c], speckle[r, c] = 3.0, True
            elif ch in "dg":
                shade[r, c], darkest[r, c] = 0.5, True
            else:
                shade[r, c] = int(ch)
    return shade, speckle, darkest


def sample(a, x, y, pad=0.0):
    """Bilinear sample of a pixel array a[row, column] of the whole picture (values at the pixels' centres)."""
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


def spine_coordinate(px, py):
    """For points (px, py): the fraction of the spine's length at the nearest point of the spine."""
    pts = np.array(SPINE, float)
    seg = pts[1:] - pts[:-1]
    lengths = np.hypot(seg[:, 0], seg[:, 1])
    arc = np.concatenate([[0.0], np.cumsum(lengths)])
    best = np.full(px.shape, np.inf)
    along = np.zeros(px.shape)
    for i in range(len(seg)):
        t = np.clip(((px - pts[i, 0]) * seg[i, 0] + (py - pts[i, 1]) * seg[i, 1]) / lengths[i] ** 2, 0.0, 1.0)
        dist = np.hypot(px - pts[i, 0] - t * seg[i, 0], py - pts[i, 1] - t * seg[i, 1])
        better = dist < best
        best = np.where(better, dist, best)
        along = np.where(better, arc[i] + t * lengths[i], along)
    return along / arc[-1]


def spine_points(step=0.25):
    pts = np.array(SPINE, float)
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.ceil(np.hypot(*(b - a)) / step)))
        for i in range(n):
            out.append(a + (b - a) * i / n)
    out.append(pts[-1])
    return np.array(out)


def plates(gx, gy):
    """The plates' seams (1 on a seam, 0 a SEAM_W from it) and their middles (1 at a seed, 0 a CELL from it)."""
    rng = np.random.default_rng(1145)
    seeds = []
    row_h = CELL * math.sqrt(3.0) / 2.0
    for j in range(int((-4.0 - Y0) / row_h) + 2):
        for i in range(int(52.0 / CELL) + 2):
            x = -26.0 + i * CELL + (CELL / 2.0 if j % 2 else 0.0)
            y = Y0 + j * row_h
            seeds.append((x, y))
    seeds = np.array(seeds) + rng.uniform(-JITTER, JITTER, (len(seeds), 2)) * CELL
    p = np.stack([gx.ravel(), gy.ravel()], 1)
    d2 = ((p[:, None, :] - seeds[None, :, :]) ** 2).sum(-1)
    part = np.partition(d2, 1, axis=1)
    d1, dd = np.sqrt(part[:, 0]), np.sqrt(part[:, 1])
    seam = 1.0 - smoothstep(0.0, SEAM_W, dd - d1)
    middle = np.clip(1.0 - (d1 / CELL) ** 2, 0.0, 1.0)
    return seam.reshape(gx.shape), middle.reshape(gx.shape)


def circ(t):
    """A quarter circle from the edge (t 0) to the top (t 1)."""
    t = np.clip(t, 0.0, 1.0)
    return np.sqrt(np.maximum(0.0, 2.0 * t - t * t))


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
    e = np.maximum(-side, 0.0)
    # The tube's half-width along the spine (the plan's depth at the spine), smoothed, and its height there.
    sp = spine_points()
    sp_s = spine_coordinate(sp[:, 0], sp[:, 1])
    sp_r = sample_grid(e, sp[:, 0], sp[:, 1])
    kernel = np.ones(9) / 9.0
    sp_r = np.convolve(np.pad(sp_r, 4, mode="edge"), kernel, "valid")
    s = spine_coordinate(gx, gy)
    radius = np.maximum(np.interp(s, sp_s, sp_r), 0.6)
    zc = np.interp(s, [p[0] for p in ZC], [p[1] for p in ZC])
    g = circ(np.minimum(e, radius) / radius)
    top = zc + KZ * radius * g
    bottom = zc - KB * radius * g
    top = np.maximum(top, FOOT_H * circ(np.minimum(e, FOOT_W) / FOOT_W))
    filled = fill_outside(shade)
    s_px = sample(filled, gx, gy)
    fine, mid, broad = blur(s_px, 0.5), blur(s_px, 1.6), blur(s_px, 4.5)
    top += RELIEF * (fine - mid) * np.clip(3.0 * g, 0.0, 1.0)
    seam, middle = plates(gx, gy)
    lift = np.clip(2.5 * g, 0.0, 1.0)
    top += (BULGE * middle - SEAM_DEPTH * seam) * lift
    # The colours: the broad shading kept in part round MID, the fine kept (softened a little, so that the patches are
    # round, not the pixels' squares); the speckles' and the darkest browns' spots, softened the same way.
    local = blur(s_px, 0.6)
    paint = MID + (broad - MID) * KEEP + DETAIL * (local - broad)
    paint += (BULGE_SHADE * middle - SEAM_SHADE * seam) * lift
    paint = np.minimum(paint, local + DARK_KEEP)        # (the picture's dark parts stay dark: the root's claws)
    spots = blur(sample(speckle.astype(np.float64), gx, gy), 0.4)
    brown = blur(sample(darkest.astype(np.float64), gx, gy), 0.4)
    print("fields: %.1f s (radius %.1f .. %.1f)" % (time.time() - t0, sp_r.min(), sp_r.max()))
    return {"side": side, "top": top, "bottom": bottom, "paint": paint, "mask": mask, "spots": spots, "brown": brown}


def solid(fl):
    t0 = time.time()
    z = ZS.astype(np.float32)[None, None, :]
    d = smax(fl["side"].astype(np.float32)[:, :, None], z - fl["top"].astype(np.float32)[:, :, None], K_SIDE)
    d = smax(d, fl["bottom"].astype(np.float32)[:, :, None] - z, K_TOP)
    d = smax(d, np.float32(-SKIRT) - z, K_BOT).astype(np.float32)
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = XS[i], YS[j], ZS[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * noise3(x / scale, y / scale, zz / scale, 53 + n)
    detail *= np.clip((zz - 0.1) / 0.8, 0.0, 1.0)          # (none under the ground)
    d[i, j, kz] += detail.astype(np.float32)
    for axis in range(3):                                    # smoothed a little: nothing finer than the grid
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


def shear_to_camera(obj, sign=-1.0):
    """Moves every point along the camera's line of sight: y - z tan 20 (sign -1; +1 undoes it)."""
    mesh = obj.data
    co = np.empty(3 * len(mesh.vertices))
    mesh.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co[:, 1] += sign * SHEAR * co[:, 2]
    mesh.vertices.foreach_set("co", co.ravel())
    mesh.update()


def mirror(src, name):
    """The object mirrored about x = 0 (its faces' winding turned, so that they face out)."""
    obj = src.copy()
    obj.data = src.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        v.co.x = -v.co.x
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    obj.data.update()
    return obj


# --- Colours ----------------------------------------------------------------------------------------------------------

def materials():
    m = {i: k.material("mound_rock", palette=i, metallic=0.0, roughness=0.85) for i in range(0x70, 0x78)}
    m[0xf6] = k.material("mound_speckle", palette=0xf6, metallic=0.0, roughness=0.8)
    m[0x42] = k.material("mound_brown", palette=0x42, metallic=0.0, roughness=0.9)
    return m


def shades(centres, normals, fl, flip):
    """Each face's palette index: the picture's colours under it (its point taken back into the picture's plane, and
    mirrored for the second horn)."""
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    px, py = flip * x, y + SHEAR * z
    s = sample_grid(fl["paint"], px, py)
    s = s + DITHER * noise3(px / 1.2, py / 1.2, z / 1.2, 59)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 1.4), s)       # the undersides in shade
    idx = 0x70 + np.clip(np.round(s), 0, 7).astype(int)
    up = normals[:, 2] > 0.25
    idx = np.where(up & (sample_grid(fl["spots"], px, py) > 0.42), 0xf6, idx)
    idx = np.where(up & (sample_grid(fl["brown"], px, py) > 0.42), 0x42, idx)
    return idx


# --- Pieces -----------------------------------------------------------------------------------------------------------

def cut_piece(whole, x0, x1, name, cap_mat):
    """The part of the whole between x0 and x1, its cuts closed (caps: material slot 1, facing out of the piece; the
    faces' winding kept). Returns the object and its vertices on the cuts."""
    obj = whole.copy()
    obj.data = whole.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0))):
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
        return min(abs(co.x - x0), abs(co.x - x1)) < 1e-4
    bm.normal_update()
    bm.verts.index_update()
    rim = {v.index for v in bm.verts if on_plane(v.co)}
    for f in bm.faces:
        cap = all(v.index in rim for v in f.verts) and abs(f.normal.x) > 0.999
        f.material_index = 1 if cap else 0
        if cap:
            f.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    obj.data.materials.append(cap_mat)
    obj.data.materials.append(cap_mat)
    return obj, rim


def view_coverage(objects, w, h, centre):
    """What the game's camera sees of the objects, in the picture's pixels: their top view with the shear undone (on
    copies: undoing and redoing it would move the points by rounding, and the output must not depend on --check)."""
    copies = []
    for obj in objects:
        c = obj.copy()
        c.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(c)
        shear_to_camera(c, +1.0)
        copies.append(c)
    covered = mk.coverage(copies, w, h, centre=centre)
    for c in copies:
        data = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(data)
    return covered


def horn_mask(fl, flip, c0=0, c1=48, r0=0, r1=56):
    m = fl["mask"][:, ::-1] if flip < 0 else fl["mask"]
    return m[r0:r1, c0:c1].tolist()


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
    whole_a = finish_whole(mesh_object("horn_a", verts, quads))
    shear_to_camera(whole_a)
    whole_a.data.update()
    whole_b = mirror(whole_a, "horn_b")
    wholes = {"a": (whole_a, 1.0), "b": (whole_b, -1.0)}
    print("whole: %d vertices, %d triangles" % (len(whole_a.data.vertices), len(whole_a.data.polygons)))
    sources = {key: mk.NormalSource(obj) for key, (obj, _) in wholes.items()}
    if "whole" in options or sheet:
        for key, (obj, flip) in wholes.items():
            preview = obj.copy()
            preview.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(preview)
            centres, normals = face_data(preview)
            assign(preview, shades(centres, normals, fl, flip), mats)
            for o, _ in wholes.values():
                o.hide_render = True
            if sheet:
                mk.compare("whole %s as the camera sees it (the sprites and the tiles' horn)" % key,
                           view_coverage([preview], 48, 56, (0.0, -14.0)), horn_mask(fl, flip))
            if "whole" in options:
                mk.preview(options["whole"] + "red_mound_whole_" + key, [preview], size=(48, 56), scale=12,
                           distance=1.3, centre=(0.0, -14.0))
                if key == "a":
                    triangulate([preview])
                    mk.export([preview], options["whole"] + "red_mound_whole_a.glb")
            bpy.data.objects.remove(preview)
            for o, _ in wholes.values():
                o.hide_render = False
    for name, sprite, key, (x0, x1), (ox, oy) in PIECES:
        if only and name not in only:
            continue
        whole, flip = wholes[key]
        obj, rim = cut_piece(whole, x0, x1, name, mats[CAP])
        for o, _ in wholes.values():
            o.hide_render = True
        decimate(obj, rim, TARGET)
        shade_like(obj, sources[key])
        centres, normals = face_data(obj)
        indices = shades(centres, normals, fl, flip)
        flags = np.empty(len(obj.data.polygons), np.int64)
        obj.data.polygons.foreach_get("material_index", flags)
        indices[flags == 1] = CAP
        assign(obj, indices, mats)
        if sheet:
            c0 = 0 if x0 < 0 else 24
            mk.compare("%s (L %d) as the camera sees it, its sprite's own pixels" % (name, sprite),
                       view_coverage([obj], 24, 28, (ox, oy)), k.sprite_mask(sheet, sprite))
            mk.compare("%s (L %d) as the camera sees it, its half of the horn (sprite and tile)" % (name, sprite),
                       view_coverage([obj], 24, 56, (ox, oy - 14.0)), horn_mask(fl, flip, c0, c0 + 24))
        obj.data.transform(Matrix.Translation((-ox, -oy, 0.0)))
        obj.data.validate()
        mk.apply(obj)
        triangulate([obj])
        bpy.context.view_layer.update()
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], size=(24, 56), scale=12, centre=(0.0, -14.0))
        bpy.data.objects.remove(obj)
        for o, _ in wholes.values():
            o.hide_render = False


if __name__ == "__main__":
    build()
