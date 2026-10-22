"""IXMUCANE's stone maw and the stone spike it spits (sheet 8: sprite 9 above sprite 45, 2x2 each, one 24 x 56 picture;
enemies 106 (9 11 13 15 17 47 49 51 53 55 85) and 107 (45 45 45 45 45 45 87 89 91 93 123) of episode 3, in the sky;
nine pairs, the second 28 pixels below the first, of one link: IXMUCANE's events 1339/1353, 1493/1507, 1703/1717 (type
15, moving down 2 pixels a tick: background 2's speed), each pair's animation run once by an event 24 a few ticks
later, a frame a tick, then an event 20 that speeds the pair up down the screen), modelled (2026-10-22; until now they
had no model and were drawn as flat volumes).

What they are: background 2's tile 469 coming alive. Background 2 is IXMUCANE's floating ridges of cobbled rock (a solid
in the 3D view, its top 16 pixels over the ground); along the front of a branch of them sit stone maws (tile 469: nine
of them, at rows 494 (columns 4, 8), 483 (6, 8, 10) and 468 (4, 6, 8, 10)), and each pair is made exactly over one of
them: sprite 9 is the tile, pixel for pixel (all 562 pixels; drawn 1-3 pixels lower, by the events' timing). The
animation pushes a stone spike out of the maw's throat: it comes out from under the maw's upper rim (11: its point at
row 11), slides down the screen over the floor of the mouth and the lower jaw's fangs (13 17 47: the point at rows 18,
26, 27), on over the ridge's edge into the lower sprite (87 89 91 93: its point at rows 33, 38, 45, 53 of the picture),
and is out (85 above 123: the maw gone, the tile left behind on the ridge; the spike whole: a mushroom-shaped cap of
smooth stone at its back, a neck, a body of cobbles tapering to its point), then shoots down the screen at the player,
faster and faster. 45 is blank. No other enemy shows any of these sprites (catalog.json); none is another sprite's
pixels mirrored or turned.

Built for the game's camera (ramp 1's tans, as the ridges' rock):
- the maw (ixm_maw, every frame of 106 but 85): a relief of the tile on the ridge's top, a solid sampled on a grid STEP
  apart: its plan the tile's pixels (the fangs hanging over the ridge's edge), its top the sprite's shading as height
  (MAW_RELIEF: the dark mouth its floor, the cobbles of its rim and cheeks and the fangs of its lower jaw standing up as
  light as they are drawn), flat at the tile's top and side edges where the ridge goes on, a skirt down under the
  ridge's bevelled edge; its surface by surface nets, reduced, shaded with the dense surface's normals, painted with the
  sprite's own shades under each face (the broad shading lifted, the fine kept; the mouth dark);
- the spike: a solid lying along the screen's y (as drawn whole in 85 above 123: its outline's half-widths along it, an
  oval section SPIKE_FLAT as high as it is wide, its cap a smooth dome, its body's cobbles standing out, one round
  each light blob of its sprite (COBBLES: a Voronoi diagram of the blobs, polish_ixm_wall_rock's way)), painted with its
  sprite's shades; in each frame it lies where the frame draws its point (POSES: the point's y, how much lower it lies,
  the spike pitched down behind it into the throat), cut off where it is inside the ridge's rock behind the mouth
  (CLIP), and the picture is cut along the sprites' common edge (y 0): what lies above is 106's model (with the maw),
  below 107's.
The models are drawn at their own origins (origin) and lowered onto background 2's solid with height=-42: in IXMUCANE
the layers above the ground's enemies stand TERRAIN_HEADROOM (36) higher, so the sky enemies' plane is 58 pixels up and
the ridges' solid top (render_gpu.c solid_top(2): 0.4 x (58 - 6 - 12)) 16: 42 below it (the renderer aligns an object by
its own height, so the maw then lies on its tile exactly); without the height the maw would hover 42 pixels over its
tile with its shadow far beside it. The spike flies off at the ridges' height (16-28 pixels over the ground).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up (z 0: the ridge's top plane); the
picture's are the pieces' sprites side by side: y 0 their common edge, 106's centre at y 14, 107's at -14; column c is
x = c + 0.5 - 12, the picture's row R is y = 27.5 - R.

models.cfg (new): model ixm_maw enemies/ixm_maw.glb origin, model ixm_maw_11 ... (likewise _13 _15 _17 _47 _49 _51 _53
_55 _85), model ixm_maw_low enemies/ixm_maw_low.glb origin, model ixm_maw_low_87 ... (likewise _89 _91 _93 _123);
sprite 8 9 ixm_maw yaw=0 height=-42, sprite 8 45 ixm_maw_low yaw=0 height=-42, frame 8 11 ixm_maw_11 (likewise 13 15 17
47 49 51 53 55 85), frame 8 87 ixm_maw_low_87 (likewise 89 91 93 123). ixm_maw_low (sprite 45, blank) is one tiny
triangle under the ridge's top plane (the renderer refuses a model without triangles).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's top view against
its sprite), --preview <prefix> (each model's top and 3/4 views), --only <model,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_ixm_wall_rock as rw  # noqa: E402
import polish_ixm_wall_slot as ws  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_rock_arch import face_data, finish_whole, mesh_object, noise3, smax, smoothstep, surface_nets  # noqa: E402

# The maw (8 9 = background 2's tile 469): each pixel its shade in ramp 1 (palette index 0x10 + digit; 0 also for the
# near-black of ramp 0), '.' none.
MAW = """
213475332342233355753003
2257b9505885069947d86424
4259bb7479bc29bb54676435
2037a9401234036961276424
1232530000000025415ab613
065100000000000000499502
097000000000000000033201
075000000000000000000001
032000000000000010001021
001001000000000020002372
000012000000000021003691
0011220010001000310037a0
025a53001000200041002350
035cc4002000300162200210
023895102001510264810012
023652047114741279401241
0237304ac14ada3276202341
0237006cb08ceb4033013341
013502563036742002123352
000023310044631012335200
0...0310003463202335510.
....030..02462202345300.
.....0...0145210235500..
..........03510025520...
..........02300.03400...
...........000..0110....
............0....00.....
"""

# The spike whole (8 85 above 123, the picture's rows 0-51).
SPIKE = """
........0000000.........
......00677777600.......
.....057aaaa9887500.....
....079cedbbba88851.....
...089abbba999998860....
...0789aa88888888660....
...05888888877654450....
...03787777675333340....
....0276666753333440....
....0124358643344430....
.....003469742333320....
.....00047b95441000.....
.....0354777888400......
.....026a48a767830......
.....006b9c87658310.....
.....00689c97667330.....
.....00587bc76742210....
.....047688744332230....
.....07a977b87544310....
....0389a98c88745320....
....06988b7ca6733340....
....08878c89a9853330....
....0757bb8999988220....
...0356ac8988669d430....
...004ac8ccb966ac540....
...020469aadc7ae8550....
...0775aa89bf9a96430....
...0685a999bf6785340....
...0322accdec6682550....
....0036bcebb5672450....
....01466656c9782110....
....034976798db7320.....
....0639daac9a85410.....
....0858aefe8855410.....
....08868cfb7875330.....
....0ab77bc87a832120....
....07c959a89e502220....
....05aa59aadb424520....
....0588499b97424410....
....0357375896414330....
....011549b68631320.....
.....05b87d96630100.....
.....048a7b86620000.....
.....0178598641100......
......066487541100......
......03137654110.......
.......0126653020.......
........01554310........
........0235410.........
.........023020.........
..........0210..........
...........00...........
"""

# The maw's relief: its floor's height (the mouth), the height a shade adds, the blur of the shading, the height at the
# tile's top and side edges (where the ridge goes on, faded within MAW_EDGE pixels), the skirt's depth under the ridge's
# top plane (its edges are bevelled 4 down), the rounding of its edges.
MAW_RELIEF = (1.0, 0.5, 0.5)
MAW_FLAT, MAW_EDGE = 0.6, (2.6, 2.2)
SKIRT = -4.6
MAW_ROUND = 0.5
# The spike: its section's height (a share of its half-width), how high its middle lies (over its lowest point), the
# shading's relief on its body (fine minus broad, times this), where its cap ends (the picture's row) and how much
# rounder it is.
SPIKE_FLAT = 0.62
SPIKE_LIFT = 0.45
COBBLES = (2.8, 1.1, 1.4, 0.5, 0.25)   # the least distance between two, their height, reach, the cracks' depth, light
CAP_ROWS = 11.5
NECK = (11.4, 0.3, 1.4)      # the neck under the cap: its row, how much narrower, over how many rows
TIP_FADE = (43.0, 49.5)      # the rows over which the cobbles fade out towards the point
TIP_Y = 27.5 - 51.5          # the spike's point in its drawn place (85 above 123)
# The frames: (106's model, its sprite, 107's model, its sprite or None, the spike's pose: its point's y, how much
# lower its middle lies at the point than where 85 above 123 draws it, its pitch (degrees, its back going down into the
# throat), whether it is cut off behind the mouth; or None (no spike), whether the maw is there).
POSES = [("ixm_maw", 9, "ixm_maw_low", 45, None, True),
         ("ixm_maw_11", 11, None, None, (16.6, 4.6, 18.0, True), True),
         ("ixm_maw_13", 13, None, None, (9.6, 3.0, 18.0, True), True),
         ("ixm_maw_15", 15, None, None, (5.6, 1.7, 18.0, True), True),
         ("ixm_maw_17", 17, None, None, (1.6, 0.7, 18.0, True), True),
         ("ixm_maw_47", 47, None, None, (0.6, 0.0, 18.0, True), True),
         ("ixm_maw_49", 49, "ixm_maw_low_87", 87, (-5.5, 0.0, 13.0, True), True),
         ("ixm_maw_51", 51, "ixm_maw_low_89", 89, (-10.5, 0.0, 8.5, True), True),
         ("ixm_maw_53", 53, "ixm_maw_low_91", 91, (-17.5, 0.0, 4.0, True), True),
         ("ixm_maw_55", 55, "ixm_maw_low_93", 93, (-25.0, 0.0, 1.5, False), True),
         ("ixm_maw_85", 85, "ixm_maw_low_123", 123, (-23.5, 0.0, 0.0, False), False)]
CLIP = 24.6                  # behind this (y) the spike is inside the ridge's rock (the throat)

# The grids the solids are sampled on.
STEP = 0.2
MAW_GRID = ((-12.6, 127), (-14.6, 147), (-4.8, 72))    # x, y (106's own), z: start, count
SPIKE_STEP = 0.22
SPIKE_GRID = ((-10.4, 95), (-24.6, 247), (-0.4, 76))   # x, y (the picture's), z
MAW_TARGET, SPIKE_TARGET = 2800, 6500
TANS = (0x10, 0x12, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d)
CAP_SHADE = 0x14             # the cuts


def art(text):
    rows = text.strip("\n").split("\n")
    out = np.full((len(rows), 24), np.nan)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                out[r, c] = int(ch, 16)
    return out


def without_ring(shade):
    """The shades without the sprite's dark outline ring (its shade 0-1 pixels next to a transparent one or the
    picture's edge, which in the round are the solid's sides, not cracks): their neighbours' shades fill them."""
    out = shade.copy()
    h, w = shade.shape
    for r in range(h):
        for c in range(w):
            if np.isnan(shade[r, c]) or shade[r, c] > 1:
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if not (0 <= rr < h and 0 <= cc < w) or np.isnan(shade[rr, cc]):
                    out[r, c] = np.nan
                    break
    return out


def axes(grid, step):
    return [start + step * np.arange(count) for start, count in grid]


def materials():
    return {i: k.material("maw_rock", palette=i, metallic=0.0, roughness=0.86) for i in TANS}


def shade_index(s):
    """The nearest of TANS to shade s (0-15 in ramp 1)."""
    levels = np.array(TANS) - 0x10
    return np.array(TANS)[np.argmin(np.abs(np.asarray(s)[:, None] - levels[None, :]), axis=1)]


def lifted(fine, broad, keep=0.5, detail=0.75, middle=8.5):
    low = np.where(broad < middle, middle + (broad - middle) * keep, broad)
    return low + detail * (fine - broad)


# --- The maw --------------------------------------------------------------------------------------------------------

def maw_solid():
    shade = art(MAW)
    known = (~np.isnan(shade)).astype(float)
    filled = rw.fill(without_ring(shade))
    xs, ys, zs = axes(MAW_GRID, STEP)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    col, row = gx + 12.0, 14.0 - gy
    # the plan: the tile's pixels (bilinear, a little blurred), as a rough signed distance
    mask = rw.sample(rw.blur2(known, 0.45, 1.0), col, row)
    outside = (col < 0) | (col > 24) | (row < 0) | (row > 28)
    plan = np.where(outside, 2.0, (0.5 - mask) * 2.2)
    # the top: the shading as height, flat at the top and side edges
    base, per, blur = MAW_RELIEF
    s = rw.sample(rw.blur2(filled, blur, 1.0), col, row)
    top = base + per * s
    flat = smoothstep(14.0 - MAW_EDGE[0], 14.0, gy) + smoothstep(12.0 - MAW_EDGE[1], 12.0, np.abs(gx))
    w = np.clip(flat, 0.0, 1.0)
    top = top * (1.0 - w) + MAW_FLAT * w
    z = zs[None, None, :]
    d = smax(plan[:, :, None], z - top[:, :, None], MAW_ROUND)
    d = np.maximum(d, SKIRT - z).astype(np.float32)
    verts, quads = surface_nets(d, (xs[0], ys[0], zs[0]), STEP)
    return finish_whole(mesh_object("maw_dense", verts, quads), smooth=1), filled


def maw_shades(centres, normals, filled):
    """The maw's faces' palette indices: the sprite's shades under them (the broad shading lifted, the fine kept);
    the mouth's floor and everything turned down dark."""
    x, y = centres[:, 0], centres[:, 1]
    col, row = x + 12.0, 14.0 - y
    fine = rw.sample(rw.blur2(filled, 0.45, 1.0), col, row)
    broad = rw.sample(rw.blur2(filled, 2.0, 1.0), col, row)
    s = np.where(fine < 0.8, fine, lifted(fine, broad))
    mouth = rw.sample((filled < 0.5).astype(float), col, row)
    s = np.where((mouth > 0.35) & (centres[:, 2] < MAW_RELIEF[0] + 0.9), np.minimum(s, 0.5), s)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 2.0), s)
    s = np.where(centres[:, 2] < MAW_FLAT - 0.4, np.minimum(s, 3.0), s)   # the skirt under the ridge's edge
    return shade_index(s)


# --- The spike ------------------------------------------------------------------------------------------------------

def spike_profile(shade):
    """The spike's half-width and its middle's x along the picture's rows (from its pixels)."""
    widths, middles = [], []
    for r in range(shade.shape[0]):
        cs = np.nonzero(~np.isnan(shade[r]))[0]
        if len(cs):
            widths.append((cs[-1] + 1 - cs[0]) / 2.0)
            middles.append((cs[0] + cs[-1] + 1) / 2.0 - 12.0)
        else:
            widths.append(0.0)
            middles.append(0.0)
    return np.array(widths), np.array(middles)


def cobbles(gx, gy, light, inside):
    """The spike's cobbles (polish_ixm_wall_rock.cobbles' way): one round each light blob of its sprite (the local
    maxima of its shading, COBBLES[0] apart at least, within inside), the cracks between them where two cells meet (a
    Voronoi diagram of the blobs, its borders wavering), each a dome rising from the cracks, lighter blobs higher."""
    gap, height, reach, sink, lift = COBBLES
    smooth = rw.blur2(light, 0.5, SPIKE_STEP)
    r = int(round(1.0 / SPIKE_STEP))
    p = np.pad(smooth, r, mode="edge")
    peak = np.ones_like(smooth, bool)
    for di in range(-r, r + 1):
        for dj in range(-r, r + 1):
            if di or dj:
                peak &= smooth >= p[r + di:r + di + smooth.shape[0], r + dj:r + dj + smooth.shape[1]]
    cand = sorted(np.argwhere(peak & inside).tolist(), key=lambda ij: (-smooth[ij[0], ij[1]], ij[0], ij[1]))
    seeds = []
    for i, j in cand:
        x, y = gx[i, j], gy[i, j]
        if all((x - sx) ** 2 + (y - sy) ** 2 >= gap ** 2 for sx, sy, _ in seeds):
            seeds.append((x, y, smooth[i, j]))
    print("spike cobbles: %d" % len(seeds))
    sx = np.array([q[0] for q in seeds], np.float32)
    sy = np.array([q[1] for q in seeds], np.float32)
    sv = np.array([q[2] for q in seeds], np.float32)
    fx, fy = gx.ravel(), gy.ravel()
    wx = fx + 0.6 * noise3(fx / 2.4, fy / 2.4, np.full(fx.shape, 0.5), 91)
    wy = fy + 0.6 * noise3(fx / 2.4, fy / 2.4, np.full(fx.shape, 2.5), 93)
    d = np.sqrt((wx[:, None] - sx[None, :]) ** 2 + (wy[:, None] - sy[None, :]) ** 2)
    order = np.argsort(d, axis=1)
    d1 = np.take_along_axis(d, order[:, :1], 1)[:, 0]
    d2 = np.take_along_axis(d, order[:, 1:2], 1)[:, 0]
    h = height * (1.0 + lift * np.clip((sv[order[:, 0]] - 9.0) / 4.0, -1.0, 1.0))
    t = np.clip((d2 - d1) / 2.0 / reach, 0.0, 1.0)
    return (-sink + (h + sink) * np.sqrt(t * (2.0 - t))).reshape(gx.shape).astype(np.float32)


def spike_solid():
    shade = art(SPIKE)
    filled = rw.fill(without_ring(shade))
    widths, middles = spike_profile(shade)
    # smoothed along the spike (its outline is a pixel staircase), its point kept pointed
    rows = np.arange(len(widths)) + 0.5
    kernel = np.exp(-0.5 * (np.arange(-3, 4) / 1.2) ** 2)
    kernel /= kernel.sum()
    w_s = np.convolve(np.pad(widths, 3, mode="edge"), kernel, mode="valid")
    m_s = np.convolve(np.pad(middles, 3, mode="edge"), kernel, mode="valid")
    w_s = np.minimum(w_s, widths + 0.6)
    xs, ys, zs = axes(SPIKE_GRID, SPIKE_STEP)
    r_y = 27.5 - ys                                  # the picture's row at each y
    hw = np.interp(r_y, rows, w_s, left=0.0, right=0.0)
    mid = np.interp(r_y, rows, m_s)
    hw = np.where(r_y > 51.6, 0.0, hw) - 0.35          # (its outline is the sprite's dark ring)
    hw = hw * (1.0 - NECK[1] * np.exp(-((r_y - NECK[0]) / NECK[2]) ** 2))
    hw = np.maximum(hw, 0.05)
    # the cap rounder (a dome), the body flatter; its lowest point at z 0
    cap = smoothstep(CAP_ROWS + 1.5, CAP_ROWS - 1.0, r_y)
    flat = SPIKE_FLAT + 0.18 * cap
    height = hw * flat
    zc = SPIKE_LIFT + height.max()
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    col, row = gx + 12.0, 28.0 - gy
    light = rw.sample(rw.blur2(filled, 0.45, 1.0), col, row)
    inside = (np.abs(gx - mid[None, :]) < hw[None, :] - 0.8) & (r_y[None, :] > CAP_ROWS + 1.0) & (r_y[None, :] < 50.0)
    point = smoothstep(TIP_FADE[0], TIP_FADE[1], r_y)          # the point smooth, as the sprite draws it
    relief = cobbles(gx, gy, light, inside) * ((1.0 - cap) * (1.0 - point))[None, :]
    u = (gx - mid[None, :]) / hw[None, :]
    z = zs[None, None, :]
    hz = height[None, :, None]
    v = (z - zc) / hz
    ell = np.sqrt(u[:, :, None] ** 2 + v ** 2)
    d = (ell - 1.0) * np.minimum(hw[None, :, None], hz) - relief[:, :, None] * np.clip(v + 0.4, 0.0, 1.0)
    ends = np.maximum(ys[None, :, None] - 27.4, TIP_Y - 0.1 - ys[None, :, None])
    d = np.maximum(d, ends).astype(np.float32)
    verts, quads = surface_nets(d, (xs[0], ys[0], zs[0]), SPIKE_STEP)
    return finish_whole(mesh_object("spike_dense", verts, quads), smooth=1), filled, zc


def spike_shades(free_centres, normals, filled):
    """The spike's faces' palette indices from its sprite's shades at the faces' places on the spike lying as drawn."""
    x, y = free_centres[:, 0], free_centres[:, 1]
    col, row = x + 12.0, 28.0 - y
    fine = rw.sample(rw.blur2(filled, 0.5, 1.0), col, row)
    broad = rw.sample(rw.blur2(filled, 2.2, 1.0), col, row)
    s = lifted(fine, broad, keep=0.55, detail=0.7, middle=9.0)
    s = np.where(normals[:, 2] < -0.35, np.minimum(s, 3.0), s)
    return shade_index(s)


def pose_matrix(pose, zc):
    """The spike moved from where 85 above 123 draws it to a frame's pose: pitched about its point (its back down by
    pitch degrees), its point at (y, z)."""
    y, lower, pitch = pose[0], pose[1], pose[2]
    to_origin = Matrix.Translation((0.0, -TIP_Y, -zc))
    turn = Matrix.Rotation(math.radians(-pitch), 4, "X")   # (+y back end goes down)
    back = Matrix.Translation((0.0, y, zc - lower))
    return back @ turn @ to_origin


# --- Pieces ---------------------------------------------------------------------------------------------------------

def reduced(dense, target, name):
    obj = dense.copy()
    obj.data = dense.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    rw.decimate(obj, set(), target)
    return obj


def cut(obj, planes, mats, name, shading):
    """The part of obj on the inner side of the planes, capped, its normals the dense shading's (caps flat)."""
    piece, rim = ws.cut_planes(obj, planes, mats[CAP_SHADE], name)
    if piece is None:
        return None, None
    piece.hide_render = False
    slot = mk.slot_of(piece, mats[CAP_SHADE])
    flags = [1 if p.material_index == slot else 0 for p in piece.data.polygons]
    piece.data.polygons.foreach_set("material_index", flags)
    rw.shade_like(piece, shading)
    return piece, flags


def paint(obj, indices, flags, mats):
    indices = np.array(indices)
    indices[np.array(flags) == 1] = CAP_SHADE
    rw.assign(obj, indices, mats)


def blank(name, mats):
    """One tiny triangle under the ridge's top plane (the renderer refuses a model without triangles)."""
    obj = k.mesh_object(name, [(0.0, 0.0, -6.0), (0.02, 0.0, -6.0), (0.0, 0.02, -6.0)], [(0, 1, 2)], mats[TANS[0]])
    return obj


def top_mask(sheet, sprite):
    return k.sprite_mask(sheet, sprite)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = materials()
    maw_dense, maw_filled = maw_solid()
    maw_shading = mk.NormalSource(maw_dense)
    maw = reduced(maw_dense, MAW_TARGET, "maw")
    rw.shade_like(maw, maw_shading)
    centres, normals = face_data(maw)
    rw.assign(maw, maw_shades(centres, normals, maw_filled), mats)
    spike_dense, spike_filled, zc = spike_solid()
    spike = reduced(spike_dense, SPIKE_TARGET, "spike")
    spike.data.materials.append(mats[TANS[6]])
    for obj in (maw_dense, spike_dense, spike):
        obj.hide_render = True
    maw.hide_render = True
    print("maw: %d triangles, spike: %d (dense %d)" % (len(maw.data.polygons), len(spike.data.polygons),
                                                       len(spike_dense.data.polygons)))
    sheet = os.path.join(options["check"], "enemy_8.png") if "check" in options else None
    for name_top, sprite_top, name_low, sprite_low, pose, with_maw in POSES:
        if pose is None:
            pieces = {name_top: ([], with_maw, 14.0, sprite_top), name_low: (None, False, -14.0, sprite_low)}
        else:
            m = pose_matrix(pose, zc)
            posed = spike.copy()
            posed.data = spike.data.copy()
            posed.name = posed.data.name = "spike_posed"
            bpy.context.scene.collection.objects.link(posed)
            posed.data.transform(m)
            dense = spike_dense.copy()
            dense.data = spike_dense.data.copy()
            bpy.context.scene.collection.objects.link(dense)
            dense.data.transform(m)
            dense.data.update()
            shading = mk.NormalSource(dense)
            clip = [((0.0, CLIP, 0.0), (0.0, 1.0, 0.0))] if pose[3] else []
            parts_top, parts_low = [], []
            inverse = m.inverted()
            for planes, parts, label in (([((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))] + clip, parts_top, "top"),
                                         ([((0.0, 0.0, 0.0), (0.0, 1.0, 0.0))] + clip, parts_low, "low")):
                piece, flags = cut(posed, planes, mats, "spike_" + label, shading)
                if piece is None:
                    continue
                c, n = face_data(piece)
                free = np.array([tuple(inverse @ Vector(p)) for p in c])
                rot = inverse.to_3x3()
                free_n = np.array([tuple(rot @ Vector(q)) for q in n])
                paint(piece, spike_shades(free, free_n, spike_filled), flags, mats)
                parts.append(piece)
            bpy.data.objects.remove(posed)
            bpy.data.objects.remove(dense)
            pieces = {name_top: (parts_top, with_maw, 14.0, sprite_top)}
            if name_low:
                pieces[name_low] = (parts_low, False, -14.0, sprite_low)
            else:
                for p in parts_low:     # (nothing of the spike below the sprites' edge yet)
                    bpy.data.objects.remove(p)
        for name, (parts, add_maw, centre, sprite) in pieces.items():
            if only and name not in only:
                for p in parts or []:
                    bpy.data.objects.remove(p)
                continue
            objs = []
            if parts is None:
                objs = [blank(name, mats)]
            else:
                for p in parts:
                    p.data.transform(Matrix.Translation((0.0, -centre, 0.0)))
                    objs.append(p)
                if add_maw:
                    c = maw.copy()
                    c.data = maw.data.copy()
                    bpy.context.scene.collection.objects.link(c)
                    c.hide_render = False
                    objs.append(c)
            triangulate(objs)
            obj = join(objs, name) if len(objs) > 1 else objs[0]
            obj.name = name
            obj.hide_render = False
            bpy.context.view_layer.update()
            if sheet and sprite != 45:
                mk.compare("%s (8 %d)" % (name, sprite), mk.coverage([obj], 24, 28), top_mask(sheet, sprite))
            mk.report(name, [obj], os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, [obj])
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
