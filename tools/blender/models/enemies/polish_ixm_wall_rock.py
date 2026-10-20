"""The rock of IXMUCANE's and SAWBLADES' wall (sheet 8 sprites 167 above 205 above 243, 2x2 each: one 24 x 84 column, its
rock rows 0-69; enemies 112, 113, 114, on the sky, ground or top layer as the events put the wall), polished
(2026-10-20; it replaces wave3_y_wall.py's rock column, a heightfield of bumps painted from the sprite in odd shades).
models.cfg (the model lines stay): sprite 8 167 ixm_wall_rock_top yaw=0, sprite 8 205 ixm_wall_rock_mid yaw=0, sprite
8 243 ixm_wall_rock_low yaw=0 (unchanged). None of the three is another sprite's pixels mirrored or in other ramps.

The levels build the wall from columns of three sprites, 24 pixels apart: a left end (169 / 207 / 245), a slot (277 /
203 / 241), one or three of these rock columns, a slot and a right end (161 / 199 / 237) (events 6, 7, 10 or 15).
wave3_y_wall.py stood the wall up: its top level at HEIGHT (20) from the cliff at y CLIFF (-16.5) back to its rounded
back edge (about y 22 to 25.5), the cliff upright down to the ground (z 0); every column's left and right edges have
that section, so the columns meet whatever their neighbours. This column keeps it: within EDGE pixels of its edges
everything below fades into it, so it meets the slots and ends (still wave3_y_wall.py's) and itself.

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 70 rock; tans of ramp 1): the wall's top
(rows 0-44) a bed of rounded boulders between dark cracks, lit at their upper left, bumps along the back edge (rows
0-3); its front (rows 45-69) a cliff of upright ribs and fingers of rock between dark clefts, their feet ragged (rows
63-69). Mapped as wave3_y_wall.py mapped them: the top's row r at y = 28 - r, the cliff's row r at z = 20 (70.5 - r) /
26.

Built as weathered layered sandstone matching the tan rock of the level's ridges (its tile map paints them in the same
ramp, 14-19, lighter on top) and polish_rock_arch.py's arch: a signed distance on a grid STEP pixels apart, its
surface extracted (polish_rock_arch.surface_nets) and smoothed: the slab of the wall's section; on its top a bed of
cobbles, one round each light blob of the sprite's top (a Voronoi diagram of the blobs, its cells' borders wavering:
the cracks), each a dome BOULDER high rising from the cracks (lighter blobs a little higher), the cracks sunk; out of
its cliff the ribs, rounded bars standing out between the sprite's clefts (RIB), the clefts sunk into it, their feet
where the sprite's end; sandstone's bedding: grooves round the steep faces every STRATA pixels, the layers' colours
banded; smooth noise. Its colours are the sprite's own shades under each face (the top's from rows 0-44, the cliff's
from rows 45-69), their broad shading lifted towards the middle (the game's light adds it again), their fine shading
kept, grained a little, the cliff's a little lighter (it faces away from the sun), the undersides dark, the flat strip
at the edges dark as a crack (where the columns meet, a joint). The whole is reduced, then cut into its three pieces
along the sprites' edges (y 14 and -14; the cuts capped), each piece's triangles reduced to about TARGET with the
vertices on its cuts kept where they are (pieces meet exactly) and its normals those of the dense whole, then moved so
its sprite's centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
column's whole is wave3_y_wall.py's column: x -12..12, the middle piece's centre at y 0 (the top piece's at y 28, the
low piece's at y -28).

Replaces wave3_y_wall.py's rock pieces: in its PIECES loop over COLUMNS skip the rock column (if _name == "rock":
continue), so that it no longer exports ixm_wall_rock_top/_mid/_low, and drop the ixm_wall_rock lines of its
docstring. Keep the rock column in COLUMNS and build_wall(): every piece is cut from the one whole wall and each
column's heightfield reaches 6 pixels past its edges, so the slots' pieces (and wave3_ap_ixm.py's damaged slot, which
builds the same whole with build_wall(stand=False)) keep the rock column's overlap; removing it would change them.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of each
piece's top view against the sprites, where the rock lies: the top pieces' lower half and the low piece's upper
half), --preview <prefix>, --whole <prefix> (the whole column's views), --only <model,...>.
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
from polish_rock_arch import face_data, finish_whole, mesh_object, noise3, smax, smoothstep, surface_nets  # noqa: E402

# The rock's pixels (8 167 above 205 above 243, rows 0-69): each its shade in ramp 1 (palette index 0x10 + digit;
# 0 also for the near-black clefts of ramp 0), '.' none.
ART = """
.............000........
..00..000...05670.000...
.07800ba80.05cbb007640..
08a969ea9705bfbb36bb840.
88d858bb9836bdcb58bba740
8dc656999534adba58bb7624
8a638a5332228ca758b97645
6642ceb73412698456777568
7315ba875531463222366488
850387766652254674345579
9542566666645147a9438967
668536666645641162589997
898822666457a96223899aaa
9988534435adba851689aaa8
8887643479ca999834787777
887764478aba999764677777
777765788ab9998663367777
777667888ab9987664345677
775688889aba866663653356
544799889aa8666654666325
6558a999aa86666446787736
66599aaa9766664258888757
773455666666545547887667
876445555544468874766668
9887433444367ab985455379
aa98632334479a898843358b
99998457775a9888887657ab
98899547884a888888877599
88888746883a888888886568
88888753773a888888876548
88887653354a888888866547
887666632258888888766545
876666445334888887666535
666654767753677766666535
566547888873666666666445
356478888763476666663356
546488877434256666642477
644468853476335666416988
76633448ab98315543169a88
877218ab9988433026259bc9
98516ab98887333479649bb7
7613bb88887345268b846765
6408cb98884277357a942455
6319cdc98647975257741255
6327accb735bb76024652155
63279987526dc85211453055
541456664049841342010013
541245554046411565300355
553233554034304795542465
654421253012017865543595
a542001230000587554424a5
b541000000230596544413a5
954000000133158544430285
954001100363157544520185
953012210483257544510165
853023320493257445601265
753023320483257445601365
763023420373257456502265
663023520273157467202255
653023520063058576002245
553023520012047664023245
553023520100047660023235
551023620130047740124115
542023720232135520234103
541023700344423301334112
500013500244641212335212
000023300244632012335200
0...0310003473212335510.
....030..02472212345300.
.....0...0145210235500..
"""

# The pieces: (name, sprite, the box it covers (y0, y1)); all span x -12..12.
PIECES = [("ixm_wall_rock_top", 167, (14.0, 42.0)), ("ixm_wall_rock_mid", 205, (-14.0, 14.0)),
          ("ixm_wall_rock_low", 243, (-42.0, -14.0))]

# The wall's section (wave3_y_wall.py's, upright): its top, its cliff, its back's rounding (the back at BACK[0] at
# the top, BACK[0] + BACK[1] at the ground, an ellipse between).
HEIGHT, CLIFF, BACK = 20.0, -16.5, (22.0, 3.5)
TOP_ROWS, FACE_ROWS = 44.5, (44.5, 70.5)   # the sprite's rows: the top above TOP_ROWS, the cliff between FACE_ROWS
EDGE = (10.7, 11.85)       # |x| where the relief starts fading and where it is gone (the shared section)
# The relief: the boulders on the top (their height over the slab, the distance from a crack at which they reach it,
# how much deeper the cracks are, how much the sprite's light adds); the ribs out of the cliff (likewise).
BOULDER = (1.9, 1.9, 1.1, 0.25)
COBBLE_GAP = 3.4        # the least distance between two boulders' middles
RIB = (1.7, 1.5, 1.0, 0.3)
CRACK_FACE = 2.6         # the sprite's shades up to which a cliff's pixel is a cleft          # the sprite's shades up to which a pixel is a crack / a cleft
ROUND = 0.9                # the rounding of the top's front edge (fading to none at the edges)
NOISE = ((0.1, 2.4), (0.045, 0.9))
STRATA = (0.3, 2.3)        # the bedding: groove depth, spacing
DARK_KEEP, DETAIL, DITHER, BANDS = 0.5, 0.7, 0.1, 0.45
FACE_LIFT = 1.0            # the cliff's colours this much lighter (it faces away from the sun)
JOINT_DARK = 2.0           # how much darker the edges' flat strip is (where the columns meet: a joint)
CAP = 0x16                 # the cuts (where the pieces and the neighbouring columns meet)
TARGET = 4400              # triangles per piece (fewer where the piece holds less rock)
WHOLE_TARGET = 30000       # the whole's triangles before it is cut

# The grid the solid is sampled on.
STEP = 0.2
X0, NX = -12.6, 127
Y0, NY = -20.0, 238
Z0, NZ = -0.6, 125
XS = X0 + STEP * np.arange(NX)
YS = Y0 + STEP * np.arange(NY)
ZS = Z0 + STEP * np.arange(NZ)


# --- The sprite's fields ----------------------------------------------------------------------------------------------

def art():
    rows = ART.strip("\n").split("\n")
    out = np.full((len(rows), 24), np.nan)
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != ".":
                out[r, c] = int(ch, 16)
    return out


def fill(a, steps=12):
    """The pixels without a value take their neighbours' (step by step outwards)."""
    a = a.copy()
    for _ in range(steps):
        known = ~np.isnan(a)
        if known.all():
            break
        v = np.pad(np.where(known, a, 0.0), 1)
        kn = np.pad(known.astype(np.float64), 1)
        acc = v[:-2, 1:-1] + v[2:, 1:-1] + v[1:-1, :-2] + v[1:-1, 2:]
        cnt = kn[:-2, 1:-1] + kn[2:, 1:-1] + kn[1:-1, :-2] + kn[1:-1, 2:]
        new = ~known & (cnt > 0)
        a[new] = acc[new] / cnt[new]
    a[np.isnan(a)] = 0.0
    return a


def sample(a, u, v):
    """Bilinear sample of a pixel array a[row, column] at pixel coordinates u (column, edges) and v (row, edges)."""
    rows, cols = a.shape
    uu, vv = np.asarray(u, float) - 0.5, np.asarray(v, float) - 0.5
    c0, r0 = np.floor(uu).astype(int), np.floor(vv).astype(int)
    fu, fv = uu - c0, vv - r0

    def at(r, c):
        return a[np.clip(r, 0, rows - 1), np.clip(c, 0, cols - 1)]
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def blur2(a, sigma, step):
    """A Gaussian blur of a 2D field sampled step pixels apart."""
    s = sigma / step
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


def crack_distance(field, level, step, reach=4.0):
    """For a 2D field on a grid step pixels apart, about how far each point is from the nearest point below level (a
    chamfer distance grown from the cracks, up to reach)."""
    big = np.float32(reach + 1.0)
    d = np.where(field < level, 0.0, big).astype(np.float32)
    moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142),
             (-1, -1, 1.4142)]
    for _ in range(int(math.ceil(reach / step)) + 2):
        p = np.pad(d, 1, mode="edge")
        best = d
        for di, dj, w in moves:
            shifted = p[1 + di:1 + di + d.shape[0], 1 + dj:1 + dj + d.shape[1]] + np.float32(w * step)
            best = np.minimum(best, shifted)
        if np.array_equal(best, d):
            break
        d = best
    return d


def dome(d, height, reach, sink):
    """A rounded rise from a crack: -sink at the crack, height from reach on (a quarter circle between)."""
    t = np.clip(d / reach, 0.0, 1.0)
    return -sink + (height + sink) * np.sqrt(t * (2.0 - t))


def cobbles(gx, gy, s_top):
    """The boulders on the top: one round each light blob of the sprite's top (the local maxima of its shading,
    COBBLE_GAP apart at least), the cracks between them where two boulders' cells meet (a Voronoi diagram of the
    blobs, its cells' borders wavering), each a dome rising from the cracks, lighter blobs a little higher."""
    smooth = blur2(s_top, 1.0, STEP)
    r = int(round(1.4 / STEP))
    p = np.pad(smooth, r, mode="edge")
    peak = np.ones_like(smooth, bool)
    for di in range(-r, r + 1):
        for dj in range(-r, r + 1):
            if di or dj:
                peak &= smooth >= p[r + di:r + di + smooth.shape[0], r + dj:r + dj + smooth.shape[1]]
    inside = (gy > CLIFF - 1.0) & (gy < BACK[0] + BACK[1] + 1.5)
    cand = np.argwhere(peak & inside)
    cand = sorted(cand.tolist(), key=lambda ij: -smooth[ij[0], ij[1]])
    seeds = []
    for i, j in cand:
        x, y = gx[i, j], gy[i, j]
        if all((x - sx) ** 2 + (y - sy) ** 2 >= COBBLE_GAP ** 2 for sx, sy, _ in seeds):
            seeds.append((x, y, smooth[i, j]))
    print("cobbles: %d" % len(seeds))
    sx = np.array([q[0] for q in seeds], np.float32)
    sy = np.array([q[1] for q in seeds], np.float32)
    sv = np.array([q[2] for q in seeds], np.float32)
    # The cells' borders waver: the points' positions are warped by smooth noise before measuring.
    flat_x, flat_y = gx.ravel(), gy.ravel()
    wx = flat_x + 0.7 * noise3(flat_x / 2.6, flat_y / 2.6, np.full(flat_x.shape, 0.5), 71)
    wy = flat_y + 0.7 * noise3(flat_x / 2.6, flat_y / 2.6, np.full(flat_x.shape, 2.5), 73)
    d = np.sqrt((wx[:, None] - sx[None, :]) ** 2 + (wy[:, None] - sy[None, :]) ** 2)
    order = np.argsort(d, axis=1)
    d1 = np.take_along_axis(d, order[:, :1], 1)[:, 0]
    d2 = np.take_along_axis(d, order[:, 1:2], 1)[:, 0]
    nearest = order[:, 0]
    edge = (d2 - d1) / 2.0                              # how far inside its cell a point is
    h, reach, sink, light = BOULDER
    height = h * (1.0 + light * np.clip((sv[nearest] - 9.0) / 4.0, -1.0, 1.0))
    t = np.clip(edge / reach, 0.0, 1.0)
    out = -sink + (height + sink) * np.sqrt(t * (2.0 - t))
    return out.reshape(gx.shape).astype(np.float32)


def fade(x):
    return smoothstep(EDGE[1], EDGE[0], np.abs(x))


def fields(shade):
    """The relief on the grid: the boulders' height over the top (x, y) and the ribs' out of the cliff (x, z)."""
    t0 = time.time()
    filled = fill(shade)
    # The top: x, y -> the sprite's column and row.
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    s_top = blur2(sample(filled, gx + 12.0, 28.0 - gy), 0.45, STEP)
    boulders = cobbles(gx, gy, s_top) * fade(gx)
    # The cliff: x, z -> the sprite's column and row.
    fx, fz = np.meshgrid(XS, ZS, indexing="ij")
    row = FACE_ROWS[1] - (FACE_ROWS[1] - FACE_ROWS[0]) * np.clip(fz, 0.0, HEIGHT) / HEIGHT
    s_face = blur2(sample(filled, fx + 12.0, row), 0.3, STEP)
    gone = sample(np.isnan(shade).astype(float), fx + 12.0, row) > 0.5
    s_face = np.where(gone, 0.0, s_face)              # where the sprite's ribs end: clefts
    d_face = crack_distance(s_face, CRACK_FACE, STEP)
    h, reach, sink, light = RIB
    ribs = dome(d_face, h, reach, sink) + light * np.clip((blur2(s_face, 1.0, STEP) - 6.0) / 4.0, -1.0, 1.0)
    ribs *= fade(fx)
    print("fields: %.1f s" % (time.time() - t0))
    return boulders.astype(np.float32), ribs.astype(np.float32), s_top, s_face


def solid(boulders, ribs):
    """The column's signed distance on the grid (negative inside)."""
    t0 = time.time()
    x = XS[:, None, None].astype(np.float32)
    y = YS[None, :, None].astype(np.float32)
    z = ZS[None, None, :].astype(np.float32)
    top = z - (HEIGHT + boulders[:, :, None])                     # under the top and its boulders
    front = (CLIFF - ribs[:, None, :]) - y                        # behind the cliff and its ribs
    back_y = BACK[0] + BACK[1] * np.sqrt(np.clip(1.0 - (np.clip(z, 0.0, HEIGHT) / HEIGHT) ** 2, 0.0, 1.0))
    back = y - back_y
    kk = 0.03 + ROUND * fade(x)
    d = smax(top, front, kk)
    d = np.maximum(d, back)
    d = np.maximum(d, -z).astype(np.float32)
    # Weathering near the surface, faded at the edges: smooth noise; the bedding's grooves round the steep faces.
    i, j, kz = np.nonzero(np.abs(d) < 1.5)
    px, py, pz = XS[i], YS[j], ZS[kz]
    w = fade(px) * np.clip(pz / 0.8, 0.0, 1.0)
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * noise3(px / scale, py / scale, pz / scale, 167 + n)
    gz = np.gradient(d, STEP, axis=2)[i, j, kz]
    wall = np.clip(1.0 - 1.3 * np.abs(gz), 0.0, 1.0)
    warp = 0.6 * noise3(px / 9.0, py / 9.0, np.full(len(i), 0.3), 5)
    phase = (pz + warp) / STRATA[1] - 0.3
    detail += STRATA[0] * wall * np.exp(-((phase - np.round(phase)) / 0.2) ** 2)
    d[i, j, kz] += (detail * w).astype(np.float32)
    # Smoothed a little (no features finer than the grid).
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


# --- Colours ----------------------------------------------------------------------------------------------------------

def materials():
    return {i: k.material("ixm_rock", palette=i, metallic=0.0, roughness=0.86) for i in range(0x10, 0x20)}


def shades(centres, normals, s_top, s_face):
    """Each face's palette index: the sprite's shade under it (the top's or the cliff's), its broad shading lifted,
    its fine shading kept, grained, banded with the bedding; the undersides dark."""
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    # The cliff (and the ribs out of it) takes the cliff's shades, everything behind its top edge the top's (the
    # boulders' and cracks' walls too).
    up = ~((y < CLIFF + 2.2) & (z < HEIGHT + 0.6) & (normals[:, 1] < 0.25))
    # The top's fields are on the (x, y) grid, the cliff's on (x, z): bilinear lookups.

    def grid(a, u0, du, u, v0, dv, v):
        fu = np.clip((u - u0) / du, 0, a.shape[0] - 1.001)
        fv = np.clip((v - v0) / dv, 0, a.shape[1] - 1.001)
        iu, iv = np.floor(fu).astype(int), np.floor(fv).astype(int)
        tu, tv = fu - iu, fv - iv
        return (a[iu, iv] * (1 - tu) * (1 - tv) + a[iu + 1, iv] * tu * (1 - tv) + a[iu, iv + 1] * (1 - tu) * tv +
                a[iu + 1, iv + 1] * tu * tv)
    fine_t, broad_t = grid(s_top, X0, STEP, x, Y0, STEP, y), grid(blur2(s_top, 3.0, STEP), X0, STEP, x, Y0, STEP, y)
    fine_f, broad_f = grid(s_face, X0, STEP, x, Z0, STEP, z), grid(blur2(s_face, 2.5, STEP), X0, STEP, x, Z0, STEP, z)
    fine = np.where(up, fine_t, fine_f)
    broad = np.where(up, broad_t, broad_f)
    lifted = np.where(broad < 9.0, 9.0 + (broad - 9.0) * DARK_KEEP, broad)
    s = lifted + DETAIL * (fine - broad) + np.where(up, 0.0, FACE_LIFT)
    s = s - JOINT_DARK * (1.0 - fade(x))                  # the flat strip at the edges: a joint, dark as a crack
    s = s + DITHER * noise3(x / 1.3, y / 1.3, z / 1.3, 41)
    s = s - BANDS * np.cos(2.0 * math.pi * z / STRATA[1]) * (~up)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 4.5), s)
    return 0x10 + np.clip(np.round(s), 3, 13).astype(int)


def assign(obj, indices, mats):
    mesh = obj.data
    used = sorted(set(indices.tolist()))
    mesh.materials.clear()
    for u in used:
        mesh.materials.append(mats[u])
    slot = {u: s for s, u in enumerate(used)}
    mesh.polygons.foreach_set("material_index", [slot[u] for u in indices.tolist()])
    mesh.update()


# --- Pieces -----------------------------------------------------------------------------------------------------------

def cut_piece(whole, box, name, mats):
    """The part of the whole inside box (x0, x1, y0, y1), its cuts closed (caps: material slot 1). Returns the object
    and the indices of its vertices on the cuts (polish_rock_arch.cut_piece's, with this rock's materials)."""
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
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None, set()

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
    obj.data.materials.append(mats[0x18])
    obj.data.materials.append(mats[CAP])
    return obj, rim


def decimate(obj, rim, target):
    """Collapses the rock's triangles to about target, the vertices on the cuts kept where they are."""
    n = len(obj.data.polygons)
    if n <= target:
        return obj
    group = obj.vertex_groups.new(name="free")
    group.add([i for i in range(len(obj.data.vertices)) if i not in rim], 1.0, "REPLACE")
    if rim:
        group.add(sorted(rim), 0.0, "REPLACE")
    mod = obj.modifiers.new("decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = target / n
    mod.use_collapse_triangulate = True
    mod.vertex_group = "free"
    mod.vertex_group_factor = 1000.0
    mk.apply(obj)
    obj.vertex_groups.clear()
    return obj


def shade_like(obj, shading):
    """The piece's normals those of the dense whole at the same points, the caps flat."""
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        flat = poly.material_index == 1
        for li in poly.loop_indices:
            n = None if flat else shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)


def piece_mask(sheet, sprite, y0):
    """The sprite's pixels where this piece's rock lies in its top view: the wall's footprint (y CLIFF - 2 .. the
    back) within the piece's box, as the top view sees it (the cliff seen edge-on)."""
    full = k.sprite_mask(sheet, sprite)
    rows = []
    for r in range(28):
        yc = y0 + 28.0 - (r + 0.5)
        inside = CLIFF - 1.5 <= yc <= BACK[0] + BACK[1]
        rows.append([full[r][c] and inside for c in range(24)])
    return rows


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mats = materials()
    shade = art()
    boulders, ribs, s_top, s_face = fields(shade)
    d = solid(boulders, ribs)
    t0 = time.time()
    verts, quads = surface_nets(d, (X0, Y0, Z0), STEP)
    del d
    whole = finish_whole(mesh_object("rock_whole", verts, quads))
    print("whole: %d vertices, %d triangles (%.1f s)" % (len(whole.data.vertices), len(whole.data.polygons),
                                                        time.time() - t0))
    shading = mk.NormalSource(whole)
    # The whole reduced first (its cuts then cross fewer, larger triangles: fewer vertices to keep on them), the
    # pieces cut from it; their shading stays the dense whole's.
    coarse = whole.copy()
    coarse.data = whole.data.copy()
    bpy.context.scene.collection.objects.link(coarse)
    decimate(coarse, set(), WHOLE_TARGET)
    dense = len(coarse.data.polygons)
    if "whole" in options:
        preview = whole.copy()
        preview.data = whole.data.copy()
        bpy.context.scene.collection.objects.link(preview)
        centres, normals = face_data(preview)
        assign(preview, shades(centres, normals, s_top, s_face), mats)
        whole.hide_render = True
        mk.preview(options["whole"] + "ixm_wall_rock_whole", [preview], size=(24, 84), scale=8, distance=2.0)
        bpy.data.objects.remove(preview)
        whole.hide_render = False
    sheet = os.path.join(options["check"], "enemy_8.png") if "check" in options else None
    for name, sprite, (y0, y1) in PIECES:
        if only and name not in only:
            continue
        box = (-12.0, 12.0, y0, y1)
        obj, rim = cut_piece(coarse, box, name, mats)
        if obj is None:
            print("== %s: nothing" % name)
            continue
        whole.hide_render = coarse.hide_render = True
        share = len(obj.data.polygons) / max(1.0, dense / 3.0)
        decimate(obj, rim, int(TARGET * min(1.0, max(0.35, share))))
        shade_like(obj, shading)
        centres, normals = face_data(obj)
        indices = shades(centres, normals, s_top, s_face)
        flags = np.empty(len(obj.data.polygons), np.int64)
        obj.data.polygons.foreach_get("material_index", flags)
        indices[flags == 1] = CAP
        assign(obj, indices, mats)
        obj.data.transform(Matrix.Translation((0.0, -(y0 + y1) / 2, 0.0)))
        obj.data.validate()
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s (8 %d)" % (name, sprite), mk.coverage([obj], 24, 28), piece_mask(sheet, sprite, y0))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        whole.hide_render = coarse.hide_render = False


if __name__ == "__main__":
    build()
