"""The two ends of IXMUCANE's and SAWBLADES' upright rock wall (sheet 8: the left end 169 above 207 above 245, the
right end 161 above 199 above 237; 2x2 sprites, one 24 x 84 column each, its rock in rows 4-69; enemies 115, 116, 117
and 118, 119, 120, the low ones armour 0, the others 254; on the sky, ground or top layer as the events put the wall),
polished (2026-10-22; it replaces wave3_y_wall.py's end columns: heightfields of bumps painted from the sprites in odd
shades, their rounded ends pixel staircases).

The levels build the wall from columns of three sprites, 24 pixels apart, all of one link (IXMUCANE's events 1820
(type 6), 2120 (7), 2160 (15), 2200 (10), 2320 (6); SAWBLADES' 800 (7), 1400 (7), 1500 (6), 1600 (15), 1700 (7)):
always a left end, a slot (polish_ixm_wall_slot.py), one or three rock columns (polish_ixm_wall_rock.py), a slot and a
right end, the top sprites 56 pixels above the low ones. So each end meets a slot: the left end's right edge the slot's
left one, the right end's left edge the slot's right one. There the end has the section every column shares
(polish_ixm_wall_rock's: the upright wall's top level at HEIGHT 20 from the cliff at y CLIFF -16.5 back to its rounded
back, y 22 at the top and 25.5 at the ground; the relief and weathering faded out within EDGE of the edge, its top's
front edge sharp there). No other enemy shows these sprites (catalog.json).

The right end is the left end's pixels mirrored and one row higher, shade for shade (all 562 pixels): its model is the
left end's whole mirrored (x -> -x), kept on the shared section (without the row's offset, so that it meets its slot as
the left end meets its own), cut into its pieces the same way.

As the sprites and their 4x upscales draw the left end (columns and rows of its 24 x 84 column; the tans of ramp 1):
rock only in the column's right half, its outer side rounding off. On top (rows 5-44; the top's row r stands at y 28 - r
on the upright wall, as polish_ixm_wall_rock maps it) a cluster of big round boulders, the outline curving out from the
back corner (row 5, column 22) to column 12 (rows 13-20) and running down at columns 13-14 to the cliff's edge; down the
cliff (rows 45-69; the cliff's row r at height 20 (70.5 - r) / 26) ribs of rock between dark clefts, the outline
stepping in from column 14 to 21 towards the foot: the end's front corner worn away towards the ground.

Built as the rock column is built (polish_ixm_wall_rock's fields() with the end's own pixels, ART: weathered layered
sandstone, a bed of cobbles on top, ribs down the cliff, the bedding's grooves; its surface by surface nets, its colours
the sprite's own shades under each face), with two differences: the relief, the rounding of the top's front edge and
the weathering fade out at the inner edge only (fade_inner: the outer side is the rock's own end, not a joint), and the
solid is ended at the outer side before it is weathered: cut by the end's surface (end_field: x of the top's outline
along the wall, smoothed; near the cliff the cliff's outline taken in towards the foot, FRONT_DEPTH deep; never nearer
the inner edge than END_LIMIT, where the shared section must stay whole), the edges between them rounded (END_ROUND).
The colours are polish_ixm_wall_rock.shades' (the sprite's shades, their broad shading lifted towards the middle, the
fine kept, grained, the cliff's a little lighter and banded with the bedding, the joint at the inner edge dark), taken
from the pixels without their black outline on the outer side (in the round that outline is the end's side, not a
crack: the side takes the boulders' colours, banded with the bedding as the cliff is).

The pieces are cut as the slot's are (polish_ixm_wall_slot.PIECES: as the sprites own the wall): the top piece the top
behind y 0 (the top's row 28) above the cliff's row 56, the middle piece the rest of the top and the cliff down to row
56, the low piece the cliff below and the foot behind it; so the ends' pieces meet the slots' along the same planes (the
wall's pieces all die together, their link shared; on the ground each leaves its wreck, slumped about its own origin,
and the pieces' wrecks together make the wall at half height). The whole is reduced, each piece cut from it (the cuts
capped, the faces' winding kept: polish_ixm_wall_slot.cut_planes), its triangles reduced to about TARGET with the
vertices on its cuts kept where they are and its normals those of the dense whole, then moved so that its sprite's
centre is its origin; every mesh is triangulated before export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
column's whole as polish_ixm_wall_rock's: x -12..12 (column c's left edge at x c - 12), the middle piece's centre at
y 0, the top piece's at y 28, the low piece's at y -28.

models.cfg (the model and sprite lines stay as they are): model ixm_wall_end_l_top enemies/ixm_wall_end_l_top.glb
origin (likewise _mid, _low and ixm_wall_end_r_top, _mid, _low), sprite 8 169 ixm_wall_end_l_top yaw=0, sprite 8 207
ixm_wall_end_l_mid yaw=0, sprite 8 245 ixm_wall_end_l_low yaw=0, sprite 8 161 ixm_wall_end_r_top yaw=0, sprite 8 199
ixm_wall_end_r_mid yaw=0, sprite 8 237 ixm_wall_end_r_low yaw=0.

Replaces wave3_y_wall.py, all of it (with the rock and slot columns polished, the ends were all it still exported) and
wave3_y_art.py's WALL (only wave3_y_wall.py reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each end's whole column's top
view against its sprites' top rows as the upright wall lays them out), --preview <prefix> (each model's top and 3/4
views, the wholes'), --only <model,...>.
"""
import math
import os
import sys
import time

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_ixm_wall_rock as rw  # noqa: E402
import polish_ixm_wall_slot as ws  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_rock_arch import face_data, finish_whole, mesh_object, noise3, smax, smoothstep, surface_nets  # noqa: E402

# The left end's rock pixels (8 169 above 207 above 245, rows 0-69): each its shade in ramp 1 (palette index 0x10 +
# digit; 0 also for the near-black outline and clefts of ramp 0), '.' none.
ART = """
........................
........................
........................
........................
........................
......................00
.....................006
...................00068
.................0003588
................00334588
..............0045303578
.............00999973246
.............0899aa96225
............0999aaaa8368
............06aaaab98368
............067abb988378
............0668aa887278
............066658987268
............066544566235
............065444566324
............004444565445
.............00444553269
..............004443168a
..............002431378a
.............0020022688a
.............00575137889
.............037a7316889
.............049ca726788
.............049bb834688
.............0689b523678
.............00676382467
..............04305c7235
..............00049ea415
..............00478b8533
..............0156666416
...............025653267
................02430688
...............020004798
..............00640068a9
..............037630589b
..............0489502778
..............06ba600565
..............05be702155
..............045b703235
..............0358615425
..............0347608502
..............0247609632
..............0246519632
..............0246329642
..............0244029633
...............042028624
................01047525
.................0157515
.................0256435
..................056445
..................056355
..................046375
..................035385
..................031485
..................020585
..................001575
..................003585
..................004585
..................004585
...................03785
...................03675
...................00770
...................01650
....................050.
.....................0..
"""

# The pieces: (left end's model, its sprite, the right end's model, its sprite, the half-spaces the piece keeps (point,
# outward normal): polish_ixm_wall_slot's), and its sprite's centre (y).
PIECES = [("ixm_wall_end_l_top", 169, "ixm_wall_end_r_top", 161, ws.PIECES[0][2], 28.0),
          ("ixm_wall_end_l_mid", 207, "ixm_wall_end_r_mid", 199, ws.PIECES[1][2], 0.0),
          ("ixm_wall_end_l_low", 245, "ixm_wall_end_r_low", 237, ws.PIECES[2][2], -28.0)]
SIDES = ws.SIDES             # every piece: the column's edges (x -12, 12)

# The end.
OUTLINE_BLUR = 1.1           # how much the outline is smoothed along the wall (pixels; it is a pixel staircase)
END_ROUND = 1.4              # the rounding where the top, the cliff and the back meet the end's side
FRONT_DEPTH = 7.0            # how far behind the cliff the cliff's outline, taken in towards the foot, reaches
END_LIMIT = 10.2             # the end's side never nearer the inner edge (x 12) than this: the shared section stays
SIDE_NORMAL = -0.55          # faces turned this far to the outer side are the end's side (coloured as such)
TARGET = 3200                # triangles per piece (fewer where the piece holds less rock)
WHOLE_TARGET = 18000         # the whole's triangles before it is cut


def art(text=ART):
    rows = text.strip("\n").split("\n")
    out = np.full((len(rows), 24), np.nan)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                out[r, c] = int(ch, 16)
    return out


def fade_inner(x):
    """polish_ixm_wall_rock.fade at the inner edge only (the left end's right edge, x 12): 1 inside, 0 at the edge."""
    return smoothstep(rw.EDGE[1], rw.EDGE[0], np.asarray(x, dtype=np.float64))


class InnerFade:
    """polish_ixm_wall_rock's functions with fade_inner for their fade (they look it up when called)."""

    def __enter__(self):
        self.saved = rw.fade
        rw.fade = fade_inner

    def __exit__(self, *exc):
        rw.fade = self.saved


# --- The end's surface -----------------------------------------------------------------------------------------------

def outline(shade):
    """The end's outer edge from its pixels: each row's first pixel's left edge (x), the top's rows (5-44) by their y
    on the upright wall (their middles, y 27.5 - r), the cliff's (45-69) by their height (z 20 (70 - r) / 26)."""
    known = ~np.isnan(shade)
    top, face = [], []
    for r in range(shade.shape[0]):
        if not known[r].any():
            continue
        x = float(np.argmax(known[r])) - 12.0
        if r < 45:
            top.append((27.5 - r, x))
        else:
            face.append((rw.HEIGHT * (70.0 - r) / 26.0, x))
    return top, face


def smooth_samples(samples, sigma):
    """A Gaussian smoothing of (t, value) samples one pixel apart along t (their ends held)."""
    values = np.array([v for _, v in samples], float)
    reach = int(math.ceil(3 * sigma))
    kernel = np.exp(-0.5 * (np.arange(-reach, reach + 1) / sigma) ** 2)
    kernel /= kernel.sum()
    padded = np.pad(values, reach, mode="edge")
    return [(t, float(np.dot(kernel, padded[i:i + 2 * reach + 1]))) for i, (t, _) in enumerate(samples)]


def end_field(shade):
    """The end's surface as a field on the grid (positive outside, about the distance across it): x of the top's
    outline along the wall (behind the back corner, and anywhere nearer the inner edge, END_LIMIT), near the cliff the
    cliff's outline (how far it steps in from its top) added, fading out FRONT_DEPTH behind the cliff."""
    top, face = outline(shade)
    top = smooth_samples(top, OUTLINE_BLUR)
    face = smooth_samples(face, OUTLINE_BLUR)
    ty = np.array([t for t, _ in top])[::-1]               # increasing y
    tx = np.array([v for _, v in top])[::-1]
    plan = np.interp(rw.YS, ty, tx)
    plan = np.where(rw.YS > ty[-1], END_LIMIT, plan)       # behind the back corner
    fz = np.array([t for t, _ in face])[::-1]               # increasing z
    fx = np.array([v for _, v in face])[::-1]
    step_in = np.maximum(0.0, np.interp(rw.ZS, fz, fx) - fx[-1])
    near = smoothstep(rw.CLIFF + FRONT_DEPTH, rw.CLIFF - 1.0, rw.YS)
    x_end = np.minimum(plan[:, None] + near[:, None] * step_in[None, :], END_LIMIT)
    gy = np.gradient(x_end, rw.STEP, axis=0)
    gz = np.gradient(x_end, rw.STEP, axis=1)
    norm = np.sqrt(1.0 + gy ** 2 + gz ** 2)
    return ((x_end[None, :, :] - rw.XS[:, None, None]) / norm[None, :, :]).astype(np.float32)


def solid(boulders, ribs, end):
    """polish_ixm_wall_rock.solid with the end: the column's signed distance on the grid (negative inside), the end's
    surface cutting it off (rounded END_ROUND) before the weathering; the rounding of the top's front edge and the
    weathering faded at the inner edge only."""
    t0 = time.time()
    x = rw.XS[:, None, None].astype(np.float32)
    y = rw.YS[None, :, None].astype(np.float32)
    z = rw.ZS[None, None, :].astype(np.float32)
    top = z - (rw.HEIGHT + boulders[:, :, None])
    front = (rw.CLIFF - ribs[:, None, :]) - y
    back_y = rw.BACK[0] + rw.BACK[1] * np.sqrt(np.clip(1.0 - (np.clip(z, 0.0, rw.HEIGHT) / rw.HEIGHT) ** 2, 0.0, 1.0))
    back = y - back_y
    kk = 0.03 + rw.ROUND * fade_inner(x)
    d = smax(top, front, kk)
    d = np.maximum(d, back)
    d = smax(d, end, END_ROUND)
    d = np.maximum(d, -z).astype(np.float32)
    # Weathering near the surface (polish_ixm_wall_rock.solid's, its noise the same): smooth noise, the bedding's
    # grooves round the steep faces; faded at the inner edge.
    i, j, kz = np.nonzero(np.abs(d) < 1.5)
    px, py, pz = rw.XS[i], rw.YS[j], rw.ZS[kz]
    w = fade_inner(px) * np.clip(pz / 0.8, 0.0, 1.0)
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(rw.NOISE):
        detail += amp * noise3(px / scale, py / scale, pz / scale, 167 + n)
    gz = np.gradient(d, rw.STEP, axis=2)[i, j, kz]
    wall = np.clip(1.0 - 1.3 * np.abs(gz), 0.0, 1.0)
    warp = 0.6 * noise3(px / 9.0, py / 9.0, np.full(len(i), 0.3), 5)
    phase = (pz + warp) / rw.STRATA[1] - 0.3
    detail += rw.STRATA[0] * wall * np.exp(-((phase - np.round(phase)) / 0.2) ** 2)
    d[i, j, kz] += (detail * w).astype(np.float32)
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


# --- Colours ----------------------------------------------------------------------------------------------------------

def colour_fields(shade):
    """The shades the colours take (polish_ixm_wall_rock.fields' s_top and s_face) from the pixels without their black
    outline on the outer side (each row's first run of shade 0): their neighbours' shades fill it. Where the sprite
    has no pixel inside the end's span (between the ribs' feet) the cliff is dark, as the rock column's."""
    colour = shade.copy()
    inner_gone = np.zeros(shade.shape)
    for r in range(shade.shape[0]):
        cs = np.nonzero(~np.isnan(shade[r]))[0]
        if not len(cs):
            continue
        c = cs[0]
        while c < 24 and colour[r, c] == 0:
            colour[r, c] = np.nan
            c += 1
        inner_gone[r, cs[0]:] = np.isnan(shade[r, cs[0]:])
    filled = rw.fill(colour)
    gx, gy = np.meshgrid(rw.XS, rw.YS, indexing="ij")
    s_top = rw.blur2(rw.sample(filled, gx + 12.0, 28.0 - gy), 0.45, rw.STEP)
    fx, fz = np.meshgrid(rw.XS, rw.ZS, indexing="ij")
    row = rw.FACE_ROWS[1] - (rw.FACE_ROWS[1] - rw.FACE_ROWS[0]) * np.clip(fz, 0.0, rw.HEIGHT) / rw.HEIGHT
    s_face = rw.blur2(rw.sample(filled, fx + 12.0, row), 0.3, rw.STEP)
    gone = rw.sample(inner_gone, fx + 12.0, row) > 0.5
    return s_top, np.where(gone, 0.0, s_face)


def lookup(a, u0, du, u, v0, dv, v):
    """Bilinear lookup in a field on a grid (u0 + du i, v0 + dv j)."""
    fu = np.clip((u - u0) / du, 0, a.shape[0] - 1.001)
    fv = np.clip((v - v0) / dv, 0, a.shape[1] - 1.001)
    iu, iv = np.floor(fu).astype(int), np.floor(fv).astype(int)
    tu, tv = fu - iu, fv - iv
    return (a[iu, iv] * (1 - tu) * (1 - tv) + a[iu + 1, iv] * tu * (1 - tv) + a[iu, iv + 1] * (1 - tu) * tv +
            a[iu + 1, iv + 1] * tu * tv)


def shades(centres, normals, s_top, s_face):
    """Each face's palette index (polish_ixm_wall_rock.shades, with the end's side banded with the bedding as the cliff
    is, and the joint's dark strip at the inner edge only)."""
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    up = ~((y < rw.CLIFF + 2.2) & (z < rw.HEIGHT + 0.6) & (normals[:, 1] < 0.25))
    side = normals[:, 0] < SIDE_NORMAL
    fine_t = lookup(s_top, rw.X0, rw.STEP, x, rw.Y0, rw.STEP, y)
    broad_t = lookup(rw.blur2(s_top, 3.0, rw.STEP), rw.X0, rw.STEP, x, rw.Y0, rw.STEP, y)
    fine_f = lookup(s_face, rw.X0, rw.STEP, x, rw.Z0, rw.STEP, z)
    broad_f = lookup(rw.blur2(s_face, 2.5, rw.STEP), rw.X0, rw.STEP, x, rw.Z0, rw.STEP, z)
    fine = np.where(up, fine_t, fine_f)
    broad = np.where(up, broad_t, broad_f)
    lifted = np.where(broad < 9.0, 9.0 + (broad - 9.0) * rw.DARK_KEEP, broad)
    s = lifted + rw.DETAIL * (fine - broad) + np.where(up, 0.0, rw.FACE_LIFT)
    s = s - rw.JOINT_DARK * (1.0 - fade_inner(x))
    s = s + rw.DITHER * noise3(x / 1.3, y / 1.3, z / 1.3, 41)
    s = s - rw.BANDS * np.cos(2.0 * math.pi * z / rw.STRATA[1]) * (~up | side)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 4.5), s)
    return 0x10 + np.clip(np.round(s), 3, 13).astype(int)


# --- The wholes and their pieces ------------------------------------------------------------------------------------

def build_left(mats):
    """The left end's dense whole, its reduced copy (to cut the pieces from) and its colours' fields."""
    shade = art()
    with InnerFade():
        boulders, ribs, _, _ = rw.fields(shade)
    d = solid(boulders, ribs, end_field(shade))
    verts, quads = surface_nets(d, (rw.X0, rw.Y0, rw.Z0), rw.STEP)
    del d
    whole = finish_whole(mesh_object("end_l_whole", verts, quads))
    print("whole: %d vertices, %d triangles" % (len(whole.data.vertices), len(whole.data.polygons)))
    coarse = whole.copy()
    coarse.data = whole.data.copy()
    coarse.name = coarse.data.name = "end_l_coarse"
    bpy.context.scene.collection.objects.link(coarse)
    rw.decimate(coarse, set(), WHOLE_TARGET)
    coarse.data.materials.append(mats[0x18])     # slot 0: the rock (the cuts' caps get slot 1)
    return whole, coarse, colour_fields(shade)


def mirrored(obj, name):
    """A copy of the object mirrored in x (its faces turned back outwards)."""
    c = obj.copy()
    c.data = obj.data.copy()
    c.name = c.data.name = name
    bpy.context.scene.collection.objects.link(c)
    c.data.transform(Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0)))
    c.data.flip_normals()
    c.data.update()
    return c


def piece(coarse, shading, planes, name, mats, colour, mirror):
    """One piece's rock: cut from the reduced whole (caps: slot 1), reduced with its cut edges kept, shaded as the
    dense whole, painted (a mirrored piece by the left end's colours at its mirror image)."""
    obj, rim = ws.cut_planes(coarse, planes, mats[rw.CAP], name)
    if obj is None:
        return None
    obj.hide_render = False                       # (a copy of the hidden whole)
    cap_slot = mk.slot_of(obj, mats[rw.CAP])
    flags = [1 if p.material_index == cap_slot else 0 for p in obj.data.polygons]
    obj.data.polygons.foreach_set("material_index", flags)
    share = len(obj.data.polygons) / max(1.0, len(coarse.data.polygons) / 3.0)
    rw.decimate(obj, rim, int(TARGET * min(1.0, max(0.35, share))))
    rw.shade_like(obj, shading)
    centres, normals = face_data(obj)
    if mirror:
        centres[:, 0] *= -1.0
        normals[:, 0] *= -1.0
    indices = shades(centres, normals, *colour)
    caps = np.empty(len(obj.data.polygons), np.int64)
    obj.data.polygons.foreach_get("material_index", caps)
    indices[caps == 1] = rw.CAP
    rw.assign(obj, indices, mats)
    return obj


def top_mask(sheet, sprites):
    """The column's top view as the upright wall lays out its sprites' pixels (polish_ixm_wall_slot.top_mask's way):
    the top's rows 0-44 at y 28 - r (rows 14-58 of a 24 x 84 frame round y 0), the cliff's ribs standing out two rows
    below that, only within the wall's footprint."""
    full = sum((k.sprite_mask(sheet, s) for s in sprites), [])
    rows = [[False] * 24 for _ in range(84)]
    for r in range(45):
        rows[14 + r] = list(full[r])
    for extra in (59, 60):
        rows[extra] = [full[44][c] and full[45][c] for c in range(24)]
    for row in range(84):
        yc = 42.0 - (row + 0.5)
        if not rw.CLIFF - 2.5 <= yc <= rw.BACK[0] + rw.BACK[1]:
            rows[row] = [False] * 24
    return rows


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = rw.materials()
    t0 = time.time()
    whole_l, coarse_l, colour = build_left(mats)
    whole_r, coarse_r = mirrored(whole_l, "end_r_whole"), mirrored(coarse_l, "end_r_coarse")
    print("wholes: %.1f s, reduced to %d triangles" % (time.time() - t0, len(coarse_l.data.polygons)))
    sheet = os.path.join(options["check"], "enemy_8.png") if "check" in options else None
    ends = (("l", whole_l, coarse_l, (169, 207, 245), False), ("r", whole_r, coarse_r, (161, 199, 237), True))
    for side, whole, coarse, sprites, mirror in ends:
        for obj in (whole_l, coarse_l, whole_r, coarse_r):
            obj.hide_render = obj is not coarse
        if sheet:
            mk.compare("whole %s end (8 %d above %d above %d, the top's pixels as the upright wall lays them out)" %
                       ((side,) + sprites), mk.coverage([coarse], 24, 84), top_mask(sheet, sprites))
        if "preview" in options:
            mk.preview(options["preview"] + "ixm_wall_end_%s_whole" % side, [coarse], size=(24, 84), scale=8,
                       distance=2.0)
        shading = mk.NormalSource(whole)
        for obj in (whole_l, coarse_l, whole_r, coarse_r):
            obj.hide_render = True
        for name_l, _, name_r, _, keep, centre in PIECES:
            name = name_r if mirror else name_l
            if only and name not in only:
                continue
            obj = piece(coarse, shading, SIDES + keep, name, mats, colour, mirror)
            if obj is None:
                print("== %s: nothing" % name)
                continue
            obj.data.transform(Matrix.Translation((0.0, -centre, 0.0)))
            obj.data.validate()
            triangulate([obj])
            bpy.context.view_layer.update()
            mk.report(name, [obj], os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, [obj])
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
